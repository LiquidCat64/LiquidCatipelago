from typing import TYPE_CHECKING
from .cvlod_text import cvlod_text_wrap, cvlod_string_to_bytearray, LEN_LIMIT_MULTIWORLD_TEXT
from .rom import ARCHIPELAGO_CLIENT_COMPAT_VER, ARCHIPELAGO_IDENTIFIER_START
from .data.enums import Scenes, Players, Items, StageNames

from BaseClasses import ItemClassification
from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
import base64
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

GAME_STATE_ADDRESS = 0x1CAA30  # Not actually a natural consistent address, but one the game is hacked to mirror it to.
QUEUED_REMOTE_RECEIVES_START = 0x1CAA4C
SAVE_STRUCT_START = 0x1CAA60
GAMEPLAY_STATE_FLAGS_START = 0x1CABC8
NUM_RECEIVED_ITEMS_ADDRESS = 0x1CABBE
CURRENT_CUTSCENE_ID_ADDRESS = 0x1CAE8B
QUEUED_TEXTBOX_TEXT_START = 0x1E5CC
QUEUED_MULTIWORLD_MSG_START = 0x1E6DC
ROM_NAME_START = 0x20

GAME_STATE_GAMEPLAY = 0x03
GAME_STATE_CREDITS = 0x0A
ENDING_CUTSCENE_IDS = [0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x3C]

DEATHLINK_AREA_NUMBERS = [1, 2, 2, 3, 3, 3, 3, 4, 5, 9, 9, 9, 9, 9, 9, 9,
                          0, 0, 0, 17, 16, 16, 17, 15, 16, 17, 3, 14, 17, 13, 12, 12,
                          12, 10, 10, 8, 8, 7, 7, 11, 15, 15, 6, 17, 17, 17, 16, 17, 17, 17]

DEATHLINK_AREA_NAMES = [StageNames.FOGGY, StageNames.FOREST, StageNames.C_WALL, StageNames.VILLA,
                        StageNames.TUNNEL, StageNames.WATERWAY, StageNames.OUTER, StageNames.ART, StageNames.RUINS,
                        StageNames.CENTER, StageNames.SCIENCE, StageNames.DUEL, StageNames.EXECUTION,
                        StageNames.SORCERY, StageNames.ROOM, StageNames.CLOCK, StageNames.KEEP,
                        "Level: You Cheated"]

