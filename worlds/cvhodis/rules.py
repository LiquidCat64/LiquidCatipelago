from typing import Dict, TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import CollectionRule
from .data import item_names, loc_names,  ent_names
from .items import FURNITURE, SPELLBOOKS
from .options import SpellboundBossLogic, CastleWarpCondition

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
    spellbound_bosses: int

    def __init__(self, world: "CVHoDisWorld") -> None:
        self.player = world.player
        self.world = world
        self.furniture_amount_required = world.furniture_amount_required
        self.medium_ending_required = world.options.medium_ending_required.value
        self.worst_ending_required = world.options.worst_ending_required.value
        self.best_ending_required = world.options.best_ending_required.value
        self.spellbound_bosses = world.options.spellbound_boss_logic.value
        self.castle_warp_condition = world.options.castle_warp_condition.value

        self.location_rules = {
            # Entrance A
            loc_names.eta2: lambda state: self.can_break_ceilings(state) and self.can_cross_drawbridges(state),
            loc_names.eta3: lambda state: self.can_break_ceilings(state) and self.can_cross_drawbridges(state),
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
            loc_names.sca10: self.can_beat_hard_bosses,  # VS Legion (corpse)
            # Luminous Cavern A
            loc_names.lca11: self.can_break_walls,
            loc_names.lca8a: self.can_super_jump,
            loc_names.lca10: self.can_super_jump,
            loc_names.lca23: self.can_beat_hard_bosses,  # VS Death
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
            # Clock Tower A
            loc_names.cra22a: self.can_win_ball_race_a,
            loc_names.cra22d: self.can_win_ball_race_a,
            loc_names.cra22c: self.can_win_ball_race_a,
            loc_names.cra22b: self.can_win_ball_race_a,
            # Top Floor A
            loc_names.tfa1b: self.can_double_jump,
            loc_names.tfa1a: self.can_double_jump,
            loc_names.tfa11: self.can_beat_hard_bosses,  # VS Minotaur Lv2
            # Entrance B
            loc_names.etb0: self.can_cross_drawbridges,
            loc_names.etb2b: lambda state: self.can_break_ceilings(state) and self.can_cross_drawbridges(state),
            loc_names.etb2a: lambda state: self.can_break_ceilings(state) and self.can_cross_drawbridges(state),
            loc_names.etb3: self.can_break_ceilings,
            loc_names.etb9: self.can_super_jump,
            # Marble Corridor B
            loc_names.mcb9: self.can_slide,
            loc_names.mcb11: self.can_double_jump,
            # The Wailing Way B
            loc_names.wwb0b: self.can_double_jump,
            loc_names.wwb4a: self.can_super_jump,
            loc_names.wwb4b: self.can_super_jump,
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
            ent_names.eta_warp_u: lambda state: self.can_super_jump(state) and self.can_warp_castles(state),
            ent_names.eta_cstone_ul: lambda state: self.can_break_walls(state) and self.can_super_jump(state),
            ent_names.eta_warp_l: lambda state: self.can_open_lure_doors(state) and self.can_warp_castles(state),
            ent_names.eta_cstone_ur: lambda state: self.can_break_walls(state) and self.can_super_jump(state),
            ent_names.eta_cstone_lr: self.can_break_walls,
            ent_names.eta_cstone_ll: self.can_break_walls,
            ent_names.mca_exit_tfa: self.can_open_skull_doors,
            ent_names.ria_slide_r: self.can_slide,
            ent_names.ria_slide_l: self.can_slide,
            ent_names.wwa_exit_cya: self.can_open_skull_doors,
            ent_names.cya_warp:  lambda state: self.can_open_lure_doors(state) and self.can_warp_castles(state),
            ent_names.cya_djumps: self.can_double_jump,
            ent_names.cya_exit_wwa: self.can_open_skull_doors,
            ent_names.cya_exit_tfa: self.can_double_jump,
            ent_names.sca_crates_r: self.can_double_jump,
            ent_names.sca_crates_l: self.can_double_jump,
            ent_names.lca_warp:  lambda state: self.can_break_walls(state) and self.can_warp_castles(state),
            ent_names.lca_floodgate: self.can_open_floodgate,
            ent_names.lca_talos: self.can_beat_hard_bosses,  # VS Talos
            ent_names.lca_sjump_l: self.can_super_jump,
            ent_names.lca_sjump_r: self.can_super_jump,
            ent_names.swa_djump_p: self.can_double_jump,
            ent_names.swa_djump_c: lambda state: self.can_double_jump(state) and self.can_beat_medium_bosses(state),  # VS Devil
            ent_names.swa_goggles_u: self.can_see_in_darkness,
            ent_names.swa_goggles_l: self.can_see_in_darkness,
            ent_names.swa_dark_u: self.can_double_jump,
            ent_names.swa_devil: self.can_beat_medium_bosses,  # VS Devil
            ent_names.cda_djump: self.can_double_jump,
            ent_names.cda_exit_tfa: self.can_open_mk_doors,
            ent_names.ada_djump_l: self.can_double_jump,
            ent_names.ada_cstone_r: self.can_break_walls,
            ent_names.ada_djump_r: lambda state: self.can_double_jump(state) and self.can_beat_medium_bosses(state),  # VS Giant Merman
            ent_names.ada_down_m: self.can_beat_medium_bosses,  # VS Giant Merman
            ent_names.ada_cstone_l: lambda state: self.can_break_walls(state) and self.can_double_jump(state),
            ent_names.cra_djump_l: self.can_double_jump,
            ent_names.cra_djump_p: self.can_double_jump,
            ent_names.cra_slide: lambda state: self.can_pass_clock_a_wall(state) and self.can_slide(state),
            ent_names.cra_slimer_l: self.can_beat_medium_bosses,  # VS Max Slimer
            ent_names.cra_slimer_r: self.can_beat_medium_bosses,  # VS Max Slimer
            ent_names.cra_warp: self.can_warp_castles,
            ent_names.tfa_exit_cda: self.can_open_mk_doors,
            ent_names.tfa_cstone_r: self.can_break_walls,
            ent_names.tfa_cboots: self.can_break_ceilings,
            ent_names.tfa_cstone_l: self.can_break_walls,
            ent_names.tfa_warp: self.can_warp_castles,
            ent_names.tfa_pazuzu: self.can_beat_hard_bosses,  # VS Pazuzu
            ent_names.tfa_sjump_r: self.can_super_jump,
            ent_names.tfa_exit_mca: self.can_open_skull_doors,
            ent_names.tfa_sjump_l: self.can_super_jump,

            # Castle B
            ent_names.etb_warp_u: lambda state: self.can_super_jump(state) and self.can_warp_castles(state),
            ent_names.etb_cstone_ul: lambda state: self.can_break_walls(state) and self.can_super_jump(state),
            ent_names.etb_warp_l: lambda state: self.can_open_lure_doors(state) and self.can_warp_castles(state),
            ent_names.etb_cstone_ur: lambda state: self.can_break_walls(state) and self.can_super_jump(state),
            ent_names.etb_cstone_lr: self.can_break_walls,
            ent_names.etb_cstone_ll: self.can_break_walls,
            ent_names.mcb_exit_tfb: self.can_open_skull_doors,
            ent_names.wwb_exit_cyb: self.can_open_skull_doors,
            ent_names.sab_cyclops_r: self.can_beat_hard_bosses,  # VS Cyclops
            ent_names.sab_cyclops_l: self.can_beat_hard_bosses,  # VS Cyclops
            ent_names.cyb_warp: lambda state: self.can_open_lure_doors(state) and self.can_warp_castles(state),
            ent_names.cyb_djump: self.can_double_jump,
            ent_names.cyb_exit_wwb: self.can_open_skull_doors,
            ent_names.cyb_exit_tfb: self.can_double_jump,
            ent_names.scb_rock: self.can_double_jump,
            ent_names.lcb_sjump_l: self.can_super_jump,
            ent_names.lcb_sjump_r: self.can_super_jump,
            ent_names.lcb_portal: self.can_double_jump,
            ent_names.swb_djump_c: lambda state: self.can_double_jump(state) and self.can_beat_medium_bosses(state),  # VS Legion (saint)
            ent_names.swb_djump_m: self.can_double_jump,
            ent_names.swb_legion: self.can_beat_medium_bosses,  # VS Legion (saint)
            ent_names.cdb_djump: self.can_double_jump,
            ent_names.cdb_exit_tfb: self.can_open_mk_doors,
            ent_names.adb_djump_l: self.can_double_jump,
            ent_names.adb_cstone_r: self.can_break_walls,
            ent_names.adb_djump_r: self.can_double_jump,
            ent_names.adb_cstone_l: lambda state: self.can_break_walls(state) and self.can_double_jump(state),
            ent_names.crb_djump_l: self.can_double_jump,
            ent_names.crb_abutton_b: self.can_pass_clock_b_gate,
            ent_names.crb_abutton_t: self.can_pass_clock_b_gate,
            ent_names.crb_djump_p: self.can_double_jump,
            ent_names.crb_peep_l: self.can_beat_medium_bosses,  # VS Peeping Big
            ent_names.crb_peep_r: self.can_beat_medium_bosses,  # VS Peeping Big
            ent_names.crb_slide: self.can_slide,
            ent_names.crb_warp: self.can_warp_castles,
            ent_names.tfb_exit_cdb: self.can_open_mk_doors,
            ent_names.tfb_cboots: self.can_break_ceilings,
            ent_names.tfb_warp: self.can_warp_castles,
            ent_names.tfb_abutton_t: self.can_pass_top_b_gate,
            ent_names.tfb_abutton_b: self.can_pass_top_b_gate,
            ent_names.tfb_sjump_r: self.can_super_jump,
            ent_names.tfb_exit_mcb: self.can_open_skull_doors,
            ent_names.tfb_sjump_l: self.can_super_jump,
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
        """JB's Bracelet, met Death at Clock Tower, or nothing depending on the Castle Warp Condition option."""
        if self.castle_warp_condition == CastleWarpCondition.option_bracelet:
            return state.has(item_names.equip_bracelet_jb, self.player)
        elif self.castle_warp_condition == CastleWarpCondition.option_death:
            return state.has(item_names.event_death, self.player)
        return True

    def can_win_ball_race_a(self, state: CollectionState) -> bool:
        """Specifically Sylph Feather; Griffin's Wing makes this challenge way too hard."""
        return state.has(item_names.relic_feather, self.player)

    def can_beat_medium_bosses(self, state: CollectionState) -> bool:
        """1 spell book if Spellbound Boss Logic is Normal, 2 if Easy, or none if Disabled."""
        if self.spellbound_bosses == SpellboundBossLogic.option_normal:
            return state.has_from_list_unique([book for book in SPELLBOOKS], self.player, 1)
        elif self.spellbound_bosses == SpellboundBossLogic.option_easy:
            return state.has_from_list_unique([book for book in SPELLBOOKS], self.player, 2)
        else:
            return True

    def can_beat_hard_bosses(self, state: CollectionState) -> bool:
        """2 spell books if Spellbound Boss Logic is Normal, 3 if Easy, or none if Disabled."""
        if self.spellbound_bosses == SpellboundBossLogic.option_normal:
            return state.has_from_list_unique([book for book in SPELLBOOKS], self.player, 2)
        elif self.spellbound_bosses == SpellboundBossLogic.option_easy:
            return state.has_from_list_unique([book for book in SPELLBOOKS], self.player, 3)
        else:
            return True

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
        return state.has_from_list_unique([furn for furn in FURNITURE], self.player, self.furniture_amount_required)

    def can_pass_skeleton_b_wall(self, state: CollectionState) -> bool:
        """Broke the Crushing Stone wall in Skeleton Cave A."""
        return state.has_all([item_names.event_wall_skeleton, item_names.whip_crush], self.player)

    def can_pass_sky_a_wall(self, state: CollectionState) -> bool:
        """Broke the Crushing Stone wall in Sky Walkway B and can beat Shadow, a medium difficulty boss."""
        return (state.has_all([item_names.event_wall_skeleton, item_names.whip_crush], self.player) and
                self.can_beat_medium_bosses(state))

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

    def can_cross_drawbridges(self, state: CollectionState) -> bool:
        """Defeated Giant Bat in Marble Corridor A."""
        return state.has(item_names.event_giant_bat, self.player)

    def set_cvhodis_rules(self) -> None:
        multiworld = self.world.multiworld

        # Set each Entrance's rule if it should have one.
        for ent_name, rule in self.entrance_rules.items():
            entrance = multiworld.get_entrance(ent_name, self.player)
            entrance.access_rule = rule

        # Set each Location's rule if it should have one.
        for loc in multiworld.get_locations(self.player):
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
