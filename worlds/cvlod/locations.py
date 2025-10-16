import logging

from BaseClasses import Location
from .data import loc_names, item_names
from .data.enums import Scenes
from .options import CVLoDOptions, SubWeaponShuffle, DraculasCondition, RenonFightCondition, VincentFightCondition, \
    VillaState

from typing import NamedTuple


class CVLoDLocation(Location):
    game: str = "Castlevania - Legacy of Darkness"


class CVLoDLocationData(NamedTuple):
    flag_id: int # The Location object's unique code attribute, as well as the in-game pickup flag index. starting from
              # 0x801CAA60 that indicates the Location has been checked.
    scene_id: int # Which scene in the game the Location is associated to. Used in determining what actor to alter the
                  # properties of as well as what Countdown number it contributes to.
    normal_item: str # What Item to add to the AP itempool if that Location is added with the Normal item pool enabled.
                     # Usually but not always, this is the Item that's normally there in the vanilla game on Normal.
    easy_item: str = ""  # What Item to add to the AP itempool if that Location is added with the Easy item pool
                         # enabled. Usually but not always, this is the Item that's normally there in the vanilla game
                         # on Easy. If None, the Normal item will be defaulted to.
    hard_item: str = ""  # What Item to add to the AP itempool if that Location is added with the Hard item pool
                         # enabled. Usually but not always, this is the Item that's normally there in the vanilla game
                         # on Hard. If None, the Normal item will be defaulted to.
    type: str = ""  # Anything special about this Location, whether it be invisible, a 3HB drop, etc.
    actor: tuple[str, int] | None = None  # Which actor in which actor list in the Location's scene is associated to the
                                          # Location. Formatted (list_name, list_index).


CVLOD_LOCATIONS_INFO = {
    # Foggy Lake
    loc_names.fld_forecast_port:            CVLoDLocationData(0x150, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.gold_500, actor=("proxy", 129)),
    loc_names.fld_forecast_starboard:       CVLoDLocationData(0x14F, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rl, actor=("proxy", 128)),
    loc_names.fld_foremast_lower:           CVLoDLocationData(0x152, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rl, actor=("proxy", 131)),
    loc_names.fld_stairs_port:              CVLoDLocationData(0x146, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 87)),
    loc_names.fld_stairs_starboard:         CVLoDLocationData(0x148, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 85)),
    loc_names.fld_net_port:                 CVLoDLocationData(0x14C, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 81)),
    loc_names.fld_net_starboard:            CVLoDLocationData(0x147, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 86)),
    loc_names.fld_mainmast_base:            CVLoDLocationData(0x142, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.sub_knife, actor=("proxy", 91)),
    loc_names.fld_near_door:                CVLoDLocationData(0x149, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 84)),
    loc_names.fld_near_block_l:             CVLoDLocationData(0x14B, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.gold_100, actor=("proxy", 82)),
    loc_names.fld_near_block_r:             CVLoDLocationData(0x14A, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rl, actor=("proxy", 83)),
    loc_names.fld_above_door:               CVLoDLocationData(0x143, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rl, actor=("proxy", 90)),
    loc_names.fld_stern_port:               CVLoDLocationData(0x145, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 88)),
    loc_names.fld_stern_starboard:          CVLoDLocationData(0x144, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rs, actor=("proxy", 89)),
    loc_names.fld_poop_port_crates:         CVLoDLocationData(0x140, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.powerup, actor=("proxy", 93)),
    loc_names.fld_poop_starboard_crates:    CVLoDLocationData(0x141, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.jewel_rl, actor=("proxy", 92)),
    loc_names.fld_mainmast_top:             CVLoDLocationData(0x151, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.use_chicken, actor=("proxy", 130)),
    loc_names.fld_jiggermast:               CVLoDLocationData(0x27C, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.quest_key_deck, actor=("proxy", 125)),
    loc_names.fld_foremast_upper_port:      CVLoDLocationData(0x14D, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.use_beef, actor=("proxy", 126)),
    loc_names.fld_foremast_upper_starboard: CVLoDLocationData(0x14E, Scenes.FOGGY_LAKE_ABOVE_DECKS, item_names.sub_axe, actor=("proxy", 127)),
    loc_names.flb_hallway_l:                CVLoDLocationData(0x15A, Scenes.FOGGY_LAKE_BELOW_DECKS, item_names.gold_300, actor=("room 1", 13)),
    loc_names.flb_hallway_r:                CVLoDLocationData(0x15B, Scenes.FOGGY_LAKE_BELOW_DECKS, item_names.jewel_rs, actor=("room 1", 12)),
    loc_names.flb_tall_crates:              CVLoDLocationData(0x155, Scenes.FOGGY_LAKE_BELOW_DECKS, item_names.sub_knife, actor=("room 0", 14)),
    loc_names.flb_short_crates_l:           CVLoDLocationData(0x156, Scenes.FOGGY_LAKE_BELOW_DECKS, item_names.jewel_rl, actor=("room 0", 13)),
    loc_names.flb_short_crates_r:           CVLoDLocationData(0x157, Scenes.FOGGY_LAKE_BELOW_DECKS, item_names.gold_500, actor=("room 0", 12)),
    loc_names.flp_pier_l:                   CVLoDLocationData(0x162, Scenes.FOGGY_LAKE_PIER, item_names.use_chicken, actor=("proxy", 82)),
    loc_names.flp_pier_m:                   CVLoDLocationData(0x163, Scenes.FOGGY_LAKE_PIER, item_names.sub_axe, actor=("proxy", 84)),
    loc_names.flp_pier_r:                   CVLoDLocationData(0x164, Scenes.FOGGY_LAKE_PIER, item_names.jewel_rl, actor=("proxy", 85)),
    loc_names.flp_statue_l:                 CVLoDLocationData(0x161, Scenes.FOGGY_LAKE_PIER, item_names.use_beef, actor=("proxy", 77)),
    loc_names.flp_statue_r:                 CVLoDLocationData(0x160, Scenes.FOGGY_LAKE_PIER, item_names.use_chicken, actor=("proxy", 80)),

    # Forest of Silence
    loc_names.forest_pier_center:  CVLoDLocationData(0x16, Scenes.FOREST_OF_SILENCE, item_names.jewel_rs, actor=("proxy", 134)),
    loc_names.forest_pier_end:     CVLoDLocationData(0x17, Scenes.FOREST_OF_SILENCE, item_names.gold_300, actor=("proxy", 135)),
    loc_names.forest_sypha_ne:     CVLoDLocationData(0x19, Scenes.FOREST_OF_SILENCE, item_names.use_ampoule, actor=("proxy", 137)),
    loc_names.forest_sypha_se:     CVLoDLocationData(0x18, Scenes.FOREST_OF_SILENCE, item_names.jewel_rl, actor=("proxy", 136)),
    loc_names.forest_sypha_nw:     CVLoDLocationData(0x1A, Scenes.FOREST_OF_SILENCE, item_names.gold_500, actor=("proxy", 138)),
    loc_names.forest_sypha_sw:     CVLoDLocationData(0x1B, Scenes.FOREST_OF_SILENCE, item_names.use_purifying, actor=("proxy", 139)),
    loc_names.forest_flea_trail:   CVLoDLocationData(0x1C, Scenes.FOREST_OF_SILENCE, item_names.sub_axe, actor=("proxy", 140)),
    loc_names.forest_leap:         CVLoDLocationData(0x1E, Scenes.FOREST_OF_SILENCE, item_names.gold_500, actor=("proxy", 142)),
    loc_names.forest_descent:      CVLoDLocationData(0x1D, Scenes.FOREST_OF_SILENCE, item_names.powerup, actor=("proxy", 141)),
    loc_names.forest_passage:      CVLoDLocationData(0x21, Scenes.FOREST_OF_SILENCE, item_names.use_beef, actor=("proxy", 145)),
    loc_names.forest_child_ledge:  CVLoDLocationData(0x22, Scenes.FOREST_OF_SILENCE, item_names.gold_100, actor=("proxy", 122)),
    loc_names.forest_charnel_1:    CVLoDLocationData(0x11, Scenes.FOREST_OF_SILENCE, item_names.use_card_m),
    loc_names.forest_charnel_2:    CVLoDLocationData(0x12, Scenes.FOREST_OF_SILENCE, item_names.use_card_s),
    loc_names.forest_charnel_3:    CVLoDLocationData(0x13, Scenes.FOREST_OF_SILENCE, item_names.gold_500),
    loc_names.forest_werewolf_pit: CVLoDLocationData(0x20, Scenes.FOREST_OF_SILENCE, item_names.sub_knife, actor=("proxy", 144)),
    loc_names.forest_pike:         CVLoDLocationData(0x27, Scenes.FOREST_OF_SILENCE, item_names.use_chicken, actor=("proxy", 133)),
    loc_names.forest_end_gate:     CVLoDLocationData(0x1F, Scenes.FOREST_OF_SILENCE, item_names.gold_500, actor=("proxy", 143)),
    loc_names.forest_skelly_mouth: CVLoDLocationData(0x23, Scenes.FOREST_OF_SILENCE, item_names.use_chicken, actor=("proxy", 171)),

    # Castle Wall
    loc_names.cwr_bottom:        CVLoDLocationData(0x2D, Scenes.CASTLE_WALL_TOWERS, item_names.use_card_s),
    loc_names.cwr_top:           CVLoDLocationData(0x30, Scenes.CASTLE_WALL_TOWERS, item_names.use_chicken),
    loc_names.cw_dragon_sw:      CVLoDLocationData(0x49, Scenes.CASTLE_WALL_MAIN, item_names.use_chicken),
    loc_names.cw_save_slab1:     CVLoDLocationData(0x2B8, Scenes.CASTLE_WALL_MAIN, item_names.jewel_rl, type="3hb"),
    loc_names.cw_save_slab2:     CVLoDLocationData(0x2B9, Scenes.CASTLE_WALL_MAIN, item_names.jewel_rl, type="3hb"),
    loc_names.cw_save_slab3:     CVLoDLocationData(0x2BA, Scenes.CASTLE_WALL_MAIN, item_names.jewel_rl, type="3hb"),
    loc_names.cw_save_slab4:     CVLoDLocationData(0x2BB, Scenes.CASTLE_WALL_MAIN, item_names.jewel_rl, type="3hb"),
    loc_names.cw_save_slab5:     CVLoDLocationData(0x2BC, Scenes.CASTLE_WALL_MAIN, item_names.jewel_rl, type="3hb"),
    loc_names.cw_rrampart:       CVLoDLocationData(0x46, Scenes.CASTLE_WALL_MAIN, item_names.gold_300),
    loc_names.cw_lrampart:       CVLoDLocationData(0x47, Scenes.CASTLE_WALL_MAIN, item_names.use_card_m),
    loc_names.cw_pillar:         CVLoDLocationData(0x44, Scenes.CASTLE_WALL_MAIN, item_names.powerup),
    loc_names.cw_shelf:          CVLoDLocationData(0x42, Scenes.CASTLE_WALL_MAIN, item_names.quest_winch),
    loc_names.cw_shelf_torch:    CVLoDLocationData(0x4C, Scenes.CASTLE_WALL_MAIN, item_names.sub_cross),
    loc_names.cw_ground_left:    CVLoDLocationData(0x48, Scenes.CASTLE_WALL_MAIN, item_names.use_purifying),
    loc_names.cw_ground_middle:  CVLoDLocationData(0x27D, Scenes.CASTLE_WALL_MAIN, item_names.quest_key_left),
    loc_names.cw_ground_right:   CVLoDLocationData(0x4D, Scenes.CASTLE_WALL_MAIN, item_names.sub_axe),
    loc_names.cwl_bottom:        CVLoDLocationData(0x2E, Scenes.CASTLE_WALL_TOWERS, item_names.use_card_m),
    loc_names.cwl_bridge:        CVLoDLocationData(0x2F, Scenes.CASTLE_WALL_TOWERS, item_names.use_beef),
    loc_names.cw_drac_sw:        CVLoDLocationData(0x4E, Scenes.CASTLE_WALL_MAIN, item_names.use_chicken),
    loc_names.cw_drac_slab1:     CVLoDLocationData(0x2BD, Scenes.CASTLE_WALL_MAIN, item_names.gold_300, type="3hb"),
    loc_names.cw_drac_slab2:     CVLoDLocationData(0x2BE, Scenes.CASTLE_WALL_MAIN, item_names.gold_300, type="3hb"),
    loc_names.cw_drac_slab3:     CVLoDLocationData(0x2BF, Scenes.CASTLE_WALL_MAIN, item_names.gold_300, type="3hb"),
    loc_names.cw_drac_slab4:     CVLoDLocationData(0x2C0, Scenes.CASTLE_WALL_MAIN, item_names.gold_300, type="3hb"),
    loc_names.cw_drac_slab5:     CVLoDLocationData(0x2C1, Scenes.CASTLE_WALL_MAIN, item_names.gold_300, type="3hb"),

    # Villa
    loc_names.villafy_outer_gate_l:         CVLoDLocationData(0x62, Scenes.VILLA_FRONT_YARD, item_names.use_purifying),
    loc_names.villafy_outer_gate_r:         CVLoDLocationData(0x63, Scenes.VILLA_FRONT_YARD, item_names.jewel_rl),
    loc_names.villafy_inner_gate:           CVLoDLocationData(0x60, Scenes.VILLA_FRONT_YARD, item_names.use_beef),
    loc_names.villafy_gate_marker:          CVLoDLocationData(0x65, Scenes.VILLA_FRONT_YARD, item_names.powerup),
    loc_names.villafy_villa_marker:         CVLoDLocationData(0x64, Scenes.VILLA_FRONT_YARD, item_names.use_beef),
    loc_names.villafy_fountain_fl:          CVLoDLocationData(0x5F, Scenes.VILLA_FRONT_YARD, item_names.gold_500),
    loc_names.villafy_fountain_fr:          CVLoDLocationData(0x61, Scenes.VILLA_FRONT_YARD, item_names.use_purifying),
    loc_names.villafy_fountain_ml:          CVLoDLocationData(0x5E, Scenes.VILLA_FRONT_YARD, item_names.use_card_s),
    loc_names.villafy_fountain_mr:          CVLoDLocationData(0x5A, Scenes.VILLA_FRONT_YARD, item_names.use_card_m),
    loc_names.villafy_fountain_rl:          CVLoDLocationData(0x5C, Scenes.VILLA_FRONT_YARD, item_names.use_beef),
    loc_names.villafy_fountain_rr:          CVLoDLocationData(0x5B, Scenes.VILLA_FRONT_YARD, item_names.gold_500),
    loc_names.villafy_fountain_shine:       CVLoDLocationData(0x68, Scenes.VILLA_FRONT_YARD, item_names.quest_crest_a),
    loc_names.villafo_front_l:              CVLoDLocationData(0x72, Scenes.VILLA_FOYER, item_names.jewel_rs),
    loc_names.villafo_front_r:              CVLoDLocationData(0x73, Scenes.VILLA_FOYER, item_names.gold_300),
    loc_names.villafo_mid_l:                CVLoDLocationData(0x71, Scenes.VILLA_FOYER, item_names.gold_300),
    loc_names.villafo_mid_r:                CVLoDLocationData(0x70, Scenes.VILLA_FOYER, item_names.jewel_rs),
    loc_names.villafo_rear_l:               CVLoDLocationData(0x6E, Scenes.VILLA_FOYER, item_names.jewel_rs),
    loc_names.villafo_rear_r:               CVLoDLocationData(0x6F, Scenes.VILLA_FOYER, item_names.jewel_rs),
    loc_names.villafo_pot_l:                CVLoDLocationData(0x6D, Scenes.VILLA_FOYER, item_names.quest_key_arch),
    loc_names.villafo_pot_r:                CVLoDLocationData(0x6C, Scenes.VILLA_FOYER, item_names.jewel_rl),
    loc_names.villafo_sofa:                 CVLoDLocationData(0x75, Scenes.VILLA_FOYER, item_names.use_purifying),
    loc_names.villafo_chandelier1:          CVLoDLocationData(0x302, Scenes.VILLA_FOYER, item_names.gold_500, type="3hb"),
    loc_names.villafo_chandelier2:          CVLoDLocationData(0x303, Scenes.VILLA_FOYER, item_names.jewel_rl, type="3hb"),
    loc_names.villafo_chandelier3:          CVLoDLocationData(0x304, Scenes.VILLA_FOYER, item_names.use_purifying, type="3hb"),
    loc_names.villafo_chandelier4:          CVLoDLocationData(0x305, Scenes.VILLA_FOYER, item_names.use_ampoule, type="3hb"),
    loc_names.villafo_chandelier5:          CVLoDLocationData(0x306, Scenes.VILLA_FOYER, item_names.use_chicken, type="3hb"),
    loc_names.villafo_6am_roses:            CVLoDLocationData(0x78, Scenes.VILLA_FOYER, item_names.quest_key_thorn),
    loc_names.villala_hallway_stairs:       CVLoDLocationData(0x80, Scenes.VILLA_LIVING_AREA, item_names.jewel_rl),
    loc_names.villala_hallway_l:            CVLoDLocationData(0x82, Scenes.VILLA_LIVING_AREA, item_names.sub_knife),
    loc_names.villala_hallway_r:            CVLoDLocationData(0x81, Scenes.VILLA_LIVING_AREA, item_names.sub_axe),
    loc_names.villala_vincent:              CVLoDLocationData(0x27F, Scenes.VILLA_LIVING_AREA, item_names.jewel_rl),
    loc_names.villala_slivingroom_table_l:  CVLoDLocationData(0x283, Scenes.VILLA_LIVING_AREA, item_names.gold_100),
    loc_names.villala_slivingroom_table_r:  CVLoDLocationData(0x88, Scenes.VILLA_LIVING_AREA, item_names.gold_300),
    loc_names.villala_mary:                 CVLoDLocationData(0x86, Scenes.VILLA_LIVING_AREA, item_names.gold_100),
    loc_names.villala_slivingroom_mirror:   CVLoDLocationData(0x83, Scenes.VILLA_LIVING_AREA, item_names.sub_cross),
    loc_names.villala_diningroom_roses:     CVLoDLocationData(0x90, Scenes.VILLA_LIVING_AREA, item_names.use_purifying),
    loc_names.villala_llivingroom_pot_r:    CVLoDLocationData(0x27E, Scenes.VILLA_LIVING_AREA, item_names.quest_key_store),
    loc_names.villala_llivingroom_pot_l:    CVLoDLocationData(0x7E, Scenes.VILLA_LIVING_AREA, item_names.use_chicken),
    loc_names.villala_llivingroom_painting: CVLoDLocationData(0x8E, Scenes.VILLA_LIVING_AREA, item_names.use_purifying),
    loc_names.villala_llivingroom_light:    CVLoDLocationData(0x7F, Scenes.VILLA_LIVING_AREA, item_names.use_purifying),
    loc_names.villala_llivingroom_lion:     CVLoDLocationData(0x8D, Scenes.VILLA_LIVING_AREA, item_names.use_chicken),
    loc_names.villala_exit_knight:          CVLoDLocationData(0x8F, Scenes.VILLA_LIVING_AREA, item_names.use_purifying),
    loc_names.villala_storeroom_l:          CVLoDLocationData(0x2B3, Scenes.VILLA_LIVING_AREA, item_names.use_beef),
    loc_names.villala_storeroom_r:          CVLoDLocationData(0x2B2, Scenes.VILLA_LIVING_AREA, item_names.use_chicken),
    loc_names.villala_storeroom_s:          CVLoDLocationData(0x8C, Scenes.VILLA_LIVING_AREA, item_names.use_purifying),
    loc_names.villala_archives_table:       CVLoDLocationData(0x84, Scenes.VILLA_LIVING_AREA, item_names.quest_diary),
    loc_names.villala_archives_rear:        CVLoDLocationData(0x85, Scenes.VILLA_LIVING_AREA, item_names.quest_key_grdn),
    loc_names.villam_malus_torch:           CVLoDLocationData(0xA3, Scenes.VILLA_MAZE, item_names.jewel_rs),
    loc_names.villam_malus_bush:            CVLoDLocationData(0xAA, Scenes.VILLA_MAZE, item_names.use_chicken),
    loc_names.villam_fplatform:             CVLoDLocationData(0xA7, Scenes.VILLA_MAZE, item_names.sub_axe),
    loc_names.villam_frankieturf_l:         CVLoDLocationData(0x9F, Scenes.VILLA_MAZE, item_names.gold_300),
    loc_names.villam_frankieturf_r:         CVLoDLocationData(0xA8, Scenes.VILLA_MAZE, item_names.sub_holy),
    loc_names.villam_frankieturf_ru:        CVLoDLocationData(0xAC, Scenes.VILLA_MAZE, item_names.jewel_rs),
    loc_names.villam_hole_de:               CVLoDLocationData(0x281, Scenes.VILLA_MAZE, item_names.quest_key_rose),
    loc_names.villam_fgarden_f:             CVLoDLocationData(0xA5, Scenes.VILLA_MAZE, item_names.jewel_rs),
    loc_names.villam_fgarden_mf:            CVLoDLocationData(0xA2, Scenes.VILLA_MAZE, item_names.jewel_rs),
    loc_names.villam_fgarden_mr:            CVLoDLocationData(0xA4, Scenes.VILLA_MAZE, item_names.quest_brooch),
    loc_names.villam_fgarden_r:             CVLoDLocationData(0xA6, Scenes.VILLA_MAZE, item_names.jewel_rl),
    loc_names.villam_child_de:              CVLoDLocationData(0x87, Scenes.VILLA_MAZE, item_names.gold_100),
    loc_names.villam_rplatform_f:           CVLoDLocationData(0xA9, Scenes.VILLA_MAZE, item_names.sub_axe),
    loc_names.villam_rplatform_r:           CVLoDLocationData(0x9C, Scenes.VILLA_MAZE, item_names.quest_crest_b),
    loc_names.villam_rplatform_de:          CVLoDLocationData(0xA0, Scenes.VILLA_MAZE, item_names.gold_300),
    loc_names.villam_exit_de:               CVLoDLocationData(0xA1, Scenes.VILLA_MAZE, item_names.gold_300),
    loc_names.villam_serv_path_sl:          CVLoDLocationData(0xAB, Scenes.VILLA_MAZE, item_names.use_purifying),
    loc_names.villam_serv_path_sr:          CVLoDLocationData(0x280, Scenes.VILLA_MAZE, item_names.quest_key_cppr),
    loc_names.villam_serv_path_l:           CVLoDLocationData(0x2B1, Scenes.VILLA_MAZE, item_names.use_ampoule),
    loc_names.villafo_serv_ent:             CVLoDLocationData(0x74, Scenes.VILLA_FOYER, item_names.use_chicken),
    loc_names.villam_crypt_ent:             CVLoDLocationData(0x9E, Scenes.VILLA_MAZE, item_names.use_purifying),
    loc_names.villam_crypt_upstream:        CVLoDLocationData(0x9D, Scenes.VILLA_MAZE, item_names.use_beef),
    loc_names.villac_ent_l:                 CVLoDLocationData(0x192, Scenes.VILLA_CRYPT, item_names.jewel_rs),
    loc_names.villac_ent_r:                 CVLoDLocationData(0x193, Scenes.VILLA_CRYPT, item_names.gold_300),
    loc_names.villac_wall_l:                CVLoDLocationData(0x196, Scenes.VILLA_CRYPT, item_names.sub_cross),
    loc_names.villac_wall_r:                CVLoDLocationData(0x197, Scenes.VILLA_CRYPT, item_names.jewel_rl),
    loc_names.villac_coffin_l:              CVLoDLocationData(0x194, Scenes.VILLA_CRYPT, item_names.jewel_rs),
    loc_names.villac_coffin_r:              CVLoDLocationData(0x195, Scenes.VILLA_CRYPT, item_names.jewel_rs),

    # Tunnel
    loc_names.tunnel_landing:               CVLoDLocationData(0xB6, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 146)),
    loc_names.tunnel_landing_rc:            CVLoDLocationData(0xB7, Scenes.TUNNEL, item_names.jewel_rs, actor=("proxy", 182)),
    loc_names.tunnel_stone_alcove_r:        CVLoDLocationData(0xCC, Scenes.TUNNEL, item_names.sub_holy, actor=("proxy", 168)),
    loc_names.tunnel_stone_alcove_l:        CVLoDLocationData(0xC5, Scenes.TUNNEL, item_names.use_beef, actor=("proxy", 179)),
    loc_names.tunnel_twin_arrows:           CVLoDLocationData(0xD3, Scenes.TUNNEL, item_names.use_ampoule, actor=("proxy", 209)),
    loc_names.tunnel_arrows_rock1:          CVLoDLocationData(0x307, Scenes.TUNNEL, item_names.use_purifying, type="3hb"),
    loc_names.tunnel_arrows_rock2:          CVLoDLocationData(0x308, Scenes.TUNNEL, item_names.use_purifying, type="3hb"),
    loc_names.tunnel_arrows_rock3:          CVLoDLocationData(0x309, Scenes.TUNNEL, item_names.use_ampoule, type="3hb"),
    loc_names.tunnel_arrows_rock4:          CVLoDLocationData(0x30A, Scenes.TUNNEL, item_names.use_ampoule, type="3hb"),
    loc_names.tunnel_arrows_rock5:          CVLoDLocationData(0x30B, Scenes.TUNNEL, item_names.use_chicken, type="3hb"),
    loc_names.tunnel_lonesome_bucket:       CVLoDLocationData(0xD6, Scenes.TUNNEL, item_names.use_ampoule, actor=("proxy", 211)),
    loc_names.tunnel_lbucket_mdoor_l:       CVLoDLocationData(0xCE, Scenes.TUNNEL, item_names.sub_knife, actor=("proxy", 170)),
    loc_names.tunnel_lbucket_quag:          CVLoDLocationData(0xBB, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 151)),
    loc_names.tunnel_bucket_quag_rock1:     CVLoDLocationData(0x30C, Scenes.TUNNEL, item_names.use_chicken, type="3hb"),
    loc_names.tunnel_bucket_quag_rock2:     CVLoDLocationData(0x30D, Scenes.TUNNEL, item_names.use_chicken, type="3hb"),
    loc_names.tunnel_bucket_quag_rock3:     CVLoDLocationData(0x30E, Scenes.TUNNEL, item_names.use_chicken, type="3hb"),
    loc_names.tunnel_lbucket_albert:        CVLoDLocationData(0xBC, Scenes.TUNNEL, item_names.jewel_rs, actor=("proxy", 184)),
    loc_names.tunnel_albert_camp:           CVLoDLocationData(0xBA, Scenes.TUNNEL, item_names.jewel_rs, actor=("proxy", 186)),
    loc_names.tunnel_albert_quag:           CVLoDLocationData(0xB9, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 149)),
    loc_names.tunnel_gondola_rc_sdoor_l:    CVLoDLocationData(0xCD, Scenes.TUNNEL, item_names.use_beef, actor=("proxy", 169)),
    loc_names.tunnel_gondola_rc_sdoor_m:    CVLoDLocationData(0xBE, Scenes.TUNNEL, item_names.use_beef, actor=("proxy", 154)),
    loc_names.tunnel_gondola_rc_sdoor_r:    CVLoDLocationData(0xBD, Scenes.TUNNEL, item_names.sub_cross, actor=("proxy", 153)),
    loc_names.tunnel_gondola_rc:            CVLoDLocationData(0xBF, Scenes.TUNNEL, item_names.powerup, actor=("proxy", 155)),
    loc_names.tunnel_rgondola_station:      CVLoDLocationData(0xB8, Scenes.TUNNEL, item_names.jewel_rs, actor=("proxy", 192)),
    loc_names.tunnel_gondola_transfer:      CVLoDLocationData(0xC7, Scenes.TUNNEL, item_names.gold_500, actor=("proxy", 163)),
    loc_names.tunnel_corpse_bucket_quag:    CVLoDLocationData(0xC0, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 156)),
    loc_names.tunnel_corpse_bucket_mdoor_l: CVLoDLocationData(0xCF, Scenes.TUNNEL, item_names.sub_holy, actor=("proxy", 194)),
    loc_names.tunnel_corpse_bucket_mdoor_r: CVLoDLocationData(0xC8, Scenes.TUNNEL, item_names.use_card_s, actor=("proxy", 164)),
    loc_names.tunnel_shovel_quag_start:     CVLoDLocationData(0xC1, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 157)),
    loc_names.tunnel_exit_quag_start:       CVLoDLocationData(0xC2, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 158)),
    loc_names.tunnel_shovel_quag_end:       CVLoDLocationData(0xC3, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 159)),
    loc_names.tunnel_exit_quag_end:         CVLoDLocationData(0xC9, Scenes.TUNNEL, item_names.gold_300, actor=("proxy", 199)),
    loc_names.tunnel_shovel:                CVLoDLocationData(0xD2, Scenes.TUNNEL, item_names.use_beef, actor=("proxy", 213)),
    loc_names.tunnel_shovel_save:           CVLoDLocationData(0xC4, Scenes.TUNNEL, item_names.jewel_rl, actor=("proxy", 160)),
    loc_names.tunnel_shovel_mdoor_c:        CVLoDLocationData(0x24, Scenes.TUNNEL, item_names.gold_100, actor=("proxy", 131)),
    loc_names.tunnel_shovel_mdoor_l:        CVLoDLocationData(0xCA, Scenes.TUNNEL, item_names.use_card_s, actor=("proxy", 166)),
    loc_names.tunnel_shovel_mdoor_r:        CVLoDLocationData(0xD0, Scenes.TUNNEL, item_names.sub_axe, actor=("proxy", 172)),
    loc_names.tunnel_shovel_sdoor_l:        CVLoDLocationData(0xCB, Scenes.TUNNEL, item_names.use_card_m, actor=("proxy", 167)),
    loc_names.tunnel_shovel_sdoor_m:        CVLoDLocationData(0xC6, Scenes.TUNNEL, item_names.use_chicken, actor=("proxy", 162)),
    loc_names.tunnel_shovel_sdoor_r:        CVLoDLocationData(0xD1, Scenes.TUNNEL, item_names.sub_cross, actor=("proxy", 173)),

    # Underground Waterway
    loc_names.uw_near_ent:         CVLoDLocationData(0xDC, Scenes.WATERWAY, item_names.gold_300, actor=("proxy", 92)),
    loc_names.uw_across_ent:       CVLoDLocationData(0xDD, Scenes.WATERWAY, item_names.gold_300, actor=("proxy", 94)),
    loc_names.uw_first_ledge1:     CVLoDLocationData(0x30F, Scenes.WATERWAY, item_names.use_purifying, type="3hb"),
    loc_names.uw_first_ledge2:     CVLoDLocationData(0x310, Scenes.WATERWAY, item_names.use_purifying, type="3hb"),
    loc_names.uw_first_ledge3:     CVLoDLocationData(0x311, Scenes.WATERWAY, item_names.use_ampoule, type="3hb"),
    loc_names.uw_first_ledge4:     CVLoDLocationData(0x312, Scenes.WATERWAY, item_names.use_ampoule, type="3hb"),
    loc_names.uw_first_ledge5:     CVLoDLocationData(0x313, Scenes.WATERWAY, item_names.gold_300, type="3hb"),
    loc_names.uw_first_ledge6:     CVLoDLocationData(0x314, Scenes.WATERWAY, item_names.gold_300, type="3hb"),
    loc_names.uw_poison_parkour:   CVLoDLocationData(0xDE, Scenes.WATERWAY, item_names.use_ampoule, actor=("proxy", 80)),
    loc_names.uw_waterfall_ledge:  CVLoDLocationData(0xE2, Scenes.WATERWAY, item_names.gold_500, actor=("proxy", 84)),
    loc_names.uw_waterfall_child:  CVLoDLocationData(0x25, Scenes.WATERWAY, item_names.gold_100, actor=("proxy", 70)),
    loc_names.uw_carrie1:          CVLoDLocationData(0xDF, Scenes.WATERWAY, item_names.use_card_m, type="carrie", actor=("proxy", 81)),
    loc_names.uw_carrie2:          CVLoDLocationData(0xE0, Scenes.WATERWAY, item_names.use_beef, type="carrie", actor=("proxy", 82)),
    loc_names.uw_bricks_save:      CVLoDLocationData(0xE1, Scenes.WATERWAY, item_names.powerup, actor=("proxy", 83)),
    loc_names.uw_above_skel_ledge: CVLoDLocationData(0xE3, Scenes.WATERWAY, item_names.use_chicken, actor=("proxy", 100)),
    loc_names.uw_in_skel_ledge1:   CVLoDLocationData(0x315, Scenes.WATERWAY, item_names.use_chicken, type="3hb"),
    loc_names.uw_in_skel_ledge2:   CVLoDLocationData(0x316, Scenes.WATERWAY, item_names.use_chicken, type="3hb"),
    loc_names.uw_in_skel_ledge3:   CVLoDLocationData(0x317, Scenes.WATERWAY, item_names.use_chicken, type="3hb"),

    # The Outer Wall
    loc_names.towf_start_rear:           CVLoDLocationData(0x26A, Scenes.THE_OUTER_WALL, item_names.gold_500, actor=("proxy", 56)),
    loc_names.towf_start_front:          CVLoDLocationData(0x269, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 55)),
    loc_names.towf_start_entry_l:        CVLoDLocationData(0x338, Scenes.THE_OUTER_WALL, item_names.gold_100, actor=("proxy", 103), type="empty"),
    loc_names.towf_start_entry_r:        CVLoDLocationData(0x339, Scenes.THE_OUTER_WALL, item_names.gold_100, actor=("proxy", 102), type="empty"),
    loc_names.towf_start_climb_b:        CVLoDLocationData(0x267, Scenes.THE_OUTER_WALL, item_names.sub_axe, actor=("proxy", 53)),
    loc_names.towf_start_climb_t:        CVLoDLocationData(0x268, Scenes.THE_OUTER_WALL, item_names.jewel_rs, actor=("proxy", 77)),
    loc_names.towf_start_elevator_l:     CVLoDLocationData(0x33A, Scenes.THE_OUTER_WALL, item_names.gold_300, actor=("proxy", 105), type="empty"),
    loc_names.towf_start_elevator_r:     CVLoDLocationData(0x33B, Scenes.THE_OUTER_WALL, item_names.gold_300, actor=("proxy", 104), type="empty"),
    loc_names.towse_pillar_l:            CVLoDLocationData(0x26B, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 57)),
    loc_names.towse_pillar_r:            CVLoDLocationData(0x26C, Scenes.THE_OUTER_WALL, item_names.gold_300, actor=("proxy", 83)),
    loc_names.towse_eagle:               CVLoDLocationData(0x266, Scenes.THE_OUTER_WALL, item_names.use_beef, actor=("proxy", 51)),
    loc_names.towse_saws_door_l:         CVLoDLocationData(0x26D, Scenes.THE_OUTER_WALL, item_names.use_card_s, actor=("proxy", 59)),
    loc_names.towse_saws_door_r:         CVLoDLocationData(0x26E, Scenes.THE_OUTER_WALL, item_names.sub_axe, actor=("proxy", 86)),
    loc_names.towse_child:               CVLoDLocationData(0x26, Scenes.THE_OUTER_WALL, item_names.gold_100, actor=("proxy", 41)),
    loc_names.towse_key_ledge:           CVLoDLocationData(0x26F, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 61)),
    loc_names.towse_key_entry_l:         CVLoDLocationData(0x33C, Scenes.THE_OUTER_WALL, item_names.gold_500, actor=("proxy", 107), type="empty"),
    loc_names.towse_key_entry_r:         CVLoDLocationData(0x33D, Scenes.THE_OUTER_WALL, item_names.gold_500, actor=("proxy", 106), type="empty"),
    loc_names.towse_key_alcove:          CVLoDLocationData(0x285, Scenes.THE_OUTER_WALL, item_names.quest_key_wall, actor=("proxy", 42)),
    loc_names.towse_locked_door_l:       CVLoDLocationData(0x33E, Scenes.THE_OUTER_WALL, item_names.jewel_rs, actor=("proxy", 109), type="empty"),
    loc_names.towse_locked_door_r:       CVLoDLocationData(0x33F, Scenes.THE_OUTER_WALL, item_names.jewel_rs, actor=("proxy", 108), type="empty"),
    loc_names.towse_half_arch_under:     CVLoDLocationData(0x271, Scenes.THE_OUTER_WALL, item_names.gold_300, actor=("proxy", 90)),
    loc_names.towse_half_arch_between:   CVLoDLocationData(0x272, Scenes.THE_OUTER_WALL, item_names.jewel_rs, actor=("proxy", 89)),
    loc_names.towse_half_arch_secret:    CVLoDLocationData(0x270, Scenes.THE_OUTER_WALL, item_names.use_beef, actor=("proxy", 92)),
    loc_names.towf_retract_elevator_l:   CVLoDLocationData(0x340, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 111), type="empty"),
    loc_names.towf_retract_elevator_r:   CVLoDLocationData(0x341, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 110), type="empty"),
    loc_names.towf_retract_shimmy_start: CVLoDLocationData(0x273, Scenes.THE_OUTER_WALL, item_names.jewel_rs, actor=("proxy", 78)),
    loc_names.towf_retract_shimmy_mid:   CVLoDLocationData(0x274, Scenes.THE_OUTER_WALL, item_names.use_card_m, actor=("proxy", 66)),
    loc_names.towf_boulders_door_l:      CVLoDLocationData(0x275, Scenes.THE_OUTER_WALL, item_names.sub_cross, actor=("proxy", 80)),
    loc_names.towf_boulders_door_r:      CVLoDLocationData(0x276, Scenes.THE_OUTER_WALL, item_names.gold_300, actor=("proxy", 100)),
    loc_names.towh_boulders_elevator_l:  CVLoDLocationData(0x342, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 113), type="empty"),
    loc_names.towh_boulders_elevator_r:  CVLoDLocationData(0x343, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 112), type="empty"),
    loc_names.towh_near_boulders_exit:   CVLoDLocationData(0x277, Scenes.THE_OUTER_WALL, item_names.sub_axe, actor=("proxy", 69)),
    loc_names.towh_slide_start:          CVLoDLocationData(0x278, Scenes.THE_OUTER_WALL, item_names.jewel_rs, actor=("proxy", 95)),
    loc_names.towh_slide_first_u:        CVLoDLocationData(0x27A, Scenes.THE_OUTER_WALL, item_names.sub_cross, actor=("proxy", 72)),
    loc_names.towh_slide_first_l:        CVLoDLocationData(0x279, Scenes.THE_OUTER_WALL, item_names.use_chicken, actor=("proxy", 96)),
    loc_names.towh_slide_second:         CVLoDLocationData(0x27B, Scenes.THE_OUTER_WALL, item_names.jewel_rl, actor=("proxy", 73)),

    # Art Tower
    loc_names.atm_ww:            CVLoDLocationData(0x22A, Scenes.ART_TOWER_MUSEUM, item_names.gold_300),
    loc_names.atm_nw_ped:        CVLoDLocationData(0x236, Scenes.ART_TOWER_MUSEUM, item_names.sub_holy),
    loc_names.atm_nw_corner:     CVLoDLocationData(0x22B, Scenes.ART_TOWER_MUSEUM, item_names.use_card_m),
    loc_names.atm_sw_alcove_1:   CVLoDLocationData(0x22C, Scenes.ART_TOWER_MUSEUM, item_names.jewel_rl),
    loc_names.atm_sw_alcove_2:   CVLoDLocationData(0x22D, Scenes.ART_TOWER_MUSEUM, item_names.jewel_rs),
    loc_names.atm_sw_alcove_4:   CVLoDLocationData(0x22E, Scenes.ART_TOWER_MUSEUM, item_names.gold_100),
    loc_names.atm_sw_alcove_6:   CVLoDLocationData(0x22F, Scenes.ART_TOWER_MUSEUM, item_names.sub_holy),
    loc_names.atm_sw_key_ped:    CVLoDLocationData(0x286, Scenes.ART_TOWER_MUSEUM, item_names.quest_key_art_1),
    loc_names.atm_sw_key_corner: CVLoDLocationData(0x230, Scenes.ART_TOWER_MUSEUM, item_names.use_purifying),
    loc_names.atm_se:            CVLoDLocationData(0x231, Scenes.ART_TOWER_MUSEUM, item_names.powerup),
    loc_names.atm_ne_ped:        CVLoDLocationData(0x237, Scenes.ART_TOWER_MUSEUM, item_names.gold_500),
    loc_names.atm_ne_near:       CVLoDLocationData(0x232, Scenes.ART_TOWER_MUSEUM, item_names.use_card_s),
    loc_names.atm_ee_plat_1:     CVLoDLocationData(0x233, Scenes.ART_TOWER_MUSEUM, item_names.jewel_rs),
    loc_names.atm_ee_plat_2:     CVLoDLocationData(0x234, Scenes.ART_TOWER_MUSEUM, item_names.jewel_rl),
    loc_names.atm_ee_key_ped:    CVLoDLocationData(0x287, Scenes.ART_TOWER_MUSEUM, item_names.quest_key_art_2),
    loc_names.atm_ee_key_corner: CVLoDLocationData(0x235, Scenes.ART_TOWER_MUSEUM, item_names.use_card_m),
    loc_names.atc_sw_statue_l:   CVLoDLocationData(0x23D, Scenes.ART_TOWER_CONSERVATORY, item_names.use_purifying),
    loc_names.atc_sw_statue_r:   CVLoDLocationData(0x23C, Scenes.ART_TOWER_CONSERVATORY, item_names.jewel_rl),
    loc_names.atc_ne_statue_l:   CVLoDLocationData(0x23E, Scenes.ART_TOWER_CONSERVATORY, item_names.jewel_rs),
    loc_names.atc_ne_statue_r:   CVLoDLocationData(0x23F, Scenes.ART_TOWER_CONSERVATORY, item_names.jewel_rs),
    loc_names.atc_organ:         CVLoDLocationData(0x23B, Scenes.ART_TOWER_CONSERVATORY, item_names.use_ampoule),
    loc_names.atc_pillar_l:      CVLoDLocationData(0x23A, Scenes.ART_TOWER_CONSERVATORY, item_names.use_chicken),
    loc_names.atc_pillar_r:      CVLoDLocationData(0x239, Scenes.ART_TOWER_CONSERVATORY, item_names.sub_cross),
    loc_names.atc_doorway_l:     CVLoDLocationData(0x2AF, Scenes.ART_TOWER_CONSERVATORY, item_names.gold_500),
    loc_names.atc_doorway_m:     CVLoDLocationData(0x2AE, Scenes.ART_TOWER_CONSERVATORY, item_names.use_beef),
    loc_names.atc_doorway_r:     CVLoDLocationData(0x2B0, Scenes.ART_TOWER_CONSERVATORY, item_names.gold_500),
    loc_names.atc_balcony_save:  CVLoDLocationData(0x240, Scenes.ART_TOWER_CONSERVATORY, item_names.sub_cross),
    loc_names.atc_bp_f:          CVLoDLocationData(0x241, Scenes.ART_TOWER_CONSERVATORY, item_names.use_purifying),
    loc_names.atc_bp_r:          CVLoDLocationData(0x242, Scenes.ART_TOWER_CONSERVATORY, item_names.gold_300),

    # Tower of Ruins
    loc_names.torm_trap_side:   CVLoDLocationData(0x20D, Scenes.RUINS_DOOR_MAZE, item_names.sub_holy),
    loc_names.torm_trap_corner: CVLoDLocationData(0x20E, Scenes.RUINS_DOOR_MAZE, item_names.jewel_rl),
    loc_names.torm_b6:          CVLoDLocationData(0x201, Scenes.RUINS_DOOR_MAZE, item_names.gold_300),
    loc_names.torm_b4_corner:   CVLoDLocationData(0x206, Scenes.RUINS_DOOR_MAZE, item_names.jewel_rl),
    loc_names.torm_b4_statue:   CVLoDLocationData(0x200, Scenes.RUINS_DOOR_MAZE, item_names.use_chicken),
    loc_names.torm_a3:          CVLoDLocationData(0x205, Scenes.RUINS_DOOR_MAZE, item_names.powerup),
    loc_names.torm_b2:          CVLoDLocationData(0x208, Scenes.RUINS_DOOR_MAZE, item_names.sub_holy),
    loc_names.torm_a1:          CVLoDLocationData(0x207, Scenes.RUINS_DOOR_MAZE, item_names.gold_300),
    loc_names.torm_d4:          CVLoDLocationData(0x203, Scenes.RUINS_DOOR_MAZE, item_names.gold_300),
    loc_names.torm_g4:          CVLoDLocationData(0x20B, Scenes.RUINS_DOOR_MAZE, item_names.use_purifying),
    loc_names.torm_g3_l:        CVLoDLocationData(0x209, Scenes.RUINS_DOOR_MAZE, item_names.sub_holy),
    loc_names.torm_g3_r:        CVLoDLocationData(0x20A, Scenes.RUINS_DOOR_MAZE, item_names.sub_cross),
    loc_names.torm_g3_s:        CVLoDLocationData(0x202, Scenes.RUINS_DOOR_MAZE, item_names.gold_300),
    loc_names.torm_lookback_l:  CVLoDLocationData(0x211, Scenes.RUINS_DOOR_MAZE, item_names.jewel_rs),
    loc_names.torm_lookback_r:  CVLoDLocationData(0x210, Scenes.RUINS_DOOR_MAZE, item_names.jewel_rs),
    loc_names.torm_lookback_u:  CVLoDLocationData(0x20C, Scenes.RUINS_DOOR_MAZE, item_names.use_chicken),
    loc_names.torc_lfloor_f:    CVLoDLocationData(0x215, Scenes.RUINS_DARK_CHAMBERS, item_names.jewel_rl),
    loc_names.torc_lfloor_r:    CVLoDLocationData(0x216, Scenes.RUINS_DARK_CHAMBERS, item_names.jewel_rs),
    loc_names.torc_walkway_l:   CVLoDLocationData(0x21C, Scenes.RUINS_DARK_CHAMBERS, item_names.jewel_rs),
    loc_names.torc_ufloor_rl:   CVLoDLocationData(0x21B, Scenes.RUINS_DARK_CHAMBERS, item_names.jewel_rs),
    loc_names.torc_ufloor_m:    CVLoDLocationData(0x219, Scenes.RUINS_DARK_CHAMBERS, item_names.powerup),
    loc_names.torc_ufloor_fr:   CVLoDLocationData(0x21A, Scenes.RUINS_DARK_CHAMBERS, item_names.sub_holy),
    loc_names.torc_meat_l:      CVLoDLocationData(0x2AC, Scenes.RUINS_DARK_CHAMBERS, item_names.use_beef),
    loc_names.torc_meat_r:      CVLoDLocationData(0x2AD, Scenes.RUINS_DARK_CHAMBERS, item_names.powerup),
    loc_names.torc_walkway_u:   CVLoDLocationData(0x21D, Scenes.RUINS_DARK_CHAMBERS, item_names.gold_300),
    loc_names.torc_aries:       CVLoDLocationData(0x21E, Scenes.RUINS_DARK_CHAMBERS, item_names.jewel_rs),
    loc_names.torc_taurus:      CVLoDLocationData(0x21F, Scenes.RUINS_DARK_CHAMBERS, item_names.gold_100),
    loc_names.torc_leo:         CVLoDLocationData(0x220, Scenes.RUINS_DARK_CHAMBERS, item_names.use_purifying),
    loc_names.torc_sagittarius: CVLoDLocationData(0x221, Scenes.RUINS_DARK_CHAMBERS, item_names.sub_holy),
    loc_names.torc_across_exit: CVLoDLocationData(0x223, Scenes.RUINS_DARK_CHAMBERS, item_names.use_card_m),
    loc_names.torc_near_exit:   CVLoDLocationData(0x222, Scenes.RUINS_DARK_CHAMBERS, item_names.use_card_s),

    # Castle Center
    loc_names.ccb_skel_hallway_ent:          CVLoDLocationData(0xF5, Scenes.CASTLE_CENTER_BASEMENT, item_names.jewel_rs),
    loc_names.ccb_skel_hallway_jun:          CVLoDLocationData(0xF8, Scenes.CASTLE_CENTER_BASEMENT, item_names.powerup),
    loc_names.ccb_skel_hallway_tc:           CVLoDLocationData(0xF6, Scenes.CASTLE_CENTER_BASEMENT, item_names.jewel_rl),
    loc_names.ccb_skel_hallway_ba:           CVLoDLocationData(0xF7, Scenes.CASTLE_CENTER_BASEMENT, item_names.sub_cross),
    loc_names.ccb_behemoth_l_ff:             CVLoDLocationData(0xF9, Scenes.CASTLE_CENTER_BASEMENT, item_names.jewel_rs),
    loc_names.ccb_behemoth_l_mf:             CVLoDLocationData(0xFA, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_300),
    loc_names.ccb_behemoth_l_mr:             CVLoDLocationData(0xFB, Scenes.CASTLE_CENTER_BASEMENT, item_names.jewel_rl),
    loc_names.ccb_behemoth_l_fr:             CVLoDLocationData(0xFC, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500),
    loc_names.ccb_behemoth_r_ff:             CVLoDLocationData(0x100, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_300),
    loc_names.ccb_behemoth_r_mf:             CVLoDLocationData(0xFF, Scenes.CASTLE_CENTER_BASEMENT, item_names.jewel_rl),
    loc_names.ccb_behemoth_r_mr:             CVLoDLocationData(0xFE, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500),
    loc_names.ccb_behemoth_r_fr:             CVLoDLocationData(0xFD, Scenes.CASTLE_CENTER_BASEMENT, item_names.jewel_rl),
    loc_names.ccb_behemoth_crate1:           CVLoDLocationData(0x318, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500, type="3hb"),
    loc_names.ccb_behemoth_crate2:           CVLoDLocationData(0x319, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500, type="3hb"),
    loc_names.ccb_behemoth_crate3:           CVLoDLocationData(0x31A, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500, type="3hb"),
    loc_names.ccb_behemoth_crate4:           CVLoDLocationData(0x31B, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500, type="3hb"),
    loc_names.ccb_behemoth_crate5:           CVLoDLocationData(0x31C, Scenes.CASTLE_CENTER_BASEMENT, item_names.gold_500, type="3hb"),
    loc_names.ccbe_near_machine:             CVLoDLocationData(0x108, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.jewel_rs),
    loc_names.ccbe_atop_machine:             CVLoDLocationData(0x109, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.powerup),
    loc_names.ccbe_stand1:                   CVLoDLocationData(0x31D, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.use_beef, type="3hb"),
    loc_names.ccbe_stand2:                   CVLoDLocationData(0x31E, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.use_beef, type="3hb"),
    loc_names.ccbe_stand3:                   CVLoDLocationData(0x31F, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.use_beef, type="3hb"),
    loc_names.ccbe_pipes:                    CVLoDLocationData(0x10A, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.gold_300),
    loc_names.ccbe_switch:                   CVLoDLocationData(0x10C, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.sub_holy),
    loc_names.ccbe_staircase:                CVLoDLocationData(0x10B, Scenes.CASTLE_CENTER_BOTTOM_ELEV, item_names.jewel_rl),
    loc_names.ccff_gears_side:               CVLoDLocationData(0x10E, Scenes.CASTLE_CENTER_FACTORY, item_names.jewel_rs),
    loc_names.ccff_gears_mid:                CVLoDLocationData(0x10F, Scenes.CASTLE_CENTER_FACTORY, item_names.use_purifying),
    loc_names.ccff_gears_corner:             CVLoDLocationData(0x110, Scenes.CASTLE_CENTER_FACTORY, item_names.use_chicken),
    loc_names.ccff_lizard_near_knight:       CVLoDLocationData(0x111, Scenes.CASTLE_CENTER_FACTORY, item_names.sub_axe),
    loc_names.ccff_lizard_pit:               CVLoDLocationData(0x112, Scenes.CASTLE_CENTER_FACTORY, item_names.use_card_s),
    loc_names.ccff_lizard_corner:            CVLoDLocationData(0x113, Scenes.CASTLE_CENTER_FACTORY, item_names.use_card_m),
    loc_names.ccff_lizard_locker_nfr:        CVLoDLocationData(0x117, Scenes.CASTLE_CENTER_FACTORY, item_names.jewel_rl, type="liz"),
    loc_names.ccff_lizard_locker_nmr:        CVLoDLocationData(0x118, Scenes.CASTLE_CENTER_FACTORY, item_names.gold_500, type="liz"),
    loc_names.ccff_lizard_locker_nml:        CVLoDLocationData(0x119, Scenes.CASTLE_CENTER_FACTORY, item_names.use_ampoule, type="liz"),
    loc_names.ccff_lizard_locker_nfl:        CVLoDLocationData(0x11A, Scenes.CASTLE_CENTER_FACTORY, item_names.powerup, type="liz"),
    loc_names.ccff_lizard_locker_fl:         CVLoDLocationData(0x11B, Scenes.CASTLE_CENTER_FACTORY, item_names.gold_500, type="liz"),
    loc_names.ccff_lizard_locker_fr:         CVLoDLocationData(0x11C, Scenes.CASTLE_CENTER_FACTORY, item_names.use_card_s, type="liz"),
    loc_names.ccff_lizard_slab1:             CVLoDLocationData(0x320, Scenes.CASTLE_CENTER_FACTORY, item_names.use_purifying, type="3hb"),
    loc_names.ccff_lizard_slab2:             CVLoDLocationData(0x321, Scenes.CASTLE_CENTER_FACTORY, item_names.use_purifying, type="3hb"),
    loc_names.ccff_lizard_slab3:             CVLoDLocationData(0x322, Scenes.CASTLE_CENTER_FACTORY, item_names.use_ampoule, type="3hb"),
    loc_names.ccff_lizard_slab4:             CVLoDLocationData(0x323, Scenes.CASTLE_CENTER_FACTORY, item_names.use_ampoule, type="3hb"),
    loc_names.ccb_mandrag_shelf_l:           CVLoDLocationData(0x345, Scenes.CASTLE_CENTER_BASEMENT, item_names.quest_mandragora),
    loc_names.ccb_mandrag_shelf_r:           CVLoDLocationData(0x346, Scenes.CASTLE_CENTER_BASEMENT, item_names.quest_mandragora),
    loc_names.ccb_torture_rack:              CVLoDLocationData(0x101, Scenes.CASTLE_CENTER_BASEMENT, item_names.use_purifying),
    loc_names.ccb_torture_rafters:           CVLoDLocationData(0x102, Scenes.CASTLE_CENTER_BASEMENT, item_names.use_beef),
    loc_names.ccll_brokenstairs_floor:       CVLoDLocationData(0x123, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.jewel_rl),
    loc_names.ccll_brokenstairs_save:        CVLoDLocationData(0x122, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.jewel_rl),
    loc_names.ccll_glassknight_l:            CVLoDLocationData(0x12A, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.jewel_rs),
    loc_names.ccll_glassknight_r:            CVLoDLocationData(0x12B, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.jewel_rs),
    loc_names.ccll_butlers_door:             CVLoDLocationData(0x125, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.jewel_rs),
    loc_names.ccll_butlers_side:             CVLoDLocationData(0x124, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.use_purifying),
    loc_names.ccll_cwhall_butlerflames_past: CVLoDLocationData(0x126, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.use_ampoule),
    loc_names.ccll_cwhall_flamethrower:      CVLoDLocationData(0x129, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.gold_500),
    loc_names.ccll_cwhall_cwflames:          CVLoDLocationData(0x127, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.use_chicken),
    loc_names.ccll_heinrich:                 CVLoDLocationData(0x284, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.quest_key_chbr),
    loc_names.ccia_nitro_crates:             CVLoDLocationData(0x13A, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_kit),
    loc_names.ccia_nitro_shelf_h:            CVLoDLocationData(0x347, Scenes.CASTLE_CENTER_INVENTIONS, item_names.quest_nitro),
    loc_names.ccia_stairs_knight:            CVLoDLocationData(0x13B, Scenes.CASTLE_CENTER_INVENTIONS, item_names.gold_500),
    loc_names.ccia_maids_vase:               CVLoDLocationData(0x135, Scenes.CASTLE_CENTER_INVENTIONS, item_names.jewel_rl),
    loc_names.ccia_maids_outer:              CVLoDLocationData(0x130, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_purifying),
    loc_names.ccia_maids_inner:              CVLoDLocationData(0x131, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_ampoule),
    loc_names.ccia_inventions_maids:         CVLoDLocationData(0x133, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_card_m),
    loc_names.ccia_inventions_crusher:       CVLoDLocationData(0x132, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_card_s),
    loc_names.ccia_inventions_famicart:      CVLoDLocationData(0x137, Scenes.CASTLE_CENTER_INVENTIONS, item_names.gold_500),
    loc_names.ccia_inventions_zeppelin:      CVLoDLocationData(0x2AA, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_beef),
    loc_names.ccia_inventions_round:         CVLoDLocationData(0x138, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_beef),
    loc_names.ccia_nitrohall_flamethrower:   CVLoDLocationData(0x139, Scenes.CASTLE_CENTER_INVENTIONS, item_names.jewel_rl),
    loc_names.ccia_nitrohall_torch:          CVLoDLocationData(0x134, Scenes.CASTLE_CENTER_INVENTIONS, item_names.use_chicken),
    loc_names.ccia_nitro_shelf_i:            CVLoDLocationData(0x348, Scenes.CASTLE_CENTER_INVENTIONS, item_names.quest_nitro),
    loc_names.ccll_cwhall_wall:              CVLoDLocationData(0x128, Scenes.CASTLE_CENTER_LIZARD_LAB, item_names.use_beef),
    loc_names.ccl_bookcase:                  CVLoDLocationData(0x13E, Scenes.CASTLE_CENTER_LIBRARY, item_names.use_card_s),

    # Duel Tower
    loc_names.dt_pre_sweeper_l:  CVLoDLocationData(0x249, Scenes.DUEL_TOWER, item_names.jewel_rs),
    loc_names.dt_pre_sweeper_r:  CVLoDLocationData(0x248, Scenes.DUEL_TOWER, item_names.jewel_rs),
    loc_names.dt_werewolf_ledge: CVLoDLocationData(0x254, Scenes.DUEL_TOWER, item_names.powerup),
    loc_names.dt_post_sweeper_l: CVLoDLocationData(0x252, Scenes.DUEL_TOWER, item_names.jewel_rs),
    loc_names.dt_post_sweeper_r: CVLoDLocationData(0x253, Scenes.DUEL_TOWER, item_names.jewel_rs),
    loc_names.dt_slant_l:        CVLoDLocationData(0x24B, Scenes.DUEL_TOWER, item_names.gold_300),
    loc_names.dt_slant_r:        CVLoDLocationData(0x24A, Scenes.DUEL_TOWER, item_names.jewel_rs),
    loc_names.dt_pinwheels_l:    CVLoDLocationData(0x24C, Scenes.DUEL_TOWER, item_names.use_chicken),
    loc_names.dt_pinwheels_r:    CVLoDLocationData(0x24D, Scenes.DUEL_TOWER, item_names.jewel_rl),
    loc_names.dt_guards_l:       CVLoDLocationData(0x24E, Scenes.DUEL_TOWER, item_names.jewel_rs),
    loc_names.dt_guards_r:       CVLoDLocationData(0x24F, Scenes.DUEL_TOWER, item_names.gold_300),
    loc_names.dt_werebull_l:     CVLoDLocationData(0x251, Scenes.DUEL_TOWER, item_names.use_chicken),
    loc_names.dt_werebull_r:     CVLoDLocationData(0x250, Scenes.DUEL_TOWER, item_names.powerup),

    # Tower of Execution
    loc_names.toe_start_l:          CVLoDLocationData(0x1BB, Scenes.EXECUTION_MAIN, item_names.sub_axe),
    loc_names.toe_start_r:          CVLoDLocationData(0x1BC, Scenes.EXECUTION_MAIN, item_names.jewel_rs),
    loc_names.toe_spike_alcove_l:   CVLoDLocationData(0x1BE, Scenes.EXECUTION_MAIN, item_names.use_purifying),
    loc_names.toe_spike_alcove_r:   CVLoDLocationData(0x1BD, Scenes.EXECUTION_MAIN, item_names.gold_100),
    loc_names.toe_spike_platform_l: CVLoDLocationData(0x1C0, Scenes.EXECUTION_MAIN, item_names.gold_300),
    loc_names.toe_spike_platform_r: CVLoDLocationData(0x1BF, Scenes.EXECUTION_MAIN, item_names.sub_knife),
    loc_names.toem_stones_l:        CVLoDLocationData(0x1CD, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.jewel_rl),
    loc_names.toem_stones_r:        CVLoDLocationData(0x1CE, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.gold_100),
    loc_names.toem_walkway:         CVLoDLocationData(0x1CF, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.gold_300),
    loc_names.toeg_platform:        CVLoDLocationData(0x1C5, Scenes.EXECUTION_SIDE_ROOMS_1, item_names.jewel_rl),
    loc_names.toeg_alcove_l:        CVLoDLocationData(0x1C7, Scenes.EXECUTION_SIDE_ROOMS_1, item_names.use_ampoule),
    loc_names.toeg_alcove_r:        CVLoDLocationData(0x1C6, Scenes.EXECUTION_SIDE_ROOMS_1, item_names.sub_holy),
    loc_names.toeb_midway_l:        CVLoDLocationData(0x1C8, Scenes.EXECUTION_SIDE_ROOMS_1, item_names.jewel_rl),
    loc_names.toeb_midway_r:        CVLoDLocationData(0x1C9, Scenes.EXECUTION_SIDE_ROOMS_1, item_names.use_card_m),
    loc_names.toeb_corner:          CVLoDLocationData(0x1CA, Scenes.EXECUTION_SIDE_ROOMS_1, item_names.use_beef),
    loc_names.toe_renon_l:          CVLoDLocationData(0x1C2, Scenes.EXECUTION_MAIN, item_names.gold_500),
    loc_names.toe_renon_r:          CVLoDLocationData(0x1C1, Scenes.EXECUTION_MAIN, item_names.use_card_s),
    loc_names.toe_knights:          CVLoDLocationData(0x1C3, Scenes.EXECUTION_MAIN, item_names.sub_cross),
    loc_names.toe_first_pillar:     CVLoDLocationData(0x1B5, Scenes.EXECUTION_MAIN, item_names.powerup),
    loc_names.toe_last_pillar:      CVLoDLocationData(0x1B8, Scenes.EXECUTION_MAIN, item_names.sub_cross),
    loc_names.toe_tower:            CVLoDLocationData(0x1BA, Scenes.EXECUTION_MAIN, item_names.use_beef),
    loc_names.toe_top_platform:     CVLoDLocationData(0x1C4, Scenes.EXECUTION_MAIN, item_names.use_chicken),
    loc_names.toeu_fort_save:       CVLoDLocationData(0x1D3, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.use_card_s),
    loc_names.toeu_fort_ibridge:    CVLoDLocationData(0x1D4, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.use_chicken),
    loc_names.toeu_fort_left:       CVLoDLocationData(0x1D5, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.sub_cross),
    loc_names.toeu_fort_lookout:    CVLoDLocationData(0x1CB, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.sub_cross),
    loc_names.toeu_ult_l:           CVLoDLocationData(0x1D0, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.gold_300),
    loc_names.toeu_ult_r:           CVLoDLocationData(0x1D1, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.jewel_rl),
    loc_names.toeu_ult_crack:       CVLoDLocationData(0x1CC, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.jewel_rs),
    loc_names.toeu_jails:           CVLoDLocationData(0x1D7, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.gold_100),
    loc_names.toeu_end_l:           CVLoDLocationData(0x1D9, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.jewel_rs),
    loc_names.toeu_end_r:           CVLoDLocationData(0x1D8, Scenes.EXECUTION_SIDE_ROOMS_2, item_names.jewel_rs),

    # Tower of Science
    loc_names.toscic_first:             CVLoDLocationData(0x1DC, Scenes.SCIENCE_CONVEYORS, item_names.gold_300),
    loc_names.toscic_second:            CVLoDLocationData(0x1DB, Scenes.SCIENCE_CONVEYORS, item_names.jewel_rs),
    loc_names.toscic_elevator:          CVLoDLocationData(0x1DA, Scenes.SCIENCE_CONVEYORS, item_names.jewel_rs),
    loc_names.toscit_lone_c:            CVLoDLocationData(0x1E6, Scenes.SCIENCE_LABS, item_names.gold_300),
    loc_names.toscit_lone_rl:           CVLoDLocationData(0x1E7, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_lone_rr:           CVLoDLocationData(0x1E8, Scenes.SCIENCE_LABS, item_names.gold_300),
    loc_names.toscit_sec_1:             CVLoDLocationData(0x1E9, Scenes.SCIENCE_LABS, item_names.sub_axe),
    loc_names.toscit_sec_2:             CVLoDLocationData(0x1EA, Scenes.SCIENCE_LABS, item_names.jewel_rl),
    loc_names.toscit_sec_check_l:       CVLoDLocationData(0x1EC, Scenes.SCIENCE_LABS, item_names.powerup),
    loc_names.toscit_sec_check_r:       CVLoDLocationData(0x1EB, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_25d_pipes:         CVLoDLocationData(0x1EE, Scenes.SCIENCE_LABS, item_names.sub_holy),
    loc_names.toscit_25d_cover:         CVLoDLocationData(0x1ED, Scenes.SCIENCE_LABS, item_names.use_chicken),
    loc_names.toscit_course_d1_l:       CVLoDLocationData(0x1F0, Scenes.SCIENCE_LABS, item_names.gold_300),
    loc_names.toscit_course_d1_r:       CVLoDLocationData(0x1EF, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_course_d2_l:       CVLoDLocationData(0x1F1, Scenes.SCIENCE_LABS, item_names.sub_cross),
    loc_names.toscit_course_d2_r:       CVLoDLocationData(0x1F2, Scenes.SCIENCE_LABS, item_names.sub_knife),
    loc_names.toscit_course_d3_l:       CVLoDLocationData(0x1F3, Scenes.SCIENCE_LABS, item_names.use_chicken),
    loc_names.toscit_course_d3_c:       CVLoDLocationData(0x1F6, Scenes.SCIENCE_LABS, item_names.gold_300),
    loc_names.toscit_course_alcove:     CVLoDLocationData(0x1F5, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_course_end:        CVLoDLocationData(0x288, Scenes.SCIENCE_LABS, item_names.quest_key_ctrl),
    loc_names.toscit_ctrl_fl:           CVLoDLocationData(0x1E2, Scenes.SCIENCE_LABS, item_names.jewel_rl),
    loc_names.toscit_ctrl_fr:           CVLoDLocationData(0x1E3, Scenes.SCIENCE_LABS, item_names.jewel_rl),
    loc_names.toscit_ctrl_l:            CVLoDLocationData(0x1E1, Scenes.SCIENCE_LABS, item_names.use_chicken),
    loc_names.toscit_ctrl_r:            CVLoDLocationData(0x1E4, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_ctrl_rl:           CVLoDLocationData(0x1E0, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_ctrl_rr:           CVLoDLocationData(0x1E5, Scenes.SCIENCE_LABS, item_names.jewel_rs),
    loc_names.toscit_ctrl_interface_f:  CVLoDLocationData(0x1F4, Scenes.SCIENCE_LABS, item_names.gold_300),
    loc_names.toscit_ctrl_interface_rl: CVLoDLocationData(0x1F7, Scenes.SCIENCE_LABS, item_names.use_chicken),
    loc_names.toscit_ctrl_interface_rr: CVLoDLocationData(0x1F8, Scenes.SCIENCE_LABS, item_names.use_card_s),

    # Tower of Sorcery
    loc_names.tosor_electric: CVLoDLocationData(0x1A9, Scenes.TOWER_OF_SORCERY, item_names.jewel_rs),
    loc_names.tosor_lasers:   CVLoDLocationData(0x1AA, Scenes.TOWER_OF_SORCERY, item_names.sub_axe),
    loc_names.tosor_climb_l:  CVLoDLocationData(0x1AB, Scenes.TOWER_OF_SORCERY, item_names.jewel_rs),
    loc_names.tosor_climb_r:  CVLoDLocationData(0x1AC, Scenes.TOWER_OF_SORCERY, item_names.gold_300),
    loc_names.tosor_ibridge:  CVLoDLocationData(0x1AD, Scenes.TOWER_OF_SORCERY, item_names.powerup),
    loc_names.tosor_super_1:  CVLoDLocationData(0x349, Scenes.TOWER_OF_SORCERY, item_names.gold_500),
    loc_names.tosor_super_2:  CVLoDLocationData(0x34A, Scenes.TOWER_OF_SORCERY, item_names.gold_500),
    loc_names.tosor_super_3:  CVLoDLocationData(0x34B, Scenes.TOWER_OF_SORCERY, item_names.use_kit),

    # Room of Clocks
    loc_names.roc_ent_l:  CVLoDLocationData(0x19C, Scenes.ROOM_OF_CLOCKS, item_names.jewel_rl),
    loc_names.roc_ent_r:  CVLoDLocationData(0x2B5, Scenes.ROOM_OF_CLOCKS, item_names.powerup),
    loc_names.roc_elev_r: CVLoDLocationData(0x19E, Scenes.ROOM_OF_CLOCKS, item_names.sub_axe),
    loc_names.roc_elev_l: CVLoDLocationData(0x19D, Scenes.ROOM_OF_CLOCKS, item_names.sub_cross),
    loc_names.roc_cont_r: CVLoDLocationData(0x19F, Scenes.ROOM_OF_CLOCKS, item_names.jewel_rs),
    loc_names.roc_cont_l: CVLoDLocationData(0x1A1, Scenes.ROOM_OF_CLOCKS, item_names.sub_holy),
    loc_names.roc_exit:   CVLoDLocationData(0x1A0, Scenes.ROOM_OF_CLOCKS, item_names.sub_knife),
    # loc_names.roc_boss:   {"event": item_names.trophy, "add conds": ["boss"]},

    # Clock Tower
    loc_names.ctgc_gearclimb_battery_slab1: CVLoDLocationData(0x324, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_500, type="3hb"),
    loc_names.ctgc_gearclimb_battery_slab2: CVLoDLocationData(0x325, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_500, type="3hb"),
    loc_names.ctgc_gearclimb_battery_slab3: CVLoDLocationData(0x326, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_500, type="3hb"),
    loc_names.ctgc_gearclimb_battery_slab4: CVLoDLocationData(0x327, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_500, type="3hb"),
    loc_names.ctgc_gearclimb_battery_slab5: CVLoDLocationData(0x328, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_500, type="3hb"),
    loc_names.ctgc_gearclimb_battery_slab6: CVLoDLocationData(0x329, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_500, type="3hb"),
    loc_names.ctgc_gearclimb_corner_r:      CVLoDLocationData(0x289, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.quest_key_clock_a),
    loc_names.ctgc_gearclimb_corner_f:      CVLoDLocationData(0x181, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.jewel_rl),
    loc_names.ctgc_gearclimb_door_slab1:    CVLoDLocationData(0x32A, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.use_chicken, type="3hb"),
    loc_names.ctgc_gearclimb_door_slab2:    CVLoDLocationData(0x32B, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.use_chicken, type="3hb"),
    loc_names.ctgc_gearclimb_door_slab3:    CVLoDLocationData(0x32C, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.use_chicken, type="3hb"),
    loc_names.ctgc_bp_chasm_fl:             CVLoDLocationData(0x182, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.gold_300),
    loc_names.ctgc_bp_chasm_fr:             CVLoDLocationData(0x183, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.jewel_rl),
    loc_names.ctgc_bp_chasm_rl:             CVLoDLocationData(0x180, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.sub_knife),
    loc_names.ctgc_bp_chasm_k:              CVLoDLocationData(0x28A, Scenes.CLOCK_TOWER_GEAR_CLIMB, item_names.quest_key_clock_b),
    loc_names.ctga_near_floor:              CVLoDLocationData(0x256, Scenes.CLOCK_TOWER_ABYSS, item_names.gold_300),
    loc_names.ctga_near_climb:              CVLoDLocationData(0x28B, Scenes.CLOCK_TOWER_ABYSS, item_names.quest_key_clock_c),
    loc_names.ctga_far_slab1:               CVLoDLocationData(0x32D, Scenes.CLOCK_TOWER_ABYSS, item_names.jewel_rl, type="3hb"),
    loc_names.ctga_far_slab2:               CVLoDLocationData(0x32E, Scenes.CLOCK_TOWER_ABYSS, item_names.powerup, type="3hb"),
    loc_names.ctga_far_slab3:               CVLoDLocationData(0x32F, Scenes.CLOCK_TOWER_ABYSS, item_names.use_card_s, type="3hb"),
    loc_names.ctga_far_alcove:              CVLoDLocationData(0x28C, Scenes.CLOCK_TOWER_ABYSS, item_names.quest_key_clock_d),
    loc_names.ctf_clock:                    CVLoDLocationData(0x28D, Scenes.CLOCK_TOWER_FACE, item_names.quest_key_clock_e),
    loc_names.ctf_walkway_end:              CVLoDLocationData(0x25E, Scenes.CLOCK_TOWER_FACE, item_names.jewel_rs),
    loc_names.ctf_engine_floor:             CVLoDLocationData(0x260, Scenes.CLOCK_TOWER_FACE, item_names.jewel_rs),
    loc_names.ctf_engine_furnace:           CVLoDLocationData(0x261, Scenes.CLOCK_TOWER_FACE, item_names.gold_300),
    loc_names.ctf_pendulums_l:              CVLoDLocationData(0x25D, Scenes.CLOCK_TOWER_FACE, item_names.use_beef),
    loc_names.ctf_pendulums_r:              CVLoDLocationData(0x25C, Scenes.CLOCK_TOWER_FACE, item_names.use_chicken),
    loc_names.ctf_slope_slab1:              CVLoDLocationData(0x330, Scenes.CLOCK_TOWER_FACE, item_names.gold_500, type="3hb"),
    loc_names.ctf_slope_slab2:              CVLoDLocationData(0x331, Scenes.CLOCK_TOWER_FACE, item_names.powerup, type="3hb"),
    loc_names.ctf_slope_slab3:              CVLoDLocationData(0x332, Scenes.CLOCK_TOWER_FACE, item_names.gold_500, type="3hb"),
    loc_names.ctf_walkway_mid:              CVLoDLocationData(0x25F, Scenes.CLOCK_TOWER_FACE, item_names.powerup, type="3hb"),

    # Castle Keep
    loc_names.ck_renon_sw:    CVLoDLocationData(0x176, Scenes.CASTLE_KEEP_EXTERIOR, item_names.use_ampoule),
    loc_names.ck_renon_se:    CVLoDLocationData(0x175, Scenes.CASTLE_KEEP_EXTERIOR, item_names.jewel_rl),
    loc_names.ck_renon_nw:    CVLoDLocationData(0x178, Scenes.CASTLE_KEEP_EXTERIOR, item_names.use_ampoule),
    loc_names.ck_renon_ne:    CVLoDLocationData(0x177, Scenes.CASTLE_KEEP_EXTERIOR, item_names.use_purifying),
    loc_names.ck_flame_l:     CVLoDLocationData(0x179, Scenes.CASTLE_KEEP_EXTERIOR, item_names.use_beef),
    loc_names.ck_flame_r:     CVLoDLocationData(0x17A, Scenes.CASTLE_KEEP_EXTERIOR, item_names.use_beef),
    loc_names.ck_behind_drac: CVLoDLocationData(0x173, Scenes.CASTLE_KEEP_EXTERIOR, item_names.powerup),
    loc_names.ck_cube:        CVLoDLocationData(0x174, Scenes.CASTLE_KEEP_EXTERIOR, item_names.use_chicken),
}

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

# All Locations specific to Reinhardt and Carrie's version of the Villa. These should not be created if the Villa State
# is Cornell's.
REIN_CARRIE_VILLA_LOCATIONS: list[str] = [
    loc_names.event_villa_rosa,
    loc_names.villala_vincent,
    loc_names.villam_rplatform_f,
    loc_names.event_villa_boss_4,
    loc_names.event_villa_boss_5
]

# All Locations specific to Cornell's version of the Villa. These should not be created if the Villa State is Reinhardt
# and Carrie's.
CORNELL_VILLA_LOCATIONS: list[str] = [
    loc_names.villafy_fountain_shine,
    loc_names.villafo_6am_roses,
    loc_names.event_villa_boss_2,
    loc_names.villala_mary,
    loc_names.event_villa_child,
    loc_names.villam_rplatform_r,
    loc_names.event_villa_boss_3
]

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
        # Don't place the Location if it's a Reinhardt/Carrie Villa Location and the Villa State is Cornell's, or if
        # it's a Cornell Villa Location and the Villa State is Reinhardt/Carrie's.
        if (loc in REIN_CARRIE_VILLA_LOCATIONS and options.villa_state == VillaState.option_cornell) or \
                (loc in CORNELL_VILLA_LOCATIONS and options.villa_state == VillaState.option_reinhardt_carrie):
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

            # If the Location is a 3HB Location, and 3HBs are not enabled, don't add it.
            if CVLOD_LOCATIONS_INFO[loc].type == "3hb" and not options.multi_hit_breakables:
                continue

            # If the Location is a Carrie-only Location, and Carrie Logic is not enabled, don't add it.
            if CVLOD_LOCATIONS_INFO[loc].type == "carrie" and not options.carrie_logic:
                continue

            # If the Location is a Lizard Locker Location, and the Lizard Lockers are not enabled, don't add it.
            if CVLOD_LOCATIONS_INFO[loc].type == "liz" and not options.lizard_locker_items:
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
