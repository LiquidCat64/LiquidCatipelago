from typing import Dict, TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import CollectionRule
from .data import item_names, loc_names
from .items import FURNITURE

if TYPE_CHECKING:
    from . import CVHoDisWorld


class CVHoDisRules:
    player: int
    world: "CVHoDisWorld"
    rules: Dict[str, CollectionRule]
    required_furniture: int
    medium_ending_required: int
    worst_ending_required: int
    best_ending_required: int

    def __init__(self, world: "CVHoDisWorld") -> None:
        self.player = world.player
        self.world = world
        self.furniture_amount_required = world.furniture_amount_required
        self.medium_ending_required = world.options.medium_ending_required.value
        self.worst_ending_required = world.options.worst_ending_required.value
        self.best_ending_required = world.options.best_ending_required.value

        self.location_rules = {
            # Entrance A
            loc_names.eta2: self.can_break_ceilings,
            loc_names.eta3: self.can_break_ceilings,
            loc_names.eta9: self.can_super_jump,
            loc_names.eta18: self.can_super_jump,
            loc_names.eta17: self.can_open_lure_doors,
            # Marble Corridor A
            loc_names.mca9a: self.can_slide,
            loc_names.mca9b: self.can_slide,
            loc_names.mca11b: self.can_double_jump,
            loc_names.mca11e: self.can_double_jump,
            # The Wailing Way A
            loc_names.wwa0c: self.can_double_jump,
            loc_names.wwa4a: self.can_double_jump,
            loc_names.wwa4b: self.can_double_jump,
            # Shrine of the Apostates A
            loc_names.saa16: self.can_slide,
            loc_names.saa6b: self.can_slide,
            loc_names.saa6a: self.can_slide,
            loc_names.saa7: self.can_slide,
            # Room of Illusion A
            loc_names.ria17: self.can_slide,
            # Castle Treasury A
            loc_names.cya4: self.can_open_lure_doors,
            loc_names.cya20a: self.can_open_lure_doors,
            loc_names.cya20b: self.can_open_lure_doors,
            loc_names.event_ending_m: self.can_open_center_a_gate,
            # Skeleton Cave A
            loc_names.sca2: self.can_double_jump,
            loc_names.sca4: self.can_double_jump,
            loc_names.sca12a: self.can_super_jump,
            loc_names.sca12b: self.can_super_jump,
            # Luminous Cavern A
            loc_names.lca11: self.can_break_walls,
            loc_names.lca8a: self.can_super_jump,
            loc_names.lca10: self.can_super_jump,
            # Sky Walkway A
            loc_names.swa7: self.can_pass_sky_a_wall,
            loc_names.swa12a: self.can_double_jump,
            loc_names.swa12b: self.can_double_jump,
            loc_names.swa14: self.can_double_jump,
            loc_names.swa10a: self.can_double_jump,
            loc_names.swa15a: self.can_break_walls,
            loc_names.swa15b: self.can_break_walls,
            loc_names.swa18a: self.can_slide,
            loc_names.swa18b: self.can_slide,
            # Chapel of Dissonance A
            loc_names.cda0e: self.can_double_jump,
            loc_names.cda0a: self.can_double_jump,
            loc_names.cda0b: self.can_double_jump,
            loc_names.cda0d: self.can_super_jump,
            # Top Floor A
            loc_names.tfa1b: self.can_double_jump,
            loc_names.tfa1a: self.can_double_jump,
            # Entrance B
            loc_names.etb2b: self.can_break_ceilings,
            loc_names.etb2a: self.can_break_ceilings,
            loc_names.etb3: self.can_break_ceilings,
            loc_names.etb9: self.can_super_jump,
            # Marble Corridor B
            loc_names.mcb9: self.can_slide,
            loc_names.mcb11: self.can_double_jump,
            # The Wailing Way B
            loc_names.wwb0b: self.can_double_jump,
            loc_names.wwb4a: self.can_super_jump,
            loc_names.wwb4b: self.can_super_jump,
            # Shrine of the Apostates B
            loc_names.sab5: self.can_slide,
            loc_names.sab7: self.can_slide,
            # Treasury B
            loc_names.cyb20: self.can_open_lure_doors,
            loc_names.event_ending_b: self.can_open_center_b_gate,
            loc_names.event_ending_g: self.can_free_maxim,
            # Skeleton Cave B
            loc_names.scb3: self.can_pass_skeleton_b_wall,
            loc_names.scb2: self.can_double_jump,
            loc_names.scb12a: self.can_super_jump,
            loc_names.scb12b: self.can_super_jump,
            loc_names.scb11: self.can_double_jump,
            # Luminous Cavern B
            loc_names.lcb8b: self.can_super_jump,
            loc_names.lcb8a: self.can_super_jump,
            # Sky Walkway B
            loc_names.swb8: self.can_break_walls,
            loc_names.swb12a: self.can_double_jump,
            loc_names.swb12b: self.can_double_jump,
            loc_names.swb14: self.can_double_jump,
            loc_names.swb16: self.can_double_jump,
            loc_names.swb15: self.can_break_walls,
            # Chapel of Dissonance B
            loc_names.cdb0e: self.can_double_jump,
            loc_names.cdb0b: self.can_double_jump,
            loc_names.cdb0d: self.can_double_jump,
            loc_names.cdb0a: self.can_double_jump,
            loc_names.cdb0c: self.can_super_jump,
            # Clock Tower B
            loc_names.crb10: self.can_pass_under_crank,

            # The Empty Room
            loc_names.event_furniture: self.can_place_required_furniture
        }

        self.entrance_rules = {
            # Castle A
            "Entrance A Upper Warp Gate": lambda state:
                self.can_super_jump(state) and self.can_warp_castles(state),
            "Entrance A Upper Crush Wall Left": lambda state:
                self.can_break_walls(state) and self.can_super_jump(state),
            "Entrance A Lower Warp Gate": lambda state:
                self.can_open_lure_doors(state) and self.can_warp_castles(state),
            "Entrance A Upper Crush Wall Right": lambda state:
                self.can_break_walls(state) and self.can_super_jump(state),
            "Entrance A Lower Crush Wall Right": self.can_break_walls,
            "Entrance A Lower Crush Wall Left": self.can_break_walls,
            "Corridor A Right Skull Door": self.can_open_skull_doors,
            "Room A Slide Space Right": self.can_slide,
            "Room A Slide Space Left": self.can_slide,
            "Wailing A Right Skull Door": self.can_open_skull_doors,
            "Treasury A Warp Gates":  lambda state:
                self.can_open_lure_doors(state) and self.can_warp_castles(state),
            "Treasury A Double Jumps": self.can_double_jump,
            "Treasury A Top Skull Door": self.can_open_skull_doors,
            "Treasury A Top Ceiling Transition": self.can_double_jump,
            "Skeleton A Crate Rooms from Right": self.can_double_jump,
            "Skeleton A Crate Rooms from Left": self.can_double_jump,
            "Luminous A Warp Gate":  lambda state:
                self.can_break_walls(state) and self.can_warp_castles(state),
            "Luminous A Floodgate Keyhole": self.can_open_floodgate,
            "Luminous A Top Super Jump from Left": self.can_super_jump,
            "Luminous A Top Super Jump from Right": self.can_super_jump,
            "Walkway A Double Jump from Portal Hall": self.can_double_jump,
            "Walkway A Double Jump from Clock Exit": self.can_double_jump,
            "Walkway A Main Downward": self.can_see_in_darkness,
            "Walkway A Press Onwards in Darkness": self.can_see_in_darkness,
            "Chapel A Upward Hall Climb": self.can_double_jump,
            "Chapel A Top MK Door": self.can_open_mk_doors,
            "Aqueduct A Main Left Double Jump": self.can_double_jump,
            "Aqueduct A Crush Wall Right": self.can_break_walls,
            "Aqueduct A Main Right Double Jump": self.can_double_jump,
            "Aqueduct A Crush Wall Left": lambda state: self.can_break_walls(state) and self.can_double_jump(state),
            "Clock A Double Jump from Bottom": self.can_double_jump,
            "Clock A Double Jumps from Pendulum Area": self.can_double_jump,
            "Clock A Slide Space": lambda state: self.can_pass_clock_a_wall(state) and self.can_slide(state),
            "Clock A Warp Gate": self.can_warp_castles,
            "Top A Top MK Door": self.can_open_mk_doors,
            "Top A Crush Wall Right": self.can_break_walls,
            "Top A Crush Blocks": self.can_break_ceilings,
            "Top A Crush Wall Left": self.can_break_walls,
            "Top A Warp Gate": self.can_warp_castles,
            "Top A Lower Super Jump from Right": self.can_super_jump,
            "Top A Bottom Skull Door": self.can_open_skull_doors,
            "Top A Lower Super Jump from Left": self.can_super_jump,

            # Castle B
            "Entrance B Upper Warp Gate": lambda state:
                self.can_super_jump(state) and self.can_warp_castles(state),
            "Entrance B Upper Crush Wall Left": lambda state:
                self.can_break_walls(state) and self.can_super_jump(state),
            "Entrance B Lower Warp Gate": lambda state:
                self.can_open_lure_doors(state) and self.can_warp_castles(state),
            "Entrance B Upper Crush Wall Right": lambda state:
                self.can_break_walls(state) and self.can_super_jump(state),
            "Entrance B Lower Crush Wall Right": self.can_break_walls,
            "Entrance B Lower Crush Wall Left": self.can_break_walls,
            "Corridor B Right Skull Door": self.can_open_skull_doors,
            "Wailing B Right Skull Door": self.can_open_skull_doors,
            "Treasury B Warp Gates": lambda state:
                self.can_open_lure_doors(state) and self.can_warp_castles(state),
            "Treasury B Double Jumps": self.can_double_jump,
            "Treasury B Top Skull Door": self.can_open_skull_doors,
            "Treasury B Top Ceiling Transition": self.can_double_jump,
            "Skeleton B Right Collapsing Rock": self.can_double_jump,
            "Luminous B Top Super Jump from Left": self.can_super_jump,
            "Luminous B Top Super Jump from Right": self.can_super_jump,
            "Luminous B Portal Area Double Jump": self.can_double_jump,
            "Walkway B Double Jump from Clock Exit": self.can_double_jump,
            "Walkway B Hall of Mirrors Double Jumps": self.can_double_jump,
            "Chapel B Upward Hall Climb": self.can_double_jump,
            "Chapel B Top MK Door": self.can_open_mk_doors,
            "Aqueduct B Main Left Double Jump": self.can_double_jump,
            "Aqueduct B Crush Wall Right": self.can_break_walls,
            "Aqueduct B Main Right Double Jump": self.can_double_jump,
            "Aqueduct B Crush Wall Left": lambda state: self.can_break_walls(state) and self.can_double_jump(state),
            "Clock B Double Jump from Bottom": self.can_double_jump,
            "Clock B Lower Alt-button Press from Bottom": self.can_pass_clock_b_gate,
            "Clock B Lower Alt-button Press from Top": self.can_pass_clock_b_gate,
            "Clock B Double Jumps from Pendulum Area": self.can_double_jump,
            "Clock B Slide Space": self.can_slide,
            "Clock B Warp Gate": self.can_warp_castles,
            "Top B Top MK Door": self.can_open_mk_doors,
            "Top B Crush Blocks": self.can_break_ceilings,
            "Top B Warp Gate": self.can_warp_castles,
            "Top B Throne Alt-button Press from Top": self.can_pass_top_b_gate,
            "Top B Throne Alt-button Press from Bottom": self.can_pass_top_b_gate,
            "Top B Lower Super Jump from Left": self.can_super_jump,
            "Top B Bottom Skull Door": self.can_open_skull_doors,
            "Top B Lower Super Jump from Right": self.can_super_jump,
        }

    def can_double_jump(self, state: CollectionState) -> bool:
        """Sylph Feather or any item that lets you gain infinite height."""
        return state.has_any([item_names.relic_feather, item_names.relic_wing, item_names.equip_boots_in,
                              item_names.equip_boots_f], self.player)

    def can_super_jump(self, state: CollectionState) -> bool:
        """Any item that lets you gain infinite height."""
        return state.has_any([item_names.relic_wing, item_names.equip_boots_in, item_names.equip_boots_f], self.player)

    def can_break_ceilings(self, state: CollectionState) -> bool:
        """Griffin's Wing and Crush Boots specifically."""
        return state.has_all([item_names.relic_wing, item_names.equip_boots_c], self.player)

    def can_break_walls(self, state: CollectionState) -> bool:
        """Crushing Stone."""
        return state.has(item_names.whip_crush, self.player)

    def can_slide(self, state: CollectionState) -> bool:
        """Lizard Tail."""
        return state.has(item_names.relic_tail, self.player)

    def can_open_mk_doors(self, state: CollectionState) -> bool:
        """MK's Bracelet."""
        return state.has(item_names.equip_bracelet_mk, self.player)

    def can_open_skull_doors(self, state: CollectionState) -> bool:
        """Skull Key."""
        return state.has(item_names.use_key_s, self.player)

    def can_open_lure_doors(self, state: CollectionState) -> bool:
        """Lure Key."""
        return state.has(item_names.use_key_l, self.player)

    def can_open_floodgate(self, state: CollectionState) -> bool:
        """Floodgate Key as well as the jump height needed to reach the floodgate to begin with."""
        return self.can_double_jump(state) and state.has(item_names.use_key_f, self.player)

    def can_see_in_darkness(self, state: CollectionState) -> bool:
        """Night Goggles."""
        return state.has(item_names.equip_goggles, self.player)

    def can_warp_castles(self, state: CollectionState) -> bool:
        """JB's Bracelet."""
        return state.has(item_names.equip_bracelet_jb, self.player)

    def can_open_center_a_gate(self, state: CollectionState) -> bool:
        """Broke the hand statue in the Castle Top Floor A attic."""
        return state.has(item_names.event_hand, self.player)

    def can_open_center_b_gate(self, state: CollectionState) -> bool:
        """All six Vlad relics found."""
        return state.has_all([item_names.relic_v_nail, item_names.relic_v_eye, item_names.relic_v_fang,
                              item_names.relic_v_heart, item_names.relic_v_rib, item_names.relic_v_ring], self.player)

    def can_free_maxim(self, state: CollectionState) -> bool:
        """Both Juste and Maxim's Bracelets as well as the Vlads."""
        return self.can_open_center_b_gate(state) and state.has_all([item_names.equip_bracelet_jb,
                                                                     item_names.equip_bracelet_mk], self.player)

    def can_place_required_furniture(self, state: CollectionState) -> bool:
        """The number of unique furniture types specified by the Required Furniture Amount option."""
        return state.has_from_list([furn for furn in FURNITURE], self.player, self.furniture_amount_required)

    def can_pass_skeleton_b_wall(self, state: CollectionState) -> bool:
        """Broke the Crushing Stone wall in Skeleton Cave A."""
        return state.has_all([item_names.event_wall_skeleton, item_names.whip_crush], self.player)

    def can_pass_sky_a_wall(self, state: CollectionState) -> bool:
        """Broke the Crushing Stone wall in Sky Walkway B."""
        return state.has_all([item_names.event_wall_skeleton, item_names.whip_crush], self.player)

    def can_pass_clock_a_wall(self, state: CollectionState) -> bool:
        """Hammered Bronze Guarder into the wall in Clock Tower B."""
        return state.has(item_names.event_guarder, self.player)

    def can_pass_under_crank(self, state: CollectionState) -> bool:
        """Raised the crankshaft in Clock Tower B and can slide under it."""
        return state.has_all([item_names.event_crank and item_names.relic_tail], self.player)

    def can_pass_clock_b_gate(self, state: CollectionState) -> bool:
        """Pressed the gate button in Clock Tower A."""
        return state.has(item_names.event_button_clock, self.player)

    def can_pass_top_b_gate(self, state: CollectionState) -> bool:
        """Pressed the gate button in Castle Top Floor A."""
        return state.has(item_names.event_button_top, self.player)

    def set_cvhodis_rules(self) -> None:
        multiworld = self.world.multiworld

        for region in multiworld.get_regions(self.player):
            # Set each Entrance's rule if it should have one.
            for ent in region.entrances:
                if ent.name in self.entrance_rules:
                    ent.access_rule = self.entrance_rules[ent.name]

            # Set each Location's rule if it should have one.
            for loc in region.locations:
                if loc.name in self.location_rules:
                    loc.access_rule = self.location_rules[loc.name]

        # Set the World's completion condition depending on which goal objectives are required.
        required_objectives = []
        if self.medium_ending_required:
            required_objectives += [item_names.event_ending_m]
        if self.worst_ending_required:
            required_objectives += [item_names.event_ending_b]
        if self.best_ending_required:
            required_objectives += [item_names.event_ending_g]
        if self.furniture_amount_required:
            required_objectives += [item_names.event_furniture]

        multiworld.completion_condition[self.player] = lambda state: state.has_all(required_objectives, self.player)
