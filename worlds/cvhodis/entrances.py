from Options import Accessibility
from .data import ent_names
from .options import AreaShuffle
from enum import IntEnum
from BaseClasses import Entrance
from entrance_rando import ERPlacementState
from typing import NamedTuple

class CVHoDisEntrance(Entrance):
    def can_connect_to(self, other: Entrance, dead_end: bool, er_state: "ERPlacementState") -> bool:
        """
        The regular Entrance's method, but with more conditions specific to Harmony of Dissonance to accommodate the
        Castle Symmetry option on full Accessibility.
        """
        if er_state.world.options.castle_symmetry and er_state.world.options.area_shuffle.value == \
            AreaShuffle.option_separate and er_state.world.options.accessibility == Accessibility.option_full:

            # Always deny connecting the right Room A transition to a dead end or the right Skeleton A door, as this
            # will create isolated inaccessible regions in the other castle due to right Room B being a dead end.
            if self.name == ent_names.ria_exit_mca_r and (dead_end or other.name == ent_names.sca_exit_cya):
                return False

            # Don't connect to the Skeleton A left side unless the Skeleton B right door is reachable, to ensure nothing
            # is locked out by the Skeleton B one-way rock before the left ceiling transition.
            if other.name == ent_names.sca_exit_eta and not \
                    er_state.collection_state.can_reach_entrance(ent_names.sca_exit_eta, er_state.world.player):
                return False

            # Don't connect to the Shrine B left side unless the Shrine A top transition is reachable, to ensure
            # nothing is locked out by the Shrine A one-way wall after Living Armor.
            if other.name == ent_names.sab_exit_etb and not \
                    er_state.collection_state.can_reach_entrance(ent_names.saa_exit_wwa, er_state.world.player):
                return False

        # Run the regular Entrance class's method and return its result like normal.
        return super().can_connect_to(other, dead_end, er_state)

class ERGroups(IntEnum):
    # NOTE: The current stable GER's on_connect is not perfect, so for now, Top and Bottom entrances are considered Left
    # and Right respectively to simplify things.
    LEFT_A = 1
    LEFT_SKULL_A = 2
    LEFT_MK_A = 3
    RIGHT_A = 4
    RIGHT_SKULL_A = 5
    RIGHT_MK_A = 6
    TOP_A = 7
    BOTTOM_A = 8
    LEFT_B = 9
    LEFT_SKULL_B = 10
    LEFT_MK_B = 11
    RIGHT_B = 12
    RIGHT_SKULL_B = 13
    RIGHT_MK_B = 14
    TOP_B = 15
    BOTTOM_B = 16

TOP_GROUPS = [ERGroups.TOP_A, ERGroups.TOP_B]
BOTTOM_GROUPS = [ERGroups.BOTTOM_A, ERGroups.BOTTOM_B]
VERTICAL_GROUPS = TOP_GROUPS + BOTTOM_GROUPS
LEFT_GROUPS = [ERGroups.LEFT_A, ERGroups.LEFT_SKULL_A, ERGroups.LEFT_MK_A, ERGroups.LEFT_B, ERGroups.LEFT_SKULL_B,
               ERGroups.LEFT_MK_B]
RIGHT_GROUPS = [ERGroups.RIGHT_A, ERGroups.RIGHT_SKULL_A, ERGroups.RIGHT_MK_A, ERGroups.RIGHT_B, ERGroups.RIGHT_SKULL_B,
                ERGroups.RIGHT_MK_B]
HORIZONTAL_GROUPS = LEFT_GROUPS + RIGHT_GROUPS
CASTLE_A_GROUPS = [ERGroups.TOP_A, ERGroups.BOTTOM_A, ERGroups.LEFT_A, ERGroups.RIGHT_A]
CASTLE_B_GROUPS = [ERGroups.TOP_B, ERGroups.BOTTOM_B, ERGroups.LEFT_B, ERGroups.RIGHT_B]
SKULL_DOOR_GROUPS = [ERGroups.LEFT_SKULL_A, ERGroups.LEFT_SKULL_B, ERGroups.RIGHT_SKULL_A, ERGroups.RIGHT_SKULL_B]
MK_DOOR_GROUPS = [ERGroups.LEFT_MK_A, ERGroups.LEFT_MK_B, ERGroups.RIGHT_MK_A, ERGroups.RIGHT_MK_B]

