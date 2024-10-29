import json
import base64
import Utils

from BaseClasses import Location
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
from typing import List, Dict, Tuple, Union, Iterable, Collection, TYPE_CHECKING

import hashlib
import os
import pkgutil

from . import lzkn64
from .data import patches, ni_files
from .stages import get_stage_info
from .text import cv64_string_to_bytearray, cv64_text_truncate, cv64_text_wrap
from .aesthetics import renon_item_dialogue, get_item_text_color
from .locations import get_location_info
from .options import CharacterStages, VincentFightCondition, RenonFightCondition, PostBehemothBoss, RoomOfClocksBoss, \
    BadEndingCondition, DeathLink, DraculasCondition, InvisibleItems, Countdown, PantherDash
from settings import get_settings

if TYPE_CHECKING:
    from . import CV64World

CV64_US_10_HASH = "1cc5cf3b4d29d8c3ade957648b529dc1"

warp_map_offsets = [0xADF67, 0xADF77, 0xADF87, 0xADF97, 0xADFA7, 0xADFBB, 0xADFCB, 0xADFDF]


class RomData:
    main_file: bytearray
    decompressed_files: Dict[int, bytearray]
    compressed_files: Dict[int, bytearray]

    ni_table_start: int
    ni_file_buffers_start: int
    decomp_file_sizes_table_start: int
    number_of_ni_files: int

    def __init__(self, file: bytes) -> None:
        self.main_file = bytearray(file)

        self.decompressed_files = {}
        self.compressed_files = {}

        # Seek the "Nisitenma-Ichigo" string in the ROM indicating where the table containing the compressed file start
        # and end offsets begins.
        nisitenma_ichigo_start = self.main_file.find("Nisitenma-Ichigo".encode("utf-8"))
        # If the "Nisitenma-Ichigo" string is nowhere to be found, raise an exception.
        if nisitenma_ichigo_start == -1:
            raise Exception("Nisitenma-Ichigo string not found.")

        self.ni_table_start = nisitenma_ichigo_start + 16
        self.ni_file_buffers_start = int.from_bytes(self.main_file[self.ni_table_start: self.ni_table_start + 4],
                                                    "big") & 0xFFFFFFF

        # Figure out how many Nisitenma-Ichigo files there are alongside grabbing them out of the ROM.
        self.number_of_ni_files = 1
        while True:
            ni_table_entry_start = self.ni_table_start + ((self.number_of_ni_files - 1) * 8)
            file_start_addr = int.from_bytes(self.read_bytes(ni_table_entry_start, 4), "big") & 0xFFFFFFF
            # If the file start address is 0, we've reached the end of the NI table. In which case, end the loop.
            if not file_start_addr:
                break
            # Calculate the compressed file's size and use that to read it out of the ROM.
            file_size = (int.from_bytes(self.read_bytes(ni_table_entry_start + 4, 4), "big") & 0xFFFFFFF) - \
                file_start_addr
            self.compressed_files[self.number_of_ni_files] = self.read_bytes(file_start_addr, file_size)
            self.number_of_ni_files += 1

        # Figure out where the decompressed file sizes table starts by going backwards the number of NI files from the
        # start of "Nisitenma-Ichigo".
        self.decomp_file_sizes_table_start = nisitenma_ichigo_start - 4 - (8 * self.number_of_ni_files)

    def read_byte(self, address: int) -> int:
        return self.main_file[address]

    def read_bytes(self, start_address: int, length: int) -> bytearray:
        return self.main_file[start_address:start_address + length]

    def write_byte(self, address: int, value: int, file_num: int = 0) -> None:
        if file_num == 0:
            self.main_file[address] = value
        else:
            if file_num not in self.decompressed_files:
                self.decompress_file(file_num)
            self.decompressed_files[file_num][address] = value

    def write_bytes(self, start_address: int, values: Collection[int], file_num: int = 0) -> None:
        if file_num == 0:
            self.main_file[start_address:start_address + len(values)] = values
        else:
            if file_num not in self.decompressed_files:
                self.decompress_file(file_num)
            self.decompressed_files[file_num][start_address:start_address + len(values)] = values

    def write_int16(self, address: int, value: int, file_num: int = 0) -> None:
        value = value & 0xFFFF
        self.write_bytes(address, [(value >> 8) & 0xFF, value & 0xFF], file_num)

    def write_int16s(self, start_address: int, values: List[int], file_num: int = 0) -> None:
        for i, value in enumerate(values):
            self.write_int16(start_address + (i * 2), value, file_num)

    def write_int24(self, address: int, value: int, file_num: int = 0) -> None:
        value = value & 0xFFFFFF
        self.write_bytes(address, [(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF], file_num)

    def write_int24s(self, start_address: int, values: List[int], file_num: int = 0) -> None:
        for i, value in enumerate(values):
            self.write_int24(start_address + (i * 3), value, file_num)

    def write_int32(self, address: int, value: int, file_num: int = 0) -> None:
        value = value & 0xFFFFFFFF
        self.write_bytes(address, [(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF],
                         file_num)

    def write_int32s(self, start_address: int, values: List[int], file_num: int = 0) -> None:
        for i, value in enumerate(values):
            self.write_int32(start_address + (i * 4), value, file_num)

    def decompress_file(self, file_num: int) -> None:
        self.decompressed_files[file_num] = lzkn64.decompress_buffer(self.compressed_files[file_num])

    def compress_file(self, file_num: int) -> None:
        self.compressed_files[file_num] = bytearray(lzkn64.compress_buffer(self.decompressed_files[file_num]))

    def get_bytes(self) -> bytes:
        # Reinsert all Nisitenma-Ichigo files, both modified and unmodified, in the order they should be.
        displacement = 0
        for i in range(1, self.number_of_ni_files):
            # Re-compress the file if decompressed and update the decompressed sizes table
            if i in self.decompressed_files:
                self.compress_file(i)
                self.write_int24(self.decomp_file_sizes_table_start + (i * 8) + 5, len(self.decompressed_files[i]))

            start_addr = self.ni_file_buffers_start + displacement
            end_addr = start_addr + len(self.compressed_files[i])
            displacement += len(self.compressed_files[i])

            self.write_bytes(start_addr, self.compressed_files[i])

            # Update the Nisitenma-Ichigo table
            self.write_int24(self.ni_table_start + ((i - 1) * 8) + 1, start_addr)
            self.write_int24(self.ni_table_start + ((i - 1) * 8) + 5, end_addr)

        return bytes(self.main_file)


class CV64PatchExtensions(APPatchExtension):
    game = "Castlevania 64"

    @staticmethod
    def apply_patches(caller: APProcedurePatch, rom: bytes, options_file: str, ni_edits: str) -> bytes:
        rom_data = RomData(rom)
        options = json.loads(caller.get_file(options_file).decode("utf-8"))
        ni_edits = json.loads(caller.get_file(ni_edits).decode("utf-8"))

        # NOP out the CRC BNEs.
        rom_data.write_int32(0x66C, 0x00000000)
        rom_data.write_int32(0x678, 0x00000000)

        # Always offer Hard Mode on file creation.
        rom_data.write_int32(0xC8810, 0x240A0100)  # ADDIU	T2, R0, 0x0100

        # Allow using the alternate costumes from the start.
        rom_data.write_int32(0xC78, 0x3C0A8000, ni_files.OVL_PLAYER_SELECT)  # LUI  T2, 0x8000
        rom_data.write_int16(0xCA0, 0x240E, ni_files.OVL_PLAYER_SELECT)
        rom_data.write_int16(0xCDC, 0x240F, ni_files.OVL_PLAYER_SELECT)
        # Allow Hard Mode from the start without a controller pak.
        rom_data.write_int16(0x168, 0x24, ni_files.OVL_PLAYER_SELECT)

        # Disable the Easy Mode cutoff point at Castle Center's elevator.
        rom_data.write_int32(0xD9E18, 0x240D0000)  # ADDIU	T5, R0, 0x0000

        # Disable the Forest intro cutscene being played by the intro narration cutscene
        # and make it possible to change what starting map the intro narration cutscene sends you to.
        rom_data.write_byte(0x11B7, 0x00, ni_files.OVL_INTRO_NARRATION_CS)
        rom_data.write_byte(0x11C9, 0x40, ni_files.OVL_INTRO_NARRATION_CS)
        rom_data.write_byte(0x11D9, 0x4C, ni_files.OVL_INTRO_NARRATION_CS)
        # Disable the Castle Wall intro cutscene being played by the Forest ending cutscene and have it store a spawn
        # position ID instead.
        rom_data.write_byte(0xD6F, 0x00, ni_files.OVL_DRAWBRIDGE_LOWERS_CS)
        rom_data.write_int32(0xD88, 0xA058642B, ni_files.OVL_DRAWBRIDGE_LOWERS_CS)  # SB T8, 0x642B (V0)
        rom_data.write_int32(0xD98, 0x00000000, ni_files.OVL_DRAWBRIDGE_LOWERS_CS)  # NOP
        # Disable the Villa intro cutscene being set to play upon touching the Castle Wall end loading zone.
        rom_data.write_byte(0x109F8F, 0x00)

        # Prevent the Forest end cutscene flag from setting, so it can be triggered indefinitely.
        rom_data.write_byte(0xEEA51, 0x01)

        # Hack to make the Forest, CW and Villa intro cutscenes play at the start of their levels no matter what map
        # the player came in from.
        rom_data.write_int32(0x97244, 0x803FDD60)
        rom_data.write_int32s(0xBFDD60, patches.forest_cw_villa_intro_cs_player)

        # Make changing the map ID to 0xFF reset the map. Helpful to work around a bug wherein the camera gets stuck
        # when entering a loading zone that doesn't change the map.
        rom_data.write_int32s(0x197B0, [0x0C0FF7E6,  # JAL   0x803FDF98
                                        0x24840008])  # ADDIU A0, A0, 0x0008
        rom_data.write_int32s(0xBFDF98, patches.map_id_refresher)

        # Enable swapping characters when loading into a map by holding L.
        rom_data.write_int32(0x97294, 0x803FDFC4)
        rom_data.write_int32(0x19710, 0x080FF80E)  # J 0x803FE038
        rom_data.write_int32s(0xBFDFC4, patches.character_changer)

        # Villa coffin time-of-day hack
        rom_data.write_byte(0xD9D83, 0x74)
        rom_data.write_int32(0xD9D84, 0x080FF14D)  # J 0x803FC534
        rom_data.write_int32s(0xBFC534, patches.coffin_time_checker)

        # Fix both Castle Center elevator bridges for both characters unless enabling only one character's stages.
        # At which point one bridge will be always broken and one always repaired instead.
        if options["character_stages"] == CharacterStages.option_reinhardt_only:
            rom_data.write_int32(0x6CEAA0, 0x240B0000)  # ADDIU T3, R0, 0x0000
        elif options["character_stages"] == CharacterStages.option_carrie_only:
            rom_data.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
        else:
            rom_data.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
            rom_data.write_int32(0x6CEAA4, 0x240D0001)  # ADDIU T5, R0, 0x0001

        # Were-bull arena flag hack
        rom_data.write_int32(0x6E38F0, 0x0C0FF157)  # JAL   0x803FC55C
        rom_data.write_int32s(0xBFC55C, patches.werebull_flag_unsetter)
        rom_data.write_int32(0xA949C, 0x0C0FF380)  # JAL   0x803FCE00
        rom_data.write_int32s(0xBFCE00, patches.werebull_flag_pickup_setter)

        # Enable being able to carry multiple Special jewels, Nitros, and Mandragoras simultaneously.
        rom_data.write_int32(0xBF1F4, 0x3C038039)  # LUI V1, 0x8039
        # Special1
        rom_data.write_int32(0xBF210, 0x80659C4B)  # LB A1, 0x9C4B (V1)
        rom_data.write_int32(0xBF214, 0x24A50001)  # ADDIU A1, A1, 0x0001
        rom_data.write_int32(0xBF21C, 0xA0659C4B)  # SB A1, 0x9C4B (V1)
        # Special2
        rom_data.write_int32(0xBF230, 0x80659C4C)  # LB A1, 0x9C4C (V1)
        rom_data.write_int32(0xBF234, 0x24A50001)  # ADDIU A1, A1, 0x0001
        rom_data.write_int32(0xbf23C, 0xA0659C4C)  # SB A1, 0x9C4C (V1)
        # Magical Nitro
        rom_data.write_int32(0xBF360, 0x10000004)  # B 0x8013C184
        rom_data.write_int32(0xBF378, 0x25E50001)  # ADDIU A1, T7, 0x0001
        rom_data.write_int32(0xBF37C, 0x10000003)  # B 0x8013C19C
        # Mandragora
        rom_data.write_int32(0xBF3A8, 0x10000004)  # B 0x8013C1CC
        rom_data.write_int32(0xBF3C0, 0x25050001)  # ADDIU A1, T0, 0x0001
        rom_data.write_int32(0xBF3C4, 0x10000003)  # B 0x8013C1E4

        # Give PowerUps their Legacy of Darkness behavior when attempting to pick up more than two
        # (it won't power you up further, but it will clear it and set the pickup flag).
        rom_data.write_int16(0xA9624, 0x1000)
        rom_data.write_int32(0xA9730, 0x24090000)  # ADDIU	T1, R0, 0x0000
        rom_data.write_int32(0xBF2FC, 0x080FF16D)  # J	0x803FC5B4
        rom_data.write_int32(0xBF300, 0x00000000)  # NOP
        rom_data.write_int32s(0xBFC5B4, patches.give_powerup_stopper)

        # Rename the Wooden Stake and Rose to "You are a FOOL!"
        rom_data.write_bytes(0xEFE34,
                             bytearray([0xFF, 0xFF, 0xA2, 0x0B]) + cv64_string_to_bytearray("You are a FOOL!",
                                                                                            append_end=False))
        # Capitalize the "k" in "Archives key" to be consistent with...literally every other key name!
        rom_data.write_byte(0xEFF21, 0x2D)

        # Skip the "There is a white jewel" text so checking one saves the game instantly.
        rom_data.write_int32s(0xEFC72, [0x00020002 for _ in range(37)])
        rom_data.write_int32(0xA8FC0, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Skip the yes/no prompts when activating things.
        rom_data.write_int32s(0xBFDACC, patches.map_text_redirector)
        rom_data.write_int32(0xA9084, 0x24020001)  # ADDIU V0, R0, 0x0001
        rom_data.write_int32(0xBEBE8, 0x0C0FF6B4)  # JAL   0x803FDAD0
        # Skip Vincent and Heinrich's mandatory-for-a-check dialogue
        rom_data.write_int32(0xBED9C, 0x0C0FF6DA)  # JAL   0x803FDB68
        # Skip the long yes/no prompt in the CC planetarium to set the pieces.
        rom_data.write_int32(0x1F4, 0x24030001, ni_files.OVL_CC_LIBRARY_PUZZLE_TEXTBOX)  # ADDIU  V1, R0, 0x0001
        # Skip the yes/no prompt to activate the CC elevator.
        rom_data.write_int32(0x294, 0x24020001, ni_files.OVL_CC_ELEVATOR_TEXTBOX)  # ADDIU  V0, R0, 0x0001
        # Skip the yes/no prompts to set Nitro/Mandragora at both walls.
        rom_data.write_int32(0x4A0, 0x24030001, ni_files.OVL_INGREDIENT_SET_TEXTBOX)  # ADDIU  V1, R0, 0x0001

        # Custom message if you try checking the downstairs CC crack before removing the seal.
        rom_data.write_bytes(0xBFDBAC, cv64_string_to_bytearray("The Furious Nerd Curse\n"
                                                                "prevents you from setting\n"
                                                                "anything until the seal\n"
                                                                "is removed!", True))

        # Special1/2 descriptions redirection.
        rom_data.write_int16(0x1D1E, 0x8040, ni_files.OVL_PAUSE_MENU)
        rom_data.write_int16(0x1D22, 0xDD20, ni_files.OVL_PAUSE_MENU)
        rom_data.write_int32s(0xBFDD20, patches.special_descriptions_redirector)

        # Change the Stage Select menu options.
        rom_data.write_int32s(0xADF64, patches.warp_menu_rewrite)
        rom_data.write_int32s(0x10E0C8, patches.warp_pointer_table)

        # Play the "teleportation" sound effect when teleporting.
        rom_data.write_int32s(0xAE088, [0x08004FAB,  # J 0x80013EAC
                                        0x2404019E])  # ADDIU A0, R0, 0x019E

        # Prevent saving the game when there's a boss health bar on-screen (possible in Underground Waterway if you turn
        # the first waterfall off before triggering the triple lizard fight).
        rom_data.write_int32(0xA99AC, 0x080FF0B8)  # J 0x803FC2E0
        rom_data.write_int32s(0xBFC2E0, patches.boss_save_stopper)

        # Disable or guarantee vampire Vincent's fight.
        if options["vincent_fight_condition"] == VincentFightCondition.option_never:
            rom_data.write_int32(0xAACC0, 0x24010001)  # ADDIU AT, R0, 0x0001
            rom_data.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000
        elif options["vincent_fight_condition"] == VincentFightCondition.option_always:
            rom_data.write_int32(0xAACE0, 0x24180010)  # ADDIU T8, R0, 0x0010
        else:
            rom_data.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000

        # Disable or guarantee Renon's fight.
        rom_data.write_int32(0xAACB4, 0x080FF1A4)  # J 0x803FC690
        if options["renon_fight_condition"] == RenonFightCondition.option_never:
            rom_data.write_byte(0x223, 0x00, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x3C7, 0x00, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x5AB, 0x00, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x813, 0xB8, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x18C7, 0xB8, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x1A43, 0x00, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
        elif options["renon_fight_condition"] == RenonFightCondition.option_always:
            rom_data.write_byte(0x223, 0x0C, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x3C7, 0x0C, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x5AB, 0x0C, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x813, 0xC4, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x18C7, 0xC4, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_byte(0x1A43, 0x0C, ni_files.OVL_RENONS_DEPARTURE_CS)
            rom_data.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
        else:
            rom_data.write_int32s(0xBFC690, patches.renon_cutscene_checker)

        # NOP the Easy Mode check when buying a thing from Renon, so his fight can be triggered even on this mode.
        rom_data.write_int32(0xBD8B4, 0x00000000)

        # Disable or guarantee the Bad Ending.
        if options["bad_ending_condition"] == BadEndingCondition.option_never:
            rom_data.write_int32(0xB7D8, 0x3C0A0000, ni_files.OVL_FAKE_DRACULA)  # LUI  T2, 0x0000
        elif options["bad_ending_condition"] == BadEndingCondition.option_always:
            rom_data.write_int32(0xB7D8, 0x3C0A0040, ni_files.OVL_FAKE_DRACULA)  # LUI  T2, 0x0040

        # Play Castle Keep's song if teleporting in front of Dracula's door outside the escape sequence.
        rom_data.write_int32(0x6E937C, 0x080FF12E)  # J 0x803FC4B8
        rom_data.write_int32s(0xBFC4B8, patches.ck_door_music_player)

        # Increase the item capacity to 100 if "Increase Item Limit" is turned on.
        if options["increase_item_limit"]:
            rom_data.write_byte(0xBF30B, 0x63)  # Most items
            rom_data.write_byte(0xBF3F7, 0x63)  # Sun/Moon cards
        rom_data.write_byte(0xBF353, 0x64)  # Keys (increase regardless)

        # Change the item healing values if "Nerf Healing" is turned on.
        if options["nerf_healing_items"]:
            rom_data.write_byte(0x2F72, 0x50, ni_files.OVL_PAUSE_MENU)  # Healing kit   (100 -> 80)
            rom_data.write_byte(0x2F75, 0x32, ni_files.OVL_PAUSE_MENU)  # Roast beef    ( 80 -> 50)
            rom_data.write_byte(0x2F78, 0x19, ni_files.OVL_PAUSE_MENU)  # Roast chicken ( 50 -> 25)

        # Disable loading zone healing if it was turned off.
        if not options["loading_zone_heals"]:
            # Skip all loading zone checks.
            rom_data.write_byte(0xD99A5, 0x00)
            # Disable the free heal from King Skeleton by reading the unused magic meter value.
            rom_data.write_byte(0x34DF, 0x40, ni_files.OVL_KING_SKELETON)

        # Disable spinning on the Special1 and 2 pickup models so colorblind people can more easily distinguish them
        # from the other jewels.
        rom_data.write_byte(0xEE4F5, 0x00)  # Special1
        rom_data.write_byte(0xEE505, 0x00)  # Special2
        # Make the Special2 the same size as a Red jewel(L) to further distinguish it from the Special1.
        rom_data.write_int32(0xEE4FC, 0x3FA66666)

        # Change some shelf decoration Nitros and Mandragoras into actual items.
        rom_data.write_int16(0x26980, 0xFFFC, ni_files.MAP_CC_BASEMENT)
        rom_data.write_int16(0x26990, 0xFFFC, ni_files.MAP_CC_BASEMENT)
        rom_data.write_int16s(0x26986, [0x0027, 0x0001, 0x4000], ni_files.MAP_CC_BASEMENT)
        rom_data.write_int16s(0x26996, [0x0027, 0x0001, 0x8000], ni_files.MAP_CC_BASEMENT)
        rom_data.write_byte(0x306F1, 0xC0, ni_files.MAP_CC_INVENTIONS)
        rom_data.write_byte(0x30721, 0xCE, ni_files.MAP_CC_INVENTIONS)
        rom_data.write_int16s(0x306F6, [0x0027, 0x0001, 0x8000, 0x0000], ni_files.MAP_CC_INVENTIONS)
        rom_data.write_int16s(0x30726, [0x0027, 0x0001, 0x0400, 0xFF05], ni_files.MAP_CC_INVENTIONS)

        # Prevent taking Nitro or Mandragora through their shelf text.
        rom_data.write_int32(0x194, 0x24020000, ni_files.OVL_TAKE_NITRO_TEXTBOX)  # ADDIU V0, R0, 0x0000
        rom_data.write_int32(0x194, 0x24020000, ni_files.OVL_TAKE_MANDRAGORA_TEXTBOX)  # ADDIU V0, R0, 0x0000

        # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes.
        rom_data.write_byte(0xBF, 0x03, ni_files.OVL_VAMPIRES)

        # Prevent throwing Nitro in the Hazardous Materials Disposals.
        rom_data.write_int32(0x1D4, 0x24020001, ni_files.OVL_NITRO_DISPOSAL_TEXTBOX)  # ADDIU V0, R0, 0x0001

        # Allow placing both bomb components at a cracked wall at once while having multiple copies of each, prevent
        # placing them at the downstairs crack altogether until the seal is removed, and enable placing both in one
        # interaction.
        rom_data.write_byte(0x30F, 0x40, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int16(0x312, 0xC338, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_byte(0x33F, 0x40, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int16(0x342, 0xC338, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_byte(0x3E3, 0x40, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int16(0x3E6, 0xC3D4, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_byte(0x39F, 0x40, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int16(0x3A2, 0xC38C, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_byte(0x3CB, 0x40, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int16(0x3CE, 0xC38C, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_byte(0x5CF, 0x40, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int16(0x5D2, 0xE074, ni_files.OVL_INGREDIENT_SET_TEXTBOX)
        rom_data.write_int32s(0xBFC338, patches.double_component_checker)
        rom_data.write_int32s(0xBFC3D4, patches.downstairs_seal_checker)
        rom_data.write_int32s(0xBFE074, patches.mandragora_with_nitro_setter)

        # Disable the rapid flashing effect in the CC planetarium cutscene to ensure it won't trigger seizures.
        # TODO: Make this an option.
        rom_data.write_int32(0xC5C, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xCD0, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xC64, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xC74, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xC80, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xC88, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xC90, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xC9C, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xCB4, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)
        rom_data.write_int32(0xCC8, 0x00000000, ni_files.OVL_CC_PLANETARIUM_SOLVED_CS)

        # Enable the Game Over screen's "Continue" menu starting the cursor on whichever checkpoint is more recent.
        rom_data.write_int32(0xB4DDC, 0x0C060D58)  # JAL 0x80183560
        rom_data.write_int32s(0x106750, patches.continue_cursor_start_checker)
        rom_data.write_int32(0x1C444, 0x080FF08A)  # J   0x803FC228
        rom_data.write_int32(0x1C2A0, 0x080FF08A)  # J   0x803FC228
        rom_data.write_int32s(0xBFC228, patches.savepoint_cursor_updater)
        rom_data.write_int32(0x1C2D0, 0x080FF094)  # J   0x803FC250
        rom_data.write_int32s(0xBFC250, patches.stage_start_cursor_updater)
        rom_data.write_byte(0x1DE9, 0xFF, ni_files.OVL_GAME_OVER_SCREEN)

        # Make the Special1 and 2 play sounds when you reach milestones in collecting them.
        rom_data.write_int32s(0xBFDA50, patches.special_sound_notifs)
        rom_data.write_int32(0xBF240, 0x080FF694)  # J 0x803FDA50
        rom_data.write_int32(0xBF220, 0x080FF69E)  # J 0x803FDA78

        # Add data for White Jewel #22 (the new Duel Tower savepoint) at the end of the White Jewel ID data list.
        rom_data.write_int16s(0x104AC8, [0x0000, 0x0006,
                                         0x0013, 0x0015])

        # Take the Contract in Waterway off of its 00400000 bitflag.
        rom_data.write_byte(0x1CC5B, 0x00, ni_files.MAP_WATERWAY)

        # Put each Lizard Locker item on its own flag.
        rom_data.write_int16(0x2BA7A, 0x1000, ni_files.MAP_CC_FACTORY_FLOOR)
        rom_data.write_int16(0x2BA8A, 0x2000, ni_files.MAP_CC_FACTORY_FLOOR)
        rom_data.write_int16(0x2BAAA, 0x0400, ni_files.MAP_CC_FACTORY_FLOOR)
        rom_data.write_int16(0x2BA9A, 0x0800, ni_files.MAP_CC_FACTORY_FLOOR)
        rom_data.write_int16(0x2BABA, 0x0200, ni_files.MAP_CC_FACTORY_FLOOR)
        rom_data.write_int16(0x2BACA, 0x0100, ni_files.MAP_CC_FACTORY_FLOOR)

        # Spawn coordinates list extension.
        rom_data.write_int32(0xD5BF4, 0x080FF103)  # J	0x803FC40C
        rom_data.write_int32s(0xBFC40C, patches.spawn_coordinates_extension)
        rom_data.write_int32s(0x108A5E, patches.waterway_end_coordinates)

        # Add an actor in Duel Tower (replaces one of the flames on one of the billboarding pillars) for
        # White Jewel number 0x22.
        rom_data.write_int16s(0x15EA0, [0x00B9, 0x012B, 0xFE2A, 0x0027, 0x0001, 0x0000, 0x0022, 0x0100],
                              ni_files.MAP_DUEL)

        # Fix a vanilla issue wherein saving in a character-exclusive stage as the other character would incorrectly
        # display the name of that character's equivalent stage on the save file instead of the one they're actually in.
        rom_data.write_byte(0xC9FE3, 0xD4)
        rom_data.write_byte(0xCA055, 0x08)
        rom_data.write_byte(0xCA066, 0x40)
        rom_data.write_int32(0xCA068, 0x860C17D0)  # LH T4, 0x17D0 (S0)
        rom_data.write_byte(0xCA06D, 0x08)
        rom_data.write_byte(0x104A31, 0x01)
        rom_data.write_byte(0x104A39, 0x01)
        rom_data.write_byte(0x104A89, 0x01)
        rom_data.write_byte(0x104A91, 0x01)
        rom_data.write_byte(0x104A99, 0x01)
        rom_data.write_byte(0x104AA1, 0x01)

        # Make the Castle Center top elevator check for the bottom elevator switch being active before activating.
        rom_data.write_int32(0x6CF0A0, 0x0C0FF0B0)  # JAL 0x803FC2C0
        rom_data.write_int32s(0xBFC2C0, patches.elevator_flag_checker)

        # Disable time restrictions.
        if options["disable_time_restrictions"]:
            # Fountain
            rom_data.write_int32(0x6C2340, 0x00000000)  # NOP
            rom_data.write_int32(0x6C257C, 0x10000023)  # B [forward 0x23]
            # Rosa
            rom_data.write_byte(0xEEAAB, 0x00)
            rom_data.write_byte(0xEEAAD, 0x18)
            # Moon doors
            rom_data.write_int32(0xDC3E0, 0x00000000)  # NOP
            rom_data.write_int32(0xDC3E8, 0x00000000)  # NOP
            # Sun doors
            rom_data.write_int32(0xDC410, 0x00000000)  # NOP
            rom_data.write_int32(0xDC418, 0x00000000)  # NOP

        # Custom data-loading code.
        rom_data.write_int32(0x6B5028, 0x08060D70)  # J 0x801835D0
        rom_data.write_int32s(0x1067B0, patches.custom_code_loader)

        # Custom remote item rewarding and DeathLink receiving code.
        rom_data.write_int32(0x19B98, 0x080FF000)  # J 0x803FC000
        rom_data.write_int32s(0xBFC000, patches.remote_item_giver)
        rom_data.write_int32s(0xBFE190, patches.subweapon_surface_checker)

        # Make received DeathLinks blow you to smithereens instead of kill you normally.
        if options["death_link"] == DeathLink.option_explosive:
            rom_data.write_int32(0x27A70, 0x10000008)  # B [forward 0x08]
            rom_data.write_int32s(0xBFC0D0, patches.deathlink_nitro_edition)

        # Set the DeathLink ROM flag if it's on at all.
        if options["death_link"]:
            rom_data.write_byte(0xBFBFDE, 0x01)

        # DeathLink counter decrementer code.
        rom_data.write_int32(0x1C340, 0x080FF8F0)  # J 0x803FE3C0
        rom_data.write_int32s(0xBFE3C0, patches.deathlink_counter_decrementer)
        rom_data.write_int32(0x25B6C, 0x080FFA5E)  # J 0x803FE978
        rom_data.write_int32s(0xBFE978, patches.launch_fall_killer)

        # Death flag un-setter on "Beginning of stage" state overwrite code.
        rom_data.write_int32(0x1C2B0, 0x080FF047)  # J 0x803FC11C
        rom_data.write_int32s(0xBFC11C, patches.death_flag_unsetter)

        # Warp menu-opening code.
        rom_data.write_int32(0xB9BA8, 0x080FF099)  # J	0x803FC264
        rom_data.write_int32s(0xBFC264, patches.warp_menu_opener)

        # NPC item textbox hack. TODO: Make this not jank
        rom_data.write_int32(0xBF1DC, 0x080FF904)  # J 0x803FE410
        rom_data.write_int32(0xBF1E0, 0x27BDFFE0)  # ADDIU SP, SP, -0x20
        rom_data.write_int32s(0xBFE410, patches.npc_item_hack)

        # Sub-weapon check function hook.
        rom_data.write_int32(0xBF32C, 0x00000000)  # NOP
        rom_data.write_int32(0xBF330, 0x080FF05E)  # J	0x803FC178
        rom_data.write_int32s(0xBFC178, patches.give_subweapon_stopper)

        # Warp menu Special1 restriction.
        rom_data.write_int32(0xADD68, 0x0C04AB12)  # JAL 0x8012AC48
        rom_data.write_int32s(0xADE28, patches.stage_select_overwrite)
        rom_data.write_byte(0xADE47, options["s1s_per_warp"])

        # Dracula's door text pointer hijack.
        rom_data.write_int32(0xD69F0, 0x080FF141)  # J 0x803FC504
        rom_data.write_int32s(0xBFC504, patches.dracula_door_text_redirector)

        # Dracula's chamber condition.
        rom_data.write_int32(0xE2FDC, 0x0804AB25)  # J 0x8012AC78
        rom_data.write_int32s(0xADE84, patches.special_goal_checker)
        rom_data.write_bytes(0xBFCC48,
                             [0xA0, 0x00, 0xFF, 0xFF, 0xA0, 0x01, 0xFF, 0xFF, 0xA0, 0x02, 0xFF, 0xFF, 0xA0, 0x03, 0xFF,
                              0xFF, 0xA0, 0x04, 0xFF, 0xFF, 0xA0, 0x05, 0xFF, 0xFF, 0xA0, 0x06, 0xFF, 0xFF, 0xA0, 0x07,
                              0xFF, 0xFF, 0xA0, 0x08, 0xFF, 0xFF, 0xA0, 0x09])
        if options["draculas_condition"] == DraculasCondition.option_crystal:
            rom_data.write_int32(0x6C8A54, 0x0C0FF0C1)  # JAL 0x803FC304
            rom_data.write_int32s(0xBFC304, patches.crystal_special2_giver)
            rom_data.write_bytes(0xBFCC6E, cv64_string_to_bytearray(f"It won't budge!\n"
                                                                    f"You'll need the power\n"
                                                                    f"of the basement crystal\n"
                                                                    f"to undo the seal.", True))
            special2_name = "Crystal "
            special2_text = "The crystal is on!\n" \
                            "Time to teach the old man\n" \
                            "a lesson!"
        elif options["draculas_condition"] == DraculasCondition.option_bosses:
            rom_data.write_int32(0xBBD50, 0x080FF18C)  # J	0x803FC630
            rom_data.write_int32s(0xBFC630, patches.boss_special2_giver)
            rom_data.write_int32s(0xBFC55C, patches.werebull_flag_unsetter_special2_electric_boogaloo)
            rom_data.write_bytes(0xBFCC6E, cv64_string_to_bytearray(f"It won't budge!\n"
                                                                    f"You'll need to defeat\n"
                                                                    f"{options['required_s2s']} powerful monsters\n"
                                                                    f"to undo the seal.", True))
            special2_name = "Trophy  "
            special2_text = f"Proof you killed a powerful\n" \
                            f"Night Creature. Earn {options['required_s2s']}/{options['total_s2s']}\n" \
                            f"to battle Dracula."
        elif options["draculas_condition"] == DraculasCondition.option_specials:
            special2_name = "Special2"
            rom_data.write_bytes(0xBFCC6E, cv64_string_to_bytearray(f"It won't budge!\n"
                                                                    f"You'll need to find\n"
                                                                    f"{options['required_s2s']} Special2 jewels\n"
                                                                    f"to undo the seal.", True))
            special2_text = f"Need {options['required_s2s']}/{options['total_s2s']} to kill Dracula.\n" \
                            f"Looking closely, you see...\n" \
                            f"a piece of him within?"
        else:
            rom_data.write_byte(0xADE8F, 0x00)
            special2_name = "Special2"
            special2_text = "If you're reading this,\n" \
                            "how did you get a Special2!?"
        rom_data.write_byte(0xADE8F, options["required_s2s"])
        # Change the Special2 name depending on the setting.
        rom_data.write_bytes(0xEFD4E, cv64_string_to_bytearray(special2_name))
        # Change the Special1 and 2 menu descriptions to tell you how many you need to unlock a warp and fight Dracula
        # respectively.
        special_text_bytes = cv64_string_to_bytearray(f"{options['s1s_per_warp']} per warp unlock.\n"
                                                      f"{options['total_special1s']} exist in total.\n"
                                                      f"Z + R + START to warp.") + cv64_string_to_bytearray(
            special2_text)
        rom_data.write_bytes(0xBFE53C, special_text_bytes)

        # On-the-fly actor data modifier hook TODO: Scrap every last bit of this, too!
        #rom_data.write_int32(0xEAB04, 0x080FF21E)  # J 0x803FC878
        #rom_data.write_int32s(0xBFC870, patches.map_data_modifiers)

        # Fix to make flags apply to freestanding invisible items properly.
        rom_data.write_int32(0xA84F8, 0x90CC0039)  # LBU T4, 0x0039 (A2)

        # Fix locked doors to check the key counters instead of their vanilla key locations' bitflags
        # Pickup flag check modifications:
        rom_data.write_int32(0x10B2D8, 0x00000002)  # Left Tower Door
        rom_data.write_int32(0x10B2F0, 0x00000003)  # Storeroom Door
        rom_data.write_int32(0x10B2FC, 0x00000001)  # Archives Door
        rom_data.write_int32(0x10B314, 0x00000004)  # Maze Gate
        rom_data.write_int32(0x10B350, 0x00000005)  # Copper Door
        rom_data.write_int32(0x10B3A4, 0x00000006)  # Torture Chamber Door
        rom_data.write_int32(0x10B3B0, 0x00000007)  # ToE Gate
        rom_data.write_int32(0x10B3BC, 0x00000008)  # Science Door1
        rom_data.write_int32(0x10B3C8, 0x00000009)  # Science Door2
        rom_data.write_int32(0x10B3D4, 0x0000000A)  # Science Door3
        rom_data.write_int32(0x6F0094, 0x0000000B)  # CT Door 1
        rom_data.write_int32(0x6F00A4, 0x0000000C)  # CT Door 2
        rom_data.write_int32(0x6F00B4, 0x0000000D)  # CT Door 3
        # Item counter decrement check modifications:
        rom_data.write_int32(0xEDA84, 0x00000001)  # Archives Door
        rom_data.write_int32(0xEDA8C, 0x00000002)  # Left Tower Door
        rom_data.write_int32(0xEDA94, 0x00000003)  # Storeroom Door
        rom_data.write_int32(0xEDA9C, 0x00000004)  # Maze Gate
        rom_data.write_int32(0xEDAA4, 0x00000005)  # Copper Door
        rom_data.write_int32(0xEDAAC, 0x00000006)  # Torture Chamber Door
        rom_data.write_int32(0xEDAB4, 0x00000007)  # ToE Gate
        rom_data.write_int32(0xEDABC, 0x00000008)  # Science Door1
        rom_data.write_int32(0xEDAC4, 0x00000009)  # Science Door2
        rom_data.write_int32(0xEDACC, 0x0000000A)  # Science Door3
        rom_data.write_int32(0xEDAD4, 0x0000000B)  # CT Door 1
        rom_data.write_int32(0xEDADC, 0x0000000C)  # CT Door 2
        rom_data.write_int32(0xEDAE4, 0x0000000D)  # CT Door 3

        # Fix ToE gate's "unlocked" flag in the locked door flags table.
        rom_data.write_int16(0x10B3B6, 0x0001)

        rom_data.write_int32(0x10AB2C, 0x8015FBD4)  # Maze Gates' check code pointer adjustments.
        rom_data.write_int32(0x10AB40, 0x8015FBD4)
        rom_data.write_int32s(0x10AB50, [0x0D0C0000,
                                         0x8015FBD4])
        rom_data.write_int32s(0x10AB64, [0x0D0C0000,
                                         0x8015FBD4])
        rom_data.write_int32s(0xE2E14, patches.normal_door_hook)
        rom_data.write_int32s(0xBFC5D0, patches.normal_door_code)
        rom_data.write_int32s(0x6EF298, patches.ct_door_hook)
        rom_data.write_int32s(0xBFC608, patches.ct_door_code)
        # Fix key counter not decrementing if 2 or above.
        rom_data.write_int32(0xAA0E0, 0x24020000)  # ADDIU	V0, R0, 0x0000

        # Make the Easy-only candle drops in Room of Clocks appear on any difficulty.
        rom_data.write_byte(0xBF7E, 0x01, ni_files.MAP_ROOM_OF_CLOCKS)
        rom_data.write_byte(0xBF8E, 0x01, ni_files.MAP_ROOM_OF_CLOCKS)

        # Slightly move some once-invisible freestanding items to be more visible.
        if options["invisible_items"] == InvisibleItems.option_reveal_all:
            rom_data.write_byte(0x3D0F1, 0xEF, ni_files.MAP_FOREST)  # Forest dirge maiden statue
            rom_data.write_byte(0x3D105, 0xAB, ni_files.MAP_FOREST)  # Forest werewolf statue
            rom_data.write_byte(0x1AA71, 0x8C, ni_files.MAP_VILLA_FRONT_YARD)  # Villa courtyard tombstone
            rom_data.write_byte(0x2C735, 0xC2, ni_files.MAP_VILLA_LIVING_AREA)  # Villa living room painting
            rom_data.write_byte(0x26891, 0xF5, ni_files.MAP_CC_BASEMENT)  # CC torture instrument rack
            rom_data.write_byte(0x2BA55, 0x22, ni_files.MAP_CC_FACTORY_FLOOR)  # CC red carpet hallway knight
            rom_data.write_byte(0x292A5, 0xF1, ni_files.MAP_CC_LIZARD_LAB)  # CC cracked wall flamethrower
            rom_data.write_byte(0x30675, 0xA5, ni_files.MAP_CC_INVENTIONS)  # CC nitro hallway flamethrower
            rom_data.write_byte(0x30471, 0x9A, ni_files.MAP_CC_INVENTIONS)  # CC invention room round machine
            rom_data.write_byte(0x30485, 0x03, ni_files.MAP_CC_INVENTIONS)  # CC invention room giant famicart
            rom_data.write_byte(0x30931, 0x97, ni_files.MAP_CC_INVENTIONS)  # CC staircase knight (x)
            rom_data.write_byte(0x30935, 0xFB, ni_files.MAP_CC_INVENTIONS)  # CC staircase knight (z)

        # Change the bitflag on the item in upper coffin in Forest final switch gate tomb to one that's not used by
        # something else.
        rom_data.write_int32(0x10C77C, 0x00000002)

        # Make the torch directly behind Dracula's chamber that normally doesn't set a flag set bitflag 0x08 in
        # 0x80389BFA.
        rom_data.write_byte(0x10CE9F, 0x01)
        # Make the two flame invisible items set unique flags as well.
        rom_data.write_byte(0x1F58B, 0x01, ni_files.MAP_CK_EXTERIOR)
        rom_data.write_byte(0x1F59B, 0x02, ni_files.MAP_CK_EXTERIOR)

        # Change the CC post-Behemoth boss depending on the option for Post-Behemoth Boss
        if options["post_behemoth_boss"] == PostBehemothBoss.option_inverted:
            rom_data.write_byte(0xEEDAD, 0x02)
            rom_data.write_byte(0xEEDD9, 0x01)
        elif options["post_behemoth_boss"] == PostBehemothBoss.option_always_rosa:
            rom_data.write_byte(0xEEDAD, 0x00)
            rom_data.write_byte(0xEEDD9, 0x03)
            # Put both on the same flag so changing character won't trigger a rematch with the same boss.
            rom_data.write_byte(0xEED8B, 0x40)
        elif options["post_behemoth_boss"] == PostBehemothBoss.option_always_camilla:
            rom_data.write_byte(0xEEDAD, 0x03)
            rom_data.write_byte(0xEEDD9, 0x00)
            rom_data.write_byte(0xEED8B, 0x40)

        # Change the RoC boss depending on the option for Room of Clocks Boss
        if options["room_of_clocks_boss"] == RoomOfClocksBoss.option_inverted:
            rom_data.write_byte(0x109FB3, 0x56)
            rom_data.write_byte(0x109FBF, 0x44)
            rom_data.write_byte(0xD9D44, 0x14)
            rom_data.write_byte(0xD9D4C, 0x14)
        elif options["room_of_clocks_boss"] == RoomOfClocksBoss.option_always_death:
            rom_data.write_byte(0x109FBF, 0x44)
            rom_data.write_byte(0xD9D45, 0x00)
            # Put both on the same flag so changing character won't trigger a rematch with the same boss.
            rom_data.write_byte(0x109FB7, 0x90)
            rom_data.write_byte(0x109FC3, 0x90)
        elif options["room_of_clocks_boss"] == RoomOfClocksBoss.option_always_actrise:
            rom_data.write_byte(0x109FB3, 0x56)
            rom_data.write_int32(0xD9D44, 0x00000000)
            rom_data.write_byte(0xD9D4D, 0x00)
            rom_data.write_byte(0x109FB7, 0x90)
            rom_data.write_byte(0x109FC3, 0x90)

        # Un-nerf Actrise when playing as Reinhardt. This is likely a leftover feature from the Tokyo Game Show 1998
        # demo wherein players could battle Actrise as Reinhardt.
        rom_data.write_int32(0x79C, 0x240E0001, ni_files.OVL_ACTRISE)  # ADDIU	T6, R0, 0x0001

        # Tunnel gondola skip stuff.
        if options["skip_gondolas"]:
            rom_data.write_int32(0x6C5F58, 0x080FF7D0)  # J 0x803FDF40
            rom_data.write_int32s(0xBFDF40, patches.gondola_skipper)
            # New gondola transfer point candle coordinates
            rom_data.write_int16s(0x323D0, [0x0427, 0x0110, 0xF7A0], ni_files.MAP_TUNNEL)

        # Waterway brick platforms skip
        if options["skip_waterway_blocks"]:
            rom_data.write_int32(0x6C7E2C, 0x00000000)  # NOP

        # Ambience silencing fix
        rom_data.write_int32(0xD9270, 0x080FF840)  # J 0x803FE100
        rom_data.write_int32s(0xBFE100, patches.ambience_silencer)
        # Fix for the door sliding sound playing infinitely if leaving the fan meeting room before the door closes
        # entirely. Hooking this in the ambience silencer code does nothing for some reason.
        rom_data.write_int32s(0xAE10C, [0x08004FAB,  # J   0x80013EAC
                                        0x3404829B])  # ORI A0, R0, 0x829B
        rom_data.write_int32s(0xD9E8C, [0x08004FAB,  # J   0x80013EAC
                                        0x3404829B])  # ORI A0, R0, 0x829B
        # Fan meeting room ambience fix
        rom_data.write_int32(0x109964, 0x803FE13C)

        # Make the Villa coffin cutscene skippable
        rom_data.write_int32(0xAA530, 0x080FF880)  # J 0x803FE200
        rom_data.write_int32s(0xBFE200, patches.coffin_cutscene_skipper)

        # Increase shimmy speed
        if options["increase_shimmy_speed"]:
            rom_data.write_byte(0xA4241, 0x5A)

        # Disable landing fall damage
        if options["fall_guard"]:
            rom_data.write_byte(0x27B23, 0x00)

        # Enable the unused film reel effect on all cutscenes
        if options["cinematic_experience"]:
            rom_data.write_int32(0xAA33C, 0x240A0001)  # ADDIU T2, R0, 0x0001
            rom_data.write_byte(0xAA34B, 0x0C)
            rom_data.write_int32(0xAA4C4, 0x24090001)  # ADDIU T1, R0, 0x0001

        # Permanent PowerUp stuff
        if options["permanent_powerups"]:
            # Make receiving PowerUps increase the unused menu PowerUp counter instead of the one outside the save
            # struct.
            rom_data.write_int32(0xBF2EC, 0x806B619B)  # LB	T3, 0x619B (V1)
            rom_data.write_int32(0xBFC5BC, 0xA06C619B)  # SB	T4, 0x619B (V1)
            # Make Reinhardt's whip check the menu PowerUp counter
            rom_data.write_int32(0x69FA08, 0x80CC619B)  # LB	T4, 0x619B (A2)
            rom_data.write_int32(0x69FBFC, 0x80C3619B)  # LB	V1, 0x619B (A2)
            rom_data.write_int32(0x69FFE0, 0x818C9C53)  # LB	T4, 0x9C53 (T4)
            # Make Carrie's orb check the menu PowerUp counter
            rom_data.write_int32(0x6AC86C, 0x8105619B)  # LB	A1, 0x619B (T0)
            rom_data.write_int32(0x6AC950, 0x8105619B)  # LB	A1, 0x619B (T0)
            rom_data.write_int32(0x6AC99C, 0x810E619B)  # LB	T6, 0x619B (T0)
            rom_data.write_int32(0x5AFA0, 0x80639C53)  # LB	V1, 0x9C53 (V1)
            rom_data.write_int32(0x5B0A0, 0x81089C53)  # LB	T0, 0x9C53 (T0)
            rom_data.write_byte(0x391C7, 0x00)  # Prevent PowerUps from dropping from regular enemies.
            rom_data.write_byte(0xEDEDF, 0x03)  # Make any vanishing PowerUps that do show up L jewels instead.
            # Rename the PowerUp to "PermaUp"
            rom_data.write_bytes(0xEFDEE, cv64_string_to_bytearray("PermaUp"))
            # Replace the PowerUp in the Forest Special1 Bridge 3HB rock with an L jewel if 3HBs aren't randomized
            if not options["multi_hit_breakables"]:
                rom_data.write_byte(0x10C7A1, 0x03)
            # Remove the PowerUp in one of the Lizard Lockers if they are off.
            rom_data.write_byte(0x2BAC9, 0x03, ni_files.MAP_CC_FACTORY_FLOOR)
        # Change the appearance of the Pot-Pourri to that of a larger PowerUp regardless of the above setting, so other
        # game PermaUps are distinguishable.
        rom_data.write_int32s(0xEE558, [0x06005F08, 0x3FB00000, 0xFFFFFF00])

        # Write the associated code for the randomized (or disabled) music list.
        if options["background_music"]:
            rom_data.write_int32(0x14588, 0x08060D60)  # J 0x80183580
            rom_data.write_int32(0x14590, 0x00000000)  # NOP
            rom_data.write_int32s(0x106770, patches.music_modifier)
            rom_data.write_int32(0x15780, 0x0C0FF36E)  # JAL 0x803FCDB8
            rom_data.write_int32s(0xBFCDB8, patches.music_comparer_modifier)

        # Enable storing item flags anywhere and changing the item model/visibility on any item instance.
        rom_data.write_int32s(0xA857C, [0x080FF38F,  # J     0x803FCE3C
                                        0x94D90038])  # LHU   T9, 0x0038 (A2)
        rom_data.write_int32s(0xBFCE3C, patches.item_customizer)
        rom_data.write_int32s(0xA86A0, [0x0C0FF3AF,  # JAL   0x803FCEBC
                                        0x95C40002])  # LHU   A0, 0x0002 (T6)
        rom_data.write_int32s(0xBFCEBC, patches.item_appearance_switcher)
        rom_data.write_int32s(0xA8728, [0x0C0FF3B8,  # JAL   0x803FCEE4
                                        0x01396021])  # ADDU  T4, T1, T9
        rom_data.write_int32s(0xBFCEE4, patches.item_model_visibility_switcher)
        rom_data.write_int32s(0xA8A04, [0x0C0FF3C2,  # JAL   0x803FCF08
                                        0x018B6021])  # ADDU  T4, T4, T3
        rom_data.write_int32s(0xBFCF08, patches.item_shine_visibility_switcher)

        # Make Axes and Crosses in AP Locations drop to their correct height, and make items with changed appearances
        # spin their correct speed.
        rom_data.write_int32s(0xE649C, [0x0C0FFA03,  # JAL   0x803FE80C
                                        0x956C0002])  # LHU   T4, 0x0002 (T3)
        rom_data.write_int32s(0xA8B08, [0x080FFA0C,  # J     0x803FE830
                                        0x960A0038])  # LHU   T2, 0x0038 (S0)
        rom_data.write_int32s(0xE8584, [0x0C0FFA21,  # JAL   0x803FE884
                                        0x95D80000])  # LHU   T8, 0x0000 (T6)
        rom_data.write_int32s(0xE7AF0, [0x0C0FFA2A,  # JAL   0x803FE8A8
                                        0x958D0000])  # LHU   T5, 0x0000 (T4)
        rom_data.write_int32s(0xBFE7DC, patches.item_drop_spin_corrector)

        # Disable the 3HBs checking and setting flags when breaking them and enable their individual items checking and
        # setting flags instead.
        if options["multi_hit_breakables"]:
            rom_data.write_int32(0xE87F8, 0x00000000)  # NOP
            rom_data.write_int16(0xE836C, 0x1000)
            rom_data.write_int32(0xE8B40, 0x0C0FF3CD)  # JAL 0x803FCF34
            rom_data.write_int32s(0xBFCF34, patches.three_hit_item_flags_setter)
            # Villa foyer chandelier-specific functions (yeah, IDK why KCEK made different functions for this one).
            rom_data.write_int32(0xE7D54, 0x00000000)  # NOP
            rom_data.write_int16(0xE7908, 0x1000)
            rom_data.write_byte(0xE7A5C, 0x10)
            rom_data.write_int32(0xE7F08, 0x0C0FF3DF)  # JAL 0x803FCF7C
            rom_data.write_int32s(0xBFCF7C, patches.chandelier_item_flags_setter)

            # New flag values to put in each 3HB vanilla flag's spot.
            rom_data.write_int32(0x10C7C8, 0x8000FF48)  # FoS dirge maiden rock
            rom_data.write_int32(0x10C7B0, 0x0200FF48)  # FoS S1 bridge rock
            rom_data.write_int32(0x10C86C, 0x0010FF48)  # CW upper rampart save nub
            rom_data.write_int32(0x10C878, 0x4000FF49)  # CW Dracula switch slab
            rom_data.write_int32(0x10CAD8, 0x0100FF49)  # Tunnel twin arrows slab
            rom_data.write_int32(0x10CAE4, 0x0004FF49)  # Tunnel lonesome bucket pit rock
            rom_data.write_int32(0x10CB54, 0x4000FF4A)  # UW poison parkour ledge
            rom_data.write_int32(0x10CB60, 0x0080FF4A)  # UW skeleton crusher ledge
            rom_data.write_int32(0x10CBF0, 0x0008FF4A)  # CC Behemoth crate
            rom_data.write_int32(0x10CC2C, 0x2000FF4B)  # CC elevator pedestal
            rom_data.write_int32(0x10CC70, 0x0200FF4B)  # CC lizard locker slab
            rom_data.write_int32(0x10CD88, 0x0010FF4B)  # ToE pre-midsavepoint platforms ledge
            rom_data.write_int32(0x10CE6C, 0x4000FF4C)  # ToSci invisible bridge crate
            rom_data.write_int32(0x10CF20, 0x0080FF4C)  # CT inverted battery slab
            rom_data.write_int32(0x10CF2C, 0x0008FF4C)  # CT inverted door slab
            rom_data.write_int32(0x10CF38, 0x8000FF4D)  # CT final room door slab
            rom_data.write_int32(0x10CF44, 0x1000FF4D)  # CT Renon slab
            rom_data.write_int32(0x10C908, 0x0008FF4D)  # Villa foyer chandelier
            rom_data.write_byte(0x10CF37, 0x04)  # pointer for CT final room door slab item data

        # Once-per-frame gameplay checks
        rom_data.write_int32(0x6C848, 0x080FF40D)  # J 0x803FD034
        rom_data.write_int32(0xBFD058, 0x0801AEB5)  # J 0x8006BAD4

        # Everything related to dropping the previous sub-weapon
        if options["drop_previous_sub_weapon"]:
            rom_data.write_int32(0xBFD034, 0x080FF3FF)  # J 0x803FCFFC
            rom_data.write_int32(0xBFC190, 0x080FF3F2)  # J 0x803FCFC8
            rom_data.write_int32s(0xBFCFC4, patches.prev_subweapon_spawn_checker)
            rom_data.write_int32s(0xBFCFFC, patches.prev_subweapon_fall_checker)
            rom_data.write_int32s(0xBFD060, patches.prev_subweapon_dropper)

        # Everything related to the Countdown counter
        if options["countdown"]:
            rom_data.write_int32(0xBFD03C, 0x080FF9DC)  # J 0x803FE770
            rom_data.write_int32(0xD5D48, 0x080FF4EC)  # J 0x803FD3B0
            rom_data.write_int32s(0xBFD3B0, patches.countdown_number_displayer)
            rom_data.write_int32s(0xBFD6DC, patches.countdown_number_manager)
            rom_data.write_int32s(0xBFE770, patches.countdown_demo_hider)
            rom_data.write_int32(0xBFCE2C, 0x080FF5D2)  # J 0x803FD748
            rom_data.write_int32s(0xBB168, [0x080FF5F4,  # J 0x803FD7D0
                                            0x8E020028])  # LW	V0, 0x0028 (S0)
            rom_data.write_int32s(0xBB1D0, [0x080FF5FB,  # J 0x803FD7EC
                                            0x8E020028])  # LW	V0, 0x0028 (S0)
            rom_data.write_int32(0xBC4A0, 0x080FF5E6)  # J 0x803FD798
            rom_data.write_int32(0xBC4C4, 0x080FF5E6)  # J 0x803FD798
            rom_data.write_int32(0x19844, 0x080FF602)  # J 0x803FD808
            # If the option is set to "all locations", count it down no matter what the item is.
            if options["countdown"] == Countdown.option_all_locations:
                rom_data.write_int32s(0xBFD71C, [0x01010101, 0x01010101, 0x01010101, 0x01010101, 0x01010101, 0x01010101,
                                                 0x01010101, 0x01010101, 0x01010101, 0x01010101, 0x01010101])
            else:
                # If it's majors, then insert this last minute check I threw together for the weird edge case of a CV64
                # ice trap for another CV64 player taking the form of a major.
                rom_data.write_int32s(0xBFD788, [0x080FF717,  # J 0x803FDC5C
                                                 0x2529FFFF])  # ADDIU T1, T1, 0xFFFF
                rom_data.write_int32s(0xBFDC5C, patches.countdown_extra_safety_check)
            rom_data.write_int32(0xA9ECC,
                                 0x00000000)  # NOP the pointless overwrite of the item actor appearance custom value.

        # Ice Trap stuff.
        rom_data.write_int32(0x697C60, 0x080FF06B)  # J 0x803FC18C
        rom_data.write_int32(0x6A5160, 0x080FF06B)  # J 0x803FC18C
        rom_data.write_int32s(0xBFC1AC, patches.ice_trap_initializer)
        rom_data.write_int32s(0xBFE700, patches.the_deep_freezer)
        rom_data.write_int32s(0x9630, [0x3C19803F,  # LUI T9, 0x803F
                                       0x3739E4C0,  # ORI T9, T9, 0xE4C0
                                       0x03200008,  # JR  T9
                                       0x00000000],  # NOP
                              ni_files.OVL_CAMILLA)  # NOP
        rom_data.write_int32s(0xBFE4C0, patches.freeze_verifier)

        # Fix for the ice chunk model staying when getting bitten by the maze garden dogs.
        rom_data.write_int32(0x6338, 0x803FE9C0, ni_files.OVL_STONE_DOG)
        rom_data.write_int32s(0xBFE9C0, patches.dog_bite_ice_trap_fix)
        # TODO: Fix this in more places

        # Initial Countdown numbers.
        rom_data.write_int32(0xAD6A8, 0x080FF60A)  # J	0x803FD828
        rom_data.write_int32s(0xBFD828, patches.new_game_extras)

        # Everything related to shopsanity.
        if options["shopsanity"]:
            rom_data.write_byte(0xBFBFDF, 0x01)
            rom_data.write_bytes(0x103868, cv64_string_to_bytearray("Not obtained. "))
            rom_data.write_int32s(0xBFD8D0, patches.shopsanity_stuff)
            rom_data.write_int32(0xBD828, 0x0C0FF643)  # JAL	0x803FD90C
            rom_data.write_int32(0xBD5B8, 0x0C0FF651)  # JAL	0x803FD944
            rom_data.write_int32(0xB0610, 0x0C0FF665)  # JAL	0x803FD994
            rom_data.write_int32s(0xBD24C, [0x0C0FF677,  # J  	0x803FD9DC
                                            0x00000000])  # NOP
            rom_data.write_int32(0xBD618, 0x0C0FF684)  # JAL	0x803FDA10

        # Panther Dash running.
        if options["panther_dash"]:
            rom_data.write_int32(0x69C8C4, 0x0C0FF77E)  # JAL   0x803FDDF8
            rom_data.write_int32(0x6AA228, 0x0C0FF77E)  # JAL   0x803FDDF8
            rom_data.write_int32s(0x69C86C, [0x0C0FF78E,  # JAL   0x803FDE38
                                             0x3C01803E])  # LUI   AT, 0x803E
            rom_data.write_int32s(0x6AA1D0, [0x0C0FF78E,  # JAL   0x803FDE38
                                             0x3C01803E])  # LUI   AT, 0x803E
            rom_data.write_int32(0x69D37C, 0x0C0FF79E)  # JAL   0x803FDE78
            rom_data.write_int32(0x6AACE0, 0x0C0FF79E)  # JAL   0x803FDE78
            rom_data.write_int32s(0xBFDDF8, patches.panther_dash)
            # Jump prevention.
            if options["panther_dash"] == PantherDash.option_jumpless:
                rom_data.write_int32(0xBFDE2C, 0x080FF7BB)  # J     0x803FDEEC
                rom_data.write_int32(0xBFD044, 0x080FF7B1)  # J     0x803FDEC4
                rom_data.write_int32s(0x69B630, [0x0C0FF7C6,  # JAL   0x803FDF18
                                                 0x8CCD0000])  # LW    T5, 0x0000 (A2)
                rom_data.write_int32s(0x6A8EC0, [0x0C0FF7C6,  # JAL   0x803FDF18
                                                 0x8CCC0000])  # LW    T4, 0x0000 (A2)
                # Fun fact: KCEK put separate code to handle coyote time jumping.
                rom_data.write_int32s(0x69910C, [0x0C0FF7C6,  # JAL   0x803FDF18
                                                 0x8C4E0000])  # LW    T6, 0x0000 (V0)
                rom_data.write_int32s(0x6A6718, [0x0C0FF7C6,  # JAL   0x803FDF18
                                                 0x8C4E0000])  # LW    T6, 0x0000 (V0)
                rom_data.write_int32s(0xBFDEC4, patches.panther_jump_preventer)

        # Everything related to Big Toss.
        if options["big_toss"]:
            rom_data.write_int32s(0x27E90, [0x0C0FFA38,  # JAL 0x803FE8E0
                                            0xAFB80074])  # SW  T8, 0x0074 (SP)
            rom_data.write_int32(0x26F54, 0x0C0FFA4D)  # JAL 0x803FE934
            rom_data.write_int32s(0xBFE8E0, patches.big_tosser)

        # Write the specified window colors.
        rom_data.write_byte(0xAEC23, options["window_color_r"] << 4)
        rom_data.write_byte(0xAEC33, options["window_color_g"] << 4)
        rom_data.write_byte(0xAEC47, options["window_color_b"] << 4)
        rom_data.write_byte(0xAEC43, options["window_color_a"] << 4)

        # Everything relating to loading the other game items text.
        rom_data.write_int32(0xA8D8C, 0x080FF88F)  # J   0x803FE23C
        rom_data.write_int32(0xBEA98, 0x0C0FF8B4)  # JAL 0x803FE2D0
        rom_data.write_int32(0xBEAB0, 0x0C0FF8BD)  # JAL 0x803FE2F8
        rom_data.write_int32(0xBEACC, 0x0C0FF8C5)  # JAL 0x803FE314
        rom_data.write_int32s(0xBFE23C, patches.multiworld_item_name_loader)
        rom_data.write_bytes(0x10F188, [0x00 for _ in range(264)])
        rom_data.write_bytes(0x10F298, [0x00 for _ in range(264)])

        # When the game normally JALs to the item prepare textbox function after the player picks up an item, set the
        # "no receiving" timer to ensure the item textbox doesn't freak out if you pick something up while there's a
        # queue of unreceived items.
        # TODO: The textbox can still freak out in other interact spots.
        rom_data.write_int32(0xA8D94, 0x0C0FF9F0)  # JAL	0x803FE7C0
        rom_data.write_int32s(0xBFE7C0, [0x3C088039,  # LUI   T0, 0x8039
                                         0x24090020,  # ADDIU T1, R0, 0x0020
                                         0x0804EDCE,  # J     0x8013B738
                                         0xA1099BE0])  # SB    T1, 0x9BE0 (T0)

        # Append the AP icons to the pickable items assets file.
        rom_data.write_bytes(0x69B6, pkgutil.get_data(__name__, "data/ap_icons.bin"), ni_files.ASSETS_ITEMS)
        # Update the map files' sizes table with the new pickable items assets file size.
        rom_data.write_int16(0x104CCE, len(rom_data.decompressed_files[ni_files.ASSETS_ITEMS]))
        # Update the Wooden Stake and Roses' item appearance settings table to point to the Archipelago item graphics.
        rom_data.write_int16(0xEE5BA, 0x7B38)
        rom_data.write_int16(0xEE5CA, 0x7280)
        # Change the items' sizes. The progression one will be larger than the non-progression one.
        rom_data.write_int32(0xEE5BC, 0x3FF00000)
        rom_data.write_int32(0xEE5CC, 0x3FA00000)

        # Write all the edits to the Nisitenma-Ichigo files decided during generation.
        for file in ni_edits:
            for offset in ni_edits[file]:
                rom_data.write_bytes(int(offset), base64.b64decode(ni_edits[file][offset].encode()), int(file))

        return rom_data.get_bytes()


class CV64ProcedurePatch(APProcedurePatch, APTokenMixin):
    hash = [CV64_US_10_HASH]
    patch_file_ending: str = ".apcv64"
    result_file_ending: str = ".z64"

    game = "Castlevania 64"

    procedure = [
        ("apply_patches", ["options.json", "ni_edits.json"]),
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def write_patch(world: "CV64World", patch: CV64ProcedurePatch, offset_data: Dict[Union[int, Tuple[int, int]], bytes],
                shop_name_list: List[str], shop_desc_list: List[List[Union[int, str, None]]],
                shop_colors_list: List[bytearray], active_locations: Iterable[Location]) -> None:
    active_warp_list = world.active_warp_list
    s1s_per_warp = world.s1s_per_warp

    # Compressed Nisitenma-Ichigo file edits.
    ni_edits: Dict[int, Dict[int, str]] = {}

    # Write all the new item/loading zone/shop/lighting/music/etc. values.
    for offset, data in offset_data.items():
        # If the offset is an int, write the data as a token to the main buffer.
        if isinstance(offset, int):
            patch.write_token(APTokenTypes.WRITE, offset, data)
        # If the offset is a tuple, the second element in said tuple will be the compressed NI file number to write to
        # and the first will be the offset in said file. Add the edit to the NI edits dict under the specified file
        # number.
        elif isinstance(offset, tuple):
            if offset[1] not in ni_edits:
                ni_edits[offset[1]] = {offset[0]: base64.b64encode(data).decode()}
            else:
                ni_edits[offset[1]].update({offset[0]: base64.b64encode(data).decode()})

    # Write the new Stage Select menu destinations.
    for i in range(len(active_warp_list)):
        if i == 0:
            patch.write_token(APTokenTypes.WRITE,
                              warp_map_offsets[i], get_stage_info(active_warp_list[i], "start map id"))
            patch.write_token(APTokenTypes.WRITE,
                              warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "start spawn id"))
        else:
            patch.write_token(APTokenTypes.WRITE,
                              warp_map_offsets[i], get_stage_info(active_warp_list[i], "mid map id"))
            patch.write_token(APTokenTypes.WRITE,
                              warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "mid spawn id"))

    # Change the Stage Select menu's text to reflect its new purpose.
    patch.write_token(APTokenTypes.WRITE, 0xEFAD0, bytes(
        cv64_string_to_bytearray(f"Where to...?\t{active_warp_list[0]}\t"
                                 f"`{str(s1s_per_warp).zfill(2)} {active_warp_list[1]}\t"
                                 f"`{str(s1s_per_warp * 2).zfill(2)} {active_warp_list[2]}\t"
                                 f"`{str(s1s_per_warp * 3).zfill(2)} {active_warp_list[3]}\t"
                                 f"`{str(s1s_per_warp * 4).zfill(2)} {active_warp_list[4]}\t"
                                 f"`{str(s1s_per_warp * 5).zfill(2)} {active_warp_list[5]}\t"
                                 f"`{str(s1s_per_warp * 6).zfill(2)} {active_warp_list[6]}\t"
                                 f"`{str(s1s_per_warp * 7).zfill(2)} {active_warp_list[7]}")))

    # Write the new File Select stage numbers.
    for stage in world.active_stage_exits:
        for offset in get_stage_info(stage, "save number offsets"):
            patch.write_token(APTokenTypes.WRITE, offset, bytes([world.active_stage_exits[stage]["position"]]))

    # Write all the shop text.
    if world.options.shopsanity:
        patch.write_token(APTokenTypes.WRITE, 0x103868, bytes(cv64_string_to_bytearray("Not obtained. ")))

        shopsanity_name_text = bytearray(0)
        shopsanity_desc_text = bytearray(0)
        for i in range(len(shop_name_list)):
            shopsanity_name_text += bytearray([0xA0, i]) + shop_colors_list[i] + \
                                    cv64_string_to_bytearray(cv64_text_truncate(shop_name_list[i], 74))

            shopsanity_desc_text += bytearray([0xA0, i])
            if shop_desc_list[i][1] is not None:
                shopsanity_desc_text += cv64_string_to_bytearray("For " + shop_desc_list[i][1] + ".\n",
                                                                 append_end=False)
            shopsanity_desc_text += cv64_string_to_bytearray(renon_item_dialogue[shop_desc_list[i][0]])
        patch.write_token(APTokenTypes.WRITE, 0x1AD00, bytes(shopsanity_name_text))
        patch.write_token(APTokenTypes.WRITE, 0x1A800, bytes(shopsanity_desc_text))

    # Write the item/player names for other game items.
    for loc in active_locations:
        if loc.address is None or get_location_info(loc.name, "type") == "shop" or loc.item.player == world.player:
            continue
        if len(loc.item.name) > 67:
            item_name = loc.item.name[0x00:0x68]
        else:
            item_name = loc.item.name
        inject_address = 0xBB7164 + (256 * (loc.address & 0xFFF))
        wrapped_name, num_lines = cv64_text_wrap(item_name + "\nfor " +
                                                 world.multiworld.get_player_name(loc.item.player), 96)
        patch.write_token(APTokenTypes.WRITE, inject_address, bytes(get_item_text_color(loc) +
                                                                    cv64_string_to_bytearray(wrapped_name)))
        patch.write_token(APTokenTypes.WRITE, inject_address + 255, bytes([num_lines]))

    # Write the secondary name the client will use to distinguish a vanilla ROM from an AP one.
    patch.write_token(APTokenTypes.WRITE, 0xBFBFD0, "ARCHIPELAGO1".encode("utf-8"))
    # Write the slot authentication
    patch.write_token(APTokenTypes.WRITE, 0xBFBFE0, bytes(world.auth))

    patch.write_file("token_data.bin", patch.get_token_binary())

    # Write these slot options to a JSON.
    options_dict = {
        "character_stages": world.options.character_stages.value,
        "vincent_fight_condition": world.options.vincent_fight_condition.value,
        "renon_fight_condition": world.options.renon_fight_condition.value,
        "bad_ending_condition": world.options.bad_ending_condition.value,
        "increase_item_limit": world.options.increase_item_limit.value,
        "nerf_healing_items": world.options.nerf_healing_items.value,
        "loading_zone_heals": world.options.loading_zone_heals.value,
        "disable_time_restrictions": world.options.disable_time_restrictions.value,
        "death_link": world.options.death_link.value,
        "draculas_condition": world.options.draculas_condition.value,
        "invisible_items": world.options.invisible_items.value,
        "post_behemoth_boss": world.options.post_behemoth_boss.value,
        "room_of_clocks_boss": world.options.room_of_clocks_boss.value,
        "skip_gondolas": world.options.skip_gondolas.value,
        "skip_waterway_blocks": world.options.skip_waterway_blocks.value,
        "s1s_per_warp": world.options.special1s_per_warp.value,
        "required_s2s": world.required_s2s,
        "total_s2s": world.total_s2s,
        "total_special1s": world.options.total_special1s.value,
        "increase_shimmy_speed": world.options.increase_shimmy_speed.value,
        "fall_guard": world.options.fall_guard.value,
        "cinematic_experience": world.options.cinematic_experience.value,
        "permanent_powerups": world.options.permanent_powerups.value,
        "background_music": world.options.background_music.value,
        "multi_hit_breakables": world.options.multi_hit_breakables.value,
        "drop_previous_sub_weapon": world.options.drop_previous_sub_weapon.value,
        "countdown": world.options.countdown.value,
        "shopsanity": world.options.shopsanity.value,
        "panther_dash": world.options.panther_dash.value,
        "big_toss": world.options.big_toss.value,
        "window_color_r": world.options.window_color_r.value,
        "window_color_g": world.options.window_color_g.value,
        "window_color_b": world.options.window_color_b.value,
        "window_color_a": world.options.window_color_a.value,
    }

    patch.write_file("options.json", json.dumps(options_dict).encode('utf-8'))

    # Write all of our Nisitenma-Ichigo file edits to another JSON.
    patch.write_file("ni_edits.json", json.dumps(ni_edits).encode('utf-8'))


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if CV64_US_10_HASH != basemd5.hexdigest():
            raise Exception("Supplied Base Rom does not match known MD5 for Castlevania 64 US 1.0."
                            "Get the correct game and version, then dump it.")
        setattr(get_base_rom_bytes, "base_rom_bytes", base_rom_bytes)
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    if not file_name:
        file_name = get_settings()["cv64_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name
