import logging
import zlib
import json
import base64
import struct
import Utils

from BaseClasses import Location
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
from abc import ABC
from typing import List, Dict, Union, Iterable, TYPE_CHECKING

import hashlib
import os
# import pkgutil

from .data import patches, loc_names
from .data.enums import Scenes, NIFiles, Objects, ObjectExecutionFlags, ActorSpawnFlags, Items, Pickups, PickupFlags, \
    DoorFlags
from .patcher import CVLoDRomPatcher, CVLoDSceneTextEntry, CVLoDNormalActorEntry, CVLoDDoorEntry, CVLoDPillarActorEntry, CVLoDLoadingZoneEntry, CVLoDEnemyPillarEntry, CVLoD1HitBreakableEntry, CVLoD3HitBreakableEntry, CVLoDSpawnEntranceEntry
from .stages import CVLOD_STAGE_INFO
from .cvlod_text import cvlod_string_to_bytearray, cvlod_text_wrap, cvlod_bytes_to_string, CVLOD_STRING_END_CHARACTER, \
    CVLOD_TEXT_POOL_END_CHARACTER
# from .aesthetics import renon_item_dialogue
# from .locations import CVLOD_LOCATIONS_INFO
# from .options import StageLayout, VincentFightCondition, RenonFightCondition, PostBehemothBoss, RoomOfClocksBoss, \
#     CastleKeepEndingSequence, DeathLink, DraculasCondition, InvisibleItems, Countdown, PantherDash
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

WARP_SCENE_OFFSETS = [0xADF67, 0xADF77, 0xADF87, 0xADF97, 0xADFA7, 0xADFBB, 0xADFCB, 0xADFDF]


