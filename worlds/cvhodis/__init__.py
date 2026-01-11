import os
import typing
import settings
import base64
import logging

from BaseClasses import Tutorial, ItemClassification, EntranceType
from entrance_rando import disconnect_entrance_for_randomization, randomize_entrances
from .items import CVHoDisItem, FILLER_ITEM_NAMES, ALL_CVHODIS_ITEMS, FURNITURE, get_item_names_to_ids, \
    get_item_counts, get_pickup_type
from .locations import CVHoDisLocation, get_location_names_to_ids, BASE_ID, get_locations_to_create, \
    get_location_name_groups
from .options import cvhodis_option_groups, CVHoDisOptions, SubWeaponShuffle, TransitionShuffler, CastleSwapper, \
    AreaDivisions
from .regions import get_all_region_names, CVHoDisRegion, ALL_CVHODIS_REGIONS
from .entrances import SHUFFLEABLE_TRANSITIONS, ERGroups, TARGET_GROUP_RELATIONSHIPS, cvhodis_on_connect, \
    link_room_transitions, SORTED_TRANSITIONS, SKULL_DOOR_GROUPS, MK_DOOR_GROUPS, CVHoDisEntrance, \
    invert_castle_transitions, verify_entrances, MAIN_SUB_AREAS, get_er_group
from .rules import CVHoDisRules
from .data import item_names, loc_names
from worlds.AutoWorld import WebWorld, World

from .aesthetics import shuffle_sub_weapons, get_location_data, get_countdown_flags, get_start_inventory_data, \
    get_hint_card_hints
from .rom import RomData, patch_rom, get_base_rom_path, CVHoDisProcedurePatch, CVHODIS_CT_US_HASH, CVHODIS_AC_US_HASH
from .client import CastlevaniaHoDisClient


class CVHoDisSettings(settings.Group):
    class RomFile(settings.UserFilePath):
        """File name of the Castlevania HoD US rom"""
        copy_to = "Castlevania - Harmony of Dissonance (USA).gba"
        description = "Castlevania HoD (US) ROM File"
        md5s = [CVHODIS_CT_US_HASH, CVHODIS_AC_US_HASH]

    rom_file: RomFile = RomFile(RomFile.copy_to)


class CVHoDisWeb(WebWorld):
    theme = "stone"
    # options_presets = cvhodis_options_presets

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Archipleago Castlevania: Harmony of Dissonance randomizer on your computer and "
        "connecting it to a multiworld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Liquid Cat"]
    )]

    option_groups = cvhodis_option_groups


