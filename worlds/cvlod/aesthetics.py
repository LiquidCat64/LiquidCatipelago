import base64

from BaseClasses import ItemClassification, Location, Item
from .data import item_names, reg_names, stage_names, ent_names, loc_names
from .data.enums import NIFiles, Scenes, Items
from .options import CVLoDOptions, BackgroundMusic, Countdown, IceTrapAppearance, InvisibleItems, StageLayout, \
    CastleCenterBranchingPaths, VillaBranchingPaths
from .stages import CVLOD_STAGE_INFO
from .locations import CVLOD_LOCATIONS_INFO
from .items import ALL_CVLOD_ITEMS, SUB_WEAPON_IDS
from .cvlod_text import cvlod_string_to_bytearray

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from . import CVLoDWorld

AP_ITEM_INDEX = 0x06
SCENE_REFRESH_VALUE = 0xFF
CASTLE_CENTER_TOP_ELEVATOR_SAVE_SPAWN = 0x03

# All Item names exclusive to CV64 mapped to what their equivalent appearance IDs should be in LoD.
CV64_EXCLUSIVE_ITEMS: dict[str, int] = {
    item_names.quest_key_exec: Items.EXECUTION_KEY,  # This key still exists in LoD as an unused leftover.
                                                     # It's notably the only purple key in both games.
    "Science Key1": Items.GARDEN_KEY,
    "Science Key2": Items.GARDEN_KEY,
    "Science Key3": Items.GARDEN_KEY,
    "Clocktower Key1": Items.STOREROOM_KEY,
    "Clocktower Key2": Items.STOREROOM_KEY,
    "Clocktower Key3": Items.STOREROOM_KEY,
}

SCENE_COUNTDOWN_NUMBERS = [1, 2, 2, 3, 3, 3, 17, 4, 5, 9, 9, 9, 18, 18, 18, 9, 0, 0, 0, 19, 16, 16, 19, 15, 16, 9, 17,
                           14, 19, 13, 11, 11, 11, 12, 12, 8, 8, 7, 7, 10, 16, 16, 6, 19, 19, 19, 16, 19, 19, 19]

FOUNTAIN_LETTERS_TO_BYTES = {"O": b"\x01", "M": b"\x02", "H": b"\x03", "V": b"\x04"}
CHARNEL_COFFIN_ACTORS_START = 0x777C94

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


def randomize_lighting(world: "CVLoDWorld") -> dict[int, bytes]:
    """Generates randomized data for the map lighting table."""
    randomized_lighting = {}
    for entry in range(67):
        for sub_entry in range(19):
            if sub_entry not in [3, 7, 11, 15] and entry != 4:
                # The fourth entry in the lighting table affects the lighting on some item pickups; skip it
                randomized_lighting[0x1091A0 + (entry * 28) + sub_entry] = bytes([world.random.randint(0, 255)])
    return randomized_lighting


def shuffle_sub_weapons(world: "CVLoDWorld") -> dict[str, int]:
    """Shuffles the sub-weapons in their own Locations."""

    # Get every active sub-weapon Location in the world by looping over each active stage and checking all its
    # Locations. Sub-weapon Locations will not normally have been created.
    all_locs_dict = {loc: ALL_CVLOD_ITEMS[CVLOD_LOCATIONS_INFO[loc].normal_item].pickup_id
                     for stage, stage_info in CVLOD_STAGE_INFO.items() for reg, reg_info in stage_info.regions.items()
                     for loc in reg_info["locations"] if loc in CVLOD_LOCATIONS_INFO}

    # Filter all Locations that have a sub-weapon normally.
    sub_weapon_dict = {}
    for loc, item in all_locs_dict.items():
        if CVLOD_LOCATIONS_INFO[loc].normal_item in SUB_WEAPON_IDS:
            sub_weapon_dict[loc] = item

    # Shuffle the values in the sub-weapon dict and return it.
    sub_bytes = list(sub_weapon_dict.values())
    world.random.shuffle(sub_bytes)
    return dict(zip(sub_weapon_dict, sub_bytes))


def randomize_music(world: "CVLoDWorld") -> dict[int, bytes]:
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


def randomize_shop_prices(world: "CVLoDWorld") -> dict[int, bytes]:
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


