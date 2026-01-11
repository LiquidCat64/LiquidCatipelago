from typing import TYPE_CHECKING, Set, NamedTuple
from .locations import BASE_ID, get_location_names_to_ids
# from .items import ALL_CVHODIS_ITEMS
# from .locations import CVHODIS_LOCATIONS_INFO
# from .cvhodis_text import cvhodis_string_to_bytearray
from .rom import ARCHIPELAGO_IDENTIFIER_START, ARCHIPELAGO_IDENTIFIER, AUTH_NUMBER_START, QUEUED_TEXT_STRING_START
from .data import item_names, loc_names
from .data.enums import PickupTypes
from .aesthetics import CVHODIS_INVENTORIES, MAX_STAT_VALUE, MAX_UP_INCREMENT_VALUE

from BaseClasses import ItemClassification
from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
import base64
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

GAME_STATE_ADDRESS = 0xC
FLAGS_BITFIELD_START = 0x310
NUM_RECEIVED_ITEMS_ADDRESS = 0x18872
RELICS_EQUIPPED_BITFIELD_START = 0x18841
FURN_PLACED_BITFIELD_START = 0x18847
QUEUED_TEXTBOX_SMALL_ADDRESS = 0x18A00
QUEUED_TEXTBOX_LARGE_ADDRESS = 0x18A02
QUEUED_RECEIVED_INDEX_INCREMENT_ADDRESS = 0x18A04
QUEUED_SOUND_ID_ADDRESS = 0x18A06
DELAY_TIMER_ADDRESS = 0x18A08
QUEUED_MAX_UP_GRAPHIC_ADDRESS = 0x18A0B
PLAYER_FROZEN_CUTSCENE_ADDRESS = 0x1B
PLAYER_FROZEN_TEXTBOX_ADDRESS = 0xF
CURRENT_MENU_ADDRESS = 0x48
MAX_STATS_COUNTS_START = 0x18786
CURRENT_HP_ADDRESS = 0x1854E
CURRENT_MP_ADDRESS = 0x18550
CURRENT_HEARTS_ADDRESS = 0x18794
CURRENT_BOOK_ADDRESS = 0x1877F
# CURRENT_LOCATION_VALUES_START = 0x253FC TODO: Find a good way to tell the player's area.
ROM_NAME_START = 0xA0

GAME_STATE_GAMEPLAY = 0x03
GAME_STATE_CREDITS = 0x09
FROZEN_TEXTBOX_BITS = 0x03
CAN_PAUSE_BIT = 0x04
OUT_OF_MENU_VALUE = 0x01
TEXT_ID_MULTIWORLD_MESSAGE = b"\xF2\x84"
SOUND_ID_PICKUP_MINOR = b"\x2D"
SOUND_ID_PICKUP_MONEY = b"\x2E"
SOUND_ID_PICKUP_HEART = b"\x2F"
SOUND_ID_PICKUP_SUB_WEAPON = b"\x30"
SOUND_ID_PICKUP_MAX_UP = b"\x34"
SOUND_ID_PICKUP_MAJOR = b"\x36"

ITEM_NAME_LIMIT = 300
PLAYER_NAME_LIMIT = 50

FLAG_CLOCK_TOWER_DEATH_CUTSCENE = 0x3D
FLAG_DRACULA_WRAITH_INTRO = 0x48
FLAG_MEDIUM_ENDING = 0x45
FLAG_WORST_ENDING = 0x46
FLAG_BEST_ENDING = 0x1F

INV_NUMBERS = [pickup_type for pickup_type in CVHODIS_INVENTORIES]