#TARGET_GROUP_RELATIONSHIPS: dict[int: list[int]] = {
    # Randomized entrances cannot connect to their same direction and only to their same castle.
#    ERGroups.LEFT_A: [ERGroups.RIGHT_A, ERGroups.TOP_A, ERGroups.BOTTOM_A],
#    ERGroups.RIGHT_A: [ERGroups.LEFT_A, ERGroups.TOP_A, ERGroups.BOTTOM_A],
#    ERGroups.TOP_A: [ERGroups.RIGHT_A, ERGroups.LEFT_A, ERGroups.BOTTOM_A],
#    ERGroups.BOTTOM_A: [ERGroups.RIGHT_A, ERGroups.TOP_A, ERGroups.LEFT_A],
#    ERGroups.LEFT_B: [ERGroups.RIGHT_B, ERGroups.TOP_B, ERGroups.BOTTOM_B],
#    ERGroups.RIGHT_B: [ERGroups.LEFT_B, ERGroups.TOP_B, ERGroups.BOTTOM_B],
#    ERGroups.TOP_B: [ERGroups.RIGHT_B, ERGroups.LEFT_B, ERGroups.BOTTOM_B],
#    ERGroups.BOTTOM_B: [ERGroups.RIGHT_B, ERGroups.TOP_B, ERGroups.LEFT_B],
#}

TARGET_GROUP_RELATIONSHIPS: dict[int: list[int]] = {
    # Randomized entrances cannot connect to their same direction and only to their same castle.
    ERGroups.LEFT_A: [ERGroups.RIGHT_A, ERGroups.TOP_A],
    ERGroups.LEFT_SKULL_A: [ERGroups.RIGHT_SKULL_A],
    ERGroups.LEFT_MK_A: [ERGroups.RIGHT_MK_A],
    ERGroups.RIGHT_A: [ERGroups.LEFT_A, ERGroups.BOTTOM_A],
    ERGroups.RIGHT_SKULL_A: [ERGroups.LEFT_SKULL_A],
    ERGroups.RIGHT_MK_A: [ERGroups.LEFT_MK_A],
    ERGroups.TOP_A: [ERGroups.LEFT_A, ERGroups.BOTTOM_A],
    ERGroups.BOTTOM_A: [ERGroups.RIGHT_A, ERGroups.TOP_A],
    ERGroups.LEFT_B: [ERGroups.RIGHT_B, ERGroups.TOP_B],
    ERGroups.LEFT_SKULL_B: [ERGroups.RIGHT_SKULL_B],
    ERGroups.LEFT_MK_B: [ERGroups.RIGHT_MK_B],
    ERGroups.RIGHT_B: [ERGroups.LEFT_B, ERGroups.BOTTOM_B],
    ERGroups.RIGHT_SKULL_B: [ERGroups.LEFT_SKULL_B],
    ERGroups.RIGHT_MK_B: [ERGroups.LEFT_MK_B],
    ERGroups.TOP_B: [ERGroups.LEFT_B, ERGroups.BOTTOM_B],
    ERGroups.BOTTOM_B: [ERGroups.RIGHT_B, ERGroups.TOP_B],
}

class CVHoDisTransitionData(NamedTuple):
    transition_offset: int # Where in the ROM the data for the room transition at that destination begins.
    room_ptr: int # Where in the ROM the destination's source room info begins.
    camera_x_pos: int # X position of the camera (from the left) when arriving at the destination.
    camera_y_pos: int # Y position of the camera (from the top) when arriving at the destination.
    er_group: int # Number in the ERGroups enum for which ER group it's in; indicates things like which side of the
                  # screen the destination's room transition is on, what castle the destination belongs to, etc.
    player_depart_y_pos: int # The on-screen standing Y position the player should be at upon entering the entrance
                             # transition.
    player_arrive_y_pos: int # The on-screen standing Y position the player should be moved to upon arriving at the
                             # exit transition.
    other_castle_transition: str # The transition that corresponds to this one in the other castle.

