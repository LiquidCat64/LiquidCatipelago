import zlib

import Utils

from worlds.Files import APDeltaPatch

import hashlib
import os
import pkgutil

from .data import patches, lname
from .stages import get_stage_info
from .text import cvlod_string_to_bytes, cvlod_text_truncate, cvlod_text_wrap
from .aesthetics import renon_item_dialogue, get_item_text_color
from .options import CVLoDOptions
from .locations import get_location_info
from settings import get_settings

CVLODUSHASH = '25258460f98f567497b24844abe3a05b'
ROM_PLAYER_LIMIT = 65535

nisitenma_ichigo_table_start = 0xB1B90
decomp_file_size_table_start = 0xB0CBC
number_of_ni_files = 473
file_buffers_start = 0x85C590

warp_map_offsets = [0xADF67, 0xADF77, 0xADF87, 0xADF97, 0xADFA7, 0xADFBB, 0xADFCB, 0xADFDF]

fountain_letters_to_numbers = {"O": 1, "M": 2, "H": 3, "V": 4}


class LocalRom(object):

    def __init__(self, file):
        self.orig_buffer = None
        self.decompressed_files = {}
        self.compressed_files = {}

        with open(file, 'rb') as stream:
            self.buffer = bytearray(stream.read())

        # Grab all the compressed files out of the ROM based on the Nisitenma-Ichigo table addresses.
        for i in range(1, number_of_ni_files):
            ni_table_entry_start = nisitenma_ichigo_table_start + (i * 8)
            file_start_addr = int.from_bytes(self.read_bytes(ni_table_entry_start + 1, 3), "big")
            file_size = int.from_bytes(self.read_bytes(ni_table_entry_start + 5, 3), "big") - file_start_addr
            self.compressed_files[i] = self.read_bytes(file_start_addr, file_size)

    def read_bit(self, address: int, bit_number: int) -> bool:
        bitflag = (1 << bit_number)
        return (self.buffer[address] & bitflag) != 0

    def read_byte(self, address: int) -> int:
        return self.buffer[address]

    def read_bytes(self, startaddress: int, length: int) -> bytes:
        return self.buffer[startaddress:startaddress + length]

    def write_byte(self, address: int, value: int, file_num: int = 0):
        if file_num == 0:
            self.buffer[address] = value
        else:
            if file_num not in self.decompressed_files:
                self.decompress_file(file_num)
            self.decompressed_files[file_num][address] = value

    def write_bytes(self, startaddress: int, values, file_num: int = 0):
        if file_num == 0:
            self.buffer[startaddress:startaddress + len(values)] = values
        else:
            if file_num not in self.decompressed_files:
                self.decompress_file(file_num)
            self.decompressed_files[file_num][startaddress:startaddress + len(values)] = values

    def write_int16(self, address, value: int, file_num: int = 0):
        value = value & 0xFFFF
        self.write_bytes(address, [(value >> 8) & 0xFF, value & 0xFF], file_num)

    def write_int16s(self, startaddress, values, file_num: int = 0):
        for i, value in enumerate(values):
            self.write_int16(startaddress + (i * 2), value, file_num)

    def write_int24(self, address, value: int, file_num: int = 0):
        value = value & 0xFFFFFF
        self.write_bytes(address, [(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF], file_num)

    def write_int24s(self, startaddress, values, file_num: int = 0):
        for i, value in enumerate(values):
            self.write_int24(startaddress + (i * 3), value, file_num)

    def write_int32(self, address, value: int, file_num: int = 0):
        value = value & 0xFFFFFFFF
        self.write_bytes(address, [(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF],
                         file_num)

    def write_int32s(self, startaddress, values, file_num: int = 0):
        for i, value in enumerate(values):
            self.write_int32(startaddress + (i * 4), value, file_num)

    def decompress_file(self, file_num):
        self.decompressed_files[file_num] = bytearray(zlib.decompress(self.compressed_files[file_num][4:]))

    def compress_file(self, file_num):
        compressed_file = bytearray(zlib.compress(self.decompressed_files[file_num], level=zlib.Z_BEST_COMPRESSION))
        # Pad the file to 0x02
        if len(compressed_file) % 2:
            compressed_file.append(0x00)
        self.compressed_files[file_num] = bytearray((0x80000004 + len(compressed_file)).to_bytes(4, "big")) \
                                          + bytearray(compressed_file)

    def reinsert_all_files(self):
        displacement = 0
        for i in range(1, number_of_ni_files):
            # Re-compress the file if decompressed and update the decompressed sizes table
            if i in self.decompressed_files:
                self.compress_file(i)
                self.write_int24(decomp_file_size_table_start + (i * 8) + 5, len(self.decompressed_files[i]))

            start_addr = file_buffers_start + displacement
            end_addr = start_addr + len(self.compressed_files[i])
            displacement += len(self.compressed_files[i])

            self.write_bytes(start_addr, self.compressed_files[i])

            # Update the Nisitenma-Ichigo table
            self.write_int24(nisitenma_ichigo_table_start + (i * 8) + 1, start_addr)
            self.write_int24(nisitenma_ichigo_table_start + (i * 8) + 5, end_addr)

    def write_to_file(self, file):
        with open(file, 'wb') as outfile:
            outfile.write(self.buffer)

    def read_from_file(self, file):
        with open(file, 'rb') as stream:
            self.buffer = bytearray(stream.read())


def patch_rom(multiworld, options: CVLoDOptions, rom, player, offset_data, active_stage_exits, s1s_per_warp,
              active_warp_list, required_s2s, total_s2s, shop_name_list, shop_desc_list, shop_colors_list, slot_name,
              active_locations, villa_fountain_order):
    w1 = str(s1s_per_warp).zfill(2)
    w2 = str(s1s_per_warp * 2).zfill(2)
    w3 = str(s1s_per_warp * 3).zfill(2)
    w4 = str(s1s_per_warp * 4).zfill(2)
    w5 = str(s1s_per_warp * 5).zfill(2)
    w6 = str(s1s_per_warp * 6).zfill(2)
    w7 = str(s1s_per_warp * 7).zfill(2)

    # NOP out the CRC BNEs
    rom.write_int32(0x66C, 0x00000000)
    rom.write_int32(0x678, 0x00000000)

    # Unlock Hard Mode and all characters and costumes from the start
    rom.write_int32(0x145C, 0x08007872)  # J 0x8001E1C8
    rom.write_int32(0x1D01C, 0x08007872)  # J 0x8001E1C8
    rom.write_int32s(0x1EDC8, patches.extras_unlocker)

    # NOP the store instructions that clear fields 0x02 in the actor lists so the rando can use them to "delete" actors.
    rom.write_int32(0xC232C, 0x00000000)
    rom.write_int32(0xC236C, 0x00000000)
    rom.write_int32(0xC300C, 0x00000000)
    rom.write_int32(0xC3284, 0x00000000)

    # Custom data-loading code
    rom.write_int32(0x18A94, 0x0800793C)  # J 0x8001E4F0
    rom.write_int32s(0x1F0F0, patches.custom_code_loader)

    # Custom remote item rewarding and DeathLink receiving code
    rom.write_int32(0x1C854, 0x080FF000)  # J 0x803FC000
    rom.write_int32s(0xFFC000, patches.remote_item_giver)
    rom.write_int32s(0xFFE190, patches.subweapon_surface_checker)

    # Extract the item models file, decompress it, append the AP icons, compress it back, re-insert it.
    # items_file = lzkn64.decompress_buffer(rom.read_bytes(0x9C5310, 0x3D28))
    # compressed_file = lzkn64.compress_buffer(items_file[0:0x69B6] + pkgutil.get_data(__name__, "data/ap_icons.bin"))
    # rom.write_bytes(0xBB2D88, compressed_file)
    # Update the items' Nisitenma-Ichigo table entry to point to the new file's start and end addresses in the ROM.
    # rom.write_int32s(0x95F04, [0x80BB2D88, 0x00BB2D88 + len(compressed_file)])
    # Update the items' decompressed file size tables with the new file's decompressed file size.
    # rom.write_int16(0x95706, 0x7BF0)
    # rom.write_int16(0x104CCE, 0x7BF0)
    # Update the Wooden Stake and Roses' item appearance settings table to point to the Archipelago item graphics.
    # rom.write_int16(0xEE5BA, 0x7B38)
    # rom.write_int16(0xEE5CA, 0x7280)
    # Change the items' sizes. The progression one will be larger than the non-progression one.
    # rom.write_int32(0xEE5BC, 0x3FF00000)
    # rom.write_int32(0xEE5CC, 0x3FA00000)

    # Make it possible to change the starting level.
    rom.write_byte(0x15D3, 0x46, 468)
    rom.write_byte(0x15D5, 0x00, 468)
    rom.write_byte(0x15DB, 0x02, 468)

    # Prevent flags from pre-setting in Henry Mode.
    rom.write_byte(0x22F, 0x04, 335)

    # Give Henry all the time in the world just like everyone else.
    rom.write_byte(0x86DDF, 0x04)

    # Make the final Cerberus in Villa Front Yard un-set the Villa entrance portcullis closed flag for all characters.
    rom.write_int32(0x35A4, 0x00000000, 303)

    # Give the Gardener his Cornell behavior for everyone.
    rom.write_int32(0x490, 0x24020002, 304)  # ADDIU V0, R0, 0x0002
    rom.write_int32(0xD20, 0x00000000, 304)
    rom.write_int32(0x13CC, 0x00000000, 304)

    # Give Child Henry his Cornell behavior for everyone.
    rom.write_int32(0x1B8, 0x24020002, 275)  # ADDIU V0, R0, 0x0002
    rom.write_byte(0x613, 0x04, 275)
    rom.write_int32(0x844, 0x240F0002, 275)  # ADDIU T7, R0, 0x0002
    rom.write_int32(0x8B8, 0x240F0002, 275)  # ADDIU T7, R0, 0x0002

    # Make Gilles De Rais spawn in the Villa crypt for everyone.
    rom.write_byte(0x195, 0x00, 262)

    # Lock the two doors dividing the front and rear Maze Garden with the Rose Garden Key
    rom.write_byte(0x7983C1, 0x08)
    rom.write_byte(0x7983E1, 0x09)
    rom.write_int16(0x797F50, 0x5300)
    rom.write_int16(0x797F58, 0x0293)
    rom.write_byte(0x797F5F, 0x23)
    rom.write_int16(0x797F62, 0x0405)
    rom.write_int16(0x797F7C, 0x5300)
    rom.write_int16(0x797F84, 0x0293)
    rom.write_byte(0x797F8B, 0x23)
    rom.write_int16(0x797F8E, 0x0405)
    rom.write_bytes(0x797308, cvlod_string_to_bytes("\"Maze Gate\"\n"
                                                    "\"One key unlocks both.\"", append_end=False))
    rom.write_bytes(0x797294, cvlod_string_to_bytes("A click sounds from\n"
                                                    "both Garden gates... ", append_end=False))
    rom.write_bytes(0x78836E, cvlod_string_to_bytes("A door marked\n"
                                                    " \"Rose Garden Door\"\n"
                                                    "\"One key unlocks us all.\"", a_advance=True))
    rom.write_bytes(0x7883E8, cvlod_string_to_bytes("A click sounds from\n"
                                                    "all Rose Garden Key doors...", a_advance=True))
    rom.write_bytes(0x796FD6, cvlod_string_to_bytes("A door marked\n"
                                                    " \"Rose Garden Door\"\n"
                                                    "\"One key unlocks us all.\"       ", append_end=False))
    rom.write_bytes(0x79705E, cvlod_string_to_bytes("A click sounds from\n"
                                                    "all Rose Garden Key doors...", append_end=False))

    # Apply the child Henry gate checks to the two doors leading to the vampire crypt, so he can't be brought in there.
    rom.write_byte(0x797BB4, 0x53)
    rom.write_int32(0x797BB8, 0x802E4C34)
    rom.write_byte(0x797D6C, 0x52)
    rom.write_int32(0x797D70, 0x802E4C34)

    # Hack to make the Forest, CW and Villa intro cutscenes play at the start of their levels no matter what map came
    # before them
    # #rom.write_int32(0x97244, 0x803FDD60)
    # #rom.write_int32s(0xBFDD60, patches.forest_cw_villa_intro_cs_player)

    # Make changing the map ID to 0xFF reset the map. Helpful to work around a bug wherein the camera gets stuck when
    # entering a loading zone that doesn't change the map.
    # #rom.write_int32s(0x197B0, [0x0C0FF7E6,  # JAL   0x803FDF98
    #                            0x24840008])  # ADDIU A0, A0, 0x0008
    # #rom.write_int32s(0xBFDF98, patches.map_id_refresher)

    # Enable swapping characters when loading into a map by holding L.
    # rom.write_int32(0x97294, 0x803FDFC4)
    # rom.write_int32(0x19710, 0x080FF80E)  # J 0x803FE038
    # rom.write_int32s(0xBFDFC4, patches.character_changer)

    # Villa coffin time-of-day hack
    # rom.write_byte(0xD9D83, 0x74)
    # rom.write_int32(0xD9D84, 0x080FF14D)  # J 0x803FC534
    # rom.write_int32s(0xBFC534, patches.coffin_time_checker)

    # Fix both Castle Center elevator bridges for both characters unless enabling only one character's stages. At which
    # point one bridge will be always broken and one always repaired instead.
    # if options.character_stages.value == options.character_stages.option_reinhardt_only:
    # rom.write_int32(0x6CEAA0, 0x240B0000)  # ADDIU T3, R0, 0x0000
    # elif options.character_stages.value == options.character_stages.option_carrie_only == 3:
    # rom.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
    # else:
    # rom.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
    # rom.write_int32(0x6CEAA4, 0x240D0001)  # ADDIU T5, R0, 0x0001

    # Enable being able to carry multiple Special jewels, Nitros, Mandragoras, and Key Items simultaneously
    # Special1
    rom.write_int32s(0x904B8, [0x90C8AB47,  # LBU   T0, 0xAB47 (A2)
                               0x00681821,  # ADDU  V1, V1, T0
                               0xA0C3AB47])  # SB    V1, 0xAB47 (A2)
    rom.write_int32(0x904C8, 0x24020001)  # ADDIU V0, R0, 0x0001
    # Special2
    rom.write_int32s(0x904CC, [0x90C8AB48,  # LBU   T0, 0xAB48 (A2)
                               0x00681821,  # ADDU  V1, V1, T0
                               0xA0C3AB48])  # SB    V1, 0xAB48 (A2)
    rom.write_int32(0x904DC, 0x24020001)  # ADDIU V0, R0, 0x0001
    # Special3 (NOP this one for usage as the AP item)
    rom.write_int32(0x904E8, 0x00000000)
    # Magical Nitro
    rom.write_int32(0x9071C, 0x10000004)  # B [forward 0x04]
    rom.write_int32s(0x90734, [0x25430001,  # ADDIU	V1, T2, 0x0001
                               0x10000003])  # B [forward 0x03]
    # Mandragora
    rom.write_int32(0x906D4, 0x10000004)  # B [forward 0x04]
    rom.write_int32s(0x906EC, [0x25030001,  # ADDIU	V1, T0, 0x0001
                               0x10000003])  # B [forward 0x03]
    # Key Items
    rom.write_byte(0x906C7, 0x63)
    # Increase Use Item capacity to 99 if "Increase Item Limit" is turned on
    if options.increase_item_limit.value:
        rom.write_byte(0x90617, 0x63)  # Most items
        rom.write_byte(0x90767, 0x63)  # Sun/Moon cards

    # Rename the Special3 to "AP Item"
    rom.write_bytes(0xB89AA, cvlod_string_to_bytes("AP Item ", append_end=False))
    # Change the Special3's appearance to that of a spinning contract
    rom.write_int32s(0x11770A, [0x63583F80, 0x0000FFFF])
    # Disable spinning on the Special1 and 2 pickup models so colorblind people can more easily identify them
    rom.write_byte(0x1176F5, 0x00)  # Special1
    rom.write_byte(0x117705, 0x00)  # Special2
    # Make the Special2 the same size as a Red jewel(L) to further distinguish them
    rom.write_int32(0x1176FC, 0x3FA66666)
    # Capitalize the "k" in "Archives key" and "Rose Garden key" to be consistent with...literally every other key name!
    rom.write_byte(0xB8AFF, 0x2B)
    rom.write_byte(0xB8BCB, 0x2B)
    # Make the "PowerUp" textbox appear even if you already have two.
    rom.write_int32(0x87E34, 0x00000000)  # NOP

    # Enable changing the item model/visibility on any item instance.
    rom.write_int32s(0x107740, [0x0C0FF0C0,  # JAL   0x803FC300
                                0x25CFFFFF])  # ADDIU T7, T6, 0xFFFF
    rom.write_int32s(0xFFC300, patches.item_customizer)
    rom.write_int32(0x1078D0, 0x0C0FF0CB),  # JAL   0x803FC32C
    rom.write_int32s(0xFFC32C, patches.item_appearance_switcher)

    # Disable the 3HBs checking and setting flags when breaking them and enable their individual items checking and
    # setting flags instead.
    if options.multi_hit_breakables.value:
        rom.write_int16(0xE3488, 0x1000)
        rom.write_int32(0xE3800, 0x24050000)  # ADDIU	A1, R0, 0x0000
        rom.write_byte(0xE39EB, 0x00)
        rom.write_int32(0xE3A58, 0x0C0FF0D4),  # JAL   0x803FC350
        rom.write_int32s(0xFFC350, patches.three_hit_item_flags_setter)
        # Villa foyer chandelier-specific functions (yeah, KCEK was really insistent on having special handling just
        # for this one)
        rom.write_int32(0xE2F4C, 0x00000000)  # NOP
        rom.write_int32(0xE3114, 0x0C0FF0DE),  # JAL   0x803FC378
        rom.write_int32s(0xFFC378, patches.chandelier_item_flags_setter)

        # New flag values to put in each 3HB vanilla flag's spot
        rom.write_int16(0x7816F6, 0x02B8)  # CW upper rampart save nub
        rom.write_int16(0x78171A, 0x02BD)  # CW Dracula switch slab
        rom.write_int16(0x787F66, 0x0302)  # Villa foyer chandelier
        rom.write_int16(0x79F19E, 0x0307)  # Tunnel twin arrows rock
        rom.write_int16(0x79F1B6, 0x030C)  # Tunnel lonesome bucket pit rock
        rom.write_int16(0x7A41B6, 0x030F)  # UW poison parkour ledge
        rom.write_int16(0x7A41DA, 0x0315)  # UW skeleton crusher ledge
        rom.write_int16(0x7A8AF6, 0x0318)  # CC Behemoth crate
        rom.write_int16(0x7AD836, 0x031D)  # CC elevator pedestal
        rom.write_int16(0x7B0592, 0x0320)  # CC lizard locker slab
        rom.write_int16(0x7D0DDE, 0x0324)  # CT gear climb battery slab
        rom.write_int16(0x7D0DC6, 0x032A)  # CT gear climb top corner slab
        rom.write_int16(0x829A16, 0x032D)  # CT giant chasm farside climb
        rom.write_int16(0x82CC8A, 0x0330)  # CT beneath final slide

        # Kills the pointer to the Countdown number and resets the "in a demo?" value whenever changing/reloading the
        # game state.
        rom.write_int32(0x1168, 0x08007938)  # J 0x8001E4E0
        rom.write_int32s(0x1F0E0, [0x3C08801D,   # LUI   T0, 0x801D
                                   0xA100AA4A,   # SB    R0, 0xAA4A (T0)
                                   0x03E00008,   # JR    RA
                                   0xFD00AA40])  # SD    R0, 0xAA40 (T0)

    # Everything related to the Countdown counter
    if options.countdown.value:
        rom.write_int32(0x1C734, 0x080FF141)  # J 0x803FC504
        rom.write_int32(0x1F118, 0x080FF147)  # J 0x803FC51C
        rom.write_int32s(0xFFC3C0, patches.countdown_number_displayer)
        rom.write_int32s(0xFFC4D0, patches.countdown_number_manager)
        rom.write_int32(0x877E0, 0x080FF18D)  # J 0x803FC634
        rom.write_int32(0x878F0, 0x080FF188)  # J 0x803FC620
        rom.write_int32s(0x8BFF0, [0x0C0FF192,   # JAL 0x803FC648
                                   0xA2090000])  # SB  T1, 0x0000 (S0)
        rom.write_int32s(0x8C028, [0x0C0FF199,   # JAL 0x803FC664
                                   0xA20E0000])  # SB  T6, 0x0000 (S0)
        rom.write_int32(0x108D80, 0x0C0FF1A0)  # JAL 0x803FC680

    # Skip the "There is a white jewel" text so checking one saves the game instantly.
    # rom.write_int32s(0xEFC72, [0x00020002 for _ in range(37)])
    # rom.write_int32(0xA8FC0, 0x24020001)  # ADDIU V0, R0, 0x0001
    # Skip the yes/no prompts when activating things.
    # rom.write_int32s(0xBFDACC, patches.map_text_redirector)
    # rom.write_int32(0xA9084, 0x24020001)  # ADDIU V0, R0, 0x0001
    # rom.write_int32(0xBEBE8, 0x0C0FF6B4)  # JAL   0x803FDAD0
    # Skip Vincent and Heinrich's mandatory-for-a-check dialogue
    # rom.write_int32(0xBED9C, 0x0C0FF6DA)  # JAL   0x803FDB68
    # Skip the long yes/no prompt in the CC planetarium to set the pieces.
    # rom.write_int32(0xB5C5DF, 0x24030001)  # ADDIU  V1, R0, 0x0001
    # Skip the yes/no prompt to activate the CC elevator.
    # rom.write_int32(0xB5E3FB, 0x24020001)  # ADDIU  V0, R0, 0x0001
    # Skip the yes/no prompts to set Nitro/Mandragora at both walls.
    # rom.write_int32(0xB5DF3E, 0x24030001)  # ADDIU  V1, R0, 0x0001

    # Custom message if you try checking the downstairs CC crack before removing the seal.
    # rom.write_bytes(0xBFDBAC, cvlod_string_to_bytes("The Furious Nerd Curse\n"
    #                                               "prevents you from setting\n"
    #                                               "anything until the seal\n"
    #                                               "is removed!", True))

    # rom.write_int32s(0xBFDD20, patches.special_descriptions_redirector)

    # Change the Stage Select menu options
    # rom.write_int32s(0xADF64, patches.warp_menu_rewrite)
    # rom.write_int32s(0x10E0C8, patches.warp_pointer_table)
    # for i in range(len(active_warp_list)):
    #    if i == 0:
    # rom.write_byte(warp_map_offsets[i], get_stage_info(active_warp_list[i], "start map id"))
    # rom.write_byte(warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "start spawn id"))
    #    else:
    # rom.write_byte(warp_map_offsets[i], get_stage_info(active_warp_list[i], "mid map id"))
    # rom.write_byte(warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "mid spawn id"))

    # Play the "teleportation" sound effect when teleporting
    # rom.write_int32s(0xAE088, [0x08004FAB,  # J 0x80013EAC
    #                           0x2404019E])  # ADDIU A0, R0, 0x019E

    # Change the Stage Select menu's text to reflect its new purpose
    # rom.write_bytes(0xEFAD0, cvlod_string_to_bytes(f"Where to...?\t{active_warp_list[0]}\t"
    #                                              f"`{w1} {active_warp_list[1]}\t"
    #                                              f"`{w2} {active_warp_list[2]}\t"
    #                                              f"`{w3} {active_warp_list[3]}\t"
    #                                              f"`{w4} {active_warp_list[4]}\t"
    #                                              f"`{w5} {active_warp_list[5]}\t"
    #                                              f"`{w6} {active_warp_list[6]}\t"
    #                                              f"`{w7} {active_warp_list[7]}"))

    # Lizard-man save proofing
    # rom.write_int32(0xA99AC, 0x080FF0B8)  # J 0x803FC2E0
    # rom.write_int32s(0xBFC2E0, patches.boss_save_stopper)

    # Disable or guarantee vampire Vincent's fight
    # if options.vincent_fight_condition.value == options.vincent_fight_condition.option_never:
    # rom.write_int32(0xAACC0, 0x24010001)  # ADDIU AT, R0, 0x0001
    # rom.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000
    # elif options.vincent_fight_condition.value == options.vincent_fight_condition.option_always:
    # rom.write_int32(0xAACE0, 0x24180010)  # ADDIU T8, R0, 0x0010
    # else:
    # rom.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000

    # Disable or guarantee Renon's fight
    # rom.write_int32(0xAACB4, 0x080FF1A4)  # J 0x803FC690
    # if options.renon_fight_condition.value == options.renon_fight_condition.option_never:
    # rom.write_byte(0xB804F0, 0x00)
    # rom.write_byte(0xB80632, 0x00)
    # rom.write_byte(0xB807E3, 0x00)
    # rom.write_byte(0xB80988, 0xB8)
    # rom.write_byte(0xB816BD, 0xB8)
    # rom.write_byte(0xB817CF, 0x00)
    # rom.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
    # elif options.renon_fight_condition.value == options.renon_fight_condition.option_always:
    # rom.write_byte(0xB804F0, 0x0C)
    # rom.write_byte(0xB80632, 0x0C)
    # rom.write_byte(0xB807E3, 0x0C)
    # rom.write_byte(0xB80988, 0xC4)
    # rom.write_byte(0xB816BD, 0xC4)
    # rom.write_byte(0xB817CF, 0x0C)
    # rom.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
    # else:
    # rom.write_int32s(0xBFC690, patches.renon_cutscene_checker)

    # NOP the Easy Mode check when buying a thing from Renon, so he can be triggered even on this mode.
    # rom.write_int32(0xBD8B4, 0x00000000)

    # Disable or guarantee the Bad Ending
    # if options.bad_ending_condition.value == options.bad_ending_condition.option_never:
    # rom.write_int32(0xAEE5C6, 0x3C0A0000)  # LUI  T2, 0x0000
    # elif options.bad_ending_condition.value == options.bad_ending_condition.option_always:
    # rom.write_int32(0xAEE5C6, 0x3C0A0040)  # LUI  T2, 0x0040

    # Play Castle Keep's song if teleporting in front of Dracula's door outside the escape sequence
    # rom.write_int32(0x6E937C, 0x080FF12E)  # J 0x803FC4B8
    # rom.write_int32s(0xBFC4B8, patches.ck_door_music_player)

    # Change the item healing values if "Nerf Healing" is turned on
    # if options.nerf_healing_items.value:
    # rom.write_byte(0xB56371, 0x50)  # Healing kit   (100 -> 80)
    # rom.write_byte(0xB56374, 0x32)  # Roast beef    ( 80 -> 50)
    # rom.write_byte(0xB56377, 0x19)  # Roast chicken ( 50 -> 25)

    # Disable loading zone healing if turned off
    # if not options.loading_zone_heals.value:
    # rom.write_byte(0xD99A5, 0x00)  # Skip all loading zone checks
    # rom.write_byte(0xA9DFFB, 0x40)  # Disable free heal from King Skeleton by reading the unused magic meter value

    # Prevent the vanilla Magical Nitro transport's "can explode" flag from setting
    # rom.write_int32(0xB5D7AA, 0x00000000)  # NOP

    # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes
    # rom.write_byte(0xA6253D, 0x03)

    # Enable the Game Over's "Continue" menu starting the cursor on whichever checkpoint is most recent
    # rom.write_int32(0xB4DDC, 0x0C060D58)  # JAL 0x80183560
    # rom.write_int32s(0x106750, patches.continue_cursor_start_checker)
    # rom.write_int32(0x1C444, 0x080FF08A)  # J   0x803FC228
    # rom.write_int32(0x1C2A0, 0x080FF08A)  # J   0x803FC228
    # rom.write_int32s(0xBFC228, patches.savepoint_cursor_updater)
    # rom.write_int32(0x1C2D0, 0x080FF094)  # J   0x803FC250
    # rom.write_int32s(0xBFC250, patches.stage_start_cursor_updater)
    # rom.write_byte(0xB585C8, 0xFF)

    # Make the Special1 and 2 play sounds when you reach milestones with them.
    # rom.write_int32s(0xBFDA50, patches.special_sound_notifs)
    # rom.write_int32(0xBF240, 0x080FF694)  # J 0x803FDA50
    # rom.write_int32(0xBF220, 0x080FF69E)  # J 0x803FDA78

    # Add data for White Jewel #22 (the new Duel Tower savepoint) at the end of the White Jewel ID data list
    # rom.write_int16s(0x104AC8, [0x0000, 0x0006,
    #                            0x0013, 0x0015])

    # Change the File Select stage numbers to match the new stage order. Also fix a vanilla issue wherein saving in a
    # character-exclusive stage as the other character would incorrectly display the name of that character's equivalent
    # stage on the save file instead of the one they're actually in.
    # rom.write_byte(0xC9FE3, 0xD4)
    # rom.write_byte(0xCA055, 0x08)
    # rom.write_byte(0xCA066, 0x40)
    # rom.write_int32(0xCA068, 0x860C17D0)  # LH T4, 0x17D0 (S0)
    # rom.write_byte(0xCA06D, 0x08)
    # rom.write_byte(0x104A31, 0x01)
    # rom.write_byte(0x104A39, 0x01)
    # rom.write_byte(0x104A89, 0x01)
    # rom.write_byte(0x104A91, 0x01)
    # rom.write_byte(0x104A99, 0x01)
    # rom.write_byte(0x104AA1, 0x01)

    # for stage in active_stage_exits:
    #    for offset in get_stage_info(stage, "save number offsets"):
    # rom.write_byte(offset, active_stage_exits[stage]["position"])

    # CC top elevator switch check
    # rom.write_int32(0x6CF0A0, 0x0C0FF0B0)  # JAL 0x803FC2C0
    # rom.write_int32s(0xBFC2C0, patches.elevator_flag_checker)

    # Disable time restrictions
    # if options.disable_time_restrictions.value:
    # Fountain
    # rom.write_int32(0x6C2340, 0x00000000)  # NOP
    # rom.write_int32(0x6C257C, 0x10000023)  # B [forward 0x23]
    # Rosa
    # rom.write_byte(0xEEAAB, 0x00)
    # rom.write_byte(0xEEAAD, 0x18)
    # Moon doors
    # rom.write_int32(0xDC3E0, 0x00000000)  # NOP
    # rom.write_int32(0xDC3E8, 0x00000000)  # NOP
    # Sun doors
    # rom.write_int32(0xDC410, 0x00000000)  # NOP
    # rom.write_int32(0xDC418, 0x00000000)  # NOP

    # Make received DeathLinks blow you to smithereens instead of kill you normally.
    # if options.death_link.value == options.death_link.option_explosive:
    # rom.write_int32(0x27A70, 0x10000008)  # B [forward 0x08]
    # rom.write_int32s(0xBFC0D0, patches.deathlink_nitro_edition)

    # DeathLink counter decrementer code
    # rom.write_int32(0x1C340, 0x080FF8F0)  # J 0x803FE3C0
    # rom.write_int32s(0xBFE3C0, patches.deathlink_counter_decrementer)
    # rom.write_int32(0x25B6C, 0x0080FF052)  # J 0x803FC148
    # rom.write_int32s(0xBFC148, patches.nitro_fall_killer)

    # Death flag un-setter on "Beginning of stage" state overwrite code
    # rom.write_int32(0x1C2B0, 0x080FF047)  # J 0x803FC11C
    # rom.write_int32s(0xBFC11C, patches.death_flag_unsetter)

    # Warp menu-opening code
    # rom.write_int32(0xB9BA8, 0x080FF099)  # J	0x803FC264
    # rom.write_int32s(0xBFC264, patches.warp_menu_opener)

    # NPC item textbox hack
    rom.write_int32s(0xFFC6F0, patches.npc_item_hack)
    # Change all the NPC item gives to run through the new function.
    # Fountain Top Shine
    rom.write_int16(0x35E, 0x8040, 371)
    rom.write_int16(0x362, 0xC700, 371)
    rom.write_byte(0x367, 0x00, 371)
    rom.write_int16(0x36E, 0x0068, 371)
    rom.write_bytes(0x720, cvlod_string_to_bytes("...", a_advance=True), 371)
    # 6am Rose Patch
    rom.write_int16(0x1E2, 0x8040, 370)
    rom.write_int16(0x1E6, 0xC700, 370)
    rom.write_byte(0x1EB, 0x01, 370)
    rom.write_int16(0x1F2, 0x0078, 370)
    rom.write_bytes(0x380, cvlod_string_to_bytes("...", a_advance=True), 370)
    # Vincent
    rom.write_int16(0x180E, 0x8040, 263)
    rom.write_int16(0x1812, 0xC700, 263)
    rom.write_byte(0x1817, 0x02, 263)
    rom.write_int16(0x181E, 0x027F, 263)
    rom.write_bytes(0x78E776, cvlod_string_to_bytes(" " * 173, append_end=False))
    # Mary
    rom.write_int16(0xB16, 0x8040, 280)
    rom.write_int16(0xB1A, 0xC700, 280)
    rom.write_byte(0xB1F, 0x03, 280)
    rom.write_int16(0xB26, 0x0086, 280)
    rom.write_bytes(0x78F40E, cvlod_string_to_bytes(" " * 295, append_end=False))
    # Heinrich
    rom.write_int16(0x962A, 0x8040, 252)
    rom.write_int16(0x962E, 0xC700, 252)
    rom.write_byte(0x9633, 0x04, 252)
    rom.write_int16(0x963A, 0x0284, 252)

    # Sub-weapon check function hook
    # rom.write_int32(0xBF32C, 0x00000000)  # NOP
    # rom.write_int32(0xBF330, 0x080FF05E)  # J	0x803FC178
    # rom.write_int32s(0xBFC178, patches.give_subweapon_stopper)

    # Warp menu Special1 restriction
    # rom.write_int32(0xADD68, 0x0C04AB12)  # JAL 0x8012AC48
    # rom.write_int32s(0xADE28, patches.stage_select_overwrite)
    # rom.write_byte(0xADE47, s1s_per_warp)

    # Dracula's door text pointer hijack
    # rom.write_int32(0xD69F0, 0x080FF141)  # J 0x803FC504
    # rom.write_int32s(0xBFC504, patches.dracula_door_text_redirector)

    # Dracula's chamber condition
    # rom.write_int32(0xE2FDC, 0x0804AB25)  # J 0x8012AC78
    # rom.write_int32s(0xADE84, patches.special_goal_checker)
    # rom.write_bytes(0xBFCC48, [0xA0, 0x00, 0xFF, 0xFF, 0xA0, 0x01, 0xFF, 0xFF, 0xA0, 0x02, 0xFF, 0xFF, 0xA0, 0x03, 0xFF,
    #                           0xFF, 0xA0, 0x04, 0xFF, 0xFF, 0xA0, 0x05, 0xFF, 0xFF, 0xA0, 0x06, 0xFF, 0xFF, 0xA0, 0x07,
    #                           0xFF, 0xFF, 0xA0, 0x08, 0xFF, 0xFF, 0xA0, 0x09])
    # if options.draculas_condition.value == options.draculas_condition.option_crystal:
    # rom.write_int32(0x6C8A54, 0x0C0FF0C1)  # JAL 0x803FC304
    # rom.write_int32s(0xBFC304, patches.crystal_special2_giver)
    # rom.write_bytes(0xBFCC6E, cvlod_string_to_bytes(f"It won't budge!\n"
    #                                                   f"You'll need the power\n"
    #                                                   f"of the basement crystal\n"
    #                                                   f"to undo the seal.", True))
    #    special2_name = "Crystal "
    #    special2_text = "The crystal is on!\n" \
    #                    "Time to teach the old man\n" \
    #                    "a lesson!"
    # elif options.draculas_condition.value == options.draculas_condition.option_bosses:
    # rom.write_int32(0xBBD50, 0x080FF18C)  # J	0x803FC630
    # rom.write_int32s(0xBFC630, patches.boss_special2_giver)
    # rom.write_bytes(0xBFCC6E, cvlod_string_to_bytes(f"It won't budge!\n"
    #                                                   f"You'll need to defeat\n"
    #                                                   f"{required_s2s} powerful monsters\n"
    #                                                   f"to undo the seal.", True))
    #    special2_name = "Trophy  "
    #    special2_text = f"Proof you killed a powerful\n" \
    #                    f"Night Creature. Earn {required_s2s}/{total_s2s}\n" \
    #                    f"to battle Dracula."
    # elif options.draculas_condition.value == options.draculas_condition.option_specials:
    #    special2_name = "Special2"
    # rom.write_bytes(0xBFCC6E, cvlod_string_to_bytes(f"It won't budge!\n"
    #                                                   f"You'll need to find\n"
    #                                                   f"{required_s2s} Special2 jewels\n"
    #                                                   f"to undo the seal.", True))
    #    special2_text = f"Need {required_s2s}/{total_s2s} to kill Dracula.\n" \
    #                    f"Looking closely, you see...\n" \
    #                    f"a piece of him within?"
    # else:
    #    #rom.write_byte(0xADE8F, 0x00)
    #    special2_name = "Special2"
    #    special2_text = "If you're reading this,\n" \
    #                    "how did you get a Special2!?"
    # rom.write_byte(0xADE8F, required_s2s)
    # Change the Special2 name depending on the setting.
    # rom.write_bytes(0xEFD4E, cvlod_string_to_bytes(special2_name))
    # Change the Special1 and 2 menu descriptions to tell you how many you need to unlock a warp and fight Dracula
    # respectively.
    # special_text_bytes = cvlod_string_to_bytes(f"{s1s_per_warp} per warp unlock.\n"
    #                                          f"{options.total_special1s.value} exist in total.\n"
    #                                          f"Z + R + START to warp.") + \
    #                     cvlod_string_to_bytes(special2_text)
    # rom.write_bytes(0xBFE53C, special_text_bytes)

    # On-the-fly TLB script modifier
    # rom.write_int32s(0xBFC338, patches.double_component_checker)
    # rom.write_int32s(0xBFC3D4, patches.downstairs_seal_checker)
    # rom.write_int32s(0xBFE074, patches.mandragora_with_nitro_setter)
    # rom.write_int32s(0xBFC700, patches.overlay_modifiers)

    # On-the-fly actor data modifier hook
    # rom.write_int32(0xEAB04, 0x080FF21E)  # J 0x803FC878
    # rom.write_int32s(0xBFC870, patches.map_data_modifiers)

    # Fix to make flags apply to freestanding invisible items properly
    # rom.write_int32(0xA84F8, 0x90CC0039)  # LBU T4, 0x0039 (A2)

    # Fix locked doors to check the key counters instead of their vanilla key locations' bitflags
    # Pickup flag check modifications:
    # rom.write_int32(0x10B2D8, 0x00000002)  # Left Tower Door
    # rom.write_int32(0x10B2F0, 0x00000003)  # Storeroom Door
    # rom.write_int32(0x10B2FC, 0x00000001)  # Archives Door
    # rom.write_int32(0x10B314, 0x00000004)  # Maze Gate
    # rom.write_int32(0x10B350, 0x00000005)  # Copper Door
    # rom.write_int32(0x10B3A4, 0x00000006)  # Torture Chamber Door
    # rom.write_int32(0x10B3B0, 0x00000007)  # ToE Gate
    # rom.write_int32(0x10B3BC, 0x00000008)  # Science Door1
    # rom.write_int32(0x10B3C8, 0x00000009)  # Science Door2
    # rom.write_int32(0x10B3D4, 0x0000000A)  # Science Door3
    # rom.write_int32(0x6F0094, 0x0000000B)  # CT Door 1
    # rom.write_int32(0x6F00A4, 0x0000000C)  # CT Door 2
    # rom.write_int32(0x6F00B4, 0x0000000D)  # CT Door 3
    # Item counter decrement check modifications:
    # rom.write_int32(0xEDA84, 0x00000001)  # Archives Door
    # rom.write_int32(0xEDA8C, 0x00000002)  # Left Tower Door
    # rom.write_int32(0xEDA94, 0x00000003)  # Storeroom Door
    # rom.write_int32(0xEDA9C, 0x00000004)  # Maze Gate
    # rom.write_int32(0xEDAA4, 0x00000005)  # Copper Door
    # rom.write_int32(0xEDAAC, 0x00000006)  # Torture Chamber Door
    # rom.write_int32(0xEDAB4, 0x00000007)  # ToE Gate
    # rom.write_int32(0xEDABC, 0x00000008)  # Science Door1
    # rom.write_int32(0xEDAC4, 0x00000009)  # Science Door2
    # rom.write_int32(0xEDACC, 0x0000000A)  # Science Door3
    # rom.write_int32(0xEDAD4, 0x0000000B)  # CT Door 1
    # rom.write_int32(0xEDADC, 0x0000000C)  # CT Door 2
    # rom.write_int32(0xEDAE4, 0x0000000D)  # CT Door 3

    # Fix ToE gate's "unlocked" flag in the locked door flags table
    # rom.write_int16(0x10B3B6, 0x0001)

    # rom.write_int32(0x10AB2C, 0x8015FBD4)  # Maze Gates' check code pointer adjustments
    # rom.write_int32(0x10AB40, 0x8015FBD4)
    # rom.write_int32s(0x10AB50, [0x0D0C0000,
    #                            0x8015FBD4])
    # rom.write_int32s(0x10AB64, [0x0D0C0000,
    #                            0x8015FBD4])
    # rom.write_int32s(0xE2E14, patches.normal_door_hook)
    # rom.write_int32s(0xBFC5D0, patches.normal_door_code)
    # rom.write_int32s(0x6EF298, patches.ct_door_hook)
    # rom.write_int32s(0xBFC608, patches.ct_door_code)
    # Fix key counter not decrementing if 2 or above
    # rom.write_int32(0xAA0E0, 0x24020000)  # ADDIU	V0, R0, 0x0000

    # Make the Easy-only candle drops in Room of Clocks appear on any difficulty
    # rom.write_byte(0x9B518F, 0x01)

    # Slightly move some once-invisible freestanding items to be more visible
    # if options.invisible_items.value == options.invisible_items.option_reveal_all:
    # rom.write_byte(0x7C7F95, 0xEF)  # Forest dirge maiden statue
    # rom.write_byte(0x7C7FA8, 0xAB)  # Forest werewolf statue
    # rom.write_byte(0x8099C4, 0x8C)  # Villa courtyard tombstone
    # rom.write_byte(0x83A626, 0xC2)  # Villa living room painting
    # #rom.write_byte(0x83A62F, 0x64)  # Villa Mary's room table
    # rom.write_byte(0xBFCB97, 0xF5)  # CC torture instrument rack
    # rom.write_byte(0x8C44D5, 0x22)  # CC red carpet hallway knight
    # rom.write_byte(0x8DF57C, 0xF1)  # CC cracked wall hallway flamethrower
    # rom.write_byte(0x90FCD6, 0xA5)  # CC nitro hallway flamethrower
    # rom.write_byte(0x90FB9F, 0x9A)  # CC invention room round machine
    # rom.write_byte(0x90FBAF, 0x03)  # CC invention room giant famicart
    # rom.write_byte(0x90FE54, 0x97)  # CC staircase knight (x)
    # rom.write_byte(0x90FE58, 0xFB)  # CC staircase knight (z)

    # Change bitflag on item in upper coffin in Forest final switch gate tomb to one that's not used by something else
    # rom.write_int32(0x10C77C, 0x00000002)

    # Make the torch directly behind Dracula's chamber that normally doesn't set a flag set bitflag 0x08 in 0x80389BFA
    # rom.write_byte(0x10CE9F, 0x01)

    # Change the CC post-Behemoth boss depending on the option for Post-Behemoth Boss
    # if options.post_behemoth_boss.value == options.post_behemoth_boss.option_inverted:
    # rom.write_byte(0xEEDAD, 0x02)
    # rom.write_byte(0xEEDD9, 0x01)
    # elif options.post_behemoth_boss.value == options.post_behemoth_boss.option_always_rosa:
    # rom.write_byte(0xEEDAD, 0x00)
    # rom.write_byte(0xEEDD9, 0x03)
    # Put both on the same flag so changing character won't trigger a rematch with the same boss.
    # rom.write_byte(0xEED8B, 0x40)
    # elif options.post_behemoth_boss.value == options.post_behemoth_boss.option_always_camilla:
    # rom.write_byte(0xEEDAD, 0x03)
    # rom.write_byte(0xEEDD9, 0x00)
    # rom.write_byte(0xEED8B, 0x40)

    # Change the RoC boss depending on the option for Room of Clocks Boss
    # if options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_inverted:
    # rom.write_byte(0x109FB3, 0x56)
    # rom.write_byte(0x109FBF, 0x44)
    # rom.write_byte(0xD9D44, 0x14)
    # rom.write_byte(0xD9D4C, 0x14)
    # elif options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_always_death:
    # rom.write_byte(0x109FBF, 0x44)
    # rom.write_byte(0xD9D45, 0x00)
    # Put both on the same flag so changing character won't trigger a rematch with the same boss.
    # rom.write_byte(0x109FB7, 0x90)
    # rom.write_byte(0x109FC3, 0x90)
    # elif options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_always_actrise:
    # rom.write_byte(0x109FB3, 0x56)
    # rom.write_int32(0xD9D44, 0x00000000)
    # rom.write_byte(0xD9D4D, 0x00)
    # rom.write_byte(0x109FB7, 0x90)
    # rom.write_byte(0x109FC3, 0x90)

    # Tunnel gondola skip
    # if options.skip_gondolas.value:
    # rom.write_int32(0x6C5F58, 0x080FF7D0)  # J 0x803FDF40
    # rom.write_int32s(0xBFDF40, patches.gondola_skipper)
    # New gondola transfer point candle coordinates
    # rom.write_byte(0xBFC9A3, 0x04)
    # rom.write_bytes(0x86D824, [0x27, 0x01, 0x10, 0xF7, 0xA0])

    # Waterway brick platforms skip
    # if options.skip_waterway_blocks.value:
    # rom.write_int32(0x6C7E2C, 0x00000000)  # NOP

    # Ambience silencing fix
    # rom.write_int32(0xD9270, 0x080FF840)  # J 0x803FE100
    # rom.write_int32s(0xBFE100, patches.ambience_silencer)
    # Fix for the door sliding sound playing infinitely if leaving the fan meeting room before the door closes entirely.
    # Hooking this in the ambience silencer code does nothing for some reason.
    # rom.write_int32s(0xAE10C, [0x08004FAB,  # J   0x80013EAC
    #                           0x3404829B])  # ORI A0, R0, 0x829B
    # rom.write_int32s(0xD9E8C, [0x08004FAB,  # J   0x80013EAC
    #                           0x3404829B])  # ORI A0, R0, 0x829B
    # Fan meeting room ambience fix
    # rom.write_int32(0x109964, 0x803FE13C)

    # Make the Villa coffin cutscene skippable
    # rom.write_int32(0xAA530, 0x080FF880)  # J 0x803FE200
    # rom.write_int32s(0xBFE200, patches.coffin_cutscene_skipper)

    # Increase shimmy speed
    # if options.increase_shimmy_speed.value:
    # rom.write_byte(0xA4241, 0x5A)

    # Disable landing fall damage
    # if options.fall_guard.value:
    # rom.write_byte(0x27B23, 0x00)

    # Permanent PowerUp stuff
    # if options.permanent_powerups.value:
    # Make receiving PowerUps increase the unused menu PowerUp counter instead of the one outside the save struct
    # rom.write_int32(0xBF2EC, 0x806B619B)  # LB	T3, 0x619B (V1)
    # rom.write_int32(0xBFC5BC, 0xA06C619B)  # SB	T4, 0x619B (V1)
    # Make Reinhardt's whip check the menu PowerUp counter
    # rom.write_int32(0x69FA08, 0x80CC619B)  # LB	T4, 0x619B (A2)
    # rom.write_int32(0x69FBFC, 0x80C3619B)  # LB	V1, 0x619B (A2)
    # rom.write_int32(0x69FFE0, 0x818C9C53)  # LB	T4, 0x9C53 (T4)
    # Make Carrie's orb check the menu PowerUp counter
    # rom.write_int32(0x6AC86C, 0x8105619B)  # LB	A1, 0x619B (T0)
    # rom.write_int32(0x6AC950, 0x8105619B)  # LB	A1, 0x619B (T0)
    # rom.write_int32(0x6AC99C, 0x810E619B)  # LB	T6, 0x619B (T0)
    # rom.write_int32(0x5AFA0, 0x80639C53)  # LB	V1, 0x9C53 (V1)
    # rom.write_int32(0x5B0A0, 0x81089C53)  # LB	T0, 0x9C53 (T0)
    # rom.write_byte(0x391C7, 0x00)  # Prevent PowerUps from dropping from regular enemies
    # rom.write_byte(0xEDEDF, 0x03)  # Make any vanishing PowerUps that do show up L jewels instead
    # Rename the PowerUp to "PermaUp"
    # rom.write_bytes(0xEFDEE, cvlod_string_to_bytes("PermaUp"))
    # Replace the PowerUp in the Forest Special1 Bridge 3HB rock with an L jewel if 3HBs aren't randomized
    #    if not options.multi_hit_breakables.value:
    # rom.write_byte(0x10C7A1, 0x03)
    # Change the appearance of the Pot-Pourri to that of a larger PowerUp regardless of the above setting, so other
    # game PermaUps are distinguishable.
    # rom.write_int32s(0xEE558, [0x06005F08, 0x3FB00000, 0xFFFFFF00])

    # Write the randomized (or disabled) music ID list and its associated code
    # if options.background_music.value:
    # rom.write_int32(0x14588, 0x08060D60)  # J 0x80183580
    # rom.write_int32(0x14590, 0x00000000)  # NOP
    # rom.write_int32s(0x106770, patches.music_modifier)
    # rom.write_int32(0x15780, 0x0C0FF36E)  # JAL 0x803FCDB8
    # rom.write_int32s(0xBFCDB8, patches.music_comparer_modifier)

    # Once-per-frame gameplay checks
    # rom.write_int32(0x6C848, 0x080FF40D)  # J 0x803FD034
    # rom.write_int32(0xBFD058, 0x0801AEB5)  # J 0x8006BAD4

    # Everything related to dropping the previous sub-weapon
    # if options.drop_previous_sub_weapon.value:
    # rom.write_int32(0xBFD034, 0x080FF3FF)  # J 0x803FCFFC
    # rom.write_int32(0xBFC18C, 0x080FF3F2)  # J 0x803FCFC8
    # rom.write_int32s(0xBFCFC4, patches.prev_subweapon_spawn_checker)
    # rom.write_int32s(0xBFCFFC, patches.prev_subweapon_fall_checker)
    # rom.write_int32s(0xBFD060, patches.prev_subweapon_dropper)

    # Ice Trap stuff
    # rom.write_int32(0x697C60, 0x080FF06B)  # J 0x803FC18C
    # rom.write_int32(0x6A5160, 0x080FF06B)  # J 0x803FC18C
    # rom.write_int32s(0xBFC1AC, patches.ice_trap_initializer)
    # rom.write_int32s(0xBFC1D8, patches.the_deep_freezer)
    # rom.write_int32s(0xB2F354, [0x3739E4C0,  # ORI T9, T9, 0xE4C0
    #                            0x03200008,  # JR  T9
    #                            0x00000000])  # NOP
    # rom.write_int32s(0xBFE4C0, patches.freeze_verifier)

    # Initial Countdown numbers and Start Inventory
    rom.write_int32(0x90DBC, 0x080FF200)  # J	0x803FC800
    rom.write_int32s(0xFFC800, patches.new_game_extras)

    # Everything related to shopsanity
    # if options.shopsanity.value:
    # rom.write_bytes(0x103868, cvlod_string_to_bytes("Not obtained. "))
    # rom.write_int32s(0xBFD8D0, patches.shopsanity_stuff)
    # rom.write_int32(0xBD828, 0x0C0FF643)  # JAL	0x803FD90C
    # rom.write_int32(0xBD5B8, 0x0C0FF651)  # JAL	0x803FD944
    # rom.write_int32(0xB0610, 0x0C0FF665)  # JAL	0x803FD994
    # rom.write_int32s(0xBD24C, [0x0C0FF677,  # J  	0x803FD9DC
    #                               0x00000000])  # NOP
    # rom.write_int32(0xBD618, 0x0C0FF684)  # JAL	0x803FDA10

    # shopsanity_name_text = []
    # shopsanity_desc_text = []
    # for i in range(len(shop_name_list)):
    #    shopsanity_name_text += [0xA0, i] + shop_colors_list[i] + cvlod_string_to_bytes(cvlod_text_truncate(
    #        shop_name_list[i], 74))

    #    shopsanity_desc_text += [0xA0, i]
    #    if shop_desc_list[i][1] is not None:
    #        shopsanity_desc_text += cvlod_string_to_bytes("For " + shop_desc_list[i][1] + ".\n", append_end=False)
    #    shopsanity_desc_text += cvlod_string_to_bytes(renon_item_dialogue[shop_desc_list[i][0]])
    # rom.write_bytes(0x1AD00, shopsanity_name_text)
    # rom.write_bytes(0x1A800, shopsanity_desc_text)

    # Panther Dash running
    # if options.panther_dash.value:
    # rom.write_int32(0x69C8C4, 0x0C0FF77E)  # JAL   0x803FDDF8
    # rom.write_int32(0x6AA228, 0x0C0FF77E)  # JAL   0x803FDDF8
    # rom.write_int32s(0x69C86C, [0x0C0FF78E,  # JAL   0x803FDE38
    #                            0x3C01803E])  # LUI   AT, 0x803E
    # rom.write_int32s(0x6AA1D0, [0x0C0FF78E,  # JAL   0x803FDE38
    #                            0x3C01803E])  # LUI   AT, 0x803E
    # rom.write_int32(0x69D37C, 0x0C0FF79E)  # JAL   0x803FDE78
    # rom.write_int32(0x6AACE0, 0x0C0FF79E)  # JAL   0x803FDE78
    # rom.write_int32s(0xBFDDF8, patches.panther_dash)
    # Jump prevention
    # if options.panther_dash.value == options.panther_dash.option_jumpless:
    # rom.write_int32(0xBFDE2C, 0x080FF7BB)  # J     0x803FDEEC
    # rom.write_int32(0xBFD044, 0x080FF7B1)  # J     0x803FDEC4
    # rom.write_int32s(0x69B630, [0x0C0FF7C6,  # JAL   0x803FDF18
    #                                0x8CCD0000])  # LW    T5, 0x0000 (A2)
    # rom.write_int32s(0x6A8EC0, [0x0C0FF7C6,  # JAL   0x803FDF18
    #                                0x8CCC0000])  # LW    T4, 0x0000 (A2)
    # Fun fact: KCEK put separate code to handle coyote time jumping
    # rom.write_int32s(0x69910C, [0x0C0FF7C6,  # JAL   0x803FDF18
    #                                0x8C4E0000])  # LW    T6, 0x0000 (V0)
    # rom.write_int32s(0x6A6718, [0x0C0FF7C6,  # JAL   0x803FDF18
    #                                0x8C4E0000])  # LW    T6, 0x0000 (V0)
    # rom.write_int32s(0xBFDEC4, patches.panther_jump_preventer)

    # Write all the new item and loading zone bytes
    for offset in patches.always_actor_edits:
        rom.write_byte(offset, patches.always_actor_edits[offset])
    for offset in patches.cw_combined_edits:
        rom.write_byte(offset, patches.cw_combined_edits[offset])
    for offset in patches.villa_combined_edits:
        rom.write_byte(offset, patches.villa_combined_edits[offset])

    # Make the lever checks for Cornell always pass
    rom.write_int32(0xE6C18, 0x240A0002)  # ADDIU T2, R0, 0x0002
    rom.write_int32(0xE6F64, 0x240E0002)  # ADDIU T6, R0, 0x0002
    rom.write_int32(0xE70F4, 0x240D0002)  # ADDIU T5, R0, 0x0002
    rom.write_int32(0xE7364, 0x24080002)  # ADDIU T0, R0, 0x0002
    rom.write_int32(0x109C10, 0x240E0002)  # ADDIU T6, R0, 0x0002

    # Make the fountain pillar checks for Cornell always pass
    rom.write_int32(0xD77E0, 0x24030002)  # ADDIU V1, R0, 0x0002
    rom.write_int32(0xD7A60, 0x24030002)  # ADDIU V1, R0, 0x0002

    # Make only some rose garden checks for Cornell always pass
    rom.write_byte(0x78619B, 0x24)
    rom.write_int16(0x7861A0, 0x5423)
    rom.write_int32(0x786324, 0x240E0002)  # ADDIU T6, R0, 0x0002
    # Make the thirsty J. A. Oldrey cutscene check for Cornell always pass
    rom.write_byte(0x11831D, 0x00)
    # Make the Villa coffin lid Henry checks never pass
    rom.write_byte(0x7D45FB, 0x04)
    rom.write_byte(0x7D4BFB, 0x04)
    # Make the Villa coffin loading zone Henry check always pass
    rom.write_int32(0xD3A78, 0x000C0821)  # ADDU  AT, R0, T4
    # Make the Villa coffin lid Cornell attack collision check always pass
    rom.write_int32(0x7D4D9C, 0x00000000)  # NOP
    # Make the Villa coffin lid Cornell cutscene check never pass
    rom.write_byte(0x7D518F, 0x04)
    # Make the hardcoded Cornell check in the Villa crypt Reinhardt/Carrie first vampire intro cutscene not pass.
    # IDK what KCEK was smoking here, since Cornell normally doesn't get this cutscene, but if it passes the game
    # literally ceases functioning.
    rom.write_int16(0x230, 0x1000, 427)
    # Insert a special message over the "Found a hidden path" text.
    rom.write_bytes(0xB30, cvlod_string_to_bytes("<To Be Continued|\\|/", append_end=False), 429)

    # Change Oldrey's Diary into an item location.
    rom.write_int16(0x792A24, 0x0027)
    rom.write_int16(0x792A28, 0x0084)
    rom.write_byte(0x792A2D, 0x17)
    # Change the Maze Henry Mode kid into a location.
    rom.write_int32s(0x798CF8, [0x01D90000, 0x00000000, 0x000C0000])
    rom.write_byte(0x796D4F, 0x87)

    # Move the following locations that have flags shared with other locations to their own flags.
    rom.write_int16(0x792A48, 0x0085)  # Archives Garden Key
    rom.write_int16(0xAAA, 0x0086, 280)  # Mary's Copper Key
    rom.write_int16(0xAE2, 0x0086, 280)
    rom.write_int16(0xB12, 0x0086, 280)

    # Write "Z + R + START" over the Special1 description.
    rom.write_bytes(0x3B7C, cvlod_string_to_bytes("Z + R + START"), 327)
    # Write the new Villa fountain puzzle order both in the code and Oldrey's Diary's description.
    rom.write_bytes(0x4780, cvlod_string_to_bytes(f"{villa_fountain_order[0]} {villa_fountain_order[1]} "
                                                  f"{villa_fountain_order[2]} {villa_fountain_order[3]}      "), 327)
    rom.write_byte(0x173, fountain_letters_to_numbers[villa_fountain_order[0]], 373)
    rom.write_byte(0x16B, fountain_letters_to_numbers[villa_fountain_order[1]], 373)
    rom.write_byte(0x163, fountain_letters_to_numbers[villa_fountain_order[2]], 373)
    rom.write_byte(0x143, fountain_letters_to_numbers[villa_fountain_order[3]], 373)

    for offset, item_id in offset_data.items():
        if item_id <= 0xFF:
            rom.write_byte(offset, item_id)
        elif item_id <= 0xFFFF:
            rom.write_int16(offset, item_id)
        elif item_id <= 0xFFFFFF:
            rom.write_int24(offset, item_id)
        else:
            rom.write_int32(offset, item_id)

    # Extract the item models file, decompress it, append the AP icons, compress it back, re-insert it.
    # items_file = lzkn64.decompress_buffer(rom.read_bytes(0x9C5310, 0x3D28))
    # compressed_file = lzkn64.compress_buffer(items_file[0:0x69B6] + pkgutil.get_data(__name__, "data/ap_icons.bin"))
    # rom.write_bytes(0xBB2D88, compressed_file)
    # Update the items' Nisitenma-Ichigo table entry to point to the new file's start and end addresses in the ROM.
    # rom.write_int32s(0x95F04, [0x80BB2D88, 0x00BB2D88 + len(compressed_file)])
    # Update the items' decompressed file size tables with the new file's decompressed file size.
    # rom.write_int16(0x95706, 0x7BF0)
    # rom.write_int16(0x104CCE, 0x7BF0)
    # Update the Wooden Stake and Roses' item appearance settings table to point to the Archipelago item graphics.
    # rom.write_int16(0xEE5BA, 0x7B38)
    # rom.write_int16(0xEE5CA, 0x7280)
    # Change the items' sizes. The progression one will be larger than the non-progression one.
    # rom.write_int32(0xEE5BC, 0x3FF00000)
    # rom.write_int32(0xEE5CC, 0x3FA00000)

    # Write the slot name
    # rom.write_bytes(0xBFBFE0, slot_name)

    # Write the specified window colors
    rom.write_byte(0x8881A, options.window_color_r.value << 4)
    rom.write_byte(0x8881B, options.window_color_g.value << 4)
    rom.write_byte(0x8881E, options.window_color_b.value << 4)
    rom.write_byte(0x8881F, options.window_color_a.value << 4)

    # Write the item/player names for other game items
    for loc in active_locations:
        if loc.address is not None and get_location_info(loc.name, "type") != "shop":
            # Truncate the item name if it's above 67 characters in length.
            item_name = loc.item.name
            #if len(loc.item.name) > 67:
            #    item_name = loc.item.name[0x00:0x68]

            # Make Mary say what her item is so players can then decide if Henry is worth saving or not.
            if loc.name == lname.villala_mary:

                mary_text = "Save Henry, and I will "
                if loc.item.player == player:
                    mary_text += f"give you this {item_name}."
                else:
                    mary_text += f"send this {item_name} to {multiworld.get_player_name(loc.item.player)}."
                mary_text += "\nGood luck out there!"

                mary_text = cvlod_text_wrap(mary_text, 254)

                rom.write_bytes(0x78EAE0, cvlod_string_to_bytes(mary_text[0] + (" " * (598 - len(mary_text))),
                                                                append_end=False))

    # if loc.item.player != player:
    #        inject_address = 0xBB7164 + (256 * (loc.address & 0xFFF))
    #        wrapped_name, num_lines = cvlod_text_wrap(item_name + "\nfor " + multiworld.get_player_name(
    #            loc.item.player), 96)
    # rom.write_bytes(inject_address, get_item_text_color(loc) + cvlod_string_to_bytes(wrapped_name))
    # rom.write_byte(inject_address + 255, num_lines)

    # Everything relating to loading the other game items text
    # rom.write_int32(0xA8D8C, 0x080FF88F)  # J   0x803FE23C
    # rom.write_int32(0xBEA98, 0x0C0FF8B4)  # JAL 0x803FE2D0
    # rom.write_int32(0xBEAB0, 0x0C0FF8BD)  # JAL 0x803FE2F8
    # rom.write_int32(0xBEACC, 0x0C0FF8C5)  # JAL 0x803FE314
    # rom.write_int32s(0xBFE23C, patches.multiworld_item_name_loader)
    # rom.write_bytes(0x10F188, [0x00 for _ in range(264)])
    # rom.write_bytes(0x10F298, [0x00 for _ in range(264)])

    rom.reinsert_all_files()


class CVLoDDeltaPatch(APDeltaPatch):
    hash = CVLODUSHASH
    patch_file_ending: str = ".apcvlod"
    result_file_ending: str = ".z64"

    game = "Castlevania Legacy of Darkness"

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if CVLODUSHASH != basemd5.hexdigest():
            raise Exception("Supplied Base Rom does not match known MD5 for Castlevania: Legacy of Darkness USA."
                            "Get the correct game and version, then dump it.")
        setattr(get_base_rom_bytes, "base_rom_bytes", base_rom_bytes)
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    if not file_name:
        file_name = get_settings()["cvlod_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name