# These flags are communicated to the tracker as a bitfield using this order.
# Modifying the order will cause undetectable autotracking issues.
EVENT_FLAG_MAP = {
    FLAG_MEDIUM_ENDING: "FLAG_OBTAINED_MEDIUM_ENDING",
    FLAG_WORST_ENDING: "FLAG_OBTAINED_WORST_ENDING",
    FLAG_BEST_ENDING: "FLAG_OBTAINED_BEST_ENDING",
    0xFF: "FLAG_PLACED_REQUIRED_FURNITURE",
    # Not actually set by the game, but we consider it set when enough furniture
    # is detected as having been placed.
    0x3D: "FLAG_MET_DEATH_IN_CLOCK_TOWER",
    0x33: "FLAG_BROKE_LOWER_SKELETON_A_WALL",
    0x27: "FLAG_BROKE_SKY_B_WALL_TO_SHADOW",
    0x01: "FLAG_PRESSED_LOWER_CLOCK_A_BUTTON",
    0x25: "FLAG_RAISED_CLOCK_B_CRANK",
    0x24: "FLAG_HAMMERED_BRONZE_GUARDER",
    0x53: "FLAG_DESTROYED_TOP_FLOOR_A_HAND",
    0x02: "FLAG_PRESSED_TOP_FLOOR_A_BUTTON",
    0x20: "FLAG_DRAINED_LUMINOUS_A_WATER",
    0xE1: "FLAG_DEFEATED_GIANT_BAT",
    0xE2: "FLAG_DEFEATED_SKULL_KNIGHT",
    0xE3: "FLAG_DEFEATED_LIVING_ARMOR",
    0xE4: "FLAG_DEFEATED_GOLEM",
    0xE5: "FLAG_DEFEATED_MINOTAUR",
    0xE6: "FLAG_DEFEATED_DEVIL",
    0xE7: "FLAG_DEFEATED_GIANT_MERMAN",
    0xE8: "FLAG_DEFEATED_MAX_SLIMER",
    0xE9: "FLAG_DEFEATED_PEEPING_BIG",
    0xEA: "FLAG_DEFEATED_LEGION_SAINT",
    0xEB: "FLAG_DEFEATED_SHADOW",
    0xEC: "FLAG_DEFEATED_MINOTAUR_LV2",
    0xED: "FLAG_DEFEATED_LEGION_CORPSE",
    0xEE: "FLAG_DEFEATED_TALOS",
    0xEF: "FLAG_DEFEATED_DEATH",
    0xF0: "FLAG_DEFEATED_CYCLOPS",
    # NOTE: 0xF1 is Intro Talos, but I don't think we care about him.
    0xF2: "FLAG_DEFEATED_PAZUZU",
}

DEATHLINK_AREA_NAMES = ["Sealed Room", "Catacomb", "Abyss Staircase", "Audience Room", "Triumph Hallway",
                        "Machine Tower", "Eternal Corridor", "Chapel Tower", "Underground Warehouse",
                        "Underground Gallery", "Underground Waterway", "Outer Wall", "Observation Tower",
                        "Ceremonial Room", "Battle Arena"]


