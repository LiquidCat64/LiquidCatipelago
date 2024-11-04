from BaseClasses import Location
from .data import lname, iname
from .options import CVLoDOptions, SubWeaponShuffle, DraculasCondition, RenonFightCondition, VincentFightCondition

from typing import Dict, Optional, Union, List, Tuple

base_id = 0xC10D_000


class CVLoDLocation(Location):
    game: str = "Castlevania - Legacy of Darkness"


# # #    KEY    # # #
# "code" = The unique part of the Location's AP code attribute, as well as the in-game bitflag index starting from
#          0x80389BE4 that indicates the Location has been checked. Add this + base_id to get the actual AP code.
# "offset" = The offset in the ROM to overwrite to change the Item on that Location.
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
    # Castle Wall
    lname.cwr_bottom:        {"code": 0x2D,  "offset": 0x77BD92, "normal item": iname.s_card, "countdown": 2},
    lname.cwr_top:           {"code": 0x30,  "offset": 0x77BDC2, "normal item": iname.chicken, "countdown": 2},
    lname.cw_dragon_sw:      {"code": 0x49,  "offset": 0x78163A, "normal item": iname.chicken, "countdown": 2},
    # lname.cw_boss:           {"event": iname.trophy, "add conds": ["boss"]},
    lname.cw_save_slab1:     {"code": 0x2B8, "offset": 0x7816B0, "normal item": iname.jewel_l,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_save_slab2:     {"code": 0x2B9, "offset": 0x7816B2, "normal item": iname.jewel_l,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_save_slab3:     {"code": 0x2BA, "offset": 0x7816B4, "normal item": iname.jewel_l,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_save_slab4:     {"code": 0x2BB, "offset": 0x7816B6, "normal item": iname.jewel_l,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_save_slab5:     {"code": 0x2BC, "offset": 0x7816B8, "normal item": iname.jewel_l,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_rrampart:       {"code": 0x46,  "offset": 0x781646, "normal item": iname.gold_300,  "countdown": 2},
    lname.cw_lrampart:       {"code": 0x47,  "offset": 0x781616, "normal item": iname.m_card,  "countdown": 2},
    lname.cw_pillar:         {"code": 0x44,  "offset": 0x782754, "normal item": iname.powerup,  "countdown": 2},
    lname.cw_shelf:          {"code": 0x42,  "offset": 0x782734, "normal item": iname.winch,  "countdown": 2},
    lname.cw_shelf_torch:    {"code": 0x4C,  "offset": 0x78165E, "normal item": iname.cross,  "countdown": 2,
                              "add conds": ["sub"]},
    lname.cw_ground_left:    {"code": 0x48, "offset": 0x781622, "normal item": iname.purify,  "countdown": 2},
    lname.cw_ground_middle:  {"code": 0x27D, "offset": 0x7815FE, "normal item": iname.lt_key,  "countdown": 2},
    lname.cw_ground_right:   {"code": 0x4D,  "offset": 0x781682, "normal item": iname.axe,  "countdown": 2,
                              "add conds": ["sub"]},
    lname.cwl_bottom:        {"code": 0x2E,  "offset": 0x77BD9E, "normal item": iname.m_card,  "countdown": 2},
    lname.cwl_bridge:        {"code": 0x2F,  "offset": 0x77BDAA, "normal item": iname.beef,  "countdown": 2},
    lname.cw_drac_sw:        {"code": 0x4E,  "offset": 0x78169A, "normal item": iname.chicken,  "countdown": 2},
    lname.cw_drac_slab1:     {"code": 0x2BD, "offset": 0x7816D4, "normal item": iname.gold_300,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_drac_slab2:     {"code": 0x2BE, "offset": 0x7816D6, "normal item": iname.gold_300,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_drac_slab3:     {"code": 0x2BF, "offset": 0x7816D8, "normal item": iname.gold_300,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_drac_slab4:     {"code": 0x2C0, "offset": 0x7816DA, "normal item": iname.gold_300,  "countdown": 2,
                              "add conds": ["3hb"]},
    lname.cw_drac_slab5:     {"code": 0x2C1, "offset": 0x7816DC, "normal item": iname.gold_300,  "countdown": 2,
                              "add conds": ["3hb"]},

    # Villa
    lname.villafy_outer_gate_l:         {"code": 0x62,  "offset": 0x78468A, "normal item": iname.purify,
                                         "countdown": 3},
    lname.villafy_outer_gate_r:         {"code": 0x63,  "offset": 0x784696, "normal item": iname.jewel_l,
                                         "countdown": 3},
    lname.villafy_inner_gate:           {"code": 0x60,  "offset": 0x785B8C, "normal item": iname.beef, "countdown": 3},
    lname.villafy_gate_marker:          {"code": 0x65,  "offset": 0x7846AE, "normal item": iname.powerup,
                                         "countdown": 3},
    lname.villafy_villa_marker:         {"code": 0x64,  "offset": 0x7846A2, "normal item": iname.beef, "countdown": 3},
    lname.villafy_fountain_fl:          {"code": 0x5F,  "offset": 0x785B2C, "normal item": iname.gold_500,
                                         "countdown": 3},
    lname.villafy_fountain_fr:          {"code": 0x61,  "offset": 0x785B6C, "normal item": iname.purify,
                                         "countdown": 3},
    lname.villafy_fountain_ml:          {"code": 0x5E,  "offset": 0x785B0C, "normal item": iname.s_card,
                                         "countdown": 3},
    lname.villafy_fountain_mr:          {"code": 0x5A,  "offset": 0x785A6C, "normal item": iname.m_card,
                                         "countdown": 3},
    lname.villafy_fountain_rl:          {"code": 0x5C,  "offset": 0x785ACC, "normal item": iname.beef, "countdown": 3},
    lname.villafy_fountain_rr:          {"code": 0x5B,  "offset": 0x785A8C, "normal item": iname.gold_500,
                                         "countdown": 3},
    lname.villafy_fountain_shine:       {"code": 0x68,  "offset": 0xFFC6F0, "normal item": iname.crest_a,
                                         "countdown": 3,
                                         "type": "npc"},
    lname.villafo_front_l:              {"code": 0x72,  "offset": 0x787F22, "normal item": iname.jewel_s,
                                         "countdown": 3},
    lname.villafo_front_r:              {"code": 0x73,  "offset": 0x787F2E, "normal item": iname.gold_300,
                                         "countdown": 3},
    lname.villafo_mid_l:                {"code": 0x71,  "offset": 0x787F16, "normal item": iname.gold_300,
                                         "countdown": 3},
    lname.villafo_mid_r:                {"code": 0x70,  "offset": 0x787F0A, "normal item": iname.jewel_s,
                                         "countdown": 3},
    lname.villafo_rear_l:               {"code": 0x6E,  "offset": 0x787EF2, "normal item": iname.jewel_s,
                                         "countdown": 3},
    lname.villafo_rear_r:               {"code": 0x6F,  "offset": 0x787EFE, "normal item": iname.jewel_s,
                                         "countdown": 3},
    lname.villafo_pot_l:                {"code": 0x6D,  "offset": 0x787E6E, "normal item": iname.arc_key,
                                         "countdown": 3},
    lname.villafo_pot_r:                {"code": 0x6C,  "offset": 0x787E62, "normal item": iname.jewel_l,
                                         "countdown": 3},
    lname.villafo_sofa:                 {"code": 0x75,  "offset": 0x7892DC, "normal item": iname.purify,
                                         "countdown": 3, "type": "inv"},
    lname.villafo_chandelier1:          {"code": 0x302, "offset": 0x787F50, "normal item": iname.gold_500,
                                         "countdown": 3, "add conds": ["3hb"]},
    lname.villafo_chandelier2:          {"code": 0x303, "offset": 0x787F52, "normal item": iname.jewel_l,
                                         "countdown": 3, "add conds": ["3hb"]},
    lname.villafo_chandelier3:          {"code": 0x304, "offset": 0x787F54, "normal item": iname.purify,
                                         "countdown": 3, "add conds": ["3hb"]},
    lname.villafo_chandelier4:          {"code": 0x305, "offset": 0x787F56, "normal item": iname.ampoule,
                                         "countdown": 3, "add conds": ["3hb"]},
    lname.villafo_chandelier5:          {"code": 0x306, "offset": 0x787F58, "normal item": iname.chicken,
                                         "countdown": 3, "add conds": ["3hb"]},
    lname.villafo_6am_roses:            {"code": 0x78,  "offset": 0xFFC6F2, "normal item": iname.tho_key,
                                         "countdown": 3, "type": "npc"},
    lname.villala_hallway_stairs:       {"code": 0x80,  "offset": 0x78DDF6, "normal item": iname.jewel_l,
                                         "countdown": 3},
    lname.villala_hallway_l:            {"code": 0x82,  "offset": 0x78DE0E, "normal item": iname.knife,
                                         "countdown": 3, "add conds": ["sub"]},
    lname.villala_hallway_r:            {"code": 0x81,  "offset": 0x78DE02, "normal item": iname.axe,
                                         "countdown": 3, "add conds": ["sub"]},
    lname.villala_vincent:              {"code": 0x27F, "offset": 0xFFC6F4, "normal item": iname.jewel_l,
                                         "countdown": 3, "type": "npc"},
    lname.villala_slivingroom_table_l:  {"code": 0x283, "offset": 0x791C6C, "normal item": iname.gold_100,
                                         "countdown": 3},
    lname.villala_slivingroom_table_r:  {"code": 0x8B,  "offset": 0x791CAC, "normal item": iname.gold_300,
                                         "countdown": 3, "type": "inv"},
    lname.villala_mary:                 {"code": 0x86, "offset": 0xFFC6F6, "normal item": iname.cu_key,
                                         "countdown": 3, "type": "npc"},
    lname.villala_slivingroom_mirror:   {"code": 0x83,  "offset": 0x78DE1A, "normal item": iname.cross,
                                         "countdown": 3, "add conds": ["sub"]},
    lname.villala_diningroom_roses:     {"code": 0x90,  "offset": 0x79184C, "normal item": iname.purify,
                                         "countdown": 3, "type": "inv"},
    lname.villala_llivingroom_pot_r:    {"code": 0x27E, "offset": 0x78DDD2, "normal item": iname.str_key,
                                         "countdown": 3},
    lname.villala_llivingroom_pot_l:    {"code": 0x7E,  "offset": 0x78DDDE, "normal item": iname.chicken,
                                         "countdown": 3},
    lname.villala_llivingroom_painting: {"code": 0x8E,  "offset": 0x790FAC, "normal item": iname.purify,
                                         "countdown": 3, "type": "inv"},
    lname.villala_llivingroom_light:    {"code": 0x7F,  "offset": 0x78DDEA, "normal item": iname.purify,
                                         "countdown": 3},
    lname.villala_llivingroom_lion:     {"code": 0x8D,  "offset": 0x790F6C, "normal item": iname.chicken,
                                         "countdown": 3, "type": "inv"},
    lname.villala_exit_knight:          {"code": 0x8F,  "offset": 0x7909AC, "normal item": iname.purify,
                                         "countdown": 3, "type": "inv"},
    lname.villala_storeroom_l:          {"code": 0x2B3, "offset": 0x792B8C, "normal item": iname.beef,
                                         "countdown": 3},
    lname.villala_storeroom_r:          {"code": 0x2B2, "offset": 0x792B6C, "normal item": iname.chicken,
                                         "countdown": 3},
    lname.villala_storeroom_s:          {"code": 0x8C,  "offset": 0x792B2C, "normal item": iname.purify,
                                         "countdown": 3, "type": "inv"},
    lname.villala_archives_table:       {"code": 0x84,  "offset": 0x792A2C, "normal item": iname.diary,
                                         "countdown": 3, "type": "inv"},
    lname.villala_archives_rear:        {"code": 0x85,  "offset": 0x792A4C, "normal item": iname.gdn_key,
                                         "countdown": 3},
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
    lname.villafo_serv_ent:             {"code": 0x74,  "offset": 0x787EC2, "normal item": iname.chicken,
                                         "countdown": 3},
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
