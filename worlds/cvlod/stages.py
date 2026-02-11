import logging

from .data import reg_names, ent_names, loc_names
from .options import CVLoDOptions, WarpOrder, StageLayout, VillaBranchingPaths, CastleCenterBranchingPaths
from .data.enums import Scenes, StageIDs, StageNames

from BaseClasses import Region
from typing import TYPE_CHECKING, NamedTuple, TypedDict

if TYPE_CHECKING:
    from . import CVLoDWorld, CVLoDOptions


class CVLoDRegionData(TypedDict):
    locations: list[str]  # List of Locations to add to the Region when the Region is added.
    entrances: list[str]  # List of Entrances to add to the Region when the Region is added.


class CVLoDStageData(NamedTuple):
    start_region: str  # The AP Region that the start of the stage is in. Used for connecting the previous stage's end
    # and alternate end (if it exists) AP Entrances to the start of the next one.
    start_entrance: str  # The AP Entrance that leads out of this stage from the start of it, if one exists.
    start_scene_id: int  # The scene ID that the start of the stage is in.
    start_spawn_id: int  # The player spawn location ID for the start of the stage. This and "start scene id" are both
    # written to the previous stage's end loading zone to make it send the player to the next stage
    # in the slot's determined stage order.
    start_zone_id: int | None  # ID for the loading zone in the scene that takes the player back a prior stage normally.
    mid_region: str  # The AP Region that the stage's middle warp point is in. Used for connecting the warp AP Entrances
    # after the starting stage to where they should be connecting to.
    mid_scene_id: int  # The scene ID that the stage's middle warp point is in.
    mid_spawn_id: int  # The player spawn location ID for the stage's middle warp point. This and "mid scene id" are
    # both written to the warp menu code to make it send the player to where they should be.
    end_region: str  # The AP Region that the end of the stage is in. Used for connecting the next stage's beginning
    # AP Entrance (if it exists) to the end of the previous one.
    end_entrance: str # The primary AP Entrance that leads out of this stage from the end of it, if one exists.
    end_scene_id: int  # The scene ID that the end of the stage is in.
    end_spawn_id: int  # The player spawn location ID for the end of the stage. This and "end map id" are both written
    end_zone_id: int | None  # ID for the loading zone in the scene that takes the player to the next stage normally.
    id_number: int  # Internal ID number for this stage that the game uses in a few places. This apworld also uses it
                    # for stuff like player options.
    regions: dict[str, CVLoDRegionData]  # Info for each AP Region that make up the stage. If the stage is one of the
    # slot's active stages, its Regions and their corresponding Locations and Entrances will all be created.


MISC_REGIONS = {
    reg_names.menu: CVLoDRegionData(locations=[],
                                    entrances=[]),

    reg_names.renon: CVLoDRegionData(locations=[loc_names.renon1,
                                                loc_names.renon2,
                                                loc_names.renon3,
                                                loc_names.renon4,
                                                loc_names.renon5,
                                                loc_names.renon6,
                                                loc_names.renon7],
                                     entrances=[])
}

