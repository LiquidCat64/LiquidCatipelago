from BaseClasses import ItemClassification, Location
from .options import Countdown
from .locations import CVHODIS_CHECKS_INFO, ALT_PICKUP_OFFSETS, GUARDIAN_GRINDER_LOCATIONS
from .items import ALL_CVHODIS_ITEMS, PICKUP_TYPE_BOOK, PICKUP_TYPE_RELIC, PICKUP_TYPE_FURN
from .cvhodis_text import cvhodis_string_to_bytearray, LEN_LIMIT_DESCRIPTION, DESCRIPTION_DISPLAY_LINES
from .rom import AP_HINT_TEXT_START
from .data import item_names

from typing import TYPE_CHECKING, Iterable, TypedDict

if TYPE_CHECKING:
    from . import CVHoDisWorld

FURN_AP_FILLER_INDEX = 0x1F
FURN_AP_USEFUL_INDEX = 0x20
FURN_AP_TRAP_INDEX = 0x21
BOOK_AP_PROGRESSION_INDEX = 0x05
RELIC_AP_PROG_USEFUL_INDEX = 0x0C

class StatInfo(TypedDict):
    # Amount this stat increases per Max Up the player starts with.
    amount_per: int
    # The most amount of this stat the player is allowed to start with. Problems arise if the stat  exceeds 9999, so we
    # must ensure it can't if the player raises any class to level 99 as well as collects 255 of that max up. The game
    # caps hearts at 999 automatically, so it doesn't matter so much for that one.
    max_allowed: int
    # The key variable in extra_stats that the stat max up affects.
    variable: str


extra_starting_stat_info: dict[str, StatInfo] = {
    item_names.max_life: {"amount_per": 10,
                          "max_allowed": 5289,
                          "variable": "extra health"},
    item_names.max_heart: {"amount_per": 6,
                           "max_allowed": 999,
                           "variable": "extra hearts"},
}

other_player_subtype_bytes = {
    0xE4: 0x03,
    0xE6: 0x14,
    0xE8: 0x0A
}


class OtherGameAppearancesInfo(TypedDict):
    # What type of item to place for the other player.
    type: int
    # What item to display it as for the other player.
    appearance: int


other_game_item_appearances: dict[str, dict[str, OtherGameAppearancesInfo]] = {
    # NOTE: Symphony of the Night is currently an unsupported world not in main.
    # "Symphony of the Night": {"Life Vessel": {"type": 0xE4,
    #                                           "appearance": 0x01},
    #                           "Heart Vessel": {"type": 0xE4,
    #                                            "appearance": 0x00}},
    # "Timespinner": {"Max HP": {"type": 0xE4,
    #                            "appearance": 0x01},
    #                 "Max Aura": {"type": 0xE4,
    #                              "appearance": 0x02},
    #                 "Max Sand": {"type": 0xE8,
    #                              "appearance": 0x0F}}
}

rom_sub_weapon_offsets = {

}


def shuffle_sub_weapons(world: "CVHoDisWorld") -> dict[int, bytes]:
    """Shuffles the sub-weapons amongst themselves."""
    sub_bytes = list(rom_sub_weapon_offsets.values())
    world.random.shuffle(sub_bytes)
    return dict(zip(rom_sub_weapon_offsets, sub_bytes))


def get_countdown_flags(world: "CVHoDisWorld", active_locations: Iterable[Location]) -> dict[int, bytes]:
    """Figures out which Countdown numbers to increase for each Location after verifying the Item on the Location should
    count towards a number.

    Which number to increase is determined by the Location's "countdown" attr in its CVCotMLocationData."""
    pass


def get_location_data(world: "CVHoDisWorld", active_locations: Iterable[Location]) -> dict[int, bytes]:
    """Gets ALL the Item data to go into the ROM. Items consist of four bytes; the first two represent the object ID
    for the "category" of item that it belongs to, the third is the sub-value for which item within that "category" it
    is, and the fourth controls the appearance it takes."""

    location_bytes = {}

    for loc in active_locations:
        # Figure out the item ID bytes to put in each Location's offset here.
        # If it's a HoD Item, always write the Item's primary type byte.
        # if loc.item.game == "Castlevania - Harmony of Dissonance":
        if loc.item.player == world.player:
            type_byte = (loc.item.code >> 8) & 0xFF

            # If the Item is for this player, set the index to actually be that Item.
            # Otherwise, set a dummy index value that is different for every item type.
            if loc.item.player == world.player:
                index_byte = loc.item.code & 0xFF
            else:
                index_byte = other_player_subtype_bytes[type_byte]

        # If it's not a HoD Item at all, set the type and index bytes to one of the off-world AP Items. Which one to use
        # depends on the Item's classification.
        else:
            # Decide which AP Item to use to represent the other game item.
            if loc.item.classification & ItemClassification.progression and \
                    loc.item.classification & ItemClassification.useful:
                type_byte = PICKUP_TYPE_RELIC
                index_byte = RELIC_AP_PROG_USEFUL_INDEX  # Progression + Useful
            elif loc.item.classification & ItemClassification.progression:
                type_byte = PICKUP_TYPE_BOOK
                index_byte = BOOK_AP_PROGRESSION_INDEX  # Progression
            elif loc.item.classification & ItemClassification.useful:
                type_byte = PICKUP_TYPE_FURN
                index_byte = FURN_AP_USEFUL_INDEX  # Useful
            elif loc.item.classification & ItemClassification.trap:
                type_byte = PICKUP_TYPE_FURN
                index_byte = FURN_AP_TRAP_INDEX  # Trap
            else:
                type_byte = PICKUP_TYPE_FURN
                index_byte = FURN_AP_FILLER_INDEX  # Filler

            # Check if the Item's game is in the other game item appearances' dict, and if so, if the Item is under that
            # game's name. If it is, change the appearance accordingly.
            # Right now, only SotN and Timespinner stat ups are supported.
            other_game_name = world.multiworld.worlds[loc.item.player].game
            if other_game_name in other_game_item_appearances:
                if loc.item.name in other_game_item_appearances[other_game_name]:
                    type_byte = other_game_item_appearances[other_game_name][loc.item.name]["type"]
                    index_byte = other_player_subtype_bytes[type_byte]
                    appearance_byte = other_game_item_appearances[other_game_name][loc.item.name]["appearance"]

        # Create the correct bytes object for the Item on that Location.
        location_bytes[CVHODIS_CHECKS_INFO[loc.name].offset + 0x5] = bytes([type_byte])
        location_bytes[CVHODIS_CHECKS_INFO[loc.name].offset + 0xA] = bytes([index_byte])

        # If the Location has an alternate pickup actor that must also be modified, add the Item bytes by them as well.
        if loc.name in ALT_PICKUP_OFFSETS:
            location_bytes[ALT_PICKUP_OFFSETS[loc.name] + 0x5] = bytes([type_byte])
            location_bytes[ALT_PICKUP_OFFSETS[loc.name] + 0xA] = bytes([index_byte])

        # If the Location is one of the Guardian Armor drops, add the Item bytes by those respective offsets as well.
        if loc.name in GUARDIAN_GRINDER_LOCATIONS:
            location_bytes[GUARDIAN_GRINDER_LOCATIONS[loc.name]] = bytes([type_byte])
            location_bytes[GUARDIAN_GRINDER_LOCATIONS[loc.name] + 0x2] = bytes([index_byte])

    return location_bytes