SHUFFLEABLE_TRANSITIONS: dict[str, CVHoDisTransitionData] = {
    # Castle A
    ent_names.eta_exit_saa:   CVHoDisTransitionData(0x499340, 0x849934C, 0x0410, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.etb_exit_sab),
    ent_names.eta_exit_mca:   CVHoDisTransitionData(0x499020, 0x849902C, 0x0210, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.etb_exit_mcb),
    ent_names.eta_exit_sca:   CVHoDisTransitionData(0x49940C, 0x8499418, 0x0000, 0x0660, ERGroups.BOTTOM_A,
                                                    0xA3, 0x8F, ent_names.etb_exit_scb),
    ent_names.mca_exit_eta:   CVHoDisTransitionData(0x49ABF4, 0x849AC0C, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.mcb_exit_etb),
    # NOTE: Technically, the player is on the ground at screen position 0x60 in vertically-scrolling rooms.
    # In practice, however, the game offsets the player in the same way they would be if going to/from a static
    # transition at the center screen position.
    ent_names.mca_exit_ria_l: CVHoDisTransitionData(0x49B3C0, 0x849B3CC, 0x0000, 0x0130, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.mcb_exit_rib_l),
    ent_names.mca_exit_ria_r: CVHoDisTransitionData(0x49B3B4, 0x849B3CC, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.mcb_exit_rib_r),
    ent_names.mca_exit_wwa:   CVHoDisTransitionData(0x49B330, 0x849B33C, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.mcb_exit_wwb),
    ent_names.mca_exit_tfa:   CVHoDisTransitionData(0x49B2AC, 0x849B2B8, 0x0210, 0x0000, ERGroups.RIGHT_SKULL_A,
                                                    0x67, 0x67, ent_names.mcb_exit_tfb),
    ent_names.ria_exit_mca_l: CVHoDisTransitionData(0x49B4BC, 0x849B4C8, 0x0210, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.rib_exit_mcb_l),
    ent_names.ria_exit_mca_r: CVHoDisTransitionData(0x49B438, 0x849B450, 0x0000, 0x0030, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.rib_exit_mcb_r),
    ent_names.wwa_exit_mca:   CVHoDisTransitionData(0x49D028, 0x849D040, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.wwb_exit_mcb),
    ent_names.wwa_exit_cya:   CVHoDisTransitionData(0x49D37C, 0x849D388, 0x0110, 0x0000, ERGroups.RIGHT_SKULL_A,
                                                    0x67, 0x67, ent_names.wwb_exit_cyb),
    ent_names.wwa_exit_saa:   CVHoDisTransitionData(0x49D3F4, 0x849D400, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.wwb_exit_sab),
    ent_names.saa_exit_wwa:   CVHoDisTransitionData(0x49D478, 0x849D484, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.sab_exit_wwb),
    ent_names.saa_exit_eta:   CVHoDisTransitionData(0x49D740, 0x849D758, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.sab_exit_etb),
    ent_names.cya_exit_sca:   CVHoDisTransitionData(0x4AD0D8, 0x84AD0F0, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.cyb_exit_scb),
    ent_names.cya_exit_lca:   CVHoDisTransitionData(0x4AD024, 0x84AD054, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.cyb_exit_lcb),
    ent_names.cya_exit_wwa:   CVHoDisTransitionData(0x4AD458, 0x84AD47C, 0x0000, 0x0000, ERGroups.LEFT_SKULL_A,
                                                    0x67, 0x67, ent_names.cyb_exit_wwb),
    ent_names.cya_exit_tfa:   CVHoDisTransitionData(0x4AD464, 0x84AD47C, 0x0200, 0x0000, ERGroups.TOP_A,
                                                    0x9F, 0x1F, ent_names.cyb_exit_tfb),
    ent_names.sca_exit_cya:   CVHoDisTransitionData(0x4A0A10, 0x84A0A1C, 0x0000, 0x0030, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.scb_exit_cyb),
    ent_names.sca_exit_eta:   CVHoDisTransitionData(0x4A10C8, 0x84A10E0, 0x0108, 0x0000, ERGroups.TOP_A,
                                                    0x9F, 0x1F, ent_names.scb_exit_etb),
    ent_names.lca_exit_cya:   CVHoDisTransitionData(0x4A2CAC, 0x84A2CB8, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.lcb_exit_cyb),
    ent_names.lca_exit_ada:   CVHoDisTransitionData(0x4A2EF8, 0x84A2F04, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.lcb_exit_adb),
    ent_names.swa_exit_cda:   CVHoDisTransitionData(0x4A7500, 0x84A7518, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x7F, 0x7F, ent_names.swb_exit_cdb),
    ent_names.swa_exit_cra:   CVHoDisTransitionData(0x4A79CC, 0x84A79D8, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.swb_exit_crb),
    ent_names.swa_exit_ada:   CVHoDisTransitionData(0x4A7BB4, 0x84A7BCC, 0x0008, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.swb_exit_adb),
    ent_names.cda_exit_swa:   CVHoDisTransitionData(0x4A7488, 0x84A7494, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x7F, 0x7F, ent_names.cdb_exit_swb),
    ent_names.cda_exit_tfa:   CVHoDisTransitionData(0x4A7248, 0x84A7260, 0x0000, 0x0130, ERGroups.LEFT_MK_A,
                                                    0x67, 0x67, ent_names.cdb_exit_tfb),
    ent_names.ada_exit_swa:   CVHoDisTransitionData(0x4A6040, 0x84A604C, 0x0000, 0x0030, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.adb_exit_swb),
    ent_names.ada_exit_lca:   CVHoDisTransitionData(0x4A5CEC, 0x84A5D04, 0x0000, 0x0130, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.adb_exit_lcb),
    ent_names.ada_exit_cra:   CVHoDisTransitionData(0x4A627C, 0x84A6288, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x8F, 0x8F, ent_names.adb_exit_crb),
    ent_names.cra_exit_ada:   CVHoDisTransitionData(0x4A9CA8, 0x84A9CCC, 0x0000, 0x0260, ERGroups.LEFT_A,
                                                    0x8F, 0x8F, ent_names.crb_exit_adb),
    ent_names.cra_exit_swa:   CVHoDisTransitionData(0x4A9614, 0x84A9650, 0x0000, 0x0230, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.crb_exit_swb),
    ent_names.tfa_exit_cda:   CVHoDisTransitionData(0x49F280, 0x849F28C, 0x0110, 0x0130, ERGroups.RIGHT_MK_A,
                                                    0x67, 0x67, ent_names.tfb_exit_cdb),
    ent_names.tfa_exit_cya:   CVHoDisTransitionData(0x49F4F8, 0x849F504, 0x0000, 0x0560, ERGroups.BOTTOM_A,
                                                    0xA3, 0x8F, ent_names.tfb_exit_cyb),
    ent_names.tfa_exit_mca:   CVHoDisTransitionData(0x49F570, 0x849F588, 0x0000, 0x0130, ERGroups.LEFT_SKULL_A,
                                                    0x67, 0x67, ent_names.tfb_exit_mcb),
    # Castle B
    ent_names.etb_exit_sab:   CVHoDisTransitionData(0x49A344, 0x849A350, 0x0410, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.eta_exit_saa),
    ent_names.etb_exit_mcb:   CVHoDisTransitionData(0x49A028, 0x849A034, 0x0210, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.eta_exit_mca),
    ent_names.etb_exit_scb:   CVHoDisTransitionData(0x49A404, 0x849A410, 0x0000, 0x0660, ERGroups.BOTTOM_B,
                                                    0xA3, 0x8F, ent_names.eta_exit_sca),
    ent_names.mcb_exit_etb:   CVHoDisTransitionData(0x49BE80, 0x849BE98, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.mca_exit_eta),
    ent_names.mcb_exit_rib_l: CVHoDisTransitionData(0x49C62C, 0x849C638, 0x0000, 0x0130, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.mca_exit_ria_l),
    ent_names.mcb_exit_rib_r: CVHoDisTransitionData(0x49C620, 0x849C638, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.mca_exit_ria_r),
    ent_names.mcb_exit_wwb:   CVHoDisTransitionData(0x49C59C, 0x849C5A8, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.mca_exit_wwa),
    ent_names.mcb_exit_tfb:   CVHoDisTransitionData(0x49C518, 0x849C524, 0x0210, 0x0000, ERGroups.RIGHT_SKULL_B,
                                                    0x67, 0x67, ent_names.mca_exit_tfa),
    ent_names.rib_exit_mcb_l: CVHoDisTransitionData(0x49C748, 0x849C754, 0x0210, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.ria_exit_mca_l),
    ent_names.rib_exit_mcb_r: CVHoDisTransitionData(0x49C6B8, 0x849C6D0, 0x0000, 0x0030, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.ria_exit_mca_r),
    ent_names.wwb_exit_mcb:   CVHoDisTransitionData(0x49E0BC, 0x849E0D4, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.wwa_exit_mca),
    ent_names.wwb_exit_cyb:   CVHoDisTransitionData(0x49E400, 0x849E40C, 0x0110, 0x0000, ERGroups.RIGHT_SKULL_B,
                                                    0x67, 0x67, ent_names.wwa_exit_cya),
    ent_names.wwb_exit_sab:   CVHoDisTransitionData(0x49E478, 0x849E484, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.wwa_exit_saa),
    ent_names.sab_exit_wwb:   CVHoDisTransitionData(0x49E4FC, 0x849E508, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.saa_exit_wwa),
    ent_names.sab_exit_etb:   CVHoDisTransitionData(0x49E7A4, 0x849E7BC, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.saa_exit_eta),
    ent_names.cyb_exit_scb:   CVHoDisTransitionData(0x4AE9A4, 0x84AE9BC, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.cya_exit_sca),
    ent_names.cyb_exit_lcb:   CVHoDisTransitionData(0x4AE8F0, 0x84AE920, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.cya_exit_lca),
    ent_names.cyb_exit_wwb:   CVHoDisTransitionData(0x4AED20, 0x84AED44, 0x0000, 0x0000, ERGroups.LEFT_SKULL_B,
                                                    0x67, 0x67, ent_names.cya_exit_wwa),
    ent_names.cyb_exit_tfb:   CVHoDisTransitionData(0x4AED2C, 0x84AED44, 0x0200, 0x0000, ERGroups.TOP_B,
                                                    0x9F, 0x1F, ent_names.cya_exit_tfa),
    ent_names.scb_exit_cyb:   CVHoDisTransitionData(0x4A1B10, 0x84A1B1C, 0x0000, 0x0030, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.sca_exit_cya),
    ent_names.scb_exit_etb:   CVHoDisTransitionData(0x4A2210, 0x84A2228, 0x0108, 0x0000, ERGroups.TOP_B,
                                                    0x9F, 0x1F, ent_names.sca_exit_eta),
    ent_names.lcb_exit_cyb:   CVHoDisTransitionData(0x4A45A4, 0x84A45B0, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.lca_exit_cya),
    ent_names.lcb_exit_adb:   CVHoDisTransitionData(0x4A47F0, 0x84A47FC, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.lca_exit_ada),
    ent_names.swb_exit_cdb:   CVHoDisTransitionData(0x4A8740, 0x84A8758, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x7F, 0x7F, ent_names.swa_exit_cda),
    ent_names.swb_exit_crb:   CVHoDisTransitionData(0x4A8BE4, 0x84A8BF0, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.swa_exit_cra),
    ent_names.swb_exit_adb:   CVHoDisTransitionData(0x4A8DF4, 0x84A8E0C, 0x0008, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.swa_exit_ada),
    ent_names.cdb_exit_swb:   CVHoDisTransitionData(0x4A86C8, 0x84A86D4, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x7F, 0x7F, ent_names.cda_exit_swa),
    ent_names.cdb_exit_tfb:   CVHoDisTransitionData(0x4A84A0, 0x84A84B8, 0x0000, 0x0130, ERGroups.LEFT_MK_B,
                                                    0x67, 0x67, ent_names.cda_exit_tfa),
    ent_names.adb_exit_swb:   CVHoDisTransitionData(0x4A6B3C, 0x84A6B48, 0x0000, 0x0030, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.ada_exit_swa),
    ent_names.adb_exit_lcb:   CVHoDisTransitionData(0x4A6800, 0x84A6818, 0x0000, 0x0130, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.ada_exit_lca),
    ent_names.adb_exit_crb:   CVHoDisTransitionData(0x4A6D7C, 0x84A6D88, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x8F, 0x8F, ent_names.ada_exit_cra),
    ent_names.crb_exit_adb:   CVHoDisTransitionData(0x4AB6B4, 0x84AB6D8, 0x0000, 0x0260, ERGroups.LEFT_B,
                                                    0x8F, 0x8F, ent_names.cra_exit_ada),
    ent_names.crb_exit_swb:   CVHoDisTransitionData(0x4AB004, 0x84AB040, 0x0000, 0x0230, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.cra_exit_swa),
    ent_names.tfb_exit_cdb:   CVHoDisTransitionData(0x49FF90, 0x849FF9C, 0x0110, 0x0130, ERGroups.RIGHT_MK_B,
                                                    0x67, 0x67, ent_names.tfa_exit_cda),
    ent_names.tfb_exit_cyb:   CVHoDisTransitionData(0x4A020C, 0x84A0218, 0x0000, 0x0560, ERGroups.BOTTOM_B,
                                                    0xA3, 0x8F, ent_names.tfa_exit_cya),
    ent_names.tfb_exit_mcb:   CVHoDisTransitionData(0x4A0284, 0x84A029C, 0x0000, 0x0130, ERGroups.LEFT_SKULL_B,
                                                    0x67, 0x67, ent_names.tfa_exit_mca)
}

