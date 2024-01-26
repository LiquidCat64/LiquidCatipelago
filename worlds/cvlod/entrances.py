from .data import ename, iname, rname, lname
from .stages import get_stage_info
from .options import CVLoDOptions

entrance_info = {
    # Forest of Silence
    #ename.forest_dbridge_gate: {"destination": rname.forest_mid},
    #ename.forest_werewolf_gate: {"destination": rname.forest_end},
    #ename.forest_end: {"destination": ["next", rname.forest_of_silence]},

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
    ename.villa_copper_door: {"destination": rname.villa_crypt_e, "rule": iname.cu_key},
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
    ename.villa_crest_door: {"destination": rname.villa_crypt_i, "rule": "crests"},
    #ename.villa_end_r: {"destination": ["next", rname.villa]},
    #ename.villa_end_c: {"destination": ["alt", rname.villa]},

    # Tunnel
    #ename.tunnel_start_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    #ename.tunnel_gondolas: {"destination": rname.tunnel_end},
    #ename.tunnel_end_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    #ename.tunnel_end: {"destination": ["next", rname.tunnel]},
    # Underground Waterway
    #ename.uw_renon: {"destination": rname.renon, "add conds": ["shopsanity"]},
    #ename.uw_final_waterfall: {"destination": rname.uw_end},
    #ename.uw_waterfall_skip: {"destination": rname.uw_main, "add conds": ["hard"]},
    #ename.uw_end: {"destination": ["next", rname.underground_waterway]},
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


def lookup_rule(rule: str, player: int):
    rules = {
        iname.s1: lambda state: state.has(iname.s1, player),
        iname.lt_key: lambda state: state.has(iname.lt_key, player),
        iname.winch: lambda state: state.has(iname.winch, player),
        iname.diary: lambda state: state.has(iname.diary, player),
        iname.brooch: lambda state: state.has(iname.brooch, player),
        iname.rg_key: lambda state: state.has(iname.rg_key, player),
        iname.str_key: lambda state: state.has(iname.str_key, player),
        iname.arc_key: lambda state: state.has(iname.arc_key, player),
        iname.gdn_key: lambda state: state.has(iname.gdn_key, player),
        iname.tho_key: lambda state: state.has(iname.tho_key, player),
        iname.cu_key: lambda state: state.has(iname.cu_key, player),
        "Mary": lambda state: state.has(iname.rg_key, player) and state.can_reach(lname.villam_malus_torch,
                                                                                  "Location", player),
        "crests": lambda state: state.has(iname.crest_a, player) and state.has(iname.crest_b, player),
        iname.chb_key: lambda state: state.has(iname.chb_key, player),
        "Bomb 1": lambda state: state.has(iname.nitro, player) and state.has(iname.mandrag, player),
        "Bomb 2": lambda state: state.has(iname.nitro, player, 2) and state.has(iname.mandrag, player, 2),
    }
    return rules[rule]


def get_entrance_info(entrance: str, info: str):
    if info in entrance_info[entrance]:
        return entrance_info[entrance][info]
    return None


def get_warp_entrances(options: CVLoDOptions, active_warp_list: list, player: int):
    warp_entrances = {get_stage_info(active_warp_list[0], "start region"): "Start stage"}
    warp_rules = {}

    # Create the warp entrances and Special1 rules.
    for i in range(1, len(active_warp_list)):
        mid_stage_region = get_stage_info(active_warp_list[i], "mid region")
        warp_entrances.update({mid_stage_region: f"Warp {i}"})
        warp_rules.update({mid_stage_region: lambda state, needed=i: state.has(iname.s1, player,
                                                                               options.special1s_per_warp * needed)})

    return warp_entrances, warp_rules


def get_drac_rule(options: CVLoDOptions, player: int, required_s2s: int):
    drac_object_name = None
    if options.draculas_condition.value == options.draculas_condition.option_crystal:
        drac_object_name = "Crystal"
    elif options.draculas_condition.value == options.draculas_condition.option_bosses:
        drac_object_name = "Trophy"
    elif options.draculas_condition.value == options.draculas_condition.option_specials:
        drac_object_name = "Special2"

    if drac_object_name is not None:
        return {rname.ck_drac_chamber: lambda state: state.has(drac_object_name, player, required_s2s)}
    else:
        return None


def verify_entrances(options: CVLoDOptions, entrances: list, active_stage_exits: dict, player: int):
    verified_entrances = {}
    verified_rules = {}

    for ent in entrances:
        ent_add_conds = get_entrance_info(ent, "add conds")

        # Check any options that might be associated with the Location before adding it.
        add_it = True
        if ent_add_conds is not None:
            for cond in ent_add_conds:
                if not ((getattr(options, add_conds[cond][0]).value == add_conds[cond][1]) == add_conds[cond][2]):
                    add_it = False

        if not add_it:
            continue

        # Add the entrance to the verified entrances if the above check passes.
        # If the entrance is a stage connection, get the corresponding other stage region.
        connection = get_entrance_info(ent, "destination")

        if type(connection) == list:
            connecting_stage = active_stage_exits[connection[1]][connection[0]]
            if connecting_stage in ["Menu", None]:
                continue
            connection = get_stage_info(connecting_stage, stage_connection_types[connection[0]])
        verified_entrances.update({connection: ent})

        # If the entrance has item rules, add them to the rules' dict.
        rule = get_entrance_info(ent, "rule")
        if rule is not None:
            verified_rules.update({connection: lookup_rule(rule, player)})

    return verified_entrances, verified_rules
