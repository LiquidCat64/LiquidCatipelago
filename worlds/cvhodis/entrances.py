import logging

from Options import Accessibility
from .data import ent_names, reg_names
from .data.ent_names import tfa_exit_mca
from .data.enums import AreaNames, TransitionNames
from .options import CVHoDisOptions, TransitionShuffler, CastleSwapper, AreaDivisions, CastleWarpCondition
from enum import IntEnum
from BaseClasses import Entrance
from entrance_rando import ERPlacementState
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from . import CVHoDisWorld, CVHoDisOptions


class CVHoDisEntrance(Entrance):
    def can_connect_to(self, other: Entrance, dead_end: bool, er_state: "ERPlacementState") -> bool:
        """
        The regular Entrance's method, but with more conditions specific to Harmony of Dissonance to accommodate the
        Castle Symmetry option.
        """
        if er_state.world.options.castle_symmetry and \
                er_state.world.options.castle_swapper.value != CastleSwapper.option_transitions:

            # Check the Collection State's blocked connections for this slot. If there are three connections remaining,
            # and two of them are the other castle versions of both the entrance and exit we are trying to connect,
            # don't do the connection on behalf of the fact that we would run out of connections. Unless we the placed
            # connections is equal to the slot's total connections minus 4, in which case we will allow the final
            # connection.
            blocked_connections = {ent.name for ent in er_state.collection_state.blocked_connections[self.player]}
            if len(blocked_connections) <= 3 and \
                    (SHUFFLEABLE_TRANSITIONS[self.name].other_castle_transition in blocked_connections and
                     SHUFFLEABLE_TRANSITIONS[other.name].other_castle_transition in blocked_connections) and \
                     len(er_state.placements) < len(er_state.world.inverted_transitions):
                return False

            # Don't connect the Skeleton A right side door to anywhere until Skeleton B's right side is reachable, to
            # ensure we don't create any unwinnable layouts due to Skeleton B's one-way rock.
            if self.name == ent_names.sca_exit_cya and \
                    not er_state.collection_state.can_reach_entrance(ent_names.scb_exit_cyb, er_state.world.player):
                return False

            # If we're on Full Accessibility, run some additional checks...
            if er_state.world.options.accessibility == Accessibility.option_full:
                # Always deny connecting the right Room A transition to either a dead end or the right Skeleton A door,
                # as this will create isolated inaccessible regions in the other castle due to right Room B being a dead
                # end and right Skeleton B only being accessible through the one transition.
                if self.name == ent_names.ria_exit_mca_r and (dead_end or other.name == ent_names.sca_exit_cya):
                    return False

                # Don't connect to the Skeleton A left side unless the Skeleton B right door is reachable, to ensure
                # nothing is locked out by the Skeleton B one-way rock before the left ceiling transition.
                if other.name == ent_names.sca_exit_eta and not \
                        er_state.collection_state.can_reach_entrance(ent_names.scb_exit_cyb, er_state.world.player):
                    return False

                # Don't connect to the Shrine B left side unless the Shrine A top transition is reachable, to ensure
                # nothing is locked out by the Shrine A one-way wall after Living Armor (never mind the fact you can get
                # past it with a frame-perfect backdash through the transition to it...).
                if other.name == ent_names.sab_exit_etb and not \
                        er_state.collection_state.can_reach_entrance(ent_names.saa_exit_wwa, er_state.world.player):
                    return False

                # If Entrances are coupled, always deny connecting the top Shrine B and right Skeleton A transitions to
                # dead-ends.
                if self.name in [ent_names.sab_exit_wwb, ent_names.sca_exit_cya] and dead_end and \
                        er_state.world.options.transition_shuffler.value == TransitionShuffler.option_coupled:
                    return False

        # Run the regular Entrance class's method and return its result like normal.
        return super().can_connect_to(other, dead_end, er_state)

class ERGroups(IntEnum):
    # TODO: Allow horizontals to connect to either vertical direction and vice versa.
    LEFT_A = 1
    LEFT_B = 2
    LEFT_SKULL_A = 3
    LEFT_SKULL_B = 4
    LEFT_MK_A = 5
    LEFT_MK_B = 6
    RIGHT_A = 7
    RIGHT_B = 8
    RIGHT_SKULL_A = 9
    RIGHT_SKULL_B = 10
    RIGHT_MK_A = 11
    RIGHT_MK_B = 12
    TOP_A = 13
    TOP_B = 14
    BOTTOM_A = 15
    BOTTOM_B = 16

SUB_MAIN_AREAS = {AreaNames.ROOM: AreaNames.MARBLE,
                  AreaNames.WAILING: AreaNames.SHRINE,
                  AreaNames.SKELETON: AreaNames.ENTRANCE,
                  AreaNames.WALKWAY: AreaNames.CHAPEL,
                  AreaNames.TOP: AreaNames.TREASURY}
SUB_TRANSITIONS = [TransitionNames.ET_SC, TransitionNames.MC_RI_R, TransitionNames.MC_RI_L, TransitionNames.WW_SA,
                   TransitionNames.CY_TF, TransitionNames.SW_CD]
MAIN_SUB_AREAS = {value: key for key, value in SUB_MAIN_AREAS.items()}

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
    # Castle A
    ERGroups.LEFT_A: [ERGroups.RIGHT_A, ERGroups.TOP_A],
    ERGroups.LEFT_SKULL_A: [ERGroups.RIGHT_SKULL_A],
    ERGroups.LEFT_MK_A: [ERGroups.RIGHT_MK_A],
    ERGroups.RIGHT_A: [ERGroups.LEFT_A, ERGroups.BOTTOM_A],
    ERGroups.RIGHT_SKULL_A: [ERGroups.LEFT_SKULL_A],
    ERGroups.RIGHT_MK_A: [ERGroups.LEFT_MK_A],
    ERGroups.TOP_A: [ERGroups.LEFT_A, ERGroups.BOTTOM_A],
    ERGroups.BOTTOM_A: [ERGroups.RIGHT_A, ERGroups.TOP_A],
    # Castle B
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
    transition_offset: int  # Where in the ROM the data for the room transition at that destination begins.
    room_ptr: int  # Where in the ROM the destination's source room info begins.
    camera_x_pos: int  # X position of the camera (from the left) when arriving at the destination.
    camera_y_pos: int  # Y position of the camera (from the top) when arriving at the destination.
    er_group: int  # Number in the ERGroups enum for which ER group it's in; indicates things like which side of the
                   # screen the destination's room transition is on, what castle the destination belongs to, etc.
    player_depart_y_pos: int  # The on-screen standing Y position the player should be at upon entering the entrance
                              # transition.
    player_arrive_y_pos: int  # The on-screen standing Y position the player should be moved to upon arriving at the
                              # exit transition.
    destination_transition: str  # The transition that this one normally connects to in the other area.
    other_castle_transition: str  # The transition that corresponds to this one in the other castle.
    area: AreaNames  # What main area in the game the transition belongs to. Used if Area Divisions is Doors Only.
    trans_group: TransitionNames  # What group of transitions the transition belongs to.
    is_door: bool  # Whether this transition is a door transition. If not, it will be left vanilla if Area Divisions is
                   # set to Doors Only.