class CastlevaniaHoDisClient(BizHawkClient):
    game = "Castlevania - Harmony of Dissonance"
    system = "GBA"
    patch_suffix = ".apcvhodis"
    sent_initial_packets: bool
    self_induced_death: bool
    time_of_sent_death: float | None
    local_checked_locations: Set[int]
    client_set_events = {flag_name: False for flag, flag_name in EVENT_FLAG_MAP.items()}
    got_medium_ending: bool
    got_worst_ending: bool
    got_best_ending: bool
    completed_furniture: bool
    sent_message_queue: list
    death_causes: list
    currently_dead: bool
    synced_set_events: bool

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        from CommonClient import logger

        try:
            # Check ROM name/patch version
            game_names = await bizhawk.read(ctx.bizhawk_ctx, [(ROM_NAME_START, 0xC, "ROM"),
                                                              (ARCHIPELAGO_IDENTIFIER_START, 12, "ROM")])
            if game_names[0].decode("ascii") != "CASTLEVANIA1":
                return False
            if game_names[1] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                logger.info("ERROR: You appear to be running an unpatched version of Castlevania: Harmony of "
                            "Dissonance. You need to generate a patch file and use it to create a patched ROM.")
                return False
            if game_names[1].decode("ascii") != ARCHIPELAGO_IDENTIFIER:
                logger.info("ERROR: The patch file used to create this ROM is not compatible with "
                            "this client. Double check your client version against the version being "
                            "used by the generator.")
                return False
        except UnicodeDecodeError:
            return False
        except bizhawk.RequestFailedError:
            return False  # Should verify on the next pass

        ctx.game = self.game
        ctx.items_handling = 0b001
        ctx.want_slot_data = True
        ctx.watcher_timeout = 0.125
        return True

    async def set_auth(self, ctx: "BizHawkClientContext") -> None:
        auth_raw = (await bizhawk.read(ctx.bizhawk_ctx, [(AUTH_NUMBER_START, 16, "ROM")]))[0]
        ctx.auth = base64.b64encode(auth_raw).decode("utf-8")
        # Initialize all the local client attributes here so that nothing will be carried over from a previous HoD if
        # the player tried changing HoD ROMs without resetting their Bizhawk Client instance.
        self.sent_initial_packets = False
        self.local_checked_locations = set()
        self.self_induced_death = False
        self.time_of_sent_death = None
        self.client_set_events = {flag_name: False for flag, flag_name in EVENT_FLAG_MAP.items()}
        self.got_medium_ending = False
        self.got_worst_ending = False
        self.got_best_ending = False
        self.completed_furniture = False
        self.sent_message_queue = []
        self.death_causes = []
        self.currently_dead = False
        self.synced_set_events = False

    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd != "Bounced":
            return
        if "tags" not in args:
            return
        if ctx.slot is None:
            return
        if "DeathLink" in args["tags"] and args["data"]["time"] != self.time_of_sent_death:
            if "cause" in args["data"]:
                cause = args["data"]["cause"]
                # If the other game sent a death with a blank string for the cause, use the default death message.
                if cause == "":
                    cause = f"{args['data']['source']} killed you without a word!"
                if len(cause) > ITEM_NAME_LIMIT + PLAYER_NAME_LIMIT:
                    cause = cause[:ITEM_NAME_LIMIT + PLAYER_NAME_LIMIT]
            else:
                # If the other game sent a death with no cause at all, use the default death message.
                cause = f"{args['data']['source']} killed you without a word!"

            self.death_causes += [cause]

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None or ctx.slot is None:
            return

        try:
            # Scout all Locations and get our Set events upon initial connection.
            if not self.sent_initial_packets:
                await ctx.send_msgs([{
                    "cmd": "LocationScouts",
                    "locations": [code for name, code in get_location_names_to_ids().items()
                                  if code in ctx.server_locations],
                    "create_as_hint": 0
                }])
                await ctx.send_msgs([{
                    "cmd": "Get",
                    "keys": [f"castlevania_hodis_events_{ctx.team}_{ctx.slot}"]
                }])
                self.sent_initial_packets = True

            read_state = await bizhawk.read(ctx.bizhawk_ctx, [(CVHODIS_INVENTORIES[inv].main_start_addr,
                                                               CVHODIS_INVENTORIES[inv].length,
                                                               "EWRAM") for inv in CVHODIS_INVENTORIES] + [
                                                              (RELICS_EQUIPPED_BITFIELD_START,
                                                               CVHODIS_INVENTORIES[PickupTypes.RELIC].length, "EWRAM"),
                                                              (GAME_STATE_ADDRESS, 1, "EWRAM"),
                                                              (FLAGS_BITFIELD_START, 76, "EWRAM"),
                                                              (NUM_RECEIVED_ITEMS_ADDRESS, 2, "EWRAM"),
                                                              (QUEUED_TEXTBOX_SMALL_ADDRESS, 12, "EWRAM"),
                                                              (DELAY_TIMER_ADDRESS, 2, "EWRAM"),
                                                              (CURRENT_MENU_ADDRESS, 1, "EWRAM"),
                                                              (PLAYER_FROZEN_CUTSCENE_ADDRESS, 1, "EWRAM"),
                                                              (PLAYER_FROZEN_TEXTBOX_ADDRESS, 1, "EWRAM"),
                                                              (MAX_STATS_COUNTS_START, 6, "EWRAM"),
                                                              (CURRENT_HP_ADDRESS, 2, "EWRAM"),
                                                              (CURRENT_HEARTS_ADDRESS, 2, "EWRAM"),
                                                              (CURRENT_BOOK_ADDRESS, 1, "EWRAM"),
                                                              (FURN_PLACED_BITFIELD_START,
                                                               CVHODIS_INVENTORIES[PickupTypes.FURNITURE].length,
                                                               "EWRAM")])

            curr_invs = {INV_NUMBERS[i]: bytearray(read_state[i]) for i in range(len(INV_NUMBERS))}

            enabled_relics = bytearray(read_state[len(CVHODIS_INVENTORIES)])
            game_state = int.from_bytes(read_state[len(CVHODIS_INVENTORIES) + 1], "little")
            all_flags = read_state[len(CVHODIS_INVENTORIES) + 2]
            num_received_items = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 3]), "little")
            queued_received_info = bytearray(read_state[len(CVHODIS_INVENTORIES) + 4])
            delay_timer = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 5]), "little")
            menu_state = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 6]), "little")
            cutscene_state = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 7]), "little")
            textbox_state = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 8]), "little")
            max_stats_array = bytearray(read_state[len(CVHODIS_INVENTORIES) + 9])
            curr_hp = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 10]), "little")
            curr_hearts = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 11]), "little")
            curr_book = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 12]), "little")
            placed_furniture_flags = int.from_bytes(bytearray(read_state[len(CVHODIS_INVENTORIES) + 13]), "little")

            # Get out each of the individual max stat values.
            max_hp = int.from_bytes(max_stats_array[0:2], "little")
            # max_mp = int.from_bytes(max_stats_array[2:4], "little") Not used. But it's here if it's ever needed!
            max_hearts = int.from_bytes(max_stats_array[4:], "little")

            # Get out each individual flag array. For easiest flag ID reading, they should be split up by word and in
            # big endian.
            event_flags_array = [int.from_bytes(all_flags[0x04:0x20][i:i + 4], "little") for i in
                                 range(0, len(all_flags[0x04:0x20]), 4)]
            # Append the boss kill flags to the event flags as an additional word. We'll consider them Events 0xE0-0xFF.
            event_flags_array.append(int.from_bytes(all_flags[0x48:], "little"))
            # Consider the very last flag (Flag 0xFF) in our event flag array set if the furniture goal is complete.
            if self.completed_furniture:
                event_flags_array[7] |= 0x80000000

            pickup_flags_array = [int.from_bytes(all_flags[0x20:0x48][i:i + 4], "little") for i in
                                  range(0, len(all_flags[0x20:0x48]), 4)]

            # If there's no receive sound queued, the delay timer is 0, we are not in a cutscene, not frozen due to an
            # item textbox, are able to pause, and are not currently paused, it should be safe to call a textbox.
            ok_to_inject = (queued_received_info[6:8] == b"\x00\x00" and not delay_timer and menu_state == 1 and
                            not cutscene_state and not textbox_state & FROZEN_TEXTBOX_BITS and textbox_state &
                            CAN_PAUSE_BIT == CAN_PAUSE_BIT)

            # Make sure we are in the Gameplay state before detecting sent locations or giving items/deaths.
            # If we are in any other state, such as the Game Over state, reset the textbox buffers back to 0 so that we
            # don't receive the most recent item upon loading back in.
            if game_state != GAME_STATE_GAMEPLAY:
                self.currently_dead = False
                await bizhawk.write(ctx.bizhawk_ctx, [(QUEUED_TEXTBOX_SMALL_ADDRESS, [0 for _ in range(12)], "EWRAM")])
                return

            # Update the ending events already being done on past separate sessions for if the player is running
            # multiple of them.
            if f"castlevania_hodis_events_{ctx.team}_{ctx.slot}" in ctx.stored_data:
                if ctx.stored_data[f"castlevania_hodis_events_{ctx.team}_{ctx.slot}"] is not None:
                    if ctx.stored_data[f"castlevania_hodis_events_{ctx.team}_{ctx.slot}"] & 0x1:
                        self.got_medium_ending = True

                    if ctx.stored_data[f"castlevania_hodis_events_{ctx.team}_{ctx.slot}"] & 0x2:
                        self.got_worst_ending = True

                    if ctx.stored_data[f"castlevania_hodis_events_{ctx.team}_{ctx.slot}"] & 0x4:
                        self.got_best_ending = True

                    if ctx.stored_data[f"castlevania_hodis_events_{ctx.team}_{ctx.slot}"] & 0x8:
                        self.completed_furniture = True

            # Enable DeathLink if it's in our slot_data.
            if "DeathLink" not in ctx.tags and ctx.slot_data["death_link"]:
                await ctx.update_death_link(True)

            # Send a DeathLink if we died on our own independently of receiving another one.
            # To ensure we don't send a death on an exact frame in the gameplay state before the player's current health
            # gets initialized, the current menu state should be checked too.
            if "DeathLink" in ctx.tags and menu_state == 1 and curr_hp == 0 and not self.currently_dead:
                self.currently_dead = True

                # Take the name of whatever area the player is currently in.
                # area_of_death = DEATHLINK_AREA_NAMES[area]

                # Send the death.
                # await ctx.send_death(f"{ctx.player_names[ctx.slot]} perished in {area_of_death}. Dracula has won!")
                await ctx.send_death(f"{ctx.player_names[ctx.slot]} perished. Dracula has won!")

                # Record the time in which the death was sent so when we receive the packet we can tell it wasn't our
                # own death. ctx.on_deathlink overwrites it later, so it MUST be grabbed now.
                self.time_of_sent_death = ctx.last_death_link

            # If we have any queued death causes, handle DeathLink giving here.
            if self.death_causes and ok_to_inject and not self.currently_dead:

                # Inject the oldest cause as a textbox message and play the Dracula charge attack sound.
                death_text = self.death_causes[0]
                # death_writes = [(QUEUED_TEXTBOX_1_ADDRESS, TEXT_ID_MULTIWORLD_MESSAGE, "EWRAM"),
                #                 (QUEUED_SOUND_ID_ADDRESS, SOUND_ID_DRACULA_CHARGE, "EWRAM")]
                death_writes = []

                # Kill the player by setting their current HP to 0. The textbox frozen state should be manually updated
                # as well so that nothing weird will happen on the title screen.
                death_writes += [(CURRENT_HP_ADDRESS, b"\x00\00", "EWRAM"),
                                 (PLAYER_FROZEN_TEXTBOX_ADDRESS, b"\x00", "EWRAM")]

                # Add the final death text and write the whole shebang.
                # death_writes += [(QUEUED_TEXT_STRING_START,
                #                   bytes(cvhodis_string_to_bytearray(death_text + "◊", "big middle", 0)), "ROM")]
                await bizhawk.write(ctx.bizhawk_ctx, death_writes)

                # Delete the oldest death cause that we just wrote and set currently_dead to True so the client doesn't
                # think we just died on our own on the subsequent frames before the Game Over state.
                del(self.death_causes[0])
                self.currently_dead = True
            # If somehow we have more than 0 HP while the client thinks we are dead at this point, set ourselves back
            # to alive. The player likely loaded a savestate before the game state changed to Game Over.
            elif curr_hp > 0 and self.currently_dead:
                self.currently_dead = False

            # If we have a queue of Locations to inject "sent" messages with, do so before giving any subsequent Items.
            #elif self.sent_message_queue and ok_to_inject and not self.currently_dead and ctx.locations_info:
            #    loc = self.sent_message_queue[0]
                # Truncate the Item name. ArchipIDLE's FFXIV Item is 214 characters, for comparison.
            #    item_name = ctx.item_names.lookup_in_slot(ctx.locations_info[loc].item, ctx.locations_info[loc].player)
            #    if len(item_name) > ITEM_NAME_LIMIT:
            #        item_name = item_name[:ITEM_NAME_LIMIT]
                # Truncate the player name. Player names are normally capped at 16 characters, but there is no limit on
                # ItemLink group names.
            #    player_name = ctx.player_names[ctx.locations_info[loc].player]
            #    if len(player_name) > PLAYER_NAME_LIMIT:
            #        player_name = player_name[:PLAYER_NAME_LIMIT]

            #    sent_text = cvhodis_string_to_bytearray(f"「{item_name}」 sent to 「{player_name}」◊", "big middle", 0)

                # Set the correct sound to play depending on the Item's classification.
            #    if ctx.slot_info[ctx.locations_info[loc].player].game == "Castlevania - Harmony of Dissonance":
            #        mssg_sfx_id = SOUND_ID_MAIDEN_BREAKING
            #        sent_text = cvhodis_string_to_bytearray(f"「Iron Maidens」 broken for 「{player_name}」◊",
            #                                                "big middle", 0)
            #    elif ctx.locations_info[loc].flags & ItemClassification.progression:
            #        mssg_sfx_id = SOUND_ID_MAJOR_PICKUP
            #    elif ctx.locations_info[loc].flags & ItemClassification.trap:
            #        mssg_sfx_id = SOUND_ID_BAD_CONFIG
            #    else:  # Filler
            #        mssg_sfx_id = SOUND_ID_MINOR_PICKUP

            #    await bizhawk.write(ctx.bizhawk_ctx, [(QUEUED_TEXTBOX_1_ADDRESS, TEXT_ID_MULTIWORLD_MESSAGE, "EWRAM"),
            #                                          (QUEUED_SOUND_ID_ADDRESS, mssg_sfx_id, "EWRAM"),
            #                                          (QUEUED_TEXT_STRING_START, sent_text, "ROM")])

            #    del(self.sent_message_queue[0])

            # If the game hasn't received all items yet, it's ok to inject, and the current number of received items
            # still matches what we read before, then write the next incoming item into the inventory and, separately,
            # the textbox ID to trigger the multiworld textbox, sound effect to play when the textbox opens, number to
            # increment the received items count by, and the text to go into the multiworld textbox. The game will then
            # do the rest when it's able to.
            elif num_received_items < len(ctx.items_received) and ok_to_inject and not self.currently_dead:

                # Figure out what inventory array and offset from said array to increase based on what we are
                # receiving.
                next_item = ctx.items_received[num_received_items]
                pickup_type = (next_item.item & 0xFF00) >> 8
                pickup_index = next_item.item & 0xFF

                item_name = ctx.item_names.lookup_in_slot(next_item.item)

                if pickup_type in CVHODIS_INVENTORIES:
                    inv_array = curr_invs[pickup_type]
                    inv_array_start = CVHODIS_INVENTORIES[pickup_type].main_start_addr
                    text_id = int.to_bytes(CVHODIS_INVENTORIES[pickup_type].text_id_start + pickup_index,
                                           2, "little")
                    # If the item is JB or MK's Bracelet, play the major pickup sound with the small textbox. These are
                    # the only two items to use this specific combination.
                    if item_name in [item_names.equip_bracelet_jb, item_names.equip_bracelet_mk]:
                        mssg_sfx_id = SOUND_ID_PICKUP_MAJOR
                        text_id_buffer_addr = QUEUED_TEXTBOX_SMALL_ADDRESS
                    # If the item normally calls a large textbox when picked up, play the major pickup sound and choose
                    # the large textbox buffer to write the text ID at.
                    elif CVHODIS_INVENTORIES[pickup_type].is_large_textbox:
                        mssg_sfx_id = SOUND_ID_PICKUP_MAJOR
                        text_id_buffer_addr = QUEUED_TEXTBOX_LARGE_ADDRESS
                    # Otherwise, play the minor pickup sound and choose the small textbox buffer to write the ID at.
                    else:
                        mssg_sfx_id = SOUND_ID_PICKUP_MINOR
                        text_id_buffer_addr = QUEUED_TEXTBOX_SMALL_ADDRESS
                # If the pickup's type ID had no mapping in the inventory data dict, assume it's a Max Up and everything
                # that implies.
                else:
                    inv_array = []
                    inv_array_start = 0
                    text_id = int.to_bytes(pickup_index + 1, 1, "little")
                    mssg_sfx_id = SOUND_ID_PICKUP_MAX_UP
                    text_id_buffer_addr = QUEUED_MAX_UP_GRAPHIC_ADDRESS

                player_name = ctx.player_names[next_item.player]
                # Truncate the player name.
                if len(player_name) > PLAYER_NAME_LIMIT:
                    player_name = player_name[:PLAYER_NAME_LIMIT]

                # If the Item came from a different player, display a custom received message. Otherwise, display the
                # vanilla received message for that Item.
                #if next_item.player != ctx.slot:
                    # text_id_1 = TEXT_ID_MULTIWORLD_MESSAGE
                #    received_text = cvhodis_string_to_bytearray(f"「{item_name}」 received from "
                #                                                f"「{player_name}」◊", "big middle", 0)
                #    text_write = [(QUEUED_TEXT_STRING_START, bytes(received_text), "ROM")]
                #else:
                    # text_id_1 = ALL_CVHODIS_ITEMS[item_name].text_id
                #    text_write = []

                refill_write = []
                inv_writes = []
                inv_guards = []

                # If the Item is stored in a count and not a bitfield, check to see if the player has 99 of that Item.
                # If they do, don't increase their count of that Item any further.
                if pickup_type in CVHODIS_INVENTORIES:
                    if not CVHODIS_INVENTORIES[pickup_type].is_bitfield:
                        if inv_array[pickup_index] + 1 <= 99:
                            inv_address = inv_array_start + pickup_index
                            inv_guards += [(inv_address, int.to_bytes(inv_array[pickup_index], 1, "little"), "EWRAM")]
                            inv_writes += [(inv_address, int.to_bytes(inv_array[pickup_index] + 1, 1, "little"),
                                            "EWRAM")]

                    # If the Item is stored in a bitfield, set the bit for that Item in the bitfield.
                    else:
                        inv_address = inv_array_start + (pickup_index // 8)
                        inv_guards += [(inv_address, int.to_bytes(inv_array[pickup_index // 8], 1, "little"), "EWRAM")]
                        inv_writes += [(inv_address, int.to_bytes(
                            inv_array[pickup_index // 8] | (0x01 << (pickup_index % 8)), 1, "little"), "EWRAM")]
                        # If the Item being received is a Relic, turn on that Relic for the player in addition to
                        # putting it in their inventory.
                        if pickup_type == PickupTypes.RELIC:
                            relic_equip_addr = RELICS_EQUIPPED_BITFIELD_START + (pickup_index // 8)
                            inv_guards += [(relic_equip_addr, int.to_bytes(
                                enabled_relics[pickup_index // 8], 1, "little"), "EWRAM")]
                            inv_writes += [(relic_equip_addr, int.to_bytes(
                                enabled_relics[pickup_index // 8] | (0x01 << (pickup_index % 8)), 1,
                                "little"),"EWRAM")]
                        # If the Item being received is a Spell Book and no Spell Book is currently equipped (implying
                        # it is the first one received), equip that Spell Book automatically without turning it on.
                        elif pickup_type == PickupTypes.SPELLBOOK and not curr_book:
                            inv_writes += [(CURRENT_BOOK_ADDRESS, int.to_bytes(pickup_index + 1, 1, "little"),"EWRAM")]
                # If the Item's pickup type was not in the inventory data dict, meaning it is a Max Up, handle that
                # behavior here.
                else:
                    # If it's a Life Max Up being received, increment the player's max HP by 5 (if it's not above the
                    # max already) and give them a full health refill.
                    if item_name == item_names.max_life:
                        if max_hp + MAX_UP_INCREMENT_VALUE <= MAX_STAT_VALUE:
                            new_hp = max_hp + MAX_UP_INCREMENT_VALUE
                        else:
                            new_hp = MAX_STAT_VALUE
                        inv_guards += [(MAX_STATS_COUNTS_START, int.to_bytes(max_hp, 2, "little"), "EWRAM")]
                        inv_writes += [(MAX_STATS_COUNTS_START, int.to_bytes(new_hp, 2, "little"), "EWRAM")]
                        refill_write = [(CURRENT_HP_ADDRESS, int.to_bytes(new_hp, 2, "little"), "EWRAM")]
                    # If it's a Heart Max Up being received, increment the player's max Hearts by 5 (if it's not above
                    # the max already) and increase their current Hearts by 5 (if it's not above the new max).
                    else:
                        if max_hearts + MAX_UP_INCREMENT_VALUE <= MAX_STAT_VALUE:
                            new_max_hearts = max_hearts + MAX_UP_INCREMENT_VALUE
                        else:
                            new_max_hearts = MAX_STAT_VALUE

                        if curr_hearts + MAX_UP_INCREMENT_VALUE > new_max_hearts:
                            new_curr_hearts = new_max_hearts
                        else:
                            new_curr_hearts = curr_hearts + MAX_UP_INCREMENT_VALUE
                        inv_guards += [(MAX_STATS_COUNTS_START + 4, int.to_bytes(max_hearts, 2, "little"), "EWRAM")]
                        inv_writes += [(MAX_STATS_COUNTS_START + 4, int.to_bytes(new_max_hearts, 2, "little"), "EWRAM")]
                        refill_write = [(CURRENT_HEARTS_ADDRESS, int.to_bytes(new_curr_hearts, 2, "little"), "EWRAM")]

                await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                            [(text_id_buffer_addr, text_id, "EWRAM"),
                                             (QUEUED_RECEIVED_INDEX_INCREMENT_ADDRESS, b"\x01", "EWRAM"),
                                             (QUEUED_SOUND_ID_ADDRESS, mssg_sfx_id, "EWRAM")]
                                            + inv_writes + refill_write,
                                            # Make sure the number of received items and inventory to overwrite are
                                            # still what we expect them to be.
                                            [(NUM_RECEIVED_ITEMS_ADDRESS, read_state[len(CVHODIS_INVENTORIES) + 3],
                                              "EWRAM")]
                                            + inv_guards),

            # Check how many bits are set in the placed furniture flags array to determine whether the player has
            # completed the furniture objective (if more than 0 pieces are required).
            if placed_furniture_flags.bit_count() >= ctx.slot_data["furniture_amount_required"] \
                    and ctx.slot_data["furniture_amount_required"]:
                self.completed_furniture = True

            # Check each bit in the event flags array for set AP event flags.
            # NOTE: Flag IDs in this game are a bit strange in that they follow this bit format:
            # A AAAB BBBB
            # A = Index for the bitflag word to store the flag in, starting at the flag array start address.
            # B = ID for which bit within the word specified by A should be set, starting from the far right of it
            # (after converting to big endian).
            checked_set_events = {flag_name: False for flag, flag_name in EVENT_FLAG_MAP.items()}
            for word_index, word in enumerate(event_flags_array):
                for bit_index in range(0x20):
                    and_value = 0x01 << bit_index

                    if not word & and_value:
                        continue

                    # To get the proper flag ID, take the word index, right shift it up by 5, and add the bit index to
                    # that.
                    flag_id = (word_index << 5) + bit_index

                    # Due to how the sequence of events is set up in-game, the Worst Ending flag should only be
                    # registered if the Dracula Wraith intro flag is not also set.
                    if flag_id not in EVENT_FLAG_MAP or (flag_id == FLAG_WORST_ENDING and event_flags_array[2] & 0x100):
                        continue

                    checked_set_events[EVENT_FLAG_MAP[flag_id]] = True

                    # Update the client's statuses for each of the goal objectives.
                    if flag_id == FLAG_MEDIUM_ENDING:
                        self.got_medium_ending = True

                    if flag_id == FLAG_WORST_ENDING:
                        self.got_worst_ending = True

                    if flag_id == FLAG_BEST_ENDING:
                        self.got_best_ending = True

            # Check the pickup flags for any checked Locations that can be sent.
            locs_to_send = set()
            for word_index, word in enumerate(pickup_flags_array):
                for bit_index in range(0x20):
                    and_value = 0x01 << bit_index

                    if not word & and_value:
                        continue

                    # To get the proper flag ID, take the word index, right shift it up by 5, and add the bit index to
                    # that.
                    flag_id = (word_index << 5) + bit_index

                    location_id = flag_id + BASE_ID
                    if location_id in ctx.server_locations:
                        locs_to_send.add(location_id)

            # Send Locations if there are any to send.
            if locs_to_send != self.local_checked_locations:
                self.local_checked_locations = locs_to_send

                if locs_to_send is not None:
                    # Capture all the Locations with non-local Items to send that are in ctx.missing_locations
                    # (the ones that were definitely never sent before).
                    if ctx.locations_info:
                        self.sent_message_queue += [loc for loc in locs_to_send if loc in ctx.missing_locations and
                                                    ctx.locations_info[loc].player != ctx.slot]
                    # If we still don't have the locations info at this point, send another LocationScout packet just
                    # in case something went wrong, and we never received the initial LocationInfo packet.
                    else:
                        await ctx.send_msgs([{
                            "cmd": "LocationScouts",
                            "locations": [code for name, code in get_location_names_to_ids().items()
                                          if code in ctx.server_locations],
                            "create_as_hint": 0
                        }])

                    await ctx.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": list(locs_to_send)
                    }])

            # Determine all of our win conditions based on what combination of options are being used.
            win_cons = []
            if ctx.slot_data["medium_ending_required"]:
                win_cons += [self.got_medium_ending]
            if ctx.slot_data["worst_ending_required"]:
                win_cons += [self.got_worst_ending]
            if ctx.slot_data["best_ending_required"]:
                win_cons += [self.got_best_ending]
            if ctx.slot_data["furniture_amount_required"]:
                win_cons += [self.completed_furniture]

            # Send game clear if we've satisfied all the win conditions.
            if not ctx.finished_game and all(win_cons):
                ctx.finished_game = True
                await ctx.send_msgs([{
                    "cmd": "StatusUpdate",
                    "status": ClientStatus.CLIENT_GOAL
                }])

            # Update the tracker event flags
            if checked_set_events != self.client_set_events and ctx.slot is not None:
                event_bitfield = 0
                for index, (flag, flag_name) in enumerate(EVENT_FLAG_MAP.items()):
                    if checked_set_events[flag_name]:
                        event_bitfield |= 1 << index

                await ctx.send_msgs([{
                    "cmd": "Set",
                    "key": f"castlevania_hodis_events_{ctx.team}_{ctx.slot}",
                    "default": 0,
                    "want_reply": False,
                    "operations": [{"operation": "or", "value": event_bitfield}],
                }])
                self.client_set_events = checked_set_events

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass
