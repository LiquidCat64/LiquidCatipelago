import logging

from BaseClasses import Item, ItemClassification
from .data import item_names
from .data.misc_names import GAME_NAME
from .locations import CVLOD_LOCATIONS_INFO
from .options import SpareKeys, CastleWallState, VillaState, SubWeaponShuffle
from .data.enums import Items, Pickups

from enum import IntFlag
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from . import CVLoDWorld


class CVLoDItem(Item):
    game: str = GAME_NAME

class PickupMiscFlags(IntFlag):
    NONE =         0x00
    SPIN =         0x01  # Makes the pickup spin in place.
    IN_SHOP =      0x40  # Available in Renon's shop. Doesn't actually put the item in Renon's shop, unlike in CV64,
                         # but it's still used on every pickup that would be, sooooooo...
    NO_BILLBOARD = 0x80  # Makes the pickup not turn to face the camera if not spinning. Used on most Cornell quest
                         # items, but only matters for Oldrey's Diary because it's the only one without the Spin flag...

class CVLoDPickupData(NamedTuple):
    item_id: int
    shine_height: int
    dlist_addr: int
    scale: float
    texture_id: int
    color_id: int
    text_pool_id: int
    misc_flags: PickupMiscFlags
    opacity: int = 0xFF
    skip_flag_check: bool = False
# "item_id" = The in-game ID to pass to the in-game "prepare item textbox" function to grant that Item to the player
#             in-game amongst other stuff, as well as its AP Item ID. Sometimes this is the same as the regular pickup 
#             ID used everywhere else, other times it differs. Namely, the sub-weapon pickups are in a different order 
#             from their items, and the gold bag pickups are before the keys instead of after.
# "shine_height" = How many units above the bottom of the pickup the "shine" effect should appear at.
# "dlist_addr" = Where in the file containing the pickup models (Nisitenma-Ichigo file 50) the F3DEX2 display list
#                commands for this pickup's model begins.
# "scale" = The pickup's scale value. The larger the number the larger the model will be in-game.
# "texture_id" = ID for which texture the pickup uses, if multiple are available for the model. 0xFF = not applicable.
#                Only the Sun and Moon Card use this setting properly.
# "color_id" = ID for which color the pickup uses, if multiple are available for the model. 0xFF = not applicable.
# "text_pool_id" = ID for which messages in the item name and description text pools are to be shown for this pickup.
# "misc_flags" = Flags set on the pickup to make it do additional behaviors (spinning, etc.).
# "opacity" = How see through-able the pickup is. The only pickup that doesn't have this set to 100% normally is the
#             unused Engagement Ring from CV64 (not present in this game).
# "skip_flag_check" = Whether the pickup should skip the check for its pickup flag being set upon spawning.

class CVLoDItemData(NamedTuple):
    pickup_id: int
    default_classification: ItemClassification = ItemClassification.filler
# "default_classification" = The AP Item Classification that gets assigned to instances of that Item in create_item
#                            by default, unless deliberately overridden.

CVLOD_PICKUP_INFO = [
    CVLoDPickupData(Items.WHITE_JEWEL.value,        0x32, 0x06005700, 1.0, 0x00, 0x00, 0x00, PickupMiscFlags.SPIN,
                    skip_flag_check=True),
    CVLoDPickupData(Items.RED_JEWEL_S.value,        0x32, 0x06005700, 1.0, 0x00, 0x01, 0x01, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.RED_JEWEL_L.value,        0x46, 0x06005700, 1.3, 0x00, 0x01, 0x02, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.SPECIAL1.value,           0x32, 0x06005700, 1.0, 0x00, 0x02, 0x03, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.SPECIAL2.value,           0x32, 0x06005700, 1.3, 0x00, 0x03, 0x04, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.SPECIAL3.value,           0x32, 0x06005700, 1.0, 0x00, 0x03, 0x05, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.ROAST_CHICKEN.value,      0x1E, 0x060071D8, 1.0, 0xFF, 0xFF, 0x06, PickupMiscFlags.IN_SHOP),
    CVLoDPickupData(Items.ROAST_BEEF.value,         0x28, 0x06006FC8, 1.0, 0xFF, 0xFF, 0x07, PickupMiscFlags.IN_SHOP),
    CVLoDPickupData(Items.HEALING_KIT.value,        0x28, 0x06006B58, 1.0, 0xFF, 0xFF, 0x08, PickupMiscFlags.IN_SHOP),
    CVLoDPickupData(Items.PURIFYING.value,          0x28, 0x06005B28, 1.3, 0xFF, 0xFF, 0x09, PickupMiscFlags.IN_SHOP),
    CVLoDPickupData(Items.CURE_AMPOULE.value,       0x28, 0x060073F8, 1.0, 0xFF, 0xFF, 0x0A, PickupMiscFlags.IN_SHOP),
    CVLoDPickupData(Items.POWERUP.value,            0x28, 0x06008D00, 1.0, 0xFF, 0xFF, 0x0B, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.HOLY_WATER.value,         0x14, 0x06008A58, 2.0, 0xFF, 0xFF, 0x0D, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CROSS.value,              0x14, 0x060068F0, 1.0, 0xFF, 0xFF, 0x0E, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.AXE.value,                0x14, 0x06006050, 1.0, 0xFF, 0xFF, 0x0F, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.KNIFE.value,              0x0A, 0x06008288, 1.0, 0xFF, 0xFF, 0x0C, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.THE_CONTRACT.value,       0x0A, 0x06006358, 1.0, 0xFF, 0xFF, 0x10, PickupMiscFlags.NONE,
                    skip_flag_check=True),
    CVLoDPickupData(Items.MAGICAL_NITRO.value,      0x28, 0x060085F0, 1.0, 0xFF, 0xFF, 0x11, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.MANDRAGORA.value,         0x28, 0x06006D50, 1.0, 0xFF, 0xFF, 0x12, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.SUN_CARD.value,           0x28, 0x060052C8, 1.0, 0x00, 0x00, 0x13,
                    PickupMiscFlags.IN_SHOP|PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.MOON_CARD.value,          0x28, 0x060052C8, 1.0, 0x01, 0x01, 0x14,
                    PickupMiscFlags.IN_SHOP|PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.WINCH_LEVER.value,        0x0A, 0x06009158, 1.0, 0xFF, 0xFF, 0x27,
                    PickupMiscFlags.NO_BILLBOARD|PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.OLDREYS_DIARY.value,      0x14, 0x06005950, 1.0, 0xFF, 0xFF, 0x28,
                    PickupMiscFlags.NO_BILLBOARD),
    CVLoDPickupData(Items.CREST_HALF_A.value,       0x32, 0x06007A78, 0.7, 0xFF, 0xFF, 0x29,
                    PickupMiscFlags.NO_BILLBOARD|PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CREST_HALF_B.value,       0x32, 0x06007E90, 0.7, 0xFF, 0xFF, 0x2A,
                    PickupMiscFlags.NO_BILLBOARD|PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.ROSE_BROOCH.value,        0x0A, 0x06004E30, 1.5, 0xFF, 0xFF, 0x2C, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.FIVE_HUNDRED_GOLD.value,  0x28, 0x06007788, 1.0, 0x00, 0x02, 0x24, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.THREE_HUNDRED_GOLD.value, 0x28, 0x06007788, 1.0, 0x00, 0x01, 0x25, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.ONE_HUNDRED_GOLD.value,   0x28, 0x06007788, 1.0, 0x00, 0x00, 0x26, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.ARCHIVES_KEY.value,       0x1E, 0x060065A8, 1.0, 0x00, 0x00, 0x15, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.LEFT_TOWER_KEY.value,     0x1E, 0x060065A8, 1.0, 0x00, 0x01, 0x16, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.STOREROOM_KEY.value,      0x1E, 0x060065A8, 1.0, 0x00, 0x02, 0x17, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.GARDEN_KEY.value,         0x1E, 0x060065A8, 1.0, 0x00, 0x03, 0x18, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.COPPER_KEY.value,         0x1E, 0x060065A8, 1.0, 0x00, 0x04, 0x19, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CHAMBER_KEY.value,        0x1E, 0x060065A8, 1.0, 0x00, 0x05, 0x1A, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.EXECUTION_KEY.value,      0x1E, 0x060065A8, 1.0, 0x00, 0x06, 0x1B, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.DECK_KEY.value,           0x1E, 0x060065A8, 1.0, 0x00, 0x02, 0x1C, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.ROSE_GARDEN_KEY.value,    0x1E, 0x060065A8, 1.0, 0x00, 0x02, 0x1D, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.THORN_KEY.value,          0x1E, 0x060065A8, 1.0, 0x00, 0x02, 0x1E, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CLOCKTOWER_KEY_C.value,   0x1E, 0x060065A8, 1.0, 0x00, 0x03, 0x1F, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CLOCKTOWER_KEY_D.value,   0x1E, 0x060065A8, 1.0, 0x00, 0x04, 0x20, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.ART_TOWER_KEY_1.value,    0x1E, 0x060065A8, 1.0, 0x00, 0x03, 0x21, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.ART_TOWER_KEY_2.value,    0x1E, 0x060065A8, 1.0, 0x00, 0x04, 0x22, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CONTROL_ROOM_KEY.value,   0x1E, 0x060065A8, 1.0, 0x00, 0x03, 0x23, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.WALL_KEY.value,           0x1E, 0x060065A8, 1.0, 0x00, 0x03, 0x2B, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CLOCKTOWER_KEY_E.value,   0x1E, 0x060065A8, 1.0, 0x00, 0x05, 0x2D, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CLOCKTOWER_KEY_A.value,   0x1E, 0x060065A8, 1.0, 0x00, 0x03, 0x2E, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.CLOCKTOWER_KEY_B.value,   0x1E, 0x060065A8, 1.0, 0x00, 0x04, 0x2F, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.PERMAUP.value,            0x32, 0x06008D00, 1.3, 0xFF, 0xFF, 0x30, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.PERMA_KNIFE.value,         0x0B, 0x06008288, 1.3, 0xFF, 0xFF, 0x31, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.PERMA_WATER.value,         0x16, 0x06008A58, 2.8, 0xFF, 0xFF, 0x32, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.PERMA_CROSS.value,         0x16, 0x060068F0, 1.3, 0xFF, 0xFF, 0x33, PickupMiscFlags.SPIN),
    CVLoDPickupData(Items.PERMA_AXE.value,           0x16, 0x06006050, 1.3, 0xFF, 0xFF, 0x34, PickupMiscFlags.SPIN),
    # item_names.trap_ice:          CVLoDPickupData(Items.EXECUTION_KEY.value, Pickups.EXECUTION_KEY,
    #                                            ItemClassification.trap),
    CVLoDPickupData(Items.AP_FILLER.value,          0x14, 0x0600A520, 1.3, 0xFF, 0xFF, 0x35, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.AP_USEFUL.value,          0x14, 0x0600B690, 1.3, 0xFF, 0xFF, 0x35, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.AP_PROG.value,            0x15, 0x0600ADD8, 1.9, 0xFF, 0xFF, 0x35, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.AP_TRAP.value,            0x25, 0x0600ADD8, 1.9, 0xFF, 0xFF, 0x35, PickupMiscFlags.NONE),
    CVLoDPickupData(Items.AP_PROG_USEFUL.value,     0x15, 0x0600BF48, 1.9, 0xFF, 0xFF, 0x35, PickupMiscFlags.NONE),
]