SHUFFLEABLE_TRANSITIONS: dict[str, CVHoDisTransitionData] = {
    ent_names.eta_exit_saa:   CVHoDisTransitionData(0x499340, 0x849934C, 0x0410, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.saa_exit_eta, ent_names.etb_exit_sab,
                                                    AreaNames.ENTRANCE, TransitionNames.ET_SA, True),
    ent_names.eta_exit_mca:   CVHoDisTransitionData(0x499020, 0x849902C, 0x0210, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.mca_exit_eta, ent_names.etb_exit_mcb,
                                                    AreaNames.ENTRANCE, TransitionNames.ET_MC, True),
    ent_names.eta_exit_sca:   CVHoDisTransitionData(0x49940C, 0x8499418, 0x0000, 0x0660, ERGroups.BOTTOM_A,
                                                    0xA3, 0x8F, ent_names.sca_exit_eta, ent_names.etb_exit_scb,
                                                    AreaNames.ENTRANCE, TransitionNames.ET_SC, False),
    ent_names.mca_exit_eta:   CVHoDisTransitionData(0x49ABF4, 0x849AC0C, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.eta_exit_mca, ent_names.mcb_exit_etb,
                                                    AreaNames.MARBLE, TransitionNames.ET_MC, True),
    # NOTE: Technically, the player is on the ground at screen position 0x60 in vertically-scrolling rooms.
    # In practice, however, the game offsets the player in the same way they would be if going to/from a static
    # transition at the center screen position.
    ent_names.mca_exit_ria_l: CVHoDisTransitionData(0x49B3C0, 0x849B3CC, 0x0000, 0x0130, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.ria_exit_mca_l, ent_names.mcb_exit_rib_l,
                                                    AreaNames.MARBLE, TransitionNames.MC_RI_L, False),
    ent_names.mca_exit_ria_r: CVHoDisTransitionData(0x49B3B4, 0x849B3CC, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.ria_exit_mca_r, ent_names.mcb_exit_rib_r,
                                                    AreaNames.MARBLE, TransitionNames.MC_RI_R, False),
    ent_names.mca_exit_wwa:   CVHoDisTransitionData(0x49B330, 0x849B33C, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.wwa_exit_mca, ent_names.mcb_exit_wwb,
                                                    AreaNames.MARBLE, TransitionNames.MC_WW, True),
    ent_names.mca_exit_tfa:   CVHoDisTransitionData(0x49B2AC, 0x849B2B8, 0x0210, 0x0000, ERGroups.RIGHT_SKULL_A,
                                                    0x67, 0x67, tfa_exit_mca, ent_names.mcb_exit_tfb,
                                                    AreaNames.MARBLE, TransitionNames.MC_TF, True),
    ent_names.ria_exit_mca_l: CVHoDisTransitionData(0x49B4BC, 0x849B4C8, 0x0210, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.mca_exit_ria_l, ent_names.rib_exit_mcb_l,
                                                    AreaNames.ROOM, TransitionNames.MC_RI_L, False),
    ent_names.ria_exit_mca_r: CVHoDisTransitionData(0x49B438, 0x849B450, 0x0000, 0x0030, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.mca_exit_ria_r, ent_names.rib_exit_mcb_r,
                                                    AreaNames.ROOM, TransitionNames.MC_RI_R, False),
    ent_names.wwa_exit_mca:   CVHoDisTransitionData(0x49D028, 0x849D040, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.mca_exit_wwa, ent_names.wwb_exit_mcb,
                                                    AreaNames.WAILING, TransitionNames.MC_WW, True),
    ent_names.wwa_exit_cya:   CVHoDisTransitionData(0x49D37C, 0x849D388, 0x0110, 0x0000, ERGroups.RIGHT_SKULL_A,
                                                    0x67, 0x67, ent_names.cya_exit_wwa, ent_names.wwb_exit_cyb,
                                                    AreaNames.WAILING, TransitionNames.WW_CY, True),
    ent_names.wwa_exit_saa:   CVHoDisTransitionData(0x49D3F4, 0x849D400, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.saa_exit_wwa, ent_names.wwb_exit_sab,
                                                    AreaNames.WAILING, TransitionNames.WW_SA, False),
    ent_names.saa_exit_wwa:   CVHoDisTransitionData(0x49D478, 0x849D484, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.wwa_exit_saa, ent_names.sab_exit_wwb,
                                                    AreaNames.SHRINE, TransitionNames.WW_SA, False),
    ent_names.saa_exit_eta:   CVHoDisTransitionData(0x49D740, 0x849D758, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.eta_exit_saa, ent_names.sab_exit_etb,
                                                    AreaNames.SHRINE, TransitionNames.ET_SA, True),
    ent_names.cya_exit_sca:   CVHoDisTransitionData(0x4AD0D8, 0x84AD0F0, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.sca_exit_cya, ent_names.cyb_exit_scb,
                                                    AreaNames.TREASURY, TransitionNames.CY_SC, True),
    ent_names.cya_exit_lca:   CVHoDisTransitionData(0x4AD024, 0x84AD054, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.lca_exit_cya, ent_names.cyb_exit_lcb,
                                                    AreaNames.TREASURY, TransitionNames.CY_LC, True),
    ent_names.cya_exit_wwa:   CVHoDisTransitionData(0x4AD458, 0x84AD47C, 0x0000, 0x0000, ERGroups.LEFT_SKULL_A,
                                                    0x67, 0x67, ent_names.wwa_exit_cya, ent_names.cyb_exit_wwb,
                                                    AreaNames.TREASURY, TransitionNames.WW_CY, True),
    ent_names.cya_exit_tfa:   CVHoDisTransitionData(0x4AD464, 0x84AD47C, 0x0200, 0x0000, ERGroups.TOP_A,
                                                    0x9F, 0x1F, ent_names.tfa_exit_cya, ent_names.cyb_exit_tfb,
                                                    AreaNames.TREASURY, TransitionNames.CY_TF, False),
    ent_names.sca_exit_cya:   CVHoDisTransitionData(0x4A0A10, 0x84A0A1C, 0x0000, 0x0030, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.cya_exit_sca, ent_names.scb_exit_cyb,
                                                    AreaNames.SKELETON, TransitionNames.CY_SC, True),
    ent_names.sca_exit_eta:   CVHoDisTransitionData(0x4A10C8, 0x84A10E0, 0x0108, 0x0000, ERGroups.TOP_A,
                                                    0x9F, 0x1F, ent_names.eta_exit_sca, ent_names.scb_exit_etb,
                                                    AreaNames.SKELETON, TransitionNames.ET_SC, False),
    ent_names.lca_exit_cya:   CVHoDisTransitionData(0x4A2CAC, 0x84A2CB8, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.cya_exit_lca, ent_names.lcb_exit_cyb,
                                                    AreaNames.LUMINOUS, TransitionNames.CY_LC, True),
    ent_names.lca_exit_ada:   CVHoDisTransitionData(0x4A2EF8, 0x84A2F04, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.ada_exit_lca, ent_names.lcb_exit_adb,
                                                    AreaNames.LUMINOUS, TransitionNames.LC_AD, True),
    ent_names.swa_exit_cda:   CVHoDisTransitionData(0x4A7500, 0x84A7518, 0x0000, 0x0000, ERGroups.LEFT_A,
                                                    0x7F, 0x7F, ent_names.cda_exit_swa, ent_names.swb_exit_cdb,
                                                    AreaNames.WALKWAY, TransitionNames.SW_CD, False),
    ent_names.swa_exit_cra:   CVHoDisTransitionData(0x4A79CC, 0x84A79D8, 0x0000, 0x0130, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.cra_exit_swa, ent_names.swb_exit_crb,
                                                    AreaNames.WALKWAY, TransitionNames.SW_CR, True),
    ent_names.swa_exit_ada:   CVHoDisTransitionData(0x4A7BB4, 0x84A7BCC, 0x0008, 0x0000, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.ada_exit_swa, ent_names.swb_exit_adb,
                                                    AreaNames.WALKWAY, TransitionNames.SW_AD, True),
    ent_names.cda_exit_swa:   CVHoDisTransitionData(0x4A7488, 0x84A7494, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x7F, 0x7F, ent_names.swa_exit_cda, ent_names.cdb_exit_swb,
                                                    AreaNames.CHAPEL, TransitionNames.SW_CD, False),
    ent_names.cda_exit_tfa:   CVHoDisTransitionData(0x4A7248, 0x84A7260, 0x0000, 0x0130, ERGroups.LEFT_MK_A,
                                                    0x67, 0x67, ent_names.tfa_exit_cda, ent_names.cdb_exit_tfb,
                                                    AreaNames.CHAPEL, TransitionNames.CD_TF, True),
    ent_names.ada_exit_swa:   CVHoDisTransitionData(0x4A6040, 0x84A604C, 0x0000, 0x0030, ERGroups.RIGHT_A,
                                                    0x67, 0x67, ent_names.swa_exit_ada, ent_names.adb_exit_swb,
                                                    AreaNames.AQUEDUCT, TransitionNames.SW_AD, True),
    ent_names.ada_exit_lca:   CVHoDisTransitionData(0x4A5CEC, 0x84A5D04, 0x0000, 0x0130, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.lca_exit_ada, ent_names.adb_exit_lcb,
                                                    AreaNames.AQUEDUCT, TransitionNames.LC_AD, True),
    ent_names.ada_exit_cra:   CVHoDisTransitionData(0x4A627C, 0x84A6288, 0x0110, 0x0000, ERGroups.RIGHT_A,
                                                    0x8F, 0x8F, ent_names.cra_exit_ada, ent_names.adb_exit_crb,
                                                    AreaNames.AQUEDUCT, TransitionNames.AD_CR, True),
    ent_names.cra_exit_ada:   CVHoDisTransitionData(0x4A9CA8, 0x84A9CCC, 0x0000, 0x0260, ERGroups.LEFT_A,
                                                    0x8F, 0x8F, ent_names.ada_exit_cra, ent_names.crb_exit_adb,
                                                    AreaNames.CLOCK, TransitionNames.AD_CR, True),
    ent_names.cra_exit_swa:   CVHoDisTransitionData(0x4A9614, 0x84A9650, 0x0000, 0x0230, ERGroups.LEFT_A,
                                                    0x67, 0x67, ent_names.swa_exit_cra, ent_names.crb_exit_swb,
                                                    AreaNames.CLOCK, TransitionNames.SW_CR, True),
    ent_names.tfa_exit_cda:   CVHoDisTransitionData(0x49F280, 0x849F28C, 0x0110, 0x0130, ERGroups.RIGHT_MK_A,
                                                    0x67, 0x67, ent_names.cda_exit_tfa, ent_names.tfb_exit_cdb,
                                                    AreaNames.TOP, TransitionNames.CD_TF, True),
    ent_names.tfa_exit_cya:   CVHoDisTransitionData(0x49F4F8, 0x849F504, 0x0000, 0x0560, ERGroups.BOTTOM_A,
                                                    0xA3, 0x8F, ent_names.cya_exit_tfa, ent_names.tfb_exit_cyb,
                                                    AreaNames.TOP, TransitionNames.CY_TF, False),
    ent_names.tfa_exit_mca:   CVHoDisTransitionData(0x49F570, 0x849F588, 0x0000, 0x0130, ERGroups.LEFT_SKULL_A,
                                                    0x67, 0x67, ent_names.mca_exit_tfa, ent_names.tfb_exit_mcb,
                                                    AreaNames.TOP, TransitionNames.MC_TF, True),
    # Castle B
    ent_names.etb_exit_sab:   CVHoDisTransitionData(0x49A344, 0x849A350, 0x0410, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.sab_exit_etb, ent_names.eta_exit_saa,
                                                    AreaNames.ENTRANCE, TransitionNames.ET_SA, True),
    ent_names.etb_exit_mcb:   CVHoDisTransitionData(0x49A028, 0x849A034, 0x0210, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.mcb_exit_etb, ent_names.eta_exit_mca,
                                                    AreaNames.ENTRANCE, TransitionNames.ET_MC, True),
    ent_names.etb_exit_scb:   CVHoDisTransitionData(0x49A404, 0x849A410, 0x0000, 0x0660, ERGroups.BOTTOM_B,
                                                    0xA3, 0x8F, ent_names.scb_exit_etb, ent_names.eta_exit_sca,
                                                    AreaNames.ENTRANCE, TransitionNames.ET_SC, False),
    ent_names.mcb_exit_etb:   CVHoDisTransitionData(0x49BE80, 0x849BE98, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.etb_exit_mcb, ent_names.mca_exit_eta,
                                                    AreaNames.MARBLE, TransitionNames.ET_MC, True),
    ent_names.mcb_exit_rib_l: CVHoDisTransitionData(0x49C62C, 0x849C638, 0x0000, 0x0130, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.rib_exit_mcb_l, ent_names.mca_exit_ria_l,
                                                    AreaNames.MARBLE, TransitionNames.MC_RI_L, False),
    ent_names.mcb_exit_rib_r: CVHoDisTransitionData(0x49C620, 0x849C638, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.rib_exit_mcb_r, ent_names.mca_exit_ria_r,
                                                    AreaNames.MARBLE, TransitionNames.MC_RI_R, False),
    ent_names.mcb_exit_wwb:   CVHoDisTransitionData(0x49C59C, 0x849C5A8, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.wwb_exit_mcb, ent_names.mca_exit_wwa,
                                                    AreaNames.MARBLE, TransitionNames.MC_WW, True),
    ent_names.mcb_exit_tfb:   CVHoDisTransitionData(0x49C518, 0x849C524, 0x0210, 0x0000, ERGroups.RIGHT_SKULL_B,
                                                    0x67, 0x67, ent_names.tfb_exit_mcb, ent_names.mca_exit_tfa,
                                                    AreaNames.MARBLE, TransitionNames.MC_TF, True),
    ent_names.rib_exit_mcb_l: CVHoDisTransitionData(0x49C748, 0x849C754, 0x0210, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.mcb_exit_rib_l, ent_names.ria_exit_mca_l,
                                                    AreaNames.ROOM, TransitionNames.MC_RI_L, False),
    ent_names.rib_exit_mcb_r: CVHoDisTransitionData(0x49C6B8, 0x849C6D0, 0x0000, 0x0030, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.mcb_exit_rib_r, ent_names.ria_exit_mca_r,
                                                    AreaNames.ROOM, TransitionNames.MC_RI_R, False),
    ent_names.wwb_exit_mcb:   CVHoDisTransitionData(0x49E0BC, 0x849E0D4, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.mcb_exit_wwb, ent_names.wwa_exit_mca,
                                                    AreaNames.WAILING, TransitionNames.MC_WW, True),
    ent_names.wwb_exit_cyb:   CVHoDisTransitionData(0x49E400, 0x849E40C, 0x0110, 0x0000, ERGroups.RIGHT_SKULL_B,
                                                    0x67, 0x67, ent_names.cyb_exit_wwb, ent_names.wwa_exit_cya,
                                                    AreaNames.WAILING, TransitionNames.WW_CY, True),
    ent_names.wwb_exit_sab:   CVHoDisTransitionData(0x49E478, 0x849E484, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.sab_exit_wwb, ent_names.wwa_exit_saa,
                                                    AreaNames.WAILING, TransitionNames.WW_SA, False),
    ent_names.sab_exit_wwb:   CVHoDisTransitionData(0x49E4FC, 0x849E508, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.wwb_exit_sab, ent_names.saa_exit_wwa,
                                                    AreaNames.SHRINE, TransitionNames.WW_SA, False),
    ent_names.sab_exit_etb:   CVHoDisTransitionData(0x49E7A4, 0x849E7BC, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.etb_exit_sab, ent_names.saa_exit_eta,
                                                    AreaNames.SHRINE, TransitionNames.ET_SA, True),
    ent_names.cyb_exit_scb:   CVHoDisTransitionData(0x4AE9A4, 0x84AE9BC, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.scb_exit_cyb, ent_names.cya_exit_sca,
                                                    AreaNames.TREASURY, TransitionNames.CY_SC, True),
    ent_names.cyb_exit_lcb:   CVHoDisTransitionData(0x4AE8F0, 0x84AE920, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.lcb_exit_cyb, ent_names.cya_exit_lca,
                                                    AreaNames.TREASURY, TransitionNames.CY_LC, True),
    ent_names.cyb_exit_wwb:   CVHoDisTransitionData(0x4AED20, 0x84AED44, 0x0000, 0x0000, ERGroups.LEFT_SKULL_B,
                                                    0x67, 0x67, ent_names.wwb_exit_cyb, ent_names.cya_exit_wwa,
                                                    AreaNames.TREASURY, TransitionNames.WW_CY, True),
    ent_names.cyb_exit_tfb:   CVHoDisTransitionData(0x4AED2C, 0x84AED44, 0x0200, 0x0000, ERGroups.TOP_B,
                                                    0x9F, 0x1F, ent_names.tfb_exit_cyb, ent_names.cya_exit_tfa,
                                                    AreaNames.TREASURY, TransitionNames.CY_TF, False),
    ent_names.scb_exit_cyb:   CVHoDisTransitionData(0x4A1B10, 0x84A1B1C, 0x0000, 0x0030, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.cyb_exit_scb, ent_names.sca_exit_cya,
                                                    AreaNames.SKELETON, TransitionNames.CY_SC, True),
    ent_names.scb_exit_etb:   CVHoDisTransitionData(0x4A2210, 0x84A2228, 0x0108, 0x0000, ERGroups.TOP_B,
                                                    0x9F, 0x1F, ent_names.etb_exit_scb, ent_names.sca_exit_eta,
                                                    AreaNames.SKELETON, TransitionNames.ET_SC, False),
    ent_names.lcb_exit_cyb:   CVHoDisTransitionData(0x4A45A4, 0x84A45B0, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.cyb_exit_lcb, ent_names.lca_exit_cya,
                                                    AreaNames.LUMINOUS, TransitionNames.CY_LC, True),
    ent_names.lcb_exit_adb:   CVHoDisTransitionData(0x4A47F0, 0x84A47FC, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.adb_exit_lcb, ent_names.lca_exit_ada,
                                                    AreaNames.LUMINOUS, TransitionNames.LC_AD, True),
    ent_names.swb_exit_cdb:   CVHoDisTransitionData(0x4A8740, 0x84A8758, 0x0000, 0x0000, ERGroups.LEFT_B,
                                                    0x7F, 0x7F, ent_names.cdb_exit_swb, ent_names.swa_exit_cda,
                                                    AreaNames.WALKWAY, TransitionNames.SW_CD, False),
    ent_names.swb_exit_crb:   CVHoDisTransitionData(0x4A8BE4, 0x84A8BF0, 0x0000, 0x0130, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.crb_exit_swb, ent_names.swa_exit_cra,
                                                    AreaNames.WALKWAY, TransitionNames.SW_CR, True),
    ent_names.swb_exit_adb:   CVHoDisTransitionData(0x4A8DF4, 0x84A8E0C, 0x0008, 0x0000, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.adb_exit_swb, ent_names.swa_exit_ada,
                                                    AreaNames.WALKWAY, TransitionNames.SW_AD, True),
    ent_names.cdb_exit_swb:   CVHoDisTransitionData(0x4A86C8, 0x84A86D4, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x7F, 0x7F, ent_names.swb_exit_cdb, ent_names.cda_exit_swa,
                                                    AreaNames.CHAPEL, TransitionNames.SW_CD, False),
    ent_names.cdb_exit_tfb:   CVHoDisTransitionData(0x4A84A0, 0x84A84B8, 0x0000, 0x0130, ERGroups.LEFT_MK_B,
                                                    0x67, 0x67, ent_names.tfb_exit_cdb, ent_names.cda_exit_tfa,
                                                    AreaNames.CHAPEL, TransitionNames.CD_TF, True),
    ent_names.adb_exit_swb:   CVHoDisTransitionData(0x4A6B3C, 0x84A6B48, 0x0000, 0x0030, ERGroups.RIGHT_B,
                                                    0x67, 0x67, ent_names.swb_exit_adb, ent_names.ada_exit_swa,
                                                    AreaNames.AQUEDUCT, TransitionNames.SW_AD, True),
    ent_names.adb_exit_lcb:   CVHoDisTransitionData(0x4A6800, 0x84A6818, 0x0000, 0x0130, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.lcb_exit_adb, ent_names.ada_exit_lca,
                                                    AreaNames.AQUEDUCT, TransitionNames.LC_AD, True),
    ent_names.adb_exit_crb:   CVHoDisTransitionData(0x4A6D7C, 0x84A6D88, 0x0110, 0x0000, ERGroups.RIGHT_B,
                                                    0x8F, 0x8F, ent_names.crb_exit_adb, ent_names.ada_exit_cra,
                                                    AreaNames.AQUEDUCT, TransitionNames.AD_CR, True),
    ent_names.crb_exit_adb:   CVHoDisTransitionData(0x4AB6B4, 0x84AB6D8, 0x0000, 0x0260, ERGroups.LEFT_B,
                                                    0x8F, 0x8F, ent_names.adb_exit_crb, ent_names.cra_exit_ada,
                                                    AreaNames.CLOCK, TransitionNames.AD_CR, True),
    ent_names.crb_exit_swb:   CVHoDisTransitionData(0x4AB004, 0x84AB040, 0x0000, 0x0230, ERGroups.LEFT_B,
                                                    0x67, 0x67, ent_names.swb_exit_crb, ent_names.cra_exit_swa,
                                                    AreaNames.CLOCK, TransitionNames.SW_CR, True),
    ent_names.tfb_exit_cdb:   CVHoDisTransitionData(0x49FF90, 0x849FF9C, 0x0110, 0x0130, ERGroups.RIGHT_MK_B,
                                                    0x67, 0x67, ent_names.cdb_exit_tfb, ent_names.tfa_exit_cda,
                                                    AreaNames.TOP, TransitionNames.CD_TF, True),
    ent_names.tfb_exit_cyb:   CVHoDisTransitionData(0x4A020C, 0x84A0218, 0x0000, 0x0560, ERGroups.BOTTOM_B,
                                                    0xA3, 0x8F, ent_names.cyb_exit_tfb, ent_names.tfa_exit_cya,
                                                    AreaNames.TOP, TransitionNames.CY_TF, False),
    ent_names.tfb_exit_mcb:   CVHoDisTransitionData(0x4A0284, 0x84A029C, 0x0000, 0x0130, ERGroups.LEFT_SKULL_B,
                                                    0x67, 0x67, ent_names.mcb_exit_tfb, ent_names.tfa_exit_mca,
                                                    AreaNames.TOP, TransitionNames.MC_TF, True),
}

SORTED_TRANSITIONS = [transition for transition in SHUFFLEABLE_TRANSITIONS]
VERTICAL_SHAFT_EXITS = [ent_names.eta_exit_sca, ent_names.etb_exit_scb]

NORMAL_ENTRANCE_DESTINATIONS: dict[str, str] = {
    # Castle A
    ent_names.eta_exit_saa: reg_names.saa_end,
    ent_names.eta_exit_mca: reg_names.mca,
    ent_names.eta_warp_u: reg_names.etb_main,
    ent_names.eta_cstone_ul: reg_names.eta_sub,
    ent_names.eta_warp_l: reg_names.etb_sub,
    ent_names.eta_cstone_ur: reg_names.eta_main,
    ent_names.eta_cstone_ll: reg_names.eta_sub_bottom,
    ent_names.eta_exit_sca: reg_names.sca_left,
    ent_names.eta_cstone_lr: reg_names.eta_sub,
    ent_names.mca_exit_eta: reg_names.eta_main,
    ent_names.mca_exit_ria_l: reg_names.ria_left,
    ent_names.mca_exit_ria_r: reg_names.ria_right,
    ent_names.mca_exit_wwa: reg_names.wwa,
    ent_names.mca_exit_tfa: reg_names.tfa_sjumps,
    ent_names.ria_exit_mca_l: reg_names.mca,
    ent_names.ria_exit_mca_r: reg_names.mca,
    ent_names.ria_slide_r: reg_names.ria_right_slide,
    ent_names.ria_slide_l: reg_names.ria_right,
    ent_names.ria_portal: reg_names.rt_portal,
    ent_names.wwa_exit_mca: reg_names.mca,
    ent_names.wwa_exit_cya: reg_names.cya_upper,
    ent_names.wwa_exit_saa: reg_names.saa_main,
    ent_names.saa_exit_wwa: reg_names.wwa,
    ent_names.saa_button: reg_names.saa_end,
    ent_names.saa_exit_eta: reg_names.eta_main,
    ent_names.cya_warp: reg_names.cyb_lower,
    ent_names.cya_exit_sca: reg_names.sca_right,
    ent_names.cya_exit_lca: reg_names.lca_main,
    ent_names.cya_djumps: reg_names.cya_upper,
    ent_names.cya_room: reg_names.the_room,
    ent_names.cya_exit_wwa: reg_names.wwa,
    ent_names.cya_exit_tfa: reg_names.tfa_lower,
    ent_names.cya_down: reg_names.cya_lower,
    ent_names.sca_exit_cya: reg_names.cya_lower,
    ent_names.sca_crates_r: reg_names.sca_left,
    ent_names.sca_exit_eta: reg_names.eta_sub_bottom,
    ent_names.sca_crates_l: reg_names.sca_right,
    ent_names.lca_exit_cya: reg_names.cya_lower,
    ent_names.lca_warp: reg_names.lcb_main,
    ent_names.lca_floodgate: reg_names.lca_death,
    ent_names.lca_talos: reg_names.lca_talos,
    ent_names.lca_sjump_l: reg_names.lca_top,
    ent_names.lca_exit_ada: reg_names.ada_lower,
    ent_names.lca_sjump_r: reg_names.lca_main,
    ent_names.swa_portal: reg_names.lw_portal,
    ent_names.swa_djump_p: reg_names.swa_main,
    ent_names.swa_exit_cda: reg_names.swa_dark_exit,
    ent_names.swa_down_p: reg_names.swa_portal,
    ent_names.swa_devil: reg_names.swa_right_exit,
    ent_names.swa_goggles_u: reg_names.swa_dark,
    ent_names.swa_exit_cra: reg_names.cra_pendulums,
    ent_names.swa_djump_c: reg_names.swa_main,
    ent_names.swa_dark_d: reg_names.swa_dark_exit,
    ent_names.swa_dark_u: reg_names.swa_main,
    ent_names.swa_exit_ada: reg_names.ada_top,
    ent_names.swa_goggles_l: reg_names.swa_dark,
    ent_names.cda_exit_swa: reg_names.swa_main,
    ent_names.cda_djump: reg_names.cda_upper,
    ent_names.cda_exit_tfa: reg_names.tfa_throne,
    ent_names.cda_down: reg_names.cda_lower,
    ent_names.ada_exit_swa: reg_names.swa_dark_exit,
    ent_names.ada_down_u: reg_names.ada_main,
    ent_names.ada_djump_l: reg_names.ada_top,
    ent_names.ada_cstone_r: reg_names.ada_lower,
    ent_names.ada_djump_r: reg_names.ada_merman,
    ent_names.ada_exit_lca: reg_names.lca_top,
    ent_names.ada_cstone_l: reg_names.ada_main,
    ent_names.ada_exit_cra: reg_names.cra_lower_exit,
    ent_names.ada_down_m: reg_names.ada_main,
    ent_names.cra_exit_ada: reg_names.ada_merman,
    ent_names.cra_djump_l: reg_names.cra_lower,
    ent_names.cra_down_door: reg_names.cra_lower_exit,
    ent_names.cra_button: reg_names.cra_pendulums,
    ent_names.cra_exit_swa: reg_names.swa_right_exit,
    ent_names.cra_djump_p: reg_names.cra_main,
    ent_names.cra_down: reg_names.cra_pendulums,
    ent_names.cra_slide: reg_names.cra_ball,
    ent_names.cra_slimer_l: reg_names.cra_slimer,
    ent_names.cra_slimer_r: reg_names.cra_main,
    ent_names.cra_warp: reg_names.crb_peeper,
    ent_names.tfa_exit_cda: reg_names.cda_upper,
    ent_names.tfa_cstone_r: reg_names.tfa_throne,
    ent_names.tfa_warp: reg_names.tfb_throne,
    ent_names.tfa_cboots: reg_names.tfa_attic,
    ent_names.tfa_cstone_l: reg_names.tfa_throne_door,
    ent_names.tfa_pazuzu: reg_names.tfa_lydie,
    ent_names.tfa_button: reg_names.tfa_middle,
    ent_names.tfa_down: reg_names.tfa_lower,
    ent_names.tfa_exit_cya: reg_names.cya_upper,
    ent_names.tfa_sjump_r: reg_names.tfa_sjumps,
    ent_names.tfa_exit_mca: reg_names.mca,
    ent_names.tfa_sjump_l: reg_names.tfa_lower,

    # Castle B
    ent_names.etb_exit_sab: reg_names.sab_end,
    ent_names.etb_exit_mcb: reg_names.mcb,
    ent_names.etb_warp_u: reg_names.eta_main,
    ent_names.etb_cstone_ul: reg_names.etb_sub,
    ent_names.etb_warp_l: reg_names.eta_sub,
    ent_names.etb_cstone_ur: reg_names.etb_main,
    ent_names.etb_cstone_ll: reg_names.etb_sub_bottom,
    ent_names.etb_exit_scb: reg_names.scb_left_exit,
    ent_names.etb_cstone_lr: reg_names.etb_sub,
    ent_names.mcb_exit_etb: reg_names.etb_main,
    ent_names.mcb_exit_rib_l: reg_names.rib_left,
    ent_names.mcb_exit_rib_r: reg_names.rib_right,
    ent_names.mcb_exit_wwb: reg_names.wwb,
    ent_names.mcb_exit_tfb: reg_names.tfb_sjumps,
    ent_names.rib_exit_mcb_l: reg_names.mcb,
    ent_names.rib_exit_mcb_r: reg_names.mcb,
    ent_names.wwb_exit_mcb: reg_names.mcb,
    ent_names.wwb_exit_cyb: reg_names.cyb_upper,
    ent_names.wwb_exit_sab: reg_names.sab_main,
    ent_names.sab_exit_wwb: reg_names.wwb,
    ent_names.sab_cyclops_r: reg_names.sab_end,
    ent_names.sab_cyclops_l: reg_names.sab_main,
    ent_names.sab_exit_etb: reg_names.etb_main,
    ent_names.cyb_portal: reg_names.rt_portal,
    ent_names.cyb_warp: reg_names.cya_lower,
    ent_names.cyb_exit_scb: reg_names.scb_main,
    ent_names.cyb_exit_lcb: reg_names.lcb_main,
    ent_names.cyb_djump: reg_names.cyb_upper,
    ent_names.cyb_room: reg_names.the_room,
    ent_names.cyb_exit_wwb: reg_names.wwb,
    ent_names.cyb_exit_tfb: reg_names.tfb_lower,
    ent_names.cyb_down: reg_names.cyb_lower,
    ent_names.scb_exit_cyb: reg_names.cyb_lower,
    ent_names.scb_rock: reg_names.scb_left_exit,
    ent_names.scb_exit_etb: reg_names.etb_sub_bottom,
    ent_names.lcb_exit_cyb: reg_names.cyb_lower,
    ent_names.lcb_portal: reg_names.lw_portal,
    ent_names.lcb_sjump_l: reg_names.lcb_top,
    ent_names.lcb_exit_adb: reg_names.adb_lower,
    ent_names.lcb_sjump_r: reg_names.lcb_main,
    ent_names.swb_exit_cdb: reg_names.cdb_lower,
    ent_names.swb_legion: reg_names.swb_right_exit,
    ent_names.swb_down: reg_names.swb_mirrors,
    ent_names.swb_exit_crb: reg_names.crb_pendulums,
    ent_names.swb_djump_c: reg_names.swb_main,
    ent_names.swb_exit_adb: reg_names.adb_top,
    ent_names.swb_djump_m: reg_names.swb_main,
    ent_names.cdb_exit_swb: reg_names.swb_main,
    ent_names.cdb_djump: reg_names.cdb_upper,
    ent_names.cdb_exit_tfb: reg_names.tfb_throne,
    ent_names.cdb_down: reg_names.cdb_lower,
    ent_names.adb_exit_swb: reg_names.swb_mirrors,
    ent_names.adb_down_u: reg_names.adb_main,
    ent_names.adb_djump_l: reg_names.adb_top,
    ent_names.adb_cstone_r: reg_names.adb_lower,
    ent_names.adb_djump_r: reg_names.adb_merman,
    ent_names.adb_exit_lcb: reg_names.lcb_top,
    ent_names.adb_cstone_l: reg_names.adb_main,
    ent_names.adb_exit_crb: reg_names.crb_lower_exit,
    ent_names.adb_down_m: reg_names.adb_main,
    ent_names.crb_exit_adb: reg_names.adb_merman,
    ent_names.crb_djump_l: reg_names.crb_lower,
    ent_names.crb_down_door: reg_names.crb_lower_exit,
    ent_names.crb_abutton_b: reg_names.crb_pendulums,
    ent_names.crb_exit_swb: reg_names.swb_right_exit,
    ent_names.crb_abutton_t: reg_names.crb_lower,
    ent_names.crb_djump_p: reg_names.crb_main,
    ent_names.crb_down: reg_names.crb_pendulums,
    ent_names.crb_peep_l: reg_names.crb_peeper,
    ent_names.crb_peep_r: reg_names.crb_main,
    ent_names.crb_slide: reg_names.crb_ball,
    ent_names.crb_warp: reg_names.cra_slimer,
    ent_names.tfb_exit_cdb: reg_names.cdb_upper,
    ent_names.tfb_warp: reg_names.tfa_throne,
    ent_names.tfb_cboots: reg_names.tfb_attic,
    ent_names.tfb_abutton_t: reg_names.tfb_middle,
    ent_names.tfb_abutton_b: reg_names.tfb_throne,
    ent_names.tfb_down: reg_names.tfb_lower,
    ent_names.tfb_exit_cyb: reg_names.cyb_upper,
    ent_names.tfb_sjump_r: reg_names.tfb_sjumps,
    ent_names.tfb_exit_mcb: reg_names.mcb,
    ent_names.tfb_sjump_l: reg_names.tfb_lower,

    # Misc.
    ent_names.rt_portal_exit_r: reg_names.ria_right_slide,
    ent_names.rt_portal_exit_t: reg_names.cyb_lower,
    ent_names.lw_portal_exit_l: reg_names.lcb_main,
    ent_names.lw_portal_exit_w: reg_names.swa_portal
}

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

def invert_castle_transitions(world: "CVHoDisWorld") -> tuple[dict[str: bool], dict[str: bool]]:
    """Figures out which area transitions link across the two castles.
    Returns a dict of every transition name mapped to either True or False. Transitions with True are the ones that should be changed to go to their other castle-equivalent destination."""
    inverted_transitions = {transition: False for transition in SHUFFLEABLE_TRANSITIONS}
    inverted_groups = {}

    # If Castle Swapper is set to Areas, invert the Areas at random.
    if world.options.castle_swapper.value == CastleSwapper.option_areas:
        # Don't pick up the sub Areas if Area Divisions is set to Doors Only.
        inverted_groups = {area_name: False for area_name in AreaNames if area_name not in SUB_MAIN_AREAS.keys() or
                           world.options.area_divisions == AreaDivisions.option_all_transitions}
        # Loop over each Area name (barring Entrance) and roll a 50/50 chance. If it succeeds, consider that Area
        # swapped.
        for area in inverted_groups:
            if world.random.randint(0, 1) and area != AreaNames.ENTRANCE:
                inverted_groups[area] = True

        # If Death is our Castle Warp Condition, and Clock Tower is inverted, we'll need to ensure at least one keyhole
        # portal set goes across the slot's castles. If not, the slot could very well be unwinnable.
        if world.options.castle_warp_condition == CastleWarpCondition.option_death and inverted_groups[AreaNames.CLOCK]:
            # Check the main areas the portals are in if Area Divisions are Doors Only, or the sub areas if not.
            if world.options.area_divisions == AreaDivisions.option_doors_only:
                portal_1_areas = [AreaNames.MARBLE, AreaNames.TREASURY]
                portal_2_areas = [AreaNames.LUMINOUS, AreaNames.CHAPEL]
            else:
                portal_1_areas = [AreaNames.ROOM, AreaNames.TREASURY]
                portal_2_areas = [AreaNames.LUMINOUS, AreaNames.WALKWAY]

            # If one portal area is inverted but not the other, then that keyhole portal does not go across castles.
            # If neither go across castles, invert/un-invert one of the four portal areas at random.
            if (inverted_groups[portal_1_areas[0]] and not inverted_groups[portal_1_areas[1]] or
                    not inverted_groups[portal_1_areas[0]] and inverted_groups[portal_1_areas[1]]) and \
                    (inverted_groups[portal_2_areas[0]] and not inverted_groups[portal_2_areas[1]] or
                     not inverted_groups[portal_2_areas[0]] and inverted_groups[portal_2_areas[1]]):
                area_to_flip = world.random.choice([portal_1_areas[0], portal_1_areas[1],
                                                    portal_2_areas[0], portal_2_areas[1]])
                inverted_groups[area_to_flip] = True if not inverted_groups[area_to_flip] else False

        # Now loop over every shuffleable transition and check to see if it should be inverted based on what we know
        # about the castle Areas.
        for trans_name, trans_data in SHUFFLEABLE_TRANSITIONS.items():
            # Take the main area of both this transition and the destination transition if Area Divisions is set to
            # Doors Only, or the sub areas if set to All Transitions.
            trans_area = trans_data.area
            trans_dest_area = SHUFFLEABLE_TRANSITIONS[trans_data.destination_transition].area
            if world.options.area_divisions == AreaDivisions.option_doors_only:
                if trans_area in SUB_MAIN_AREAS:
                    trans_area = SUB_MAIN_AREAS[trans_area]
                if trans_dest_area in SUB_MAIN_AREAS:
                    trans_dest_area = SUB_MAIN_AREAS[trans_dest_area]
            # If we're going from a non-inverted Area to an inverted Area, or vice versa, invert the transition by
            # setting the boolean mapped to it to True. Otherwise, leave it at False.
            if not all([inverted_groups[trans_area], inverted_groups[trans_dest_area]]) and \
                    any([inverted_groups[trans_area], inverted_groups[trans_dest_area]]):
                inverted_transitions[trans_name] = True

    # If Castle Swapper is set to Transitions, invert each individual set of transitions at random.
    elif world.options.castle_swapper.value == CastleSwapper.option_transitions:
        # Don't pick up the sub Transitions if Area Divisions is set to Doors Only.
        inverted_groups = {trans_name: False for trans_name in TransitionNames if trans_name not in SUB_TRANSITIONS or
                           world.options.area_divisions == AreaDivisions.option_all_transitions}
        # Loop over each transition group name and roll a 50/50 chance. If it succeeds, consider that transition group
        # swapped.
        for trans_group in inverted_groups:
            if world.random.randint(0, 1):
                inverted_groups[trans_group] = True

        # Now loop over every shuffleable transition and check if its associated transition group is inverted.
        # If it is, invert just that singular transition; all four transitions in the group will be hit eventually.
        for trans_name, trans_data in SHUFFLEABLE_TRANSITIONS.items():
            # Don't ever invert non-door transitions if Area Divisions is set to Doors Only.
            if world.options.area_divisions == AreaDivisions.option_doors_only and not trans_data.is_door:
                continue
            if inverted_groups[trans_data.trans_group]:
                inverted_transitions[trans_name] = True

    return inverted_transitions, inverted_groups

def get_er_group(trans_name: str, options: CVHoDisOptions, inverted_groups: dict[str, bool]) -> int:
    """Gets the ERe ER Group of a given Transition for ER purposes. Will return the group of its other castle transition
    if the Entrance's area/transition group is inverted."""

    # If Castle Swapper is Areas, check to see if the Entrance's Area is inverted.
    if options.castle_swapper == CastleSwapper.option_areas:
        # Take the main area of this Entrance if Area Divisions is set to Doors Only, or the sub area if set to
        # All Transitions.
        trans_area = SHUFFLEABLE_TRANSITIONS[trans_name].area
        if options.area_divisions == AreaDivisions.option_doors_only:
            if trans_area in SUB_MAIN_AREAS:
                trans_area = SUB_MAIN_AREAS[trans_area]
        # If the Entrance's Area is inverted, return its other castle transition's ER Group.
        if inverted_groups[trans_area]:
            return SHUFFLEABLE_TRANSITIONS[SHUFFLEABLE_TRANSITIONS[trans_name].other_castle_transition].er_group
    # If Castle Swapper is Transitions, and the Entrance is not a non-door transition while Area Divisions is Doors
    # Only, check to see if the Entrance's transition group is inverted.
    elif options.castle_swapper == CastleSwapper.option_transitions and \
            (SHUFFLEABLE_TRANSITIONS[trans_name].is_door or
             options.area_divisions == AreaDivisions.option_all_transitions):
        # If the Entrance's transition group is inverted, return its other castle transition's ER Group.
        if inverted_groups[SHUFFLEABLE_TRANSITIONS[trans_name].trans_group]:
            return SHUFFLEABLE_TRANSITIONS[SHUFFLEABLE_TRANSITIONS[trans_name].other_castle_transition].er_group

    # If we make it all the way here, meaning no inverted area/transition condition was satisfied, return the Entrance's
    # regular ER Group.
    return SHUFFLEABLE_TRANSITIONS[trans_name].er_group

