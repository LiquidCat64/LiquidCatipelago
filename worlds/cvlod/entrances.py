from .data import ent_names, reg_names, stage_names
from .stages import CVLOD_STAGE_INFO, CVLoDActiveStage, find_stage_in_list
from .options import CVLoDOptions, VillaState
from .data.enums import Scenes

from typing import NamedTuple
# from enum import IntEnum

import logging

class CVLoDEntranceData(NamedTuple):
    stage: str  # What stage the Entrance is a part of.
    dest: str  # The name of the Region the Entrance normally connects into. Will be ignored if stage connection has a
               # value set on it in favor of getting this from the active stage list.
    stage_connection: str = ""  # The key in the dict in the stage connection value in the world's active stage list
                                # parameter that this refers to. Used in determining what stage's starting or ending
                                # Region to connect into instead of the dest value if applicable.
    type: str = ""  # Anything extra to know about the Entrance. Used to know if it should be added or not based on the
                    # slot options.

CVLOD_ENTRANCE_INFO = {
    # Foggy Lake
    # Above Decks
    ent_names.fld_to_below: CVLoDEntranceData(stage_names.FOGGY, reg_names.flb_below),
    # Below Decks
    ent_names.flb_from_below: CVLoDEntranceData(stage_names.FOGGY, reg_names.fld_above),
    ent_names.flb_sink:       CVLoDEntranceData(stage_names.FOGGY, reg_names.flp_pier),
    # Pier
    ent_names.flp_end: CVLoDEntranceData(stage_names.FOGGY, reg_names.forest_start, stage_connection="next"),

    # Forest of Silence
    ent_names.forest_king_skeleton_1: CVLoDEntranceData(stage_names.FOREST, reg_names.forest_half_1),
    ent_names.forest_dbridge_gate:    CVLoDEntranceData(stage_names.FOREST, reg_names.forest_half_2),
    ent_names.forest_reverse_leap:    CVLoDEntranceData(stage_names.FOREST, reg_names.forest_half_1,
                                                        type="hard"),
    ent_names.forest_final_switch:    CVLoDEntranceData(stage_names.FOREST, reg_names.forest_end),
    ent_names.forest_end:             CVLoDEntranceData(stage_names.FOREST, reg_names.cw_start,
                                                        stage_connection="next"),

    # Castle Wall
    # Main
    ent_names.cw_start:        CVLoDEntranceData(stage_names.C_WALL, reg_names.forest_end,
                                                 stage_connection="prev"),
    ent_names.cw_rt_door_b:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cwr_rtower),
    ent_names.cw_rt_door_t:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cwr_rtower),
    ent_names.cw_portcullis_c: CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_exit),
    ent_names.cw_lt_door_b:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cwl_ltower),
    ent_names.cw_lt_door_t:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cwl_ltower),
    ent_names.cw_dragon_drop:  CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_save_ramp),
    ent_names.cw_save_drop:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_descent),
    ent_names.cw_desc_drop:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_start),
    ent_names.cw_drac_drop:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_descent, type="easy"),
    ent_names.cw_drac_leap:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_save_ramp, type="hard"),
    ent_names.cw_end:          CVLoDEntranceData(stage_names.C_WALL, reg_names.villafy_start,
                                                 stage_connection="next"),
    # Right Tower
    ent_names.cwr_bottom: CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_start),
    ent_names.cwr_top:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_dragon_sw),
    # Left Tower
    ent_names.cwl_bottom: CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_start),
    ent_names.cwl_top:    CVLoDEntranceData(stage_names.C_WALL, reg_names.cw_drac_sw),


    # Villa Front Yard
    ent_names.villafy_start: CVLoDEntranceData(stage_names.VILLA, reg_names.cw_exit,
                                             stage_connection="prev"),
    ent_names.villafy_dog_gates: CVLoDEntranceData(stage_names.VILLA, reg_names.villafy_front_yard),
    ent_names.villafy_fountain_pillar: CVLoDEntranceData(stage_names.VILLA, reg_names.villafy_fountain),
    ent_names.villafy_front_doors: CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_foyer),
    # Villa Foyer
    ent_names.villafo_front_doors: CVLoDEntranceData(stage_names.VILLA, reg_names.villafy_front_yard),
    ent_names.villafo_to_rose_garden: CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_garden),
    ent_names.villafo_from_rose_garden: CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_foyer),
    ent_names.villafo_living_door: CVLoDEntranceData(stage_names.VILLA, reg_names.villala_living),
    ent_names.villafo_to_serv_door: CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_serv_recep),
    ent_names.villafo_from_serv_door: CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_foyer),
    ent_names.villafo_serv_exit: CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_ent_s),
    # Villa Living Area
    ent_names.villala_rose_door: CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_garden),
    ent_names.villala_to_storeroom: CVLoDEntranceData(stage_names.VILLA, reg_names.villala_storeroom),
    ent_names.villala_from_storeroom: CVLoDEntranceData(stage_names.VILLA, reg_names.villala_living),
    ent_names.villala_archives: CVLoDEntranceData(stage_names.VILLA, reg_names.villala_archives),
    # ent_names.villala_renon: CVLoDEntranceData(stage_names.VILLA, reg_names.renon, type="shop"),
    ent_names.villala_maze_doors: CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_ent_m),
    # Villa Maze
    ent_names.villam_back_doors:          CVLoDEntranceData(stage_names.VILLA, reg_names.villala_living),
    ent_names.villam_to_main_maze_gate:   CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_f),
    ent_names.villam_from_main_maze_gate: CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_ent_m),
    ent_names.villam_copper_door:         CVLoDEntranceData(stage_names.VILLA, reg_names.villam_crypt_e),
    ent_names.villam_bridge_door:         CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_f),
    ent_names.villam_crypt_door:          CVLoDEntranceData(stage_names.VILLA, reg_names.villac_crypt_i),
    ent_names.villam_front_divide:        CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_r),
    ent_names.villam_rear_divide:         CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_f),
    ent_names.villam_thorn_fence:         CVLoDEntranceData(stage_names.VILLA, reg_names.villam_garden_f),
    ent_names.villam_rear_escape:         CVLoDEntranceData(stage_names.VILLA, reg_names.villam_serv_path),
    ent_names.villam_path_escape:         CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_r),
    ent_names.villam_to_servant_gate:     CVLoDEntranceData(stage_names.VILLA, reg_names.villam_serv_path),
    ent_names.villam_from_servant_gate:   CVLoDEntranceData(stage_names.VILLA, reg_names.villam_maze_ent_s),
    ent_names.villam_serv_door:           CVLoDEntranceData(stage_names.VILLA, reg_names.villafo_serv_recep),
    ent_names.villam_copper_skip_o:       CVLoDEntranceData(stage_names.VILLA, reg_names.villam_crypt_e, type="hard"),
    ent_names.villam_copper_skip_c:       CVLoDEntranceData(stage_names.VILLA, reg_names.villac_crypt_i, type="hard"),
    # Villa crypt
    ent_names.villac_door:   CVLoDEntranceData(stage_names.VILLA, reg_names.villam_crypt_e),
    ent_names.villac_end_r:  CVLoDEntranceData(stage_names.VILLA, reg_names.tunnel_start, stage_connection="next"),
    ent_names.villac_end_ca: CVLoDEntranceData(stage_names.VILLA, reg_names.uw_main, stage_connection="next alt 1"),
    ent_names.villac_end_co: CVLoDEntranceData(stage_names.VILLA, reg_names.towf_face_climb, stage_connection="next alt 2"),

    # Tunnel
    # Main
    ent_names.tunnel_start_warp: CVLoDEntranceData(stage_names.TUNNEL, reg_names.villac_crypt_i, stage_connection="prev"),
    ent_names.tunnel_cutscene:  CVLoDEntranceData(stage_names.TUNNEL, reg_names.tunnel_main),
    # ent_names.tunnel_start_renon: {"destination": reg_names.renon, "add conds": ["shopsanity"]},
    ent_names.tunnel_gondolas: CVLoDEntranceData(stage_names.TUNNEL, reg_names.tunnel_end),
    ent_names.tunnel_reverse: CVLoDEntranceData(stage_names.TUNNEL, reg_names.tunnel_main, type="hard"),
    #ent_names.tunnel_end_renon: {"destination": reg_names.renon, "add conds": ["shopsanity"]},
    ent_names.tunnel_boss_door: CVLoDEntranceData(stage_names.TUNNEL, reg_names.tunnelb_arena),
    # Boss Arena
    ent_names.tunnelb_return: CVLoDEntranceData(stage_names.TUNNEL, reg_names.tunnel_end),
    ent_names.tunnelb_end: CVLoDEntranceData(stage_names.TUNNEL, reg_names.ccb_basement, stage_connection="next"),

    # Underground Waterway
    # Main
    ent_names.uw_start_warp: CVLoDEntranceData(stage_names.WATERWAY, reg_names.villac_crypt_i, stage_connection="prev"),
    #ent_names.uw_renon: {"destination": reg_names.renon, "add conds": ["shopsanity"]},
    ent_names.uw_final_waterfall: CVLoDEntranceData(stage_names.WATERWAY, reg_names.uw_end),
    ent_names.uw_boss_door: CVLoDEntranceData(stage_names.WATERWAY, reg_names.uwb_arena),
    # Boss Arena
    ent_names.uwb_return: CVLoDEntranceData(stage_names.WATERWAY, reg_names.uw_end),
    ent_names.uwb_end: CVLoDEntranceData(stage_names.WATERWAY, reg_names.ccb_basement, stage_connection="next"),

    # The Outer Wall
    # Face
    ent_names.towf_start_warp: CVLoDEntranceData(stage_names.OUTER, reg_names.villac_crypt_i, stage_connection="prev"),
    ent_names.towf_ascent_elev: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_slaughter_ext_f),
    ent_names.towf_leap: CVLoDEntranceData(stage_names.OUTER, reg_names.towf_face_desc, type="hard"),
    ent_names.towf_descent_elev: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_key_hall),
    ent_names.towf_bowling_door: CVLoDEntranceData(stage_names.OUTER, reg_names.towb_bowling),
    # Slaughterhouse Exterior
    ent_names.towse_slaughter_elev: CVLoDEntranceData(stage_names.OUTER, reg_names.towf_face_climb),
    ent_names.towse_slaughter_door: CVLoDEntranceData(stage_names.OUTER, reg_names.towsi_slaughter_int),
    ent_names.towse_pillar: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_slaughter_ext_r),
    ent_names.towse_return: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_slaughter_ext_f),
    ent_names.towse_to_wall_door: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_key_hall),
    ent_names.towse_from_wall_door: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_slaughter_ext_r),
    ent_names.towse_key_elev: CVLoDEntranceData(stage_names.OUTER, reg_names.towf_face_desc),
    # Slaughterhouse Interior
    ent_names.towsi_door: CVLoDEntranceData(stage_names.OUTER, reg_names.towse_slaughter_ext_f),
    # Bowling Alley
    ent_names.towb_door: CVLoDEntranceData(stage_names.OUTER, reg_names.towf_face_desc),
    ent_names.towb_elev: CVLoDEntranceData(stage_names.OUTER, reg_names.towh_saw_roof),
    # Harpy Rooftops
    ent_names.towh_bowling_elev: CVLoDEntranceData(stage_names.OUTER, reg_names.towb_bowling),
    ent_names.towh_gondola: CVLoDEntranceData(stage_names.OUTER, reg_names.towh_end),
    ent_names.towh_end: CVLoDEntranceData(stage_names.OUTER, reg_names.atm_museum, stage_connection="next"),

    # Art Tower
    # Museum
    ent_names.atm_start: CVLoDEntranceData(stage_names.ART, reg_names.towh_end, stage_connection="prev"),
    ent_names.atm_to_door_1: CVLoDEntranceData(stage_names.ART, reg_names.atm_middle),
    ent_names.atm_from_door_1: CVLoDEntranceData(stage_names.ART, reg_names.atm_museum),
    ent_names.atm_to_door_2: CVLoDEntranceData(stage_names.ART, reg_names.atm_middle_door),
    ent_names.atm_from_door_2: CVLoDEntranceData(stage_names.ART, reg_names.atm_middle),
    ent_names.atm_hall_ent: CVLoDEntranceData(stage_names.ART, reg_names.atc_conservatory),
    ent_names.atm_skip_door_1: CVLoDEntranceData(stage_names.ART, reg_names.atm_middle, type="hard"),
    # Conservatory
    ent_names.atc_bottom: CVLoDEntranceData(stage_names.ART, reg_names.atm_middle_door),
    ent_names.atc_end: CVLoDEntranceData(stage_names.ART, reg_names.torm_maze_main, stage_connection="next"),

    # Tower of Ruins
    # Door Maze
    ent_names.torm_start: CVLoDEntranceData(stage_names.RUINS, reg_names.atc_conservatory, stage_connection="prev"),
    ent_names.torm_maze: CVLoDEntranceData(stage_names.RUINS, reg_names.torm_maze_end),
    ent_names.torm_burial_door: CVLoDEntranceData(stage_names.RUINS, reg_names.torc_dark),
    ent_names.torc_maze_door:  CVLoDEntranceData(stage_names.RUINS, reg_names.torm_maze_end),
    ent_names.torc_climb: CVLoDEntranceData(stage_names.RUINS, reg_names.torc_end),
    ent_names.torc_end: CVLoDEntranceData(stage_names.RUINS, reg_names.toscic_factory, stage_connection="next"),

    # Castle Center
    # Basement
    ent_names.ccb_tc_door: CVLoDEntranceData(stage_names.CENTER, reg_names.ccb_torture_chamber),
    ent_names.ccb_wall: CVLoDEntranceData(stage_names.CENTER, reg_names.ccb_behemoth_crack),
    ent_names.ccb_stairs: CVLoDEntranceData(stage_names.CENTER, reg_names.ccbe_bottom_elevator),
    # Bottom Elevator Room
    ent_names.ccbe_downstairs: CVLoDEntranceData(stage_names.CENTER, reg_names.ccb_basement),
    ent_names.ccbe_upstairs: CVLoDEntranceData(stage_names.CENTER, reg_names.ccff_factory),
    ent_names.ccbe_elevator: CVLoDEntranceData(stage_names.CENTER, reg_names.ccte_elev_top),
    # Factory Floor
    ent_names.ccff_carpet_stairs: CVLoDEntranceData(stage_names.CENTER, reg_names.ccll_lizard_main),
    ent_names.ccff_gear_stairs: CVLoDEntranceData(stage_names.CENTER, reg_names.ccia_inventions),
    ent_names.ccff_lizard_door: CVLoDEntranceData(stage_names.CENTER, reg_names.ccll_lizard_main),
    # Lizard Labs
    ent_names.ccll_brokenstairs_door: CVLoDEntranceData(stage_names.CENTER, reg_names.ccff_factory),
    ent_names.ccll_heinrich_door: CVLoDEntranceData(stage_names.CENTER, reg_names.ccia_nitro_liz),
    ent_names.ccll_upper_wall_out: CVLoDEntranceData(stage_names.CENTER, reg_names.ccll_lizard_crack),
    ent_names.ccll_upper_wall_in: CVLoDEntranceData(stage_names.CENTER, reg_names.ccll_lizard_main),
    ent_names.ccll_library_passage: CVLoDEntranceData(stage_names.CENTER, reg_names.ccl_library),
    # Library
    ent_names.ccl_exit: CVLoDEntranceData(stage_names.CENTER, reg_names.ccll_lizard_crack),
    # Invention Area
    ent_names.ccia_stairs: CVLoDEntranceData(stage_names.CENTER, reg_names.ccff_factory),
    ent_names.ccia_lizard_door: CVLoDEntranceData(stage_names.CENTER, reg_names.ccll_lizard_main),
    # ent_names.cc_renon: {"destination": reg_names.renon, "add conds": ["shopsanity"]},
    # Top Elevator Room
    ent_names.ccte_elevator: CVLoDEntranceData(stage_names.CENTER, reg_names.ccbe_bottom_elevator),
    ent_names.ccte_exit_r: CVLoDEntranceData(stage_names.CENTER, reg_names.dt_start, stage_connection="next"),
    ent_names.ccte_exit_c: CVLoDEntranceData(stage_names.CENTER, reg_names.toscic_factory, stage_connection="next alt 1"),

    # Duel Tower
    ent_names.dt_start: CVLoDEntranceData(stage_names.DUEL, reg_names.ccte_elev_top, stage_connection="prev"),
    ent_names.dt_drop: CVLoDEntranceData(stage_names.DUEL, reg_names.dt_main),
    ent_names.dt_last: CVLoDEntranceData(stage_names.DUEL, reg_names.dt_end),
    ent_names.dt_end: CVLoDEntranceData(stage_names.DUEL, reg_names.toe_bottom, stage_connection="next"),

    # Tower of Execution
    # Main
    ent_names.toe_bottom_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.dt_end, stage_connection="prev"),
    ent_names.toe_bottom_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toem_stones),
    ent_names.toe_side: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toeg_grates),
    ent_names.toe_side_drop: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_bottom, type="hard"),
    ent_names.toe_middle_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toeg_grates),
    ent_names.toe_middle_drop: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_bottom, type="hard"),
    ent_names.toe_middle_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toeb_balls),
    ent_names.toe_top_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toeb_balls),
    ent_names.toe_top_drop_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_middle_i, type="hard"),
    ent_names.toe_top_drop_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_middle_k, type="hard"),
    ent_names.toe_top_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toeu_ultimate),
    # Melting Pond
    ent_names.toem_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_bottom),
    ent_names.toem_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toeg_grates),
    # Flaming Grates
    ent_names.toeg_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toem_stones),
    ent_names.toeg_side: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_middle_i),
    ent_names.toeg_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_middle_k),
    # 1000-Blow Corridor
    ent_names.toeb_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_middle_k),
    ent_names.toeb_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_top),
    # Ultimate
    ent_names.toeu_start: CVLoDEntranceData(stage_names.EXECUTION, reg_names.toe_top),
    ent_names.toeu_end: CVLoDEntranceData(stage_names.EXECUTION, reg_names.roc_int, stage_connection="next"),

    # Tower of Science
    ent_names.toscic_start: CVLoDEntranceData(stage_names.SCIENCE, reg_names.ccte_elev_top, stage_connection="prev"),
    ent_names.toscic_elev: CVLoDEntranceData(stage_names.SCIENCE, reg_names.toscit_halls_start),
    ent_names.toscit_elev: CVLoDEntranceData(stage_names.SCIENCE, reg_names.toscic_factory),
    ent_names.toscit_lone_door: CVLoDEntranceData(stage_names.SCIENCE, reg_names.toscit_halls_main),
    ent_names.toscit_to_ctrl_door: CVLoDEntranceData(stage_names.SCIENCE, reg_names.toscit_end),
    ent_names.toscit_from_ctrl_door: CVLoDEntranceData(stage_names.SCIENCE, reg_names.toscit_end),
    ent_names.toscit_end: CVLoDEntranceData(stage_names.SCIENCE, reg_names.tosor_main, stage_connection="next"),

    # Tower of Sorcery
    ent_names.tosor_start: CVLoDEntranceData(stage_names.SORCERY, reg_names.toscit_end, stage_connection="prev"),
    ent_names.tosor_end: CVLoDEntranceData(stage_names.SORCERY, reg_names.roc_int, stage_connection="next"),

    # Room of Clocks
    # Interior
    ent_names.roci_elev: CVLoDEntranceData(stage_names.ROOM, reg_names.roc_ext),
    ent_names.roci_gate: CVLoDEntranceData(stage_names.ROOM, reg_names.ctgc_start, stage_connection="next"),
    # Exterior
    ent_names.roce_elev: CVLoDEntranceData(stage_names.ROOM, reg_names.roc_int),

    # Clock Tower
    # Gear Climb
    ent_names.ctgc_to_door_a: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctgc_bpillars),
    ent_names.ctgc_from_door_a: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctgc_start),
    ent_names.ctgc_to_door_b: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctgc_bpillars_end),
    ent_names.ctgc_from_door_b: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctgc_bpillars),
    ent_names.ctgc_abyss_door: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctga_abyss_near),
    # Grand Abyss
    ent_names.ctga_climb_door: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctgc_bpillars_end),
    ent_names.ctga_door_c: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctga_abyss_far),
    ent_names.ctga_door_c_skip: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctga_abyss_far, type="hard"),
    ent_names.ctga_door_c_reverse: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctga_abyss_near, type="hard"),
    ent_names.ctga_door_d: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctf_face),
    # Face
    ent_names.ctf_door_d: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctga_abyss_far),
    ent_names.ctf_door_e: CVLoDEntranceData(stage_names.CLOCK, reg_names.ctf_engine),
    ent_names.ctf_end: CVLoDEntranceData(stage_names.CLOCK, reg_names.ck_main, stage_connection="next"),
    # ent_names.ct_renon: {"destination": reg_names.renon, "add conds": ["shopsanity"]},
}

