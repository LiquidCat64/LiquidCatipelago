import os
import typing
import settings
import base64
import logging
import json

from BaseClasses import Region, Tutorial, ItemClassification
from .items import CVLoDItem, ALL_CVLOD_ITEMS, POSSIBLE_EXTRA_FILLER, get_item_names_to_ids, get_item_pool
from .locations import CVLoDLocation, get_locations_to_create, get_location_name_groups, get_location_names_to_ids
from .entrances import verify_entrances, get_warp_entrances
from .options import CVLoDOptions, DraculasCondition, SubWeaponShuffle
from .stages import get_active_stages, shuffle_stages, get_stage_exits, get_active_warps, \
    get_regions_from_all_active_stages, verify_branches, CVLoDActiveStage, MISC_REGIONS, ALL_CVLOD_REGIONS
from .rules import CVLoDRules
from .data import item_names, reg_names, ent_names, stage_names
from worlds.AutoWorld import WebWorld, World
from .aesthetics import randomize_lighting, shuffle_sub_weapons, randomize_music, get_start_inventory_data,\
    get_location_write_values, randomize_shop_prices, get_transition_write_values,  get_countdown_numbers,\
    randomize_fountain_puzzle, randomize_charnel_prize_coffin, get_location_text
from .rom import CVLoDRomPatcher, get_base_rom_path, CVLoDProcedurePatch, CVLOD_US_HASH, ARCHIPELAGO_PATCH_IDENTIFIER
from .client import CastlevaniaLoDClient


class CVLoDSettings(settings.Group):
    class RomFile(settings.UserFilePath):
        """File name of the CVLoD US rom"""
        copy_to = "Castlevania - Legacy of Darkness (USA).z64"
        description = "CVLoD (USA) ROM File"
        md5s = [CVLOD_US_HASH]

    rom_file: RomFile = RomFile(RomFile.copy_to)


class CVLoDWeb(WebWorld):
    theme = "stone"

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Archipleago Castlevania 64 randomizer on your computer and connecting it to a "
        "multiworld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Liquid Cat"]
    )]


