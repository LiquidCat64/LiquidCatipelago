from dataclasses import dataclass
from Options import OptionGroup, Choice, DefaultOnToggle, PerGameCommonOptions, Range, Toggle, TextChoice, FreeText, \
    StartInventoryPool, DeathLink
from .data.enums import StageIDs


class StageLayout(TextChoice):
    """Which stages in the game appear in the slot and in what order.
    Supports creating a custom layout by typing the name of each stage separated by a semicolon.
    Note that because Castle Keep is always at the end, there is no need to specify it. That is, unless you intend to play a slot that is ONLY it...
    Example: Room of Clocks;Art Tower;Foggy Lake creates a layout of Room of Clocks followed by Art Tower followed by Foggy Lake.
    If Villa branches are enabled, the next 2, 3, or 5 non-Castle Center stages in the list after Villa will represent the branching path stages.
    Example: Villa;Forest of Silence;Foggy Lake;Clock Tower;Castle Wall;Duel Tower results in Villa followed by Forest of Silence on branch 1, Foggy Lake on branch 2, and Clock Tower, Castle Wall, and Duel Tower making up the Cornell path.
    If Castle Center branches are enabled, the next 4 non-Villa stages after Castle Center will represent the branching path stages.
    Example: Castle Center;Tower of Ruins;Tunnel;The Outer Wall;Tower of Science results in Castle Center followed by Tower of Ruins and Tunnel on branch 1, and The Outer Wall and Tower of Science on branch 2."""
    display_name = "Stage Layout"
    option_cornell_only = 0
    option_reinhardt_only = 1
    option_carrie_only = 2
    option_henry_only = 3
    option_reinhardt_carrie = 4
    option_all = 5
    default = 5


class StageShuffle(Toggle):
    """Shuffles which stages appear in which stage slots. Villa and Castle Center will never appear in any character
    stage slots if Character Stages is set to Both; they can only be somewhere on the main path.
    Castle Keep will always be at the end of the line."""
    display_name = "Stage Shuffle"


class ShuffledStartingStage(Choice):
    """Which stage to start at if Stage Shuffle is turned on."""
    display_name = "Shuffled Starting Stage"
    option_foggy_lake = StageIDs.FOGGY.value
    option_forest_of_silence = StageIDs.FOREST.value
    option_castle_wall = StageIDs.C_WALL.value
    option_villa = StageIDs.VILLA.value
    option_the_outer_wall = StageIDs.OUTER.value
    option_tunnel = StageIDs.TUNNEL.value
    option_underground_waterway = StageIDs.WATERWAY.value
    option_castle_center = StageIDs.CENTER.value
    option_art_tower = StageIDs.ART.value
    option_tower_of_ruins = StageIDs.RUINS.value
    option_tower_of_science = StageIDs.SCIENCE.value
    option_duel_tower = StageIDs.DUEL.value
    option_tower_of_execution = StageIDs.EXECUTION.value
    option_tower_of_sorcery = StageIDs.SORCERY.value
    option_room_of_clocks = StageIDs.ROOM.value
    option_clock_tower = StageIDs.CLOCK.value
    default = "random"


class VillaBranchingPaths(Choice):
    """Whether Villa is immediately followed by two diverging stage paths, three diverging stage paths, or three diverging stage paths with the third leading to two more stages that connect directly to the end of Castle Center.
    The latter option is only available if Castle Center is also enabled. If two paths are available, entering the Villa end coffin at day or night will send you to one path or the other.
    If three are available, entering within the following times will send you to path 1, 2, or 3 respectively: 12:01 AM - 8:00 AM, 8:01 AM - 4:00 PM, and 4:01 PM - 12:00 PM."""
    display_name = "Villa Branching Paths"
    option_one = 0
    option_two = 1
    option_three = 2
    option_three_with_cornell_path = 3
    default = 3


