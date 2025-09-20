import logging

from BaseClasses import Item, ItemClassification
from .data import item_names
from .locations import CVLOD_LOCATIONS_INFO
from .options import DraculasCondition, SpareKeys
from .data.enums import Items, Pickups

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from . import CVLoDWorld


class CVLoDItem(Item):
    game: str = "Castlevania - Legacy of Darkness"


class CVLoDItemData(NamedTuple):
    item_id: int
    pickup_id: int
    default_classification: ItemClassification = ItemClassification.filler
# "item_id" = The in-game ID to pass to the in-game "prepare item textbox" function to grant that Item to the player
#             in-game amongst other stuff, as well as its AP Item ID.
# "pickup_id" = The in-game ID for the pickup actor version of the item. Sometimes this is the same as the regular
#               item ID used everywhere else, other times it differs. Namely, the sub-weapon pickups are in a different
#               order from their items, and the gold bag pickups are before the keys instead of after.
# "default_classification" = The AP Item Classification that gets assigned to instances of that Item in create_item
#                            by default, unless deliberately overridden.


ALL_CVLOD_ITEMS = {
    item_names.jewel_rs:          CVLoDItemData(Items.RED_JEWEL_S.value, Pickups.RED_JEWEL_S),
    item_names.jewel_rl:          CVLoDItemData(Items.RED_JEWEL_L.value, Pickups.RED_JEWEL_L),
    item_names.special1:          CVLoDItemData(Items.SPECIAL1.value, Pickups.SPECIAL1,
                                                ItemClassification.progression_deprioritized_skip_balancing),
    item_names.special2:          CVLoDItemData(Items.SPECIAL2.value, Pickups.SPECIAL2,
                                                ItemClassification.progression_deprioritized_skip_balancing),
    item_names.use_chicken:       CVLoDItemData(Items.ROAST_CHICKEN.value, Pickups.ROAST_CHICKEN),
    item_names.use_beef:          CVLoDItemData(Items.ROAST_BEEF.value, Pickups.ROAST_BEEF),
    item_names.use_kit:           CVLoDItemData(Items.HEALING_KIT.value, Pickups.HEALING_KIT,
                                                ItemClassification.useful),
    item_names.use_purifying:     CVLoDItemData(Items.PURIFYING.value, Pickups.PURIFYING),
    item_names.use_ampoule:       CVLoDItemData(Items.CURE_AMPOULE.value, Pickups.CURE_AMPOULE),
    item_names.powerup:           CVLoDItemData(Items.POWERUP.value, Pickups.POWERUP),
    item_names.permaup:           CVLoDItemData(Items.POWERUP.value | 0x100, Pickups.POWERUP,
                                                ItemClassification.useful),
    item_names.sub_knife:         CVLoDItemData(Items.KNIFE.value, Pickups.KNIFE),
    item_names.sub_holy:          CVLoDItemData(Items.HOLY_WATER.value, Pickups.HOLY_WATER),
    item_names.sub_cross:         CVLoDItemData(Items.CROSS.value, Pickups.CROSS),
    item_names.sub_axe:           CVLoDItemData(Items.AXE.value, Pickups.AXE),
    item_names.quest_nitro:       CVLoDItemData(Items.MAGICAL_NITRO.value, Pickups.MAGICAL_NITRO,
                                                ItemClassification.progression),
    item_names.quest_mandragora:  CVLoDItemData(Items.MANDRAGORA.value, Pickups.MANDRAGORA,
                                                ItemClassification.progression),
    item_names.use_card_s:        CVLoDItemData(Items.SUN_CARD.value, Pickups.SUN_CARD),
    item_names.use_card_m:        CVLoDItemData(Items.MOON_CARD.value, Pickups.MOON_CARD),
    item_names.quest_winch:       CVLoDItemData(Items.WINCH_LEVER.value, Pickups.WINCH_LEVER,
                                                ItemClassification.progression),
    item_names.quest_diary:       CVLoDItemData(Items.OLDREYS_DIARY.value, Pickups.OLDREYS_DIARY,
                                                ItemClassification.progression),
    item_names.quest_crest_a:     CVLoDItemData(Items.CREST_HALF_A.value, Pickups.CREST_HALF_A,
                                                ItemClassification.progression),
    item_names.quest_crest_b:     CVLoDItemData(Items.CREST_HALF_B.value, Pickups.CREST_HALF_B,
                                                ItemClassification.progression),
    item_names.quest_brooch:      CVLoDItemData(Items.ROSE_BROOCH.value, Pickups.ROSE_BROOCH,
                                                ItemClassification.progression),
    item_names.quest_key_arch:    CVLoDItemData(Items.ARCHIVES_KEY.value, Pickups.ARCHIVES_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_left:    CVLoDItemData(Items.LEFT_TOWER_KEY.value, Pickups.LEFT_TOWER_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_store:   CVLoDItemData(Items.STOREROOM_KEY.value, Pickups.STOREROOM_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_grdn:    CVLoDItemData(Items.GARDEN_KEY.value, Pickups.GARDEN_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_cppr:    CVLoDItemData(Items.COPPER_KEY.value, Pickups.COPPER_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_chbr:    CVLoDItemData(Items.CHAMBER_KEY.value, Pickups.CHAMBER_KEY,
                                                ItemClassification.progression),
    item_names.trap_ice:          CVLoDItemData(Items.EXECUTION_KEY.value, Pickups.EXECUTION_KEY,
                                                ItemClassification.trap),
    item_names.quest_key_deck:    CVLoDItemData(Items.DECK_KEY.value, Pickups.DECK_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_rose:    CVLoDItemData(Items.ROSE_GARDEN_KEY.value, Pickups.ROSE_GARDEN_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_thorn:   CVLoDItemData(Items.THORN_KEY.value, Pickups.THORN_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_clock_c: CVLoDItemData(Items.CLOCKTOWER_KEY_C.value, Pickups.CLOCKTOWER_KEY_C,
                                                ItemClassification.progression),
    item_names.quest_key_clock_d: CVLoDItemData(Items.CLOCKTOWER_KEY_D.value, Pickups.CLOCKTOWER_KEY_D,
                                                ItemClassification.progression),
    item_names.quest_key_art_1:   CVLoDItemData(Items.ART_TOWER_KEY_1.value, Pickups.ART_TOWER_KEY_1,
                                                ItemClassification.progression),
    item_names.quest_key_art_2:   CVLoDItemData(Items.ART_TOWER_KEY_2.value, Pickups.ART_TOWER_KEY_2,
                                                ItemClassification.progression),
    item_names.quest_key_ctrl:    CVLoDItemData(Items.CONTROL_ROOM_KEY.value, Pickups.CONTROL_ROOM_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_wall:    CVLoDItemData(Items.WALL_KEY.value, Pickups.WALL_KEY,
                                                ItemClassification.progression),
    item_names.quest_key_clock_e: CVLoDItemData(Items.CLOCKTOWER_KEY_E.value, Pickups.CLOCKTOWER_KEY_E,
                                                ItemClassification.progression),
    item_names.quest_key_clock_a: CVLoDItemData(Items.CLOCKTOWER_KEY_A.value, Pickups.CLOCKTOWER_KEY_A,
                                                ItemClassification.progression),
    item_names.quest_key_clock_b: CVLoDItemData(Items.CLOCKTOWER_KEY_B.value, Pickups.CLOCKTOWER_KEY_B,
                                                ItemClassification.progression),
    item_names.gold_500:          CVLoDItemData(Items.FIVE_HUNDRED_GOLD.value, Pickups.FIVE_HUNDRED_GOLD),
    item_names.gold_300:          CVLoDItemData(Items.THREE_HUNDRED_GOLD.value, Pickups.THREE_HUNDRED_GOLD),
    item_names.gold_100:          CVLoDItemData(Items.ONE_HUNDRED_GOLD.value, Pickups.ONE_HUNDRED_GOLD)
}

SUB_WEAPON_IDS: dict[str, int] = {item_names.sub_knife: 1,
                                  item_names.sub_holy: 2,
                                  item_names.sub_cross: 3,
                                  item_names.sub_axe: 4}

POSSIBLE_EXTRA_FILLER = [item_names.jewel_rs, item_names.jewel_rl,
                         item_names.gold_500, item_names.gold_300, item_names.gold_100]


def get_item_names_to_ids() -> dict[str, int]:
    return {item: data.item_id for item, data in ALL_CVLOD_ITEMS.items()}


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

        # If the Item we're adding is a PowerUp and Permanent PowerUps are on, add a random extra filler instead.
        # The PermaUps will be added after the initial item pool is created.
        if item_name == item_names.powerup and world.options.permanent_powerups:
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
        replace_filler([world.create_item(item_names.permaup), world.create_item(item_names.permaup)])

    # Check if the total filler is less than the number of Specials we are adding. If it is, then we will need to adjust
    # the Special totals.
    total_specials = world.options.total_special1s.value + world.options.total_special2s.value
    total_filler = len(tier_1_filler) + len(tier_2_filler)
    if total_specials > total_filler:
        # Figure out the new number of S1s and S2s by taking the total filler count and getting the percentages of it
        # that the S1s and S2s consist of in the total Special count. When downsizing this way, the ratio between the
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

    # Add the total Special2s if Dracula's Condition is Special2s (should be 0 if not).
    if world.options.draculas_condition == DraculasCondition.option_specials:
        # If there are 5 or fewer S2s present, then they will not be deprioritized. Otherwise, they will be.
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
