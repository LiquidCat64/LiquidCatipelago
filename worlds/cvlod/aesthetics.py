import logging

from BaseClasses import ItemClassification, Location, Item
from .data import iname, rname, ni_files
from .options import CVLoDOptions, BackgroundMusic, Countdown, IceTrapAppearance, InvisibleItems, CharacterStages
from .stages import vanilla_stage_order, get_stage_info
from .locations import get_location_info, base_id
from .regions import get_region_info
from .items import get_item_info, item_info
from .text import cvlod_string_to_bytearray

from typing import TYPE_CHECKING, Dict, List, Tuple, Union, Iterable

if TYPE_CHECKING:
    from . import CVLoDWorld

FOUNTAIN_LETTERS_TO_BYTES = {"O": b"\x01", "M": b"\x02", "H": b"\x03", "V": b"\x04"}

rom_sub_weapon_offsets = {
    # 0x10C6EB: [0x10, rname.forest_of_silence],  # Forest
    # 0x10C6F3: [0x0F, rname.forest_of_silence],
    # 0x10C6FB: [0x0E, rname.forest_of_silence],
    # 0x10C703: [0x0D, rname.forest_of_silence],

    0x78165F: (b"\x0E", rname.castle_wall),  # Castle Wall
    0x781683: (b"\x0F", rname.castle_wall),

    0x78DE0F: (b"\x10", rname.villa),  # Villa
    0x78DE03: (b"\x0F", rname.villa),
    0x78DE1B: (b"\x0E", rname.villa),
    0x796DAB: (b"\x0F", rname.villa),
    0x796D6F: (b"\x0D", rname.villa),
    0x796D7B: (b"\x0F", rname.villa),
    0x7D63C3: (b"\x0E", rname.villa),

    # 0x10CA57: [0x0D, rname.tunnel],  # Tunnel
    # 0x10CA5F: [0x0E, rname.tunnel],
    # 0x10CA67: [0x10, rname.tunnel],
    # 0x10CA6F: [0x0D, rname.tunnel],
    # 0x10CA77: [0x0F, rname.tunnel],
    # 0x10CA7F: [0x0E, rname.tunnel],

    # 0x10CBC7: [0x0E, rname.castle_center],  # Castle Center
    # 0x10CC0F: [0x0D, rname.castle_center],
    # 0x10CC5B: [0x0F, rname.castle_center],

    # 0x10CD3F: [0x0E, rname.tower_of_execution],  # Character towers
    # 0x10CD65: [0x0D, rname.tower_of_execution],
    # 0x10CE2B: [0x0E, rname.tower_of_science],
    # 0x10CE83: [0x10, rname.duel_tower],

    # 0x10CF8B: [0x0F, rname.room_of_clocks],  # Room of Clocks
    # 0x10CF93: [0x0D, rname.room_of_clocks],

    # 0x99BC5A: [0x0D, rname.clock_tower],  # Clock Tower
    # 0x10CECB: [0x10, rname.clock_tower],
    # 0x10CED3: [0x0F, rname.clock_tower],
    # 0x10CEDB: [0x0E, rname.clock_tower],
    # 0x10CEE3: [0x0D, rname.clock_tower],
}

rom_empty_breakables_flags = {
    0x10C74D: 0x40FF05,  # Forest of Silence
    0x10C765: 0x20FF0E,
    0x10C774: 0x0800FF0E,
    0x10C755: 0x80FF05,
    0x10C784: 0x0100FF0E,
    0x10C73C: 0x0200FF0E,

    0x10C8D0: 0x0400FF0E,  # Villa foyer

    0x10CF9F: 0x08,  # Room of Clocks flags
    0x10CFA7: 0x01,
    0xBFCB6F: 0x04,  # Room of Clocks candle property IDs
    0xBFCB73: 0x05,
}

# TODO: Find and lower all the problematic freestanding sub-weapon spots.
rom_axe_cross_lower_values = {
    # 0x30: [0x83A60A, 0x71],  # Villa hallway
    # 0x27: [0x83A617, 0x26],
    # 0x2C: [0x83A624, 0x6E],

    # 0x16C: [0x850FE6, 0x07],  # Villa maze

    # 0x10A: [0x8C44D3, 0x08],  # CC factory floor
    # 0x109: [0x8C44E1, 0x08],

    # 0x74: [0x8DF77C, 0x07],  # CC invention area
    # 0x60: [0x90FD37, 0x43],
    # 0x55: [0xBFCC2B, 0x43],
    # 0x65: [0x90FBA1, 0x51],
    # 0x64: [0x90FBAD, 0x50],
    # 0x61: [0x90FE56, 0x43]
}

rom_looping_music_fade_ins = {
    0x10: None,
    0x11: None,
    0x12: None,
    0x13: None,
    0x14: None,
    0x15: None,
    0x16: 0x17,
    0x18: 0x19,
    0x1A: 0x1B,
    0x21: 0x75,
    0x27: None,
    0x2E: 0x23,
    0x39: None,
    0x45: 0x63,
    0x56: None,
    0x57: 0x58,
    0x59: None,
    0x5A: None,
    0x5B: 0x5C,
    0x5D: None,
    0x5E: None,
    0x5F: None,
    0x60: 0x61,
    0x62: None,
    0x64: None,
    0x65: None,
    0x66: None,
    0x68: None,
    0x69: None,
    0x6D: 0x78,
    0x6E: None,
    0x6F: None,
    0x73: None,
    0x74: None,
    0x77: None,
    0x79: None
}

music_sfx_ids = [0x1C, 0x4B, 0x4C, 0x4D, 0x4E, 0x55, 0x6C, 0x76]

renon_item_dialogue = {
    0x02: "More Sub-weapon uses!\n"
          "Just what you need!",
    0x03: "Galamoth told me it's\n"
          "a heart in other times.",
    0x04: "Who needs Warp Rooms\n"
          "when you have these?",
    0x05: "I was told to safeguard\n"
          "this, but I dunno why.",
    0x06: "Fresh off a Behemoth!\n"
          "Those cows are weird.",
    0x07: "Preserved with special\n"
          " wall-based methods.",
    0x08: "Don't tell Geneva\n"
          "about this...",
    0x09: "If this existed in 1094,\n"
          "that whip wouldn't...",
    0x0A: "For when some lizard\n"
          "brain spits on your ego.",
    0x0C: "It'd be a shame if you\n"
          "lost it immediately...",
    0x10C: "No consequences should\n"
           "you perish with this!",
    0x0D: "Arthur was far better\n"
          "with it than you!",
    0x0E: "Night Creatures handle\n"
          "with care!",
    0x0F: "Some may call it a\n"
          "\"Banshee Boomerang.\"",
    0x10: "No weapon triangle\n"
          "advantages with this.",
    0x12: "It looks sus? Trust me,"
          "my wares are genuine.",
    0x15: "This non-volatile kind\n"
          "is safe to handle.",
    0x16: "If you can soul-wield,\n"
          "they have a good one!",
    0x17: "Calls the morning sun\n"
          "to vanquish the night.",
    0x18: "1 on-demand horrible\n"
          "night. Devils love it!",
    0x1A: "Want to study here?\n"
          "It will cost you.",
    0x1B: "\"Let them eat cake!\"\n"
          "Said no princess ever.",
    0x1C: "Why do I suspect this\n"
          "was a toilet room?",
    0x1D: "When you see Coller,\n"
          "tell him I said hi!",
    0x1E: "Atomic number is 29\n"
          "and weight is 63.546.",
    0x1F: "One torture per pay!\n"
          "Who will it be?",
    0x20: "Being here feels like\n"
          "time is slowing down.",
    0x21: "Only one thing beind\n"
          "this. Do you dare?",
    0x22: "The key 2 Science!\n"
          "Both halves of it!",
    0x23: "This warehouse can\n"
          "be yours for a fee.",
    0x24: "Long road ahead if you\n"
          "don't have the others.",
    0x25: "Will you get the curse\n"
          "of eternal burning?",
    0x26: "What's beyond time?\n"
          "Find out your",
    0x27: "Want to take out a\n"
          "loan? By all means!",
    0x28: "The bag is green,\n"
          "so it must be lucky!",
    0x29: "(Does this fool realize?)\n"
          "Oh, sorry.",
    "prog": "They will absolutely\n"
            "need it in time!",
    "useful": "Now, this would be\n"
              "useful to send...",
    "common": "Every last little bit\n"
              "helps, right?",
    "trap": "I'll teach this fool\n"
            " a lesson for a price!",
    "dlc coin": "1 coin out of... wha!?\n"
                "You imp, why I oughta!"
}


def randomize_lighting(world: "CVLoDWorld") -> Dict[int, bytes]:
    """Generates randomized data for the map lighting table."""
    randomized_lighting = {}
    for entry in range(67):
        for sub_entry in range(19):
            if sub_entry not in [3, 7, 11, 15] and entry != 4:
                # The fourth entry in the lighting table affects the lighting on some item pickups; skip it
                randomized_lighting[0x1091A0 + (entry * 28) + sub_entry] = bytes([world.random.randint(0, 255)])
    return randomized_lighting


def shuffle_sub_weapons(world: "CVLoDWorld") -> Dict[int, bytes]:
    """Shuffles the sub-weapons amongst themselves."""
    sub_weapon_dict = {offset: rom_sub_weapon_offsets[offset][0] for offset in rom_sub_weapon_offsets if
                       rom_sub_weapon_offsets[offset][1] in world.active_stage_exits}

    # Remove the one 3HB sub-weapon in Tower of Execution if 3HBs are not shuffled.
    if not world.options.multi_hit_breakables and 0x10CD65 in sub_weapon_dict:
        del (sub_weapon_dict[0x10CD65])

    sub_bytes = list(sub_weapon_dict.values())
    world.random.shuffle(sub_bytes)
    return dict(zip(sub_weapon_dict, sub_bytes))


def randomize_music(world: "CVLoDWorld") -> Dict[int, bytes]:
    """Generates randomized or disabled data for all the music in the game."""
    music_array = bytearray(0x7A)
    for number in music_sfx_ids:
        music_array[number] = number
        # if world.options.background_music == BackgroundMusic.option_randomized:
        looping_songs = []
        non_looping_songs = []
        fade_in_songs = {}
        # Create shuffle-able lists of all the looping, non-looping, and fade-in track IDs
        for i in range(0x10, len(music_array)):
            if i not in rom_looping_music_fade_ins.keys() and i not in rom_looping_music_fade_ins.values() and \
                    i != 0x72:  # Credits song is blacklisted
                non_looping_songs.append(i)
            elif i in rom_looping_music_fade_ins.keys():
                looping_songs.append(i)
            elif i in rom_looping_music_fade_ins.values():
                fade_in_songs[i] = i
        # Shuffle the looping songs
        rando_looping_songs = looping_songs.copy()
        world.random.shuffle(rando_looping_songs)
        looping_songs = dict(zip(looping_songs, rando_looping_songs))
        # Shuffle the non-looping songs
        rando_non_looping_songs = non_looping_songs.copy()
        world.random.shuffle(rando_non_looping_songs)
        non_looping_songs = dict(zip(non_looping_songs, rando_non_looping_songs))
        non_looping_songs[0x72] = 0x72
        # Figure out the new fade-in songs if applicable
        for vanilla_song in looping_songs:
            if rom_looping_music_fade_ins[vanilla_song]:
                if rom_looping_music_fade_ins[looping_songs[vanilla_song]]:
                    fade_in_songs[rom_looping_music_fade_ins[vanilla_song]] = rom_looping_music_fade_ins[
                        looping_songs[vanilla_song]]
                else:
                    fade_in_songs[rom_looping_music_fade_ins[vanilla_song]] = looping_songs[vanilla_song]
        # Build the new music array
        for i in range(0x10, len(music_array)):
            if i in looping_songs.keys():
                music_array[i] = looping_songs[i]
            elif i in non_looping_songs.keys():
                music_array[i] = non_looping_songs[i]
            else:
                music_array[i] = fade_in_songs[i]
    del (music_array[0x00: 0x10])

    return {0xBFCD30: bytes(music_array)}


