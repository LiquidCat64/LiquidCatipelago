from BaseClasses import ItemClassification, Location, Item
from .data import item_names, reg_names, ent_names
from .data.enums import Pickups, StageNames, TextColors
from .data.misc_names import GAME_NAME
from .options import CVLoDOptions, Countdown, InvisibleItems, CastleCenterBranchingPaths, VillaBranchingPaths
from .stages import CVLOD_STAGE_INFO
from .locations import CVLOD_LOCATIONS_INFO, NPC_LOCATIONS
from .items import ALL_CVLOD_ITEMS, SUB_WEAPON_EQUIP_IDS, CVLOD_PICKUP_INFO, CVLoDItem
from .cvlod_text import cvlod_command_scrubber

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from . import CVLoDWorld

AP_NON_PROG_PICKUP_INDEX = Pickups.SPECIAL3
AP_PROG_PICKUP_INDEX = Pickups.CLOCKTOWER_KEY_B
SCENE_REFRESH_VALUE = 0xFF
CASTLE_CENTER_TOP_ELEVATOR_SAVE_SPAWN = 0x03
MAX_JEWELS = 99
MAX_GOLD = 99999

# All Item names exclusive to CV64 mapped to what their equivalent appearance IDs should be in LoD.
CV64_EXCLUSIVE_ITEMS: dict[str, int] = {
    item_names.quest_key_exec: Pickups.EXECUTION_KEY,  # This key still exists in LoD as an unused leftover.
                                                       # It's notably the only purple key in both games.
    "Science Key1": Pickups.GARDEN_KEY,
    "Science Key2": Pickups.GARDEN_KEY,
    "Science Key3": Pickups.GARDEN_KEY,
    "Clocktower Key1": Pickups.STOREROOM_KEY,
    "Clocktower Key2": Pickups.STOREROOM_KEY,
    "Clocktower Key3": Pickups.STOREROOM_KEY,
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


def get_countdown_flags(options: CVLoDOptions, active_locations: Iterable[Location]) -> list[list[int]]:
    """Figures out which Locations have Items that should count towards a Countdown number and assembles each array of
    event flag IDs that will be checked to determine what the current on-screen number should be in each scene.

    The exact number each Location contributes to is determined by the ID of the scene that said Location is in. Said
    scene ID is an index in a table that, in turn, contains a pointer to the current map's array of event flag IDs to
    check to determine what the current number on-screen should be."""

    # Create the array of arrays. The number of countdown numbers is the highest number in the list of countdown numbers
    # for each scene.
    countdown_arrays = [[] for _ in range(19)]

    # Loop over every Location, figure out which countdown number it is, and if it should count on it.
    for loc in active_locations:
        # If the Countdown option is set to Majors, then only Items with the Progression and/or Useful classifications
        # set on them will count. Otherwise, all Locations will count, including those with filler/trap Items. Event
        # Locations will never count no matter what.
        if loc.address is not None and CVLOD_LOCATIONS_INFO[loc.name].countdown is not None and \
                (options.countdown == Countdown.option_all_locations or
                 (options.countdown == Countdown.option_progression_only and loc.item.classification &
                  ItemClassification.progression) or
                 (options.countdown == Countdown.option_progression_useful and loc.item.classification &
                  (ItemClassification.progression | ItemClassification.useful))):

            # Get the Location's countdown array and add its Location ID to it
            # (said Location ID is the event flag ID the game will check to see if you have it).
            countdown_arrays[CVLOD_LOCATIONS_INFO[loc.name].countdown] += [loc.address]

    # Add a 0 to the end of each array to indicate to the game that that's where the array terminates.
    # An event flag of 0 in the game's code is often used to skip the flag check or other special behaviors.
    for array in countdown_arrays:
        array += [0]

        # Add another 0 if the array length is now odd to keep it 4-aligned when it actually goes into the game.
        if len(array) % 2:
            array += [0]

    # Return the final array.
    return countdown_arrays


def get_location_write_values(world: "CVLoDWorld", active_locations: Iterable[Location]) -> {int: (int, bool)}:
    """Gets ALL the Item values to write on each Location in the ROM. Item values consists of two bytes: the first
    (upper) byte dictates the appearance of the Item's in-game pickup, while the second (lower) determines what the Item
    actually is when picked up. All Items from other worlds will be AP Items that do nothing when picked up other than
    set their flag, and their appearance will depend on whether it's another N64-vania player's item and, if so, what
    item it is in their game. Ice Traps can assume the form of any item that is progression, non-progression, or either
    depending on the player's settings.

    Also determined in here is whether the Item's in-game pickup should be visible or not.

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
            # If the Location does not give its Item via a pickup (read: it's either an NPC or a shop Item), write the
            # Item's actual ID instead of its Pickup ID.
            if loc.name in NPC_LOCATIONS:
                item_byte = CVLOD_PICKUP_INFO[ALL_CVLOD_ITEMS[loc.item.name].pickup_id - 1].item_id
            else:
                item_byte = ALL_CVLOD_ITEMS[loc.item.name].pickup_id
        else:
            # Make the Item one of the AP Items. Which one it is should only matter for the Trap Item in practice,
            # as that one plays the character's "hurt" sound when picked up.
            if loc.item.classification & ItemClassification.progression and \
                loc.item.classification & ItemClassification.useful:
                item_byte = Pickups.AP_PROG_USEFUL  # Progression + Useful
            elif loc.item.classification & ItemClassification.progression:
                item_byte = Pickups.AP_PROG  # Progression
            elif loc.item.classification & ItemClassification.useful:
                item_byte = Pickups.AP_USEFUL  # Useful
            elif loc.item.classification & ItemClassification.trap:
                item_byte = Pickups.AP_TRAP  # Trap
            else:
                item_byte = Pickups.AP_FILLER  # Filler

        # Figure out the Item's appearance byte.
        # If the Item is a LoD Item, pick the Pickup ID of the Item its assuming (regardless of whether it's local).
        if loc.item.game == GAME_NAME:
            # If it's an Ice Trap, change its model to one of the appearances we determined before.
            # elif loc.item.code == 0x12:
            #     appearance_byte = get_item_info(world.random.choice(trap_appearances), "code")
            # If we chose a PermaUp as our trap appearance, change it to its actual in-game ID of 0x0B.
            #     if appearance_byte == 0x10C:
            #         appearance_byte = 0x0B
            # If it's none of the above exceptions, make the appearance whatever it should be as per the pickup ID
            # for the pickup it's taking the appearance of minus 1.
            appearance_byte = ALL_CVLOD_ITEMS[loc.item.name].pickup_id - 1
        # If it's a CV64 Item, see if it has an ID in either LoD's Item Info dict or the CV64-exclusive Items dict.
        # If it does, use that Pickup ID.
        elif loc.item.game == "Castlevania 64" and (loc.item.name in ALL_CVLOD_ITEMS
                                                    or loc.item.name in CV64_EXCLUSIVE_ITEMS):
            # Use the Pickup ID from the CV64 Exclusive Items mapping if present there.
            if loc.item.name in CV64_EXCLUSIVE_ITEMS:
                appearance_byte = CV64_EXCLUSIVE_ITEMS[loc.item.name] - 1
            # Otherwise, use the Pickup ID from its regular Item info.
            else:
                appearance_byte = ALL_CVLOD_ITEMS[loc.item.name].pickup_id - 1
        # If not from either N64-vania, or it's an undefined CV64-exclusive Item, use one of the off-world AP Items.
        # Which one to use depends on the Item's classification.
        else:
            # Decide which AP Item to use to represent the other game item.
            if loc.item.classification & ItemClassification.progression and \
                loc.item.classification & ItemClassification.useful:
                appearance_byte = Pickups.AP_PROG_USEFUL - 1  # Progression + Useful
            elif loc.item.classification & ItemClassification.progression:
                appearance_byte = Pickups.AP_PROG - 1  # Progression
            elif loc.item.classification & ItemClassification.useful:
                appearance_byte = Pickups.AP_USEFUL - 1  # Useful
            elif loc.item.classification & ItemClassification.trap:
                appearance_byte = Pickups.AP_TRAP - 1  # Trap
            else:
                appearance_byte = Pickups.AP_FILLER - 1  # Filler

        # Put the appearance and item bytes together to get the final item value to write on that Location.
        item_value = (appearance_byte << 8) + item_byte

        # Determine if the pickup should be invisible or not.
        # If Invisible Items is set to Hide All, we will consider it not visible.
        if world.options.invisible_items == InvisibleItems.option_hide_all:
            item_visible = False
        # If set to Chance, it will have a 50/50 chance of being visible or not.
        elif world.options.invisible_items == InvisibleItems.option_chance:
            item_visible = world.random.choice([True, False])
        # Otherwise, we will go with visible (if Vanilla was chosen, we will simply not write this)
        else:
            item_visible = True

        # Create the final item info tuple and map it to the location address.
        location_values[loc.address] = (item_value, item_visible)

    # Return the final dict of Location values.
    return location_values


def get_location_text(world: "CVLoDWorld", active_locations: Iterable[Location]) -> dict[int, tuple[str, str, int]]:
    """Gets the patch data for all in-game text specific to every created Location, including the Item's name, the Item's player's name, and a value for what color the name should be in-game.
    The data will be returned mapped to their respective Location IDs."""
    location_text = {}

    for loc in active_locations:
        # Skip all Event Locations.
        if not loc.address:
            continue

        # If the Item's name is longer than 103 characters, truncate the name to inject at 103.
        # Regardless, scrub all command characters from it in order to be safe.
        if len(loc.item.name) > 103:
            item_name = cvlod_command_scrubber(loc.item.name[0:103])
        else:
            item_name = cvlod_command_scrubber(loc.item.name)

        # If the Item is local, put an empty string for the player name. The slot's own name will never be shown in-game
        # when it comes to local Items, so we'll be using that to determine if it's local while patching.
        if loc.item.player == world.player:
            player_name = ""
        # Otherwise, get the actual player name. Scrub all command characters from it just to be safe.
        else:
            player_name = cvlod_command_scrubber(world.multiworld.get_player_name(loc.item.player))
            # The player name should not be more than 16 characters. But truncate it at that just to be safe!
            if len(player_name) > 16:
                player_name = player_name[0:16]

        # Determine what color the Item's text should be.
        item_text_color = get_item_text_color(loc.item.classification)

        # The location text data format should be (item name string, player name string, progression boolean)
        location_text[loc.address] = (item_name, player_name, item_text_color)

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
                if stage["connecting_stages"]["prev"][0] == StageNames.CENTER and \
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
            if stage["name"] == StageNames.VILLA:
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
            if stage["name"] == StageNames.CENTER and \
                    options.castle_center_branching_paths == CastleCenterBranchingPaths.option_two:
                transition_values.update({ent_names.ccte_exit_c:
                        (CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 1"][0]].start_scene_id,
                         CVLOD_STAGE_INFO[stage["connecting_stages"]["next alt 1"][0]].start_spawn_id)})

    # Return the final transition values.
    return transition_values


def get_statue_hints(world: "CVLoDWorld") -> list[str]:
    """Creates multiworld-specific hint text to go in the text that appears when checking the Castle Center goddess
    statues. The elevator room statue will contain a hint on the whereabouts of a Mandragora, the gear room statue a
    Magical Nitro, and the library statue both (getting here requires using a pair in the first place, so hinting
    about a second pair here makes sense).

    The hints don't tell you the exact Location name, but rather, a Location name group that the Location can be found
    in, which should tell players roughly where to search for it without completely being a free client hint. If the
    Location is in no Location name groups, then it will only mention the name of the slot that has the Item."""

    # If there aren't at least two Nitros and Mandragoras, return an empty list. Don't bother creating any statue text.
    if len(world.goddess_statue_hint_items[0]) < 2 or len(world.goddess_statue_hint_items[1]) < 2:
        return []

    def create_hint_text(own_hint_item: CVLoDItem):
        # If the drawn Item is local in the player's own world, use a blank player name.
        if own_hint_item.location.player == world.player:
            other_player_name = ""
        # Otherwise, get the name of that other player. Make sure we scrub all command characters from it!
        # Other than the magenta text start/end characters we'll be wrapping this up in...
        else:
            other_player_name = f"✨{TextColors.MAGENTA}/" + cvlod_command_scrubber(
                f"{world.multiworld.get_player_name(own_hint_item.location.player)}'s ") + "✨0/"

        # Figure out what Location groups in the other player's game the Item's Location is a part of. Don't take
        # the "Everywhere" group as that just includes everything.
        other_world_loc_groups = world.multiworld.worlds[own_hint_item.location.player].location_name_groups
        selectable_loc_groups = [loc_group for loc_group in other_world_loc_groups if own_hint_item.location.name in
                                 other_world_loc_groups[loc_group] and loc_group != "Everywhere"]

        # If no valid group was found, use "world somewhere" as the generic group name.
        if not selectable_loc_groups:
            chosen_loc_group_name = "world somewhere"
        # Otherwise, choose one of our found Location group names at random and build a string with that.
        # Limit the group name at 50 characters and scrub any commands just to be safe!
        else:
            chosen_loc_group_name = cvlod_command_scrubber(world.random.choice(selectable_loc_groups)[:50])

        # Create the hint text and add it to the end of the card strings list.
        return f'"{own_hint_item.name} can be found in {other_player_name}{chosen_loc_group_name}."'

    # Create and return all strings.
    return [create_hint_text(world.goddess_statue_hint_items[0][0]),             # Gears statue
            create_hint_text(world.goddess_statue_hint_items[1][0]),             # Elevator statue
            create_hint_text(world.goddess_statue_hint_items[0][1]) + "🅰0/\n" +  # Library statue (2-in-one)
            create_hint_text(world.goddess_statue_hint_items[1][1])]


def get_start_inventory_data(player: int, options: CVLoDOptions, precollected_items: list[Item]) \
        -> dict[str, list[int] | int]:
    """Calculate and return the starting inventory values. Not every Item goes into the menu inventory, so everything
    has to be handled appropriately."""
    start_inventory_data = {"inv array": [0 for _ in range(len(CVLOD_PICKUP_INFO))],
                            "gold": 0,
                            "powerups": 0,
                            "ice traps": 0,
                            "sub weapon": 0,
                            "sub weapon level": 0}

    max_items = 10
    # Raise the items max if Increase Item Limit is enabled.
    if options.increase_item_limit:
        max_items = 99

    # Loop over every Item in our pre-collected Items list.
    for item in precollected_items:
        # If the Item is a sub-weapon, set the current starting sub-weapon to this one.
        if item.name in SUB_WEAPON_EQUIP_IDS:
            # If we are receiving another instance of the same sub-weapon as before, increment the starting weapon
            # level (if it's not already at the max).
            if SUB_WEAPON_EQUIP_IDS[item.name] == start_inventory_data["sub weapon"]:
                if start_inventory_data["sub weapon level"] < 2:
                    start_inventory_data["sub weapon level"] += 1
            # Otherwise, set the level back to 0 and change the sub-weapon to the new one.
            else:
                start_inventory_data["sub weapon"] = SUB_WEAPON_EQUIP_IDS[item.name]
                start_inventory_data["sub weapon level"] = 0
        # If the Item is a PowerUp, increment the starting PowerUp count (if it's not already at the max).
        elif item.name == item_names.powerup:
            if start_inventory_data["powerups"] < 2:
                start_inventory_data["powerups"] += 1
        # If the Item is a moneybag, increment the starting gold amount by that bag's worth (it's right in the name).
        elif "GOLD" in item.name:
            start_inventory_data["gold"] += int(item.name[0:4])
            # Money cannot be higher than 99999.
            if start_inventory_data["powerups"] > MAX_GOLD:
                start_inventory_data["powerups"] = MAX_GOLD
        # If the Item is a jewel, increment the starting jewel count by that jewel's worth.
        # Note that the starting jewel count is the second element in the inventory array.
        elif "jewel" in item.name:
            if "L" in item.name:
                start_inventory_data["inv array"][1] += 10
            else:
                start_inventory_data["inv array"][1] += 5
            # Jewels cannot be higher than 99.
            if start_inventory_data["inv array"][1] > MAX_JEWELS:
                start_inventory_data["inv array"][1] = MAX_JEWELS
        # If the Item is an Ice Trap, increment the starting Ice Trap count (if it's not already at the max).
        elif item.name == item_names.trap_ice:
            if start_inventory_data["ice traps"] < 0xFF:
                start_inventory_data["ice traps"] += 1
        # If it's literally any other Item, increment its count in the inventory array (the index in which is determined
        # by the regular Item ID). Note that Specials hax a max of 99 regardless of the maximum for the other Items,
        # and the Perma series of items all have their own maxes as well.
        else:
            if (start_inventory_data["inv array"][item.code-1] < max_items) or \
                    ("Special" in item.name and start_inventory_data["inv array"][item.code-1] < 99) or \
                    (item.name == item_names.perma_up and start_inventory_data["inv array"][item.code-1] < 2) or \
                    ("Perma" in item.name and start_inventory_data["inv array"][item.code-1] < 3):
                start_inventory_data["inv array"][item.code-1] += 1

        # If receiving a perma weapon, and we currently don't have a starting sub-weapon set, set the weapon now.
        if item.name in [item_names.perma_axe, item_names.perma_cross, item_names.perma_water, item_names.perma_knife] \
            and not start_inventory_data["sub weapon"]:
            start_inventory_data["sub weapon"] = item.code - 0x31

    # Return the final start inventory data.
    return start_inventory_data


def get_item_text_color(classification: int) -> int:
    """Given an item classification, returns an in-game color index value that is associated with that classification + 1 for the purposes of coloring item names in-game."""
    # Progression + Useful
    if ItemClassification.progression & classification and ItemClassification.useful & classification:
        return TextColors.YELLOW
    # Progression
    elif ItemClassification.progression & classification:
        return TextColors.PLUM
    # Useful
    elif ItemClassification.useful & classification:
        return TextColors.SLATE_BLUE
    # Trap
    elif ItemClassification.trap & classification:
        return TextColors.SALMON
    # Filler
    else:
        return TextColors.CYAN