CVLOD_STAGE_INFO = {
    StageNames.FOGGY:
        CVLoDStageData(reg_names.fld_above, "", Scenes.FOGGY_LAKE_ABOVE_DECKS, 0x00, None,
                       reg_names.flb_below, Scenes.FOGGY_LAKE_BELOW_DECKS, 0x02,
                       reg_names.flp_pier, ent_names.flp_end, Scenes.FOGGY_LAKE_PIER, 0x01, 0,
                       StageIDs.FOGGY,
                       # Above Decks
                       {reg_names.fld_above: CVLoDRegionData(locations=[loc_names.fld_forecast_port,
                                                                        loc_names.fld_forecast_starboard,
                                                                        loc_names.fld_foremast_lower,
                                                                        loc_names.fld_stairs_port,
                                                                        loc_names.fld_stairs_starboard,
                                                                        loc_names.fld_net_port,
                                                                        loc_names.fld_net_starboard,
                                                                        loc_names.fld_mainmast_base,
                                                                        loc_names.fld_near_door,
                                                                        loc_names.fld_near_block_l,
                                                                        loc_names.fld_near_block_r,
                                                                        loc_names.fld_above_door,
                                                                        loc_names.fld_stern_port,
                                                                        loc_names.fld_stern_starboard,
                                                                        loc_names.fld_poop_port_crates,
                                                                        loc_names.fld_poop_starboard_crates,
                                                                        loc_names.fld_mainmast_top,
                                                                        loc_names.fld_jiggermast,
                                                                        loc_names.fld_foremast_upper_port,
                                                                        loc_names.fld_foremast_upper_starboard],
                                                             entrances=[ent_names.fld_to_below]),

                        # Below Decks
                        reg_names.flb_below: CVLoDRegionData(locations=[loc_names.flb_hallway_l,
                                                                        loc_names.flb_hallway_r,
                                                                        loc_names.flb_tall_crates,
                                                                        loc_names.flb_short_crates_l,
                                                                        loc_names.flb_short_crates_r],
                                                             entrances=[ent_names.flb_from_below,
                                                                        ent_names.flb_sink]),

                        # Pier
                        reg_names.flp_pier: CVLoDRegionData(locations=[loc_names.flp_pier_l,
                                                                       loc_names.flp_pier_m,
                                                                       loc_names.flp_pier_r,
                                                                       loc_names.event_fl_boss,
                                                                       loc_names.flp_statue_l,
                                                                       loc_names.flp_statue_r],
                                                            entrances=[ent_names.flp_end])}),

    StageNames.FOREST:
        CVLoDStageData(reg_names.forest_start, "", Scenes.FOREST_OF_SILENCE, 0x00, 0,
                       reg_names.forest_half_2, Scenes.FOREST_OF_SILENCE, 0x06,
                       reg_names.forest_end, ent_names.forest_end, Scenes.FOREST_OF_SILENCE, 0x01, 1,
                       StageIDs.FOREST,
                       {reg_names.forest_start: CVLoDRegionData(locations=[loc_names.forest_pier_center,
                                                                           loc_names.forest_pier_end,
                                                                           loc_names.event_forest_boss_1],
                                                                entrances=[ent_names.forest_king_skeleton_1]),

                        reg_names.forest_half_1: CVLoDRegionData(locations=[loc_names.forest_sypha_ne,
                                                                            loc_names.forest_sypha_se,
                                                                            loc_names.forest_sypha_nw,
                                                                            loc_names.forest_sypha_sw,
                                                                            loc_names.event_forest_boss_2,
                                                                            loc_names.forest_flea_trail,
                                                                            loc_names.forest_leap,
                                                                            loc_names.forest_descent,
                                                                            loc_names.forest_passage,
                                                                            loc_names.forest_child_ledge],
                                                                 entrances=[ent_names.forest_dbridge_gate]),

                        reg_names.forest_half_2: CVLoDRegionData(locations=[loc_names.forest_charnel_1,
                                                                            loc_names.forest_charnel_2,
                                                                            loc_names.forest_charnel_3,
                                                                            loc_names.event_forest_boss_3,
                                                                            loc_names.forest_pike,
                                                                            loc_names.forest_werewolf_pit,
                                                                            loc_names.forest_end_gate],
                                                                 entrances=[ent_names.forest_reverse_leap,
                                                                            ent_names.forest_final_switch]),

                        reg_names.forest_end: CVLoDRegionData(locations=[loc_names.event_forest_boss_4,
                                                                         loc_names.forest_skelly_mouth],
                                                              entrances=[ent_names.forest_end])}),

    StageNames.C_WALL:
        CVLoDStageData(reg_names.cw_start, ent_names.cw_start, Scenes.CASTLE_WALL_MAIN, 0x00, 0,
                       reg_names.cw_start, Scenes.CASTLE_WALL_MAIN, 0x08,
                       reg_names.cw_exit, ent_names.cw_end, Scenes.CASTLE_WALL_MAIN, 0x05, 5,
                       StageIDs.C_WALL,
                       # Main
                       {reg_names.cw_start: CVLoDRegionData(locations=[],
                                                            entrances=[ent_names.cw_start,
                                                                       ent_names.cw_portcullis_c,
                                                                       ent_names.cw_rt_door_b,
                                                                       ent_names.cw_lt_door_b]),

                        reg_names.cw_dragon_sw: CVLoDRegionData(locations=[loc_names.cw_dragon_sw,
                                                                           loc_names.event_cw_boss,
                                                                           loc_names.event_cw_right],
                                                                entrances=[ent_names.cw_rt_door_t,
                                                                           ent_names.cw_dragon_drop]),

                        reg_names.cw_save_ramp: CVLoDRegionData(locations=[loc_names.cw_save_slab1,
                                                                           loc_names.cw_save_slab2,
                                                                           loc_names.cw_save_slab3,
                                                                           loc_names.cw_save_slab4,
                                                                           loc_names.cw_save_slab5],
                                                                entrances=[ent_names.cw_save_drop]),

                        reg_names.cw_descent: CVLoDRegionData(locations=[loc_names.cw_rrampart,
                                                                         loc_names.cw_lrampart,
                                                                         loc_names.cw_pillar,
                                                                         loc_names.cw_shelf,
                                                                         loc_names.cw_shelf_torch],
                                                              entrances=[ent_names.cw_desc_drop]),

                        reg_names.cw_drac_sw: CVLoDRegionData(locations=[loc_names.cw_drac_sw,
                                                                         loc_names.cw_drac_slab1,
                                                                         loc_names.cw_drac_slab2,
                                                                         loc_names.cw_drac_slab3,
                                                                         loc_names.cw_drac_slab4,
                                                                         loc_names.cw_drac_slab5,
                                                                         loc_names.event_cw_left],
                                                              entrances=[ent_names.cw_lt_door_t,
                                                                         ent_names.cw_drac_drop,
                                                                         ent_names.cw_drac_leap]),

                        reg_names.cw_exit: CVLoDRegionData(locations=[loc_names.cw_ground_left,
                                                                      loc_names.cw_ground_middle,
                                                                      loc_names.cw_ground_right],
                                                           entrances=[ent_names.cw_end]),

                        # Right Tower
                        reg_names.cwr_rtower: CVLoDRegionData(locations=[loc_names.cwr_bottom,
                                                                         loc_names.cwr_top],
                                                              entrances=[ent_names.cwr_bottom,
                                                                         ent_names.cwr_top]),

                        # Left Tower
                        reg_names.cwl_ltower: CVLoDRegionData(locations=[loc_names.cwl_bottom,
                                                                         loc_names.cwl_bridge],
                                                              entrances=[ent_names.cwl_bottom,
                                                                         ent_names.cwl_top])}),

    StageNames.VILLA:
        CVLoDStageData(reg_names.villafy_start, ent_names.villafy_start, Scenes.VILLA_FRONT_YARD, 0x00, 0,
                       reg_names.villala_storeroom, Scenes.VILLA_LIVING_AREA, 0x04,
                       reg_names.villac_crypt_i, ent_names.villac_end_r, Scenes.VILLA_CRYPT, 0x02, 4,
                       StageIDs.VILLA,
                       # Front yard
                       {reg_names.villafy_start: CVLoDRegionData(locations=[loc_names.villafy_outer_gate_l,
                                                                            loc_names.villafy_outer_gate_r,
                                                                            loc_names.villafy_inner_gate],
                                                                 entrances=[ent_names.villafy_start,
                                                                            ent_names.villafy_dog_gates]),

                        reg_names.villafy_front_yard: CVLoDRegionData(locations=[loc_names.villafy_gate_marker,
                                                                                 loc_names.villafy_villa_marker],
                                                                      entrances=[ent_names.villafy_fountain_pillar,
                                                                                 ent_names.villafy_front_doors]),

                        reg_names.villafy_fountain: CVLoDRegionData(locations=[loc_names.villafy_fountain_fl,
                                                                               loc_names.villafy_fountain_fr,
                                                                               loc_names.villafy_fountain_ml,
                                                                               loc_names.villafy_fountain_mr,
                                                                               loc_names.villafy_fountain_rl,
                                                                               loc_names.villafy_fountain_rr,
                                                                               loc_names.villafy_fountain_shine],
                                                                    entrances=[]),

                        # Foyer
                        reg_names.villafo_foyer: CVLoDRegionData(locations=[loc_names.villafo_front_r,
                                                                            loc_names.villafo_front_l,
                                                                            loc_names.villafo_mid_l,
                                                                            loc_names.villafo_mid_r,
                                                                            loc_names.villafo_rear_r,
                                                                            loc_names.villafo_rear_l,
                                                                            loc_names.event_villa_boss_1,
                                                                            loc_names.villafo_pot_r,
                                                                            loc_names.villafo_pot_l,
                                                                            loc_names.villafo_sofa,
                                                                            loc_names.villafo_chandelier1,
                                                                            loc_names.villafo_chandelier2,
                                                                            loc_names.villafo_chandelier3,
                                                                            loc_names.villafo_chandelier4,
                                                                            loc_names.villafo_chandelier5],
                                                                 entrances=[ent_names.villafo_front_doors,
                                                                            ent_names.villafo_to_serv_door,
                                                                            ent_names.villafo_to_rose_garden]),

                        reg_names.villafo_serv_recep: CVLoDRegionData(locations=[loc_names.villafo_serv_ent],
                                                                      entrances=[ent_names.villafo_from_serv_door,
                                                                                 ent_names.villafo_serv_exit]),

                        reg_names.villafo_garden: CVLoDRegionData(locations=[loc_names.villafo_6am_roses,
                                                                             loc_names.event_villa_rosa],
                                                                  entrances=[ent_names.villafo_from_rose_garden,
                                                                             ent_names.villafo_living_door]),

                        # Living Area
                        reg_names.villala_living: CVLoDRegionData(locations=[loc_names.villala_hallway_stairs,
                                                                             loc_names.villala_hallway_l,
                                                                             loc_names.villala_hallway_r,
                                                                             loc_names.event_villa_boss_2,
                                                                             loc_names.villala_vincent,
                                                                             loc_names.villala_slivingroom_table_l,
                                                                             loc_names.villala_slivingroom_table_r,
                                                                             loc_names.villala_slivingroom_mirror,
                                                                             loc_names.villala_mary,
                                                                             loc_names.event_villa_boss_3,
                                                                             loc_names.villala_diningroom_roses,
                                                                             loc_names.villala_llivingroom_pot_r,
                                                                             loc_names.villala_llivingroom_pot_l,
                                                                             loc_names.villala_llivingroom_painting,
                                                                             loc_names.villala_llivingroom_light,
                                                                             loc_names.villala_llivingroom_lion,
                                                                             loc_names.villala_exit_knight],
                                                                  entrances=[ent_names.villala_rose_door,
                                                                             ent_names.villala_maze_doors,
                                                                             ent_names.villala_archives,
                                                                             ent_names.villala_to_storeroom
                                                                             # ent_names.villala_renon,
                                                                             ]),

                        reg_names.villala_storeroom: CVLoDRegionData(locations=[loc_names.villala_storeroom_l,
                                                                                loc_names.villala_storeroom_r,
                                                                                loc_names.villala_storeroom_s],
                                                                     entrances=[ent_names.villala_from_storeroom]),

                        reg_names.villala_archives: CVLoDRegionData(locations=[loc_names.villala_archives_table,
                                                                               loc_names.villala_archives_rear],
                                                                    entrances=[]),

                        # Maze Garden
                        reg_names.villam_maze_ent_m: CVLoDRegionData(locations=[],
                                                                     entrances=[ent_names.villam_back_doors,
                                                                                ent_names.villam_to_main_maze_gate]),

                        reg_names.villam_maze_f: CVLoDRegionData(locations=[loc_names.event_villa_child,
                                                                            loc_names.villam_malus_torch,
                                                                            loc_names.villam_malus_bush,
                                                                            loc_names.villam_fplatform,
                                                                            loc_names.villam_frankieturf_l,
                                                                            loc_names.villam_frankieturf_r,
                                                                            loc_names.villam_frankieturf_ru],
                                                                 entrances=[ent_names.villam_from_main_maze_gate,
                                                                            ent_names.villam_copper_door,
                                                                            ent_names.villam_front_divide]),

                        reg_names.villam_maze_r: CVLoDRegionData(locations=[loc_names.villam_hole_de,
                                                                            loc_names.villam_child_de,
                                                                            loc_names.villam_rplatform_f,
                                                                            loc_names.villam_rplatform_r,
                                                                            loc_names.villam_rplatform_de,
                                                                            loc_names.villam_exit_de],
                                                                 entrances=[ent_names.villam_rear_escape,
                                                                            ent_names.villam_thorn_fence,
                                                                            ent_names.villam_copper_skip_c,
                                                                            ent_names.villam_copper_skip_o,
                                                                            ent_names.villam_rear_divide]),

                        reg_names.villam_garden_f: CVLoDRegionData(locations=[loc_names.villam_fgarden_f,
                                                                              loc_names.villam_fgarden_mf,
                                                                              loc_names.villam_fgarden_mr,
                                                                              loc_names.villam_fgarden_r],
                                                                   entrances=[]),

                        reg_names.villam_serv_path: CVLoDRegionData(locations=[loc_names.villam_serv_path_l,
                                                                               loc_names.villam_serv_path_sl,
                                                                               loc_names.villam_serv_path_sr],
                                                                    entrances=[ent_names.villam_from_servant_gate,
                                                                               ent_names.villam_path_escape]),

                        reg_names.villam_maze_ent_s: CVLoDRegionData(locations=[],
                                                                     entrances=[ent_names.villam_to_servant_gate,
                                                                                ent_names.villam_serv_door]),

                        reg_names.villam_crypt_e: CVLoDRegionData(locations=[loc_names.villam_crypt_ent,
                                                                             loc_names.villam_crypt_upstream],
                                                                  entrances=[ent_names.villam_bridge_door,
                                                                             ent_names.villam_crypt_door]),

                        # Crypt
                        reg_names.villac_crypt_i: CVLoDRegionData(locations=[loc_names.villac_ent_l,
                                                                             loc_names.villac_ent_r,
                                                                             loc_names.villac_wall_l,
                                                                             loc_names.villac_wall_r,
                                                                             loc_names.villac_coffin_l,
                                                                             loc_names.villac_coffin_r,
                                                                             loc_names.event_villa_boss_4,
                                                                             loc_names.event_villa_boss_5,
                                                                             loc_names.event_villa_boss_6],
                                                                  entrances=[ent_names.villac_door,
                                                                             ent_names.villac_end_r,
                                                                             ent_names.villac_end_ca,
                                                                             ent_names.villac_end_co])}),

    StageNames.TUNNEL:
        CVLoDStageData(reg_names.tunnel_start, ent_names.tunnel_start_warp, Scenes.TUNNEL, 0x00, None,
                       reg_names.tunnel_end, Scenes.TUNNEL, 0x04,
                       reg_names.tunnelb_arena, ent_names.tunnelb_end, Scenes.ALGENIE_MEDUSA_ARENA, 0x41, 1,
                       StageIDs.TUNNEL,
                       # Main
                       {reg_names.tunnel_start: CVLoDRegionData(locations=[loc_names.tunnel_landing,
                                                                           loc_names.tunnel_landing_rc],
                                                                entrances=[ent_names.tunnel_start_warp,
                                                                           ent_names.tunnel_cutscene]),

                        reg_names.tunnel_main: CVLoDRegionData(locations=[loc_names.tunnel_stone_alcove_r,
                                                                          loc_names.tunnel_stone_alcove_l,
                                                                          loc_names.tunnel_twin_arrows,
                                                                          loc_names.tunnel_arrows_rock1,
                                                                          loc_names.tunnel_arrows_rock2,
                                                                          loc_names.tunnel_arrows_rock3,
                                                                          loc_names.tunnel_arrows_rock4,
                                                                          loc_names.tunnel_arrows_rock5,
                                                                          loc_names.tunnel_lonesome_bucket,
                                                                          loc_names.tunnel_lbucket_mdoor_l,
                                                                          loc_names.tunnel_lbucket_quag,
                                                                          loc_names.tunnel_bucket_quag_rock1,
                                                                          loc_names.tunnel_bucket_quag_rock2,
                                                                          loc_names.tunnel_bucket_quag_rock3,
                                                                          loc_names.tunnel_lbucket_albert,
                                                                          loc_names.tunnel_albert_camp,
                                                                          loc_names.tunnel_albert_quag,
                                                                          loc_names.tunnel_gondola_rc_sdoor_l,
                                                                          loc_names.tunnel_gondola_rc_sdoor_m,
                                                                          loc_names.tunnel_gondola_rc_sdoor_r,
                                                                          loc_names.tunnel_gondola_rc,
                                                                          loc_names.tunnel_rgondola_station,
                                                                          loc_names.tunnel_gondola_transfer],
                                                               entrances=[  # ent_names.tunnel_start_renon,
                                                                   ent_names.tunnel_gondolas]),

                        reg_names.tunnel_end: CVLoDRegionData(locations=[loc_names.tunnel_corpse_bucket_quag,
                                                                         loc_names.tunnel_corpse_bucket_mdoor_l,
                                                                         loc_names.tunnel_corpse_bucket_mdoor_r,
                                                                         loc_names.tunnel_shovel_quag_start,
                                                                         loc_names.tunnel_exit_quag_start,
                                                                         loc_names.tunnel_shovel_quag_end,
                                                                         loc_names.tunnel_exit_quag_end,
                                                                         loc_names.tunnel_shovel,
                                                                         loc_names.tunnel_shovel_save,
                                                                         loc_names.tunnel_shovel_mdoor_c,
                                                                         loc_names.tunnel_shovel_mdoor_l,
                                                                         loc_names.tunnel_shovel_mdoor_r,
                                                                         loc_names.tunnel_shovel_sdoor_l,
                                                                         loc_names.tunnel_shovel_sdoor_m,
                                                                         loc_names.tunnel_shovel_sdoor_r],
                                                              entrances=[  # ent_names.tunnel_end_renon,
                                                                  ent_names.tunnel_reverse,
                                                                  ent_names.tunnel_boss_door]),

                        # Boss Arena
                        reg_names.tunnelb_arena: CVLoDRegionData(locations=[loc_names.event_tunnel_boss],
                                                                 entrances=[ent_names.tunnelb_return,
                                                                            ent_names.tunnelb_end])}),

    StageNames.WATERWAY:
        CVLoDStageData(reg_names.uw_main, ent_names.uw_start_warp, Scenes.WATERWAY, 0x00, None,
                       reg_names.uw_main, Scenes.WATERWAY, 0x04,
                       reg_names.uwb_arena, ent_names.uwb_end, Scenes.ALGENIE_MEDUSA_ARENA, 0x81, 3,
                       StageIDs.WATERWAY,
                       # Main
                       {reg_names.uw_main: CVLoDRegionData(locations=[loc_names.uw_near_ent,
                                                                      loc_names.uw_across_ent,
                                                                      loc_names.uw_first_ledge1,
                                                                      loc_names.uw_first_ledge2,
                                                                      loc_names.uw_first_ledge3,
                                                                      loc_names.uw_first_ledge4,
                                                                      loc_names.uw_first_ledge5,
                                                                      loc_names.uw_first_ledge6,
                                                                      loc_names.uw_poison_parkour,
                                                                      loc_names.event_uw_boss_1,
                                                                      loc_names.uw_waterfall_ledge,
                                                                      loc_names.uw_waterfall_child,
                                                                      loc_names.uw_carrie1,
                                                                      loc_names.uw_carrie2,
                                                                      loc_names.uw_bricks_save,
                                                                      loc_names.uw_above_skel_ledge,
                                                                      loc_names.uw_in_skel_ledge1,
                                                                      loc_names.uw_in_skel_ledge2,
                                                                      loc_names.uw_in_skel_ledge3],
                                                           entrances=[ent_names.uw_start_warp,
                                                                      ent_names.uw_final_waterfall,
                                                                      # ent_names.uw_renon
                                                                      ]),

                        reg_names.uw_end: CVLoDRegionData(locations=[],
                                                          entrances=[ent_names.uw_boss_door]),

                        # Boss Arena
                        reg_names.uwb_arena: CVLoDRegionData(locations=[loc_names.event_uw_boss_2],
                                                             entrances=[ent_names.uwb_return,
                                                                        ent_names.uwb_end])}),

    StageNames.OUTER:
        CVLoDStageData(reg_names.towf_face_climb, ent_names.towf_start_warp, Scenes.THE_OUTER_WALL, 0x00, None,
                       reg_names.towse_slaughter_ext_f, Scenes.THE_OUTER_WALL, 0x0F,
                       reg_names.towfr_end, ent_names.towfr_end, Scenes.FAN_MEETING_ROOM, 0xC2, 2,
                       StageIDs.OUTER,
                       # Face (Climb)
                       {reg_names.towf_face_climb: CVLoDRegionData(locations=[loc_names.towf_start_rear,
                                                                              loc_names.towf_start_front,
                                                                              loc_names.towf_start_entry_l,
                                                                              loc_names.towf_start_entry_r,
                                                                              loc_names.towf_start_climb_b,
                                                                              loc_names.towf_start_climb_t,
                                                                              loc_names.towf_start_elevator_l,
                                                                              loc_names.towf_start_elevator_r],
                                                                   entrances=[ent_names.towf_start_warp,
                                                                              ent_names.towf_leap,
                                                                              ent_names.towf_ascent_elev]),

                        # Slaughterhouse Exterior (front side)
                        reg_names.towse_slaughter_ext_f: CVLoDRegionData(locations=[loc_names.towse_pillar_l,
                                                                                    loc_names.towse_pillar_r,
                                                                                    loc_names.towse_eagle,
                                                                                    loc_names.towse_saws_door_l,
                                                                                    loc_names.towse_saws_door_r],
                                                                         entrances=[ent_names.towse_slaughter_elev,
                                                                                    ent_names.towse_pillar,
                                                                                    ent_names.towse_slaughter_door]),

                        # Slaughterhouse Interior
                        reg_names.towsi_slaughter_int: CVLoDRegionData(locations=[loc_names.event_tow_switch],
                                                                       entrances=[ent_names.towsi_door]),

                        # Slaughterhouse Exterior (rear side)
                        reg_names.towse_slaughter_ext_r: CVLoDRegionData(
                            locations=[loc_names.towse_child,
                                       loc_names.towse_key_ledge,
                                       loc_names.towse_key_entry_l,
                                       loc_names.towse_key_entry_r,
                                       loc_names.towse_key_alcove,
                                       loc_names.towse_locked_door_l,
                                       loc_names.towse_locked_door_r,
                                       loc_names.towse_half_arch_under,
                                       loc_names.towse_half_arch_between,
                                       loc_names.towse_half_arch_secret],
                            entrances=[ent_names.towse_return,
                                       ent_names.towse_to_wall_door]),

                        reg_names.towse_key_hall: CVLoDRegionData(locations=[],
                                                                  entrances=[ent_names.towse_from_wall_door,
                                                                             ent_names.towse_key_elev]),

                        # Face (descent)
                        reg_names.towf_face_desc: CVLoDRegionData(locations=[loc_names.towf_retract_elevator_l,
                                                                             loc_names.towf_retract_elevator_r,
                                                                             loc_names.towf_retract_shimmy_start,
                                                                             loc_names.towf_retract_shimmy_mid,
                                                                             loc_names.towf_boulders_door_l,
                                                                             loc_names.towf_boulders_door_r],
                                                                  entrances=[ent_names.towf_descent_elev,
                                                                             ent_names.towf_bowling_door]),

                        # Bowling Alley
                        reg_names.towb_bowling: CVLoDRegionData(locations=[],
                                                                entrances=[ent_names.towb_door,
                                                                           ent_names.towb_elev]),

                        # Harpy Rooftops
                        reg_names.towh_harpy_roof: CVLoDRegionData(locations=[loc_names.towh_boulders_elevator_l,
                                                                             loc_names.towh_boulders_elevator_r,
                                                                             loc_names.towh_near_boulders_exit,
                                                                             loc_names.towh_slide_start,
                                                                             loc_names.towh_slide_first_u,
                                                                             loc_names.towh_slide_first_l,
                                                                             loc_names.towh_slide_second,
                                                                             loc_names.event_tow_boss],
                                                                  entrances=[ent_names.towh_bowling_elev,
                                                                             ent_names.towh_drop]),

                        reg_names.towfr_end: CVLoDRegionData(locations=[],
                                                             entrances=[ent_names.towfr_end])}),

    StageNames.ART:
        CVLoDStageData(reg_names.atm_museum, ent_names.atm_start, Scenes.ART_TOWER_MUSEUM, 0x00, 0,
                       reg_names.atm_museum, Scenes.ART_TOWER_MUSEUM, 0x02,
                       reg_names.atc_conservatory, ent_names.atc_end, Scenes.ART_TOWER_CONSERVATORY, 0x01, 1,
                       StageIDs.ART,
                       # Museum
                       {reg_names.atm_museum: CVLoDRegionData(locations=[loc_names.atm_ww,
                                                                         loc_names.atm_nw_ped,
                                                                         loc_names.atm_nw_corner,
                                                                         loc_names.atm_sw_alcove_1,
                                                                         loc_names.atm_sw_alcove_2,
                                                                         loc_names.atm_sw_alcove_4,
                                                                         loc_names.atm_sw_alcove_6,
                                                                         loc_names.atm_sw_key_ped,
                                                                         loc_names.atm_sw_key_corner,
                                                                         loc_names.atm_se,
                                                                         loc_names.atm_ne_ped,
                                                                         loc_names.atm_ne_near,
                                                                         loc_names.atm_ee_plat_1,
                                                                         loc_names.atm_ee_plat_2,
                                                                         loc_names.atm_ee_key_ped,
                                                                         loc_names.atm_ee_key_corner],
                                                              entrances=[ent_names.atm_start,
                                                                         ent_names.atm_to_door_1,
                                                                         ent_names.atm_skip_door_1]),

                        reg_names.atm_middle: CVLoDRegionData(locations=[],
                                                              entrances=[ent_names.atm_from_door_1,
                                                                         ent_names.atm_to_door_2]),

                        reg_names.atm_middle_door: CVLoDRegionData(locations=[],
                                                                   entrances=[ent_names.atm_from_door_2,
                                                                              ent_names.atm_hall_ent]),

                        # Conservatory
                        reg_names.atc_conservatory: CVLoDRegionData(locations=[loc_names.atc_sw_statue_l,
                                                                               loc_names.atc_sw_statue_r,
                                                                               loc_names.atc_ne_statue_l,
                                                                               loc_names.atc_ne_statue_r,
                                                                               loc_names.atc_organ,
                                                                               loc_names.atc_pillar_l,
                                                                               loc_names.atc_pillar_r,
                                                                               loc_names.atc_doorway_l,
                                                                               loc_names.atc_doorway_m,
                                                                               loc_names.atc_doorway_r,
                                                                               loc_names.atc_balcony_save,
                                                                               loc_names.atc_bp_f,
                                                                               loc_names.atc_bp_r],
                                                                    entrances=[ent_names.atc_bottom,
                                                                               ent_names.atc_end])}),

    StageNames.RUINS:
        CVLoDStageData(reg_names.torm_maze_main, ent_names.torm_start, Scenes.RUINS_DOOR_MAZE, 0x00, 0,
                       reg_names.torc_dark, Scenes.RUINS_DARK_CHAMBERS, 0x02,
                       reg_names.torc_end, ent_names.torc_end, Scenes.RUINS_DARK_CHAMBERS, 0x01, 1,
                       StageIDs.RUINS,
                       # Door Maze
                       {reg_names.torm_maze_main: CVLoDRegionData(locations=[loc_names.torm_trap_side,
                                                                             loc_names.torm_trap_corner,
                                                                             loc_names.torm_b6,
                                                                             loc_names.torm_b4_corner,
                                                                             loc_names.torm_b4_statue,
                                                                             loc_names.torm_a3,
                                                                             loc_names.torm_b2,
                                                                             loc_names.torm_a1,
                                                                             loc_names.torm_d4,
                                                                             loc_names.torm_g4,
                                                                             loc_names.torm_g3_l,
                                                                             loc_names.torm_g3_r,
                                                                             loc_names.torm_g3_statue],
                                                                  entrances=[ent_names.torm_start,
                                                                             ent_names.torm_maze]),

                        reg_names.torm_maze_end: CVLoDRegionData(locations=[loc_names.torm_lookback_l,
                                                                            loc_names.torm_lookback_r,
                                                                            loc_names.torm_lookback_u],
                                                                 entrances=[ent_names.torm_burial_door]),

                        # Dark Chambers
                        reg_names.torc_dark: CVLoDRegionData(locations=[loc_names.torc_lfloor_f,
                                                                        loc_names.torc_lfloor_r,
                                                                        loc_names.torc_walkway_l,
                                                                        loc_names.torc_ufloor_rl,
                                                                        loc_names.torc_ufloor_m,
                                                                        loc_names.torc_ufloor_fr,
                                                                        loc_names.torc_meat_l,
                                                                        loc_names.torc_meat_r,
                                                                        loc_names.torc_walkway_u,
                                                                        loc_names.torc_aries,
                                                                        loc_names.torc_taurus,
                                                                        loc_names.torc_leo,
                                                                        loc_names.torc_sagittarius],
                                                             entrances=[ent_names.torc_maze_door,
                                                                        ent_names.torc_climb]),

                        reg_names.torc_end: CVLoDRegionData(locations=[loc_names.torc_across_exit,
                                                                       loc_names.torc_near_exit],
                                                            entrances=[ent_names.torc_end])}),

    StageNames.CENTER:
        CVLoDStageData(reg_names.ccfr_fan_room, "", Scenes.FAN_MEETING_ROOM, 0x40, 0,
                       reg_names.ccb_torture_chamber, Scenes.CASTLE_CENTER_BASEMENT, 0x06,
                       reg_names.ccte_elev_top, ent_names.ccte_exit_r, Scenes.CASTLE_CENTER_TOP_ELEV, 0x01, 1,
                       StageIDs.CENTER,
                       # Fan room
                       {reg_names.ccfr_fan_room: CVLoDRegionData(locations=[],
                                                                 entrances=[ent_names.ccfr_door_r]),
                       # Basement
                        reg_names.ccb_basement: CVLoDRegionData(locations=[loc_names.ccb_skel_hallway_ent,
                                                                           loc_names.ccb_skel_hallway_jun,
                                                                           loc_names.ccb_skel_hallway_tc,
                                                                           loc_names.ccb_skel_hallway_ba,
                                                                           loc_names.ccb_behemoth_l_ff,
                                                                           loc_names.ccb_behemoth_l_mf,
                                                                           loc_names.ccb_behemoth_l_mr,
                                                                           loc_names.ccb_behemoth_l_fr,
                                                                           loc_names.ccb_behemoth_r_ff,
                                                                           loc_names.ccb_behemoth_r_mf,
                                                                           loc_names.ccb_behemoth_r_mr,
                                                                           loc_names.ccb_behemoth_r_fr,
                                                                           loc_names.ccb_behemoth_crate1,
                                                                           loc_names.ccb_behemoth_crate2,
                                                                           loc_names.ccb_behemoth_crate3,
                                                                           loc_names.ccb_behemoth_crate4,
                                                                           loc_names.ccb_behemoth_crate5],
                                                                entrances=[ent_names.ccb_tc_to_door,
                                                                           ent_names.ccb_wall,
                                                                           ent_names.ccb_stairs]),

                        reg_names.ccb_behemoth_crack: CVLoDRegionData(locations=[loc_names.event_cc_crystal,
                                                                                 loc_names.event_cc_boss_1,
                                                                                 loc_names.event_cc_boss_2],
                                                                      entrances=[
                                                                          # ent_names.cc_renon,
                                                                      ]),

                        reg_names.ccb_torture_chamber: CVLoDRegionData(locations=[loc_names.ccb_mandrag_shelf_l,
                                                                                  loc_names.ccb_mandrag_shelf_r,
                                                                                  loc_names.ccb_torture_rack,
                                                                                  loc_names.ccb_torture_rafters],
                                                                       entrances=[ent_names.ccb_tc_from_door]),

                        # Bottom Elevator Room
                        reg_names.ccbe_bottom_elevator: CVLoDRegionData(locations=[loc_names.ccbe_near_machine,
                                                                                   loc_names.ccbe_atop_machine,
                                                                                   loc_names.ccbe_stand1,
                                                                                   loc_names.ccbe_stand2,
                                                                                   loc_names.ccbe_stand3,
                                                                                   loc_names.ccbe_pipes,
                                                                                   loc_names.ccbe_switch,
                                                                                   loc_names.ccbe_staircase,
                                                                                   loc_names.event_cc_elevator],
                                                                        entrances=[ent_names.ccbe_upstairs,
                                                                                   ent_names.ccbe_downstairs,
                                                                                   ent_names.ccbe_elevator]),

                        # Factory Floor
                        reg_names.ccff_factory: CVLoDRegionData(locations=[loc_names.ccff_gears_side,
                                                                           loc_names.ccff_gears_mid,
                                                                           loc_names.ccff_gears_corner,
                                                                           loc_names.ccff_lizard_near_knight,
                                                                           loc_names.ccff_lizard_pit,
                                                                           loc_names.ccff_lizard_corner,
                                                                           loc_names.ccff_lizard_locker_nfr,
                                                                           loc_names.ccff_lizard_locker_nmr,
                                                                           loc_names.ccff_lizard_locker_nml,
                                                                           loc_names.ccff_lizard_locker_nfl,
                                                                           loc_names.ccff_lizard_locker_fl,
                                                                           loc_names.ccff_lizard_locker_fr,
                                                                           loc_names.ccff_lizard_slab1,
                                                                           loc_names.ccff_lizard_slab2,
                                                                           loc_names.ccff_lizard_slab3,
                                                                           loc_names.ccff_lizard_slab4],
                                                                entrances=[ent_names.ccff_carpet_stairs,
                                                                           ent_names.ccff_gear_stairs,
                                                                           ent_names.ccff_lizard_door]),

                        # Lizard Labs
                        reg_names.ccll_lizard_main: CVLoDRegionData(locations=[loc_names.ccll_brokenstairs_floor,
                                                                               loc_names.ccll_brokenstairs_save,
                                                                               loc_names.ccll_glassknight_l,
                                                                               loc_names.ccll_glassknight_r,
                                                                               loc_names.ccll_butlers_door,
                                                                               loc_names.ccll_butlers_side,
                                                                               loc_names.ccll_cwhall_butlerflames_past,
                                                                               loc_names.ccll_cwhall_flamethrower,
                                                                               loc_names.ccll_cwhall_cwflames,
                                                                               loc_names.ccll_heinrich],
                                                                    entrances=[ent_names.ccll_brokenstairs_door,
                                                                               ent_names.ccll_upper_wall_out,
                                                                               ent_names.ccll_heinrich_door]),

                        reg_names.ccll_lizard_crack: CVLoDRegionData(locations=[loc_names.ccll_cwhall_wall],
                                                                     entrances=[ent_names.ccll_library_passage,
                                                                                ent_names.ccll_upper_wall_in]),

                        # Library
                        reg_names.ccl_library: CVLoDRegionData(locations=[loc_names.ccl_bookcase,
                                                                          loc_names.event_cc_planets],
                                                               entrances=[ent_names.ccl_exit]),

                        # Invention Area
                        reg_names.ccia_nitro_liz: CVLoDRegionData(locations=[loc_names.ccia_nitro_crates,
                                                                             loc_names.ccia_nitro_shelf_h],
                                                                  entrances=[ent_names.ccia_lizard_door]),

                        reg_names.ccia_inventions: CVLoDRegionData(locations=[loc_names.ccia_stairs_knight,
                                                                              loc_names.ccia_maids_vase,
                                                                              loc_names.ccia_maids_outer,
                                                                              loc_names.ccia_maids_inner,
                                                                              loc_names.ccia_inventions_maids,
                                                                              loc_names.ccia_inventions_crusher,
                                                                              loc_names.ccia_inventions_famicart,
                                                                              loc_names.ccia_inventions_zeppelin,
                                                                              loc_names.ccia_inventions_round,
                                                                              loc_names.ccia_nitrohall_flamethrower,
                                                                              loc_names.ccia_nitrohall_torch,
                                                                              loc_names.ccia_nitro_shelf_i],
                                                                   entrances=[ent_names.ccia_stairs]),

                        # Top Elevator Room
                        reg_names.ccte_elev_top: CVLoDRegionData(locations=[],
                                                                 entrances=[ent_names.ccte_elevator,
                                                                            ent_names.ccte_exit_r,
                                                                            ent_names.ccte_exit_c])}),

    StageNames.SCIENCE:
        CVLoDStageData(reg_names.toscic_factory, ent_names.toscic_start, Scenes.SCIENCE_CONVEYORS, 0x00, 0,
                       reg_names.toscit_halls_main, Scenes.SCIENCE_LABS, 0x02,
                       reg_names.toscit_end, ent_names.toscit_end, Scenes.SCIENCE_LABS, 0x01, 1,
                       StageIDs.SCIENCE,
                       # Cube Factory
                       {reg_names.toscic_factory: CVLoDRegionData(locations=[loc_names.toscic_first,
                                                                             loc_names.toscic_second,
                                                                             loc_names.toscic_elevator],
                                                                  entrances=[ent_names.toscic_start,
                                                                             ent_names.toscic_elev]),

                        # Turret Halls
                        reg_names.toscit_halls_start: CVLoDRegionData(locations=[loc_names.toscit_lone_c,
                                                                                 loc_names.toscit_lone_rl,
                                                                                 loc_names.toscit_lone_rr],
                                                                      entrances=[ent_names.toscit_elev,
                                                                                 ent_names.toscit_lone_door]),

                        reg_names.toscit_halls_main: CVLoDRegionData(locations=[loc_names.toscit_sec_1,
                                                                                loc_names.toscit_sec_2,
                                                                                loc_names.toscit_sec_check_l,
                                                                                loc_names.toscit_sec_check_r,
                                                                                loc_names.toscit_25d_pipes,
                                                                                loc_names.toscit_25d_cover,
                                                                                loc_names.toscit_course_d1_l,
                                                                                loc_names.toscit_course_d1_r,
                                                                                loc_names.toscit_course_d2_l,
                                                                                loc_names.toscit_course_d2_r,
                                                                                loc_names.toscit_course_d3_l,
                                                                                loc_names.toscit_course_d3_c,
                                                                                loc_names.toscit_course_alcove,
                                                                                loc_names.toscit_course_end],
                                                                     entrances=[ent_names.toscit_to_ctrl_door]),

                        reg_names.toscit_end: CVLoDRegionData(locations=[loc_names.toscit_ctrl_fl,
                                                                         loc_names.toscit_ctrl_fr,
                                                                         loc_names.toscit_ctrl_l,
                                                                         loc_names.toscit_ctrl_r,
                                                                         loc_names.toscit_ctrl_rl,
                                                                         loc_names.toscit_ctrl_rr,
                                                                         loc_names.toscit_ctrl_interface_f,
                                                                         loc_names.toscit_ctrl_interface_rl,
                                                                         loc_names.toscit_ctrl_interface_rr],
                                                              entrances=[ent_names.toscit_from_ctrl_door,
                                                                         ent_names.toscit_end])}),

    StageNames.DUEL:
        CVLoDStageData(reg_names.dt_start, ent_names.dt_start, Scenes.DUEL_TOWER, 0x00, 0,
                       reg_names.dt_main, Scenes.DUEL_TOWER, 0x02,
                       reg_names.dt_end, ent_names.dt_end, Scenes.DUEL_TOWER, 0x01, 1,
                       StageIDs.DUEL,
                       {reg_names.dt_start: CVLoDRegionData(locations=[loc_names.event_dt_boss_1],
                                                            entrances=[ent_names.dt_start,
                                                                       ent_names.dt_drop]),

                        reg_names.dt_main: CVLoDRegionData(locations=[loc_names.dt_pre_sweeper_l,
                                                                      loc_names.dt_pre_sweeper_r,
                                                                      loc_names.event_dt_boss_2,
                                                                      loc_names.dt_werewolf_ledge,
                                                                      loc_names.dt_post_sweeper_l,
                                                                      loc_names.dt_post_sweeper_r,
                                                                      loc_names.dt_slant_l,
                                                                      loc_names.dt_slant_r,
                                                                      loc_names.dt_pinwheels_l,
                                                                      loc_names.dt_pinwheels_r,
                                                                      loc_names.dt_guards_l,
                                                                      loc_names.dt_guards_r,
                                                                      loc_names.event_dt_boss_3,
                                                                      loc_names.dt_werebull_l,
                                                                      loc_names.dt_werebull_r,
                                                                      loc_names.event_dt_boss_4],
                                                           entrances=[ent_names.dt_last]),

                        reg_names.dt_end: CVLoDRegionData(locations=[],
                                                          entrances=[ent_names.dt_end])}),

    StageNames.EXECUTION:
        CVLoDStageData(reg_names.toe_bottom, ent_names.toe_bottom_start, Scenes.EXECUTION_MAIN, 0x00, 0,
                       reg_names.toe_middle_i, Scenes.EXECUTION_MAIN, 0x02,
                       reg_names.toeu_ultimate, ent_names.toeu_end, Scenes.EXECUTION_SIDE_ROOMS_2, 0x03, 3,
                       StageIDs.EXECUTION,
                       {reg_names.toe_bottom: CVLoDRegionData(locations=[loc_names.toe_start_l,
                                                                         loc_names.toe_start_r,
                                                                         loc_names.toe_spike_alcove_l,
                                                                         loc_names.toe_spike_alcove_r,
                                                                         loc_names.toe_spike_platform_l,
                                                                         loc_names.toe_spike_platform_r],
                                                              entrances=[ent_names.toe_bottom_start,
                                                                         ent_names.toe_bottom_end]),

                        reg_names.toem_stones: CVLoDRegionData(locations=[loc_names.toem_stones_l,
                                                                          loc_names.toem_stones_r,
                                                                          loc_names.toem_walkway],
                                                               entrances=[ent_names.toem_start,
                                                                          ent_names.toem_end]),

                        reg_names.toeg_grates: CVLoDRegionData(locations=[loc_names.toeg_platform,
                                                                          loc_names.toeg_alcove_l,
                                                                          loc_names.toeg_alcove_r],
                                                               entrances=[ent_names.toeg_start,
                                                                          ent_names.toeg_side,
                                                                          ent_names.toeg_end]),

                        reg_names.toe_middle_i: CVLoDRegionData(locations=[loc_names.toe_renon_l,
                                                                           loc_names.toe_renon_r],
                                                                entrances=[ent_names.toe_side_drop,
                                                                           ent_names.toe_side]),

                        reg_names.toe_middle_k: CVLoDRegionData(locations=[loc_names.toe_knights],
                                                                entrances=[ent_names.toe_middle_start,
                                                                           ent_names.toe_middle_drop,
                                                                           ent_names.toe_middle_end]),

                        reg_names.toeb_balls: CVLoDRegionData(locations=[loc_names.toeb_midway_l,
                                                                         loc_names.toeb_midway_r,
                                                                         loc_names.toeb_corner],
                                                              entrances=[ent_names.toeb_start,
                                                                         ent_names.toeb_end]),

                        reg_names.toe_top: CVLoDRegionData(locations=[loc_names.toe_first_pillar,
                                                                      loc_names.toe_last_pillar,
                                                                      loc_names.toe_tower,
                                                                      loc_names.toe_top_platform],
                                                           entrances=[ent_names.toe_top_start,
                                                                      ent_names.toe_top_drop_start,
                                                                      ent_names.toe_top_drop_end,
                                                                      ent_names.toe_top_end]),

                        reg_names.toeu_ultimate: CVLoDRegionData(locations=[loc_names.toeu_fort_save,
                                                                            loc_names.toeu_fort_ibridge,
                                                                            loc_names.toeu_fort_left,
                                                                            loc_names.toeu_fort_lookout,
                                                                            loc_names.toeu_ult_l,
                                                                            loc_names.toeu_ult_r,
                                                                            loc_names.toeu_ult_crack,
                                                                            loc_names.toeu_jails,
                                                                            loc_names.toeu_end_l,
                                                                            loc_names.toeu_end_r],
                                                                 entrances=[ent_names.toeu_start,
                                                                            ent_names.toeu_end])}),

    StageNames.SORCERY:
        CVLoDStageData(reg_names.tosor_main, ent_names.tosor_start, Scenes.TOWER_OF_SORCERY, 0x00, 0,
                       reg_names.tosor_main, Scenes.TOWER_OF_SORCERY, 0x02,
                       reg_names.tosor_main, ent_names.tosor_end, Scenes.TOWER_OF_SORCERY, 0x01, 1,
                       StageIDs.SORCERY,
                       {reg_names.tosor_main: CVLoDRegionData(locations=[loc_names.tosor_icemen_l,
                                                                         loc_names.tosor_icemen_r,
                                                                         loc_names.tosor_archi,
                                                                         loc_names.tosor_side_isle,
                                                                         loc_names.tosor_mag_bridge,
                                                                         loc_names.tosor_lasers_m,
                                                                         loc_names.tosor_lasers_s,
                                                                         loc_names.tosor_climb_l,
                                                                         loc_names.tosor_climb_r,
                                                                         loc_names.tosor_climb_m,
                                                                         loc_names.tosor_ibridge,
                                                                         loc_names.tosor_super_1,
                                                                         loc_names.tosor_super_2,
                                                                         loc_names.tosor_super_3],
                                                              entrances=[ent_names.tosor_start,
                                                                         ent_names.tosor_end])}),

    StageNames.ROOM:
        CVLoDStageData(reg_names.roc_int, "", Scenes.ROOM_OF_CLOCKS, 0x00, 0,
                       reg_names.roc_int, Scenes.ROOM_OF_CLOCKS, 0x04,
                       reg_names.roc_int, ent_names.roci_gate, Scenes.ROOM_OF_CLOCKS, 0x02, 2,
                       StageIDs.ROOM,
                       {reg_names.roc_int: CVLoDRegionData(locations=[loc_names.roc_ent_l,
                                                                      loc_names.roc_ent_r,
                                                                      loc_names.roc_elev_r,
                                                                      loc_names.roc_elev_l,
                                                                      loc_names.roc_cont_r,
                                                                      loc_names.roc_cont_l,
                                                                      loc_names.roc_exit],
                                                           entrances=[ent_names.roci_elev,
                                                                      ent_names.roci_gate]),
                        reg_names.roc_ext: CVLoDRegionData(locations=[loc_names.event_roc_boss],
                                                           entrances=[ent_names.roce_elev])}),

    StageNames.CLOCK:
        CVLoDStageData(reg_names.ctgc_start, "", Scenes.CLOCK_TOWER_GEAR_CLIMB, 0x00, 0,
                       reg_names.ctga_abyss_near, Scenes.CLOCK_TOWER_ABYSS, 0x02,
                       reg_names.ctf_face, ent_names.ctf_end, Scenes.CLOCK_TOWER_FACE, 0x03, 1,
                       StageIDs.CLOCK,
                       # Gear Climb
                       {reg_names.ctgc_start: CVLoDRegionData(locations=[loc_names.ctgc_gearclimb_battery_slab1,
                                                                         loc_names.ctgc_gearclimb_battery_slab2,
                                                                         loc_names.ctgc_gearclimb_battery_slab3,
                                                                         loc_names.ctgc_gearclimb_battery_slab4,
                                                                         loc_names.ctgc_gearclimb_battery_slab5,
                                                                         loc_names.ctgc_gearclimb_battery_slab6,
                                                                         loc_names.ctgc_gearclimb_corner_r,
                                                                         loc_names.ctgc_gearclimb_corner_f,
                                                                         loc_names.ctgc_gearclimb_door_slab1,
                                                                         loc_names.ctgc_gearclimb_door_slab2,
                                                                         loc_names.ctgc_gearclimb_door_slab3],
                                                              entrances=[ent_names.ctgc_to_door_a]),

                        reg_names.ctgc_bpillars: CVLoDRegionData(locations=[loc_names.ctgc_bp_chasm_fl,
                                                                            loc_names.ctgc_bp_chasm_fr,
                                                                            loc_names.ctgc_bp_chasm_rl,
                                                                            loc_names.ctgc_bp_chasm_k],
                                                                 entrances=[ent_names.ctgc_from_door_a,
                                                                            ent_names.ctgc_to_door_b]),

                        reg_names.ctgc_bpillars_end: CVLoDRegionData(locations=[],
                                                                     entrances=[ent_names.ctgc_from_door_b,
                                                                                ent_names.ctgc_abyss_door]),

                        # Grand Abyss
                        reg_names.ctga_abyss_near: CVLoDRegionData(locations=[loc_names.ctga_near_floor,
                                                                              loc_names.ctga_near_climb],
                                                                   entrances=[ent_names.ctga_climb_door,
                                                                              ent_names.ctga_door_c,
                                                                              ent_names.ctga_door_c_skip]),

                        reg_names.ctga_abyss_far: CVLoDRegionData(locations=[loc_names.ctga_far_slab1,
                                                                             loc_names.ctga_far_slab2,
                                                                             loc_names.ctga_far_slab3,
                                                                             loc_names.ctga_far_slab4,
                                                                             loc_names.ctga_far_alcove],
                                                                  entrances=[ent_names.ctga_door_d,
                                                                             ent_names.ctga_door_c_reverse]),

                        # Face
                        reg_names.ctf_face: CVLoDRegionData(locations=[loc_names.ctf_clock,
                                                                       loc_names.ctf_walkway_end],
                                                            entrances=[ent_names.ctf_door_d,
                                                                       # ent_names.ctf_renon
                                                                       ent_names.ctf_door_e,
                                                                       ent_names.ctf_end]),

                        reg_names.ctf_engine: CVLoDRegionData(locations=[loc_names.ctf_engine_floor,
                                                                         loc_names.ctf_engine_furnace,
                                                                         loc_names.ctf_pendulums_l,
                                                                         loc_names.ctf_pendulums_r,
                                                                         loc_names.ctf_slope_slab1,
                                                                         loc_names.ctf_slope_slab2,
                                                                         loc_names.ctf_slope_slab3,
                                                                         loc_names.ctf_walkway_mid],
                                                              entrances=[])}),

    StageNames.KEEP:
        CVLoDStageData(reg_names.ck_main, "", Scenes.CASTLE_KEEP_EXTERIOR, 0x00, 0,
                       reg_names.ck_main, Scenes.CASTLE_KEEP_EXTERIOR, 0x01,
                       reg_names.ck_main, "", Scenes.CASTLE_KEEP_DRAC_CHAMBER, 0x00, None,
                       StageIDs.KEEP,
                       {reg_names.ck_main: CVLoDRegionData(locations=[loc_names.ck_renon_sw,
                                                                      loc_names.ck_renon_se,
                                                                      loc_names.ck_renon_nw,
                                                                      loc_names.ck_renon_ne,
                                                                      loc_names.event_ck_boss_1,
                                                                      loc_names.event_ck_boss_2,
                                                                      loc_names.ck_flame_l,
                                                                      loc_names.ck_flame_r,
                                                                      loc_names.ck_behind_drac,
                                                                      loc_names.ck_cube,
                                                                      loc_names.event_dracula],
                                                           entrances=[])}),
}

