from dataclasses import dataclass
from Options import OptionGroup, Choice, Range, Toggle, PerGameCommonOptions, StartInventoryPool, DeathLink,\
    DefaultOnToggle
from .data.enums import SubWeaponPickups


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


class FillerPool(Choice):
    """
    How the item pool should be populated with non-progression equipment and consumables. All other items will always be created no matter what.
    Vanilla = The pool will be filled with what's on each location from the vanilla game always, with a few notable exceptions.
    Mystery = The pool will be filled with random equipment/consumables with varying weights.
    """
    option_vanilla = 0
    option_mystery = 1
    default = 1
    display_name = "Filler Pool"


class AddJBsBracelet(Toggle):
    """
    Adds JB's Bracelet to the item pool, which is required for the best ending and, optionally, activating all round warp gates.
    You will not start with it. Will be forced on if Bracelet Warp Condition is on.
    """
    display_name = "Add JB's Bracelet"


class GateItems(Choice):
    """
    Defines how the 3 one-way switch gates act.
    Normal: Normal behavior. Gates can only be opened by pressing the respective button.
    Add Keys: The same as normal behavior, but also adds keys to the item pool that can open the gate from the other side.
    Buttonsanity: Adds keys to each gate, and the corresponding button will grant a check.

    The following keys correspond to the following gates:
    Living Armor Key -> Shrine A post-Living Armor gate
    Clock Key -> Clock Tower A/B basement gate
    Throne Key -> Top Floor A/B throne room rear gate
    """
    option_normal = 0
    option_add_keys = 1
    option_buttonsanity = 2
    default = 0
    display_name = "Gate Items"


class AddFloatingBoots(Toggle):
    """
    Adds Floating Boots to the item pool. These allow you to float freely in midair and can be logically expected for flight in lieu of the Griffin's Wing.
    The Griffin's Wing is still needed to break ceilings with the Crush Boots.
    """
    display_name = "Add Floating Boots"


class AddInfiniteBoots(Toggle):
    """
    Adds Infinite Boots to the item pool. These allow infinite midair jumps when found along with the Sylph Feather and can be logically expected for flight in lieu of the Griffin's Wing.
    The Griffin's Wing is still needed to break ceilings with the Crush Boots.
    """
    display_name = "Add Infinite Boots"


class AddNoonStar(Toggle):
    """
    Adds the Noon Star to the item pool, which allows shopping at the Merchant's shops in Clock Tower A/B on the path to the ball race.
    """
    display_name = "Add Noon Star"


class StartWithLureKey(Toggle):
    """
    Starts you with the Lure Key in your inventory already. It won't be added to the pool.
    """
    display_name = "Start With Lure Key"


class RemoveFurniture(Toggle):
    """
    Removes all furniture from the pool and replaces them with other random filler. Will be ignored if placing more than 0 furniture is a required goal condition.
    """
    display_name = "Remove Furniture"


class EarlyLizard(Toggle):
    """
    Ensures you will find Lizard Tail in the multiworld's Sphere 1 somewhere, making the harder paths out less likely. Disabling recommended with entrance randomization.
    """
    display_name = "Early Lizard"


class SpellboundBossLogic(Choice):
    """
    Makes certain bosses that are considered "medium" or "hard" in difficulty logically expect spell books to get past. See the Game Page for information on which bosses are considered what difficulty.
    None: No boss expects any number of spell books.
    Normal: Medium bosses expect 1 spell book and hard bosses expect 2 spell books.
    Easy: Medium bosses expect 2 spell books and hard bosses expect 3 spell books.
    """
    display_name = "Spellbound Boss Logic"
    option_none = 0
    option_normal = 1
    option_easy = 2
    default = 1


class CardboundBossLogic(Choice):
    """
    Makes certain bosses that are considered "medium" or "hard" in difficulty logically expect Hint Cards to get past. See the Game Page for information on which bosses are considered what difficulty.
    None: No boss expects any number of spell books.
    Normal: Medium bosses expect 1 Hint Card and hard bosses expect 2 Hint Cards.
    Easy: Medium bosses expect 2 Hint Cards and hard bosses expect 3 Hint Cards.
    """
    display_name = "Cardbound Boss Logic"
    option_none = 0
    option_normal = 1
    option_easy = 2
    default = 1


class CardAmountWarpRequirement(Range):
    """
    How many Hint Cards are required to activate all the warp room round gates to travel between castles.
    Can be mixed with other Warp Requirement options.
    """
    display_name = "Card Amount Warp Requirement"
    range_start = 0
    range_end = 6
    default = 4


class DeathWarpRequirement(Toggle):
    """
    Whether talking to Death at Clock Tower A like in the vanilla game is required to activate all the warp room round gates to travel between castles.
    Can be mixed with other Warp Requirement options.
    """
    display_name = "Death Warp Requirement"


