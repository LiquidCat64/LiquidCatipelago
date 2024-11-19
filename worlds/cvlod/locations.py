from BaseClasses import Location
from .data import lname, iname, ni_files
from .options import CVLoDOptions, SubWeaponShuffle, DraculasCondition, RenonFightCondition, VincentFightCondition

from typing import Dict, Optional, Union, List, Tuple

base_id = 0xC10D_000


class CVLoDLocation(Location):
    game: str = "Castlevania - Legacy of Darkness"


# # #    KEY    # # #
# "code" = The unique part of the Location's AP code attribute, as well as the in-game bitflag index starting from
#          0x80389BE4 that indicates the Location has been checked. Add this + base_id to get the actual AP code.
# "offset" = The offset in the ROM to overwrite to change the Item on that Location.
# "alt offset" = An alternate offset in the ROM to also overwrite for that same Location, for the very few that you can
#                check in multiple ways.
# "normal item" = The Item normally there in vanilla on most difficulties in most versions of the game. Used to
#                 determine the World's Item counts by checking what Locations are active.
# "hard item" = The Item normally there in Hard Mode in the PAL version of CV64 specifically. Used instead of the
#               normal Item when the hard Item pool is enabled if it's in the Location's data dict.
# "add conds" = A list of player options conditions that must be satisfied for the Location to be added. Can be of
#               varying length depending on how many conditions need to be satisfied. In the add_conds dict's tuples,
#               the first element is the name of the option, the second is the option value to check for, and the third
#               is a boolean for whether we are evaluating for the option value or not.
# "event" = What event Item to place on that Location, for Locations that are events specifically.
# "countdown" = What Countdown number in the array of Countdown numbers that Location contributes to. For the most part,
#               this is figured out by taking that Location's corresponding stage's postion in the vanilla stage order,
#               but there are some exceptions made for Locations in parts of Villa and Castle Center that split off into
#               their own numbers.
# "type" = Anything special about this Location in-game, whether it be NPC-given, invisible, etc.
location_info = {
    # Foggy Lake
    lname.fld_forecast_port:            {"code": 0x150, "offset": 0x7BCE4E, "normal item": iname.gold_500},
    lname.fld_forecast_starboard:       {"code": 0x14F, "offset": 0x7BCE42, "normal item": iname.jewel_l},
    lname.fld_foremast_lower:           {"code": 0x152, "offset": 0x7BCE66, "normal item": iname.jewel_l},
    lname.fld_stairs_port:              {"code": 0x146, "offset": 0x7BCC02, "normal item": iname.jewel_s},
    lname.fld_stairs_starboard:         {"code": 0x148, "offset": 0x7BCBDE, "normal item": iname.jewel_s},
    lname.fld_net_port:                 {"code": 0x14C, "offset": 0x7BCBA2, "normal item": iname.jewel_s},
    lname.fld_net_starboard:            {"code": 0x147, "offset": 0x7BCBF6, "normal item": iname.jewel_s},
    lname.fld_mainmast_base:            {"code": 0x142, "offset": 0x7BCC32, "normal item": iname.knife,
                                         "add conds": ["sub"]},
    lname.fld_near_door:                {"code": 0x149, "offset": 0x7BCBC6, "normal item": iname.jewel_s},
    lname.fld_near_block_l:             {"code": 0x14B, "offset": 0x7BCBAE, "normal item": iname.gold_100},
    lname.fld_near_block_r:             {"code": 0x14A, "offset": 0x7BCBBA, "normal item": iname.jewel_l},
    lname.fld_above_door:               {"code": 0x143, "offset": 0x7BCC26, "normal item": iname.jewel_l},
    lname.fld_stern_port:               {"code": 0x145, "offset": 0x7BCC0E, "normal item": iname.jewel_s},
    lname.fld_stern_starboard:          {"code": 0x144, "offset": 0x7BCC1A, "normal item": iname.jewel_s},
    lname.fld_poop_port_crates:         {"code": 0x140, "offset": 0x7BCC4A, "normal item": iname.powerup},
    lname.fld_poop_starboard_crates:    {"code": 0x141, "offset": 0x7BCC3E, "normal item": iname.jewel_l},
    lname.fld_mainmast_top:             {"code": 0x151, "offset": 0x7BCE5A, "normal item": iname.chicken},
    lname.fld_jiggermast:               {"code": 0x27C, "offset": 0x7BCE1E, "normal item": iname.dck_key},
    lname.fld_foremast_upper_port:      {"code": 0x14D, "offset": 0x7BCE2A, "normal item": iname.beef},
    lname.fld_foremast_upper_starboard: {"code": 0x14E, "offset": 0x7BCE36, "normal item": iname.axe,
                                         "add conds": ["sub"]},
    lname.flb_hallway_l:                {"code": 0x15A, "offset": 0x7C19D6, "normal item": iname.gold_300},
    lname.flb_hallway_r:                {"code": 0x15B, "offset": 0x7C19CA, "normal item": iname.jewel_s},
    lname.flb_tall_crates:              {"code": 0x155, "offset": 0x7C1A12, "normal item": iname.knife,
                                         "add conds": ["sub"]},
    lname.flb_short_crates_l:           {"code": 0x156, "offset": 0x7C1A06, "normal item": iname.jewel_l},
    lname.flb_short_crates_r:           {"code": 0x157, "offset": 0x7C19FA, "normal item": iname.gold_500},
    lname.flp_pier_l:                   {"code": 0x162, "offset": 0x7C68CC, "normal item": iname.chicken},
    lname.flp_pier_m:                   {"code": 0x163, "offset": 0x7C690C, "normal item": iname.axe,
                                         "add conds": ["sub"]},
    lname.flp_pier_r:                   {"code": 0x164, "offset": 0x7C692C, "normal item": iname.jewel_l},
    lname.flp_statue_l:                 {"code": 0x161, "offset": 0x7C682C, "normal item": iname.beef},
    lname.flp_statue_r:                 {"code": 0x160, "offset": 0x7C688C, "normal item": iname.chicken},

    # Forest of Silence
    lname.forest_pier_center:  {"code": 0x16, "offset": 0x77584A, "normal item": iname.jewel_s},
    lname.forest_pier_end:     {"code": 0x17, "offset": 0x775856, "normal item": iname.gold_300},
    lname.forest_sypha_ne:     {"code": 0x19, "offset": 0x77586E, "normal item": iname.ampoule},
    lname.forest_sypha_se:     {"code": 0x18, "offset": 0x775862, "normal item": iname.jewel_l},
    lname.forest_sypha_nw:     {"code": 0x1A, "offset": 0x77587A, "normal item": iname.gold_500},
    lname.forest_sypha_sw:     {"code": 0x1B, "offset": 0x775886, "normal item": iname.purify},
    lname.forest_flea_trail:   {"code": 0x1C, "offset": 0x775892, "normal item": iname.axe, "add conds": ["sub"]},
    lname.forest_leap:         {"code": 0x1E, "offset": 0x7758AA, "normal item": iname.gold_500},
    lname.forest_descent:      {"code": 0x1D, "offset": 0x77589E, "normal item": iname.powerup},
    lname.forest_tunnel:       {"code": 0x21, "offset": 0x7758CE, "normal item": iname.beef},
    lname.forest_child_ledge:  {"code": 0x22, "offset": 0x7758DA, "normal item": iname.gold_100},
    lname.forest_charnel_1:    {"code": 0x11, "offset": 0x774962, "normal item": iname.m_card},
    lname.forest_charnel_2:    {"code": 0x12, "offset": 0x77496E, "normal item": iname.s_card},
    lname.forest_charnel_3:    {"code": 0x13, "offset": 0x7749C2, "normal item": iname.gold_500},
    lname.forest_werewolf_pit: {"code": 0x20, "offset": 0x7758C2, "normal item": iname.knife, "add conds": ["sub"]},
    lname.forest_pike:         {"code": 0x27, "offset": 0x77844C, "normal item": iname.chicken},
    lname.forest_end_gate:     {"code": 0x1F, "offset": 0x7758B6, "normal item": iname.gold_500},
    lname.forest_skelly_mouth: {"code": 0x23, "offset": 0x77842C, "alt offset": (0x43CA, ni_files.OVL_KING_SKELETON),
                                "normal item": iname.chicken},

    # Castle Wall
    lname.cwr_bottom:        {"code": 0x2D,  "offset": 0x77BD92, "normal item": iname.s_card},
    lname.cwr_top:           {"code": 0x30,  "offset": 0x77BDC2, "normal item": iname.chicken},
    lname.cw_dragon_sw:      {"code": 0x49,  "offset": 0x78163A, "normal item": iname.chicken},
    # lname.cw_boss:           {"event": iname.trophy, "add conds": ["boss"]},
    lname.cw_save_slab1:     {"code": 0x2B8, "offset": 0x7816B0, "normal item": iname.jewel_l,   "add conds": ["3hb"]},
    lname.cw_save_slab2:     {"code": 0x2B9, "offset": 0x7816B2, "normal item": iname.jewel_l,   "add conds": ["3hb"]},
    lname.cw_save_slab3:     {"code": 0x2BA, "offset": 0x7816B4, "normal item": iname.jewel_l,   "add conds": ["3hb"]},
    lname.cw_save_slab4:     {"code": 0x2BB, "offset": 0x7816B6, "normal item": iname.jewel_l,   "add conds": ["3hb"]},
    lname.cw_save_slab5:     {"code": 0x2BC, "offset": 0x7816B8, "normal item": iname.jewel_l,   "add conds": ["3hb"]},
    lname.cw_rrampart:       {"code": 0x46,  "offset": 0x781646, "normal item": iname.gold_300},
    lname.cw_lrampart:       {"code": 0x47,  "offset": 0x781616, "normal item": iname.m_card},
    lname.cw_pillar:         {"code": 0x44,  "offset": 0x782754, "normal item": iname.powerup},
    lname.cw_shelf:          {"code": 0x42,  "offset": 0x782734, "normal item": iname.winch},
    lname.cw_shelf_torch:    {"code": 0x4C,  "offset": 0x78165E, "normal item": iname.cross,     "add conds": ["sub"]},
    lname.cw_ground_left:    {"code": 0x48,  "offset": 0x781622, "normal item": iname.purify},
    lname.cw_ground_middle:  {"code": 0x27D, "offset": 0x7815FE, "normal item": iname.lt_key},
    lname.cw_ground_right:   {"code": 0x4D,  "offset": 0x781682, "normal item": iname.axe,       "add conds": ["sub"]},
    lname.cwl_bottom:        {"code": 0x2E,  "offset": 0x77BD9E, "normal item": iname.m_card},
    lname.cwl_bridge:        {"code": 0x2F,  "offset": 0x77BDAA, "normal item": iname.beef},
    lname.cw_drac_sw:        {"code": 0x4E,  "offset": 0x78169A, "normal item": iname.chicken},
    lname.cw_drac_slab1:     {"code": 0x2BD, "offset": 0x7816D4, "normal item": iname.gold_300,  "add conds": ["3hb"]},
    lname.cw_drac_slab2:     {"code": 0x2BE, "offset": 0x7816D6, "normal item": iname.gold_300,  "add conds": ["3hb"]},
    lname.cw_drac_slab3:     {"code": 0x2BF, "offset": 0x7816D8, "normal item": iname.gold_300,  "add conds": ["3hb"]},
    lname.cw_drac_slab4:     {"code": 0x2C0, "offset": 0x7816DA, "normal item": iname.gold_300,  "add conds": ["3hb"]},
    lname.cw_drac_slab5:     {"code": 0x2C1, "offset": 0x7816DC, "normal item": iname.gold_300,  "add conds": ["3hb"]},

    # Villa
    lname.villafy_outer_gate_l:         {"code": 0x62,  "offset": 0x78468A, "normal item": iname.purify},
    lname.villafy_outer_gate_r:         {"code": 0x63,  "offset": 0x784696, "normal item": iname.jewel_l},
    lname.villafy_inner_gate:           {"code": 0x60,  "offset": 0x785B8C, "normal item": iname.beef},
    lname.villafy_gate_marker:          {"code": 0x65,  "offset": 0x7846AE, "normal item": iname.powerup},
    lname.villafy_villa_marker:         {"code": 0x64,  "offset": 0x7846A2, "normal item": iname.beef},
    lname.villafy_fountain_fl:          {"code": 0x5F,  "offset": 0x785B2C, "normal item": iname.gold_500},
    lname.villafy_fountain_fr:          {"code": 0x61,  "offset": 0x785B6C, "normal item": iname.purify},
    lname.villafy_fountain_ml:          {"code": 0x5E,  "offset": 0x785B0C, "normal item": iname.s_card},
    lname.villafy_fountain_mr:          {"code": 0x5A,  "offset": 0x785A6C, "normal item": iname.m_card},
    lname.villafy_fountain_rl:          {"code": 0x5C,  "offset": 0x785ACC, "normal item": iname.beef},
    lname.villafy_fountain_rr:          {"code": 0x5B,  "offset": 0x785A8C, "normal item": iname.gold_500},
    lname.villafy_fountain_shine:       {"code": 0x68,  "offset": 0xFFC6F0, "normal item": iname.crest_a,
                                         "type": "npc"},
    lname.villafo_front_l:              {"code": 0x72,  "offset": 0x787F22, "normal item": iname.jewel_s},
    lname.villafo_front_r:              {"code": 0x73,  "offset": 0x787F2E, "normal item": iname.gold_300},
    lname.villafo_mid_l:                {"code": 0x71,  "offset": 0x787F16, "normal item": iname.gold_300},
    lname.villafo_mid_r:                {"code": 0x70,  "offset": 0x787F0A, "normal item": iname.jewel_s},
    lname.villafo_rear_l:               {"code": 0x6E,  "offset": 0x787EF2, "normal item": iname.jewel_s},
    lname.villafo_rear_r:               {"code": 0x6F,  "offset": 0x787EFE, "normal item": iname.jewel_s},
    lname.villafo_pot_l:                {"code": 0x6D,  "offset": 0x787E6E, "normal item": iname.arc_key},
    lname.villafo_pot_r:                {"code": 0x6C,  "offset": 0x787E62, "normal item": iname.jewel_l},
    lname.villafo_sofa:                 {"code": 0x75,  "offset": 0x7892DC, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villafo_chandelier1:          {"code": 0x302, "offset": 0x787F50, "normal item": iname.gold_500,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier2:          {"code": 0x303, "offset": 0x787F52, "normal item": iname.jewel_l,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier3:          {"code": 0x304, "offset": 0x787F54, "normal item": iname.purify,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier4:          {"code": 0x305, "offset": 0x787F56, "normal item": iname.ampoule,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier5:          {"code": 0x306, "offset": 0x787F58, "normal item": iname.chicken,
                                         "add conds": ["3hb"]},
    lname.villafo_6am_roses:            {"code": 0x78,  "offset": 0xFFC6F2, "normal item": iname.tho_key,
                                         "type": "npc"},
    lname.villala_hallway_stairs:       {"code": 0x80,  "offset": 0x78DDF6, "normal item": iname.jewel_l},
    lname.villala_hallway_l:            {"code": 0x82,  "offset": 0x78DE0E, "normal item": iname.knife,
                                         "add conds": ["sub"]},
    lname.villala_hallway_r:            {"code": 0x81,  "offset": 0x78DE02, "normal item": iname.axe,
                                         "add conds": ["sub"]},
    lname.villala_vincent:              {"code": 0x27F, "offset": 0xFFC6F4, "normal item": iname.jewel_l,
                                         "type": "npc"},
    lname.villala_slivingroom_table_l:  {"code": 0x283, "offset": 0x791C6C, "normal item": iname.gold_100},
    lname.villala_slivingroom_table_r:  {"code": 0x8B,  "offset": 0x791CAC, "normal item": iname.gold_300,
                                         "type": "inv"},
    lname.villala_mary:                 {"code": 0x86, "offset": 0xFFC6F6, "normal item": iname.cu_key,
                                         "type": "npc"},
    lname.villala_slivingroom_mirror:   {"code": 0x83,  "offset": 0x78DE1A, "normal item": iname.cross,
                                         "add conds": ["sub"]},
    lname.villala_diningroom_roses:     {"code": 0x90,  "offset": 0x79184C, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_llivingroom_pot_r:    {"code": 0x27E, "offset": 0x78DDD2, "normal item": iname.str_key},
    lname.villala_llivingroom_pot_l:    {"code": 0x7E,  "offset": 0x78DDDE, "normal item": iname.chicken},
    lname.villala_llivingroom_painting: {"code": 0x8E,  "offset": 0x790FAC, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_llivingroom_light:    {"code": 0x7F,  "offset": 0x78DDEA, "normal item": iname.purify},
    lname.villala_llivingroom_lion:     {"code": 0x8D,  "offset": 0x790F6C, "normal item": iname.chicken,
                                         "type": "inv"},
    lname.villala_exit_knight:          {"code": 0x8F,  "offset": 0x7909AC, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_storeroom_l:          {"code": 0x2B3, "offset": 0x792B8C, "normal item": iname.beef},
    lname.villala_storeroom_r:          {"code": 0x2B2, "offset": 0x792B6C, "normal item": iname.chicken},
    lname.villala_storeroom_s:          {"code": 0x8C,  "offset": 0x792B2C, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_archives_table:       {"code": 0x84,  "offset": 0x792A2C, "normal item": iname.diary,
                                         "type": "inv"},
    lname.villala_archives_rear:        {"code": 0x85,  "offset": 0x792A4C, "normal item": iname.gdn_key},
    lname.villam_malus_torch:           {"code": 0xA3,  "offset": 0x796D9E, "normal item": iname.jewel_s,
                                         "countdown": 17},
    lname.villam_malus_bush:            {"code": 0xAA, "offset": 0x799040, "normal item": iname.chicken,
                                         "type": "inv", "countdown": 17},
    lname.villam_fplatform:             {"code": 0xA7,  "offset": 0x796DAA, "normal item": iname.axe,
                                         "add conds": ["sub"], "countdown": 17},
    lname.villam_frankieturf_l:         {"code": 0x9F,  "offset": 0x796E52, "normal item": iname.gold_300,
                                         "countdown": 17},
    lname.villam_frankieturf_r:         {"code": 0xA8,  "offset": 0x796D6E, "normal item": iname.holy,
                                         "add conds": ["sub"], "countdown": 17},
    lname.villam_frankieturf_ru:        {"code": 0xAC,  "offset": 0x796D86, "normal item": iname.jewel_s,
                                         "countdown": 17},
    lname.villam_hole_de:               {"code": 0x281, "offset": 0x796CBA, "normal item": iname.rg_key,
                                         "countdown": 17},
    lname.villam_fgarden_f:             {"code": 0xA5,  "offset": 0x796E22, "normal item": iname.jewel_s,
                                         "countdown": 17},
    lname.villam_fgarden_mf:            {"code": 0xA2,  "offset": 0x796E16, "normal item": iname.jewel_s,
                                         "countdown": 17},
    lname.villam_fgarden_mr:            {"code": 0xA4,  "offset": 0x796D3E, "normal item": iname.brooch,
                                         "countdown": 17},
    lname.villam_fgarden_r:             {"code": 0xA6,  "offset": 0x796D56, "normal item": iname.jewel_l,
                                         "countdown": 17},
    lname.villam_child_de:              {"code": 0x87,  "offset": 0x796D4A, "normal item": iname.gold_100,
                                         "countdown": 17},
    lname.villam_rplatform_f:           {"code": 0xA9,  "offset": 0x796D7A, "normal item": iname.axe,
                                         "add conds": ["sub"], "countdown": 17},
    lname.villam_rplatform_r:           {"code": 0x9C,  "offset": 0x796CD2, "normal item": iname.crest_b,
                                         "countdown": 17},
    lname.villam_rplatform_de:          {"code": 0xA0,  "offset": 0x796DE6, "normal item": iname.gold_300,
                                         "countdown": 17},
    lname.villam_exit_de:               {"code": 0xA1,  "offset": 0x796E3A, "normal item": iname.gold_300,
                                         "countdown": 17},
    lname.villam_serv_path_sl:          {"code": 0xAB,  "offset": 0x796E6A, "normal item": iname.purify,
                                         "countdown": 17},
    lname.villam_serv_path_sr:          {"code": 0x280, "offset": 0x796CDE, "normal item": iname.gold_100,
                                         "countdown": 17},
    lname.villam_serv_path_l:           {"code": 0x2B1, "offset": 0x796E76, "normal item": iname.ampoule,
                                         "countdown": 17},
    lname.villafo_serv_ent:             {"code": 0x74,  "offset": 0x787EC2, "normal item": iname.chicken},
    lname.villam_crypt_ent:             {"code": 0x9E,  "offset": 0x796CF6, "normal item": iname.purify,
                                         "countdown": 17},
    lname.villam_crypt_upstream:        {"code": 0x9D,  "offset": 0x796CEA, "normal item": iname.beef,
                                         "countdown": 17},
    lname.villac_ent_l:                 {"code": 0x192, "offset": 0x7D63DA, "normal item": iname.jewel_s,
                                         "countdown": 17},
    lname.villac_ent_r:                 {"code": 0x193, "offset": 0x7D63E6, "normal item": iname.gold_300,
                                         "countdown": 17},
    lname.villac_wall_l:                {"code": 0x196, "offset": 0x7D63C2, "normal item": iname.cross,
                                         "add conds": ["sub"], "countdown": 17},
    lname.villac_wall_r:                {"code": 0x197, "offset": 0x7D63CE, "normal item": iname.jewel_l,
                                         "countdown": 17},
    lname.villac_coffin_l:              {"code": 0x194, "offset": 0x7D63FE, "normal item": iname.jewel_s,
                                         "countdown": 17},
    lname.villac_coffin_r:              {"code": 0x195, "offset": 0x7D640A, "normal item": iname.jewel_s,
                                         "countdown": 17},

    # Tunnel
    lname.tunnel_landing:               {"code": 0xB6, "offset": 0x79EED6, "normal item": iname.jewel_l},
    lname.tunnel_landing_rc:            {"code": 0xB7, "offset": 0x79F04A, "normal item": iname.jewel_s},
    lname.tunnel_stone_alcove_r:        {"code": 0xCC, "offset": 0x79EFDE, "normal item": iname.holy,
                                         "add conds": ["sub"]},
    lname.tunnel_stone_alcove_l:        {"code": 0xC5, "offset": 0x79F026, "normal item": iname.beef},
    lname.tunnel_twin_arrows:           {"code": 0xD3, "offset": 0x7A1E40, "normal item": iname.ampoule,
                                         "type": "inv"},
    lname.tunnel_arrows_rock1:          {"code": 0x307, "offset": 0x79F176, "normal item": iname.purify,
                                         "add conds": ["3hb"]},
    lname.tunnel_arrows_rock2:          {"code": 0x308, "offset": 0x79F178, "normal item": iname.purify,
                                         "add conds": ["3hb"]},
    lname.tunnel_arrows_rock3:          {"code": 0x309, "offset": 0x79F17A, "normal item": iname.ampoule,
                                         "add conds": ["3hb"]},
    lname.tunnel_arrows_rock4:          {"code": 0x30A, "offset": 0x79F17C, "normal item": iname.ampoule,
                                         "add conds": ["3hb"]},
    lname.tunnel_arrows_rock5:          {"code": 0x30B, "offset": 0x79F17E, "normal item": iname.chicken,
                                         "add conds": ["3hb"]},
    lname.tunnel_lonesome_bucket:       {"code": 0xD6, "offset": 0x7A1E80, "normal item": iname.ampoule,
                                         "type": "inv"},
    lname.tunnel_lbucket_mdoor_l:       {"code": 0xCE, "offset": 0x79EFF6, "normal item": iname.knife,
                                         "add conds": ["sub"]},
    lname.tunnel_lbucket_quag:          {"code": 0xBB, "offset": 0x79EF12, "normal item": iname.jewel_l},
    lname.tunnel_bucket_quag_rock1:     {"code": 0x30C, "offset": 0x79F180, "normal item": iname.chicken,
                                         "add conds": ["3hb"]},
    lname.tunnel_bucket_quag_rock2:     {"code": 0x30D, "offset": 0x79F182, "normal item": iname.chicken,
                                         "add conds": ["3hb"]},
    lname.tunnel_bucket_quag_rock3:     {"code": 0x30E, "offset": 0x79F184, "normal item": iname.chicken,
                                         "add conds": ["3hb"]},
    lname.tunnel_lbucket_albert:        {"code": 0xBC, "offset": 0x79F062, "normal item": iname.jewel_s},
    lname.tunnel_albert_camp:           {"code": 0xBA, "offset": 0x79F07A, "normal item": iname.jewel_s},
    lname.tunnel_albert_quag:           {"code": 0xB9, "offset": 0x79EEFA, "normal item": iname.jewel_l},
    lname.tunnel_gondola_rc_sdoor_l:    {"code": 0xCD, "offset": 0x79EFEA, "normal item": iname.beef},
    lname.tunnel_gondola_rc_sdoor_m:    {"code": 0xBE, "offset": 0x79EF36, "normal item": iname.beef},
    lname.tunnel_gondola_rc_sdoor_r:    {"code": 0xBD, "offset": 0x79EF2A, "normal item": iname.cross,
                                         "add conds": ["sub"]},
    lname.tunnel_gondola_rc:            {"code": 0xBF, "offset": 0x79EF42, "normal item": iname.powerup},
    lname.tunnel_rgondola_station:      {"code": 0xB8, "offset": 0x79F0C2, "normal item": iname.jewel_s},
    lname.tunnel_gondola_transfer:      {"code": 0xC7, "offset": 0x79EFA2, "normal item": iname.gold_500},
    lname.tunnel_corpse_bucket_quag:    {"code": 0xC0, "offset": 0x79EF4E, "normal item": iname.jewel_l},
    lname.tunnel_corpse_bucket_mdoor_l: {"code": 0xCF, "offset": 0x79F0DA, "normal item": iname.holy,
                                         "add conds": ["sub"]},
    lname.tunnel_corpse_bucket_mdoor_r: {"code": 0xC8, "offset": 0x79EFAE, "normal item": iname.s_card},
    lname.tunnel_shovel_quag_start:     {"code": 0xC1, "offset": 0x79EF5A, "normal item": iname.jewel_l},
    lname.tunnel_exit_quag_start:       {"code": 0xC2, "offset": 0x79EF66, "normal item": iname.jewel_l},
    lname.tunnel_shovel_quag_end:       {"code": 0xC3, "offset": 0x79EF72, "normal item": iname.jewel_l},
    lname.tunnel_exit_quag_end:         {"code": 0xC9, "offset": 0x79F116, "normal item": iname.gold_300},
    lname.tunnel_shovel:                {"code": 0xD2, "offset": 0x7A1EC0, "normal item": iname.beef, "type": "inv"},
    lname.tunnel_shovel_save:           {"code": 0xC4, "offset": 0x79EF7E, "normal item": iname.jewel_l},
    lname.tunnel_shovel_mdoor_c:        {"code": 0x24, "offset": 0x79EF8A, "normal item": iname.gold_100},
    lname.tunnel_shovel_mdoor_l:        {"code": 0xCA, "offset": 0x79EFC6, "normal item": iname.s_card},
    lname.tunnel_shovel_mdoor_r:        {"code": 0xD0, "offset": 0x79F00E, "normal item": iname.axe,
                                         "add conds": ["sub"]},
    lname.tunnel_shovel_sdoor_l:        {"code": 0xCB, "offset": 0x79EFD2, "normal item": iname.m_card},
    lname.tunnel_shovel_sdoor_m:        {"code": 0xC6, "offset": 0x79EF96, "normal item": iname.chicken},
    lname.tunnel_shovel_sdoor_r:        {"code": 0xD1, "offset": 0x79F01A, "normal item": iname.cross,
                                         "add conds": ["sub"]},

    # Underground Waterway
    lname.uw_near_ent:         {"code": 0xDC,  "offset": 0x7A40FA, "normal item": iname.gold_300},
    lname.uw_across_ent:       {"code": 0xDD,  "offset": 0x7A4112, "normal item": iname.gold_300},
    lname.uw_first_ledge1:     {"code": 0x30F, "offset": 0x7A4180, "normal item": iname.purify,   "add conds": ["3hb"]},
    lname.uw_first_ledge2:     {"code": 0x310, "offset": 0x7A4182, "normal item": iname.purify,   "add conds": ["3hb"]},
    lname.uw_first_ledge3:     {"code": 0x311, "offset": 0x7A4184, "normal item": iname.ampoule,  "add conds": ["3hb"]},
    lname.uw_first_ledge4:     {"code": 0x312, "offset": 0x7A4186, "normal item": iname.ampoule,  "add conds": ["3hb"]},
    lname.uw_first_ledge5:     {"code": 0x313, "offset": 0x7A4188, "normal item": iname.gold_300, "add conds": ["3hb"]},
    lname.uw_first_ledge6:     {"code": 0x314, "offset": 0x7A418A, "normal item": iname.gold_300, "add conds": ["3hb"]},
    lname.uw_poison_parkour:   {"code": 0xDE,  "offset": 0x7A40B2, "normal item": iname.ampoule},
    # lname.uw_boss: {"event": iname.trophy, "add conds": ["boss"]},
    lname.uw_waterfall_ledge:  {"code": 0xE2,  "offset": 0x7A40E2, "normal item": iname.gold_500},
    lname.uw_waterfall_child:  {"code": 0x25,  "offset": 0x7A409A, "normal item": iname.gold_100},
    lname.uw_carrie1:          {"code": 0xDF,  "offset": 0x7A40BE, "normal item": iname.m_card,
                                "add conds": ["carrie"]},
    lname.uw_carrie2:          {"code": 0xE0,  "offset": 0x7A40CA, "normal item": iname.beef,
                                "add conds": ["carrie"]},
    lname.uw_bricks_save:      {"code": 0xE1,  "offset": 0x7A40D6, "normal item": iname.powerup},
    lname.uw_above_skel_ledge: {"code": 0xE3,  "offset": 0x7A415A, "normal item": iname.chicken},
    lname.uw_in_skel_ledge1:   {"code": 0x315, "offset": 0x7A419A, "normal item": iname.chicken, "add conds": ["3hb"]},
    lname.uw_in_skel_ledge2:   {"code": 0x316, "offset": 0x7A419C, "normal item": iname.chicken, "add conds": ["3hb"]},
    lname.uw_in_skel_ledge3:   {"code": 0x317, "offset": 0x7A419E, "normal item": iname.chicken, "add conds": ["3hb"]},

    # The Outer Wall
    lname.tow_start_rear:           {"code": 0x26A, "offset": 0x833AB2, "normal item": iname.gold_500},
    lname.tow_start_front:          {"code": 0x269, "offset": 0x833AA6, "normal item": iname.jewel_l},
    lname.tow_start_entry_l:        {"code": 0x338, "offset": 0x833ACA, "normal item": iname.gold_100,
                                     "add conds": ["empty"]},
    lname.tow_start_entry_r:        {"code": 0x339, "offset": 0x833AE2, "normal item": iname.gold_100,
                                     "add conds": ["empty"]},
    lname.tow_start_climb_b:        {"code": 0x267, "offset": 0x833A8E, "normal item": iname.axe, "add conds": ["sub"]},
    lname.tow_start_climb_t:        {"code": 0x268, "offset": 0x833BBA, "normal item": iname.jewel_s},
    lname.tow_start_elevator_l:     {"code": 0x33A, "offset": 0x833AFA, "normal item": iname.gold_300,
                                     "add conds": ["empty"]},
    lname.tow_start_elevator_r:     {"code": 0x33B, "offset": 0x833B06, "normal item": iname.gold_300,
                                     "add conds": ["empty"]},
    lname.tow_pillar_l:             {"code": 0x26B, "offset": 0x833ABE, "normal item": iname.jewel_l},
    lname.tow_pillar_r:             {"code": 0x26C, "offset": 0x833C02, "normal item": iname.gold_300},
    lname.tow_eagle:                {"code": 0x266, "offset": 0x834C6C, "normal item": iname.beef},
    lname.tow_saws_door_l:          {"code": 0x26D, "offset": 0x833AD6, "normal item": iname.s_card},
    lname.tow_saws_door_r:          {"code": 0x26E, "offset": 0x833C26, "normal item": iname.axe, "add conds": ["sub"]},
    lname.tow_child:                {"code": 0x26,  "offset": 0x833A9A, "normal item": iname.gold_100},
    lname.tow_key_ledge:            {"code": 0x26F, "offset": 0x833AEE, "normal item": iname.jewel_l},
    lname.tow_key_entry_l:          {"code": 0x33C, "offset": 0x833B12, "normal item": iname.gold_500,
                                     "add conds": ["empty"]},
    lname.tow_key_entry_r:          {"code": 0x33D, "offset": 0x833B1E, "normal item": iname.gold_500,
                                     "add conds": ["empty"]},
    lname.tow_key_alcove:           {"code": 0x285, "offset": 0x833A82, "normal item": iname.wall_key},
    lname.tow_locked_door_l:        {"code": 0x33E, "offset": 0x833B36, "normal item": iname.jewel_s,
                                     "add conds": ["empty"]},
    lname.tow_locked_door_r:        {"code": 0x33F, "offset": 0x833B42, "normal item": iname.jewel_s,
                                     "add conds": ["empty"]},
    lname.tow_half_arch_under:      {"code": 0x271, "offset": 0x833C56, "normal item": iname.gold_300},
    lname.tow_half_arch_between:    {"code": 0x272, "offset": 0x833C4A, "normal item": iname.jewel_s},
    lname.tow_half_arch_secret:     {"code": 0x270, "offset": 0x833C6E, "normal item": iname.beef},
    lname.tow_retract_elevator_l:   {"code": 0x340, "offset": 0x833B5A, "normal item": iname.jewel_l,
                                     "add conds": ["empty"]},
    lname.tow_retract_elevator_r:   {"code": 0x341, "offset": 0x833B66, "normal item": iname.jewel_l,
                                     "add conds": ["empty"]},
    lname.tow_retract_shimmy_start: {"code": 0x273, "offset": 0x833BC6, "normal item": iname.jewel_s},
    lname.tow_retract_shimmy_mid:   {"code": 0x274, "offset": 0x833B2A, "normal item": iname.m_card},
    lname.tow_boulders_door_l:      {"code": 0x275, "offset": 0x833BDE, "normal item": iname.cross,
                                     "add conds": ["sub"]},
    lname.tow_boulders_door_r:      {"code": 0x276, "offset": 0x833CCE, "normal item": iname.gold_300},
    lname.tow_boulders_elevator_l:  {"code": 0x342, "offset": 0x833BA2, "normal item": iname.jewel_l,
                                     "add conds": ["empty"]},
    lname.tow_boulders_elevator_r:  {"code": 0x343, "offset": 0x833BAE, "normal item": iname.jewel_l,
                                     "add conds": ["empty"]},
    lname.tow_near_boulders_exit:   {"code": 0x277, "offset": 0x833B4E, "normal item": iname.axe, "add conds": ["sub"]},
    lname.tow_slide_start:          {"code": 0x278, "offset": 0x833C92, "normal item": iname.jewel_s},
    lname.tow_slide_first_u:        {"code": 0x27A, "offset": 0x833B72, "normal item": iname.cross,
                                     "add conds": ["sub"]},
    lname.tow_slide_first_l:        {"code": 0x279, "offset": 0x833C9E, "normal item": iname.chicken},
    lname.tow_slide_second:         {"code": 0x27B, "offset": 0x833B7E, "normal item": iname.jewel_l},

    lname.the_end:        {"event": iname.victory},
}


add_conds = {"carrie":  ("carrie_logic", True, True),
             "liz":     ("lizard_locker_items", True, True),
             "sub":     ("sub_weapon_shuffle", 2, True),
             "3hb":     ("multi_hit_breakables", True, True),
             "empty":   ("empty_breakables", True, True),
             "shop":    ("shopsanity", True, True),
             "crystal": ("draculas_condition", 1, True),
             "boss":    ("draculas_condition", 2, True),
             "renon":   ("renon_fight_condition", 0, False),
             "vincent": ("vincent_fight_condition", 0, False)}


def get_location_info(location: str, info: str) -> Union[int, str, List[str], None]:
    return location_info[location].get(info, None)


def get_location_names_to_ids() -> Dict[str, int]:
    return {name: get_location_info(name, "code")+base_id for name in location_info if get_location_info(name, "code")
            is not None}


def verify_locations(options: CVLoDOptions, locations: List[str]) -> Tuple[Dict[str, Optional[int]], Dict[str, str]]:

    verified_locations = {}
    locked_pairs = {}

    for loc in locations:
        loc_add_conds = get_location_info(loc, "add conds")
        loc_code = get_location_info(loc, "code")

        # Check any options that might be associated with the Location before adding it.
        add_it = True
        if isinstance(loc_add_conds, list):
            for cond in loc_add_conds:
                if not ((getattr(options, add_conds[cond][0]).value == add_conds[cond][1]) == add_conds[cond][2]):
                    add_it = False

        if not add_it:
            continue

        # Add the location to the verified Locations if the above check passes.
        # If we are looking at an event Location, add its associated event Item to the events' dict.
        # Otherwise, add the base_id to the Location's code.
        if loc_code is None:
            locked_pairs[loc] = get_location_info(loc, "event")
        else:
            loc_code += base_id
        verified_locations.update({loc: loc_code})

    return verified_locations, locked_pairs
