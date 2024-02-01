import os
import typing
import base64
import threading
import settings

from BaseClasses import Item, Region, MultiWorld, Tutorial, ItemClassification
from .items import CVLoDItem, filler_item_names, get_item_info, get_item_names_to_ids, get_item_counts
from .locations import CVLoDLocation, get_location_info, verify_locations, get_location_names_to_ids, base_id
from .entrances import verify_entrances, get_warp_entrances, get_drac_rule
from .options import CVLoDOptions
from .stages import get_stage_info, get_locations_from_stage, get_normal_stage_exits, vanilla_stage_order, \
    shuffle_stages, generate_warps, get_region_names
from .regions import get_region_info
from .data import iname, lname, rname, ename
from ..AutoWorld import WebWorld, World
from .aesthetics import randomize_lighting, shuffle_sub_weapons, rom_empty_breakables_flags, randomize_music, \
    get_start_inventory_data, get_location_data, randomize_shop_prices, get_loading_zone_bytes, get_countdown_numbers
from .rom import LocalRom, patch_rom, get_base_rom_path, get_item_text_color, CVLoDDeltaPatch
from .client import CastlevaniaLoDClient


class CVLoDSettings(settings.Group):
    class RomFile(settings.UserFilePath):
        """File name of the CVLoD US rom"""
        copy_to = "Castlevania - Legacy of Darkness (USA).z64"
        description = "CVLoD (USA) ROM File"
        md5s = [CVLoDDeltaPatch.hash]

    rom_file: RomFile = RomFile(RomFile.copy_to)


