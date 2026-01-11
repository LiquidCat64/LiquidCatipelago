from BaseClasses import ItemClassification, Location
from .options import Countdown
from .locations import CVHODIS_LOCATIONS_INFO, ALT_PICKUP_OFFSETS, GUARDIAN_GRINDER_LOCATIONS
from .items import ALL_CVHODIS_ITEMS
from .cvhodis_text import cvhodis_string_to_bytearray, LEN_LIMIT_DESCRIPTION, DESCRIPTION_DISPLAY_LINES
from .rom import AP_HINT_TEXT_START, START_INVENTORY_USE_START, START_INVENTORY_EQUIP_START, \
    START_INVENTORY_BOOK_START, START_INVENTORY_RELICS_START, START_INVENTORY_FURN_START, START_INVENTORY_WHIPS_START, \
    START_INVENTORY_MAX_START
from .data import item_names
from .data.enums import PickupTypes

from typing import TYPE_CHECKING, Iterable, TypedDict, NamedTuple

if TYPE_CHECKING:
    from . import CVHoDisWorld

FURN_AP_FILLER_INDEX = 0x1F
FURN_AP_USEFUL_INDEX = 0x20
FURN_AP_TRAP_INDEX = 0x21
BOOK_AP_PROGRESSION_INDEX = 0x05
RELIC_AP_PROG_USEFUL_INDEX = 0x0C

MAX_STAT_VALUE = 999
MAX_ITEMS_VALUE = 99
MAX_UP_INCREMENT_VALUE = 5

class CVHoDisInventoryData(NamedTuple):
    main_start_addr: int
    start_inventory_start_addr: int
    length: int
    text_id_start: int
    is_large_textbox: bool
    is_bitfield: bool

# Each pickup type mapped to the following information on its dedicated inventory: Where it starts, where its start
# inventory starts, its size in bytes, what text ID the item name strings start at, whether receiving an item for it
# calls a small or large textbox, and whether it's a bitfield or array of counts.
CVHODIS_INVENTORIES = {
    PickupTypes.USE_ITEM:         CVHoDisInventoryData(0x187A0, START_INVENTORY_USE_START,     28, 0x22, False, False),
    PickupTypes.WHIP_ATTACHMENT:  CVHoDisInventoryData(0x187BC, START_INVENTORY_WHIPS_START,    2, 0x1C, True,  True),
    PickupTypes.EQUIPMENT:        CVHoDisInventoryData(0x187BE, START_INVENTORY_EQUIP_START,  128, 0x47, False, False),
    PickupTypes.RELIC:            CVHoDisInventoryData(0x1883F, START_INVENTORY_RELICS_START,   2, 0xAA, True,  True),
    PickupTypes.SPELLBOOK:        CVHoDisInventoryData(0x1883E, START_INVENTORY_BOOK_START,     1, 0xA5, True,  True),
    PickupTypes.FURNITURE:        CVHoDisInventoryData(0x18843, START_INVENTORY_FURN_START,     4, 0xD8, False, True),
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
                type_byte = PickupTypes.RELIC
                index_byte = RELIC_AP_PROG_USEFUL_INDEX  # Progression + Useful
            elif loc.item.classification & ItemClassification.progression:
                type_byte = PickupTypes.SPELLBOOK
                index_byte = BOOK_AP_PROGRESSION_INDEX  # Progression
            elif loc.item.classification & ItemClassification.useful:
                type_byte = PickupTypes.FURNITURE
                index_byte = FURN_AP_USEFUL_INDEX  # Useful
            elif loc.item.classification & ItemClassification.trap:
                type_byte = PickupTypes.FURNITURE
                index_byte = FURN_AP_TRAP_INDEX  # Trap
            else:
                type_byte = PickupTypes.FURNITURE
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
        location_bytes[CVHODIS_LOCATIONS_INFO[loc.name].offset + 0x5] = bytes([type_byte])
        location_bytes[CVHODIS_LOCATIONS_INFO[loc.name].offset + 0xA] = bytes([index_byte])

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

    inventory_arrays = {
        inv_id: bytearray(CVHODIS_INVENTORIES[inv_id].length) for inv_id in CVHODIS_INVENTORIES
    }
    extra_life = 0
    extra_hearts = 0
    starting_spellbook = 0

    for item in world.multiworld.precollected_items[world.player]:

        type_byte = (item.code >> 8) & 0xFF
        index_byte = item.code & 0xFF

        # If the Item's type byte is a known type of item with an inventory array, handle it here.
        if type_byte in inventory_arrays:
            # If the inventory array is a bitfield, set the bit for that Item in that inventory array.
            if CVHODIS_INVENTORIES[type_byte].is_bitfield:
                inventory_arrays[type_byte][index_byte // 8] |= 1 << (index_byte % 8)
            # Othrwise, meaning it's an array of counts, increment the count at that index if said count is not already
            # the max inventory count.
            else:
                if inventory_arrays[type_byte][index_byte] < MAX_ITEMS_VALUE:
                    inventory_arrays[type_byte][index_byte] += 1
        # If it doesn't have an inventory array, then it must be a Max Up. In which case, handle it accordingly here.
        elif item.name == item_names.max_life:
            if extra_life + 5 < MAX_STAT_VALUE:
                extra_life += MAX_UP_INCREMENT_VALUE
            else:
                extra_life = MAX_STAT_VALUE
        else:
            if extra_hearts + 5 < MAX_STAT_VALUE:
                extra_hearts += MAX_UP_INCREMENT_VALUE
            else:
                extra_life = MAX_STAT_VALUE

        # If the Item is a spell book, set the starting equipped spell book value to that book's index + 1.
        if type_byte == PickupTypes.SPELLBOOK:
            starting_spellbook = index_byte + 1

    # Map the start inventory arrays to their ROM offsets.
    for inv_id, inv_array in inventory_arrays.items():
        start_inventory_data[CVHODIS_INVENTORIES[inv_id].start_inventory_start_addr] = bytes(inv_array)

    # Map the extra starting stats to their offsets as well.
    start_inventory_data[START_INVENTORY_MAX_START] = int.to_bytes(extra_life, 2, "little")
    # MP is not currently supported, but it's here just in case.
    start_inventory_data[START_INVENTORY_MAX_START + 2] = int.to_bytes(0x0000, 2, "little")
    start_inventory_data[START_INVENTORY_MAX_START + 4] = int.to_bytes(extra_hearts, 2, "little")

    # Map the starting spell book value to where it should be as well.
    start_inventory_data[START_INVENTORY_BOOK_START + 1] = int.to_bytes(starting_spellbook, 1, "little")

    return start_inventory_data