class CastleCenterBranchingPaths(Choice):
    """Whether Castle Center is immediately followed by two diverging stage paths of two stages each.
    Both bridges at the end of Castle Center leading to both exits will be intact if Two enabled, or just the ones for Reinhardt or Carrie if a One option is chosen."""
    display_name = "Castle Center Branching Paths"
    option_one_reinhardt = 0
    option_one_carrie = 1
    option_two = 2
    default = 2


class WarpOrder(Choice):
    """Arranges the warps in the Z + R + START warp menu in whichever stage order chosen, thereby affecting the order they are unlocked in.
    Set Order only matters if using a custom Warp Layout; otherwise, Seed Stage Order will be deferred to."""
    display_name = "Warp Order"
    option_set_order = 0
    option_seed_stage_order = 1
    option_vanilla_stage_order = 2
    option_randomized_order = 3
    default = 0


class SubWeaponShuffle(Choice):
    """Shuffles all sub-weapons in the game within each other in their own pool or in the main item pool."""
    display_name = "Sub-weapon Shuffle"
    option_off = 0
    option_own_pool = 1
    option_anywhere = 2
    default = 0


class SpareKeys(Choice):
    """Puts an additional copy of every non-Special key item in the pool for every key item that there is.
    Chance gives each key item a 50% chance of having a duplicate instead of guaranteeing one for all of them."""
    display_name = "Spare Keys"
    option_off = 0
    option_on = 1
    option_chance = 2
    default = 0


class HardItemPool(Toggle):
    """Replaces some items in the item pool with less valuable ones, to make the item pool sort of resemble Hard Mode
    in the PAL version."""
    display_name = "Hard Item Pool"


class TotalRandomWarps(Range):
    """How many randomly-chosen warps to later stages are available. Will be ignored if a custom Warp Layout is being used."""
    display_name = "Total Random Warps"
    range_start = 0
    range_end = 16
    default = 7


class WarpLayout(FreeText):
    """Allows specifying a custom set of warps to be used, rather than it being a specific number of random ones.
    Type the names of each stage that you want to have a warp, separated by a semicolon. The starting stage does not need to be included.
    Example: Castle Center;Duel Tower;The Outer Wall creates warps for Castle Wall, Duel Tower, and The Outer Wall, unlocked in that order if Warp Order is set to Seed Stage Order.
    If left blank or an invalid list is provided, a random selection will be used instead, the number of which can be specified in Total Random Warps."""
    display_name = "Warp Layout"


class Special1sPerWarp(Range):
    """How many Special1 jewels are needed per warp menu option unlock.
    Does not apply if Total Available Warps is 0."""
    range_start = 0
    range_end = 6
    default = 1
    display_name = "Special1s Per Warp"


class TotalSpecial1s(Range):
    """How many Speical1 jewels are available to be found in the multiworld item pool. Will auto-increase to Total Available Warps x Special1s Per Warp if lower."""
    range_start = 0
    range_end = 99
    default = 7
    display_name = "Total Special1s"


class DraculasCondition(Choice):
    """Sets the requirement for unlocking and opening the door to Dracula's chamber.
    None: No requirement. Door is unlocked from the start.
    Crystal: Activate the big crystal in Castle Center's basement. Neither boss afterwards has to be defeated.
    Bosses: Kill a specified number of bosses with health bars and claim their Trophies.
    Specials: Find a specified number of Special2 jewels shuffled in the main item pool."""
    display_name = "Dracula's Condition"
    option_none = 0
    option_crystal = 1
    option_bosses = 2
    option_specials = 3
    default = 1


class PercentSpecial2sRequired(Range):
    """Percentage of Special2s required to enter Dracula's chamber when Dracula's Condition is Special2s."""
    range_start = 1
    range_end = 100
    default = 80
    display_name = "Percent Special2s Required"


class TotalSpecial2s(Range):
    """How many Speical2 jewels are in the pool in total when Dracula's Condition is Special2s."""
    range_start = 1
    range_end = 99
    default = 25
    display_name = "Total Special2s"


class BossesRequired(Range):
    """How many bosses need to be defeated to enter Dracula's chamber when Dracula's Condition is set to Bosses.
    This will automatically adjust if there are fewer available bosses than the chosen number."""
    range_start = 1
    range_end = 25
    default = 23
    display_name = "Bosses Required"


class CarrieLogic(Toggle):
    """Adds the 2 checks inside Underground Waterway's crawlspace to the pool.
    If you (and everyone else if playing the same slot) are planning to only ever play Reinhardt, don't enable this.
    Can be combined with Hard Logic to include Carrie-only tricks."""
    display_name = "Carrie Logic"


class HardLogic(Toggle):
    """Properly considers sequence break tricks in logic (i.e. maze skip). Can be combined with Carrie Logic to include
    Carrie-only tricks.
    See the Game Page for a full list of tricks and glitches that may be logically required."""
    display_name = "Hard Logic"


class MultiHitBreakables(Toggle):
    """Adds the items that drop from the objects that break in three hits to the pool. There are 18 of these throughout
    the game, adding up to 79 or 80 checks (depending on sub-weapons
    being shuffled anywhere or not) in total with all stages.
    The game will be modified to
    remember exactly which of their items you've picked up instead of simply whether they were broken or not."""
    display_name = "Multi-hit Breakables"


class EmptyBreakables(Toggle):
    """Adds 12 check locations in the form of breakables that normally have nothing (all empty Outer Wall torches, etc.)
    and some additional Red Jewels and/or moneybags into the item pool to compensate."""
    display_name = "Empty Breakables"


class LizardLockerItems(Toggle):
    """Adds the 6 items inside Castle Center 2F's Lizard-man generators to the pool.
    Picking up all of these can be a very tedious luck-based process, so they are off by default."""
    display_name = "Lizard Locker Items"


class Shopsanity(Toggle):
    """Adds 7 one-time purchases from Renon's shop into the location pool. After buying an item from a slot, it will
    revert to whatever it is in the vanilla game."""
    display_name = "Shopsanity"


class CastleWallState(Choice):
    """Which character's state Castle Wall should be in. Hybrid will have it be a combination of both Reinhardt/Carrie and Cornell's versions, with both Left Tower Key and Winch Lever required to progress past it."""
    display_name = "Castle Wall State"
    option_reinhardt_carrie = 0
    option_cornell = 1
    option_hybrid = 2
    default = 2


class VillaState(Choice):
    """Which character's state Villa should be in. Hybrid will have it be a combination of both Reinhardt/Carrie and Cornell's versions, with blockages, events, and fights from both.
    Rose Garden Key will be needed to unlock the maze's middle dividing doors."""
    display_name = "Villa State"
    option_reinhardt_carrie = 0
    option_cornell = 1
    option_hybrid = 2
    default = 2


class VillaMazeKid(Choice):
    """Which kid is found and rescued from the maze, regardless of the Villa state."""
    display_name = "Villa Maze Kid"
    option_malus = 0
    option_henry = 1
    default = 0


class ShopPrices(Choice):
    """Randomizes the amount of gold each item costs in Renon's shop.
    Use the below options to control how much or little an item can cost."""
    display_name = "Shop Prices"
    option_vanilla = 0
    option_randomized = 1
    default = 0


class MinimumGoldPrice(Range):
    """The lowest amount of gold an item can cost in Renon's shop, divided by 100."""
    display_name = "Minimum Gold Price"
    range_start = 1
    range_end = 50
    default = 2


class MaximumGoldPrice(Range):
    """The highest amount of gold an item can cost in Renon's shop, divided by 100."""
    display_name = "Maximum Gold Price"
    range_start = 1
    range_end = 50
    default = 30


class PostBehemothBoss(Choice):
    """Sets which boss is fought in the vampire triplets' room in Castle Center after defeating Behemoth."""
    display_name = "Post-Behemoth Boss"
    option_rosa = 0
    option_camilla = 1
    default = "random"

class DuelTowerFinalBoss(Choice):
    """Sets which boss is fought at the fourth Duel Tower arena."""
    display_name = "Duel Tower Final Boss"
    option_were_tiger = 0
    option_giant_werewolf = 1
    default = "random"


class RoomOfClocksBoss(Choice):
    """Sets which boss is fought at Room of Clocks."""
    display_name = "Room of Clocks Boss"
    option_death = 0
    option_actrise = 1
    option_ortega = 2
    default = "random"


class RenonFightCondition(Choice):
    """Sets the condition on which the Renon fight will trigger."""
    display_name = "Renon Fight Condition"
    option_never = 0
    option_spend_30k = 1
    option_always = 2
    default = 1


class VincentFightCondition(Choice):
    """Sets the condition on which the vampire Vincent fight will trigger."""
    display_name = "Vincent Fight Condition"
    option_never = 0
    option_wait_16_days = 1
    option_always = 2
    default = 1


class CastleKeepEndingSequence(Choice):
    """Which character final boss and ending sequence you will go through at Castle Keep upon making it inside Dracula's chamber.
    Reinhardt Carrie Timed = You will receive either their good or bad ending depending on whether you took 16 in-game days to reach Dracula's chamber, regardless of whether you fought Vincent."""
    display_name = "Castle Keep Ending Sequence"
    option_reinhardt_carrie_good = 0
    option_reinhardt_carrie_bad = 1
    option_reinhardt_carrie_timed = 2
    option_cornell = 3
    default = 0


class IncreaseItemLimit(DefaultOnToggle):
    """Increases the holding limit of usable items from 10 to 99 of each item."""
    display_name = "Increase Item Limit"


class NerfHealingItems(Toggle):
    """Decreases the amount of health healed by Roast Chickens to 25%, Roast Beefs to 50%, and Healing Kits to 80%."""
    display_name = "Nerf Healing Items"


class LoadingZoneHeals(DefaultOnToggle):
    """Whether end-of-level loading zones restore health and cure status aliments or not.
    Recommended off for those looking for more of a survival horror experience!"""
    display_name = "Loading Zone Heals"


class InvisibleItems(Choice):
    """Sets which items are visible in their locations and which are invisible until picked up.
    'Chance' gives each item a 50/50 chance of being visible or invisible."""
    display_name = "Invisible Items"
    option_vanilla = 0
    option_reveal_all = 1
    option_hide_all = 2
    option_chance = 3
    default = 0


class DropPreviousSubWeapon(DefaultOnToggle):
    """When receiving a sub-weapon, the one you had before will drop behind you, so it can be taken back if desired. The dropped sub-weapon will retain its level as well."""
    display_name = "Drop Previous Sub-weapon"


class PermanentPowerUps(Toggle):
    """Replaces PowerUps with PermaUps, which upgrade your B weapon level permanently and will stay even after
    dying and/or continuing.
    To compensate, only two will be in the pool overall, and they will not drop from any enemy or projectile."""
    display_name = "Permanent PowerUps"


class IceTrapPercentage(Range):
    """Replaces a percentage of junk items with Ice Traps.
    These will be visibly disguised as other items, and receiving one will freeze you
    as if you were hit by Camilla's ice cloud attack."""
    display_name = "Ice Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0


class IceTrapAppearance(Choice):
    """What items Ice Traps can possibly be disguised as."""
    display_name = "Ice Trap Appearance"
    option_major_only = 0
    option_junk_only = 1
    option_anything = 2
    default = 0


class DisableTimeRestrictions(Choice):
    """Disables the restrictions on some doors and events that require the current time to be within a specific range, so they can be triggered at any time.
    Art Tower Only will only affect the doors in Art Tower, while All will affect every stage with such doors and events.
    In the Villa, this includes the fountain pillar if the Villa State is Reinhardt/Carrie, the meeting with Rosa if the Villa State is Reinhardt/Carrie or Hybrid, and/or the 6AM rose patch if the Villa State is Cornell or Hybrid.
    The Villa end coffin is not affected by this."""
    display_name = "Disable Time Restrictions"
    option_none = 0
    option_art_tower_only = 1
    option_all = 2
    default = 0