# All Entrances specific to Reinhardt and Carrie's version of the Villa. These should not be created if the Villa State
# is Cornell's.
REIN_CARRIE_VILLA_ENTRANCES: list[str] = [
    ent_names.villam_rear_divide
]

# All Entrances specific to Cornell's version of the Villa. These should not be created if the Villa State is Reinhardt
# and Carrie's.
CORNELL_VILLA_ENTRANCES: list[str] = [
    ent_names.villafo_to_serv_door
]


class CVLoDTransitionData(NamedTuple):
    # transition_offset: int # Where in the ROM the data for the room transition at that destination begins.
    scene_id: int  # ID for which scene in the game the transition is in.
    spawn_id: int  # ID for which spawn location in the scene the transition is at.


SHUFFLEABLE_TRANSITIONS: dict[str, CVLoDTransitionData] = {
    # Foggy Lake
    ent_names.fld_to_below:   CVLoDTransitionData(Scenes.FOGGY_LAKE_ABOVE_DECKS, 0x01),
    ent_names.flb_from_below: CVLoDTransitionData(Scenes.FOGGY_LAKE_BELOW_DECKS, 0x00),
    ent_names.flb_sink:       CVLoDTransitionData(Scenes.FOGGY_LAKE_BELOW_DECKS, 0x01),
    # ent_names.flb_sink: CVLoDTransitionData(Scenes.FOGGY_LAKE_PIER, 0x00),
    ent_names.flp_end:        CVLoDTransitionData(Scenes.FOGGY_LAKE_PIER, 0x01),

    # Forest of Silence
    # ent_names.flp_end: CVLoDTransitionData(Scenes.FOREST_OF_SILENCE, 0x00),
    ent_names.forest_end: CVLoDTransitionData(Scenes.FOREST_OF_SILENCE, 0x01),

    # Castle Wall
    ent_names.cw_start:     CVLoDTransitionData(Scenes.CASTLE_WALL_MAIN, 0x00),
    ent_names.cw_rt_door_b: CVLoDTransitionData(Scenes.CASTLE_WALL_MAIN, 0x02),
    ent_names.cw_lt_door_b: CVLoDTransitionData(Scenes.CASTLE_WALL_MAIN, 0x01),
    ent_names.cw_rt_door_t: CVLoDTransitionData(Scenes.CASTLE_WALL_MAIN, 0x04),
    ent_names.cw_lt_door_t: CVLoDTransitionData(Scenes.CASTLE_WALL_MAIN, 0x03),
    ent_names.cw_end:       CVLoDTransitionData(Scenes.CASTLE_WALL_MAIN, 0x05),
    ent_names.cwr_bottom:   CVLoDTransitionData(Scenes.CASTLE_WALL_TOWERS, 0x01),
    ent_names.cwl_bottom:   CVLoDTransitionData(Scenes.CASTLE_WALL_TOWERS, 0x00),
    ent_names.cwr_top:      CVLoDTransitionData(Scenes.CASTLE_WALL_TOWERS, 0x03),
    ent_names.cwl_top:      CVLoDTransitionData(Scenes.CASTLE_WALL_TOWERS, 0x02),

    # Villa
    ent_names.villafy_start:       CVLoDTransitionData(Scenes.VILLA_FRONT_YARD, 0x00),
    ent_names.villafy_front_doors: CVLoDTransitionData(Scenes.VILLA_FRONT_YARD, 0x01),
    ent_names.villafo_front_doors: CVLoDTransitionData(Scenes.VILLA_FOYER, 0x00),
    ent_names.villafo_serv_exit:   CVLoDTransitionData(Scenes.VILLA_FOYER, 0x01),
    ent_names.villafo_living_door: CVLoDTransitionData(Scenes.VILLA_FOYER, 0x02),
    ent_names.villala_rose_door:   CVLoDTransitionData(Scenes.VILLA_LIVING_AREA, 0x00),
    ent_names.villala_maze_doors:  CVLoDTransitionData(Scenes.VILLA_LIVING_AREA, 0x01),
    ent_names.villam_back_doors:   CVLoDTransitionData(Scenes.VILLA_MAZE, 0x00),
    ent_names.villam_serv_door:    CVLoDTransitionData(Scenes.VILLA_MAZE, 0x01),
    ent_names.villam_crypt_door:   CVLoDTransitionData(Scenes.VILLA_MAZE, 0x02),
    ent_names.villac_door:         CVLoDTransitionData(Scenes.VILLA_CRYPT, 0x00),
    ent_names.villac_end_r:        CVLoDTransitionData(Scenes.VILLA_CRYPT, 0x02),
    ent_names.villac_end_ca:       CVLoDTransitionData(Scenes.VILLA_CRYPT, 0x02),
    ent_names.villac_end_co:       CVLoDTransitionData(Scenes.VILLA_CRYPT, 0x02),

    # Tunnel
    ent_names.tunnel_start_warp: CVLoDTransitionData(Scenes.TUNNEL, 0x00),
    ent_names.tunnel_boss_door:  CVLoDTransitionData(Scenes.TUNNEL, 0x01),
    ent_names.tunnelb_return:    CVLoDTransitionData(Scenes.ALGENIE_MEDUSA_ARENA, 0x40),
    ent_names.tunnelb_end:       CVLoDTransitionData(Scenes.ALGENIE_MEDUSA_ARENA, 0x41),

    # Underground Waterway
    ent_names.uw_start_warp: CVLoDTransitionData(Scenes.WATERWAY, 0x00),
    ent_names.uw_boss_door:  CVLoDTransitionData(Scenes.WATERWAY, 0x01),
    ent_names.uwb_return:    CVLoDTransitionData(Scenes.ALGENIE_MEDUSA_ARENA, 0x80),
    ent_names.uwb_end:       CVLoDTransitionData(Scenes.ALGENIE_MEDUSA_ARENA, 0x81),

    # The Outer Wall
    ent_names.towf_start_warp:      CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x00),
    ent_names.towf_ascent_elev:     CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x01),
    ent_names.towse_slaughter_elev: CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x02),
    ent_names.towse_slaughter_door: CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x03),
    ent_names.towsi_door:           CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x04),
    ent_names.towse_key_elev:       CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x05),
    ent_names.towf_descent_elev:    CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x06),
    ent_names.towf_bowling_door:    CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x07),
    ent_names.towb_door:            CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x08),
    ent_names.towb_elev:            CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x09),
    ent_names.towh_bowling_elev:    CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x0A),
    ent_names.towh_end:             CVLoDTransitionData(Scenes.THE_OUTER_WALL, 0x0B),

    # Art Tower
    ent_names.atm_start:    CVLoDTransitionData(Scenes.ART_TOWER_MUSEUM, 0x00),
    ent_names.atm_hall_ent: CVLoDTransitionData(Scenes.ART_TOWER_MUSEUM, 0x01),
    ent_names.atc_bottom:   CVLoDTransitionData(Scenes.ART_TOWER_CONSERVATORY, 0x00),
    ent_names.atc_end:      CVLoDTransitionData(Scenes.ART_TOWER_CONSERVATORY, 0x01),

    # Tower of Ruins
    ent_names.torm_start:       CVLoDTransitionData(Scenes.RUINS_DOOR_MAZE, 0x00),
    ent_names.torm_burial_door: CVLoDTransitionData(Scenes.RUINS_DOOR_MAZE, 0x01),
    ent_names.torc_maze_door:   CVLoDTransitionData(Scenes.RUINS_DARK_CHAMBERS, 0x00),
    ent_names.torc_end:         CVLoDTransitionData(Scenes.RUINS_DARK_CHAMBERS, 0x01),

    # Castle Center
    # ent_names.ccb_stairs: CVLoDTransitionData(Scenes.CASTLE_CENTER_BASEMENT, 0x00),
    ent_names.ccb_stairs:             CVLoDTransitionData(Scenes.CASTLE_CENTER_BASEMENT, 0x01),
    ent_names.ccbe_downstairs:        CVLoDTransitionData(Scenes.CASTLE_CENTER_BOTTOM_ELEV, 0x00),
    ent_names.ccbe_upstairs:          CVLoDTransitionData(Scenes.CASTLE_CENTER_BOTTOM_ELEV, 0x01),
    ent_names.ccbe_elevator:          CVLoDTransitionData(Scenes.CASTLE_CENTER_BOTTOM_ELEV, 0x02),
    ent_names.ccff_carpet_stairs:     CVLoDTransitionData(Scenes.CASTLE_CENTER_FACTORY, 0x00),
    ent_names.ccff_lizard_door:       CVLoDTransitionData(Scenes.CASTLE_CENTER_FACTORY, 0x01),
    ent_names.ccff_gear_stairs:       CVLoDTransitionData(Scenes.CASTLE_CENTER_FACTORY, 0x02),
    ent_names.ccll_brokenstairs_door: CVLoDTransitionData(Scenes.CASTLE_CENTER_LIZARD_LAB, 0x00),
    ent_names.ccll_heinrich_door:     CVLoDTransitionData(Scenes.CASTLE_CENTER_LIZARD_LAB, 0x01),
    ent_names.ccll_library_passage:   CVLoDTransitionData(Scenes.CASTLE_CENTER_LIZARD_LAB, 0x02),
    ent_names.ccl_exit:               CVLoDTransitionData(Scenes.CASTLE_CENTER_LIBRARY, 0x00),
    ent_names.ccia_stairs:            CVLoDTransitionData(Scenes.CASTLE_CENTER_INVENTIONS, 0x00),
    ent_names.ccia_lizard_door:       CVLoDTransitionData(Scenes.CASTLE_CENTER_INVENTIONS, 0x01),
    ent_names.ccte_elevator:          CVLoDTransitionData(Scenes.CASTLE_CENTER_INVENTIONS, 0x00),
    ent_names.ccte_exit_r:            CVLoDTransitionData(Scenes.CASTLE_CENTER_INVENTIONS, 0x01),
    ent_names.ccte_exit_c:            CVLoDTransitionData(Scenes.CASTLE_CENTER_INVENTIONS, 0x02),

    # Duel Tower
    ent_names.dt_start: CVLoDTransitionData(Scenes.DUEL_TOWER, 0x00),
    ent_names.dt_end:   CVLoDTransitionData(Scenes.DUEL_TOWER, 0x01),

    # Tower of Execution
    ent_names.toe_bottom_start: CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x00),
    ent_names.toe_bottom_end:   CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x01),
    ent_names.toe_side:         CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x02),
    ent_names.toe_middle_start: CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x03),
    ent_names.toe_middle_end:   CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x04),
    ent_names.toe_top_start:    CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x05),
    ent_names.toe_top_end:      CVLoDTransitionData(Scenes.EXECUTION_MAIN, 0x06),
    ent_names.toeg_start:       CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_1, 0x00),
    ent_names.toeg_side:        CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_1, 0x01),
    ent_names.toeg_end:         CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_1, 0x02),
    ent_names.toeb_start:       CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_1, 0x03),
    ent_names.toeb_end:         CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_1, 0x04),
    ent_names.toem_start:       CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_2, 0x00),
    ent_names.toem_end:         CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_2, 0x01),
    ent_names.toeu_start:       CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_2, 0x02),
    ent_names.toeu_end:         CVLoDTransitionData(Scenes.EXECUTION_SIDE_ROOMS_2, 0x03),

    # Tower of Science
    ent_names.toscic_start: CVLoDTransitionData(Scenes.SCIENCE_CONVEYORS, 0x00),
    ent_names.toscic_elev:  CVLoDTransitionData(Scenes.SCIENCE_CONVEYORS, 0x01),
    ent_names.toscit_elev:  CVLoDTransitionData(Scenes.SCIENCE_LABS, 0x00),
    ent_names.toscit_end:   CVLoDTransitionData(Scenes.SCIENCE_LABS, 0x01),

    # Tower of Sorcery
    ent_names.tosor_start: CVLoDTransitionData(Scenes.TOWER_OF_SORCERY, 0x00),
    ent_names.tosor_end:   CVLoDTransitionData(Scenes.TOWER_OF_SORCERY, 0x01),

    # Room of Clocks
    # ent_names.roci_elev: CVLoDTransitionData(Scenes.ROOM_OF_CLOCKS, 0x00),
    ent_names.roci_elev: CVLoDTransitionData(Scenes.ROOM_OF_CLOCKS, 0x01),
    ent_names.roci_gate: CVLoDTransitionData(Scenes.ROOM_OF_CLOCKS, 0x02),
    ent_names.roce_elev: CVLoDTransitionData(Scenes.CASTLE_KEEP_EXTERIOR, 0x02),

    # Clock Tower
    # ent_names.ctgc_abyss_door: CVLoDTransitionData(Scenes.CLOCK_TOWER_GEAR_CLIMB, 0x00),
    ent_names.ctgc_abyss_door: CVLoDTransitionData(Scenes.CLOCK_TOWER_GEAR_CLIMB, 0x02),
    ent_names.ctga_climb_door: CVLoDTransitionData(Scenes.CLOCK_TOWER_ABYSS, 0x00),
    ent_names.ctga_door_d:  CVLoDTransitionData(Scenes.CLOCK_TOWER_ABYSS, 0x01),
    ent_names.ctf_door_d: CVLoDTransitionData(Scenes.CLOCK_TOWER_ABYSS, 0x00),
    ent_names.ctf_end: CVLoDTransitionData(Scenes.CLOCK_TOWER_ABYSS, 0x03),

    # Castle Keep
    # CVLoDTransitionData(Scenes.Castle Keep, 0x00),
}


