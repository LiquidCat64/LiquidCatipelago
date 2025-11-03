import logging
import zlib
import json
import base64
import struct
import Utils

from BaseClasses import Location
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
from typing import List, Dict, Union, Iterable, TYPE_CHECKING

import hashlib
import os
# import pkgutil

from .data import patches, loc_names
from .data.enums import Scenes, NIFiles, Objects, ObjectExecutionFlags, ActorSpawnFlags, Items, Pickups, PickupFlags, \
    DoorFlags
from .locations import CVLOD_LOCATIONS_INFO
from .patcher import CVLoDRomPatcher, CVLoDSceneTextEntry, CVLoDNormalActorEntry, CVLoDDoorEntry, CVLoDPillarActorEntry, CVLoDLoadingZoneEntry, CVLoDEnemyPillarEntry, CVLoD1HitBreakableEntry, CVLoD3HitBreakableEntry, CVLoDSpawnEntranceEntry, SCENE_OVERLAY_RDRAM_START
from .stages import CVLOD_STAGE_INFO
from .cvlod_text import cvlod_string_to_bytearray, cvlod_text_wrap, cvlod_bytes_to_string, CVLOD_STRING_END_CHARACTER, \
    CVLOD_TEXT_POOL_END_CHARACTER
# from .aesthetics import renon_item_dialogue
# from .locations import CVLOD_LOCATIONS_INFO
from .options import StageLayout, VincentFightCondition, RenonFightCondition, PostBehemothBoss, RoomOfClocksBoss, \
    DuelTowerFinalBoss, CastleKeepEndingSequence, DeathLink, DraculasCondition, InvisibleItems, Countdown, \
    PantherDash, VillaBranchingPaths, CastleCenterBranchingPaths, CastleWallState, VillaState
from settings import get_settings

if TYPE_CHECKING:
    from . import CVLoDWorld

CVLOD_US_HASH = "25258460f98f567497b24844abe3a05b"

ARCHIPELAGO_IDENTIFIER_START = 0xFFFF00
ARCHIPELAGO_PATCH_IDENTIFIER = "ARCHIPELAG01"
AUTH_NUMBER_START = 0xFFFF10
QUEUED_TEXT_STRING_START = 0x7CEB00
MULTIWORLD_TEXTBOX_POINTERS_START = 0x671C10
ROM_PADDING_START = 0xFCC000
ROM_PADDING_BYTE = 0x00

START_INVENTORY_USE_START = 0x6A7200
START_INVENTORY_EQUIP_START = 0x6A7220
START_INVENTORY_BOOK_START = 0x6A72B0
START_INVENTORY_RELICS_START = 0x6A72B2
START_INVENTORY_FURN_START = 0x6A72B4
START_INVENTORY_WHIPS_START = 0x6A72B8
START_INVENTORY_MAX_START = 0x6A72BA

FOREST_OVL_CHARNEL_ITEMS_START = 0x7C60
CHARNEL_ITEM_LEN = 0xC
FIRST_CHARNEL_LID_ACTOR = 72

WARP_SCENE_OFFSETS = [0xADF67, 0xADF77, 0xADF87, 0xADF97, 0xADFA7, 0xADFBB, 0xADFCB, 0xADFDF]

SPECIAL_1HBS = [Objects.FOGGY_LAKE_ABOVE_DECKS_BARREL, Objects.FOGGY_LAKE_BELOW_DECKS_BARREL,
                Objects.SORCERY_BLUE_DIAMOND]

CC_CORNELL_INTRO_ACTOR_LISTS = {Scenes.CASTLE_CENTER_BASEMENT: "room 1",
                                Scenes.CASTLE_CENTER_BOTTOM_ELEV: "init",
                                Scenes.CASTLE_CENTER_FACTORY: "room 1",
                                Scenes.CASTLE_CENTER_LIZARD_LAB: "room 2"}