def verify_entrances(entrances: list[str], inverted_transitions: dict[str, bool]) -> dict[str, str]:
    """Verifies which Entrances in a given list should be created. A dict will be returned with verified Entrance names
    mapped to their destination Region names, ready to be created with Region.add_exits."""
    verified_entrances = {}

    for ent_name in entrances:
        # Check if the Entrance is in the mapping of Entrances to destination Regions.
        # If it isn't, throw an error and don't add it.
        if ent_name not in NORMAL_ENTRANCE_DESTINATIONS:
            logging.error(f"The Entrance \"{ent_name}\" is not in NORMAL_ENTRANCE_DESITNATIONS. "
                          f"Please add it to create it properly.")
            continue

        # If the Entrance is in the inverted transitions mapping, check its entry there to see if we should be getting
        # its corresponding destination Region in the other castle.
        if ent_name in inverted_transitions and ent_name in SHUFFLEABLE_TRANSITIONS:
            # If inverted, get the destination Region of the Entrance's equivalent other castle Entrance instead of its
            # regular destination Region.
            if inverted_transitions[ent_name]:
                destination = NORMAL_ENTRANCE_DESTINATIONS[
                    SHUFFLEABLE_TRANSITIONS[ent_name].other_castle_transition]
            # If the transition Entrance was not inverted, get its destination Region from the normal Entrance
            # destinations like normal.
            else:
                destination = NORMAL_ENTRANCE_DESTINATIONS[ent_name]
        # If it was not in the inverted transitions mapping, get its destination Region from the normal Entrance
        # destinations.
        else:
            destination = NORMAL_ENTRANCE_DESTINATIONS[ent_name]

        verified_entrances.update({destination: ent_name})

    return verified_entrances

def cvhodis_on_connect(er_state: ERPlacementState, placed_exits: list[Entrance],
                       paired_entrances: list[Entrance]) -> bool:
    """Additional GER behavior specific to Castlevania HoD after an Entrance is connected."""
    # TODO: Finish implementing this with some GER-related fixes.

    # If Castle Symmetry is on and Castle Swapper is not set to Transitions, connect the same exit in the other castle
    # to the same corresponding area.
    if er_state.world.options.castle_swapper.value == CastleSwapper.option_transitions or \
            not er_state.world.options.castle_symmetry:
        return False

    other_castle_exit = er_state.world.multiworld.get_entrance(
        SHUFFLEABLE_TRANSITIONS[placed_exits[0].name].other_castle_transition, er_state.world.player)
    other_castle_target = er_state.entrance_lookup.find_target(
        SHUFFLEABLE_TRANSITIONS[paired_entrances[0].name].other_castle_transition)

    er_state.connect(other_castle_exit, other_castle_target)

    return True