def get_warp_entrances(active_warp_list: list[str]) -> dict[str, str]:
    """Gets the names of all warp Entrances mapped to their destination Regions in a dictionary, ready to be added
    to the Menu Region."""

    # Add the Entrance to the starting stage, mapped to the starting stage's start Region.
    warp_entrances = {CVLOD_STAGE_INFO[active_warp_list[0]].start_region: "Start stage"}

    # Add the warp Entrances, each mapped to its destination stage's middle Region.
    for i in range(1, len(active_warp_list)):
        warp_entrances.update({CVLOD_STAGE_INFO[active_warp_list[i]].mid_region: f"Warp {i}"})

    # Return the complete mapping of destination Region names to Entrance names.
    return warp_entrances


def verify_entrances(options: CVLoDOptions, entrances: list[str],
                     active_stage_info: list[CVLoDActiveStage]) -> dict[str, str]:
    """Verifies which Entrances in a given list should be created. A dict will be returned with verified Entrance names
    mapped to their destination Region names, ready to be created with Region.add_exits."""
    verified_entrances = {}

    for ent in entrances:
        # Check if the Entrance is in the Entrance info dict. If it isn't, throw an error and don't add it.
        if ent not in CVLOD_ENTRANCE_INFO:
            logging.error(f"The Entrance \"{ent}\" is not in CVLOD_ENTRANCE_INFO. Please add it to create it properly.")
            continue

        # Check if the Entrance's stage is active, if it has a stage assigned. If the stage is not active, then throw
        # an error indicating such and don't add it.
        ent_stage_info = find_stage_in_list(CVLOD_ENTRANCE_INFO[ent].stage, active_stage_info)
        if CVLOD_ENTRANCE_INFO[ent].stage and not ent_stage_info:
            logging.error(f"The stage for the Entrance \"{ent}\" is not active. Are you sure this Entrance is for "
                          f"{CVLOD_ENTRANCE_INFO[ent].stage}?")
            continue

        # If it's a Hard Entrance, and Hard Logic is not on, don't add it.
        if CVLOD_ENTRANCE_INFO[ent].type == "hard" and not options.hard_logic:
            continue

        # If it's an Easy Entrance, and Hard Logic is on, don't add it.
        if CVLOD_ENTRANCE_INFO[ent].type == "easy" and options.hard_logic:
            continue

        # If it's a Cornell Villa Entrance and the Villa State is Reinhardt/Carrie's, or if it's a Reinhardt/Carrie
        # Entrance in the Villa state is Cornell's, don't add it.
        if (ent in CORNELL_VILLA_ENTRANCES and options.villa_state == VillaState.option_reinhardt_carrie) or \
                (ent in REIN_CARRIE_VILLA_ENTRANCES and options.villa_state == VillaState.option_cornell):
            continue

        # If the Entrance is a connection to a different stage, and we already established it's a stage Entrance, get
        # the corresponding other stage Region.
        if CVLOD_ENTRANCE_INFO[ent].stage_connection and ent_stage_info:
            # If the Entrance's stage connection is not in the stage's active info, don't add the Entrance.
            if CVLOD_ENTRANCE_INFO[ent].stage_connection not in ent_stage_info["connecting_stages"]:
                continue

            # If the stage connection has an associated Region, consider that the Entrance's destination Region.
            # Otherwise, we won't add it.
            if not ent_stage_info["connecting_stages"][CVLOD_ENTRANCE_INFO[ent].stage_connection][1]:
                continue
            destination = ent_stage_info["connecting_stages"][CVLOD_ENTRANCE_INFO[ent].stage_connection][1]

        # Otherwise, if the Entrance is not a stage connection at all, get the Entrance's regular defined exit Region
        # name.
        else:
            destination = CVLOD_ENTRANCE_INFO[ent].dest

        verified_entrances.update({destination: ent})

    return verified_entrances
