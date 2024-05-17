from typing import TYPE_CHECKING, Optional, Set
from .locations import base_id
from .text import cvlod_text_wrap, cvlod_string_to_bytes

from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext
else:
    BizHawkClientContext = object


class CastlevaniaLoDClient(BizHawkClient):
    game = "Castlevania - Legacy of Darkness"
    system = "N64"
    patch_suffix = ".apcvlod"
    self_induced_death = False
    received_deathlinks = 0
    death_link = False
    local_checked_locations: Set[int]
    rom_slot_name: Optional[str]

    def __init__(self) -> None:
        super().__init__()
        self.local_checked_locations = set()
        self.rom_slot_name = None

    async def validate_rom(self, ctx: BizHawkClientContext) -> bool:
        from CommonClient import logger

        try:
            # Check if ROM is some version of Castlevania: Legacy of Darkness
            game_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x20, 0x14, "ROM")]))[0]).decode("ascii")
            if game_name != "CASTLEVANIA2        ":
                return False
            
            # Check if we can read the slot name. Doing this here instead of set_auth as a protection against
            # validating a ROM where there's no slot name to read.
            try:
                slot_name_bytes = (await bizhawk.read(ctx.bizhawk_ctx, [(0xFFBFE0, 0x10, "ROM")]))[0]
                self.rom_slot_name = bytes([byte for byte in slot_name_bytes if byte != 0]).decode("utf-8")
            except UnicodeDecodeError:
                logger.info("Could not read slot name from ROM. Are you sure this ROM matches this client version?")
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

    async def set_auth(self, ctx: BizHawkClientContext) -> None:
        ctx.auth = self.rom_slot_name

    def on_package(self, ctx: BizHawkClientContext, cmd: str, args: dict) -> None:
        if cmd == "Bounced":
            if "tags" in args:
                if "DeathLink" in args["tags"] and args["data"]["source"] != ctx.slot_info[ctx.slot].name:
                    self.received_deathlinks += 1

    async def game_watcher(self, ctx: BizHawkClientContext) -> None:

        try:
            read_state = await bizhawk.read(ctx.bizhawk_ctx, [(0x1CAA30, 1, "RDRAM"),
                                                              (0x1CAA4B, 5, "RDRAM"),
                                                              (0x1CAA60, 356, "RDRAM"),
                                                              (0x1CAE8B, 1, "RDRAM")])

            game_state = int.from_bytes(read_state[0], "big")
            save_struct = read_state[2]
            written_deathlinks = int.from_bytes(bytearray(read_state[1][5:]), "big")
            deathlink_induced_death = int.from_bytes(bytearray(read_state[1][0:1]), "big")
            cutscene_value = int.from_bytes(read_state[3], "big")
            num_received_items = int.from_bytes(bytearray(save_struct[0x15E:0x160]), "big")

            # Make sure we are in the Gameplay or Credits states before detecting sent locations and/or DeathLinks.
            # If we are in any other state, such as the Game Over state, set currently_dead to false, so we can once
            # again send a DeathLink once we are back in the Gameplay state.
            if game_state not in [0x3 or 0xA]:
                self.self_induced_death = False
                return

            # Enable DeathLink if it's on in our slot_data
            if ctx.slot_data is not None:
                if ctx.slot_data["death_link"]:
                    if not self.death_link:
                        self.death_link = True
                        await ctx.update_death_link(self.death_link)

            # Send a DeathLink if we died on our own independently of receiving another one.
            if "DeathLink" in ctx.tags and save_struct[0x124] & 0x80 and not self.self_induced_death and not \
                    deathlink_induced_death:
                self.self_induced_death = True
                await ctx.send_death("Dracula wins!")

            # Increase the game's number of received DeathLinks if the client has received some. To minimize Bizhawk
            # Write jank, the DeathLink write will be prioritized over the item received one.
            if self.received_deathlinks and not self.self_induced_death:
                written_deathlinks += self.received_deathlinks
                self.received_deathlinks = 0
                await bizhawk.write(ctx.bizhawk_ctx, [(0x1CAA4F, [written_deathlinks], "RDRAM")])
            else:
                # If the game hasn't received all items yet, the received item struct doesn't contain an item, the
                # current number of received items still matches what we read before, and there are no open text boxes,
                # then fill it with the next item and write the "item from player" text in its buffer. The game will
                # increment the number of received items on its own.
                if num_received_items < len(ctx.items_received):
                    next_item = ctx.items_received[num_received_items]
                    if next_item.flags & 0b001:
                        text_color = [0xA2, 0x0C]
                    elif next_item.flags & 0b010:
                        text_color = [0xA2, 0x0A]
                    elif next_item.flags & 0b100:
                        text_color = [0xA2, 0x0B]
                    else:
                        text_color = [0xA2, 0x02]
                    received_text, num_lines = cvlod_text_wrap(f"{ctx.item_names[next_item.item]}\n"
                                                               f"from {ctx.player_names[next_item.player]}", 96)
                    await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                [(0x1CAA4D, (next_item.item & 0xFF).to_bytes(1, "big"), "RDRAM")],
                                                 #(0x18C0A8, text_color + cvlod_string_to_bytes(received_text, False),
                                                 # "RDRAM"),
                                                 #(0x18C1A7, [num_lines], "RDRAM")],
                                                [(0x1CAA4D, [0x00], "RDRAM"),   # Remote item reward buffer
                                                 (0x1CABBE, save_struct[0x15E:0x160], "RDRAM"),  # Received items
                                                 (0x1CAA4E, [0x00], "RDRAM")])   # Timer till next remote item textbox

            flag_bytes = bytearray(save_struct[0x00:0xB8])
            locs_to_send = set()

            # Check for set location flags.
            found_a_hidden_path = False
            for byte_i, byte in enumerate(flag_bytes):
                for i in range(8):
                    and_value = 0x80 >> i
                    if byte & and_value != 0:
                        flag_id = byte_i * 8 + i

                        if flag_id == 0x18D:  # The "found a hidden path" cutscene flag
                            found_a_hidden_path = True

                        location_id = flag_id + base_id
                        if location_id in ctx.server_locations:
                            locs_to_send.add(location_id)

            # Send locations if there are any to send.
            if locs_to_send != self.local_checked_locations:
                self.local_checked_locations = locs_to_send

                if locs_to_send is not None:
                    await ctx.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": list(locs_to_send)
                    }])

            # Send game clear if we're in either any ending cutscene or the credits state.
            if not ctx.finished_game and (found_a_hidden_path or game_state == 0xA):
                await ctx.send_msgs([{
                    "cmd": "StatusUpdate",
                    "status": ClientStatus.CLIENT_GOAL
                }])

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass
