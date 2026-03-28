import struct

from typing import Collection, TypedDict, NotRequired
from .data.enums import Areas, Enemies, PickupTypes, ActorTypes, SpecialObjects

GBA_ROM_START = 0x8000000
GBA_EWRAM_START = 0x2000000
IPS_EOF = 0x454F46

AREA_PTRS_PTR_START = 0x1EC8

ACTOR_ENTRY_LENGTH = 0xC
LOADING_ZONE_ENTRY_LENGTH = 0xC

ROM_PADDING_START = 0x69D400
ROM_PADDING_WORD = bytearray(b'\xFF\xFF\xFF\xFF')

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
    actor_list_ptr: int  # Ptr to the state's actor list.
    actor_list: list[CVHoDisActorEntry]  # Actors in the room state.
    loading_zone_list_ptr: int  # Ptr to the state's loading zone list.
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
    free_space_lookup: dict[int, int]

    def __init__(self, input_rom: bytearray) -> None:
        self.rom = input_rom

        # Determine the initial available free space in the ROM past where the padding segment begins.
        self.free_space_lookup = {ROM_PADDING_START: len(self.rom[ROM_PADDING_START:])}
        current_free_space_start = ROM_PADDING_START
        # Scan the free space segment for any extra data that may have been added (i.e. by the Advance Collection).
        extra_data_start = 0
        padding_after_extra_data = 0
        for i in range(ROM_PADDING_START, len(self.rom), 4):
            # If we find a non-padding word, reset the padding after extra data to 0.
            if self.rom[i:i+4] != ROM_PADDING_WORD:
                padding_after_extra_data = 0
                # If we had no extra data start address recorded, then we found the start of an extra data segment.
                # In which case, record it and update the most recent free space range to end here.
                if not extra_data_start:
                    extra_data_start = i
                    self.free_space_lookup[current_free_space_start] = len(self.rom[current_free_space_start:i])
            # If we found a padding word, and we currently have an extra data address recorded, increment the padding
            # after extra data counter by 1.
            elif self.rom[i:i+4] == ROM_PADDING_WORD and extra_data_start:
                padding_after_extra_data += 1
                # If we go over 8 padding words, consider this the end of the extra data segment. Clear the current
                # extra data address and record a new free space range starting here and tentatively going to the end.
                if padding_after_extra_data > 8:
                    current_free_space_start = i
                    self.free_space_lookup[current_free_space_start] = len(self.rom[current_free_space_start:])
                    extra_data_start = 0

        # Grab a hardcoded pointer to the start of the Area room pointer lists.
        self.area_ptrs_start = self.read_bytes(AREA_PTRS_PTR_START, 4, "<I") & ~GBA_ROM_START

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
                            # ROM pointer, then we have reached the end of the list. In which case, break out of the
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
                                actor_list_ptr=actor_list_ptr,
                                actor_list=actor_list,
                                loading_zone_list_ptr=loading_zone_list_ptr,
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

    def write_byte(self, address: int, value: int, update_free_space: bool = True) -> None:
        """Write a given byte at a specified address."""
        self.rom[address] = value & 0xFF

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(address, 1)

    def write_bytes(self, start_address: int, values: Collection[int], update_free_space: bool = True) -> None:
        """Write a given string of bytes beginning at a specified address."""
        self.rom[start_address:start_address + len(values)] = values

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(start_address, len(values))

    def write_int16(self, address: int, value: int, update_free_space: bool = True) -> None:
        """Write a given int16 at a specified address. Value will be written in little endian."""
        value = value & 0xFFFF
        self.write_bytes(address, [value & 0xFF, (value >> 8) & 0xFF], update_free_space=False)

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(address, 2)

    def write_int16s(self, start_address: int, values: list[int], update_free_space: bool = True) -> None:
        """Write a given string of int16s beginning at a specified address. Values will be written in little endian."""
        for i, value in enumerate(values):
            self.write_int16(start_address + (i * 2), value, update_free_space=False)

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(start_address, len(values))

    def write_int24(self, address: int, value: int, update_free_space: bool = True) -> None:
        """Write a given int24 at a specified address. Value will be written in little endian."""
        value = value & 0xFFFFFF
        self.write_bytes(address, [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF], update_free_space=False)

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(address, 3)

    def write_int24s(self, start_address: int, values: list[int], update_free_space: bool = True) -> None:
        """Write a given string of int24s beginning at a specified address. Values will be written in little endian."""
        for i, value in enumerate(values):
            self.write_int24(start_address + (i * 3), value, update_free_space=False)

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(start_address, len(values))

    def write_int32(self, address: int, value: int, update_free_space: bool = True) -> None:
        """Write a given int32 at a specified address. Value will be written in little endian."""
        value = value & 0xFFFFFFFF
        self.write_bytes(address, [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF],
                         update_free_space=False)

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(address, 4)

    def write_int32s(self, start_address: int, values: list[int], update_free_space: bool = True) -> None:
        """Write a given string of int32s beginning at a specified address. Values will be written in little endian."""
        for i, value in enumerate(values):
            self.write_int32(start_address + (i * 4), value, update_free_space=False)

        # Update the free space lookup if we are opting to.
        if update_free_space:
            self.remove_free_space(start_address, len(values))

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

    def generate_dynamic_asm(self, asm_instructions: list[int], ldr_nums: list[int], hook_addr: int = 0,
                             hook_register: int = 0) -> int:
        """Assembles a complete assembly blob given a list of byte instructions and their associated ldr numbers, finds
        an empty spot at the end of the ROM where they fit, writes them in, as well as hooking a specified spot in the
        game's regular assembly to jump to it. Returns the found start address where the custom assembly begins."""
        if ldr_nums is None:
            ldr_nums = []

        # If the list of instructions is an odd length, append an extra 0x0000 to keep the assembly blob 4-aligned.
        if len(asm_instructions) % 2:
            asm_instructions.append(0x0000)

        # Assemble the full assembly blob bytearray.
        assembly = bytearray(0)
        for i in range(len(asm_instructions)):
            # Check to see if the instruction is a "load immediate" instruction (highest nybble has ONLY bit 0100 set,
            # and second-highest nybble has bit 1000 set with no regard to the other 3 bits).
            if asm_instructions[i] & 0xF000 == 0x4000 and asm_instructions[i] & 0x0800:
                # If that is the case, refer to the lower byte to determine which index in the input ldr_num list we
                # are actually trying to link to, and add that to the number of words separating this instruction from
                # the end of the list to get what number the byte should REALLY be.
                assembly += struct.pack("<H", asm_instructions[i] & 0xFF00 | \
                                        ((asm_instructions[i] & 0xFF) + ((len(asm_instructions) - (i + 1)) // 2)))
            else:
                # Otherwise, append the instruction as-is.
                assembly += struct.pack("<H", asm_instructions[i])

        # Build the ldr number pool and append it to the end of the assembly blob.
        for ldr_num in ldr_nums:
            assembly += struct.pack("<I", ldr_num)

        # Write the assembly in a free space and save the address we wrote it to.
        asm_addr = self.find_space_and_write_buffer(assembly)

        # If we are not generating a hook (see: hook address is 0), return now.
        if not hook_addr:
            return asm_addr

        # Otherwise, start generating the hook code here.
        # Assert that the hook address is 2-aligned. If not, raise an exception.
        if hook_addr % 2:
            raise Exception(f"Hook address {hook_addr} needs to be 2-aligned, ideally 4-aligned. Try again!")

        # Generate the ldr instruction. The upper byte should be 0x48 + whichever register number we're using.
        hook_ldr = (0x48 + hook_register) << 8
        # Generate the mov instruction. Upper byte should be 0x46, lower should be 0x87 (bits 1-3 set to indicate
        # loading into r15) + bits 4-7 being the register number we're moving from (shift it up by 3 to get this).
        mov_ldr = 0x4687 | (hook_register << 3)

        # Generate and write the final hook code blob. If our hook address isn't 4-aligned, add +1 to the ldr
        # lower byte and insert an extra 0000 between the instructions and the custom assembly address.
        if hook_addr % 4:
            self.write_bytes(hook_addr, bytearray(struct.pack("<H", hook_ldr + 1)) + struct.pack("<H", mov_ldr) +
                             b"\x00\x00" + struct.pack("<I", GBA_ROM_START | asm_addr))
        # Otherwise, there'll be nothing separating the instructions and the address.
        else:
            self.write_bytes(hook_addr, bytearray(struct.pack("<H", hook_ldr)) + struct.pack("<H", mov_ldr) +
                             struct.pack("<I", GBA_ROM_START | asm_addr))

        # Return now with the custom assembly address.
        return asm_addr

    def remove_free_space(self, remove_start: int, remove_len: int) -> None:
        """Alters the free space lookup to no longer consider a given space range free."""
        new_free_space_lookup = {}

        # Pad the start address and length to both be 4-aligned.
        padded_remove_start = remove_start - remove_start % 4
        padded_remove_len = remove_len + (remove_start - padded_remove_start)
        if padded_remove_len % 4:
            padded_remove_len += 4 - padded_remove_len % 4

        # Loop over every free space range in the lookup and construct a new lookup with any overlaps with the removal
        # range modified/removed.
        remove_end = padded_remove_start + padded_remove_len
        for free_space_start, free_space_size in self.free_space_lookup.items():
            free_space_end = free_space_start + free_space_size
            # Horseman #1: Is the free space completely encompassed inside the removal range (free space start is higher
            # than the removal start and free space end is lower than the removal end)? If so, delete the free space
            # completely (continue without adding it to the new lookup).
            if free_space_start >= padded_remove_start and free_space_end <= remove_end:
                continue
            # Horseman #2: Is the removal space completely encompassed inside the free space (remove start is higher
            # than the free space start and remove end is lower than the free space end)? If so, split the free space
            # into two separate free spaces, with the first ending where the removal begins and the second beginning
            # where the removal ends.
            elif padded_remove_start > free_space_start and remove_end < free_space_end:
                new_free_space_lookup[free_space_start] = padded_remove_start - free_space_start
                new_free_space_lookup[remove_end] = \
                    free_space_size - (padded_remove_start - free_space_start) - padded_remove_len
            # Horseman #3: Is the end of the removal space within the free space but the start of the removal space is
            # not? If so, shrink the length of the free space and have it begin at the end of the removal space.
            elif padded_remove_start <= free_space_start < remove_end < free_space_end:
                new_free_space_lookup[remove_end] = \
                    free_space_size - (padded_remove_len - (free_space_start - padded_remove_start))
            # Horseman #4: Is the start of the removal space within the free space but the end of the removal space is
            # not? If so, shrink the length of the free space to make it end where the removal space begins.
            elif free_space_start < padded_remove_start < free_space_end <= remove_end:
                new_free_space_lookup[free_space_start] = padded_remove_start - free_space_start
            # Otherwise, copy the free space over exactly.
            else:
                new_free_space_lookup[free_space_start] = free_space_size

        # Overwrite the old lookup with the newly-created one.
        self.free_space_lookup = new_free_space_lookup

    def find_space_and_write_buffer(self, values: Collection[int]) -> int:
        """Finds a space in the free space lookup to write a given buffer and writes it in the ROM, returning the start
        address the buffer was written to and updating the lookup in the process."""

        # Pad the buffer size to find to be 4-aligned.
        size_to_find = len(values)
        if size_to_find % 4:
            size_to_find += 4 - size_to_find % 4

        # Copy the lookup so we can check each element individually.
        unchecked_spaces = self.free_space_lookup.copy()
        while unchecked_spaces:
            # Check the spaces in order from closest to the end of the ROM to closest to the padding start. This will
            # make it less likely that we will end up colliding with used data in an applied user patch.
            furthest_space_start = max(unchecked_spaces)

            # If the size of the buffer is less than or equal to the chosen free space size, we have found a valid spot
            # for the buffer.
            if size_to_find <= unchecked_spaces[furthest_space_start]:
                # Write the buffer so that its end ends at where the free space ends, updating the free spaces lookup,
                # and return the start address we wrote to.
                write_spot = furthest_space_start + (unchecked_spaces[furthest_space_start] - size_to_find)
                self.write_bytes(write_spot, values)
                return write_spot

            # Otherwise, if the free space size is too small, remove it from the unchecked spaces lookup and try the
            # next furthest-out space...
            del unchecked_spaces[furthest_space_start]

        # If we make it here, meaning there's no available free space to write the buffer, raise an exception.
        raise Exception("Not enough space in the ROM to write everything. "
                        "If you are using custom patches, you may need to remove some. "
                        "Otherwise, this is a bug that should be reported...")

    def get_output_rom(self) -> bytes:
        """Reinserts all modified extracted data and returns the resulting ROM."""

        # # # ACTOR LISTS # # #
        # Loop over all the actor lists and reinsert them in the ROM.
        expanded_actor_list_ptrs = {}
        for address, actor_list in self.actor_lists.items():
            # Create the final actor list with all entries primed for deletion removed.
            new_actor_list = [actor_entry for actor_entry in actor_list if "delete" not in actor_entry]

            # Get the size of the original actor list by counting the number of entries in the list without entries
            # deleted that have a defined start address. If the new actor data is the same size or smaller
            # than it was before, write it back where it was originally (if we even have a list to begin with).
            if len(new_actor_list) <= len([orig_entry for orig_entry in actor_list if "start_addr" in orig_entry]):
                if new_actor_list:
                    self.write_bytes(~GBA_ROM_START & address, get_actor_list_bytes(new_actor_list))
            # If it's larger, however, find a new free space in the ROM to put it, write it there, and save the new
            # pointer to it.
            else:
                expanded_actor_list_ptrs[address] = \
                    GBA_ROM_START | self.find_space_and_write_buffer(get_actor_list_bytes(new_actor_list))

        # # # LOADING ZONE LISTS # # #
        # Loop over all the loading zone lists and reinsert them in the ROM.
        expanded_loading_zone_list_ptrs = {}
        for address, loading_zone_list in self.loading_zone_lists.items():
            # Create the final loading zone list with all entries primed for deletion removed.
            new_loading_zone_list = [loading_zone_entry for loading_zone_entry in loading_zone_list
                                     if "delete" not in loading_zone_entry]

            # Get the size of the original loading zone list by counting the number of entries in the list without
            # entries deleted that have a defined start address. If the new zone data is the same size or smaller
            # than it was before, write it back where it was originally (if we even have a list to begin with).
            if len(new_loading_zone_list) <= len([orig_entry for orig_entry in loading_zone_list
                                                  if "start_addr" in orig_entry]):
                if new_loading_zone_list:
                    self.write_bytes(~GBA_ROM_START & address, get_loading_zone_list_bytes(new_loading_zone_list))
            # If it's larger, however, find a new free space in the ROM to put it, write it there, and save the new
            # pointer to it.
            else:
                # Add a 0x00000000 word to the end of the list data in case another extractor (like DSVania Editor)
                # needs to extract the loading zone data (we check for not a valid GBA ROM pointer in the next entry's
                # dest room pointer to see if the end of the list has or hasn't been reached).
                expanded_loading_zone_list_ptrs[address] = GBA_ROM_START | self.find_space_and_write_buffer(
                    get_loading_zone_list_bytes(new_loading_zone_list) + bytearray(b"\x00\x00\x00\x00"))

        # # # ROOM STATES # # #
        # Loop over every room state data and update each one and its associated additional data.
        for area_room_list in self.areas:
            for room_state_list in area_room_list:
                for room_state in room_state_list:
                    # If the room state has an actor list assigned to it, write it and/or update the state's pointer
                    # to it.
                    if room_state["actor_list"]:
                        # If the room state has a 00000000 pointer to an actor list, or if it has a valid pointer but
                        # said pointer is not in the mapping of pointers to actor lists, then said list should be
                        # written along with the state's actor list being pointer updated.
                        if not room_state["actor_list_ptr"] or room_state["actor_list_ptr"] not in self.actor_lists:
                            room_state["actor_list_ptr"] = GBA_ROM_START | self.find_space_and_write_buffer(
                                get_actor_list_bytes(room_state["actor_list"]))
                        else:
                            # If the state's actor list doesn't match the one assigned to its actor list pointer in the
                            # actor list pointers mapping, then write the list and update the state's pointer.
                            if room_state["actor_list"] != self.actor_lists[room_state["actor_list_ptr"]]:
                                room_state["actor_list_ptr"] = GBA_ROM_START | self.find_space_and_write_buffer(
                                    get_actor_list_bytes(room_state["actor_list"]))
                            # Otherwise, meaning we modified its vanilla list instead of replacing it outright, check
                            # if the list's size increased and, if it did, update the state's pointer with the new
                            # list's address (that we already wrote earlier.
                            elif room_state["actor_list_ptr"] in expanded_actor_list_ptrs:
                                room_state["actor_list_ptr"] = expanded_actor_list_ptrs[room_state["actor_list_ptr"]]

                    # If the room state has a loading zone list assigned to it, write it and/or update the state's
                    # pointer to it.
                    if room_state["loading_zone_list"]:
                        # If the room state has a 00000000 pointer to a loading zone list, or if it has a valid pointer
                        # but said pointer is not in the mapping of pointers to loading zone lists, then said list
                        # should be written along with the state's loading zone list being pointer updated.
                        if not room_state["loading_zone_list_ptr"] or \
                                room_state["loading_zone_list_ptr"] not in self.loading_zone_lists:
                            room_state["loading_zone_list_ptr"] = GBA_ROM_START | self.find_space_and_write_buffer(
                                get_loading_zone_list_bytes(room_state["loading_zone_list"]) +
                                bytearray(b"\x00\x00\x00\x00"))
                        else:
                            # If the state's loading zone list doesn't match the one assigned to its loading zone list
                            # pointer in the loading zone list pointers mapping, then write the list and update the
                            # state's pointer.
                            if room_state["loading_zone_list"] != \
                                    self.loading_zone_lists[room_state["loading_zone_list_ptr"]]:
                                room_state["loading_zone_list_ptr"] = GBA_ROM_START | self.find_space_and_write_buffer(
                                    get_loading_zone_list_bytes(room_state["loading_zone_list"]) +
                                    bytearray(b"\x00\x00\x00\x00"))
                            # Otherwise, meaning we modified its vanilla list instead of replacing it outright, check
                            # if the list's size increased and, if it did, update the state's pointer with the new
                            # list's address (that we already wrote earlier.
                            elif room_state["loading_zone_list_ptr"] in expanded_loading_zone_list_ptrs:
                                room_state["loading_zone_list_ptr"] = \
                                    expanded_loading_zone_list_ptrs[room_state["loading_zone_list_ptr"]]
                    # Otherwise, meaning the loading zone list is empty, zero out the pointer to it.
                    else:
                        room_state["loading_zone_list_ptr"] = 0

                    # Write the final room state data.
                    self.write_bytes(~GBA_ROM_START & room_state["start_addr"], get_room_state_bytes(room_state))

        # Return the final output ROM.
        return bytes(self.rom)

def get_actor_list_bytes(actor_list: list[CVHoDisActorEntry]) -> bytearray:
    """Converts a given actor list into data to be inserted into the ROM."""
    list_data = bytearray(0)
    for entry in actor_list:
        list_data += struct.pack("<h", entry["x_pos"]) + \
                     struct.pack("<h", entry["y_pos"]) + \
                     struct.pack("<B", (entry["type_id"] << 6) | entry["unique_id"]) + \
                     struct.pack("<B", entry["subtype_id"]) + \
                     struct.pack("<B", entry["y_offset"]) + \
                     struct.pack("<B", entry["byte_8"]) + \
                     struct.pack("<h", entry["var_a"]) + \
                     struct.pack("<h", entry["var_b"])

    # Return the list data with the list end entry for all normal actor lists appended.
    return list_data + b'\xFF\x7F\xFF\x7F\x00\x00\x00\x00\x00\x00\x00\x00'

def get_loading_zone_list_bytes(loading_zone_list: list[CVHoDisLoadingZoneEntry]) -> bytearray:
    """Converts a given loading zone list into data to be inserted into the ROM."""
    list_data = bytearray(0)
    for entry in loading_zone_list:
        list_data += struct.pack("<I", entry["dest_room_ptr"]) + \
                     struct.pack("<b", entry["x_coord"]) + \
                     struct.pack("<b", entry["y_coord"]) + \
                     struct.pack("<b", entry["player_x_offset"]) + \
                     struct.pack("<b", entry["player_y_offset"]) + \
                     struct.pack("<h", entry["camera_x_pos"]) + \
                     struct.pack("<h", entry["camera_y_pos"])

    # Return the list data.
    # NOTE: Loading zone lists don't have a list end entry.
    return list_data

def get_room_state_bytes(room_state: CVHoDisRoomState) -> bytearray:
    """Converts a given room state into data to be inserted into the ROM."""
    return bytearray(struct.pack("<H", room_state["display_flags"]) + \
                     struct.pack("<H", room_state["alt_state_flag_id"]) + \
                     struct.pack("<I", room_state["alt_state_ptr"]) + \
                     struct.pack("<I", room_state["layer_info_ptr"]) + \
                     struct.pack("<I", room_state["gfx_info_ptr"]) + \
                     struct.pack("<I", room_state["unknown_ptr"]) + \
                     struct.pack("<I", room_state["palette_info_ptr"]) + \
                     struct.pack("<I", room_state["actor_list_ptr"]) + \
                     struct.pack("<I", room_state["loading_zone_list_ptr"]) + \
                     struct.pack("<B", room_state["background_effect_id"]) + \
                     struct.pack("<B", room_state["palette_shift_id"]) + \
                     struct.pack("<H", room_state["area_info"]))