def randomize_shop_prices(world: "CVLoDWorld") -> Dict[int, bytes]:
    """Randomize the shop prices based on the minimum and maximum values chosen.
    The minimum price will adjust if it's higher than the max."""
    pass
    # min_price = world.options.minimum_gold_price.value
    # max_price = world.options.maximum_gold_price.value

    # if min_price > max_price:
    #    min_price = world.random.randint(0, max_price)
    #    logging.warning(f"[{world.multiworld.player_name[world.player]}] The Minimum Gold Price "
    #                    f"({world.options.minimum_gold_price.value * 100}) is higher than the "
    #                    f"Maximum Gold Price ({max_price * 100}). Lowering the minimum to: {min_price * 100}")
    #    world.options.minimum_gold_price.value = min_price

    # shop_price_list = [world.random.randint(min_price * 100, max_price * 100) for _ in range(7)]

    # Convert the price list into a data dict.
    # price_dict = {}
    # for i in range(len(shop_price_list)):
    #    price_dict[0x103D6C + (i * 12)] = int.to_bytes(shop_price_list[i], 4, "big")

    # return price_dict


def randomize_fountain_puzzle(world: "CVLoDWorld") -> Dict[Tuple[int, int], bytes]:
    """Randomizes the combination for the Cornell Villa fountain puzzle and returns both the solution bytes to write
    in the fountain puzzle code AND in Oldrey's Diary's description."""

    villa_fountain_order = ["O", "M", "H", "V"]  # Vanilla order
    world.random.shuffle(villa_fountain_order)

    return {(0x4780, ni_files.OVL_PAUSE_MENU): cvlod_string_to_bytearray(f"{villa_fountain_order[0]} "
                                                                         f"{villa_fountain_order[1]} "
                                                                         f"{villa_fountain_order[2]} "
                                                                         f"{villa_fountain_order[3]}      "),
            (0x173, ni_files.OVL_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[0]],
            (0x16B, ni_files.OVL_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[1]],
            (0x163, ni_files.OVL_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[2]],
            (0x143, ni_files.OVL_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[3]]}


def get_countdown_numbers(options: CVLoDOptions, active_locations: Iterable[Location]) -> Dict[int, bytes]:
    """Figures out which Countdown numbers to increase for each Location after verifying the Item on the Location should
    increase a number.

    First, check the location's info to see if it has a countdown number override.
    If not, then figure it out based on the parent region's stage's position in the vanilla stage order.
    If the parent region is not part of any stage (as is the case for Renon's shop), skip the location entirely."""
    countdown_list = [0 for _ in range(19)]
    for loc in active_locations:
        if loc.address is not None and (options.countdown == Countdown.option_all_locations or
                                        (options.countdown == Countdown.option_majors
                                         and loc.item.advancement)):

            countdown_number = get_location_info(loc.name, "countdown")

            if countdown_number is None:
                stage = get_region_info(loc.parent_region.name, "stage")
                if stage is not None:
                    countdown_number = vanilla_stage_order.index(stage)

            if countdown_number is not None:
                countdown_list[countdown_number] += 1

    return {0xFFC7D0: bytes(countdown_list)}