class SkipGondolas(Toggle):
    """Makes jumping on and activating a gondola in Tunnel instantly teleport you
    to the other station, thereby skipping the entire three-minute ride.
    The item normally at the gondola transfer point is moved to instead be
    near the red gondola at its station."""
    display_name = "Skip Gondolas"


class SkipWaterwayBlocks(Toggle):
    """Opens the door to the third switch in Underground Waterway from the start so that the jumping across floating
    brick platforms won't have to be done. Shopping at the Contract on the other side of them may still be logically
    required if Shopsanity is on."""
    display_name = "Skip Waterway Blocks"


class Countdown(Choice):
    """Displays, near the HUD clock and below the health bar, the number of unobtained progression items, progression + useful items,
    or the total check locations remaining in the stage or part of the stage you are currently in."""
    display_name = "Countdown"
    option_none = 0
    option_progression_only = 1
    option_progression_useful = 2
    option_all_locations = 3
    default = 0


class BigToss(Toggle):
    """Makes every non-immobilizing damage source launch you as if you got hit by Behemoth's charge.
    Press A while tossed to cancel the launch momentum and avoid being thrown off ledges.
    Hold Z to have all incoming damage be treated as it normally would.
    Any tricks that might be possible with it are NOT considered in logic by any options."""
    display_name = "Big Toss"


class PantherDash(Choice):
    """Hold C-right at any time to sprint way faster. Any tricks that might be
    possible with it are NOT considered in logic by any options and any boss
    fights with boss health meters, if started, are expected to be finished
    before leaving their arenas if Dracula's Condition is bosses. Jumpless will
    prevent jumping while moving at the increased speed to ensure logic cannot be broken with it."""
    display_name = "Panther Dash"
    option_off = 0
    option_on = 1
    option_jumpless = 2
    default = 0


class IncreaseShimmySpeed(Toggle):
    """Increases the speed at which characters shimmy left and right while hanging on ledges."""
    display_name = "Increase Shimmy Speed"


class FallGuard(Toggle):
    """Removes fall damage from landing too hard. Note that falling for too long will still result in instant death."""
    display_name = "Fall Guard"


class BackgroundMusic(Choice):
    """Randomizes or disables the music heard throughout the game.
    Randomized music is split into two pools: songs that loop and songs that don't.
    The "lead-in" versions of some songs will be paired accordingly."""
    display_name = "Background Music"
    option_normal = 0
    option_disabled = 1
    option_randomized = 2
    default = 0


class MapLighting(Choice):
    """Randomizes the lighting color RGB values on every map during every time of day to be literally anything.
    The colors and/or shading of the following things are affected: fog, maps, player, enemies, and some objects."""
    display_name = "Map Lighting"
    option_normal = 0
    option_randomized = 1
    default = 0


class WindowColorR(Range):
    """The red (RR) value for the background color of the text windows during gameplay."""
    display_name = "Window Color R"
    range_start = 0
    range_end = 255
    default = 160


class WindowColorG(Range):
    """The green (GG) value for the background color of the text windows during gameplay."""
    display_name = "Window Color G"
    range_start = 0
    range_end = 255
    default = 160


class WindowColorB(Range):
    """The blue (BB) value for the background color of the text windows during gameplay."""
    display_name = "Window Color B"
    range_start = 0
    range_end = 255
    default = 160


class WindowColorA(Range):
    """The alpha (AA) value for the background color of the text windows during gameplay."""
    display_name = "Window Color A"
    range_start = 0
    range_end = 255
    default = 96


class CVLoDDeathLink(Choice):
    __doc__ = (DeathLink.__doc__ + "\n\n    Explosive: Makes received death links kill you via the Magical Nitro " +
               "explosion instead of the normal death animation.")

    display_name = "Death Link"
    option_off = 0
    alias_no = 0
    alias_true = 1
    alias_yes = 1
    option_on = 1
    option_explosive = 2