ALL_CVLOD_REGIONS = {**MISC_REGIONS,
                     **{reg: reg_info for stage, stage_info in CVLOD_STAGE_INFO.items()
                        for reg, reg_info in stage_info.regions.items()}}

STAGE_LAYOUT_PRESETS: dict[int, list[str]] = {
    StageLayout.option_cornell_only: [StageNames.FOGGY, StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA,
                                      StageNames.OUTER, StageNames.ART, StageNames.RUINS, StageNames.SCIENCE,
                                      StageNames.DUEL, StageNames.EXECUTION, StageNames.SORCERY, StageNames.ROOM,
                                      StageNames.CLOCK, StageNames.KEEP],
    StageLayout.option_reinhardt_only: [StageNames.FOGGY, StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA,
                                        StageNames.TUNNEL, StageNames.CENTER, StageNames.DUEL, StageNames.EXECUTION,
                                        StageNames.ROOM, StageNames.CLOCK, StageNames.KEEP],
    StageLayout.option_carrie_only: [StageNames.FOGGY, StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA,
                                     StageNames.WATERWAY, StageNames.CENTER, StageNames.SCIENCE, StageNames.SORCERY,
                                     StageNames.ROOM, StageNames.CLOCK, StageNames.KEEP],
    StageLayout.option_henry_only: [StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA, StageNames.TUNNEL,
                                    StageNames.WATERWAY, StageNames.OUTER],
    StageLayout.option_reinhardt_carrie: [StageNames.FOGGY, StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA,
                                          StageNames.TUNNEL, StageNames.WATERWAY, StageNames.CENTER,
                                          StageNames.DUEL, StageNames.EXECUTION, StageNames.SCIENCE,
                                          StageNames.SORCERY, StageNames.ROOM, StageNames.CLOCK, StageNames.KEEP],
    StageLayout.option_all: [StageNames.FOGGY, StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA,
                             StageNames.TUNNEL, StageNames.WATERWAY, StageNames.OUTER, StageNames.ART,
                             StageNames.RUINS, StageNames.CENTER, StageNames.DUEL, StageNames.EXECUTION,
                             StageNames.SCIENCE, StageNames.SORCERY, StageNames.ROOM, StageNames.CLOCK,
                             StageNames.KEEP]
}