class CVLoDWorld(World):
    """
    Castlevania: Legacy of Darkness is an expanded "director's cut" edition of Castlevania 64, featuring new characters,
    new and heavily altered stages, new bosses, and more. In addition to Reinhardt and Carrie from the prior game, you
    can now play as Cornell, a man-beast who sets out on a quest to rescue his sister, and Henry, a gun-toting knight
    tasked by the church to rescue kidnapped children.
    """
    game = "Castlevania - Legacy of Darkness"
    item_name_groups = {
        "Bomb": {item_names.quest_nitro, item_names.quest_mandragora},
        "Ingredient": {item_names.quest_nitro, item_names.quest_mandragora},
        "Crest": {item_names.quest_crest_a, item_names.quest_crest_b},
    }
    location_name_groups = get_location_name_groups()
    options_dataclass = CVLoDOptions
    options: CVLoDOptions
    settings: typing.ClassVar[CVLoDSettings]
    topology_present = True

    item_name_to_id = get_item_names_to_ids()
    location_name_to_id = get_location_names_to_ids()

    active_stage_info: list[CVLoDActiveStage]
    active_warp_list: list[str]

    # Default values to possibly be updated in generate_early
    required_s2s: int = 0
    total_available_bosses: int = 0

    auth: bytearray

    web = CVLoDWeb()

    def generate_early(self) -> None:
        # Generate the player's unique authentication
        self.auth = bytearray(self.random.getrandbits(8) for _ in range(16))

        # Set the total and required Special2s to the specified YAML numbers if it's Specials, or to 0 if not.
        if self.options.draculas_condition == DraculasCondition.option_specials:
            self.options.total_special2s.value = self.options.total_special2s.value
            self.required_s2s = int(self.options.percent_special2s_required.value / 100 *
                                    self.options.total_special2s.value)
        else:
            self.options.total_special2s.value = 0
            self.required_s2s = 0

        stage_1_blacklist = {}

        # Prevent Clock Tower from being Stage 1 if more than 4 Special1s are needed to warp out of it and 3HBs are off.
        # This start is simply too constrained for the generator to handle when many S1s are needed to warp.
        if self.options.special1s_per_warp > 4 and not self.options.multi_hit_breakables:
            stage_1_blacklist[stage_names.CLOCK] = ("Too many Special1s needed to warp out for the generator to handle "
                                                    "with Multi Hit Breakables disabled.")

        # Get the slot's "intended" stage list in the order said stages appear in.
        active_stage_order = get_active_stages(self, stage_1_blacklist)

        # If Dracula's Condition is Crystal, check to see if Castle Center is in the stage list. If it's not, then we'll
        # have to change it to something else.
        if self.options.draculas_condition == DraculasCondition.option_crystal \
                and stage_names.CENTER not in active_stage_order:
            logging.warning(f"[{self.player_name}] Dracula's Condition cannot be Crystal if Castle Center is not "
                            f"present in the stage list. It will be changed to None instead.")
            self.options.draculas_condition.value = DraculasCondition.option_none

        # Validate the chosen stage branch options with the chosen stage list.
        verify_branches(self, active_stage_order)

        # Shuffle the stages if the option is on and the list is not just Castle Keep.
        if self.options.stage_shuffle and active_stage_order != [stage_names.KEEP]:
            active_stage_order = shuffle_stages(self, active_stage_order, stage_1_blacklist)

        # Add Castle Keep onto the end if it isn't present.
        if stage_names.KEEP not in active_stage_order:
            active_stage_order.append(stage_names.KEEP)

        # Get the final list of stage infos that we will save for later generation stages.
        self.active_stage_info = get_stage_exits(self.options, active_stage_order)

        # Create the seed's list of warps.
        self.active_warp_list = get_active_warps(self)

        # If there are more S1s needed to unlock the whole warp menu than there are S1s in total, drop S1s per warp to
        # the highest valid number.
        if self.options.special1s_per_warp * (len(self.active_warp_list) - 1) > self.options.total_special1s:
            new_s1s_per_warp = self.options.total_special1s // (len(self.active_warp_list) - 1)
            logging.warning(f"[{self.player_name}] Too many required Special1s "
                            f"({self.options.special1s_per_warp.value * (len(self.active_warp_list) - 1)}) for "
                            f"Special1s Per Warp setting: {self.options.special1s_per_warp.value} with Total Special1s "
                            f"setting: {self.options.total_special1s.value}. Lowering Special1s Per Warp to: "
                            f"{new_s1s_per_warp}")
            self.options.special1s_per_warp.value = new_s1s_per_warp

    def create_regions(self) -> None:
        # Create the Menu Region and all Stage Regions.
        created_regions = [Region(reg_names.menu, self.player, self.multiworld)] \
                          + get_regions_from_all_active_stages(self)

        # Create Renon's shop Region if shopsanity is on.
        #if self.options.shopsanity:
        #    created_regions.append(Region(rname.renon, self.player, self.multiworld))

        # Attach the Regions to the Multiworld.
        self.multiworld.regions.extend(created_regions)

        # Add the warp Entrances to the Menu Region (the one always at the start of our created Regions list).
        created_regions[0].add_exits(get_warp_entrances(self.active_warp_list))

        # Loop over every Region and create and add its Locations and Entrances.
        for reg in created_regions:

            # Add the Entrances to the Region (if it has any).
            if ALL_CVLOD_REGIONS[reg.name]["entrances"]:
                reg.add_exits(verify_entrances(self.options, ALL_CVLOD_REGIONS[reg.name]["entrances"],
                                               self.active_stage_info))

            # Add the Locations to the Region (if it has any).
            reg_loc_names = ALL_CVLOD_REGIONS[reg.name]["locations"]
            if reg_loc_names is None:
                continue
            locations_with_ids, locked_pairs = get_locations_to_create(reg_loc_names, self.options)
            reg.add_locations(locations_with_ids, CVLoDLocation)

            # Place locked Items on all of their associated Locations (if any Locations have any).
            for locked_loc, locked_item in locked_pairs.items():
                self.get_location(locked_loc).place_locked_item(self.create_item(locked_item,
                                                                                 ItemClassification.progression))

                # If we're looking at a boss kill Trophy, increment the total available bosses. This way, we can catch
                # gen failures should the player set more bosses required than there are total.
                if locked_item == item_names.event_trophy:
                    self.total_available_bosses += 1

        # If Dracula's Condition is Bosses and there are fewer bosses total than the required number specified by the
        # player, throw a warning and lower the option value to something valid.
        if self.options.draculas_condition == DraculasCondition.option_bosses and self.total_available_bosses < \
                self.options.bosses_required.value:
            # If we have absolutely no bosses available at all, meaning we have no active stages with bosses and the
            # Renon and Vincent fights are both disabled, let the player know of this and change Dracula's Condition to
            # None. Otherwise, throw a regular warning and lower the required bosses.
            if not self.total_available_bosses:
                logging.warning(f"[{self.multiworld.player_name[self.player]}] Dracula's Condition cannot be Bosses "
                                f"because there are absolutely no stages present in the stage list with bosses at all. "
                                f"It will be changed to None instead.")
                self.options.draculas_condition.value = DraculasCondition.option_none
            else:
                logging.warning(f"[{self.multiworld.player_name[self.player]}] Not enough bosses available for a "
                                f"{self.options.bosses_required.value}-boss requirement. Bosses Required will be "
                                f"lowered to {self.total_available_bosses}.")
                self.options.bosses_required.value = self.total_available_bosses

    def create_item(self, name: str, force_classification: ItemClassification | None = None) -> CVLoDItem:
        if force_classification is not None:
            classification = force_classification
        else:
            classification = ALL_CVLOD_ITEMS[name].default_classification

        if name in ALL_CVLOD_ITEMS:
            code = ALL_CVLOD_ITEMS[name].item_id
        else:
            code = None

        created_item = CVLoDItem(name, classification, code, self.player)

        return created_item

    def create_items(self) -> None:
        # Set up the Items correctly and submit them to the multiworld's Item pool.
        self.multiworld.itempool += get_item_pool(self)

    def set_rules(self) -> None:
        # Set all the Entrance rules properly.
        CVLoDRules(self).set_cvlod_rules()

    def generate_output(self, output_directory: str) -> None:
        active_locations = self.multiworld.get_locations(self.player)

        # Prepare the slot info to write to a JSON inside the AP patch file.
        slot_patch_info = {"options":
                               {"villa_branching_paths": self.options.villa_branching_paths.value,
                                "castle_center_branching_paths": self.options.castle_center_branching_paths.value,
                                "special1s_per_warp": self.options.special1s_per_warp.value,
                                "total_special1s": self.options.total_special1s.value,
                                "castle_wall_state": self.options.castle_wall_state.value,
                                "villa_state": self.options.villa_state.value,
                                "draculas_condition": self.options.draculas_condition.value,
                                "total_special2s": self.options.total_special2s.value,
                                "required_special2s": self.required_s2s,
                                "bosses_required": self.options.bosses_required.value,
                                "empty_breakables": self.options.empty_breakables.value,
                                "lizard_locker_items": self.options.lizard_locker_items.value,
                                "renon_fight_condition": self.options.renon_fight_condition.value,
                                "vincent_fight_condition": self.options.vincent_fight_condition.value,
                                "castle_keep_ending_sequence": self.options.castle_keep_ending_sequence.value,
                                "increase_item_limit": self.options.increase_item_limit.value,
                                "nerf_healing_items": self.options.nerf_healing_items.value,
                                "loading_zone_heals": self.options.loading_zone_heals.value,
                                "permanent_powerups": self.options.permanent_powerups.value,
                                "disable_time_restrictions": self.options.disable_time_restrictions.value,
                                "skip_gondolas": self.options.skip_gondolas.value,
                                "skip_waterway_blocks": self.options.skip_waterway_blocks.value,
                                "countdown": self.options.countdown.value,
                                "window_color_r": self.options.window_color_r.value,
                                "window_color_g": self.options.window_color_g.value,
                                "window_color_b": self.options.window_color_b.value,
                                "window_color_a": self.options.window_color_a.value},
                           "start inventory": get_start_inventory_data(self.player, self.options,
                                                                       self.multiworld.precollected_items[self.player]),
                           "stages": self.active_stage_info,
                           "warps": self.active_warp_list,
                           "location values": get_location_write_values(self, active_locations),
                           "location text": get_location_text(self, active_locations),
                           "transition values": get_transition_write_values(self.options, self.active_stage_info),
                           # Randomize which Forest Charnel House coffin is the prize one.
                           "prize coffin id": self.random.randint(0, 4),
                           # Cornell Villa fountain puzzle order to be randomized.
                           "fountain order": ["O", "M", "H", "V"],
                           "patch version": ARCHIPELAGO_PATCH_IDENTIFIER,
                           "auth": base64.b64encode(self.auth).decode()}

        # Randomize the fountain order.
        self.random.shuffle(slot_patch_info["fountain order"])

        # If Sub-weapons are shuffled amongst themselves, update the location values with them.
        if self.options.sub_weapon_shuffle == SubWeaponShuffle.option_own_pool:
            slot_patch_info["location values"].update(shuffle_sub_weapons(self))

        # Shop prices
        #if self.options.shop_prices:
        #    offset_data.update(randomize_shop_prices(self))
        # Map lighting
        #if self.options.map_lighting:
        #    offset_data.update(randomize_lighting(self))
        # Music
        #if self.options.background_music:
        #    offset_data.update(randomize_music(self))

        # Create and write the patch file.
        patch = CVLoDProcedurePatch(player=self.player, player_name=self.multiworld.player_name[self.player])
        patch.write_file("slot_patch_info.json", json.dumps(slot_patch_info).encode('utf-8'))

        patch.write(os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}"
                                                   f"{patch.patch_file_ending}"))

    def get_filler_item_name(self) -> str:
        return self.random.choice(POSSIBLE_EXTRA_FILLER)

    #def extend_hint_information(self, hint_data: typing.Dict[int, typing.Dict[int, str]]):
        # Attach each location's stage's position to its hint information if Stage Shuffle is on.
    #    if not self.options.stage_shuffle:
    #        return

    #    stage_pos_data = {}
    #    for loc in list(self.multiworld.get_locations(self.player)):
    #        stage = get_region_info(loc.parent_region.name, "stage")
    #        if stage is not None and loc.address is not None:
    #            num = str(self.active_stage_exits[stage]["position"]).zfill(2)
    #            path = self.active_stage_exits[stage]["path"]
    #            stage_pos_data[loc.address] = f"Stage {num}"
    #            if path != " ":
    #                stage_pos_data[loc.address] += path
    #    hint_data[self.player] = stage_pos_data

    def modify_multidata(self, multidata: typing.Dict[str, typing.Any]):
        # Put the player's unique authentication in connect_names.
        multidata["connect_names"][base64.b64encode(self.auth).decode("ascii")] = \
            multidata["connect_names"][self.multiworld.player_name[self.player]]

    #def write_spoiler(self, spoiler_handle: typing.TextIO) -> None:
        # Write the stage order to the spoiler log
    #    spoiler_handle.write(f"\nCastlevania 64 stage & warp orders for {self.multiworld.player_name[self.player]}:\n")
    #    for stage in self.active_stage_list:
    #        num = str(self.active_stage_exits[stage]["position"]).zfill(2)
    #        path = self.active_stage_exits[stage]["path"]
    #        spoiler_handle.writelines(f"Stage {num}{path}:\t{stage}\n")

        # Write the warp order to the spoiler log
    #    spoiler_handle.writelines(f"\nStart :\t{self.active_stage_list[0]}\n")
    #    for i in range(1, len(self.active_warp_list)):
    #        spoiler_handle.writelines(f"Warp {i}:\t{self.active_warp_list[i]}\n")
