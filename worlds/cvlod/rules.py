from typing import Dict, TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import allow_self_locking_items, CollectionRule
from .options import DraculasCondition
from .entrances import get_entrance_info
from .data import iname, rname, lname

if TYPE_CHECKING:
    from . import CVLoDWorld


class CVLoDRules:
    player: int
    world: "CVLoDWorld"
    rules: Dict[str, CollectionRule]
    s1s_per_warp: int
    required_s2s: int
    drac_condition: int

    def __init__(self, world: "CVLoDWorld") -> None:
        self.player = world.player
        self.world = world
        self.s1s_per_warp = world.s1s_per_warp
        self.required_s2s = world.required_s2s
        self.drac_condition = world.drac_condition

        self.rules = {
            iname.s1: lambda state: state.has(iname.s1, self.player),
            iname.dck_key: lambda state: state.has(iname.dck_key, self.player),
            iname.lt_key: lambda state: state.has(iname.lt_key, self.player),
            iname.winch: lambda state: state.has(iname.winch, self.player),
            iname.rg_key: lambda state: state.has(iname.rg_key, self.player),
            iname.str_key: lambda state: state.has(iname.str_key, self.player),
            iname.arc_key: lambda state: state.has(iname.arc_key, self.player),
            iname.gdn_key: lambda state: state.has(iname.gdn_key, self.player),
            iname.cu_key: lambda state: state.has(iname.cu_key, self.player),
            iname.tho_key: lambda state: state.has(iname.tho_key, self.player),
            iname.diary: lambda state: state.has(iname.diary, self.player),
            iname.brooch: lambda state: state.has(iname.brooch, self.player),
            "Mary": lambda state: state.has(iname.rg_key, self.player) and state.can_reach(lname.villam_malus_torch,
                                                                                           "Location", self.player),
            "Crests": lambda state: state.has_all({iname.crest_a, iname.crest_b}, self.player),
            iname.wall_key: lambda state: state.has(iname.wall_key, self.player),
            iname.at1_key: lambda state: state.has(iname.at1_key, self.player),
            iname.at2_key: lambda state: state.has(iname.at2_key, self.player),
            iname.chb_key: lambda state: state.has(iname.chb_key, self.player),
            "Bomb 1": lambda state: state.has_all({iname.nitro, iname.mandragora}, self.player),
            "Bomb 2": lambda state: state.has(iname.nitro, self.player, 2) and state.has(iname.mandragora,
                                                                                         self.player, 2),
            iname.ctrl_key: lambda state: state.has(iname.ctrl_key, self.player),
            iname.cta_key: lambda state: state.has(iname.cta_key, self.player),
            iname.ctb_key: lambda state: state.has(iname.ctb_key, self.player),
            iname.ctc_key: lambda state: state.has(iname.ctc_key, self.player),
            iname.ctd_key: lambda state: state.has(iname.ctd_key, self.player),
            iname.cte_key: lambda state: state.has(iname.cte_key, self.player),
            "Dracula": self.can_enter_dracs_chamber
        }

    def can_enter_dracs_chamber(self, state: CollectionState) -> bool:
        drac_object_name = None
        if self.drac_condition == DraculasCondition.option_crystal:
            drac_object_name = "Crystal"
        elif self.drac_condition == DraculasCondition.option_bosses:
            drac_object_name = "Trophy"
        elif self.drac_condition == DraculasCondition.option_specials:
            drac_object_name = "Special2"

        if drac_object_name is not None:
            return state.has(drac_object_name, self.player, self.required_s2s)
        return True

    def set_cvlod_rules(self) -> None:
        multiworld = self.world.multiworld

        for region in multiworld.get_regions(self.player):
            # Set each entrance's rule if it should have one.
            # Warp entrances have their own special handling.
            for entrance in region.entrances:
                if entrance.parent_region.name == "Menu":
                    if entrance.name.startswith("Warp "):
                        entrance.access_rule = lambda state, warp_num=int(entrance.name[5]): \
                            state.has(iname.s1, self.player, self.s1s_per_warp * warp_num)
                else:
                    ent_rule = get_entrance_info(entrance.name, "rule")
                    if ent_rule in self.rules:
                        entrance.access_rule = self.rules[ent_rule]

        multiworld.completion_condition[self.player] = lambda state: state.has(iname.victory, self.player)
        if self.world.options.accessibility:  # not locations accessibility
            self.set_self_locking_items()

    def set_self_locking_items(self) -> None:
        multiworld = self.world.multiworld

        # Do the regions that we know for a fact always exist, and we always do no matter what.
        allow_self_locking_items(multiworld.get_region(rname.villa_archives, self.player), iname.arc_key)
        allow_self_locking_items(multiworld.get_region(rname.villa_fgarden, self.player), iname.tho_key)
        allow_self_locking_items(multiworld.get_region(rname.villa_fountain, self.player), iname.diary)
        allow_self_locking_items(multiworld.get_region(rname.villa_fountain_top, self.player), iname.brooch)
        #allow_self_locking_items(multiworld.get_region(rname.cc_torture_chamber, self.player), iname.chb_key)

        # Add this region if the world doesn't have the Villa Storeroom warp entrance.
        #if "Villa" not in self.world.active_warp_list[1:]:
        #    allow_self_locking_items(multiworld.get_region(rname.villa_storeroom, self.player), iname.str_key)
