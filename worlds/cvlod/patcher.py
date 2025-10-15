import logging
import zlib
import struct

from typing import Collection, TypedDict, NotRequired
from .data.enums import Scenes, Objects, ObjectExecutionFlags, ActorSpawnFlags, Items, Pickups, PickupFlags, \
    DoorFlags
from .cvlod_text import cvlod_string_to_bytearray, cvlod_bytes_to_string, CVLOD_STRING_END_CHARACTER, \
    CVLOD_TEXT_POOL_END_CHARACTER

N64_RDRAM_START = 0x80000000
COMMON_SEGMENT_RDRAM_START = 0x141870 | N64_RDRAM_START
SCENE_OVERLAY_RDRAM_START = 0x2E3B70 | N64_RDRAM_START

COMMON_SEGMENT_ROM_START = 0xC2120  # 80141870
SCENE_OVERLAY_RDRAM_ADDRS_START = 0xB3858  # 800B2C58
SCENE_OVERLAY_ROM_ADDRS_START = 0xB39E8  # 800B2DE8
SCENE_ACTOR_PTRS_START = 0x10D150  # 8018C8A0
SCENE_1HB_PTRS_START = 0x11222C  # 8019197C
SCENE_3HB_PTRS_START = 0x1122F4  # 80191A44
SCENE_ENEMY_PILLARS_PTRS_START = 0x10DBB4  # 8018D304
SCENE_DOOR_PTRS_START = 0x1108C0  # 80190010
SCENE_LOADING_ZONE_PTRS_START = 0x110D38  # 80190488
SCENE_TEXT_PTRS_START = 0xB8DE0  # 800B81E0
SCENE_SPAWN_COORDS_PTRS_START = 0x1107F8  # 8018FF48

NORMAL_ACTOR_ENTRY_LENGTH = 0x20
ONE_HIT_BREAKABLE_ENTRY_LENGTH = 0xC
THREE_HIT_BREAKABLE_ENTRY_LENGTH = 0xC
ENEMY_PILLAR_ENTRY_LENGTH = 0x10
ENEMY_PILLAR_ACTOR_ENTRY_LENGTH = 0x18
LOADING_ZONE_ENTRY_LENGTH = 0x14
DOOR_ENTRY_LENGTH = 0x2C
SCENE_SPAWN_LENGTH = 0x16

EXTENDED_DATA_ACTORS: dict[int, str] = {Objects.ONE_HIT_BREAKABLE: "1hb",
                                        Objects.THREE_HIT_BREAKABLE: "3hb",
                                        Objects.FOGGY_LAKE_ABOVE_DECKS_BARREL: "1hb special",
                                        Objects.FOGGY_LAKE_BELOW_DECKS_BARREL: "1hb special",
                                        Objects.SORCERY_CYAN_DIAMOND: "1hb special",
                                        Objects.ENEMY_GENERATOR_PILLAR: "pillar",
                                        Objects.DOOR: "door",
                                        Objects.LOADING_ZONE: "load"}

SPECIAL_1HB_HARDCODED_PTRS_ADDRS: dict[int, int] = {Scenes.FOGGY_LAKE_ABOVE_DECKS: 0xC4,  # 0x802E3C34
                                                    Scenes.FOGGY_LAKE_BELOW_DECKS: 0xC4,  # 0x802E3C34
                                                    Scenes.TOWER_OF_SORCERY: 0x3FA4}  # 0x802E7B14

class CVLoDSceneDataEntry(TypedDict):
    """Base class that all CVLoD scene data entries inherit from."""

    start_addr: NotRequired[int]  # Where in the RDRAM the data entry starts, if it's vanilla. For easier debugging.
    delete: NotRequired[bool]  # Whether the entry should be deleted when it comes time to reinsert the list.


class CVLoDNormalActorEntry(CVLoDSceneDataEntry):
    """An entry from any regular actor list in any scene in the game."""

    spawn_flags: int  # 16-bit bitfield comprising flags that affect the condition under which the actor spawns.
    status_flags: int  # 16-bit bitfield comprising flags used to tell the actor's current spawned state. Normally 0.
    x_pos: float  # How far east/west from the center of the scene the actor is located. 32-bit float.
    y_pos: float  # How far up/down from the center of the scene the actor is located. 32-bit float.
    z_pos: float  # Hor far north/south from the center of the scene the actor is located. 32-bit float.
    execution_flags: int # Flags related to execution functionality with the actor. Upper 5 bits in the object ID bytes.
    object_id: int  # The game's ID for what object the actor is (breakable, enemy, pickup, etc.). Lower 11 bits in the
                    # object ID bytes.
    flag_id: int  # For normal: Int16 ID for the flag value the actor checks to see if it should or shouldn't spawn, if
                  # spawn flags 0x0020 or 0x0080 are set on it.
                  # For pillar: 32-bit struct for a flag to check to see if the pillar should spawn the actor. If the
                  # 80000000 bitflag is set, check the flag ID being set. If 40000000 is set, check it being un-set.
    var_a: int  # Extra int16 parameters that apply to the actor (exactly what these mean vary per actor).
    var_b: int
    var_c: int
    var_d: int
    extra_condition_ptr: int  # Int32 pointer to an extra spawn check function to run, if spawn flag 0x0008 is enabled.


class CVLoDPillarActorEntry(CVLoDSceneDataEntry):
    """An entry from the enemy generator pillar actor list found exclusively in Tower of Execution (Central Tower)."""
    x_pos: int  # How far east/west from the center of the scene the actor is located. Signed 16-bit int, unlike the
                # regular actor lists which use floats.
    y_pos: int  # How far up/down from the center of the scene the actor is located. Signed 16-bit int.
    z_pos: int  # Hor far north/south from the center of the scene the actor is located. Signed 16-bit int.
    execution_flags: int # Flags related to execution functionality with the actor. Upper 5 bits in the object ID bytes.
    object_id: int  # The game's ID for what object the actor is (breakable, enemy, pickup, etc.). Lower 11 bits in the
                    # object ID bytes.
    flag_id: int  # For normal: Int16 ID for the flag value the actor checks to see if it should or shouldn't spawn, if
                  # spawn flags 0x0020 or 0x0080 are set on it.
                  # For pillar: 32-bit struct for a flag to check to see if the pillar should spawn the actor. If the
                  # 80000000 bitflag is set, check the flag ID being set. If 40000000 is set, check it being un-set.
    var_c: int  # Extra int16 parameters that apply to the actor (exactly what these mean vary per actor).
    var_a: int  # (Yes, these are out of order in the actual game's structs).
    var_b: int
    var_d: int


class CVLoD1HitBreakableEntry(CVLoDSceneDataEntry):
    """An entry from the scene's list of 1-hit breakable datas."""

    appearance_id: int  # Int16 ID for what appearance the 1HB takes. 0 = normal floor candle, 1 = wall candle, etc.
    pickup_id: int  # Int16 ID for what pickup to drop upon breaking the 1HB if the event flag isn't set.
    flag_id: int  # Int32 ID for what event flag the dropped pickup checks to see if it should spawn and sets upon being
                  # picked up.
    pickup_flags: int  # 16-bit bitfield comprising bitflags that affect the dropped pickup's behavior.


class CVLoD3HitBreakableEntry(CVLoDSceneDataEntry):
    """An entry from the scene's list of 3-hit breakable datas."""

    appearance_id: int  # Int16 ID for what breakable's appearance the 3HB takes.
    pickup_count: int  # How many item IDs from the item array start the 3HB drops. Int16.
    pickup_array_start: int  # 32-bit address in RAM for the first pickup ID the 3HB drops. The remaining pickup IDs are
                             # always located right after the first one.
    flag_id: int  # Int32 ID for what event flag the 3HB checks to see if it should break and sets upon breaking. In
                  # this implementation, it is instead the first flag ID to set on the first dropped pickup, with the
                  # subsequent pickups getting +1 every time (the 3HBs break every time no matter what).


class CVLoDEnemyPillarEntry(CVLoDSceneDataEntry):
    """An entry from the scene's list of enemy generator pillar datas (exclusive to Tower of Execution (Central))."""

    actor_list_start: int  # 32-bit address in RAM for the first actor the pillar spawns when broken. The remaining
                           # actors are always located right after the first one.
    actor_count: int  # How many actors from the actor list start the pillar spawns. Int16.
    dissolve_flags: int  # 16-bit bitfield comprising flags that affect the dissolve effect when the pillar breaks.
    rotation: int  # What angle direction the pillar is facing on the Y axis. Signed int16.
    flag_id: int  # Int32 ID for what event flag the pillar checks to see if it should break and sets upon breaking.


