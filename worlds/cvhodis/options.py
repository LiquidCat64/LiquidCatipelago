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
    early_lizard: EarlyLizard
    death_link: DeathLink


cvhodis_option_groups = [
    OptionGroup("goal requirements", [
        MediumEndingRequired, WorstEndingRequired, BestEndingRequired, FurnitureAmountRequired,
        # MapPercentRequired
    ]),

    OptionGroup("difficulty", [
        EarlyLizard, DeathLink]),
    # OptionGroup("quality of life", [
    #     Countdown])
]
