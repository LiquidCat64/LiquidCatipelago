import logging

from BaseClasses import Location
from .data import loc_names, item_names
from .data.misc_names import GAME_NAME
from .options import CVLoDOptions, SubWeaponShuffle, DraculasCondition, RenonFightCondition, VincentFightCondition, \
    VillaState, CastleWallState

from typing import NamedTuple


class CVLoDLocation(Location):
    game: str = GAME_NAME


class CVLoDLocationData(NamedTuple):
    flag_id: int # The Location object's unique code attribute, as well as the in-game pickup flag index. starting from
              # 0x801CAA60 that indicates the Location has been checked.
    countdown: int | None # Index in the array of Countdown numbers it contributes to.
    normal_item: str # What Item to add to the AP itempool if that Location is added with the Normal item pool enabled.
                     # Usually but not always, this is the Item that's normally there in the vanilla game on Normal.
    easy_item: str = ""  # What Item to add to the AP itempool if that Location is added with the Easy item pool
                         # enabled. Usually but not always, this is the Item that's normally there in the vanilla game
                         # on Easy. If None, the Normal item will be defaulted to.
    hard_item: str = ""  # What Item to add to the AP itempool if that Location is added with the Hard item pool
                         # enabled. Usually but not always, this is the Item that's normally there in the vanilla game
                         # on Hard. If None, the Normal item will be defaulted to.


class CVLoD3HBData(NamedTuple):
    new_first_flag_id: int  # What rando-specific Flag ID the 3HB's drops will be starting at.
    location_names: list[str]  # List of Locations inside that 3HB.