VILLA_BRANCH_STAGE_MINIMUMS = {
    VillaBranchingPaths.option_one: 1,
    VillaBranchingPaths.option_two: 2,
    VillaBranchingPaths.option_three: 3,
    VillaBranchingPaths.option_three_with_cornell_path: 5
}

STAGE_NAME_ALIASES = {
    "foggy lake": StageNames.FOGGY,
    "foggy": StageNames.FOGGY,
    "lake": StageNames.FOGGY,
    "fl": StageNames.FOGGY,
    "ship": StageNames.FOGGY,
    "pirate": StageNames.FOGGY,
    "pirate ship": StageNames.FOGGY,
    "pirate ship of fools": StageNames.FOGGY,
    "channel": StageNames.FOGGY,
    "kalidus channel": StageNames.FOGGY,
    "galleon": StageNames.FOGGY,
    "galleon minerva": StageNames.FOGGY,
    "forest of silence": StageNames.FOREST,
    "forest": StageNames.FOREST,
    "silence": StageNames.FOREST,
    "silent": StageNames.FOREST,
    "silent forest": StageNames.FOREST,
    "fos": StageNames.FOREST,
    "woods": StageNames.FOREST,
    "ruvas forest": StageNames.FOREST,
    "misty forest road": StageNames.FOREST,
    "forest of doom": StageNames.FOREST,
    "forest of darkness": StageNames.FOREST,
    "forest of evil spirits": StageNames.FOREST,
    "forest of eternal night": StageNames.FOREST,
    "forest of jigramunt": StageNames.FOREST,
    "castle wall": StageNames.C_WALL,
    "cw": StageNames.C_WALL,
    "castle rampart": StageNames.C_WALL,
    "rampart": StageNames.C_WALL,
    "villa": StageNames.VILLA,
    "v": StageNames.VILLA,
    "annex": StageNames.VILLA,
    "annex to the evil castle": StageNames.VILLA,
    "estate": StageNames.VILLA,
    "oldrey estate": StageNames.VILLA,
    "garden": StageNames.VILLA,
    "maze": StageNames.VILLA,
    "maze garden": StageNames.VILLA,
    "garden maze": StageNames.VILLA,
    "garden forgotten by time": StageNames.VILLA,
    "mansion": StageNames.VILLA,
    "manor": StageNames.VILLA,
    "mystery manor": StageNames.VILLA,
    "dwelling": StageNames.VILLA,
    "giant's dwelling": StageNames.VILLA,
    "tunnel": StageNames.TUNNEL,
    "t": StageNames.TUNNEL,
    "cave of spiderwomen": StageNames.TUNNEL,
    "cave": StageNames.TUNNEL,
    "passage": StageNames.TUNNEL,
    "underground passage": StageNames.TUNNEL,
    "mine": StageNames.TUNNEL,
    "mining tunnel": StageNames.TUNNEL,
    "underground mining tunnel": StageNames.TUNNEL,
    "cavern": StageNames.TUNNEL,
    "caverns": StageNames.TUNNEL,
    "large cavern": StageNames.TUNNEL,
    "luminous cavern": StageNames.TUNNEL,
    "underground caverns": StageNames.TUNNEL,
    "ground water vein": StageNames.TUNNEL,
    "underground reservoir": StageNames.TUNNEL,
    "underground gallery": StageNames.TUNNEL,
    "reservoir": StageNames.TUNNEL,
    "subterranean hell": StageNames.TUNNEL,
    "batcave": StageNames.TUNNEL,
    "underground waterway": StageNames.WATERWAY,
    "underground": StageNames.WATERWAY,
    "waterway": StageNames.WATERWAY,
    "uw": StageNames.WATERWAY,
    "aqueduct": StageNames.WATERWAY,
    "aqueduct of dragons": StageNames.WATERWAY,
    "mortvia aqueduct": StageNames.WATERWAY,
    "dark palace of waterfalls": StageNames.WATERWAY,
    "underground labyrinth": StageNames.WATERWAY,
    "labyrinth": StageNames.WATERWAY,
    "the outer wall": StageNames.OUTER,
    "outer wall": StageNames.OUTER,
    "outer": StageNames.OUTER,
    "tow": StageNames.OUTER,
    "ow": StageNames.OUTER,
    "sky walkway": StageNames.OUTER,
    "art tower": StageNames.ART,
    "tower of art": StageNames.ART,
    "art": StageNames.ART,
    "at": StageNames.ART,
    "ghostly theatre": StageNames.ART,
    "marble gallery": StageNames.ART,
    "marble corridor": StageNames.ART,
    "gallery": StageNames.ART,
    "dance hall": StageNames.ART,
    "demon guest house": StageNames.ART,
    "tower of ruins": StageNames.RUINS,
    "ruins tower": StageNames.RUINS,
    "ruins": StageNames.RUINS,
    "tor": StageNames.RUINS,
    "sandy grave": StageNames.RUINS,
    "forgotten city": StageNames.RUINS,
    "castle center": StageNames.CENTER,
    "center": StageNames.CENTER,
    "cc": StageNames.CENTER,
    "vs behimos": StageNames.CENTER,
    "vs behemoth": StageNames.CENTER,
    "colosseum": StageNames.CENTER,
    "library": StageNames.CENTER,
    "long library": StageNames.CENTER,
    "underground warehouse": StageNames.CENTER,
    "warehouse": StageNames.CENTER,
    "treasury": StageNames.CENTER,
    "castle treasury": StageNames.CENTER,
    "audience room": StageNames.CENTER,
    "castle corridor": StageNames.CENTER,
    "study": StageNames.CENTER,
    "tower of science": StageNames.SCIENCE,
    "science tower": StageNames.SCIENCE,
    "science": StageNames.SCIENCE,
    "tosci": StageNames.SCIENCE,
    "the munitions factory": StageNames.SCIENCE,
    "munitions factory": StageNames.SCIENCE,
    "factory": StageNames.SCIENCE,
    "anti soul mystery lab": StageNames.SCIENCE,
    "lab": StageNames.SCIENCE,
    "duel tower": StageNames.DUEL,
    "tower of duels": StageNames.DUEL,
    "duel": StageNames.DUEL,
    "dt": StageNames.DUEL,
    "it's time to d-d-d-d duel": StageNames.DUEL,
    "the arena": StageNames.DUEL,
    "arena": StageNames.DUEL,
    "battle arena": StageNames.DUEL,
    "wipeout zone": StageNames.DUEL,
    "pit of 4 trials": StageNames.DUEL,
    "sammer kingdom if it was good": StageNames.DUEL,
    "tower of execution": StageNames.EXECUTION,
    "toe": StageNames.EXECUTION,
    "execution tower": StageNames.EXECUTION,
    "execution": StageNames.EXECUTION,
    "tower of sorcery": StageNames.SORCERY,
    "tosor": StageNames.SORCERY,
    "sorcery tower": StageNames.SORCERY,
    "sorcery": StageNames.SORCERY,
    "spelltower": StageNames.SORCERY,
    "room of clocks": StageNames.ROOM,
    "room": StageNames.ROOM,
    "clocks": StageNames.ROOM,
    "roc": StageNames.ROOM,
    "room of illusion": StageNames.ROOM,
    "vs death": StageNames.ROOM,
    "vs actrise": StageNames.ROOM,
    "vs ortega": StageNames.ROOM,
    "clock tower": StageNames.CLOCK,
    "tower of clocks": StageNames.CLOCK,
    "clock": StageNames.CLOCK,
    "ct": StageNames.CLOCK,
    "cursed clock tower": StageNames.CLOCK,
    "machine tower": StageNames.CLOCK,
    "mechanical tower": StageNames.CLOCK,
    "eneomaos machine tower": StageNames.CLOCK,
    "tower of death": StageNames.CLOCK,
    "castle keep": StageNames.KEEP,
    "keep": StageNames.KEEP,
    "ck": StageNames.KEEP,
    "master's keep": StageNames.KEEP,
    "top": StageNames.KEEP,
    "top floor": StageNames.KEEP,
    "castle top floor": StageNames.KEEP,
    "final approach": StageNames.KEEP,
    "the pinnacle": StageNames.KEEP,
    "pinnacle": StageNames.KEEP,
    "pagoda of the misty moon": StageNames.KEEP,
}


class CVLoDActiveStage(TypedDict):
    name: str  # Name of the stage.
    connecting_stages: dict[str, tuple[str, str]]  # Which other stages the stage connects to. The first element in the
                                                   # tuple is the name of the connecting stage, and the second is the
                                                   # name of the connecting stage's Region.
    position: str  # Which position in the order the stage is considered. Mainly for spoiler log purposes.


def find_stage_in_list(stage_to_find: str, active_stage_info: list[CVLoDActiveStage]) -> CVLoDActiveStage | None:
    """Loops over every element in a list of CVLoDActiveStages and tries to find a particular stage by name.
    Returns the stage if it exists is or None if it doesn't respectively."""
    for stage in active_stage_info:
        if stage["name"] == stage_to_find:
            return stage
    return None


def find_stage_of_region(region_name: str) -> str | None:
    """ Given the name of a Region, tries to find the stage that Region belongs to in the list of stage datas.
    Returns the name of the stage if found or None if not found."""
    for stage, info in CVLOD_STAGE_INFO.items():
        if region_name in info.regions:
            return stage
    return None


def get_regions_from_all_active_stages(world: "CVLoDWorld") -> list[Region]:
    """Returns the data of all Regions in a provided list of active stages. Regions will be returned in the vanilla
    stage order so that the spoiler log Locations will always be ordered the same."""

    # Loop over every stage data in the entire game and check to see which ones are active.
    stage_regions = []
    for stage, info in CVLOD_STAGE_INFO.items():
        # If the current stage is active, add that stage's Regions to the active Region names list.
        if find_stage_in_list(stage, world.active_stage_info):
            stage_regions += ([Region(reg, world.player, world.multiworld) for reg in info.regions])

    # Return the complete list of Regions.
    return stage_regions