@dataclass
class CVLoDOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    stage_layout: StageLayout
    villa_branching_paths: VillaBranchingPaths
    castle_center_branching_paths: CastleCenterBranchingPaths
    stage_shuffle: StageShuffle
    shuffled_starting_stage: ShuffledStartingStage
    warp_layout: WarpLayout
    warp_order: WarpOrder
    total_random_warps: TotalRandomWarps
    special1s_per_warp: Special1sPerWarp
    total_special1s: TotalSpecial1s
    castle_wall_state: CastleWallState
    villa_state: VillaState
    villa_maze_kid: VillaMazeKid
    sub_weapon_shuffle: SubWeaponShuffle
    spare_keys: SpareKeys
    # hard_item_pool: HardItemPool
    draculas_condition: DraculasCondition
    percent_special2s_required: PercentSpecial2sRequired
    total_special2s: TotalSpecial2s
    bosses_required: BossesRequired
    carrie_logic: CarrieLogic
    hard_logic: HardLogic
    multi_hit_breakables: MultiHitBreakables
    empty_breakables: EmptyBreakables
    lizard_locker_items: LizardLockerItems
    # shopsanity: Shopsanity
    # shop_prices: ShopPrices
    # minimum_gold_price: MinimumGoldPrice
    # maximum_gold_price: MaximumGoldPrice
    post_behemoth_boss: PostBehemothBoss
    duel_tower_final_boss: DuelTowerFinalBoss
    room_of_clocks_boss: RoomOfClocksBoss
    renon_fight_condition: RenonFightCondition
    vincent_fight_condition: VincentFightCondition
    castle_keep_ending_sequence: CastleKeepEndingSequence
    increase_item_limit: IncreaseItemLimit
    nerf_healing_items: NerfHealingItems
    loading_zone_heals: LoadingZoneHeals
    invisible_items: InvisibleItems
    drop_previous_sub_weapon: DropPreviousSubWeapon
    permanent_powerups: PermanentPowerUps
    # ice_trap_percentage: IceTrapPercentage
    # ice_trap_appearance: IceTrapAppearance
    disable_time_restrictions: DisableTimeRestrictions
    skip_gondolas: SkipGondolas
    skip_waterway_blocks: SkipWaterwayBlocks
    countdown: Countdown
    # big_toss: BigToss
    # panther_dash: PantherDash
    increase_shimmy_speed: IncreaseShimmySpeed
    # background_music: BackgroundMusic
    # map_lighting: MapLighting
    fall_guard: FallGuard
    window_color_r: WindowColorR
    window_color_g: WindowColorG
    window_color_b: WindowColorB
    window_color_a: WindowColorA
    death_link: CVLoDDeathLink


cvlod_option_groups = [
    OptionGroup("castle wall state", [
        WindowColorR, WindowColorG, WindowColorB, WindowColorA, BackgroundMusic, MapLighting
    ], start_collapsed=True),
    OptionGroup("villa state", [
        WindowColorR, WindowColorG, WindowColorB, WindowColorA, BackgroundMusic, MapLighting
    ], start_collapsed=True),
    OptionGroup("gameplay tweaks", [
        HardItemPool, ShopPrices, MinimumGoldPrice, MaximumGoldPrice, PostBehemothBoss, RoomOfClocksBoss,
        RenonFightCondition, VincentFightCondition, CastleKeepEndingSequence, IncreaseItemLimit, NerfHealingItems,
        LoadingZoneHeals, InvisibleItems, DropPreviousSubWeapon, PermanentPowerUps, IceTrapPercentage,
        IceTrapAppearance, DisableTimeRestrictions, SkipGondolas, SkipWaterwayBlocks, Countdown, BigToss, PantherDash,
        IncreaseShimmySpeed, FallGuard, CVLoDDeathLink
    ]),
    OptionGroup("cosmetics", [
        WindowColorR, WindowColorG, WindowColorB, WindowColorA, BackgroundMusic, MapLighting
    ])
]
