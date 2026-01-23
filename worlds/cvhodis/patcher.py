import struct

from typing import Collection, TypedDict, NotRequired
from .data.enums import Areas, Enemies, PickupTypes, ActorTypes, SpecialObjects

GBA_ROM_START = 0x8000000
GBA_EWRAM_START = 0x2000000
IPS_EOF = 0x454F46

AREA_PTRS_PTR_START = 0x1EC8

ACTOR_ENTRY_LENGTH = 0xC
LOADING_ZONE_ENTRY_LENGTH = 0xC

class CVHoDisRoomDataEntry(TypedDict):
    """Base class that all CVHoDis room data entries inherit from."""

    start_addr: NotRequired[int]  # Where in the ROM the data entry starts, if it's vanilla.
    delete: NotRequired[bool]  # Whether the entry should be deleted when it comes time to reinsert the list.


class CVHoDisActorEntry(CVHoDisRoomDataEntry):
    """An entry from any regular actor list in any room in the game."""

    x_pos: int  # How far right horizontally from the left edge of the map the actor is located. Int16.
    y_pos: int  # How far down vertically from the top edge of the map the actor is located. Int16.
    type_id: int  # ID for which "category" of actor the actor belongs to. Upper 2 bits in the object ID byte.
    unique_id: int  # Unique number assigned to this specific actor instance. Lower 6 bits in the object ID byte.
    subtype_id: int  # Sub-ID for which actor in the main actor "category" it is. Int8.
    y_offset: int  # If it's a candle actor, determines how high to offset it. Unknown purpose for other actors. Int8.
    byte_8: int  # Unknown purpose.
    var_a: int  # Extra int16 parameters that apply to the actor (exactly what these mean vary per actor).
    var_b: int


class CVHoDisLoadingZoneEntry(CVHoDisRoomDataEntry):
    """An entry from the room's list of loading zone datas."""

    dest_room_ptr: int  # Pointer to the destination room's default state information.
    x_coord: int  # Which map square column from the left of the room the zone covers. Int8 signed.
    y_coord: int  # Which map square row from the top of the room the zone covers. Int8 signed.
    player_x_offset: int  # How much the transition should offset the player's screen X position. Int8 signed.
    player_y_offset: int  # How much the transition should offset the player's screen Y position. Int8 signed.
    camera_x_pos: int  # What X position in the destination room the camera should be placed starting at. Int16.
    camera_y_pos: int  # What Y position in the destination room the camera should be placed starting at. Int16.


class CVHoDisRoomState(CVHoDisRoomDataEntry):
    display_flags: int  # 16 bitflags that tell the game what to display in the room. Player, health bar, etc.
    alt_state_flag_id: int  # Int16 event flag ID that will set the room to an alternate state if said flag is set
                            # instead of this one. Will be 0xFFFF if there's no alternate state.
    alt_state_ptr: int  # Ptr to the alternate state if the above alternate state flag is set. 0x00000000 if N/A.
    layer_info_ptr: int  # Ptr to the state's layer info.
    gfx_info_ptr: int  # Ptr to the state's GFX info.
    unknown_ptr: int
    palette_info_ptr: int  # Ptr to the state's palette info.
    actor_list: list[CVHoDisActorEntry]  # Actors in the room state.
    loading_zone_list: list[CVHoDisLoadingZoneEntry]  # Loading zones in the room state.
    background_effect_id: int  # Int8 ID for what background effect to display.
    palette_shift_id: int  # Int8 ID for what palette shift effect to apply to the background with some bg effects.
    area_info: int  # Information associated to what Area the room state is associated with. Used to know what song to
                    # play and what area name to display if it's an area the player hasn't been to yet.

