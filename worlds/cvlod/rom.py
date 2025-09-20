import logging
import zlib
import json
import base64
import Utils

from BaseClasses import Location
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
from abc import ABC
from typing import List, Dict, Union, Iterable, Collection, Optional, TYPE_CHECKING, NamedTuple

import hashlib
import os
import pkgutil

from .data import patches, loc_names
from .data.enums import Scenes, NIFiles, Objects, ObjectExecutionFlags, ActorSpawnFlags, Items, Pickups, PickupFlags, \
    DoorFlags
from .stages import CVLOD_STAGE_INFO
from .cvlod_text import cvlod_string_to_bytearray, cvlod_text_wrap, cvlod_bytes_to_string, CVLOD_STRING_END_CHARACTER, \
    CVLOD_TEXT_POOL_END_CHARACTER
from .aesthetics import renon_item_dialogue
from .locations import CVLOD_LOCATIONS_INFO
from .options import StageLayout, VincentFightCondition, RenonFightCondition, PostBehemothBoss, RoomOfClocksBoss, \
    CastleKeepEndingSequence, DeathLink, DraculasCondition, InvisibleItems, Countdown, PantherDash
from settings import get_settings

if TYPE_CHECKING:
    from . import CVLoDWorld

CVLOD_US_HASH = "25258460f98f567497b24844abe3a05b"

N64_RDRAM_START = 0x80000000
MAP_OVERLAY_RDRAM_START = 0x2E3B70 | N64_RDRAM_START

MAP_OVERLAY_RDRAM_ADDRS_START = 0xB3858  # 800B2C58
MAP_OVERLAY_ROM_ADDRS_START = 0xB39E8  # 800B2DE8
MAP_ACTOR_PTRS_START = 0x10D150  # 8018C8A0
MAP_1HB_PTRS_START = 0x11222C  # 8019197C
MAP_3HB_PTRS_START = 0x1122F4  # 80191A44
MAP_ENEMY_PILLARS_PTRS_START = 0x10DBB4  # 8018D304
MAP_DOOR_PTRS_START = 0x1108C0  # 80190010
MAP_LOADING_ZONE_PTRS_START = 0x110D38  # 80190488
MAP_TEXT_PTRS_START = 0xB8DE0  # 800B81E0
MAP_ENTRANCE_COORS_PTRS_START = 0x1107F8  # 8018FF48

NORMAL_ACTOR_ENTRY_LENGTH = 0x20
ONE_HIT_BREAKABLE_ENTRY_LENGTH = 0xC
THREE_HIT_BREAKABLE_ENTRY_LENGTH = 0xC
ENEMY_PILLAR_ENTRY_LENGTH = 0x10
ENEMY_PILLAR_ACTOR_ENTRY_LENGTH = 0x18
LOADING_ZONE_ENTRY_LENGTH = 0x14
DOOR_ENTRY_LENGTH = 0x2C
MAP_ENTRANCE_LENGTH = 0x16

REGULAR_MAP_OVERLAYS_START = 0x76CD00
REGULAR_MAP_OVERLAYS_END = 0x838350

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

EXTENDED_DATA_ACTORS: dict[int, str] = {Objects.ONE_HIT_BREAKABLE: "1hb",
                                        Objects.THREE_HIT_BREAKABLE: "3hb",
                                        Objects.ENEMY_GENERATOR_PILLAR: "pillar",
                                        Objects.DOOR: "door",
                                        Objects.LOADING_ZONE: "load"}

WARP_MAP_OFFSETS = [0xADF67, 0xADF77, 0xADF87, 0xADF97, 0xADFA7, 0xADFBB, 0xADFCB, 0xADFDF]


class CVLoDMapDataEntry(ABC):
    """Abstract class that all CVLoD map data entries inherit from."""

    start_addr: int | None  # Where in the RDRAM the data entry starts, if it's vanilla. For easier debugging.

    def check_enums(self) -> None:
        """Checks select values in the data against enums defined in data/enums.py and makes them those enum values.
        For better debugger viewing."""
        return None

    def get_rom_bytes(self) -> bytes:
        """Returns the entry data in bytes form, as it would be in the ROM."""
        pass


class CVLoDMapDataList(NamedTuple):
    """Container for complete lists of extracted CVLoD map data entries, including general information about them."""

    orig_addr: int  # Original address of the data in the map overlay.
    orig_len: int  # Original length of the data.
    data_sequence: list[CVLoDMapDataEntry | str]  # The data contained extracted from the map overlay itself.


class CVLoDActorEntry(CVLoDMapDataEntry):
    """Common class both types of CVLoD map actor list entries inherit from."""

    x_pos: int  # How far east/west from the center of the map the actor is located.
                # 32-bit float (normal) / int16 (pillar).
    y_pos: int  # How far up/down from the center of the map the actor is located.
                # 32-bit float (normal) / int16 (pillar).
    z_pos: int  # Hor far north/south from the center of the map the actor is located.
                # 32-bit float (normal) / int16 (pillar).
    execution_flags: int # Flags related to execution functionality with the actor. Upper 5 bits in the object ID bytes.
    object_id: int  # The game's ID for what object the actor is (breakable, enemy, pickup, etc.). Lower 11 bits in the
                    # object ID bytes.
    flag_id: int  # For normal: Int16 ID for the flag value the actor checks to see if it should or shouldn't spawn, if
                  # spawn flags 0x0020 or 0x0080 are set on it.
                  # For pillar: 32-bit struct for a flag to check to see if the pillar should spawn the actor. If the
                  # 80000000 bitflag is set, check the flag ID being set. If 40000000 is set, check it being un-set.
    variable_1: int  # Extra int16 parameters that apply to the actor (exactly what these mean vary per actor).
    variable_2: int
    variable_3: int
    variable_4: int

    def __init__(self, x_pos: int = 0, y_pos: int = 0, z_pos: int = 0, execution_flags: int = 0, object_id: int = 0,
                 flag_id: int = 0, variable_1: int = 0, variable_2: int = 0, variable_3: int = 0, variable_4: int = 0,
                 start_addr: int | None = None):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos
        self.execution_flags = execution_flags
        self.object_id = object_id
        self.flag_id = flag_id
        self.variable_1 = variable_1
        self.variable_2 = variable_2
        self.variable_3 = variable_3
        self.variable_4 = variable_4
        self.start_addr = start_addr

    def check_enums(self) -> None:

        # Check if the object has a documented entry in the objects enum.
        if self.object_id in Objects:
            self.object_id = Objects(self.object_id)

        # Check if the object is an item pickup actor, and if it is, does it have has an entry in the pickups enum.
        if self.object_id == Objects.PICKUP_ITEM and self.variable_3 in Pickups:
            self.variable_3 = Pickups(self.variable_3)

        # Loop over every spawn flag see if we have any of them set and documented.
        for flag_index in range(0x16):
            flag_to_check = self.execution_flags & (1 << flag_index)
            if flag_to_check in ActorSpawnFlags:
                self.execution_flags |= ActorSpawnFlags(flag_to_check)

        # Loop over every execution flag and see if we have any of them set and documented.
        for flag_index in range(0x5):
            flag_to_check = self.execution_flags & (1 << flag_index)
            if flag_to_check in ObjectExecutionFlags:
                self.execution_flags |= ObjectExecutionFlags(flag_to_check)

    def get_rom_bytes(self) -> bytes:
        return b''


class CVLoDNormalActorEntry(CVLoDActorEntry):
    """An entry from any regular actor list in any map in the game."""

    spawn_flags: int  # 16-bit bitfield comprising flags that affect the condition under which the actor spawns.
    status_flags: int  # 16-bit bitfield comprising flags used to tell the actor's current spawned state. Normally 0.
    extra_condition_ptr: int  # Int32 pointer to an extra spawn check function to run, if spawn flag 0x0008 is enabled.

    def __init__(self, spawn_flags: int = 0, status_flags: int = 0, x_pos: int = 0, y_pos: int = 0, z_pos: int = 0,
                 execution_flags: int = 0, object_id: int = 0, flag_id: int = 0, variable_1: int = 0, variable_2: int = 0,
                 variable_3: int = 0, variable_4: int = 0, extra_condition_ptr: int = 0, start_addr: int = 0):
        super().__init__(x_pos, y_pos, z_pos, execution_flags, object_id, flag_id, variable_1, variable_2, variable_3,
                         variable_4, start_addr)
        self.spawn_flags = spawn_flags
        self.status_flags = status_flags
        self.extra_condition_ptr = extra_condition_ptr


    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.spawn_flags, 2, "big") +
                int.to_bytes(self.status_flags, 2, "big") +
                int.to_bytes(self.x_pos, 4, "big") +
                int.to_bytes(self.y_pos, 4, "big") +
                int.to_bytes(self.z_pos, 4, "big") +
                int.to_bytes(self.object_id | (self.execution_flags << 0x5), 2, "big") +
                int.to_bytes(self.flag_id, 2, "big") +
                int.to_bytes(self.variable_1, 2, "big") +
                int.to_bytes(self.variable_2, 2, "big") +
                int.to_bytes(self.variable_3, 2, "big") +
                int.to_bytes(self.variable_4, 2, "big") +
                int.to_bytes(self.extra_condition_ptr, 4, "big"))


class CVLoDPillarActorEntry(CVLoDActorEntry):
    """An entry from the enemy generator pillar actor list found exclusively in Tower of Execution (Central Tower)."""

    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.x_pos, 2, "big") +
                int.to_bytes(self.y_pos, 2, "big") +
                int.to_bytes(self.z_pos, 2, "big") +
                int.to_bytes(self.object_id | (self.execution_flags << 0x5), 2, "big") +
                int.to_bytes(self.variable_3, 2, "big") +
                int.to_bytes(self.variable_1, 2, "big") +
                int.to_bytes(self.variable_2, 2, "big") +
                int.to_bytes(self.variable_4, 2, "big") + b'\x00\x00\x00\x00' +
                int.to_bytes(self.flag_id, 4, "big"))


class CVLoD1HitBreakableEntry(CVLoDMapDataEntry):
    """An entry from the map's list of 1-hit breakable datas."""

    appearance_id: int  # Int16 ID for what appearance the 1HB takes. 0 = normal floor candle, 1 = wall candle, etc.
    pickup_id: int  # Int16 ID for what pickup to drop upon breaking the 1HB if the event flag isn't set.
    flag_id: int  # Int32 ID for what event flag the dropped pickup checks to see if it should spawn and sets upon being
                  # picked up.
    pickup_flags: int  # 16-bit bitfield comprising bitflags that affect the dropped pickup's behavior.

    def __init__(self, appearance_id: int = 0, pickup_id: int = 0, flag_id: int = 0, pickup_flags: int = 0,
                 start_addr: int | None = None):
        self.appearance_id = appearance_id
        self.pickup_id = pickup_id
        self.flag_id = flag_id
        self.pickup_flags = pickup_flags
        self.start_addr = start_addr

    def check_enums(self) -> None:
        
        # Check if the pickup ID has an entry in the pickups enum.
        if self.pickup_id in Pickups:
            self.pickup_id = Pickups(self.pickup_id)

        # Loop over every pickup flag and see if we have any of them set and documented.
        for flag_index in range(0x16):
            flag_to_check = self.pickup_flags & (1 << flag_index)
            if flag_to_check in PickupFlags:
                self.pickup_flags |= PickupFlags(flag_to_check)


    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.appearance_id, 2, "big") +
                int.to_bytes(self.pickup_id, 2, "big") +
                int.to_bytes(self.flag_id, 4, "big") +
                int.to_bytes(self.pickup_flags, 2, "big") + b'\x00\x00')


class CVLoD3HitBreakableEntry(CVLoDMapDataEntry):
    """An entry from the map's list of 3-hit breakable datas."""

    appearance_id: int  # Int16 ID for what breakable's appearance the 3HB takes.
    pickup_count: int  # How many item IDs from the item array start the 3HB drops. Int16.
    pickup_array_start: int  # 32-bit address in RAM for the first pickup ID the 3HB drops. The remaining pickup IDs are
                             # always located right after the first one.
    flag_id: int  # Int32 ID for what event flag the 3HB checks to see if it should break and sets upon breaking. In
                  # this implementation, it is instead the first flag ID to set on the first dropped pickup, with the
                  # subsequent pickups getting +1 every time (the 3HBs break every time no matter what).

    def __init__(self, appearance_id: int = 0, pickup_count: int = 0, pickup_array_start: int = 0, flag_id: int = 0,
                 start_addr: int | None = None):
        self.appearance_id = appearance_id
        self.pickup_count = pickup_count
        self.flag_id = flag_id
        self.pickup_array_start = pickup_array_start
        self.start_addr = start_addr

    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.appearance_id, 2, "big") +
                int.to_bytes(self.pickup_count, 2, "big") +
                int.to_bytes(self.pickup_array_start, 4, "big") +
                int.to_bytes(self.flag_id, 4, "big"))


class CVLoDEnemyPillarEntry(CVLoDMapDataEntry):
    """An entry from the map's list of enemy generator pillar datas (exclusive to Tower of Execution (Central))."""

    actor_list_start: int  # 32-bit address in RAM for the first actor the pillar spawns when broken. The remaining
                           # actors are always located right after the first one.
    actor_count: int  # How many actors from the actor list start the pillar spawns. Int16.
    dissolve_flags: int  # 16-bit bitfield comprising flags that affect the dissolve effect when the pillar breaks.
    rotation: int  # What angle direction the pillar is facing on the Y axis. Int32.
    flag_id: int  # Int32 ID for what event flag the pillar checks to see if it should break and sets upon breaking.

    def __init__(self, actor_list_start: int = 0, actor_count: int = 0, dissolve_flags: int = 0, rotation: int = 0,
                 flag_id: int = 0, start_addr: int | None = None):
        self.actor_list_start = actor_list_start
        self.actor_count = actor_count
        self.dissolve_flags = dissolve_flags
        self.rotation = rotation
        self.flag_id = flag_id
        self.start_addr = start_addr

    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.actor_list_start, 4, "big") +
                int.to_bytes(self.actor_count, 2, "big") +
                int.to_bytes(self.dissolve_flags, 2, "big") +
                int.to_bytes(self.rotation, 4, "big") +
                int.to_bytes(self.flag_id, 4, "big"))


class CVLoDLoadingZoneEntry(CVLoDMapDataEntry):
    """An entry from the map's list of loading zone datas."""

    heal_player: bool  # Whether the loading zone should heal the player. 16 bits.
    map_id: int  # Int8 ID for which map in the game the loading zone will send the player to.
    entrance_id: int  # Int8 ID for which entrance in the destination map the player will spawn at.
    fade_settings_id: int  # Int8 ID for which settings in the game's fade settings table will be used.
    cutscene_settings_id: int  # Int16 ID for which settings in the game's loading zone cutscene settings table will be
                               # used. 0 if no cutscene should play.
    min_x_pos: int  # How far east/west the map the zone's bounding box min is located. 16-bit.
    min_y_pos: int  # How far up/down the zone's bounding box min is located. 16-bit.
    min_z_pos: int  # How far north/south the zone's bounding box min is located. 16-bit.
    max_x_pos: int  # How far east/west the zone's bounding box max is located. 16-bit.
    max_y_pos: int  # How far up/down the zone's bounding box max is located. 16-bit.
    max_z_pos: int  # How far north/south the zone's bounding box max is located. 16-bit.

    def __init__(self, heal_player: bool = False, map_id: int = 0, entrance_id: int = 0, fade_settings_id: int = 0,
                 cutscene_settings_id: int = 0, min_x_pos: int = 0, min_y_pos: int = 0, min_z_pos: int = 0,
                 max_x_pos: int = 0, max_y_pos: int = 0, max_z_pos: int = 0, start_addr: int | None = None):
        self.heal_player = heal_player
        self.map_id = map_id
        self.entrance_id = entrance_id
        self.fade_settings_id = fade_settings_id
        self.cutscene_settings_id = cutscene_settings_id
        self.min_x_pos = min_x_pos
        self.min_y_pos = min_y_pos
        self.min_z_pos = min_z_pos
        self.max_x_pos = max_x_pos
        self.max_y_pos = max_y_pos
        self.max_z_pos = max_z_pos
        self.start_addr = start_addr

    def check_enums(self) -> None:

        # Check if the zone's destination map has a map ID with an entry in the maps enum.
        if self.map_id in Scenes:
            self.map_id = Scenes(self.map_id)

    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.heal_player, 2, "big") +
                int.to_bytes(self.map_id, 1, "big") +
                int.to_bytes(self.entrance_id, 1, "big") +
                int.to_bytes(self.fade_settings_id, 1, "big") +
                int.to_bytes(self.cutscene_settings_id, 2, "big") +
                int.to_bytes(self.min_x_pos, 2, "big") +
                int.to_bytes(self.min_y_pos, 2, "big") +
                int.to_bytes(self.min_z_pos, 2, "big") +
                int.to_bytes(self.max_x_pos, 2, "big") +
                int.to_bytes(self.max_y_pos, 2, "big") +
                int.to_bytes(self.max_z_pos, 2, "big"))


class CVLoDDoorEntry(CVLoDMapDataEntry):
    """An entry from the map's list of door datas."""

    dlist_addr: int  # Int32 DisplayList address for the door's model in the map file.
    texture_id: int  # Int8 ID for what texture to apply to the door. FF if not applicable.
    palette_id: int  # Int8 ID for what palette to apply to the door's texture. FF if not applicable.
    byte_6: int  # Something???
    door_flags: int  # 16-bit bitfield comprising flags that affect the door's opening conditions.
    extra_condition_ptr: int  # Int32 pointer to a custom door opening check function to run, if door flag 0x0200 is
                              # enabled. NOTE: This function is called INSTEAD of the regular door flags check one, so
                              # the custom function must call the regular one as part of it if that behavior's desired.
    flag_id: int  # Int16 ID for what event flag to check if certain door flags are set on this door.
    item_id: int  # Int32 ID for what item is used to open the door if door flag 0x0100 is enabled.
    front_room_id: int  # Int8 ID for which room to load when opening the door from the back. 80 if not applicable.
    back_room_id: int  # Int8 ID for which room to load when opening the door from the front. 80 if not applicable.
    cant_open_text_id: int  # Int8 ID for what text in the map's text pool to display if the player tries opening the
                            # door when they can't. 80 if nothing.
    unlocked_text_id: int  # Int8 ID for what text in the map's text pool to display if the player unlocks the door.
                           # 80 if nothing.
    byte_1c: int  # Something??? 80 if not applicable.
    opening_sound_id: int  # Int16 ID for what sound to play when the door starts opening.
    closing_sound_id: int  # Int16 ID for what sound to play when the door starts closing.
    shut_sound_id: int  # Int16 ID for what sound to play when the door slams shut.

    def __init__(self, dlist_addr: int = 0, texture_id: int = 0, palette_id: int = 0, byte_6: int = 0,
                 door_flags: int = 0, extra_condition_ptr: int = 0, flag_id: int = 0, item_id: int = 0,
                 front_room_id: int = 0, back_room_id: int = 0, cant_open_text_id: int = 0, unlocked_text_id: int = 0,
                 byte_1c: int = 0, opening_sound_id: int = 0, closing_sound_id: int = 0, shut_sound_id: int = 0,
                 start_addr: int | None = None):
        self.dlist_addr = dlist_addr
        self.texture_id = texture_id
        self.palette_id = palette_id
        self.byte_6 = byte_6
        self.door_flags = door_flags
        self.extra_condition_ptr = extra_condition_ptr
        self.flag_id = flag_id
        self.item_id = item_id
        self.front_room_id = front_room_id
        self.back_room_id = back_room_id
        self.cant_open_text_id = cant_open_text_id
        self.unlocked_text_id = unlocked_text_id
        self.byte_1c = byte_1c
        self.opening_sound_id = opening_sound_id
        self.closing_sound_id = closing_sound_id
        self.shut_sound_id = shut_sound_id
        self.start_addr = start_addr

    def check_enums(self) -> None:

        # Check if the door has an item ID with an entry in the items enum.
        if self.item_id in Items:
            self.item_id = Items(self.item_id)

        # Loop over every door flag and see if we have any of them set and documented.
        for flag_index in range(0x16):
            flag_to_check = self.door_flags & (1 << flag_index)
            if flag_to_check in DoorFlags:
                self.door_flags |= DoorFlags(flag_to_check)

    def get_rom_bytes(self) -> bytes:

        # Any sound IDs that are not 0000 should have 0200 in the bytes that follow them instead of 0000.
        post_opening = b'\x00\x00'
        if self.opening_sound_id:
            post_opening = b'\x02\x00'

        post_closing = b'\x00\x00'
        if self.closing_sound_id:
            post_closing = b'\x02\x00'

        post_shut = b'\x00\x00'
        if self.shut_sound_id:
            post_shut = b'\x02\x00'

        return (int.to_bytes(self.dlist_addr, 4, "big") +
                int.to_bytes(self.texture_id, 1, "big") +
                int.to_bytes(self.palette_id, 1, "big") +
                int.to_bytes(self.byte_6, 1, "big") + b'\x00' +
                int.to_bytes(self.door_flags, 2, "big") + b'\x00\x00' +
                int.to_bytes(self.extra_condition_ptr, 4, "big") +
                int.to_bytes(self.flag_id, 2, "big") + b'\x00\x00' +
                int.to_bytes(self.item_id, 4, "big") +
                int.to_bytes(self.front_room_id, 1, "big") +
                int.to_bytes(self.back_room_id, 1, "big") +
                int.to_bytes(self.cant_open_text_id, 1, "big") +
                int.to_bytes(self.unlocked_text_id, 1, "big") +
                int.to_bytes(self.byte_1c, 1, "big") + b'\x00' +
                int.to_bytes(self.opening_sound_id, 2, "big") + post_opening +
                int.to_bytes(self.closing_sound_id, 2, "big") + post_closing +
                int.to_bytes(self.shut_sound_id, 2, "big") + post_shut + b'\x80\x00')


class CVLoDMapEntranceEntry(CVLoDMapDataEntry):
    """An entry from the map's list entrance coordinate datas."""

    room_id: int  # Int16 ID for which room to load initially if it's a room-based map.
    player_x_pos: int  # How far east/west from the center of the map the player spawns. Int16.
    player_y_pos: int  # How far up/down from the center of the map the player spawns. Int16.
    player_z_pos: int  # How far north/south from the center of the map the player spawns. Int16.
    player_rotation: int  # What angle direction the player is facing upon spawning in here. Int16.
    camera_x_pos: int  # How far east/west from the center of the map the camera spawns. Int16.
    camera_y_pos: int  # How far up/down from the center of the map the camera spawns. Int16.
    camera_z_pos: int  # How far north/south from the center of the map the camera spawns. Int16.
    focus_x_pos: int  # How far east/west from the center of the map the camera's initial point of focus is. Int16.
    focus_y_pos: int  # How far up/down from the center of the map the camera's initial point of focus is. Int16.
    focus_z_pos: int  # How far north/south from the center of the map the camera's initial point of focus is. Int16.
    start_addr: int | None = None # Where in the ROM the entrance's data starts, if it's vanilla. For easier debugging.

    def __init__(self, room_id: int = 0, player_x_pos: int = 0, player_y_pos: int = 0, player_z_pos: int = 0,
                 player_rotation: int = 0, camera_x_pos: int = 0, camera_y_pos: int = 0, camera_z_pos: int = 0,
                 focus_x_pos: int = 0, focus_y_pos: int = 0, focus_z_pos: int = 0, start_addr: int | None = None):
        self.room_id = room_id
        self.player_x_pos = player_x_pos
        self.player_y_pos = player_y_pos
        self.player_z_pos = player_z_pos
        self.player_rotation = player_rotation
        self.camera_x_pos = camera_x_pos
        self.camera_y_pos = camera_y_pos
        self.camera_z_pos = camera_z_pos
        self.focus_x_pos = focus_x_pos
        self.focus_y_pos = focus_y_pos
        self.focus_z_pos = focus_z_pos
        self.start_addr = start_addr

    def get_rom_bytes(self) -> bytes:
        return (int.to_bytes(self.room_id, 2, "little") +
                int.to_bytes(self.player_x_pos, 2, "little") +
                int.to_bytes(self.player_y_pos, 2, "little") +
                int.to_bytes(self.player_z_pos, 2, "little") +
                int.to_bytes(self.player_rotation, 2, "little") +
                int.to_bytes(self.camera_x_pos, 2, "little") +
                int.to_bytes(self.camera_y_pos, 2, "little") +
                int.to_bytes(self.camera_z_pos, 2, "little") +
                int.to_bytes(self.focus_z_pos, 2, "little") +
                int.to_bytes(self.focus_z_pos, 2, "little") +
                int.to_bytes(self.focus_z_pos, 2, "little"))


class CVLoDMap:
    overlay: bytearray | None
    entrance_list: CVLoDMapEntranceEntry  # List of spawn entrances in the map.
    enemy_pillars: CVLoDMapDataList
    one_hit_breakables: CVLoDMapDataList
    three_hit_drop_ids: list[int]  # Array of item IDs that the 3HBs on the map can drop.
    three_hit_breakables: CVLoDMapDataList
    map_text: list[str]  # All textbox texts associated with the map.
    doors: CVLoDMapDataList
    loading_zones: CVLoDMapDataList
    actor_lists: dict[str, CVLoDMapDataList]  # Dict of actor lists in the map mapped to which one it is.
    highest_ids: dict[str, int]  # The highest IDs for specific data like 1-hit breakables, determined from the actors.
    start_addr: int | None  # Where in RDRAM the (loaded) map's data starts, if it's vanilla. For easier debugging.
    name: str | None  # The name of the map. To more easily see which one it is while debugging.
    space_available: dict[int, int]  # Start and end addresses of space in the overlay freed up from moving a data from
                                     # one spot to another.

    def __init__(self, entrance_list=None, actor_lists=None, start_addr: int | None=None,
                 name: str | None=None) -> None:
        if entrance_list is None:
            entrance_list = []
        if actor_lists is None:
            actor_lists = {}

        self.entrance_list = entrance_list
        self.actor_lists = actor_lists
        self.start_addr = start_addr
        self.name = name

        self.highest_ids = {extended_data: -1 for object_id, extended_data in EXTENDED_DATA_ACTORS.items()}

    def read_ovl_byte(self, offset: int) -> int | None:
        """Return a byte at a specified address in the map's overlay."""
        if self.overlay:
            return self.overlay[offset]
        logging.error(f"Map {self.name} has no overlay associated with it. Fix the code and Try, Try Again!")

    def read_ovl_bytes(self, start_address: int, length: int, return_as_int: bool = False) -> bytearray | int | None:
        """Return a string of bytes of a specified length beginning at a specified address in the map's overlay."""
        if not self.overlay:
            logging.error(f"Map {self.name} has no overlay associated with it. Fix the code and Never Let Up!")
            return None
        if return_as_int:
            return int.from_bytes(self.overlay[start_address:start_address + length], "little")
        return self.overlay[start_address:start_address + length]

    def setup_overlay(self) -> bytes:
        """Adjusts the map's associated overlay with all of its modified data and updates the relevant pointers in the
        ROM's data tables."""

        # Loop over every map entrance and assemble its data struct.
        map_entrance_structs = []
        for entrance in self.entrance_list:
            # Get the map spawn entrance in bytes form.
            map_entrance_structs.append(entrance.get_rom_bytes())

        # Assemble the struct header for the list of map entrances. The first two bytes are an int16 for the length of
        # the entire struct, including this header which is always 4 bytes in length. Each entrance struct itself is 8
        # bytes in length.
        map_entrance_list_data = int.to_bytes(4 + (len(map_entrance_structs)) * 8, 2, "little")

        # The second two bytes are an int16 for the total number of entrances in the struct.
        map_entrance_list_data += int.to_bytes(len(map_entrance_structs), 2, "little")

        # Now stick on each map entrance data to get the complete struct.
        for map_entrance_struct in map_entrance_structs:
            map_entrance_list_data += map_entrance_struct


        # Assemble the complete scene setup list data.
        # Start by getting the complete byte datas for each and every scene setup.
        scene_setup_structs = []
        for scene_setup in self.scene_setups:
            scene_setup_structs.append(scene_setup.get_rom_bytes())

        # Assemble the scene setup list header. The first byte is an int8 for the total number of setups.
        scene_setup_list_data = int.to_bytes(len(scene_setup_structs), 1, "little")

        # Up next is an array of bytes corresponding to every story sequence value that tell the game which scene setup
        # to use for each sequence, followed by a 0xFF to keep things 4-aligned.
        scene_setup_list_data += bytes(self.sequence_scene_setup_ids) + b'\xFF'

        # After that is an array of byte distances from the start of the map entrance data struct to the start of every
        # scene setup (each one being an int16 followed by six 0x00s). To get this, take the length of the map entrance
        # data struct, the length of the scene setup list header we have so far (should be 0x30), and the number of
        # scene setups times 8 (for each entry in the array).
        scene_setup_byte_distance = len(map_entrance_list_data) + len(scene_setup_list_data) + \
                                    (len(scene_setup_structs) * 8)

        # Loop over each scene setup struct and for each one, determine the total byte distance to it from the start of
        # the struct and add it (and six 0x00's) to the header.
        for scene_setup_struct in scene_setup_structs:
            scene_setup_list_data += int.to_bytes(scene_setup_byte_distance, 2, "little") + b'\x00\x00\x00\x00\x00\x00'

            # Add the total length of the current scene setup to get the distance towards the next one.
            scene_setup_byte_distance += len(scene_setup_struct)

        # Stick the scene setup datas on in the same order as their byte distances from the start of the struct to get
        # our complete list of scene setups struct.
        for scene_setup_struct in scene_setup_structs:
            scene_setup_list_data += scene_setup_struct

        # Return the complete map data.
        return map_entrance_list_data + scene_setup_list_data


class CVLoDRomHandler:
    rom: bytearray
    decompressed_files: Dict[int, bytearray]
    compressed_files: Dict[int, bytearray]
    maps: list[CVLoDMap]
    ni_table_start: int
    ni_file_buffers_start: int
    decomp_file_sizes_table_start: int
    number_of_ni_files: int

    def __init__(self, input_rom: bytearray) -> None:
        self.rom = input_rom

        self.decompressed_files = {}
        self.compressed_files = {}

        # Seek the "Nisitenma-Ichigo" string in the ROM indicating where the table containing the compressed file start
        # and end offsets begins.
        nisitenma_ichigo_start = self.rom.find("Nisitenma-Ichigo".encode("utf-8"))
        # If the "Nisitenma-Ichigo" string is somehow nowhere to be found, raise an exception.
        if nisitenma_ichigo_start == -1:
            raise Exception("Nisitenma-Ichigo string not found.")

        self.ni_table_start = nisitenma_ichigo_start + 16
        self.ni_file_buffers_start = int.from_bytes(self.rom[self.ni_table_start: self.ni_table_start + 4],
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

        # Read out all the common map data structs (actor lists, breakable datas, map text, etc.).
        for map_id in range(len(Scenes)):
            self.maps.append(CVLoDMap(name=Scenes(map_id).name))

            # Check to see if the map has an associated overlay. If it doesn't (because the map has no start address
            # in the game's hardcoded list of map overlay ROM starts), skip it.
            map_overlay_start = self.read_bytes(MAP_OVERLAY_ROM_ADDRS_START + (map_id * 8), 4, return_as_int=True)
            map_overlay_end = self.read_bytes(MAP_OVERLAY_ROM_ADDRS_START + (map_id * 8) + 4, 4, return_as_int=True)
            if not map_overlay_start:
                self.maps[map_id].overlay = None
                continue

            # Otherwise, save its vanilla overlay data and continue.
            self.maps[map_id].overlay = self.rom[map_overlay_start: map_overlay_end]

            # Extract the map's init actor list (the one that spawns all of its contents upon the map initializing
            # and keeps them spawned regardless of both the player's distance to them and what room they're in). Take
            # the third pointer in the map's entry in the game's table of loaded map actor list starts and determine how
            # far in it is relative to the start of the overlay in RDRAM.
            self.maps[map_id].actor_lists["init"] = \
                self.extract_normal_map_actor_list(map_id, self.read_bytes(MAP_ACTOR_PTRS_START + 8 + (map_id * 0x10),
                                                                           4, return_as_int=True)
                                                   - MAP_OVERLAY_RDRAM_START)

            # Extract the map's distance actor list (the one that will spawn its things ONLY while the player is within
            # a certain distance from them and is also not tied to any room). This is the second pointer in the map's
            # entry in the above-mentioned table.
            self.maps[map_id].actor_lists["distance"] = \
                self.extract_normal_map_actor_list(map_id, self.read_bytes(MAP_ACTOR_PTRS_START + 4 + (map_id * 0x10),
                                                                           4, return_as_int=True)
                                                   - MAP_OVERLAY_RDRAM_START)

            # Extract the map's room actor lists (the ones that will spawn their things only while their designated
            # rooms are loaded and, much like the init list, don't care about the player's distance). Not every map has
            # these; in fact, most don't. To see if the current map we're looking at has one, we will check if the
            # fourth pointer in the map's table entry is not 00000000.
            room_actor_ptrs_start = self.read_bytes(MAP_ACTOR_PTRS_START + 0xC + (map_id * 0x10), 4,
                                                    return_as_int=True) - MAP_OVERLAY_RDRAM_START

            # While we are at it, also take the first pointer, which points to not an actor list-related thing but the
            # start of the map's decoration data list. This is where the room actor pointers list ends.
            map_decorations_data_start = self.read_bytes(MAP_ACTOR_PTRS_START + (map_id * 0x10), 4,
                                                         return_as_int=True) - MAP_OVERLAY_RDRAM_START

            # If room actor lists exist, extract them.
            if room_actor_ptrs_start != 0:
                # Grab the list of pointers to said lists. To determine how many pointers the list has, take the
                # difference between the map decorations data start address and the room actor pointers start address;
                # the latter structs always begin immediately after the former.
                room_list_ptrs = [self.maps[map_id].read_ovl_bytes(room_actor_ptrs_start + (room_id * 4), 4,
                                                                        return_as_int=True) - MAP_OVERLAY_RDRAM_START
                                  for room_id in range((map_decorations_data_start - room_actor_ptrs_start) // 4)]
                # Extract the actor lists at the pointers we just extracted.
                for room_id in range(len(room_list_ptrs)):
                    self.maps[map_id].actor_lists[f"room {room_id}"] = \
                        self.extract_normal_map_actor_list(map_id, room_list_ptrs[room_id])

            # Extract the enemy pillar data if enemy pillar data exists (highest found enemy pillar ID is 0 or higher).
            # This should only occur for the Tower of Execution (Central tower) map.
            if self.maps[map_id].highest_ids["pillar"] > -1:

                # Get the start address of the map's enemy pillar data in the overlay.
                enemy_pillars_start = self.read_bytes(MAP_ENEMY_PILLARS_PTRS_START + (map_id * 4), 4,
                                                      return_as_int=True) - MAP_OVERLAY_RDRAM_START

                # Loop over every enemy pillar data that is known to exist based on how high the highest ID is.
                enemy_pillar_list = []
                lowest_pillar_actor_list_start = 0xFFFFFF
                highest_pillar_actor_list_end = 0x000000
                for enemy_pillar_id in range(self.maps[map_id].highest_ids["pillar"] + 1):
                    current_enemy_pillar_start = enemy_pillars_start + (enemy_pillar_id * ENEMY_PILLAR_ENTRY_LENGTH)
                    enemy_pillar_data = self.maps[map_id].read_ovl_bytes(current_enemy_pillar_start,
                                                                              ENEMY_PILLAR_ENTRY_LENGTH)
                    enemy_pillar = CVLoDEnemyPillarEntry(
                        actor_list_start=int.from_bytes(enemy_pillar_data[0x00:0x04], "big"),
                        actor_count=int.from_bytes(enemy_pillar_data[0x04:0x06], "big"),
                        dissolve_flags=int.from_bytes(enemy_pillar_data[0x06:0x08], "big"),
                        rotation=int.from_bytes(enemy_pillar_data[0x08:0x0C], "big"),
                        flag_id=int.from_bytes(enemy_pillar_data[0x0C:], "big"),
                        start_addr=current_enemy_pillar_start + MAP_OVERLAY_RDRAM_START
                    )

                    # If the pillar has a lower actor list start address than the lowest one we've found, save the new
                    # one.
                    if enemy_pillar.actor_list_start < lowest_pillar_actor_list_start:
                        lowest_pillar_actor_list_start = enemy_pillar.actor_list_start

                    # If the pillar has a higher actor list end address than the lowest one we've found, save the new
                    # one.
                    pillar_actor_list_end = enemy_pillar.actor_list_start + \
                                            (enemy_pillar.actor_list_start * ENEMY_PILLAR_ACTOR_ENTRY_LENGTH)
                    if pillar_actor_list_end > highest_pillar_actor_list_end:
                        highest_pillar_actor_list_end = pillar_actor_list_end

                    # Append the enemy pillar to the end of the list.
                    enemy_pillar_list.append(enemy_pillar)

                # Save the complete enemy pillar list.
                self.maps[map_id].enemy_pillars = CVLoDMapDataList(enemy_pillars_start, len(enemy_pillar_list),
                                                                   enemy_pillar_list)

                # Extract the map's enemy pillar actor list using the lowest and highest pillar actor list addresses
                # that we gleamed from the regular enemy pillar data.
                pillar_actor_list = []
                for pillar_actor_list_id in range((highest_pillar_actor_list_end - lowest_pillar_actor_list_start)
                                                  // ENEMY_PILLAR_ACTOR_ENTRY_LENGTH):
                    current_enemy_pillar_actor_start = lowest_pillar_actor_list_start - MAP_OVERLAY_RDRAM_START + \
                                                       (pillar_actor_list_id * ENEMY_PILLAR_ACTOR_ENTRY_LENGTH)
                    pillar_actor_data = self.maps[map_id].read_ovl_bytes(current_enemy_pillar_actor_start,
                        ENEMY_PILLAR_ACTOR_ENTRY_LENGTH)

                    object_id = int.from_bytes(pillar_actor_data[0x06:0x08], "big")
                    pillar_actor = CVLoDPillarActorEntry(
                        x_pos=int.from_bytes(pillar_actor_data[0x00:0x02], "big"),
                        y_pos=int.from_bytes(pillar_actor_data[0x02:0x04], "big"),
                        z_pos=int.from_bytes(pillar_actor_data[0x04:0x06], "big"),
                        execution_flags=object_id >> 0xB,
                        object_id=object_id & 0x7FF,
                        variable_3=int.from_bytes(pillar_actor_data[0x06:0x08], "big"),
                        variable_1=int.from_bytes(pillar_actor_data[0x08:0x0A], "big"),
                        variable_2=int.from_bytes(pillar_actor_data[0x0A:0x0C], "big"),
                        variable_4=int.from_bytes(pillar_actor_data[0x0C:0x0E], "big"),
                        flag_id=int.from_bytes(pillar_actor_data[0x14:], "big"),
                        start_addr=current_enemy_pillar_actor_start + MAP_OVERLAY_RDRAM_START
                    )
                    pillar_actor.check_enums()

                    # If the actor is in the dict of actors with extended data, check the data ID in param 3 against the
                    # highest one we've found so far for that actor on this map. If it's higher, then consider it the
                    # new highest.
                    if pillar_actor.object_id in EXTENDED_DATA_ACTORS.keys():
                        extended_data_type = EXTENDED_DATA_ACTORS[pillar_actor.object_id]

                        if pillar_actor.variable_3 > self.maps[map_id].highest_ids[extended_data_type]:
                            self.maps[map_id].highest_ids[extended_data_type] = pillar_actor.variable_3

                    # Append the actor to the end of the list.
                    pillar_actor_list.append(pillar_actor)

                # Save the complete pillar actor list.
                self.maps[map_id].actor_lists["pillars"] = CVLoDMapDataList(lowest_pillar_actor_list_start,
                                                                            len(pillar_actor_list), pillar_actor_list)


                # Get the start address of the map's enemy pillar data in the overlay.
                enemy_pillars_start = self.read_bytes(MAP_ENEMY_PILLARS_PTRS_START + (map_id * 4), 4,
                                                      return_as_int=True) - MAP_OVERLAY_RDRAM_START

                # Loop over every enemy pillar data that is known to exist based on how high the highest ID is.
                enemy_pillar_list = []
                for enemy_pillar_id in range(self.maps[map_id].highest_ids["pillar"] + 1):
                    current_enemy_pillar_start = enemy_pillars_start + (enemy_pillar_id * ENEMY_PILLAR_ENTRY_LENGTH)
                    enemy_pillar_data = self.maps[map_id].read_ovl_bytes(current_enemy_pillar_start,
                                                                              ENEMY_PILLAR_ENTRY_LENGTH)
                    enemy_pillar = CVLoDEnemyPillarEntry(
                        actor_list_start=int.from_bytes(enemy_pillar_data[0x00:0x04], "big"),
                        actor_count=int.from_bytes(enemy_pillar_data[0x04:0x06], "big"),
                        dissolve_flags=int.from_bytes(enemy_pillar_data[0x06:0x08], "big"),
                        rotation=int.from_bytes(enemy_pillar_data[0x08:0x0C], "big"),
                        flag_id=int.from_bytes(enemy_pillar_data[0x0C:], "big"),
                        start_addr=current_enemy_pillar_start + MAP_OVERLAY_RDRAM_START
                    )

                    # Append the enemy pillar to the end of the list.
                    enemy_pillar_list.append(enemy_pillar)

                # Save the complete enemy pillar list.
                self.maps[map_id].enemy_pillars = CVLoDMapDataList(enemy_pillars_start, len(enemy_pillar_list),
                                                                   enemy_pillar_list)

            # Extract the 1-hit breakables data if 1HB data exists (highest found 1HB ID is 0 or higher).
            if self.maps[map_id].highest_ids["1hb"] > -1:
                # Get the start address of the map's 1HB data in the overlay.
                one_hit_breakables_start = self.read_bytes(MAP_1HB_PTRS_START + (map_id * 4), 4, return_as_int=True) \
                                           - MAP_OVERLAY_RDRAM_START

                # Loop over every 1HB data that is known to exist based on how high the highest ID is.
                one_hit_list = []
                for one_hit_id in range(self.maps[map_id].highest_ids["1hb"] + 1):
                    current_one_hit_start = one_hit_breakables_start + (one_hit_id * ONE_HIT_BREAKABLE_ENTRY_LENGTH)
                    one_hit_data = self.maps[map_id].read_ovl_bytes(current_one_hit_start,
                                                                         ONE_HIT_BREAKABLE_ENTRY_LENGTH)

                    one_hit = CVLoD1HitBreakableEntry(
                        appearance_id=int.from_bytes(one_hit_data[0x00:0x02], "big"),
                        pickup_id=int.from_bytes(one_hit_data[0x02:0x04], "big"),
                        flag_id=int.from_bytes(one_hit_data[0x04:0x08], "big"),
                        pickup_flags=int.from_bytes(one_hit_data[0x08:0x0A], "big"),
                        start_addr=current_one_hit_start + MAP_OVERLAY_RDRAM_START,
                    )

                    one_hit.check_enums()

                    # Append the 1HB to the end of the list.
                    one_hit_list.append(one_hit)

                # Save the complete 1HB list.
                self.maps[map_id].one_hit_breakables = CVLoDMapDataList(one_hit_breakables_start, len(one_hit_list),
                                                                        one_hit_list)

            # Extract the 3-hit breakables data if 3HB data exists (highest found 3HB ID is 0 or higher).
            if self.maps[map_id].highest_ids["3hb"] > -1:

                # Get the start address of the map's 3HB data in the overlay.
                three_hit_breakables_start = self.read_bytes(MAP_3HB_PTRS_START + (map_id * 4), 4, return_as_int=True) \
                                             - MAP_OVERLAY_RDRAM_START

                # Loop over every 3HB data that is known to exist based on how high the highest ID is.
                three_hit_list = []
                lowest_3hb_pickup_array_start = 0xFFFFFF
                highest_3hb_pickup_array_end = 0x000000
                for three_hit_id in range(self.maps[map_id].highest_ids["3hb"] + 1):
                    current_three_hit_start = three_hit_breakables_start + (three_hit_id *
                                                                            THREE_HIT_BREAKABLE_ENTRY_LENGTH)
                    three_hit_data = self.maps[map_id].read_ovl_bytes(current_three_hit_start,
                                                                           THREE_HIT_BREAKABLE_ENTRY_LENGTH)
                    three_hit = CVLoD3HitBreakableEntry(
                        appearance_id=int.from_bytes(three_hit_data[0x00:0x02], "big"),
                        pickup_count=int.from_bytes(three_hit_data[0x02:0x04], "big"),
                        pickup_array_start=int.from_bytes(three_hit_data[0x04:0x08], "big"),
                        flag_id=int.from_bytes(three_hit_data[0x08:], "big"),
                        start_addr=current_three_hit_start + MAP_OVERLAY_RDRAM_START
                    )

                    # If the 3HB has a lower pickup array start address than the lowest one we've found, save the new
                    # one.
                    if three_hit.pickup_array_start < lowest_3hb_pickup_array_start:
                        lowest_3hb_pickup_array_start = three_hit.pickup_array_start

                    # If the 3HB has a higher pickup array end address than the lowest one we've found, save the new
                    # one.
                    pickup_array_end = three_hit.pickup_array_start + (three_hit.pickup_count * 2)
                    if pickup_array_end > highest_3hb_pickup_array_end:
                        highest_3hb_pickup_array_end = pickup_array_end

                    # Append the 3HB to the end of the list.
                    three_hit_list.append(three_hit)

                # Save the complete 3HB list.
                self.maps[map_id].three_hit_breakables = CVLoDMapDataList(three_hit_breakables_start,
                                                                          len(three_hit_list), three_hit_list)

                # Extract the map's array of 3HB pickup IDs using the lowest and highest 3HB drop array addresses that
                # we gleamed from the regular 3HB data.
                three_hit_pickups_list = []
                for three_hit_pickup_array_id in range((highest_3hb_pickup_array_end -
                                                        lowest_3hb_pickup_array_start) // 2):
                    three_hit_pickup_id = self.maps[map_id].read_ovl_bytes(
                        lowest_3hb_pickup_array_start - MAP_OVERLAY_RDRAM_START + (three_hit_pickup_array_id * 2), 2)

                    # Check if the pickup ID is in the pickups enum and then add it to the list.
                    if three_hit_pickup_id in Pickups:
                        three_hit_pickup_id = Pickups(three_hit_pickup_id)
                    three_hit_pickups_list.append(three_hit_pickup_id)

                # Save the complete 3HB pickups list.
                self.maps[map_id].three_hit_drop_ids = CVLoDMapDataList(lowest_3hb_pickup_array_start,
                                                                        len(three_hit_pickups_list),
                                                                        three_hit_pickups_list)

            # Extract the door data if door data exists (highest found door ID is 0 or higher).
            if self.maps[map_id].highest_ids["door"] > -1:

                # Get the start address of the map's door data in the overlay.
                doors_start = self.read_bytes(MAP_DOOR_PTRS_START + (map_id * 4), 4, return_as_int=True) \
                                             - MAP_OVERLAY_RDRAM_START

                # Loop over every door data that is known to exist based on how high the highest ID is.
                door_list = []
                for door_id in range(self.maps[map_id].highest_ids["door"] + 1):
                    current_door_start = doors_start + (door_id * DOOR_ENTRY_LENGTH)
                    door_data = self.maps[map_id].read_ovl_bytes(current_door_start, DOOR_ENTRY_LENGTH)
                    door = CVLoDDoorEntry(
                        dlist_addr=int.from_bytes(door_data[0x00:0x04], "big"),
                        texture_id=door_data[0x04],
                        palette_id=door_data[0x05],
                        byte_6=door_data[0x06],
                        door_flags=int.from_bytes(door_data[0x08:0x0A], "big"),
                        extra_condition_ptr=int.from_bytes(door_data[0x0C:0x10], "big"),
                        flag_id=int.from_bytes(door_data[0x10:0x12], "big"),
                        item_id=int.from_bytes(door_data[0x14:0x18], "big"),
                        front_room_id=door_data[0x18],
                        back_room_id=door_data[0x19],
                        cant_open_text_id=door_data[0x1A],
                        unlocked_text_id=door_data[0x1B],
                        byte_1c=door_data[0x1C],
                        opening_sound_id=int.from_bytes(door_data[0x1E:0x20], "big"),
                        closing_sound_id=int.from_bytes(door_data[0x22:0x24], "big"),
                        shut_sound_id=int.from_bytes(door_data[0x26:0x28], "big"),
                        start_addr=current_door_start + MAP_OVERLAY_RDRAM_START
                    )
                    door.check_enums()

                    # Append the 3HB to the end of the list.
                    door_list.append(door)

                # Save the complete door list.
                self.maps[map_id].doors = CVLoDMapDataList(doors_start, len(door_list), door_list)

            # Extract the loading zone data if door data exists (highest found loading zone ID is 0 or higher).
            if self.maps[map_id].highest_ids["load"] > -1:

                # Get the start address of the map's loading zone data in the overlay.
                loading_zones_start = self.read_bytes(MAP_LOADING_ZONE_PTRS_START + (map_id * 4), 4,
                                                      return_as_int=True) - MAP_OVERLAY_RDRAM_START

                # Loop over every loading zone data that is known to exist based on how high the highest ID is.
                loading_zone_list = []
                for loading_zone_id in range(self.maps[map_id].highest_ids["load"] + 1):
                    current_loading_zone_start = loading_zones_start + (loading_zone_id * LOADING_ZONE_ENTRY_LENGTH)
                    loading_zone_data = self.maps[map_id].read_ovl_bytes(current_loading_zone_start,
                                                                         LOADING_ZONE_ENTRY_LENGTH)
                    loading_zone = CVLoDLoadingZoneEntry(
                        heal_player=bool.from_bytes(loading_zone_data[0x00:0x02], "big"),  # heal_player
                        map_id=loading_zone_data[0x02],
                        entrance_id=loading_zone_data[0x03],
                        fade_settings_id=loading_zone_data[0x04],
                        cutscene_settings_id=int.from_bytes(loading_zone_data[0x06:0x08], "big"),  # cutscene_settings_id
                        min_x_pos=int.from_bytes(loading_zone_data[0x08:0x0A], "big"),
                        min_y_pos=int.from_bytes(loading_zone_data[0x0A:0x0C], "big"),
                        min_z_pos=int.from_bytes(loading_zone_data[0x0C:0x0E], "big"),
                        max_x_pos=int.from_bytes(loading_zone_data[0x0E:0x10], "big"),
                        max_y_pos=int.from_bytes(loading_zone_data[0x10:0x12], "big"),
                        max_z_pos=int.from_bytes(loading_zone_data[0x12:], "big"),
                        start_addr=current_loading_zone_start + MAP_OVERLAY_RDRAM_START
                    )
                    loading_zone.check_enums()

                    # Append the 3HB to the end of the list.
                    loading_zone_list.append(loading_zone)

                # Save the complete loading zone list.
                self.maps[map_id].loading_zones = CVLoDMapDataList(loading_zones_start, len(loading_zone_list),
                                                                   loading_zone_list)

            # Extract the map text pool if it has one (map ID is 0x2A or lower).
            if map_id <= 0x2A:
                map_text_start = self.read_bytes(MAP_TEXT_PTRS_START + (map_id * 4), 4,
                                                 return_as_int=True) - MAP_OVERLAY_RDRAM_START

                # Loop over every character in the map text pool.
                current_map_text_char_start = map_text_start
                raw_map_text = bytes(0)
                converted_text = []
                while True:
                    map_text_char = self.maps[map_id].read_ovl_bytes(current_map_text_char_start, 2, return_as_int=True)

                    # Increment the current text character start for the next loop.
                    current_map_text_char_start += 2

                    # If we found the character indicating the end of the entire pool, terminate the loop.
                    if map_text_char == CVLOD_TEXT_POOL_END_CHARACTER:
                        break

                    # If we found the character indicating the end of a string in the text pool, convert what we
                    # extracted of the current string now.
                    if map_text_char == CVLOD_STRING_END_CHARACTER:
                        converted_text.append(cvlod_bytes_to_string(raw_map_text))
                        # Reset the raw map text back to nothing and then continue to the next iteration.
                        raw_map_text = bytes(0)
                        continue

                    raw_map_text += map_text_char

                # Save the complete map text list.
                self.maps[map_id].map_text = CVLoDMapDataList(map_text_start, len(converted_text), converted_text)






    def read_byte(self, address: int, file_num: int = 0) -> int:
        """Return a byte at a specified address in a specified file."""
        if file_num == 0:
            return self.rom[address]
        if file_num not in self.decompressed_files:
            self.decompress_file(file_num)
        return self.decompressed_files[file_num][address]

    def read_bytes(self, start_address: int, length: int, return_as_int: bool = False,
                   file_num: int = 0) -> bytearray | int:
        """Return a string of bytes of a specified length beginning at a specified address in a specified file."""
        if file_num == 0:
            values = self.rom[start_address:start_address + length]
        else:
            if file_num not in self.decompressed_files:
                self.decompress_file(file_num)
            values = self.decompressed_files[file_num][start_address:start_address + length]

        if return_as_int:
            return int.from_bytes(values, "big")
        return self.rom[values]

    def write_byte(self, address: int, value: int, file_num: int = 0) -> None:
        if file_num == 0:
            self.rom[address] = value
        else:
            if file_num not in self.decompressed_files:
                self.decompress_file(file_num)
            self.decompressed_files[file_num][address] = value

    def write_bytes(self, start_address: int, values: Collection[int], file_num: int = 0) -> None:
        if file_num == 0:
            self.rom[start_address:start_address + len(values)] = values
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

    def extract_normal_map_actor_list(self, map_id: int, start_addr: int) -> CVLoDMapDataList:
        """Extracts normal actor list data out of a given map ID's overlay starting at a given address."""

        # Loop over each actor list entry and read it out. Continue looping until we reach the end of the list.
        actor_list = []
        curr_addr = start_addr
        while True:
            actor_data = self.maps[map_id].read_ovl_bytes(curr_addr, NORMAL_ACTOR_ENTRY_LENGTH)
            # The execution flags (the upper 5 bits) need to be split out of the object ID (the lower 11 bits).
            object_id = int.from_bytes(actor_data[0x10:0x12], "big")
            actor = CVLoDNormalActorEntry(
                spawn_flags=int.from_bytes(actor_data[0x00:0x02], "big"),
                status_flags=int.from_bytes(actor_data[0x02:0x04], "big"),
                x_pos=int.from_bytes(actor_data[0x04:0x08], "big"),
                y_pos=int.from_bytes(actor_data[0x08:0x0C], "big"),
                z_pos=int.from_bytes(actor_data[0x0C:0x10], "big"),
                execution_flags=object_id >> 0xB,
                object_id=object_id & 0x7FF,
                flag_id=int.from_bytes(actor_data[0x12:0x14], "big"),
                variable_1=int.from_bytes(actor_data[0x14:0x16], "big"),
                variable_2=int.from_bytes(actor_data[0x16:0x18], "big"),
                variable_3=int.from_bytes(actor_data[0x18:0x1A], "big"),
                variable_4=int.from_bytes(actor_data[0x1A:0x1C], "big"),
                extra_condition_ptr=int.from_bytes(actor_data[0x1C:], "big"),
                start_addr=curr_addr + MAP_OVERLAY_RDRAM_START
            )
            actor.check_enums()

            # If the actor we extracted has an object ID of 0x7FF, then we have reached the actor entry signifying
            # the end of the list. In which case, return the actor list as-is (don't append the end-of-list entry).
            if actor.object_id == Objects.END_OF_ACTOR_LIST:
                return CVLoDMapDataList(start_addr, len(actor_list), actor_list)

            # If the actor is in the dict of actors with extended data, check the data ID in param 3 against the highest
            # one we've found so far for that actor on this map. If it's higher, then consider it the new highest.
            if actor.object_id in EXTENDED_DATA_ACTORS.keys():
                extended_data_type = EXTENDED_DATA_ACTORS[actor.object_id]

                if actor.variable_3 > self.maps[map_id].highest_ids[extended_data_type]:
                    self.maps[map_id].highest_ids[extended_data_type] = actor.variable_3

            # Append the actor to the end of the list.
            actor_list.append(actor)

            # Increment the current main actor sotart address so we will be at the start of the next one on the
            # next loop.
            curr_addr += NORMAL_ACTOR_ENTRY_LENGTH

    def decompress_file(self, file_num: int) -> None:
        self.decompressed_files[file_num] = bytearray(zlib.decompress(self.compressed_files[file_num][4:]))

    def compress_file(self, file_num: int) -> None:
        compressed_file = bytearray(zlib.compress(self.decompressed_files[file_num], level=zlib.Z_BEST_COMPRESSION))
        # Pad the buffer to 0x02.
        if len(compressed_file) % 2:
            compressed_file.append(0x00)
        # Add the length header at the beginning.
        self.compressed_files[file_num] = bytearray((0x80000004 + len(compressed_file)).to_bytes(4, "big")) \
            + bytearray(compressed_file)

    def get_output_rom(self) -> bytes:
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

        # Return the final output ROM
        return bytes(self.rom)


class CVLoDPatchExtensions(APPatchExtension):
    game = "Castlevania - Legacy of Darkness"

    @staticmethod
    def patch_rom(caller: APProcedurePatch, input_rom: bytes, options_file: str, ni_edits: str) -> bytes:
        handler = CVLoDRomHandler(bytearray(input_rom))
        options = json.loads(caller.get_file(options_file).decode("utf-8"))
        ni_edits = json.loads(caller.get_file(ni_edits).decode("utf-8"))

        # NOP out the CRC BNEs
        handler.write_int32(0x66C, 0x00000000)
        handler.write_int32(0x678, 0x00000000)

        # Unlock Hard Mode and all characters and costumes from the start
        handler.write_int32(0x244, 0x00000000, NIFiles.OVERLAY_CHARACTER_SELECT)
        handler.write_int32(0x1DE4, 0x00000000, NIFiles.OVERLAY_NECRONOMICON)
        handler.write_int32(0x1E28, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        handler.write_int32(0x1FF8, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        handler.write_int32(0x2000, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        handler.write_int32(0x2008, 0x00000000, NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        handler.write_int32(0x96C, 0x240D4000, NIFiles.OVERLAY_CHARACTER_SELECT)
        handler.write_int32(0x994, 0x00000000, NIFiles.OVERLAY_CHARACTER_SELECT)
        handler.write_int32(0x9C0, 0x00000000, NIFiles.OVERLAY_CHARACTER_SELECT)
        handler.write_int32s(0x18E8, [0x3C0400FF,
                                       0x3484FF00,
                                       0x00045025], NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)
        handler.write_int32s(0x19A0, [0x3C0400FF,
                                       0x3484FF00,
                                       0x00044025], NIFiles.OVERLAY_FILE_SELECT_CONTROLLER)

        # NOP the store instructions that clear fields 0x02 in the actor entries
        # so the rando can use field 0x02 to "delete" actors.
        handler.write_int32(0xC232C, 0x00000000)
        handler.write_int32(0xC236C, 0x00000000)
        handler.write_int32(0xC300C, 0x00000000)
        handler.write_int32(0xC3284, 0x00000000)

        # Check for exactly 0x8000 in the first actor field to tell if the actor list should terminate rather than if
        # the 0x8000 flag is there, period. This will free it up for a different usage.
        handler.write_int32s(0xC28B0, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x544FFFCA])  # BNEL  V0, T7, [backward 0x36]
        handler.write_int32s(0xC2DAC, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x548FFFF5])  # BNEL  A0, T7, [backward 0x0B]
        handler.write_int32s(0xC2320, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x546FFFF8])  # BNEL  V1, T7, [backward 0x08]
        handler.write_int32s(0xC2360, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x546FFFF8])  # BNEL  V1, T7, [backward 0x08]
        handler.write_int32s(0xC2570, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x544FFFD6])  # BNEL  V0, T7, [backward 0x2A]
        handler.write_int32s(0xC3000, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x546FFFF8])  # BNEL  V1, T7, [backward 0x08]
        handler.write_int32s(0xC26C0, [0x00000000,   # NOP
                                        0x340F8000,   # ORI   T7, R0, 0x8000
                                        0x544FFFCA])  # BNEL  V0, T7, [backward 0x36]

        # Hack to check if an actor should spawn based on what "era" we're in (event flag 0x05BF being set or not).
        handler.write_int32(0xC2C30, 0x080FF3BC)  # J 0x803FCEF0
        handler.write_int32s(0xFFCEF0, patches.actor_era_spawn_checker)

        # Custom data-loading code
        handler.write_int32(0x18A94, 0x0800793D)  # J 0x8001E4F4
        handler.write_int32s(0x1F0F4, patches.custom_code_loader)

        # Custom remote item rewarding and DeathLink receiving code
        handler.write_int32(0x1C854, 0x080FF000)  # J 0x803FC000
        handler.write_int32s(0xFFC000, patches.remote_item_giver)
        handler.write_int32s(0xFFE190, patches.subweapon_surface_checker)

        # Make it possible to change the starting level.
        handler.write_byte(0x15D3, 0x10, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        handler.write_byte(0x15D5, 0x00, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)
        handler.write_byte(0x15DB, 0x10, NIFiles.OVERLAY_CS_INTRO_NARRATION_COMMON)

        # Prevent flags from pre-setting in Henry Mode.
        handler.write_byte(0x22F, 0x04, NIFiles.OVERLAY_HENRY_NG_INITIALIZER)

        # Give Henry all the time in the world just like everyone else.
        handler.write_byte(0x86DDF, 0x04)
        # Make the Henry warp jewels work for everyone at the expense of the light effect surrounding them.
        # The code that creates and renders it is exclusively inside Henry's overlay, so it must go for it to function
        # for the rest of the characters, sadly.
        handler.write_int32(0xF6A5C, 0x00000000)  # NOP

        # Lock the door in Foggy Lake below decks leading out to above decks with the Deck Key.
        # It's the same door in-universe as the above decks one but on a different map.
        handler.write_int16(0x7C1BD4, 0x5100)
        handler.write_int16(0x7C1BDC, 0x028E)
        handler.write_byte(0x7C1BE3, 0x22)
        handler.write_int16(0x7C1BE6, 0x0001)
        # Custom text for the new locked door instance.
        handler.write_bytes(0x7C1B14, cvlod_string_to_bytearray("Locked in!\n"
                                                                 "You need Deck Key.»\t"
                                                                 "Deck Key\n"
                                                                 "       has been used.»\t", wrap=False)[0])
        # Prevent the Foggy Lake cargo hold door from locking.
        handler.write_int16(0x7C1C00, 0x0000)

        # Disable the Foggy Lake Pier save jewel checking for one of the ship sinking cutscene flags to spawn.
        # To preserve the cutscene director's vision, we'll put it on our custom "not in a cutscene" check instead!
        handler.write_byte(0x7C67F5, 0x08)
        handler.write_int16(0x7C6806, 0x0000)
        handler.write_int32(0x7C6810, 0x803FCDBC)
        # Prevent the Sea Monster from respawning if you leave the pier map and return.
        handler.write_byte(0x7C67B5, 0x80)
        handler.write_int16(0x7C67C6, 0x015D)
        # Un-set the "debris path sunk" flag after the Sea Monster is killed and when the door flag is set.
        handler.write_int16(0x725A, 0x8040, NIFiles.OVERLAY_SEA_MONSTER)
        handler.write_int16(0x725E, 0xCB90, NIFiles.OVERLAY_SEA_MONSTER)
        handler.write_int32s(0xFFCB90, patches.sea_monster_sunk_path_flag_unsetter)
        # Disable the two pier statue items checking each other's flags being not set as an additional spawn condition.
        handler.write_byte(0x7C6815, 0x00)
        handler.write_int16(0x7C6826, 0x0000)
        handler.write_byte(0x7C6835, 0x00)
        handler.write_int16(0x7C6846, 0x0000)
        handler.write_byte(0x7C6855, 0x00)
        handler.write_int16(0x7C6866, 0x0000)
        handler.write_byte(0x7C6875, 0x00)
        handler.write_int16(0x7C6886, 0x0000)

        # Make coffins 01-04 in the Forest Charnel Houses never spawn items (as in, the RNG for them will never pass).
        handler.write_int32(0x76F440, 0x10000005)  # B [forward 0x05]
        # Make coffin 00 always try spawning the same consistent three items regardless of whether we previously broke
        # it or not and regardless of difficulty.
        handler.write_int32(0x76F478, 0x00000000)  # NOP-ed Hard difficulty check
        handler.write_byte(0x76FAC3, 0x00)  # No event flag set for coffin 00.
        handler.write_int32(0x76F4B4, 0x00000000)  # NOP-ed Not Easy difficulty check
        # Use the current loop iteration to tell what entry in the table to spawn.
        handler.write_int32(0x76F4D4, 0x264E0000)  # ADDIU T6, S2, 0x0000
        # Assign the event flags and remove the "vanish timer" flag on each of the three coffin item entries we'll use.
        handler.write_int16(0x774966, 0x0011)
        handler.write_byte(0x774969, 0x00)
        handler.write_int16(0x774972, 0x0012)
        handler.write_byte(0x774975, 0x00)
        handler.write_int16(0x7749C6, 0x0013)
        handler.write_byte(0x7749C9, 0x00)
        # Turn the Forest Henry child actor into a torch check with all necessary parameters assigned.
        handler.write_int16(0x7758DE, 0x0022)  # Dropped item flag ID
        handler.write_byte(0x7782D5, 0x00)     # Flag check unassignment
        handler.write_int16(0x7782E4, 0x01D9)  # Candle actor ID
        handler.write_int16(0x7782E6, 0x0000)  # Flag check unassignment
        handler.write_int16(0x7782E8, 0x0000)  # Flag check unassignment
        handler.write_int16(0x7782EC, 0x000C)  # Candle ID
        # Set Flag 0x23 on the item King Skeleton 2 leaves behind, and prevent it from being the possible Henry drop.
        handler.write_int32(0x43F8, 0x10000006, NIFiles.OVERLAY_KING_SKELETON)
        handler.write_int32s(0x444C, [0x3C088040,  # LUI   T0, 0x8040
                                       0x2508CBB0,  # ADDIU T0, T0, 0xCBB0
                                       0x0100F809,  # JALR  RA, T0
                                       0x00000000], NIFiles.OVERLAY_KING_SKELETON)
        handler.write_int32s(0xFFCBB0, patches.king_skeleton_chicken_flag_setter)
        # Add the backup King Skeleton jaws item that will spawn only if the player orphans it the first time.
        handler.write_byte(0x778415, 0x20)
        handler.write_int32s(0x778418, [0x3D000000, 0x00000000, 0xC4B2C000])
        handler.write_int16(0x778426, 0x002C)
        handler.write_int16(0x778428, 0x0023)
        handler.write_int16(0x77842A, 0x0000)
        # Make the drawbridge cutscene's end behavior its Henry end behavior for everyone.
        # The "drawbridge lowered" flag should be set so that Forest's regular end zone is easily accessible, and no
        # separate cutscene should play in the next map.
        handler.write_int32(0x1294, 0x1000000C, NIFiles.OVERLAY_CS_DRAWBRIDGE_LOWERS)

        # Make the final Cerberus in Villa Front Yard
        # un-set the Villa entrance portcullis closed flag for all characters (not just Henry).
        handler.write_int32(0x35A4, 0x00000000, NIFiles.OVERLAY_CERBERUS)

        # Give the Gardener his Cornell behavior for everyone.
        handler.write_int32(0x490, 0x24020002, NIFiles.OVERLAY_GARDENER)  # ADDIU V0, R0, 0x0002
        handler.write_int32(0xD20, 0x00000000, NIFiles.OVERLAY_GARDENER)
        handler.write_int32(0x13CC, 0x00000000, NIFiles.OVERLAY_GARDENER)

        # Give Child Henry his Cornell behavior for everyone.
        handler.write_int32(0x1B8, 0x24020002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU V0, R0, 0x0002
        handler.write_byte(0x613, 0x04, NIFiles.OVERLAY_CHILD_HENRY)
        handler.write_int32(0x844, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002
        handler.write_int32(0x8B8, 0x240F0002, NIFiles.OVERLAY_CHILD_HENRY)  # ADDIU T7, R0, 0x0002

        # Change the player spawn coordinates for Villa maze entrance 4 to put the player in front of the child escape
        # gate instead of the rear maze exit door.
        handler.write_int16s(0x10F876, [0x0290,   # Player X position
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
        handler.write_bytes(0x79712C, cvlod_string_to_bytearray("「 TIME GATE\n"
                                                                 "Present Her brooch\n"
                                                                 "to enter.\n"
                                                                 "    -Saint Germain」»\t", wrap=False)[0])
        handler.write_bytes(0x796FD6, cvlod_string_to_bytearray("Is that plaque referring\n"
                                                                 "to the Rose Brooch?\n"
                                                                 "You should find it...»\t")[0])

        # Make the escape gates check for the Rose Brooch in the player's inventory (without subtracting it) before
        # letting them through.
        handler.write_int32s(0xFFCF48, patches.rose_brooch_checker)
        # Malus gate
        handler.write_int16(0x797C0C, 0x0200)
        handler.write_int32(0x797C10, 0x803FCF48)
        handler.write_int16(0x797C38, 0x0200)
        handler.write_int32(0x797C3C, 0x803FCF48)
        # Henry gate
        handler.write_int16(0x797FD4, 0x0200)
        handler.write_int32(0x797FD8, 0x803FCF48)
        handler.write_int16(0x798000, 0x0200)
        handler.write_int32(0x798004, 0x803FCF48)

        # Add a new loading zone behind the "time gate" in the Villa maze. To do this, we'll have to relocate the map's
        # existing loading zone properties and update the pointer to them.
        handler.write_int32(0x110D50, 0x803FCF78)
        handler.write_bytes(0xFFCF78, handler.read_bytes(0x79807C, 0x3C))
        # Add the new loading zone property data on the end.
        handler.write_int32s(0xFFCFB4, [0x00000604, 0x03010000, 0x02D0001E, 0x023002BC, 0x00000208])
        # Replace the Hard-exclusive item in Malus's bush with the new loading zone actor.
        handler.write_int32s(0x799048, [0x00000000, 0x442E0000, 0x00000000, 0x44036000,
                                         0x01AF0000, 0x00000000, 0x00030000, 0x00000000])

        # Change the color of the fourth loading zone fade settings entry.
        handler.write_int32(0x110D2C, 0xE1B9FF00)
        # Era switcher hack
        handler.write_int32(0xD3C08, 0x080FF3F8)  # J 0x803FCFE0
        handler.write_int32s(0xFFCFE0, patches.era_switcher)

        # Change the map name display actor in the Villa crypt to use entry 0x02 instead of 0x11 and have entry 0x02
        # react to entrance 0x02 (the Villa end's).
        handler.write_byte(0x861, 0x02, NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        handler.write_byte(0x7D6561, 0x02)
        # Replace the second map name display settings entry for the Villa end with the one for our year text.
        handler.write_int32s(0x910, [0x00060100, 0x04642E00], NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        # Replace the far rear Iron Thorn Fenced Garden text spot with the new map name display actor.
        handler.write_int32s(0x7981E8, [0x00000000, 0x00000000, 0x00000000, 0x00000000,
                                         0x219F0000, 0x00000000, 0x00110000, 0x00000000])
        # Hack to change the map name display string to a custom year string when time traveling.
        handler.write_int16(0x3C6, 0x8040, NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        handler.write_int16(0x3CA, 0xD040, NIFiles.OVERLAY_MAP_NAME_DISPLAY)
        handler.write_int32s(0xFFD040, patches.map_name_year_switcher)
        # Year text for the above map name display hack.
        handler.write_bytes(0xFFD020, cvlod_string_to_bytearray("1852\t1844\t")[0])

        # Make Gilles De Rais spawn in the Villa crypt for everyone (not just Cornell).
        # This should instead be controlled by the actor list.
        handler.write_byte(0x195, 0x00, NIFiles.OVERLAY_GILLES_DE_RAIS)

        # Apply the child Henry gate checks to the two doors leading to the vampire crypt,
        # so he can't be brought in there.
        handler.write_byte(0x797BB4, 0x53)
        handler.write_int32(0x797BB8, 0x802E4C34)
        handler.write_byte(0x797D6C, 0x52)
        handler.write_int32(0x797D70, 0x802E4C34)

        # Make the Tunnel gondolas check for the Spider Women cutscene like they do in CV64.
        handler.write_int32(0x79B8CC, 0x0C0FF2F8)  # JAL	0x803FCBE0
        handler.write_int32s(0xFFCBE0, patches.gondola_spider_cutscene_checker)
        # Turn the Tunnel Henry child actor into a torch check with all necessary parameters assigned.
        handler.write_int16(0x79EF8E, 0x0024)  # Dropped item flag ID
        handler.write_byte(0x7A1469, 0x00)     # Flag check unassignment
        handler.write_int16(0x7A1478, 0x01D9)  # Candle actor ID
        handler.write_int16(0x7A147A, 0x0000)  # Flag check unassignment
        handler.write_int16(0x7A147C, 0x0000)  # Flag check unassignment
        handler.write_int16(0x7A147E, 0x0000)  # Rotation unassignment
        handler.write_int16(0x7A1480, 0x000F)  # Candle ID
        # Set the Tunnel end zone destination ID to the ID for the decoupled Spider Queen arena.
        handler.write_byte(0x79FD8F, 0x40)

        # Turn the Waterway Henry child actor into a torch check with all necessary parameters assigned.
        handler.write_int16(0x7A409E, 0x0025)  # Dropped item flag ID
        handler.write_byte(0x7A5759, 0x00)     # Flag check unassignment
        handler.write_int16(0x7A5768, 0x01D9)  # Candle actor ID
        handler.write_int16(0x7A576A, 0x0000)  # Flag check unassignment
        handler.write_int16(0x7A576C, 0x0000)  # Flag check unassignment
        handler.write_int16(0x7A576E, 0x0000)  # Rotation unassignment
        handler.write_int16(0x7A5770, 0x0000)  # Candle ID
        handler.write_int32(0x7A5774, 0x00000000)  # Removed special spawn check address
        # Set the Waterway end zone destination ID to the ID for the decoupled Medusa arena.
        handler.write_byte(0x7A4A0B, 0x80)

        # Make different Tunnel/Waterway boss arena end loading zones spawn depending on whether the 0x2A1 or 0x2A2
        # flags are set.
        handler.write_byte(0x7C87B5, 0x20)  # Flag check assignment
        handler.write_int16(0x7C87C6, 0x02A1)  # Tunnel flag ID
        handler.write_byte(0x7C87D5, 0x20)  # Flag check assignment
        handler.write_int16(0x7C87E6, 0x02A2)  # Underground Waterway flag ID

        # Turn the Outer Wall Henry child actor into a torch check with all necessary parameters assigned.
        handler.write_int16(0x833A9E, 0x0026)  # Dropped item flag ID
        handler.write_byte(0x834B15, 0x00)     # Flag check unassignment
        handler.write_int16(0x834B24, 0x01D9)  # Candle actor ID
        handler.write_int16(0x834B26, 0x0000)  # Flag check unassignment
        handler.write_int16(0x834B28, 0x0000)  # Flag check unassignment
        handler.write_int16(0x834B2A, 0x0000)  # Rotation unassignment
        handler.write_int16(0x834B2C, 0x0002)  # Candle ID
        handler.write_int32(0x834B30, 0x00000000)  # Removed special spawn check address
        # Make the Outer Wall end loading zone send you to the start of Art Tower instead of the fan map, as well as
        # heal the player.
        handler.write_int16(0x834448, 0x0001)
        handler.write_int16(0x83444A, 0x2500)

        # Make the Art Tower start loading zone send you to the end of The Outer Wall instead of the fan map.
        handler.write_int16(0x818DF2, 0x2A0B)
        # Make the loading zone leading from Art Tower museum -> conservatory slightly smaller.
        handler.write_int16(0x818E10, 0xFE18)
        # Change the player spawn coordinates coming from Art Tower conservatory -> museum to start them behind the
        # Key 2 door, so they will need Key 2 to come this way.
        handler.write_int16(0x1103E4, 0xFE22)  # Player Z position
        handler.write_int16(0x1103E8, 0x000D)  # Camera X position
        handler.write_int16(0x1103EC, 0xFE10)  # Camera Z position
        handler.write_int16(0x1103F2, 0xFE22)  # Focus point Z position
        # Prevent the Hell Knights in the middle Art Tower hallway from locking the doors until defeated.
        handler.write_byte(0x81A5B0, 0x00)
        handler.write_byte(0x81A5D0, 0x02)
        handler.write_byte(0x81A5F0, 0x02)
        # Put the left item on top of the Art Tower conservatory doorway on its correct flag.
        handler.write_int16(0x81DDB4, 0x02AF)
        # Prevent the middle item on top of the Art Tower conservatory doorway from self-modifying itself.
        handler.write_byte(0x81DD81, 0x80)
        handler.write_int32(0x81DD9C, 0x00000000)

        # Remove the Tower of Science item flag checks from the invisible Tower of Ruins statue items.
        # Yeah, your guess as to what the devs may have been thinking with this is as good as mine.
        handler.write_byte(0x808C65, 0x00)
        handler.write_int16(0x808C76, 0x0000)
        handler.write_byte(0x809185, 0x00)
        handler.write_int16(0x809196, 0x0000)
        # Clone the third Tower of Ruins gate actor and turn it around the other way. These actors normally only have
        # collision on one side, so if you were coming the other way you could very easily sequence break.
        handler.write_byte(0x809925, 0x00)     # Flag check unassignment
        handler.write_int32s(0x809928, [0x43DB0000, 0x42960000, 0x43100000])  # XYZ coordinates
        handler.write_int16(0x809934, 0x01B9)  # Special door actor ID
        handler.write_int16(0x809936, 0x0000)  # Flag check unassignment
        handler.write_int16(0x809938, 0x0000)  # Flag check unassignment
        handler.write_int16(0x80993A, 0x8000)  # Rotation
        handler.write_int16(0x80993C, 0x0002)  # Door ID
        # Set the Tower of Ruins end loading zone destination to the Castle Center top elevator White Jewel.
        handler.write_int16(0x8128EE, 0x0F03)

        # Make the Cornell intro cutscene actors in Castle Center spawn only when we are actually in a cutscene.
        handler.write_int32s(0xFFCDA0, patches.cutscene_active_checkers)
        # Basement
        handler.write_byte(0x7AA2A5, 0x0A)
        handler.write_int32(0x7AA2C0, 0x803FCDBC)
        handler.write_byte(0x7AA2C5, 0x0A)
        handler.write_int32(0x7AA2E0, 0x803FCDBC)
        handler.write_byte(0x7AA2E5, 0x0A)
        handler.write_int32(0x7AA300, 0x803FCDBC)
        handler.write_byte(0x7AA305, 0x0A)
        handler.write_int32(0x7AA320, 0x803FCDBC)
        handler.write_byte(0x7AA325, 0x0A)
        handler.write_int32(0x7AA340, 0x803FCDBC)
        handler.write_byte(0x7AA345, 0x0A)
        handler.write_int32(0x7AA360, 0x803FCDBC)
        handler.write_byte(0x7AA365, 0x08)
        handler.write_int32(0x7AA380, 0x803FCDBC)
        handler.write_byte(0x7AA405, 0x08)
        handler.write_int32(0x7AA420, 0x803FCDA0)
        handler.write_byte(0x7AA425, 0x08)
        handler.write_int32(0x7AA440, 0x803FCDA0)
        handler.write_byte(0x7AA445, 0x08)
        handler.write_int32(0x7AA460, 0x803FCDA0)
        handler.write_byte(0x7AA465, 0x08)
        handler.write_int32(0x7AA480, 0x803FCDA0)
        handler.write_byte(0x7AA485, 0x08)
        handler.write_int32(0x7AA4A0, 0x803FCDA0)
        handler.write_byte(0x7AA4A5, 0x08)
        handler.write_int32(0x7AA4C0, 0x803FCDA0)
        # Factory Floor
        handler.write_byte(0x7B1369, 0x08)
        handler.write_int32(0x7B1384, 0x803FCDA0)
        handler.write_byte(0x7B1389, 0x08)
        handler.write_int32(0x7B13A4, 0x803FCDA0)
        handler.write_byte(0x7B13A9, 0x08)
        handler.write_int32(0x7B13C4, 0x803FCDA0)
        handler.write_byte(0x7B13C9, 0x08)
        handler.write_int32(0x7B13E4, 0x803FCDA0)
        handler.write_byte(0x7B13E9, 0x08)
        handler.write_int32(0x7B1404, 0x803FCDA0)
        handler.write_byte(0x7B1429, 0x08)
        handler.write_int32(0x7B1444, 0x803FCDBC)
        handler.write_byte(0x7B1449, 0x08)
        handler.write_int32(0x7B1464, 0x803FCDBC)
        handler.write_byte(0x7B1469, 0x08)
        handler.write_int32(0x7B1484, 0x803FCDBC)
        # Lizard Lab
        handler.write_byte(0x7B4309, 0x88)
        handler.write_int32(0x7B4324, 0x803FCDBC)
        handler.write_byte(0x7B4349, 0x08)
        handler.write_int32(0x7B4364, 0x803FCDBC)
        handler.write_byte(0x7B4369, 0x08)
        handler.write_int32(0x7B4384, 0x803FCDBC)
        handler.write_byte(0x7B4389, 0x08)
        handler.write_int32(0x7B43A4, 0x803FCDBC)
        # Change some shelf decoration Nitros and Mandragoras into actual items.
        handler.write_int32(0x7A9BE8, 0xC0800000)  # X position
        handler.write_int32(0x7A9C08, 0xC0800000)  # X position
        handler.write_int16(0x7A9BF4, 0x0027)  # Interactable actor ID
        handler.write_int16(0x7A9C14, 0x0027)  # Interactable actor ID
        handler.write_int16(0x7A9BF8, 0x0346)  # Flag ID
        handler.write_int16(0x7A9C18, 0x0345)  # Flag ID
        handler.write_int32(0x7B8940, 0xC3A00000)  # X position
        handler.write_int32(0x7B89A0, 0xC3990000)  # X position
        handler.write_int16(0x7B894C, 0x0027)  # Interactable actor ID
        handler.write_int16(0x7B89AC, 0x0027)  # Interactable actor ID
        handler.write_int16(0x7B8950, 0x0347)  # Flag ID
        handler.write_int16(0x7B89B0, 0x0348)  # Flag ID
        handler.write_int16(0x7B8952, 0x0000)  # Param unassignment
        handler.write_int16(0x7B89B2, 0x0000)  # Param unassignment
        # Restore the Castle Center library bookshelf item by moving its actor entry into the main library actor list.
        handler.write_bytes(0x7B6620, handler.read_bytes(0x7B6720, 0x20))
        handler.write_byte(0x7B6621, 0x80)
        # Make the Castle Center post-Behemoth boss cutscenes trigger-able by anyone.
        handler.write_byte(0x118139, 0x00)
        handler.write_byte(0x118165, 0x00)
        # Fix both Castle Center elevator bridges for both characters unless enabling only one character's stages.
        # At which point one bridge will be always broken and one always repaired instead.
        handler.write_int32(0x7B938C, 0x51200004)  # BEQZL  T1, [forward 0x04]
        handler.write_byte(0x7B9B8D, 0x01)  # Reinhardt bridge
        handler.write_byte(0x7B9BAD, 0x01)  # Carrie bridge
        # if options.character_stages.value == options.character_stages.option_reinhardt_only:
        # handler.write_int32(0x6CEAA0, 0x240B0000)  # ADDIU T3, R0, 0x0000
        # elif options.character_stages.value == options.character_stages.option_carrie_only == 3:
        # handler.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
        # else:
        # handler.write_int32(0x6CEAA0, 0x240B0001)  # ADDIU T3, R0, 0x0001
        # handler.write_int32(0x6CEAA4, 0x240D0001)  # ADDIU T5, R0, 0x0001

        # Prevent taking Nitro or Mandragora through their shelf text.
        handler.write_int32(0x1F0, 0x240C0000, NIFiles.OVERLAY_TAKE_NITRO_TEXTBOX)  # ADDIU T4, R0, 0x0000
        handler.write_bytes(0x7B7406, cvlod_string_to_bytearray("Huh!? Someone super glued\n"
                                                                 "all these Magical Nitro bottles\n"
                                                                 "to the shelf!»\n"
                                                                 "Better find some elsewhere,\n"
                                                                 "lest you suffer the fate of an\n"
                                                                 "insane lunatic coyote in trying\n"
                                                                 "to force-remove one...»\t\t")[0])
        handler.write_int32(0x22C, 0x240F0000, NIFiles.OVERLAY_TAKE_MANDRAGORA_TEXTBOX)  # ADDIU T7, R0, 0x0000
        handler.write_bytes(0x7A8FFC, cvlod_string_to_bytearray("\tThese Mandragora bottles\n"
                                                                 "are empty, and a note was\n"
                                                                 "left behind:»\n"
                                                                 "\"Come 2035, and the Boss\n"
                                                                 "will be in for a very LOUD\n"
                                                                 "surprise! Hehehehe!\"»\n"
                                                                 "Whoever battles Dracula then\n"
                                                                 "may have an easy time...»\t")[0])

        # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes.
        handler.write_int32(0x128, 0x24020001, NIFiles.OVERLAY_VAMPIRE_SPAWNER)  # ADDIU V0, R0, 0x0001

        # Prevent throwing Nitro in the Hazardous Materials Disposals.
        handler.write_int32(0x1E4, 0x24020001, NIFiles.OVERLAY_NITRO_DISPOSAL_TEXTBOX)  # ADDIU V0, R0, 0x0001
        handler.write_bytes(0x7ADCCE, cvlod_string_to_bytearray("\t\"Hazardous materials disposal.\"»\n"
                                                                 "\"DO NOT OPERATE:\n"
                                                                 "Traces of gelatinous bloody "
                                                                 "tears need cleaning.\"»    \t")[0])
        handler.write_bytes(0x7B0770, cvlod_string_to_bytearray("\t\"Hazardous materials disposal.\"»\n"
                                                                 "\"DO NOT OPERATE:\n"
                                                                 "Jammed shut by repeated use "
                                                                 "from COWARDS.\"»     \t")[0])
        handler.write_bytes(0x7B2B2A, cvlod_string_to_bytearray("\t\"Hazardous materials disposal.\"»\n"
                                                                 "\"DO NOT OPERATE:\n"
                                                                 "Busted by Henrich attempting "
                                                                 "to escape through it.\"»  \t")[0])

        # Allow placing both bomb components at a cracked wall at once while having multiple copies of each, prevent
        # placing them at the downstairs crack altogether until the seal is removed, and enable placing both in one
        # interaction.
        handler.write_int32(0xEE8, 0x803FCD50, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x34A, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x34E, 0xCCC0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x38A, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x38E, 0xCCC0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x3F6, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x3FA, 0xCD00, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x436, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x43A, 0xCD00, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int32s(0xFFCCC0, patches.double_component_checker)
        handler.write_int32s(0xFFCD50, patches.basement_seal_checker)
        handler.write_int16(0x646, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x64A, 0xCDE0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x65E, 0x8040, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int16(0x662, 0xCDE0, NIFiles.OVERLAY_INGREDIENT_SET_TEXTBOX)
        handler.write_int32s(0xFFCDE0, patches.mandragora_with_nitro_setter)

        # Custom message for if you try checking the downstairs Castle Center crack before removing the seal.
        handler.write_bytes(0x7A924C, cvlod_string_to_bytearray("The Furious Nerd Curse\n"
                                                                 "prevents you from setting\n"
                                                                 "anything until the seal\n"
                                                                 "is removed!»\t")[0])

        # Disable the rapid flashing effect in the CC planetarium cutscene to ensure it won't trigger seizures.
        # TODO: Make this an option.
        #handler.write_int32(0xC5C, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xCD0, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xC64, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xC74, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xC80, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xC88, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xC90, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xC9C, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xCB4, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)
        #handler.write_int32(0xCC8, 0x00000000, NIFiles.OVERLAY_CC_PLANETARIUM_SOLVED_CS)

        # Make one of the lone turret room doors in Tower of Science display an unused message if you try to open it
        # before blowing up said turret.
        handler.write_byte(0x803E28, 0x00)
        handler.write_byte(0x803E54, 0x00)
        # Touch up the message to clarify the room number (to try and minimize confusion if the player approaches the
        # door from the other side).
        handler.write_bytes(0x803C12, cvlod_string_to_bytearray("Room 1\ncannon ")[0] +
                             handler.read_bytes(0x803C20, 0xE6))
        # Change the Security Crystal's play sound function call into a set song to play call when it tries to play its
        # music theme, so it will actually play correctly when coming in from a different stage with a different song.
        handler.write_int16(0x800526, 0x7274)
        # Make it so checking the Control Room doors will play the map's song, in the event the player tries going
        # backwards after killing the Security Crystal and having there be no music.
        handler.write_int16(0x803F74, 0x5300)
        handler.write_int32(0x803F78, 0x803FCE40)
        handler.write_int16(0x803FA0, 0x5300)
        handler.write_int32(0x803FA4, 0x803FCE40)
        handler.write_int32s(0xFFCE40, patches.door_map_music_player)

        # Make the Tower of Execution 3HB pillars with 1HB breakables not set their flags, and have said 1HB breakables
        # set the flags instead.
        handler.write_int16(0x7E0A66, 0x0000)
        handler.write_int16(0x7E0B26, 0x01B5)
        handler.write_int16(0x7E0A96, 0x0000)
        handler.write_int16(0x7E0B32, 0x01B8)

        # Make the Tower of Sorcery pink diamond always drop the same 3 items, prevent it from setting its own flag when
        # broken, and have it set individual flags on each of its drops.
        handler.write_int32(0x7DD624, 0x00106040)  # SLL   T4, S0, 1
        handler.write_int32(0x7DCE2C, 0x00000000)  # NOP
        handler.write_int32(0x7DCDFC, 0x0C0FF3A4)  # JAL   0x803FCE90
        handler.write_int32s(0xFFCE80, patches.pink_sorcery_diamond_customizer)

        # Lock the door in Clock Tower workshop leading out to the grand abyss map with Clocktower Key D.
        # It's the same door in-universe as Clocktower Door D but on a different map.
        handler.write_int16(0x82D104, 0x5300)
        handler.write_int16(0x82D130, 0x5300)
        handler.write_int32(0x82D108, 0x803FCEC0)
        handler.write_int32(0x82D134, 0x803FCED4)
        handler.write_int16(0x82D10C, 0x029E)
        handler.write_byte(0x82D113, 0x26)
        handler.write_int16(0x82D116, 0x0102)
        handler.write_int32s(0xFFCEC0, patches.clock_tower_workshop_text_modifier)
        # Custom text for the new locked door instance.
        handler.write_bytes(0x7C1B14, cvlod_string_to_bytearray("Locked in!\n"
                                                                 "You need Deck Key.»\t"
                                                                 "Deck Key\n"
                                                                 "       has been used.»\t", wrap=False)[0])

        # Prevent the Renon's Departure cutscene from triggering during the castle escape sequence.
        handler.write_byte(0x7CCFF1, 0x80)
        handler.write_int16(0x7CD002, 0x017D)

        # Hack to make the Forest, CW and Villa intro cutscenes play at the start of their levels no matter what map
        # came before them
        # #handler.write_int32(0x97244, 0x803FDD60)
        # #handler.write_int32s(0xBFDD60, patches.forest_cw_villa_intro_cs_player)

        # Make changing the map ID to 0xFF reset the map (helpful to work around a bug wherein the camera gets stuck
        # when entering a loading zone that doesn't change the map) or changing the map ID to 0x53 or 0x93 to go to a
        # decoupled version of the Spider Queen or Medusa arena respectively.
        handler.write_int32s(0x1C3B4, [0x0C0FF304,    # JAL   0x803FCC10
                                        0x24840008]),  # ADDIU A0, A0, 0x0008
        handler.write_int32s(0xFFCC10, patches.map_refresher)

        # Enable swapping characters when loading into a map by holding L.
        # handler.write_int32(0x97294, 0x803FDFC4)
        # handler.write_int32(0x19710, 0x080FF80E)  # J 0x803FE038
        # handler.write_int32s(0xBFDFC4, patches.character_changer)

        # Villa coffin time-of-day hack
        # handler.write_byte(0xD9D83, 0x74)
        # handler.write_int32(0xD9D84, 0x080FF14D)  # J 0x803FC534
        # handler.write_int32s(0xBFC534, patches.coffin_time_checker)

        # Enable being able to carry multiple Special jewels, Nitros, Mandragoras, and Key Items simultaneously
        # Special1
        handler.write_int32s(0x904B8, [0x90C8AB47,  # LBU   T0, 0xAB47 (A2)
                                        0x00681821,  # ADDU  V1, V1, T0
                                        0xA0C3AB47])  # SB    V1, 0xAB47 (A2)
        handler.write_int32(0x904C8, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Special2
        handler.write_int32s(0x904CC, [0x90C8AB48,  # LBU   T0, 0xAB48 (A2)
                                        0x00681821,  # ADDU  V1, V1, T0
                                        0xA0C3AB48])  # SB    V1, 0xAB48 (A2)
        handler.write_int32(0x904DC, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Special3 (NOP this one for usage as the AP item)
        handler.write_int32(0x904E8, 0x00000000)
        # Magical Nitro
        handler.write_int32(0x9071C, 0x10000004)  # B [forward 0x04]
        handler.write_int32s(0x90734, [0x25430001,  # ADDIU	V1, T2, 0x0001
                                        0x10000003])  # B [forward 0x03]
        # Mandragora
        handler.write_int32(0x906D4, 0x10000004)  # B [forward 0x04]
        handler.write_int32s(0x906EC, [0x25030001,  # ADDIU	V1, T0, 0x0001
                                        0x10000003])  # B [forward 0x03]
        # Key Items
        handler.write_byte(0x906C7, 0x63)
        # Increase Use Item capacity to 99 if "Increase Item Limit" is turned on
        if options["increase_item_limit"]:
            handler.write_byte(0x90617, 0x63)  # Most items
            handler.write_byte(0x90767, 0x63)  # Sun/Moon cards

        # Rename the Special3 to "AP Item"
        handler.write_bytes(0xB89AA, cvlod_string_to_bytearray("AP Item ")[0])
        # Change the Special3's appearance to that of a spinning contract.
        handler.write_int32s(0x11770A, [0x63583F80, 0x0000FFFF])
        # Disable spinning on the Special1 and 2 pickup models so colorblind people can more easily identify them.
        handler.write_byte(0x1176F5, 0x00)  # Special1
        handler.write_byte(0x117705, 0x00)  # Special2
        # Make the Special2 the same size as a Red jewel(L) to further distinguish them.
        handler.write_int32(0x1176FC, 0x3FA66666)
        # Capitalize the "k" in "Archives key" and "Rose Garden key" to be consistent with...
        # literally every other key name!
        handler.write_byte(0xB8AFF, 0x2B)
        handler.write_byte(0xB8BCB, 0x2B)
        # Make the "PowerUp" textbox appear even if you already have two.
        handler.write_int32(0x87E34, 0x00000000)  # NOP

        # Enable changing the item model/visibility on any item instance.
        handler.write_int32s(0x107740, [0x0C0FF0C0,  # JAL   0x803FC300
                                         0x25CFFFFF])  # ADDIU T7, T6, 0xFFFF
        handler.write_int32s(0xFFC300, patches.item_customizer)
        handler.write_int32(0x1078D0, 0x0C0FF0CB),  # JAL   0x803FC32C
        handler.write_int32s(0xFFC32C, patches.item_appearance_switcher)

        # Disable the 3HBs checking and setting flags when breaking them and enable their individual items checking and
        # setting flags instead.
        if options["multi_hit_breakables"]:
            handler.write_int16(0xE3488, 0x1000)
            handler.write_int32(0xE3800, 0x24050000)  # ADDIU	A1, R0, 0x0000
            handler.write_byte(0xE39EB, 0x00)
            handler.write_int32(0xE3A58, 0x0C0FF0D4),  # JAL   0x803FC350
            handler.write_int32s(0xFFC350, patches.three_hit_item_flags_setter)
            # Villa foyer chandelier-specific functions (yeah, KCEK was really insistent on having special handling just
            # for this one)
            handler.write_int32(0xE2F4C, 0x00000000)  # NOP
            handler.write_int32(0xE3114, 0x0C0FF0DE),  # JAL   0x803FC378
            handler.write_int32s(0xFFC378, patches.chandelier_item_flags_setter)

            # New flag values to put in each 3HB vanilla flag's spot
            handler.write_int16(0x7816F6, 0x02B8)  # CW upper rampart save nub
            handler.write_int16(0x78171A, 0x02BD)  # CW Dracula switch slab
            handler.write_int16(0x787F66, 0x0302)  # Villa foyer chandelier
            handler.write_int16(0x79F19E, 0x0307)  # Tunnel twin arrows rock
            handler.write_int16(0x79F1B6, 0x030C)  # Tunnel lonesome bucket pit rock
            handler.write_int16(0x7A41B6, 0x030F)  # UW poison parkour ledge
            handler.write_int16(0x7A41DA, 0x0315)  # UW skeleton crusher ledge
            handler.write_int16(0x7A8AF6, 0x0318)  # CC Behemoth crate
            handler.write_int16(0x7AD836, 0x031D)  # CC elevator pedestal
            handler.write_int16(0x7B0592, 0x0320)  # CC lizard locker slab
            handler.write_int16(0x7D0DDE, 0x0324)  # CT gear climb battery slab
            handler.write_int16(0x7D0DC6, 0x032A)  # CT gear climb top corner slab
            handler.write_int16(0x829A16, 0x032D)  # CT giant chasm farside climb
            handler.write_int16(0x82CC8A, 0x0330)  # CT beneath final slide

        # If the empty breakables are on, write all data associated with them.
        if options["empty_breakables"]:
            for offset in patches.empty_breakables_data:
                handler.write_bytes(offset, patches.empty_breakables_data[offset])

        # Kills the pointer to the Countdown number, resets the "in a demo?" value whenever changing/reloading the
        # game state, and mirrors the current game state value in a spot that's easily readable.
        handler.write_int32(0x1168, 0x08007938)  # J 0x8001E4E0
        handler.write_int32s(0x1F0E0, [0x3C08801D,  # LUI   T0, 0x801D
                                        0xA104AA30,  # SB    A0, 0xAA30 (T0)
                                        0xA100AA4A,  # SB    R0, 0xAA4A (T0)
                                        0x03E00008,  # JR    RA
                                        0xFD00AA40])  # SD    R0, 0xAA40 (T0)

        # Everything related to the Countdown counter.
        if options["countdown"]:
            handler.write_int32(0x1C670, 0x080FF141)  # J 0x803FC504
            handler.write_int32(0x1F11C, 0x080FF147)  # J 0x803FC51C
            handler.write_int32s(0xFFC3C0, patches.countdown_number_displayer)
            handler.write_int32s(0xFFC4D0, patches.countdown_number_manager)
            handler.write_int32(0x877E0, 0x080FF18D)  # J 0x803FC634
            handler.write_int32(0x878F0, 0x080FF188)  # J 0x803FC620
            handler.write_int32s(0x8BFF0, [0x0C0FF192,  # JAL 0x803FC648
                                            0xA2090000])  # SB  T1, 0x0000 (S0)
            handler.write_int32s(0x8C028, [0x0C0FF199,  # JAL 0x803FC664
                                            0xA20E0000])  # SB  T6, 0x0000 (S0)
            handler.write_int32(0x108D80, 0x0C0FF1A0)  # JAL 0x803FC680

        # Skip the "There is a white jewel" text so checking one saves the game instantly.
        # handler.write_int32s(0xEFC72, [0x00020002 for _ in range(37)])
        # handler.write_int32(0xA8FC0, 0x24020001)  # ADDIU V0, R0, 0x0001
        # Skip the yes/no prompts when activating things.
        # handler.write_int32s(0xBFDACC, patches.map_text_redirector)
        # handler.write_int32(0xA9084, 0x24020001)  # ADDIU V0, R0, 0x0001
        # handler.write_int32(0xBEBE8, 0x0C0FF6B4)  # JAL   0x803FDAD0
        # Skip Vincent and Heinrich's mandatory-for-a-check dialogue
        # handler.write_int32(0xBED9C, 0x0C0FF6DA)  # JAL   0x803FDB68
        # Skip the long yes/no prompt in the CC planetarium to set the pieces.
        # handler.write_int32(0xB5C5DF, 0x24030001)  # ADDIU  V1, R0, 0x0001
        # Skip the yes/no prompt to activate the CC elevator.
        # handler.write_int32(0xB5E3FB, 0x24020001)  # ADDIU  V0, R0, 0x0001
        # Skip the yes/no prompts to set Nitro/Mandragora at both walls.
        # handler.write_int32(0xB5DF3E, 0x24030001)  # ADDIU  V1, R0, 0x0001

        # handler.write_int32s(0xBFDD20, patches.special_descriptions_redirector)

        # Change the Stage Select menu options
        # handler.write_int32s(0xADF64, patches.warp_menu_rewrite)
        # handler.write_int32s(0x10E0C8, patches.warp_pointer_table)
        # for i in range(len(active_warp_list)):
        #    if i == 0:
        # handler.write_byte(warp_map_offsets[i], get_stage_info(active_warp_list[i], "start map id"))
        # handler.write_byte(warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "start spawn id"))
        #    else:
        # handler.write_byte(warp_map_offsets[i], get_stage_info(active_warp_list[i], "mid map id"))
        # handler.write_byte(warp_map_offsets[i] + 4, get_stage_info(active_warp_list[i], "mid spawn id"))

        # Play the "teleportation" sound effect when teleporting
        # handler.write_int32s(0xAE088, [0x08004FAB,  # J 0x80013EAC
        #                           0x2404019E])  # ADDIU A0, R0, 0x019E

        # Change the Stage Select menu's text to reflect its new purpose
        # handler.write_bytes(0xEFAD0, cvlod_string_to_bytearray(f"Where to...?\t{active_warp_list[0]}\t"
        #                                              f"`{w1} {active_warp_list[1]}\t"
        #                                              f"`{w2} {active_warp_list[2]}\t"
        #                                              f"`{w3} {active_warp_list[3]}\t"
        #                                              f"`{w4} {active_warp_list[4]}\t"
        #                                              f"`{w5} {active_warp_list[5]}\t"
        #                                              f"`{w6} {active_warp_list[6]}\t"
        #                                              f"`{w7} {active_warp_list[7]}"))

        # Lizard-man save proofing
        # handler.write_int32(0xA99AC, 0x080FF0B8)  # J 0x803FC2E0
        # handler.write_int32s(0xBFC2E0, patches.boss_save_stopper)

        # Disable or guarantee vampire Vincent's fight
        # if options.vincent_fight_condition.value == options.vincent_fight_condition.option_never:
        # handler.write_int32(0xAACC0, 0x24010001)  # ADDIU AT, R0, 0x0001
        # handler.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000
        # elif options.vincent_fight_condition.value == options.vincent_fight_condition.option_always:
        # handler.write_int32(0xAACE0, 0x24180010)  # ADDIU T8, R0, 0x0010
        # else:
        # handler.write_int32(0xAACE0, 0x24180000)  # ADDIU T8, R0, 0x0000

        # Disable or guarantee Renon's fight
        # handler.write_int32(0xAACB4, 0x080FF1A4)  # J 0x803FC690
        # if options.renon_fight_condition.value == options.renon_fight_condition.option_never:
        # handler.write_byte(0xB804F0, 0x00)
        # handler.write_byte(0xB80632, 0x00)
        # handler.write_byte(0xB807E3, 0x00)
        # handler.write_byte(0xB80988, 0xB8)
        # handler.write_byte(0xB816BD, 0xB8)
        # handler.write_byte(0xB817CF, 0x00)
        # handler.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
        # elif options.renon_fight_condition.value == options.renon_fight_condition.option_always:
        # handler.write_byte(0xB804F0, 0x0C)
        # handler.write_byte(0xB80632, 0x0C)
        # handler.write_byte(0xB807E3, 0x0C)
        # handler.write_byte(0xB80988, 0xC4)
        # handler.write_byte(0xB816BD, 0xC4)
        # handler.write_byte(0xB817CF, 0x0C)
        # handler.write_int32s(0xBFC690, patches.renon_cutscene_checker_jr)
        # else:
        # handler.write_int32s(0xBFC690, patches.renon_cutscene_checker)

        # NOP the Easy Mode check when buying a thing from Renon, so he can be triggered even on this mode.
        # handler.write_int32(0xBD8B4, 0x00000000)

        # Disable or guarantee the Bad Ending
        # if options.bad_ending_condition.value == options.bad_ending_condition.option_never:
        # handler.write_int32(0xAEE5C6, 0x3C0A0000)  # LUI  T2, 0x0000
        # elif options.bad_ending_condition.value == options.bad_ending_condition.option_always:
        # handler.write_int32(0xAEE5C6, 0x3C0A0040)  # LUI  T2, 0x0040

        # Play Castle Keep's song if teleporting in front of Dracula's door outside the escape sequence
        # handler.write_int32(0x6E937C, 0x080FF12E)  # J 0x803FC4B8
        # handler.write_int32s(0xBFC4B8, patches.ck_door_music_player)

        # Change the item healing values if "Nerf Healing" is turned on
        # if options.nerf_healing_items.value:
        # handler.write_byte(0xB56371, 0x50)  # Healing kit   (100 -> 80)
        # handler.write_byte(0xB56374, 0x32)  # Roast beef    ( 80 -> 50)
        # handler.write_byte(0xB56377, 0x19)  # Roast chicken ( 50 -> 25)

        # Disable loading zone healing if turned off
        # if not options.loading_zone_heals.value:
        # handler.write_byte(0xD99A5, 0x00)  # Skip all loading zone checks

        # Prevent the vanilla Magical Nitro transport's "can explode" flag from setting
        # handler.write_int32(0xB5D7AA, 0x00000000)  # NOP

        # Ensure the vampire Nitro check will always pass, so they'll never not spawn and crash the Villa cutscenes
        # handler.write_byte(0xA6253D, 0x03)

        # Enable the Game Over's "Continue" menu starting the cursor on whichever checkpoint is most recent
        handler.write_int32s(0x82120, [0x0C0FF2B4,  # JAL 0x803FCAD0
                                        0x91830024])  # LBU V1, 0x0024 (T4)
        handler.write_int32s(0xFFCAD0, patches.continue_cursor_start_checker)
        handler.write_int32(0x1D4A8, 0x080FF2C5)  # J   0x803FCB14
        handler.write_int32s(0xFFCB14, patches.savepoint_cursor_updater)
        handler.write_int32(0x1D344, 0x080FF2C0)  # J   0x803FCB00
        handler.write_int32s(0xFFCB00, patches.stage_start_cursor_updater)
        handler.write_byte(0x21C7, 0xFF, NIFiles.OVERLAY_GAME_OVER_SCREEN)
        # Multiworld buffer clearer/"death on load" safety checks.
        handler.write_int32s(0x1D314, [0x080FF2D0,  # J   0x803FCB40
                                        0x24040000])  # ADDIU A0, R0, 0x0000
        handler.write_int32s(0x1D3B4, [0x080FF2D0,  # J   0x803FCB40
                                        0x24040001])  # ADDIU A0, R0, 0x0001
        handler.write_int32s(0xFFCB40, patches.load_clearer)

        # Make the Special1 and 2 play sounds when you reach milestones with them.
        # handler.write_int32s(0xBFDA50, patches.special_sound_notifs)
        # handler.write_int32(0xBF240, 0x080FF694)  # J 0x803FDA50
        # handler.write_int32(0xBF220, 0x080FF69E)  # J 0x803FDA78

        # Add data for White Jewel #22 (the new Duel Tower savepoint) at the end of the White Jewel ID data list
        # handler.write_int16s(0x104AC8, [0x0000, 0x0006,
        #                            0x0013, 0x0015])

        # Fix a vanilla issue wherein saving in a character-exclusive stage as the other character would incorrectly
        # display the name of that character's equivalent stage on the save file instead of the one they're actually in.
        # handler.write_byte(0xC9FE3, 0xD4)
        # handler.write_byte(0xCA055, 0x08)
        # handler.write_byte(0xCA066, 0x40)
        # handler.write_int32(0xCA068, 0x860C17D0)  # LH T4, 0x17D0 (S0)
        # handler.write_byte(0xCA06D, 0x08)
        # handler.write_byte(0x104A31, 0x01)
        # handler.write_byte(0x104A39, 0x01)
        # handler.write_byte(0x104A89, 0x01)
        # handler.write_byte(0x104A91, 0x01)
        # handler.write_byte(0x104A99, 0x01)
        # handler.write_byte(0x104AA1, 0x01)

        # for stage in active_stage_exits:
        #    for offset in get_stage_info(stage, "save number offsets"):
        # handler.write_byte(offset, active_stage_exits[stage]["position"])

        # CC top elevator switch check
        # handler.write_int32(0x6CF0A0, 0x0C0FF0B0)  # JAL 0x803FC2C0
        # handler.write_int32s(0xBFC2C0, patches.elevator_flag_checker)

        # Disable time restrictions
        # if options.disable_time_restrictions.value:
        # Fountain
        # handler.write_int32(0x6C2340, 0x00000000)  # NOP
        # handler.write_int32(0x6C257C, 0x10000023)  # B [forward 0x23]
        # Rosa
        # handler.write_byte(0xEEAAB, 0x00)
        # handler.write_byte(0xEEAAD, 0x18)
        # Moon doors
        # handler.write_int32(0xDC3E0, 0x00000000)  # NOP
        # handler.write_int32(0xDC3E8, 0x00000000)  # NOP
        # Sun doors
        # handler.write_int32(0xDC410, 0x00000000)  # NOP
        # handler.write_int32(0xDC418, 0x00000000)  # NOP

        # Make received DeathLinks blow you to smithereens instead of kill you normally.
        # if options.death_link.value == options.death_link.option_explosive:
        # handler.write_int32(0x27A70, 0x10000008)  # B [forward 0x08]
        # handler.write_int32s(0xBFC0D0, patches.deathlink_nitro_edition)

        # Warp menu-opening code
        handler.write_int32(0x86FE4, 0x0C0FF254)  # JAL	0x803FC950
        handler.write_int32s(0xFFC950, patches.warp_menu_opener)

        # NPC item textbox hack
        handler.write_int32s(0xFFC6F0, patches.npc_item_hack)
        # Change all the NPC item gives to run through the new function.
        # Fountain Top Shine
        handler.write_int16(0x35E, 0x8040, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        handler.write_int16(0x362, 0xC700, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        handler.write_byte(0x367, 0x00, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        handler.write_int16(0x36E, 0x0068, NIFiles.OVERLAY_FOUNTAIN_TOP_SHINE_TEXTBOX)
        handler.write_bytes(0x720, cvlod_string_to_bytearray("...»\t")[0], 371)
        # 6am Rose Patch
        handler.write_int16(0x1E2, 0x8040, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        handler.write_int16(0x1E6, 0xC700, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        handler.write_byte(0x1EB, 0x01, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        handler.write_int16(0x1F2, 0x0078, NIFiles.OVERLAY_6AM_ROSE_PATCH_TEXTBOX)
        handler.write_bytes(0x380, cvlod_string_to_bytearray("...»\t")[0], 370)
        # Vincent
        handler.write_int16(0x180E, 0x8040, NIFiles.OVERLAY_VINCENT)
        handler.write_int16(0x1812, 0xC700, NIFiles.OVERLAY_VINCENT)
        handler.write_byte(0x1817, 0x02, NIFiles.OVERLAY_VINCENT)
        handler.write_int16(0x181E, 0x027F, NIFiles.OVERLAY_VINCENT)
        handler.write_bytes(0x78E776, cvlod_string_to_bytearray(" " * 173, wrap=False)[0])
        # Mary
        handler.write_int16(0xB16, 0x8040, NIFiles.OVERLAY_MARY)
        handler.write_int16(0xB1A, 0xC700, NIFiles.OVERLAY_MARY)
        handler.write_byte(0xB1F, 0x03, NIFiles.OVERLAY_MARY)
        handler.write_int16(0xB26, 0x0086, NIFiles.OVERLAY_MARY)
        handler.write_bytes(0x78F40E, cvlod_string_to_bytearray(" " * 295, wrap=False)[0])
        # Heinrich
        handler.write_int16(0x962A, 0x8040, NIFiles.OVERLAY_LIZARD_MEN)
        handler.write_int16(0x962E, 0xC700, NIFiles.OVERLAY_LIZARD_MEN)
        handler.write_byte(0x9633, 0x04, NIFiles.OVERLAY_LIZARD_MEN)
        handler.write_int16(0x963A, 0x0284, NIFiles.OVERLAY_LIZARD_MEN)
        handler.write_bytes(0x7B3210, cvlod_string_to_bytearray(" " * 415, wrap=False)[0])

        # Sub-weapon check function hook
        # handler.write_int32(0xBF32C, 0x00000000)  # NOP
        # handler.write_int32(0xBF330, 0x080FF05E)  # J	0x803FC178
        # handler.write_int32s(0xBFC178, patches.give_subweapon_stopper)

        # Warp menu Special1 restriction
        # handler.write_int32(0xADD68, 0x0C04AB12)  # JAL 0x8012AC48
        # handler.write_int32s(0xADE28, patches.stage_select_overwrite)
        # handler.write_byte(0xADE47, s1s_per_warp)

        # Dracula's door text pointer hijack
        # handler.write_int32(0xD69F0, 0x080FF141)  # J 0x803FC504
        # handler.write_int32s(0xBFC504, patches.dracula_door_text_redirector)

        # Dracula's chamber condition
        # handler.write_int32(0xE2FDC, 0x0804AB25)  # J 0x8012AC78
        # handler.write_int32s(0xADE84, patches.special_goal_checker)
        # handler.write_bytes(0xBFCC48, [0xA0, 0x00, 0xFF, 0xFF, 0xA0, 0x01, 0xFF, 0xFF, 0xA0, 0x02, 0xFF, 0xFF, 0xA0, 0x03, 0xFF,
        #                           0xFF, 0xA0, 0x04, 0xFF, 0xFF, 0xA0, 0x05, 0xFF, 0xFF, 0xA0, 0x06, 0xFF, 0xFF, 0xA0, 0x07,
        #                           0xFF, 0xFF, 0xA0, 0x08, 0xFF, 0xFF, 0xA0, 0x09])
        # if options.draculas_condition.value == options.draculas_condition.option_crystal:
        # handler.write_int32(0x6C8A54, 0x0C0FF0C1)  # JAL 0x803FC304
        # handler.write_int32s(0xBFC304, patches.crystal_special2_giver)
        # handler.write_bytes(0xBFCC6E, cvlod_string_to_bytearray(f"It won't budge!\n"
        #                                                   f"You'll need the power\n"
        #                                                   f"of the basement crystal\n"
        #                                                   f"to undo the seal.", True))
        #    special2_name = "Crystal "
        #    special2_text = "The crystal is on!\n" \
        #                    "Time to teach the old man\n" \
        #                    "a lesson!"
        # elif options.draculas_condition.value == options.draculas_condition.option_bosses:
        # handler.write_int32(0xBBD50, 0x080FF18C)  # J	0x803FC630
        # handler.write_int32s(0xBFC630, patches.boss_special2_giver)
        # handler.write_bytes(0xBFCC6E, cvlod_string_to_bytearray(f"It won't budge!\n"
        #                                                   f"You'll need to defeat\n"
        #                                                   f"{required_s2s} powerful monsters\n"
        #                                                   f"to undo the seal.", True))
        #    special2_name = "Trophy  "
        #    special2_text = f"Proof you killed a powerful\n" \
        #                    f"Night Creature. Earn {required_s2s}/{total_s2s}\n" \
        #                    f"to battle Dracula."
        # elif options.draculas_condition.value == options.draculas_condition.option_specials:
        #    special2_name = "Special2"
        # handler.write_bytes(0xBFCC6E, cvlod_string_to_bytearray(f"It won't budge!\n"
        #                                                   f"You'll need to find\n"
        #                                                   f"{required_s2s} Special2 jewels\n"
        #                                                   f"to undo the seal.", True))
        #    special2_text = f"Need {required_s2s}/{total_s2s} to kill Dracula.\n" \
        #                    f"Looking closely, you see...\n" \
        #                    f"a piece of him within?"
        # else:
        #    #handler.write_byte(0xADE8F, 0x00)
        #    special2_name = "Special2"
        #    special2_text = "If you're reading this,\n" \
        #                    "how did you get a Special2!?"
        # handler.write_byte(0xADE8F, required_s2s)
        # Change the Special2 name depending on the setting.
        # handler.write_bytes(0xEFD4E, cvlod_string_to_bytearray(special2_name))
        # Change the Special1 and 2 menu descriptions to tell you how many you need to unlock a warp and fight Dracula
        # respectively.
        # special_text_bytes = cvlod_string_to_bytearray(f"{s1s_per_warp} per warp unlock.\n"
        #                                          f"{options.total_special1s.value} exist in total.\n"
        #                                          f"Z + R + START to warp.") + \
        #                     cvlod_string_to_bytearray(special2_text)
        # handler.write_bytes(0xBFE53C, special_text_bytes)

        # On-the-fly TLB script modifier
        # handler.write_int32s(0xBFC338, patches.double_component_checker)
        # handler.write_int32s(0xBFC3D4, patches.downstairs_seal_checker)
        # handler.write_int32s(0xBFE074, patches.mandragora_with_nitro_setter)
        # handler.write_int32s(0xBFC700, patches.overlay_modifiers)

        # On-the-fly actor data modifier hook
        # handler.write_int32(0xEAB04, 0x080FF21E)  # J 0x803FC878
        # handler.write_int32s(0xBFC870, patches.map_data_modifiers)

        # Fix to make flags apply to freestanding invisible items properly
        # handler.write_int32(0xA84F8, 0x90CC0039)  # LBU T4, 0x0039 (A2)

        # Fix locked doors to check the key counters instead of their vanilla key locations' bitflags
        # Pickup flag check modifications:
        # handler.write_int32(0x10B2D8, 0x00000002)  # Left Tower Door
        # handler.write_int32(0x10B2F0, 0x00000003)  # Storeroom Door
        # handler.write_int32(0x10B2FC, 0x00000001)  # Archives Door
        # handler.write_int32(0x10B314, 0x00000004)  # Maze Gate
        # handler.write_int32(0x10B350, 0x00000005)  # Copper Door
        # handler.write_int32(0x10B3A4, 0x00000006)  # Torture Chamber Door
        # handler.write_int32(0x10B3B0, 0x00000007)  # ToE Gate
        # handler.write_int32(0x10B3BC, 0x00000008)  # Science Door1
        # handler.write_int32(0x10B3C8, 0x00000009)  # Science Door2
        # handler.write_int32(0x10B3D4, 0x0000000A)  # Science Door3
        # handler.write_int32(0x6F0094, 0x0000000B)  # CT Door 1
        # handler.write_int32(0x6F00A4, 0x0000000C)  # CT Door 2
        # handler.write_int32(0x6F00B4, 0x0000000D)  # CT Door 3
        # Item counter decrement check modifications:
        # handler.write_int32(0xEDA84, 0x00000001)  # Archives Door
        # handler.write_int32(0xEDA8C, 0x00000002)  # Left Tower Door
        # handler.write_int32(0xEDA94, 0x00000003)  # Storeroom Door
        # handler.write_int32(0xEDA9C, 0x00000004)  # Maze Gate
        # handler.write_int32(0xEDAA4, 0x00000005)  # Copper Door
        # handler.write_int32(0xEDAAC, 0x00000006)  # Torture Chamber Door
        # handler.write_int32(0xEDAB4, 0x00000007)  # ToE Gate
        # handler.write_int32(0xEDABC, 0x00000008)  # Science Door1
        # handler.write_int32(0xEDAC4, 0x00000009)  # Science Door2
        # handler.write_int32(0xEDACC, 0x0000000A)  # Science Door3
        # handler.write_int32(0xEDAD4, 0x0000000B)  # CT Door 1
        # handler.write_int32(0xEDADC, 0x0000000C)  # CT Door 2
        # handler.write_int32(0xEDAE4, 0x0000000D)  # CT Door 3

        # Fix ToE gate's "unlocked" flag in the locked door flags table
        # handler.write_int16(0x10B3B6, 0x0001)

        # handler.write_int32(0x10AB2C, 0x8015FBD4)  # Maze Gates' check code pointer adjustments
        # handler.write_int32(0x10AB40, 0x8015FBD4)
        # handler.write_int32s(0x10AB50, [0x0D0C0000,
        #                            0x8015FBD4])
        # handler.write_int32s(0x10AB64, [0x0D0C0000,
        #                            0x8015FBD4])
        # handler.write_int32s(0xE2E14, patches.normal_door_hook)
        # handler.write_int32s(0xBFC5D0, patches.normal_door_code)
        # handler.write_int32s(0x6EF298, patches.ct_door_hook)
        # handler.write_int32s(0xBFC608, patches.ct_door_code)
        # Fix key counter not decrementing if 2 or above
        # handler.write_int32(0xAA0E0, 0x24020000)  # ADDIU	V0, R0, 0x0000

        # Make the Easy-only candle drops in Room of Clocks appear on any difficulty
        # handler.write_byte(0x9B518F, 0x01)

        # Slightly move some once-invisible freestanding items to be more visible
        # if options.invisible_items.value == options.invisible_items.option_reveal_all:
        # handler.write_byte(0x7C7F95, 0xEF)  # Forest dirge maiden statue
        # handler.write_byte(0x7C7FA8, 0xAB)  # Forest werewolf statue
        # handler.write_byte(0x8099C4, 0x8C)  # Villa courtyard tombstone
        # handler.write_byte(0x83A626, 0xC2)  # Villa living room painting
        # #handler.write_byte(0x83A62F, 0x64)  # Villa Mary's room table
        # handler.write_byte(0xBFCB97, 0xF5)  # CC torture instrument rack
        # handler.write_byte(0x8C44D5, 0x22)  # CC red carpet hallway knight
        # handler.write_byte(0x8DF57C, 0xF1)  # CC cracked wall hallway flamethrower
        # handler.write_byte(0x90FCD6, 0xA5)  # CC nitro hallway flamethrower
        # handler.write_byte(0x90FB9F, 0x9A)  # CC invention room round machine
        # handler.write_byte(0x90FBAF, 0x03)  # CC invention room giant famicart
        # handler.write_byte(0x90FE54, 0x97)  # CC staircase knight (x)
        # handler.write_byte(0x90FE58, 0xFB)  # CC staircase knight (z)

        # Make the torch directly behind Dracula's chamber that normally doesn't set a flag set bitflag 0x08 in 0x80389BFA
        # handler.write_byte(0x10CE9F, 0x01)

        # Change the CC post-Behemoth boss depending on the option for Post-Behemoth Boss
        # if options.post_behemoth_boss.value == options.post_behemoth_boss.option_inverted:
        # handler.write_byte(0xEEDAD, 0x02)
        # handler.write_byte(0xEEDD9, 0x01)
        # elif options.post_behemoth_boss.value == options.post_behemoth_boss.option_always_rosa:
        # handler.write_byte(0xEEDAD, 0x00)
        # handler.write_byte(0xEEDD9, 0x03)
        # Put both on the same flag so changing character won't trigger a rematch with the same boss.
        # handler.write_byte(0xEED8B, 0x40)
        # elif options.post_behemoth_boss.value == options.post_behemoth_boss.option_always_camilla:
        # handler.write_byte(0xEEDAD, 0x03)
        # handler.write_byte(0xEEDD9, 0x00)
        # handler.write_byte(0xEED8B, 0x40)

        # Change the RoC boss depending on the option for Room of Clocks Boss
        # if options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_inverted:
        # handler.write_byte(0x109FB3, 0x56)
        # handler.write_byte(0x109FBF, 0x44)
        # handler.write_byte(0xD9D44, 0x14)
        # handler.write_byte(0xD9D4C, 0x14)
        # elif options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_always_death:
        # handler.write_byte(0x109FBF, 0x44)
        # handler.write_byte(0xD9D45, 0x00)
        # Put both on the same flag so changing character won't trigger a rematch with the same boss.
        # handler.write_byte(0x109FB7, 0x90)
        # handler.write_byte(0x109FC3, 0x90)
        # elif options.room_of_clocks_boss.value == options.room_of_clocks_boss.option_always_actrise:
        # handler.write_byte(0x109FB3, 0x56)
        # handler.write_int32(0xD9D44, 0x00000000)
        # handler.write_byte(0xD9D4D, 0x00)
        # handler.write_byte(0x109FB7, 0x90)
        # handler.write_byte(0x109FC3, 0x90)

        # Tunnel gondola skip
        # if options.skip_gondolas.value:
        # handler.write_int32(0x6C5F58, 0x080FF7D0)  # J 0x803FDF40
        # handler.write_int32s(0xBFDF40, patches.gondola_skipper)
        # New gondola transfer point candle coordinates
        # handler.write_byte(0xBFC9A3, 0x04)
        # handler.write_bytes(0x86D824, [0x27, 0x01, 0x10, 0xF7, 0xA0])

        # Waterway brick platforms skip
        # if options.skip_waterway_blocks.value:
        # handler.write_int32(0x6C7E2C, 0x00000000)  # NOP

        # Ambience silencing fix
        handler.write_int32(0x1BB20, 0x080FF280)  # J 0x803FCA00
        handler.write_int32s(0xFFCA00, patches.ambience_silencer)
        # Fix for the door sliding sound playing infinitely if leaving the fan meeting room before the door closes entirely.
        # Hooking this in the ambience silencer code does nothing for some reason.
        # handler.write_int32s(0xAE10C, [0x08004FAB,  # J   0x80013EAC
        #                           0x3404829B])  # ORI A0, R0, 0x829B
        # handler.write_int32s(0xD9E8C, [0x08004FAB,  # J   0x80013EAC
        #                           0x3404829B])  # ORI A0, R0, 0x829B
        # Fan meeting room ambience fix
        # handler.write_int32(0x109964, 0x803FE13C)

        # Increase shimmy speed
        # if options.increase_shimmy_speed.value:
        # handler.write_byte(0xA4241, 0x5A)

        # Disable landing fall damage
        # if options.fall_guard.value:
        # handler.write_byte(0x27B23, 0x00)

        # Permanent PowerUp stuff
        # if options.permanent_powerups.value:
        # Make receiving PowerUps increase the unused menu PowerUp counter instead of the one outside the save struct
        # handler.write_int32(0xBF2EC, 0x806B619B)  # LB	T3, 0x619B (V1)
        # handler.write_int32(0xBFC5BC, 0xA06C619B)  # SB	T4, 0x619B (V1)
        # Make Reinhardt's whip check the menu PowerUp counter
        # handler.write_int32(0x69FA08, 0x80CC619B)  # LB	T4, 0x619B (A2)
        # handler.write_int32(0x69FBFC, 0x80C3619B)  # LB	V1, 0x619B (A2)
        # handler.write_int32(0x69FFE0, 0x818C9C53)  # LB	T4, 0x9C53 (T4)
        # Make Carrie's orb check the menu PowerUp counter
        # handler.write_int32(0x6AC86C, 0x8105619B)  # LB	A1, 0x619B (T0)
        # handler.write_int32(0x6AC950, 0x8105619B)  # LB	A1, 0x619B (T0)
        # handler.write_int32(0x6AC99C, 0x810E619B)  # LB	T6, 0x619B (T0)
        # handler.write_int32(0x5AFA0, 0x80639C53)  # LB	V1, 0x9C53 (V1)
        # handler.write_int32(0x5B0A0, 0x81089C53)  # LB	T0, 0x9C53 (T0)
        # handler.write_byte(0x391C7, 0x00)  # Prevent PowerUps from dropping from regular enemies
        # handler.write_byte(0xEDEDF, 0x03)  # Make any vanishing PowerUps that do show up L jewels instead
        # Rename the PowerUp to "PermaUp"
        # handler.write_bytes(0xEFDEE, cvlod_string_to_bytearray("PermaUp"))
        # Replace the PowerUp in the Forest Special1 Bridge 3HB rock with an L jewel if 3HBs aren't randomized
        #    if not options.multi_hit_breakables.value:
        # handler.write_byte(0x10C7A1, 0x03)
        # Change the appearance of the Pot-Pourri to that of a larger PowerUp regardless of the above setting, so other
        # game PermaUps are distinguishable.
        # handler.write_int32s(0xEE558, [0x06005F08, 0x3FB00000, 0xFFFFFF00])

        # Write the randomized (or disabled) music ID list and its associated code
        # if options.background_music.value:
        # handler.write_int32(0x14588, 0x08060D60)  # J 0x80183580
        # handler.write_int32(0x14590, 0x00000000)  # NOP
        # handler.write_int32s(0x106770, patches.music_modifier)
        # handler.write_int32(0x15780, 0x0C0FF36E)  # JAL 0x803FCDB8
        # handler.write_int32s(0xBFCDB8, patches.music_comparer_modifier)

        # Once-per-frame gameplay checks
        # handler.write_int32(0x6C848, 0x080FF40D)  # J 0x803FD034
        # handler.write_int32(0xBFD058, 0x0801AEB5)  # J 0x8006BAD4

        # Everything related to dropping the previous sub-weapon
        # if options.drop_previous_sub_weapon.value:
        # handler.write_int32(0xBFD034, 0x080FF3FF)  # J 0x803FCFFC
        # handler.write_int32(0xBFC18C, 0x080FF3F2)  # J 0x803FCFC8
        # handler.write_int32s(0xBFCFC4, patches.prev_subweapon_spawn_checker)
        # handler.write_int32s(0xBFCFFC, patches.prev_subweapon_fall_checker)
        # handler.write_int32s(0xBFD060, patches.prev_subweapon_dropper)

        # Ice Trap stuff
        # handler.write_int32(0x697C60, 0x080FF06B)  # J 0x803FC18C
        # handler.write_int32(0x6A5160, 0x080FF06B)  # J 0x803FC18C
        # handler.write_int32s(0xBFC1AC, patches.ice_trap_initializer)
        # handler.write_int32s(0xBFC1D8, patches.the_deep_freezer)
        # handler.write_int32s(0xB2F354, [0x3739E4C0,  # ORI T9, T9, 0xE4C0
        #                            0x03200008,  # JR  T9
        #                            0x00000000])  # NOP
        # handler.write_int32s(0xBFE4C0, patches.freeze_verifier)

        # Initial Countdown numbers and Start Inventory
        handler.write_int32(0x90DBC, 0x080FF200)  # J	0x803FC800
        handler.write_int32s(0xFFC800, patches.new_game_extras)

        # Everything related to shopsanity
        # if options.shopsanity.value:
        # handler.write_bytes(0x103868, cvlod_string_to_bytearray("Not obtained. "))
        # handler.write_int32s(0xBFD8D0, patches.shopsanity_stuff)
        # handler.write_int32(0xBD828, 0x0C0FF643)  # JAL	0x803FD90C
        # handler.write_int32(0xBD5B8, 0x0C0FF651)  # JAL	0x803FD944
        # handler.write_int32(0xB0610, 0x0C0FF665)  # JAL	0x803FD994
        # handler.write_int32s(0xBD24C, [0x0C0FF677,  # J  	0x803FD9DC
        #                               0x00000000])  # NOP
        # handler.write_int32(0xBD618, 0x0C0FF684)  # JAL	0x803FDA10

        # Panther Dash running
        # if options.panther_dash.value:
        # handler.write_int32(0x69C8C4, 0x0C0FF77E)  # JAL   0x803FDDF8
        # handler.write_int32(0x6AA228, 0x0C0FF77E)  # JAL   0x803FDDF8
        # handler.write_int32s(0x69C86C, [0x0C0FF78E,  # JAL   0x803FDE38
        #                            0x3C01803E])  # LUI   AT, 0x803E
        # handler.write_int32s(0x6AA1D0, [0x0C0FF78E,  # JAL   0x803FDE38
        #                            0x3C01803E])  # LUI   AT, 0x803E
        # handler.write_int32(0x69D37C, 0x0C0FF79E)  # JAL   0x803FDE78
        # handler.write_int32(0x6AACE0, 0x0C0FF79E)  # JAL   0x803FDE78
        # handler.write_int32s(0xBFDDF8, patches.panther_dash)
        # Jump prevention
        # if options.panther_dash.value == options.panther_dash.option_jumpless:
        # handler.write_int32(0xBFDE2C, 0x080FF7BB)  # J     0x803FDEEC
        # handler.write_int32(0xBFD044, 0x080FF7B1)  # J     0x803FDEC4
        # handler.write_int32s(0x69B630, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8CCD0000])  # LW    T5, 0x0000 (A2)
        # handler.write_int32s(0x6A8EC0, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8CCC0000])  # LW    T4, 0x0000 (A2)
        # Fun fact: KCEK put separate code to handle coyote time jumping
        # handler.write_int32s(0x69910C, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8C4E0000])  # LW    T6, 0x0000 (V0)
        # handler.write_int32s(0x6A6718, [0x0C0FF7C6,  # JAL   0x803FDF18
        #                                0x8C4E0000])  # LW    T6, 0x0000 (V0)
        # handler.write_int32s(0xBFDEC4, patches.panther_jump_preventer)

        # Write all the actor list spawn condition edits that we apply always (things like difficulty items, etc.).
        for offset in patches.always_actor_edits:
            handler.write_byte(offset, patches.always_actor_edits[offset])
        for start_addr in patches.era_specific_actors:
            era_statuses = patches.era_specific_actors[start_addr]
            for actor_number in era_statuses:
                curr_addr = start_addr + (actor_number * 0x20)
                byte_to_alter = handler.read_byte(curr_addr)
                if era_statuses[actor_number]:
                    byte_to_alter |= 0x78
                else:
                    byte_to_alter |= 0xF8
                handler.write_byte(curr_addr, byte_to_alter)

        # Make the lever checks for Cornell always pass
        handler.write_int32(0xE6C18, 0x240A0002)  # ADDIU T2, R0, 0x0002
        handler.write_int32(0xE6F64, 0x240E0002)  # ADDIU T6, R0, 0x0002
        handler.write_int32(0xE70F4, 0x240D0002)  # ADDIU T5, R0, 0x0002
        handler.write_int32(0xE7364, 0x24080002)  # ADDIU T0, R0, 0x0002
        handler.write_int32(0x109C10, 0x240E0002)  # ADDIU T6, R0, 0x0002

        # Make the fountain pillar checks for Cornell always pass
        handler.write_int32(0xD77E0, 0x24030002)  # ADDIU V1, R0, 0x0002
        handler.write_int32(0xD7A60, 0x24030002)  # ADDIU V1, R0, 0x0002

        # Make only some rose garden checks for Cornell always pass
        handler.write_byte(0x78619B, 0x24)
        handler.write_int16(0x7861A0, 0x5423)
        handler.write_int32(0x786324, 0x240E0002)  # ADDIU T6, R0, 0x0002
        # Make the thirsty J. A. Oldrey cutscene check for Cornell always pass
        handler.write_byte(0x11831D, 0x00)
        # Make the Villa coffin lid Henry checks never pass
        handler.write_byte(0x7D45FB, 0x04)
        handler.write_byte(0x7D4BFB, 0x04)
        # Make the Villa coffin loading zone Henry check always pass
        handler.write_int32(0xD3A78, 0x000C0821)  # ADDU  AT, R0, T4
        # Make the Villa coffin lid Cornell attack collision check always pass
        handler.write_int32(0x7D4D9C, 0x00000000)  # NOP
        # Make the Villa coffin lid Cornell cutscene check never pass
        handler.write_byte(0x7D518F, 0x04)
        # Make the hardcoded Cornell check in the Villa crypt Reinhardt/Carrie first vampire intro cutscene not pass.
        # IDK what KCEK was planning here, since Cornell normally doesn't get this cutscene, but if it passes the game
        # completely ceases functioning.
        handler.write_int16(0x230, 0x1000, NIFiles.OVERLAY_CS_1ST_REIN_CARRIE_CRYPT_VAMPIRE)

        # Change Oldrey's Diary into an item location.
        handler.write_int16(0x792A24, 0x0027)
        handler.write_int16(0x792A28, 0x0084)
        handler.write_byte(0x792A2D, 0x17)
        # Change the Maze Henry Mode kid into a location.
        handler.write_int32s(0x798CF8, [0x01D90000, 0x00000000, 0x000C0000])
        handler.write_byte(0x796D4F, 0x87)

        # Move the following Locations that have flags shared with other Locations to their own flags.
        handler.write_int16(0x792A48, 0x0085)  # Archives Garden Key
        handler.write_int16(0xAAA, 0x0086, NIFiles.OVERLAY_MARY)  # Mary's Copper Key
        handler.write_int16(0xAE2, 0x0086, NIFiles.OVERLAY_MARY)
        handler.write_int16(0xB12, 0x0086, NIFiles.OVERLAY_MARY)

        # Write "Z + R + START" over the Special1 description.
        handler.write_bytes(0x3B7C, cvlod_string_to_bytearray("Z + R + START\t")[0], NIFiles.OVERLAY_PAUSE_MENU)

        # Write the specified window colors
        handler.write_byte(0x8881A, options["window_color_r"] << 4)
        handler.write_byte(0x8881B, options["window_color_g"] << 4)
        handler.write_byte(0x8881E, options["window_color_b"] << 4)
        handler.write_byte(0x8881F, options["window_color_a"] << 4)

        # if loc.item.player != player:
        #        inject_address = 0xBB7164 + (256 * (loc.address & 0xFFF))
        #        wrapped_name, num_lines = cvlod_text_wrap(item_name + "\nfor " + multiworld.get_player_name(
        #            loc.item.player), 96)
        # handler.write_bytes(inject_address, get_item_text_color(loc) + cvlod_string_to_bytearray(wrapped_name))
        # handler.write_byte(inject_address + 255, num_lines)

        # Everything relating to loading the other game items text
        # handler.write_int32(0xA8D8C, 0x080FF88F)  # J   0x803FE23C
        # handler.write_int32(0xBEA98, 0x0C0FF8B4)  # JAL 0x803FE2D0
        # handler.write_int32(0xBEAB0, 0x0C0FF8BD)  # JAL 0x803FE2F8
        # handler.write_int32(0xBEACC, 0x0C0FF8C5)  # JAL 0x803FE314
        # handler.write_int32s(0xBFE23C, patches.multiworld_item_name_loader)
        # handler.write_bytes(0x10F188, [0x00 for _ in range(264)])
        # handler.write_bytes(0x10F298, [0x00 for _ in range(264)])

        # Write all the edits to the Nisitenma-Ichigo files decided during generation.
        for file in ni_edits:
            for offset in ni_edits[file]:
                handler.write_bytes(int(offset), base64.b64decode(ni_edits[file][offset].encode()), int(file))

        return handler.get_output_rom()


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