def get_active_stages(world: "CVLoDWorld", stage_1_blacklist: dict[StageNames, str]) -> list[str]:
    """Verifies and returns a list of active stages, based on the slot world's options, in the intended regular order
    and with the default regular exits."""

    # Check if the stage layout option is an existing preset. If it is, return that preset's stage list.
    if world.options.stage_layout.value in STAGE_LAYOUT_PRESETS:
        return STAGE_LAYOUT_PRESETS[world.options.stage_layout.value]

    # Otherwise if we make it here, meaning it's a custom-submitted layout, we'll have to do some additional
    # verification on it.

    # Split the user text at each semicolon and loop over each submitted stage name.
    invalidation_reason = ""
    custom_stage_list = []
    user_stage_list = world.options.stage_layout.value.split(";")
    for stage_index in range(len(user_stage_list)):
        # Make the submitted name all lowercase to make it not case-sensitive.
        user_stage_name = user_stage_list[stage_index].lower()

        # VALIDATION CHECK 1: The user stage name must have a mapping in the stage name aliases dict.
        if user_stage_name not in STAGE_NAME_ALIASES:
            invalidation_reason = f'"{user_stage_list[stage_index]}" is not a stage in Castlevania: Legacy of Darkness.'
            break

        # If it was in the aliases, get that stage's proper internal name.
        stage_internal_name = STAGE_NAME_ALIASES[user_stage_name]

        # VALIDATION CHECK 2: The stage cannot occur in the list twice.
        if stage_internal_name in custom_stage_list:
            invalidation_reason = f"Stages can only occur once, and {stage_internal_name} is in the list twice."
            break

        # VALIDATION CHECK 3: If the stage is in the Stage 1 Blacklist, it cannot be the first stage unless Stage
        # Shuffle is on (in which case it will be randomized to a different, not-stage-1 position later).
        if stage_internal_name in stage_1_blacklist and stage_index == 0 and not world.options.stage_shuffle:
            invalidation_reason = (f"{stage_internal_name} cannot be the starting stage with the chosen options. "
                                   f"Reason: {stage_1_blacklist[stage_internal_name]}")
            break

        # VALIDATION CHECK 4: Castle Keep, if it's in the list, can only go at the end.
        if stage_internal_name == StageNames.KEEP and stage_index != len(user_stage_list) - 1:
            invalidation_reason = f"{StageNames.KEEP} can only be at the end of the list."
            break

        # If we passed all validation checks, add the stage internal name to the final custom stage list.
        custom_stage_list.append(STAGE_NAME_ALIASES[user_stage_name])

    # If we made it out of the loop with all stages validated, return the final custom stage list.
    if not invalidation_reason:
        return custom_stage_list

    # If not however, throw a warning, pick a preset at random, and return its stage list.
    logging.warning(f"[{world.player_name}] The submitted custom stage layout is invalid. {invalidation_reason} "
                    f"A random layout preset will be chosen instead.")
    world.options.stage_layout.value = world.random.choice(list(STAGE_LAYOUT_PRESETS.keys()))
    return STAGE_LAYOUT_PRESETS[world.options.stage_layout.value]


def verify_branches(world: "CVLoDWorld", active_stage_order: list[str]) -> None:
    """Verifies a submitted stage list actually meets the requirements of the slot's chosen branch options regarding
    what stages are placed after Villa and/or Castle Center. Will alter said options if the requirements are not met."""

    # Count the number of valid branch stages in the entire stage list, starting from the beginning of it. A valid
    # branch stage is any stage that is not Villa, Castle Center, or Castle Keep.
    total_valid_branch_stages = len([stage for stage in active_stage_order if stage not in
                                     [StageNames.VILLA, StageNames.CENTER, StageNames.KEEP]])

    valid_villa_branch_stages = 0
    valid_cc_branch_stages = 0

    # If Villa has more than one branch enabled, and Villa is in the stage list, check to see if its chosen branches
    # are valid.
    if world.options.villa_branching_paths != VillaBranchingPaths.option_one and \
            StageNames.VILLA in active_stage_order:
        villa_index = active_stage_order.index(StageNames.VILLA)
        # Find the number of valid branch stages after Villa.
        # If Stage Shuffle is off, starting from where Villa is, count the stages forward until we find Castle Center,
        # Castle Keep, or the end of the list.
        if not world.options.stage_shuffle:
            for i in range(villa_index + 1, len(active_stage_order)):
                if active_stage_order[i] in [StageNames.CENTER, StageNames.KEEP]:
                    break
                valid_villa_branch_stages += 1
        # Otherwise, if Stage Shuffle is on, consider the total number of branch stages as the number of valid Villa
        # branch stages.
        else:
            valid_villa_branch_stages = total_valid_branch_stages

        villa_invalidation_reason = ""
        # If Villa And Cornell Path is chosen, Castle Center must be in the stage list somewhere.
        if world.options.villa_branching_paths == VillaBranchingPaths.option_three_with_cornell_path \
                and StageNames.CENTER not in active_stage_order:
            villa_invalidation_reason = f"{StageNames.CENTER} is not in the stage list for the Cornell path to end at."
        # Otherwise, whether the option is valid depends on if the minimum requirement for valid Villa branching stages
        # is met.
        elif valid_villa_branch_stages < VILLA_BRANCH_STAGE_MINIMUMS[world.options.villa_branching_paths]:
            villa_invalidation_reason = f"Too few possible Villa branch stages in the stage list."

        # If the Villa branch option was invalidated, throw a warning and change it to the highest valid option.
        if villa_invalidation_reason:
            logging.warning(f"[{world.player_name}] The chosen Villa Branching Stages option is invalid with the "
                            f"submitted stage layout. {villa_invalidation_reason} "
                            f"A choice with a lower required branch stage count will be chosen instead.")
            highest_valid_villa_option = VillaBranchingPaths.option_one
            for option, minimum in VILLA_BRANCH_STAGE_MINIMUMS.items():
                if valid_villa_branch_stages >= minimum > VILLA_BRANCH_STAGE_MINIMUMS[highest_valid_villa_option] and \
                        (option != VillaBranchingPaths.option_three_with_cornell_path
                         or StageNames.CENTER in active_stage_order):
                    highest_valid_villa_option = option
            world.options.villa_branching_paths.value = highest_valid_villa_option

    # If Castle Center has more than one branch enabled, and CC is in the stage list, check to see if its chosen
    # branches are valid.
    if world.options.castle_center_branching_paths == CastleCenterBranchingPaths.option_two \
            and StageNames.CENTER in active_stage_order:
        cc_index = active_stage_order.index(StageNames.CENTER)
        # Find the number of valid branch stages after Castle Center.
        # If Stage Shuffle is off, starting from where CC is, count the stages forward until we find Villa, Castle Keep,
        # or the end of the list.
        if not world.options.stage_shuffle:
            for i in range(cc_index + 1, len(active_stage_order)):
                if active_stage_order[i] in [StageNames.VILLA, StageNames.KEEP]:
                    break
                valid_cc_branch_stages += 1
        # Otherwise, if Stage Shuffle is on, consider the total number of branch stages, minus the total number of
        # decided-upon valid Villa branch stages, as the number of valid Castle Center branch stages.
        else:
            valid_cc_branch_stages = total_valid_branch_stages - \
                                     VILLA_BRANCH_STAGE_MINIMUMS[world.options.villa_branching_paths]

        # If less than four valid CC branch stages are available, throw a warning and change it to one of the One
        # options chosen at random.
        if valid_cc_branch_stages < 4:
            logging.warning(f"[{world.player_name}] The chosen Castle Center Branching Stages option is invalid with "
                            f"the submitted stage layout. Too few possible Castle Center branch stages in the stage "
                            f"list. A one-branch choice will be chosen instead.")
            world.options.castle_center_branching_paths.value = world.random.choice(
                [CastleCenterBranchingPaths.option_one_reinhardt, CastleCenterBranchingPaths.option_one_carrie])


