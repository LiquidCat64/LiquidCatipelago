from typing import TYPE_CHECKING
from .locations import BASE_ID
from .text import cv64_text_wrap, cv64_string_to_bytearray

from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
import base64
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

PLAYER_COORDINATES_START = 0x9E1B0

# These flags are communicated to the tracker as a bitfield using this order.
# Modifying this here without also modifying the tracker will cause autotracking issues.
# TODO: Add the rest of the boss kill flags
EVENT_FLAG_MAP = {
    0x1BF: "FLAG_ACTIVATED_CRYSTAL",
    0xD2: "FLAG_DEFEATED_KING_SKELETON_1",
    0xD3: "FLAG_DEFEATED_FOREST_WERE_TIGER",
    0xD1: "FLAG_DEFEATED_KING_SKELETON_2",
    0x14F: "FLAG_DEFEATED_WHITE_DRAGONS",
    0xCC: "FLAG_DEFEATED_JA_OLDREY",
    0xCA: "FLAG_DEFEATED_UNDEAD_MAIDEN",
    0x5E: "FLAG_DEFEATED_LIZARD_MEN_TRIO",
    0x1A3: "FLAG_DEFEATED_BEHEMOTH",
    0x1BB: "FLAG_DEFEATED_ROSA",
    0x1B9: "FLAG_DEFEATED_CAMILLA",
    0x87: "FLAG_DEFEATED_WERE_JAGUAR",
    0x86: "FLAG_DEFEATED_WEREWOLF",
    0x85: "FLAG_DEFEATED_WERE_BULL",
    0x84: "FLAG_DEFEATED_DUEL_TOWER_WERE_TIGER",
    0xB9: "FLAG_DEFEATED_DEATH",
    0xB8: "FLAG_DEFEATED_ACTRISE",
    0xBE: "FLAG_DEFEATED_RENON",
    0xBD: "FLAG_DEFEATED_VINCENT",
}

DEATHLINK_AREA_NUMBERS = [0, 1, 1, 2, 2, 2, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5,
                          7, 9, 8, 6, 12, 12, 13, 11, 12, 5, 2, 10, 13, 13]

DEATHLINK_AREA_NAMES = ["Forest of Silence", "Castle Wall", "Villa", "Tunnel", "Underground Waterway", "Castle Center",
                        "Duel Tower", "Tower of Execution", "Tower of Science", "Tower of Sorcery", "Room of Clocks",
                        "Clock Tower", "Castle Keep", "Level: You Cheated"]