ALL_CVLOD_ITEMS = {
    item_names.jewel_rs:          CVLoDItemData(Pickups.RED_JEWEL_S),
    item_names.jewel_rl:          CVLoDItemData(Pickups.RED_JEWEL_L),
    item_names.special1:          CVLoDItemData(Pickups.SPECIAL1,
                                                ItemClassification.progression_deprioritized_skip_balancing),
    item_names.special2:          CVLoDItemData(Pickups.SPECIAL2,
                                                ItemClassification.progression_deprioritized_skip_balancing),
    item_names.use_chicken:       CVLoDItemData(Pickups.ROAST_CHICKEN),
    item_names.use_beef:          CVLoDItemData(Pickups.ROAST_BEEF),
    item_names.use_kit:           CVLoDItemData(Pickups.HEALING_KIT, ItemClassification.useful),
    item_names.use_purifying:     CVLoDItemData(Pickups.PURIFYING),
    item_names.use_ampoule:       CVLoDItemData(Pickups.CURE_AMPOULE),
    item_names.powerup:           CVLoDItemData(Pickups.POWERUP),
    item_names.sub_knife:         CVLoDItemData(Pickups.KNIFE),
    item_names.sub_holy:          CVLoDItemData(Pickups.HOLY_WATER),
    item_names.sub_cross:         CVLoDItemData(Pickups.CROSS),
    item_names.sub_axe:           CVLoDItemData(Pickups.AXE),
    item_names.quest_nitro:       CVLoDItemData(Pickups.MAGICAL_NITRO, ItemClassification.progression),
    item_names.quest_mandragora:  CVLoDItemData(Pickups.MANDRAGORA, ItemClassification.progression),
    item_names.use_card_s:        CVLoDItemData(Pickups.SUN_CARD),
    item_names.use_card_m:        CVLoDItemData(Pickups.MOON_CARD),
    item_names.quest_winch:       CVLoDItemData(Pickups.WINCH_LEVER, ItemClassification.progression),
    item_names.quest_diary:       CVLoDItemData(Pickups.OLDREYS_DIARY, ItemClassification.progression),
    item_names.quest_crest_a:     CVLoDItemData(Pickups.CREST_HALF_A, ItemClassification.progression),
    item_names.quest_crest_b:     CVLoDItemData(Pickups.CREST_HALF_B, ItemClassification.progression),
    item_names.quest_brooch:      CVLoDItemData(Pickups.ROSE_BROOCH, ItemClassification.progression),
    item_names.quest_key_arch:    CVLoDItemData(Pickups.ARCHIVES_KEY, ItemClassification.progression),
    item_names.quest_key_left:    CVLoDItemData(Pickups.LEFT_TOWER_KEY, ItemClassification.progression),
    item_names.quest_key_store:   CVLoDItemData(Pickups.STOREROOM_KEY, ItemClassification.progression),
    item_names.quest_key_grdn:    CVLoDItemData(Pickups.GARDEN_KEY, ItemClassification.progression),
    item_names.quest_key_cppr:    CVLoDItemData(Pickups.COPPER_KEY, ItemClassification.progression),
    item_names.quest_key_chbr:    CVLoDItemData(Pickups.CHAMBER_KEY, ItemClassification.progression),
    item_names.quest_key_deck:    CVLoDItemData(Pickups.DECK_KEY, ItemClassification.progression),
    item_names.quest_key_rose:    CVLoDItemData(Pickups.ROSE_GARDEN_KEY, ItemClassification.progression),
    item_names.quest_key_thorn:   CVLoDItemData(Pickups.THORN_KEY, ItemClassification.progression),
    item_names.quest_key_clock_c: CVLoDItemData(Pickups.CLOCKTOWER_KEY_C, ItemClassification.progression),
    item_names.quest_key_clock_d: CVLoDItemData(Pickups.CLOCKTOWER_KEY_D, ItemClassification.progression),
    item_names.quest_key_art_1:   CVLoDItemData(Pickups.ART_TOWER_KEY_1, ItemClassification.progression),
    item_names.quest_key_art_2:   CVLoDItemData(Pickups.ART_TOWER_KEY_2, ItemClassification.progression),
    item_names.quest_key_ctrl:    CVLoDItemData(Pickups.CONTROL_ROOM_KEY, ItemClassification.progression),
    item_names.quest_key_wall:    CVLoDItemData(Pickups.WALL_KEY, ItemClassification.progression),
    item_names.quest_key_clock_e: CVLoDItemData(Pickups.CLOCKTOWER_KEY_E, ItemClassification.progression),
    item_names.quest_key_clock_a: CVLoDItemData(Pickups.CLOCKTOWER_KEY_A, ItemClassification.progression),
    item_names.quest_key_clock_b: CVLoDItemData(Pickups.CLOCKTOWER_KEY_B, ItemClassification.progression),
    item_names.gold_500:          CVLoDItemData(Pickups.FIVE_HUNDRED_GOLD),
    item_names.gold_300:          CVLoDItemData(Pickups.THREE_HUNDRED_GOLD),
    item_names.gold_100:          CVLoDItemData(Pickups.ONE_HUNDRED_GOLD),
    item_names.perma_up:          CVLoDItemData(Pickups.PERMAUP, ItemClassification.useful),
    item_names.perma_knife:       CVLoDItemData(Pickups.PERMA_KNIFE, ItemClassification.useful),
    item_names.perma_water:       CVLoDItemData(Pickups.PERMA_WATER, ItemClassification.useful),
    item_names.perma_cross:       CVLoDItemData(Pickups.PERMA_CROSS, ItemClassification.useful),
    item_names.perma_axe:         CVLoDItemData(Pickups.PERMA_AXE, ItemClassification.useful),
    # item_names.trap_ice:          CVLoDItemData(Items.EXECUTION_KEY.value, Pickups.EXECUTION_KEY,
    #                                            ItemClassification.trap),
}

SUB_WEAPON_IDS: dict[str, int] = {item_names.sub_knife: 1,
                                  item_names.sub_holy: 2,
                                  item_names.sub_cross: 3,
                                  item_names.sub_axe: 4}

POSSIBLE_EXTRA_FILLER = [item_names.jewel_rs, item_names.jewel_rl,
                         item_names.gold_500, item_names.gold_300, item_names.gold_100]

# These Item pickups spawn 3.2 units higher than the other pickups and therefore must be lowered by that amount for
# a few Locations wherein they can spawn barely out of reach.
HIGHER_SPAWNING_ITEMS = [Pickups.CROSS, Pickups.AXE, Pickups.WINCH_LEVER, Pickups.CREST_HALF_A, Pickups.CREST_HALF_B,
                         Pickups.ROSE_BROOCH]

def get_item_names_to_ids() -> dict[str, int]:
    return {item: CVLOD_PICKUP_INFO[data.pickup_id].item_id for item, data in ALL_CVLOD_ITEMS.items()}


def get_item_pool(world: "CVLoDWorld") -> list[CVLoDItem]:
    """Builds the player's entire Item pool based on a number of factors, including what stages are in, what Locations
    are created, and chosen Options."""

    active_locations = world.multiworld.get_unfilled_locations(world.player)

    tier_1_filler = []
    tier_2_filler = []
    non_filler = []

    def replace_filler(replacement_items: [CVLoDItem]) -> None:
        """Replaces filler Items in the already-created Item pool with specified, different Items. Tier 1 filler will
        be replaced first, and then tier 2 when the less valuable tier 1 has run out. If there's no filler left, an
        exception will be raised."""
        nonlocal non_filler, tier_1_filler, tier_2_filler

        for _ in range(len(replacement_items)):
            # If the tier 1 filler list has stuff in it, remove a random Item from it.
            if tier_1_filler:
                del tier_1_filler[world.random.randrange(0, len(tier_1_filler))]
            # If the tier 2 filler list has stuff in it, remove a random Item from it instead.
            elif tier_2_filler:
                del tier_2_filler[world.random.randrange(0, len(tier_2_filler))]
            # Otherwise, if both lists were empty, raise an exception because something went wrong.
            # We should NOT be hitting this to begin with.
            else:
                raise Exception(f"Ran out of replaceable filler for {world.player_name}. "
                                f"Something wasn't handled right...")

        # Add the replacement Item to the non-Filler list.
        non_filler += replacement_items


    total_items = 0
    extras_count = 0

    # Get from each Location its vanilla Item and add it to the item lists.
    for loc in active_locations:
        if loc.address is None:
            continue

        #if world.options.hard_item_pool and get_location_info(loc.name, "hard item") is not None:
        #    item_to_add = get_location_info(loc.name, "hard item")
        #else:
        item_name = CVLOD_LOCATIONS_INFO[loc.name].normal_item

        # If the Item is a Winch Lever, and the Castle Wall State is Reinhardt/Carrie's, add a PowerUp instead because
        # the Winch Lever is useless.
        if item_name == item_names.quest_winch and \
                world.options.castle_wall_state == CastleWallState.option_reinhardt_carrie:
            item_name = item_names.powerup

        # If the Item is Oldrey's Diary, and the Villa State is Reinhardt/Carrie's, add a Purifying instead because
        # Oldrey's Diary is useless.
        if item_name == item_names.quest_diary and world.options.villa_state == VillaState.option_reinhardt_carrie:
            item_name = item_names.use_purifying
        # Similar for the Rose Brooch but adding a Red Jewel (L) instead.
        if item_name == item_names.quest_brooch and world.options.villa_state == VillaState.option_reinhardt_carrie:
            item_name = item_names.jewel_rl

        # If the Item we're adding is a PowerUp and Permanent PowerUps are on, add a random extra filler instead.
        # The PermaUps will be added after the initial item pool is created.
        if item_name == item_names.powerup and world.options.permanent_powerups:
            item_name = world.get_filler_item_name()

        # If the Item we're adding is a sub-weapon and Permanent Sub-weapons is on, add a random extra filler.
        # The Perma weapons will be added after the initial item pool is created.
        if item_name in SUB_WEAPON_IDS and world.options.permanent_sub_weapons:
            item_name = world.get_filler_item_name()

        # Create the Item object.
        item_to_add = world.create_item(item_name)

        # If the Item's classification is Filler, add it to one of the filler lists.
        if item_to_add.classification == ItemClassification.filler:
            # If the Item is a possible extra filler Item, consider it tier 1 filler. When we start modifying the pool,
            # these will be the first replaced in it.
            if item_to_add.name in POSSIBLE_EXTRA_FILLER:
                tier_1_filler.append(item_to_add)
            # Otherwise, consider it tier 2 filler. These filler items are more valuable than mere moneybags and jewels
            # and as such won't be replaced until there's no more tier 1 filler.
            else:
                tier_2_filler.append(item_to_add)
        # Otherwise, if the Item is not filler, add it to the non-filler list.
        else:
            non_filler.append(item_to_add)

    # Add the extra key item copies if Spare Keys is on. Do it now before any Specials or anything else get added, as
    # we check the classification of each individual Item in the non-filler list.
    if world.options.spare_keys:
        extra_copies = []
        for item in non_filler:
            # If the Item has the Progression classification bit set, consider it eligible for duping.
            if item.classification & ItemClassification.progression:
                # If the Spare Keys option is set to Chance, then there will be a 50% chance wherein we don't actually
                # create it after all.
                if world.options.spare_keys == SpareKeys.option_chance and not world.random.randint(0, 1):
                    continue
                extra_copies.append(world.create_item(item.name))
        replace_filler(extra_copies)

    # Add the two PermaUps now if Permanent Powerups is on.
    if world.options.permanent_powerups:
        replace_filler([world.create_item(item_names.perma_up), world.create_item(item_names.perma_up)])

    # Get the total filler amount for the purposes of determining if we can replace existing filler with other Items.
    total_filler = len(tier_1_filler) + len(tier_2_filler)

    # Add the Perma Sub-weapons to the pool if Permanent Sub-weapons is on,
    # and we have enough filler to add all 12 instances.
    if world.options.permanent_sub_weapons:
        perma_weapons = [world.create_item(item_names.perma_knife) for _ in range(3)] + \
                        [world.create_item(item_names.perma_water) for _ in range(3)] + \
                        [world.create_item(item_names.perma_cross) for _ in range(3)] + \
                        [world.create_item(item_names.perma_axe) for _ in range(3)]
        if total_filler > 12:
            replace_filler(perma_weapons)
        # If there is NOT enough filler, push all the weapons as precollected. The slot is very likely a 1 or 2 stage
        # micro slot if we're hitting this, so we might as well let the player just start with them...
        else:
            for weapon in perma_weapons:
                world.push_precollected(weapon)

    # Check if the total filler is less than the number of Specials we are adding. If it is, then we will need to adjust
    # the Special totals. The PANIC adjuster, if you will!
    total_specials = world.options.total_special1s.value + world.options.total_special2s.value
    if total_specials > total_filler:
        # Figure out the new number of S1s and S2s by taking the total filler count and getting the percentages of it
        # that the S1s and S2s consist of in the total Special count. When downscaling this way, the ratio between the
        # two should remain the same.
        new_s1s = int((world.options.total_special1s.value / total_specials * 100) * total_filler // 100)
        new_s2s = int((world.options.total_special2s.value / total_specials * 100) * total_filler // 100)

        # Create the initial part of the warning message.
        special_count_warning = (f"[{world.player_name}] Not enough Locations to accommodate the chosen Total "
                                 f"Special1s and/or Special2s. The following Special counts were adjusted:\n"
                                 f"Total Special1s: {world.options.total_special1s} -> {new_s1s}\n"
                                 f"Total Special2s: {world.options.total_special2s} -> {new_s2s}")

        # Adjust the Special count option values proper.
        world.options.total_special1s.value = new_s1s
        world.options.total_special2s.value = new_s2s

        # Adjust the world's required Special2s to be the specified percentage of the new number.
        world.required_s2s = int(world.options.percent_special2s_required.value / 100 *
                                 world.options.total_special2s.value)

        # If this caused there to be not enough Special1s to unlock every warp, adjust Special1s Per Warp down as well.
        if world.options.special1s_per_warp.value * (len(world.active_warp_list) - 1) > world.options.total_special1s:
            new_s1s_per_warp = world.options.total_special1s // (len(world.active_warp_list) - 1)
            special_count_warning += (f"\nConsequently, Special1s Per Warp also had to be lowered from "
                                      f"{world.options.special1s_per_warp.value} to {new_s1s_per_warp}.")
            world.options.special1s_per_warp.value = new_s1s_per_warp

        # Throw the final warning message.
        logging.warning(special_count_warning)

    # Add the Special1s.
    all_special1s = []
    for _ in range(world.options.total_special1s.value):
        # If Special1s Per Warp is 3 or lower, then the exact necessary amount of S1s needed to unlock the full menu
        # will be marked regular Progression instead of Progression Deprioritized Skip Balancing.
        if world.options.special1s_per_warp.value <= 3 and \
                len(all_special1s) <= world.options.special1s_per_warp.value * (len(world.active_warp_list) - 1):
            all_special1s.append(world.create_item(item_names.special1, ItemClassification.progression))
        else:
            all_special1s.append(world.create_item(item_names.special1))
    replace_filler(all_special1s)

    # Add the total Special2s. If there are 5 or fewer S2s present, then they will not be deprioritized.
    # Otherwise, they will be.
    if world.options.total_special2s <= 5:
        replace_filler([world.create_item(item_names.special2, ItemClassification.progression_skip_balancing)
                        for _ in range(world.options.total_special2s.value)])
    else:
        replace_filler([world.create_item(item_names.special2) for _ in range(world.options.total_special2s.value)])

    # TODO: Actually implement traps.
    # Determine the Ice Trap count by taking a certain % of the total filler remaining at this point.
    #item_counts[ItemClassification.trap][item_names.ice_trap] = math.floor((total_filler_junk + total_non_filler_junk) *
    #                                                 (world.options.ice_trap_percentage.value / 100.0))
    #for i in range(item_counts[ItemClassification.trap][item_names.ice_trap]):
    #    # Subtract the remaining filler after determining the ice trap count.
    #    item_to_subtract = world.random.choice(list(item_counts[ItemClassification.filler].keys()))
    #    item_counts[ItemClassification.filler][item_to_subtract] -= 1
    #    if item_counts[ItemClassification.filler][item_to_subtract] == 0:
    #        del (item_counts[ItemClassification.filler][item_to_subtract])

    # Return the final complete lists of created Item objects.
    return tier_1_filler + tier_2_filler + non_filler
