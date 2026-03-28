import pathlib
import struct

import Utils
import json

from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
from typing import Dict, Collection, TYPE_CHECKING

import hashlib
import os

from .data import patches, loc_names
from .data.enums import ActorTypes, PickupTypes
from .data.misc_names import GAME_NAME
from .entrances import CVHoDisTransitionData, SHUFFLEABLE_TRANSITIONS, VERTICAL_GROUPS, VERTICAL_SHAFT_EXITS, \
    LEFT_GROUPS, RIGHT_GROUPS, TOP_GROUPS, BOTTOM_GROUPS
from .locations import CVHODIS_LOCATIONS_INFO, GUARDIAN_GRINDER_LOCATIONS
from .options import CastleWarpCondition
from .cvhodis_text import cvhodis_string_to_bytearray, LEN_LIMIT_DESCRIPTION, DESCRIPTION_DISPLAY_LINES
from .patcher import CVHoDisRomPatcher, GBA_ROM_START
from settings import get_settings

if TYPE_CHECKING:
    from . import CVHoDisWorld

CVHODIS_CT_US_HASH = "ea589465486d15e91ba94165c8024b55"  # Original GBA cartridge ROM
CVHODIS_AC_US_HASH = "35db4a2bacdec253672db68e73a41005"  # Castlevania Advance Collection ROM

USER_PATCHES_FOLDER_NAME = "cvhodis_user_patches"

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
ARCHIPELAGO_PATCH_COMPAT_VER = 2
ARCHIPELAGO_CLIENT_COMPAT_VER = "ARCHIPELAG03"
AUTH_NUMBER_START = 0x7FFF10
QUEUED_TEXT_STRING_START = 0x7CEB00
MULTIWORLD_TEXTBOX_POINTERS_START = 0x671C10
ROM_PADDING_START = 0x69D400

class CVHoDisPatchExtensions(APPatchExtension):
    game = GAME_NAME

    @staticmethod
    def patch_rom(caller: APProcedurePatch, input_rom: bytes, slot_patch_file) -> bytes:
        """Patches the game into its rando state."""
        patcher = CVHoDisRomPatcher(bytearray(input_rom))
        slot_patch_info = json.loads(caller.get_file(slot_patch_file).decode("utf-8"))

        # Check to see if the patch was generated on a compatible APWorld version.
        # If the Slot Patch Info doesn't contain a "patch compatibility" key, or if it does, but the compatibility
        # version doesn't match with this APWorld's, consider it incompatible.
        compatible = True
        if "patch compatibility" in slot_patch_info:
            if slot_patch_info["patch compatibility"] != ARCHIPELAGO_PATCH_COMPAT_VER:
                compatible = False
        else:
            compatible = False

        # If incompatible, stop executing and raise an exception.
        if not compatible:
            raise Exception("Incompatible patch/APWorld version. Please verify your Harmony of Dissonance APWorld "
                            "matches the one that generated this .apcvhodis file, and (preferably) that both are "
                            "up-to-date.")

        # Re encode the start inventory arrays back into bytes (because we converted them to string format to be JSON
        # serializable).
        for array_id, inv_array in slot_patch_info["start inventory"]["inv arrays"].items():
            slot_patch_info["start inventory"]["inv arrays"][array_id] = inv_array.encode("utf-8")

        # Apply any user-supplied patch in a dedicated folder at the root of their Archipelago installation
        # (after checking to see if it exists).
        user_patch_folder_path = Utils.local_path(USER_PATCHES_FOLDER_NAME)
        if pathlib.Path(user_patch_folder_path).is_dir():
            for patch_name in [file for file in os.listdir(user_patch_folder_path) if file.endswith(".ips")]:
                with open(os.path.join(user_patch_folder_path, patch_name), "rb") as patch:
                    patcher.apply_ips(patch.read())

        # Get the dictionaries of item values mapped to their location IDs and relevant name texts out of the slot
        # patch info and convert each location ID key from a string into an int.
        loc_values = {int(loc_id): item_value for loc_id, item_value in slot_patch_info["location values"].items()}
        # loc_text = {int(loc_id): item_names for loc_id, item_names in slot_patch_info["location text"].items()}

        # Extract the camera coordinates that are associated with the location of each transition. These are gotten
        # from the other loading zone that normally connects to that transition.
        trans_camera_coords = {}
        for trans_name in SHUFFLEABLE_TRANSITIONS:
            other_trans_data = SHUFFLEABLE_TRANSITIONS[trans_name].destination_transition
            trans_camera_coords[trans_name] = [
                patcher.areas[SHUFFLEABLE_TRANSITIONS[other_trans_data].area_id][
                    SHUFFLEABLE_TRANSITIONS[other_trans_data].room_id][0]["loading_zone_list"][
                    SHUFFLEABLE_TRANSITIONS[other_trans_data].zone_id]["camera_x_pos"],
                patcher.areas[SHUFFLEABLE_TRANSITIONS[other_trans_data].area_id][
                    SHUFFLEABLE_TRANSITIONS[other_trans_data].room_id][0]["loading_zone_list"][
                    SHUFFLEABLE_TRANSITIONS[other_trans_data].zone_id]["camera_y_pos"]]
            # If the Y position is higher than 0 and ends with a 00 byte, add 0x30 so that the door should be right in
            # the middle of the camera. We need to do this to ensure transitioning through a bottom floor loading zone
            # will allow us to reach this entrance properly.
            if trans_camera_coords[trans_name][1] and not trans_camera_coords[trans_name][1] & 0xFF:
                trans_camera_coords[trans_name][1] += 0x30

        # Unlock all extras from the start (cutscene skipping, playable Maxim, Boss Rush, etc.).
        patcher.write_bytes(0x1FF4, [0x00, 0x49,  # ldr r1, 0x86A1000
                                     0x8F, 0x46,  # mov r15, r1
                                     0x00, 0x10, 0x6A, 0x08])
        patcher.write_bytes(0x6A1000, patches.extras_unlocker)

        # Add capabilities to remotely receive any item.
        patcher.write_bytes(0x754C, [0x00, 0x4A,  # ldr r2, 0x86A2000
                                      0x97, 0x46,  # mov r15, r2
                                      0x00, 0x20, 0x6A, 0x08])
        patcher.write_bytes(0x6A2000, patches.remote_textbox_shower)

        # Make spawning pickups with custom palettes default to the always-loaded OBP1 palette if there are already
        # 2 custom item palettes loaded instead of despawning.
        patcher.write_bytes(0x197D0, [0x00, 0x49,  # ldr r1, 0x86A0100
                                       0x8F, 0x46,  # mov r15, r1
                                       0x00, 0x01, 0x6A, 0x08])
        patcher.write_bytes(0x6A0100, patches.item_palette_defaulter)

        # Fix the MK's Bracelet check cutscene softlocking you if it gives you something that isn't MK's Bracelet.
        # Change the pointer to the actor data in the Sky Walkway A post-Shadow Maxim meeting room.
        patcher.write_bytes(SWA7_ALT_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_LOCATIONS_INFO[loc_names.swa7].offset - 0xC) | GBA_ROM_START, 4, "little"))
        # Copy the actor data over to the new location and insert a new actor for a pre-placed MK's Bracelet pickup.
        patcher.write_bytes(CVHODIS_LOCATIONS_INFO[loc_names.swa7].offset - 0xC,
                             list(patcher.read_bytes(MK_ACTORS_START, 0xC)) +
                             [0x38, 0x00,  # X position
                              0x90, 0x00,  # Y position
                              0xC1,  # Unique ID/Type
                              0x05,  # Subtype
                              0x00, 0x00,  # Not used
                              CVHODIS_LOCATIONS_INFO[loc_names.swa7].code, 0x00,  # Pickup flag
                              0x2C, 0x00]  # Item index
                             + list(patcher.read_bytes(MK_ACTORS_START + 0xC, 0xC)))
        # NOP the calls to the spawn pickup function so that the cutscene spawns nothing.
        # Useless fun fact: you can get two MK Bracelets in the vanilla game by only skipping the cutscene after the
        # game spawns one during it, which spawns a second one!
        patcher.write_bytes(0x2DE08, [0x00, 0x00, 0x00, 0x00])
        patcher.write_bytes(0x2DE74, [0x00, 0x00, 0x00, 0x00])
        # NOP the BEQ that checks to see if MK's Bracelet is in the inventory before ending the cutscene.
        patcher.write_bytes(0x2DE24, [0x00, 0x00])

        # Change the flag value of the Treasury B portal staircase bottom to be unique from its cousin in Treasury A.
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.cyb8].offset + 0x08, CVHODIS_LOCATIONS_INFO[loc_names.cyb8].code)

        # Put the upper Entrance, lower Treasury, and Luminous (all A) warp rooms on their own actor lists instead of
        # them all pointing to the exact same one, and make the pickup actor's flag in each one unique.
        warp_a_basic_actors = patcher.read_bytes(WARP_A_ACTORS_START, 0x30)

        patcher.write_bytes(ETA18_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_LOCATIONS_INFO[loc_names.eta18].offset - 0x18) | GBA_ROM_START,
                                          4, "little"))
        patcher.write_bytes(CVHODIS_LOCATIONS_INFO[loc_names.eta18].offset - 0x18, warp_a_basic_actors)
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.eta18].offset + 0x08, CVHODIS_LOCATIONS_INFO[loc_names.eta18].code)
        patcher.write_bytes(CYA4_ROOM_INFO_START + 0x18,
                            int.to_bytes((CVHODIS_LOCATIONS_INFO[loc_names.cya4].offset - 0x18) | GBA_ROM_START,
                                          4, "little"))
        patcher.write_bytes(CVHODIS_LOCATIONS_INFO[loc_names.cya4].offset - 0x18, warp_a_basic_actors)
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.cya4].offset + 0x08, CVHODIS_LOCATIONS_INFO[loc_names.cya4].code)
        patcher.write_bytes(LCA11_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_LOCATIONS_INFO[loc_names.lca11].offset - 0x18) | GBA_ROM_START,
                                          4, "little"))
        patcher.write_bytes(CVHODIS_LOCATIONS_INFO[loc_names.lca11].offset - 0x18, warp_a_basic_actors)
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.lca11].offset + 0x08, CVHODIS_LOCATIONS_INFO[loc_names.lca11].code)
        # Change the X position of the "right" upper Treasury A item and make its flag unique.
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.cya20a].offset, 0xB0)
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.cya20a].offset + 0x08, CVHODIS_LOCATIONS_INFO[loc_names.cya20a].code)
        # Make the flag of the before Panzuzu warp room pickup unique.
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.tfa15].offset + 0x08, CVHODIS_LOCATIONS_INFO[loc_names.tfa15].code)

        # Put the portal rooms between Luminous B and Walkway A on their own actor list and make the pickup flag on the
        # item in these rooms unique from the other pair's.
        portal_actors = patcher.read_bytes(PORTAL_ACTORS_START, 0x24)
        patcher.write_bytes(LCA23_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_LOCATIONS_INFO[loc_names.portals_lw].offset - 0xC) | GBA_ROM_START,
                                          4, "little"))
        patcher.write_bytes(SWA19_ROOM_INFO_START + 0x18,
                             int.to_bytes((CVHODIS_LOCATIONS_INFO[loc_names.portals_lw].offset - 0xC) | GBA_ROM_START,
                                          4, "little"))
        patcher.write_bytes(CVHODIS_LOCATIONS_INFO[loc_names.portals_lw].offset - 0xC, portal_actors)
        patcher.write_byte(CVHODIS_LOCATIONS_INFO[loc_names.portals_lw].offset + 0x08,
                            CVHODIS_LOCATIONS_INFO[loc_names.portals_lw].code)

        # Add the GFX for the AP Items.
        for offset, data in patches.extra_item_sprites.items():
            patcher.write_bytes(offset, data)

        # Add the "Archipelago Item" text over one of the NULL enemy names.
        patcher.write_bytes(0xD8FEC, cvhodis_string_to_bytearray("Filler Item\n\t"))
        patcher.write_bytes(0xD900C, cvhodis_string_to_bytearray("Useful Item\n\t"))
        patcher.write_bytes(0xD902C, cvhodis_string_to_bytearray("Trap Item\n\t"))
        patcher.write_bytes(0xD904C, cvhodis_string_to_bytearray("Progression Item\n\t"))
        patcher.write_bytes(0xD907C, cvhodis_string_to_bytearray("Prog-Useful Item\n\t"))

        # Move the Spell Book info table and expand it with an extra entry for our Progression item.
        patcher.write_bytes(0x19798, int.to_bytes(NEW_BOOK_INFO_START | GBA_ROM_START, 4, "little"))
        patcher.write_bytes(0x1A020, int.to_bytes(NEW_BOOK_INFO_START | GBA_ROM_START, 4, "little"))
        patcher.write_bytes(NEW_BOOK_INFO_START, patcher.read_bytes(BOOK_INFO_START, BOOK_INFO_LENGTH))
        patcher.write_bytes(NEW_BOOK_INFO_START + BOOK_INFO_LENGTH, [0xD8, 0x00, 0xE0, 0x01])  # Progression

        # Prevent auto-equipping Spell Books with a value higher than 5.
        patcher.write_bytes(0x1A046, [0xED, 0xE7])  # b    [backward 0x12]
        patcher.write_bytes(0x1A024, [0x05, 0x28,   # cmp r0, 5
                                       0x0F, 0xD8,   # bhi  [forward 0x10]
                                       0xF8, 0x73,   # strb r0, [r7, 0x0F]
                                       0x0D, 0xE0])  # b    [forward 0x0E]

        # Move the relic info table and expand it with an extra entry for our Prog + Useful item.
        patcher.write_bytes(0x197A4, int.to_bytes(NEW_RELIC_INFO_START | GBA_ROM_START, 4, "little"))
        patcher.write_bytes(0x1A0F0, int.to_bytes(NEW_RELIC_INFO_START | GBA_ROM_START, 4, "little"))
        patcher.write_bytes(NEW_RELIC_INFO_START, patcher.read_bytes(RELIC_INFO_START, RELIC_INFO_LENGTH))
        patcher.write_bytes(NEW_RELIC_INFO_START + RELIC_INFO_LENGTH, [0xD9, 0x00, 0xE2, 0x01])  # Prog + Useful

        # Move the furniture info table and expand it with three more entries for our Filler, Useful, and Trap items.
        furn_info_ptr_bytes = int.to_bytes(NEW_FURNITURE_INFO_START | GBA_ROM_START, 4, "little")
        patcher.write_bytes(0x197E4, furn_info_ptr_bytes)
        patcher.write_bytes(0x19E30, furn_info_ptr_bytes)
        patcher.write_bytes(0x19EE8, furn_info_ptr_bytes)
        patcher.write_bytes(0x19FA4, furn_info_ptr_bytes)
        patcher.write_bytes(0x1A068, furn_info_ptr_bytes)
        patcher.write_bytes(0x1A134, furn_info_ptr_bytes)
        patcher.write_bytes(0x1A24C, furn_info_ptr_bytes)
        patcher.write_bytes(0x1A458, furn_info_ptr_bytes)
        patcher.write_bytes(0x2A8CC, furn_info_ptr_bytes)
        patcher.write_bytes(0x2AA24, furn_info_ptr_bytes)
        patcher.write_bytes(0x2AAD0, furn_info_ptr_bytes)
        patcher.write_bytes(NEW_FURNITURE_INFO_START, patcher.read_bytes(FURNITURE_INFO_START, FURNITURE_INFO_LENGTH))
        patcher.write_bytes(NEW_FURNITURE_INFO_START + FURNITURE_INFO_LENGTH, [0xD5, 0x00, 0xDF, 0x01,   # Filler
                                                                                0xD6, 0x00, 0xE1, 0x01,   # Useful
                                                                                0xD7, 0x00, 0xE3, 0x01])  # Trap

        # Move the array of string IDs that the pickup textbox can normally access and add the extra IDs for the
        # multiworld item pickups.
        patcher.write_bytes(NEW_ITEM_TEXT_IDS_START, patcher.read_bytes(ITEM_TEXT_IDS_START, ITEM_TEXT_IDS_LENGTH))
        patcher.write_bytes(NEW_ITEM_TEXT_IDS_START + ITEM_TEXT_IDS_LENGTH, [0x30, 0x02, 0x32, 0x02, 0x34, 0x02,
                                                                              0x36, 0x02, 0x39, 0x02])
        # Update all the pointers to the above array of string IDs.
        item_text_ids_ptr_bytes = int.to_bytes(NEW_ITEM_TEXT_IDS_START | GBA_ROM_START, 4, "little")
        patcher.write_bytes(0x19E34, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x19FA8, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x1A250, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x1A45C, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x286EC, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x28744, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x289A4, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x28B54, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x298CC, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x29C80, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x29EA0, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x2A8D0, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x2B468, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x2B568, item_text_ids_ptr_bytes)
        patcher.write_bytes(0x2C730, item_text_ids_ptr_bytes)

        # Prevent furniture pickups with indexes over 0x1E from going into the inventory and play a different sound with
        # Trap items being picked up.
        patcher.write_bytes(0x1A1D0, [0x00, 0x4B,  # ldr r3, 0x86A1000
                                       0x9F, 0x46,  # mov r15, r3
                                       0x00, 0x34, 0x6A, 0x08])
        patcher.write_bytes(0x6A3400, patches.furniture_pickup_customizer)

        # Play the "major pickup" sound when picking up JB's Bracelet.
        patcher.write_bytes(0x19F84, [0x00, 0x4B,  # ldr r3, 0x86A4000
                                       0x9F, 0x46,  # mov r15, r3
                                       0x00, 0x40, 0x6A, 0x08])
        patcher.write_bytes(0x6A4000, patches.major_pickup_sound_player)

        # Disable the text when using a teleport to Castle B for the first time.
        patcher.write_byte(0x7645, 0xE0)

        # Block usage of the cross-castle round gate if they don't have the "cross-castle warp condition satisfied"
        # flag set.
        if slot_patch_info["options"]["castle_warp_condition"] != CastleWarpCondition.option_none:
            patcher.write_bytes(0x1BC34, [0x00, 0x4A,  # ldr r2, 0x86A4700
                                           0x97, 0x46,  # mov r15, r2
                                           0x00, 0x47, 0x6A, 0x08])
            if slot_patch_info["options"]["double_sided_warps"]:
                patcher.write_bytes(0x6A4700, patches.double_sided_cross_castle_warp_blocker)
            else:
                patcher.write_bytes(0x6A4700, patches.cross_castle_warp_blocker)

            # Block warping to a warp room the player hasn't been to yet in the current castle if they don't have the
            # cross-castle warp condition satisfied.
            patcher.write_bytes(0x9C30, [0x00, 0x48,  # ldr r0, 0x86A4500
                                          0x87, 0x46,  # mov r15, r0
                                          0x00, 0x45, 0x6A, 0x08])
            patcher.write_bytes(0x6A4500, patches.unvisited_warp_destination_blocker)

        # Make the round warp gates set the "can warp castles" flag if the player has JB's Bracelet.
        if slot_patch_info["options"]["castle_warp_condition"] == CastleWarpCondition.option_bracelet:
            patcher.write_bytes(0x494F70, int.to_bytes(0x86A4101, 4, "little"))
            patcher.write_bytes(0x6A4100, patches.jb_bracelet_checker)

        # Nuke the Clock Tower Death cutscene event and the text when changing castles through a warp room for the
        # first time if the Castle Warp Condition is not Death. Otherwise, keep them.
        if slot_patch_info["options"]["castle_warp_condition"] != CastleWarpCondition.option_death:
            patcher.write_bytes(0x1BEC8, [0x00, 0x00])
            patcher.write_bytes(0x4AAF98, [0xFF, 0x7F, 0xFF, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            # Make the warp room round gates always spawn in their closed states regardless of the Clock Tower Death
            # cutscene flag being set or not.
            patcher.write_byte(0x1BAF9, 0xE0)
        else:
            # If the warp condition is Death, make the gates check to see if we're in Death's room upon
            # initialization.
            patcher.write_bytes(0x1BAFC, [0x00, 0x49,  # ldr r1, 0x86A4100
                                           0x8F, 0x46,  # mov r15, r1
                                           0x00, 0x41, 0x6A, 0x08])
            patcher.write_bytes(0x6A4100, patches.portal_death_room_checker)

        # Make MK's Bracelet doors unlockable in Castle B.
        patcher.write_byte(0x1CD09, 0xE0)

        # Allow warping between warp rooms without seeing the post-Shadow Maxim cutscene in Sky Walkway A first.
        patcher.write_byte(0x1BD37, 0xE0)

        # Prevent starting with JB's Bracelet already equipped.
        patcher.write_byte(0x6B76E, 0xFF)

        # Update the Hint Card description pointers to point to the new AP hint strings.
        for i in range(6):
            patcher.write_bytes(TEXT_POINTERS_START + ((0x107 + i) * 4),
                                 int.to_bytes(AP_HINT_TEXT_START + (i * 0x100) | GBA_ROM_START, 4, "little"))

        # Add the ability to set your spawn location to the start while saving.
        patcher.write_bytes(0xBA58, [0x00, 0x49,  # ldr r1, 0x86A6000
                                      0x8F, 0x46,  # mov r15, r1
                                      0x00, 0x60, 0x6A, 0x08])
        patcher.write_bytes(0x6A6000, patches.start_spawn_setter)

        # Change the "Quick Save now?" text to tell the player about the new start spawn setter.
        # NOTE: For some reason, this pause screen INFORMATION textbox doesn't support placing newlines manually, so we
        # have to rely on the game's own text auto-wrap feature to get text onto the second line.
        patcher.write_bytes(0x495E70, int.to_bytes(START_SPAWN_SET_TEXT_START | GBA_ROM_START, 4, "little"))
        patcher.write_bytes(START_SPAWN_SET_TEXT_START,
                             cvhodis_string_to_bytearray("Hold R while the game saves to set your   "
                                                         "spawn location back to start.\t",
                                                         len_limit=LEN_LIMIT_DESCRIPTION, wrap=False,
                                                         max_lines=DESCRIPTION_DISPLAY_LINES, textbox_advance=False))

        # Make the game auto-save after the intro with Talos.
        patcher.write_bytes(0x9554C, [0x00, 0x49,  # ldr r1, 0x86A6200
                                       0x8F, 0x46,  # mov r15, r1
                                       0x00, 0x62, 0x6A, 0x08])
        patcher.write_bytes(0x6A6200, patches.post_intro_autosave)
        # Custom autosave message.
        patcher.write_bytes(0xD91B4, cvhodis_string_to_bytearray("Autosaved\n\t"))

        # Give the player their Start Inventory upon starting a new game.
        # Write the player start inventories and record where they start.
        # Use Items
        start_inventory_use_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            slot_patch_info["start inventory"]["inv arrays"][str(PickupTypes.USE_ITEM)])
        # Equipment
        start_inventory_equip_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            slot_patch_info["start inventory"]["inv arrays"][str(PickupTypes.EQUIPMENT)])
        # Spellbooks and starting Spellbook
        start_inventory_book_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            slot_patch_info["start inventory"]["inv arrays"][str(PickupTypes.SPELLBOOK)] + \
            struct.pack("<B", slot_patch_info["start inventory"]["spellbook"]))
        # Relics
        start_inventory_relic_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            slot_patch_info["start inventory"]["inv arrays"][str(PickupTypes.RELIC)])
        # Furniture
        start_inventory_furn_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            slot_patch_info["start inventory"]["inv arrays"][str(PickupTypes.FURNITURE)])
        # Whip attachments
        start_inventory_whips_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            slot_patch_info["start inventory"]["inv arrays"][str(PickupTypes.WHIP_ATTACHMENT)])
        # Stat maxes
        start_inventory_max_start = GBA_ROM_START | patcher.find_space_and_write_buffer(
            bytearray(struct.pack("<H", slot_patch_info["start inventory"]["extra life"]) +
                      struct.pack("<H", slot_patch_info["start inventory"]["extra magic"]) +
                      struct.pack("<H", slot_patch_info["start inventory"]["extra hearts"])))
        # Write the start inventory giver hack with the above pointers to the start inventory arrays.
        patcher.generate_dynamic_asm(patches.start_inventory_giver_asm,
                                     patches.start_inventory_giver_ldr + [start_inventory_use_start,
                                                                          start_inventory_equip_start,
                                                                          start_inventory_book_start,
                                                                          start_inventory_relic_start,
                                                                          start_inventory_furn_start,
                                                                          start_inventory_whips_start,
                                                                          start_inventory_max_start],
                                     hook_addr=0x6B730, hook_register=1)

        # Terraform the left side of the Entrance -> Skeleton Cave floor transition to allow being placed there in ER.
        # Entrance A
        patcher.write_bytes(0x187486, [0x46, 0x00, 0x12, 0x00])
        patcher.write_bytes(0x187496, [0x50, 0x00, 0x40, 0x00, 0x1A, 0x00])
        patcher.write_bytes(0x1874A6, [0x50, 0x00, 0x31, 0x00, 0x41, 0x00])
        patcher.write_bytes(0x1874B6, [0x19, 0x00, 0x16, 0x00, 0x41, 0x00])
        # Entrance B
        patcher.write_bytes(0x1889E6, [0x67, 0x00, 0x88, 0x00])
        patcher.write_bytes(0x1889F6, [0x6B, 0x00, 0x0B, 0x00, 0x0B, 0x00])
        patcher.write_bytes(0x188A06, [0x6B, 0x00, 0x48, 0x00, 0x48, 0x00])
        patcher.write_bytes(0x188A16, [0x8C, 0x00, 0x89, 0x00, 0x52, 0x00])

        # Loop over EVERY room state and overwrite all pickups in their actor lists to be what they should be in the
        # player's slot.
        for area_id in range(len(patcher.areas)):
            for room_id in range(len(patcher.areas[area_id])):
                for room_state in patcher.areas[area_id][room_id]:
                    for actor in room_state["actor_list"]:
                        # If the actor is not a pickup, or if it's already marked for deletion, skip it.
                        if actor["type_id"] != ActorTypes.PICKUP or "delete" in actor:
                            continue
                        # Check if the flag ID (in the pickup's Var A) has Location values associated with it in the
                        # slot patch info. If it does, write those values in the pickup's Subtype and Var B.
                        if actor["var_a"] in loc_values:
                            actor["subtype_id"] = loc_values[actor["var_a"]][0]
                            actor["var_b"] = loc_values[actor["var_a"]][1]

        # Loop over every transition in the player's transitions list and link them all together in-game.
        for trans_pair in slot_patch_info["transition values"]:
            # Get the loading zone associated with the source transition.
            source_zone = patcher.areas[
                SHUFFLEABLE_TRANSITIONS[trans_pair[0]].area_id][SHUFFLEABLE_TRANSITIONS[trans_pair[0]].room_id][0][
                "loading_zone_list"][SHUFFLEABLE_TRANSITIONS[trans_pair[0]].zone_id]

            # Write the destination's room pointer and camera X and Y positions.
            source_zone["dest_room_ptr"] = patcher.areas[SHUFFLEABLE_TRANSITIONS[trans_pair[1]].area_id][
                SHUFFLEABLE_TRANSITIONS[trans_pair[1]].room_id][0]["start_addr"]
            source_zone["camera_x_pos"] = trans_camera_coords[trans_pair[1]][0]
            source_zone["camera_y_pos"] = trans_camera_coords[trans_pair[1]][1]

            # The player Y offset is way trickier; we need to take where on-screen they would be both before and after
            # the transition and shift the player accordingly. Unless it's a top transition connected to a bottom, in
            # which case we shift by 0.
            if SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in VERTICAL_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in VERTICAL_GROUPS:
                source_zone["player_y_offset"] = 0
            else:
                # Take the lower byte of the camera position plus the player's departing Y position to get the "true"
                # position that the game calculates from.
                player_y_entrance = (SHUFFLEABLE_TRANSITIONS[trans_pair[0]].player_depart_y_pos +
                                     trans_camera_coords[trans_pair[0]][1]) & 0xFF

                # If the position is or greater than or equal to 0xA0 (the very bottom-of-screen subpixel), "Pac-Man"
                # the value back up to the top.
                if player_y_entrance >= 0xA0:
                    player_y_entrance -= 0xA0

                # Take the difference between this value and the destination Y position to get the Y shift value to put
                # in the source loading zone's data.
                source_zone["player_y_offset"] = SHUFFLEABLE_TRANSITIONS[trans_pair[1]].player_arrive_y_pos - \
                                                 player_y_entrance

                # If the value is outside the (-)128-(+)127 range, set it to the range min or max as that's as far as
                # we are allowed to go.
                if source_zone["player_y_offset"] > 127:
                    source_zone["player_y_offset"] = 127
                elif source_zone["player_y_offset"] < -128:
                    source_zone["player_y_offset"] = -128

            # If the entrance is a vertical transition and the exit is in a 1-wide vertical room,
            # set -8 as the player X offset.
            if SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in VERTICAL_GROUPS and trans_pair[1] in VERTICAL_SHAFT_EXITS:
                source_zone["player_x_offset"] = -8
            # If the entrance is a vertical transition and the exit is on the left, set -104 as the player X offset.
            elif SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in VERTICAL_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in LEFT_GROUPS:
                source_zone["player_x_offset"] = -104
            # If the entrance is a vertical transition and the exit is on the right, set 88 as the player X offset.
            elif SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in VERTICAL_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in RIGHT_GROUPS:
                source_zone["player_x_offset"] = 88
            # If the entrance is on the right and the exit is on the top, set 127 as the player X offset.
            elif SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in RIGHT_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in TOP_GROUPS:
                source_zone["player_x_offset"] = 127
            # If the entrance is on the left and the exit is on the top, set -128 as the player X offset.
            elif SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in LEFT_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in TOP_GROUPS:
                source_zone["player_x_offset"] = -128
            # If the entrance is on the right and the exit is on the bottom, set 79 as the player X offset.
            elif SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in RIGHT_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in BOTTOM_GROUPS:
                source_zone["player_x_offset"] = 79
            # If the entrance is on the left and the exit is on the bottom, set -80 as the player X offset.
            elif SHUFFLEABLE_TRANSITIONS[trans_pair[0]].er_group in LEFT_GROUPS and \
                    SHUFFLEABLE_TRANSITIONS[trans_pair[1]].er_group in BOTTOM_GROUPS:
                source_zone["player_x_offset"] = -80
            # Otherwise, the player X offset should be 0.
            else:
                source_zone["player_x_offset"] = 0

        return patcher.get_output_rom()


        # Test
        # rom_data.write_bytes(0xCAA16, cvhodis_string_to_bytearray("❖1/⬘0      Howdy ✨6/@everyone✨8/!\nHow do you do?\nNice\n✨12/weather✨8/\ntoday!\nPretty\ngr8\nm8\nI\nr8\n8/8\rHave a free🅰 trial of the critically acclamied MMORPG ✨13/Final Fantasy XIV✨8/,🅰\rincluding the entirety🅰\rof ✨14/A Realm Reborn✨8/ and the award-winning ✨4/Heavansward✨8/ ~and~ ✨4/Stormblood✨8/ expansions up to ✨10/level 70✨8/ with ✨13/no restrictions on playtime✨8/! REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE▶1/EEEEEEEE✨2/EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE✨6/EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE✨9/EEEEEEE✨15/EEEEE✨3/EEEEEEEEEEEEEEEEEEEE✨5/EEEEEEE✨7/EEEEEE✨13/EEEEEEEEEEEEEE!!!✨6/!!!✨7/!!!!✨6/1✨8/🅰\f❖2/⬘1/Okay, Juste, I get it! Are you done now? Take a \b22/ or something!🅰\f\t"))

        # Go anywhere
        # rom_data.write_bytes(0x498EC8, int.to_bytes(0x084AA128, 4, "little"))
        # rom_data.write_bytes(0x498ECE, [0x54, 0x00])

    @staticmethod
    def fix_guardian_drops(caller: APProcedurePatch, rom: bytes) -> bytes:
        """After writing all the items into the ROM via token application, checks the Guardian Grinder cutscene item
        placements for any Max Ups. If there are any, then that item's hardcoded spawn function call will be changed to
        instead be the specific spawn function meant for Max Ups. Max Ups CANNOT go through the regular spawn function
        meant for most other pickups."""
        pass
        #rom_data = RomData(rom)

        #for guardian_loc in GUARDIAN_GRINDER_LOCATIONS:
        #    if rom_data.read_byte(GUARDIAN_GRINDER_LOCATIONS[guardian_loc]) == PickupTypes.MAX_UP:
                # Change the mov instruction to put the Max Up's pickup index in the r2 register instead of r3, where
                # the "Spawn Max Up" function expects it to be.
        #        rom_data.write_byte(GUARDIAN_GRINDER_LOCATIONS[guardian_loc] + 3, 0x22)
                # Make the bl instruction go further backward by 0x54, where the "Spawn Max Up" function begins.
        #        rom_data.write_bytes(GUARDIAN_GRINDER_LOCATIONS[guardian_loc] + 6, int.to_bytes(int.from_bytes(
        #            rom_data.read_bytes(GUARDIAN_GRINDER_LOCATIONS[guardian_loc] + 6, 2), "little") - 0x54,
        #                                                                                        2, "little"))

        #return rom_data.get_bytes()


class CVHoDisProcedurePatch(APProcedurePatch, APTokenMixin):
    hash = [CVHODIS_CT_US_HASH, CVHODIS_AC_US_HASH]
    patch_file_ending: str = ".apcvhodis"
    result_file_ending: str = ".gba"

    game = GAME_NAME

    procedure = [
        ("patch_rom", ["slot_patch_info.json"]),
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


#def patch_rom(world: "CVHoDisWorld", patch: CVHoDisProcedurePatch, offset_data: Dict[int, bytes]) -> None:
    # Write all the new item values
#    for offset, data in offset_data.items():
#        patch.write_token(APTokenTypes.WRITE, offset, data)

    # Write the secondary name the client will use to distinguish a vanilla ROM from an AP one.
#    patch.write_token(APTokenTypes.WRITE, ARCHIPELAGO_IDENTIFIER_START, ARCHIPELAGO_CLIENT_COMPAT_VER.encode("utf-8"))
    # Write the slot authentication
#    patch.write_token(APTokenTypes.WRITE, AUTH_NUMBER_START, bytes(world.auth))

#    patch.write_file("token_data.bin", patch.get_token_binary())

    # Write these slot options to a JSON.
#    options_dict = {
#        "required_furniture": world.furniture_amount_required,
#        "double_sided_warps": world.options.double_sided_warps.value,
#        "castle_warp_condition": world.options.castle_warp_condition.value,
#        "seed": world.multiworld.seed,
#        "compat_identifier": ARCHIPELAGO_CLIENT_COMPAT_VER
#    }

#    patch.write_file("options.json", json.dumps(options_dict).encode('utf-8'))


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