CVLOD_LOCATIONS_INFO = {
    # Foggy Lake
    loc_names.fld_forecast_port:            CVLoDLocationData(0x150, 0, item_names.gold_500),
    loc_names.fld_forecast_starboard:       CVLoDLocationData(0x14F, 0, item_names.jewel_rl),
    loc_names.fld_foremast_lower:           CVLoDLocationData(0x152, 0, item_names.jewel_rl),
    loc_names.fld_stairs_port:              CVLoDLocationData(0x146, 0, item_names.jewel_rs),
    loc_names.fld_stairs_starboard:         CVLoDLocationData(0x148, 0, item_names.jewel_rs),
    loc_names.fld_net_port:                 CVLoDLocationData(0x14C, 0, item_names.jewel_rs),
    loc_names.fld_net_starboard:            CVLoDLocationData(0x147, 0, item_names.jewel_rs),
    loc_names.fld_mainmast_base:            CVLoDLocationData(0x142, 0, item_names.sub_knife),
    loc_names.fld_near_door:                CVLoDLocationData(0x149, 0, item_names.jewel_rs),
    loc_names.fld_near_block_l:             CVLoDLocationData(0x14B, 0, item_names.gold_100),
    loc_names.fld_near_block_r:             CVLoDLocationData(0x14A, 0, item_names.jewel_rl),
    loc_names.fld_above_door:               CVLoDLocationData(0x143, 0, item_names.jewel_rl),
    loc_names.fld_stern_port:               CVLoDLocationData(0x145, 0, item_names.jewel_rs),
    loc_names.fld_stern_starboard:          CVLoDLocationData(0x144, 0, item_names.jewel_rs),
    loc_names.fld_poop_port_crates:         CVLoDLocationData(0x140, 0, item_names.powerup),
    loc_names.fld_poop_starboard_crates:    CVLoDLocationData(0x141, 0, item_names.jewel_rl),
    loc_names.fld_mainmast_top:             CVLoDLocationData(0x151, 0, item_names.use_chicken),
    loc_names.fld_jiggermast:               CVLoDLocationData(0x27C, 0, item_names.quest_key_deck),
    loc_names.fld_foremast_upper_port:      CVLoDLocationData(0x14D, 0, item_names.use_beef),
    loc_names.fld_foremast_upper_starboard: CVLoDLocationData(0x14E, 0, item_names.sub_axe),
    loc_names.flb_hallway_l:                CVLoDLocationData(0x15A, 0, item_names.gold_300),
    loc_names.flb_hallway_r:                CVLoDLocationData(0x15B, 0, item_names.jewel_rs),
    loc_names.flb_tall_crates:              CVLoDLocationData(0x155, 0, item_names.sub_knife),
    loc_names.flb_short_crates_l:           CVLoDLocationData(0x156, 0, item_names.jewel_rl),
    loc_names.flb_short_crates_r:           CVLoDLocationData(0x157, 0, item_names.gold_500),
    loc_names.flp_pier_l:                   CVLoDLocationData(0x162, 0, item_names.use_chicken),
    loc_names.flp_pier_m:                   CVLoDLocationData(0x163, 0, item_names.sub_axe),
    loc_names.flp_pier_r:                   CVLoDLocationData(0x164, 0, item_names.jewel_rl),
    loc_names.flp_statue_l:                 CVLoDLocationData(0x161, 0, item_names.use_beef),
    loc_names.flp_statue_r:                 CVLoDLocationData(0x160, 0, item_names.use_chicken),

    # Forest of Silence
    loc_names.forest_pier_center:  CVLoDLocationData(0x16, 1, item_names.jewel_rs),
    loc_names.forest_pier_end:     CVLoDLocationData(0x17, 1, item_names.gold_300),
    loc_names.forest_sypha_ne:     CVLoDLocationData(0x19, 1, item_names.use_ampoule),
    loc_names.forest_sypha_se:     CVLoDLocationData(0x18, 1, item_names.jewel_rl),
    loc_names.forest_sypha_nw:     CVLoDLocationData(0x1A, 1, item_names.gold_500),
    loc_names.forest_sypha_sw:     CVLoDLocationData(0x1B, 1, item_names.use_purifying),
    loc_names.forest_flea_trail:   CVLoDLocationData(0x1C, 1, item_names.sub_axe),
    loc_names.forest_leap:         CVLoDLocationData(0x1E, 1, item_names.gold_500),
    loc_names.forest_descent:      CVLoDLocationData(0x1D, 1, item_names.powerup),
    loc_names.forest_passage:      CVLoDLocationData(0x21, 1, item_names.use_beef),
    loc_names.forest_child_ledge:  CVLoDLocationData(0x22, 1, item_names.gold_100),
    loc_names.forest_charnel_1:    CVLoDLocationData(0x11, 1, item_names.use_card_m),
    loc_names.forest_charnel_2:    CVLoDLocationData(0x12, 1, item_names.use_card_s),
    loc_names.forest_charnel_3:    CVLoDLocationData(0x13, 1, item_names.gold_500),
    loc_names.forest_werewolf_pit: CVLoDLocationData(0x20, 1, item_names.sub_knife),
    loc_names.forest_pike:         CVLoDLocationData(0x27, 1, item_names.use_chicken),
    loc_names.forest_end_gate:     CVLoDLocationData(0x1F, 1, item_names.gold_500),
    loc_names.forest_skelly_mouth: CVLoDLocationData(0x23, 1, item_names.use_chicken),

    # Castle Wall
    loc_names.cwr_bottom:        CVLoDLocationData(0x2D,  2, item_names.use_card_s),
    loc_names.cwr_top:           CVLoDLocationData(0x30,  2, item_names.use_chicken),
    loc_names.cw_dragon_sw:      CVLoDLocationData(0x49,  2, item_names.use_chicken),
    loc_names.cw_save_slab1:     CVLoDLocationData(0x2B8, 2, item_names.jewel_rl,),
    loc_names.cw_save_slab2:     CVLoDLocationData(0x2B9, 2, item_names.jewel_rl,),
    loc_names.cw_save_slab3:     CVLoDLocationData(0x2BA, 2, item_names.jewel_rl,),
    loc_names.cw_save_slab4:     CVLoDLocationData(0x2BB, 2, item_names.jewel_rl,),
    loc_names.cw_save_slab5:     CVLoDLocationData(0x2BC, 2, item_names.jewel_rl,),
    loc_names.cw_rrampart:       CVLoDLocationData(0x46,  2, item_names.gold_300),
    loc_names.cw_lrampart:       CVLoDLocationData(0x47,  2, item_names.use_card_m),
    loc_names.cw_pillar:         CVLoDLocationData(0x44,  2, item_names.powerup),
    loc_names.cw_shelf:          CVLoDLocationData(0x42,  2, item_names.quest_winch),
    loc_names.cw_shelf_torch:    CVLoDLocationData(0x4C,  2, item_names.sub_cross),
    loc_names.cw_ground_left:    CVLoDLocationData(0x48,  2, item_names.use_purifying),
    loc_names.cw_ground_middle:  CVLoDLocationData(0x27D, 2, item_names.quest_key_left),
    loc_names.cw_ground_right:   CVLoDLocationData(0x4D,  2, item_names.sub_axe),
    loc_names.cwl_bottom:        CVLoDLocationData(0x2E,  2, item_names.use_card_m),
    loc_names.cwl_bridge:        CVLoDLocationData(0x2F,  2, item_names.use_beef),
    loc_names.cw_drac_sw:        CVLoDLocationData(0x4E,  2, item_names.use_chicken),
    loc_names.cw_drac_slab1:     CVLoDLocationData(0x2BD, 2, item_names.gold_300,),
    loc_names.cw_drac_slab2:     CVLoDLocationData(0x2BE, 2, item_names.gold_300,),
    loc_names.cw_drac_slab3:     CVLoDLocationData(0x2BF, 2, item_names.gold_300,),
    loc_names.cw_drac_slab4:     CVLoDLocationData(0x2C0, 2, item_names.gold_300,),
    loc_names.cw_drac_slab5:     CVLoDLocationData(0x2C1, 2, item_names.gold_300,),

    # Villa
    loc_names.villafy_outer_gate_l:         CVLoDLocationData(0x62,   3, item_names.use_purifying),
    loc_names.villafy_outer_gate_r:         CVLoDLocationData(0x63,   3, item_names.jewel_rl),
    loc_names.villafy_inner_gate:           CVLoDLocationData(0x60,   3, item_names.use_beef),
    loc_names.villafy_gate_marker:          CVLoDLocationData(0x65,   3, item_names.powerup),
    loc_names.villafy_villa_marker:         CVLoDLocationData(0x64,   3, item_names.use_beef),
    loc_names.villafy_fountain_fl:          CVLoDLocationData(0x5F,   3, item_names.gold_500),
    loc_names.villafy_fountain_fr:          CVLoDLocationData(0x61,   3, item_names.use_purifying),
    loc_names.villafy_fountain_ml:          CVLoDLocationData(0x5E,   3, item_names.use_card_s),
    loc_names.villafy_fountain_mr:          CVLoDLocationData(0x5A,   3, item_names.use_card_m),
    loc_names.villafy_fountain_rl:          CVLoDLocationData(0x5C,   3, item_names.use_beef),
    loc_names.villafy_fountain_rr:          CVLoDLocationData(0x5B,   3, item_names.gold_500),
    loc_names.villafy_fountain_shine:       CVLoDLocationData(0x68,   3, item_names.quest_crest_a),
    loc_names.villafo_front_l:              CVLoDLocationData(0x72,   3, item_names.jewel_rs),
    loc_names.villafo_front_r:              CVLoDLocationData(0x73,   3, item_names.gold_300),
    loc_names.villafo_mid_l:                CVLoDLocationData(0x71,   3, item_names.gold_300),
    loc_names.villafo_mid_r:                CVLoDLocationData(0x70,   3, item_names.jewel_rs),
    loc_names.villafo_rear_l:               CVLoDLocationData(0x6E,   3, item_names.jewel_rs),
    loc_names.villafo_rear_r:               CVLoDLocationData(0x6F,   3, item_names.jewel_rs),
    loc_names.villafo_pot_l:                CVLoDLocationData(0x6D,   3, item_names.quest_key_arch),
    loc_names.villafo_pot_r:                CVLoDLocationData(0x6C,   3, item_names.jewel_rl),
    loc_names.villafo_sofa:                 CVLoDLocationData(0x75,   3, item_names.use_purifying),
    loc_names.villafo_chandelier1:          CVLoDLocationData(0x2C2,  3, item_names.gold_500,),
    loc_names.villafo_chandelier2:          CVLoDLocationData(0x2C3,  3, item_names.jewel_rl,),
    loc_names.villafo_chandelier3:          CVLoDLocationData(0x2C4,  3, item_names.use_purifying,),
    loc_names.villafo_chandelier4:          CVLoDLocationData(0x2C5,  3, item_names.use_ampoule,),
    loc_names.villafo_chandelier5:          CVLoDLocationData(0x2C6,  3, item_names.use_chicken,),
    loc_names.villafo_6am_roses:            CVLoDLocationData(0x78,   3, item_names.quest_key_thorn),
    loc_names.villala_hallway_stairs:       CVLoDLocationData(0x80,   3, item_names.jewel_rl),
    loc_names.villala_hallway_l:            CVLoDLocationData(0x82,   3, item_names.sub_knife),
    loc_names.villala_hallway_r:            CVLoDLocationData(0x81,   3, item_names.sub_axe),
    loc_names.villala_vincent:              CVLoDLocationData(0x27F,  3, item_names.jewel_rl),
    loc_names.villala_slivingroom_table_l:  CVLoDLocationData(0x283,  3, item_names.gold_100),
    loc_names.villala_slivingroom_table_r:  CVLoDLocationData(0x8B,   3, item_names.gold_300),
    loc_names.villala_mary:                 CVLoDLocationData(0x86,   3, item_names.gold_100),
    loc_names.villala_slivingroom_mirror:   CVLoDLocationData(0x83,   3, item_names.sub_cross),
    loc_names.villala_diningroom_roses:     CVLoDLocationData(0x90,   3, item_names.use_purifying),
    loc_names.villala_llivingroom_pot_r:    CVLoDLocationData(0x27E,  3, item_names.quest_key_store),
    loc_names.villala_llivingroom_pot_l:    CVLoDLocationData(0x7E,   3, item_names.use_chicken),
    loc_names.villala_llivingroom_painting: CVLoDLocationData(0x8E,   3, item_names.use_purifying),
    loc_names.villala_llivingroom_light:    CVLoDLocationData(0x7F,   3, item_names.use_purifying),
    loc_names.villala_llivingroom_lion:     CVLoDLocationData(0x8D,   3, item_names.use_chicken),
    loc_names.villala_exit_knight:          CVLoDLocationData(0x8F,   3, item_names.use_purifying),
    loc_names.villala_storeroom_l:          CVLoDLocationData(0x2B3,  3, item_names.use_beef),
    loc_names.villala_storeroom_r:          CVLoDLocationData(0x2B2,  3, item_names.use_chicken),
    loc_names.villala_storeroom_s:          CVLoDLocationData(0x8C,   3, item_names.use_purifying),
    loc_names.villala_archives_table:       CVLoDLocationData(0x84,   3, item_names.quest_diary),
    loc_names.villala_archives_rear:        CVLoDLocationData(0x85,   3, item_names.quest_key_grdn),
    loc_names.villam_malus_torch:           CVLoDLocationData(0xA3,  17, item_names.jewel_rs),
    loc_names.villam_malus_bush:            CVLoDLocationData(0xAA,  17, item_names.use_chicken),
    loc_names.villam_fplatform:             CVLoDLocationData(0xA7,  17, item_names.sub_axe),
    loc_names.villam_frankieturf_l:         CVLoDLocationData(0x9F,  17, item_names.gold_300),
    loc_names.villam_frankieturf_r:         CVLoDLocationData(0xA8,  17, item_names.sub_holy),
    loc_names.villam_frankieturf_ru:        CVLoDLocationData(0xAC,  17, item_names.jewel_rs),
    loc_names.villam_hole_de:               CVLoDLocationData(0x281, 17, item_names.quest_key_rose),
    loc_names.villam_fgarden_f:             CVLoDLocationData(0xA5,  17, item_names.jewel_rs),
    loc_names.villam_fgarden_mf:            CVLoDLocationData(0xA2,  17, item_names.jewel_rs),
    loc_names.villam_fgarden_mr:            CVLoDLocationData(0xA4,  17, item_names.quest_brooch),
    loc_names.villam_fgarden_r:             CVLoDLocationData(0xA6,  17, item_names.jewel_rl),
    loc_names.villam_child_de:              CVLoDLocationData(0x87,  17, item_names.gold_100),
    loc_names.villam_rplatform_f:           CVLoDLocationData(0xA9,  17, item_names.sub_axe),
    loc_names.villam_rplatform_r:           CVLoDLocationData(0x9C,  17, item_names.quest_crest_b),
    loc_names.villam_rplatform_de:          CVLoDLocationData(0xA0,  17, item_names.gold_300),
    loc_names.villam_exit_de:               CVLoDLocationData(0xA1,  17, item_names.gold_300),
    loc_names.villam_serv_path_sl:          CVLoDLocationData(0xAB,  17, item_names.use_purifying),
    loc_names.villam_serv_path_sr:          CVLoDLocationData(0x280, 17, item_names.use_ampoule),
    loc_names.villam_serv_path_l:           CVLoDLocationData(0x2B1, 17, item_names.quest_key_cppr),
    loc_names.villafo_serv_ent:             CVLoDLocationData(0x74,   3, item_names.use_chicken),
    loc_names.villam_crypt_ent:             CVLoDLocationData(0x9E,  17, item_names.use_purifying),
    loc_names.villam_crypt_upstream:        CVLoDLocationData(0x9D,  17, item_names.use_beef),
    loc_names.villac_ent_l:                 CVLoDLocationData(0x192, 17, item_names.jewel_rs),
    loc_names.villac_ent_r:                 CVLoDLocationData(0x193, 17, item_names.gold_300),
    loc_names.villac_wall_l:                CVLoDLocationData(0x196, 17, item_names.sub_cross),
    loc_names.villac_wall_r:                CVLoDLocationData(0x197, 17, item_names.jewel_rl),
    loc_names.villac_coffin_l:              CVLoDLocationData(0x194, 17, item_names.jewel_rs),
    loc_names.villac_coffin_r:              CVLoDLocationData(0x195, 17, item_names.jewel_rs),

    # Tunnel
    loc_names.tunnel_landing:               CVLoDLocationData(0xB6,  4, item_names.jewel_rl),
    loc_names.tunnel_landing_rc:            CVLoDLocationData(0xB7,  4, item_names.jewel_rs),
    loc_names.tunnel_stone_alcove_r:        CVLoDLocationData(0xCC,  4, item_names.sub_holy),
    loc_names.tunnel_stone_alcove_l:        CVLoDLocationData(0xC5,  4, item_names.use_beef),
    loc_names.tunnel_twin_arrows:           CVLoDLocationData(0xD3,  4, item_names.use_ampoule),
    loc_names.tunnel_arrows_rock1:          CVLoDLocationData(0x2C7, 4, item_names.use_purifying),
    loc_names.tunnel_arrows_rock2:          CVLoDLocationData(0x2C8, 4, item_names.use_purifying),
    loc_names.tunnel_arrows_rock3:          CVLoDLocationData(0x2C9, 4, item_names.use_ampoule),
    loc_names.tunnel_arrows_rock4:          CVLoDLocationData(0x2CA, 4, item_names.use_ampoule),
    loc_names.tunnel_arrows_rock5:          CVLoDLocationData(0x2CB, 4, item_names.use_chicken),
    loc_names.tunnel_lonesome_bucket:       CVLoDLocationData(0xD6,  4, item_names.use_ampoule),
    loc_names.tunnel_lbucket_mdoor_l:       CVLoDLocationData(0xCE,  4, item_names.sub_knife),
    loc_names.tunnel_lbucket_quag:          CVLoDLocationData(0xBB,  4, item_names.jewel_rl),
    loc_names.tunnel_bucket_quag_rock1:     CVLoDLocationData(0x2CC, 4, item_names.use_chicken),
    loc_names.tunnel_bucket_quag_rock2:     CVLoDLocationData(0x2CD, 4, item_names.use_chicken),
    loc_names.tunnel_bucket_quag_rock3:     CVLoDLocationData(0x2CE, 4, item_names.use_chicken),
    loc_names.tunnel_lbucket_albert:        CVLoDLocationData(0xBC,  4, item_names.jewel_rs),
    loc_names.tunnel_albert_camp:           CVLoDLocationData(0xBA,  4, item_names.jewel_rs),
    loc_names.tunnel_albert_quag:           CVLoDLocationData(0xB9,  4, item_names.jewel_rl),
    loc_names.tunnel_gondola_rc_sdoor_l:    CVLoDLocationData(0xCD,  4, item_names.use_beef),
    loc_names.tunnel_gondola_rc_sdoor_m:    CVLoDLocationData(0xBE,  4, item_names.use_beef),
    loc_names.tunnel_gondola_rc_sdoor_r:    CVLoDLocationData(0xBD,  4, item_names.sub_cross),
    loc_names.tunnel_gondola_rc:            CVLoDLocationData(0xBF,  4, item_names.powerup),
    loc_names.tunnel_rgondola_station:      CVLoDLocationData(0xB8,  4, item_names.jewel_rs),
    loc_names.tunnel_gondola_transfer:      CVLoDLocationData(0xC7,  4, item_names.gold_500),
    loc_names.tunnel_corpse_bucket_quag:    CVLoDLocationData(0xC0,  4, item_names.jewel_rl),
    loc_names.tunnel_corpse_bucket_mdoor_l: CVLoDLocationData(0xCF,  4, item_names.sub_holy),
    loc_names.tunnel_corpse_bucket_mdoor_r: CVLoDLocationData(0xC8,  4, item_names.use_card_s),
    loc_names.tunnel_shovel_quag_start:     CVLoDLocationData(0xC1,  4, item_names.jewel_rl),
    loc_names.tunnel_exit_quag_start:       CVLoDLocationData(0xC2,  4, item_names.jewel_rl),
    loc_names.tunnel_shovel_quag_end:       CVLoDLocationData(0xC3,  4, item_names.jewel_rl),
    loc_names.tunnel_exit_quag_end:         CVLoDLocationData(0xC9,  4, item_names.gold_300),
    loc_names.tunnel_shovel:                CVLoDLocationData(0xD2,  4, item_names.use_beef),
    loc_names.tunnel_shovel_save:           CVLoDLocationData(0xC4,  4, item_names.jewel_rl),
    loc_names.tunnel_shovel_mdoor_c:        CVLoDLocationData(0x24,  4, item_names.gold_100),
    loc_names.tunnel_shovel_mdoor_l:        CVLoDLocationData(0xCA,  4, item_names.use_card_s),
    loc_names.tunnel_shovel_mdoor_r:        CVLoDLocationData(0xD0,  4, item_names.sub_axe),
    loc_names.tunnel_shovel_sdoor_l:        CVLoDLocationData(0xCB,  4, item_names.use_card_m),
    loc_names.tunnel_shovel_sdoor_m:        CVLoDLocationData(0xC6,  4, item_names.use_chicken),
    loc_names.tunnel_shovel_sdoor_r:        CVLoDLocationData(0xD1,  4, item_names.sub_cross),

    # Underground Waterway
    loc_names.uw_near_ent:         CVLoDLocationData(0xDC,  5, item_names.gold_300),
    loc_names.uw_across_ent:       CVLoDLocationData(0xDD,  5, item_names.gold_300),
    loc_names.uw_first_ledge1:     CVLoDLocationData(0x2CF, 5, item_names.use_purifying,),
    loc_names.uw_first_ledge2:     CVLoDLocationData(0x2D0, 5, item_names.use_purifying,),
    loc_names.uw_first_ledge3:     CVLoDLocationData(0x2D1, 5, item_names.use_ampoule,),
    loc_names.uw_first_ledge4:     CVLoDLocationData(0x2D2, 5, item_names.use_ampoule,),
    loc_names.uw_first_ledge5:     CVLoDLocationData(0x2D3, 5, item_names.gold_300,),
    loc_names.uw_first_ledge6:     CVLoDLocationData(0x2D4, 5, item_names.gold_300,),
    loc_names.uw_poison_parkour:   CVLoDLocationData(0xDE,  5, item_names.use_ampoule),
    loc_names.uw_waterfall_ledge:  CVLoDLocationData(0xE2,  5, item_names.gold_500),
    loc_names.uw_waterfall_child:  CVLoDLocationData(0x25,  5, item_names.gold_100),
    loc_names.uw_carrie1:          CVLoDLocationData(0xDF,  5, item_names.use_card_m),
    loc_names.uw_carrie2:          CVLoDLocationData(0xE0,  5, item_names.use_beef),
    loc_names.uw_bricks_save:      CVLoDLocationData(0xE1,  5, item_names.powerup),
    loc_names.uw_above_skel_ledge: CVLoDLocationData(0xE3,  5, item_names.use_chicken),
    loc_names.uw_in_skel_ledge1:   CVLoDLocationData(0x2D5, 5, item_names.use_chicken,),
    loc_names.uw_in_skel_ledge2:   CVLoDLocationData(0x2D6, 5, item_names.use_chicken,),
    loc_names.uw_in_skel_ledge3:   CVLoDLocationData(0x2D7, 5, item_names.use_chicken,),

    # The Outer Wall
    loc_names.towf_start_rear:           CVLoDLocationData(0x26A, 6, item_names.gold_500),
    loc_names.towf_start_front:          CVLoDLocationData(0x269, 6, item_names.jewel_rl),
    loc_names.towf_start_entry_l:        CVLoDLocationData(0x300, 6, item_names.gold_100),
    loc_names.towf_start_entry_r:        CVLoDLocationData(0x301, 6, item_names.gold_100),
    loc_names.towf_start_climb_b:        CVLoDLocationData(0x267, 6, item_names.sub_axe),
    loc_names.towf_start_climb_t:        CVLoDLocationData(0x268, 6, item_names.jewel_rs),
    loc_names.towf_start_elevator_l:     CVLoDLocationData(0x302, 6, item_names.gold_300),
    loc_names.towf_start_elevator_r:     CVLoDLocationData(0x303, 6, item_names.gold_300),
    loc_names.towse_pillar_l:            CVLoDLocationData(0x26B, 6, item_names.jewel_rl),
    loc_names.towse_pillar_r:            CVLoDLocationData(0x26C, 6, item_names.gold_300),
    loc_names.towse_eagle:               CVLoDLocationData(0x266, 6, item_names.use_beef),
    loc_names.towse_saws_door_l:         CVLoDLocationData(0x26D, 6, item_names.use_card_s),
    loc_names.towse_saws_door_r:         CVLoDLocationData(0x26E, 6, item_names.sub_axe),
    loc_names.towse_child:               CVLoDLocationData(0x26,  6, item_names.gold_100),
    loc_names.towse_key_ledge:           CVLoDLocationData(0x26F, 6, item_names.jewel_rl),
    loc_names.towse_key_entry_l:         CVLoDLocationData(0x304, 6, item_names.gold_500),
    loc_names.towse_key_entry_r:         CVLoDLocationData(0x305, 6, item_names.gold_500),
    loc_names.towse_key_alcove:          CVLoDLocationData(0x285, 6, item_names.quest_key_wall),
    loc_names.towse_locked_door_l:       CVLoDLocationData(0x306, 6, item_names.jewel_rs),
    loc_names.towse_locked_door_r:       CVLoDLocationData(0x307, 6, item_names.jewel_rs),
    loc_names.towse_half_arch_under:     CVLoDLocationData(0x271, 6, item_names.gold_300),
    loc_names.towse_half_arch_between:   CVLoDLocationData(0x272, 6, item_names.jewel_rs),
    loc_names.towse_half_arch_secret:    CVLoDLocationData(0x270, 6, item_names.use_beef),
    loc_names.towf_retract_elevator_l:   CVLoDLocationData(0x308, 6, item_names.jewel_rl),
    loc_names.towf_retract_elevator_r:   CVLoDLocationData(0x309, 6, item_names.jewel_rl),
    loc_names.towf_retract_shimmy_start: CVLoDLocationData(0x273, 6, item_names.jewel_rs),
    loc_names.towf_retract_shimmy_mid:   CVLoDLocationData(0x274, 6, item_names.use_card_m),
    loc_names.towf_boulders_door_l:      CVLoDLocationData(0x275, 6, item_names.sub_cross),
    loc_names.towf_boulders_door_r:      CVLoDLocationData(0x276, 6, item_names.gold_300),
    loc_names.towh_boulders_elevator_l:  CVLoDLocationData(0x30A, 6, item_names.jewel_rl),
    loc_names.towh_boulders_elevator_r:  CVLoDLocationData(0x30B, 6, item_names.jewel_rl),
    loc_names.towh_near_boulders_exit:   CVLoDLocationData(0x277, 6, item_names.sub_axe),
    loc_names.towh_slide_start:          CVLoDLocationData(0x278, 6, item_names.jewel_rs),
    loc_names.towh_slide_first_u:        CVLoDLocationData(0x27A, 6, item_names.sub_cross),
    loc_names.towh_slide_first_l:        CVLoDLocationData(0x279, 6, item_names.use_chicken),
    loc_names.towh_slide_second:         CVLoDLocationData(0x27B, 6, item_names.jewel_rl),

    # Art Tower
    loc_names.atm_ww:            CVLoDLocationData(0x22A, 7, item_names.gold_300),
    loc_names.atm_nw_ped:        CVLoDLocationData(0x236, 7, item_names.sub_holy),
    loc_names.atm_nw_corner:     CVLoDLocationData(0x22B, 7, item_names.use_card_m),
    loc_names.atm_sw_alcove_1:   CVLoDLocationData(0x22C, 7, item_names.jewel_rl),
    loc_names.atm_sw_alcove_2:   CVLoDLocationData(0x22D, 7, item_names.jewel_rs),
    loc_names.atm_sw_alcove_4:   CVLoDLocationData(0x22E, 7, item_names.gold_100),
    loc_names.atm_sw_alcove_6:   CVLoDLocationData(0x22F, 7, item_names.sub_holy),
    loc_names.atm_sw_key_ped:    CVLoDLocationData(0x286, 7, item_names.quest_key_art_1),
    loc_names.atm_sw_key_corner: CVLoDLocationData(0x230, 7, item_names.use_purifying),
    loc_names.atm_se:            CVLoDLocationData(0x231, 7, item_names.powerup),
    loc_names.atm_ne_ped:        CVLoDLocationData(0x237, 7, item_names.gold_500),
    loc_names.atm_ne_near:       CVLoDLocationData(0x232, 7, item_names.use_card_s),
    loc_names.atm_ee_plat_1:     CVLoDLocationData(0x233, 7, item_names.jewel_rs),
    loc_names.atm_ee_plat_2:     CVLoDLocationData(0x234, 7, item_names.jewel_rl),
    loc_names.atm_ee_key_ped:    CVLoDLocationData(0x287, 7, item_names.quest_key_art_2),
    loc_names.atm_ee_key_corner: CVLoDLocationData(0x235, 7, item_names.use_card_m),
    loc_names.atc_sw_statue_l:   CVLoDLocationData(0x23D, 7, item_names.use_purifying),
    loc_names.atc_sw_statue_r:   CVLoDLocationData(0x23C, 7, item_names.jewel_rl),
    loc_names.atc_ne_statue_l:   CVLoDLocationData(0x23E, 7, item_names.jewel_rs),
    loc_names.atc_ne_statue_r:   CVLoDLocationData(0x23F, 7, item_names.jewel_rs),
    loc_names.atc_organ:         CVLoDLocationData(0x23B, 7, item_names.use_ampoule),
    loc_names.atc_pillar_l:      CVLoDLocationData(0x23A, 7, item_names.use_chicken),
    loc_names.atc_pillar_r:      CVLoDLocationData(0x239, 7, item_names.sub_cross),
    loc_names.atc_doorway_l:     CVLoDLocationData(0x2AF, 7, item_names.gold_500),
    loc_names.atc_doorway_m:     CVLoDLocationData(0x2AE, 7, item_names.use_beef),
    loc_names.atc_doorway_r:     CVLoDLocationData(0x2B0, 7, item_names.gold_500),
    loc_names.atc_balcony_save:  CVLoDLocationData(0x240, 7, item_names.sub_cross),
    loc_names.atc_bp_f:          CVLoDLocationData(0x241, 7, item_names.use_purifying),
    loc_names.atc_bp_r:          CVLoDLocationData(0x242, 7, item_names.gold_300),

    # Tower of Ruins
    loc_names.torm_trap_side:   CVLoDLocationData(0x20D, 8, item_names.sub_holy),
    loc_names.torm_trap_corner: CVLoDLocationData(0x20E, 8, item_names.jewel_rl),
    loc_names.torm_b6:          CVLoDLocationData(0x201, 8, item_names.gold_300),
    loc_names.torm_b4_corner:   CVLoDLocationData(0x206, 8, item_names.jewel_rl),
    loc_names.torm_b4_statue:   CVLoDLocationData(0x200, 8, item_names.use_chicken),
    loc_names.torm_a3:          CVLoDLocationData(0x205, 8, item_names.powerup),
    loc_names.torm_b2:          CVLoDLocationData(0x208, 8, item_names.sub_holy),
    loc_names.torm_a1:          CVLoDLocationData(0x207, 8, item_names.gold_300),
    loc_names.torm_d4:          CVLoDLocationData(0x203, 8, item_names.powerup),
    loc_names.torm_g4:          CVLoDLocationData(0x20B, 8, item_names.use_purifying),
    loc_names.torm_g3_l:        CVLoDLocationData(0x209, 8, item_names.sub_holy),
    loc_names.torm_g3_r:        CVLoDLocationData(0x20A, 8, item_names.sub_cross),
    loc_names.torm_g3_statue:   CVLoDLocationData(0x202, 8, item_names.gold_300),
    loc_names.torm_lookback_l:  CVLoDLocationData(0x211, 8, item_names.jewel_rs),
    loc_names.torm_lookback_r:  CVLoDLocationData(0x210, 8, item_names.jewel_rs),
    loc_names.torm_lookback_u:  CVLoDLocationData(0x20C, 8, item_names.use_chicken),
    loc_names.torc_lfloor_f:    CVLoDLocationData(0x215, 8, item_names.jewel_rl),
    loc_names.torc_lfloor_r:    CVLoDLocationData(0x216, 8, item_names.jewel_rs),
    loc_names.torc_walkway_l:   CVLoDLocationData(0x21C, 8, item_names.jewel_rs),
    loc_names.torc_ufloor_rl:   CVLoDLocationData(0x21B, 8, item_names.jewel_rs),
    loc_names.torc_ufloor_m:    CVLoDLocationData(0x219, 8, item_names.powerup),
    loc_names.torc_ufloor_fr:   CVLoDLocationData(0x21A, 8, item_names.sub_holy),
    loc_names.torc_meat_l:      CVLoDLocationData(0x2AC, 8, item_names.use_beef),
    loc_names.torc_meat_r:      CVLoDLocationData(0x2AD, 8, item_names.powerup),
    loc_names.torc_walkway_u:   CVLoDLocationData(0x21D, 8, item_names.gold_300),
    loc_names.torc_aries:       CVLoDLocationData(0x21E, 8, item_names.jewel_rs),
    loc_names.torc_taurus:      CVLoDLocationData(0x21F, 8, item_names.gold_100),
    loc_names.torc_leo:         CVLoDLocationData(0x220, 8, item_names.use_purifying),
    loc_names.torc_sagittarius: CVLoDLocationData(0x221, 8, item_names.sub_cross),
    loc_names.torc_across_exit: CVLoDLocationData(0x223, 8, item_names.use_card_m),
    loc_names.torc_near_exit:   CVLoDLocationData(0x222, 8, item_names.use_card_s),

    # Castle Center
    loc_names.ccb_skel_hallway_ent:          CVLoDLocationData(0xF5,   9, item_names.jewel_rs),
    loc_names.ccb_skel_hallway_jun:          CVLoDLocationData(0xF8,   9, item_names.powerup),
    loc_names.ccb_skel_hallway_tc:           CVLoDLocationData(0xF6,   9, item_names.jewel_rl),
    loc_names.ccb_skel_hallway_ba:           CVLoDLocationData(0xF7,   9, item_names.sub_cross),
    loc_names.ccb_behemoth_l_ff:             CVLoDLocationData(0xF9,   9, item_names.jewel_rs),
    loc_names.ccb_behemoth_l_mf:             CVLoDLocationData(0xFA,   9, item_names.gold_300),
    loc_names.ccb_behemoth_l_mr:             CVLoDLocationData(0xFB,   9, item_names.jewel_rl),
    loc_names.ccb_behemoth_l_fr:             CVLoDLocationData(0xFC,   9, item_names.gold_500),
    loc_names.ccb_behemoth_r_ff:             CVLoDLocationData(0x100,  9, item_names.gold_300),
    loc_names.ccb_behemoth_r_mf:             CVLoDLocationData(0xFF,   9, item_names.jewel_rl),
    loc_names.ccb_behemoth_r_mr:             CVLoDLocationData(0xFE,   9, item_names.gold_500),
    loc_names.ccb_behemoth_r_fr:             CVLoDLocationData(0xFD,   9, item_names.jewel_rl),
    loc_names.ccb_behemoth_crate1:           CVLoDLocationData(0x2D8,  9, item_names.gold_500,),
    loc_names.ccb_behemoth_crate2:           CVLoDLocationData(0x2D9,  9, item_names.gold_500,),
    loc_names.ccb_behemoth_crate3:           CVLoDLocationData(0x2DA,  9, item_names.gold_500,),
    loc_names.ccb_behemoth_crate4:           CVLoDLocationData(0x2DB,  9, item_names.gold_500,),
    loc_names.ccb_behemoth_crate5:           CVLoDLocationData(0x2DC,  9, item_names.gold_500,),
    loc_names.ccbe_near_machine:             CVLoDLocationData(0x108,  9, item_names.jewel_rs),
    loc_names.ccbe_atop_machine:             CVLoDLocationData(0x109,  9, item_names.powerup),
    loc_names.ccbe_stand1:                   CVLoDLocationData(0x2DD,  9, item_names.use_beef,),
    loc_names.ccbe_stand2:                   CVLoDLocationData(0x2DE,  9, item_names.use_beef,),
    loc_names.ccbe_stand3:                   CVLoDLocationData(0x2DF,  9, item_names.use_beef,),
    loc_names.ccbe_pipes:                    CVLoDLocationData(0x10A,  9, item_names.gold_300),
    loc_names.ccbe_switch:                   CVLoDLocationData(0x10C,  9, item_names.sub_holy),
    loc_names.ccbe_staircase:                CVLoDLocationData(0x10B,  9, item_names.jewel_rl),
    loc_names.ccff_gears_side:               CVLoDLocationData(0x10E,  9, item_names.jewel_rs),
    loc_names.ccff_gears_mid:                CVLoDLocationData(0x10F,  9, item_names.use_purifying),
    loc_names.ccff_gears_corner:             CVLoDLocationData(0x110,  9, item_names.use_chicken),
    loc_names.ccff_lizard_near_knight:       CVLoDLocationData(0x111,  9, item_names.sub_axe),
    loc_names.ccff_lizard_pit:               CVLoDLocationData(0x112,  9, item_names.use_card_s),
    loc_names.ccff_lizard_corner:            CVLoDLocationData(0x113,  9, item_names.use_card_m),
    loc_names.ccff_lizard_locker_nfr:        CVLoDLocationData(0x117,  9, item_names.jewel_rl),
    loc_names.ccff_lizard_locker_nmr:        CVLoDLocationData(0x118,  9, item_names.gold_500),
    loc_names.ccff_lizard_locker_nml:        CVLoDLocationData(0x119,  9, item_names.use_ampoule),
    loc_names.ccff_lizard_locker_nfl:        CVLoDLocationData(0x11A,  9, item_names.powerup),
    loc_names.ccff_lizard_locker_fl:         CVLoDLocationData(0x11B,  9, item_names.gold_500),
    loc_names.ccff_lizard_locker_fr:         CVLoDLocationData(0x11C,  9, item_names.use_card_s),
    loc_names.ccff_lizard_slab1:             CVLoDLocationData(0x2E0,  9, item_names.use_purifying,),
    loc_names.ccff_lizard_slab2:             CVLoDLocationData(0x2E1,  9, item_names.use_purifying,),
    loc_names.ccff_lizard_slab3:             CVLoDLocationData(0x2E2,  9, item_names.use_ampoule,),
    loc_names.ccff_lizard_slab4:             CVLoDLocationData(0x2E3,  9, item_names.use_ampoule,),
    loc_names.ccb_mandrag_shelf_l:           CVLoDLocationData(0x30C,  9, item_names.quest_mandragora),
    loc_names.ccb_mandrag_shelf_r:           CVLoDLocationData(0x30D,  9, item_names.quest_mandragora),
    loc_names.ccb_torture_rack:              CVLoDLocationData(0x101,  9, item_names.use_purifying),
    loc_names.ccb_torture_rafters:           CVLoDLocationData(0x102,  9, item_names.use_beef),
    loc_names.ccll_brokenstairs_floor:       CVLoDLocationData(0x123, 18, item_names.jewel_rl),
    loc_names.ccll_brokenstairs_save:        CVLoDLocationData(0x122, 18, item_names.jewel_rl),
    loc_names.ccll_glassknight_l:            CVLoDLocationData(0x12A, 18, item_names.jewel_rs),
    loc_names.ccll_glassknight_r:            CVLoDLocationData(0x12B, 18, item_names.jewel_rs),
    loc_names.ccll_butlers_door:             CVLoDLocationData(0x125, 18, item_names.jewel_rs),
    loc_names.ccll_butlers_side:             CVLoDLocationData(0x124, 18, item_names.use_purifying),
    loc_names.ccll_cwhall_butlerflames_past: CVLoDLocationData(0x126, 18, item_names.use_ampoule),
    loc_names.ccll_cwhall_flamethrower:      CVLoDLocationData(0x129, 18, item_names.gold_500),
    loc_names.ccll_cwhall_cwflames:          CVLoDLocationData(0x127, 18, item_names.use_chicken),
    loc_names.ccll_heinrich:                 CVLoDLocationData(0x284, 18, item_names.quest_key_chbr),
    loc_names.ccia_nitro_crates:             CVLoDLocationData(0x13A, 18, item_names.use_kit),
    loc_names.ccia_nitro_shelf_h:            CVLoDLocationData(0x30E, 18, item_names.quest_nitro),
    loc_names.ccia_stairs_knight:            CVLoDLocationData(0x13B, 18, item_names.gold_500),
    loc_names.ccia_maids_vase:               CVLoDLocationData(0x135, 18, item_names.jewel_rl),
    loc_names.ccia_maids_outer:              CVLoDLocationData(0x130, 18, item_names.use_purifying),
    loc_names.ccia_maids_inner:              CVLoDLocationData(0x131, 18, item_names.use_ampoule),
    loc_names.ccia_inventions_maids:         CVLoDLocationData(0x133, 18, item_names.use_card_m),
    loc_names.ccia_inventions_crusher:       CVLoDLocationData(0x132, 18, item_names.use_card_s),
    loc_names.ccia_inventions_famicart:      CVLoDLocationData(0x137, 18, item_names.gold_500),
    loc_names.ccia_inventions_zeppelin:      CVLoDLocationData(0x2AA, 18, item_names.use_beef),
    loc_names.ccia_inventions_round:         CVLoDLocationData(0x138, 18, item_names.use_beef),
    loc_names.ccia_nitrohall_flamethrower:   CVLoDLocationData(0x139, 18, item_names.jewel_rl),
    loc_names.ccia_nitrohall_torch:          CVLoDLocationData(0x134, 18, item_names.use_chicken),
    loc_names.ccia_nitro_shelf_i:            CVLoDLocationData(0x30F, 18, item_names.quest_nitro),
    loc_names.ccll_cwhall_wall:              CVLoDLocationData(0x128, 18, item_names.use_beef),
    loc_names.ccl_bookcase:                  CVLoDLocationData(0x13E, 18, item_names.use_card_s),

    # Duel Tower
    loc_names.dt_pre_sweeper_l:  CVLoDLocationData(0x249, 10, item_names.jewel_rs),
    loc_names.dt_pre_sweeper_r:  CVLoDLocationData(0x248, 10, item_names.jewel_rs),
    loc_names.dt_werewolf_ledge: CVLoDLocationData(0x254, 10, item_names.powerup),
    loc_names.dt_post_sweeper_l: CVLoDLocationData(0x252, 10, item_names.jewel_rs),
    loc_names.dt_post_sweeper_r: CVLoDLocationData(0x253, 10, item_names.jewel_rs),
    loc_names.dt_slant_l:        CVLoDLocationData(0x24B, 10, item_names.gold_300),
    loc_names.dt_slant_r:        CVLoDLocationData(0x24A, 10, item_names.jewel_rs),
    loc_names.dt_pinwheels_l:    CVLoDLocationData(0x24C, 10, item_names.use_chicken),
    loc_names.dt_pinwheels_r:    CVLoDLocationData(0x24D, 10, item_names.jewel_rl),
    loc_names.dt_guards_l:       CVLoDLocationData(0x24E, 10, item_names.jewel_rs),
    loc_names.dt_guards_r:       CVLoDLocationData(0x24F, 10, item_names.gold_300),
    loc_names.dt_werebull_l:     CVLoDLocationData(0x251, 10, item_names.use_chicken),
    loc_names.dt_werebull_r:     CVLoDLocationData(0x250, 10, item_names.powerup),

    # Tower of Execution
    loc_names.toe_start_l:          CVLoDLocationData(0x1BB, 11, item_names.sub_axe),
    loc_names.toe_start_r:          CVLoDLocationData(0x1BC, 11, item_names.jewel_rs),
    loc_names.toe_spike_alcove_l:   CVLoDLocationData(0x1BE, 11, item_names.use_purifying),
    loc_names.toe_spike_alcove_r:   CVLoDLocationData(0x1BD, 11, item_names.gold_100),
    loc_names.toe_spike_platform_l: CVLoDLocationData(0x1C0, 11, item_names.gold_300),
    loc_names.toe_spike_platform_r: CVLoDLocationData(0x1BF, 11, item_names.sub_knife),
    loc_names.toem_stones_l:        CVLoDLocationData(0x1CD, 11, item_names.jewel_rl),
    loc_names.toem_stones_r:        CVLoDLocationData(0x1CE, 11, item_names.gold_100),
    loc_names.toem_walkway:         CVLoDLocationData(0x1CF, 11, item_names.gold_300),
    loc_names.toeg_platform:        CVLoDLocationData(0x1C5, 11, item_names.jewel_rl),
    loc_names.toeg_alcove_l:        CVLoDLocationData(0x1C7, 11, item_names.use_ampoule),
    loc_names.toeg_alcove_r:        CVLoDLocationData(0x1C6, 11, item_names.sub_holy),
    loc_names.toeb_midway_l:        CVLoDLocationData(0x1C8, 11, item_names.jewel_rl),
    loc_names.toeb_midway_r:        CVLoDLocationData(0x1C9, 11, item_names.use_card_m),
    loc_names.toeb_corner:          CVLoDLocationData(0x1CA, 11, item_names.use_beef),
    loc_names.toe_renon_l:          CVLoDLocationData(0x1C2, 11, item_names.gold_500),
    loc_names.toe_renon_r:          CVLoDLocationData(0x1C1, 11, item_names.use_card_s),
    loc_names.toe_knights:          CVLoDLocationData(0x1C3, 11, item_names.sub_cross),
    loc_names.toe_first_pillar:     CVLoDLocationData(0x1B5, 11, item_names.powerup),
    loc_names.toe_last_pillar:      CVLoDLocationData(0x1B8, 11, item_names.sub_cross),
    loc_names.toe_tower:            CVLoDLocationData(0x1BA, 11, item_names.use_beef),
    loc_names.toe_top_platform:     CVLoDLocationData(0x1C4, 11, item_names.use_chicken),
    loc_names.toeu_fort_save:       CVLoDLocationData(0x1D3, 11, item_names.use_card_s),
    loc_names.toeu_fort_ibridge:    CVLoDLocationData(0x1D4, 11, item_names.use_chicken),
    loc_names.toeu_fort_left:       CVLoDLocationData(0x1D5, 11, item_names.sub_cross),
    loc_names.toeu_fort_lookout:    CVLoDLocationData(0x1CB, 11, item_names.sub_cross),
    loc_names.toeu_ult_l:           CVLoDLocationData(0x1D0, 11, item_names.gold_300),
    loc_names.toeu_ult_r:           CVLoDLocationData(0x1D1, 11, item_names.jewel_rl),
    loc_names.toeu_ult_crack:       CVLoDLocationData(0x1CC, 11, item_names.jewel_rs),
    loc_names.toeu_jails:           CVLoDLocationData(0x1D7, 11, item_names.gold_100),
    loc_names.toeu_end_l:           CVLoDLocationData(0x1D9, 11, item_names.jewel_rs),
    loc_names.toeu_end_r:           CVLoDLocationData(0x1D8, 11, item_names.jewel_rs),

    # Tower of Science
    loc_names.toscic_first:             CVLoDLocationData(0x1DC, 12, item_names.gold_300),
    loc_names.toscic_second:            CVLoDLocationData(0x1DB, 12, item_names.jewel_rs),
    loc_names.toscic_elevator:          CVLoDLocationData(0x1DA, 12, item_names.jewel_rs),
    loc_names.toscit_lone_c:            CVLoDLocationData(0x1E6, 12, item_names.gold_300),
    loc_names.toscit_lone_rl:           CVLoDLocationData(0x1E7, 12, item_names.jewel_rs),
    loc_names.toscit_lone_rr:           CVLoDLocationData(0x1E8, 12, item_names.gold_300),
    loc_names.toscit_sec_1:             CVLoDLocationData(0x1E9, 12, item_names.sub_axe),
    loc_names.toscit_sec_2:             CVLoDLocationData(0x1EA, 12, item_names.jewel_rl),
    loc_names.toscit_sec_check_l:       CVLoDLocationData(0x1EC, 12, item_names.powerup),
    loc_names.toscit_sec_check_r:       CVLoDLocationData(0x1EB, 12, item_names.jewel_rs),
    loc_names.toscit_25d_pipes:         CVLoDLocationData(0x1EE, 12, item_names.sub_holy),
    loc_names.toscit_25d_cover:         CVLoDLocationData(0x1ED, 12, item_names.use_chicken),
    loc_names.toscit_course_d1_l:       CVLoDLocationData(0x1F0, 12, item_names.gold_300),
    loc_names.toscit_course_d1_r:       CVLoDLocationData(0x1EF, 12, item_names.jewel_rs),
    loc_names.toscit_course_d2_l:       CVLoDLocationData(0x1F1, 12, item_names.sub_cross),
    loc_names.toscit_course_d2_r:       CVLoDLocationData(0x1F2, 12, item_names.sub_knife),
    loc_names.toscit_course_d3_l:       CVLoDLocationData(0x1F3, 12, item_names.use_chicken),
    loc_names.toscit_course_d3_c:       CVLoDLocationData(0x1F6, 12, item_names.gold_300),
    loc_names.toscit_course_alcove:     CVLoDLocationData(0x1F5, 12, item_names.jewel_rs),
    loc_names.toscit_course_end:        CVLoDLocationData(0x288, 12, item_names.quest_key_ctrl),
    loc_names.toscit_ctrl_fl:           CVLoDLocationData(0x1E2, 12, item_names.jewel_rl),
    loc_names.toscit_ctrl_fr:           CVLoDLocationData(0x1E3, 12, item_names.jewel_rl),
    loc_names.toscit_ctrl_l:            CVLoDLocationData(0x1E1, 12, item_names.use_chicken),
    loc_names.toscit_ctrl_r:            CVLoDLocationData(0x1E4, 12, item_names.jewel_rs),
    loc_names.toscit_ctrl_rl:           CVLoDLocationData(0x1E0, 12, item_names.jewel_rs),
    loc_names.toscit_ctrl_rr:           CVLoDLocationData(0x1E5, 12, item_names.jewel_rs),
    loc_names.toscit_ctrl_interface_f:  CVLoDLocationData(0x1F4, 12, item_names.gold_300),
    loc_names.toscit_ctrl_interface_rl: CVLoDLocationData(0x1F7, 12, item_names.use_chicken),
    loc_names.toscit_ctrl_interface_rr: CVLoDLocationData(0x1F8, 12, item_names.use_card_s),

    # Tower of Sorcery
    loc_names.tosor_icemen_l:   CVLoDLocationData(0x318, 13, item_names.jewel_rs),
    loc_names.tosor_icemen_r:   CVLoDLocationData(0x319, 13, item_names.jewel_rl),
    loc_names.tosor_archi:      CVLoDLocationData(0x1A9, 13, item_names.jewel_rs),
    loc_names.tosor_side_isle:  CVLoDLocationData(0x31A, 13, item_names.gold_500),
    loc_names.tosor_mag_bridge: CVLoDLocationData(0x31B, 13, item_names.gold_300),
    loc_names.tosor_lasers_m:   CVLoDLocationData(0x1AA, 13, item_names.sub_axe),
    loc_names.tosor_lasers_s:   CVLoDLocationData(0x31C, 13, item_names.gold_100),
    loc_names.tosor_climb_l:    CVLoDLocationData(0x1AB, 13, item_names.jewel_rs),
    loc_names.tosor_climb_r:    CVLoDLocationData(0x1AC, 13, item_names.gold_300),
    loc_names.tosor_climb_m:    CVLoDLocationData(0x31D, 13, item_names.jewel_rl),
    loc_names.tosor_ibridge:    CVLoDLocationData(0x1AD, 13, item_names.powerup),
    loc_names.tosor_super_1:    CVLoDLocationData(0x310, 13, item_names.gold_500),
    loc_names.tosor_super_2:    CVLoDLocationData(0x311, 13, item_names.gold_500),
    loc_names.tosor_super_3:    CVLoDLocationData(0x312, 13, item_names.use_kit),

    # Room of Clocks
    loc_names.roc_ent_l:  CVLoDLocationData(0x19C, 14, item_names.jewel_rl),
    loc_names.roc_ent_r:  CVLoDLocationData(0x2B5, 14, item_names.powerup),
    loc_names.roc_elev_r: CVLoDLocationData(0x19E, 14, item_names.sub_axe),
    loc_names.roc_elev_l: CVLoDLocationData(0x19D, 14, item_names.sub_cross),
    loc_names.roc_cont_r: CVLoDLocationData(0x19F, 14, item_names.jewel_rs),
    loc_names.roc_cont_l: CVLoDLocationData(0x1A1, 14, item_names.sub_holy),
    loc_names.roc_exit:   CVLoDLocationData(0x1A0, 14, item_names.sub_knife),

    # Clock Tower
    loc_names.ctgc_gearclimb_battery_slab1: CVLoDLocationData(0x2E4, 15, item_names.gold_500,),
    loc_names.ctgc_gearclimb_battery_slab2: CVLoDLocationData(0x2E5, 15, item_names.gold_500,),
    loc_names.ctgc_gearclimb_battery_slab3: CVLoDLocationData(0x2E6, 15, item_names.gold_500,),
    loc_names.ctgc_gearclimb_battery_slab4: CVLoDLocationData(0x2E7, 15, item_names.gold_500,),
    loc_names.ctgc_gearclimb_battery_slab5: CVLoDLocationData(0x2E8, 15, item_names.gold_500,),
    loc_names.ctgc_gearclimb_battery_slab6: CVLoDLocationData(0x2E9, 15, item_names.gold_500,),
    loc_names.ctgc_gearclimb_corner_r:      CVLoDLocationData(0x289, 15, item_names.quest_key_clock_a),
    loc_names.ctgc_gearclimb_corner_f:      CVLoDLocationData(0x181, 15, item_names.jewel_rl),
    loc_names.ctgc_gearclimb_door_slab1:    CVLoDLocationData(0x2EA, 15, item_names.use_chicken,),
    loc_names.ctgc_gearclimb_door_slab2:    CVLoDLocationData(0x2EB, 15, item_names.use_chicken,),
    loc_names.ctgc_gearclimb_door_slab3:    CVLoDLocationData(0x2EC, 15, item_names.use_chicken,),
    loc_names.ctgc_bp_chasm_fl:             CVLoDLocationData(0x182, 15, item_names.gold_300),
    loc_names.ctgc_bp_chasm_fr:             CVLoDLocationData(0x183, 15, item_names.jewel_rl),
    loc_names.ctgc_bp_chasm_rl:             CVLoDLocationData(0x180, 15, item_names.sub_knife),
    loc_names.ctgc_bp_chasm_k:              CVLoDLocationData(0x28A, 15, item_names.quest_key_clock_b),
    loc_names.ctga_near_floor:              CVLoDLocationData(0x256, 15, item_names.gold_300),
    loc_names.ctga_near_climb:              CVLoDLocationData(0x28B, 15, item_names.quest_key_clock_c),
    loc_names.ctga_far_slab1:               CVLoDLocationData(0x2ED, 15, item_names.jewel_rl),
    loc_names.ctga_far_slab2:               CVLoDLocationData(0x2EE, 15, item_names.powerup),
    loc_names.ctga_far_slab3:               CVLoDLocationData(0x2EF, 15, item_names.use_card_s),
    loc_names.ctga_far_slab4:               CVLoDLocationData(0x2F0, 15, item_names.gold_100),
    loc_names.ctga_far_alcove:              CVLoDLocationData(0x28C, 15, item_names.quest_key_clock_d),
    loc_names.ctf_clock:                    CVLoDLocationData(0x28D, 15, item_names.quest_key_clock_e),
    loc_names.ctf_walkway_end:              CVLoDLocationData(0x25E, 15, item_names.jewel_rs),
    loc_names.ctf_engine_floor:             CVLoDLocationData(0x260, 15, item_names.jewel_rs),
    loc_names.ctf_engine_furnace:           CVLoDLocationData(0x261, 15, item_names.gold_300),
    loc_names.ctf_pendulums_l:              CVLoDLocationData(0x25D, 15, item_names.use_beef),
    loc_names.ctf_pendulums_r:              CVLoDLocationData(0x25C, 15, item_names.use_chicken),
    loc_names.ctf_slope_slab1:              CVLoDLocationData(0x2F1, 15, item_names.gold_500),
    loc_names.ctf_slope_slab2:              CVLoDLocationData(0x2F2, 15, item_names.powerup),
    loc_names.ctf_slope_slab3:              CVLoDLocationData(0x2F3, 15, item_names.gold_500),
    loc_names.ctf_walkway_mid:              CVLoDLocationData(0x25F, 15, item_names.powerup),

    # Castle Keep
    loc_names.ck_renon_sw:    CVLoDLocationData(0x176, 16, item_names.use_ampoule),
    loc_names.ck_renon_se:    CVLoDLocationData(0x175, 16, item_names.jewel_rl),
    loc_names.ck_renon_nw:    CVLoDLocationData(0x178, 16, item_names.use_ampoule),
    loc_names.ck_renon_ne:    CVLoDLocationData(0x177, 16, item_names.use_purifying),
    loc_names.ck_flame_l:     CVLoDLocationData(0x179, 16, item_names.use_beef),
    loc_names.ck_flame_r:     CVLoDLocationData(0x17A, 16, item_names.use_beef),
    loc_names.ck_behind_drac: CVLoDLocationData(0x173, 16, item_names.powerup),
    loc_names.ck_cube:        CVLoDLocationData(0x174, 16, item_names.use_chicken),
}

LOC_IDS_TO_INFO = {loc_info.flag_id: loc_info for loc_name, loc_info in CVLOD_LOCATIONS_INFO.items()}

# All event Locations mapped to their respective event Items.
# Because this is the only info we need for them, they are kept separate from the regular Item checks for nicer typing.
CVLOD_EVENT_MAPPING: dict[str, str] = {
    loc_names.event_cw_right: item_names.event_cw_right,
    loc_names.event_cw_left: item_names.event_cw_left,
    loc_names.event_villa_rosa: item_names.event_villa_rosa,
    loc_names.event_villa_child: item_names.event_villa_child,
    loc_names.event_tow_switch: item_names.event_tow_switch,
    loc_names.event_cc_planets: item_names.event_cc_planets,
    loc_names.event_cc_elevator: item_names.event_cc_elevator,
    loc_names.event_cc_crystal: item_names.event_crystal,
    loc_names.event_fl_boss: item_names.event_trophy,
    loc_names.event_forest_boss_1: item_names.event_trophy,
    loc_names.event_forest_boss_2: item_names.event_trophy,
    loc_names.event_forest_boss_3: item_names.event_trophy,
    loc_names.event_forest_boss_4: item_names.event_trophy,
    loc_names.event_cw_boss: item_names.event_trophy,
    loc_names.event_villa_boss_1: item_names.event_trophy,
    loc_names.event_villa_boss_2: item_names.event_trophy,
    loc_names.event_villa_boss_3: item_names.event_trophy,
    loc_names.event_villa_boss_4: item_names.event_trophy,
    loc_names.event_villa_boss_5: item_names.event_trophy,
    loc_names.event_tunnel_boss: item_names.event_trophy,
    loc_names.event_uw_boss_1: item_names.event_trophy,
    loc_names.event_uw_boss_2: item_names.event_trophy,
    loc_names.event_tow_boss: item_names.event_trophy,
    loc_names.event_cc_boss_1: item_names.event_trophy,
    loc_names.event_cc_boss_2: item_names.event_trophy,
    loc_names.event_dt_boss_1: item_names.event_trophy,
    loc_names.event_dt_boss_2: item_names.event_trophy,
    loc_names.event_dt_boss_3: item_names.event_trophy,
    loc_names.event_dt_boss_4: item_names.event_trophy,
    loc_names.event_roc_boss: item_names.event_trophy,
    loc_names.event_ck_boss_1: item_names.event_trophy,
    loc_names.event_ck_boss_2: item_names.event_trophy,
    loc_names.event_dracula: item_names.event_dracula,
}