class CVLoDLoadingZoneEntry(CVLoDSceneDataEntry):
    """An entry from the scene's list of loading zone datas."""

    heal_player: bool  # Whether the loading zone should heal the player. 16 bits.
    scene_id: int  # Int8 ID for which scene in the game the loading zone will send the player to.
    spawn_id: int  # Int8 ID for which entrance in the destination scene the player will spawn at.
    fade_settings_id: int  # Int8 ID for which settings in the game's fade settings table will be used.
    cutscene_settings_id: int  # Int16 ID for which settings in the game's loading zone cutscene settings table will be
                               # used. 0 if no cutscene should play.
    min_x_pos: int  # How far east/west the scene the zone's bounding box min is located. Signed int16.
    min_y_pos: int  # How far up/down the zone's bounding box min is located. Signed int16.
    min_z_pos: int  # How far north/south the zone's bounding box min is located. Signed int16.
    max_x_pos: int  # How far east/west the zone's bounding box max is located. Signed int16.
    max_y_pos: int  # How far up/down the zone's bounding box max is located. Signed int16.
    max_z_pos: int  # How far north/south the zone's bounding box max is located. Signed int16.


class CVLoDDoorEntry(CVLoDSceneDataEntry):
    """An entry from the scene's list of door datas."""

    dlist_addr: int  # Int32 DisplayList address for the door's model in the scene file.
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
    cant_open_text_id: int  # Int8 ID for what text in the scene's text pool to display if the player tries opening the
                            # door when they can't. 80 if nothing.
    unlocked_text_id: int  # Int8 ID for what text in the scene's text pool to display if the player unlocks the door.
                           # 80 if nothing.
    byte_1c: int  # Something??? 80 if not applicable.
    opening_sound_id: int  # Int16 ID for what sound to play when the door starts opening.
    half_20: int
    closing_sound_id: int  # Int16 ID for what sound to play when the door starts closing.
    half_24: int
    shut_sound_id: int  # Int16 ID for what sound to play when the door slams shut.
    half_28: int
    half_2a: int


class CVLoDSpawnEntranceEntry(CVLoDSceneDataEntry):
    """An entry from the scene's list of spawn entrance coordinate datas."""

    room_id: int  # Int16 ID for which room to load initially if it's a room-based scene.
    player_x_pos: int  # How far east/west from the center of the scene the player spawns. Signed int16.
    player_y_pos: int  # How far up/down from the center of the scene the player spawns. Signed int16.
    player_z_pos: int  # How far north/south from the center of the scene the player spawns. Signed int16.
    player_rotation: int  # What angle direction the player is facing upon spawning in here. Signed int16.
    camera_x_pos: int  # How far east/west from the center of the scene the camera spawns. Signed int16.
    camera_y_pos: int  # How far up/down from the center of the scene the camera spawns. Signed int16.
    camera_z_pos: int  # How far north/south from the center of the scene the camera spawns. Signed int16.
    focus_x_pos: int  # How far e/w from the center of the scene the camera's initial point of focus is. Signed int16.
    focus_y_pos: int  # How far u/d from the center of the scene the camera's initial point of focus is. Signed int16.
    focus_z_pos: int  # How far n/s from the center of the scene the camera's initial point of focus is. Signed int16.


class CVLoDSceneTextEntry(CVLoDSceneDataEntry):
    """An entry from the scene's text pool."""
    text: str