class CVLoDPatchExtensions(APPatchExtension):
    game = "Castlevania - Legacy of Darkness"

    @staticmethod
    def patch_rom(caller: APProcedurePatch, input_rom: bytes, slot_patch_file) -> bytes:
        patcher = CVLoDRomPatcher(bytearray(input_rom))
        slot_patch_info = json.loads(caller.get_file(slot_patch_file).decode("utf-8"))

        # Get the dictionary of item values mapped to their location IDs out of the slot patch info and convert each
        # location ID key from a string into an int.
        loc_values = {int(loc_id): item_value for loc_id, item_value in slot_patch_info["location values"].items()}


        # # # # # # # # #
        # GENERAL EDITS #
        # # # # # # # # #
        # NOP out the CRC BNEs
        patcher.write_int32(0x66C, 0x00000000)
        patcher.write_int32(0x678, 0x00000000)

        # Initial Countdown numbers and Start Inventory
        patcher.write_int32(0x90DBC, 0x080FF200)  # J	0x803FC800
        patcher.write_int32s(0xFFC800, patches.new_game_extras)

        # Everything related to the Countdown counter.
        if slot_patch_info["options"]["countdown"]:
            patcher.write_int32(0x1C670, 0x080FF141)  # J 0x803FC504
            patcher.write_int32(0x1F11C, 0x080FF147)  # J 0x803FC51C
            patcher.write_int32s(0xFFC3C0, patches.countdown_number_displayer)
            patcher.write_int32s(0xFFC4D0, patches.countdown_number_manager)
            patcher.write_int32(0x877E0, 0x080FF18D)  # J 0x803FC634
            patcher.write_int32(0x878F0, 0x080FF188)  # J 0x803FC620
            patcher.write_int32s(0x8BFF0, [0x0C0FF192,  # JAL 0x803FC648
                                            0xA2090000])  # SB  T1, 0x0000 (S0)
            patcher.write_int32s(0x8C028, [0x0C0FF199,  # JAL 0x803FC664
                                            0xA20E0000])  # SB  T6, 0x0000 (S0)
            patcher.write_int32(0x108D80, 0x0C0FF1A0)  # JAL 0x803FC680

        # Kills the pointer to the Countdown number, resets the "in a demo?" value whenever changing/reloading the
        # game state, and mirrors the current game state value in a spot that's easily readable.
        patcher.write_int32(0x1168, 0x08007938)  # J 0x8001E4E0
        patcher.write_int32s(0x1F0E0, [0x3C08801D,  # LUI   T0, 0x801D
                                        0xA104AA30,  # SB    A0, 0xAA30 (T0)
                                        0xA100AA4A,  # SB    R0, 0xAA4A (T0)
                                        0x03E00008,  # JR    RA
                                        0xFD00AA40])  # SD    R0, 0xAA40 (T0)

        # Make changing the map ID to 0xFF reset the map (helpful to work around a bug wherein the camera gets stuck
        # when entering a loading zone that doesn't change the map) or changing the spawn ID to 0x40 or 0x80 to go to a
        # decoupled version of the Spider Queen or Medusa arena respectively.
        patcher.write_int32s(0x1C3B4, [0x0C0FF304,    # JAL   0x803FCC10
                                        0x24840008]),  # ADDIU A0, A0, 0x0008
        patcher.write_int32s(0xFFCC10, patches.map_refresher)

        # Add keys in an AP logo formation to the title screen.
        patcher.scenes[Scenes.INTRO_NARRATION].actor_lists["proxy"] += [
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=0.0, y_pos=3.8, z_pos=0.0, execution_flags=0,
                                  object_id=Objects.PICKUP_ITEM, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.LEFT_TOWER_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=-3.6, y_pos=1.8, z_pos=-2.8, execution_flags=0,
                                  object_id=Objects.PICKUP_ITEM, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.STOREROOM_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=3.6, y_pos=1.8, z_pos=2.8, execution_flags=0,
                                  object_id=Objects.PICKUP_ITEM, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.COPPER_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=-3.6, y_pos=-2.2, z_pos=-2.8, execution_flags=0,
                                  object_id=Objects.PICKUP_ITEM, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.CHAMBER_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=3.6, y_pos=-2.2, z_pos=2.8, execution_flags=0,
                                  object_id=Objects.PICKUP_ITEM, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.EXECUTION_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=0.0, y_pos=-4.2, z_pos=0.0, execution_flags=0,
                                  object_id=Objects.PICKUP_ITEM, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.ARCHIVES_KEY, var_d=0, extra_condition_ptr=0),
            ]

        # Unlock Hard Mode and all characters and costumes from the start.
        patcher.write_int32(0x244, 0x00000000, NIFiles.OVERLAY_CHARACTER_SELECT)
        patcher.write_int32(0x1DE4, 0x00000000, NIFiles.OVERLAY_NECRONOMICON)
        patcher.write_int32(0x1E28, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        patcher.write_int32(0x1FF8, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        patcher.write_int32(0x2000, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        patcher.write_int32(0x2008, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        patcher.write_int32(0x96C, 0x240D4000, NIFiles.OVERLAY_CHARACTER_SELECT)
        patcher.write_int32(0x994, 0x00000000, NIFiles.OVERLAY_CHARACTER_SELECT)
        patcher.write_int32(0x9C0, 0x00000000, NIFiles.OVERLAY_CHARACTER_SELECT)
        patcher.write_int32s(0x18E8, [0x3C0400FF,
                                      0x3484FF00,
                                      0x00045025], NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        patcher.write_int32s(0x19A0, [0x3C0400FF,
                                      0x3484FF00,
                                      0x00044025], NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)

        # Prevent event flags from pre-setting themselves in Henry Mode.
        patcher.write_byte(0x22F, 0x04, NIFiles.OVERLAY_HENRY_NG_INITIALIZER)
        # Give Henry all the time in the world just like everyone else.
        patcher.write_byte(0x86DDF, 0x04)
        # Make the Henry teleport jewels work for everyone at the expense of the light effect surrounding them.
        # The code that creates and renders it is exclusively inside Henry's overlay, so it must be tossed for the actor
        # to function for the rest of the characters, sadly.
        patcher.write_int32(0xF6A5C, 0x00000000)  # NOP

        # Custom data-loading code
        patcher.write_int32(0x18A94, 0x0800793D)  # J 0x8001E4F4
        patcher.write_int32s(0x1F0F4, patches.custom_code_loader)

        # Custom remote item rewarding and DeathLink receiving code
        patcher.write_int32(0x1C854, 0x080FF000)  # J 0x803FC000
        patcher.write_int32s(0xFFC000, patches.remote_item_giver)
        patcher.write_int32s(0xFFE190, patches.subweapon_surface_checker)

        # Change the starting stage to whatever stage the player is actually starting at.
        patcher.write_byte(0x15DB, CVLOD_STAGE_INFO[slot_patch_info["stages"][0]["name"]].start_scene_id,
                           NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        patcher.write_byte(0x15D3, CVLOD_STAGE_INFO[slot_patch_info["stages"][0]["name"]].start_spawn_id,
                           NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        patcher.write_byte(0x15DB, 0x15, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        patcher.write_byte(0x15D3, 0x00, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        # Change the instruction that stores the Foggy Lake intro cutscene value to store a 0 (from R0) instead.
        patcher.write_int32(0x1614, 0xAC402BCC, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON) # SW  R0, 0x2BCC (V0)
        # Instead of always 0 as the spawn entrance, store the aftermentined cutscene value as it.
        patcher.write_int32(0x1618, 0xA04B2BBB, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON) # SB  T3, 0x2BBB (V0)
        # Make the starting level the same for Henry as everyone else.
        patcher.write_byte(0x15D5, 0x00, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)

        # Active cutscene checker routines for certain actors.
        patcher.write_int32s(0xFFCDA0, patches.cutscene_active_checkers)

        # Ambience silencing fix
        patcher.write_int32(0x1BB20, 0x080FF280)  # J 0x803FCA00
        patcher.write_int32s(0xFFCA00, patches.ambience_silencer)

        # Enable being able to carry multiple Special jewels, Nitros, Mandragoras, and Key Items simultaneously
        # Special1
        patcher.write_int32s(0x904B8, [0x90C8AB47,  # LBU   T0, 0xAB47 (A2)
                                        0x00681821,  # ADDU  V1, V1, T0
                                        0xA0C3AB47])  # SB    V1, 0xAB47 (A2)
        patcher.write_int32(0x904C8, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Special2
        patcher.write_int32s(0x904CC, [0x90C8AB48,  # LBU   T0, 0xAB48 (A2)
                                        0x00681821,  # ADDU  V1, V1, T0
                                        0xA0C3AB48])  # SB    V1, 0xAB48 (A2)
        patcher.write_int32(0x904DC, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Special3 (NOP this one for usage as the AP item)
        patcher.write_int32(0x904E8, 0x00000000)
        # Magical Nitro
        patcher.write_int32(0x9071C, 0x10000004)  # B [forward 0x04]
        patcher.write_int32s(0x90734, [0x25430001,  # ADDIU	V1, T2, 0x0001
                                        0x10000003])  # B [forward 0x03]
        # Mandragora
        patcher.write_int32(0x906D4, 0x10000004)  # B [forward 0x04]
        patcher.write_int32s(0x906EC, [0x25030001,  # ADDIU	V1, T0, 0x0001
                                        0x10000003])  # B [forward 0x03]
        # Key Items
        patcher.write_byte(0x906C7, 0x63)
        # Increase Use Item capacity to 99 if "Increase Item Limit" is turned on
        if slot_patch_info["options"]["increase_item_limit"]:
            patcher.write_byte(0x90617, 0x63)  # Most items
            patcher.write_byte(0x90767, 0x63)  # Sun/Moon cards

        # Rename the Special3 to "AP Item"
        patcher.write_bytes(0xB89AA, cvlod_string_to_bytearray("AP Item "))
        # Change the Special3's appearance to that of a spinning contract.
        patcher.write_int32s(0x11770A, [0x63583F80, 0x0000FFFF])
        # Disable spinning on the Special1 and 2 pickup models so colorblind people can more easily identify them.
        patcher.write_byte(0x1176F5, 0x00)  # Special1
        patcher.write_byte(0x117705, 0x00)  # Special2
        # Make the Special2 the same size as a Red jewel(L) to further distinguish them.
        patcher.write_int32(0x1176FC, 0x3FA66666)
        # Capitalize the "k" in "Archives key" and "Rose Garden key" to be consistent with...
        # literally every other key name!
        patcher.write_byte(0xB8AFF, 0x2B)
        patcher.write_byte(0xB8BCB, 0x2B)
        # Make the "PowerUp" textbox appear even if you already have two.
        patcher.write_int32(0x87E34, 0x00000000)  # NOP

        # Enable changing the item model/visibility on any item instance.
        patcher.write_int32s(0x107740, [0x0C0FF0C0,  # JAL   0x803FC300
                                         0x25CFFFFF])  # ADDIU T7, T6, 0xFFFF
        patcher.write_int32s(0xFFC300, patches.item_customizer)
        patcher.write_int32(0x1078D0, 0x0C0FF0CB),  # JAL   0x803FC32C
        patcher.write_int32s(0xFFC32C, patches.item_appearance_switcher)

        # Enable the Game Over's "Continue" menu starting the cursor on whichever checkpoint is most recent
        patcher.write_int32s(0x82120, [0x0C0FF2B4,  # JAL 0x803FCAD0
                                        0x91830024])  # LBU V1, 0x0024 (T4)
        patcher.write_int32s(0xFFCAD0, patches.continue_cursor_start_checker)
        patcher.write_int32(0x1D4A8, 0x080FF2C5)  # J   0x803FCB14
        patcher.write_int32s(0xFFCB14, patches.savepoint_cursor_updater)
        patcher.write_int32(0x1D344, 0x080FF2C0)  # J   0x803FCB00
        patcher.write_int32s(0xFFCB00, patches.stage_start_cursor_updater)
        patcher.write_byte(0x21C7, 0xFF, NIFiles.OVERLAY_GAME_OVER_SCREEN)
        # Multiworld buffer clearer/"death on load" safety checks.
        patcher.write_int32s(0x1D314, [0x080FF2D0,  # J   0x803FCB40
                                        0x24040000])  # ADDIU A0, R0, 0x0000
        patcher.write_int32s(0x1D3B4, [0x080FF2D0,  # J   0x803FCB40
                                        0x24040001])  # ADDIU A0, R0, 0x0001
        patcher.write_int32s(0xFFCB40, patches.load_clearer)

        # Write the specified window colors
        patcher.write_byte(0x8881A, slot_patch_info["options"]["window_color_r"] << 4)
        patcher.write_byte(0x8881B, slot_patch_info["options"]["window_color_g"] << 4)
        patcher.write_byte(0x8881E, slot_patch_info["options"]["window_color_b"] << 4)
        patcher.write_byte(0x8881F, slot_patch_info["options"]["window_color_a"] << 4)


        # # # # # # # # # # #
        # FOGGY LAKE EDITS  #
        # # # # # # # # # # #
        # Lock the door in Foggy Lake below decks leading out to above decks with the Deck Key.
        # It's the same door in-universe as the above decks one but on a different map.
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["door_flags"] = DoorFlags.LOCKED_BY_KEY
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["flag_id"] = 0x28E  # Deck Door unlocked flag.
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["item_id"] = Items.DECK_KEY
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["flag_locked_text_id"] = 0x01
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["unlocked_text_id"] = 0x02
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].scene_text += [
            CVLoDSceneTextEntry(text="You're locked in!\n"
                                     "Looks like you will need\n"
                                     "the Deck Key...🅰0/"),
            CVLoDSceneTextEntry(text="Deck Key\n"
                                     "       has been used.🅰0/")
        ]

        # Make the Foggy Lake cargo hold door openable only from the outside instead of it locking permanently after
        # going through it once.
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[1]["door_flags"] = DoorFlags.LOCK_FROM_BACK_SIDE

        # Disable the Foggy Lake Pier save jewel checking for one of the ship sinking cutscene flags to spawn in case
        # we find the stage from the end point.
        # To preserve the cutscene director's vision, we'll put it on our custom "not in a cutscene" check instead!
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][76]["spawn_flags"] = \
            ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][76]["flag_id"] = 0
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][76]["extra_condition_ptr"] = 0x803FCDBC
        # Prevent the Sea Monster from respawning if you leave the pier map and return.
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][74]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][74]["flag_id"] = 0x15D
        # Un-set the "debris path sunk" flag after the Sea Monster is killed and when the door flag is set.
        patcher.write_int32(0x7268, 0x0FC04164, NIFiles.OVERLAY_SEA_MONSTER)  # JAL 0x0F010590
        patcher.write_int32s(0x10590, patches.sea_monster_sunk_path_flag_unsetter, NIFiles.OVERLAY_SEA_MONSTER)
        # Disable the two pier statue items checking each other's flags being not set as an additional spawn condition.
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][77]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][77]["flag_id"] = 0
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][80]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["proxy"][80]["flag_id"] = 0


        # # # # # # # # # # # # # #
        # FOREST OF SILENCE EDITS #
        # # # # # # # # # # # # # #
        # Make coffins 1-4 in the Forest Charnel Houses never spawn items
        # (as in, the RNG check for them will never pass).
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int32(0x2740, 0x10000005)  # B [forward 0x05]
        # Make coffin 0 always try spawning the same consistent three items regardless of whether we previously broke
        # it or not and regardless of difficulty.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int32(0x2778, 0x00000000)  # NOP-ed Hard difficulty check
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(0x2DC3, 0x00)  # No event flag set for coffin 00.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int32(0x27B4, 0x00000000)  # NOP-ed Not Easy difficulty check
        # Use the current loop iteration to tell what entry in the table to spawn.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int32(0x27D4, 0x264E0000)  # ADDIU T6, S2, 0x0000
        # Assign the event flags, remove the "vanish timer" flag on each of the three coffin item entries we'll use,
        # and write their pickups.
        # Entry 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
            FOREST_OVL_CHARNEL_ITEMS_START + 2, loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id])
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
            FOREST_OVL_CHARNEL_ITEMS_START + 6, CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id)
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(FOREST_OVL_CHARNEL_ITEMS_START + 9, 0x00)
        # Entry 1
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
            FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 2,
            loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_2].flag_id])
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
            FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 6,
            CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_2].flag_id)
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 9,
                                                                0x00)
        # Entry 8
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
            FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 2,
            loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_3].flag_id])
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
            FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 6,
            CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_3].flag_id)
        patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(
            FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 9, 0x00)
        # If the chosen prize coffin is not coffin 0, swap the actor var C's of the lids of coffin 0 and the coffin that
        # did get chosen.
        if slot_patch_info["prize coffin id"]:
            patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][
                FIRST_CHARNEL_LID_ACTOR]["var_c"] = slot_patch_info["prize coffin id"]
            patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][
                FIRST_CHARNEL_LID_ACTOR + slot_patch_info["prize coffin id"]]["var_c"] = 0

        # Turn the Forest Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["execution_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["flag_id"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.forest_child_ledge].flag_id
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["var_c"] = Pickups.ONE_HUNDRED_GOLD

        # Ensure King Skeleton 2 will never drop his secret beef for beating him as Henry without running
        # (yes, this is ACTUALLY a thing!)
        patcher.write_int32(0x43F8, 0x10000006, NIFiles.OVERLAY_KING_SKELETON)  # B [forward 0x06]
        # Set Flag 0x23 on the item King Skeleton 2 otherwise leaves behind if the above condition isn't fulfilled, and
        # prevent it from expiring.
        patcher.write_int32s(0x444C, [0x0FC0307C,  # JAL 0x0F00C1F0
                                      0x8E2C001C], # LW  T4, 0x001C (S1)
                             NIFiles.OVERLAY_KING_SKELETON)
        patcher.write_int32s(0xC1F0, [(0x24080000 +  # ADDIU T0, R0, 0x0023
                                       CVLOD_LOCATIONS_INFO[loc_names.forest_skelly_mouth].flag_id),
                                      0xA4480014,  # SH  T0, 0x0014 (V0)
                                      0xA0400017,  # SB  R0, 0x0017 (V0)
                                      0x03E00008,  # JR  RA
                                      0x3C010040], # LUI AT, 0x0040
                             NIFiles.OVERLAY_KING_SKELETON)
        # Turn the item that drops into what it should be.
        patcher.write_int16(0x43CA, loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_skelly_mouth].flag_id],
                            NIFiles.OVERLAY_KING_SKELETON)
        # Add the backup King Skeleton jaws item that will spawn only if the player orphans it the first time.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"].append(
            CVLoDNormalActorEntry(spawn_flags=ActorSpawnFlags.SPAWN_IF_FLAG_SET, status_flags=0, x_pos= 0.03125,
                                  y_pos=0, z_pos=-1430,execution_flags=0, object_id=Objects.PICKUP_ITEM,
                                  flag_id=0x2C,  # Drawbridge lowering cutscene flag.
                                  var_a=CVLOD_LOCATIONS_INFO[loc_names.forest_skelly_mouth].flag_id, var_b=0,
                                  var_c=Pickups.ROAST_CHICKEN, var_d=0, extra_condition_ptr=0)
        )

        # Make the drawbridge cutscene's end behavior its Henry end behavior for everyone.
        # The "drawbridge lowered" flag should be set so that Forest's regular end zone is easily accessible, and no
        # separate cutscene should play in the next map.
        patcher.write_int32(0x1294, 0x1000000C, NIFiles.OVERLAY_CS_DRAWBRIDGE_LOWERS)

        # Make Reinhardt/Carrie/Cornell's White Jewels universal to everyone and remove Henry's.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][123]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][124]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][125]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][126]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][127]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][128]["delete"] = True
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][129]["delete"] = True
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][130]["delete"] = True
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][131]["delete"] = True


        # # # # # # # # # # #
        # CASTLE WALL EDITS #
        # # # # # # # # # # #
        # Remove the Castle Wall Henry child actor and make the candle actor there universal for everyone else.
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][142]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][162]["spawn_flags"] = 0
        # Make Reinhardt/Carrie/Cornell's White Jewels universal to everyone and remove Henry's.
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][22]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][23]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][24]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][25]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][26]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][27]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][156]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][157]["delete"] = True
        # Remove the Cornell-specific pickups and breakables and make Reinhardt/Carrie's equivalent ones universal.
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][28]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][29]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][30]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][31]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][32]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][158]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][159]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][160]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][161]["delete"] = True
        # Make the Henry-only start loading zone universal to everyone.
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][59]["spawn_flags"] = 0

        # If the Castle Wall State is Reinhardt/Carrie's, put the stage in Reinhardt and Carrie's state.
        if slot_patch_info["options"]["castle_wall_state"] == CastleWallState.option_reinhardt_carrie:
            # Right Tower switch spot is the non-lever missing version.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][9]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][10]["spawn_flags"] = 0
            # Portcullises are Reinhardt/Carrie's versions.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][52]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][53]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][54]["delete"] = True
            # Main area Right Tower door is a normal door. Left Tower door is a Left Tower Key door.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][55]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][56]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][57]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][58]["delete"] = True

            # Left Tower interior top door is a moon door.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][191]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][192]["delete"] = True
            # Left Tower interior top loading zone plays the Fake Dracula taunt cutscene.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][195]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][196]["delete"] = True
        # If the Castle Wall State is Cornell's, put the stage in Reinhardt and Cornell's state.
        if slot_patch_info["options"]["castle_wall_state"] == CastleWallState.option_cornell:
            # Right Tower switch spot is the lever missing version.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][9]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][10]["delete"] = True
            # Portcullises are Cornell's versions.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][52]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][53]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][54]["spawn_flags"] = 0
            # Main area Right Tower door is a sun door. Left Tower door is a moon door.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][55]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][56]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][57]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][58]["spawn_flags"] = 0


            # Left Tower interior top door is a regular door.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][191]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][192]["spawn_flags"] = 0
            # Left Tower interior top loading zone plays no cutscene.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][195]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][196]["spawn_flags"] = 0
        # Otherwise, if Hybrid was chosen, put the stage in a hybrid state.
        else:
            # Right Tower switch spot is the lever missing version.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][9]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][10]["delete"] = True
            # Portcullises are Cornell's versions.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][52]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][53]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][54]["spawn_flags"] = 0
            # Main area Right Tower door is a normal door. Left Tower door is a Left Tower Key door.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][55]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][56]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][57]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][58]["delete"] = True

            # Left Tower interior top door is a regular door.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][191]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][192]["spawn_flags"] = 0
            # Left Tower interior top loading zone plays no cutscene.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][195]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][196]["spawn_flags"] = 0


        # # # # # # # #
        # VILLA EDITS #
        # # # # # # # #
        # Give Child Henry his Cornell behavior for everyone.
        patcher.write_int32(0x1B8, 0x24020002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU V0, R0, 0x0002
        patcher.write_byte(0x613, 0x04, NIFiles.OVERLAY_CHILD_HENRY)
        patcher.write_int32(0x844, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002
        patcher.write_int32(0x8B8, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002


        # # # # # # # # #
        # TUNNEL EDITS  #
        # # # # # # # # #
        # Make the Tunnel gondolas check for the Spider Women cutscene like they do in CV64.
        patcher.write_int32(0x79B8CC, 0x0C0BADF4)  # JAL  0x802EB7D0
        patcher.scenes[Scenes.TUNNEL].write_ovl_int32s(0x7C60, patches.gondola_spider_cutscene_checker)

        # Turn the Tunnel Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["execution_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["flag_id"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.tunnel_shovel_mdoor_c].flag_id
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["var_b"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["var_c"] = Pickups.ONE_HUNDRED_GOLD

        # Set the Tunnel end zone spawn ID to the ID for the decoupled Spider Queen arena.
        patcher.scenes[Scenes.TUNNEL].loading_zones[0]["spawn_id"] |= 0x40

        # Make the Spider Women introduction cutscene trigger universal to everyone.
        patcher.scenes[Scenes.TUNNEL].actor_lists["init"][7]["spawn_flags"] = 0
        # Make Henry's teleport jewel universal to everyone.
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][215]["spawn_flags"] = 0
        # Make Reinhardt/Carrie/Cornell's White Jewels universal to everyone and remove Henry's.
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][132]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][133]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][134]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][135]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][136]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][137]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][138]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][139]["delete"] = True
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][140]["delete"] = True
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][141]["delete"] = True
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][142]["delete"] = True
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][143]["delete"] = True
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][144]["delete"] = True
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][145]["delete"] = True


        # # # # # # # # # # # # # # # #
        # UNDERGROUND WATERWAY EDITS  #
        # # # # # # # # # # # # # # # #
        # Turn the Waterway Henry child actor into a freestanding pickup with all necessary parameters assigned.
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["execution_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["flag_id"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.uw_waterfall_child].flag_id
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["var_b"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["var_c"] = Pickups.ONE_HUNDRED_GOLD
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["extra_condition_ptr"] = 0

        # Set the Waterway end zone destination ID to the ID for the decoupled Medusa arena.
        patcher.scenes[Scenes.WATERWAY].loading_zones[0]["spawn_id"] |= 0x80

        # Make the "I Smell Poison" and lizard-men cutscene triggers and all text spots universal to everyone.
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][1]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][2]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][3]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][4]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][5]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][6]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][7]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][8]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][9]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][10]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["init"][12]["spawn_flags"] = 0
        # Make Henry's teleport jewel universal to everyone.
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][103]["spawn_flags"] = 0
        # Make Reinhardt/Carrie/Cornell's White Jewels universal to everyone and remove Henry's.
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][71]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][72]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][73]["spawn_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][74]["delete"] = True
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][75]["delete"] = True
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][76]["delete"] = True


        # # # # # # # # # # # # # # # #
        # TUNNEL/WATERWAY ARENA EDITS #
        # # # # # # # # # # # # # # # #
        # Make different end loading zones spawn depending on whether the 0x2A1 or 0x2A2 flags are set
        # (specifically, Reinhardt and Carrie's ones).
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][12]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][12]["flag_id"] = 0x02A1  # Tunnel flag ID
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][13]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][13]["flag_id"] = 0x02A2  # Waterway flag ID

        # Delete the end sun door for Reinhardt/Carrie/Cornell and keep the regular door for Henry.
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][6]["delete"] = True
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][7]["spawn_flags"] ^= ActorSpawnFlags.HENRY
        # Delete the end zone specific to Henry and the start zones specific to Reinhardt/Carrie, and make the Henry
        # start zones universal to everyone.
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][8]["delete"] = True
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][9]["delete"] = True
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][10]["spawn_flags"] ^= ActorSpawnFlags.HENRY
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][11]["spawn_flags"] ^= ActorSpawnFlags.HENRY
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][14]["delete"] = True
        # Delete the boss instances specific to Reinhardt and Carrie and make Henry's spawn for everyone
        # (without removing the flag checks).
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][2]["delete"] = True
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][4]["delete"] = True
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][3]["spawn_flags"] ^= ActorSpawnFlags.HENRY
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].actor_lists["proxy"][5]["spawn_flags"] ^= ActorSpawnFlags.HENRY

        # Remove the cutscene setting ID on the Reinhardt and Carrie end loading zone data so that said cutscenes won't
        # cause us to get teleported to the void should the loading zones' destinations change.
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].loading_zones[1]["cutscene_settings_id"] = 0
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].loading_zones[3]["cutscene_settings_id"] = 0


        # # # # # # # # # # # # #
        # THE OUTER WALL EDITS  #
        # # # # # # # # # # # # #
        # Turn the Outer Wall Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["spawn_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["execution_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["flag_id"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.towse_child].flag_id
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["var_b"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["var_c"] = Pickups.ONE_HUNDRED_GOLD
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["extra_condition_ptr"] = 0

        # Make the Outer Wall end loading zone send you to the start of Art Tower by default instead of the fan map, as
        # well as heal the player.
        patcher.scenes[Scenes.THE_OUTER_WALL].loading_zones[10]["scene_id"] = Scenes.ART_TOWER_MUSEUM
        patcher.scenes[Scenes.THE_OUTER_WALL].loading_zones[10]["spawn_id"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].loading_zones[10]["heal_player"] = True

        # Make the Harpy cutscene trigger universal for everyone.
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["init"][1]["spawn_flags"] = 0
        # Make Henry's teleport jewel universal for everyone.
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][114]["spawn_flags"] = 0
        # Make the candle normally containing the Wall Key universal for everyone.
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][42]["spawn_flags"] = 0
        # Make Cornell's White Jewels universal to everyone and remove Henry's.
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][43]["spawn_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][44]["spawn_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][45]["spawn_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][46]["spawn_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][47]["delete"] = True
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][48]["delete"] = True
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][49]["delete"] = True
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][50]["delete"] = True

        # If the empty breakables are on, write all data associated with them.
        if slot_patch_info["options"]["empty_breakables"]:
            # Assign every empty 1HB a unique 1HB ID.
            # For our purposes, we will be using the Outer Wall's Easy/Hard-specific 1HB data.
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][103]["var_c"] = 0x8
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][102]["var_c"] = 0x6
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][105]["var_c"] = 0xB
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][104]["var_c"] = 0xA
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][107]["var_c"] = 0xD
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][106]["var_c"] = 0xC
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][109]["var_c"] = 0x10
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][108]["var_c"] = 0xF
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][111]["var_c"] = 0x13
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][110]["var_c"] = 0x12
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][113]["var_c"] = 0x19
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][112]["var_c"] = 0x18

            # Change the flag IDs in the 1HB data we are using to be the actual unique flags for the new locations.
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x8]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towf_start_entry_l].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x6]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towf_start_entry_r].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xB]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towf_start_elevator_l].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xA]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towf_start_elevator_r].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xD]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towse_key_entry_l].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xC]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towse_key_entry_r].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x10]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towse_locked_door_l].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xF]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towse_locked_door_r].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x13]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towf_retract_elevator_l].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x12]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towf_retract_elevator_r].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x19]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towh_boulders_elevator_l].flag_id
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x18]["flag_id"] = \
                CVLOD_LOCATIONS_INFO[loc_names.towh_boulders_elevator_r].flag_id

            # Change the appearance value of each 1HB data to be a wall-mounted candle.
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x8]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x6]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xB]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xA]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xD]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xC]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x10]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0xF]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x13]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x12]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x19]["appearance_id"] = 1
            patcher.scenes[Scenes.THE_OUTER_WALL].one_hit_breakables[0x18]["appearance_id"] = 1

            # Move these specific 1HB actors slightly so that they don't just drop their contents into the abyss.
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][103]["z_pos"] = -169.5
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][105]["z_pos"] = -129.5
            patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][107]["z_pos"] = -1149.5


        # # # # # # # # # #
        # ART TOWER EDITS #
        # # # # # # # # # #
        # Make the Art Tower start loading zone send you to the end of The Outer Wall instead of the fan map.
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].loading_zones[0]["scene_id"] = Scenes.THE_OUTER_WALL
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].loading_zones[0]["spawn_id"] = 0x0B

        # Make the loading zone leading from Art Tower museum -> conservatory slightly smaller.
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].loading_zones[1]["min_z_pos"] = -488
        # Duplicate the player spawn position data coming from Art Tower conservatory -> museum and change its player
        # spawn coordinates coming from Art Tower conservatory -> museum to start them behind the Key 2 door, so they
        # will need Key 2 to come this way.
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots.append(
            patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots[1].copy())
        del patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots[5]["start_addr"]
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots[5]["player_z_pos"] = -478
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots[5]["camera_x_pos"] = 0
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots[5]["camera_z_pos"] = -496
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].spawn_spots[5]["focus_z_pos"] = -478
        # Duplicate the Art Tower conservatory -> museum loading zone data and change its spawn ID to the new one above
        # for the museum.
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].loading_zones.append(
            patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].loading_zones[0].copy())
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].loading_zones[2]["spawn_id"] = 5
        del patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].loading_zones[2]["start_addr"]
        # Duplicate the loading zone actor for Art Tower conservatory -> museum, change its zone ID that of the new one
        # we just made, and make it spawn only when the Art Tower Door 2 Unlocked flag is CLEARED.
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"].append(
            patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][59].copy())
        del patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][61]["start_addr"]
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][61]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][61]["flag_id"] = 0x299  # Art Door 2 flag ID
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][61]["var_c"] = 2
        # Make the original loading zone actor spawn only when the Art Tower Door 2 Unlocked flag is SET. With this
        # setup, depending on if the door is locked or unlocked, the player should be placed at the new spawn spot
        # behind Door 2 in the museum scene or the vanilla one before it.
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][59]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][59]["flag_id"] = 0x299 # Art Door 2 flag ID

        # Prevent the Hell Knights in the middle Art Tower hallway from spawning and locking the doors if the player
        # spawns in our new spawn location until they actually go through the doors.
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["room 10"][3]["spawn_flags"] |= \
            ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["room 10"][4]["spawn_flags"] |= \
            ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["room 10"][5]["spawn_flags"] |= \
            ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
        at_knight_check_spot = len(patcher.scenes[Scenes.ART_TOWER_MUSEUM].overlay) + SCENE_OVERLAY_RDRAM_START
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["room 10"][3]["extra_condition_ptr"] = at_knight_check_spot
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["room 10"][4]["extra_condition_ptr"] = at_knight_check_spot
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["room 10"][5]["extra_condition_ptr"] = at_knight_check_spot
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].write_ovl_int32s(at_knight_check_spot - SCENE_OVERLAY_RDRAM_START,
                                                                 patches.art_tower_knight_spawn_check)

        # Put the left item on top of the Art Tower conservatory doorway on its correct flag.
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][55]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.atc_doorway_l].flag_id

        # Prevent the middle item on top of the Art Tower conservatory doorway from self-modifying itself.
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][54]["spawn_flags"] ^= \
            ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][54]["extra_condition_ptr"] = 0

        # Make Cornell's Loading Zones universal to everyone.
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].actor_lists["proxy"][14]["spawn_flags"] = 0
        patcher.scenes[Scenes.ART_TOWER_CONSERVATORY].actor_lists["proxy"][60]["spawn_flags"] = 0


        # # # # # # # # # # # # #
        # TOWER OF RUINS EDITS  #
        # # # # # # # # # # # # #
        # Remove the Tower of Science pickup flag checks from the invisible Tower of Ruins statue items.
        # Yeah, your guess as to what the devs may have been thinking with this is as good as mine.
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 7"][13]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 7"][13]["flag_id"] = 0
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 13"][11]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 13"][11]["flag_id"] = 0

        # Clone the maze end gate actor and turn it around the other way. These actors normally only have
        # collision on one side, so if you were coming the other way you could very easily sequence break.
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"].append(
            patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"][0].copy())
        del patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"][11]["start_addr"]
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"][11]["x_pos"] = 438.0
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"][11]["y_pos"] = 75.0
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"][11]["z_pos"] = 144.0
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 18"][11]["var_b"] = 0x8000
        patcher.write_byte(0x809925, 0x00)     # Flag check unassignment
        patcher.write_int32s(0x809928, [0x43DB0000, 0x42960000, 0x43100000])  # XYZ coordinates
        patcher.write_int16(0x809934, 0x01B9)  # Special door actor ID
        patcher.write_int16(0x809936, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x809938, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x80993A, 0x8000)  # Rotation
        patcher.write_int16(0x80993C, 0x0002)  # Door ID

        # Make Cornell's Loading Zones universal to everyone.
        patcher.scenes[Scenes.RUINS_DOOR_MAZE].actor_lists["room 25"][1]["spawn_flags"] = 0
        patcher.scenes[Scenes.RUINS_DARK_CHAMBERS].actor_lists["room 6"][0]["spawn_flags"] = 0

        # Set the Tower of Ruins end loading zone destination to the Castle Center top elevator White Jewel by default.
        patcher.scenes[Scenes.RUINS_DARK_CHAMBERS].loading_zones[1]["scene_id"] = Scenes.CASTLE_CENTER_TOP_ELEV
        patcher.scenes[Scenes.RUINS_DARK_CHAMBERS].loading_zones[1]["spawn_id"] = 3


        # # # # # # # # # # # #
        # CASTLE CENTER EDITS #
        # # # # # # # # # # # #
        # Make the Behemoth and crying blood statue cutscene triggers universal for everyone.
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][7]["spawn_flags"] ^= \
            ActorSpawnFlags.REINHARDT_AND_CARRIE
        patcher.scenes[Scenes.CASTLE_CENTER_BOTTOM_ELEV].actor_lists["init"][5]["spawn_flags"] ^= \
            ActorSpawnFlags.REINHARDT_AND_CARRIE

        # Before doing anything else to this stage, loop over the specific actor lists for the Castle Center scenes that
        # appear in Cornell's intro cutscene and check the character flags on each one.
        for scene_id, list_name in CC_CORNELL_INTRO_ACTOR_LISTS.items():
            for actor in patcher.scenes[scene_id].actor_lists[list_name]:
                # Is it exclusive to Cornell and NOT Reinhardt or Carrie? If so, make it universal to everyone and put
                # the custom "In a cutscene?" check on it because we are only meant to see it in Cornell's intro.
                if actor["spawn_flags"] & ActorSpawnFlags.CORNELL and not \
                        (actor["spawn_flags"] & ActorSpawnFlags.REINHARDT |
                         actor["spawn_flags"] & ActorSpawnFlags.CARRIE):
                    actor["spawn_flags"] &= ActorSpawnFlags.NO_CHARACTERS
                    actor["spawn_flags"] |= ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
                    actor["extra_condition_ptr"] = 0x803FCDA0
                # Is it exclusive to Reinhardt or Carrie and NOT Cornell? If so, put the custom "Not in a cutscene?"
                # check on it because it's a Reinhardt/Carrie actor we are NOT meant to see in Cornell's intro.
                elif not actor["spawn_flags"] & ActorSpawnFlags.CORNELL and \
                        (actor["spawn_flags"] & ActorSpawnFlags.REINHARDT |
                         actor["spawn_flags"] & ActorSpawnFlags.CARRIE):
                    actor["spawn_flags"] |= ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
                    actor["extra_condition_ptr"] = 0x803FCDBC

                    # Only make it character-universal if it's truly exclusive to both Reinhardt AND Carrie; don't touch
                    # it if it's only one character or the other.
                    if actor["spawn_flags"] & ActorSpawnFlags.REINHARDT_AND_CARRIE == \
                            ActorSpawnFlags.REINHARDT_AND_CARRIE:
                        actor["spawn_flags"] &= ActorSpawnFlags.NO_CHARACTERS

        # Set the Cerberuses in the basement to trigger for Cornell in addition to Reinhardt. The Motorskellies here
        # are already set up to spawn for Carrie and, interestingly enough, Henry, so we shall mirror that for Cornell.
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 1"][34]["spawn_flags"] |= \
            ActorSpawnFlags.CORNELL
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 1"][35]["spawn_flags"] |= \
            ActorSpawnFlags.CORNELL
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 1"][36]["spawn_flags"] |= \
            ActorSpawnFlags.CORNELL

        # Change some shelf decoration Nitros and Mandragoras into actual items.
        # Mandragora shelf right
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][14]["x_pos"] = -4.0
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][14]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][14]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccb_mandrag_shelf_r].flag_id
        # Mandragora shelf left
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["x_pos"] = -4.0
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccb_mandrag_shelf_l].flag_id
        # Nitro shelf Heinrich side
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["x_pos"] = -320.0
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_shelf_h].flag_id
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["var_b"] = 0
        # Nitro shelf invention side
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["x_pos"] = -306.0
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["object_id"] = Objects.PICKUP_ITEM
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_shelf_i].flag_id
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["var_b"] = 0

        # Restore the Castle Center library bookshelf item by moving its actor entry in room 2's list (the planetarium)
        # into room 0's list (the lower floor library) instead, and taking it off of its own-pickup-flag-set check.
        patcher.scenes[Scenes.CASTLE_CENTER_LIBRARY].actor_lists["room 0"].append(
            patcher.scenes[Scenes.CASTLE_CENTER_LIBRARY].actor_lists["room 2"][4].copy())
        del patcher.scenes[Scenes.CASTLE_CENTER_LIBRARY].actor_lists["room 0"][15]["start_addr"]
        patcher.scenes[Scenes.CASTLE_CENTER_LIBRARY].actor_lists["room 0"][15]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET | ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        # Delete the actor entry from the original list.
        patcher.scenes[Scenes.CASTLE_CENTER_LIBRARY].actor_lists["room 2"][4]["delete"] = True

        # Clear the Reinhardt and Carrie-only settings from the post-Behemoth boss cutscenes in the universal cutscene
        # trigger settings table so anyone will be allowed to trigger them (a hangover from Ye Olde CV64 Days when the
        # actor system wasn't as awesome). We'll instead simply assign each cutscene trigger actor its correct
        # characters.
        patcher.write_byte(0x118139, 0x00)
        patcher.write_byte(0x118165, 0x00)
        # If Rosa was chosen for the post-Behemoth boss, delete the trigger for Camilla's battle intro cutscene and
        # make Rosa's universal for everyone.
        if slot_patch_info["options"]["post_behemoth_boss"] == PostBehemothBoss.option_rosa:
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][6]["delete"] = True
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][5]["spawn_flags"] ^= \
                ActorSpawnFlags.REINHARDT
        # If Camilla was chosen for the post-Behemoth boss, delete the trigger for Rosa's battle intro cutscene and
        # make Camilla's universal for everyone.
        elif slot_patch_info["options"]["post_behemoth_boss"] == PostBehemothBoss.option_camilla:
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][5]["delete"] = True
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][6]["spawn_flags"] ^= \
                ActorSpawnFlags.CARRIE
        # Otherwise, if Character Dependant was chosen, set up Rosa's to trigger for Reinhardt and Cornell and
        # Camilla's to trigger for Carrie and Henry.
        else:
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][5]["spawn_flags"] |= \
                ActorSpawnFlags.CORNELL
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][6]["spawn_flags"] |= \
                ActorSpawnFlags.HENRY

        # Make it possible to fix or break both Castle Center top elevator bridges universally for all characters by
        # putting 1 or 0 in their var_c respectively.
        patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].write_ovl_int32(0xEC, 0x51200004)  # BEQZL  T1, [forward 0x04]
        # If CC Branching Paths is set to One Reinhardt, break Carrie's bridge and fix Reinhardt's.
        if slot_patch_info["options"]["castle_center_branching_paths"] == \
                CastleCenterBranchingPaths.option_one_reinhardt:
            patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"][1]["var_c"] = 1
            patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"][2]["var_c"] = 0
            # Loop through every actor in the scene and make all Reinhardt ones universal while killing all Carrie ones.
            for actor in patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"]:
                if actor["spawn_flags"] & ActorSpawnFlags.REINHARDT:
                    actor["spawn_flags"] ^= ActorSpawnFlags.REINHARDT
                elif actor["spawn_flags"] & ActorSpawnFlags.CARRIE:
                    actor["delete"] = True
        # If set to One Carrie, break Reinhardt's bridge and fix Carrie's.
        elif slot_patch_info["options"]["castle_center_branching_paths"] == \
                CastleCenterBranchingPaths.option_one_carrie:
            patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"][1]["var_c"] = 0
            patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"][2]["var_c"] = 1
            # Loop through every actor in the scene and make all Carrie ones universal while killing all Reinhardt ones.
            for actor in patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"]:
                if actor["spawn_flags"] & ActorSpawnFlags.CARRIE:
                    actor["spawn_flags"] ^= ActorSpawnFlags.CARRIE
                elif actor["spawn_flags"] & ActorSpawnFlags.REINHARDT:
                    actor["delete"] = True
        # Otherwise, if set to Two, fix both bridge for everyone and make all character-specific actors universal.
        else:
            patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"][1]["var_c"] = 1
            patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"][2]["var_c"] = 1
            for actor in patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].actor_lists["proxy"]:
                if actor["spawn_flags"] & ActorSpawnFlags.REINHARDT_AND_CARRIE:
                    actor["spawn_flags"] &= ActorSpawnFlags.NO_CHARACTERS

        # Prevent the CC elevator from working from the top if the elevator switch is not activated.
        patcher.write_int32(0xD7A74, 0x080FF0B0)  # J 0x803FC2C0
        patcher.write_int32s(0xFFC2C0, patches.elevator_flag_checker)
        # Put said elevator on the map-specific checks so our custom one will actually work.
        patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].write_ovl_byte(0x72F, 0x01)

        # Prevent taking Nitro or Mandragora through their shelf text.
        patcher.write_int32(0x1F0, 0x240C0000, NIFiles.OVERLAY_TAKE_NITRO_TEXTBOX)  # ADDIU T4, R0, 0x0000
        patcher.write_int32(0x22C, 0x240F0000, NIFiles.OVERLAY_TAKE_MANDRAGORA_TEXTBOX)  # ADDIU T7, R0, 0x0000
        # Custom message for when trying to activate the "Take Nitro?" text box, explaining why we can't take them.
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].scene_text[5]["text"] = (
            "Huh!? Someone super glued\n"
            "all these Magical Nitro bottles\n"
            "to the shelf!🅰0/\n"
            "Better find some elsewhere;\n"
            "without a certain coyote's\n"
            "toon DNA, trying to force-\n"
            "remove one could prove fatal!🅰0/")
        # Custom message for when trying to activate the "Take Mandragora?" text box, explaining why we can't take them.
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].scene_text[13]["text"] = (
            "These Mandragora bottles\n"
            "are empty, and a note was\n"
            "left behind:🅰0/\f"
            "\"Come 2035, and the Count\n"
            "will be in for a very LOUD\n"
            "surprise! Hehehehe!\"🅰0/\n"
            "Sounds like whichever poor\n"
            "soul battles Dracula then may\n"
            "have an easier time...🅰0/")

        # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes.
        patcher.write_int32(0x128, 0x24020001, NIFiles.OVERLAY_VAMPIRE_SPAWNER)  # ADDIU V0, R0, 0x0001

        # Prevent throwing Nitro in the Hazardous Materials Disposals.
        patcher.write_int32(0x1E4, 0x24020001, NIFiles.OVERLAY_NITRO_DISPOSAL_TEXTBOX)  # ADDIU V0, R0, 0x0001
        # Custom messages for when trying to interact with each of the Hazardous Materials Disposals, explaining why we
        # can't use any of them.
        patcher.scenes[Scenes.CASTLE_CENTER_BOTTOM_ELEV].scene_text[8]["text"] = (
            "\"Hazardous materials\n"
            " disposal.\"🅰0/\n"
            "You stare inside its darkness\n"
            "only to see a terrifying\n"
            "smiling face entity stare back!\n"
            "Yeah, let's...leave it alone.🅰0/")
        patcher.scenes[Scenes.CASTLE_CENTER_FACTORY].scene_text[3]["text"] = (
            "\"Hazardous materials\n"
            " disposal.\"\n"
            "It seems jammed shut.🅰0/\f"
            "Some graffiti is scrawled on:\n"
            "\"This'll teach you to not be a\n"
            "COWARD transporting Nitro\n"
            "through here!\"🅰0/")
        patcher.scenes[Scenes.CASTLE_CENTER_LIZARD_LAB].scene_text[4]["text"] = (
            "\"Hazardous materials\n"
            " disposal.\"\n"
            "There's a sticky note\n"
            "attached:🅰0/\f"
            "\"Usage of this unit suspended\n"
            "until further notice after D-573\n"
            "attempted to escape through it.\n"
            "-Dr. [       ]\"🅰0/\f"
            "The writer's name is blacked\n"
            "out and there's an insignia\n"
            "with three arrows that you've\n"
            "never seen before.🅰30/.🅰30/.🅰30/.🅰30/.🅰30/\n"
            "yet it feels eerily familiar!?🅰0/")

        # Allow placing both bomb components at a cracked wall at once while having multiple copies of each, prevent
        # placing them at the downstairs crack altogether until the seal is removed, and enable placing both in one
        # interaction.
        # Add the three separate patches onto the end of the Ingredient Set Textbox overlay and record their start \
        # addresses.
        double_comp_check_location = patcher.get_decompressed_file_size(NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX) + \
                                     0x0E000000
        patcher.write_int32s(double_comp_check_location - 0x0E000000, patches.double_component_checker,
                             NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        basement_seal_check_location = patcher.get_decompressed_file_size(NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX) + \
                                       0x0E000000
        patcher.write_int32s(basement_seal_check_location - 0x0E000000, patches.basement_seal_checker,
                             NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        mandrag_with_nitro_location = patcher.get_decompressed_file_size(NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX) + \
                                      0x0E000000
        patcher.write_int32s(mandrag_with_nitro_location - 0x0E000000, patches.mandragora_with_nitro_setter,
                             NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        # Update the following jump pointers in the overlay's code to go to our new hacks instead. Some are two separate
        # instructions, one loading the upper half of the address and then the other the lower.
        patcher.write_int32(0xEE8, basement_seal_check_location, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x34A, double_comp_check_location >> 0x10, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x34E, double_comp_check_location & 0xFFFF, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x38A, double_comp_check_location >> 0x10, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x38E, double_comp_check_location & 0xFFFF, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x3F6, double_comp_check_location >> 0x10, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x3FA, (double_comp_check_location & 0xFFFF) + 0x4C, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x436, double_comp_check_location >> 0x10, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x43A, (double_comp_check_location & 0xFFFF) + 0x4C, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x646, mandrag_with_nitro_location >> 0x10, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x64A, mandrag_with_nitro_location & 0xFFFF, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x65E, mandrag_with_nitro_location >> 0x10, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x662, mandrag_with_nitro_location & 0xFFFF, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int32s(0xFFCDE0, patches.mandragora_with_nitro_setter)

        # Custom message for if you try checking the downstairs Castle Center crack before removing the seal, explaining
        # why we can't do that.
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].scene_text[17]["text"] = ("The Furious Nerd Curse\n" 
                                                                                "prevents you from setting\n" 
                                                                                "anything until the seal\n" 
                                                                                "is removed!🅰0/")

        # Disable the rapid flashing effect in the CC planetarium cutscene to ensure it won't trigger seizures.
        # TODO: Make this an option.
        #patcher.write_int32(0xC5C, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xCD0, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xC64, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xC74, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xC80, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xC88, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xC90, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xC9C, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xCB4, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #patcher.write_int32(0xCC8, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)


        # # # # # # # # # # # # # #
        # TOWER OF SCIENCE EDITS  #
        # # # # # # # # # # # # # #
        # Prevent Turret 4 (the one in the first room) from locking the doors while active, so that the message on
        # Door 2 when locked works properly.
        patcher.scenes[Scenes.SCIENCE_LABS].write_ovl_int32(0x2AB4, 0x00000000)
        # Touch up the message to clarify the room number (to try and minimize confusion if the player approaches the
        # door from the other side).
        turret_door_text = patcher.scenes[Scenes.SCIENCE_LABS].scene_text[0]["text"]
        patcher.scenes[Scenes.SCIENCE_LABS].scene_text[0]["text"] = \
            turret_door_text[0:65] + "Room 1\ncannon " + turret_door_text[72:]

        # Change the Security Crystal's "play sound" function call into a "set song to play" call when it tries to play
        # its music theme, so it will actually play correctly when entering the fight from the rear entrance.
        patcher.scenes[Scenes.SCIENCE_LABS].write_ovl_int16(0x10F46, 0x7274)

        # Make it so checking the Control Room doors will play the map's song, in the event the player tries going
        # backwards after killing the Security Crystal and having there be no music.
        science_door_music_player_start = len(patcher.scenes[Scenes.SCIENCE_LABS].overlay)
        patcher.scenes[Scenes.SCIENCE_LABS].write_ovl_int32s(science_door_music_player_start,
                                                             patches.door_map_music_player)
        patcher.scenes[Scenes.SCIENCE_LABS].doors[10]["door_flags"] |= DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.SCIENCE_LABS].doors[10]["extra_condition_ptr"] = \
            science_door_music_player_start + SCENE_OVERLAY_RDRAM_START
        patcher.scenes[Scenes.SCIENCE_LABS].doors[11]["door_flags"] |= DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.SCIENCE_LABS].doors[11]["extra_condition_ptr"] = \
            science_door_music_player_start + SCENE_OVERLAY_RDRAM_START

        # Make Carrie's loading zones universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.SCIENCE_CONVEYORS].actor_lists["proxy"][96]["spawn_flags"] = 0
        patcher.scenes[Scenes.SCIENCE_CONVEYORS].actor_lists["proxy"][98]["delete"] = True
        patcher.scenes[Scenes.SCIENCE_LABS].actor_lists["proxy"][166]["spawn_flags"] = 0
        patcher.scenes[Scenes.SCIENCE_LABS].actor_lists["proxy"][167]["delete"] = True
        # Make Carrie's White Jewels universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.SCIENCE_CONVEYORS].actor_lists["proxy"][77]["delete"] = True
        patcher.scenes[Scenes.SCIENCE_CONVEYORS].actor_lists["proxy"][78]["spawn_flags"] = 0
        patcher.scenes[Scenes.SCIENCE_LABS].actor_lists["proxy"][101]["delete"] = True
        patcher.scenes[Scenes.SCIENCE_LABS].actor_lists["proxy"][102]["delete"] = True
        patcher.scenes[Scenes.SCIENCE_LABS].actor_lists["proxy"][103]["spawn_flags"] = 0
        patcher.scenes[Scenes.SCIENCE_LABS].actor_lists["proxy"][104]["spawn_flags"] = 0


        # # # # # # # # # # #
        # DUEL TOWER EDITS  #
        # # # # # # # # # # #
        # Clear the Cornell-only setting from the Giant Werewolf boss intro cutscene in the universal cutscene settings
        # table so anyone will be allowed to trigger it. Just like with the Castle Center bosses, we'll instead rely
        # entirely on the actor system to ensure the trigger only spawns for the correct characters.
        patcher.write_byte(0x118349, 0x00)
        # Make specific changes depending on what was chosen for the Duel Tower Final Boss (unless Character Dependant
        # was chosen, in which case we do nothing).
        # If Giant Werewolf was chosen, prevent the hardcoded Not Cornell checks on Arena 4 from passing for non-Cornell
        # characters and make the Giant Werewolf cutscene trigger universal to everyone.
        if slot_patch_info["options"]["duel_tower_final_boss"] == DuelTowerFinalBoss.option_giant_werewolf:
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x58D0, 0x00000000)  # NOP
            patcher.scenes[Scenes.DUEL_TOWER].actor_lists["init"][2]["spawn_flags"] = 0
            # Prevent the ceiling from falling in Arena 4 for everyone.
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x1A5C, 0x340D0002)  # ORI T5, R0, 0x0002
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x5B4C, 0x340E0002)  # ORI T6, R0, 0x0002
        # If Were-Tiger was chosen, make the hardcoded Not Cornell checks on Arena 4 pass even for Cornell and delete
        # the Giant Werewolf cutscene trigger actor entirely.
        elif slot_patch_info["options"]["duel_tower_final_boss"] == DuelTowerFinalBoss.option_were_tiger:
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x58D0, 0x10000003)  # B [forward 0x03]
            patcher.scenes[Scenes.DUEL_TOWER].actor_lists["init"][2]["delete"] = True
            # Make the ceiling fall in Arena 4 for everyone.
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x1A5C, 0x340D0000)  # ORI T5, R0, 0x0000
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x5B4C, 0x340E0000)  # ORI T6, R0, 0x0000

        # Make Reinhardt's White Jewels universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][117]["delete"] = True
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][118]["spawn_flags"] = 0
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][119]["delete"] = True
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][120]["spawn_flags"] = 0
        # Make Reinhardt's loading zones universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][157]["spawn_flags"] = 0
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][158]["spawn_flags"] = 0
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][159]["delete"] = True
        patcher.scenes[Scenes.DUEL_TOWER].actor_lists["proxy"][160]["delete"] = True


        # # # # # # # # # # # # # # #
        # TOWER OF EXECUTION EDITS  #
        # # # # # # # # # # # # # # #
        # Make the Tower of Execution 3HB pillars that spawn 1HBs not set their flags, and have said 1HBs
        # set the flags instead.
        patcher.scenes[Scenes.EXECUTION_MAIN].enemy_pillars[0]["flag_id"] = 0
        patcher.scenes[Scenes.EXECUTION_MAIN].enemy_pillars[3]["flag_id"] = 0
        patcher.scenes[Scenes.EXECUTION_MAIN].enemy_pillars[4]["flag_id"] = 0
        patcher.scenes[Scenes.EXECUTION_MAIN].one_hit_breakables[10]["flag_id"] = \
            CVLOD_LOCATIONS_INFO[loc_names.toe_first_pillar].flag_id
        patcher.scenes[Scenes.EXECUTION_MAIN].one_hit_breakables[11]["flag_id"] = \
            CVLOD_LOCATIONS_INFO[loc_names.toe_last_pillar].flag_id

        # Make Reinhardt's White Jewels universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][99]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][100]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][101]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][102]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][103]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][104]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_1].actor_lists["proxy"][78]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_1].actor_lists["proxy"][79]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][86]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][87]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][88]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][89]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][90]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][91]["spawn_flags"] = 0
        # Make Reinhardt's loading zones universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][148]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_MAIN].actor_lists["proxy"][155]["delete"] = True
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][135]["spawn_flags"] = 0
        patcher.scenes[Scenes.EXECUTION_SIDE_ROOMS_2].actor_lists["proxy"][136]["delete"] = True


        # # # # # # # # # # # # # #
        # TOWER OF SORCERY EDITS  #
        # # # # # # # # # # # # # #
        # Make the pink diamond always drop the same 3 items, prevent it from setting its own flag when broken, and
        # have it set individual flags on each of its drops.
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int32(0x3E94, 0x00106040)  # SLL   T4, S0, 1
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int32(0x369C, 0x00000000)  # NOP
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int32(0x366C, 0x0C0BAB10)  # JAL   0x802EAC30
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int32s(0x70C0, patches.pink_sorcery_diamond_customizer)
        # Write the randomizer items manually here.
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(
            0x5400, loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_1].flag_id])
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(
            0x5402, loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_2].flag_id])
        patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(
            0x5404, loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_3].flag_id])

        # Make Carrie's White Jewels universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][128]["delete"] = True
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][129]["delete"] = True
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][130]["delete"] = True
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][131]["spawn_flags"] = 0
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][132]["spawn_flags"] = 0
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][133]["spawn_flags"] = 0
        # Make Carrie's loading zones universal to everyone and remove Cornell's.
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][144]["spawn_flags"] = 0
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][145]["spawn_flags"] = 0
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][146]["delete"] = True
        patcher.scenes[Scenes.TOWER_OF_SORCERY].actor_lists["proxy"][147]["delete"] = True


        # # # # # # # # # # # # #
        # ROOM OF CLOCKS EDITS  #
        # # # # # # # # # # # # #
        # Depending on what was chosen for the Room of Clocks Boss option, make only one character's elevator loading
        # zone (the one corresponding to that boss) universal and remove the other two.
        if slot_patch_info["options"]["room_of_clocks_boss"] == RoomOfClocksBoss.option_death:
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][35]["spawn_flags"] = 0  # Reinhardt (Death)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][38]["delete"] = True    # Carrie (Actrise)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][41]["delete"] = True    # Cornell (Ortega)
        elif slot_patch_info["options"]["room_of_clocks_boss"] == RoomOfClocksBoss.option_actrise:
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][35]["delete"] = True    # Reinhardt (Death)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][38]["spawn_flags"] = 0  # Carrie (Actrise)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][41]["delete"] = True    # Cornell (Ortega)
        elif slot_patch_info["options"]["room_of_clocks_boss"] == RoomOfClocksBoss.option_ortega:
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][35]["delete"] = True    # Reinhardt (Death)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][38]["delete"] = True    # Carrie (Actrise)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][41]["spawn_flags"] = 0  # Cornell (Ortega)
        # Henry normally doesn't have a boss here. So if Character Dependent is chosen, we'll give him Death.
        # Otherwise, don't touch Carrie and Cornell's elevator zones.
        else:
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][35]["spawn_flags"] |= ActorSpawnFlags.HENRY

        # Make Reinhardt and Carrie's White Jewel universal for everyone and remove Cornell's.
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][18]["delete"] = True
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][19]["spawn_flags"] = 0
        # Make Reinhardt's start/end loading zones universal to everyone and remove Carrie and Cornell's.
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][34]["spawn_flags"] = 0
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][36]["spawn_flags"] = 0
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][37]["delete"] = True
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][39]["delete"] = True
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][40]["delete"] = True
        patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][42]["delete"] = True
        # Make the elevator zones to Room of Clocks in Castle Keep Exterior universal to everyone as well.
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["proxy"][55]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["proxy"][56]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["proxy"][57]["spawn_flags"] = 0


        # # # # # # # # # # #
        # CLOCK TOWER EDITS #
        # # # # # # # # # # #
        # Lock the door in Clock Tower Face leading out to the grand abyss scene with Clocktower Key D.
        # It's the same door in-universe as Clocktower Door D but on a different scene.
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].doors[5]["door_flags"] = DoorFlags.LOCKED_BY_KEY
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].doors[5]["flag_id"] = 0x29E  # Clocktower Door D unlocked flag.
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].doors[5]["item_id"] = Items.CLOCKTOWER_KEY_D
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].doors[5]["flag_locked_text_id"] = 0x04
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].doors[5]["unlocked_text_id"] = 0x05
        # Custom text for the new locked door instance (copy the Door E text and change the E's to D's).
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].scene_text += [
            CVLoDSceneTextEntry(text=patcher.scenes[Scenes.CLOCK_TOWER_FACE].scene_text[1]["text"][0:33] + "D" + \
                                     patcher.scenes[Scenes.CLOCK_TOWER_FACE].scene_text[1]["text"][34:]),
            CVLoDSceneTextEntry(text=patcher.scenes[Scenes.CLOCK_TOWER_FACE].scene_text[2]["text"][0:20] + "D" + \
                                     patcher.scenes[Scenes.CLOCK_TOWER_FACE].scene_text[2]["text"][21:])
        ]

        # Make Reinhardt and Carrie's White Jewels universal for everyone and remove Cornell's.
        patcher.scenes[Scenes.CLOCK_TOWER_GEAR_CLIMB].actor_lists["room 1"][3]["delete"] = True
        patcher.scenes[Scenes.CLOCK_TOWER_GEAR_CLIMB].actor_lists["room 1"][4]["spawn_flags"] = 0
        patcher.scenes[Scenes.CLOCK_TOWER_ABYSS].actor_lists["proxy"][24]["delete"] = True
        patcher.scenes[Scenes.CLOCK_TOWER_ABYSS].actor_lists["proxy"][25]["delete"] = True
        patcher.scenes[Scenes.CLOCK_TOWER_ABYSS].actor_lists["proxy"][26]["spawn_flags"] = 0
        patcher.scenes[Scenes.CLOCK_TOWER_ABYSS].actor_lists["proxy"][27]["spawn_flags"] = 0
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].actor_lists["room 0"][17]["delete"] = True
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].actor_lists["room 0"][18]["spawn_flags"] = 0
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].actor_lists["room 0"][19]["delete"] = True
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].actor_lists["room 0"][20]["spawn_flags"] = 0
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].actor_lists["room 1"][22]["delete"] = True
        patcher.scenes[Scenes.CLOCK_TOWER_FACE].actor_lists["room 1"][23]["spawn_flags"] = 0


        # # # # # # # # # # #
        # CASTLE KEEP EDITS #
        # # # # # # # # # # #
        # Make the Renon's Departure cutscene trigger universal to everyone (including Henry, whom it's normally set to
        # not spawn for) and stop it from spawning if in the castle escape sequence.
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][1]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][1]["flag_id"] = 0x17D  # Castle escape flag
        # If the Renon Fight Condition is Never, then make every money spent check in the Renon's Departure cutscene
        # always assume the player spent nothing so the fight should never trigger with the appropriate dialogue.
        if slot_patch_info["options"]["renon_fight_condition"] == RenonFightCondition.option_never:
            patcher.write_int32(0x294,  0x34180000, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T8, R0, 0x0000
            patcher.write_int32(0x2C4,  0x34080000, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T0, R0, 0x0000
            patcher.write_int32(0x3E4,  0x34180000, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T8, R0, 0x0000
            patcher.write_int32(0x434,  0x340F0000, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T7, R0, 0x0000
            patcher.write_int32(0x6A8,  0x340D0000, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T5, R0, 0x0000
            patcher.write_int32(0x18CC, 0x34090000, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T1, R0, 0x0000
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int32(0x13C0, 0x34090000)  # ORI  T1, R0, 0x0000
        # If the Renon Fight Condition is Always, then make every money spent check in the Renon's Departure cutscene
        # always assume the player spent 30K so the fight should always trigger with the appropriate dialogue.
        elif slot_patch_info["options"]["renon_fight_condition"] == RenonFightCondition.option_always:
            patcher.write_int32(0x294,  0x34187531, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T8, R0, 0x7531
            patcher.write_int32(0x2C4,  0x34087531, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T0, R0, 0x7531
            patcher.write_int32(0x3E4,  0x34187531, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T8, R0, 0x7531
            patcher.write_int32(0x434,  0x340F7531, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T7, R0, 0x7531
            patcher.write_int32(0x6A8,  0x340D7531, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T5, R0, 0x7531
            patcher.write_int32(0x18CC, 0x34097531, NIFiles.OVERLAY_CS_RENONS_DEPARTURE)  # ORI  T1, R0, 0x7531
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int32(0x13C0, 0x34097531)  # ORI  T1, R0, 0x7531
        # Otherwise, If the Renon Fight Condition option is Spend 30K, put the cutscene trigger actor for it on the
        # custom Renon spawn check as well and don't touch any of the money spent checks.
        else:
            renon_cutscene_check_location = len(patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].overlay)
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int32s(renon_cutscene_check_location,
                                                                         patches.renon_cutscene_checker)
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][1]["extra_condition_ptr"] = \
                renon_cutscene_check_location + SCENE_OVERLAY_RDRAM_START
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][1]["spawn_flags"] |= \
                ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED

        # If the Vincent Fight Condition is Always, make the Vincent fight intro cutscene trigger universal to everyone
        # and remove the "16 days passed?" check in its cutscene trigger settings.
        if slot_patch_info["options"]["vincent_fight_condition"] == VincentFightCondition.option_always:
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][2]["spawn_flags"] = 0
            patcher.write_int16(0x1181A4,  0x0000)
        # If the Vincent Fight Condition is Never, remove the cutscene trigger entirely.
        elif slot_patch_info["options"]["vincent_fight_condition"] == VincentFightCondition.option_never:
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][2]["delete"] = True
        # Otherwise, if it's Wait 16 Days, simply make the trigger universal and do nothing further to it.
        else:
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][2]["spawn_flags"] = 0

        # Make the escape sequence Malus cutscene triggers universal to everyone.
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][3]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].actor_lists["init"][4]["spawn_flags"] = 0
        # Remove Cornell's White Jewel from Dracula's chamber and make Reinhardt and Carrie's universal.
        patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["proxy"][4]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["proxy"][5]["delete"] = True

        # If the Castle Keep Ending Sequence option is Cornell, make Cornell's cutscene trigger in Dracula's chamber
        # universal to everyone and remove Reinhardt and Carrie's.
        if slot_patch_info["options"]["castle_keep_ending_sequence"] == CastleKeepEndingSequence.option_cornell:
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][0]["delete"] = True
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][1]["spawn_flags"] = 0
            # Force Dracula to have all his Cornell behaviors for Reinhardt/Carrie/Henry.
            patcher.write_int32(0x904, 0x34050002, NIFiles.OVERLAY_CS_FAKE_DRACULA_BATTLE_INTRO)  # ORI  A1, R0, 0x0002
            # Red high energy ring.
            patcher.write_int32(0x40C, 0x34030002, NIFiles.OVERLAY_DRACULA_ENERGY_RING)  # ORI  V1, R0, 0x0002
            # Red low energy ring.
            patcher.write_int32(0x650, 0x34030002, NIFiles.OVERLAY_DRACULA_ENERGY_RING)  # ORI  V1, R0, 0x0002
            # Move pool with electric attacks and no flamethrower.
            patcher.write_int32(0x9388, 0x34020002, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V0, R0, 0x0002
            # Blue fire bats.
            patcher.write_int32(0xB83C, 0x34030002, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V1, R0, 0x0002
            # Cutscene when beaten by Cornell.
            patcher.write_int32(0x90FC, 0x34020002, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V0, R0, 0x0002
            patcher.write_int32(0x9138, 0x34020002, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V0, R0, 0x0002

        # Otherwise, if a Reinhardt/Carrie option was chosen, remove Cornell's trigger, make Reinhardt and Carrie's
        # universal, and force the good ending check after Fake Dracula to always pass.
        else:
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][0]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][1]["delete"] = True
            # Force Fake Dracula to have all his Reinhardt/Carrie behaviors for Cornell/Henry.
            patcher.write_int32(0x904, 0x34050000, NIFiles.OVERLAY_CS_FAKE_DRACULA_BATTLE_INTRO)  # ORI  A1, R0, 0x0000
            # Blue high energy ring.
            patcher.write_int32(0x40C, 0x34030000, NIFiles.OVERLAY_DRACULA_ENERGY_RING)  # ORI  V1, R0, 0x0000
            # Blue low energy ring.
            patcher.write_int32(0x650, 0x34030000, NIFiles.OVERLAY_DRACULA_ENERGY_RING)  # ORI  V1, R0, 0x0000
            # Move pool with flamethrower attack and no electric attacks.
            patcher.write_int32(0x9388, 0x34020000, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V0, R0, 0x0000
            # Orange fire bats.
            patcher.write_int32(0xB83C, 0x34030000, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V1, R0, 0x0000
            # Cutscene when beaten by Reinhardt/Carrie.
            patcher.write_int32(0x90FC, 0x34020000, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V0, R0, 0x0000
            patcher.write_int32(0x9138, 0x34020000, NIFiles.OVERLAY_FAKE_DRACULA)  # ORI  V0, R0, 0x0000
            # If the Castle Keep Ending Sequence option is Reinhardt Carrie Good, make the White Jewel clear the
            # Bad Ending flag upon spawning to ensure we will never get it.
            if slot_patch_info["options"]["castle_keep_ending_sequence"] == \
                    CastleKeepEndingSequence.option_reinhardt_carrie_good:
                patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["proxy"][4]["spawn_flags"] = \
                    ActorSpawnFlags.CLEAR_FLAG_ON_SPAWN
                patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["proxy"][4]["flag_id"] = 0x1A8
            # If the Castle Keep Ending Sequence option is Reinhardt Carrie Bad, make the White Jewel set the
            # Bad Ending flag upon spawning to ensure we will always get it. Otherwise, if it's Reinhardt Carrie Timed,
            # don't modify this any further.
            elif slot_patch_info["options"]["castle_keep_ending_sequence"] == \
                    CastleKeepEndingSequence.option_reinhardt_carrie_bad:
                patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["proxy"][4]["spawn_flags"] = \
                    ActorSpawnFlags.SET_FLAG_ON_SPAWN
                patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["proxy"][4]["flag_id"] = 0x1A8

        # Make the castle crumbling cutscene send Cornell and Henry to their respective endings.
        # NOP the branch instruction that skips starting a different cutscene if the player isn't Reinhardt or Carrie.
        # Reinhardt's routine should run for the other two characters.
        patcher.write_int32(0x1CF4, 0x00000000, NIFiles.OVERLAY_CS_CASTLE_CRUMBLING)
        # At the end of Reinhardt's ending cutscene setter routine, jump to a hack that switches it to Cornell or Henry
        # instead.
        patcher.write_int32(0x1DB4, 0x0B80107C, NIFiles.OVERLAY_CS_CASTLE_CRUMBLING) # J 0x0E0041F0
        patcher.write_int32s(0x41F0, patches.castle_crumbling_cornell_henry_checker,
                             NIFiles.OVERLAY_CS_CASTLE_CRUMBLING)

        # Make the Bad Ending Malus Appears cutscene send Cornell and Henry to their own respective bad ends.
        patcher.write_int32(0xBD0, 0x0B800580, NIFiles.OVERLAY_CS_BAD_ENDING_MALUS_APPEARS) # J 0x0E001600
        patcher.write_int32s(0x1600, patches.malus_bad_end_cornell_henry_checker,
                             NIFiles.OVERLAY_CS_BAD_ENDING_MALUS_APPEARS)

        # Make the Dracula Ultimate Defeated cutscene send all non-Cornell characters to their respective good ends.
        patcher.write_int32(0x4EFC, 0x0B801A18, NIFiles.OVERLAY_CS_DRACULA_ULTIMATE_DEFEATED) # J 0x0E006860
        patcher.write_int32s(0x6860, patches.dracula_ultimate_non_cornell_checker,
                             NIFiles.OVERLAY_CS_DRACULA_ULTIMATE_DEFEATED)

        # Make all children rescued checks in Henry's ending either pass or fail depending on if the Reinhardt/Carrie
        # Bad Ending flag is set or not.
        patcher.write_int16(0x2C6, 0x01A8, NIFiles.OVERLAY_CS_HENRY_ENDING)
        patcher.write_int32(0x2C8, 0x54400008, NIFiles.OVERLAY_CS_HENRY_ENDING)  # BNEZL  V0, [forward 0x08]
        patcher.write_int16(0x2FA, 0x01A8, NIFiles.OVERLAY_CS_HENRY_ENDING)
        patcher.write_int32(0x2FC, 0x1440000B, NIFiles.OVERLAY_CS_HENRY_ENDING)  # BNEZ   V0, [forward 0x0B]
        patcher.write_int16(0x33E, 0x01A8, NIFiles.OVERLAY_CS_HENRY_ENDING)
        patcher.write_int32(0x340, 0x14400009, NIFiles.OVERLAY_CS_HENRY_ENDING)  # BNEZ   V0, [forward 0x09]
        patcher.write_int16(0x3CA, 0x01A8, NIFiles.OVERLAY_CS_HENRY_ENDING)
        patcher.write_int32(0x3CC, 0x54400007, NIFiles.OVERLAY_CS_HENRY_ENDING)  # BNEZL  V0, [forward 0x07]
        patcher.write_int16(0x3FA, 0x01A8, NIFiles.OVERLAY_CS_HENRY_ENDING)
        patcher.write_int32(0x3FC, 0x1440000B, NIFiles.OVERLAY_CS_HENRY_ENDING)  # BNEZ   V0, [forward 0x0B]
        patcher.write_int16(0x43E, 0x01A8, NIFiles.OVERLAY_CS_HENRY_ENDING)
        patcher.write_int32(0x440, 0x14400008, NIFiles.OVERLAY_CS_HENRY_ENDING)  # BNEZ   V0, [forward 0x08]
        patcher.write_int16(0x24A, 0x01A8, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)
        patcher.write_int32(0x258, 0x14400005, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)  # BNEZ   V0, [forward 0x05]
        patcher.write_int16(0x276, 0x01A8, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)
        patcher.write_int32(0x278, 0x14400005, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)  # BNEZ   V0, [forward 0x05]
        patcher.write_int16(0x296, 0x01A8, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)
        patcher.write_int32(0x298, 0x14400005, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)  # BNEZ   V0, [forward 0x05]
        patcher.write_int16(0x2B6, 0x01A8, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)
        patcher.write_int32(0x2B8, 0x14400005, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)  # BNEZ   V0, [forward 0x05]
        patcher.write_int16(0x2D6, 0x01A8, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)
        patcher.write_int32(0x2D8, 0x14400005, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)  # BNEZ   V0, [forward 0x05]
        patcher.write_int16(0x2F6, 0x01A8, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)
        patcher.write_int32(0x2F8, 0x14400004, NIFiles.OVERLAY_CS_INTRO_NARRATION_HENRY)  # BNEZ   V0, [forward 0x04]

        # Loop over EVERY actor in EVERY list, find all Location-associated instances, and either delete them if they
        # are exclusive to non-Normal difficulties or try writing an Item they should have onto them if they aren't.
        for scene in patcher.scenes:
            for list_name, actor_list in scene.actor_lists.items():
                for actor in actor_list:
                    # If the actor is not a Location-associated actor, or if it's already marked for deletion, skip it.
                    if actor["object_id"] not in [Objects.ONE_HIT_BREAKABLE, Objects.THREE_HIT_BREAKABLE,
                                                  Objects.PICKUP_ITEM] + SPECIAL_1HBS or "delete" in actor:
                        continue

                    # If it's not an enemy pillar actor, check its spawn flags for what difficulties it spawns on.
                    # If it spawns on Easy and/or Hard but NOT on Normal, mark it for deletion and skip it.
                    if list_name != "pillars":
                        if actor["spawn_flags"] & (ActorSpawnFlags.EASY | ActorSpawnFlags.HARD) and not \
                                actor["spawn_flags"] & ActorSpawnFlags.NORMAL:
                            actor["delete"] = True
                            continue
                        # If it is a Normal actor, set all difficulty flags to make it more visible in the actor list.
                        else:
                            actor["spawn_flags"] |= ActorSpawnFlags.ALL_DIFFICULTIES

                    # If we make it here, then the actor is safe to write a rando Item onto. In which case, do what must
                    # be done for that actor to retrieve its associated item event flag.

                    # If it's a freestanding pickup, the flag to check is in its Var A.
                    if actor["object_id"] == Objects.PICKUP_ITEM:
                        # If the pickup is a text spot or a White Jewel (wherein Var A is actually a White Jewel ID,
                        # not a flag ID), skip it.
                        if actor["var_c"] == Pickups.WHITE_JEWEL or actor["var_c"] > len(Pickups) + 1:
                            continue
                        # Check if the flag ID has location values associated with it in the slot patch info. If it
                        # does, write that value in the pickup's Var C.
                        if actor["var_a"] in loc_values:
                            actor["var_c"] = loc_values[actor["var_a"]]
                            # Un-set the Expire bit in its pickup flags in Var B.
                            actor["var_b"] &= PickupFlags.DONT_EXPIRE
                    # If it's a regular 1HB, the flag to check AND the value to write the new Item over is in the 1HB
                    # data for the scene specified in the actor's Var C.
                    if actor["object_id"] == Objects.ONE_HIT_BREAKABLE:
                        if scene.one_hit_breakables[actor["var_c"]]["flag_id"] in loc_values:
                            scene.one_hit_breakables[actor["var_c"]]["pickup_id"] = \
                                loc_values[scene.one_hit_breakables[actor["var_c"]]["flag_id"]]
                            # Un-set the Expire bit in its pickup flags.
                            scene.one_hit_breakables[actor["var_c"]]["pickup_flags"] &= PickupFlags.DONT_EXPIRE
                    # If it's a special 1HB, then it's similar to the regular 1HB but in the special 1HB data instead.
                    if actor["object_id"] in SPECIAL_1HBS:
                        if scene.one_hit_special_breakables[actor["var_c"]]["flag_id"] in loc_values:
                            scene.one_hit_special_breakables[actor["var_c"]]["pickup_id"] = \
                                loc_values[scene.one_hit_special_breakables[actor["var_c"]]["flag_id"]]
                            # Un-set the Expire bit in its pickup flags.
                            scene.one_hit_special_breakables[actor["var_c"]]["pickup_flags"] &= PickupFlags.DONT_EXPIRE


        return patcher.get_output_rom()

        # Make the final Cerberus in Villa Front Yard
        # un-set the Villa entrance portcullis closed flag for all characters (not just Henry).
        patcher.write_int32(0x35A4, 0x00000000, NIFiles.OVERLAY_CERBERUS)

        # Give the Gardener his Cornell behavior for everyone.
        patcher.write_int32(0x490, 0x24020002, NIFiles.OVERLAY_GARDENER)  # ADDIU V0, R0, 0x0002
        patcher.write_int32(0xD20, 0x00000000, NIFiles.OVERLAY_GARDENER)
        patcher.write_int32(0x13CC, 0x00000000, NIFiles.OVERLAY_GARDENER)

        # Change the player spawn coordinates for Villa maze entrance 4 to put the player in front of the child escape
        # gate instead of the rear maze exit door.
        patcher.write_int16s(0x10F876, [0x0290,   # Player X position
                                         0x0000,   # Player Y position
                                         0x021B,   # Player Z position
                                         0x8000,   # Player rotation
                                         0x02A0,   # Camera X position
                                         0x000D,   # Camera Y position
                                         0x021B,   # Camera Z position
                                         0x0290,   # Focus point X position
                                         0x000D,   # Focus point Y position
                                         0x021B])  # Focus point Z position

        # Special message for when checking the plaque next to the escape gate.
        patcher.write_bytes(0x79712C, cvlod_string_to_bytearray("「 TIME GATE\n"
                                                                 "Present Her brooch\n"
                                                                 "to enter.\n"
                                                                 "    -Saint Germain」»\t", wrap=False)[0])
        patcher.write_bytes(0x796FD6, cvlod_string_to_bytearray("Is that plaque referring\n"
                                                                 "to the Rose Brooch?\n"
                                                                 "You should find it...»\t")[0])

        # Make the escape gates check for the Rose Brooch in the player's inventory (without subtracting it) before
        # letting them through.
        patcher.write_int32s(0xFFCF48, patches.rose_brooch_checker)
        # Malus gate
        patcher.write_int16(0x797C0C, 0x0200)
        patcher.write_int32(0x797C10, 0x803FCF48)
        patcher.write_int16(0x797C38, 0x0200)
        patcher.write_int32(0x797C3C, 0x803FCF48)
        # Henry gate
        patcher.write_int16(0x797FD4, 0x0200)
        patcher.write_int32(0x797FD8, 0x803FCF48)
        patcher.write_int16(0x798000, 0x0200)
        patcher.write_int32(0x798004, 0x803FCF48)

        # Add a new loading zone behind the "time gate" in the Villa maze. To do this, we'll have to relocate the map's
        # existing loading zone properties and update the pointer to them.
        patcher.write_int32(0x110D50, 0x803FCF78)
        patcher.write_bytes(0xFFCF78, patcher.read_bytes(0x79807C, 0x3C))
        # Add the new loading zone property data on the end.
        patcher.write_int32s(0xFFCFB4, [0x00000604, 0x03010000, 0x02D0001E, 0x023002BC, 0x00000208])
        # Replace the Hard-exclusive item in Malus's bush with the new loading zone actor.
        patcher.write_int32s(0x799048, [0x00000000, 0x442E0000, 0x00000000, 0x44036000,
                                         0x01AF0000, 0x00000000, 0x00030000, 0x00000000])

        # Change the color of the fourth loading zone fade settings entry.
        patcher.write_int32(0x110D2C, 0xE1B9FF00)
        # Era switcher hack
        patcher.write_int32(0xD3C08, 0x080FF3F8)  # J 0x803FCFE0
        patcher.write_int32s(0xFFCFE0, patches.era_switcher)

        # Change the map name display actor in the Villa crypt to use entry 0x02 instead of 0x11 and have entry 0x02
        # react to entrance 0x02 (the Villa end's).
        patcher.write_byte(0x861, 0x02, NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        patcher.write_byte(0x7D6561, 0x02)
        # Replace the second map name display settings entry for the Villa end with the one for our year text.
        patcher.write_int32s(0x910, [0x00060100, 0x04642E00], NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        # Replace the far rear Iron Thorn Fenced Garden text spot with the new map name display actor.
        patcher.write_int32s(0x7981E8, [0x00000000, 0x00000000, 0x00000000, 0x00000000,
                                         0x219F0000, 0x00000000, 0x00110000, 0x00000000])
        # Hack to change the map name display string to a custom year string when time traveling.
        patcher.write_int16(0x3C6, 0x8040, NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        patcher.write_int16(0x3CA, 0xD040, NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        patcher.write_int32s(0xFFD040, patches.map_name_year_switcher)
        # Year text for the above map name display hack.
        patcher.write_bytes(0xFFD020, cvlod_string_to_bytearray("1852\t1844\t")[0])

        # Make Gilles De Rais spawn in the Villa crypt for everyone (not just Cornell).
        # This should instead be controlled by the actor list.
        patcher.write_byte(0x195, 0x00, NIFiles.OVERLAY_GILLES_DE_RAIS)

        # Apply the child Henry gate checks to the two doors leading to the vampire crypt,
        # so he can't be brought in there.
        patcher.write_byte(0x797BB4, 0x53)
        patcher.write_int32(0x797BB8, 0x802E4C34)
        patcher.write_byte(0x797D6C, 0x52)
        patcher.write_int32(0x797D70, 0x802E4C34)

        # Hack to make the Forest, CW and Villa intro cutscenes play at the start of their levels no matter what map
        # came before them
        # #patcher.write_int32(0x97244, 0x803FDD60)
        # #patcher.write_int32s(0xBFDD60, patches.forest_cw_villa_intro_cs_player)

        # Enable swapping characters when loading into a map by holding L.
        # patcher.write_int32(0x97294, 0x803FDFC4)
        # patcher.write_int32(0x19710, 0x080FF80E)  # J 0x803FE038
        # patcher.write_int32s(0xBFDFC4, patches.character_changer)

        # Villa coffin time-of-day hack
        # patcher.write_byte(0xD9D83, 0x74)
        # patcher.write_int32(0xD9D84, 0x080FF14D)  # J 0x803FC534
        # patcher.write_int32s(0xBFC534, patches.coffin_time_checker)

        # Disable the 3HBs checking and setting flags when breaking them and enable their individual items checking and
        # setting flags instead.
        if slot_patch_info["options"]["multi_hit_breakables"]:
            patcher.write_int16(0xE3488, 0x1000)
            patcher.write_int32(0xE3800, 0x24050000)  # ADDIU	A1, R0, 0x0000
            patcher.write_byte(0xE39EB, 0x00)
            patcher.write_int32(0xE3A58, 0x0C0FF0D4),  # JAL   0x803FC350
            patcher.write_int32s(0xFFC350, patches.three_hit_item_flags_setter)
            # Villa foyer chandelier-specific functions (yeah, KCEK was really insistent on having special handling just
            # for this one)
            patcher.write_int32(0xE2F4C, 0x00000000)  # NOP
            patcher.write_int32(0xE3114, 0x0C0FF0DE),  # JAL   0x803FC378
            patcher.write_int32s(0xFFC378, patches.chandelier_item_flags_setter)

            # New flag values to put in each 3HB vanilla flag's spot
            patcher.write_int16(0x7816F6, 0x02B8)  # CW upper rampart save nub
            patcher.write_int16(0x78171A, 0x02BD)  # CW Dracula switch slab
            patcher.write_int16(0x787F66, 0x0302)  # Villa foyer chandelier
            patcher.write_int16(0x79F19E, 0x0307)  # Tunnel twin arrows rock
            patcher.write_int16(0x79F1B6, 0x030C)  # Tunnel lonesome bucket pit rock
            patcher.write_int16(0x7A41B6, 0x030F)  # UW poison parkour ledge
            patcher.write_int16(0x7A41DA, 0x0315)  # UW skeleton crusher ledge
            patcher.write_int16(0x7A8AF6, 0x0318)  # CC Behemoth crate
            patcher.write_int16(0x7AD836, 0x031D)  # CC elevator pedestal
            patcher.write_int16(0x7B0592, 0x0320)  # CC lizard locker slab
            patcher.write_int16(0x7D0DDE, 0x0324)  # CT gear climb battery slab
            patcher.write_int16(0x7D0DC6, 0x032A)  # CT gear climb top corner slab
            patcher.write_int16(0x829A16, 0x032D)  # CT giant chasm farside climb
            patcher.write_int16(0x82CC8A, 0x0330)  # CT beneath final slide

        # Skip the "There is a white jewel" text so checking one saves the game instantly.
        # patcher.write_int32s(0xEFC72, [0x00020002 for _ in range(37)])
        # patcher.write_int32(0xA8FC0, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Skip the yes/no prompts when activating things.
        # patcher.write_int32s(0xBFDACC, patches.map_text_redirector)
        # patcher.write_int32(0xA9084, 0x24020001)  # ADDIU V0, R0, 0x0001
        # patcher.write_int32(0xBEBE8, 0x0C0FF6B4)  # JAL   0x803FDAD0
        # Skip Vincent and Heinrich's mandatory-for-a-check dialogue
        # patcher.write_int32(0xBED9C, 0x0C0FF6DA)  # JAL   0x803FDB68
        # Skip the long yes/no prompt in the CC planetarium to set the pieces.
        # patcher.write_int32(0xB5C5DF, 0x24030001)  # ADDIU  V1, R0, 0x0001
        # Skip the yes/no prompt to activate the CC elevator.
        # patcher.write_int32(0xB5E3FB, 0x24020001)  # ADDIU  V0, R0, 0x0001
        # Skip the yes/no prompts to set Nitro/Mandragora at both walls.
        # patcher.write_int32(0xB5DF3E, 0x24030001)  # ADDIU  V1, R0, 0x0001

        # patcher.write_int32s(0xBFDD20, patches.special_descriptions_redirector)

        # Change the Stage Select menu options
        # patcher.write_int32s(0xADF64, patches.warp_menu_rewrite)
        # patcher.write_int32s(0x10E0C8, patches.warp_pointer_table)
        # for i in range(len(active_warp_list)):
        #    if i == 0:
        # patcher.write_byte(warp_map_offsets[i], get_stage_info(active_warp_list[i], "start map id"))
        # patcher.write_byte(warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "start spawn id"))
        #    else:
        # patcher.write_byte(warp_map_offsets[i], get_stage_info(active_warp_list[i], "mid map id"))
        # patcher.write_byte(warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "mid spawn id"))

        # Play the "teleportation" sound effect when teleporting
        # patcher.write_int32s(0xAE088, [0x08004FAB,  # J 0x80013EAC
        #                           0x2404019E])  # ADDIU A0, R0, 0x019E

        # Change the Stage Select menu's text to reflect its new purpose
        # patcher.write_bytes(0xEFAD0, cvlod_string_to_bytearray(f"Where to...?\t{active_warp_list[0]}\t"
        #                                              f"`{w1} {active_warp_list[1]}\t"
        #                                              f"`{w2} {active_warp_list[2]}\t"
        #                                              f"`{w3} {active_warp_list[3]}\t"
        #                                              f"`{w4} {active_warp_list[4]}\t"
        #                                              f"`{w5} {active_warp_list[5]}\t"
        #                                              f"`{w6} {active_warp_list[6]}\t"
        #                                              f"`{w7} {active_warp_list[7]}"))

        # Lizard-man save proofing
        # patcher.write_int32(0xA99AC, 0x080FF0B8)  # J 0x803FC2E0
        # patcher.write_int32s(0xBFC2E0, patches.boss_save_stopper)

        # Disable or guarantee the Bad Ending
        # if options.bad_ending_condition.value == options.bad_ending_condition.option_never:
        # patcher.write_int32(0xAEE5C6, 0x3C0A0000)  # LUI  T2, 0x0000
        # elif options.bad_ending_condition.value == options.bad_ending_condition.option_always:
        # patcher.write_int32(0xAEE5C6, 0x3C0A0040)  # LUI  T2, 0x0040

        # Play Castle Keep's song if teleporting in front of Dracula's door outside the escape sequence
        # patcher.write_int32(0x6E937C, 0x080FF12E)  # J 0x803FC4B8
        # patcher.write_int32s(0xBFC4B8, patches.ck_door_music_player)

        # Change the item healing values if "Nerf Healing" is turned on
        # if options.nerf_healing_items.value:
        # patcher.write_byte(0xB56371, 0x50)  # Healing kit   (100 -> 80)
        # patcher.write_byte(0xB56374, 0x32)  # Roast beef    ( 80 -> 50)
        # patcher.write_byte(0xB56377, 0x19)  # Roast chicken ( 50 -> 25)

        # Disable loading zone healing if turned off
        # if not options.loading_zone_heals.value:
        # patcher.write_byte(0xD99A5, 0x00)  # Skip all loading zone checks

        # Prevent the vanilla Magical Nitro transport's "can explode" flag from setting
        # patcher.write_int32(0xB5D7AA, 0x00000000)  # NOP

        # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes
        # patcher.write_byte(0xA6253D, 0x03)

        # Make the Special1 and 2 play sounds when you reach milestones with them.
        # patcher.write_int32s(0xBFDA50, patches.special_sound_notifs)
        # patcher.write_int32(0xBF240, 0x080FF694)  # J 0x803FDA50
        # patcher.write_int32(0xBF220, 0x080FF69E)  # J 0x803FDA78

        # Add data for White Jewel #22 (the new Duel Tower savepoint) at the end of the White Jewel ID data list
        # patcher.write_int16s(0x104AC8, [0x0000, 0x0006,
        #                            0x0013, 0x0015])

        # Fix a vanilla issue wherein saving in a character-exclusive stage as the other character would incorrectly
        # display the name of that character's equivalent stage on the save file instead of the one they're actually in.
        # patcher.write_byte(0xC9FE3, 0xD4)
        # patcher.write_byte(0xCA055, 0x08)
        # patcher.write_byte(0xCA066, 0x40)
        # patcher.write_int32(0xCA068, 0x860C17D0)  # LH T4, 0x17D0 (S0)
        # patcher.write_byte(0xCA06D, 0x08)
        # patcher.write_byte(0x104A31, 0x01)
        # patcher.write_byte(0x104A39, 0x01)
        # patcher.write_byte(0x104A89, 0x01)
        # patcher.write_byte(0x104A91, 0x01)
        # patcher.write_byte(0x104A99, 0x01)
        # patcher.write_byte(0x104AA1, 0x01)

        # for stage in active_stage_exits:
        #    for offset in get_stage_info(stage, "save number offsets"):
        # patcher.write_byte(offset, active_stage_exits[stage]["position"])

        # Disable time restrictions
        # if options.disable_time_restrictions.value:
        # Fountain
        # patcher.write_int32(0x6C2340, 0x00000000)  # NOP
        # patcher.write_int32(0x6C257C, 0x10000023)  # B [forward 0x23]
        # Rosa
        # patcher.write_byte(0xEEAAB, 0x00)
        # patcher.write_byte(0xEEAAD, 0x18)
        # Moon doors
        # patcher.write_int32(0xDC3E0, 0x00000000)  # NOP
        # patcher.write_int32(0xDC3E8, 0x00000000)  # NOP
        # Sun doors
        # patcher.write_int32(0xDC410, 0x00000000)  # NOP
        # patcher.write_int32(0xDC418, 0x00000000)  # NOP

        # Make received DeathLinks blow you to smithereens instead of kill you normally.
        # if options.death_link.value == options.death_link.option_explosive:
        # patcher.write_int32(0x27A70, 0x10000008)  # B [forward 0x08]
        # patcher.write_int32s(0xBFC0D0, patches.deathlink_nitro_edition)

        # Warp menu-opening code
        patcher.write_int32(0x86FE4, 0x0C0FF254)  # JAL	0x803FC950
        patcher.write_int32s(0xFFC950, patches.warp_menu_opener)

        # NPC item textbox hack
        patcher.write_int32s(0xFFC6F0, patches.npc_item_hack)
        # Change all the NPC item gives to run through the new function.
        # Fountain Top Shine
        patcher.write_int16(0x35E, 0x8040, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        patcher.write_int16(0x362, 0xC700, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        patcher.write_byte(0x367, 0x00, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        patcher.write_int16(0x36E, 0x0068, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        patcher.write_bytes(0x720, cvlod_string_to_bytearray("...»\t")[0], 371)
        # 6am Rose Patch
        patcher.write_int16(0x1E2, 0x8040, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        patcher.write_int16(0x1E6, 0xC700, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        patcher.write_byte(0x1EB, 0x01, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        patcher.write_int16(0x1F2, 0x0078, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        patcher.write_bytes(0x380, cvlod_string_to_bytearray("...»\t")[0], 370)
        # Vincent
        patcher.write_int16(0x180E, 0x8040, NIFiles.OVERLAY_VINCENT)
        patcher.write_int16(0x1812, 0xC700, NIFiles.OVERLAY_VINCENT)
        patcher.write_byte(0x1817, 0x02, NIFiles.OVERLAY_VINCENT)
        patcher.write_int16(0x181E, 0x027F, NIFiles.OVERLAY_VINCENT)
        patcher.write_bytes(0x78E776, cvlod_string_to_bytearray(" " * 173, wrap=False)[0])
        # Mary
        patcher.write_int16(0xB16, 0x8040, NIFiles.OVERLAY_MARY)
        patcher.write_int16(0xB1A, 0xC700, NIFiles.OVERLAY_MARY)
        patcher.write_byte(0xB1F, 0x03, NIFiles.OVERLAY_MARY)
        patcher.write_int16(0xB26, 0x0086, NIFiles.OVERLAY_MARY)
        patcher.write_bytes(0x78F40E, cvlod_string_to_bytearray(" " * 295, wrap=False)[0])
        # Heinrich
        patcher.write_int16(0x962A, 0x8040, NIFiles.OVERLAY_LIZARD_MEN)
        patcher.write_int16(0x962E, 0xC700, NIFiles.OVERLAY_LIZARD_MEN)
        patcher.write_byte(0x9633, 0x04, NIFiles.OVERLAY_LIZARD_MEN)
        patcher.write_int16(0x963A, 0x0284, NIFiles.OVERLAY_LIZARD_MEN)
        patcher.write_bytes(0x7B3210, cvlod_string_to_bytearray(" " * 415, wrap=False)[0])

        # Sub-weapon check function hook
        # patcher.write_int32(0xBF32C, 0x00000000)  # NOP
        # patcher.write_int32(0xBF330, 0x080FF05E)  # J	0x803FC178
        # patcher.write_int32s(0xBFC178, patches.give_subweapon_stopper)

        # Warp menu Special1 restriction
        # patcher.write_int32(0xADD68, 0x0C04AB12)  # JAL 0x8012AC48
        # patcher.write_int32s(0xADE28, patches.stage_select_overwrite)
        # patcher.write_byte(0xADE47, s1s_per_warp)

        # Dracula's door text pointer hijack
        # patcher.write_int32(0xD69F0, 0x080FF141)  # J 0x803FC504
        # patcher.write_int32s(0xBFC504, patches.dracula_door_text_redirector)

        # Dracula's chamber condition
        # patcher.write_int32(0xE2FDC, 0x0804AB25)  # J 0x8012AC78
        # patcher.write_int32s(0xADE84, patches.special_goal_checker)
        # patcher.write_bytes(0xBFCC48, [0xA0, 0x00, 0xFF, 0xFF, 0xA0, 0x01, 0xFF, 0xFF, 0xA0, 0x02, 0xFF, 0xFF, 0xA0, 0x03, 0xFF,
        #                           0xFF, 0xA0, 0x04, 0xFF, 0xFF, 0xA0, 0x05, 0xFF, 0xFF, 0xA0, 0x06, 0xFF, 0xFF, 0xA0, 0x07,
        #                           0xFF, 0xFF, 0xA0, 0x08, 0xFF, 0xFF, 0xA0, 0x09])
        # if options.draculas_condition.value == options.draculas_condition.option_crystal:
        # patcher.write_int32(0x6C8A54, 0x0C0FF0C1)  # JAL 0x803FC304
        # patcher.write_int32s(0xBFC304, patches.crystal_special2_giver)
        # patcher.write_bytes(0xBFCC6E, cvlod_string_to_bytearray(f"It won't budge!\n"
        #                                                   f"You'll need the power\n"
        #                                                   f"of the basement crystal\n"
        #                                                   f"to undo the seal.", True))
        #    special2_name = "Crystal "
        #    special2_text = "The crystal is on!\n" \
        #                    "Time to teach the old man\n" \
        #                    "a lesson!"
        # elif options.draculas_condition.value == options.draculas_condition.option_bosses:
        # patcher.write_int32(0xBBD50, 0x080FF18C)  # J	0x803FC630
        # patcher.write_int32s(0xBFC630, patches.boss_special2_giver)
        # patcher.write_bytes(0xBFCC6E, cvlod_string_to_bytearray(f"It won't budge!\n"
        #                                                   f"You'll need to defeat\n"
        #                                                   f"{required_s2s} powerful monsters\n"
        #                                                   f"to undo the seal.", True))
        #    special2_name = "Trophy  "
        #    special2_text = f"Proof you killed a powerful\n" \
        #                    f"Night Creature. Earn {required_s2s}/{total_s2s}\n" \
        #                    f"to battle Dracula."
        # elif options.draculas_condition.value == options.draculas_condition.option_specials:
        #    special2_name = "Special2"
        # patcher.write_bytes(0xBFCC6E, cvlod_string_to_bytearray(f"It won't budge!\n"
        #                                                   f"You'll need to find\n"
        #                                                   f"{required_s2s} Special2 jewels\n"
        #                                                   f"to undo the seal.", True))
        #    special2_text = f"Need {required_s2s}/{total_s2s} to kill Dracula.\n" \
        #                    f"Looking closely, you see...\n" \
        #                    f"a piece of him within?"
        # else:
        #    #patcher.write_byte(0xADE8F, 0x00)
        #    special2_name = "Special2"
        #    special2_text = "If you're reading this,\n" \
        #                    "how did you get a Special2!?"
        # patcher.write_byte(0xADE8F, required_s2s)
        # Change the Special2 name depending on the setting.
        # patcher.write_bytes(0xEFD4E, cvlod_string_to_bytearray(special2_name))
        # Change the Special1 and 2 menu descriptions to tell you how many you need to unlock a warp and fight Dracula
        # respectively.
        # special_text_bytes = cvlod_string_to_bytearray(f"{s1s_per_warp} per warp unlock.\n"
        #                                          f"{options.total_special1s.value} exist in total.\n"
        #                                          f"Z + R + START to warp.") + \
        #                     cvlod_string_to_bytearray(special2_text)
        # patcher.write_bytes(0xBFE53C, special_text_bytes)

        # On-the-fly TLB script modifier
        # patcher.write_int32s(0xBFC338, patches.double_component_checker)
        # patcher.write_int32s(0xBFC3D4, patches.downstairs_seal_checker)
        # patcher.write_int32s(0xBFE074, patches.mandragora_with_nitro_setter)
        # patcher.write_int32s(0xBFC700, patches.overlay_modifiers)

        # On-the-fly actor data modifier hook
        # patcher.write_int32(0xEAB04, 0x080FF21E)  # J 0x803FC878
        # patcher.write_int32s(0xBFC870, patches.map_data_modifiers)

        # Fix to make flags apply to freestanding invisible items properly
        # patcher.write_int32(0xA84F8, 0x90CC0039)  # LBU T4, 0x0039 (A2)

        # Fix locked doors to check the key counters instead of their vanilla key locations' bitflags
        # Pickup flag check modifications:
        # patcher.write_int32(0x10B2D8, 0x00000002)  # Left Tower Door
        # patcher.write_int32(0x10B2F0, 0x00000003)  # Storeroom Door
        # patcher.write_int32(0x10B2FC, 0x00000001)  # Archives Door
        # patcher.write_int32(0x10B314, 0x00000004)  # Maze Gate
        # patcher.write_int32(0x10B350, 0x00000005)  # Copper Door
        # patcher.write_int32(0x10B3A4, 0x00000006)  # Torture Chamber Door
        # patcher.write_int32(0x10B3B0, 0x00000007)  # ToE Gate
        # patcher.write_int32(0x10B3BC, 0x00000008)  # Science Door1
        # patcher.write_int32(0x10B3C8, 0x00000009)  # Science Door2
        # patcher.write_int32(0x10B3D4, 0x0000000A)  # Science Door3
        # patcher.write_int32(0x6F0094, 0x0000000B)  # CT Door 1
        # patcher.write_int32(0x6F00A4, 0x0000000C)  # CT Door 2
        # patcher.write_int32(0x6F00B4, 0x0000000D)  # CT Door 3
        # Item counter decrement check modifications:
        # patcher.write_int32(0xEDA84, 0x00000001)  # Archives Door
        # patcher.write_int32(0xEDA8C, 0x00000002)  # Left Tower Door
        # patcher.write_int32(0xEDA94, 0x00000003)  # Storeroom Door
        # patcher.write_int32(0xEDA9C, 0x00000004)  # Maze Gate
        # patcher.write_int32(0xEDAA4, 0x00000005)  # Copper Door
        # patcher.write_int32(0xEDAAC, 0x00000006)  # Torture Chamber Door
        # patcher.write_int32(0xEDAB4, 0x00000007)  # ToE Gate
        # patcher.write_int32(0xEDABC, 0x00000008)  # Science Door1
        # patcher.write_int32(0xEDAC4, 0x00000009)  # Science Door2
        # patcher.write_int32(0xEDACC, 0x0000000A)  # Science Door3
        # patcher.write_int32(0xEDAD4, 0x0000000B)  # CT Door 1
        # patcher.write_int32(0xEDADC, 0x0000000C)  # CT Door 2
        # patcher.write_int32(0xEDAE4, 0x0000000D)  # CT Door 3

        # Fix ToE gate's "unlocked" flag in the locked door flags table
        # patcher.write_int16(0x10B3B6, 0x0001)

        # patcher.write_int32(0x10AB2C, 0x8015FBD4)  # Maze Gates' check code pointer adjustments
        # patcher.write_int32(0x10AB40, 0x8015FBD4)
        # patcher.write_int32s(0x10AB50, [0x0D0C0000,
        #                            0x8015FBD4])
        # patcher.write_int32s(0x10AB64, [0x0D0C0000,
        #                            0x8015FBD4])
        # patcher.write_int32s(0xE2E14, patches.normal_door_hook)
        # patcher.write_int32s(0xBFC5D0, patches.normal_door_code)
        # patcher.write_int32s(0x6EF298, patches.ct_door_hook)
        # patcher.write_int32s(0xBFC608, patches.ct_door_code)
        # Fix key counter not decrementing if 2 or above
        # patcher.write_int32(0xAA0E0, 0x24020000)  # ADDIU	V0, R0, 0x0000

        # Make the Easy-only candle drops in Room of Clocks appear on any difficulty
        # patcher.write_byte(0x9B518F, 0x01)

        # Slightly move some once-invisible freestanding items to be more visible
        # if options.invisible_items.value == options.invisible_items.option_reveal_all:
        # patcher.write_byte(0x7C7F95, 0xEF)  # Forest dirge maiden statue
        # patcher.write_byte(0x7C7FA8, 0xAB)  # Forest werewolf statue
        # patcher.write_byte(0x8099C4, 0x8C)  # Villa courtyard tombstone
        # patcher.write_byte(0x83A626, 0xC2)  # Villa living room painting
        # #patcher.write_byte(0x83A62F, 0x64)  # Villa Mary's room table
        # patcher.write_byte(0xBFCB97, 0xF5)  # CC torture instrument rack
        # patcher.write_byte(0x8C44D5, 0x22)  # CC red carpet hallway knight
        # patcher.write_byte(0x8DF57C, 0xF1)  # CC cracked wall hallway flamethrower
        # patcher.write_byte(0x90FCD6, 0xA5)  # CC nitro hallway flamethrower
        # patcher.write_byte(0x90FB9F, 0x9A)  # CC invention room round machine
        # patcher.write_byte(0x90FBAF, 0x03)  # CC invention room giant famicart
        # patcher.write_byte(0x90FE54, 0x97)  # CC staircase knight (x)
        # patcher.write_byte(0x90FE58, 0xFB)  # CC staircase knight (z)

        # Make the torch directly behind Dracula's chamber that normally doesn't set a flag set bitflag 0x08 in 0x80389BFA
        # patcher.write_byte(0x10CE9F, 0x01)

        # Change the CC post-Behemoth boss depending on the option for Post-Behemoth Boss
        # if options.post_behemoth_boss.value == options.post_behemoth_boss.option_inverted:
        # patcher.write_byte(0xEEDAD, 0x02)
        # patcher.write_byte(0xEEDD9, 0x01)
        # elif options.post_behemoth_boss.value == options.post_behemoth_boss.option_always_rosa:
        # patcher.write_byte(0xEEDAD, 0x00)
        # patcher.write_byte(0xEEDD9, 0x03)
        # Put both on the same flag so changing character won't trigger a rematch with the same boss.
        # patcher.write_byte(0xEED8B, 0x40)
        # elif options.post_behemoth_boss.value == options.post_behemoth_boss.option_always_camilla:
        # patcher.write_byte(0xEEDAD, 0x03)
        # patcher.write_byte(0xEEDD9, 0x00)
        # patcher.write_byte(0xEED8B, 0x40)

        # Change the RoC boss depending on the option for Room of Clocks Boss
        # if options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_inverted:
        # patcher.write_byte(0x109FB3, 0x56)
        # patcher.write_byte(0x109FBF, 0x44)
        # patcher.write_byte(0xD9D44, 0x14)
        # patcher.write_byte(0xD9D4C, 0x14)
        # elif options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_always_death:
        # patcher.write_byte(0x109FBF, 0x44)
        # patcher.write_byte(0xD9D45, 0x00)
        # Put both on the same flag so changing character won't trigger a rematch with the same boss.
        # patcher.write_byte(0x109FB7, 0x90)
        # patcher.write_byte(0x109FC3, 0x90)
        # elif options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_always_actrise:
        # patcher.write_byte(0x109FB3, 0x56)
        # patcher.write_int32(0xD9D44, 0x00000000)
        # patcher.write_byte(0xD9D4D, 0x00)
        # patcher.write_byte(0x109FB7, 0x90)
        # patcher.write_byte(0x109FC3, 0x90)

        # Tunnel gondola skip
        # if options.skip_gondolas.value:
        # patcher.write_int32(0x6C5F58, 0x080FF7D0)  # J 0x803FDF40
        # patcher.write_int32s(0xBFDF40, patches.gondola_skipper)
        # New gondola transfer point candle coordinates
        # patcher.write_byte(0xBFC9A3, 0x04)
        # patcher.write_bytes(0x86D824, [0x27, 0x01, 0x10, 0xF7, 0xA0])

        # Waterway brick platforms skip
        # if options.skip_waterway_blocks.value:
        # patcher.write_int32(0x6C7E2C, 0x00000000)  # NOP

        # Fix for the door sliding sound playing infinitely if leaving the fan meeting room before the door closes entirely.
        # Hooking this in the ambience silencer code does nothing for some reason.
        # patcher.write_int32s(0xAE10C, [0x08004FAB,  # J   0x80013EAC
        #                           0x3404829B])  # ORI A0, R0, 0x829B
        # patcher.write_int32s(0xD9E8C, [0x08004FAB,  # J   0x80013EAC
        #                           0x3404829B])  # ORI A0, R0, 0x829B
        # Fan meeting room ambience fix
        # patcher.write_int32(0x109964, 0x803FE13C)

        # Increase shimmy speed
        # if options.increase_shimmy_speed.value:
        # patcher.write_byte(0xA4241, 0x5A)

        # Disable landing fall damage
        # if options.fall_guard.value:
        # patcher.write_byte(0x27B23, 0x00)

        # Permanent PowerUp stuff
        # if options.permanent_powerups.value:
        # Make receiving PowerUps increase the unused menu PowerUp counter instead of the one outside the save struct
        # patcher.write_int32(0xBF2EC, 0x806B619B)  # LB	T3, 0x619B (V1)
        # patcher.write_int32(0xBFC5BC, 0xA06C619B)  # SB	T4, 0x619B (V1)
        # Make Reinhardt's whip check the menu PowerUp counter
        # patcher.write_int32(0x69FA08, 0x80CC619B)  # LB	T4, 0x619B (A2)
        # patcher.write_int32(0x69FBFC, 0x80C3619B)  # LB	V1, 0x619B (A2)
        # patcher.write_int32(0x69FFE0, 0x818C9C53)  # LB	T4, 0x9C53 (T4)
        # Make Carrie's orb check the menu PowerUp counter
        # patcher.write_int32(0x6AC86C, 0x8105619B)  # LB	A1, 0x619B (T0)
        # patcher.write_int32(0x6AC950, 0x8105619B)  # LB	A1, 0x619B (T0)
        # patcher.write_int32(0x6AC99C, 0x810E619B)  # LB	T6, 0x619B (T0)
        # patcher.write_int32(0x5AFA0, 0x80639C53)  # LB	V1, 0x9C53 (V1)
        # patcher.write_int32(0x5B0A0, 0x81089C53)  # LB	T0, 0x9C53 (T0)
        # patcher.write_byte(0x391C7, 0x00)  # Prevent PowerUps from dropping from regular enemies
        # patcher.write_byte(0xEDEDF, 0x03)  # Make any vanishing PowerUps that do show up L jewels instead
        # Rename the PowerUp to "PermaUp"
        # patcher.write_bytes(0xEFDEE, cvlod_string_to_bytearray("PermaUp"))
        # Replace the PowerUp in the Forest Special1 Bridge 3HB rock with an L jewel if 3HBs aren't randomized
        #    if not options.multi_hit_breakables.value:
        # patcher.write_byte(0x10C7A1, 0x03)
        # Change the appearance of the Pot-Pourri to that of a larger PowerUp regardless of the above setting, so other
        # game PermaUps are distinguishable.
        # patcher.write_int32s(0xEE558, [0x06005F08, 0x3FB00000, 0xFFFFFF00])

        # Write the randomized (or disabled) music ID list and its associated code
        # if options.background_music.value:
        # patcher.write_int32(0x14588, 0x08060D60)  # J 0x80183580
        # patcher.write_int32(0x14590, 0x00000000)  # NOP
        # patcher.write_int32s(0x106770, patches.music_modifier)
        # patcher.write_int32(0x15780, 0x0C0FF36E)  # JAL 0x803FCDB8
        # patcher.write_int32s(0xBFCDB8, patches.music_comparer_modifier)

        # Once-per-frame gameplay checks
        # patcher.write_int32(0x6C848, 0x080FF40D)  # J 0x803FD034
        # patcher.write_int32(0xBFD058, 0x0801AEB5)  # J 0x8006BAD4

        # Everything related to dropping the previous sub-weapon
        # if options.drop_previous_sub_weapon.value:
        # patcher.write_int32(0xBFD034, 0x080FF3FF)  # J 0x803FCFFC
        # patcher.write_int32(0xBFC18C, 0x080FF3F2)  # J 0x803FCFC8
        # patcher.write_int32s(0xBFCFC4, patches.prev_subweapon_spawn_checker)
        # patcher.write_int32s(0xBFCFFC, patches.prev_subweapon_fall_checker)
        # patcher.write_int32s(0xBFD060, patches.prev_subweapon_dropper)

        # Ice Trap stuff
        # patcher.write_int32(0x697C60, 0x080FF06B)  # J 0x803FC18C
        # patcher.write_int32(0x6A5160, 0x080FF06B)  # J 0x803FC18C
        # patcher.write_int32s(0xBFC1AC, patches.ice_trap_initializer)
        # patcher.write_int32s(0xBFC1D8, patches.the_deep_freezer)
        # patcher.write_int32s(0xB2F354, [0x3739E4C0,  # ORI T9, T9, 0xE4C0
        #                            0x03200008,  # JR  T9
        #                            0x00000000])  # NOP
        # patcher.write_int32s(0xBFE4C0, patches.freeze_verifier)

        # Everything related to shopsanity
        # if options.shopsanity.value:
        # patcher.write_bytes(0x103868, cvlod_string_to_bytearray("Not obtained. "))
        # patcher.write_int32s(0xBFD8D0, patches.shopsanity_stuff)
        # patcher.write_int32(0xBD828, 0x0C0FF643)  # JAL	0x803FD90C
        # patcher.write_int32(0xBD5B8, 0x0C0FF651)  # JAL	0x803FD944
        # patcher.write_int32(0xB0610, 0x0C0FF665)  # JAL	0x803FD994
        # patcher.write_int32s(0xBD24C, [0x0C0FF677,  # J  	0x803FD9DC
        #                               0x00000000])  # NOP
        # patcher.write_int32(0xBD618, 0x0C0FF684)  # JAL	0x803FDA10

        # Panther Dash running
        # if options.panther_dash.value:
        # patcher.write_int32(0x69C8C4, 0x0C0FF77E)  # JAL   0x803FDDF8
        # patcher.write_int32(0x6AA228, 0x0C0FF77E)  # JAL   0x803FDDF8
        # patcher.write_int32s(0x69C86C, [0x0C0FF78E,  # JAL   0x803FDE38
        #                            0x3C01803E])  # LUI   AT, 0x803E
        # patcher.write_int32s(0x6AA1D0, [0x0C0FF78E,  # JAL   0x803FDE38
        #                            0x3C01803E])  # LUI   AT, 0x803E
        # patcher.write_int32(0x69D37C, 0x0C0FF79E)  # JAL   0x803FDE78
        # patcher.write_int32(0x6AACE0, 0x0C0FF79E)  # JAL   0x803FDE78
        # patcher.write_int32s(0xBFDDF8, patches.panther_dash)
        # Jump prevention
        # if options.panther_dash.value == options.panther_dash.option_jumpless:
        # patcher.write_int32(0xBFDE2C, 0x080FF7BB)  # J     0x803FDEEC
        # patcher.write_int32(0xBFD044, 0x080FF7B1)  # J     0x803FDEC4
        # patcher.write_int32s(0x69B630, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8CCD0000])  # LW    T5, 0x0000 (A2)
        # patcher.write_int32s(0x6A8EC0, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8CCC0000])  # LW    T4, 0x0000 (A2)
        # Fun fact: KCEK put separate code to handle coyote time jumping
        # patcher.write_int32s(0x69910C, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8C4E0000])  # LW    T6, 0x0000 (V0)
        # patcher.write_int32s(0x6A6718, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8C4E0000])  # LW    T6, 0x0000 (V0)
        # patcher.write_int32s(0xBFDEC4, patches.panther_jump_preventer)

        # Write all the actor list spawn condition edits that we apply always (things like difficulty items, etc.).
        for offset in patches.always_actor_edits:
            patcher.write_byte(offset, patches.always_actor_edits[offset])
        for start_addr in patches.era_specific_actors:
            era_statuses = patches.era_specific_actors[start_addr]
            for actor_number in era_statuses:
                curr_addr = start_addr + (actor_number * 0x20)
                byte_to_alter = patcher.read_byte(curr_addr)
                if era_statuses[actor_number]:
                    byte_to_alter |= 0x78
                else:
                    byte_to_alter |= 0xF8
                patcher.write_byte(curr_addr, byte_to_alter)

        # Make the lever checks for Cornell always pass
        patcher.write_int32(0xE6C18, 0x240A0002)  # ADDIU T2, R0, 0x0002
        patcher.write_int32(0xE6F64, 0x240E0002)  # ADDIU T6, R0, 0x0002
        patcher.write_int32(0xE70F4, 0x240D0002)  # ADDIU T5, R0, 0x0002
        patcher.write_int32(0xE7364, 0x24080002)  # ADDIU T0, R0, 0x0002
        patcher.write_int32(0x109C10, 0x240E0002)  # ADDIU T6, R0, 0x0002

        # Make the fountain pillar checks for Cornell always pass
        patcher.write_int32(0xD77E0, 0x24030002)  # ADDIU V1, R0, 0x0002
        patcher.write_int32(0xD7A60, 0x24030002)  # ADDIU V1, R0, 0x0002

        # Make only some rose garden checks for Cornell always pass
        patcher.write_byte(0x78619B, 0x24)
        patcher.write_int16(0x7861A0, 0x5423)
        patcher.write_int32(0x786324, 0x240E0002)  # ADDIU T6, R0, 0x0002
        # Make the thirsty J. A. Oldrey cutscene check for Cornell always pass
        patcher.write_byte(0x11831D, 0x00)
        # Make the Villa coffin lid Henry checks never pass
        patcher.write_byte(0x7D45FB, 0x04)
        patcher.write_byte(0x7D4BFB, 0x04)
        # Make the Villa coffin loading zone Henry check always pass
        patcher.write_int32(0xD3A78, 0x000C0821)  # ADDU  AT, R0, T4
        # Make the Villa coffin lid Cornell attack collision check always pass
        patcher.write_int32(0x7D4D9C, 0x00000000)  # NOP
        # Make the Villa coffin lid Cornell cutscene check never pass
        patcher.write_byte(0x7D518F, 0x04)
        # Make the hardcoded Cornell check in the Villa crypt Reinhardt/Carrie first vampire intro cutscene not pass.
        # IDK what KCEK was planning here, since Cornell normally doesn't get this cutscene, but if it passes the game
        # completely ceases functioning.
        patcher.write_int16(0x230, 0x1000, NIFiles.OVERLAY_CS_1ST_REIN_CARRIE_CRYPT_VAMPIRE)

        # Change Oldrey's Diary into an item location.
        patcher.write_int16(0x792A24, 0x0027)
        patcher.write_int16(0x792A28, 0x0084)
        patcher.write_byte(0x792A2D, 0x17)
        # Change the Maze Henry Mode kid into a location.
        patcher.write_int32s(0x798CF8, [0x01D90000, 0x00000000, 0x000C0000])
        patcher.write_byte(0x796D4F, 0x87)

        # Move the following Locations that have flags shared with other Locations to their own flags.
        patcher.write_int16(0x792A48, 0x0085)  # Archives Garden Key
        patcher.write_int16(0xAAA, 0x0086, NIFiles.OVERLAY_MARY)  # Mary's Copper Key
        patcher.write_int16(0xAE2, 0x0086, NIFiles.OVERLAY_MARY)
        patcher.write_int16(0xB12, 0x0086, NIFiles.OVERLAY_MARY)

        # Write "Z + R + START" over the Special1 description.
        patcher.write_bytes(0x3B7C, cvlod_string_to_bytearray("Z + R + START\t")[0], NIFiles.OVERLAY_PAUSE_MENU)

        # if loc.item.player != player:
        #        inject_address = 0xBB7164 + (256 * (loc.address & 0xFFF))
        #        wrapped_name, num_lines = cvlod_text_wrap(item_name + "\nfor " + multiworld.get_player_name(
        #            loc.item.player), 96)
        # patcher.write_bytes(inject_address, get_item_text_color(loc) + cvlod_string_to_bytearray(wrapped_name))
        # patcher.write_byte(inject_address + 255, num_lines)

        # Everything relating to loading the other game items text
        # patcher.write_int32(0xA8D8C, 0x080FF88F)  # J   0x803FE23C
        # patcher.write_int32(0xBEA98, 0x0C0FF8B4)  # JAL 0x803FE2D0
        # patcher.write_int32(0xBEAB0, 0x0C0FF8BD)  # JAL 0x803FE2F8
        # patcher.write_int32(0xBEACC, 0x0C0FF8C5)  # JAL 0x803FE314
        # patcher.write_int32s(0xBFE23C, patches.multiworld_item_name_loader)
        # patcher.write_bytes(0x10F188, [0x00 for _ in range(264)])
        # patcher.write_bytes(0x10F298, [0x00 for _ in range(264)])

        return patcher.get_output_rom()


class CVLoDProcedurePatch(APProcedurePatch):
    hash = [CVLOD_US_HASH]
    patch_file_ending: str = ".apcvlod"
    result_file_ending: str = ".z64"

    game = "Castlevania - Legacy of Darkness"

    procedure = [
        ("patch_rom", ["slot_patch_info.json"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def write_patch(world: "CVLoDWorld", patch: CVLoDProcedurePatch, offset_data: Dict[int, bytes],
                shop_name_list: List[str],
                shop_desc_list: List[List[Union[int, str, None]]], shop_colors_list: List[bytearray],
                active_locations: Iterable[Location]) -> None:
    #active_warp_list = world.active_warp_list
    #s1s_per_warp = world.s1s_per_warp


    # Write the seed's warp destination IDs.
    # for i in range(len(active_warp_list)):
    #    if i == 0:
    #        patch.write_token(APTokenTypes.WRITE,
    #                          warp_map_offsets[i], get_stage_info(active_warp_list[i], "start map id"))
    #        patch.write_token(APTokenTypes.WRITE,
    #                          warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "start spawn id"))
    #    else:
    #        patch.write_token(APTokenTypes.WRITE,
    #                          warp_map_offsets[i], get_stage_info(active_warp_list[i], "mid map id"))
    #        patch.write_token(APTokenTypes.WRITE,
    #                          warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "mid spawn id"))

    # Write the new File Select stage numbers.
    # for stage in world.active_stage_exits:
    #    for offset in get_stage_info(stage, "save number offsets"):
    #        patch.write_token(APTokenTypes.WRITE, offset, bytes([world.active_stage_exits[stage]["position"]]))

    # Write all the shop text.
    # if world.options.shopsanity:
    #    patch.write_token(APTokenTypes.WRITE, 0x103868, bytes(cv64_string_to_bytearray("Not obtained. ")))

    #    shopsanity_name_text = bytearray(0)
    #    shopsanity_desc_text = bytearray(0)
    #    for i in range(len(shop_name_list)):
    #        shopsanity_name_text += bytearray([0xA0, i]) + shop_colors_list[i] + \
    #                                cv64_string_to_bytearray(cv64_text_truncate(shop_name_list[i], 74))

    #        shopsanity_desc_text += bytearray([0xA0, i])
    #        if shop_desc_list[i][1] is not None:
    #            shopsanity_desc_text += cv64_string_to_bytearray("For " + shop_desc_list[i][1] + ".\n",
    #                                                             append_end=False)
    #        shopsanity_desc_text += cv64_string_to_bytearray(renon_item_dialogue[shop_desc_list[i][0]])
    #    patch.write_token(APTokenTypes.WRITE, 0x1AD00, bytes(shopsanity_name_text))
    #    patch.write_token(APTokenTypes.WRITE, 0x1A800, bytes(shopsanity_desc_text))

    # Make Mary say what her item is so players can then decide if Henry is worth saving or not.
    mary_loc = world.get_location(loc_names.villala_mary)
    mary_text = "Save Henry, and I will "
    if mary_loc.item.player == world.player:
        mary_text += f"give you this {mary_loc.item.name}."
    else:
        mary_text += f"send this {mary_loc.item.name} to {world.multiworld.get_player_name(mary_loc.item.player)}."
    mary_text += "\nGood luck out there!"

    # mary_text = cvlod_text_wrap(mary_text, 254)

    #patch.write_token(APTokenTypes.WRITE, 0x78EAE0,
    #                  bytes(cvlod_string_to_bytearray(mary_text[0] + (" " * (866 - len(mary_text[0]))))[0]))

    # Write the secondary name the client will use to distinguish a vanilla ROM from an AP one.
    #patch.write_token(APTokenTypes.WRITE, 0xFFBFD0, "ARCHIPELAG01".encode("utf-8"))
    # Write the slot authentication
    #patch.write_token(APTokenTypes.WRITE, 0xFFBFE0, bytes(world.auth))


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path(file_name)
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if CVLOD_US_HASH != basemd5.hexdigest():
            raise Exception("Supplied Base Rom does not match known MD5 for Castlevania: Legacy of Darkness USA. "
                            "Get the correct game and version, then dump it.")
        setattr(get_base_rom_bytes, "base_rom_bytes", base_rom_bytes)
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    if not file_name:
        file_name = get_settings()["cvlod_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name