# All 3HB datas mapped to said 3HBs' flag IDs in the vanilla game. This is to help detecting them while patching.
THREE_HIT_BREAKABLES_INFO = {
    0x4A: CVLoD3HBData(0x2B8, [loc_names.cw_save_slab1,  # CW upper rampart save nub
                               loc_names.cw_save_slab2,
                               loc_names.cw_save_slab3,
                               loc_names.cw_save_slab4,
                               loc_names.cw_save_slab5]),
    0x4B: CVLoD3HBData(0x2BD, [loc_names.cw_drac_slab1,  # CW Dracula switch slab
                               loc_names.cw_drac_slab2,
                               loc_names.cw_drac_slab3,
                               loc_names.cw_drac_slab4,
                               loc_names.cw_drac_slab5]),
    0x76: CVLoD3HBData(0x2C2, [loc_names.villafo_chandelier1,  # Villa foyer chandelier
                               loc_names.villafo_chandelier2,
                               loc_names.villafo_chandelier3,
                               loc_names.villafo_chandelier4,
                               loc_names.villafo_chandelier5]),
    0xD4: CVLoD3HBData(0x2C7, [loc_names.tunnel_arrows_rock1,  # Tunnel twin arrows rock
                               loc_names.tunnel_arrows_rock2,
                               loc_names.tunnel_arrows_rock3,
                               loc_names.tunnel_arrows_rock4,
                               loc_names.tunnel_arrows_rock5]),
    0xD5: CVLoD3HBData(0x2CC, [loc_names.tunnel_bucket_quag_rock1,  # Tunnel lonesome bucket pit rock
                               loc_names.tunnel_bucket_quag_rock2,
                               loc_names.tunnel_bucket_quag_rock3]),
    0xE4: CVLoD3HBData(0x2CF, [loc_names.uw_first_ledge1,  # UW poison parkour ledge
                               loc_names.uw_first_ledge2,
                               loc_names.uw_first_ledge3,
                               loc_names.uw_first_ledge4,
                               loc_names.uw_first_ledge5,
                               loc_names.uw_first_ledge6]),
    0xE5: CVLoD3HBData(0x2D5, [loc_names.uw_in_skel_ledge1,  # UW skeleton crusher ledge
                               loc_names.uw_in_skel_ledge2,
                               loc_names.uw_in_skel_ledge3]),
    0x103: CVLoD3HBData(0x2D8, [loc_names.ccb_behemoth_crate1,  # CC Behemoth crate
                                loc_names.ccb_behemoth_crate2,
                                loc_names.ccb_behemoth_crate3,
                                loc_names.ccb_behemoth_crate4,
                                loc_names.ccb_behemoth_crate5]),
    0x10D: CVLoD3HBData(0x2DD, [loc_names.ccbe_stand1,  # CC elevator pedestal
                                loc_names.ccbe_stand2,
                                loc_names.ccbe_stand3]),
    0x114: CVLoD3HBData(0x2E0, [loc_names.ccff_lizard_slab1,  # CC lizard locker slab
                                loc_names.ccff_lizard_slab2,
                                loc_names.ccff_lizard_slab3,
                                loc_names.ccff_lizard_slab4]),
    0x185: CVLoD3HBData(0x2E4, [loc_names.ctgc_gearclimb_battery_slab1,  # CT gear climb battery slab
                                loc_names.ctgc_gearclimb_battery_slab2,
                                loc_names.ctgc_gearclimb_battery_slab3,
                                loc_names.ctgc_gearclimb_battery_slab4,
                                loc_names.ctgc_gearclimb_battery_slab5,
                                loc_names.ctgc_gearclimb_battery_slab6]),
    0x184: CVLoD3HBData(0x2EA, [loc_names.ctgc_gearclimb_door_slab1,  # CT gear climb below door slab
                                loc_names.ctgc_gearclimb_door_slab2,
                                loc_names.ctgc_gearclimb_door_slab3]),
    0x257: CVLoD3HBData(0x2ED, [loc_names.ctga_far_slab1,  # CT grand abyss farside slab
                                loc_names.ctga_far_slab2,
                                loc_names.ctga_far_slab3,
                                loc_names.ctga_far_slab4]),
    0x262: CVLoD3HBData(0x2F1, [loc_names.ctf_slope_slab1,  # CT under slippery slope slab
                                loc_names.ctf_slope_slab2,
                                loc_names.ctf_slope_slab3]),
}

# All Locations inside 3HBs. These should NOT be created if Multi Hit Breakables are off. This includes the enemy
# pillars in Tower of Execution, which have their own handling during patching separate from the 3HBs.
THREE_HIT_BREAKABLE_LOCATIONS = [loc_names.toe_first_pillar,
                                 loc_names.toe_last_pillar] + [loc_name for three_hit_flag, three_hit_data in
                                                               THREE_HIT_BREAKABLES_INFO.items()
                                                               for loc_name in three_hit_data.location_names]

# All Locations that normally have their Items given by calling the "give item" function directly.
# These will instead be put on the rando's remote item giving functionality.
NPC_LOCATIONS = {loc_names.villafy_fountain_shine,
                 loc_names.villafo_6am_roses,
                 loc_names.villala_vincent,
                 loc_names.villala_mary,
                 loc_names.ccll_heinrich}

# All Locations inside breakables that are normally empty. These should NOT be created if Empty Breakables are off.
EMPTY_LOCATIONS = {
    loc_names.towf_start_entry_l,
    loc_names.towf_start_entry_r,
    loc_names.towf_start_elevator_l,
    loc_names.towf_start_elevator_r,
    loc_names.towse_key_entry_l,
    loc_names.towse_key_entry_r,
    loc_names.towse_locked_door_l,
    loc_names.towse_locked_door_r,
    loc_names.towf_retract_elevator_l,
    loc_names.towf_retract_elevator_r,
    loc_names.towh_boulders_elevator_l,
    loc_names.towh_boulders_elevator_r,
}

