from typing import Dict, TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import CollectionRule
from .options import DraculasCondition, CastleWallState, VillaState
from .data import item_names, loc_names, ent_names, reg_names

if TYPE_CHECKING:
    from . import CVLoDWorld


class CVLoDRules:
    player: int
    world: "CVLoDWorld"
    rules: Dict[str, CollectionRule]
    s1s_per_warp: int
    required_s2s: int
    drac_condition: int
    required_bosses: int
    castle_wall_state: int
    villa_state: int

    def __init__(self, world: "CVLoDWorld") -> None:
        self.player = world.player
        self.world = world
        self.s1s_per_warp = world.options.special1s_per_warp.value
        self.required_s2s = world.required_s2s
        self.drac_condition = world.options.draculas_condition.value
        self.required_bosses = world.options.bosses_required.value
        self.castle_wall_state = world.options.castle_wall_state.value
        self.villa_state = world.options.villa_state.value

        self.location_rules = {
            loc_names.villafy_fountain_shine: self.villa_can_get_fountain_shine,
            loc_names.villala_vincent: self.villa_can_meet_rosa,
            loc_names.villala_mary: self.villa_can_rescue_maze_kid,
            loc_names.event_villa_child: self.villa_can_open_cornell_rose_door,
            loc_names.event_cc_crystal: self.cc_can_explode_lower_wall,
            loc_names.event_cc_elevator: self.cc_can_activate_crystal,
            loc_names.event_dracula: self.ck_can_enter_dracs_chamber
        }

        self.entrance_rules = {
            # Foggy Lake
            ent_names.fld_to_below: self.fl_can_open_deck_door,
            ent_names.flb_from_below:  self.fl_can_open_deck_door,
            # Castle Wall
            ent_names.cw_lt_door_b: self.cw_can_open_left_tower_door,
            ent_names.cw_portcullis_c: self.cw_can_pass_middle_portcullis,
            ent_names.cw_end: self.cw_can_pass_end_portcullis,
            # Villa
            ent_names.villafy_fountain_pillar: self.villa_can_get_on_fountain,
            ent_names.villafo_to_rose_garden: self.villa_can_open_cornell_rose_door,
            ent_names.villafo_from_rose_garden: self.villa_can_open_cornell_rose_door,
            ent_names.villala_to_storeroom: self.villa_can_open_storeroom_door,
            ent_names.villala_from_storeroom: self.villa_can_open_storeroom_door,
            ent_names.villala_archives: self.villa_can_open_archives_door,
            ent_names.villam_to_main_maze_gate: self.villa_can_open_maze_main_gate,
            ent_names.villam_from_main_maze_gate: self.villa_can_open_maze_main_gate,
            ent_names.villam_copper_door: self.villa_can_open_copper_door,
            ent_names.villam_front_divide: self.villa_can_open_cornell_rose_door,
            ent_names.villam_to_servant_gate: self.villa_can_open_maze_side_gate,
            ent_names.villam_from_servant_gate: self.villa_can_open_maze_side_gate,
            ent_names.villam_thorn_fence: self.villa_can_open_thorn_fence,
            ent_names.villam_crypt_door: self.villa_can_open_crest_door,
            # The Outer Wall
            ent_names.towse_pillar: self.tow_can_press_slaughterhouse_button,
            ent_names.towse_to_wall_door: self.tow_can_open_wall_door,
            ent_names.towse_from_wall_door: self.tow_can_open_wall_door,
            # Art Tower
            ent_names.atm_to_door_1: self.at_can_open_door_1,
            ent_names.atm_from_door_1: self.at_can_open_door_1,
            ent_names.atm_to_door_2: self.at_can_open_door_2,
            ent_names.atm_from_door_2: self.at_can_open_door_2,
            # Castle Center
            ent_names.ccb_tc_to_door: self.cc_can_open_chamber_door,
            ent_names.ccb_tc_from_door: self.cc_can_open_chamber_door,
            ent_names.ccll_upper_wall_in: self.cc_can_explode_upper_wall,
            ent_names.ccll_upper_wall_out: self.cc_can_explode_upper_wall,
            ent_names.ccbe_elevator: self.cc_can_activate_elevator,
            ent_names.ccte_elevator: self.cc_can_activate_elevator,
            # Tower of Science
            ent_names.toscit_to_ctrl_door: self.tosci_can_open_ctrl_room_door,
            ent_names.toscit_from_ctrl_door: self.tosci_can_open_ctrl_room_door,
            # Clock Tower
            ent_names.ctgc_to_door_a: self.ct_can_open_door_a,
            ent_names.ctgc_from_door_a: self.ct_can_open_door_a,
            ent_names.ctgc_to_door_b: self.ct_can_open_door_b,
            ent_names.ctgc_from_door_b: self.ct_can_open_door_b,
            ent_names.ctga_door_c: self.ct_can_open_door_c,
            ent_names.ctga_door_d: self.ct_can_open_door_d,
            ent_names.ctf_door_d: self.ct_can_open_door_d,
            ent_names.ctf_door_e: self.ct_can_open_door_e,
            ent_names.ctf_end: self.ct_can_open_door_e,
        }

    def fl_can_open_deck_door(self, state: CollectionState) -> bool:
        """Deck Key."""
        return state.has(item_names.quest_key_deck, self.player)

    def cw_can_open_left_tower_door(self, state: CollectionState) -> bool:
        """Always True if the Castle Wall state is Cornell's. Requires Left Tower Key if Reinhardt/Carrie or Hybrid."""
        if self.castle_wall_state == CastleWallState.option_cornell:
            return True
        return state.has(item_names.quest_key_left, self.player)

    def cw_can_pass_middle_portcullis(self, state: CollectionState) -> bool:
        """Right Tower top access if the Castle Wall state is Reinhardt/Carrie. Left Tower top access if Cornell or Hybrid."""
        if self.castle_wall_state == CastleWallState.option_reinhardt_carrie:
            return state.has(item_names.event_cw_right, self.player)
        return state.has(item_names.event_cw_left, self.player)

    def cw_can_pass_end_portcullis(self, state: CollectionState) -> bool:
        """Left Tower top access if the Castle Wall state is Reinhardt/Carrie. Both tower tops access AND Winch Lever if Cornell or Hybrid."""
        if self.castle_wall_state == CastleWallState.option_reinhardt_carrie:
            return state.has(item_names.event_cw_left, self.player)
        return state.has_all([item_names.event_cw_left, item_names.event_cw_right, item_names.quest_winch], self.player)

    def villa_can_get_on_fountain(self, state: CollectionState) -> bool:
        """Oldrey's Diary if the fountain puzzle is on, or always True."""
        return state.has(item_names.quest_diary, self.player)

    def villa_can_get_fountain_shine(self, state: CollectionState) -> bool:
        """Rose Brooch."""
        return state.has(item_names.quest_brooch, self.player)

    def villa_can_open_cornell_rose_door(self, state: CollectionState) -> bool:
        """Rose Garden Key if the Villa state is Cornell's or Hybrid. Always True if Reinhardt/Carrie."""
        if self.villa_state == VillaState.option_reinhardt_carrie:
            return True
        return state.has(item_names.quest_key_rose, self.player)

    def villa_can_meet_rosa(self, state: CollectionState) -> bool:
        """Able to meet Rosa at the Villa's rose garden at 3-6am."""
        return state.has(item_names.event_villa_rosa, self.player)

    def villa_can_rescue_maze_kid(self, state: CollectionState) -> bool:
        """Able to do the entire Malus chase/child Henry escort start-to-finish."""
        return state.has(item_names.event_villa_child, self.player)

    def villa_can_open_storeroom_door(self, state: CollectionState) -> bool:
        """Storeroom Key."""
        return state.has(item_names.quest_key_store, self.player)

    def villa_can_open_archives_door(self, state: CollectionState) -> bool:
        """Archives Key."""
        return state.has(item_names.quest_key_arch, self.player)

    def villa_can_open_maze_main_gate(self, state: CollectionState) -> bool:
        """Garden Key."""
        return state.has(item_names.quest_key_grdn, self.player)

    def villa_can_open_maze_side_gate(self, state: CollectionState) -> bool:
        """Garden Key if the Villa State is Reinhardt/Carrie's or Hybrid. Always True if Cornell."""
        if self.villa_state == VillaState.option_cornell:
            return True
        return state.has(item_names.quest_key_grdn, self.player)

    def villa_can_open_thorn_fence(self, state: CollectionState) -> bool:
        """Thorn Key if the Villa State is Cornell's or Hybrid. Always True if Reinhardt/Carrie."""
        if self.villa_state == VillaState.option_reinhardt_carrie:
            return True
        return state.has(item_names.quest_key_arch, self.player)

    def villa_can_open_copper_door(self, state: CollectionState) -> bool:
        """Copper Key."""
        return state.has(item_names.quest_key_cppr, self.player)

    def villa_can_open_crest_door(self, state: CollectionState) -> bool:
        """Crest Half A and B if the Villa State is Cornell's or Hybrid. Always True if Reinhardt/Carrie."""
        if self.villa_state == VillaState.option_reinhardt_carrie:
            return True
        return state.has_all([item_names.quest_crest_a, item_names.quest_crest_b], self.player)

    def tow_can_press_slaughterhouse_button(self, state: CollectionState) -> bool:
        """Able to press the button in the Outer Wall's slaughterhouse."""
        return state.has(item_names.event_tow_switch, self.player)

    def tow_can_open_wall_door(self, state: CollectionState) -> bool:
        """Wall Key."""
        return state.has(item_names.quest_key_wall, self.player)

    def at_can_open_door_1(self, state: CollectionState) -> bool:
        """Art Tower Key 1."""
        return state.has(item_names.quest_key_art_1, self.player)

    def at_can_open_door_2(self, state: CollectionState) -> bool:
        """Art Tower Key 2."""
        return state.has(item_names.quest_key_art_2, self.player)

    def cc_can_open_chamber_door(self, state: CollectionState) -> bool:
        """Chamber Key."""
        return state.has(item_names.quest_key_chbr, self.player)

    def cc_can_explode_upper_wall(self, state: CollectionState) -> bool:
        """One Nitro/Mandragora pair."""
        return state.has_all([item_names.quest_nitro, item_names.quest_mandragora], self.player)

    def cc_can_explode_lower_wall(self, state: CollectionState) -> bool:
        """Two Nitro/Mandragora pairs and access to the Castle Center planetarium puzzle."""
        return state.has_all_counts({item_names.quest_nitro: 2, item_names.quest_mandragora: 2,
                                     item_names.event_cc_planets: 1}, self.player)

    def cc_can_solve_library_puzzle(self, state: CollectionState) -> bool:
        """Solved the planetarium puzzle in Castle Center's library."""
        return state.has(item_names.event_cc_planets, self.player)

    def cc_can_activate_crystal(self, state: CollectionState) -> bool:
        """Activated the big Crystal behind the lower Castle Center cracked wall."""
        return state.has(item_names.event_cc_crystal, self.player)

    def cc_can_activate_elevator(self, state: CollectionState) -> bool:
        """Activated the Castle Center elevator."""
        return state.has(item_names.event_cc_elevator, self.player)

    def tosci_can_open_ctrl_room_door(self, state: CollectionState) -> bool:
        """Control Room Key."""
        return state.has(item_names.quest_key_ctrl, self.player)

    def ct_can_open_door_a(self, state: CollectionState) -> bool:
        """Clocktower Key A."""
        return state.has(item_names.quest_key_clock_a, self.player)

    def ct_can_open_door_b(self, state: CollectionState) -> bool:
        """Clocktower Key B."""
        return state.has(item_names.quest_key_clock_b, self.player)

    def ct_can_open_door_c(self, state: CollectionState) -> bool:
        """Clocktower Key C."""
        return state.has(item_names.quest_key_clock_c, self.player)

    def ct_can_open_door_d(self, state: CollectionState) -> bool:
        """Clocktower Key D."""
        return state.has(item_names.quest_key_clock_d, self.player)

    def ct_can_open_door_e(self, state: CollectionState) -> bool:
        """Clocktower Key E."""
        return state.has(item_names.quest_key_clock_e, self.player)

    def ck_can_enter_dracs_chamber(self, state: CollectionState) -> bool:
        """Completed the necessary objective to fulfill Dracula's Condition. Always True if no condition is set."""
        if self.drac_condition == DraculasCondition.option_crystal:
            return state.has(item_names.event_cc_crystal, self.player)
        elif self.drac_condition == DraculasCondition.option_bosses:
            return state.has(item_names.event_trophy, self.player, self.required_bosses)
        elif self.drac_condition == DraculasCondition.option_specials:
            return state.has(item_names.special2, self.player, self.required_s2s)
        return True

    def set_cvlod_rules(self) -> None:
        # Set each Entrance's rule if it should have one.
        for ent in self.world.get_entrances():
            # If it's a warp menu Entrance, set it to require the slot's Special1s Per Warp times its warp number.
            if ent.parent_region.name == reg_names.menu and ent.name.startswith("Warp "):
                ent.access_rule = lambda state, warp_num=int(ent.name[5:]): \
                    state.has(item_names.special1, self.player, self.s1s_per_warp * warp_num)
            if ent.name in self.entrance_rules:
                ent.access_rule = self.entrance_rules[ent.name]

        # Set each Location's rule if it should have one.
        for loc in self.world.get_locations():
            if loc.name in self.location_rules:
                loc.access_rule = self.location_rules[loc.name]

        # Set the world's completion condition.
        self.world.multiworld.completion_condition[self.player] = \
            lambda state: state.has(item_names.event_dracula, self.player)
