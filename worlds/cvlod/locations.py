from BaseClasses import Location
from .data import lname, iname
from .options import CVLoDOptions

from typing import Dict

base_id = 0xC10D_000


class CVLoDLocation(Location):
    game: str = "Castlevania Legacy of Darkness"


location_info = {
    # Castle Wall
    lname.cwr_bottom:        {"code": 0x2D,  "offset": 0x77BD93, "normal item": iname.s_card},
    lname.cwr_top:           {"code": 0x30,  "offset": 0x77BDC3, "normal item": iname.chicken},
    lname.cw_dragon_sw:      {"code": 0x49,  "offset": 0x78163B, "normal item": iname.chicken},
    # lname.cw_boss:           {"event": iname.trophy, "add conds": ["boss"]},
    lname.cw_save_slab1:     {"code": 0x2B8, "offset": 0x7816B1, "normal item": iname.jewel_l, "add conds": ["3hb"]},
    lname.cw_save_slab2:     {"code": 0x2B9, "offset": 0x7816B3, "normal item": iname.jewel_l, "add conds": ["3hb"]},
    lname.cw_save_slab3:     {"code": 0x2BA, "offset": 0x7816B5, "normal item": iname.jewel_l, "add conds": ["3hb"]},
    lname.cw_save_slab4:     {"code": 0x2BB, "offset": 0x7816B7, "normal item": iname.jewel_l, "add conds": ["3hb"]},
    lname.cw_save_slab5:     {"code": 0x2BC, "offset": 0x7816B9, "normal item": iname.jewel_l, "add conds": ["3hb"]},
    lname.cw_rrampart:       {"code": 0x46,  "offset": 0x781647, "normal item": iname.gold_300},
    lname.cw_lrampart:       {"code": 0x47,  "offset": 0x781617, "normal item": iname.m_card},
    lname.cw_pillar:         {"code": 0x44,  "offset": 0x782755, "normal item": iname.powerup},
    lname.cw_shelf:          {"code": 0x42,  "offset": 0x782735, "normal item": iname.winch},
    lname.cw_shelf_torch:    {"code": 0x4C,  "offset": 0x78165F, "normal item": iname.cross, "add conds": ["sub"]},
    lname.cw_ground_left:    {"code": 0x14B, "offset": 0x781623, "normal item": iname.purify},
    lname.cw_ground_middle:  {"code": 0x27D, "offset": 0x7815FF, "normal item": iname.lt_key},
    lname.cw_ground_right:   {"code": 0x4D,  "offset": 0x781683, "normal item": iname.axe, "add conds": ["sub"]},
    lname.cwl_bottom:        {"code": 0x2E,  "offset": 0x77BD9F, "normal item": iname.m_card},
    lname.cwl_bridge:        {"code": 0x2F,  "offset": 0x77BDAB, "normal item": iname.beef},
    lname.cw_drac_sw:        {"code": 0x4E,  "offset": 0x78169B, "normal item": iname.chicken},
    lname.cw_drac_slab1:     {"code": 0x2BD, "offset": 0x7816D5, "normal item": iname.gold_300, "add conds": ["3hb"]},
    lname.cw_drac_slab2:     {"code": 0x2BE, "offset": 0x7816D7, "normal item": iname.gold_300, "add conds": ["3hb"]},
    lname.cw_drac_slab3:     {"code": 0x2BF, "offset": 0x7816D9, "normal item": iname.gold_300, "add conds": ["3hb"]},
    lname.cw_drac_slab4:     {"code": 0x2C0, "offset": 0x7816DB, "normal item": iname.gold_300, "add conds": ["3hb"]},
    lname.cw_drac_slab5:     {"code": 0x2C1, "offset": 0x7816DD, "normal item": iname.gold_300, "add conds": ["3hb"]},

    # Villa
    lname.villafy_outer_gate_l:         {"code": 0x62,  "offset": 0x78468B, "normal item": iname.purify},
    lname.villafy_outer_gate_r:         {"code": 0x63,  "offset": 0x784697, "normal item": iname.jewel_l},
    lname.villafy_inner_gate:           {"code": 0x60,  "offset": 0x785B8D, "normal item": iname.beef},
    lname.villafy_gate_marker:          {"code": 0x65,  "offset": 0x7846AF, "normal item": iname.powerup},
    lname.villafy_villa_marker:         {"code": 0x64,  "offset": 0x7846A3, "normal item": iname.beef},
    lname.villafy_fountain_fl:          {"code": 0x5F,  "offset": 0x785B2D, "normal item": iname.gold_500},
    lname.villafy_fountain_fr:          {"code": 0x61,  "offset": 0x785B6D, "normal item": iname.purify},
    lname.villafy_fountain_ml:          {"code": 0x5E,  "offset": 0x785B0D, "normal item": iname.s_card},
    lname.villafy_fountain_mr:          {"code": 0x5A,  "offset": 0x785A6D, "normal item": iname.m_card},
    lname.villafy_fountain_rl:          {"code": 0x5C,  "offset": 0x785ACD, "normal item": iname.beef},
    lname.villafy_fountain_rr:          {"code": 0x5B,  "offset": 0x785A8D, "normal item": iname.gold_500},
    lname.villafy_fountain_shine:       {"code": 0x68,  "offset": 0xFFC6F1, "normal item": iname.crest_a,
                                         "type": "npc"},
    lname.villafo_front_l:              {"code": 0x72,  "offset": 0x787F23, "normal item": iname.jewel_s},
    lname.villafo_front_r:              {"code": 0x73,  "offset": 0x787F2F, "normal item": iname.gold_300},
    lname.villafo_mid_l:                {"code": 0x71,  "offset": 0x787F17, "normal item": iname.gold_300},
    lname.villafo_mid_r:                {"code": 0x70,  "offset": 0x787F0B, "normal item": iname.jewel_s},
    lname.villafo_rear_l:               {"code": 0x6E,  "offset": 0x787EF3, "normal item": iname.jewel_s},
    lname.villafo_rear_r:               {"code": 0x6F,  "offset": 0x787EFF, "normal item": iname.jewel_s},
    lname.villafo_pot_l:                {"code": 0x6D,  "offset": 0x787E6F, "normal item": iname.arc_key},
    lname.villafo_pot_r:                {"code": 0x6C,  "offset": 0x787E63, "normal item": iname.jewel_l},
    lname.villafo_sofa:                 {"code": 0x75,  "offset": 0x7892DD, "normal item": iname.purify, "type": "inv"},
    lname.villafo_chandelier1:          {"code": 0x302, "offset": 0x787F51, "normal item": iname.gold_500,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier2:          {"code": 0x303, "offset": 0x787F53, "normal item": iname.jewel_l,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier3:          {"code": 0x304, "offset": 0x787F55, "normal item": iname.purify,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier4:          {"code": 0x305, "offset": 0x787F57, "normal item": iname.ampoule,
                                         "add conds": ["3hb"]},
    lname.villafo_chandelier5:          {"code": 0x306, "offset": 0x787F59, "normal item": iname.chicken,
                                         "add conds": ["3hb"]},
    lname.villafo_6am_roses:            {"code": 0x78,  "offset": 0xFFC6F3, "normal item": iname.tho_key,
                                         "type": "npc"},
    lname.villala_hallway_stairs:       {"code": 0x80,  "offset": 0x78DDF7, "normal item": iname.jewel_l},
    lname.villala_hallway_l:            {"code": 0x82,  "offset": 0x78DE0F, "normal item": iname.knife,
                                         "add conds": ["sub"]},
    lname.villala_hallway_r:            {"code": 0x81,  "offset": 0x78DE03, "normal item": iname.axe,
                                         "add conds": ["sub"]},
    lname.villala_vincent:              {"code": 0x27F, "offset": 0xFFC6F5, "normal item": iname.jewel_l,
                                         "type": "npc"},
    lname.villala_slivingroom_table_l:  {"code": 0x283, "offset": 0x791C6D, "normal item": iname.gold_100},
    lname.villala_slivingroom_table_r:  {"code": 0x8B,  "offset": 0x791CAD, "normal item": iname.gold_300,
                                         "type": "inv"},
    lname.villala_mary:                 {"code": 0x86, "offset": 0xFFC6F7, "normal item": iname.cu_key,
                                         "type": "npc"},
    lname.villala_slivingroom_mirror:   {"code": 0x83,  "offset": 0x78DE1B, "normal item": iname.cross,
                                         "add conds": ["sub"]},
    lname.villala_diningroom_roses:     {"code": 0x90,  "offset": 0x79184D, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_llivingroom_pot_r:    {"code": 0x27E, "offset": 0x78DDD3, "normal item": iname.str_key},
    lname.villala_llivingroom_pot_l:    {"code": 0x7E,  "offset": 0x78DDDF, "normal item": iname.chicken},
    lname.villala_llivingroom_painting: {"code": 0x8E,  "offset": 0x790FAD, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_llivingroom_light:    {"code": 0x7F,  "offset": 0x78DDEB, "normal item": iname.purify},
    lname.villala_llivingroom_lion:     {"code": 0x8D,  "offset": 0x790F6D, "normal item": iname.chicken,
                                         "type": "inv"},
    lname.villala_exit_knight:          {"code": 0x8F,  "offset": 0x7909AD, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_storeroom_l:          {"code": 0x2B3, "offset": 0x792B8D, "normal item": iname.beef},
    lname.villala_storeroom_r:          {"code": 0x2B2, "offset": 0x792B6D, "normal item": iname.chicken},
    lname.villala_storeroom_s:          {"code": 0x8C,  "offset": 0x792B2D, "normal item": iname.purify,
                                         "type": "inv"},
    lname.villala_archives_table:       {"code": 0x84,  "offset": 0x792A2D, "normal item": iname.diary,
                                         "type": "inv"},
    lname.villala_archives_rear:        {"code": 0x85,  "offset": 0x792A4D, "normal item": iname.gdn_key},
    lname.villam_malus_torch:           {"code": 0xA3,  "offset": 0x796D9F, "normal item": iname.jewel_s,
                                         "countdown": 13},
    lname.villam_malus_bush:            {"code": 0xAA, "offset": 0x799041, "normal item": iname.chicken,
                                         "type": "inv", "countdown": 13},
    lname.villam_fplatform:             {"code": 0xA7,  "offset": 0x796DAB, "normal item": iname.axe,
                                         "add conds": ["sub"], "countdown": 13},
    lname.villam_frankieturf_l:         {"code": 0x9F,  "offset": 0x796E53, "normal item": iname.gold_300,
                                         "countdown": 13},
    lname.villam_frankieturf_r:         {"code": 0xA8,  "offset": 0x796D6F, "normal item": iname.holy,
                                         "add conds": ["sub"], "countdown": 13},
    lname.villam_frankieturf_ru:        {"code": 0xAC,  "offset": 0x796D87, "normal item": iname.jewel_s,
                                         "countdown": 13},
    lname.villam_hole_de:               {"code": 0x281, "offset": 0x796CBB, "normal item": iname.rg_key,
                                         "countdown": 13},
    lname.villam_fgarden_f:             {"code": 0xA5,  "offset": 0x796E23, "normal item": iname.jewel_s,
                                         "countdown": 13},
    lname.villam_fgarden_mf:            {"code": 0xA2,  "offset": 0x796E17, "normal item": iname.jewel_s,
                                         "countdown": 13},
    lname.villam_fgarden_mr:            {"code": 0xA4,  "offset": 0x796D3F, "normal item": iname.brooch,
                                         "countdown": 13},
    lname.villam_fgarden_r:             {"code": 0xA6,  "offset": 0x796D57, "normal item": iname.jewel_l,
                                         "countdown": 13},
    lname.villam_rplatform_f:           {"code": 0xA9,  "offset": 0x796D7B, "normal item": iname.axe,
                                         "add conds": ["sub"], "countdown": 13},
    lname.villam_rplatform_r:           {"code": 0x9C,  "offset": 0x796CD3, "normal item": iname.crest_b,
                                         "countdown": 13},
    lname.villam_rplatform_de:          {"code": 0xA0,  "offset": 0x796DE7, "normal item": iname.gold_300,
                                         "countdown": 13},
    lname.villam_exit_de:               {"code": 0xA1,  "offset": 0x796E3B, "normal item": iname.gold_300,
                                         "countdown": 13},
    lname.villam_serv_path_sl:          {"code": 0xAB,  "offset": 0x796E6B, "normal item": iname.purify,
                                         "countdown": 13},
    lname.villam_serv_path_sr:          {"code": 0x280, "offset": 0x796CDF, "normal item": iname.gold_100,
                                         "countdown": 13},
    lname.villam_serv_path_l:           {"code": 0x2B1, "offset": 0x796E77, "normal item": iname.ampoule,
                                         "countdown": 13},
    lname.villafo_serv_ent:             {"code": 0x74,  "offset": 0x787EC3, "normal item": iname.chicken},
    lname.villam_crypt_ent:             {"code": 0x9E,  "offset": 0x796CF7, "normal item": iname.purify,
                                         "countdown": 13},
    lname.villam_crypt_upstream:        {"code": 0x9D,  "offset": 0x796CEB, "normal item": iname.beef,
                                         "countdown": 13},
    lname.villac_ent_l:                 {"code": 0x192, "offset": 0x7D63DB, "normal item": iname.jewel_s,
                                         "countdown": 13},
    lname.villac_ent_r:                 {"code": 0x193, "offset": 0x7D63E7, "normal item": iname.gold_300,
                                         "countdown": 13},
    lname.villac_wall_l:                {"code": 0x196, "offset": 0x7D63C3, "normal item": iname.cross,
                                         "add conds": ["sub"], "countdown": 13},
    lname.villac_wall_r:                {"code": 0x197, "offset": 0x7D63CF, "normal item": iname.jewel_l,
                                         "countdown": 13},
    lname.villac_coffin_l:              {"code": 0x194, "offset": 0x7D63FF, "normal item": iname.jewel_s,
                                         "countdown": 13},
    lname.villac_coffin_r:              {"code": 0x195, "offset": 0x7D640B, "normal item": iname.jewel_s,
                                         "countdown": 13},
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


def get_location_info(location: str, info: str):
    if info in location_info[location]:
        return location_info[location][info]
    return None


def get_location_names_to_ids() -> Dict[str, int]:
    return {name: get_location_info(name, "code")+base_id for name in location_info if get_location_info(name, "code")
            is not None}


def verify_locations(options: CVLoDOptions, locations: list) -> Dict[Location, any]:

    verified_locations = {}

    for loc in locations:
        loc_add_conds = get_location_info(loc, "add conds")
        loc_code = get_location_info(loc, "code")

        # Check any options that might be associated with the Location before adding it.
        add_it = True
        if loc_add_conds is not None:
            for cond in loc_add_conds:
                if not ((getattr(options, add_conds[cond][0]).value == add_conds[cond][1]) == add_conds[cond][2]):
                    add_it = False

        if not add_it:
            continue

        # Add the location to the verified locations if the above check passes.
        if loc_code is not None:
            loc_code += base_id
        verified_locations.update({loc: loc_code})

    return verified_locations