# All Locations that only Carrie is capable of reaching. These should NOT be created if Carrie Logic is off.
CARRIE_ONLY_LOCATIONS = {loc_names.uw_carrie1,
                         loc_names.uw_carrie2}

# All Locations inside the Castle Center lizard lockers. These should NOT be created if Lizard Locker Items are off.
LIZARD_LOCKER_LOCATIONS = {loc_names.ccff_lizard_locker_fl,
                           loc_names.ccff_lizard_locker_fr,
                           loc_names.ccff_lizard_locker_nfl,
                           loc_names.ccff_lizard_locker_nfr,
                           loc_names.ccff_lizard_locker_nml,
                           loc_names.ccff_lizard_locker_nmr}

# All Locations specific to Reinhardt and Carrie's version of Castle Wall. These should not be created if the Castle
# Wall State is Cornell's.
REIN_CARRIE_CW_LOCATIONS: list[str] = [
    loc_names.cw_ground_middle
]

# All Locations specific to Reinhardt and Carrie's version of the Villa. These should not be created if the Villa State
# is Cornell's.
REIN_CARRIE_VILLA_LOCATIONS: list[str] = [
    loc_names.event_villa_rosa,
    loc_names.villala_vincent,
    loc_names.villam_fplatform,
    loc_names.villam_rplatform_f,
    loc_names.villam_serv_path_sr,
    loc_names.event_villa_boss_4,
    loc_names.event_villa_boss_5
]

# All Locations specific to Cornell's version of the Villa. These should not be created if the Villa State is Reinhardt
# and Carrie's.
CORNELL_VILLA_LOCATIONS: list[str] = [
    loc_names.villafy_fountain_shine,
    loc_names.villafo_6am_roses,
    loc_names.event_villa_boss_2,
    loc_names.villala_slivingroom_table_l,
    loc_names.villala_mary,
    loc_names.event_villa_child,
    loc_names.villam_hole_de,
    loc_names.villam_rplatform_r,
    loc_names.villam_serv_path_sl,
    loc_names.event_villa_boss_3
]

# All freestanding Location IDs that can be problematic if a higher-spawning Item pickup is placed on them.
# If any of said Items land on one of these, they must be lowered by 3.2 units.
HIGHER_SPAWNING_PROBLEM_LOCATIONS: list[int] = [
    CVLOD_LOCATIONS_INFO[loc_names.torm_g3_statue].flag_id,
    CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_shelf_h].flag_id,
    CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_shelf_i].flag_id
]

# New XYZ scene coordinates for some select invisible-turned-visible Locations in order to make them less "inside"
# objects and more visible. None = leave that coordinate vanilla.
NEW_VISIBLE_ITEM_COORDS: {int: (float | None, float | None, float | None)} = {
    CVLOD_LOCATIONS_INFO[loc_names.flp_statue_l].flag_id: (None, None, -15.5),
    CVLOD_LOCATIONS_INFO[loc_names.flp_statue_r].flag_id: (None, None, 15.5),
    CVLOD_LOCATIONS_INFO[loc_names.villala_storeroom_s].flag_id: (None, None, -263.0),
    CVLOD_LOCATIONS_INFO[loc_names.villala_llivingroom_lion].flag_id: (-416.0, None, -263.0),
    CVLOD_LOCATIONS_INFO[loc_names.villala_llivingroom_painting].flag_id: (-255.0, None, -317.0),
    CVLOD_LOCATIONS_INFO[loc_names.villala_exit_knight].flag_id: (-155.0, None, -249.0),
    CVLOD_LOCATIONS_INFO[loc_names.tunnel_lonesome_bucket].flag_id: (None, 267.0, None),
    CVLOD_LOCATIONS_INFO[loc_names.torm_b6].flag_id: (-238.5, None, None),
    CVLOD_LOCATIONS_INFO[loc_names.torm_b4_statue].flag_id: (None, None, 361.0),
    CVLOD_LOCATIONS_INFO[loc_names.torm_g3_statue].flag_id: (None, None, 239.5),
    CVLOD_LOCATIONS_INFO[loc_names.ccb_torture_rack].flag_id: (-12.5, None, None),
    CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_crates].flag_id: (-287.0, None, None),
    CVLOD_LOCATIONS_INFO[loc_names.ccia_inventions_famicart].flag_id: (None, None, 257.0),
    CVLOD_LOCATIONS_INFO[loc_names.ccia_inventions_round].flag_id: (-100.25, None, None),
    CVLOD_LOCATIONS_INFO[loc_names.toscit_ctrl_interface_f].flag_id: (234.0, None, None),
    CVLOD_LOCATIONS_INFO[loc_names.toscit_ctrl_interface_rl].flag_id: (438.5, None, -448.5),
    CVLOD_LOCATIONS_INFO[loc_names.toscit_ctrl_interface_rr].flag_id: (438.5, None, -211.5),
}