SORTED_TRANSITIONS = [transition for transition in SHUFFLEABLE_TRANSITIONS]
VERTICAL_SHAFT_EXITS = [ent_names.eta_exit_sca, ent_names.etb_exit_scb]

def link_room_transitions(transition_pairings: list[tuple]) -> dict[int, bytes]:
    """Gets all ER-related data to go into the ROM. Including what room each altered transition should send the player
    to, where to place the camera, and how much to offset the player on-screen in said destination room."""

    transition_bytes = {}

    for pair in transition_pairings:
        # For each entrance, get the room pointer and camera X and Y positions of the exit and write them in the
        # entrance's transition.
        transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset] = \
            int.to_bytes(SHUFFLEABLE_TRANSITIONS[pair[1]].room_ptr, 4, "little")
        transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x8] = \
            int.to_bytes(SHUFFLEABLE_TRANSITIONS[pair[1]].camera_x_pos, 2, "little")
        transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0xA] = \
            int.to_bytes(SHUFFLEABLE_TRANSITIONS[pair[1]].camera_y_pos, 2, "little")

        # The player offsets are way trickier; we need to take where on-screen they would be both before and after the
        # transition and shift them accordingly. Unless it's a top transition connected to a bottom, in which case we
        # shift by 0.
        if SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in VERTICAL_GROUPS and \
             SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in VERTICAL_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x7] = b"\x00"
        else:
            # Take the lowest byte of the camera position plus the player's departing Y position to get the "true"
            # position to calculate from.
            player_y_entrance = (SHUFFLEABLE_TRANSITIONS[pair[0]].player_depart_y_pos +
                                 SHUFFLEABLE_TRANSITIONS[pair[0]].camera_y_pos) & 0xFF

            # If the position is or greater than or equal to 0xA0 (the very bottom-of-screen subpixel), "Pacman" the
            # value back around to the top.
            if player_y_entrance >= 0xA0:
                player_y_entrance -= 0xA0

            # Take the difference between this value and the destination Y position to get the Y shift value to put in
            # for that transition.
            player_y_shift = SHUFFLEABLE_TRANSITIONS[pair[1]].player_arrive_y_pos - player_y_entrance

            # If the value is outside the (-)128-(+)127 range, set it to the edges of those ranges as that's as far as
            # we are allowed to go.
            if player_y_shift > 127:
                player_y_shift = 0x7F
            elif player_y_shift < -128:
                player_y_shift = 0x80
            # Otherwise, if the value is negative within that range, make it the proper signed negative byte the game
            # expects it to be.
            elif player_y_shift < 0:
                player_y_shift += 0x100

            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x7] = \
                int.to_bytes(player_y_shift, 1, "little")

        # If the entrance is a vertical transition and the exit is in a 1-wide vertical room,
        # set 0xF8 as the player X offset.
        if SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in VERTICAL_GROUPS and pair[1] in VERTICAL_SHAFT_EXITS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\xF8"
        # If the entrance is a vertical transition and the exit is on the left, set 0x98 as the player X offset.
        elif SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in VERTICAL_GROUPS and \
                SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in LEFT_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\x98"
        # If the entrance is a vertical transition and the exit is on the right, set 0x58 as the player X offset.
        elif SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in VERTICAL_GROUPS and \
                SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in RIGHT_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\x58"
        # If the entrance is on the right and the exit is on the top, set 0x7F as the player X offset.
        elif SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in RIGHT_GROUPS and \
                SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in TOP_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\x7F"
        # If the entrance is on the left and the exit is on the top, set 0x80 as the player X offset.
        elif SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in LEFT_GROUPS and \
                SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in TOP_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\x80"
        # If the entrance is on the right and the exit is on the bottom, set 0x4F as the player X offset.
        elif SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in RIGHT_GROUPS and \
                SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in BOTTOM_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\x4F"
        # If the entrance is on the left and the exit is on the bottom, set 0xB0 as the player X offset.
        elif SHUFFLEABLE_TRANSITIONS[pair[0]].er_group in LEFT_GROUPS and \
                SHUFFLEABLE_TRANSITIONS[pair[1]].er_group in BOTTOM_GROUPS:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\xB0"
        # Otherwise, the player X offset should be 0.
        else:
            transition_bytes[SHUFFLEABLE_TRANSITIONS[pair[0]].transition_offset + 0x6] = b"\x00"

    return transition_bytes

def cvhodis_on_connect(er_state: ERPlacementState, placed_exits: list[Entrance],
                       paired_entrances: list[Entrance]) -> bool:
    """Additional GER behavior specific to Castlevania HoD after an Entrance is connected."""
    # TODO: Finish implementing this with some GER-related fixes.

    # If Castle Symmetry is on and Area Shuffle is set to Separate, connect the same exit in the other castle to the
    # same corresponding area.
    if er_state.world.options.area_shuffle.value != AreaShuffle.option_separate or \
            not er_state.world.options.castle_symmetry:
        return False

    other_castle_exit = er_state.world.multiworld.get_entrance(SHUFFLEABLE_TRANSITIONS[placed_exits[0].name].other_castle_transition, er_state.world.player)
    other_castle_target = er_state.entrance_lookup.find_target(SHUFFLEABLE_TRANSITIONS[paired_entrances[0].name].other_castle_transition)

    er_state.connect(other_castle_exit, other_castle_target)

    return True