class CastlevaniaLoDClient(BizHawkClient):
    game = "Castlevania - Legacy of Darkness"
    system = "N64"
    patch_suffix = ".apcvlod"
    self_induced_death: bool
    time_of_sent_death: float | None
    local_checked_locations: set[int]
    death_causes: list[str]
    currently_dead: bool
    currently_shopping: bool
    alt_scene_setup: str

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        from CommonClient import logger

        try:
            # Check ROM name/patch version
            game_names = await bizhawk.read(ctx.bizhawk_ctx, [(ROM_NAME_START, 0x14, "ROM"),
                                                              (ARCHIPELAGO_IDENTIFIER_START, 12, "ROM")])
            if game_names[0].decode("ascii") != "CASTLEVANIA2        ":
                return False
            if game_names[1] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                logger.info("ERROR: You appear to be running an unpatched version of Castlevania: Legacy of Darkness. "
                            "You need to generate a patch file and use it to create a patched ROM.")
                return False
            if game_names[1].decode("ascii") != ARCHIPELAGO_CLIENT_COMPAT_VER:
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
        auth_raw = (await bizhawk.read(ctx.bizhawk_ctx, [(0xFFBFE0, 16, "ROM")]))[0]
        ctx.auth = base64.b64encode(auth_raw).decode("utf-8")
        # Initialize all the local client attributes here so that nothing will be carried over from a previous LoD if
        # the player tried changing LoD ROMs without resetting their Bizhawk Client instance.
        self.self_induced_death = False
        self.time_of_sent_death = None
        self.local_checked_locations = set()
        self.death_causes = []
        self.currently_dead = False
        self.currently_shopping = False
        self.alt_scene_setup = ""

    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd != "Bounced" or "tags" not in args or ctx.slot is None:
            return
        if "DeathLink" in args["tags"] and args["data"]["time"] != self.time_of_sent_death:
            if "cause" in args["data"]:
                cause = args["data"]["cause"]
                # If the other game sent a death with a blank string for the cause, use the default death message.
                if cause == "":
                    cause = f"{args['data']['source']} killed you without a word!"
                # Truncate the death cause message at 130 characters (this is almost the max we can send to the game).
                if len(cause) > 130:
                    cause = cause[0:130]
            else:
                cause = f"{args['data']['source']} killed you without a word!"

            # Highlight the player that killed us in the game's yellow text.
            if args['data']['source'] in cause:
                words = cause.split(args['data']['source'], 1)
                cause = words[0] + "✨" + args['data']['source'] + "✨" + words[1]

            self.death_causes.append(cause)

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot is None:
            return

        try:
            read_state = await bizhawk.read(ctx.bizhawk_ctx, [(GAME_STATE_ADDRESS, 1, "RDRAM"),
                                                              (QUEUED_REMOTE_RECEIVES_START, 4, "RDRAM"),
                                                              (SAVE_STRUCT_START, 356, "RDRAM"),
                                                              (GAMEPLAY_STATE_FLAGS_START, 4, "RDRAM"),
                                                              (CURRENT_CUTSCENE_ID_ADDRESS, 1, "RDRAM"),
                                                              (ARCHIPELAGO_IDENTIFIER_START + 0xE, 2, "ROM")])

            game_state = int.from_bytes(read_state[0], "big")
            queued_receieve_bytes = read_state[1]
            save_struct = read_state[2]
            gameplay_state_flags = int.from_bytes(read_state[3], "big")
            cutscene_value = int.from_bytes(read_state[4], "big")
            num_received_items = int.from_bytes(bytearray(save_struct[0x15E:0x160]), "big")
            slot_flags = int.from_bytes(read_state[5], "big")
            curr_hp = int.from_bytes(save_struct[0xDA:0xDC], "big")

            # Make sure we are in the Gameplay or Credits states before detecting/giving anything from the Multiworld.
            # If we are in any other state, such as the Game Over state, set self_induced_death to false, so we can once
            # again send a DeathLink once we are back in the Gameplay state.
            if game_state not in [GAME_STATE_GAMEPLAY, GAME_STATE_CREDITS]:
                self.currently_dead = False
                return

            # Enable DeathLink if the bit for it is set in our ROM slot flags.
            if "DeathLink" not in ctx.tags and slot_flags & 0x0100:
                await ctx.update_death_link(True)

            # Scout the Renon shop locations if the shopsanity flag is written in the ROM.
            #if rom_flags & 0x0001 and ctx.locations_info == {}:
            #    await ctx.send_msgs([{
            #            "cmd": "LocationScouts",
            #            "locations": [base_id + i for i in range(0x1C8, 0x1CF)],
            #            "create_as_hint": 0
            #        }])

            # Send a DeathLink if we died on our own independently of receiving another one, or if Child Henry died.
            # To know if Child Henry died during the escort sequence, check for flags 00004000 and 00000080 both being
            # set in the gameplay state flags.
            if "DeathLink" in ctx.tags and not self.currently_dead and \
                    (curr_hp == 0 or 0x00004080 & gameplay_state_flags == 0x00004080):
                self.currently_dead = True

                # If the player died at the Castle Keep exterior map on one of the Room of Clocks boss towers
                # (determinable by checking the entrance value as well as the map value), consider Room of Clocks the
                # actual area of death.
                if save_struct[0x131] == Scenes.CASTLE_KEEP_EXTERIOR and save_struct[0x133] in [0, 1]:
                    area_of_death = StageNames.ROOM
                # If they died in Renon's arena in Room of Clocks (entrance 3), consider Castle Keep the actual area.
                elif save_struct[0x131] == Scenes.ROOM_OF_CLOCKS and save_struct[0x133] == 3:
                    area_of_death = StageNames.KEEP
                # If we're in the Fan Meeting Room or Algenie/Medusa Arena scenes, check the current alternate scene
                # identifier to determine which stage-specific scene setup we're in.
                elif save_struct[0x131] == Scenes.ALGENIE_MEDUSA_ARENA and self.alt_scene_setup:
                    if self.alt_scene_setup == "a":
                        area_of_death = StageNames.TUNNEL
                    else:
                        area_of_death = StageNames.WATERWAY
                elif save_struct[0x131] == Scenes.FAN_MEETING_ROOM and self.alt_scene_setup:
                    if self.alt_scene_setup == "b":
                        area_of_death = StageNames.CENTER
                    else:
                        area_of_death = StageNames.OUTER
                # Otherwise, determine what area the player perished in from the current map ID.
                else:
                    area_of_death = DEATHLINK_AREA_NAMES[DEATHLINK_AREA_NUMBERS[save_struct[0x131]]]

                # If Child Henry was the one who perished (read: we still have health), use a special message.
                # The message will be extra special if we are Adult Henry!
                if curr_hp and save_struct[0xD5] == Players.HENRY:
                    death_message = (f'"My sincere apologies, but {ctx.player_names[ctx.slot]}, in letting their '
                                     f'younger self get killed, created a huge paradox! For the sake of your own '
                                     f'timeline not collapsing in on itself, I took it upon myself to rewind you all '
                                     f'safely. Until we meet again!"\n'
                                     '-Saint Germain')
                elif curr_hp:
                    death_message = (f"{ctx.player_names[ctx.slot]} failed to protect little Henry, whose vengeful "
                                     f"spirit murdered everyone!")
                # If we had the Vamp status while dying, use a special message for it.
                elif save_struct[0xA4] & 0x08:
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

            # If we have any queued death causes, and the non-multiworld remote item byte is unoccupied, handle
            # DeathLink giving here.
            if self.death_causes and not self.currently_dead:
                # Inject the oldest cause text as a textbox message. It will be written not in the muitworld message
                # buffer, but directly in the main textbox buffer that the mult buffer would normally get copied to.
                # This is because we're giving an Item in the non-multi byte to cue up this textbox.
                death_text = cvlod_text_wrap(self.death_causes[0], LEN_LIMIT_MULTIWORLD_TEXT)
                await bizhawk.write(ctx.bizhawk_ctx,
                                    [(QUEUED_TEXTBOX_TEXT_START + 2,
                                      cvlod_string_to_bytearray(death_text, wrap=False, add_end_char=True), "RDRAM"),
                                     # Count the number of newlines. This will be written into our text buffer header.
                                     (QUEUED_TEXTBOX_TEXT_START, [death_text.count("\n") + 1], "RDRAM"),
                                     # Set the "DeathLink byte" to 1 so the game will handle killing the player.
                                     (QUEUED_REMOTE_RECEIVES_START + 3, b"\x01", "RDRAM"),
                                     # Give a Special3 (AP Item) to cue the textbox.
                                     (QUEUED_REMOTE_RECEIVES_START, [Items.SPECIAL3], "RDRAM")])

                # Delete the oldest death cause that we just wrote and set currently_dead to True so the client doesn't
                # think we just died on our own on the subsequent frames before the Game Over state.
                del(self.death_causes[0])
                self.currently_dead = True

            # If somehow we have more than 0 HP, Child Henry is alive, and the DeathLink byte is un-set while the client
            # thinks we are dead at this point, set ourselves back to alive. The player likely loaded a savestate while
            # in the dying animation and before the game state changed to Game Over.
            elif curr_hp > 0 and 0x00004080 & gameplay_state_flags == 0x00000000 and self.currently_dead \
                    and not queued_receieve_bytes[3]:
                self.currently_dead = False

            # If the game hasn't received all items yet, the received item struct doesn't contain an item, the current
            # number of received items still matches what we read before, and there are no open text boxes, then fill
            # it with the next item and write the "item from player" text in its buffer. The game will increment the
            # number of received items on its own.
            elif num_received_items < len(ctx.items_received) and not self.currently_dead:
                next_item = ctx.items_received[num_received_items]
                # If the Item was sent by a different player, generate a custom string saying who the Item was from.
                if next_item.player != ctx.slot:
                    received_text = cvlod_text_wrap(f"{ctx.item_names.lookup_in_slot(next_item.item)}\n"
                                                    f"from {ctx.player_names[next_item.player]}",
                                                    textbox_len_limit=LEN_LIMIT_MULTIWORLD_TEXT)
                    # If the Item is Progression, wrap the whole string up in the "color text" character to indicate
                    # such.
                    if next_item.flags & ItemClassification.progression:
                        received_text = "✨" + received_text + "✨"
                    # Count the number of newlines. This will be written into our text buffer header.
                    num_lines = received_text.count("\n") + 1
                # Otherwise, if it was sent by the same player, we'll inject a blank string with a zero line count so
                # the game will simply use the Item's regular in-game name string.
                else:
                    received_text = ""
                    num_lines = 0

                await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                            [(QUEUED_REMOTE_RECEIVES_START + 1, [next_item.item & 0xFF], "RDRAM"),
                                             (QUEUED_MULTIWORLD_MSG_START, [num_lines], "RDRAM"),
                                             (QUEUED_MULTIWORLD_MSG_START + 2,
                                              cvlod_string_to_bytearray(received_text, wrap=False, add_end_char=True),
                                              "RDRAM")],
                                            # Make sure the number of received items and inventory to overwrite are
                                            # still what we expect them to be.
                                            [(QUEUED_REMOTE_RECEIVES_START + 1, [0x00], "RDRAM"),
                                             (NUM_RECEIVED_ITEMS_ADDRESS, save_struct[0x15E:0x160], "RDRAM"),
                                             # Timer till next remote textbox.
                                             (QUEUED_REMOTE_RECEIVES_START + 2, [0x00], "RDRAM")])

            pickup_flags_array = [int.from_bytes(save_struct[0x00:0xB8][i:i + 4], "big")
                                  for i in range(0, len(save_struct[0x00:0xB8]), 4)]

            # Check each bit in the event flags array for any checked Locations that can be sent.
            # Flag IDs in this game follow this bit format:
            # A AAAB BBBB
            # A = Index for the bitflag word to store the flag in, starting at the flag array start address.
            # B = ID for which bit within the word specified by A should be set, starting from the far left of it.
            locs_to_send = set()
            for word_index, word in enumerate(pickup_flags_array):
                for bit_index in range(0x20):
                    and_value = 0x80000000 >> bit_index

                    # If the current bit we're looking at is not set, continue on to the next loop.
                    if not word & and_value:
                        continue

                    # To get the proper flag ID, take the word index, right shift it up by 5, and add the bit index to
                    # that.
                    flag_id = (word_index << 5) + bit_index

                    # Check if it's one of the randomizer's alternate setup flags that is set (0x2A1, 0x2A2, or 0x2A3).
                    # This is how we tell which stage-specific "version" of the Queen Algenie/Medusa Arena and
                    # Fan Meeting Room scenes we're in.
                    if flag_id == 0x2A1:
                        self.alt_scene_setup = "a"
                    elif flag_id == 0x2A2:
                        self.alt_scene_setup = "b"
                    elif flag_id == 0x2A3:
                        self.alt_scene_setup = "c"
                    else:
                        self.alt_scene_setup = ""

                    # If the flag that we detected as set is an active Location ID, record it.
                    if flag_id in ctx.server_locations:
                        locs_to_send.add(flag_id)

            # Send Locations if there are any to send.
            if locs_to_send != self.local_checked_locations:
                self.local_checked_locations = locs_to_send

                if locs_to_send is not None:
                    await ctx.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": list(locs_to_send)
                    }])

            # Check the menu value to see if we are in Renon's shop, and set currently_shopping to True if we are.
            #if current_menu == 0xA:
            #    self.currently_shopping = True

            # If we are currently shopping, and the current menu value is 0 (meaning we just left the shop), hint the
            # un-bought shop locations that have progression.
            #if current_menu == 0 and self.currently_shopping:
            #    await ctx.send_msgs([{
            #        "cmd": "LocationScouts",
            #        "locations": [loc for loc, n_item in ctx.locations_info.items() if n_item.flags & 0b001],
            #        "create_as_hint": 2
            #    }])
            #    self.currently_shopping = False

            # Send game clear if we're in either any ending cutscene or the credits state.
            if not ctx.finished_game and (cutscene_value in ENDING_CUTSCENE_IDS or game_state == GAME_STATE_CREDITS):
                ctx.finished_game = True
                await ctx.send_msgs([{
                    "cmd": "StatusUpdate",
                    "status": ClientStatus.CLIENT_GOAL
                }])

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass
