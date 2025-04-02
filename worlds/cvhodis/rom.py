import Utils
import logging
import json

from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
from typing import Dict, Optional, Collection, TYPE_CHECKING

import hashlib
import os
import pkgutil

from .data import patches, loc_names
from .locations import CVHODIS_CHECKS_INFO, GUARDIAN_GRINDER_LOCATIONS
from .items import PICKUP_TYPE_MAX
from .cvhodis_text import cvhodis_string_to_bytearray, LEN_LIMIT_DESCRIPTION, DESCRIPTION_DISPLAY_LINES
from settings import get_settings

if TYPE_CHECKING:
    from . import CVHoDisWorld

CVHODIS_CT_US_HASH = "ea589465486d15e91ba94165c8024b55"  # Original GBA cartridge ROM
CVHODIS_AC_US_HASH = "35db4a2bacdec253672db68e73a41005"  # Castlevania Advance Collection ROM

GBA_ROM_START = 0x8000000
MK_ACTORS_START = 0x4A7F40
WARP_A_ACTORS_START = 0x499C8C
PORTAL_ACTORS_START = 0x49BE08
SWA7_ALT_ROOM_INFO_START = 0x4A7590
ETA18_ROOM_INFO_START = 0x499668
CYA4_ROOM_INFO_START = 0x4ACA80
LCA11_ROOM_INFO_START = 0x4A3324
LCA23_ROOM_INFO_START = 0x4A52D0
SWA19_ROOM_INFO_START = 0x4A7C48
BOOK_INFO_START = 0x4B2C60
NEW_BOOK_INFO_START = 0x6A3100
BOOK_INFO_LENGTH = 0x14
RELIC_INFO_START = 0x4B2C74
NEW_RELIC_INFO_START = 0x6A3200
RELIC_INFO_LENGTH = 0x30
FURNITURE_INFO_START = 0x4B2CA4
NEW_FURNITURE_INFO_START = 0x6A3000
FURNITURE_INFO_LENGTH = 0x7C
AP_HINT_TEXT_START = 0x6A5000
TEXT_POINTERS_START = 0x495500
ITEM_TEXT_IDS_START = 0x4B2D20
NEW_ITEM_TEXT_IDS_START = 0x4B2D00
ITEM_TEXT_IDS_LENGTH = 0x1AA
START_SPAWN_SET_TEXT_START = 0x6A6100

ARCHIPELAGO_IDENTIFIER_START = 0x7FFF00
ARCHIPELAGO_IDENTIFIER = "ARCHIPELAG01"
AUTH_NUMBER_START = 0x7FFF10
QUEUED_TEXT_STRING_START = 0x7CEB00
MULTIWORLD_TEXTBOX_POINTERS_START = 0x671C10


class RomData:
    def __init__(self, file: bytes, name: Optional[str] = None) -> None:
        self.file = bytearray(file)
        self.name = name

    def read_byte(self, offset: int) -> int:
        return self.file[offset]

    def read_bytes(self, start_address: int, length: int) -> bytearray:
        return self.file[start_address:start_address + length]

    def write_byte(self, offset: int, value: int) -> None:
        self.file[offset] = value

    def write_bytes(self, offset: int, values: Collection[int]) -> None:
        self.file[offset:offset + len(values)] = values

    def get_bytes(self) -> bytes:
        return bytes(self.file)


class CVHoDisPatchExtensions(APPatchExtension):
    game = "Castlevania - Harmony of Dissonance"

    @staticmethod
    def apply_patches(caller: APProcedurePatch, rom: bytes, options_file: str) -> bytes:
        """Applies every patch to mod the game into its rando state."""

        rom_data = RomData(rom)
        options = json.loads(caller.get_file(options_file).decode("utf-8"))

        # Check to see if the patch was generated on a compatible APWorld version.
        if "compat_identifier" not in options:
            raise Exception("Incompatible patch/APWorld version. Make sure the Harmony of Dissonance APWorlds of both "
                            "you and the person who generated are matching (and preferably up-to-date).")
        if options["compat_identifier"] != ARCHIPELAGO_IDENTIFIER:
            raise Exception("Incompatible patch/APWorld version. Make sure the Harmony of Dissonance APWorlds of both "
                            "you and the person who generated are matching (and preferably up-to-date).")

        # Unlock all extras from the start (cutscene skipping, playable Maxim, Boss Rush, etc.).
        rom_data.write_bytes(0x1FF4, [0x00, 0x49,  # ldr r1, 0x86A1000
                                      0x8F, 0x46,  # mov r15, r1
                                      0x00, 0x10, 0x6A, 0x08])
        rom_data.write_bytes(0x6A1000, patches.extras_unlocker)

        # Add capabilities to remotely receive any item.
        rom_data.write_bytes(0x754C, [0x00, 0x4A,  # ldr r2, 0x86A2000
                                      0x97, 0x46,  # mov r15, r2
                                      0x00, 0x20, 0x6A, 0x08])
        rom_data.write_bytes(0x6A2000, patches.remote_textbox_shower)

        # Make spawning pickups with custom palettes default to the always-loaded OBP1 palette if there are already
        # 2 custom item palettes loaded instead of despawning.
        rom_data.write_bytes(0x197D0, [0x00, 0x49,  # ldr r1, 0x86A0100
                                       0x8F, 0x46,  # mov r15, r1
                                       0x00, 0x01, 0x6A, 0x08])
        rom_data.write_bytes(0x6A0100, patches.item_palette_defaulter)

        # Fix the MK's Bracelet check cutscene softlocking you if it gives you something that isn't MK's Bracelet.
        # Change the pointer to the actor data in the Sky Walkway A post-Shadow Maxim meeting room.
        rom_data.write_bytes(SWA7_ALT_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_CHECKS_INFO[loc_names.swa7].offset - 0xC) | GBA_ROM_START, 4, "little"))
        # Copy the actor data over to the new location and insert a new actor for a pre-placed MK's Bracelet pickup.
        rom_data.write_bytes(CVHODIS_CHECKS_INFO[loc_names.swa7].offset - 0xC,
                             list(rom_data.read_bytes(MK_ACTORS_START, 0xC)) +
                             [0x38, 0x00,  # X position
                              0x90, 0x00,  # Y position
                              0xC1,  # Unique ID/Type
                              0x05,  # Subtype
                              0x00, 0x00,  # Not used
                              CVHODIS_CHECKS_INFO[loc_names.swa7].code, 0x00,  # Pickup flag
                              0x2C, 0x00]  # Item index
                             + list(rom_data.read_bytes(MK_ACTORS_START + 0xC, 0xC)))
        # NOP the calls to the spawn pickup function so that the cutscene spawns nothing.
        # Useless fun fact: you can get two MK Bracelets in the vanilla game by only skipping the cutscene after the
        # game spawns one during it, which spawns a second one!
        rom_data.write_bytes(0x2DE08, [0x00, 0x00, 0x00, 0x00])
        rom_data.write_bytes(0x2DE74, [0x00, 0x00, 0x00, 0x00])
        # NOP the BEQ that checks to see if MK's Bracelet is in the inventory before ending the cutscene.
        rom_data.write_bytes(0x2DE24, [0x00, 0x00])

        # Change the flag value of the Treasury B portal staircase bottom to be unique from its cousin in Treasury A.
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.cyb8].offset + 0x08, CVHODIS_CHECKS_INFO[loc_names.cyb8].code)

        # Put the upper Entrance, lower Treasury, and Luminous (all A) warp rooms on their own actor lists instead of
        # them all pointing to the exact same one, and make the pickup actor's flag in each one unique.
        warp_a_basic_actors = rom_data.read_bytes(WARP_A_ACTORS_START, 0x30)

        rom_data.write_bytes(ETA18_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_CHECKS_INFO[loc_names.eta18].offset - 0x18) | GBA_ROM_START,
                                          4, "little"))
        rom_data.write_bytes(CVHODIS_CHECKS_INFO[loc_names.eta18].offset - 0x18, warp_a_basic_actors)
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.eta18].offset + 0x08, CVHODIS_CHECKS_INFO[loc_names.eta18].code)
        rom_data.write_bytes(CYA4_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_CHECKS_INFO[loc_names.cya4].offset - 0x18) | GBA_ROM_START,
                                          4, "little"))
        rom_data.write_bytes(CVHODIS_CHECKS_INFO[loc_names.cya4].offset - 0x18, warp_a_basic_actors)
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.cya4].offset + 0x08, CVHODIS_CHECKS_INFO[loc_names.cya4].code)
        rom_data.write_bytes(LCA11_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_CHECKS_INFO[loc_names.lca11].offset - 0x18) | GBA_ROM_START,
                                          4, "little"))
        rom_data.write_bytes(CVHODIS_CHECKS_INFO[loc_names.lca11].offset - 0x18, warp_a_basic_actors)
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.lca11].offset + 0x08, CVHODIS_CHECKS_INFO[loc_names.lca11].code)
        # Change the X position of the "right" upper Treasury A item and make its flag unique.
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.cya20a].offset, 0xB0)
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.cya20a].offset + 0x08, CVHODIS_CHECKS_INFO[loc_names.cya20a].code)
        # Make the flag of the before Panzuzu warp room pickup unique.
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.tfa15].offset + 0x08, CVHODIS_CHECKS_INFO[loc_names.tfa15].code)

        # Put the portal rooms between Luminous B and Walkway A on their own actor list and make the pickup flag on the
        # item in these rooms unique from the other pair's.
        portal_actors = rom_data.read_bytes(PORTAL_ACTORS_START, 0x24)
        rom_data.write_bytes(LCA23_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_CHECKS_INFO[loc_names.portals_lw].offset - 0xC) | GBA_ROM_START,
                                          4, "little"))
        rom_data.write_bytes(SWA19_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_CHECKS_INFO[loc_names.portals_lw].offset - 0xC) | GBA_ROM_START,
                                          4, "little"))
        rom_data.write_bytes(CVHODIS_CHECKS_INFO[loc_names.portals_lw].offset - 0xC, portal_actors)
        rom_data.write_byte(CVHODIS_CHECKS_INFO[loc_names.portals_lw].offset + 0x08,
                            CVHODIS_CHECKS_INFO[loc_names.portals_lw].code)

        # Add the GFX for the AP Items.
        for offset, data in patches.extra_item_sprites.items():
            rom_data.write_bytes(offset, data)

        # Add the "Archipelago Item" text over one of the NULL enemy names.
        rom_data.write_bytes(0xD8FEC, cvhodis_string_to_bytearray("Filler Item\n\t"))
        rom_data.write_bytes(0xD900C, cvhodis_string_to_bytearray("Useful Item\n\t"))
        rom_data.write_bytes(0xD902C, cvhodis_string_to_bytearray("Trap Item\n\t"))
        rom_data.write_bytes(0xD904C, cvhodis_string_to_bytearray("Progression Item\n\t"))
        rom_data.write_bytes(0xD907C, cvhodis_string_to_bytearray("Prog-Useful Item\n\t"))

        # Move the Spell Book info table and expand it with an extra entry for our Progression item.
        rom_data.write_bytes(0x19798, int.to_bytes(NEW_BOOK_INFO_START | GBA_ROM_START, 4, "little"))
        rom_data.write_bytes(0x1A020, int.to_bytes(NEW_BOOK_INFO_START | GBA_ROM_START, 4, "little"))
        rom_data.write_bytes(NEW_BOOK_INFO_START, rom_data.read_bytes(BOOK_INFO_START, BOOK_INFO_LENGTH))
        rom_data.write_bytes(NEW_BOOK_INFO_START + BOOK_INFO_LENGTH, [0xD8, 0x00, 0xE0, 0x01])  # Progression

        # Prevent auto-equipping Spell Books with a value higher than 5.
        rom_data.write_bytes(0x1A046, [0xED, 0xE7])  # b    [backward 0x12]
        rom_data.write_bytes(0x1A024, [0x05, 0x28,   # cmp r0, 5
                                       0x0F, 0xD8,   # bhi  [forward 0x10]
                                       0xF8, 0x73,   # strb r0, [r7, 0x0F]
                                       0x0D, 0xE0])  # b    [forward 0x0E]

        # Move the relic info table and expand it with an extra entry for our Prog + Useful item.
        rom_data.write_bytes(0x197A4, int.to_bytes(NEW_RELIC_INFO_START | GBA_ROM_START, 4, "little"))
        rom_data.write_bytes(0x1A0F0, int.to_bytes(NEW_RELIC_INFO_START | GBA_ROM_START, 4, "little"))
        rom_data.write_bytes(NEW_RELIC_INFO_START, rom_data.read_bytes(RELIC_INFO_START, RELIC_INFO_LENGTH))
        rom_data.write_bytes(NEW_RELIC_INFO_START + RELIC_INFO_LENGTH, [0xD9, 0x00, 0xE2, 0x01])  # Prog + Useful

        # Move the furniture info table and expand it with three more entries for our Filler, Useful, and Trap items.
        furn_info_ptr_bytes = int.to_bytes(NEW_FURNITURE_INFO_START | GBA_ROM_START, 4, "little")
        rom_data.write_bytes(0x197E4, furn_info_ptr_bytes)
        rom_data.write_bytes(0x19E30, furn_info_ptr_bytes)
        rom_data.write_bytes(0x19EE8, furn_info_ptr_bytes)
        rom_data.write_bytes(0x19FA4, furn_info_ptr_bytes)
        rom_data.write_bytes(0x1A068, furn_info_ptr_bytes)
        rom_data.write_bytes(0x1A134, furn_info_ptr_bytes)
        rom_data.write_bytes(0x1A24C, furn_info_ptr_bytes)
        rom_data.write_bytes(0x1A458, furn_info_ptr_bytes)
        rom_data.write_bytes(0x2A8CC, furn_info_ptr_bytes)
        rom_data.write_bytes(0x2AA24, furn_info_ptr_bytes)
        rom_data.write_bytes(0x2AAD0, furn_info_ptr_bytes)
        rom_data.write_bytes(NEW_FURNITURE_INFO_START, rom_data.read_bytes(FURNITURE_INFO_START, FURNITURE_INFO_LENGTH))
        rom_data.write_bytes(NEW_FURNITURE_INFO_START + FURNITURE_INFO_LENGTH, [0xD5, 0x00, 0xDF, 0x01,   # Filler
                                                                                0xD6, 0x00, 0xE1, 0x01,   # Useful
                                                                                0xD7, 0x00, 0xE3, 0x01])  # Trap

        # Move the array of string IDs that the pickup textbox can normally access and add the extra IDs for the
        # multiworld item pickups.
        rom_data.write_bytes(NEW_ITEM_TEXT_IDS_START, rom_data.read_bytes(ITEM_TEXT_IDS_START, ITEM_TEXT_IDS_LENGTH))
        rom_data.write_bytes(NEW_ITEM_TEXT_IDS_START + ITEM_TEXT_IDS_LENGTH, [0x30, 0x02, 0x32, 0x02, 0x34, 0x02,
                                                                              0x36, 0x02, 0x39, 0x02])
        # Update all the pointers to the above array of string IDs.
        item_text_ids_ptr_bytes = int.to_bytes(NEW_ITEM_TEXT_IDS_START | GBA_ROM_START, 4, "little")
        rom_data.write_bytes(0x19E34, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x19FA8, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x1A250, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x1A45C, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x286EC, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x28744, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x289A4, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x28B54, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x298CC, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x29C80, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x29EA0, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x2A8D0, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x2B468, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x2B568, item_text_ids_ptr_bytes)
        rom_data.write_bytes(0x2C730, item_text_ids_ptr_bytes)

        # Prevent furniture pickups with indexes over 0x1E from going into the inventory and play a different sound with
        # Trap items being picked up.
        rom_data.write_bytes(0x1A1D0, [0x00, 0x4B,  # ldr r3, 0x86A1000
                                       0x9F, 0x46,  # mov r15, r3
                                       0x00, 0x34, 0x6A, 0x08])
        rom_data.write_bytes(0x6A3400, patches.furniture_pickup_customizer)

        # Set the "can warp castles" flag when picking up JB's Bracelet.
        rom_data.write_bytes(0x19F84, [0x00, 0x4B,  # ldr r3, 0x86A4000
                                       0x9F, 0x46,  # mov r15, r3
                                       0x00, 0x40, 0x6A, 0x08])
        rom_data.write_bytes(0x6A4000, patches.jb_bracelet_checker)

        # Disable the text when both warping and teleporting to Castle B for the first time.
        rom_data.write_bytes(0x1BEC8, [0x00, 0x00])
        rom_data.write_byte(0x7645, 0xE0)

        # Make the warp room round gates always spawn in their closed states regardless of the Clock Tower Death
        # cutscene flag being set or not.
        rom_data.write_byte(0x1BAF9, 0xE0)

        # Block usage of the cross-castle round gate if they don't have the cross-castle warp condition satisfied.
        rom_data.write_bytes(0x1BC34, [0x00, 0x4A,  # ldr r2, 0x86A4700
                                       0x97, 0x46,  # mov r15, r2
                                       0x00, 0x47, 0x6A, 0x08])
        rom_data.write_bytes(0x6A4700, patches.cross_castle_warp_blocker)

        # Block warping to a warp room the player hasn't been to yet in the current castle if they don't have the
        # cross-castle warp condition satisfied.
        rom_data.write_bytes(0x9C30, [0x00, 0x48,  # ldr r0, 0x86A4500
                                      0x87, 0x46,  # mov r15, r0
                                      0x00, 0x45, 0x6A, 0x08])
        rom_data.write_bytes(0x6A4500, patches.unvisited_warp_destination_blocker)

        # Nuke the Clock Tower Death cutscene event.
        rom_data.write_bytes(0x4AAF98, [0xFF, 0x7F, 0xFF, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # Make MK's Bracelet doors unlockable in Castle B.
        rom_data.write_byte(0x1CD09, 0xE0)

        # Allow warping between warp rooms without seeing the post-Shadow Maxim cutscene in Sky Walkway A first.
        rom_data.write_byte(0x1BD37, 0xE0)

        # Prevent starting with JB's Bracelet already equipped.
        rom_data.write_byte(0x6B76E, 0xFF)

        # Update the Hint Card description pointers to point to the new AP hint strings.
        for i in range(6):
            rom_data.write_bytes(TEXT_POINTERS_START + ((0x107 + i) * 4),
                                 int.to_bytes(AP_HINT_TEXT_START + (i * 0x100) | GBA_ROM_START, 4, "little"))

        # Add the ability to set your spawn location to the start while saving.
        rom_data.write_bytes(0xBA58, [0x00, 0x49,  # ldr r1, 0x86A6000
                                      0x8F, 0x46,  # mov r15, r1
                                      0x00, 0x60, 0x6A, 0x08])
        rom_data.write_bytes(0x6A6000, patches.start_spawn_setter)

        # Change the "Quick Save now?" text to tell the player about the new start spawn setter.
        # NOTE: For some reason, this pause screen INFORMATION textbox doesn't support placing newlines manually, so we
        # have to rely on the game's own text auto-wrap feature to get text onto the second line.
        rom_data.write_bytes(0x495E70, int.to_bytes(START_SPAWN_SET_TEXT_START | GBA_ROM_START, 4, "little"))
        rom_data.write_bytes(START_SPAWN_SET_TEXT_START,
                             cvhodis_string_to_bytearray("Hold R while the game saves to set your   "
                                                         "spawn location back to start.\t",
                                                         len_limit=LEN_LIMIT_DESCRIPTION, wrap=False,
                                                         max_lines=DESCRIPTION_DISPLAY_LINES, textbox_advance=False))

        # Test
        # rom_data.write_bytes(0xCAA16, cvhodis_string_to_bytearray("❖1/⬘0      Howdy ✨6/@everyone✨8/!\nHow do you do?\nNice\n✨12/weather✨8/\ntoday!\nPretty\ngr8\nm8\nI\nr8\n8/8\rHave a free🅰 trial of the critically acclamied MMORPG ✨13/Final Fantasy XIV✨8/,🅰\rincluding the entirety🅰\rof ✨14/A Realm Reborn✨8/ and the award-winning ✨4/Heavansward✨8/ ~and~ ✨4/Stormblood✨8/ expansions up to ✨10/level 70✨8/ with ✨13/no restrictions on playtime✨8/! REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE▶1/EEEEEEEE✨2/EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE✨6/EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE✨9/EEEEEEE✨15/EEEEE✨3/EEEEEEEEEEEEEEEEEEEE✨5/EEEEEEE✨7/EEEEEE✨13/EEEEEEEEEEEEEE!!!✨6/!!!✨7/!!!!✨6/1✨8/🅰\f❖2/⬘1/Okay, Juste, I get it! Are you done now? Take a \b22/ or something!🅰\f\t"))

        # Go anywhere
        # rom_data.write_bytes(0x498EC8, int.to_bytes(0x084AD3D0, 4, "little"))
        # rom_data.write_bytes(0x498ECE, [0x54, 0x00])

        return rom_data.get_bytes()

    @staticmethod
    def fix_guardian_drops(caller: APProcedurePatch, rom: bytes) -> bytes:
        """After writing all the items into the ROM via token application, checks the Guardian Grinder cutscene item
        placements for any Max Ups. If there are any, then that item's hardcoded spawn function call will be changed to
        instead be the specific spawn function meant for Max Ups. Max Ups CANNOT go through the regular spawn function
        meant for most other pickups."""
        rom_data = RomData(rom)

        for guardian_loc in GUARDIAN_GRINDER_LOCATIONS:
            if rom_data.read_byte(GUARDIAN_GRINDER_LOCATIONS[guardian_loc]) == PICKUP_TYPE_MAX:
                # Change the mov instruction to put the Max Up's pickup index in the r2 register instead of r3, where
                # the "Spawn Max Up" function expects it to be.
                rom_data.write_byte(GUARDIAN_GRINDER_LOCATIONS[guardian_loc] + 3, 0x22)
                # Make the bl instruction go further backward by 0x54, where the "Spawn Max Up" function begins.
                rom_data.write_bytes(GUARDIAN_GRINDER_LOCATIONS[guardian_loc] + 6, int.to_bytes(int.from_bytes(
                    rom_data.read_bytes(GUARDIAN_GRINDER_LOCATIONS[guardian_loc] + 6, 2), "little") - 0x54,
                                                                                                2, "little"))

        return rom_data.get_bytes()


class CVHoDisProcedurePatch(APProcedurePatch, APTokenMixin):
    hash = [CVHODIS_CT_US_HASH, CVHODIS_AC_US_HASH]
    patch_file_ending: str = ".apcvhodis"
    result_file_ending: str = ".gba"

    game = "Castlevania - Harmony of Dissonance"

    procedure = [
        ("apply_patches", ["options.json"]),
        ("apply_tokens", ["token_data.bin"]),
        ("fix_guardian_drops", [])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def patch_rom(world: "CVHoDisWorld", patch: CVHoDisProcedurePatch, offset_data: Dict[int, bytes]) -> None:
    # Write all the new item values
    for offset, data in offset_data.items():
        patch.write_token(APTokenTypes.WRITE, offset, data)

    # Write the secondary name the client will use to distinguish a vanilla ROM from an AP one.
    patch.write_token(APTokenTypes.WRITE, ARCHIPELAGO_IDENTIFIER_START, ARCHIPELAGO_IDENTIFIER.encode("utf-8"))
    # Write the slot authentication
    patch.write_token(APTokenTypes.WRITE, AUTH_NUMBER_START, bytes(world.auth))

    patch.write_file("token_data.bin", patch.get_token_binary())

    # Write these slot options to a JSON.
    options_dict = {
        "required_furniture": world.furniture_amount_required,
        "seed": world.multiworld.seed,
        "compat_identifier": ARCHIPELAGO_IDENTIFIER
    }

    patch.write_file("options.json", json.dumps(options_dict).encode('utf-8'))


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if basemd5.hexdigest() not in [CVHODIS_CT_US_HASH, CVHODIS_AC_US_HASH]:
            raise Exception("Supplied Base ROM does not match known MD5s for Castlevania: Harmony of Dissonance USA."
                            "Get the correct game and version, then dump it.")
        setattr(get_base_rom_bytes, "base_rom_bytes", base_rom_bytes)
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    if not file_name:
        file_name = get_settings()["cvhodis_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name