def get_location_data(world: "CVLoDWorld", active_locations: Iterable[Location]) \
        -> Tuple[Dict[Union[int, Tuple[int, int]], bytes], List[str], List[bytearray],
                 List[List[Union[int, str, None]]]]:
    """Gets ALL the item data to go into the ROM. Item data consists of two bytes: the first dictates the appearance of
    the item, the second determines what the item actually is when picked up. All items from other worlds will be AP
    items that do nothing when picked up other than set their flag, and their appearance will depend on whether it's
    another CV64 player's item and, if so, what item it is in their game. Ice Traps can assume the form of any item that
    is progression, non-progression, or either depending on the player's settings.

    Appearance does not matter if it's one of the two NPC-given items (from either Vincent or Heinrich Meyer). For
    Renon's shop items, a list containing the shop item names, descriptions, and colors will be returned alongside the
    regular data."""

    # Figure out the list of possible Ice Trap appearances to use based on the settings, first and foremost.
    # if world.options.ice_trap_appearance == IceTrapAppearance.option_major_only:
    #    allowed_classifications = ["progression", "progression skip balancing"]
    # elif world.options.ice_trap_appearance == IceTrapAppearance.option_junk_only:
    #    allowed_classifications = ["filler", "useful"]
    # else:
    #    allowed_classifications = ["progression", "progression skip balancing", "filler", "useful"]

    # trap_appearances = []
    # for item in item_info:
    #    if item_info[item]["default classification"] in allowed_classifications and item != "Ice Trap" and \
    #            get_item_info(item, "code") is not None:
    #        trap_appearances.append(item)

    shop_name_list = []
    shop_desc_list = []
    shop_colors_list = []

    location_bytes = {}

    for loc in active_locations:
        # If the Location is an event, skip it.
        if loc.address is None:
            continue

        loc_type = get_location_info(loc.name, "type")

        # Figure out the Item's primary byte (that controls what Item to give the player when they pick it up) to put in
        # the Location here. If it's the player's very own Item, it should actually be that Item. Otherwise, it should
        # be an Archipelago Item.
        if loc.item.player == world.player:
            if loc_type not in ["npc", "shop"] and get_item_info(loc.item.name, "pickup actor id") is not None:
                item_byte = get_item_info(loc.item.name, "pickup actor id")
            else:
                item_byte = get_item_info(loc.item.name, "code") & 0xFF
        else:
            # Make the Item the unused Special3 - our multiworld item.
            item_byte = 0x6

        # Figure out the Item's appearance byte. If it's a CVLoD player's Item, change the multiworld Item's model to
        # match what it is. Otherwise, change it to an Archipelago progress or not progress icon. Do not write this if
        # it's an NPC item, as that will tell the majors only Countdown to decrease even if it's not a major.
        if loc_type != "npc":
            if loc.item.game == "Castlevania - Legacy of Darkness":
                # If it's a PermaUp, change the Item's model to a big PowerUp.
                if loc.item.code == 0x10C + base_id:
                    appearance_byte = 0x0B
                # If it's an Ice Trap, change its model to one of the appearances we determined before.
                # elif loc.item.code == 0x12 + base_id:
                #     appearance_byte = get_item_info(world.random.choice(trap_appearances), "code")
                # If we chose a PermaUp as our trap appearance, change it to its actual in-game ID of 0x0B.
                #     if appearance_byte == 0x10C:
                #         appearance_byte = 0x0B
                # If it's none of the above exceptions, make the appearance whatever it should be as per the Item's
                # code.
                else:
                    appearance_byte = get_item_info(loc.item.name, "code")
            elif loc.item.advancement:
                appearance_byte = 0x06  # Specail3 id
            else:
                appearance_byte = 0x06  # Also Special3 id (temporary placeholder)
        else:
            appearance_byte = 0x00

        # Apply the invisibility bit on the appearance byte depending on the "invisible items" setting.
        # if (world.options.invisible_items == InvisibleItems.option_vanilla and loc_type == "inv") or \
        #        (world.options.invisible_items == InvisibleItems.option_hide_all and loc_type not in ["npc", "shop"]):
        #    appearance_byte += 0x80
        # elif world.options.invisible_items == InvisibleItems.option_chance and loc_type not in ["npc", "shop"]:
        #    invisible = world.random.randint(0, 1)
        #    if invisible:
        #        appearance_byte += 0x80

        # Set the 0x80 flag in the appearance byte to flag the item as something that should decrement the Countdown
        # when picked up, if applicable.
        if loc.item.advancement or world.options.countdown.value == Countdown.option_all_locations:
            appearance_byte |= 0x80

        # Put the appearance and item bytes together to get the final item value to write in the ROM.
        item_value = (appearance_byte << 8) + item_byte

        # Get the offset to write the value to. If it's to be written into a compressed Nisitenma-Ichigo file, instead
        # of just the offset int, it should be formatted as a tuple consisting of the offset and the file number.
        item_offset = get_location_info(loc.name, "offset")
        item_file_num = get_location_info(loc.name, "ni file")
        if item_file_num is not None:
            item_offset = (item_offset, item_file_num)

        # Add the item value to the dict of writes by its offset.
        location_bytes[item_offset] = item_value

        # If it's an Axe or Cross in a higher freestanding location, lower it into grab range.
        # KCEK made these spawn 3.2 units higher for some reason.
        if loc.address & 0xFFF in rom_axe_cross_lower_values and loc.item.code & 0xFF in [0x0F, 0x10]:
            location_bytes[rom_axe_cross_lower_values[loc.address & 0xFFF][0]] = \
                rom_axe_cross_lower_values[loc.address & 0xFFF][1]

        # Figure out the list of shop names, descriptions, and text colors here.
        if loc.parent_region.name != rname.renon:
            continue

        shop_name = loc.item.name
        if len(shop_name) > 18:
            shop_name = shop_name[0:18]
        shop_name_list.append(shop_name)

        if loc.item.player == world.player:
            shop_desc_list.append([get_item_info(loc.item.name, "code"), None])
        elif loc.item.game == "Castlevania - Legacy of Darkness":
            shop_desc_list.append([get_item_info(loc.item.name, "code"),
                                   world.multiworld.get_player_name(loc.item.player)])
        else:
            if loc.item.game == "DLCQuest" and loc.item.name in ["DLC Quest: Coin Bundle",
                                                                 "Live Freemium or Die: Coin Bundle"]:
                if getattr(world.multiworld.worlds[loc.item.player].options, "coinbundlequantity") == 1:
                    shop_desc_list.append(["dlc coin", world.multiworld.get_player_name(loc.item.player)])
                    shop_colors_list.append(get_item_text_color(loc))
                    continue

            if loc.item.advancement:
                shop_desc_list.append(["prog", world.multiworld.get_player_name(loc.item.player)])
            elif loc.item.classification == ItemClassification.useful:
                shop_desc_list.append(["useful", world.multiworld.get_player_name(loc.item.player)])
            elif loc.item.classification == ItemClassification.trap:
                shop_desc_list.append(["trap", world.multiworld.get_player_name(loc.item.player)])
            else:
                shop_desc_list.append(["common", world.multiworld.get_player_name(loc.item.player)])

        shop_colors_list.append(get_item_text_color(loc))

    return {offset: int.to_bytes(byte, 2, "big") for offset, byte in location_bytes.items()}, shop_name_list, \
        shop_colors_list, shop_desc_list


def get_loading_zone_bytes(options: CVLoDOptions, starting_stage: str,
                           active_stage_exits: Dict[str, Dict[str, Union[str, int, None]]]) -> Dict[int, bytes]:
    """Figure out all the bytes for loading zones and map transitions based on which stages are where in the exit data.
    The same data was used earlier in figuring out the logic. Map transitions consist of two major components: which map
    to send the player to, and which spot within the map to spawn the player at."""

    # Write the byte for the starting stage to send the player to after the intro narration.
    loading_zone_bytes = {0xB73308: get_stage_info(starting_stage, "start map id")}

    for stage in active_stage_exits:

        # Start loading zones
        # If the start zone is the start of the line, have it simply refresh the map.
        if active_stage_exits[stage]["prev"] == "Menu":
            loading_zone_bytes[get_stage_info(stage, "startzone map offset")] = b"\xFF"
            loading_zone_bytes[get_stage_info(stage, "startzone spawn offset")] = b"\x00"
        elif active_stage_exits[stage]["prev"]:
            loading_zone_bytes[get_stage_info(stage, "startzone map offset")] = \
                get_stage_info(active_stage_exits[stage]["prev"], "end map id")
            loading_zone_bytes[get_stage_info(stage, "startzone spawn offset")] = \
                get_stage_info(active_stage_exits[stage]["prev"], "end spawn id")

            # Change CC's end-spawn ID to put you at Carrie's exit if appropriate
            # if active_stage_exits[stage]["prev"] == rname.castle_center:
            #    if options.character_stages == CharacterStages.option_carrie_only or \
            #            active_stage_exits[rname.castle_center]["alt"] == stage:
            #        loading_zone_bytes[get_stage_info(stage, "startzone spawn offset")] = b"\x03"

        # End loading zones
        if active_stage_exits[stage]["next"]:
            loading_zone_bytes[get_stage_info(stage, "endzone map offset")] = \
                get_stage_info(active_stage_exits[stage]["next"], "start map id")
            loading_zone_bytes[get_stage_info(stage, "endzone spawn offset")] = \
                get_stage_info(active_stage_exits[stage]["next"], "start spawn id")

        # Alternate end loading zones
        if active_stage_exits[stage]["alt"]:
            loading_zone_bytes[get_stage_info(stage, "altzone map offset")] = \
                get_stage_info(active_stage_exits[stage]["alt"], "start map id")
            loading_zone_bytes[get_stage_info(stage, "altzone spawn offset")] = \
                get_stage_info(active_stage_exits[stage]["alt"], "start spawn id")

    return loading_zone_bytes


