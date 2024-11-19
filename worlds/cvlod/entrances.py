from .data import ename, iname, rname
from .stages import get_stage_info
from .options import CVLoDOptions

from typing import Dict, List, Tuple, Union

# # #    KEY    # # #
# "connection" = The name of the Region the Entrance connects into. If it's a Tuple[str, str], we take the stage in
#                active_stage_exits given in the second string and then the stage given in that stage's slot given in
#                the first string, and take the start or end Region of that stage.
# "rule" = What rule should be applied to the Entrance during set_rules, as defined in self.rules in the CV64Rules class
#          definition in rules.py.
# "add conds" = A list of player options conditions that must be satisfied for the Entrance to be added. Can be of
#               varying length depending on how many conditions need to be satisfied. In the add_conds dict's tuples,
#               the first element is the name of the option, the second is the option value to check for, and the third
#               is a boolean for whether we are evaluating for the option value or not.
entrance_info = {
    # Forest of Silence
    ename.fl_to_below: {"destination": rname.fl_middle, "rule": iname.dck_key},
    ename.fl_from_below: {"destination": rname.fl_start, "rule": iname.dck_key},
    ename.fl_sink: {"destination": rname.fl_end},
    ename.fl_end: {"destination": rname.forest_start},

    ename.forest_king_skeleton_1: {"destination": rname.forest_half_1},
    ename.forest_dbridge_gate: {"destination": rname.forest_half_2},
    ename.forest_reverse_leap: {"destination": rname.forest_half_1, "add conds": ["hard"]},
    ename.forest_final_switch: {"destination": rname.forest_end},
    ename.forest_end: {"destination": rname.cw_start},

    # Castle Wall
    ename.cw_portcullis_c: {"destination": rname.cw_exit},
    ename.cw_lt_door: {"destination": rname.cw_ltower, "rule": iname.lt_key},
    ename.cw_end: {"destination": rname.villa_start, "rule": iname.winch},

    ename.villa_warp: {"destination": rname.villa_storeroom, "rule": iname.s1},

    # Villa start
    ename.villa_dog_gates: {"destination": rname.villa_entrance},
    # Villa front entrance
    ename.villa_snipe_dogs: {"destination": rname.villa_start, "add conds": ["carrie", "hard"]},
    ename.villa_fountain_pillar: {"destination": rname.villa_fountain, "rule": iname.diary},
    ename.villa_into_servant_door: {"destination": rname.villa_servants},
    ename.villa_to_rose_garden: {"destination": rname.villa_living, "rule": iname.rg_key},
    # Villa fountain
    ename.villa_fountain_shine: {"destination": rname.villa_fountain_top, "rule": iname.brooch},
    # Villa living area
    ename.villa_from_rose_garden: {"destination": rname.villa_entrance, "rule": iname.rg_key},
    ename.villa_to_storeroom: {"destination": rname.villa_storeroom, "rule": iname.str_key},
    ename.villa_to_archives: {"destination": rname.villa_archives, "rule": iname.arc_key},
    ename.villa_rescue_henry: {"destination": rname.villa_mary_reward, "rule": "Mary"},
    # ename.villa_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    ename.villa_to_main_maze_gate: {"destination": rname.villa_maze_f, "rule": iname.gdn_key},
    # Villa storeroom
    ename.villa_from_storeroom: {"destination": rname.villa_living, "rule": iname.str_key},
    # Villa front maze
    ename.villa_from_main_maze_gate: {"destination": rname.villa_living, "rule": iname.gdn_key},
    ename.villa_copper_door: {"destination": rname.villa_crypt_e, "rule": iname.cu_key, "add conds": ["not hard"]},
    ename.villa_front_rose_doors: {"destination": rname.villa_maze_r, "rule": iname.rg_key},
    # Villa rear maze
    ename.villa_from_rear_maze_gate: {"destination": rname.villa_servants, "rule": iname.gdn_key},
    ename.villa_thorn_fence: {"destination": rname.villa_fgarden, "rule": iname.tho_key},
    ename.villa_copper_skip_e: {"destination": rname.villa_crypt_e, "add conds": ["hard"]},
    ename.villa_copper_skip_i: {"destination": rname.villa_crypt_i, "add conds": ["hard"]},
    ename.villa_rear_rose_doors: {"destination": rname.villa_maze_f, "rule": iname.rg_key},
    # Villa servants' entrance
    ename.villa_to_rear_maze_gate: {"destination": rname.villa_maze_r, "rule": iname.gdn_key},
    ename.villa_out_of_servant_door: {"destination": rname.villa_entrance},
    # Villa crypt exterior
    ename.villa_bridge_door: {"destination": rname.villa_maze_f},
    ename.villa_crest_door: {"destination": rname.villa_crypt_i, "rule": "Crests"},
    ename.villa_end_r: {"destination": rname.tunnel_start},
    ename.villa_end_ca: {"destination": rname.uw_main},
    ename.villa_end_co: {"destination": rname.tow_start},

    # Tunnel
    ename.tunnel_cutscene: {"destination": rname.tunnel_main},
    # ename.tunnel_start_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    ename.tunnel_gondolas: {"destination": rname.tunnel_end},
    ename.tunnel_reverse: {"destination": rname.tunnel_start, "add conds": ["hard"]},
    #ename.tunnel_end_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    #ename.tunnel_end: {"destination": ["next", rname.tunnel]},

    # Underground Waterway
    #ename.uw_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    ename.uw_final_waterfall: {"destination": rname.uw_end},
    # ename.uw_end: {"destination": ["next", rname.underground_waterway]},

    # The Outer Wall
    ename.tow_to_wall_door: {"destination": rname.tow_mid, "rule": iname.wall_key, "add conds": ["not hard"]},
    ename.tow_leap: {"destination": rname.tow_mid, "add conds": ["hard"]},
    ename.tow_from_wall_door: {"destination": rname.tow_start, "rule": iname.wall_key},
    ename.tow_slide: {"destination": rname.tow_end},
    # ename.tow_end: {"destination": ["next", rname.the_outer_wall]},

    # Castle Center
    #ename.cc_tc_door: {"destination": rname.cc_torture_chamber, "rule": iname.chb_key},
    #ename.cc_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    #ename.cc_lower_wall: {"destination": rname.cc_crystal, "rule": "Bomb 2"},
    #ename.cc_upper_wall: {"destination": rname.cc_library, "rule": "Bomb 1"},
    #ename.cc_elevator: {"destination": rname.cc_elev_top},
    #ename.cc_exit_r: {"destination": ["next", rname.castle_center]},
    #ename.cc_exit_c: {"destination": ["alt", rname.castle_center]},
    # Duel Tower
    #ename.dt_start: {"destination": ["prev", rname.duel_tower]},
    #ename.dt_end: {"destination": ["next", rname.duel_tower]},
    # Tower of Execution
    #ename.toe_start: {"destination": ["prev", rname.tower_of_execution]},
    #ename.toe_end: {"destination": ["next", rname.tower_of_execution]},
    # Tower of Science
    #ename.tosci_start: {"destination": ["prev", rname.tower_of_science]},
    #ename.tosci_key1_door: {"destination": rname.tosci_three_doors, "rule": iname.science_key1},
    #ename.tosci_to_key2_door: {"destination": rname.tosci_conveyors, "rule": iname.science_key2},
    #ename.tosci_from_key2_door: {"destination": rname.tosci_start, "rule": iname.science_key2},
    #ename.tosci_key3_door: {"destination": rname.tosci_key3, "rule": iname.science_key3},
    #ename.tosci_end: {"destination": ["next", rname.tower_of_science]},
    # Tower of Sorcery
    #ename.tosor_start: {"destination": ["prev", rname.tower_of_sorcery]},
    #ename.tosor_end: {"destination": ["next", rname.tower_of_sorcery]},
    # Room of Clocks
    #ename.roc_gate: {"destination": ["next", rname.room_of_clocks]},
    # Clock Tower
    #ename.ct_to_door1: {"destination": rname.ct_middle, "rule": iname.clocktower_key1},
    #ename.ct_from_door1: {"destination": rname.ct_start, "rule": iname.clocktower_key1},
    #ename.ct_to_door2: {"destination": rname.ct_end, "rule": iname.clocktower_key2},
    #ename.ct_from_door2: {"destination": rname.ct_middle, "rule": iname.clocktower_key2},
    #ename.ct_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    #ename.ct_door_3: {"destination": ["next", rname.clock_tower], "rule": iname.clocktower_key3},
    # Castle Keep
    #ename.ck_slope_jump: {"destination": rname.roc_main, "add conds": ["hard"]},
}

