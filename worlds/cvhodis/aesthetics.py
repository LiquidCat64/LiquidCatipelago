from BaseClasses import ItemClassification, Location, Item
#from .options import Countdown
#from .locations import CVHODIS_LOCATIONS_INFO, ALT_PICKUP_OFFSETS, GUARDIAN_GRINDER_LOCATIONS
from .items import FURNITURE, SPELLBOOKS, RELICS, GATE_KEYS, ALL_CVHODIS_ITEMS
#from .cvhodis_text import cvhodis_string_to_bytearray, LEN_LIMIT_DESCRIPTION, DESCRIPTION_DISPLAY_LINES
from .data import item_names
from .data.enums import PickupTypes
from .data.misc_names import GAME_NAME

from typing import TYPE_CHECKING, Iterable, NamedTuple

if TYPE_CHECKING:
    from . import CVHoDisWorld

FURN_AP_FILLER_INDEX = len(FURNITURE)
FURN_AP_USEFUL_INDEX = len(FURNITURE) + 1
FURN_AP_TRAP_INDEX = len(FURNITURE) + 2
BOOK_AP_PROGRESSION_INDEX = len(SPELLBOOKS)
RELIC_AP_PROG_USEFUL_INDEX = len(RELICS)
AP_FILLER_GFX_ID = 0xDF
AP_PROGRESSION_GFX_ID = 0xE0
AP_USEFUL_GFX_ID = 0xE1
AP_PROG_USEFUL_GFX_ID = 0xE2
AP_TRAP_GFX_ID = 0xE3
AP_PALETTE_ID = 0x01  # Same palette for all AP Items.

MAX_MONEY_VALUE = 9999999
MAX_STAT_VALUE = 999
MAX_ITEMS_VALUE = 99
MAX_UP_INCREMENT_VALUE = 5

class CVHoDisInventoryData(NamedTuple):
    main_start_addr: int  # Where the inventory begins in the game's memory.
    length: int  # Size of the inventory in bytes
    text_id_start: int  # The first text ID associated with the names of the items in the inventory.
    is_large_textbox: bool  # Whether collecting an item in this category stops the gameplay and displays a large
                            # textbox in the middle of the screen. Otherwise, the small blue corner textbox is used.
    is_bitfield: bool  # Whether the inventory is a bitfield. If not, it's an array of counts.

# Each pickup type mapped to the following information on its dedicated inventory: Where it starts, where its start
# inventory starts, its size in bytes, what text ID the item name strings start at, whether receiving an item for it
# calls a small or large textbox, and whether it's a bitfield or array of counts.
CVHODIS_INVENTORIES = {
    PickupTypes.USE_ITEM.value:        CVHoDisInventoryData(0x187A0, 28,  0x22, False, False),
    PickupTypes.WHIP_ATTACHMENT.value: CVHoDisInventoryData(0x187BC, 2,   0x1C, True,  True),
    PickupTypes.EQUIPMENT.value:       CVHoDisInventoryData(0x187BE, 128, 0x47, False, False),
    PickupTypes.RELIC.value:           CVHoDisInventoryData(0x1883F, 2,   0xAA, True,  True),
    PickupTypes.SPELLBOOK.value:       CVHoDisInventoryData(0x1883E, 1,   0xA5, True,  True),
    PickupTypes.FURNITURE.value:       CVHoDisInventoryData(0x18843, 4,   0xD8, False, True),
}

class OtherGameAppearancesInfo(NamedTuple):
    # What GFX is used for the Item in-game.
    gfx_id: int
    # What palette is used for the Item in-game.
    palette_id: int

OTHER_GAME_ITEM_APPEARANCES: dict[str, dict[str, OtherGameAppearancesInfo]] = {
    "Symphony of the Night": {"Life Vessel":  OtherGameAppearancesInfo(0x0C, 0x01),
                              "Heart Vessel": OtherGameAppearancesInfo(0x0D, 0x01)},
    "Castlevania - Circle of the Moon": {"HP Max Up":    OtherGameAppearancesInfo(0x0C, 0x01),
                                         "MP Max Up":    OtherGameAppearancesInfo(0x0C, 0x03),
                                         "Heart Max Up": OtherGameAppearancesInfo(0x0D, 0x01)},
    "Castlevania: Portrait of Ruin": {"HP Max up":    OtherGameAppearancesInfo(0x0C, 0x01),
                                      "MP Max up":    OtherGameAppearancesInfo(0x0C, 0x03)},
    "Castlevania: Order of Ecclesia": {"HP Max up":    OtherGameAppearancesInfo(0x0C, 0x01),
                                       "MP Max up":    OtherGameAppearancesInfo(0x0C, 0x03),
                                       "HEART Max up": OtherGameAppearancesInfo(0x0D, 0x01)},
    "Bloodstained: Ritual of the Night": {"MaxHPUP":     OtherGameAppearancesInfo(0x0C, 0x01),
                                          "MaxMPUP":     OtherGameAppearancesInfo(0x0C, 0x03),
                                          "MaxBulletUP": OtherGameAppearancesInfo(0x0D, 0x01)},
    "Timespinner": {"Max HP":   OtherGameAppearancesInfo(0x0C, 0x01),
                    "Max Aura": OtherGameAppearancesInfo(0x0C, 0x03),
                    "Max Sand": OtherGameAppearancesInfo(0x0D, 0x04)},
}

class OtherHoDPlayerPickupInfo(NamedTuple):
    type_value: int
    index_value: int

OTHER_HOD_PLAYER_TYPE_BYTES = {
    PickupTypes.MONEY.value:           OtherHoDPlayerPickupInfo(PickupTypes.FURNITURE, FURN_AP_FILLER_INDEX),
    PickupTypes.SUB_WEAPON.value:      OtherHoDPlayerPickupInfo(PickupTypes.FURNITURE, FURN_AP_FILLER_INDEX),
    PickupTypes.USE_ITEM.value:        OtherHoDPlayerPickupInfo(PickupTypes.FURNITURE, FURN_AP_FILLER_INDEX),
    PickupTypes.WHIP_ATTACHMENT.value: OtherHoDPlayerPickupInfo(PickupTypes.SPELLBOOK, BOOK_AP_PROGRESSION_INDEX),
    PickupTypes.EQUIPMENT.value:       OtherHoDPlayerPickupInfo(PickupTypes.FURNITURE, FURN_AP_FILLER_INDEX),
    PickupTypes.SPELLBOOK.value:       OtherHoDPlayerPickupInfo(PickupTypes.SPELLBOOK, BOOK_AP_PROGRESSION_INDEX),
    PickupTypes.RELIC.value:           OtherHoDPlayerPickupInfo(PickupTypes.RELIC, RELIC_AP_PROG_USEFUL_INDEX),
    PickupTypes.FURNITURE.value:       OtherHoDPlayerPickupInfo(PickupTypes.FURNITURE, FURN_AP_FILLER_INDEX),
    PickupTypes.MAX_UP.value:          OtherHoDPlayerPickupInfo(PickupTypes.FURNITURE, FURN_AP_FILLER_INDEX),
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


def get_location_write_values(world: "CVHoDisWorld", active_locations: Iterable[Location]) -> \
        dict[int, tuple[int, bool]]:
    """Gets ALL the Item data to go into the ROM. Items consist of four main things; the first is the type ID for what
    category of pickup that it belongs to, and the second is the index value for which item within that category it is.
    The third is the GFX ID for the item's sprite, and the fourth is the palette ID; these go in the upper byte and
    nybble of the type and index values respectively."""

    location_values = {}

    for loc in active_locations:
        # Figure out the item ID bytes to put in each Location here.
        # If it's one of the player's own Items, set the type and index values to what they should be in-game.
        if loc.item.player == world.player:
            # The upper byte in the Item's AP ID is the type byte. The lower byte is the index byte.
            type_value = (loc.item.code >> 8) & 0xFF
            index_value = loc.item.code & 0xFF
        # If it's not for this player but still a HoD Item, set the type value to the AP Item-enabled type with the
        # behavior closest to what the Item would be. The reason why different AP Items are different pickup types is
        # because each one has different behavior in-game, which we use to reflect its importance.
        elif loc.item.game == GAME_NAME:
            type_value = OTHER_HOD_PLAYER_TYPE_BYTES[(loc.item.code >> 8) & 0xFF].type_value
            index_value = OTHER_HOD_PLAYER_TYPE_BYTES[(loc.item.code >> 8) & 0xFF].index_value
        # Otherwise, if it's not a HoD Item at all, set the type and index bytes entirely depending on the Item's
        # classification.
        else:
            if loc.item.classification & ItemClassification.progression and \
                    loc.item.classification & ItemClassification.useful:
                type_value = PickupTypes.RELIC  # Displays large center textbox + causes the Item to float.
                index_value = RELIC_AP_PROG_USEFUL_INDEX  # Progression + Useful
            elif loc.item.classification & ItemClassification.progression:
                type_value = PickupTypes.SPELLBOOK  # Displays large center texbox.
                index_value = BOOK_AP_PROGRESSION_INDEX  # Progression
            elif loc.item.classification & ItemClassification.useful:
                type_value = PickupTypes.FURNITURE  # Displays small corner textbox.
                index_value = FURN_AP_USEFUL_INDEX  # Useful
            elif loc.item.classification & ItemClassification.trap:
                type_value = PickupTypes.FURNITURE
                index_value = FURN_AP_TRAP_INDEX  # Trap
            else:
                type_value = PickupTypes.FURNITURE
                index_value = FURN_AP_FILLER_INDEX  # Filler

        # Set the Item's appearance values. If it's an Item for this game, set them to the Item's GFX and Palette values
        # so they will actually show up in-game as that Item.
        if loc.item.game == GAME_NAME:
            type_value |= ALL_CVHODIS_ITEMS[loc.item.name].palette_id << 4
            index_value |= (ALL_CVHODIS_ITEMS[loc.item.name].gfx_id + 1) << 8
        # Otherwise, if it's NOT an Item for this game at all, check if the Item's game is in the other game item
        # appearances' dict, and if so, if the Item is under that game's name. If it is, change the appearance
        # accordingly. These mostly apply to max ups in other games for now.
        else:
            other_game_name = world.multiworld.worlds[loc.item.player].game
            if other_game_name in OTHER_GAME_ITEM_APPEARANCES:
                if loc.item.name in OTHER_GAME_ITEM_APPEARANCES[other_game_name]:
                    type_value |= OTHER_GAME_ITEM_APPEARANCES[other_game_name][loc.item.name].palette_id << 4
                    index_value |= (OTHER_GAME_ITEM_APPEARANCES[other_game_name][loc.item.name].gfx_id + 1) << 8

        # Create the final item info tuple and map it to the Location address.
        location_values[loc.address] = (type_value, index_value)

    # Return the final dict of Location values.
    return location_values

def get_hint_card_hints(world: "CVHoDisWorld", active_locations: Iterable[Location]) -> list[str]:
    """Creates multiworld-specific hint text to go over the in-game descriptions of the six Hint Cards. There are two
    types of hints; one for the whereabouts of the player's own progression items, and the other for progression items
    for other slots that landed in the player's world. Odd-numbered cards will be the former while even-numbered cards
    will be the latter, making for a total of three of each.

    The hints don't tell you the exact Location name, but rather, a Location name group that the Location can be found
    in, which should tell players roughly where to search for it without completely being a free client hint. If the
    Location is in no Location name groups, then it will only mention the name of the slot that has the Item."""

    # If Hint Card Hints are not on, return an empty list. Don't bother creating any card text.
    if not world.options.hint_card_hints:
        return []

    # Get out all the world's selectable Progression Items that have Locations post-generation.
    selectable_prog_items = [item for item in world.possible_hint_card_items if item.location]

    # Get out all the Locations with Progression Items on them that are also not Skip Balancing without Useful.
    selectable_prog_locs = [loc for loc in active_locations if loc.advancement and
                            not (loc.item.classification & ItemClassification.skip_balancing and
                                 not loc.item.classification & ItemClassification.useful)]

    card_strings = []

    for card_number in range(1, 7):
        # If the card number is odd, generate a hint for one of this world's Items.
        if card_number % 2:
            # If we're out of viable placed Items (which can happen if we go crazy with, say, start_inventory_from_pool
            # or item links), make the card hint a message telling the player how few Items.
            if not selectable_prog_items:
                card_strings.append("This world has almost, if not nothing to find for it...")
            # Otherwise, select an Item and continue on as normal.
            else:
                # Grab a random non-furniture progression Item that we created and saved earlier.
                own_hint_item = selectable_prog_items.pop(world.random.randrange(len(selectable_prog_items)))

                # If the drawn Item is local in the player's own world, use a blank player name.
                if own_hint_item.location.player == world.player:
                    other_player_name = ""
                # Otherwise, get the name of that other player.
                else:
                    other_player_name = f"{world.multiworld.get_player_name(own_hint_item.location.player)}'s "

                # Figure out what Location groups in the other player's game the Item's Location is a part of. Don't
                # take the "Everywhere" group as that just includes everything.
                other_world_loc_groups = world.multiworld.worlds[own_hint_item.location.player].location_name_groups
                selectable_loc_groups = [loc_group for loc_group in other_world_loc_groups
                                         if own_hint_item.location.name in other_world_loc_groups[loc_group] and
                                         loc_group != "Everywhere"]

                # If no valid group was found, use "world somewhere" as the generic group name.
                if not selectable_loc_groups:
                    chosen_loc_group_name = "world somewhere"
                # Otherwise, choose one of our found Location group names at random and build a string with that.
                else:
                    chosen_loc_group_name = world.random.choice(selectable_loc_groups)

                # Create the hint text and add it to the end of the card strings list.
                card_strings.append(f"{own_hint_item.name} is in {other_player_name}{chosen_loc_group_name}.")

        # Otherwise, meaning the card number is even, generate a hint for a progression item of a different world.
        else:
            # If we're out of Locations containing significant Progression (if that happens, then...how the heck did
            # this world end up with less than three progression items in it anyway!? There's 200+ Locations, for crying
            # out loud!), make the card hint a message telling the player how barren their world is.
            if not selectable_prog_locs:
                card_strings.append("This world is very devoid of progression...")
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

                # Create the hint text and add it to the end of the card strings list.
                card_strings.append(f"{own_loc_group} contains {other_player_name}{own_hint_loc.item.name}.")

    return card_strings


def get_start_inventory_data(precollected_items: list[Item]) -> dict[str, dict[int, str] | int]:
    """Calculate and return the starting inventory values. Not every Item goes into a menu inventory, so they all have
    to be handled accordingly."""
    start_inventory_data: dict[str, int | dict[int, bytearray] | list[int]] = \
        {"inv arrays": {inv_id: bytearray(CVHODIS_INVENTORIES[inv_id].length) for inv_id in CVHODIS_INVENTORIES},
         "starting flags": [],
         "spellbook": 0,
         "extra life": 0,
         "extra magic": 0,  # MP is not currently supported, but it's here if needed!
         "extra hearts": 0,
         "money": 0}
    one_prog_jump = False

    # Loop over every Item in our pre-collected Items list.
    for item in precollected_items:

        type_byte = (item.code >> 8) & 0xFF
        index_byte = item.code & 0xFF

        # If the Item is a Progressive Height, add Sylph Feather if it's our first one or Griffin's Wing if it's our
        # second.
        if item.name == item_names.relic_height:
            if one_prog_jump:
                index_byte = ALL_CVHODIS_ITEMS[item_names.relic_wing].pickup_index
            else:
                index_byte = ALL_CVHODIS_ITEMS[item_names.relic_feather].pickup_index
                one_prog_jump = True

        # If the Item is a gate key, add the event flag ID it should be setting to the starting flags if it's not there
        # already.
        if item.name in GATE_KEYS:
            if GATE_KEYS[item.name] not in start_inventory_data["starting flags"]:
                start_inventory_data["starting flags"].append(GATE_KEYS[item.name])
        # If the Item is a moneybag, increment the starting money count.
        elif type_byte == PickupTypes.MONEY:
            # The number after the dollar sign in the name is the amount of money to increment by.
            if start_inventory_data["money"] + int(item.name[1:]) <= MAX_MONEY_VALUE:
                start_inventory_data["money"] += int(item.name[1:])
            else:
                start_inventory_data["money"] = MAX_MONEY_VALUE
        # If the Item's type byte is a known type of item with an inventory array, handle it here.
        elif type_byte in start_inventory_data["inv arrays"]:
            # If the inventory array is a bitfield, set the bit for that Item in that inventory array.
            if CVHODIS_INVENTORIES[type_byte].is_bitfield:
                start_inventory_data["inv arrays"][type_byte][index_byte // 8] |= 1 << (index_byte % 8)
            # Otherwise, meaning it's an array of counts, increment the count at that index if said count is not already
            # the max inventory count.
            else:
                if start_inventory_data["inv arrays"][type_byte][index_byte] < MAX_ITEMS_VALUE:
                    start_inventory_data["inv arrays"][type_byte][index_byte] += 1
        # If it doesn't have an inventory array, then it must be a Max Up. In which case, handle it accordingly here.
        elif item.name == item_names.max_life:
            if start_inventory_data["extra life"] + MAX_UP_INCREMENT_VALUE < MAX_STAT_VALUE:
                start_inventory_data["extra life"] += MAX_UP_INCREMENT_VALUE
            else:
                start_inventory_data["extra life"] = MAX_STAT_VALUE
        else:
            if start_inventory_data["extra hearts"] + MAX_UP_INCREMENT_VALUE < MAX_STAT_VALUE:
                start_inventory_data["extra hearts"] += MAX_UP_INCREMENT_VALUE
            else:
                start_inventory_data["extra hearts"] = MAX_STAT_VALUE

        # If the Item is a spellbook, set the starting equipped spellbook value to that book's index + 1.
        if type_byte == PickupTypes.SPELLBOOK:
            start_inventory_data["spellbook"] = index_byte + 1

    # Decode every inventory bytearray into a string so it will be JSON serializable.
    start_array_strings = {}
    for array_num, inv_array in start_inventory_data["inv arrays"].items():
        start_array_strings[array_num] = inv_array.decode("utf-8")
    start_inventory_data["inv arrays"] = start_array_strings

    return start_inventory_data