def shuffle_stages(world: "CVLoDWorld", unshuffled_stage_order: list[str],
                   stage_1_blacklist: dict[StageNames: str]) -> list[str]:
    """The sequel to the stage shuffle algorithm from the original CV64 apworld, now drastically rewritten to account
    for all the new stage-related options!

    So, in the vanilla game, all the stages are basically laid out on a linear "timeline" with some stages being
    different depending on who you are playing as. The character-specific stages, in question, are the ones following
    Villa and Castle Center. The ends of these two stages are considered the route divergences and, in
    this rando, the game's behavior has been changed in such that any character can access any other character's
    exclusive stages (thereby making the entire game playable in just one character run). With this in mind, when
    shuffling the stages around, there is one particularly big rule that must be kept in mind to ensure things don't get
    too wacky. That being:

    Villa and Castle Center cannot appear in branching path stage slots; they can only be on "main" path slots.*

    So for this reason, generating a new stage layout is not as simple as just scrambling a list of stages around. It
    must be done in such a way that whatever stages directly follow Villa or CC is not the other stage. The exception is
    if branching stages for Villa and/or Castle Center are not a thing at all due to the player settings, in which case
    everything I said above does not matter. Consider the following representation of a stage "timeline", wherein each
    "-" represents a main stage and a "=" represents a pair of branching stages:

    -==---=---

    In the above example, CC is the first "-" and Villa is the fourth. CC and Villa can only be "-"s whereas every other
    stage can be literally anywhere, including on one of the "=" dashes. Villa can be followed by two branches with one
    stag each, three branches with one stage each, or three branches with two of those being one stage and the third
    (referred to as the Cornell path) being three stages that connect directly to the end of Castle Center regardless
    of where it is. Castle Center can be followed by two branches with two stages each.

    This code works by generating a singular list of stages that fit the criteria of Villa and Castle Center being a
    minimum number of spaces from them.

    Once that has been figured out, it will then generate a dictionary of
    stages with the appropriate information regarding what stages come before and after them to then be used for
    Entrance creation as well as what position in the list they are in for the purposes of the spoiler log and extended
    hint information.

    I opted to use the Rondo of Blood "'" stage notation to represent stages not on branching path 1; 2 and 3 will have
    ' and " respectively. If a main stage with a backwards connection connects backwards into a pair of branching
    stages, it will be the non-"'" stage that it connects to. The other slot(s) cannot be accessed this way.
    """

    player_starting_stage = STAGE_NAME_ALIASES[world.options.shuffled_starting_stage.current_option_name.lower()]

    # Verify the starting stage is valid (in the active stage list and not in the stage 1 blacklist).
    if player_starting_stage not in stage_1_blacklist and player_starting_stage in unshuffled_stage_order:
        starting_stage = player_starting_stage
    # If it's not valid, pick a valid stage at random.
    else:
        # Throw a different warning depending on if the stage is not in the active stage list or is in the stage 1
        # blacklist.
        if player_starting_stage in stage_1_blacklist:
            logging.warning(f"[{world.player_name}] {player_starting_stage} cannot be the Shuffled Starting Stage "
                            f"with the  chosen options. Reason: {stage_1_blacklist[player_starting_stage]} "
                            f"Picking a different stage instead...")
        else:
            logging.warning(f"[{world.player_name}] {player_starting_stage} cannot be the Shuffled Starting Stage "
                            f"because it's not in the chosen stage list. Picking a different stage instead...")
        # Assemble a list of possible valid starting stages by checking to see if each stage in the active list is
        # either not in the stage 1 blacklist or is not Castle Keep, and pick a random stage from it.
        starting_stage = world.random.choice([stage for stage in unshuffled_stage_order
                                              if stage not in stage_1_blacklist and stage != StageNames.KEEP])
        world.options.shuffled_starting_stage.value = CVLOD_STAGE_INFO[starting_stage].id_number

    # Copy the world's active stage list to use as our list of stages to shuffle.
    main_stages = unshuffled_stage_order.copy()

    # Remove Castle Keep if it was in the active list that we copied. We'll put it on the end manually afterward.
    if StageNames.KEEP in main_stages:
        main_stages.remove(StageNames.KEEP)

    # Create the list of stages that are eligible to go in branching stage slots. Specifically, this should exclude
    # Villa if Villa branching paths are on, and/or Castle Center if Castle Center branching paths are on.
    branch_stages = [stage for stage in main_stages if (stage not in [StageNames.VILLA, StageNames.CENTER]) or
                     (stage == StageNames.VILLA and world.options.villa_branching_paths ==
                      VillaBranchingPaths.option_one) or
                     (stage == StageNames.CENTER and world.options.castle_center_branching_paths !=
                      CastleCenterBranchingPaths.option_two)]

    # Determine how many branching stages there should be by looking at what stages are available and what the branching
    # stage options are set to.
    total_branch_stages = 0
    if StageNames.VILLA in main_stages:
        if world.options.villa_branching_paths == VillaBranchingPaths.option_two:
            total_branch_stages += 2
        elif world.options.villa_branching_paths == VillaBranchingPaths.option_three:
            total_branch_stages += 3
        elif world.options.villa_branching_paths == VillaBranchingPaths.option_three_with_cornell_path:
            total_branch_stages += 5
    if StageNames.CENTER in main_stages \
            and world.options.castle_center_branching_paths == CastleCenterBranchingPaths.option_two:
        total_branch_stages += 4

    # Remove stages from the list of branching stages at random until its length is the determined number of stages.
    # This will be our final branching stages pool to shuffle.
    while len(branch_stages) > total_branch_stages:
        branch_stages.remove(world.random.choice(branch_stages))

    # Remove the stages left over in the branching stage list from the main list.
    # This will be our final main stages pool to shuffle.
    for stage in branch_stages:
        main_stages.remove(stage)

    # Shuffle both stage lists.
    world.random.shuffle(main_stages)
    world.random.shuffle(branch_stages)

    # Construct the new stage order list.
    # Loop over each entry in the main list and add them to the new stage order list.
    new_stage_order = []
    for stage in main_stages:
        new_stage_order.append(stage)

        # If the stage is Villa, add the first 2, 3, or 5 stages currently in the branches list depending on what the
        # Villa branching stages option is, and clear those stages from it.
        if stage == StageNames.VILLA:
            if world.options.villa_branching_paths == VillaBranchingPaths.option_two:
                new_stage_order += branch_stages[0:2]
                branch_stages = branch_stages[2:]
            elif world.options.villa_branching_paths == VillaBranchingPaths.option_three:
                new_stage_order += branch_stages[0:3]
                branch_stages = branch_stages[3:]
            elif world.options.villa_branching_paths == VillaBranchingPaths.option_three_with_cornell_path:
                new_stage_order += branch_stages[0:5]
                branch_stages = branch_stages[5:]
        # If the stage is Castle Center, add the first 4 stages currently in the branches list if the Castle Center
        # branching paths option is 2.
        elif stage == StageNames.CENTER and \
                world.options.castle_center_branching_paths == CastleCenterBranchingPaths.option_two:
            new_stage_order += branch_stages[0:4]
            branch_stages = branch_stages[4:]

    # Return the new stage order list.
    return new_stage_order