class CVLoDScene:
    overlay: bytearray | None
    spawn_spots: list[CVLoDSpawnEntranceEntry]  # Spawn entrances in the scene.
    enemy_pillars: list[CVLoDEnemyPillarEntry]  # 3HB enemy pillars in the scene.
    one_hit_breakables: list[CVLoD1HitBreakableEntry]  # 1-hit breakables in the scene.
    one_hit_special_breakables: list[CVLoD1HitBreakableEntry]  # Special 1HBs that aren't the regular 1HB actor, like
                                                               # the Foggy Lake barrels and Sorcery diamonds. Always
                                                               # scene-specific with hardcoded ptrs to their datatables.
    three_hit_drop_ids: list[int]  # Array of item IDs that the 3HBs on the scene can drop.
    three_hit_drops_start: int  # Spot in RDRAM where the scene's 3HB drop IDs array begins.
    three_hit_drops_orig_len: int  # Original length of the 3HB drop IDs array.
    three_hit_breakables: list[CVLoD3HitBreakableEntry]  # 3-hit breakables in the scene.
    scene_text: list[CVLoDSceneTextEntry]  # All textbox texts associated with the scene.
    scene_text_orig_size: int  # Original size of the scene's text pool.
    doors: list[CVLoDDoorEntry]  # Doors in the scene.
    loading_zones: list[CVLoDLoadingZoneEntry]  # Loading zones in the scene.
    # Dict of the normal init/proxy/room actor lists in the scene mapped to which one it is.
    actor_lists: dict[str, list[CVLoDNormalActorEntry | CVLoDPillarActorEntry]]
    highest_ids: dict[str, int]  # Highest IDs for specific data like 1-hit breakables, determined from the actors.
    start_addr: int | None  # Where in RDRAM the scene's data starts when loaded, if it's vanilla. For easier debugging.
    name: str | None  # The name of the scene. To more easily see which one it is while debugging.
    # space_available: dict[int, int]  # Start and end addresses of space in the overlay freed up from moving a data
    #                                  # from one spot to another.

    def __init__(self, start_addr: int | None=None, name: str | None=None) -> None:
        self.start_addr = start_addr
        self.name = name
        self.highest_ids = {extended_data: -1 for object_id, extended_data in EXTENDED_DATA_ACTORS.items()}

        self.spawn_spots = []
        self.enemy_pillars = []
        self.one_hit_breakables = []
        self.one_hit_special_breakables = []
        self.three_hit_drop_ids = []
        self.three_hit_breakables = []
        self.scene_text = []
        self.doors = []
        self.loading_zones = []
        self.actor_lists = {}
        self.space_available = {}
        self.three_hit_drops_orig_len = 0
        self.scene_text_orig_size = 0

    def read_ovl_byte(self, offset: int) -> int | None:
        """Return a byte at a specified address in the scene's overlay."""
        if self.overlay:
            return self.overlay[offset]
        logging.error(f"Scene {self.name} has no overlay associated with it. Fix the code and Try, Try Again!")

    def read_ovl_bytes(self, start_address: int, length: int, return_as_int: bool = False) -> bytearray | int | None:
        """Return a string of bytes of a specified length beginning at a specified address in the scene's overlay."""
        if not self.overlay:
            logging.error(f"Scene {self.name} has no overlay associated with it. Fix the code and Never Let Up!")
            return None
        if return_as_int:
            return int.from_bytes(self.overlay[start_address:start_address + length], "big")
        return self.overlay[start_address:start_address + length]

    def write_ovl_byte(self, address: int, value: int) -> None:
        self.overlay[address] = value

    def write_ovl_bytes(self, start_address: int, values: Collection[int]) -> None:
        self.overlay[start_address:start_address + len(values)] = values

    def write_ovl_int16(self, address: int, value: int) -> None:
        value = value & 0xFFFF
        self.write_ovl_bytes(address, [(value >> 8) & 0xFF, value & 0xFF])

    def write_ovl_int16s(self, start_address: int, values: list[int]) -> None:
        for i, value in enumerate(values):
            self.write_ovl_int16(start_address + (i * 2), value)

    def write_ovl_int24(self, address: int, value: int) -> None:
        value = value & 0xFFFFFF
        self.write_ovl_bytes(address, [(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    def write_ovl_int24s(self, start_address: int, values: list[int]) -> None:
        for i, value in enumerate(values):
            self.write_ovl_int24(start_address + (i * 3), value)

    def write_ovl_int32(self, address: int, value: int) -> None:
        value = value & 0xFFFFFFFF
        self.write_ovl_bytes(address, [(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    def write_ovl_int32s(self, start_address: int, values: list[int]) -> None:
        for i, value in enumerate(values):
            self.write_ovl_int32(start_address + (i * 4), value)


class CVLoDRomPatcher:
    rom: bytearray
    decompressed_files: dict[int, bytearray]
    compressed_files: dict[int, bytearray]
    scenes: list[CVLoDScene]
    ni_table_start: int
    ni_file_buffers_start: int
    decomp_file_sizes_table_start: int
    number_of_ni_files: int
    current_write_file_addr: int
    scene_overlays_end: int

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

        # The actual table begins 16 bytes after where the Nisitenma-Ichigo string begins.
        self.ni_table_start = nisitenma_ichigo_start + 16
        # Save the file start address of the first entry in the table to get the start of ALL the NI files in the ROM
        # as a whole.
        self.ni_file_buffers_start = int.from_bytes(self.rom[self.ni_table_start: self.ni_table_start + 4],
                                                    "big") & 0xFFFFFFF

        # Figure out how many Nisitenma-Ichigo files there are alongside grabbing them out of the ROM.
        self.number_of_ni_files = 1
        while True:
            # Each entry in the NI table is 8 bytes long. The first four are the ROM start address of a file, and the
            # last four are the end address.
            ni_table_entry_start = self.ni_table_start + ((self.number_of_ni_files - 1) * 8)
            file_start_addr = self.read_bytes(ni_table_entry_start, 4, return_as_int=True) & 0xFFFFFFF
            # If the file start address is 00000000, we've reached the end of the NI table. In which case, end the loop.
            if not file_start_addr:
                break
            # Calculate the compressed file's size based on the start and end addresses and use that to read said file
            # out of the ROM.
            file_size = (int.from_bytes(self.read_bytes(ni_table_entry_start + 4, 4), "big") & 0xFFFFFFF) - \
                file_start_addr
            self.compressed_files[self.number_of_ni_files] = self.read_bytes(file_start_addr, file_size)
            self.number_of_ni_files += 1

        # Figure out where the decompressed file sizes table starts by going backwards the number of NI files from the
        # start of "Nisitenma-Ichigo". Each entry in this table is 8 bytes long, with the 2nd-4th bytes being the size.
        self.decomp_file_sizes_table_start = nisitenma_ichigo_start - 4 - (8 * self.number_of_ni_files)

        # Figure out where the first scene overlay begins and the last scene overlay ends. This will be the first
        # free-range that we write files into.
        self.current_write_file_addr = self.read_bytes(SCENE_OVERLAY_ROM_ADDRS_START, 4, return_as_int=True)
        self.scene_overlays_end = self.read_bytes(SCENE_OVERLAY_ROM_ADDRS_START + (Scenes.TEST_GRID * 8) + 4, 4,
                                                  return_as_int=True)

        # Read out the important common scene data structs into a format that is easy to edit and then reinsert
        # (actor lists, breakable datas, scene text, etc.).
        self.scenes = []
        for scene_id in range(len(Scenes) - 1):
            self.scenes.append(CVLoDScene(name=Scenes(scene_id).name))

            # Check to see if the scene has an associated overlay. If it doesn't (because the scene has no start address
            # in the game's hardcoded list of scene overlay ROM starts), skip it.
            scene_overlay_start = self.read_bytes(SCENE_OVERLAY_ROM_ADDRS_START + (scene_id * 8), 4,
                                                  return_as_int=True)
            scene_overlay_end = self.read_bytes(SCENE_OVERLAY_ROM_ADDRS_START + (scene_id * 8) + 4, 4,
                                                return_as_int=True)
            if not scene_overlay_start:
                self.scenes[scene_id].overlay = None
                continue

            # Otherwise, save its vanilla overlay data and continue.
            self.scenes[scene_id].overlay = self.rom[scene_overlay_start: scene_overlay_end]

            # Extract the scene's init actor list (the one that spawns all of its contents upon the scene initializing
            # and keeps them spawned regardless of both the player's proximity to them and what room they're in). Take
            # the third pointer in the scene's entry in the game's table of loaded scene actor list starts and determine
            # how far in it is relative to the start of the overlay in RDRAM.
            init_actors_start = self.read_bytes(SCENE_ACTOR_PTRS_START + 8 + (scene_id * 0x10), 4,
                                                return_as_int=True) - SCENE_OVERLAY_RDRAM_START
            self.scenes[scene_id].actor_lists["init"] = self.extract_normal_scene_actor_list(scene_id,
                                                                                             init_actors_start)

            # Extract the scene's proxy actor list (the one that will spawn its things ONLY while the player is
            # within a certain proximity from them and is also not tied to any room). This is the second pointer in the
            # scene's entry in the above-mentioned table.
            proxy_actors_start = self.read_bytes(SCENE_ACTOR_PTRS_START + 4 + (scene_id * 0x10),
                                                 4, return_as_int=True) - SCENE_OVERLAY_RDRAM_START
            self.scenes[scene_id].actor_lists["proxy"] = self.extract_normal_scene_actor_list(scene_id,
                                                                                                 proxy_actors_start)

            # Extract the scene's room actor lists (the ones that will spawn their things only while their designated
            # rooms are loaded and, much like the init list, don't care about the player's proximity). Not every scene
            # has these; in fact, most don't. To see if the current scene we're looking at has one, we will check if the
            # fourth pointer in the scene's table entry is not 00000000.
            room_actor_ptrs_start = self.read_bytes(SCENE_ACTOR_PTRS_START + 0xC + (scene_id * 0x10), 4,
                                                    return_as_int=True)

            # While we are at it, also take the first pointer, which points to not an actor list-related thing but the
            # start of the scene's decoration data list. This is where the room actor pointers list ends.
            scene_decorations_data_start = self.read_bytes(SCENE_ACTOR_PTRS_START + (scene_id * 0x10), 4,
                                                           return_as_int=True)

            # If room actor lists exist, extract them.
            if room_actor_ptrs_start != 0:
                room_actor_ptrs_start -= SCENE_OVERLAY_RDRAM_START
                scene_decorations_data_start -= SCENE_OVERLAY_RDRAM_START

                # Grab the list of pointers to said lists. To determine how many pointers the list has, take the
                # difference between the scene decorations data start address and the room actor pointers start address;
                # the latter structs always begin immediately after the former.
                room_list_ptrs = [self.scenes[scene_id].read_ovl_bytes(room_actor_ptrs_start + (room_id * 4), 4,
                                                                        return_as_int=True) - SCENE_OVERLAY_RDRAM_START
                                  for room_id in range((scene_decorations_data_start - room_actor_ptrs_start) // 4)]
                # Extract the actor lists at the pointers we just extracted.
                for room_id in range(len(room_list_ptrs)):
                    self.scenes[scene_id].actor_lists[f"room {room_id}"] = \
                        self.extract_normal_scene_actor_list(scene_id, room_list_ptrs[room_id])

            # Extract the enemy pillar data if enemy pillar data exists (highest found enemy pillar ID is 0 or higher).
            # This should only occur for the Tower of Execution (Central Tower) map.
            self.scenes[scene_id].enemy_pillars = []
            if self.scenes[scene_id].highest_ids["pillar"] > -1:

                # Get the start address of the map's enemy pillar data in the overlay.
                enemy_pillars_start = self.read_bytes(SCENE_ENEMY_PILLARS_PTRS_START + (scene_id * 4), 4,
                                                      return_as_int=True) - SCENE_OVERLAY_RDRAM_START

                # Loop over every enemy pillar data that is known to exist based on how high the highest ID is.
                enemy_pillar_list = []
                lowest_pillar_actor_list_start = 0xFFFFFFFF
                highest_pillar_actor_list_end = 0x00000000
                for enemy_pillar_id in range(self.scenes[scene_id].highest_ids["pillar"] + 1):
                    current_enemy_pillar_start = enemy_pillars_start + (enemy_pillar_id * ENEMY_PILLAR_ENTRY_LENGTH)
                    enemy_pillar_data = self.scenes[scene_id].read_ovl_bytes(current_enemy_pillar_start,
                                                                             ENEMY_PILLAR_ENTRY_LENGTH)
                    enemy_pillar = CVLoDEnemyPillarEntry(
                        actor_list_start=int.from_bytes(enemy_pillar_data[0x00:0x04], "big"),
                        actor_count=int.from_bytes(enemy_pillar_data[0x04:0x06], "big"),
                        dissolve_flags=int.from_bytes(enemy_pillar_data[0x06:0x08], "big"),
                        rotation=struct.unpack('>h', enemy_pillar_data[0x0A:0x0C])[0],
                        flag_id=int.from_bytes(enemy_pillar_data[0x0C:], "big"),
                        start_addr=current_enemy_pillar_start + SCENE_OVERLAY_RDRAM_START,
                    )

                    # If the pillar has a lower actor list start address than the lowest one we've found, save the new
                    # one.
                    if enemy_pillar["actor_list_start"] < lowest_pillar_actor_list_start:
                        lowest_pillar_actor_list_start = enemy_pillar["actor_list_start"]

                    # If the pillar has a higher actor list end address than the lowest one we've found, save the new
                    # one.
                    pillar_actor_list_end = enemy_pillar["actor_list_start"] + \
                                            (enemy_pillar["actor_count"] * ENEMY_PILLAR_ACTOR_ENTRY_LENGTH)
                    if pillar_actor_list_end > highest_pillar_actor_list_end:
                        highest_pillar_actor_list_end = pillar_actor_list_end

                    # Append the enemy pillar to the end of the list.
                    enemy_pillar_list.append(enemy_pillar)

                # Save the complete enemy pillar list.
                self.scenes[scene_id].enemy_pillars = enemy_pillar_list

                # Extract the map's enemy pillar actor list using the lowest and highest pillar actor list addresses
                # that we gleamed from the regular enemy pillar data.
                pillar_actor_list = []
                for pillar_actor_list_id in range((highest_pillar_actor_list_end - lowest_pillar_actor_list_start)
                                                  // ENEMY_PILLAR_ACTOR_ENTRY_LENGTH):
                    current_enemy_pillar_actor_start = lowest_pillar_actor_list_start - SCENE_OVERLAY_RDRAM_START + \
                                                       (pillar_actor_list_id * ENEMY_PILLAR_ACTOR_ENTRY_LENGTH)
                    pillar_actor_data = self.scenes[scene_id].read_ovl_bytes(current_enemy_pillar_actor_start,
                        ENEMY_PILLAR_ACTOR_ENTRY_LENGTH)

                    object_id = int.from_bytes(pillar_actor_data[0x06:0x08], "big")
                    pillar_actor = CVLoDPillarActorEntry(
                        x_pos=struct.unpack('>h', pillar_actor_data[0x00:0x02])[0],
                        y_pos=struct.unpack('>h', pillar_actor_data[0x02:0x04])[0],
                        z_pos=struct.unpack('>h', pillar_actor_data[0x04:0x06])[0],
                        execution_flags=object_id >> 0xB,
                        object_id=object_id & 0x7FF,
                        var_c=struct.unpack('>H', pillar_actor_data[0x08:0x0A])[0],
                        var_a=struct.unpack('>H', pillar_actor_data[0x0A:0x0C])[0],
                        var_b=struct.unpack('>H', pillar_actor_data[0x0C:0x0E])[0],
                        var_d=struct.unpack('>H', pillar_actor_data[0x0E:0x10])[0],
                        flag_id=int.from_bytes(pillar_actor_data[0x14:], "big"),
                        start_addr=current_enemy_pillar_actor_start + SCENE_OVERLAY_RDRAM_START,
                    )
                    # Check if the actor has a documented entry in the actors enum.
                    if pillar_actor["object_id"] in Objects:
                        pillar_actor["object_id"] = Objects(pillar_actor["object_id"])

                    # Check if the actor is an item pickup actor, and if it is, does it have has an entry in the
                    # pickups enum.
                    if pillar_actor["object_id"] == Objects.PICKUP_ITEM and pillar_actor["var_c"] in Pickups:
                        pillar_actor["var_c"] = Pickups(pillar_actor["var_c"])

                    # Loop over every execution flag and see if we have any of them set and documented.
                    for flag_index in range(0x5):
                        flag_to_check = pillar_actor["execution_flags"] & (1 << flag_index)
                        if flag_to_check in ObjectExecutionFlags:
                            pillar_actor["execution_flags"] |= ObjectExecutionFlags(flag_to_check)

                    # If the actor is in the dict of actors with extended data, check the data ID in param 3 against the
                    # highest one we've found so far for that actor on this map. If it's higher, then consider it the
                    # new highest.
                    if pillar_actor["object_id"] in EXTENDED_DATA_ACTORS.keys():
                        extended_data_type = EXTENDED_DATA_ACTORS[pillar_actor["object_id"]]

                        if pillar_actor["var_c"] > self.scenes[scene_id].highest_ids[extended_data_type]:
                            self.scenes[scene_id].highest_ids[extended_data_type] = pillar_actor["var_c"]

                    # Append the actor to the end of the list.
                    pillar_actor_list.append(pillar_actor)

                # Save the complete pillar actor list.
                self.scenes[scene_id].actor_lists["pillars"] = pillar_actor_list

            # Extract the 1-hit breakables data if 1HB data exists (highest found 1HB ID is 0 or higher).
            if self.scenes[scene_id].highest_ids["1hb"] > -1:
                # Get the start address of the scene's 1HB data in the overlay.
                one_hit_breakables_start = self.read_bytes(SCENE_1HB_PTRS_START + (scene_id * 4), 4,
                                                           return_as_int=True) - SCENE_OVERLAY_RDRAM_START

                # Loop over every 1HB data that is known to exist based on how high the highest ID is.
                one_hit_list = []
                for one_hit_id in range(self.scenes[scene_id].highest_ids["1hb"] + 1):
                    current_one_hit_start = one_hit_breakables_start + (one_hit_id * ONE_HIT_BREAKABLE_ENTRY_LENGTH)
                    one_hit_data = self.scenes[scene_id].read_ovl_bytes(current_one_hit_start,
                                                                        ONE_HIT_BREAKABLE_ENTRY_LENGTH)

                    one_hit = CVLoD1HitBreakableEntry(
                        appearance_id=int.from_bytes(one_hit_data[0x00:0x02], "big"),
                        pickup_id=int.from_bytes(one_hit_data[0x02:0x04], "big"),
                        flag_id=int.from_bytes(one_hit_data[0x04:0x08], "big"),
                        pickup_flags=int.from_bytes(one_hit_data[0x08:0x0A], "big"),
                        start_addr=current_one_hit_start + SCENE_OVERLAY_RDRAM_START,
                    )

                    # Check if the pickup ID has an entry in the pickups enum.
                    if one_hit["pickup_id"] in Pickups:
                        one_hit["pickup_id"] = Pickups(one_hit["pickup_id"])

                    # Loop over every pickup flag and see if we have any of them set and documented.
                    for flag_index in range(0x16):
                        flag_to_check = one_hit["pickup_flags"] & (1 << flag_index)
                        if flag_to_check in PickupFlags:
                            one_hit["pickup_flags"] |= PickupFlags(flag_to_check)

                    # Append the 1HB to the end of the list.
                    one_hit_list.append(one_hit)

                # Save the complete 1HB list.
                self.scenes[scene_id].one_hit_breakables = one_hit_list

            # Extract the special 1-hit breakables data if special 1HB data exists (highest found 1HB special ID is 0
            # or higher).
            if self.scenes[scene_id].highest_ids["1hb special"] > -1:
                # Get the start address of the scene's 1HB special data in the overlay. This is hardcoded in the overlay
                # of every map that has one, so we will need to read the lower halves of two separate instructions and
                # put them together (it's an LUI followed by an ADDIU into the same register in every case).
                upper_addr_half = self.scenes[scene_id].read_ovl_bytes(SPECIAL_1HB_HARDCODED_PTRS_ADDRS[scene_id] + 2,
                                                                       2, return_as_int= True)
                lower_addr_half = self.scenes[scene_id].read_ovl_bytes(SPECIAL_1HB_HARDCODED_PTRS_ADDRS[scene_id] + 6,
                                                                       2, return_as_int= True)
                # If the lower half is 0x8000 or higher, subtract 1 from the upper half. ADDIU-ing a signed negative
                # decrements the upper half of the number being added into by 1 normally.
                if lower_addr_half >= 0x8000:
                    upper_addr_half -= 1

                # Put the two halves together to form the complete address.
                special_one_hit_breakables_start = (upper_addr_half << 0x10) + lower_addr_half \
                                                   - SCENE_OVERLAY_RDRAM_START

                # Loop over every special 1HB data that is known to exist based on how high the highest ID is. It is
                # formatted exactly the same way as regular 1HB data in every case.
                special_one_hit_list = []
                for special_one_hit_id in range(self.scenes[scene_id].highest_ids["1hb special"] + 1):
                    current_special_one_hit_start = special_one_hit_breakables_start + (special_one_hit_id *
                                                                                        ONE_HIT_BREAKABLE_ENTRY_LENGTH)
                    special_one_hit_data = self.scenes[scene_id].read_ovl_bytes(current_special_one_hit_start,
                                                                        ONE_HIT_BREAKABLE_ENTRY_LENGTH)

                    special_one_hit = CVLoD1HitBreakableEntry(
                        appearance_id=int.from_bytes(special_one_hit_data[0x00:0x02], "big"),
                        pickup_id=int.from_bytes(special_one_hit_data[0x02:0x04], "big"),
                        flag_id=int.from_bytes(special_one_hit_data[0x04:0x08], "big"),
                        pickup_flags=int.from_bytes(special_one_hit_data[0x08:0x0A], "big"),
                        start_addr=current_special_one_hit_start + SCENE_OVERLAY_RDRAM_START,
                    )

                    # Check if the pickup ID has an entry in the pickups enum.
                    if special_one_hit["pickup_id"] in Pickups:
                        special_one_hit["pickup_id"] = Pickups(special_one_hit["pickup_id"])

                    # Loop over every pickup flag and see if we have any of them set and documented.
                    for flag_index in range(0x16):
                        flag_to_check = special_one_hit["pickup_flags"] & (1 << flag_index)
                        if flag_to_check in PickupFlags:
                            special_one_hit["pickup_flags"] |= PickupFlags(flag_to_check)

                    # Append the special 1HB to the end of the list.
                    special_one_hit_list.append(special_one_hit)

                # Save the complete special 1HB list.
                self.scenes[scene_id].one_hit_special_breakables = special_one_hit_list

            # Extract the 3-hit breakables data if 3HB data exists (highest found 3HB ID is 0 or higher).
            if self.scenes[scene_id].highest_ids["3hb"] > -1:

                # Get the start address of the scene's 3HB data in the overlay.
                three_hit_breakables_start = self.read_bytes(SCENE_3HB_PTRS_START + (scene_id * 4), 4,
                                                             return_as_int=True) - SCENE_OVERLAY_RDRAM_START

                # Loop over every 3HB data that is known to exist based on how high the highest ID is.
                three_hit_list = []
                lowest_3hb_pickup_array_start = 0xFFFFFFFF
                highest_3hb_pickup_array_end = 0x00000000
                for three_hit_id in range(self.scenes[scene_id].highest_ids["3hb"] + 1):
                    current_three_hit_start = three_hit_breakables_start + (three_hit_id *
                                                                            THREE_HIT_BREAKABLE_ENTRY_LENGTH)
                    three_hit_data = self.scenes[scene_id].read_ovl_bytes(current_three_hit_start,
                                                                           THREE_HIT_BREAKABLE_ENTRY_LENGTH)
                    three_hit = CVLoD3HitBreakableEntry(
                        appearance_id=int.from_bytes(three_hit_data[0x00:0x02], "big"),
                        pickup_count=int.from_bytes(three_hit_data[0x02:0x04], "big"),
                        pickup_array_start=int.from_bytes(three_hit_data[0x04:0x08], "big"),
                        flag_id=int.from_bytes(three_hit_data[0x08:], "big"),
                        start_addr=current_three_hit_start + SCENE_OVERLAY_RDRAM_START,
                    )

                    # If the 3HB has a lower pickup array start address than the lowest one we've found, save the new
                    # one.
                    if three_hit["pickup_array_start"] < lowest_3hb_pickup_array_start:
                        lowest_3hb_pickup_array_start = three_hit["pickup_array_start"]

                    # If the 3HB has a higher pickup array end address than the lowest one we've found, save the new
                    # one.
                    pickup_array_end = three_hit["pickup_array_start"] + (three_hit["pickup_count"] * 2)
                    if pickup_array_end > highest_3hb_pickup_array_end:
                        highest_3hb_pickup_array_end = pickup_array_end

                    # Append the 3HB to the end of the list.
                    three_hit_list.append(three_hit)

                # Save the complete 3HB list and the start address of its drop IDs array.
                self.scenes[scene_id].three_hit_breakables = three_hit_list
                self.scenes[scene_id].three_hit_drops_start = lowest_3hb_pickup_array_start

                # Extract the scene's array of 3HB pickup IDs using the lowest and highest 3HB drop array addresses that
                # we gleamed from the regular 3HB data.
                three_hit_pickups_list = []
                for three_hit_pickup_array_id in range((highest_3hb_pickup_array_end -
                                                        lowest_3hb_pickup_array_start) // 2):
                    three_hit_pickup_id = self.scenes[scene_id].read_ovl_bytes(
                        lowest_3hb_pickup_array_start - SCENE_OVERLAY_RDRAM_START + (three_hit_pickup_array_id * 2), 2,
                        return_as_int=True)

                    # Check if the pickup ID is in the pickups enum and then add it to the list.
                    if three_hit_pickup_id in Pickups:
                        three_hit_pickup_id = Pickups(three_hit_pickup_id)
                    three_hit_pickups_list.append(three_hit_pickup_id)

                # Save the complete 3HB pickups list and its original length.
                self.scenes[scene_id].three_hit_drop_ids = three_hit_pickups_list
                self.scenes[scene_id].three_hit_drops_orig_len = len(three_hit_pickups_list)

            # Extract the door data if door data exists (highest found door ID is 0 or higher).
            if self.scenes[scene_id].highest_ids["door"] > -1:

                # Get the start address of the scene's door data in the overlay.
                doors_start = self.read_bytes(SCENE_DOOR_PTRS_START + (scene_id * 4), 4, return_as_int=True) \
                              - SCENE_OVERLAY_RDRAM_START

                # Loop over every door data that is known to exist based on how high the highest ID is.
                door_list = []
                for door_id in range(self.scenes[scene_id].highest_ids["door"] + 1):
                    current_door_start = doors_start + (door_id * DOOR_ENTRY_LENGTH)
                    door_data = self.scenes[scene_id].read_ovl_bytes(current_door_start, DOOR_ENTRY_LENGTH)
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
                        half_20=int.from_bytes(door_data[0x20:0x22], "big"),
                        closing_sound_id=int.from_bytes(door_data[0x22:0x24], "big"),
                        half_24=int.from_bytes(door_data[0x24:0x26], "big"),
                        shut_sound_id=int.from_bytes(door_data[0x26:0x28], "big"),
                        half_28=int.from_bytes(door_data[0x28:0x2A], "big"),
                        half_2a=int.from_bytes(door_data[0x2A:], "big"),
                        start_addr=current_door_start + SCENE_OVERLAY_RDRAM_START,
                    )

                    # Check if the door has an item ID with an entry in the items enum.
                    if door["item_id"] in Items:
                        door["item_id"] = Items(door["item_id"])

                    # Loop over every door flag and see if we have any of them set and documented.
                    for flag_index in range(0x16):
                        flag_to_check = door["door_flags"] & (1 << flag_index)
                        if flag_to_check in DoorFlags:
                            door["door_flags"] |= DoorFlags(flag_to_check)

                    # Append the 3HB to the end of the list.
                    door_list.append(door)

                # Save the complete door list.
                self.scenes[scene_id].doors = door_list

            # Extract the loading zone data if door data exists (highest found loading zone ID is 0 or higher).
            if self.scenes[scene_id].highest_ids["load"] > -1:

                # Get the start address of the scene's loading zone data in the overlay.
                loading_zones_start = self.read_bytes(SCENE_LOADING_ZONE_PTRS_START + (scene_id * 4), 4,
                                                      return_as_int=True) - SCENE_OVERLAY_RDRAM_START

                # Loop over every loading zone data that is known to exist based on how high the highest ID is.
                loading_zone_list = []
                for loading_zone_id in range(self.scenes[scene_id].highest_ids["load"] + 1):
                    current_loading_zone_start = loading_zones_start + (loading_zone_id * LOADING_ZONE_ENTRY_LENGTH)
                    loading_zone_data = self.scenes[scene_id].read_ovl_bytes(current_loading_zone_start,
                                                                             LOADING_ZONE_ENTRY_LENGTH)
                    loading_zone = CVLoDLoadingZoneEntry(
                        heal_player=bool.from_bytes(loading_zone_data[0x00:0x02], "big"),
                        scene_id=loading_zone_data[0x02],
                        spawn_id=loading_zone_data[0x03],
                        fade_settings_id=loading_zone_data[0x04],
                        cutscene_settings_id=int.from_bytes(loading_zone_data[0x06:0x08], "big"),
                        min_x_pos=struct.unpack('>h',loading_zone_data[0x08:0x0A])[0],
                        min_y_pos=struct.unpack('>h',loading_zone_data[0x0A:0x0C])[0],
                        min_z_pos=struct.unpack('>h',loading_zone_data[0x0C:0x0E])[0],
                        max_x_pos=struct.unpack('>h',loading_zone_data[0x0E:0x10])[0],
                        max_y_pos=struct.unpack('>h',loading_zone_data[0x10:0x12])[0],
                        max_z_pos=struct.unpack('>h',loading_zone_data[0x12:])[0],
                        start_addr=current_loading_zone_start + SCENE_OVERLAY_RDRAM_START,
                    )

                    # Check if the zone's destination scene has a scene ID with an entry in the scenes enum.
                    if loading_zone["scene_id"] in Scenes:
                        loading_zone["scene_id"] = Scenes(loading_zone["scene_id"])

                    # Append the 3HB to the end of the list.
                    loading_zone_list.append(loading_zone)

                # Save the complete loading zone list.
                self.scenes[scene_id].loading_zones = loading_zone_list

            # Extract the scene's text pool if it has one (scene ID is The Outer Wall's or lower).
            if scene_id <= Scenes.THE_OUTER_WALL:
                current_string_start = self.read_bytes(SCENE_TEXT_PTRS_START + (scene_id * 4), 4,
                                                       return_as_int=True) - SCENE_OVERLAY_RDRAM_START

                # Loop over every character in the scene text pool.
                current_scene_text_char_start = current_string_start
                raw_scene_text = bytearray(0)
                while True:
                    scene_text_char = self.scenes[scene_id].read_ovl_bytes(current_scene_text_char_start, 2)

                    # Increment the current text character start for the next loop.
                    current_scene_text_char_start += 2

                    # If we found the character indicating the end of the entire pool, terminate the loop.
                    if scene_text_char == CVLOD_TEXT_POOL_END_CHARACTER:
                        break

                    # If we found the character indicating the end of a string in the text pool, convert what we
                    # extracted of the current string now.
                    if scene_text_char == CVLOD_STRING_END_CHARACTER:
                        converted_text = CVLoDSceneTextEntry(text=cvlod_bytes_to_string(raw_scene_text),
                                                             start_addr=current_string_start + \
                                                                        SCENE_OVERLAY_RDRAM_START)
                        # Add the string's length to the total original size of the text pool + 1 for the end char.
                        self.scenes[scene_id].scene_text_orig_size += len(converted_text["text"]) + 1

                        # Save the text entry.
                        self.scenes[scene_id].scene_text.append(converted_text)

                        # Reset the raw scene text back to nothing and then continue to the next iteration.
                        raw_scene_text = bytearray(0)
                        current_string_start = current_scene_text_char_start
                        continue

                    raw_scene_text += scene_text_char

            # Extract the scene's spawn entrance coordinates list. All of this is actually in the common segment,
            # not an overlay, so to find this in the ROM we will need to take the pointer to it, subtract the start
            # of the common segment in RDRAM, and add the start in ROM.
            spawn_entrances_start = \
                self.read_bytes(SCENE_SPAWN_COORDS_PTRS_START + (scene_id * 4), 4, return_as_int=True) \
                - COMMON_SEGMENT_RDRAM_START + COMMON_SEGMENT_ROM_START

            # If the current scene is the last scene (the Test Grid), consider the spawn entrances end to be where their
            # pointers start.
            if scene_id == Scenes.TEST_GRID:
                spawn_entrances_end = SCENE_SPAWN_COORDS_PTRS_START
            # If it's Dracula Ultimate's arena, consider the spawn entrances end to be where the test grid's entrances
            # begin; the next two scenes after this are nonexistent and have no entrances.
            elif scene_id == Scenes.CASTLE_KEEP_VOID:
                spawn_entrances_end = \
                    self.read_bytes(SCENE_SPAWN_COORDS_PTRS_START + (Scenes.TEST_GRID * 4), 4, return_as_int=True) - \
                    COMMON_SEGMENT_RDRAM_START + COMMON_SEGMENT_ROM_START
            # Otherwise, the spawn entrances end for the current map is where the entrances for the next map begin.
            else:
                spawn_entrances_end = \
                    self.read_bytes(SCENE_SPAWN_COORDS_PTRS_START + ((scene_id + 1) * 4), 4, return_as_int=True) - \
                    COMMON_SEGMENT_RDRAM_START + COMMON_SEGMENT_ROM_START

            # Loop over every spawn entrance data and extract it.
            spawn_entrances_list = []
            for spawn_id in range((spawn_entrances_end - spawn_entrances_start) // SCENE_SPAWN_LENGTH):
                spawn_entrances_data = self.read_bytes(spawn_entrances_start + (spawn_id * SCENE_SPAWN_LENGTH),
                                                       SCENE_SPAWN_LENGTH)
                spawn_entrance = CVLoDSpawnEntranceEntry(
                    room_id=int.from_bytes(spawn_entrances_data[0x00:0x02], "big"),
                    player_x_pos=struct.unpack('>h', spawn_entrances_data[0x02:0x04])[0],
                    player_y_pos=struct.unpack('>h', spawn_entrances_data[0x04:0x06])[0],
                    player_z_pos=struct.unpack('>h', spawn_entrances_data[0x06:0x08])[0],
                    player_rotation = struct.unpack('>h', spawn_entrances_data[0x08:0x0A])[0],
                    camera_x_pos=struct.unpack('>h', spawn_entrances_data[0x0A:0x0C])[0],
                    camera_y_pos=struct.unpack('>h', spawn_entrances_data[0x0C:0x0E])[0],
                    camera_z_pos=struct.unpack('>h', spawn_entrances_data[0x0E:0x10])[0],
                    focus_x_pos=struct.unpack('>h', spawn_entrances_data[0x10:0x12])[0],
                    focus_y_pos=struct.unpack('>h', spawn_entrances_data[0x12:0x14])[0],
                    focus_z_pos=struct.unpack('>h', spawn_entrances_data[0x14:])[0],
                    start_addr=(spawn_entrances_start + (spawn_id * SCENE_SPAWN_LENGTH)) \
                               - COMMON_SEGMENT_ROM_START + COMMON_SEGMENT_RDRAM_START
                )

                # Append the spawn entrance to the end of the list.
                spawn_entrances_list.append(spawn_entrance)

            # Save the complete spawn entrances list.
            self.scenes[scene_id].spawn_spots = spawn_entrances_list

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
        return values

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

    def write_int16s(self, start_address: int, values: list[int], file_num: int = 0) -> None:
        for i, value in enumerate(values):
            self.write_int16(start_address + (i * 2), value, file_num)

    def write_int24(self, address: int, value: int, file_num: int = 0) -> None:
        value = value & 0xFFFFFF
        self.write_bytes(address, [(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF], file_num)

    def write_int24s(self, start_address: int, values: list[int], file_num: int = 0) -> None:
        for i, value in enumerate(values):
            self.write_int24(start_address + (i * 3), value, file_num)

    def write_int32(self, address: int, value: int, file_num: int = 0) -> None:
        value = value & 0xFFFFFFFF
        self.write_bytes(address, [(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF],
                         file_num)

    def write_int32s(self, start_address: int, values: list[int], file_num: int = 0) -> None:
        for i, value in enumerate(values):
            self.write_int32(start_address + (i * 4), value, file_num)

    def extract_normal_scene_actor_list(self, scene_id: int, start_addr: int) -> list[CVLoDNormalActorEntry]:
        """Extracts normal actor list data out of a given scene ID's overlay starting at a given address."""

        # Loop over each actor list entry and read it out. Continue looping until we reach the end of the list.
        actor_list = []
        curr_addr = start_addr
        while True:
            actor_data = self.scenes[scene_id].read_ovl_bytes(curr_addr, NORMAL_ACTOR_ENTRY_LENGTH)
            # The execution flags (the upper 5 bits) need to be split out of the object ID (the lower 11 bits).
            object_id = int.from_bytes(actor_data[0x10:0x12], "big")
            actor = CVLoDNormalActorEntry(
                spawn_flags=int.from_bytes(actor_data[0x00:0x02], "big"),
                status_flags=int.from_bytes(actor_data[0x02:0x04], "big"),
                x_pos=struct.unpack('>f', actor_data[0x04:0x08])[0],
                y_pos=struct.unpack('>f', actor_data[0x08:0x0C])[0],
                z_pos=struct.unpack('>f', actor_data[0x0C:0x10])[0],
                execution_flags=object_id >> 0xB,
                object_id=object_id & 0x7FF,
                flag_id=int.from_bytes(actor_data[0x12:0x14], "big"),
                var_a=struct.unpack('>H', actor_data[0x14:0x16])[0],
                var_b=struct.unpack('>H', actor_data[0x16:0x18])[0],
                var_c=struct.unpack('>H', actor_data[0x18:0x1A])[0],
                var_d=struct.unpack('>H', actor_data[0x1A:0x1C])[0],
                extra_condition_ptr=int.from_bytes(actor_data[0x1C:], "big"),
                start_addr=curr_addr + SCENE_OVERLAY_RDRAM_START,
            )
            # Check if the actor has a documented entry in the actors enum.
            if actor["object_id"] in Objects:
                actor["object_id"] = Objects(actor["object_id"])

            # Check if the actor is an item pickup actor, and if it is, does it have has an entry in the pickups enum.
            if actor["object_id"] == Objects.PICKUP_ITEM and actor["var_c"] in Pickups:
                actor["var_c"] = Pickups(actor["var_c"])

            # Loop over every spawn flag and see if we have any of them set and documented.
            for flag_index in range(0x16):
                flag_to_check = actor["spawn_flags"] & (1 << flag_index)
                if flag_to_check in ActorSpawnFlags:
                    actor["spawn_flags"] |= ActorSpawnFlags(flag_to_check)

            # Loop over every execution flag and see if we have any of them set and documented.
            for flag_index in range(0x5):
                flag_to_check = actor["execution_flags"] & (1 << flag_index)
                if flag_to_check in ObjectExecutionFlags:
                    actor["execution_flags"] |= ObjectExecutionFlags(flag_to_check)

            # If the actor we extracted has an object ID of 0x7FF, then we have reached the actor entry signifying
            # the end of the list. In which case, return the actor list as-is (don't append the end-of-list entry).
            if actor["object_id"] == Objects.END_OF_ACTOR_LIST:
                return actor_list

            # If the actor is in the dict of actors with extended data, check the data ID in Var C against the highest
            # one we've found so far for that actor on this scene. If it's higher, then consider it the new highest.
            if actor["object_id"] in EXTENDED_DATA_ACTORS.keys():
                extended_data_type = EXTENDED_DATA_ACTORS[actor["object_id"]]

                if actor["var_c"] > self.scenes[scene_id].highest_ids[extended_data_type]:
                    self.scenes[scene_id].highest_ids[extended_data_type] = actor["var_c"]

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
                    list_data += (b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                  b'\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

                # Get the size of the original actor list by counting the number of entries in the list without entries
                # deleted that have a defined start address. If the new actor data is the same size or smaller
                # than it was before, write it back where it was originally (if we even have a list to begin with).
                if len(actor_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].actor_lists[list_name]
                                           if "start_addr" in orig_entry]):
                    if actor_list:
                        self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].actor_lists[
                                                                  list_name][0]["start_addr"] \
                                                              - SCENE_OVERLAY_RDRAM_START, list_data)
                # If it's larger, however, put it on the end of the overlay and update the pointer(s) to it.
                else:
                    new_actor_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                    self.scenes[scene_id].overlay += list_data

                    # If it's an init list, the pointer to update is the third pointer in the scene's entry in the
                    # game's table of loaded scene actor list starts and determine how far in it is relative to the
                    # start of the overlay in RDRAM.
                    if list_name == "init":
                        self.write_int32(SCENE_ACTOR_PTRS_START + 8 + (scene_id * 0x10), new_actor_list_addr)
                    # If it's a proxy list, the pointer to update is the second pointer in the above-mentioned table.
                    elif list_name == "proxy":
                        self.write_int32(SCENE_ACTOR_PTRS_START + 4 + (scene_id * 0x10), new_actor_list_addr)
                    # If it's a room list, take the fourth pointer in the table to arrive at the scene's list of room
                    # actor list pointers, and then offset into it by the room number.
                    elif "room" in list_name:
                        room_list_ptrs_start = self.read_bytes(SCENE_ACTOR_PTRS_START + 12 + (scene_id * 0x10), 4,
                                                               return_as_int=True) - SCENE_OVERLAY_RDRAM_START

                        self.scenes[scene_id].write_ovl_int32(room_list_ptrs_start + (int(list_name[5:]) * 4),
                                                              new_actor_list_addr)
                    # Otherwise, if it's a 3HB pillar list, loop through every pillar data and update its actor pointer
                    # there.
                    else:
                        old_actor_list_addr = self.scenes[scene_id].actor_lists["pillars"][0]["start_addr"]
                        for pillar_data in self.scenes[scene_id].enemy_pillars:
                            pillar_data["actor_list_start"] = new_actor_list_addr + (pillar_data["actor_list_start"] -
                                                                                     old_actor_list_addr)


            # # # ENEMY PILLARS LIST # # #
            # Create the final enemy pillar list with all entries primed for deletion removed.
            new_pillar_list = [pillar_entry for pillar_entry in self.scenes[scene_id].enemy_pillars
                               if "delete" not in pillar_entry]

            # Loop over each enemy pillar, convert each one to binary data, and insert them back in the map overlay.
            list_data = bytearray(0)
            for pillar in new_pillar_list:
                list_data += int.to_bytes(pillar["actor_list_start"], 4, "big") + \
                             int.to_bytes(pillar["actor_count"], 2, "big") + \
                             int.to_bytes(pillar["dissolve_flags"], 2, "big") + b'\x00\x00' + \
                             struct.pack(">h", pillar["rotation"]) + \
                             int.to_bytes(pillar["flag_id"], 4, "big")

            # If the new pillar data is the same size or smaller than it was before, write it back where it was
            # originally (if we even have a list to begin with).
            if len(new_pillar_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].enemy_pillars
                                            if "start_addr" in orig_entry]):
                if new_pillar_list:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].enemy_pillars[0]["start_addr"] \
                                                          - SCENE_OVERLAY_RDRAM_START, list_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it
            # (if it's not higher than Outer Wall's as that's where the pointer table ends).
            elif scene_id <= Scenes.THE_OUTER_WALL:
                new_pillar_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += list_data
                self.write_int32(SCENE_ENEMY_PILLARS_PTRS_START + (scene_id * 4), new_pillar_list_addr)


            # # # 1-HIT BREAKABLES LIST # # #
            # Create the final 1-hit breakables list with all entries primed for deletion removed.
            new_1hb_list = [one_hit_entry for one_hit_entry in self.scenes[scene_id].one_hit_breakables
                            if "delete" not in one_hit_entry]

            # Loop over each 1HB, convert each one to binary data, and insert them back in the map overlay.
            list_data = bytearray(0)
            for one_hit in new_1hb_list:
                list_data += int.to_bytes(one_hit["appearance_id"], 2, "big") + \
                             int.to_bytes(one_hit["pickup_id"], 2, "big") + \
                             int.to_bytes(one_hit["flag_id"], 4, "big") + \
                             int.to_bytes(one_hit["pickup_flags"], 2, "big") + b'\x00\x00'

            # If the new 1HB data is the same size or smaller than it was before, write it back where it was originally
            # (if we even have a list to begin with).
            if len(new_1hb_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].one_hit_breakables
                                            if "start_addr" in orig_entry]):
                if new_1hb_list:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].one_hit_breakables[0]["start_addr"] \
                                                          - SCENE_OVERLAY_RDRAM_START, list_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_1hb_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += list_data
                self.write_int32(SCENE_1HB_PTRS_START + (scene_id * 4), new_1hb_list_addr)


            # # # SPECIAL 1-HIT BREAKABLES LIST # # #
            # Create the final special 1-hit breakables list with all entries primed for deletion removed.
            new_special_1hb_list = [special_one_hit_entry for special_one_hit_entry in
                                    self.scenes[scene_id].one_hit_special_breakables
                                    if "delete" not in special_one_hit_entry]

            # Loop over each special 1HB, convert each one to binary data, and insert them back in the map overlay.
            list_data = bytearray(0)
            for special_one_hit in new_special_1hb_list:
                list_data += int.to_bytes(special_one_hit["appearance_id"], 2, "big") + \
                             int.to_bytes(special_one_hit["pickup_id"], 2, "big") + \
                             int.to_bytes(special_one_hit["flag_id"], 4, "big") + \
                             int.to_bytes(special_one_hit["pickup_flags"], 2, "big") + b'\x00\x00'

            # If the new special 1HB data is the same size or smaller than it was before, write it back where it was
            # originally (if we even have a list to begin with).
            if len(new_special_1hb_list) <= len([orig_entry for orig_entry in
                                                 self.scenes[scene_id].one_hit_special_breakables
                                                 if "start_addr" in orig_entry]):
                if new_special_1hb_list:
                    self.scenes[scene_id].write_ovl_bytes(
                        self.scenes[scene_id].one_hit_special_breakables[0]["start_addr"] \
                        - SCENE_OVERLAY_RDRAM_START, list_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_special_1hb_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += list_data

                # Split the pointer up into an upper and lower half and write them separately onto the hardcoded
                # instructions for that scene.
                upper_addr_half = new_special_1hb_list_addr >> 0x10
                lower_addr_half = new_special_1hb_list_addr & 0xFFFF
                # Increment the upper half if the lower is 0x8000 or higher.
                if lower_addr_half >= 0x8000:
                    upper_addr_half += 1

                self.scenes[scene_id].write_ovl_int16(SPECIAL_1HB_HARDCODED_PTRS_ADDRS[scene_id] + 2, upper_addr_half)
                self.scenes[scene_id].write_ovl_int16(SPECIAL_1HB_HARDCODED_PTRS_ADDRS[scene_id] + 6, lower_addr_half)


            # # # 3HB DROP IDS LIST # # #
            # Convert the 3HB drops array back into binary data.
            list_data = bytearray(0)
            for three_hit_drop in self.scenes[scene_id].three_hit_drop_ids:
                list_data += int.to_bytes(three_hit_drop, 2, "big")

            # Pad the list data to be 4-aligned.
            if len(list_data) % 4:
                list_data += b'\x00\x00'

            # If the new array is the same size or smaller than it was before, write it back where it was originally
            # (if we even have an array to begin with).
            if len(self.scenes[scene_id].three_hit_drop_ids) <= self.scenes[scene_id].three_hit_drops_orig_len:
                if self.scenes[scene_id].three_hit_drop_ids:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].three_hit_drops_start \
                                                          - SCENE_OVERLAY_RDRAM_START, list_data)
            # If it's larger, however, put it on the end of the overlay and update the pointers to it.
            else:
                new_3hb_drop_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += list_data
                for three_hit_data in self.scenes[scene_id].three_hit_breakables:
                    three_hit_data["pickup_array_start"] = new_3hb_drop_list_addr + \
                                                           (three_hit_data["pickup_array_start"] -
                                                            self.scenes[scene_id].three_hit_drops_start)


            # # # 3-HIT BREAKABLES LIST # # #
            # Create the final 3-hit breakables list with all entries primed for deletion removed.
            new_3hb_list = [three_hit_entry for three_hit_entry in self.scenes[scene_id].three_hit_breakables
                            if "delete" not in three_hit_entry]

            # Loop over each 3HB, convert each one to binary data, and insert them back in the map overlay.
            list_data = bytearray(0)
            for three_hit in new_3hb_list:
                list_data += int.to_bytes(three_hit["appearance_id"], 2, "big") + \
                             int.to_bytes(three_hit["pickup_count"], 2, "big") + \
                             int.to_bytes(three_hit["pickup_array_start"], 4, "big") + \
                             int.to_bytes(three_hit["flag_id"], 4, "big")

            # If the new 3HB data is the same size or smaller than it was before, write it back where it was
            # originally (if we even have a list to begin with).
            if len(new_3hb_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].three_hit_breakables
                                            if "start_addr" in orig_entry]):
                if new_3hb_list:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].three_hit_breakables[0]["start_addr"] \
                                                          - SCENE_OVERLAY_RDRAM_START, list_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_3hb_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += list_data
                self.write_int32(SCENE_3HB_PTRS_START + (scene_id * 4), new_3hb_list_addr)


            # # # DOORS LIST # # #
            # Create the final doors list with all entries primed for deletion removed.
            new_door_list = [door_entry for door_entry in self.scenes[scene_id].doors
                             if "delete" not in door_entry]

            # Loop over each door, convert each one to binary data, and insert them back in the map overlay.
            door_data = bytearray(0)
            for door in new_door_list:
                door_data += (int.to_bytes(door["dlist_addr"], 4, "big") +
                              int.to_bytes(door["texture_id"], 1, "big") +
                              int.to_bytes(door["palette_id"], 1, "big") +
                              int.to_bytes(door["byte_6"], 1, "big") + b'\x00' +
                              int.to_bytes(door["door_flags"], 2, "big") + b'\x00\00' +
                              int.to_bytes(door["extra_condition_ptr"], 4, "big") +
                              int.to_bytes(door["flag_id"], 2, "big") + b'\x00\00' +
                              int.to_bytes(door["item_id"], 4, "big") +
                              int.to_bytes(door["front_room_id"], 1, "big") +
                              int.to_bytes(door["back_room_id"], 1, "big") +
                              int.to_bytes(door["cant_open_text_id"], 1, "big") +
                              int.to_bytes(door["unlocked_text_id"], 1, "big") +
                              int.to_bytes(door["byte_1c"], 1, "big") + b'\x00' +
                              int.to_bytes(door["opening_sound_id"], 2, "big") +
                              int.to_bytes(door["half_20"], 2, "big") +
                              int.to_bytes(door["closing_sound_id"], 2, "big") +
                              int.to_bytes(door["half_24"], 2, "big") +
                              int.to_bytes(door["shut_sound_id"], 2, "big") +
                              int.to_bytes(door["half_28"], 2, "big") +
                              int.to_bytes(door["half_2a"], 2, "big"))

            # If the new door data is the same size or smaller than it was before, write it back where it was
            # originally (if we even have a list to begin with).
            if len(new_door_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].doors
                                          if "start_addr" in orig_entry]):
                if new_door_list:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].doors[0]["start_addr"] \
                                                          - SCENE_OVERLAY_RDRAM_START, door_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_door_list_addr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += door_data
                self.write_int32(SCENE_DOOR_PTRS_START + (scene_id * 4), new_door_list_addr)


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
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].loading_zones[0]["start_addr"] \
                                                          - SCENE_OVERLAY_RDRAM_START, loading_zone_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_loading_zone_list_ptr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += loading_zone_data
                self.write_int32(SCENE_LOADING_ZONE_PTRS_START + (scene_id * 4), new_loading_zone_list_ptr)


            # # # TEXT # # #
            # Create the final text list with all entries primed for deletion removed.
            new_text_list = [text_entry for text_entry in self.scenes[scene_id].scene_text
                             if "delete" not in text_entry]

            # Loop over each text, convert each one to binary data, and insert them back in the map overlay.
            text_data = bytearray(0)
            new_text_size = 0
            for scene_text in new_text_list:
                new_text_size += len(scene_text["text"]) + 1
                text_data += (cvlod_string_to_bytearray(scene_text["text"], wrap=False, add_end_char=True))
            # Add the character indicating the end of the entire text pool.
            text_data += CVLOD_TEXT_POOL_END_CHARACTER

            # Pad the text data to be 4-aligned.
            if len(text_data) % 4:
                text_data += b'\x00\x00'

            # If the new text data is the same size or smaller than it was before, write it back where it was originally
            # (if we even have a list to begin with).
            if new_text_size <= self.scenes[scene_id].scene_text_orig_size:
                if new_text_list:
                    self.scenes[scene_id].write_ovl_bytes(self.scenes[scene_id].scene_text[0]["start_addr"] \
                                                          - SCENE_OVERLAY_RDRAM_START, text_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it
            # (if it's not higher than Outer Wall's as that's where the pointer table ends).
            elif scene_id <= Scenes.THE_OUTER_WALL:
                new_text_pool_ptr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += text_data
                self.write_int32(SCENE_TEXT_PTRS_START + (scene_id * 4), new_text_pool_ptr)


            # # # SPAWN SPOTS # # #
            # Create the final spawn spots list with all entries primed for deletion removed.
            new_spawn_list = [spawn_entry for spawn_entry in self.scenes[scene_id].spawn_spots
                              if "delete" not in spawn_entry]

            # Loop over each spawn spot, convert each one to binary data, and insert them back in the map overlay.
            spawn_data = bytearray(0)
            for spawn in new_spawn_list:
                spawn_data += (int.to_bytes(spawn["room_id"], 2, "big") +
                               struct.pack(">h", spawn["player_x_pos"]) +
                               struct.pack(">h", spawn["player_y_pos"]) +
                               struct.pack(">h", spawn["player_z_pos"]) +
                               struct.pack(">h", spawn["player_rotation"]) +
                               struct.pack(">h", spawn["camera_x_pos"]) +
                               struct.pack(">h", spawn["camera_y_pos"]) +
                               struct.pack(">h", spawn["camera_z_pos"]) +
                               struct.pack(">h", spawn["focus_x_pos"]) +
                               struct.pack(">h", spawn["focus_y_pos"]) +
                               struct.pack(">h", spawn["focus_z_pos"]))

            # Pad the list data to be 4-aligned.
            if len(spawn_data) % 4:
                spawn_data += b'\x00\x00'

            # If the new spawn spot data is the same size or smaller than it was before, write it back where it was
            # in the common segment originally (if we even have a list to begin with).
            if len(new_spawn_list) <= len([orig_entry for orig_entry in self.scenes[scene_id].spawn_spots
                                                  if "start_addr" in orig_entry]):
                if new_spawn_list:
                    self.write_bytes(self.scenes[scene_id].spawn_spots[0]["start_addr"] \
                                                          - COMMON_SEGMENT_RDRAM_START + COMMON_SEGMENT_ROM_START,
                                     spawn_data)
            # If it's larger, however, put it on the end of the overlay and update the pointer to it.
            else:
                new_spawn_list_ptr = len(self.scenes[scene_id].overlay) + SCENE_OVERLAY_RDRAM_START
                self.scenes[scene_id].overlay += spawn_data
                self.write_int32(SCENE_SPAWN_COORDS_PTRS_START + (scene_id * 4), new_spawn_list_ptr)


            # Pad the overlay to 0x10 if it isn't.
            while len(self.scenes[scene_id].overlay) % 0x10:
                self.scenes[scene_id].overlay += b'\x00'

            # Write the final scene overlay back into the ROM.
            new_overlay_start = self.find_space_and_write_file(self.scenes[scene_id].overlay)
            # Update the pointers to the start and end of the overlay in both the ROM and RDRAM scene overlay pointers
            # table.
            self.write_int32(SCENE_OVERLAY_ROM_ADDRS_START + (scene_id * 8), new_overlay_start)
            self.write_int32((SCENE_OVERLAY_ROM_ADDRS_START + (scene_id * 8)) + 4,
                             new_overlay_start + len(self.scenes[scene_id].overlay))
            self.write_int32(SCENE_OVERLAY_RDRAM_ADDRS_START + (scene_id * 8) + 4,
                             SCENE_OVERLAY_RDRAM_START + len(self.scenes[scene_id].overlay))


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

        # Return the final output ROM
        return bytes(self.rom)