class CVHoDisRomPatcher:
    rom: bytearray
    areas: list[list[list[CVHoDisRoomState]]]  # Room State lists within Room lists within Area lists.
    area_ptrs_start: int
    actor_lists: dict[int, list[CVHoDisActorEntry]]
    loading_zone_lists: dict[int, list[CVHoDisLoadingZoneEntry]]
    current_write_file_addr: int

    def __init__(self, input_rom: bytearray) -> None:
        self.rom = input_rom

        # Grab a hardcoded pointer to the start of the Area room pointer lists.
        self.area_ptrs_start = self.read_bytes(AREA_PTRS_PTR_START, 4, "<I") & ~GBA_ROM_START

        # Figure out where the first scene overlay begins and the last scene overlay ends. This will be the first
        # free-range that we write files into.
        # self.current_write_file_addr = self.read_bytes(SCENE_OVERLAY_ROM_ADDRS_START, 4, return_as_int=True)

        # Read out the important common area data structs into a format that is easy to edit and then reinsert
        # (actor lists, loading zones, etc.).
        self.areas = []
        self.actor_lists = {}
        self.loading_zone_lists = {}
        for area_id in range(len(Areas)):
            self.areas.append([])

            # Grab the pointer to the start of the current Area's list of default room state pointers and use that to
            # grab the Area's first room's default state pointer.
            area_room_ptr_list_start = self.read_bytes(self.area_ptrs_start + (area_id * 4), 4, "<I") & ~GBA_ROM_START
            default_room_state_ptr = self.read_bytes(area_room_ptr_list_start, 4, "<I") & ~GBA_ROM_START

            # Continue iterating over every default room pointer associated with the Area until we find a 00000000
            # pointer, signifying the end of the list.
            room_id = 0
            while default_room_state_ptr:
                # Extract all states associated with the room, beginning with the default one.
                self.areas[area_id].append([])
                state_ptr = default_room_state_ptr
                while state_ptr:
                    # Grab the pointer to the state's actor list from its info.
                    actor_list_ptr = self.read_bytes(state_ptr + 0x18, 4, "<I")

                    # If the actor list pointer is 00000000'd out, this means we have no actor list associated with the
                    # room state. In which case, use a blank list.
                    if not actor_list_ptr:
                        actor_list = []

                    # If not 00000000, check if the actor list pointed to by the room state is one we extracted already.
                    # If not, extract it.
                    elif actor_list_ptr not in self.actor_lists:
                        # Loop over each actor list entry and read it out. Continue looping until we reach the end of
                        # the list.
                        actor_list = []
                        curr_addr = actor_list_ptr & ~GBA_ROM_START
                        while True:
                            actor = CVHoDisActorEntry(
                                x_pos=self.read_bytes(curr_addr, 2, "<h"),
                                y_pos=self.read_bytes(curr_addr + 0x2, 2, "<h"),
                                # The Type ID (upper 2 bits) needs to be split out of the Unique ID (lower 6 bits).
                                type_id=self.read_byte(curr_addr + 0x4) >> 6,
                                unique_id=self.read_byte(curr_addr + 0x4) & 0x3F,
                                subtype_id=self.read_byte(curr_addr + 0x5),
                                y_offset=self.read_byte(curr_addr + 0x6),
                                byte_8=self.read_byte(curr_addr + 0x7),
                                var_a=self.read_bytes(curr_addr + 0x8, 2, "<h"),
                                var_b=self.read_bytes(curr_addr + 0xA, 2, "<h"),
                                start_addr=curr_addr | GBA_ROM_START,
                            )
                            # Check if the actor has a documented entry in the actor types enum.
                            if actor["type_id"] in ActorTypes:
                                actor["type_id"] = ActorTypes(actor["type_id"])

                            # Check if the actor is an item pickup or candle actor and, if it is, does the pickup/candle
                            # drop have an entry in the pickup types enum.
                            if actor["type_id"] in [ActorTypes.PICKUP, ActorTypes.CANDLE]:
                                actor["subtype_id"] = PickupTypes(actor["subtype_id"])
                            # If it's an enemy, check if it has an entry in the enemies enum.
                            elif actor["type_id"] == ActorTypes.ENEMY:
                                actor["subtype_id"] = Enemies(actor["subtype_id"])
                            # Otherwise, if it's a special object, check if it has an entry in the special objects enum.
                            else:
                                actor["subtype_id"] = SpecialObjects(actor["subtype_id"])

                            # If the actor we extracted has an X AND Y position of 0x7FFF, then we have reached the
                            # actor entry signifying the end of the list. In which case, break out of the loop
                            # (don't append the end-of-list entry).
                            if actor["x_pos"] == 0x7FFF == actor["y_pos"]:
                                break

                            # Append the actor to the end of the list.
                            actor_list.append(actor)

                            # Increment the current actor start address so we will be at the start of the next one on
                            # the next loop.
                            curr_addr += ACTOR_ENTRY_LENGTH

                        # Save the complete actor list we just extracted mapped to the list's start address.
                        self.actor_lists[actor_list_ptr] = actor_list

                    # If it WAS extracted already, however, use that already-extracted list.
                    else:
                        actor_list = self.actor_lists[actor_list_ptr]

                    # Grab the pointer to the state's loading zone list from its info.
                    loading_zone_list_ptr = self.read_bytes(state_ptr + 0x1C, 4, "<I")

                    # If the loading zone list pointer is 00000000'd out, this means we have no loading zone list
                    # associated with the room state. In which case, use a blank list.
                    if not loading_zone_list_ptr:
                        loading_zone_list = []

                    # If not 00000000, check if the loading zone list pointed to by the room state is one we extracted
                    # already. If not, extract it.
                    elif loading_zone_list_ptr not in self.loading_zone_lists:
                        # Loop over each loading zone list entry and read it out. Continue looping until we reach the
                        # end of the list.
                        loading_zone_list = []
                        curr_addr = loading_zone_list_ptr & ~GBA_ROM_START
                        while True:
                            loading_zone = CVHoDisLoadingZoneEntry(
                                dest_room_ptr=self.read_bytes(curr_addr, 4, "<I"),
                                x_coord=self.read_bytes(curr_addr + 0x4, 1, "b"),
                                y_coord=self.read_bytes(curr_addr + 0x5, 1, "b"),
                                player_x_offset=self.read_bytes(curr_addr + 0x6, 1, "b"),
                                player_y_offset=self.read_bytes(curr_addr + 0x7, 1, "b"),
                                camera_x_pos=self.read_bytes(curr_addr + 0x8, 2, "<h"),
                                camera_y_pos=self.read_bytes(curr_addr + 0xA, 2, "<h"),
                                start_addr=curr_addr | GBA_ROM_START,
                            )

                            # If the loading zone we extracted has a destination room pointer that is not a valid
                            # ROM pointer, then we have reached the end of the list. In  which case, break out of the
                            # loop (don't append what we just extracted).
                            if not GBA_ROM_START + 0x1FFFFFF >= loading_zone["dest_room_ptr"] >= GBA_ROM_START:
                                break

                            # Append the loading zone to the end of the list.
                            loading_zone_list.append(loading_zone)

                            # Increment the current loading zone start address so we will be at the start of the next
                            # one on the next loop.
                            curr_addr += LOADING_ZONE_ENTRY_LENGTH

                        # Save the complete loading zone list we just extracted mapped to the list's start address.
                        self.loading_zone_lists[loading_zone_list_ptr] = loading_zone_list

                    # If it WAS extracted already, however, use that already-extracted list.
                    else:
                        loading_zone_list = self.loading_zone_lists[loading_zone_list_ptr]

                    # Extract the rest of the room state info associated with the room state pointer we are currently
                    # looking at.
                    room_state = CVHoDisRoomState(
                                display_flags=self.read_bytes(state_ptr, 2, "<H"),
                                alt_state_flag_id=self.read_bytes(state_ptr + 0x2, 2, "<H"),
                                alt_state_ptr=self.read_bytes(state_ptr + 0x4, 4, "<I"),
                                layer_info_ptr=self.read_bytes(state_ptr + 0x8, 4, "<I"),
                                gfx_info_ptr=self.read_bytes(state_ptr + 0xC, 4, "<I"),
                                unknown_ptr=self.read_bytes(state_ptr + 0x10, 4, "<I"),
                                palette_info_ptr=self.read_bytes(state_ptr + 0x14, 4, "<I"),
                                actor_list=actor_list,
                                loading_zone_list=loading_zone_list,
                                background_effect_id=self.read_byte(state_ptr + 0x20),
                                palette_shift_id=self.read_byte(state_ptr + 0x21),
                                area_info=self.read_bytes(state_ptr + 0x22, 2, "<H"),
                                start_addr=state_ptr | GBA_ROM_START,
                            )

                    # Append the room state info we just extracted to the current room's list of room states.
                    self.areas[area_id][room_id].append(room_state)

                    # Set the pointer to the current room state we're looking at to that of our current room state's
                    # alternate room state. If there's no pointer to an alternate room state in the state we just
                    # extracted, then we have reached the "deepest" room state in the chain. In which case, the loop
                    # for this room will terminate, and we will move onto the next.
                    state_ptr = room_state["alt_state_ptr"] & ~GBA_ROM_START

                # Increment the room ID by 1 and grab the pointer to the next room's default state. If we grab a
                # 00000000 pointer, then we've reached the end of the area's room list and the loop for the current area
                # will end.
                room_id += 1
                default_room_state_ptr = \
                    self.read_bytes(area_room_ptr_list_start + (room_id * 4), 4, "<I") & ~GBA_ROM_START

    def read_byte(self, address: int) -> int:
        """Return a byte at a specified address."""
        return self.rom[address]

    def read_bytes(self, start_address: int, length: int, struct_format: str = "") -> bytearray | int:
        """Return a string of bytes of a specified length beginning at a specified address in a specified format.
        If no format was specified, it will be returned as bytes."""
        if struct_format:
            return struct.unpack(struct_format, self.rom[start_address:start_address + length])[0]
        return self.rom[start_address:start_address + length]

    def write_byte(self, address: int, value: int) -> None:
        """Write a given byte at a specified address."""
        self.rom[address] = value & 0xFF

    def write_bytes(self, start_address: int, values: Collection[int]) -> None:
        """Write a given string of bytes beginning at a specified address."""
        self.rom[start_address:start_address + len(values)] = values

    def write_int16(self, address: int, value: int) -> None:
        """Write a given int16 at a specified address. Value will be written in little endian."""
        value = value & 0xFFFF
        self.write_bytes(address, [value & 0xFF, (value >> 8) & 0xFF])

    def write_int16s(self, start_address: int, values: list[int]) -> None:
        """Write a given string of int16s beginning at a specified address. Values will be written in little endian."""
        for i, value in enumerate(values):
            self.write_int16(start_address + (i * 2), value)

    def write_int24(self, address: int, value: int) -> None:
        """Write a given int24 at a specified address. Value will be written in little endian."""
        value = value & 0xFFFFFF
        self.write_bytes(address, [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF])

    def write_int24s(self, start_address: int, values: list[int]) -> None:
        """Write a given string of int24s beginning at a specified address. Values will be written in little endian."""
        for i, value in enumerate(values):
            self.write_int24(start_address + (i * 3), value)

    def write_int32(self, address: int, value: int) -> None:
        """Write a given int32 at a specified address. Value will be written in little endian."""
        value = value & 0xFFFFFFFF
        self.write_bytes(address, [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF])

    def write_int32s(self, start_address: int, values: list[int]) -> None:
        """Write a given string of int32s beginning at a specified address. Values will be written in little endian."""
        for i, value in enumerate(values):
            self.write_int32(start_address + (i * 4), value)

    def apply_ips(self, ips_file: bytes) -> None:
        """Apply a supplied IPS Patch to the ROM data."""

        file_pos = 5
        while True:
            # Get the ROM offset bytes of the current record.
            rom_offset = int.from_bytes(ips_file[file_pos:file_pos + 3], "big")

            # If we've hit the "EOF" codeword (aka 0x454F46), stop iterating because we've reached the end of the patch.
            if rom_offset == IPS_EOF:
                return

            # Get the size bytes of the current record.
            bytes_size = int.from_bytes(ips_file[file_pos + 3:file_pos + 5], "big")

            if bytes_size != 0:
                # Write the bytes to the ROM.
                self.write_bytes(rom_offset, ips_file[file_pos + 5:file_pos + 5 + bytes_size])

                # Increase our position in the IPS patch to the start of the next record.
                file_pos += 5 + bytes_size
            else:
                # If the size is 0, we are looking at an RLE record.
                # Get the size of the RLE.
                rle_size = int.from_bytes(ips_file[file_pos + 5:file_pos + 7], "big")

                # Get the byte to be written over and over.
                rle_byte = int.from_bytes(ips_file[file_pos + 7:file_pos + 8], "big")

                # Write the RLE byte to the ROM the RLE size times over.
                self.write_bytes(rom_offset, [rle_byte for _ in range(rle_size)])

                # Increase our position in the IPS patch to the start of the next record.
                file_pos += 8

    def find_space_and_write_file(self, file: bytearray) -> int:
        """Finds a space in the ROM to write a given file and writes it, returning the start address the file was written to.
        Files will be written one after the other every time this method is called, from where the map overlays normally are first,
        and then starting from where the compressed Nistienma-Ichigo files are."""

        # If the current write address is before the Nisitenma-Ichigo files start, and either trying to write the
        # current file would have said file overflow past where the map overlay files normally end or the current write
        # address is exactly the end of the scene overlays, start writing files in the NI file range instead.
        if self.current_write_file_addr < self.ni_file_buffers_start and \
                (self.current_write_file_addr + len(file) > self.scene_overlays_end or
                 self.current_write_file_addr == self.scene_overlays_end):
            self.current_write_file_addr = self.ni_file_buffers_start

        # Write the file and update the current write address to be where the file ends.
        write_spot = self.current_write_file_addr
        self.write_bytes(self.current_write_file_addr, file)
        self.current_write_file_addr += len(file)

        # Return the start address of the spot we just wrote the file to.
        return write_spot

    def get_output_rom(self) -> bytes:
        # Rebuild and reinsert all modified scene data.
        for scene_id in range(len(self.scenes)):
            # If we're looking at an empty scene with no overlay, skip it entirely.
            if not self.scenes[scene_id].overlay:
                continue


            # # # ACTOR LISTS # # #
            # Create the final actor lists with all entries primed for deletion removed.
            new_actor_lists = {list_name: [actor_entry for actor_entry in actor_list
                                           if "delete" not in actor_entry]
                               for list_name, actor_list in self.scenes[scene_id].actor_lists.items()}

            # Loop over each actor list, convert each one to binary data, and insert them back in the map overlay.
            for list_name, actor_list in new_actor_lists.items():
                # If it's a pillar actor list, get the actor list data in pillar list format.
                list_data = bytearray(0)
                if list_name == "pillars":
                    for entry in actor_list:
                        list_data += struct.pack(">h", entry["x_pos"]) + \
                                     struct.pack(">h", entry["y_pos"]) + \
                                     struct.pack(">h", entry["z_pos"]) + \
                                     int.to_bytes(entry["object_id"] | (entry["execution_flags"] << 0xB), 2, "big") + \
                                     struct.pack(">H", entry["var_c"]) + \
                                     struct.pack(">H", entry["var_a"]) + \
                                     struct.pack(">H", entry["var_b"]) + \
                                     struct.pack(">H", entry["var_d"]) + b'\x00\x00\x00\x00' + \
                                     int.to_bytes(entry["flag_id"], 4, "big")
                # Otherwise, get it in the normal actor list format.
                else:
                    for entry in actor_list:
                        list_data += int.to_bytes(entry["spawn_flags"], 2, "big") +\
                                     int.to_bytes(entry["status_flags"], 2, "big") +\
                                     struct.pack(">f", entry["x_pos"]) + \
                                     struct.pack(">f", entry["y_pos"]) + \
                                     struct.pack(">f", entry["z_pos"]) + \
                                     int.to_bytes(entry["object_id"] | (entry["execution_flags"] << 0xB), 2, "big") + \
                                     int.to_bytes(entry["flag_id"], 2, "big") + \
                                     struct.pack(">H", entry["var_a"]) + \
                                     struct.pack(">H", entry["var_b"]) + \
                                     struct.pack(">H", entry["var_c"]) + \
                                     struct.pack(">H", entry["var_d"]) + \
                                     int.to_bytes(entry["extra_condition_ptr"], 4, "big")

                    # Append the list end entry for all normal actor lists.
                    list_data += b'\xFF\x7F\xFF\x7F\x00\x00\x00\x00\x00\x00\x00\x00'

                # Get the size of the original actor list by counting the number of entries in the list without entries
                # deleted that have a defined start address. If the new actor data is the same size or smaller
                # than it was before, write it back where it was originally (if we even have a list to begin with).
                if len(actor_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].actor_lists[list_name]
                                           if "start_addr" in orig_entry]):
                    if actor_list:
                        self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].actor_lists[
                                                                  list_name][0]["start_addr"], list_data)
                # If it's larger, however, put it on the end of the overlay and update the pointer(s) to it.
                else:
                    new_actor_list_addr = len(self.scenes[scene_id].overlay)
                    self.scenes[scene_id].overlay += list_data

                    # If it's an init list, the pointer to update is the third pointer in the scene's entry in the
                    # game's table of loaded scene actor list starts and determine how far in it is relative to the
                    # start of the overlay in RDRAM.
                    if list_name == "init":
                        self.write_int32(8 + (scene_id * 0x10), new_actor_list_addr)
                    # If it's a proxy list, the pointer to update is the second pointer in the above-mentioned table.
                    elif list_name == "proxy":
                        self.write_int32(4 + (scene_id * 0x10), new_actor_list_addr)
                    # If it's a room list, take the fourth pointer in the table to arrive at the scene's list of room
                    # actor list pointers, and then offset into it by the room number.
                    elif "room" in list_name:
                        room_list_ptrs_start = self.read_bytes( 12 + (scene_id * 0x10), 4,
                                                               return_as_int=True)

                        self.scenes[scene_id].write_ovl_int32(room_list_ptrs_start + (int(list_name[5:]) * 4),
                                                              new_actor_list_addr)
                    # Otherwise, if it's a 3HB pillar list, loop through every pillar data and update its actor pointer
                    # there.
                    else:
                        old_actor_list_addr = self.scenes[scene_id].actor_lists["pillars"][0]["start_addr"]
                        for pillar_data in self.scenes[scene_id].enemy_pillars:
                            pillar_data["actor_list_start"] = new_actor_list_addr + (pillar_data["actor_list_start"] -
                                                                                     old_actor_list_addr)


            # # # LOADING ZONES LIST # # #
            # Create the final loading zones list with all entries primed for deletion removed.
            new_loading_zone_list = [loading_zone_entry for loading_zone_entry in self.scenes[scene_id].loading_zones
                                     if "delete" not in loading_zone_entry]

            # Loop over each loading zone, convert each one to binary data, and insert them back in the map overlay.
            loading_zone_data = bytearray(0)
            for loading_zone in new_loading_zone_list:
                loading_zone_data += (int.to_bytes(loading_zone["heal_player"], 2, "big") +
                                      int.to_bytes(loading_zone["scene_id"], 1, "big") +
                                      int.to_bytes(loading_zone["spawn_id"], 1, "big") +
                                      int.to_bytes(loading_zone["fade_settings_id"], 1, "big") + b'\x00' +
                                      int.to_bytes(loading_zone["cutscene_settings_id"], 2, "big") +
                                      struct.pack(">h", loading_zone["min_x_pos"]) +
                                      struct.pack(">h", loading_zone["min_y_pos"]) +
                                      struct.pack(">h", loading_zone["min_z_pos"]) +
                                      struct.pack(">h", loading_zone["max_x_pos"]) +
                                      struct.pack(">h", loading_zone["max_y_pos"]) +
                                      struct.pack(">h", loading_zone["max_z_pos"]))

            # If the new loading zone data is the same size or smaller than it was before, write it back where it was
            # originally (if we even have a list to begin with).
            if len(new_loading_zone_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].loading_zones
                                                  if "start_addr" in orig_entry]):
                if new_loading_zone_list:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].loading_zones[0]["start_addr"], loading_zone_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_loading_zone_list_ptr = len(self.scenes[scene_id].overlay)
                self.scenes[scene_id].overlay += loading_zone_data
                self.write_int32((scene_id * 4), new_loading_zone_list_ptr)

            # Write the final scene overlay back into the ROM.
            new_overlay_start = self.find_space_and_write_file(self.scenes[scene_id].overlay)
            # Update the pointers to the start and end of the overlay in both the ROM and RDRAM scene overlay pointers
            # table.
            self.write_int32((scene_id * 8), new_overlay_start)
            self.write_int32(((scene_id * 8)) + 4,
                             new_overlay_start + len(self.scenes[scene_id].overlay))
            self.write_int32((scene_id * 8) + 4,
                             len(self.scenes[scene_id].overlay))


        # Reinsert all Nisitenma-Ichigo files, both modified and unmodified, in the order they should be.
        for i in range(1, self.number_of_ni_files):
            # Re-compress the file if decompressed and update the game's decompressed sizes table.
            if i in self.decompressed_files:
                self.compress_file(i)
                self.write_int24(self.decomp_file_sizes_table_start + (i * 8) + 5, len(self.decompressed_files[i]))

            new_overlay_start = self.find_space_and_write_file(self.compressed_files[i])

            # Update the Nisitenma-Ichigo table with the NI file's start and end addresses.
            self.write_int24(self.ni_table_start + ((i - 1) * 8) + 1, new_overlay_start)
            self.write_int24(self.ni_table_start + ((i - 1) * 8) + 5, new_overlay_start + len(self.compressed_files[i]))

        # Return the final output ROM.
        return bytes(self.rom)