def get_start_inventory_data(player: int, options: CVLoDOptions, precollected_items: List[Item]) -> Dict[int, bytes]:
    """Calculate and return the starting inventory values. Not every Item goes into the menu inventory, so everything
    has to be handled appropriately."""
    start_inventory_data = {}

    inventory_items_array = [0 for _ in range(35)]
    total_money = 0
    total_jewels = 0
    total_powerups = 0
    total_ice_traps = 0

    starting_sub_weapon = None
    starting_weapon_level = 0

    items_max = 10

    # Raise the items max if Increase Item Limit is enabled.
    if options.increase_item_limit:
        items_max = 99

    for item in precollected_items:
        if item.player != player:
            continue

        inventory_offset = get_item_info(item.name, "inventory offset")
        sub_equip_id = get_item_info(item.name, "sub equip id")
        # Starting inventory items
        if inventory_offset is not None:
            inventory_items_array[inventory_offset] += 1
            if inventory_items_array[inventory_offset] > items_max and "Special" not in item.name:
                inventory_items_array[inventory_offset] = items_max
            if item.name == iname.permaup:
                if inventory_items_array[inventory_offset] > 2:
                    inventory_items_array[inventory_offset] = 2
        # Starting sub-weapon
        elif sub_equip_id is not None:
            if item.name != starting_sub_weapon:
                start_inventory_data[0xFFC84F] = bytes(sub_equip_id)
                starting_weapon_level = 0
            else:
                starting_weapon_level += 1
        # Starting PowerUps
        elif item.name == iname.powerup:
            total_powerups += 1
            # Can't have more than 2 PowerUps.
            if total_powerups > 2:
                total_powerups = 2
        # Starting Gold
        elif "GOLD" in item.name:
            total_money += int(item.name[0:4])
            # Money cannot be higher than 99999.
            if total_money > 99999:
                total_money = 99999
        # Starting Jewels
        elif "jewel" in item.name:
            if "L" in item.name:
                total_jewels += 10
            else:
                total_jewels += 5
            # Jewels cannot be higher than 99.
            if total_jewels > 99:
                total_jewels = 99
        # Starting Ice Traps
        else:
            total_ice_traps += 1
            # Ice Traps cannot be higher than 255.
            if total_ice_traps > 0xFF:
                total_ice_traps = 0xFF

    # Get the final byte for the weapon level
    start_inventory_data[0xFFC857] = int.to_bytes(starting_weapon_level, 1, "big")

    # Get the final byte for the jewels count.
    start_inventory_data[0xFFC833] = int.to_bytes(total_jewels, 1, "big")

    # Get the final byte for the Ice Trap count.
    # start_inventory_data[0xBFD88B] = bytes([total_ice_traps])

    # Get the final bytes for the inventory items array.
    start_inventory_data[0xFFC7A0] = bytes(inventory_items_array)

    # Get the final bytes for the money amount.
    start_inventory_data[0xFFC7EE] = int.to_bytes(total_money, 4, "big")

    return start_inventory_data


# TODO: Find out the commands for colored text in this game.
def get_item_text_color(loc: Location) -> bytearray:
    if loc.item.advancement:
        return bytearray([0xA2, 0x0C])
    elif loc.item.classification == ItemClassification.useful:
        return bytearray([0xA2, 0x0A])
    elif loc.item.classification == ItemClassification.trap:
        return bytearray([0xA2, 0x0B])
    else:
        return bytearray([0xA2, 0x02])