add_conds = {"carrie": ("carrie_logic", True, True),
             "hard": ("hard_logic", True, True),
             "not hard": ("hard_logic", False, True),
             "shopsanity": ("shopsanity", True, True)}

stage_connection_types = {"prev": "end region",
                          "next": "start region",
                          "alt": "start region"}


def get_entrance_info(entrance: str, info: str) -> Union[str, Tuple[str, str], List[str], None]:
    return entrance_info[entrance].get(info, None)


def get_warp_entrances(active_warp_list: List[str]) -> Dict[str, str]:
    # Create the starting stage Entrance.
    warp_entrances = {get_stage_info(active_warp_list[0], "start region"): "Start stage"}

    # Create the warp Entrances.
    for i in range(1, len(active_warp_list)):
        mid_stage_region = get_stage_info(active_warp_list[i], "mid region")
        warp_entrances.update({mid_stage_region: f"Warp {i}"})

    return warp_entrances


def verify_entrances(options: CVLoDOptions, entrances: List[str],
                     active_stage_exits: Dict[str, Dict[str, Union[str, int, None]]]) -> Dict[str, str]:
    verified_entrances = {}

    for ent_name in entrances:
        ent_add_conds = get_entrance_info(ent_name, "add conds")

        # Check any options that might be associated with the Entrance before adding it.
        add_it = True
        if ent_add_conds is not None:
            for cond in ent_add_conds:
                if not ((getattr(options, add_conds[cond][0]).value == add_conds[cond][1]) == add_conds[cond][2]):
                    add_it = False

        if not add_it:
            continue

        # Add the Entrance to the verified Entrances if the above check passes.
        destination = get_entrance_info(ent_name, "destination")

        # If the Entrance is a connection to a different stage, get the corresponding other stage Region.
        if isinstance(destination, tuple):
            connecting_stage = active_stage_exits[destination[1]][destination[0]]
            # Stages that lead backwards at the beginning of the line will appear leading to "Menu".
            if connecting_stage in ["Menu", None]:
                continue
            destination = get_stage_info(connecting_stage, stage_connection_types[destination[0]])
        verified_entrances.update({destination: ent_name})

    return verified_entrances