class BraceletWarpRequirement(Toggle):
    """
    Whether finding JB's Bracelet is required to activate all the warp room round gates to travel between castles. There's no need to equip it.
    If this is enabled, Add JB's Bracelet will be forced on as well.
    Can be mixed with other Warp Requirement options.
    """
    display_name = "Bracelet Warp Requirement"


class AreaDivisions(Choice):
    """
    Where the divisions between areas should be considered for the purposes of the map randomization options.
    Areas can be split at either doors only or at every transition to a differently-named place.
    """
    display_name = "Area Divisions"
    option_doors_only = 0
    option_all_transitions = 1
    default = 0


class CastleSwapper(Choice):
    """
    Allows areas or individual transitions between areas to be swapped in the two castles at a 50% random chance.
    If Transition Shuffler is off, areas or transition destinations will be randomly swapped to their equivalent other castle's and be otherwise unchanged.
    If Transition Shuffler is NOT off, this option's choices will affect it in the following ways:
    Off: Castles A and B will be shuffled entirely separately from each other.
    Areas: Castles A and B will be shuffled entirely separately from each other with A and B areas randomly swapped between them.
    Transitions: No castle separation at all; any A or B transition can lead to any A or B area.
    """
    display_name = "Castle Swapper"
    option_off = 0
    option_areas = 1
    option_transitions = 2
    default = 0


class TransitionShuffler(Choice):
    """
    Shuffles where transitions to different areas of the castles lead to. The exact shuffle behavior is affected by other options.
    Off: Transitions will not be shuffled, though they CAN lead to the corresponding area in the other castle if Castle Swapper is enabled.
    Coupled: Returning through a shuffled transition will take you back to where you were before.
    Decoupled: Returning through a shuffled transition will take you somewhere entirely different. This can be very chaotic.
    """
    display_name = "Transition Shuffler"
    option_off = 0
    option_coupled = 1
    option_decoupled = 2
    default = 0


class CastleSymmetry(DefaultOnToggle):
    """
    Whether transitions shuffled with Transition Shuffler should lead to the same corresponding area in both castles. This is not applicable if Castle Swapper is set to Transitions.
    """
    display_name = "Castle Symmetry"


class MapPreset(Choice):
    """
    Option presets that apply specifically to the Castle Swapper, Transition Shuffler, and Castle Symmetry options.
    This is intended for those familiar with the standalone randomizer's map options.
    If you are unsure what these mean, leaving this on None and setting the aforementioned options is recommended; otherwise, you may set only this and ignore the other three.
    The Chaos presets are the regular Area presets but with decoupled transitions (see the Transition Shuffler description).
    If you want it to randomly pick from a specific set of choices, use the choice weight feature.
    """
    display_name = "Map Preset"
    option_none = 0
    option_vanilla = 1
    option_area_single = 2
    option_area_double = 3
    option_area_mix_single = 4
    option_area_mix_double = 5
    option_area_hybrid = 6
    option_mix_vanilla = 7
    option_hybrid_vanilla = 8
    option_chaos_area_single = 9
    option_chaos_area_double = 10
    option_chaos_area_mix_single = 11
    option_chaos_area_mix_double = 12
    option_chaos_area_hybrid = 13
    default = 0


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


class HintCardHints(Toggle):
    """
    Whether the Hint Cards' menu descriptions should contain hints as to the whereabouts of important progression items.
    Odd-numbered cards will contain hints for your own items in other players' worlds, whereas even-numbered cards will tell you where in your world you can find someone else's item.
    In both cases, the area mentioned will be a location group the item's location is in, chosen at random if there's multiple. If the location of your item in someone else's world does not have a location group defined for it, only the player who has it will be specified.
    """
    display_name = "Hint Card Hints"


class Countdown(Choice):
    """Displays, to the right of the HUD health bar, the number of unobtained progression items, progression + useful items,
    or the total check locations remaining in the place you are currently in.

    If Area Divisions is Transitions, every named sub area will have its own count. Otherwise, it'll be one count for the whole area.
    """
    display_name = "Countdown"
    option_none = 0
    option_progression_only = 1
    option_progression_useful = 2
    option_all_locations = 3
    default = 0


class SubWeaponRandomization(Choice):
    """
    Randomizes which sub-weapon candles have which sub-weapons.
    Shuffle keeps the total counts of each weapon roughly equal, mystery does not.
    """
    display_name = "Sub-weapon Randomization"
    option_none = 0
    option_shuffle = 1
    option_mystery = 2


class SubWeaponsAvailable(Range):
    """
    How many Sub-weapon types are available throughout the game. Removed sub-weapons will be replaced with an equal count of others when Sub-weapon Randomization is Shuffle.
    """
    range_start = 1
    range_end = len(SubWeaponPickups)
    default = len(SubWeaponPickups)
    display_name = "Sub-weapons available"


class ProgressiveHeights(Toggle):
    """
    Adds two Progressive Height Relics to the pool instead of the Sylph Feather and Griffin's Wing.
    The first one found will unlock the former Relic and then the second will unlock the latter.
    """
    display_name = "Progressive Heights"