def get_location_names_to_ids() -> dict[str, int]:
    return {name: CVLOD_LOCATIONS_INFO[name].flag_id for name in CVLOD_LOCATIONS_INFO}


def get_location_name_groups() -> dict[str, set[str]]:
    loc_name_groups: dict[str, set[str]] = dict()

    for loc_name in CVLOD_LOCATIONS_INFO:
        # If we are looking at an event Location, don't include it.
        if isinstance(CVLOD_LOCATIONS_INFO[loc_name].flag_id, str):
            continue

        # The part of the Location name's string before the colon is its area name.
        area_name = loc_name.split(":")[0]

        # Add each Location to its corresponding area name group.
        if area_name not in loc_name_groups:
            loc_name_groups[area_name] = {loc_name}
        else:
            loc_name_groups[area_name].add(loc_name)

    return loc_name_groups


def get_locations_to_create(locations: list[str], options: CVLoDOptions) -> \
        tuple[dict[str, int | None], dict[str, str]]:
    """Verifies which Locations in a given list should be created. A dict will be returned with verified Location names
    mapped to their IDs, ready to be created with Region.add_locations, as well as a dict of Locations that should have
    corresponding locked Items placed on them."""
    locations_with_ids = {}
    locked_pairs = {}

    for loc in locations:
        # Don't place the Location if it's a Reinhardt/Carrie Castle Wall Location and the Castle Wall State is
        # Cornell's.
        if loc in REIN_CARRIE_CW_LOCATIONS and options.castle_wall_state == CastleWallState.option_cornell:
            continue

        # Don't place the Location if it's a Reinhardt/Carrie Villa Location and the Villa State is Cornell's, or if
        # it's a Cornell Villa Location and the Villa State is Reinhardt/Carrie's.
        if (loc in REIN_CARRIE_VILLA_LOCATIONS and options.villa_state == VillaState.option_cornell) or \
                (loc in CORNELL_VILLA_LOCATIONS and options.villa_state == VillaState.option_reinhardt_carrie):
            continue

        # If the Location is a Carrie-only Location, and Carrie Logic is not enabled, don't add it.
        if loc in CARRIE_ONLY_LOCATIONS and not options.carrie_logic:
            continue

        # If the Location is a Lizard Locker Location, and the Lizard Lockers are not enabled, don't add it.
        if loc in LIZARD_LOCKER_LOCATIONS and not options.lizard_locker_items:
            continue

        # If the Location is an Empty Breakable Location, and the Empty Breakables are not enabled, don't add it.
        if loc in EMPTY_LOCATIONS and not options.empty_breakables:
            continue

        # If the Location is a 3HB Location, and 3HBs are not enabled, don't add it.
        if loc in THREE_HIT_BREAKABLE_LOCATIONS and not options.multi_hit_breakables:
            continue

        # Check to see if the Location is in the Locations Info dict.
        # If it is, then handle it like a regular check Location.
        if loc in CVLOD_LOCATIONS_INFO:
            # If the Location's normal Item is a sub-weapon, and sub-weapons are not set to shuffle anywhere, don't
            # add it.
            if CVLOD_LOCATIONS_INFO[loc].normal_item in [item_names.sub_knife, item_names.sub_holy,
                                                         item_names.sub_axe, item_names.sub_cross] \
                    and options.sub_weapon_shuffle != SubWeaponShuffle.option_anywhere:
                continue

            # Grab its ID from the Locations Info.
            loc_id = CVLOD_LOCATIONS_INFO[loc].flag_id
        # Check to see if the Location is in the Events Mapping dict.
        # If it is, then handle it like an event Location.
        elif loc in CVLOD_EVENT_MAPPING:
            # Don't place the Boss Trophy Locations if Dracula's Condition is not Bosses.
            if CVLOD_EVENT_MAPPING[loc] == item_names.event_trophy and \
                    options.draculas_condition != DraculasCondition.option_bosses:
                continue

            # Don't place the Vincent or Renon fight Locations if said fights are completely disabled.
            if (loc == loc_names.event_ck_boss_2 and
                    options.vincent_fight_condition == VincentFightCondition.option_never) or \
                    (loc == loc_names.event_ck_boss_1 and
                     options.renon_fight_condition == RenonFightCondition.option_never):
                continue

            # Set its ID to None and lock its associated event Item on it.
            loc_id = None
            locked_pairs[loc] = CVLOD_EVENT_MAPPING[loc]
        else:
            # If we end up here, meaning the Location is undefined in both dicts, throw an error indicating such and
            # skip creating it.
            logging.error(f"The Location \"{loc}\" is not in either CVLOD_LOCATIONS_INFO or "
                          f"CVLOD_EVENT_MAPPING. Please add it to one or the other to create it properly.")
            continue

        # Update the dict containing our Locations to create for the Region.
        locations_with_ids.update({loc: loc_id})

    return locations_with_ids, locked_pairs