class Castlevania64Client(BizHawkClient):
    game = "Castlevania 64"
    system = "N64"
    patch_suffix = ".apcv64"
    sent_initial_packets: bool
    self_induced_death: bool
    time_of_sent_death: float | None
    received_deathlinks: int
    death_causes: list[str]
    client_set_events = dict[str, int]
    currently_shopping: bool
    current_map_id: int
    local_checked_locations: set[int]

    def __init__(self) -> None:
        super().__init__()
        self.local_checked_locations = set()

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        from CommonClient import logger

        try:
            # Check ROM name/patch version
            game_names = await bizhawk.read(ctx.bizhawk_ctx, [(0x20, 0x14, "ROM"), (0xBFBFD0, 12, "ROM")])
            if game_names[0].decode("ascii") != "CASTLEVANIA         ":
                return False
            if game_names[1] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                logger.info("ERROR: You appear to be running an unpatched version of Castlevania 64. "
                            "You need to generate a patch file and use it to create a patched ROM.")
                return False
            if game_names[1].decode("ascii") != "ARCHIPELAGO1":
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
        ctx.want_slot_data = False
        ctx.watcher_timeout = 0.125
        return True

    async def set_auth(self, ctx: "BizHawkClientContext") -> None:
        auth_raw = (await bizhawk.read(ctx.bizhawk_ctx, [(0xBFBFE0, 16, "ROM")]))[0]
        ctx.auth = base64.b64encode(auth_raw).decode("utf-8")
        # Initialize all the local client attributes here so that nothing will be carried over from a previous CV64 if
        # the player tried changing CV64 ROMs without resetting their Bizhawk Client instance.
        self.sent_initial_packets = False
        self.self_induced_death = False
        self.time_of_sent_death = None
        self.received_deathlinks = 0
        self.death_causes = []
        self.client_set_events = {flag_name: False for flag, flag_name in EVENT_FLAG_MAP.items()}
        self.currently_shopping = False
        self.current_map_id = 0xFF
        self.local_checked_locations = set()

    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd != "Bounced":
            return
        if "tags" not in args:
            return
        if "DeathLink" in args["tags"] and args["data"]["time"] != self.time_of_sent_death:
            self.received_deathlinks += 1
            if "cause" in args["data"]:
                cause = args["data"]["cause"]
                # If the other game sent a death with a blank string for the cause, use the default death message.
                if cause == "":
                    cause = f"{args['data']['source']} killed you without a word!"
                # Truncate the death cause message at 120 characters.
                if len(cause) > 120:
                    cause = cause[0:120]
            else:
                # If the other game sent a death with no cause at all, use the default death message.
                cause = f"{args['data']['source']} killed you without a word!"
            self.death_causes.append(cause)

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot is None:
            return

        try:
            # Get our Set events upon initial connection.
            if not self.sent_initial_packets:
                await ctx.send_msgs([{
                    "cmd": "Get",
                    "keys": [f"castlevania_64_events_{ctx.team}_{ctx.slot}"]
                }])
                self.sent_initial_packets = True

            read_state = await bizhawk.read(ctx.bizhawk_ctx, [(0x342084, 4, "RDRAM"),
                                                              (0x389BDE, 6, "RDRAM"),
                                                              (0x389BE4, 224, "RDRAM"),
                                                              (0x389EFB, 1, "RDRAM"),
                                                              (0x389EEF, 1, "RDRAM"),
                                                              (0xBFBFDE, 2, "ROM"),
                                                              # (PLAYER_COORDINATES_START, 0xC, "RDRAM")
                                                              ])

            game_state = int.from_bytes(read_state[0], "big")
            save_struct = read_state[2]
            written_deathlinks = int.from_bytes(bytearray(read_state[1][4:6]), "big")
            deathlink_induced_death = int.from_bytes(bytearray(read_state[1][0:1]), "big")
            cutscene_value = int.from_bytes(read_state[3], "big")
            current_menu = int.from_bytes(read_state[4], "big")
            num_received_items = int.from_bytes(bytearray(save_struct[0xDA:0xDC]), "big")
            rom_flags = int.from_bytes(read_state[5], "big")
            current_map_id = save_struct[0xAD]
            current_entrance_id = save_struct[0xAF]
            # player_coords = read_state[6] TODO: Implement some kind of position checking.

            # Make sure we are in the Gameplay or Credits states before detecting sent locations and/or DeathLinks.
            # If we are in any other state, such as the Game Over state, set self_induced_death to false, so we can once
            # again send a DeathLink once we are back in the Gameplay state.
            if game_state not in [0x00000002, 0x0000000B]:
                self.self_induced_death = False
                return

            # Enable DeathLink if the bit for it is set in our ROM flags.
            if "DeathLink" not in ctx.tags and rom_flags & 0x0100:
                await ctx.update_death_link(True)

            # Scout the Renon shop locations if the shopsanity flag is written in the ROM.
            if rom_flags & 0x0001 and ctx.locations_info == {}:
                await ctx.send_msgs([{
                        "cmd": "LocationScouts",
                        "locations": [BASE_ID + i for i in range(0x1C8, 0x1CF)],
                        "create_as_hint": 0
                    }])

            # Check to see if the player's current map changed. If it did, notify the server so the PopTracker map can
            # auto-change.
            if 0xFF != current_map_id != self.current_map_id:
                await ctx.send_msgs([{
                    "cmd": "Set",
                    "key": f"castlevania_64_current_map_{ctx.team}_{ctx.slot}",
                    "default": 0,
                    "want_reply": False,
                    "operations": [{"operation": "replace", "value": current_map_id}],
                }])
                self.current_map_id = current_map_id

            # Send a DeathLink if we died on our own independently of receiving another one.
            if "DeathLink" in ctx.tags and save_struct[0xA4] & 0x80 and not self.self_induced_death and not \
                    deathlink_induced_death:
                self.self_induced_death = True

                # If the player died at the Castle Keep exterior map on one of the Room of Clocks boss towers
                # (determinable by checking the entrance value as well as the map value), consider Room of Clocks the
                # actual area of death.
                if current_map_id == 0x14 and current_entrance_id in [0, 1]:
                    area_of_death = DEATHLINK_AREA_NAMES[10]
                # Otherwise, determine what area the player perished in from the current map ID.
                else:
                    area_of_death = DEATHLINK_AREA_NAMES[DEATHLINK_AREA_NUMBERS[current_map_id]]

                # If we had the Vamp status while dying, use a special message.
                if save_struct[0xA4] & 0x08:
                    death_message = (f"{ctx.player_names[ctx.slot]} became a vampire at {area_of_death} and drank your "
                                     f"blood!")
                # Otherwise, use the generic one.
                else:
                    death_message = f"{ctx.player_names[ctx.slot]} perished in {area_of_death}. Dracula has won!"

                # Send the death.
                await ctx.send_death(death_message)

                # Record the time in which the death was sent so when we receive the packet we can tell it wasn't our
                # own death. ctx.on_deathlink overwrites it later, so it MUST be grabbed now.
                self.time_of_sent_death = ctx.last_death_link

            # Write any DeathLinks received along with the corresponding death cause starting with the oldest.
            # To minimize Bizhawk Write jank, the DeathLink write will be prioritized over the item received one.
            if self.received_deathlinks and not self.self_induced_death and not written_deathlinks:
                death_text, num_lines = cv64_text_wrap(self.death_causes[0], 96)
                await bizhawk.write(ctx.bizhawk_ctx, [(0x389BE3, [0x01], "RDRAM"),
                                                      (0x389BDF, [0x11], "RDRAM"),
                                                      (0x18BF98, bytearray([0xA2, 0x0B]) +
                                                       cv64_string_to_bytearray(death_text, False), "RDRAM"),
                                                      (0x18C097, [num_lines], "RDRAM")])
                self.received_deathlinks -= 1
                del self.death_causes[0]
            else:
                # If the game hasn't received all items yet, the received item struct doesn't contain an item, the
                # current number of received items still matches what we read before, and there are no open text boxes,
                # then fill it with the next item and write the "item from player" text in its buffer. The game will
                # increment the number of received items on its own.
                if num_received_items < len(ctx.items_received):
                    next_item = ctx.items_received[num_received_items]
                    if next_item.flags & 0b001:
                        text_color = bytearray([0xA2, 0x0C])
                    elif next_item.flags & 0b010:
                        text_color = bytearray([0xA2, 0x0A])
                    elif next_item.flags & 0b100:
                        text_color = bytearray([0xA2, 0x0B])
                    else:
                        text_color = bytearray([0xA2, 0x02])

                    # Get the item's player's name. If it's longer than 40 characters, truncate it at 40.
                    # 35 should be the max number of characters in a server player name right now (16 for the original
                    # name + 16 for the alias + 3 for the added parenthesis and space), but if it ever goes higher it
                    # should be future-proofed now. No need to truncate CV64 items names because its longest item name
                    # gets nowhere near the limit.
                    player_name = ctx.player_names[next_item.player]
                    if len(player_name) > 40:
                        player_name = player_name[0:40]

                    received_text, num_lines = cv64_text_wrap(f"{ctx.item_names.lookup_in_game(next_item.item)}\n"
                                                              f"from {player_name}", 96)
                    await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                [(0x389BE1, [next_item.item & 0xFF], "RDRAM"),
                                                 (0x18C0A8, text_color + cv64_string_to_bytearray(received_text, False),
                                                  "RDRAM"),
                                                 (0x18C1A7, [num_lines], "RDRAM")],
                                                [(0x389BE1, [0x00], "RDRAM"),   # Remote item reward buffer
                                                 (0x389CBE, save_struct[0xDA:0xDC], "RDRAM"),  # Received items
                                                 (0x342891, [0x02], "RDRAM")])   # Textbox state

            flag_bytes = bytearray(save_struct[0x00:0x44]) + bytearray(save_struct[0x90:0x9F])
            locs_to_send = set()

            # Check each bit in each flag byte for set Location and event flags.
            checked_set_events = {flag_name: False for flag, flag_name in EVENT_FLAG_MAP.items()}
            for byte_i, byte in enumerate(flag_bytes):
                for i in range(8):
                    and_value = 0x80 >> i
                    if byte & and_value != 0:
                        flag_id = byte_i * 8 + i

                        location_id = flag_id + BASE_ID
                        if location_id in ctx.server_locations:
                            locs_to_send.add(location_id)

                        if flag_id in EVENT_FLAG_MAP:
                            checked_set_events[EVENT_FLAG_MAP[flag_id]] = True

            # Send locations if there are any to send.
            if locs_to_send != self.local_checked_locations:
                self.local_checked_locations = locs_to_send

                if locs_to_send is not None:
                    await ctx.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": list(locs_to_send)
                    }])

            # Check the menu value to see if we are in Renon's shop, and set currently_shopping to True if we are.
            if current_menu == 0xA:
                self.currently_shopping = True

            # If we are currently shopping, and the current menu value is 0 (meaning we just left the shop), hint the
            # un-bought shop locations that have progression.
            if current_menu == 0 and self.currently_shopping:
                await ctx.send_msgs([{
                    "cmd": "LocationScouts",
                    "locations": [loc for loc, n_item in ctx.locations_info.items() if n_item.flags & 0b001],
                    "create_as_hint": 2
                }])
                self.currently_shopping = False

            # Send game clear if we're in either any ending cutscene or the credits state.
            if not ctx.finished_game and (0x26 <= int(cutscene_value) <= 0x2E or game_state == 0x0000000B):
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
                    "key": f"castlevania_64_events_{ctx.team}_{ctx.slot}",
                    "default": 0,
                    "want_reply": False,
                    "operations": [{"operation": "or", "value": event_bitfield}],
                }])
                self.client_set_events = checked_set_events

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass
