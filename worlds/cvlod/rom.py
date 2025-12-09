import json
import Utils

from BaseClasses import Location
from worlds.Files import APProcedurePatch, APPatchExtension
from typing import List, Dict, Union, Iterable, TYPE_CHECKING

import hashlib
import os
# import pkgutil

from .data import patches, loc_names, stage_names
from .data.enums import Scenes, NIFiles, Objects, ObjectExecutionFlags, ActorSpawnFlags, Items, Pickups, PickupFlags, \
    DoorFlags
from .items import HIGHER_SPAWNING_ITEMS
from .locations import CVLOD_LOCATIONS_INFO, THREE_HIT_BREAKABLES_INFO, HIGHER_SPAWNING_PROBLEM_LOCATIONS, \
    NEW_VISIBLE_ITEM_COORDS
from .patcher import CVLoDRomPatcher, CVLoDSceneTextEntry, CVLoDNormalActorEntry, CVLoDSpawnEntranceEntry, \
    SCENE_OVERLAY_RDRAM_START
from .stages import CVLOD_STAGE_INFO
from .cvlod_text import cvlod_string_to_bytearray, cvlod_text_wrap, cvlod_bytes_to_string, LEN_LIMIT_MAP_TEXT
# from .aesthetics import renon_item_dialogue
from .options import StageLayout, VincentFightCondition, RenonFightCondition, PostBehemothBoss, RoomOfClocksBoss, \
    DuelTowerFinalBoss, CastleKeepEndingSequence, DeathLink, DraculasCondition, InvisibleItems, \
    PantherDash, VillaBranchingPaths, CastleCenterBranchingPaths, CastleWallState, VillaState, VillaMazeKid, \
    DisableTimeRestrictions
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

NG_EXTRAS_START = 0xFFC800
INITIAL_COUNTDOWN_ARRAY_START = NG_EXTRAS_START - 0x30
START_INVENTORY_ARRAY_START = NG_EXTRAS_START - 0x60
START_INVENTORY_GOLD_UPPER_ADDR = NG_EXTRAS_START + 0x36
START_INVENTORY_GOLD_LOWER_ADDR = NG_EXTRAS_START + 0x3A
START_INVENTORY_POWERUPS_ADDR = NG_EXTRAS_START + 0x43
START_INVENTORY_SUBWEAPON_ADDR = NG_EXTRAS_START + 0x4B
START_INVENTORY_SUBWEAPON_LEVEL_ADDR = NG_EXTRAS_START + 0x53
START_INVENTORY_ICE_TRAP_ADDR = NG_EXTRAS_START + 0x5B

FOREST_OVL_CHARNEL_ITEMS_START = 0x7C60  # 0x802EB7D0
CHARNEL_ITEM_LEN = 0xC
FIRST_CHARNEL_LID_ACTOR = 72

TELEPORT_JEWEL_VALUES_START = 0x112FB0  # 0x80192700
TELEPORT_JEWEL_ENTRY_LEN = 0x4
TELEPORT_JEWEL_START_STAGES = [stage_names.TUNNEL, stage_names.WATERWAY, stage_names.OUTER]

WARP_SCENE_OFFSETS = [0xADF67, 0xADF77, 0xADF87, 0xADF97, 0xADFA7, 0xADFBB, 0xADFCB, 0xADFDF]

SPECIAL_1HBS = [Objects.FOGGY_LAKE_ABOVE_DECKS_BARREL, Objects.FOGGY_LAKE_BELOW_DECKS_BARREL,
                Objects.SORCERY_BLUE_DIAMOND]

FOUNTAIN_LETTERS_TO_NUMBERS = {"O": 1, "M": 2, "H": 3, "V": 4}

VILLA_MAZE_CORNELL_ENEMY_INDEXES = [66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 82,
                                    83, 84, 85, 86, 87, 88, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101]

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
        # Determine what flags should be set upon beginning a new game.
        starting_flags = []

        # Get the dictionaries of item values mapped to their location IDs and relevant name texts out of the slot
        # patch info and convert each location ID key from a string into an int.
        loc_values = {int(loc_id): item_value for loc_id, item_value in slot_patch_info["location values"].items()}
        loc_text = {int(loc_id): item_names for loc_id, item_names in slot_patch_info["location text"].items()}


        # # # # # # # # # # # # # #
        # GENERAL PRE-STAGE EDITS #
        # # # # # # # # # # # # # #
        # Custom overlay segment-loading code.
        patcher.write_int32(0x18A94, 0x0800793D)  # J 0x8001E4F4
        patcher.write_int32s(0x1F0F4, patches.custom_code_loader)

        # Initial Countdown numbers and Start Inventory.
        patcher.write_int32(0x90DBC, 0x080FF200)  # J	0x803FC800
        patcher.write_int32s(NG_EXTRAS_START, patches.new_game_extras)
        # Write the Start Inventory values here.
        patcher.write_bytes(START_INVENTORY_ARRAY_START, slot_patch_info["start inventory"]["inv array"])
        patcher.write_int16(START_INVENTORY_GOLD_UPPER_ADDR, slot_patch_info["start inventory"]["gold"] >> 16)
        patcher.write_int16(START_INVENTORY_GOLD_LOWER_ADDR, slot_patch_info["start inventory"]["gold"] & 0xFFFF)
        patcher.write_byte(START_INVENTORY_POWERUPS_ADDR, slot_patch_info["start inventory"]["powerups"])
        patcher.write_byte(START_INVENTORY_SUBWEAPON_ADDR, slot_patch_info["start inventory"]["sub weapon"])
        patcher.write_byte(START_INVENTORY_SUBWEAPON_LEVEL_ADDR,
                           slot_patch_info["start inventory"]["sub weapon level"])
        patcher.write_byte(START_INVENTORY_ICE_TRAP_ADDR, slot_patch_info["start inventory"]["ice traps"])

        # Everything related to the Countdown counter.
        # NOTE: Must be written AFTER the custom overlay stuff.
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

            # Write the initial Countdown numbers array.
            patcher.write_bytes(0xFFC7D0, slot_patch_info["initial countdowns"])

        # Kills the pointer to the Countdown number, resets the "in a demo?" value whenever changing/reloading the
        # game state, and mirrors the current game state value in a spot that's easily readable.
        patcher.write_int32(0x1168, 0x08007938)  # J 0x8001E4E0
        patcher.write_int32s(0x1F0E0, [0x3C08801D,  # LUI   T0, 0x801D
                                        0xA104AA30,  # SB    A0, 0xAA30 (T0)
                                        0xA100AA4A,  # SB    R0, 0xAA4A (T0)
                                        0x03E00008,  # JR    RA
                                        0xFD00AA40])  # SD    R0, 0xAA40 (T0)

        # Enable being able to set one of the three alternate setup flags (0x2A1, 0x2A2, or 0x2A3) by setting the 0x40
        # and/or 0x80 bits in the spawn ID.
        patcher.write_int32s(0x1C3B4, [0x0C0FF304,    # JAL   0x803FCC10
                                        0x24840008]),  # ADDIU A0, A0, 0x0008
        patcher.write_int32s(0xFFCC10, patches.alt_setup_flag_setter)

        # Add keys in an AP logo formation to the title screen.
        patcher.scenes[Scenes.INTRO_NARRATION].actor_lists["proxy"] += [
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=0.0, y_pos=3.8, z_pos=0.0, execution_flags=0,
                                  object_id=Objects.INTERACTABLE, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.LEFT_TOWER_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=-3.6, y_pos=1.8, z_pos=-2.8, execution_flags=0,
                                  object_id=Objects.INTERACTABLE, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.STOREROOM_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=3.6, y_pos=1.8, z_pos=2.8, execution_flags=0,
                                  object_id=Objects.INTERACTABLE, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.COPPER_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=-3.6, y_pos=-2.2, z_pos=-2.8, execution_flags=0,
                                  object_id=Objects.INTERACTABLE, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.CHAMBER_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=3.6, y_pos=-2.2, z_pos=2.8, execution_flags=0,
                                  object_id=Objects.INTERACTABLE, flag_id=0, var_a=0, var_b=0,
                                  var_c=Pickups.EXECUTION_KEY, var_d=0, extra_condition_ptr=0),
            CVLoDNormalActorEntry(spawn_flags=0, status_flags=0, x_pos=0.0, y_pos=-4.2, z_pos=0.0, execution_flags=0,
                                  object_id=Objects.INTERACTABLE, flag_id=0, var_a=0, var_b=0,
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

        # If the Castle Wall State is either Cornell's or Hybrid, set all the flags that the "meeting Ortega" cutscene
        # normally sets so that the stage can begin in its initial unsolved Cornell state.
        if slot_patch_info["options"]["castle_wall_state"] != CastleWallState.option_reinhardt_carrie:
            starting_flags += [0x3C,  # Met Ortega
                               0x53]  # End Portcullis open

        # Prevent Henry's days tracker object from spawning so he'll have unlimited time just like everyone else.
        patcher.write_byte(0x86DDF, 0x04)
        # Make the Henry teleport jewels work for everyone at the expense of the light effect surrounding them.
        # The code that creates and renders it is exclusively inside Henry's overlay, so it must be tossed for the actor
        # to function for the rest of the characters, sadly.
        patcher.write_int32(0xF6A5C, 0x00000000)  # NOP

        # Custom remote item rewarding and DeathLink receiving code
        patcher.write_int32(0x1C854, 0x080FF000)  # J 0x803FC000
        patcher.write_int32s(0xFFC000, patches.remote_item_giver)
        patcher.write_int32s(0xFFE190, patches.subweapon_surface_checker)

        # Make it possible to change the starting area after the intro narration cutscene.
        # Change the instruction that stores the Foggy Lake intro cutscene value to store a 0 (from R0) instead.
        patcher.write_int32(0x1614, 0xAC402BCC, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON) # SW  R0, 0x2BCC (V0)
        # Instead of always 0 as the spawn entrance, store the aftermentined cutscene value as it.
        patcher.write_int32(0x1618, 0xA04B2BBB, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON) # SB  T3, 0x2BBB (V0)
        # Make the starting level the same for Henry as everyone else.
        patcher.write_byte(0x15D5, 0x00, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)

        # Active cutscene checker routines for certain actors.
        patcher.write_int32s(0xFFCDA0, patches.cutscene_active_checkers)

        # Ambience silencing fix and map refresher.
        patcher.write_int32(0x1BB20, 0x080FF280)  # J 0x803FCA00
        patcher.write_int32s(0xFFCA00, patches.ambience_silencer)

        # Enable being able to carry multiple Special jewels, Nitros, Mandragoras, and Key Items simultaneously, and
        # make the Special1 and 2 play sounds when you reach milestones with them.
        patcher.write_int32s(0xFFDA50, patches.special_sound_notifs)
        patcher.write_int16(0xFFDA6E, slot_patch_info["options"]["special1s_per_warp"])
        patcher.write_int16(0xFFDA82, len(slot_patch_info["warps"]))
        # Special1
        patcher.write_int32s(0x904B8, [0x90C8AB47,   # LBU   T0, 0xAB47 (A2)
                                       0x00681821,   # ADDU  V1, V1, T0
                                       0xA0C3AB47,   # SB    V1, 0xAB47 (A2)
                                       0x080FF69B,   # J     0x803FDA6C
                                       0x00000000])  # NOP
        # Special2
        patcher.write_int32s(0x904CC, [0x90C8AB48,   # LBU   T0, 0xAB48 (A2)
                                       0x00681821,   # ADDU  V1, V1, T0
                                       0xA0C3AB48,   # SB    V1, 0xAB48 (A2)
                                       0x080FF694,   # J     0x803FDA50
                                       0x00000000])  # NOP
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

        # Make the Special1 and 2 play sounds when you reach milestones with them.

        # patcher.write_int32(0xBF240, 0x080FF694)  # J 0x803FDA50
        # patcher.write_int32(0xBF220, 0x080FF69E)  # J 0x803FDA78

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
        # Write "Z + R + START" over the Special1 description.
        patcher.write_bytes(0x3B7C, cvlod_string_to_bytearray("Z + R + START", add_end_char=True),
                            NIFiles.OVERLAY_PAUSE_MENU)

        # Enable changing the item model/visibility on any item instance.
        patcher.write_int32s(0x107740, [0x0C0FF0C0,   # JAL   0x803FC300
                                        0x25CFFFFF])  # ADDIU T7, T6, 0xFFFF
        patcher.write_int32s(0xFFC300, patches.item_customizer)
        patcher.write_int32s(0x1078B0, [0x0C0FF0CB,   # JAL   0x803FC32C
                                        0x94C90038])  # LHU   T1, 0x0038 (A2)
        patcher.write_int32s(0xFFC32C, patches.pickup_model_switcher)
        patcher.write_int32s(0x107A5C, [0x0C0FF0EC,   # JAL   0x803FC3B0
                                        0x94CF0038])  # LHU   T7, 0x0038 (A2)
        patcher.write_int32s(0xFFC3B0, patches.pickup_spawn_height_switcher)
        patcher.write_int32s(0x108024, [0x0C0FF0F4,   # JAL   0x803FC3D0
                                        0x96090038])  # LHU   T1, 0x0038 (S0)
        patcher.write_int32s(0xFFC3D0, patches.pickup_spin_speed_switcher)
        patcher.write_int32s(0x108E80, [0x0C0FF0FC,   # JAL   0x803FC3F0
                                        0x948F0038])  # LHU   T7, 0x0038 (A0)
        patcher.write_int32s(0xFFC3F0, patches.pickup_shine_size_switcher)
        patcher.write_int32s(0x108EB0, [0x0C0FF104,   # JAL   0x803FC410
                                        0x96190038])  # LHU   T9, 0x0038 (S0)
        patcher.write_int32s(0xFFC410, patches.pickup_shine_height_switcher)

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

        # NPC items rework
        patcher.write_int32s(0xFFC6F0, patches.npc_item_rework)
        # Change all the NPC item gives to run through the new routine, and write all their item values.
        # Fountain Top Shine
        if CVLOD_LOCATIONS_INFO[loc_names.villafy_fountain_shine].flag_id in loc_values:
            patcher.write_int16(0x35E, 0x8040, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
            patcher.write_int16(0x362, 0xC700, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
            patcher.write_byte(0x367, 0x00, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
            patcher.write_int16(0x36E, 0x0068, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
            patcher.write_bytes(0x720, cvlod_string_to_bytearray("...🅰0/", add_end_char=True),
                                NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
            patcher.write_int16(0xFFC6F0, loc_values[CVLOD_LOCATIONS_INFO[loc_names.villafy_fountain_shine].flag_id][0])
        # 6am Rose Patch
        if CVLOD_LOCATIONS_INFO[loc_names.villafo_6am_roses].flag_id in loc_values:
            patcher.write_int16(0x1E2, 0x8040, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
            patcher.write_int16(0x1E6, 0xC700, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
            patcher.write_byte(0x1EB, 0x01, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
            patcher.write_int16(0x1F2, 0x0078, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
            patcher.write_bytes(0x380, cvlod_string_to_bytearray("...🅰0/", add_end_char=True),
                                NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
            patcher.write_int16(0xFFC6F0 + 2, loc_values[CVLOD_LOCATIONS_INFO[loc_names.villafo_6am_roses].flag_id][0])
        # Vincent
        if CVLOD_LOCATIONS_INFO[loc_names.villala_vincent].flag_id in loc_values:
            patcher.write_int16(0x180E, 0x8040, NIFiles.OVERLAY_VINCENT)
            patcher.write_int16(0x1812, 0xC700, NIFiles.OVERLAY_VINCENT)
            patcher.write_byte(0x1817, 0x02, NIFiles.OVERLAY_VINCENT)
            patcher.write_int16(0x181E, 0x027F, NIFiles.OVERLAY_VINCENT)
            patcher.write_int16(0xFFC6F0 + 4, loc_values[CVLOD_LOCATIONS_INFO[loc_names.villala_vincent].flag_id][0])
        # Mary
        if CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id in loc_values:
            patcher.write_int16(0xB16, 0x8040, NIFiles.OVERLAY_MARY)
            patcher.write_int16(0xB1A, 0xC700, NIFiles.OVERLAY_MARY)
            patcher.write_byte(0xB1F, 0x03, NIFiles.OVERLAY_MARY)
            patcher.write_int16(0xB26, 0x0086, NIFiles.OVERLAY_MARY)
            patcher.write_int16(0xFFC6F0 + 6, loc_values[CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id][0])
        # Heinrich Meyer
        if CVLOD_LOCATIONS_INFO[loc_names.ccll_heinrich].flag_id in loc_values:
            patcher.write_int16(0x962A, 0x8040, NIFiles.OVERLAY_LIZARD_MEN)
            patcher.write_int16(0x962E, 0xC700, NIFiles.OVERLAY_LIZARD_MEN)
            patcher.write_byte(0x9633, 0x04, NIFiles.OVERLAY_LIZARD_MEN)
            patcher.write_int16(0x963A, 0x0284, NIFiles.OVERLAY_LIZARD_MEN)
            patcher.write_int16(0xFFC6F0 + 8, loc_values[CVLOD_LOCATIONS_INFO[loc_names.ccll_heinrich].flag_id][0])

        # Disable the 3HBs checking and setting flags when breaking them and enable their individual items checking and
        # setting flags instead.
        patcher.write_int16(0xE3488, 0x1000)
        patcher.write_int32(0xE3800, 0x24050000)  # ADDIU	A1, R0, 0x0000
        patcher.write_byte(0xE39EB, 0x00)
        patcher.write_int32(0xE3A58, 0x0C0FF0D4),  # JAL   0x803FC350
        patcher.write_int32s(0xFFC350, patches.three_hit_item_flags_setter)
        # Villa foyer chandelier-specific functions (yeah, KCEK really made special handling just for this one)
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
        sea_monster_path_unsetter_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_SEA_MONSTER)
        patcher.write_int32(0x7268, 0x0FC00000 | (sea_monster_path_unsetter_start // 4), NIFiles.OVERLAY_SEA_MONSTER)
        patcher.write_int32s(sea_monster_path_unsetter_start, patches.sea_monster_sunk_path_flag_unsetter,
                             NIFiles.OVERLAY_SEA_MONSTER)
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
        if CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id in loc_values:
            # Entry 0
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                FOREST_OVL_CHARNEL_ITEMS_START + 2,
                loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id][0])
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                FOREST_OVL_CHARNEL_ITEMS_START + 6, CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id)
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(FOREST_OVL_CHARNEL_ITEMS_START + 9, 0x00)
            # Set the "invisibility" bit if it should be.
            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla and \
                    not loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id][1]:
                patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(FOREST_OVL_CHARNEL_ITEMS_START + 8,
                                                                         PickupFlags.GRAVITY | PickupFlags.INVISIBLE)
            # Entry 1
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 2,
                loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_2].flag_id][0])
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 6,
                CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_2].flag_id)
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(
                FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 9, 0x00)
            # Set the "invisibility" bit if it should be.
            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla and \
                    not loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id][1]:
                patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                    FOREST_OVL_CHARNEL_ITEMS_START + CHARNEL_ITEM_LEN + 8,
                    PickupFlags.GRAVITY | PickupFlags.INVISIBLE)
            # Entry 8
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 2,
                loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_3].flag_id][0])
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 6,
                CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_3].flag_id)
            patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_byte(
                FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 9, 0x00)
            # Set the "invisibility" bit if it should be.
            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla and \
                    not loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_charnel_1].flag_id][1]:
                patcher.scenes[Scenes.FOREST_OF_SILENCE].write_ovl_int16(
                    FOREST_OVL_CHARNEL_ITEMS_START + (CHARNEL_ITEM_LEN * 8) + 8,
                    PickupFlags.GRAVITY | PickupFlags.INVISIBLE)
        # If the chosen prize coffin is not coffin 0, swap the actor var C's of the lids of coffin 0 and the coffin that
        # did get chosen.
        if slot_patch_info["prize coffin id"]:
            patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][
                FIRST_CHARNEL_LID_ACTOR]["var_c"] = slot_patch_info["prize coffin id"]
            patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][
                FIRST_CHARNEL_LID_ACTOR + slot_patch_info["prize coffin id"]]["var_c"] = 0

        # Turn the Forest Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["spawn_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["execution_flags"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["flag_id"] = 0
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.forest_child_ledge].flag_id
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"][122]["var_c"] = Pickups.ONE_HUNDRED_GOLD

        # Make King Skeleton 2 open the gate when defeated if the final gate switch was flipped rather than just if we
        # are Henry.
        patcher.write_int32s(0x4324, [0x9108AA61,  # LBU  T0, 0xAA61 (T0)
                                      0x31080010], # ANDI T0, T0, 0x0010
                             NIFiles.OVERLAY_KING_SKELETON)
        patcher.write_int32(0x4330, 0x11000010, NIFiles.OVERLAY_KING_SKELETON)  # BEQZ T0, [forward 0x10]

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
        if CVLOD_LOCATIONS_INFO[loc_names.forest_skelly_mouth].flag_id in loc_values:
            patcher.write_int16(0x43CA, loc_values[CVLOD_LOCATIONS_INFO[loc_names.forest_skelly_mouth].flag_id][0],
                                NIFiles.OVERLAY_KING_SKELETON)
        # Add the backup King Skeleton jaws item that will spawn only if the player orphans it the first time.
        patcher.scenes[Scenes.FOREST_OF_SILENCE].actor_lists["proxy"].append(
            CVLoDNormalActorEntry(spawn_flags=ActorSpawnFlags.SPAWN_IF_FLAG_SET, status_flags=0, x_pos= 0.03125,
                                  y_pos=0, z_pos=-1430,execution_flags=0, object_id=Objects.INTERACTABLE,
                                  flag_id=0x2C,  # Drawbridge lowering cutscene flag.
                                  var_a=CVLOD_LOCATIONS_INFO[loc_names.forest_skelly_mouth].flag_id, var_b=0,
                                  var_c=Pickups.ROAST_CHICKEN, var_d=0, extra_condition_ptr=0)
        )

        # Make the drawbridge cutscene's end behavior its Henry end behavior for everyone and make it possible to have
        # it send you to any scene at any spawn.
        # The "drawbridge lowered" flag should be set so that Forest's regular end zone is easily accessible, and no
        # separate cutscene should play in the next map.
        patcher.write_int32(0x1294, 0x1000000C, NIFiles.OVERLAY_CS_FOREST_DRAWBRIDGE_LOWERS)
        patcher.write_int32(0x1308, 0x3C080002, NIFiles.OVERLAY_CS_FOREST_DRAWBRIDGE_LOWERS)  # LUI  T0, 0x0002
        patcher.write_int32(0x1318, 0x35080000, NIFiles.OVERLAY_CS_FOREST_DRAWBRIDGE_LOWERS)  # ORI  T0, T0, 0x0000
        patcher.write_int32(0x1320, 0xAC482BB8, NIFiles.OVERLAY_CS_FOREST_DRAWBRIDGE_LOWERS)  # SW   T0, 0x2BB8 (V0)

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
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][158]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][159]["spawn_flags"] = 0
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][160]["delete"] = True
        patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][161]["delete"] = True
        # Make the Henry-only start loading zone universal to everyone.
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][59]["spawn_flags"] = 0
        # Make the end portcullis text spot universal to everyone (including Henry)
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][5]["spawn_flags"] = 0

        # Remove the cutscene settings ID on the end loading zone to Villa so that the Villa intro cutscene won't play
        # when it sends you to a different stage.
        patcher.scenes[Scenes.CASTLE_WALL_MAIN].loading_zones[5]["cutscene_settings_id"] = 0

        # Make the hardcoded Henry checks in the "set map music" function in the event the map is one of the Castle Wall
        # maps never pass.
        patcher.write_int32(0x1C448, 0x34180000)  # ORI  T8, R0, 0x0000
        patcher.write_int32(0x1C450, 0x34190000)  # ORI  T9, R0, 0x0000

        # If the Castle Wall State is Reinhardt/Carrie's, put the stage in Reinhardt and Carrie's state for everyone.
        if slot_patch_info["options"]["castle_wall_state"] == CastleWallState.option_reinhardt_carrie:
            # Right Tower switch spot is the non-lever missing version.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][9]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][10]["spawn_flags"] = 0
            # Left Tower switch text spot is absent as it's instead flipped during the Dracula cutscene.
            # The text spot for the middle portcullis is present.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][4]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][6]["delete"] = True
            # Portcullises are Reinhardt/Carrie's versions.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][52]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][53]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][54]["delete"] = True
            # Main area Right Tower door is a normal door. Left Tower door is a Left Tower Key door.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][55]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][56]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][57]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][58]["delete"] = True
            # The Ground Gatehouse Middle candle is present.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][32]["spawn_flags"] = 0

            # Left Tower interior top door is a moon door.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][191]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][192]["delete"] = True
            # Left Tower interior top loading zone plays the Fake Dracula taunt cutscene.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][195]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][196]["delete"] = True
            # Both towers' platform behaviors are Reinhardt/Carrie's for everyone.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].write_ovl_int32(0x9E0, 0x340F0000)  # ORI  T7, R0, 0x0000

            # All hardcoded lever checks for Cornell never pass.
            patcher.write_int32(0xE6C18, 0x240A0000)  # ADDIU T2, R0, 0x0000
            patcher.write_int32(0xE6F64, 0x240E0000)  # ADDIU T6, R0, 0x0000
            patcher.write_int32(0xE70F4, 0x240D0000)  # ADDIU T5, R0, 0x0000
            patcher.write_int32(0xE7364, 0x24080000)  # ADDIU T0, R0, 0x0000
            patcher.write_int32(0x109C10, 0x240E0000)  # ADDIU T6, R0, 0x0000
        # If the Castle Wall State is Cornell's, put the stage in Reinhardt and Cornell's state for everyone.
        elif slot_patch_info["options"]["castle_wall_state"] == CastleWallState.option_cornell:
            # Right Tower switch spot is the lever missing version.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][9]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][10]["delete"] = True
            # Left Tower switch text spot is present. The text spot for the middle portcullis is absent.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][4]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][6]["spawn_flags"] = 0
            # Portcullises are Cornell's versions.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][52]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][53]["spawn_flags"] ^= ActorSpawnFlags.CORNELL
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][54]["spawn_flags"] ^= ActorSpawnFlags.CORNELL
            # Main area Right Tower door is a sun door. Left Tower door is a moon door.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][55]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][56]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][57]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][58]["spawn_flags"] = 0
            # The Ground Gatehouse Middle candle is absent.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][32]["delete"] = True

            # Left Tower interior top door is a regular door.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][191]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][192]["spawn_flags"] = 0
            # Left Tower interior top loading zone plays no cutscene.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][195]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][196]["spawn_flags"] = 0
            # Both towers' platform behaviors are Cornell's for everyone.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].write_ovl_int32(0x9E0, 0x340F0002)  # ORI  T7, R0, 0x0002

            # All hardcoded lever checks for Cornell always pass.
            patcher.write_int32(0xE6C18, 0x240A0002)  # ADDIU T2, R0, 0x0002
            patcher.write_int32(0xE6F64, 0x240E0002)  # ADDIU T6, R0, 0x0002
            patcher.write_int32(0xE70F4, 0x240D0002)  # ADDIU T5, R0, 0x0002
            patcher.write_int32(0xE7364, 0x24080002)  # ADDIU T0, R0, 0x0002
            patcher.write_int32(0x109C10, 0x240E0002)  # ADDIU T6, R0, 0x0002
        # Otherwise, if Hybrid was chosen, put the stage in a hybrid state for everyone.
        else:
            # Right Tower switch spot is the lever missing version.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][9]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][10]["delete"] = True
            # Left Tower switch text spot is present. The text spot for the middle portcullis is absent.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][4]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["init"][6]["spawn_flags"] = 0
            # Portcullises are Cornell's versions.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][52]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][53]["spawn_flags"] ^= ActorSpawnFlags.CORNELL
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][54]["spawn_flags"] ^= ActorSpawnFlags.CORNELL
            # Main area Right Tower door is a normal door. Left Tower door is a Left Tower Key door.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][55]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][56]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][57]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][58]["delete"] = True
            # The Ground Gatehouse Middle candle is present.
            patcher.scenes[Scenes.CASTLE_WALL_MAIN].actor_lists["proxy"][32]["spawn_flags"] = 0

            # Left Tower interior top door is a regular door.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][191]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][192]["spawn_flags"] = 0
            # Left Tower interior top loading zone plays no cutscene.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][195]["delete"] = True
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].actor_lists["proxy"][196]["spawn_flags"] = 0
            # Both towers' platform behaviors are Cornell's for everyone.
            patcher.scenes[Scenes.CASTLE_WALL_TOWERS].write_ovl_int32(0x9E0, 0x340F0002)  # ORI  T7, R0, 0x0002

            # All hardcoded lever checks for Cornell always pass.
            patcher.write_int32(0xE6C18, 0x240A0002)  # ADDIU T2, R0, 0x0002
            patcher.write_int32(0xE6F64, 0x240E0002)  # ADDIU T6, R0, 0x0002
            patcher.write_int32(0xE70F4, 0x240D0002)  # ADDIU T5, R0, 0x0002
            patcher.write_int32(0xE7364, 0x24080002)  # ADDIU T0, R0, 0x0002
            patcher.write_int32(0x109C10, 0x240E0002)  # ADDIU T6, R0, 0x0002


        # # # # # # # #
        # VILLA EDITS #
        # # # # # # # #
        # Make Reinhardt/Carrie/Cornell's White Jewels universal to everyone and remove Henry's.
        patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][47]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][48]["delete"] = True
        patcher.scenes[Scenes.VILLA_FOYER].actor_lists["room 5"][0]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_FOYER].actor_lists["room 5"][1]["delete"] = True
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 0"][10]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 0"][11]["delete"] = True
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 8"][2]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 8"][3]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][102]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][103]["delete"] = True
        # Remove the Cornell-specific pickups and breakables with Reinhardt/Carrie equivalents and make said Reinhardt
        # and Carrie ones universal.
        patcher.scenes[Scenes.VILLA_FOYER].actor_lists["room 1"][49]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_FOYER].actor_lists["room 1"][56]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][105]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][117]["spawn_flags"] = 0
        # Make Renon's introduction cutscene trigger universal to everyone (including Henry).
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][10]["spawn_flags"] = 0
        # Remove the Henry-exclusive escape gates and Motorskellies on the maze's servant path.
        # We'll always be using the Cornell or Reinhardt/Carrie versions of these whenever applicable.
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][89]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][90]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][91]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][164]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][165]["delete"] = True
        # Make the Gardener's Stone Dogs universal for everyone (including Henry).
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][62]["spawn_flags"] ^= \
            ActorSpawnFlags.REINHARDT_AND_CARRIE | ActorSpawnFlags.CORNELL
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][63]["spawn_flags"] ^= \
            ActorSpawnFlags.REINHARDT_AND_CARRIE | ActorSpawnFlags.CORNELL

        # Make the final Cerberus in Villa Front Yard un-set the Villa entrance portcullis closed flag for all
        # characters (not just Henry).
        patcher.write_int32(0x35A4, 0x00000000, NIFiles.OVERLAY_CERBERUS)
        # Remove the start portcullis text spot since we're opening it for everyone.
        patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][2]["delete"] = True

        # Write the new Villa fountain puzzle order both in the code and Oldrey's Diary's description.
        patcher.write_bytes(0x4780, cvlod_string_to_bytearray(f"{slot_patch_info['fountain order'][0]} "
                                                               f"{slot_patch_info['fountain order'][1]} "
                                                               f"{slot_patch_info['fountain order'][2]} "
                                                               f"{slot_patch_info['fountain order'][3]}      "),
                            NIFiles.OVERLAY_PAUSE_MENU)
        patcher.write_byte(0x173, FOUNTAIN_LETTERS_TO_NUMBERS[slot_patch_info["fountain order"][0]],
                           NIFiles.OVERLAY_FOUNTAIN_PUZZLE)
        patcher.write_byte(0x16B, FOUNTAIN_LETTERS_TO_NUMBERS[slot_patch_info["fountain order"][1]],
                           NIFiles.OVERLAY_FOUNTAIN_PUZZLE)
        patcher.write_byte(0x163, FOUNTAIN_LETTERS_TO_NUMBERS[slot_patch_info["fountain order"][2]],
                           NIFiles.OVERLAY_FOUNTAIN_PUZZLE)
        patcher.write_byte(0x143, FOUNTAIN_LETTERS_TO_NUMBERS[slot_patch_info["fountain order"][3]],
                           NIFiles.OVERLAY_FOUNTAIN_PUZZLE)

        # Clear the Cornell-only setting from the JA Oldrey bedroom cutscene in the universal cutscene trigger settings
        # table so anyone will be allowed to trigger it. We'll simply remove the trigger actor if we don't want it.
        patcher.write_byte(0x11831D, 0x00)

        # Remove the JA Oldrey diary text spot for everyone and make the Reinhardt/Carrie version universal.
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][40]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][43]["delete"] = True
        # Turn the decorative Diary actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][37]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][37]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][37]["flag_id"] = 0
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][37]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.villala_archives_table].flag_id
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][37]["var_c"] = Pickups.OLDREYS_DIARY
        # Make the Garden Key pickup in the Archives universal to everyone.
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][38]["spawn_flags"] = 0

        # Move the following Locations that have flags shared with other Locations to their own flags.
        # Archives Garden Key
        patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 7"][38]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.villala_archives_rear].flag_id
        # Mary's Copper Key
        patcher.write_int16(0xAAA, CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id, NIFiles.OVERLAY_MARY)
        patcher.write_int16(0xAE2, CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id, NIFiles.OVERLAY_MARY)
        patcher.write_int16(0xB12, CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id, NIFiles.OVERLAY_MARY)

        # Give Child Henry his Cornell behaviors for everyone.
        patcher.write_int32(0x1B8, 0x24020002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU V0, R0, 0x0002
        patcher.write_byte(0x613, 0x04, NIFiles.OVERLAY_CHILD_HENRY)
        patcher.write_int32(0x844, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002
        patcher.write_int32(0x8B8, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002

        # Turn the Villa Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["execution_flags"] = 0
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["flag_id"] = 0
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.villam_child_de].flag_id
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["var_b"] = 0
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][81]["var_c"] = Pickups.ONE_HUNDRED_GOLD

        # Disable Gilles De Rais's hardcoded "Not Cornell?" check to see if he should despawn immediately upon spawning.
        # This should have REALLY been controlled instead by his settings in the actor list...
        patcher.write_byte(0x195, 0x00, NIFiles.OVERLAY_MALE_VAMPIRES)

        # Make the Cornell versions of the main maze front gates universal (the ones that have Henry escort checks on
        # them). We will not be using the Malus chases checks in the Reinhardt/Carrie versions of the main gates.
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][148]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][149]["delete"] = True
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][158]["spawn_flags"] = 0
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][159]["spawn_flags"] = 0
        # Apply the "not doing Henry escort" door checks to the two doors leading to the vampire crypt so he can't be
        # brought in there, and the "Henry nearby if doing escort" checks to the Reinhardt/Carrie versions of the maze
        # dividing doors.
        patcher.scenes[Scenes.VILLA_MAZE].doors[2]["door_flags"] |= DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.VILLA_MAZE].doors[2]["extra_condition_ptr"] = 0x802E4C34
        patcher.scenes[Scenes.VILLA_MAZE].doors[12]["door_flags"] |= DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.VILLA_MAZE].doors[12]["extra_condition_ptr"] = 0x802E4C34
        patcher.scenes[Scenes.VILLA_MAZE].doors[13]["door_flags"] |= DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.VILLA_MAZE].doors[13]["extra_condition_ptr"] = 0x802E4B9C
        patcher.scenes[Scenes.VILLA_MAZE].doors[16]["door_flags"] |= DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.VILLA_MAZE].doors[16]["extra_condition_ptr"] = 0x802E4B9C

        # Lock the Cornell maze front/rear dividing doors with the Rose Garden Key and update their text.
        # Keep the doors un-openable on the rear side.
        patcher.scenes[Scenes.VILLA_MAZE].scene_text.append(
            CVLoDSceneTextEntry(text="A sign saying:\n"
                                     " \"Rose Door\"\n"
                                     "\"Unlock from the front side.\"\n"
                                     "\"One key unlocks us all.\"🅰0/\n"
                                     "It is locked...🅰0/"))
        patcher.scenes[Scenes.VILLA_MAZE].scene_text.append(
            CVLoDSceneTextEntry(text="A click sounds from all\n"
                                     "Rose Garden Key doors.🅰0/"))
        patcher.scenes[Scenes.VILLA_FOYER].scene_text[10]["text"] = ("A door marked:\n"
                                                                     " \"Rose Door\"\n"
                                                                     "\"One key unlocks us all.\"\n"
                                                                     "It is locked...🅰0/")
        patcher.scenes[Scenes.VILLA_FOYER].scene_text[11]["text"] = ("A click sounds from all\n"
                                                                     "Rose Garden Key doors.🅰0/")
        patcher.scenes[Scenes.VILLA_MAZE].doors[23]["door_flags"] |= DoorFlags.ITEM_COST_IF_FLAG_UNSET
        patcher.scenes[Scenes.VILLA_MAZE].doors[23]["item_id"] = Items.ROSE_GARDEN_KEY
        patcher.scenes[Scenes.VILLA_MAZE].doors[23]["flag_id"] = 0x293
        patcher.scenes[Scenes.VILLA_MAZE].doors[23]["flag_locked_text_id"] = 24
        patcher.scenes[Scenes.VILLA_MAZE].doors[23]["unlocked_text_id"] = 25
        patcher.scenes[Scenes.VILLA_MAZE].doors[24]["door_flags"] |= DoorFlags.ITEM_COST_IF_FLAG_UNSET
        patcher.scenes[Scenes.VILLA_MAZE].doors[24]["item_id"] = Items.ROSE_GARDEN_KEY
        patcher.scenes[Scenes.VILLA_MAZE].doors[24]["flag_id"] = 0x293
        patcher.scenes[Scenes.VILLA_MAZE].doors[24]["flag_locked_text_id"] = 24
        patcher.scenes[Scenes.VILLA_MAZE].doors[24]["unlocked_text_id"] = 25

        # Remove the checks for the "unlocked Garden Key gate" and "spoke to Mary once" flags to have child Henry spawn.
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][65]["spawn_flags"] ^= ActorSpawnFlags.SPAWN_IF_FLAG_SET
        patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][65]["flag_id"] = 0
        patcher.write_int32(0x2CC4, 0x00000000, NIFiles.OVERLAY_CHILD_HENRY)

        # Make Mary say her congratulatory dialogue if spoken to for the first time only AFTER rescuing the maze kid
        # by setting the "spoke to Mary once" flag when the game gives the reward for doing the quest.
        mary_dialogue_check_location = patcher.get_decompressed_file_size(NIFiles.OVERLAY_MARY)
        patcher.write_int32(0xB0C, 0x0FC00000 | (mary_dialogue_check_location // 4), NIFiles.OVERLAY_MARY)
        patcher.write_int32s(mary_dialogue_check_location, [0x3C08801D,   # LUI   T0, 0x801D
                                                            0x9109AA6F,   # LBU   T1, 0xAA6F (T0)
                                                            0x35290004,   # ORI   T1, T1, 0x0004
                                                            0x03200008,   # JR    T9
                                                            0xA109AA6F],  # SB    T1, 0xAA6F (T0)
                             NIFiles.OVERLAY_MARY)

        # Make the hardcoded Villa coffin lid Henry checks never pass.
        patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_byte(0x1DB, 0x04)
        patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_byte(0x7DB, 0x04)
        # Make the hardcoded Cornell check in the Villa crypt Reinhardt/Carrie first vampire intro cutscene not pass.
        # IDK what KCEK was planning here, since Cornell normally never gets this cutscene, but if it passes the game
        # completely ceases functioning.
        patcher.write_int16(0x230, 0x1000, NIFiles.OVERLAY_CS_1ST_REIN_CARRIE_CRYPT_VAMPIRE)

        # Make Henry's Villa coffin loading zone universal while removing Reinhardt, Carrie, and Cornell's.
        patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["proxy"][17]["delete"] = True
        patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["proxy"][18]["delete"] = True
        patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["proxy"][19]["delete"] = True
        patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["proxy"][20]["spawn_flags"] = 0
        # Make the loading zone's hardcoded Henry check always pass if Villa Branching Paths is not One, or never pass
        # if it is One.
        if slot_patch_info["options"]["villa_branching_paths"] != VillaBranchingPaths.option_one:
            patcher.write_int32(0xD3A78, 0x000C0821)  # ADDU  AT, R0, T4
        else:
            patcher.write_int32(0xD3A78, 0x24010004)  # ADDIU AT, R0, 0x0004
        # Enable every Villa coffin destination also being able to set the spawn ID separately.
        patcher.write_int32s(0xD3AC8, [0x34190000,   # ORI  T9, R0, 0x0000
                                       0xAFB90028])  # SW   T9, 0x0028 (SP)
        patcher.write_int32s(0xD3B44, [0x34190000,   # ORI  T9, R0, 0x0000
                                       0xAFB90028])  # SW   T9, 0x0028 (SP)
        patcher.write_int32s(0xD3BA0, [0x34190000,   # ORI  T9, R0, 0x0000
                                       0xAFB90028])  # SW   T9, 0x0028 (SP)
        # If the Villa Branching Paths option is Two, change the coffin loading zone behavior to instead send to one of
        # two places depending on whether it's night (between 0:00-5:59 or 18:00-23:59) or day (between 6:00-17:59).
        if slot_patch_info["options"]["villa_branching_paths"] == VillaBranchingPaths.option_two:
            patcher.write_byte(0xD3AAF, 0x06)
            patcher.write_byte(0xD3B07, 0x06)
            patcher.write_int16(0xD3B0A, 0xFFEA)
            patcher.write_byte(0xD3B13, 0x12)
            patcher.write_int16(0xD3B16, 0xFFE7)

        # Generate Mary's item text here, if her Location is created.
        mary_item_text = ""
        if CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id in loc_text:
            # If it's a local Item she has, have her say she will give it to you.
            if not loc_text[CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id][1]:
                mary_item_text = f"give you this {loc_text[CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id][0]}"
            # Otherwise, have her say she will send it to [player].
            else:
                mary_item_text = (f"send this {loc_text[CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id][0]} to "
                                  f"{loc_text[CVLOD_LOCATIONS_INFO[loc_names.villala_mary].flag_id][1]}")


        # Depending on whom the maze kid is, change some more things appropriately.
        if slot_patch_info["options"]["villa_maze_kid"] == VillaMazeKid.option_malus:
            # Rewrite all of Mary's dialogue to reflect Malus being the kid in the maze.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[31]["text"] = (
                cvlod_text_wrap("⬘1/Mary:\n"
                                "Thank you so much for\n"
                                "teaching that man a lesson!\n"
                                "May I ask another favor?🅰0/\f"
                                "There's a naughty boy causing\n"
                                "mischief in the maze!🅰30/ A real\n"
                                "wicked child, you could say!🅰0/\f"
                                f"Send him packing and I will {mary_item_text}.🅰0/\f"
                                "This boy's hair is dark purple.\n"
                                "Now, get to it!🅰0/"))
            patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[32]["text"] = (
                "⬘1/Mary:\n"
                "Where was he last sighted\n"
                "in the maze?⏸30/"
                "That's a good question.🅰0/\f"
                "I know there's one particular\n"
                "bush that he loves to hide in.\n"
                "First left from the main🅰0/\n"
                "entrance. You're likely to find\n"
                "him there.🅰0/\f"
                "Be careful! Looks can be\n"
                "deceiving. Don't be fooled by\n"
                "his innocent demeanor!🅰0/\f"
                "Again, his hair is dark purple.\n"
                "You'll know him when you see\n"
                "him. Good luck!🅰0/")
            patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[33]["text"] = (
                cvlod_text_wrap("⬘1/Mary:\n"
                                "That little rascal has left?⏸30/"
                                "Oh, thank goodness!🅰0/\f"
                                "Coller will be very thrilled\n"
                                "to know he'll no longer have\n"
                                "to clean toilet paper messes!🅰0/\f"
                                f"As promised, I {mary_item_text}.\n"
                                "I hope it serves you well.🅰0/\f"
                                "Thanks for your help, young\n"
                                "stranger!🅰0/"))
            patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[34]["text"] = (
                "⬘1/Mary:\n"
                "Of course, who's to say\n"
                "he won't just return later\n"
                "to cause more mischief?🅰0/\f"
                "I should've requested you drag\n"
                "him to the Ferryman and had\n"
                "him deal with it! Dammit...🅰0/\f"
                "We shall deal with it when\n"
                "it happens, I suppose...🅰0/")

            # Have Mary check for the Malus chase end cutscene flag instead of the Henry rescued flag.
            patcher.write_byte(0xAD3, 0x92, NIFiles.OVERLAY_MARY)
            patcher.write_byte(0xB43, 0x92, NIFiles.OVERLAY_MARY)

            # The Gardener will have his Reinhardt/Carrie behavior for everyone.
            patcher.write_int32(0x490, 0x24020000, NIFiles.OVERLAY_GARDENER)   # ADDIU V0, R0, 0x0000
            patcher.write_int32(0xD14, 0x34190000, NIFiles.OVERLAY_GARDENER)   # ORI   T9, R0, 0x0000
            patcher.write_int32(0x13C0, 0x34090000, NIFiles.OVERLAY_GARDENER)  # ORI   T1, R0, 0x0000

            # Malus and his associated triggers are present, Henry is not.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["init"][1]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["init"][2]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["init"][10]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][61]["spawn_flags"] ^= \
                ActorSpawnFlags.REINHARDT_AND_CARRIE
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][65]["delete"] = True

            # The servant path escape gates are their Reinhardt/Carrie versions that specify Malus escaped through them,
            # and the maze end door is the Reinhardt/Carrie one that the Malus rescued cutscene specifically opens.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][144]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][145]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][153]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][154]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][155]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][163]["delete"] = True
        else:
            # Edit some of Mary's existing dialogue if Henry is the kid in the maze.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[31]["text"] = (
                cvlod_text_wrap("⬘1/Mary:\n"
                                "Thank you so much for\n"
                                "teaching that man a lesson!\n"
                                "May I ask another favor?🅰0/\f"
                                "My son Henry is trapped\n"
                                "in the maze! He must be\n"
                                "absolutely terrified...🅰0/\f"
                                f"Escort him out safely and I will {mary_item_text}.🅰0/\f"
                                "I'm so worried about him...\n"
                                "Please make sure he gets out!\n"
                                "It's not safe here anymore!🅰0/"))
            patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[33]["text"] = (
                patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[33]["text"][:146] +
                cvlod_text_wrap(f"As promised, I {mary_item_text}.\n"
                                "I hope it serves you well.🅰0/\f") +
                patcher.scenes[Scenes.VILLA_LIVING_AREA].scene_text[33]["text"][219:279])

            # The Reinhardt/Carrie version of the maze dividing door near the kid starting point will unlock upon Henry
            # escort beginning instead of Malus chase beginning.
            patcher.scenes[Scenes.VILLA_MAZE].doors[16]["flag_id"] = 0x93

            # The Gardener will have his Cornell behavior for everyone.
            patcher.write_int32(0x490, 0x24020002, NIFiles.OVERLAY_GARDENER)   # ADDIU V0, R0, 0x0002
            patcher.write_int32(0xD14, 0x34190002, NIFiles.OVERLAY_GARDENER)   # ORI   T9, R0, 0x0002
            patcher.write_int32(0x13C0, 0x34090002, NIFiles.OVERLAY_GARDENER)  # ORI   T1, R0, 0x0002

            # Henry and his associated triggers are present, Malus is not.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["init"][1]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["init"][2]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["init"][10]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][61]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][65]["spawn_flags"] ^= ActorSpawnFlags.CORNELL

            # The servant path escape gates are their Cornell versions that specify Henry escaped through them, and the
            # maze end door is the Cornell one that the Henry rescued cutscene specifically opens AND includes a
            # "Henry nearby if doing escort" check.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][144]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][145]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][153]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][154]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][155]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][163]["spawn_flags"] = 0


        # If the Villa State is Reinhardt/Carrie's, put the stage in Reinhardt and Carrie's state for everyone.
        if slot_patch_info["options"]["villa_state"] == VillaState.option_reinhardt_carrie:
            # The fountain puzzle does not exist.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][20]["delete"] = True
            # The fountain top shine and special text spot do not exist.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][19]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][68]["delete"] = True
            # Headstone text spots are Reinhardt/Carrie's.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][3]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][4]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][5]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][6]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][69]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][70]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][71]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][72]["delete"] = True
            # The text spots for the fountain flavor text and pillar rising at midnight hint exist, whereas the one for
            # the headstone puzzle does not.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][7]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][16]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][17]["delete"] = True
            # The fountain pillar is on its Reinhardt/Carrie check behavior for everyone (raises at midnight).
            patcher.write_int32(0xD77E0, 0x24030000)  # ADDIU V1, R0, 0x0000
            patcher.write_int32(0xD7A60, 0x24030000)  # ADDIU V1, R0, 0x0000

            # The servant door in the foyer is locked from one side. The rose garden double doors are normal.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][15]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][16]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][17]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][18]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][19]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][20]["delete"] = True
            # The 3AM Rosa cutscene exists. The 6AM rose patch does not.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][7]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x2F4, 0x240E0000)  # ADDIU T6, R0, 0x0000
            # All roses are red.
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x164, 0x34090000)  # ORI   T1, R0, 0x0000
            # The servant door AND center rose garden text spots both exist.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][9]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][11]["spawn_flags"] = 0
            # The foyer vampire that spawns is the Reinhardt/Carrie one.
            patcher.write_int32(0x320, 0x34020000, NIFiles.OVERLAY_CS_VILLA_FOYER_VAMPIRE)  # ORI  V0, R0, 0x0000

            # The Vincent introduction and vampire villager cutscenes exist. The JA Oldrey bedroom cutscene does not.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][11]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][12]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][13]["delete"] = True
            # Vincent is present. Mary and her associated table pickup are absent.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 2"][34]["spawn_flags"] ^= \
                ActorSpawnFlags.REINHARDT_AND_CARRIE
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 4"][28]["delete"] = True
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 4"][29]["delete"] = True
            # The roses in the dining room vase are red and the falling one is present.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].write_ovl_int32(0x5E8, 0x340F0000)  # ORI  T7, R0, 0x0000
            patcher.scenes[Scenes.VILLA_LIVING_AREA].write_ovl_int32(0xA4, 0x340E0000)  # ORI  T6, R0, 0x0000

            # None of the Cornell enemies are present in the maze.
            for enemy_index in VILLA_MAZE_CORNELL_ENEMY_INDEXES:
                patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][enemy_index]["delete"] = True
            # The servant entrance gates are locked by Garden Key like the main gate.
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["door_flags"] |= DoorFlags.LOCKED_BY_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["item_id"] = Items.GARDEN_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["flag_id"] = 0x295  # Garden gate unlocked flag
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["flag_locked_text_id"] = 12
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["unlocked_text_id"] = 11
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["door_flags"] |= DoorFlags.LOCKED_BY_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["item_id"] = Items.GARDEN_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["flag_id"] = 0x295  # Garden gate unlocked flag
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["flag_locked_text_id"] = 12
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["unlocked_text_id"] = 11
            # Text clarifying that using the key on one pair of gates unlocked the other.
            patcher.scenes[Scenes.VILLA_MAZE].scene_text[12]["text"] = \
                (patcher.scenes[Scenes.VILLA_MAZE].scene_text[12]["text"][:33] + "\n\"One key unlocks both.\"\n" +
                 patcher.scenes[Scenes.VILLA_MAZE].scene_text[12]["text"][35:])
            patcher.scenes[Scenes.VILLA_MAZE].scene_text[11]["text"] = ("A click sounds from\n"
                                                                        "both sets of\n"
                                                                        "Garden Key gates...🅰0/")
            # The Iron Thorn Fence gate is unlocked.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][146]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][147]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][156]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][157]["delete"] = True
            # The maze center and side dividing doors are locked from the rear side.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][150]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][152]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][160]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][162]["delete"] = True
            # The crypt door is unlocked and the crest display spot is absent.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][60]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][151]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][161]["delete"] = True
            # The breakables for Rear Viewing Platform Rear, Malus Hole Dead End, and Small Alcove Left do not exist.
            # and Small Alcove Right, Rear Viewing Platform Front, and Front Viewing Platform do.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][104]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][106]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][142]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][109]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][122]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][126]["spawn_flags"] = 0

            # Gilles De Rais is not present in the crypt. The vampire couple are.
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][0]["delete"] = True
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][2]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][3]["spawn_flags"] = 0
            # The hardcoded Villa coffin lid Not Cornell attack collision check will always pass.
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32(0x970, 0x340E0000)  # ORI T6, R0, 0x0000
            # The hardcoded Villa coffin lid Not Cornell cutscene check will always pass.
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32(0xD68, 0x34190000)  # ORI T9, R0, 0x0000
        # If the Villa State is Cornell's, put the stage in Cornell's state for everyone.
        elif slot_patch_info["options"]["villa_state"] == VillaState.option_cornell:
            # The fountain puzzle exists.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][20]["spawn_flags"] = 0
            # The fountain top shine and special text spot exist.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][19]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][68]["spawn_flags"] = 0
            # Headstone text spots are Cornell's.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][3]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][4]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][5]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][6]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][69]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][70]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][71]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][72]["spawn_flags"] = 0
            # The text spots for the fountain flavor text and pillar rising at midnight hint do not exist, whereas the
            # one for the headstone puzzle does.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][7]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][16]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][17]["spawn_flags"] = 0
            # The fountain pillar is on its Cornell check behavior for everyone (raises after solving the puzzle).
            patcher.write_int32(0xD77E0, 0x24030002)  # ADDIU V1, R0, 0x0002
            patcher.write_int32(0xD7A60, 0x24030002)  # ADDIU V1, R0, 0x0002

            # The servant door in the foyer is normal. The rose garden double doors are locked by Rose Garden Key.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][15]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][16]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][17]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][18]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][19]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][20]["spawn_flags"] = 0
            # The 3AM Rosa cutscene does not exist. The 6AM rose patch does.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][7]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x2F4, 0x240E0002)  # ADDIU T6, R0, 0x0002
            # All roses are white.
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x164, 0x34090002)  # ORI   T1, R0, 0x0002
            # Neither the servant door NOR center rose garden text spots exist.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][9]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][11]["delete"] = True
            # The foyer vampire that spawns is the Cornell one.
            patcher.write_int32(0x320, 0x34020002, NIFiles.OVERLAY_CS_VILLA_FOYER_VAMPIRE)  # ORI  V0, R0, 0x0002

            # The Vincent introduction and vampire villager cutscenes don't exist. The JA Oldrey bedroom cutscene does.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][11]["delete"] = True
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][12]["delete"] = True
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][13]["spawn_flags"] = 0
            # Vincent is absent. Mary and her associated table pickup are present.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 2"][34]["delete"] = True
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 4"][28]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 4"][29]["spawn_flags"] = 0
            # The roses in the dining room vase are white and the falling one is absent.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].write_ovl_int32(0x5E8, 0x340F0002)  # ORI  T7, R0, 0x0002
            patcher.scenes[Scenes.VILLA_LIVING_AREA].write_ovl_int32(0xA4, 0x340E0002)  # ORI  T6, R0, 0x0002

            # The servant entrance gates are left unchanged.
            # All the Cornell enemies are present in the maze.
            for enemy_index in VILLA_MAZE_CORNELL_ENEMY_INDEXES:
                patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][enemy_index]["spawn_flags"] &= \
                    ActorSpawnFlags.NO_CHARACTERS
            # The Iron Thorn Fence gate is locked by Thorn Key.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][146]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][147]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][156]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][157]["spawn_flags"] = 0
            # The maze center and side dividing doors are locked from the front side.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][150]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][152]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][160]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][162]["spawn_flags"] = 0
            # The crypt door is locked by the two crest halves and the crest display spot is present.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][60]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][151]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][161]["spawn_flags"] = 0
            # The breakables for Rear Viewing Platform Rear, Malus Hole Dead End, and Small Alcove Left exist.
            # and Small Alcove Right, Rear Viewing Platform Front, and Front Viewing Platform do not.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][104]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][106]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][142]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][109]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][122]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][126]["delete"] = True

            # Lock the crypt door from the inside if the player doesn't have the two crests on-hand and/or inserted.
            patcher.scenes[Scenes.VILLA_CRYPT].scene_text.append(
                CVLoDSceneTextEntry(text="The entrance door is sealed\n"
                                         "shut! You'll need to bring it\n"
                                         "both Crest Halves to see the\n"
                                         "light of day...🅰0/"))
            crypt_crests_check_location = len(patcher.scenes[Scenes.VILLA_CRYPT].overlay)
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32s(crypt_crests_check_location,
                                                                patches.crypt_crests_checker)
            patcher.scenes[Scenes.VILLA_CRYPT].doors[0]["door_flags"] = DoorFlags.EXTRA_CHECK_FUNC_ENABLED
            patcher.scenes[Scenes.VILLA_CRYPT].doors[0]["extra_condition_ptr"] = \
                crypt_crests_check_location + SCENE_OVERLAY_RDRAM_START
            patcher.scenes[Scenes.VILLA_CRYPT].doors[0]["flag_locked_text_id"] = 1
            # Gilles De Rais is present in the crypt. The vampire couple are not.
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][0]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][2]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][3]["delete"] = True
            # The hardcoded Villa coffin lid Not Cornell attack collision check will never pass.
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32(0x970, 0x340E0002)  # ORI T6, R0, 0x0002
            # The hardcoded Villa coffin lid Not Cornell cutscene check will never pass.
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32(0xD68, 0x34190002)  # ORI T9, R0, 0x0002
        # Otherwise, if Hybrid was chosen, put the stage in a hybrid state for everyone.
        else:
            # The fountain puzzle exists.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][20]["spawn_flags"] = 0
            # The fountain top shine and special text spot exist.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][19]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][68]["spawn_flags"] = 0
            # Headstone text spots are Cornell's.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][3]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][4]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][5]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][6]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][69]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][70]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][71]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["proxy"][72]["spawn_flags"] = 0
            # The text spots for the fountain flavor text and pillar rising at midnight hint do not exist, whereas the
            # one for the headstone puzzle does.
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][7]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][16]["delete"] = True
            patcher.scenes[Scenes.VILLA_FRONT_YARD].actor_lists["init"][17]["spawn_flags"] = 0
            # The fountain pillar is on its Cornell check behavior for everyone (raises after solving the puzzle).
            patcher.write_int32(0xD77E0, 0x24030002)  # ADDIU V1, R0, 0x0002
            patcher.write_int32(0xD7A60, 0x24030002)  # ADDIU V1, R0, 0x0002

            # The servant door in the foyer is normal. The rose garden double doors are locked by Rose Garden Key.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][15]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][16]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][17]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][18]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][19]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["proxy"][20]["spawn_flags"] = 0
            # The 3AM Rosa cutscene AND 6AM rose patch both exist.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][7]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x2F4, 0x240E0002)  # ADDIU T6, R0, 0x0002
            # The outer perimeter roses are red, while the center pillar roses are white.
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_byte(0x16B, 0x24)
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int16(0x170, 0x5423)
            # Neither the servant door NOR center rose garden text spots exist.
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][9]["delete"] = True
            patcher.scenes[Scenes.VILLA_FOYER].actor_lists["init"][11]["delete"] = True
            # The foyer vampire that spawns is the Cornell one.
            patcher.write_int32(0x320, 0x34020002, NIFiles.OVERLAY_CS_VILLA_FOYER_VAMPIRE)  # ORI  V0, R0, 0x0002

            # The Vincent introduction, vampire villager, AND JA Oldrey bedroom cutscenes all exist.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][11]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][12]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["init"][13]["spawn_flags"] = 0
            # Mary AND Vincent are both present.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 2"][34]["spawn_flags"] ^= \
                ActorSpawnFlags.REINHARDT_AND_CARRIE
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 4"][28]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_LIVING_AREA].actor_lists["room 4"][29]["spawn_flags"] = 0
            # The roses in the dining room vase are red and the falling one is present.
            patcher.scenes[Scenes.VILLA_LIVING_AREA].write_ovl_int32(0x5E8, 0x340F0000)  # ORI  T7, R0, 0x0000
            patcher.scenes[Scenes.VILLA_LIVING_AREA].write_ovl_int32(0xA4, 0x340E0000)  # ORI  T6, R0, 0x0000

            # The servant entrance gates are locked by Garden Key like the main gate.
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["door_flags"] |= DoorFlags.LOCKED_BY_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["item_id"] = Items.GARDEN_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["flag_id"] = 0x295  # Garden gate unlocked flag
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["flag_locked_text_id"] = 12
            patcher.scenes[Scenes.VILLA_MAZE].doors[10]["unlocked_text_id"] = 11
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["door_flags"] |= DoorFlags.LOCKED_BY_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["item_id"] = Items.GARDEN_KEY
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["flag_id"] = 0x295  # Garden gate unlocked flag
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["flag_locked_text_id"] = 12
            patcher.scenes[Scenes.VILLA_MAZE].doors[11]["unlocked_text_id"] = 11
            # Text clarifying that using the key on one pair of gates unlocked the other.
            patcher.scenes[Scenes.VILLA_MAZE].scene_text[12]["text"] = \
                (patcher.scenes[Scenes.VILLA_MAZE].scene_text[12]["text"][:33] + "\n\"One key unlocks both.\"\n" +
                 patcher.scenes[Scenes.VILLA_MAZE].scene_text[12]["text"][35:])
            patcher.scenes[Scenes.VILLA_MAZE].scene_text[11]["text"] = ("A click sounds from\n"
                                                                        "both sets of\n"
                                                                        "Garden Key gates...🅰0/")
            # All the Cornell enemies are present in the maze.
            for enemy_index in VILLA_MAZE_CORNELL_ENEMY_INDEXES:
                patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][enemy_index]["spawn_flags"] &= \
                    ActorSpawnFlags.NO_CHARACTERS
            # The Iron Thorn Fence gate is locked by Thorn Key.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][146]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][147]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][156]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][157]["spawn_flags"] = 0
            # The maze center and side dividing doors are locked from the front side.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][150]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][152]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][160]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][162]["spawn_flags"] = 0
            # The crypt door is locked by the two crest halves and the crest display spot is present.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][60]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][151]["delete"] = True
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][161]["spawn_flags"] = 0
            # The breakables for Rear Viewing Platform Rear, Malus Hole Dead End, Small Alcove Right,
            # Rear Viewing Platform Front, Front Viewing Platform, and Small Alcove Left ALL exist.
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][104]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][106]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][109]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][122]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][126]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_MAZE].actor_lists["proxy"][142]["spawn_flags"] = 0

            # Lock the crypt door from the inside if the player doesn't have the two crests on-hand and/or inserted.
            patcher.scenes[Scenes.VILLA_CRYPT].scene_text.append(
                CVLoDSceneTextEntry(text="The entrance door is sealed\n"
                                         "shut! You'll need to bring it\n"
                                         "both Crest Halves to see the\n"
                                         "light of day.🅰0/"))
            crypt_crests_check_location = len(patcher.scenes[Scenes.VILLA_CRYPT].overlay)
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32s(crypt_crests_check_location,
                                                                patches.crypt_crests_checker)
            patcher.scenes[Scenes.VILLA_CRYPT].doors[0]["door_flags"] = DoorFlags.EXTRA_CHECK_FUNC_ENABLED
            patcher.scenes[Scenes.VILLA_CRYPT].doors[0]["extra_condition_ptr"] = \
                crypt_crests_check_location + SCENE_OVERLAY_RDRAM_START
            patcher.scenes[Scenes.VILLA_CRYPT].doors[0]["flag_locked_text_id"] = 1
            # Gilles De Rais AND the vampire couple are all present, and the latter will be fought after the former.
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][0]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][2]["spawn_flags"] = 0
            patcher.scenes[Scenes.VILLA_CRYPT].actor_lists["init"][3]["spawn_flags"] = 0
            # The hardcoded Villa coffin lid Not Cornell attack collision check will never pass.
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32(0x970, 0x340E0002)  # ORI T6, R0, 0x0002
            # The hardcoded Villa coffin lid Not Cornell cutscene check will always pass.
            patcher.scenes[Scenes.VILLA_CRYPT].write_ovl_int32(0xD68, 0x34190000)  # ORI T9, R0, 0x0000


        # # # # # # # # #
        # TUNNEL EDITS  #
        # # # # # # # # #
        # Make the Tunnel gondolas check for the Spider Women cutscene like they do in CV64.
        gondola_hack_start = len(patcher.scenes[Scenes.TUNNEL].overlay)
        patcher.scenes[Scenes.TUNNEL].write_ovl_int32(
            0x7BC, 0x0C0B0000 | ((gondola_hack_start + (SCENE_OVERLAY_RDRAM_START & 0xFFFFFF)) // 4))
        patcher.scenes[Scenes.TUNNEL].write_ovl_int32s(gondola_hack_start, patches.gondola_spider_cutscene_checker)
        # If Skip Gondolas is on, extend the above hack to also make the gondola teleport the player when stepped on.
        if slot_patch_info["options"]["skip_gondolas"]:
            patcher.scenes[Scenes.TUNNEL].write_ovl_int32s(len(patcher.scenes[Scenes.TUNNEL].overlay) - 8,
                                                           patches.gondola_skipper)
            # Spawn coordinates for the new gondola entrances.
            patcher.scenes[Scenes.TUNNEL].spawn_spots += [
                CVLoDSpawnEntranceEntry(room_id=0, player_x_pos=1047, player_y_pos=272, player_z_pos=-2136,
                                        player_rotation=-16384, camera_x_pos=1048, camera_y_pos=296, camera_z_pos=-2181,
                                        focus_x_pos=1047, focus_y_pos=287, focus_z_pos=-2136),
                CVLoDSpawnEntranceEntry(room_id=0, player_x_pos=563, player_y_pos=272, player_z_pos=-748,
                                        player_rotation=0, camera_x_pos=518, camera_y_pos=296, camera_z_pos=-747,
                                        focus_x_pos=563, focus_y_pos=287, focus_z_pos=-748),
            ]
            # Move the candle at the gondola transfer point to be near the red gondola instead.
            patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][163]["x_pos"] = 1063.0
            patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][163]["y_pos"] = 272.0
            patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][163]["z_pos"] = -2144.0
            # Remove all enemies that would spawn only while the "gondolas in motion" flag (0xB4) is set.
            for actor in patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"]:
                if actor["spawn_flags"] & ActorSpawnFlags.SPAWN_IF_FLAG_SET and actor["flag_id"] == 0xB4:
                    actor["delete"] = True

        # Turn the Tunnel Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["spawn_flags"] = 0
        patcher.scenes[Scenes.TUNNEL].actor_lists["proxy"][131]["object_id"] = Objects.INTERACTABLE
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
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["execution_flags"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["flag_id"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.uw_waterfall_child].flag_id
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["var_b"] = 0
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["var_c"] = Pickups.ONE_HUNDRED_GOLD
        patcher.scenes[Scenes.WATERWAY].actor_lists["proxy"][70]["extra_condition_ptr"] = 0

        # Set the Waterway end zone destination ID to the ID for the decoupled Medusa arena.
        patcher.scenes[Scenes.WATERWAY].loading_zones[0]["spawn_id"] |= 0x80

        # If Skip Waterway Blocks is on, add the second switch's "pressed" flag to the starting flags list.
        if slot_patch_info["options"]["skip_waterway_blocks"]:
            starting_flags += [0xDB]

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
        # Change their spawn IDs to both go to the Fan Meeting Room in our custom pre-Castle Center state for it.
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].loading_zones[1]["spawn_id"] = 0x40
        patcher.scenes[Scenes.ALGENIE_MEDUSA_ARENA].loading_zones[3]["spawn_id"] = 0x40


        # # # # # # # # # # # # # #
        # FAN MEETING ROOM EDITS  #
        # # # # # # # # # # # # # #
        # Add Castle Center start's stage name display actor to the fan meeting room and set it up to only spawn on our
        # setup for the start of Castle Center. The "beginning of stage" state should be saved upon entering here.
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["init"].append(
            CVLoDNormalActorEntry(spawn_flags=ActorSpawnFlags.SPAWN_IF_FLAG_SET, status_flags=0, x_pos=0.0, y_pos=0.0,
                                  z_pos=0.0, execution_flags=ObjectExecutionFlags.TLB_MAP_OVERLAY,
                                  object_id=Objects.STAGE_NAME_DISPLAY, flag_id=0x2A1, var_a=0, var_b=0,
                                  var_c=5, var_d=0, extra_condition_ptr=0))

        # Remove the first actor in the proxy list, which is a sliding door actor likely put there by mistake. It's a
        # duplicate of another Reinhardt/Carrie/Cornell-only always-open sliding door in the same position on the far
        # side of the room with the same parameters, causes some ugly Z-fighting when paired with Henry's always-closed
        # far side door, and is separated from the rest of the sliding doors in the list which are all together.
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][0]["delete"] = True

        # Make Cornell's nearside sliding door universal and remove Reinhardt/Carrie's and Henry's instances
        # (the door will start closed and remain closed no matter what).
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][9]["delete"] = True
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][11]["spawn_flags"] = 0
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][12]["delete"] = True
        # Make Reinhardt/Carrie/Cornell's farside sliding door universal and remove Henry's.
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][10]["spawn_flags"] = 0
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][13]["delete"] = True
        # Make all loading zones character-universal and instead set each one up to only spawn with certain scene
        # setup flags.
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][14]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET  # Reinhardt/Carrie/Henry nearside (normally to Medusa/Algenie arena)
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][14]["flag_id"] = 0x2A1
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][15]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET  # Reinhardt/Carrie/Henry farside (normally to Castle Center)
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][15]["flag_id"] = 0x2A1
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][16]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET  # Cornell farside (normally to Art Tower)
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][16]["flag_id"] = 0x2A3

        # Make Henry's teleport jewel universal for everyone and only spawn when the 0x2A3 flag is set
        # (our dedicated alternate setup one for post-Outer Wall).
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][8]["spawn_flags"] = \
            ActorSpawnFlags.SPAWN_IF_FLAG_SET
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][8]["flag_id"] = 0x2A3
        # Move the teleport jewel to be close to the center spotlight instead of close to the farside door.
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][8]["x_pos"] = 25.0
        patcher.scenes[Scenes.FAN_MEETING_ROOM].actor_lists["proxy"][8]["z_pos"] = 25.0
        # Make the teleport jewel send the player to the start of the Outer Wall rooftop slide instead of to the
        # Villa crypt.
        patcher.write_bytes(0x112FBC, [Scenes.THE_OUTER_WALL, 0x0E])


        # # # # # # # # # # # # #
        # THE OUTER WALL EDITS  #
        # # # # # # # # # # # # #
        # Turn the Outer Wall Henry child actor into a freestanding pickup check with all necessary parameters assigned.
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["spawn_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["execution_flags"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["flag_id"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.towse_child].flag_id
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["var_b"] = 0
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["var_c"] = Pickups.ONE_HUNDRED_GOLD
        patcher.scenes[Scenes.THE_OUTER_WALL].actor_lists["proxy"][41]["extra_condition_ptr"] = 0

        # Make the Harpy arena loading zone send you to the Fan Meeting Room in our custom post-Outer Wall state.
        patcher.scenes[Scenes.THE_OUTER_WALL].loading_zones[10]["spawn_id"] = 0xC1

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
        # Make the Art Tower start loading zone send you to the Fan Meeting Room in our custom post-Outer Wall state.
        patcher.scenes[Scenes.ART_TOWER_MUSEUM].loading_zones[0]["spawn_id"] = 0xC2

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
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][14]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][14]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccb_mandrag_shelf_r].flag_id
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][14]["var_c"] = Pickups.MANDRAGORA
        # Mandragora shelf left
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["x_pos"] = -4.0
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccb_mandrag_shelf_l].flag_id
        patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["room 0"][15]["var_c"] = Pickups.MANDRAGORA
        # Nitro shelf Heinrich side
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["x_pos"] = -320.0
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_shelf_h].flag_id
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["var_b"] = 0
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][3]["var_c"] = Pickups.MAGICAL_NITRO
        # Nitro shelf invention side
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["x_pos"] = -306.0
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["object_id"] = Objects.INTERACTABLE
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["var_a"] = \
            CVLOD_LOCATIONS_INFO[loc_names.ccia_nitro_shelf_i].flag_id
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["var_b"] = 0
        patcher.scenes[Scenes.CASTLE_CENTER_INVENTIONS].actor_lists["room 4"][6]["var_c"] = Pickups.MAGICAL_NITRO

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
        # Otherwise, if Camilla was chosen for the post-Behemoth boss, delete the trigger for Rosa's battle intro
        # cutscene and make Camilla's universal for everyone.
        else:
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][5]["delete"] = True
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].actor_lists["init"][6]["spawn_flags"] ^= \
                ActorSpawnFlags.CARRIE

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

        # Prevent vampires from despawning if we have Nitro, so they'll never not spawn and crash the Villa cutscenes.
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
        # Clear the Cornell-only setting from the Giant Werewolf boss intro cutscene in the universal cutscene trigger
        # settings table so anyone will be allowed to trigger it. Just like with the Castle Center bosses, we'll instead
        # rely entirely on the actor system to ensure the trigger only spawns for the correct characters.
        patcher.write_byte(0x118349, 0x00)
        # Make specific changes depending on what was chosen for the Duel Tower Final Boss.
        # If Giant Werewolf was chosen, prevent the hardcoded Not Cornell checks on Arena 4 from passing for non-Cornell
        # characters and make the Giant Werewolf cutscene trigger universal to everyone.
        if slot_patch_info["options"]["duel_tower_final_boss"] == DuelTowerFinalBoss.option_giant_werewolf:
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x58D0, 0x00000000)  # NOP
            patcher.scenes[Scenes.DUEL_TOWER].actor_lists["init"][2]["spawn_flags"] = 0
            # Prevent the ceiling from falling in Arena 4 for everyone.
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x1A5C, 0x340D0002)  # ORI T5, R0, 0x0002
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(0x5B4C, 0x340E0002)  # ORI T6, R0, 0x0002
        # Otherwise, if Were-Tiger was chosen, make the hardcoded Not Cornell checks on Arena 4 pass even for Cornell
        # and delete the Giant Werewolf cutscene trigger actor entirely.
        else:
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
        if CVLOD_LOCATIONS_INFO[loc_names.tosor_super_1].flag_id in loc_values:
            patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(
                0x5400, loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_1].flag_id][0])
            patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(
                0x5402, loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_2].flag_id][0])
            patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(
                0x5404, loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_3].flag_id][0])
            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla:
                if not loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_1].flag_id][1]:
                    patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(0x70C0 + (4 * 0) + 2,
                                                                            PickupFlags.GRAVITY|PickupFlags.INVISIBLE)
                if not loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_2].flag_id][1]:
                    patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(0x70C0 + (4 * 1) + 2,
                                                                            PickupFlags.GRAVITY|PickupFlags.INVISIBLE)
                if not loc_values[CVLOD_LOCATIONS_INFO[loc_names.tosor_super_3].flag_id][1]:
                    patcher.scenes[Scenes.TOWER_OF_SORCERY].write_ovl_int16(0x70C0 + (4 * 2) + 2,
                                                                            PickupFlags.GRAVITY|PickupFlags.INVISIBLE)

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
        else:
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][35]["delete"] = True    # Reinhardt (Death)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][38]["delete"] = True    # Carrie (Actrise)
            patcher.scenes[Scenes.ROOM_OF_CLOCKS].actor_lists["proxy"][41]["spawn_flags"] = 0  # Cornell (Ortega)

        # Remove the artificial nerf on Actrise when playing as Reinhardt. This is likely a leftover from the playable
        # TGS 1998 CV64 demo wherein players could battle Actrise as Reinhardt.
        patcher.write_int32(0x858, 0x340E0001, NIFiles.OVERLAY_ACTRISE)  # ORI  T6, R0, 0x0001

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
        # Make the Normal difficulty 3HB in the Abyss scene drop a fourth pickup.
        # The 3HB pickups array for the scene conveniently has an unused entry between the Normal and Hard drops.
        patcher.scenes[Scenes.CLOCK_TOWER_ABYSS].three_hit_breakables[1]["pickup_count"] = 4

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

        # Prevent Dracula's doors from opening if the required amount of the goal item (Special2 normally) is not found.
        drac_door_check_start = len(patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].overlay)
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].doors[0]["door_flags"] = DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].doors[0]["extra_condition_ptr"] = \
            drac_door_check_start + SCENE_OVERLAY_RDRAM_START
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].doors[0]["flag_locked_text_id"] = 0
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].doors[1]["door_flags"] = DoorFlags.EXTRA_CHECK_FUNC_ENABLED
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].doors[1]["extra_condition_ptr"] = \
            drac_door_check_start + SCENE_OVERLAY_RDRAM_START
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].doors[1]["flag_locked_text_id"] = 0
        patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int32s(drac_door_check_start,
                                                                     patches.drac_condition_checker)
        # Write different option values and door messages and name the Special2 differently depending on what
        # Dracula's Condition is. The option values will be written to both the door check and the Dracula special
        # sound notif check.
        if slot_patch_info["options"]["draculas_condition"] == DraculasCondition.option_crystal:
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].scene_text[0]["text"] = ("The door is sealed\n"
                                                                                 "by a crystalline force...🅰0/\f"
                                                                                 "You'll need the power\n"
                                                                                 "of the big crystal in\n"
                                                                                 "Castle Center's basement\n"
                                                                                 "to undo the seal.🅰0/")
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int16(drac_door_check_start + 0xE, 1)
            patcher.write_int16(0xFFDA52, 1)
            patcher.write_bytes(0xB8998, cvlod_string_to_bytearray("Crystal "))
            # Make the Big Crystal give the Crystal item for Dracula's door.
            crystal_s2_giver_start = len(patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].overlay)
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].write_ovl_int32(
                0x548, 0x0C0B0000 | ((crystal_s2_giver_start + (SCENE_OVERLAY_RDRAM_START & 0xFFFFFF)) // 4))
            patcher.scenes[Scenes.CASTLE_CENTER_BASEMENT].write_ovl_int32s(crystal_s2_giver_start,
                                                                           patches.special2_giver)
        #    special2_text = "The crystal is on!\n" \
        #                    "Time to teach the old man\n" \
        #                    "a lesson!"
        elif slot_patch_info["options"]["draculas_condition"] == DraculasCondition.option_bosses:
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].scene_text[0]["text"] = \
                ("The door is sealed\n"
                 "by a malevolent force...🅰0/\f"
                 "You'll need to vanquish\n"
                 f"{slot_patch_info['options']['bosses_required']} powerful monsters\n"
                 "to undo the seal.🅰0/")
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int16(
                drac_door_check_start + 0xE, slot_patch_info["options"]["bosses_required"])
            patcher.write_int16(0xFFDA52, slot_patch_info["options"]["bosses_required"])
            patcher.write_bytes(0xB8998, cvlod_string_to_bytearray("Trophy  "))
            # Make everything with a health bar give Trophies.
            # Sea Monster
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_SEA_MONSTER)
            patcher.write_int32(0x7250, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_SEA_MONSTER)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_SEA_MONSTER)
            # King Skeleton 1
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_KING_SKELETON)
            patcher.write_int32(0x3FBC, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_KING_SKELETON)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_KING_SKELETON)
            # Were-Tiger (Forest)
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_WERE_TIGER)
            patcher.write_int32(0x1844, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_WERE_TIGER)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_WERE_TIGER)
            # Werewolf (Forest)
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_WEREWOLF)
            patcher.write_int32(0x3ADC, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_WEREWOLF)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_WEREWOLF)
            patcher.write_int32(boss_s2_giver_start + 8, 0x02000008, NIFiles.OVERLAY_WEREWOLF)  # JR S0
            # King Skeleton 2
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_KING_SKELETON)
            patcher.write_int32(0x43E0, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_KING_SKELETON)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_KING_SKELETON)
            patcher.write_int32(boss_s2_giver_start + 8, 0x0BC019E3, NIFiles.OVERLAY_KING_SKELETON)  # J 0x0F00678C
            # White Dragons
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_WHITE_DRAGONS)
            patcher.write_int32(0x20B8, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_WHITE_DRAGONS)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_WHITE_DRAGONS)
            # All Villa interior vampires
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_MALE_VAMPIRES)
            patcher.write_int32(0x1BD0, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_MALE_VAMPIRES)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_MALE_VAMPIRES)
            # Hard Mode Gardener (not currently implemented)
            # boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_GARDENER)
            # patcher.write_int32(0x2D84, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_GARDENER)
            # patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_GARDENER)
            # Gilles De Rais (use the same hack as the one above for the Villa interior vampires)
            patcher.write_int32(0xA9A0, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_MALE_VAMPIRES)
            # J.A. Oldrey in crypt (use the same hack as the one above for the Villa interior vampires)
            patcher.write_int32(0x1AF8, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_MALE_VAMPIRES)
            # Undead Maiden
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_FEMALE_VAMPIRES)
            patcher.write_int32(0x4AD8, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_FEMALE_VAMPIRES)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_FEMALE_VAMPIRES)
            # Queen Algenie
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_QUEEN_ALGENIE)
            patcher.write_int32(0x5820, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_QUEEN_ALGENIE)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_QUEEN_ALGENIE)
            # Lizard-man Trio
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_LIZARD_MEN)
            patcher.write_int32s(0xBC18, [0x0BC00000 | (boss_s2_giver_start // 4),  # J
                                          0x03295023],  # SUBU T2, T9, T1
                                 NIFiles.OVERLAY_LIZARD_MEN)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver_lizard_edition, NIFiles.OVERLAY_LIZARD_MEN)
            # Medusa
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_MEDUSA)
            patcher.write_int32(0x4F44, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_MEDUSA)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_MEDUSA)
            patcher.write_int32(boss_s2_giver_start + 8, 0x02200008, NIFiles.OVERLAY_MEDUSA)  # JR S1
            # Harpy
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_HARPY)
            patcher.write_int32(0x7784, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_HARPY)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_HARPY)
            # Behemoth
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_BEHEMOTH)
            patcher.write_int32(0x369C, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_BEHEMOTH)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_BEHEMOTH)
            # Rosa
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_ROSA)
            patcher.write_int32(0x5750, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_ROSA)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_ROSA)
            # Camilla
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_CAMILLA)
            patcher.write_int32(0x4198, 0x0FC03B80, NIFiles.OVERLAY_CAMILLA)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_CAMILLA)
            patcher.write_int32(boss_s2_giver_start + 8, 0x0BC011FE, NIFiles.OVERLAY_CAMILLA)  # J 0x0F00EE00
            # All possible Duel Tower opponents
            boss_s2_giver_start = len(patcher.scenes[Scenes.DUEL_TOWER].overlay)
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32(
                0x635C, 0x0C0B0000 | ((boss_s2_giver_start + (SCENE_OVERLAY_RDRAM_START & 0xFFFFFF)) // 4))
            patcher.scenes[Scenes.DUEL_TOWER].write_ovl_int32s(boss_s2_giver_start, patches.special2_giver)
            # Security Crystal
            boss_s2_giver_start = len(patcher.scenes[Scenes.SCIENCE_LABS].overlay)
            patcher.scenes[Scenes.SCIENCE_LABS].write_ovl_int32(
                0x11060, 0x0C0B0000 | ((boss_s2_giver_start + (SCENE_OVERLAY_RDRAM_START & 0xFFFFFF)) // 4))
            patcher.scenes[Scenes.SCIENCE_LABS].write_ovl_int32s(boss_s2_giver_start, patches.special2_giver)
            # Death
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_CS_DEATH_DEFEATED)
            patcher.write_int32(0xF88, 0x0F800000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_CS_DEATH_DEFEATED)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_CS_DEATH_DEFEATED)
            # Actrise
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_CS_ACTRISE_DEFEATED)
            patcher.write_int32(0xF20, 0x0F800000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_CS_ACTRISE_DEFEATED)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_CS_ACTRISE_DEFEATED)
            # Ortega
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_CS_ORTEGA_DEFEATED)
            patcher.write_int32(0x3A18, 0x0F800000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_CS_ORTEGA_DEFEATED)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_CS_ORTEGA_DEFEATED)
            # Renon
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_DEMON_RENON)
            patcher.write_int32(0xB54, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_DEMON_RENON)
            patcher.write_int32(0xD6C, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_DEMON_RENON)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_DEMON_RENON)
            # Vincent
            boss_s2_giver_start = patcher.get_decompressed_file_size(NIFiles.OVERLAY_VINCENT)
            patcher.write_int32(0x5DF8, 0x0FC00000 | (boss_s2_giver_start // 4), NIFiles.OVERLAY_VINCENT)
            patcher.write_int32s(boss_s2_giver_start, patches.special2_giver, NIFiles.OVERLAY_VINCENT)
        #    special2_text = f"Proof you killed a powerful\n" \
        #                    f"Night Creature. Earn {required_s2s}/{total_s2s}\n" \
        #                    f"to battle Dracula."
        elif slot_patch_info["options"]["draculas_condition"] == DraculasCondition.option_specials:
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].scene_text[0]["text"] = \
                ("The door is sealed\n"
                 "by a special force...🅰0/\f"
                 "You'll need to find\n"
                 f"{slot_patch_info['options']['required_special2s']} Special2 jewels\n"
                 "to undo the seal.🅰0/")
            patcher.scenes[Scenes.CASTLE_KEEP_EXTERIOR].write_ovl_int16(
                drac_door_check_start + 0xE, slot_patch_info["options"]["required_special2s"])
            patcher.write_int16(0xFFDA52, slot_patch_info["options"]["required_special2s"])
        #    special2_text = f"Need {required_s2s}/{total_s2s} to kill Dracula.\n" \
        #                    f"Looking closely, you see...\n" \
        #                    f"a piece of him within?"
        # else:
        #    special2_text = "If you're reading this,\n" \
        #                    "how did you get a Special2!?"

        # If the Castle Keep Ending Sequence option is Cornell, make Cornell's cutscene trigger in Dracula's chamber
        # universal to everyone and remove Reinhardt and Carrie's.
        if slot_patch_info["options"]["castle_keep_ending_sequence"] == CastleKeepEndingSequence.option_cornell:
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][0]["delete"] = True
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][1]["spawn_flags"] = 0
            # Force Dracula to have all his Cornell behaviors for Reinhardt/Carrie/Henry.
            patcher.write_int32(0x904, 0x34050002, NIFiles.OVERLAY_CS_DRACULA_BATTLE_INTRO)  # ORI  A1, R0, 0x0002
            # Red high energy ring.
            patcher.write_int32(0x40C, 0x34030002, NIFiles.OVERLAY_DRACULA_FIGHT_MGR)  # ORI  V1, R0, 0x0002
            # Red low energy ring.
            patcher.write_int32(0x650, 0x34030002, NIFiles.OVERLAY_DRACULA_FIGHT_MGR)  # ORI  V1, R0, 0x0002
            # Move pool with electric attacks and no flamethrower.
            patcher.write_int32(0x9388, 0x34020002, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0002
            # Blue fire bats.
            patcher.write_int32(0xB83C, 0x34030002, NIFiles.OVERLAY_DRACULA)  # ORI  V1, R0, 0x0002
            # Bats dropping extra chickens.
            patcher.write_int32(0xC7A0, 0x34020002, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0002
            patcher.write_int32(0xC90C, 0x34020002, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0002
            # Cutscene when beaten by Cornell.
            patcher.write_int32(0x90FC, 0x34020002, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0002
            patcher.write_int32(0x9138, 0x34020002, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0002

        # Otherwise, if a Reinhardt/Carrie option was chosen, remove Cornell's trigger, make Reinhardt and Carrie's
        # universal, and force the good ending check after Fake Dracula to always pass.
        else:
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][0]["spawn_flags"] = 0
            patcher.scenes[Scenes.CASTLE_KEEP_DRAC_CHAMBER].actor_lists["init"][1]["delete"] = True
            # Force Fake Dracula to have all his Reinhardt/Carrie behaviors for Cornell/Henry.
            patcher.write_int32(0x904, 0x34050000, NIFiles.OVERLAY_CS_DRACULA_BATTLE_INTRO)  # ORI  A1, R0, 0x0000
            # Blue high energy ring.
            patcher.write_int32(0x40C, 0x34030000, NIFiles.OVERLAY_DRACULA_FIGHT_MGR)  # ORI  V1, R0, 0x0000
            # Blue low energy ring.
            patcher.write_int32(0x650, 0x34030000, NIFiles.OVERLAY_DRACULA_FIGHT_MGR)  # ORI  V1, R0, 0x0000
            # Move pool with flamethrower attack and no electric attacks.
            patcher.write_int32(0x9388, 0x34020000, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0000
            # Orange fire bats.
            patcher.write_int32(0xB83C, 0x34030000, NIFiles.OVERLAY_DRACULA)  # ORI  V1, R0, 0x0000
            # Bats not dropping extra chickens.
            patcher.write_int32(0xC7A0, 0x34020000, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0000
            patcher.write_int32(0xC90C, 0x34020000, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0000
            # Cutscene when beaten by Reinhardt/Carrie.
            patcher.write_int32(0x90FC, 0x34020000, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0000
            patcher.write_int32(0x9138, 0x34020000, NIFiles.OVERLAY_DRACULA)  # ORI  V0, R0, 0x0000
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


        # # # # # # # # # # # # # # #
        # GENERAL POST-STAGE EDITS  #
        # # # # # # # # # # # # # # #
        # Loop over EVERY actor in EVERY list, find all Location-associated instances, and either delete them if they
        # are exclusive to non-Normal difficulties or try writing an Item they should have onto them if they aren't.
        for scene in patcher.scenes:
            for list_name, actor_list in scene.actor_lists.items():
                for actor in actor_list:
                    # If the actor is not a Location-associated actor, or if it's already marked for deletion, or it's
                    # a text spot pickup actor, skip it.
                    if actor["object_id"] not in [Objects.ONE_HIT_BREAKABLE, Objects.THREE_HIT_BREAKABLE,
                                                  Objects.INTERACTABLE] + SPECIAL_1HBS or "delete" in actor or \
                            (actor["object_id"] == Objects.INTERACTABLE and actor["var_c"] not in Pickups):
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
                    if actor["object_id"] == Objects.INTERACTABLE:
                        # If the pickup is a text spot or a White Jewel (wherein Var A is actually a White Jewel ID,
                        # not a flag ID), skip it.
                        if actor["var_c"] == Pickups.WHITE_JEWEL or actor["var_c"] > len(Pickups) + 1:
                            continue
                        # Check if the flag ID has location values associated with it in the slot patch info. If it
                        # does, write that value in the pickup's Var C.
                        if actor["var_a"] in loc_values:
                            actor["var_c"] = loc_values[actor["var_a"]][0]
                            # Un-set the Expire bit in its pickup flags in Var B.
                            actor["var_b"] &= PickupFlags.NEVER_EXPIRE
                            # If we're placing a higher-spawning Item on this Location, and the Location is one where
                            # higher-spawning Items can be problematic, lower it down by 3.2 units.
                            if (actor["var_c"] >> 8) & 0x7F in HIGHER_SPAWNING_ITEMS \
                                    and actor["var_a"] in HIGHER_SPAWNING_PROBLEM_LOCATIONS:
                                actor["y_pos"] -= 3.2
                            # If Invisible Items is not set to Vanilla, change the Item's visibility flag to whatever
                            # we decided for it in its Item info.
                            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla:
                                if loc_values[actor["var_a"]][1]:
                                    actor["var_b"] &= PickupFlags.VISIBLE
                                    # If the pickup location we just made visible has an entry in the new visible item
                                    # coordinates lookup, adjust its XYZ coordinates to be more visible
                                    # (by which we mean "less inside an object")
                                    if actor["var_a"] in NEW_VISIBLE_ITEM_COORDS:
                                        if NEW_VISIBLE_ITEM_COORDS[actor["var_a"]][0] is not None:
                                            actor["x_pos"] = NEW_VISIBLE_ITEM_COORDS[actor["var_a"]][0]
                                        if NEW_VISIBLE_ITEM_COORDS[actor["var_a"]][1] is not None:
                                            actor["y_pos"] = NEW_VISIBLE_ITEM_COORDS[actor["var_a"]][1]
                                        if NEW_VISIBLE_ITEM_COORDS[actor["var_a"]][2] is not None:
                                            actor["z_pos"] = NEW_VISIBLE_ITEM_COORDS[actor["var_a"]][2]
                                else:
                                    actor["var_b"] |= PickupFlags.INVISIBLE

                    # If it's a regular 1HB, the flag to check AND the value to write the new Item over is in the 1HB
                    # data for the scene specified in the actor's Var C.
                    if actor["object_id"] == Objects.ONE_HIT_BREAKABLE:
                        if scene.one_hit_breakables[actor["var_c"]]["flag_id"] in loc_values:
                            scene.one_hit_breakables[actor["var_c"]]["pickup_id"] = \
                                loc_values[scene.one_hit_breakables[actor["var_c"]]["flag_id"]][0]
                            # Un-set the Expire bit in its pickup flags.
                            scene.one_hit_breakables[actor["var_c"]]["pickup_flags"] &= PickupFlags.NEVER_EXPIRE
                            # If Invisible Items is not set to Vanilla, change the Item's visibility flag to whatever
                            # we decided for it in its Item info.
                            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla:
                                if loc_values[scene.one_hit_breakables[actor["var_c"]]["flag_id"]][1]:
                                    scene.one_hit_breakables[actor["var_c"]]["pickup_flags"] &= PickupFlags.VISIBLE
                                else:
                                    scene.one_hit_breakables[actor["var_c"]]["pickup_flags"] |= PickupFlags.INVISIBLE

                    # If it's a special 1HB, then it's similar to the regular 1HB but in the special 1HB data instead.
                    if actor["object_id"] in SPECIAL_1HBS:
                        if scene.one_hit_special_breakables[actor["var_c"]]["flag_id"] in loc_values:
                            scene.one_hit_special_breakables[actor["var_c"]]["pickup_id"] = \
                                loc_values[scene.one_hit_special_breakables[actor["var_c"]]["flag_id"]][0]
                            # Un-set the Expire bit in its pickup flags.
                            scene.one_hit_special_breakables[actor["var_c"]]["pickup_flags"] &= PickupFlags.NEVER_EXPIRE
                            # If Invisible Items is not set to Vanilla, change the Item's visibility flag to whatever
                            # we decided for it in its Item info.
                            if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla:
                                if loc_values[scene.one_hit_special_breakables[actor["var_c"]]["flag_id"]][1]:
                                    scene.one_hit_special_breakables[actor["var_c"]]["pickup_flags"] \
                                        &= PickupFlags.VISIBLE
                                else:
                                    scene.one_hit_special_breakables[actor["var_c"]]["pickup_flags"] \
                                        |= PickupFlags.INVISIBLE

                    # If it's a 3HB, get that 3HB's regular flag ID from its 3HB flag data to figure out which one it
                    # is, and then write the Items it should have into the scene's list of 3HB drop IDs.
                    if actor["object_id"] == Objects.THREE_HIT_BREAKABLE:
                        three_hit = scene.three_hit_breakables[actor["var_c"]]
                        three_hit_info = THREE_HIT_BREAKABLES_INFO[three_hit["flag_id"]]
                        # Check if the 3HB's first flag ID has a Location created for it. If not, skip this 3HB.
                        if three_hit_info.new_first_flag_id not in loc_values:
                            continue
                        # Take the difference in the 3HB's pickup IDs start address and the scene's general 3HB pickup
                        # IDs array start divided by 2 to know which index in the scene's 3HB pickup IDs array to start
                        # writing the 3HB's new pickup IDs into.
                        first_3hb_pickup_index = (three_hit["pickup_array_start"] - scene.three_hit_drops_start) // 2
                        three_hit_invisible_bits = 0
                        for three_hit_pickup_index in range(three_hit["pickup_count"]):
                            scene.three_hit_drop_ids[first_3hb_pickup_index + three_hit_pickup_index] = \
                                loc_values[CVLOD_LOCATIONS_INFO[
                                    three_hit_info.location_names[three_hit_pickup_index]].flag_id][0]
                            # If the pickup we're currently looking at has False for its Invisible Item visibility info,
                            # set a bit in a bitfield that will be used for the game to tell that this 3HB pickup should
                            # be invisible.
                            if not loc_values[CVLOD_LOCATIONS_INFO[
                                    three_hit_info.location_names[three_hit_pickup_index]].flag_id][1]:
                                three_hit_invisible_bits |= 1 << three_hit_pickup_index
                        # Change the 3HB's vanilla flag ID to the new flag ID that its pickups will begin at.
                        three_hit["flag_id"] = three_hit_info.new_first_flag_id
                        # Write the invisibility bits in the upper half of the flag ID if Invisible Items is not set to
                        # Vanilla.
                        if slot_patch_info["options"]["invisible_items"] != InvisibleItems.option_vanilla:
                            three_hit["flag_id"] |= three_hit_invisible_bits << 16


        # Loop over every active stage in the slot's stage list and connect their starts and ends properly.
        for stage in slot_patch_info["stages"]:
            # Figure out what previous stage end-associated values to put in the current stage's start transition(s).

            # If the previous stage is "Start", put 0xFF for the scene and the current stage's start spawn ID.
            # This will cause the transition to reload the map without really sending the player anywhere.
            if stage["connecting_stages"]["prev"][0] == "Start":
                prev_scene = Scenes.NULL
                prev_spawn = CVLOD_STAGE_INFO[stage["name"]].start_spawn_id
            # Otherwise, get the primary previous stage's end scene and spawn IDs.
            else:
                prev_scene = CVLOD_STAGE_INFO[stage["connecting_stages"]["prev"][0]].end_scene_id
                prev_spawn = CVLOD_STAGE_INFO[stage["connecting_stages"]["prev"][0]].end_spawn_id

            # If Castle Center is the previous stage and either Castle Center Branching Stages is One Carrie or the
            # current stage is an alternate path stage, set the end spawn ID to Carrie's CC exit instead of Reinhardt's.
            if stage["connecting_stages"]["prev"][0] == stage_names.CENTER and \
                    (slot_patch_info["options"]["castle_center_branching_paths"] ==
                     CastleCenterBranchingPaths.option_one_carrie or "'" in stage["position"]):
                prev_spawn = 0x02

            # Write the previous stage end values correctly based on what transition it is.
            # If the current stage has a start loading zone defined for it in its stage info, put the values in it.
            if CVLOD_STAGE_INFO[stage["name"]].start_zone_id is not None:
                patcher.scenes[CVLOD_STAGE_INFO[stage["name"]].start_scene_id].loading_zones[
                    CVLOD_STAGE_INFO[stage["name"]].start_zone_id]["scene_id"] = prev_scene
                patcher.scenes[CVLOD_STAGE_INFO[stage["name"]].start_scene_id].loading_zones[
                    CVLOD_STAGE_INFO[stage["name"]].start_zone_id]["spawn_id"] = prev_spawn
            # If it's one of the stages that has a teleport jewel for its start transition, write the values at these
            # specific addresses.
            elif stage["name"] in TELEPORT_JEWEL_START_STAGES:
                patcher.write_bytes(TELEPORT_JEWEL_VALUES_START + (TELEPORT_JEWEL_START_STAGES.index(stage["name"]) *
                                                                   TELEPORT_JEWEL_ENTRY_LEN),
                                    [prev_scene, prev_spawn])
            # If the current stage is Clock Tower, write the values in its other inaccessible start loading zone as well
            # (just in case).
            if stage["name"] == stage_names.CLOCK:
                patcher.scenes[Scenes.CLOCK_TOWER_GEAR_CLIMB].loading_zones[1]["scene_id"] = prev_scene
                patcher.scenes[Scenes.CLOCK_TOWER_GEAR_CLIMB].loading_zones[1]["spawn_id"] = prev_spawn


            # Figure out what next stage start-associated values to put in the current stage's end transition(s).

            # If the next stage is "End", skip everything to do with connecting forward to the next stage.
            # Because Castle Keep has no way to go further than it.
            if stage["connecting_stages"]["next"][0] == "End":
                continue
            # If the stage's position is "C", meaning it's the last stage in the Cornell path, connect the stage end to
            # the Castle Center top elevator room at the elevator's spawn point.
            elif stage["position"] == "C":
                next_scene = Scenes.CASTLE_CENTER_TOP_ELEV
                next_spawn = 0x00
            # If the next stage is Clock Tower and the Castle Center Branching Paths option is set to One Carrie, have
            # the start spawn be the grate Carrie starts in front of instead of the one Reinhardt and Cornell start at.
            elif stage["connecting_stages"]["next"][0] == stage_names.CLOCK and \
                    slot_patch_info["options"]["castle_center_branching_paths"] == \
                    CastleCenterBranchingPaths.option_one_carrie:
                next_scene = CVLOD_STAGE_INFO[stage_names.CLOCK].start_scene_id
                next_spawn = 0x01
            # Otherwise, get the primary next stage's start scene and spawn IDs.
            else:
                next_scene = CVLOD_STAGE_INFO[stage["connecting_stages"]["next"][0]].start_scene_id
                next_spawn = CVLOD_STAGE_INFO[stage["connecting_stages"]["next"][0]].start_spawn_id

            # Write the next stage start values correctly based on what transition it is.
            # Every stage barring Castle Keep should have an end loading zone.
            patcher.scenes[CVLOD_STAGE_INFO[stage["name"]].end_scene_id].loading_zones[
                CVLOD_STAGE_INFO[stage["name"]].end_zone_id]["scene_id"] = next_scene
            patcher.scenes[CVLOD_STAGE_INFO[stage["name"]].end_scene_id].loading_zones[
                CVLOD_STAGE_INFO[stage["name"]].end_zone_id]["spawn_id"] = next_spawn

            # If Forest of Silence is the current stage, make the post-King Skeleton drawbridge cutscene send the player
            # to the next stage as well.
            if stage["name"] == stage_names.FOREST:
                patcher.write_byte(0x130B, next_scene, NIFiles.OVERLAY_CS_FOREST_DRAWBRIDGE_LOWERS)
                patcher.write_byte(0x131B, next_spawn, NIFiles.OVERLAY_CS_FOREST_DRAWBRIDGE_LOWERS)

            # If Villa is the current stage, make adjustments to the coffin loading zone code based on the
            # Villa Branching Paths option.
            if stage["name"] == stage_names.VILLA:
                # If Next Alt 2 exists for Villa, meaning there are three branching paths, have the coffin zone send the
                # player to the Villa's primary next stage when it would send them to Tunnel, to the Next Alt 1 stage
                # for Waterway, and to the Next Alt 2 stage for Outer Wall.
                if "next alt 2" in stage["connecting_stages"]:
                    patcher.write_byte(0xD3AB7, next_scene)
                    patcher.write_byte(0xD3ACB, next_spawn)
                    patcher.write_byte(0xD3B1B, CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 1"][0]].start_scene_id)
                    patcher.write_byte(0xD3B47, CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 1"][0]].start_spawn_id)
                    patcher.write_byte(0xD3B0F, CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 2"][0]].start_scene_id)
                    patcher.write_byte(0xD3B47, CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 2"][0]].start_spawn_id)
                # If Next Alt 2 does not exist for Villa but Next Alt 1 does, meaning there are two branching paths,
                # have the coffin zone send the player there when it would send them to Waterway (daytime) and to the
                # Next Alt 1 stage for Waterway (nighttime).
                elif "next alt 1" in stage["connecting_stages"]:
                    patcher.write_byte(0xD3B1B, next_scene)
                    patcher.write_byte(0xD3B47, next_spawn)
                    patcher.write_byte(0xD3AB7, CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 1"][0]].start_scene_id)
                    patcher.write_byte(0xD3ACB, CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 1"][0]].start_spawn_id)

            # If Castle Center is the current stage, make adjustments to Carrie's end loading zone in the top elevator
            # room based on the Castle Center Branching Paths option.
            if stage["name"] == stage_names.CENTER:
                # If Next Alt 1 exists for Castle Center, have Carrie's loading zone send the player there.
                if "next alt 1" in stage["connecting_stages"]:
                    patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].loading_zones[2]["scene_id"] = CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 1"][0]].start_scene_id
                    patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].loading_zones[2]["spawn_id"] = CVLOD_STAGE_INFO[
                        stage["connecting_stages"]["next alt 1"][0]].start_spawn_id
                # Otherwise, have Carrie's zone send the player to the primary next stage.
                else:
                    patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].loading_zones[2]["scene_id"] = next_scene
                    patcher.scenes[Scenes.CASTLE_CENTER_TOP_ELEV].loading_zones[2]["spawn_id"] = next_spawn


        # If Disable Time Restrictions is set to All, make all events that expect a certain time able to happen anytime.
        if slot_patch_info["options"]["disable_time_restrictions"] == DisableTimeRestrictions.option_all:
            # Loop over every door data in the game and clear the time restriction flags from all of them.
            for scene in patcher.scenes:
                for door in scene.doors:
                    door["door_flags"] &= DoorFlags.NO_TIME_RESTRICTIONS

            # If we have the Reinhardt/Carrie Villa, put the fountain pillar on its Henry behavior for everyone
            # (always raised no matter what).
            if slot_patch_info["options"]["villa_state"] == VillaState.option_reinhardt_carrie:
                patcher.write_int32(0xD77E0, 0x24030003)  # ADDIU V1, R0, 0x0003
                patcher.write_int32(0xD7A60, 0x24030003)  # ADDIU V1, R0, 0x0003

            # Make the 3AM Rosa cutscene trigger active at all times.
            patcher.write_int16(0x117F12, 0x0000)
            patcher.write_int16(0x117F14, 0x0018)

            # Make the 6AM rose patch active at all times.
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x3B4, 0x34030006)  # ORI T6, V1, 0x0006
            patcher.scenes[Scenes.VILLA_FOYER].write_ovl_int32(0x660, 0x340E0006)  # ORI T6, R0, 0x0006
            patcher.write_int32(0xC4, 0x34030006, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        # Otherwise, if set to Art Tower Only, only remove the time restrictions on the Art Tower doors.
        elif slot_patch_info["options"]["disable_time_restrictions"] == DisableTimeRestrictions.option_art_tower_only:
            for door in patcher.scenes[Scenes.ART_TOWER_MUSEUM].doors:
                door["door_flags"] &= DoorFlags.NO_TIME_RESTRICTIONS

        # If Loading Zone Heals are off, loop over every loading zone data and clear its "heal player" value.
        if not slot_patch_info["options"]["loading_zone_heals"]:
            for scene in patcher.scenes:
                for loading_zone in scene.loading_zones:
                    loading_zone["heal_player"] = False
            # NOP the call to the "fill player health" function in King Skeleton 2's defeat function.
            patcher.write_int32(0x4318, 0x00000000, NIFiles.OVERLAY_KING_SKELETON)

        # Change the item healing values if "Nerf Healing" is turned on
        if slot_patch_info["options"]["nerf_healing_items"]:
            patcher.write_int16(0x4CB8, 0x1F40, NIFiles.OVERLAY_PAUSE_MENU)  # Healing kit   (10000 -> 8000)
            patcher.write_int16(0x4CBE, 0x1388, NIFiles.OVERLAY_PAUSE_MENU)  # Roast beef    ( 8000 -> 5000)
            patcher.write_int16(0x4CC4, 0x09C4, NIFiles.OVERLAY_PAUSE_MENU)  # Roast chicken ( 5000 -> 2500)
            # Update the menu descriptions to reflect the new amounts.
            patcher.write_bytes(0x3BC4, cvlod_string_to_bytearray("25%"), NIFiles.OVERLAY_PAUSE_MENU)
            patcher.write_bytes(0x3C18, cvlod_string_to_bytearray("50%"), NIFiles.OVERLAY_PAUSE_MENU)
            patcher.write_bytes(0x3C9E, cvlod_string_to_bytearray("80% "), NIFiles.OVERLAY_PAUSE_MENU)
            patcher.write_bytes(0x2D38, cvlod_string_to_bytearray("25%"), NIFiles.OVERLAY_RENONS_SHOP)
            patcher.write_bytes(0x2D8E, cvlod_string_to_bytearray("50%"), NIFiles.OVERLAY_RENONS_SHOP)
            patcher.write_bytes(0x2E16, cvlod_string_to_bytearray("80% "), NIFiles.OVERLAY_RENONS_SHOP)

        # Change the starting stage to whatever stage the player is actually starting at.
        patcher.write_byte(0x15DB, CVLOD_STAGE_INFO[slot_patch_info["stages"][0]["name"]].start_scene_id,
                           NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        patcher.write_byte(0x15D3, CVLOD_STAGE_INFO[slot_patch_info["stages"][0]["name"]].start_spawn_id,
                           NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)

        # If we have no starting flags, block the Henry Mode starting flag setter routine from running for all
        # characters.
        if not starting_flags:
            patcher.write_int32(0x220, 0x34080000, NIFiles.OVERLAY_HENRY_NG_INITIALIZER)  # ORI  T0, R0, 0x0000
        # Otherwise, if we do, make it run for all characters and have it set our starting flags instead.
        else:
            patcher.write_int32(0x220, 0x34080003, NIFiles.OVERLAY_HENRY_NG_INITIALIZER)  # ORI  T0, R0, 0x0003
            patcher.write_byte(0x3B3, 12 + (len(starting_flags) // 8 * 12), NIFiles.OVERLAY_HENRY_NG_INITIALIZER)
            patcher.write_byte(0x41B, len(starting_flags), NIFiles.OVERLAY_HENRY_NG_INITIALIZER)
            # If the length of the starting flags list is odd, add an extra 0 to pad it evenly. And then write it in.
            if len(starting_flags) % 2:
                starting_flags += [0]
            patcher.write_int16s(0x450, starting_flags, NIFiles.OVERLAY_HENRY_NG_INITIALIZER)

        return patcher.get_output_rom()

        # Hack to make the Forest, CW and Villa intro cutscenes play at the start of their levels no matter what map
        # came before them
        # #patcher.write_int32(0x97244, 0x803FDD60)
        # #patcher.write_int32s(0xBFDD60, patches.forest_cw_villa_intro_cs_player)

        # Enable swapping characters when loading into a map by holding L.
        # patcher.write_int32(0x97294, 0x803FDFC4)
        # patcher.write_int32(0x19710, 0x080FF80E)  # J 0x803FE038
        # patcher.write_int32s(0xBFDFC4, patches.character_changer)

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

        # Make received DeathLinks blow you to smithereens instead of kill you normally.
        # if options.death_link.value == options.death_link.option_explosive:
        # patcher.write_int32(0x27A70, 0x10000008)  # B [forward 0x08]
        # patcher.write_int32s(0xBFC0D0, patches.deathlink_nitro_edition)

        # Warp menu-opening code
        # patcher.write_int32(0x86FE4, 0x0C0FF254)  # JAL	0x803FC950
        # patcher.write_int32s(0xFFC950, patches.warp_menu_opener)

        # Sub-weapon check function hook
        # patcher.write_int32(0xBF32C, 0x00000000)  # NOP
        # patcher.write_int32(0xBF330, 0x080FF05E)  # J	0x803FC178
        # patcher.write_int32s(0xBFC178, patches.give_subweapon_stopper)

        # Warp menu Special1 restriction
        # patcher.write_int32(0xADD68, 0x0C04AB12)  # JAL 0x8012AC48
        # patcher.write_int32s(0xADE28, patches.stage_select_overwrite)
        # patcher.write_byte(0xADE47, s1s_per_warp)

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
    pass
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