def get_stage_exits(options: CVLoDOptions, active_stage_order: list[str]) -> list[CVLoDActiveStage]:
    """With a given list of stage names in their final decided order, figures out all relevant information regarding
    how the stages connect to one-another and returns that information in the form of a list of TypedDicts arranged in
    the same order as the input list of stage names."""
    active_stage_info = []
    villa_branch_stages = ["", "", "", "", ""]
    after_villa_main_stage = ""
    cc_branch_stages = ["", "", "", ""]
    after_cc_main_stage = ""

    # See if Villa exists in the stage order list. If it is, search ahead in the list after Villa by a length depending
    # on the Villa Branching Paths option to see what our Villa branching stages are, as well as the main path stage
    # following them.
    if StageNames.VILLA in active_stage_order:
        villa_index = active_stage_order.index(StageNames.VILLA)
        if options.villa_branching_paths == VillaBranchingPaths.option_two:
            villa_branch_stages = active_stage_order[villa_index + 1: villa_index + 3] + ["", "", ""]
            after_villa_main_stage = active_stage_order[villa_index + 3]
        elif options.villa_branching_paths == VillaBranchingPaths.option_three:
            villa_branch_stages = active_stage_order[villa_index + 1: villa_index + 4] + ["", ""]
            after_villa_main_stage = active_stage_order[villa_index + 4]
        elif options.villa_branching_paths == VillaBranchingPaths.option_three_with_cornell_path:
            villa_branch_stages = active_stage_order[villa_index + 1: villa_index + 6]
            after_villa_main_stage = active_stage_order[villa_index + 6]

    # See if Castle Center exists in the stage order list. If it is, search ahead in the list after CC by a length
    # depending on the Castle Center Branching Paths option to see what our CC branching stages are.
    if StageNames.CENTER in active_stage_order and \
            options.castle_center_branching_paths == CastleCenterBranchingPaths.option_two:
        cc_index = active_stage_order.index(StageNames.CENTER)
        cc_branch_stages = active_stage_order[cc_index + 1: cc_index + 5]
        after_cc_main_stage = active_stage_order[cc_index + 5]

    # Loop over each entry in the stage order list.
    current_stage_number = 1
    for i in range(len(active_stage_order)):
        current_stage_info = CVLoDActiveStage(name=active_stage_order[i], connecting_stages={}, position="")

        # # # Figure out the current stage's PREVIOUS stage. # # #
        # If the stage is at the beginning of the list, then we'll put "Start" as the previous stage to indicate it's
        # the starting stage.
        if i == 0:
            current_stage_info["connecting_stages"]["prev"] = ("Start", "")
        # If the stage is in the first, second, or third slot in the Villa branch stages list, the previous stage will
        # be Villa in every case.
        elif active_stage_order[i] == villa_branch_stages[1] or active_stage_order[i] == villa_branch_stages[2]:
            current_stage_info["connecting_stages"]["prev"] = (StageNames.VILLA, reg_names.villac_crypt_i)
        # If the stage is in the fourth or fifth slot in the Villa branch stages list, the previous stage will be the
        # previous stage in the Villa branch stages list.
        elif active_stage_order[i] == villa_branch_stages[3] or active_stage_order[i] == villa_branch_stages[4]:
            connecting_stage = villa_branch_stages[villa_branch_stages.index(active_stage_order[i]) - 1]
            current_stage_info["connecting_stages"]["prev"] = (connecting_stage,
                                                               CVLOD_STAGE_INFO[connecting_stage].end_region)
        # If the previous stage in the list is in the first Villa stage after all its branches, the previous stage will
        # be the first Villa branching stage.
        elif active_stage_order[i] == after_villa_main_stage:
            current_stage_info["connecting_stages"]["prev"] = (villa_branch_stages[0],
                                                               CVLOD_STAGE_INFO[villa_branch_stages[0]].end_region)
        # If the stage is in the third slot in the Castle Center branch stages list, the previous stage will be CC in
        # every case.
        elif active_stage_order[i] == cc_branch_stages[2]:
            current_stage_info["connecting_stages"]["prev"] = (StageNames.CENTER, reg_names.ccte_elev_top)
        # If the previous stage is in the list is in the first CC stage after all its branches, the previous stage will
        # be the second CC branching stage.
        elif active_stage_order[i] == after_cc_main_stage:
            current_stage_info["connecting_stages"]["prev"] = (cc_branch_stages[1],
                                                               CVLOD_STAGE_INFO[cc_branch_stages[1]].end_region)
        # Otherwise, if none of the above checks pass, put the previous stage in the active order list as the previous
        # stage.
        else:
            current_stage_info["connecting_stages"]["prev"] = (active_stage_order[i - 1],
                                                               CVLOD_STAGE_INFO[active_stage_order[i - 1]].end_region)

        # # # Figure out the current stage's NEXT stage(s). # # #
        # If the stage is at the end of the list, then we'll put "End" as the only next stage to indicate it's last.
        if i == len(active_stage_order) - 1:
            current_stage_info["connecting_stages"]["next"] = ("End", "")
        # If the stage is Villa, the next stages are the next one, two, or three stages in the main list depending on
        # how many Villa branching stages there are.
        elif active_stage_order[i] == StageNames.VILLA:
            if not villa_branch_stages[1]:
                current_stage_info["connecting_stages"]["next"] = \
                    (active_stage_order[i + 1], CVLOD_STAGE_INFO[active_stage_order[i + 1]].start_region)
            elif not villa_branch_stages[2]:
                current_stage_info["connecting_stages"]["next"] = \
                    (active_stage_order[i + 1], CVLOD_STAGE_INFO[active_stage_order[i + 1]].start_region)
                current_stage_info["connecting_stages"]["next alt 1"] = \
                    (active_stage_order[i + 2], CVLOD_STAGE_INFO[active_stage_order[i + 2]].start_region)
            else:
                current_stage_info["connecting_stages"]["next"] = \
                    (active_stage_order[i + 1], CVLOD_STAGE_INFO[active_stage_order[i + 1]].start_region)
                current_stage_info["connecting_stages"]["next alt 1"] = \
                    (active_stage_order[i + 2], CVLOD_STAGE_INFO[active_stage_order[i + 2]].start_region)
                current_stage_info["connecting_stages"]["next alt 2"] = \
                    (active_stage_order[i + 3], CVLOD_STAGE_INFO[active_stage_order[i + 3]].start_region)
        # If the stage is in the first or second slot in the Villa branch stages list, the next stage will
        # be the after-Villa main stage in every case.
        elif active_stage_order[i] == villa_branch_stages[0] or active_stage_order[i] == villa_branch_stages[1]:
            current_stage_info["connecting_stages"]["next"] = \
                    (after_villa_main_stage, CVLOD_STAGE_INFO[after_villa_main_stage].start_region)
        # If the stage is in the third slot in the Villa branch stages list, the next stage will be the after-Villa main
        # stage if no stage is in the fourth or fifth Villa slot or the fourth Villa branching stage if there is.
        elif active_stage_order[i] == villa_branch_stages[2]:
            if villa_branch_stages[3]:
                current_stage_info["connecting_stages"]["next"] = \
                    (villa_branch_stages[3], CVLOD_STAGE_INFO[villa_branch_stages[3]].start_region)
            else:
                current_stage_info["connecting_stages"]["next"] = \
                    (after_villa_main_stage, CVLOD_STAGE_INFO[after_villa_main_stage].start_region)
        # If the stage is in the fifth slot in the Villa branching stages list, the next stage will be the end of
        # Castle Center.
        elif active_stage_order[i] == villa_branch_stages[4]:
            current_stage_info["connecting_stages"]["next"] = (StageNames.CENTER, reg_names.ccte_elev_top)
        # If the stage is Castle Center, the next stages are the next one or two stages in the main list depending on
        # if there are or aren't CC branching stages.
        elif active_stage_order[i] == StageNames.CENTER:
            if not cc_branch_stages[0]:
                current_stage_info["connecting_stages"]["next"] = \
                    (active_stage_order[i + 1], CVLOD_STAGE_INFO[active_stage_order[i + 1]].start_region)
            else:
                current_stage_info["connecting_stages"]["next"] = \
                    (active_stage_order[i + 1], CVLOD_STAGE_INFO[active_stage_order[i + 1]].start_region)
                current_stage_info["connecting_stages"]["next alt 1"] = \
                    (active_stage_order[i + 3], CVLOD_STAGE_INFO[active_stage_order[i + 3]].start_region)
        # If the stage is in the second slot in the CC branch stages list, the next stage will be the after-CC main
        # stage.
        elif active_stage_order[i] == cc_branch_stages[1]:
            current_stage_info["connecting_stages"]["next"] = (after_cc_main_stage,
                                                               CVLOD_STAGE_INFO[after_cc_main_stage].start_region)
        # Otherwise, if none of the above checks pass, put the next stage in the active order list as the next stage.
        else:
            current_stage_info["connecting_stages"]["next"] = (active_stage_order[i + 1],
                                                               CVLOD_STAGE_INFO[active_stage_order[i + 1]].start_region)

        # # # Figure out the current stage's POSITION number and ALT indicator. # # #
        # If the stage is in any Villa branch slot after the first one, subtract 1 from the current stage number to
        # prevent it from net-incrementing until we are past the Villa branches entirely.
        if active_stage_order[i] in villa_branch_stages[1:]:
            current_stage_number -= 1
        # If the stage is specifically in the third Castle Center branch slot, subtract 2 from the number to put it
        # at the start of the other path.
        elif active_stage_order[i] == cc_branch_stages[2]:
            current_stage_number -= 2

        # If the stage is in the second Villa branch slot, or the third or fourth CC branch slots, the alt indicator
        # will be a "'".
        if active_stage_order[i] == villa_branch_stages[1] or active_stage_order[i] in cc_branch_stages[2:]:
            alt_indicator = "'"
        # If the stage is in the third Villa branch slot, the alt indicator will be a '"' if there are no more Villa
        # branch stages after it or an "A" if there are more stages for the Cornell path.
        elif active_stage_order[i] == villa_branch_stages[2]:
            if not villa_branch_stages[3]:
                alt_indicator = '"'
            else:
                alt_indicator = "A"
        # If the stage is the fourth Villa branch slot (aka the second Cornell path stage), the alt will be "B".
        elif active_stage_order[i] == villa_branch_stages[3]:
            alt_indicator = "B"
        # If the stage is the fifth Villa branch slot, (aka the third Cornell path stage), the alt will be "C".
        elif active_stage_order[i] == villa_branch_stages[4]:
            alt_indicator = "C"
        # Otherwise, if none of the above checks pass, the alt will be nothing ("").
        else:
            alt_indicator = ""

        # If the alt indicator is a letter, put just that letter for the stage position.
        if alt_indicator in ["A", "B", "C"]:
            current_stage_info["position"] = alt_indicator
        # Otherwise, convert the current stage number into a string zero-filled to two digits and join it with the alt
        # indicator.
        else:
            current_stage_info["position"] = str(current_stage_number).zfill(2) + alt_indicator

        # Add the final stage info to the list of stage infos and increment the current stage number by 1 for the next
        # loop.
        active_stage_info.append(current_stage_info)
        current_stage_number += 1

    return active_stage_info


def get_active_warps(world: "CVLoDWorld") -> list[str]:
    """Creates a list of warps from the active stage list. They can either be random with a specified number or created
    from a pre-made list."""
    active_warp_list = []
    # Create the list of possible warps from the active stage list. Leave the starting stage out as it's guaranteed to
    # be the first warp.
    possible_warps = [stage["name"] for stage in world.active_stage_info
                      if stage["connecting_stages"]["prev"][0] != "Start"]

    def arrange_warp_list() -> None:
        """Arranges a given of warps differently depending on what was chosen for the Warp Order option, and inserts
        the starting stage name at the beginning. If Set Order was chosen, the order will be completely left alone."""
        nonlocal active_warp_list
        # Arrange the warps to be in the seed's stage order if Seed Stage Order is the Warp Order.
        if world.options.warp_order == WarpOrder.option_seed_stage_order:
            # Create a new list out of the possible warps.
            new_list = possible_warps.copy()
            # Remove each warp from the new list if it's not in the active list and make the new list the active list.
            for warp in possible_warps:
                if warp not in active_warp_list:
                    new_list.remove(warp)
            active_warp_list = new_list
        # Arrange the warps to be in the vanilla game's stage order if Vanilla Stage Order is the Warp Order.
        elif world.options.warp_order == WarpOrder.option_vanilla_stage_order:
            # Create a new list out of the order the stage datas are arranged in.
            new_list = [stage for stage in CVLOD_STAGE_INFO]
            # Remove each warp from the new list if it's not in the active list and make the new list the active list.
            for warp in [stage for stage in CVLOD_STAGE_INFO]:
                if warp not in active_warp_list:
                    new_list.remove(warp)
            active_warp_list = new_list
        # Arrange the warps to be in a completely random order by merely shuffling the list.
        elif world.options.warp_order == WarpOrder.option_randomized_order:
            world.random.shuffle(active_warp_list)

        # Insert the starting stage at the start of the warp list
        active_warp_list.insert(0, world.active_stage_info[0]["name"])

    # If a custom warp layout was provided, try getting the stage list out of that option.
    if world.options.warp_layout:
        # Split the user text at each semicolon and loop over each submitted stage name.
        invalidation_reason = ""
        custom_warp_list = []
        user_stage_list = world.options.warp_layout.value.split(";")
        for stage_index in range(len(user_stage_list)):
            # Make the submitted name all lowercase to make it not case-sensitive.
            user_stage_name = user_stage_list[stage_index].lower()

            # VALIDATION CHECK 1: The user stage name must have a mapping in the stage name aliases dict.
            if user_stage_name not in STAGE_NAME_ALIASES:
                invalidation_reason = (f'"{user_stage_list[stage_index]}" is not a stage in Castlevania: Legacy of '
                                       f'Darkness.')
                break

            # If it was in the aliases, get that stage's proper internal name.
            stage_internal_name = STAGE_NAME_ALIASES[user_stage_name]

            # VALIDATION CHECK 2: The stage cannot occur in the list twice.
            if stage_internal_name in custom_warp_list:
                invalidation_reason = f"Stages can only occur once, and {stage_internal_name} is in the list twice."
                break

            # VALIDATION CHECK 3: The stage must be an active stage in the list of possible warps.
            if stage_internal_name not in possible_warps:
                invalidation_reason = f"{stage_internal_name} is not an active stage in the slot."
                break

            # If we passed all validation checks, and it's not the starting stage, add the stage internal name to the
            # final custom warps list. If it is the starting stage, we will skip it without invalidating the list.
            if world.active_stage_info[0]["name"] != stage_internal_name:
                custom_warp_list.append(STAGE_NAME_ALIASES[user_stage_name])

        # If we made it out of the loop with all stages validated, return the final custom warp list arranged in the
        # correct order.
        if not invalidation_reason:
            active_warp_list = custom_warp_list
            arrange_warp_list()
            return active_warp_list
        # If not however, throw a warning and move on to the random warp generation code.
        else:
            logging.warning(f"[{world.player_name}] The submitted custom warp layout is invalid. {invalidation_reason} "
                            f"A random warp layout will be generated instead.")

    # Check if the chosen number of random warps is higher than the number of possible warps. If it is, throw a warning
    # and lower the number of random warps down to a valid number.
    if world.options.total_random_warps.value > len(possible_warps):
        logging.warning(f"[{world.player_name}] The Total Random Warps ({world.options.total_random_warps.value}) is "
                        f"higher than the total number of non-starting stages ({len(possible_warps)}). The former "
                        f"will be lowered to {len(possible_warps)}.")
        world.options.total_random_warps.value = len(possible_warps)

    # Take a random sample of the specified number of random warps from the list of possible warps.
    active_warp_list = world.random.sample(possible_warps, world.options.total_random_warps.value)
    # If Set Order was chosen for the warp order, change it to Seed Stage Order now.
    if world.options.warp_order == WarpOrder.option_set_order:
        world.options.warp_order.value = WarpOrder.option_seed_stage_order

    # Arrange the final list correctly and return it.
    arrange_warp_list()
    return active_warp_list