class CVLoDPatchExtensions(APPatchExtension):
    game = "Castlevania - Legacy of Darkness"

    @staticmethod
    def patch_rom(caller: APProcedurePatch, input_rom: bytes, slot_patch_file) -> bytes:
        patcher = CVLoDRomPatcher(bytearray(input_rom))
        slot_patch_info = json.loads(caller.get_file(slot_patch_file).decode("utf-8"))


        # # # # # # # # #
        # GENERAL EDITS #
        # # # # # # # # #

        # NOP out the CRC BNEs
        patcher.write_int32(0x66C, 0x00000000)
        patcher.write_int32(0x678, 0x00000000)

        # Add keys in an AP logo formation to the title screen.
        patcher.scenes[Scenes.INTRO_NARRATION].actor_lists["distance"] += [
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
        # Make the Henry warp jewels work for everyone at the expense of the light effect surrounding them.
        # The code that creates and renders it is exclusively inside Henry's overlay, so it must go for it to function
        # for the rest of the characters, sadly.
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
        #patcher.write_byte(0x15DB, 0x11, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        #patcher.write_byte(0x15D3, 0x00, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        # Change the instruction that stores the Foggy Lake intro cutscene value to store a 0 (from R0) instead.
        patcher.write_int32(0x1614, 0xAC402BCC, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON) # SW  R0, 0x2BCC (V0)
        # Instead of always 0 as the spawn entrance, store the aftermentined cutscene value as it.
        patcher.write_int32(0x1618, 0xA04B2BBB, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON) # SB  T3, 0x2BBB (V0)
        # Make the starting level the same for Henry as everyone else.
        patcher.write_byte(0x15D5, 0x00, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)

        # Active cutscene checker routines for certain actors.
        patcher.write_int32s(0xFFCDA0, patches.cutscene_active_checkers)


        # # # # # # # # # # #
        # FOGGY LAKE EDITS  #
        # # # # # # # # # # #
        # Lock the door in Foggy Lake below decks leading out to above decks with the Deck Key.
        # It's the same door in-universe as the above decks one but on a different map.
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["door_flags"] = \
            DoorFlags.UNLOCK_AND_SET_FLAG | DoorFlags.DISREGARD_IF_FLAG_SET | DoorFlags.ITEM_COST_IF_FLAG_UNSET
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["flag_id"] = 0x28E  # Deck Door unlocked flag
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["item_id"] = Items.DECK_KEY
        patcher.scenes[Scenes.FOGGY_LAKE_BELOW_DECKS].doors[0]["cant_open_text_id"] = 0x01
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
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][76]["spawn_flags"] = \
            ActorSpawnFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][76]["flag_id"] = 0
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][76]["extra_condition_ptr"] = 0x803FCDBC
        # Prevent the Sea Monster from respawning if you leave the pier map and return.
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][74]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][74]["flag_id"] = 0x15D
        # Un-set the "debris path sunk" flag after the Sea Monster is killed and when the door flag is set.
        patcher.write_int32(0x7268, 0x0FC04164, NIFiles.OVERLAY_SEA_MONSTER)  # JAL 0x0F010590
        patcher.write_int32s(0x10590, patches.sea_monster_sunk_path_flag_unsetter, NIFiles.OVERLAY_SEA_MONSTER)
        # Disable the two pier statue items checking each other's flags being not set as an additional spawn condition.
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][77]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][77]["flag_id"] = 0
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][80]["spawn_flags"] ^= \
            ActorSpawnFlags.SPAWN_IF_FLAG_CLEARED
        patcher.scenes[Scenes.FOGGY_LAKE_PIER].actor_lists["distance"][80]["flag_id"] = 0

        return patcher.get_output_rom()


        # # # # # # # # # # # # # #
        # FOREST OF SILENCE EDITS #
        # # # # # # # # # # # # # #
        # Make coffins 01-04 in the Forest Charnel Houses never spawn items (as in, the RNG for them will never pass).
        patcher.write_int32(0x76F440, 0x10000005)  # B [forward 0x05]
        # Make coffin 00 always try spawning the same consistent three items regardless of whether we previously broke
        # it or not and regardless of difficulty.
        patcher.write_int32(0x76F478, 0x00000000)  # NOP-ed Hard difficulty check
        patcher.write_byte(0x76FAC3, 0x00)  # No event flag set for coffin 00.
        patcher.write_int32(0x76F4B4, 0x00000000)  # NOP-ed Not Easy difficulty check
        # Use the current loop iteration to tell what entry in the table to spawn.
        patcher.write_int32(0x76F4D4, 0x264E0000)  # ADDIU T6, S2, 0x0000
        # Assign the event flags and remove the "vanish timer" flag on each of the three coffin item entries we'll use.
        patcher.write_int16(0x774966, 0x0011)
        patcher.write_byte(0x774969, 0x00)
        patcher.write_int16(0x774972, 0x0012)
        patcher.write_byte(0x774975, 0x00)
        patcher.write_int16(0x7749C6, 0x0013)
        patcher.write_byte(0x7749C9, 0x00)
        # Turn the Forest Henry child actor into a torch check with all necessary parameters assigned.
        patcher.write_int16(0x7758DE, 0x0022)  # Dropped item flag ID
        patcher.write_byte(0x7782D5, 0x00)     # Flag check unassignment
        patcher.write_int16(0x7782E4, 0x01D9)  # Candle actor ID
        patcher.write_int16(0x7782E6, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x7782E8, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x7782EC, 0x000C)  # Candle ID
        # Set Flag 0x23 on the item King Skeleton 2 leaves behind, and prevent it from being the possible Henry drop.
        patcher.write_int32(0x43F8, 0x10000006, NIFiles.OVERLAY_KING_SKELETON)
        patcher.write_int32s(0x444C, [0x3C088040,  # LUI   T0, 0x8040
                                       0x2508CBB0,  # ADDIU T0, T0, 0xCBB0
                                       0x0100F809,  # JALR  RA, T0
                                       0x00000000], NIFiles.OVERLAY_KING_SKELETON)
        patcher.write_int32s(0xFFCBB0, patches.king_skeleton_chicken_flag_setter)
        # Add the backup King Skeleton jaws item that will spawn only if the player orphans it the first time.
        patcher.write_byte(0x778415, 0x20)
        patcher.write_int32s(0x778418, [0x3D000000, 0x00000000, 0xC4B2C000])
        patcher.write_int16(0x778426, 0x002C)
        patcher.write_int16(0x778428, 0x0023)
        patcher.write_int16(0x77842A, 0x0000)
        # Make the drawbridge cutscene's end behavior its Henry end behavior for everyone.
        # The "drawbridge lowered" flag should be set so that Forest's regular end zone is easily accessible, and no
        # separate cutscene should play in the next map.
        patcher.write_int32(0x1294, 0x1000000C, NIFiles.OVERLAY_CS_DRAWBRIDGE_LOWERS)

        # Make the final Cerberus in Villa Front Yard
        # un-set the Villa entrance portcullis closed flag for all characters (not just Henry).
        patcher.write_int32(0x35A4, 0x00000000, NIFiles.OVERLAY_CERBERUS)

        # Give the Gardener his Cornell behavior for everyone.
        patcher.write_int32(0x490, 0x24020002, NIFiles.OVERLAY_GARDENER)  # ADDIU V0, R0, 0x0002
        patcher.write_int32(0xD20, 0x00000000, NIFiles.OVERLAY_GARDENER)
        patcher.write_int32(0x13CC, 0x00000000, NIFiles.OVERLAY_GARDENER)

        # Give Child Henry his Cornell behavior for everyone.
        patcher.write_int32(0x1B8, 0x24020002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU V0, R0, 0x0002
        patcher.write_byte(0x613, 0x04, NIFiles.OVERLAY_CHILD_HENRY)
        patcher.write_int32(0x844, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002
        patcher.write_int32(0x8B8, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002

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

        # Make the Tunnel gondolas check for the Spider Women cutscene like they do in CV64.
        patcher.write_int32(0x79B8CC, 0x0C0FF2F8)  # JAL	0x803FCBE0
        patcher.write_int32s(0xFFCBE0, patches.gondola_spider_cutscene_checker)
        # Turn the Tunnel Henry child actor into a torch check with all necessary parameters assigned.
        patcher.write_int16(0x79EF8E, 0x0024)  # Dropped item flag ID
        patcher.write_byte(0x7A1469, 0x00)     # Flag check unassignment
        patcher.write_int16(0x7A1478, 0x01D9)  # Candle actor ID
        patcher.write_int16(0x7A147A, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x7A147C, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x7A147E, 0x0000)  # Rotation unassignment
        patcher.write_int16(0x7A1480, 0x000F)  # Candle ID
        # Set the Tunnel end zone destination ID to the ID for the decoupled Spider Queen arena.
        patcher.write_byte(0x79FD8F, 0x40)

        # Turn the Waterway Henry child actor into a torch check with all necessary parameters assigned.
        patcher.write_int16(0x7A409E, 0x0025)  # Dropped item flag ID
        patcher.write_byte(0x7A5759, 0x00)     # Flag check unassignment
        patcher.write_int16(0x7A5768, 0x01D9)  # Candle actor ID
        patcher.write_int16(0x7A576A, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x7A576C, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x7A576E, 0x0000)  # Rotation unassignment
        patcher.write_int16(0x7A5770, 0x0000)  # Candle ID
        patcher.write_int32(0x7A5774, 0x00000000)  # Removed special spawn check address
        # Set the Waterway end zone destination ID to the ID for the decoupled Medusa arena.
        patcher.write_byte(0x7A4A0B, 0x80)

        # Make different Tunnel/Waterway boss arena end loading zones spawn depending on whether the 0x2A1 or 0x2A2
        # flags are set.
        patcher.write_byte(0x7C87B5, 0x20)  # Flag check assignment
        patcher.write_int16(0x7C87C6, 0x02A1)  # Tunnel flag ID
        patcher.write_byte(0x7C87D5, 0x20)  # Flag check assignment
        patcher.write_int16(0x7C87E6, 0x02A2)  # Underground Waterway flag ID

        # Turn the Outer Wall Henry child actor into a torch check with all necessary parameters assigned.
        patcher.write_int16(0x833A9E, 0x0026)  # Dropped item flag ID
        patcher.write_byte(0x834B15, 0x00)     # Flag check unassignment
        patcher.write_int16(0x834B24, 0x01D9)  # Candle actor ID
        patcher.write_int16(0x834B26, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x834B28, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x834B2A, 0x0000)  # Rotation unassignment
        patcher.write_int16(0x834B2C, 0x0002)  # Candle ID
        patcher.write_int32(0x834B30, 0x00000000)  # Removed special spawn check address
        # Make the Outer Wall end loading zone send you to the start of Art Tower instead of the fan map, as well as
        # heal the player.
        patcher.write_int16(0x834448, 0x0001)
        patcher.write_int16(0x83444A, 0x2500)

        # Make the Art Tower start loading zone send you to the end of The Outer Wall instead of the fan map.
        patcher.write_int16(0x818DF2, 0x2A0B)
        # Make the loading zone leading from Art Tower museum -> conservatory slightly smaller.
        patcher.write_int16(0x818E10, 0xFE18)
        # Change the player spawn coordinates coming from Art Tower conservatory -> museum to start them behind the
        # Key 2 door, so they will need Key 2 to come this way.
        patcher.write_int16(0x1103E4, 0xFE22)  # Player Z position
        patcher.write_int16(0x1103E8, 0x000D)  # Camera X position
        patcher.write_int16(0x1103EC, 0xFE10)  # Camera Z position
        patcher.write_int16(0x1103F2, 0xFE22)  # Focus point Z position
        # Prevent the Hell Knights in the middle Art Tower hallway from locking the doors until defeated.
        patcher.write_byte(0x81A5B0, 0x00)
        patcher.write_byte(0x81A5D0, 0x02)
        patcher.write_byte(0x81A5F0, 0x02)
        # Put the left item on top of the Art Tower conservatory doorway on its correct flag.
        patcher.write_int16(0x81DDB4, 0x02AF)
        # Prevent the middle item on top of the Art Tower conservatory doorway from self-modifying itself.
        patcher.write_byte(0x81DD81, 0x80)
        patcher.write_int32(0x81DD9C, 0x00000000)

        # Remove the Tower of Science item flag checks from the invisible Tower of Ruins statue items.
        # Yeah, your guess as to what the devs may have been thinking with this is as good as mine.
        patcher.write_byte(0x808C65, 0x00)
        patcher.write_int16(0x808C76, 0x0000)
        patcher.write_byte(0x809185, 0x00)
        patcher.write_int16(0x809196, 0x0000)
        # Clone the third Tower of Ruins gate actor and turn it around the other way. These actors normally only have
        # collision on one side, so if you were coming the other way you could very easily sequence break.
        patcher.write_byte(0x809925, 0x00)     # Flag check unassignment
        patcher.write_int32s(0x809928, [0x43DB0000, 0x42960000, 0x43100000])  # XYZ coordinates
        patcher.write_int16(0x809934, 0x01B9)  # Special door actor ID
        patcher.write_int16(0x809936, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x809938, 0x0000)  # Flag check unassignment
        patcher.write_int16(0x80993A, 0x8000)  # Rotation
        patcher.write_int16(0x80993C, 0x0002)  # Door ID
        # Set the Tower of Ruins end loading zone destination to the Castle Center top elevator White Jewel.
        patcher.write_int16(0x8128EE, 0x0F03)

        # Basement
        patcher.write_byte(0x7AA2A5, 0x0A)
        patcher.write_int32(0x7AA2C0, 0x803FCDBC)
        patcher.write_byte(0x7AA2C5, 0x0A)
        patcher.write_int32(0x7AA2E0, 0x803FCDBC)
        patcher.write_byte(0x7AA2E5, 0x0A)
        patcher.write_int32(0x7AA300, 0x803FCDBC)
        patcher.write_byte(0x7AA305, 0x0A)
        patcher.write_int32(0x7AA320, 0x803FCDBC)
        patcher.write_byte(0x7AA325, 0x0A)
        patcher.write_int32(0x7AA340, 0x803FCDBC)
        patcher.write_byte(0x7AA345, 0x0A)
        patcher.write_int32(0x7AA360, 0x803FCDBC)
        patcher.write_byte(0x7AA365, 0x08)
        patcher.write_int32(0x7AA380, 0x803FCDBC)
        patcher.write_byte(0x7AA405, 0x08)
        patcher.write_int32(0x7AA420, 0x803FCDA0)
        patcher.write_byte(0x7AA425, 0x08)
        patcher.write_int32(0x7AA440, 0x803FCDA0)
        patcher.write_byte(0x7AA445, 0x08)
        patcher.write_int32(0x7AA460, 0x803FCDA0)
        patcher.write_byte(0x7AA465, 0x08)
        patcher.write_int32(0x7AA480, 0x803FCDA0)
        patcher.write_byte(0x7AA485, 0x08)
        patcher.write_int32(0x7AA4A0, 0x803FCDA0)
        patcher.write_byte(0x7AA4A5, 0x08)
        patcher.write_int32(0x7AA4C0, 0x803FCDA0)
        # Factory Floor
        patcher.write_byte(0x7B1369, 0x08)
        patcher.write_int32(0x7B1384, 0x803FCDA0)
        patcher.write_byte(0x7B1389, 0x08)
        patcher.write_int32(0x7B13A4, 0x803FCDA0)
        patcher.write_byte(0x7B13A9, 0x08)
        patcher.write_int32(0x7B13C4, 0x803FCDA0)
        patcher.write_byte(0x7B13C9, 0x08)
        patcher.write_int32(0x7B13E4, 0x803FCDA0)
        patcher.write_byte(0x7B13E9, 0x08)
        patcher.write_int32(0x7B1404, 0x803FCDA0)
        patcher.write_byte(0x7B1429, 0x08)
        patcher.write_int32(0x7B1444, 0x803FCDBC)
        patcher.write_byte(0x7B1449, 0x08)
        patcher.write_int32(0x7B1464, 0x803FCDBC)
        patcher.write_byte(0x7B1469, 0x08)
        patcher.write_int32(0x7B1484, 0x803FCDBC)
        # Lizard Lab
        patcher.write_byte(0x7B4309, 0x88)
        patcher.write_int32(0x7B4324, 0x803FCDBC)
        patcher.write_byte(0x7B4349, 0x08)
        patcher.write_int32(0x7B4364, 0x803FCDBC)
        patcher.write_byte(0x7B4369, 0x08)
        patcher.write_int32(0x7B4384, 0x803FCDBC)
        patcher.write_byte(0x7B4389, 0x08)
        patcher.write_int32(0x7B43A4, 0x803FCDBC)
        # Change some shelf decoration Nitros and Mandragoras into actual items.
        patcher.write_int32(0x7A9BE8, 0xC0800000)  # X position
        patcher.write_int32(0x7A9C08, 0xC0800000)  # X position
        patcher.write_int16(0x7A9BF4, 0x0027)  # Interactable actor ID
        patcher.write_int16(0x7A9C14, 0x0027)  # Interactable actor ID
        patcher.write_int16(0x7A9BF8, 0x0346)  # Flag ID
        patcher.write_int16(0x7A9C18, 0x0345)  # Flag ID
        patcher.write_int32(0x7B8940, 0xC3A00000)  # X position
        patcher.write_int32(0x7B89A0, 0xC3990000)  # X position
        patcher.write_int16(0x7B894C, 0x0027)  # Interactable actor ID
        patcher.write_int16(0x7B89AC, 0x0027)  # Interactable actor ID
        patcher.write_int16(0x7B8950, 0x0347)  # Flag ID
        patcher.write_int16(0x7B89B0, 0x0348)  # Flag ID
        patcher.write_int16(0x7B8952, 0x0000)  # Param unassignment
        patcher.write_int16(0x7B89B2, 0x0000)  # Param unassignment
        # Restore the Castle Center library bookshelf item by moving its actor entry into the main library actor list.
        patcher.write_bytes(0x7B6620, patcher.read_bytes(0x7B6720, 0x20))
        patcher.write_byte(0x7B6621, 0x80)
        # Make the Castle Center post-Behemoth boss cutscenes trigger-able by anyone.
        patcher.write_byte(0x118139, 0x00)
        patcher.write_byte(0x118165, 0x00)
        # Fix both Castle Center elevator bridges for both characters unless enabling only one character's stages.
        # At which point one bridge will be always broken and one always repaired instead.
        patcher.write_int32(0x7B938C, 0x51200004)  # BEQZL  T1, [forward 0x04]
        patcher.write_byte(0x7B9B8D, 0x01)  # Reinhardt bridge
        patcher.write_byte(0x7B9BAD, 0x01)  # Carrie bridge
        # if options.character_stages.value == options.character_stages.option_reinhardt_only:
        # patcher.write_int32(0x6CEAA0, 0x240B0000)  # ADDIU T3, R0, 0x0000
        # elif options.character_stages.value == options.character_stages.option_carrie_only == 3:
        # patcher.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
        # else:
        # patcher.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
        # patcher.write_int32(0x6CEAA4, 0x240D0001)  # ADDIU T5, R0, 0x0001

        # Prevent taking Nitro or Mandragora through their shelf text.
        patcher.write_int32(0x1F0, 0x240C0000, NIFiles.OVERLAY_TAKE_NITRO_TEXTBOX)  # ADDIU T4, R0, 0x0000
        patcher.write_bytes(0x7B7406, cvlod_string_to_bytearray("Huh!? Someone super glued\n"
                                                                 "all these Magical Nitro bottles\n"
                                                                 "to the shelf!»\n"
                                                                 "Better find some elsewhere,\n"
                                                                 "lest you suffer the fate of an\n"
                                                                 "insane lunatic coyote in trying\n"
                                                                 "to force-remove one...»\t\t")[0])
        patcher.write_int32(0x22C, 0x240F0000, NIFiles.OVERLAY_TAKE_MANDRAGORA_TEXTBOX)  # ADDIU T7, R0, 0x0000
        patcher.write_bytes(0x7A8FFC, cvlod_string_to_bytearray("\tThese Mandragora bottles\n"
                                                                 "are empty, and a note was\n"
                                                                 "left behind:»\n"
                                                                 "\"Come 2035, and the Boss\n"
                                                                 "will be in for a very LOUD\n"
                                                                 "surprise! Hehehehe!\"»\n"
                                                                 "Whoever battles Dracula then\n"
                                                                 "may have an easy time...»\t")[0])

        # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes.
        patcher.write_int32(0x128, 0x24020001, NIFiles.OVERLAY_VAMPIRE_SPAWNER)  # ADDIU V0, R0, 0x0001

        # Prevent throwing Nitro in the Hazardous Materials Disposals.
        patcher.write_int32(0x1E4, 0x24020001, NIFiles.OVERLAY_NITRO_DISPOSAL_TEXTBOX)  # ADDIU V0, R0, 0x0001
        patcher.write_bytes(0x7ADCCE, cvlod_string_to_bytearray("\t\"Hazardous materials disposal.\"»\n"
                                                                 "\"DO NOT OPERATE:\n"
                                                                 "Traces of gelatinous bloody "
                                                                 "tears need cleaning.\"»    \t")[0])
        patcher.write_bytes(0x7B0770, cvlod_string_to_bytearray("\t\"Hazardous materials disposal.\"»\n"
                                                                 "\"DO NOT OPERATE:\n"
                                                                 "Jammed shut by repeated use "
                                                                 "from COWARDS.\"»     \t")[0])
        patcher.write_bytes(0x7B2B2A, cvlod_string_to_bytearray("\t\"Hazardous materials disposal.\"»\n"
                                                                 "\"DO NOT OPERATE:\n"
                                                                 "Busted by Henrich attempting "
                                                                 "to escape through it.\"»  \t")[0])

        # Allow placing both bomb components at a cracked wall at once while having multiple copies of each, prevent
        # placing them at the downstairs crack altogether until the seal is removed, and enable placing both in one
        # interaction.
        patcher.write_int32(0xEE8, 0x803FCD50, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x34A, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x34E, 0xCCC0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x38A, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x38E, 0xCCC0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x3F6, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x3FA, 0xCD00, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x436, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x43A, 0xCD00, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int32s(0xFFCCC0, patches.double_component_checker)
        patcher.write_int32s(0xFFCD50, patches.basement_seal_checker)
        patcher.write_int16(0x646, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x64A, 0xCDE0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x65E, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int16(0x662, 0xCDE0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        patcher.write_int32s(0xFFCDE0, patches.mandragora_with_nitro_setter)

        # Custom message for if you try checking the downstairs Castle Center crack before removing the seal.
        patcher.write_bytes(0x7A924C, cvlod_string_to_bytearray("The Furious Nerd Curse\n"
                                                                 "prevents you from setting\n"
                                                                 "anything until the seal\n"
                                                                 "is removed!»\t")[0])

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

        # Make one of the lone turret room doors in Tower of Science display an unused message if you try to open it
        # before blowing up said turret.
        patcher.write_byte(0x803E28, 0x00)
        patcher.write_byte(0x803E54, 0x00)
        # Touch up the message to clarify the room number (to try and minimize confusion if the player approaches the
        # door from the other side).
        patcher.write_bytes(0x803C12, cvlod_string_to_bytearray("Room 1\ncannon ")[0] +
                             patcher.read_bytes(0x803C20, 0xE6))
        # Change the Security Crystal's play sound function call into a set song to play call when it tries to play its
        # music theme, so it will actually play correctly when coming in from a different stage with a different song.
        patcher.write_int16(0x800526, 0x7274)
        # Make it so checking the Control Room doors will play the map's song, in the event the player tries going
        # backwards after killing the Security Crystal and having there be no music.
        patcher.write_int16(0x803F74, 0x5300)
        patcher.write_int32(0x803F78, 0x803FCE40)
        patcher.write_int16(0x803FA0, 0x5300)
        patcher.write_int32(0x803FA4, 0x803FCE40)
        patcher.write_int32s(0xFFCE40, patches.door_map_music_player)

        # Make the Tower of Execution 3HB pillars with 1HB breakables not set their flags, and have said 1HB breakables
        # set the flags instead.
        patcher.write_int16(0x7E0A66, 0x0000)
        patcher.write_int16(0x7E0B26, 0x01B5)
        patcher.write_int16(0x7E0A96, 0x0000)
        patcher.write_int16(0x7E0B32, 0x01B8)

        # Make the Tower of Sorcery pink diamond always drop the same 3 items, prevent it from setting its own flag when
        # broken, and have it set individual flags on each of its drops.
        patcher.write_int32(0x7DD624, 0x00106040)  # SLL   T4, S0, 1
        patcher.write_int32(0x7DCE2C, 0x00000000)  # NOP
        patcher.write_int32(0x7DCDFC, 0x0C0FF3A4)  # JAL   0x803FCE90
        patcher.write_int32s(0xFFCE80, patches.pink_sorcery_diamond_customizer)

        # Lock the door in Clock Tower workshop leading out to the grand abyss map with Clocktower Key D.
        # It's the same door in-universe as Clocktower Door D but on a different map.
        patcher.write_int16(0x82D104, 0x5300)
        patcher.write_int16(0x82D130, 0x5300)
        patcher.write_int32(0x82D108, 0x803FCEC0)
        patcher.write_int32(0x82D134, 0x803FCED4)
        patcher.write_int16(0x82D10C, 0x029E)
        patcher.write_byte(0x82D113, 0x26)
        patcher.write_int16(0x82D116, 0x0102)
        patcher.write_int32s(0xFFCEC0, patches.clock_tower_workshop_text_modifier)
        # Custom text for the new locked door instance.
        patcher.write_bytes(0x7C1B14, cvlod_string_to_bytearray("Locked in!\n"
                                                                 "You need Deck Key.»\t"
                                                                 "Deck Key\n"
                                                                 "       has been used.»\t", wrap=False)[0])

        # Prevent the Renon's Departure cutscene from triggering during the castle escape sequence.
        patcher.write_byte(0x7CCFF1, 0x80)
        patcher.write_int16(0x7CD002, 0x017D)

        # Hack to make the Forest, CW and Villa intro cutscenes play at the start of their levels no matter what map
        # came before them
        # #patcher.write_int32(0x97244, 0x803FDD60)
        # #patcher.write_int32s(0xBFDD60, patches.forest_cw_villa_intro_cs_player)

        # Make changing the map ID to 0xFF reset the map (helpful to work around a bug wherein the camera gets stuck
        # when entering a loading zone that doesn't change the map) or changing the map ID to 0x53 or 0x93 to go to a
        # decoupled version of the Spider Queen or Medusa arena respectively.
        patcher.write_int32s(0x1C3B4, [0x0C0FF304,    # JAL   0x803FCC10
                                        0x24840008]),  # ADDIU A0, A0, 0x0008
        patcher.write_int32s(0xFFCC10, patches.map_refresher)

        # Enable swapping characters when loading into a map by holding L.
        # patcher.write_int32(0x97294, 0x803FDFC4)
        # patcher.write_int32(0x19710, 0x080FF80E)  # J 0x803FE038
        # patcher.write_int32s(0xBFDFC4, patches.character_changer)

        # Villa coffin time-of-day hack
        # patcher.write_byte(0xD9D83, 0x74)
        # patcher.write_int32(0xD9D84, 0x080FF14D)  # J 0x803FC534
        # patcher.write_int32s(0xBFC534, patches.coffin_time_checker)

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
        if options["increase_item_limit"]:
            patcher.write_byte(0x90617, 0x63)  # Most items
            patcher.write_byte(0x90767, 0x63)  # Sun/Moon cards

        # Rename the Special3 to "AP Item"
        patcher.write_bytes(0xB89AA, cvlod_string_to_bytearray("AP Item ")[0])
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

        # Disable the 3HBs checking and setting flags when breaking them and enable their individual items checking and
        # setting flags instead.
        if options["multi_hit_breakables"]:
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

        # If the empty breakables are on, write all data associated with them.
        if options["empty_breakables"]:
            for offset in patches.empty_breakables_data:
                patcher.write_bytes(offset, patches.empty_breakables_data[offset])

        # Kills the pointer to the Countdown number, resets the "in a demo?" value whenever changing/reloading the
        # game state, and mirrors the current game state value in a spot that's easily readable.
        patcher.write_int32(0x1168, 0x08007938)  # J 0x8001E4E0
        patcher.write_int32s(0x1F0E0, [0x3C08801D,  # LUI   T0, 0x801D
                                        0xA104AA30,  # SB    A0, 0xAA30 (T0)
                                        0xA100AA4A,  # SB    R0, 0xAA4A (T0)
                                        0x03E00008,  # JR    RA
                                        0xFD00AA40])  # SD    R0, 0xAA40 (T0)

        # Everything related to the Countdown counter.
        if options["countdown"]:
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

        # Disable or guarantee vampire Vincent's fight
        # if options.vincent_fight_condition.value == options.vincent_fight_condition.option_never:
        # patcher.write_int32(0xAACC0, 0x24010001)  # ADDIU AT, R0, 0x0001
        # patcher.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000
        # elif options.vincent_fight_condition.value == options.vincent_fight_condition.option_always:
        # patcher.write_int32(0xAACE0, 0x24180010)  # ADDIU T8, R0, 0x0010
        # else:
        # patcher.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000

        # Disable or guarantee Renon's fight
        # patcher.write_int32(0xAACB4, 0x080FF1A4)  # J 0x803FC690
        # if options.renon_fight_condition.value == options.renon_fight_condition.option_never:
        # patcher.write_byte(0xB804F0, 0x00)
        # patcher.write_byte(0xB80632, 0x00)
        # patcher.write_byte(0xB807E3, 0x00)
        # patcher.write_byte(0xB80988, 0xB8)
        # patcher.write_byte(0xB816BD, 0xB8)
        # patcher.write_byte(0xB817CF, 0x00)
        # patcher.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
        # elif options.renon_fight_condition.value == options.renon_fight_condition.option_always:
        # patcher.write_byte(0xB804F0, 0x0C)
        # patcher.write_byte(0xB80632, 0x0C)
        # patcher.write_byte(0xB807E3, 0x0C)
        # patcher.write_byte(0xB80988, 0xC4)
        # patcher.write_byte(0xB816BD, 0xC4)
        # patcher.write_byte(0xB817CF, 0x0C)
        # patcher.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
        # else:
        # patcher.write_int32s(0xBFC690, patches.renon_cutscene_checker)

        # NOP the Easy Mode check when buying a thing from Renon, so he can be triggered even on this mode.
        # patcher.write_int32(0xBD8B4, 0x00000000)

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

        # CC top elevator switch check
        # patcher.write_int32(0x6CF0A0, 0x0C0FF0B0)  # JAL 0x803FC2C0
        # patcher.write_int32s(0xBFC2C0, patches.elevator_flag_checker)

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

        # Ambience silencing fix
        patcher.write_int32(0x1BB20, 0x080FF280)  # J 0x803FCA00
        patcher.write_int32s(0xFFCA00, patches.ambience_silencer)
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

        # Initial Countdown numbers and Start Inventory
        patcher.write_int32(0x90DBC, 0x080FF200)  # J	0x803FC800
        patcher.write_int32s(0xFFC800, patches.new_game_extras)

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

        # Write the specified window colors
        patcher.write_byte(0x8881A, options["window_color_r"] << 4)
        patcher.write_byte(0x8881B, options["window_color_g"] << 4)
        patcher.write_byte(0x8881E, options["window_color_b"] << 4)
        patcher.write_byte(0x8881F, options["window_color_a"] << 4)

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

        # Write all the edits to the Nisitenma-Ichigo files decided during generation.
        for file in ni_edits:
            for offset in ni_edits[file]:
                patcher.write_bytes(int(offset), base64.b64decode(ni_edits[file][offset].encode()), int(file))

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

    mary_text = cvlod_text_wrap(mary_text, 254)

    patch.write_token(APTokenTypes.WRITE, 0x78EAE0,
                      bytes(cvlod_string_to_bytearray(mary_text[0] + (" " * (866 - len(mary_text[0]))))[0]))

    # Write the secondary name the client will use to distinguish a vanilla ROM from an AP one.
    patch.write_token(APTokenTypes.WRITE, 0xFFBFD0, "ARCHIPELAG01".encode("utf-8"))
    # Write the slot authentication
    patch.write_token(APTokenTypes.WRITE, 0xFFBFE0, bytes(world.auth))

    patch.write_file("token_data.bin", patch.get_token_binary())

    # Write these slot options to a JSON.
    options_dict = {
        # "character_stages": world.options.character_stages.value,
        # "vincent_fight_condition": world.options.vincent_fight_condition.value,
        # "renon_fight_condition": world.options.renon_fight_condition.value,
        # "bad_ending_condition": world.options.bad_ending_condition.value,
        "increase_item_limit": world.options.increase_item_limit.value,
        # "nerf_healing_items": world.options.nerf_healing_items.value,
        # "loading_zone_heals": world.options.loading_zone_heals.value,
        # "disable_time_restrictions": world.options.disable_time_restrictions.value,
        # "death_link": world.options.death_link.value,
        # "draculas_condition": world.options.draculas_condition.value,
        # "invisible_items": world.options.invisible_items.value,
        # "post_behemoth_boss": world.options.post_behemoth_boss.value,
        # "room_of_clocks_boss": world.options.room_of_clocks_boss.value,
        # "skip_gondolas": world.options.skip_gondolas.value,
        # "skip_waterway_blocks": world.options.skip_waterway_blocks.value,
        # "s1s_per_warp": world.options.special1s_per_warp.value,
        # "required_s2s": world.required_s2s,
        # "total_s2s": world.total_s2s,
        # "total_special1s": world.options.total_special1s.value,
        # "increase_shimmy_speed": world.options.increase_shimmy_speed.value,
        # "fall_guard": world.options.fall_guard.value,
        # "permanent_powerups": world.options.permanent_powerups.value,
        # "background_music": world.options.background_music.value,
        "multi_hit_breakables": world.options.multi_hit_breakables.value,
        "empty_breakables": world.options.empty_breakables.value,
        # "drop_previous_sub_weapon": world.options.drop_previous_sub_weapon.value,
        "countdown": world.options.countdown.value,
        # "shopsanity": world.options.shopsanity.value,
        # "panther_dash": world.options.panther_dash.value,
        # "big_toss": world.options.big_toss.value,
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