@dataclass
class CVHoDisOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    medium_ending_required: MediumEndingRequired
    worst_ending_required: WorstEndingRequired
    best_ending_required: BestEndingRequired
    furniture_amount_required: FurnitureAmountRequired
    # map_percent_requirement: MapPercentRequirement
    countdown: Countdown
    sub_weapon_randomization: SubWeaponRandomization
    sub_weapons_available: SubWeaponsAvailable
    area_divisions: AreaDivisions
    castle_swapper: CastleSwapper
    transition_shuffler: TransitionShuffler
    map_preset: MapPreset
    castle_symmetry: CastleSymmetry
    link_door_types: LinkDoorTypes
    filler_pool: FillerPool
    progressive_heights: ProgressiveHeights
    gate_items: GateItems
    add_jbs_bracelet: AddJBsBracelet
    add_floating_boots: AddFloatingBoots
    add_infinite_boots: AddInfiniteBoots
    add_noon_star: AddNoonStar
    remove_furniture: RemoveFurniture
    start_with_lure_key: StartWithLureKey
    early_lizard: EarlyLizard
    spellbound_boss_logic: SpellboundBossLogic
    cardbound_boss_logic: CardboundBossLogic
    card_amount_warp_requirement: CardAmountWarpRequirement
    death_warp_requirement: DeathWarpRequirement
    bracelet_warp_requirement: BraceletWarpRequirement
    hint_card_hints: HintCardHints
    death_link: DeathLink
    double_sided_warps: DoubleSidedWarps


cvhodis_option_groups = [
    OptionGroup("Goal Options", [
        MediumEndingRequired, WorstEndingRequired, BestEndingRequired, FurnitureAmountRequired
        # MapPercentRequired
    ]),
    OptionGroup("Entrance Randomization", [
        MapPreset, CastleSwapper, TransitionShuffler, CastleSymmetry, AreaDivisions, LinkDoorTypes
    ]),
    OptionGroup("Castle Warp Requirements", [
        CardAmountWarpRequirement, DeathWarpRequirement, BraceletWarpRequirement
    ]),
    OptionGroup("Item Options", [
        FillerPool, ProgressiveHeights, GateItems, AddJBsBracelet, AddFloatingBoots, AddInfiniteBoots, AddNoonStar,
        RemoveFurniture, StartWithLureKey
    ]),
    OptionGroup("World Options", [
        SpellboundBossLogic, CardboundBossLogic, SubWeaponRandomization, SubWeaponsAvailable, EarlyLizard
    ]),
    OptionGroup("Quality of Life", [
        HintCardHints, DoubleSidedWarps, Countdown
    ]),
]

cvhodis_map_presets: dict[int, tuple[int, int, int]] = {
    MapPreset.option_vanilla:
        (CastleSwapper.option_off,         TransitionShuffler.option_off,       CastleSymmetry.option_false),
    MapPreset.option_area_single:
        (CastleSwapper.option_off,         TransitionShuffler.option_coupled,   CastleSymmetry.option_true),
    MapPreset.option_area_double:
        (CastleSwapper.option_off,         TransitionShuffler.option_coupled,   CastleSymmetry.option_false),
    MapPreset.option_area_mix_single:
        (CastleSwapper.option_areas,       TransitionShuffler.option_coupled,   CastleSymmetry.option_true),
    MapPreset.option_area_mix_double:
        (CastleSwapper.option_areas,       TransitionShuffler.option_coupled,   CastleSymmetry.option_false),
    MapPreset.option_area_hybrid:
        (CastleSwapper.option_transitions, TransitionShuffler.option_coupled,   CastleSymmetry.option_false),
    MapPreset.option_mix_vanilla:
        (CastleSwapper.option_areas,       TransitionShuffler.option_off,       CastleSymmetry.option_false),
    MapPreset.option_hybrid_vanilla:
        (CastleSwapper.option_transitions, TransitionShuffler.option_off,       CastleSymmetry.option_false),
    MapPreset.option_chaos_area_single:
        (CastleSwapper.option_off,         TransitionShuffler.option_decoupled, CastleSymmetry.option_true),
    MapPreset.option_chaos_area_double:
        (CastleSwapper.option_off,         TransitionShuffler.option_decoupled, CastleSymmetry.option_false),
    MapPreset.option_chaos_area_mix_single:
        (CastleSwapper.option_areas,       TransitionShuffler.option_decoupled, CastleSymmetry.option_true),
    MapPreset.option_chaos_area_mix_double:
        (CastleSwapper.option_areas,       TransitionShuffler.option_decoupled, CastleSymmetry.option_false),
    MapPreset.option_chaos_area_hybrid:
        (CastleSwapper.option_transitions, TransitionShuffler.option_decoupled, CastleSymmetry.option_false)
}