class CVHoDisWorld(World):
    """
    Castlevania: Harmony of Dissonance is the second Metroidvania-style Castlevania released for the Game Boy Advance.
    After childhood friend Lydie is kidnapped away to a mysterious castle not on any map, Juste Belmont travels to
    this new place with his best friend Maxim at his side. The two split up to search for Lydie, but it soon becomes
    clear that Maxim is not his normal self... Wield powerful sub-weapon spell fusions as Juste as you hunt for
    Dracula's remains and unravel the conspiracy between two parallel castles.
    """
    game = "Castlevania - Harmony of Dissonance"
    topology_present = True
    item_name_groups = {
        "Furniture": {name for name in FURNITURE},
        "Vlad": {item_names.relic_v_nail, item_names.relic_v_eye, item_names.relic_v_fang, item_names.relic_v_heart,
                 item_names.relic_v_rib, item_names.relic_v_ring},
    }
    location_name_groups = get_location_name_groups()
    options_dataclass = CVHoDisOptions
    options: CVHoDisOptions
    settings: typing.ClassVar[CVHoDisSettings]
    origin_region_name = "Entrance A Main"

    item_name_to_id = get_item_names_to_ids()
    location_name_to_id = get_location_names_to_ids()

    possible_hint_card_items: list[CVHoDisItem]
    transition_pairings: list[tuple]
    inverted_groups: dict[str, bool]
    inverted_transitions: dict[str, bool]

    # Default values to possibly be updated in generate_early
    furniture_amount_required: int = 0
    # map_percentage_required: int = 0

    auth: bytearray

    web = CVHoDisWeb()

    def generate_early(self) -> None:
        self.possible_hint_card_items = []
        self.transition_pairings = []
        self.inverted_transitions, self.inverted_groups = invert_castle_transitions(self)

        # Generate the player's unique authentication
        self.auth = bytearray(self.random.getrandbits(8) for _ in range(16))

        self.furniture_amount_required = self.options.furniture_amount_required.value

        # If the player has no goal requirements enabled at all, throw a warning and enable the Best Ending requirement.
        if not self.furniture_amount_required and not self.options.best_ending_required and not \
                self.options.worst_ending_required and not self.options.medium_ending_required:
            logging.warning(f"{self.player_name} has no goal requirements enabled. The Best Ending requirement will be "
                            f"enabled for them.")
            self.options.best_ending_required.value = True

        # Place the Lizard Tail in early_items if the Early Lizard option is enabled.
        if self.options.early_lizard:
            self.multiworld.early_items[self.player][item_names.relic_tail] = 1

    def create_regions(self) -> None:
        # Create every Region object.
        created_regions = [CVHoDisRegion(name, self.player, self.multiworld) for name in get_all_region_names()]

        # Attach the Regions to the Multiworld.
        self.multiworld.regions.extend(created_regions)

        # Loop over every Region and create and add its Locations and Entrances.
        for reg in created_regions:

            # Add the Entrances to the Region (if it has any).
            if ALL_CVHODIS_REGIONS[reg.name]["entrances"]:
                created_entrances = reg.add_exits(verify_entrances(ALL_CVHODIS_REGIONS[reg.name]["entrances"],
                                                                   self.inverted_transitions))

                # If Transition Shuffler is on, disconnect all the created randomizable Entrances in the Region to
                # prepare it for Entrance Randomizer.
                if self.options.transition_shuffler:
                    for ent in created_entrances:
                        if ent.name in SHUFFLEABLE_TRANSITIONS:
                            # If we're looking at a non-door transition and Area Divisions is set to Doors Only, do not
                            # randomize it.
                            if not SHUFFLEABLE_TRANSITIONS[ent.name].is_door and \
                                    self.options.area_divisions.value == AreaDivisions.option_doors_only:
                                continue
                            ent.randomization_type = EntranceType.TWO_WAY
                            ent.randomization_group = get_er_group(ent.name, self.options, self.inverted_groups)
                            # If Castle Swapper is in Transitions mode, collapse all Castle B groups
                            # (all even-numbered ones) into their corresponding Castle A groups instead
                            # to make both castles randomize together.
                            if self.options.castle_swapper == CastleSwapper.option_transitions and \
                                    not ent.randomization_group % 2:
                                ent.randomization_group -= 1
                            # If Link Door Types is not on, collapse all special door type groups (MK and Skull) into
                            # their corresponding normal door direction type to randomize them together.
                            if not self.options.link_door_types:
                                if ent.randomization_group in SKULL_DOOR_GROUPS:
                                    ent.randomization_group -= 2
                                elif ent.randomization_group in MK_DOOR_GROUPS:
                                    ent.randomization_group -= 4
                            disconnect_entrance_for_randomization(ent)

            # Add the Locations to each Region (if it has any).
            reg_loc_names = ALL_CVHODIS_REGIONS[reg.name]["locations"]
            if reg_loc_names is None:
                continue
            locations_with_ids, locked_pairs = get_locations_to_create(reg_loc_names, self.options)
            reg.add_locations(locations_with_ids, CVHoDisLocation)

            # Place locked Items on all of their associated Locations (if any Locations have any).
            for locked_loc, locked_item in locked_pairs.items():
                self.get_location(locked_loc).place_locked_item(self.create_item(locked_item,
                                                                                 ItemClassification.progression))

    def create_item(self, name: str, force_classification: typing.Optional[ItemClassification] = None) -> CVHoDisItem:
        if force_classification is not None:
            classification = force_classification
        else:
            classification = ALL_CVHODIS_ITEMS[name].default_classification

        if name in ALL_CVHODIS_ITEMS:
            code = ALL_CVHODIS_ITEMS[name].pickup_index + (get_pickup_type(name) << 8) + BASE_ID
        else:
            code = None

        created_item = CVHoDisItem(name, classification, code, self.player)

        return created_item

    def create_items(self) -> None:
        item_counts = get_item_counts(self)

        # Set up the Items correctly.
        own_itempool = [self.create_item(item, classification) for classification in item_counts for item
                        in item_counts[classification] for _ in range(item_counts[classification][item])]

        # Save the created progression Items that are not furniture for the later possibility of being the subject of a
        # Hint Card hint.
        self.possible_hint_card_items = [item for item in own_itempool if item.advancement and item.name not in
                                         FURNITURE]

        # Submit the created Items to the multiworld's itempool.
        self.multiworld.itempool += own_itempool

    def set_rules(self) -> None:
        # Set all the Entrance and Location rules properly.
        CVHoDisRules(self).set_cvhodis_rules()

    def connect_entrances(self) -> None:
        # If Transition Shuffler is on, randomize the Entrances and save the result's transition entrance pairings.
        if self.options.transition_shuffler:
            result = randomize_entrances(self, coupled=not self.options.transition_shuffler.value == \
                                                           TransitionShuffler.option_decoupled,
                                         target_group_lookup=TARGET_GROUP_RELATIONSHIPS,
                                         on_connect=cvhodis_on_connect)
            self.transition_pairings = sorted(result.pairings,
                                              key=lambda transition: SORTED_TRANSITIONS.index(transition[0]))
        # If Transition Shuffler was off but Castle Swapper is on, manually create the slot's list of transition
        # pairings based on which transition Entrances are inverted and save that.
        elif self.options.castle_swapper:
            for transition_name, inverted in self.inverted_transitions.items():
                ent = self.get_entrance(transition_name)
                # Skip the transition if it's not a door and Area Divisions is Doors Only.
                if not SHUFFLEABLE_TRANSITIONS[ent.name].is_door and \
                        self.options.area_divisions == AreaDivisions.option_doors_only:
                    continue
                # If the transition is inverted, pair it with its other castle transition's destination transition.
                if inverted:
                    self.transition_pairings += [(ent.name, SHUFFLEABLE_TRANSITIONS[
                        SHUFFLEABLE_TRANSITIONS[ent.name].other_castle_transition].destination_transition)]
                # Otherwise, pair it with its own.
                else:
                    self.transition_pairings += [(ent.name, SHUFFLEABLE_TRANSITIONS[ent.name].destination_transition)]

    def generate_output(self, output_directory: str) -> None:
        # Get out all the Locations that are not Events.
        active_locations = [loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None]

        # Location data
        offset_data = get_location_data(self, active_locations)
        # Hint Card hints
        offset_data.update(get_hint_card_hints(self, active_locations))
        # Transition data
        if self.transition_pairings:
            offset_data.update(link_room_transitions(self.transition_pairings))
        # Sub-weapons
        # if self.options.sub_weapon_shuffle:
        #     offset_data.update(shuffle_sub_weapons(self))
        # Item drop randomization
        # if self.options.item_drop_randomization:
        #     offset_data.update(populate_enemy_drops(self))
        # Countdown
        # if self.options.countdown:
        #     offset_data.update(get_countdown_flags(self, active_locations))
        # Start Inventory
        offset_data.update(get_start_inventory_data(self))

        patch = CVHoDisProcedurePatch(player=self.player, player_name=self.player_name)
        patch_rom(self, patch, offset_data)

        rom_path = os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}"
                                f"{patch.patch_file_ending}")

        patch.write(rom_path)

    def fill_slot_data(self) -> dict:
        return {"death_link": self.options.death_link.value,
                "medium_ending_required": self.options.medium_ending_required.value,
                "worst_ending_required": self.options.worst_ending_required.value,
                "best_ending_required": self.options.best_ending_required.value,
                "furniture_amount_required": self.furniture_amount_required,
                "spellbound_boss_logic": self.options.spellbound_boss_logic.value,
                "area_divisions": self.options.area_divisions.value,
                "castle_swapper": self.options.castle_swapper.value,
                "transition_shuffler": self.options.transition_shuffler.value,
                "castle_symmetry": self.options.castle_symmetry.value,
                "link_door_types": self.options.link_door_types.value,
                "castle_warp_condition": self.options.castle_warp_condition.value,
                "transition_pairings": self.transition_pairings}

    def get_filler_item_name(self) -> str:
        return self.random.choice(FILLER_ITEM_NAMES)

    def modify_multidata(self, multidata: typing.Dict[str, typing.Any]):
        # Put the player's unique authentication in connect_names.
        multidata["connect_names"][base64.b64encode(self.auth).decode("ascii")] = \
            multidata["connect_names"][self.player_name]

    def write_spoiler_header(self, spoiler_handle: typing.TextIO) -> None:
        # If we have transition pairings, meaning transition Shuffler or Area Swapper is enabled, write all randomized
        # transitions to the spoiler.
        if not self.transition_pairings:
            return

        spoiler = self.multiworld.spoiler

        # If Castle Swapper is enabled, and not set to Transitions while Transition Shuffle is on, write which Areas or
        # Transitions in the game were swapped to the spoiler.
        if self.options.castle_swapper and (self.options.castle_swapper.value != CastleSwapper.option_transitions or
                                            not self.options.transition_shuffler):
            spoiler_handle.write(
                f"\n{self.player_name}'s Castle Swapper "
                f"{'areas' if self.options.castle_swapper.value == CastleSwapper.option_areas else 'transitions'}:\n"
            )
            # Loop over each Area and write it.
            for area_name, inverted in self.inverted_groups.items():
                # If Area Divisions are set to Doors Only, and the Area has an associated sub-Area that we are counting
                # as the same Area as it, add it to the full name to write in the spoiler.
                full_area_name = area_name
                if self.options.area_divisions.value == AreaDivisions.option_doors_only and area_name in MAIN_SUB_AREAS:
                    full_area_name += f"/{MAIN_SUB_AREAS[area_name]}"

                spoiler_handle.writelines(f"{full_area_name}: {'Swapped' if inverted else 'Normal'}\n")

        for pair in self.transition_pairings:
            # If transitions are coupled, and we already wrote one direction, skip writing the other one.
            if self.options.transition_shuffler.value != TransitionShuffler.option_decoupled and \
                    (pair[1], "both", self.player) in spoiler.entrances:
                continue
            spoiler.set_entrance(
                pair[0],
                pair[1],
                "both" if self.options.transition_shuffler.value != TransitionShuffler.option_decoupled else "",
                self.player
            )
