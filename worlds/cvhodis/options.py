from dataclasses import dataclass
from Options import OptionGroup, Choice, Range, Toggle, PerGameCommonOptions, StartInventoryPool, DeathLink,\
    DefaultOnToggle


class MediumEndingRequired(Toggle):
    """
    Whether watching the medium ending (defeat Maxim in Castle A) is required for goal completion.
    """
    display_name = "Medium Ending Required"


class WorstEndingRequired(Toggle):
    """
    Whether watching the worst ending (defeat Maxim in Castle B with JB's and MK's Bracelets unequipped) is required for goal completion.
    """
    display_name = "Worst Ending Required"


class BestEndingRequired(DefaultOnToggle):
    """
    Whether watching the best ending (defeat Maxim in Castle B with JB's and MK's Bracelets equipped) is required for goal completion.
    Will be forced on if no other goal requirement is enabled.
    """
    display_name = "Best Ending Required"


class FurnitureAmountRequired(Range):
    """
    How many pieces of furniture are required to be found and set for goal completion. Furniture will be irrelevant if set to 0.
    """
    range_start = 0
    range_end = 31
    default = 0
    display_name = "Furniture Amount Required"


class MapPercentRequired(Range):
    """
    What percentage of the map visited is required for goal completion.
    """
    range_start = 0
    range_end = 200
    default = 0
    display_name = "Map Percent Required"


class EarlyLizard(DefaultOnToggle):
    """
    Ensures you will find Lizard Tail in the multiworld's Sphere 1 somewhere, making the harder paths out less likely.
    """
    display_name = "Early Lizard"


class SpellboundBossLogic(Choice):
    """
    Makes certain bosses that are considered "medium" or "hard" in difficulty logically expect spell books to get past. See the Game Page for information on which bosses are considered what difficulty.
    None: No boss expects any number of spell books.
    Easy: Medium bosses expect 2 spell books and hard bosses expect 3 spell books.
    Normal: Medium bosses expect 1 spell book and hard bosses expect 2 spell books.
    """
    display_name = "Spellbound Boss Logic"
    option_none = 0
    option_easy = 1
    option_normal = 2
    default = 2


class CastleWarpCondition(Choice):
    """
    The condition for allowing usage of all the warp room round gates to travel between castles.
    None: No condition; the gates are all usable from the beginning.
    Bracelet: The gates will unlock upon finding JB's Bracelet. There's no need to equip it.
    Death: The gates will unlock after talking to Death at Clock Tower A like in the vanilla game.
    """
    display_name = "Castle Warp Condition"
    option_none = 0
    option_bracelet = 1
    option_death = 2
    default = 1


class AreaShuffle(Choice):
    """
    Randomizes where every transition to a different named area leads.
    Separate: Both castles will have their areas kept separate from each other.
    Combined: Both castles will have their areas mixed together, creating a singular, massive castle.
    """
    display_name = "Area Shuffle"
    option_none = 0
    option_separate = 1
    option_combined = 2
    default = 0


class DecoupleTransitions(Toggle):
    """
    Whether transition entrances should be decoupled from exits if Area Shuffle is enabled. Going back through an area transition will send you somewhere completely different from whence you came.
    """
    display_name = "Decouple Transitions"


class CastleSymmetry(DefaultOnToggle):
    """
    Whether randomized transitions should lead to the same corresponding area in both castles, if Area Shuffle is set to Separate.
    """
    display_name = "Castle Symmetry"


class AreaSwapper(Toggle):
    """
    Swaps areas between the two castles at random. Does not apply if Area Shuffle is set to Combined.
    """
    display_name = "Area Swapper"


class LinkDoorTypes(Toggle):
    """
    Whether special door types should only be linked with each other (all skull doors link to other skull doors and all MK's Bracelet doors link to other MK's Bracelet doors).
    """
    display_name = "Link Door Types"


class DoubleSidedWarps(DefaultOnToggle):
    """
    Allows changing castles at a round warp gate without needing to fulfill the cross-castle warp condition if the warp rooms on both sides of it have been reached independently of each other.
    """
    display_name = "Double-Sided Warps"


class Countdown(Choice):
    """
    Displays, below and near the right side of the MP bar, the number of un-found progression/useful-marked items or the total check locations remaining in the area you are currently in.
    """
    display_name = "Countdown"
    option_none = 0
    option_majors = 1
    option_all_locations = 2
    default = 0


class SubWeaponShuffle(Toggle):
    """
    Randomizes which sub-weapon candles have which sub-weapons.
    The total available count of each sub-weapon will be consistent with that of the vanilla game.
    """
    display_name = "Sub-weapon Shuffle"


class NerfGriffinWing(Toggle):
    """
    Initially nerfs the Griffin Wing by removing its ability to jump infinitely until the Sylph Feather is obtained.
    """
    display_name = "Nerf Griffin Wing"


@dataclass
class CVHoDisOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    medium_ending_required: MediumEndingRequired
    worst_ending_required: WorstEndingRequired
    best_ending_required: BestEndingRequired
    furniture_amount_required: FurnitureAmountRequired
    # map_percent_requirement: MapPercentRequirement
    # countdown: Countdown
    # sub_weapon_shuffle: SubWeaponShuffle
    # nerf_griffin_wing: NerfGriffinWing
    area_shuffle: AreaShuffle
    decouple_transitions: DecoupleTransitions
    castle_symmetry: CastleSymmetry
    link_door_types: LinkDoorTypes
    early_lizard: EarlyLizard
    spellbound_boss_logic: SpellboundBossLogic
    castle_warp_condition: CastleWarpCondition
    death_link: DeathLink
    double_sided_warps: DoubleSidedWarps


cvhodis_option_groups = [
    OptionGroup("goal requirements", [
        MediumEndingRequired, WorstEndingRequired, BestEndingRequired, FurnitureAmountRequired,
        # MapPercentRequired
    ]),
    OptionGroup("entrance randomizer", [
        AreaShuffle, DecoupleTransitions, CastleSymmetry, LinkDoorTypes]),
    OptionGroup("difficulty", [
        EarlyLizard, SpellboundBossLogic, CastleWarpCondition, DeathLink]),
    OptionGroup("quality of life", [
        DoubleSidedWarps,
    #    Countdown
    ])
]