class CVLoDWeb(WebWorld):
    theme = "stone"

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Castlevania: Legacy of Darkness randomizer connected to an Archipelago Multiworld.",
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
    game = "Castlevania Legacy of Darkness"
    item_name_groups = {
        "Bomb": {iname.nitro, iname.mandrag},
        "Ingredient": {iname.nitro, iname.mandrag},
        "Crest": {iname.crest_a, iname.crest_b},
    }
    location_name_groups = {stage: set(get_locations_from_stage(stage)) for stage in vanilla_stage_order}
    options_dataclass = CVLoDOptions
    options: CVLoDOptions
    settings: typing.ClassVar[CVLoDSettings]
    topology_present = True
    data_version = 0
    remote_items = False

    item_name_to_id = get_item_names_to_ids()
    location_name_to_id = get_location_names_to_ids()

    active_warp_list: typing.List[str]
    active_stage_list: typing.List[str]
    active_stage_exits: typing.Dict[str, typing.Dict]
    reinhardt_stages: bool = True
    carrie_stages: bool = True
    branching_stages: bool = False
    starting_stage: str

    total_s1s: int = 0
    s1s_per_warp: int = 0
    total_s2s: int = 0
    required_s2s: int = 0
    villa_fountain_order: typing.List[str] = ["O", "M", "H", "V"]
    web = CVLoDWeb()

    def __init__(self, world: MultiWorld, player: int):
        self.rom_name_available_event = threading.Event()
        super().__init__(world, player)

    @classmethod
    def stage_assert_generate(cls, world) -> None:
        rom_file = get_base_rom_path()
        if not os.path.exists(rom_file):
            raise FileNotFoundError(rom_file)

    def generate_early(self) -> None:
        self.random.shuffle(self.villa_fountain_order)

        # self.total_s1s = self.options.total_special1s.value
        # self.s1s_per_warp = self.options.special1s_per_warp.value
        # self.total_s2s = self.options.total_special2s.value
        # self.required_s2s = int(self.options.percent_special2s_required.value / 100 * self.total_s2s)

        # If there are more S1s needed to unlock the whole warp menu than there are S1s in total, drop S1s per warp to
        # something manageable.
        while self.s1s_per_warp * 7 > self.total_s1s:
            self.s1s_per_warp -= 1

        # Enable/disable character stages and branching paths accordingly
        #if self.options.character_stages.value == self.options.character_stages.option_reinhardt_only:
        #    self.carrie_stages = False
        #elif self.options.character_stages.value == self.options.character_stages.option_carrie_only:
        #    self.reinhardt_stages = False
        #elif self.options.character_stages.value == self.options.character_stages.option_both:
        #    self.branching_stages = True

        self.active_stage_exits = get_normal_stage_exits(self)

        stage_1_blacklist = []

        # Prevent Clock Tower from being Stage 1 if more than 4 S1s are needed to warp out of it.
        #if self.s1s_per_warp > 4 and not self.options.multi_hit_breakables.value:
        #    stage_1_blacklist.append(rname.clock_tower)

        # Shuffle the stages if the option is on.
        #if self.options.stage_shuffle:
        #    self.active_stage_exits, self.starting_stage, self.active_stage_list = \
        #        shuffle_stages(self, stage_1_blacklist, self.options.starting_stage.value, self.active_stage_exits)
        #else:
        #self.active_stage_list = [stage for stage in vanilla_stage_order if stage in self.active_stage_exits]
        #self.starting_stage = rname.castle_wall

        # Create a list of warps from the active stage list. They are in a random order by default and will never
        # include the starting stage.
        #self.active_warp_list = generate_warps(self, self.options, self.active_stage_list)

    def create_regions(self) -> None:
        # Create the Menu region.
        active_regions = {"Menu": Region("Menu", self.player, self.multiworld)}

        # Create every stage region by checking to see if that stage is active.
        active_regions.update({name: Region(name, self.player, self.multiworld) for name in
                               get_region_names(self.active_stage_exits)})

        # Add the Renon's shop region if shopsanity is on.
        #if self.options.shopsanity.value:
        #    active_regions.update({rname.renon: Region(rname.renon, self.player, self.multiworld)})

        # Add the Dracula's chamber (the end) region.
        # active_regions.update({rname.ck_drac_chamber: Region(rname.ck_drac_chamber, self.player, self.multiworld)})

        # Add the locations to the regions.
        for reg_name in active_regions:
            reg_locs = get_region_info(reg_name, "locations")
            if reg_locs is not None:
                active_regions[reg_name].add_locations(verify_locations(self.options, reg_locs), CVLoDLocation)

        # Set up the regions correctly
        for region in active_regions:
            self.multiworld.regions.append(active_regions[region])

    def create_item(self, name: str, force_classification=None) -> Item:
        if force_classification is not None:
            classification = getattr(ItemClassification, force_classification)
        else:
            classification = getattr(ItemClassification, get_item_info(name, "default class"))

        code = get_item_info(name, "code")
        if code is not None:
            code += base_id

        created_item = CVLoDItem(name, classification, code, self.player)

        return created_item

    def create_items(self) -> None:
        item_counts = get_item_counts(self, self.options, self.multiworld.get_unfilled_locations(self.player))

        # Set up the items correctly
        for classification in item_counts:
            for item in item_counts[classification]:
                self.multiworld.itempool += [self.create_item(item, classification)
                                             for _ in range(item_counts[classification][item])]

    def set_rules(self) -> None:
        active_regions = self.multiworld.get_regions(self.player)

        # Set the required Special2s to the number of available bosses or crystal events returned if Special2s
        # are not the goal.
        #if self.options.draculas_condition != self.options.draculas_condition.option_specials:
        #    self.total_s2s = 0
        #    self.required_s2s = 0

        for region in active_regions:
            # Place event items where they should be.
            for loc in region.locations:
                if loc.address is None:
                    event_item = get_location_info(loc.name, "event")
                    loc.place_locked_item(self.create_item(event_item, "progression"))
                    #if event_item != iname.victory:
                    #    self.total_s2s += 1
                    #    if self.required_s2s < self.options.bosses_required.value:
                    #        self.required_s2s += 1

            # Set up and connect the region's entrances.
            connections = {}
            rules = {}
            if region.name == "Menu":
                connections = {rname.cw_start}
                # connections, rules = get_warp_entrances(self.options, self.active_warp_list, self.player)
            else:
                entrance_names = get_region_info(region.name, "entrances")
                if entrance_names is not None:
                    connections, rules = verify_entrances(self.options, entrance_names, self.active_stage_exits,
                                                          self.player)
            if region.name == rname.ck_main:
                connections.update({rname.ck_drac_chamber: ename.ck_drac_door})
                drac_rule = get_drac_rule(self.options, self.player, self.required_s2s)
                if drac_rule is not None:
                    rules.update(drac_rule)
            region.add_exits(connections, rules)

        # Set the completion condition
        self.multiworld.completion_condition[self.player] = lambda state: state.has(iname.victory, self.player)

    def generate_output(self, output_directory: str) -> None:
        try:
            active_locations = self.multiworld.get_locations(self.player)

            # Location data and shop names, descriptions, and colors
            offset_data, shop_name_list, shop_colors_list, shop_desc_list = \
                get_location_data(self, self.options, active_locations)
            # Shop prices
            #if self.options.shop_prices.value:
            #    offset_data.update(randomize_shop_prices(self, self.options.minimum_gold_price.value,
            #                                             self.options.maximum_gold_price.value))
            # Map lighting
            #if self.options.map_lighting.value:
            #    offset_data.update(randomize_lighting(self))
            # Sub-weapons
            if self.options.sub_weapon_shuffle.value == self.options.sub_weapon_shuffle.option_own_pool:
                offset_data.update(shuffle_sub_weapons(self))
            # Empty breakables
            #if self.options.empty_breakables.value:
            #    offset_data.update(rom_empty_breakables_flags)
            # Music
            #if self.options.background_music.value:
            #    offset_data.update(randomize_music(self, self.options))
            # Loading zones
            #offset_data.update(get_loading_zone_bytes(self.options, self.starting_stage, self.active_stage_exits))
            # Countdown
            if self.options.countdown.value:
                offset_data.update(get_countdown_numbers(self.options, active_locations))
            # Start Inventory
            offset_data.update(get_start_inventory_data(self.options, self.options.start_inventory.value))

            cvlod_rom = LocalRom(get_base_rom_path())

            slot_name = self.multiworld.player_name[self.player].encode("utf-8")

            rompath = os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}.z64")

            patch_rom(self.multiworld, self.options, cvlod_rom, self.player, offset_data, self.active_stage_exits,
                      self.s1s_per_warp, [], self.required_s2s, self.total_s2s, [],
                      shop_desc_list, shop_colors_list, slot_name, active_locations, self.villa_fountain_order)

            cvlod_rom.write_to_file(rompath)

            patch = CVLoDDeltaPatch(os.path.splitext(rompath)[0] + CVLoDDeltaPatch.patch_file_ending, player=self.player,
                                   player_name=self.multiworld.player_name[self.player], patched_path=rompath)
            patch.write()
        except:
            print(f"D'oh, something went wrong in CVLoD's generate_output for player "
                  f"{self.multiworld.player_name[self.player]}!")
            raise
        finally:
            if os.path.exists(rompath):
                os.unlink(rompath)
            self.rom_name_available_event.set()  # make sure threading continues and errors are collected

    def write_spoiler(self, spoiler_handle: typing.TextIO) -> None:
        pass
        # Write the stage order to the spoiler log
        #spoiler_handle.write(f"\nCastlevania LoD stage & warp orders for {self.multiworld.player_name[self.player]}:\n")
        #for stage in self.active_stage_list:
        #    num = str(self.active_stage_exits[stage]["position"]).zfill(2)
        #    path = self.active_stage_exits[stage]["path"]
        #    spoiler_handle.writelines(f"Stage {num}{path}:\t{stage}\n")

        # Write the warp order to the spoiler log
        #spoiler_handle.writelines(f"\nStart :\t{self.active_stage_list[0]}\n")
        #for i in range(1, len(self.active_warp_list)):
        #    spoiler_handle.writelines(f"Warp {i}:\t{self.active_warp_list[i]}\n")

    #def fill_slot_data(self) -> typing.Dict[str, typing.Any]:
    #    pass
        # return {"death_link": self.options.death_link.value}

    def modify_multidata(self, multidata: dict):
        # wait for self.rom_name to be available.
        self.rom_name_available_event.wait()
        rom_name = getattr(self, "rom_name", None)
        # we skip in case of error, so that the original error in the output thread is the one that gets raised
        if rom_name:
            new_name = base64.b64encode(bytes(self.rom_name)).decode()
            multidata["connect_names"][new_name] = multidata["connect_names"][self.multiworld.player_name[self.player]]

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_item_names)

    def extend_hint_information(self, hint_data: typing.Dict[int, typing.Dict[int, str]]):
        pass
        # Attach each location's stage's position to its hint information if Stage Shuffle is on.
        #if self.options.stage_shuffle.value:
        #    stage_pos_data = {}
        #    for loc in self.multiworld.get_locations(self.player):
        #        stage = get_region_info(loc.parent_region.name, "stage")
        #        if stage is not None and loc.address is not None:
        #            num = str(self.active_stage_exits[stage]["position"]).zfill(2)
        #            path = self.active_stage_exits[stage]["path"]
        #            stage_pos_data[loc.address] = f"Stage {num}"
        #            if path != " ":
        #                stage_pos_data[loc.address] += path
        #    hint_data[self.player] = stage_pos_data