def randomize_charnel_prize_coffin(world: "CVLoDWorld") -> dict[int, bytes]:
    """Randomizes which of the five coffins in the Forest of Silence's Charnel Houses will be the "prize coffin" that
    will contain three checks upon being broken. Returns the bytes and addresses to write to make the change after
    deciding it."""
    pass
    # correct_charnel_coffin = world.random.randint(0, 4)

    # Swap the IDs of coffin 00 and the new coffin the checks will be in.
    # return {CHARNEL_COFFIN_ACTORS_START + 0x19 + (ACTOR_ENTRY_LENGTH * correct_charnel_coffin): b"\x00",
    #         CHARNEL_COFFIN_ACTORS_START + 0x19: int.to_bytes(correct_charnel_coffin, 1, "big")}


def randomize_fountain_puzzle(world: "CVLoDWorld") -> dict[tuple[int, int], bytes]:
    """Randomizes the combination for the Cornell Villa fountain puzzle and returns both the solution bytes to write
    in the fountain puzzle code AND in Oldrey's Diary's description."""

    villa_fountain_order = ["O", "M", "H", "V"]  # Vanilla order
    world.random.shuffle(villa_fountain_order)

    return {(0x4780, NIFiles.OVERLAY_PAUSE_MENU): cvlod_string_to_bytearray(f"{villa_fountain_order[0]} "
                                                                         f"{villa_fountain_order[1]} "
                                                                         f"{villa_fountain_order[2]} "
                                                                         f"{villa_fountain_order[3]}      ")[0],
            (0x173, NIFiles.OVERLAY_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[0]],
            (0x16B, NIFiles.OVERLAY_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[1]],
            (0x163, NIFiles.OVERLAY_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[2]],
            (0x143, NIFiles.OVERLAY_FOUNTAIN_PUZZLE): FOUNTAIN_LETTERS_TO_BYTES[villa_fountain_order[3]]}


def get_countdown_numbers(options: CVLoDOptions, active_locations: Iterable[Location]) -> list[int]:
    """Figures out which Countdown numbers to increase for each Location after verifying the Item on the Location should
    count towards a number and creates the entire array of starting countdown numbers.

    The exact number each Location contributes to is determined by the ID of the scene that said Location is in. Said
    scene ID is an index in a table that, in turn, contains the actual index of the Location's countdown number in the
    countdown numbers array."""

    # Create the array. The number of countdown numbers is the highest number in the list of countdown numbers for each
    # scene.
    countdown_array = [0 for _ in range(max(SCENE_COUNTDOWN_NUMBERS))]

    # Loop over every Location, figure out which countdown number it is, and if it should count on it.
    for loc in active_locations:
        # If the Countdown option is set to Majors, then only Items with the Progression and/or Useful classifications
        # set on them will count. Otherwise, all Locations will count, including those with filler/trap Items. Event
        # Locations and Locations with a scene ID of 0xFF (indicating they occur in multiple scenes) will never count
        # no matter what.
        if loc.address is not None and CVLOD_LOCATIONS_INFO[loc.name].scene_id != Scenes.NULL and \
                (options.countdown == Countdown.option_all_locations or
                 (options.countdown == Countdown.option_majors and loc.item.classification &
                  (ItemClassification.progression | ItemClassification.useful))):

            # Get the Location's countdown number and increment it.
            countdown_array[CVLOD_LOCATIONS_INFO[loc.name].scene_id] += 1

    # Return the final array.
    return countdown_array


def get_location_write_values(world: "CVLoDWorld", active_locations: Iterable[Location]) -> dict[str, int]:
    """Gets ALL the Item values to write on each Location in the ROM. Item values consists of two bytes: the first
    (upper) byte dictates the appearance of the item, while the second (lower) determines what the Item actually is when
    picked up. All Items from other worlds will be AP Items that do nothing when picked up other than set their flag,
    and their appearance will depend on whether it's another N64-vania player's item and, if so, what item it is in
    their game. Ice Traps can assume the form of any item that is progression, non-progression, or either depending on
    the player's settings.

    Appearance does not matter if it's one of the NPC-given items (from either Vincent or Heinrich Meyer, etc.). For
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

    location_values = {}

    for loc in active_locations:
        # If the Location is an event, skip it.
        if loc.address is None:
            continue

        # Figure out the Item's primary byte (that controls what Item to give the player when they pick it up) to put in
        # the Location here. If it's the player's very own Item, it should actually be that Item. Otherwise, it should
        # be an Archipelago Item.
        if loc.item.player == world.player:
            # If the Location does not give its Item via a pickup, write the Item's actual ID instead of its Pickup ID.
            if CVLOD_LOCATIONS_INFO[loc.name].type in ["npc", "shop"]:
                item_byte = ALL_CVLOD_ITEMS[loc.item.name].item_id
            else:
                item_byte = ALL_CVLOD_ITEMS[loc.item.name].pickup_id
        else:
            # Make the Item the unused Special3 - our multiworld item. Its Pickup and Item ID are both the same (6).
            item_byte = AP_ITEM_INDEX

        # Figure out the Item's appearance byte. If it's an N64-vania player's Item, change the multiworld Item's model
        # to match what it is. Otherwise, have it be an Archipelago Item. Do not write this if it's an NPC item, as that
        # would tell the majors only Countdown to decrease even if it's not a major.
        if CVLOD_LOCATIONS_INFO[loc.name].type not in ["npc", "shop"]:
            # If the Item is a LoD Item, pick its Item ID.
            if loc.item.game == "Castlevania - Legacy of Darkness":
                # If it's a PermaUp, change the Item's model to a big PowerUp.
                if loc.item.code == 0x10C:
                    appearance_byte = 0x0B
                # If it's an Ice Trap, change its model to one of the appearances we determined before.
                # elif loc.item.code == 0x12:
                #     appearance_byte = get_item_info(world.random.choice(trap_appearances), "code")
                # If we chose a PermaUp as our trap appearance, change it to its actual in-game ID of 0x0B.
                #     if appearance_byte == 0x10C:
                #         appearance_byte = 0x0B
                # If it's none of the above exceptions, make the appearance whatever it should be as per the regular
                # Item ID.
                else:
                    appearance_byte = ALL_CVLOD_ITEMS[loc.item.name].item_id
            # If it's a CV64 Item, see if it has an ID in either LoD's Item Info dict or the CV64-exclusive Items dict.
            # If it does, use that Item ID.
            elif loc.item.game == "Castlevania 64" and (loc.item.name in ALL_CVLOD_ITEMS
                                                        or loc.item.name in CV64_EXCLUSIVE_ITEMS):
                if loc.item.name in CV64_EXCLUSIVE_ITEMS:
                    appearance_byte = CV64_EXCLUSIVE_ITEMS[loc.item.name]
                else:
                    appearance_byte = ALL_CVLOD_ITEMS[loc.item.name].item_id
            # If not from either N64-vania, or it's an undefined CV64-exclusive Item, choose a generic Archipelago Item.
            elif loc.item.advancement:
                appearance_byte = AP_ITEM_INDEX  # Specail3 ID
            else:
                # Also Special3 ID (temporary placeholder until distinct classification items are added)
                appearance_byte = AP_ITEM_INDEX
        else:
            appearance_byte = 0x00

        # Set the 0x80 flag in the appearance byte to flag the Item as something that should decrement the Countdown
        # when picked up, if applicable.
        if loc.item.classification & (ItemClassification.progression | ItemClassification.useful) or \
                world.options.countdown.value == Countdown.option_all_locations:
            appearance_byte |= 0x80

        # Put the appearance and item bytes together to get the final item value to write in the ROM.
        location_values[loc.name] = (appearance_byte << 8) + item_byte

    # Return the final dict of Location values.
    return location_values


def get_location_text(world: "CVLoDWorld", active_locations: Iterable[Location]) -> dict[int, str]:
    """Gets all in-game text specific to every created Location. Text will be returned encoded in LoD's format and
    mapped to their respective Location IDs."""
    location_text = {}

    for loc in active_locations:
        # If the Location is Mary Oldrey's, create her entire custom dialogue. She should say what her Item is so
        # players can then decide if the Villa maze kid is worth saving or not.
        if loc.name == loc_names.villala_mary:
            mary_text = "Save Henry, and I will "
            # If it's a local Item, have her say she will give it to you.
            if loc.item.player == world.player:
                mary_text += f"give you this {loc.item.name}."
            # If it's a nonlocal Item, have her say she will send it to that other player.
            else:
                mary_text += f"send this {loc.item.name} to {world.multiworld.get_player_name(loc.item.player)}."
            mary_text += "\nGood luck out there!"

            # Convert the text.
            mary_text = base64.b64encode(cvlod_string_to_bytearray(mary_text)).decode()

            location_text.update({loc.address: mary_text})

    # Return the final dict of Location text.
    return location_text


def get_transition_write_values(options: CVLoDOptions, active_stage_info: list[CVLOD_STAGE_INFO]) \
        -> dict[str, tuple[int, int]]:
    """Figures out all the bytes for loading zones and map transitions based on which stages are where in the exit data.
    The same data was used earlier in figuring out the logic. Transition destination values consist of two things: the
    ID for which scene to send the player to, and the ID for which spawn point in the scene to start the player at.
    In the returned tuples, these are the first and second int values respectively."""

    # Get the byte for the starting stage to send the player to after the intro narration.
    transition_values = {"Start stage": (CVLOD_STAGE_INFO[active_stage_info[0]["name"]].start_scene_id,
                                           CVLOD_STAGE_INFO[active_stage_info[0]["name"]].start_spawn_id)}

    # Loop over every active stage and figure out the scene/spawn values to put for each one's start and end Entrances.
    for stage in active_stage_info:

        # # # START TRANSITIONS # # #
        # Check to see if the stage has a valid start Entrance. If it doesn't, we will skip this part.
        if CVLOD_STAGE_INFO[stage["name"]].start_entrance:
            # If the previous stage is "Start", meaning this stage is the first stage in the line, put the scene refresh
            # byte for the scene (0xFF) and the transition's regular spawn ID. This will effectively connect the
            # transition back to itself.
            if stage["connecting_stages"]["prev"][0] == "Start":
                prev_scene = SCENE_REFRESH_VALUE
                prev_spawn = CVLOD_STAGE_INFO[stage["name"]].start_spawn_id
            # If not, then get the previous stage's defined end scene/spawn values like normal.
            else:
                prev_scene = CVLOD_STAGE_INFO[stage["connecting_stages"]["prev"][0]].end_scene_id
                prev_spawn = CVLOD_STAGE_INFO[stage["connecting_stages"]["prev"][0]].end_spawn_id
                # If the previous stage is Castle Center, and either Castle Center Branching Paths is set to One Carrie
                # or the stage position has the altternate path indicator "'" in it, increment the spawn ID by 1 to get
                # us Carrie's CC exit (it's Reinhardt's by default).
                if stage["connecting_stages"]["prev"][0] == stage_names.CENTER and \
                        (options.castle_center_branching_paths == CastleCenterBranchingPaths.option_one_carrie or
                         "'" in stage["position"]):
                    prev_spawn += 1

            # Update the output dict with the start Entrance.
            transition_values.update({CVLOD_STAGE_INFO[stage["name"]].start_entrance: (prev_scene, prev_spawn)})

        # # # END TRANSITIONS # # #
        # Check to see if the stage has a valid end Entrance. If it doesn't, we will skip this part.
        # NOTE: The only stage that shouldn't is Castle Keep.
        if CVLOD_STAGE_INFO[stage["name"]].end_entrance:
            # If the next stage is the end of Castle Center, set the scene to Castle Center's end scene and the spawn to
            # the White Jewel there.
            if stage["connecting_stages"]["next"][1] == reg_names.ccte_elev_top:
                next_scene = CVLOD_STAGE_INFO[stage["connecting_stages"]["next"][0]].end_scene_id
                next_spawn = CASTLE_CENTER_TOP_ELEVATOR_SAVE_SPAWN
            # If not, then get the next stage's defined start scene/spawn values like normal.
            else:
                next_scene = CVLOD_STAGE_INFO[stage["connecting_stages"]["next"][0]].start_scene_id
                next_spawn = CVLOD_STAGE_INFO[stage["connecting_stages"]["next"][0]].start_spawn_id

            # Update the output dict with the end Entrance.
            transition_values.update({CVLOD_STAGE_INFO[stage["name"]].end_entrance: (next_scene, next_spawn)})

            # If the stage is Villa, and Villa Branching Paths are higher than 1, figure out the Villa's alternate
            # end transition values.
            if stage["name"] == stage_names.VILLA:
                if options.villa_branching_paths != VillaBranchingPaths.option_one:
                    transition_values.update({ent_names.villac_end_ca:
                             (CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 1"][0]].start_scene_id,
                              CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 1"][0]].start_spawn_id)})
                if options.villa_branching_paths in [VillaBranchingPaths.option_three,
                                                     VillaBranchingPaths.option_three_with_cornell_path]:
                    transition_values.update({ent_names.villac_end_co:
                             (CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 2"][0]].start_scene_id,
                              CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 2"][0]].start_spawn_id)})

            # If the stage is Castle Center, and CC Branching Paths are 2, figure out CC's alternate end transition
            # values.
            if stage["name"] == stage_names.CENTER and \
                    options.castle_center_branching_paths == CastleCenterBranchingPaths.option_two:
                transition_values.update({ent_names.ccte_exit_c:
                        (CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 1"][0]].start_scene_id,
                         CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 1"][0]].start_spawn_id)})

    # Return the final transition values.
    return transition_values


def get_start_inventory_data(player: int, options: CVLoDOptions, precollected_items: list[Item]) \
        -> dict[str, list[int] | int]:
    """Calculate and return the starting inventory values. Not every Item goes into the menu inventory, so everything
    has to be handled appropriately."""
    start_inventory_data = {"inv array": [0 for _ in range(0x30)],
                            "gold": 0,
                            "jewels": 0,
                            "powerups": 0,
                            "ice traps": 0,
                            "sub weapon": 0,
                            "sub weapon level": 0}

    items_max = 10
    # Raise the items max if Increase Item Limit is enabled.
    if options.increase_item_limit:
        items_max = 99

    # Loop over every Item in our pre-collected Items list.
    for item in precollected_items:
        # If the Item is a sub-weapon, set the current starting sub-weapon to this one.
        if item.name in SUB_WEAPON_IDS:
            # If we are receiving another instance of the same sub-weapon as before, increment the starting weapon
            # level (if it's not already at the max).
            if SUB_WEAPON_IDS[item.name] == start_inventory_data["sub weapon"]:
                if start_inventory_data["sub weapon level"] < 2:
                    start_inventory_data["sub weapon level"] += 1
            # Otherwise, set the level back to 0 and change the sub-weapon to the new one.
            else:
                start_inventory_data["sub weapon"] = SUB_WEAPON_IDS[item.name]
                start_inventory_data["sub weapon level"] = 0
        # If the Item is a PowerUp, increment the starting PowerUp count (if it's not already at the max).
        elif item.name == item_names.powerup:
            if start_inventory_data["powerups"] < 2:
                start_inventory_data["powerups"] += 1
        # If it's a PermaUp, increment the PowerUp ID's count in the inventory array specifically (if we already have
        # fewer than 2).
        elif item.name == item_names.permaup:
            if start_inventory_data["inv array"][ALL_CVLOD_ITEMS[item_names.powerup].item_id-1] < 2:
                start_inventory_data["inv array"][ALL_CVLOD_ITEMS[item_names.powerup].item_id - 1] += 1
        # If the Item is a moneybag, increment the starting gold amount by that bag's worth (it's right in the name).
        elif "GOLD" in item.name:
            start_inventory_data["gold"] += int(item.name[0:4])
            # Money cannot be higher than 99999.
            if start_inventory_data["powerups"] > 99999:
                start_inventory_data["powerups"] = 99999
        # If the Item is a jewel, increment the starting jewel count by that jewel's worth.
        elif "jewel" in item.name:
            if "L" in item.name:
                start_inventory_data["jewels"] += 10
            else:
                start_inventory_data["jewels"] += 5
            # Jewels cannot be higher than 99.
            if start_inventory_data["jewels"] > 99:
                start_inventory_data["jewels"] = 99
        # If the Item is an Ice Trap, increment the starting Ice Trap count (if it's not already at the max).
        elif item.name == item_names.trap_ice:
            if start_inventory_data["ice traps"] < 0xFF:
                start_inventory_data["ice traps"] += 1
        # If it's literally any other Item, increment its count in the inventory array (the index in which is determined
        # by the regular Item ID).
        else:
            if start_inventory_data["inv array"][item.code-1] < items_max or "Special" in item.name:
                start_inventory_data["inv array"][item.code-1] += 1

    # Return the final start inventory data.
    return start_inventory_data