def get_hint_card_hints(world: "CVHoDisWorld", active_locations: Iterable[Location]) -> dict[int, bytes]:
    """Creates multiworld-specific hint text to go over the in-game descriptions of the six Hint Cards. There are two
    types of hints; one for the whereabouts of the player's own progression items, and the other for progression items
    for other slots that landed in the player's world. Odd-numbered cards will be the former while even-numbered cards
    will be the latter, making for a total of three of each.

    The hints don't tell you the exact Location name, but rather, a Location name group that the Location can be found
    in, which should tell players roughly where to search for it without completely being a free client hint. If the
    Location is in no Location name groups, then it will only mention the name of the slot that has the Item."""

    # Get out all the world's selectable Progression Items
    selectable_prog_items = world.possible_hint_card_items.copy()

    # Get out all the Locations with Progression Items on them that are also not Skip Balancing without Useful.
    selectable_prog_locs = [loc for loc in active_locations if loc.advancement and
                            not (loc.item.classification & ItemClassification.skip_balancing and
                                 not loc.item.classification & ItemClassification.useful)]

    converted_strings = {}

    for card_number in range(1, 7):
        # If the card number is odd, generate a hint for one of this world's Items.
        if card_number % 2:
            # Grab a random non-furniture progression Item that we created and saved earlier.
            own_hint_item = selectable_prog_items.pop(world.random.randrange(len(selectable_prog_items)))

            # If the drawn Item is local in the player's own world, use a blank player name.
            if own_hint_item.location.player == world.player:
                other_player_name = ""
            # Otherwise, get the name of that other player.
            else:
                other_player_name = f"{world.multiworld.get_player_name(own_hint_item.location.player)}'s "

            # Figure out what Location groups in the other player's game the Item's Location is a part of. Don't take
            # the "Everywhere" group as that just includes everything.
            other_world_loc_groups = world.multiworld.worlds[own_hint_item.location.player].location_name_groups
            selectable_loc_groups = [loc_group for loc_group in other_world_loc_groups if own_hint_item.location.name in
                                     other_world_loc_groups[loc_group] and loc_group != "Everywhere"]

            # If no valid group was found, use "world somewhere" as the generic group name.
            if not selectable_loc_groups:
                chosen_loc_group_name = "world somewhere"
            # Otherwise, choose one of our found Location group names at random and build a string with that.
            else:
                chosen_loc_group_name = world.random.choice(selectable_loc_groups)

            # Create the hint text.
            card_hint = f"{own_hint_item.name} is in {other_player_name}{chosen_loc_group_name}.\t"

        # Otherwise, meaning the card number is even, generate a hint for a progression item of a different world.
        else:
            # If we're out of Locations containing significant Progression (if that happens, then...how the heck did
            # this world end up with less than three progression items in it anyway!? There's 200+ Locations, for crying
            # out loud!), make the card hint a message telling the player how barren their world is.
            if not selectable_prog_locs:
                card_hint = "This world is very devoid of progression..."
            # Otherwise, select a Location and continue on as normal.
            else:
                own_hint_loc = selectable_prog_locs.pop(world.random.randrange(len(selectable_prog_locs)))

                # If the Item on the drawn Location is one of this player's own, use a blank player name.
                if own_hint_loc.item.player == world.player:
                    other_player_name = ""
                # Otherwise, get the name of that other player.
                else:
                    other_player_name = f"{world.multiworld.get_player_name(own_hint_loc.item.player)}'s "

                # Figure out what HoD Location group in this player's game the chosen Location is a part of (that is not
                # "Everywhere"). Every HoD Location should be part of only one group, so we take the first list element
                # of our found groups in this case.
                own_loc_group = [loc_group for loc_group in world.location_name_groups if own_hint_loc.name in
                                world.location_name_groups[loc_group] and loc_group != "Everywhere"][0]

                # Create the hint text.
                card_hint = f"{own_loc_group} contains {other_player_name}{own_hint_loc.item.name}.\t"

        # Convert the hint to HoD's text format and map it to its ROM address.
        converted_strings[AP_HINT_TEXT_START + ((card_number - 1) * 0x100)] = bytes(cvhodis_string_to_bytearray(
            card_hint, len_limit=LEN_LIMIT_DESCRIPTION, max_lines=DESCRIPTION_DISPLAY_LINES, textbox_advance=False))

    return converted_strings


def get_start_inventory_data(world: "CVHoDisWorld") -> dict[int, bytes]:
    """Calculate and return the starting inventory arrays. Different items go into different arrays, so they all have
    to be handled accordingly."""
    start_inventory_data = {}

    magic_items_array = [0 for _ in range(8)]
    cards_array = [0 for _ in range(20)]
    extra_stats = {"extra health": 0,
                   "extra magic": 0,
                   "extra hearts": 0}

    # Always start with the Dash Boots.
    magic_items_array[0] = 1

    for item in world.multiworld.precollected_items[world.player]:

        array_offset = item.code & 0xFF

        # If it's a Max Up we're starting with, check if increasing the extra amount of that stat will put us over the
        # max amount of the stat allowed. If it will, set the current extra amount to the max. Otherwise, increase it by
        # the amount that it should.
        if "Max Up" in item.name:
            info = extra_starting_stat_info[item.name]
            if extra_stats[info["variable"]] + info["amount_per"] > info["max_allowed"]:
                extra_stats[info["variable"]] = info["max_allowed"]
            else:
                extra_stats[info["variable"]] += info["amount_per"]
        # If it's a DSS card we're starting with, set that card's value in the cards array.
        elif "Card" in item.name:
            cards_array[array_offset] = 1
        # If it's none of the above, it has to be a regular Magic Item.
        # Increase that Magic Item's value in the Magic Items array if it's not greater than 240. Last Keys are the only
        # Magic Item wherein having more than one is relevant.
        else:
            # Decrease the Magic Item array offset by 1 if it's higher than the unused Map's item value.
            if array_offset > 5:
                array_offset -= 1
            if magic_items_array[array_offset] < 240:
                magic_items_array[array_offset] += 1

    # Add the start inventory arrays to the offset data in bytes form.
    start_inventory_data[0x680080] = bytes(magic_items_array)
    start_inventory_data[0x6800A0] = bytes(cards_array)

    # Add the extra max HP/MP/Hearts to all classes' base stats. Doing it this way makes us less likely to hit the max
    # possible Max Ups.
    # Vampire Killer
    start_inventory_data[0xE08C6] = int.to_bytes(100 + extra_stats["extra health"], 2, "little")
    start_inventory_data[0xE08CE] = int.to_bytes(100 + extra_stats["extra magic"], 2, "little")
    start_inventory_data[0xE08D4] = int.to_bytes(50 + extra_stats["extra hearts"], 2, "little")

    # Magician
    start_inventory_data[0xE090E] = int.to_bytes(50 + extra_stats["extra health"], 2, "little")
    start_inventory_data[0xE0916] = int.to_bytes(400 + extra_stats["extra magic"], 2, "little")
    start_inventory_data[0xE091C] = int.to_bytes(50 + extra_stats["extra hearts"], 2, "little")

    # Fighter
    start_inventory_data[0xE0932] = int.to_bytes(200 + extra_stats["extra health"], 2, "little")
    start_inventory_data[0xE093A] = int.to_bytes(50 + extra_stats["extra magic"], 2, "little")
    start_inventory_data[0xE0940] = int.to_bytes(50 + extra_stats["extra hearts"], 2, "little")

    # Shooter
    start_inventory_data[0xE0832] = int.to_bytes(50 + extra_stats["extra health"], 2, "little")
    start_inventory_data[0xE08F2] = int.to_bytes(100 + extra_stats["extra magic"], 2, "little")
    start_inventory_data[0xE08F8] = int.to_bytes(250 + extra_stats["extra hearts"], 2, "little")

    # Thief
    start_inventory_data[0xE0956] = int.to_bytes(50 + extra_stats["extra health"], 2, "little")
    start_inventory_data[0xE095E] = int.to_bytes(50 + extra_stats["extra magic"], 2, "little")
    start_inventory_data[0xE0964] = int.to_bytes(50 + extra_stats["extra hearts"], 2, "little")

    return start_inventory_data
