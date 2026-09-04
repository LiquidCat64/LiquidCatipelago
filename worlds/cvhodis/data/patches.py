
class DynamicGBAAsmPatch:
    assembly: list[int]
    ldr_numbers: list[int]
    input_ptrs: list[int]

    def __init__(self, assembly: list[int], ldr_numbers: list[int]):
        self.assembly = assembly
        self.ldr_numbers = ldr_numbers

item_palette_defaulter_asm = [
    # So normally, item pickup sprites in the game have a choice of either using a palette that the game always keeps
    # loaded, or a custom one that is dynamically loaded in with the item sprite. Up to two custom item palettes can be
    # loaded at once, and if the game tries loading a third item with a third distinct custom palette that's not already
    # being used by something else at that point, the item will despawn instantly. This can be quite problematic in
    # rooms that have more than 2 location checks inside them, so to """""fix""""" the issue, this hack will, instead of
    # despawn the item, switch its palette to the always-loaded OBP1 one. The item will look weird, but it's still
    # better than any potential seed softlock scenarios that may arise from the alternative...
    0x1602,  # asr r2, r0, 18
    0x21FF,  # mov r1, 0xFF
    0x4011,  # and r1, r2
    0x20FF,  # mov r0, 0xFF
    0x4288,  # cmp r0, r1
    0xD100,  # bne [forward 0x01]
    0x2201,  # mov r2, 0x01
    0x2F00,  # cmp r7, 0x00
    0xDB02,  # blt [forward 0x03]
    0x2A00,  # cmp r2, 0x00
    0x4800,  # ldr  r0, 0x80197D8
    0xE000,  # b   [forward 0x01]
    0x4801,  # ldr  r0, 0x80197DA
    0x4687,  # mov  r15, r0
]
item_palette_defaulter_ldr = [
    0x080197D8,
    0x080197DA,
]


extras_unlocker_asm = [
    # On the Konami logo screen, this will set all flags in the save file (in both EWRAM and SRAM) that unlock all
    # postgame extras. Including Boss Rush; playable Maxim; hard mode; and, most importantly, the ability to skip all
    # cutscenes.
    0x21C2,  # mov r1, 0xC2
    0x6001,  # str r1, [r0]
    0x4801,  # ldr r0, 0xE000BF8
    0x6001,  # str r1, [r0]
    0x4800,  # ldr r0, 0x8001FFC
    0x4687,  # mov r15, r0
]
extras_unlocker_ldr = [
    0x08001FFC,
    0x0E000BF8,
]

remote_textbox_shower_asm = [
    # Pops up the textbox(s) of whatever textbox IDs is written at 0x02018A00 and 0x02018A02 and increments the current
    # received item index at 0x02028862 if a number to increment it by is written at 0x02018A04. Also plays the sound
    # effect of the ID written at 0x02018A06, if one is written there. The halfword at 0x02018A08 is a frame delay timer
    # for any situations wherein it'd be unsafe to trigger any of this stuff, and the byte at 0x02018A0A is used to tell
    # whether there is a center-screen textbox that should be cleared or not.
    #
    # This will NOT give any items on its own; the item has to be written by the client into the inventory alongside
    # writing the above-mentioned things.

    # Run the function that checks to see if the player is on top of a loading zone. If they are, skip doing any more of
    # this.
    0x1840,  # add  r0, r0, r1
    0x6800,  # ldr  r0, [r0]
    0x4A08,  # ldr  r2, 0x800AF38
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    0xB431,  # push r0, r4, r5
    0x2800,  # cmp  r0, 0x00
    0xD103,  # bne [forward 0x04]
    # If we were in a loading zone, un-prime the center textbox for deletion. The textbox wll have been auto-deleted
    # upon room transitioning by the next time this runs. This is more likely to occur while going through a door.
    0x4800,  # ldr  r0, 0x2018A00
    0x2100,  # mov  r1, 0x00
    0x7281,  # strb r1, [r0, 0x0A]
    0xE062,  # b    [forward 0x63]
    # Check the current menu state to make sure it's safe to call a textbox and that we are not in a room transition
    # or something else that would cause problems. If it's not safe, skip running anything else here.
    0x4A07,  # ldr  r2, 0x2000048
    0x7813,  # ldrb r3, [r2]
    0x2B01,  # cmp  r3, 0x01
    0xD15E,  # bne [forward 0x5F]
    # Check the "on-screen textbox" byte to see if the 0x01 or 0x02 bit is set. If either is, we are looking at a
    # textbox or max up graphic and Juste should be frozen in place.
    0x4A09,  # ldr  r2, 0x2000000
    0x2003,  # mov  r0, 0x03
    0x7BD3,  # ldrb r3, [r2, 0x0F]
    0x4003,  # and  r3, r0
    0x2B00,  # cmp  r3, 0x00
    0xD158,  # bne  [forward 0x59]
    # Check the "in control of player" byte to make sure we are not in a cutscene or saving.
    0x7ED3,  # ldrb r3, [r2, 0x1B]
    0x2B00,  # cmp  r3, 0x00
    0xD155,  # bne  [forward 0x56]
    # Check the "delay" timer buffer for a non-zero. If it is, decrement it by one and skip straight to the return part
    # of this code, as we may have received an item on a frame wherein it's "unsafe" to pop the item textboxes.
    0x4A00,  # ldr  r2, 0x2018A00
    0x8913,  # ldrh r3, [r2, 0x08]
    0x2B00,  # cmp  r3, 0x00
    0xD002,  # beq  [forward 0x03]
    0x3B01,  # sub  r3, 0x01
    0x8113,  # strh r3, [r2, 0x08]
    0xE04E,  # b    [forward 0x4F]
    # Run the "clear center-screen textbox" function if our "primed" byte for it is set.
    0x4800,  # ldr  r0, 0x2018A00
    0x7A81,  # ldrb r1, [r0, 0x0A]
    0x2900,  # cmp  r1, 0x00
    0xD009,  # beq  [forward 0x0A]
    0x200E,  # mov  r0, 0x0E
    0x2101,  # mov  r1, 0x01
    0x4A06,  # ldr  r2, 0x802B5DC
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    0x4800,  # ldr  r0, 0x2018A00
    0x2100,  # mov  r1, 0x00
    0x7281,  # strb r1, [r0, 0x0A]
    # Check our bottom-left corner textbox buffer for a non-zero number. If we have one, run the "display bottom-left
    # blue corner textbox" function with that number in r0.
    0x8800,  # ldrh r0, [r0]
    0x2800,  # cmp  r0, 0x00
    0xD00C,  # beq  [forward 0x0D]
    0x4A01,  # ldr  r2, 0x8008980
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Run the "update movement abilities" function in case we were given a movement Relic.
    0x480B,  # ldr  r0, 0x80290C0
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4687,  # mov  r15, r0
    # Add sixty frames (1 second) to the delay timer.
    0x4800,  # ldr  r0, 0x2018A00
    0x213C,  # mov  r1, 0x3C
    0x8101,  # strh r1, [r0, 0x08]
    # Check our center textbox buffer for a non-zero number. If we have one, run the "display gray center-of-screen
    # textbox" function with that number in r1 and 0xE in r2.
    0x4A00,  # ldr  r2, 0x2018A00
    0x8851,  # ldrh r1, [r2, 0x02]
    0x2900,  # cmp  r1, 0x00
    0xD00F,  # beq  [forward 0x10]
    0x220E,  # mov  r2, 0x0E
    0x4802,  # ldr  r0, 0x802B4E4
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4687,  # mov  r15, r0
    # Run the "update movement abilities" function in case we were given a movement Relic.
    0x480B,  # ldr  r0, 0x80290C0
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4687,  # mov  r15, r0
    # Add two frames to the delay timer and prime the textbox for deletion upon regaining control.
    0x4800,  # ldr  r0, 0x2018A00
    0x2102,  # mov  r1, 0x02
    0x8101,  # strh r1, [r0, 0x08]
    0x2101,  # mov  r1, 0x01
    0x7281,  # strb r1, [r0, 0x0A]
    # Check our max up buffer for a non-zero number. If we have one, run the "call max up graphic" function with that
    # number minus 1 in r0.
    0x4800,  # ldr  r0, 0x2018A00
    0x7AC0,  # ldrb r0, [r0, 0x0B]
    0x2800,  # cmp  r0, 0x00
    0xD005,  # beq  [forward 0x06]
    0x3801,  # sub  r0, 0x01
    0x4A0A,  # ldr  r2, 0x801A8B0
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Increase the "received item index" by the specified number in our "item index amount to increase" buffer.
    0x4800,  # ldr  r0, 0x2018A00
    0x8883,  # ldrh r3, [r0, 0x04]
    0x4A05,  # ldr  r2, 0x2028872
    0x8811,  # ldrh r1, [r2]
    0x18C9,  # add  r1, r1, r3
    0x8011,  # strh r1, [r2]
    # Check our "sound effect ID" buffer and run the "play sound" function if it's a non-zero number.
    0x88C0,  # ldrh r0, [r0, #6]
    0x2800,  # cmp  r0, #0
    0xD004,  # beq  [forward 0x05]
    0x4A04,  # ldr  r2, 0x80BB120
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Clear all our buffers and return to the "check for player inputs" function we've hooked into.
    0x4800,  # ldr  r0, 0x2018A00
    0x2100,  # mov  r1, #0
    0x6001,  # str  r1, [r0]
    0x6041,  # str  r1, [r0, 0x04]
    0x72C1,  # strb r1, [r0, 0x0B]
    0xBC31,  # pop  r0, r4, r5
    0x4A03,  # ldr  r2, 0x8007554
    0x4697,  # mov  r15, r2
]
remote_textbox_shower_ldr = [
    0x02018A00,
    0x08008980,
    0x0802B4E4,
    0x08007554,
    0x080BB120,
    0x02018872,
    0x0802B5DC,
    0x02000048,
    0x0800AF38,
    0x02000000,
    0x0801A8B0,
    0x080290C0,
]

furniture_pickup_customizer_asm = [
    # Blocks putting furniture with an index higher than 0x1E in the inventory upon picking one up; all furniture with
    # an index higher than that are AP off-world items. In addition, if the index is 0x21 (our AP Trap item), the pickup
    # sound effect will be changed to a specific "trap" sound.
    0xB410,  # push r4
    0x1C0C,  # add  r4, r1, 0x00
    0x4001,  # and  r1, r0
    0x2001,  # mov  r0, 0x01
    0x4088,  # lsl  r0, r1
    0x7811,  # ldrb r1, [r2]
    0xB404,  # push r2
    0x2C21,  # cmp  r4, 0x21
    0xD101,  # bne  [forward 0x02]
    0x228F,  # mov  r2, 0x8F
    0x4690,  # mov  r2, r8
    0x4B00,  # ldr  r3, 0x801A1D8
    0x2C1E,  # cmp  r4, 0x1E
    0xDD00,  # ble  [forward 0x01]
    0x3304,  # add  r3, 0x04
    0xBC14,  # pop  r2, r4
    0x469F,  # mov  r15, r3
]
furniture_pickup_customizer_ldr = [
    0x0801A1D8
]

start_inventory_giver_asm = [
    # When the player create function runs upon starting a new game, this will give the player their entire start
    # inventory. Item/equipment counts, relics, etc. will be copied into their respective inventories.

    # Also handles anything extra that should be done upon file creation, like setting any additional flags.
    0x84A0,  # strh r0, [r4, 0x24]
    # Use Items
    0x4800,  # ldr  r0, 0x20187A0
    0x490B,  # ldr  r1, start_inventory_use_start
    0x2200,  # mov  r2, 0x00
    0x588B,  # ldr  r3, [r1, r2]
    0x5083,  # str  r3, [r0, r2]
    0x3204,  # add  r2, 0x04
    0x2A1C,  # cmp  r2, 0x1C
    0xDBFA,  # blt [backward 0x05]
    # Equipment
    0x4801,  # ldr  r0, 0x20187BE
    0x490C,  # ldr  r1, start_inventory_equip_start
    0x2200,  # mov  r2, 0x00
    0x5A8B,  # ldrh r3, [r1, r2]
    0x5283,  # strh r3, [r0, r2]
    0x3202,  # add  r2, 0x02
    0x2A80,  # cmp  r2, 0x80
    0xDBFA,  # blt [backward 0x05]
    # Spell Books
    0x4802,  # ldr  r0, 0x201883E
    0x490D,  # ldr  r1, start_inventory_book_start
    0x780B,  # ldrb r3, [r1]
    0x7003,  # strb r3, [r0]
    0x784B,  # ldrb r3, [r1, 0x01]
    0x4803,  # ldr  r0, 0x201877F
    0x7003,  # strb r3, [r0]
    # Relics
    0x4804,  # ldr  r0, 0x201883F
    0x490E,  # ldr  r1, start_inventory_relic_start
    0x2200,  # mov  r2, 0x00
    0x5C8B,  # ldrb r3, [r1, r2]
    0x5483,  # strb r3, [r0, r2]
    0x1C80,  # add  r0, r0, 0x02
    0x5483,  # strb r3, [r0, r2]
    0x1E80,  # sub  r0, r0, 0x02
    0x3201,  # add  r2, 0x01
    0x2A02,  # cmp  r2, 0x02
    0xDBF7,  # blt [backward 0x08]
    # Furniture
    0x4805,  # ldr  r0, 0x2018843
    0x490F,  # ldr  r1, start_inventory_furn_start
    0x2200,  # mov  r2, 0x00
    0x5C8B,  # ldrb r3, [r1, r2]
    0x5483,  # strb r3, [r0, r2]
    0x3201,  # add  r2, 0x01
    0x2A04,  # cmp  r2, 0x04
    0xDBFA,  # blt [backward 0x05]
    # Whip attachments
    0x4806,  # ldr  r0, 0x20187BC
    0x4910,  # ldr  r1, start_inventory_whips_start
    0x880B,  # ldrh r3, [r1]
    0x8003,  # strh r3, [r0]
    # Extra HP, MP, and Hearts
    0x4807,  # ldr  r0, 0x2018786
    0x4911,  # ldr  r1, start_inventory_max_start
    # Max HP
    0x880A,  # ldrh r2, [r1]
    0x8803,  # ldrh r3, [r0]
    0x189B,  # add  r3, r3, r2
    0x8003,  # strh r3, [r0]
    # Max MP
    0x884A,  # ldrh r2, [r1, 0x02]
    0x8843,  # ldrh r3, [r0, 0x02]
    0x189B,  # add  r3, r3, r2
    0x8043,  # strh r3, [r0, 0x02]
    # Max Hearts
    0x888A,  # ldrh r2, [r1, 0x04]
    0x8883,  # ldrh r3, [r0, 0x04]
    0x189B,  # add  r3, r3, r2
    0x8083,  # strh r3, [r0, 0x04]
    # Current Hearts
    0x89C3,  # ldrh r3, [r0, 0x0E]
    0x189B,  # add  r3, r3, r2
    0x81C3,  # strh r3, [r0, 0x0E]
    # Set the "can see Castle A + B maps" flag.
    0x4808,  # ldr  r0, 0x200030D
    0x7801,  # ldrb r1, [r0]
    0x2280,  # mov  r2, 0x80
    0x4311,  # orr  r1, r2
    0x7001,  # strb r1, [r0]
    # Return to the function that gives characters their starting stuff.
    0x4B09,  # ldr  r3, 0x8494580
    0x6819,  # ldr  r1, [r3]
    0x8AE2,  # ldrh r2, [r4, 0x16]
    0x480A,  # ldr  r0, 0x806B738
    0x4687,  # mov  r15, r0
]
start_inventory_giver_ldr = [
    0x020187A0,
    0x020187BE,
    0x0201883E,
    0x0201877F,
    0x0201883F,
    0x02018843,
    0x020187BC,
    0x02018786,
    0x0200030D,
    0x08494580,
    0x0806B738,
]

major_pickup_sound_player_asm = [
    # When picking up a piece of equipment, this will check to see if it was JB's Bracelet that was picked up and, if it
    # was, sets the "can warp castles" flag and changes the pickup sound to play to be the "major" sound.
    0xB405,  # push r0, r2
    0x203A,  # mov  r0, 0x3A
    0x5E32,  # ldsh r2, [r6, r0]
    0x2A2A,  # cmp  r2, 0x2A
    0xD101,  # bne  [forward 0x02]
    0x2036,  # mov  r0, 0x36
    0x4680,  # mov  r8, r0
    0xBC05,  # pop  r0, r2
    0x304E,  # add  r0, 0x4E
    0x1882,  # add  r2, r0, r2
    0x7810,  # ldrb r0, [r2]
    0x2862,  # cmp  r0, 0x62
    0x4B00,  # ldr  r3, 0x8019F8C
    0x469F,  # mov  r15, r3
]
major_pickup_sound_player_ldr = [
    0x08019F8C
]

jb_bracelet_checker_asm = [
    # When the round gate update code runs, this will check to see if JB's Bracelet is equipped or in the inventory. If
    # it is, the "can warp between castles" flag will be set, allowing warping between castles and warping to unvisited
    # warp rooms in the same castle that were visited in the other castle.

    # Check if JB's Bracelet is in the inventory.
    0xB401,  # push r0
    0x2000,  # mov  r0, 0x00
    0x4902,  # ldr  r1, 0x20187E8
    0x7808,  # ldrb r0, [r1]
    0x3968,  # sub  r1, 0x68
    # Check if JB's Bracelet is in any of the three equipped accessory slots.
    0x784A,  # ldrb r2, [r1, 0x01]
    0x2A2A,  # cmp  r2, 0x2A
    0xD100,  # bne  [forward 0x01]
    0x3001,  # add  r0, 0x01
    0x788A,  # ldrb r2, [r1, 0x01]
    0x2A2A,  # cmp  r2, 0x2A
    0xD100,  # bne  [forward 0x01]
    0x3001,  # add  r0, 0x01
    0x78CA,  # ldrb r2, [r1, 0x01]
    0x2A2A,  # cmp  r2, 0x2A
    0xD100,  # bne  [forward 0x01]
    0x3001,  # add  r0, 0x01
    # If JB's Bracelet was in any of the above, set the "can warp between castles" flag. Otherwise, un-set it.
    0x4901,  # ldr  r1, 0x200031B
    0x780A,  # ldrb r2, [r1]
    0x2800,  # cmp  r0, 0x00
    0xD102,  # bne  [forward 0x03]
    0x23DF,  # mov  r3, 0xDF
    0x401A,  # and  r2, r3
    0xE001,  # b    [forward 0x02]
    0x2320,  # mov  r3, 0x20
    0x431A,  # orr  r2, r3
    0x700A,  # strb r2, [r1]
    # Go to and run the round gate's regular update code like normal.
    0xBC01,  # pop  r0
    0x4B00,  # ldr  r3, 0x801BB58
    0x469F,  # mov  r15, r3
]
jb_bracelet_checker_ldr = [
    0x0801BB58,
    0x0200031B,
    0x020187E8,
]

portal_death_room_checker_asm = [
    # When a warp room gate initializes, this will run to see if we are currently in Death's room in Clock Tower and,
    # if we are, start the gate in its open state. Should be skipped entirely if the death cutscene flag is set.

    # Check to see if the player's room coordinates are 70, 0C.
    0x2102,  # mov  r1, 0x02
    0x0609,  # lsl  r1, r1, 0x18
    0x3170,  # add  r1, 0x70
    0x8809,  # ldrh r1, [r1]
    0x220C,  # mov  r2, 0x0C
    0x0212,  # lsl  r2, r2, 0x08
    0x3270,  # add  r2, 0x70
    0x4291,  # cmp  r1, r2
    0xD001,  # beq  [forward 0x02]
    # If they aren't, jump to the "close gates" part of the code.
    0x4900,  # ldr  r1, 0x801BB18
    0x468F,  # mov  r15, r1
    # If they are, jump to the "open gates" part of the code.
    0x0380,  # lsl  r0, r0, 0x0E
    0x6160,  # str  r0, [r4, 0x14]
    0x201E,  # mov  r0, 0x1E
    0x72A0,  # strb r0, [r4, 0x0A]
    0x4901,  # ldr  r1, 0x801BB44
    0x468F,  # mov  r15, r1
]
portal_death_room_checker_ldr = [
    0x0801BB18,
    0x0801BB44,
]

cross_castle_warp_blocker_asm = [
    # Blocks usage of the warp room cross-castle warp gates if the player doesn't have the cross-castle condition
    # satisfied. This is necessary to have due to the change of making said gate always spawn in its closed state.

    # Check to see if the "can warp castles" flag is set. If the cross-castle warp condition is satisfied, it should
    # be set.
    0x4803,  # ldr  r0, 0x200031B
    0x7800,  # ldrb r0, [r0]
    0x2120,  # mov  r1, 0x20
    0x4008,  # and  r0, r1
    0x2800,  # cmp  r0, 0x00
    0xD101,  # bne  [forward 0x02]
    # Abort the "activate round gate" function.
    0x4902,  # ldr  r1, 0x801BCB8
    0x468F,  # mov  r15, r1
    # Return to the function like normal.
    0x4901,  # ldr  r1, 0x1848C
    0x1858,  # add  r0, r3, r1
    0x6802,  # ldr  r2, [r0]
    0x7A90,  # ldrb r0, [r2, 0x0A]
    0x4900,  # ldr  r1, 0x801BC3C
    0x468F,  # mov  r15, r1
]
cross_castle_warp_blocker_ldr = [
    0x0801BC3C,
    0x0001848C,
    0x0801BCB8,
    0x0200031B,
]

double_sided_cross_castle_warp_blocker_asm = [
    # Similar to the above, except this one WILL allow the warp without the cross-castle condition satisfied on the
    # condition that the warp room on the other side has been visited. If the Double-Sided Warps option is enabled, this
    # will be injected instead.

    # Check to see if the "can warp castles" flag is set. If the cross-castle warp condition is satisfied, it should
    # be set.
    0x4803,  # ldr  r0, 0x200031B
    0x7800,  # ldrb r0, [r0]
    0x2120,  # mov  r1, 0x20
    0x4008,  # and  r0, r1
    0x2800,  # cmp  r0, 0x00
    0xD11D,  # bne  [forward 0x1E]
    # If it wasn't set, check to see if the player has the map square for the other castle's equivalent warp room.
    # If they do, then allow the warp anyway.
    0xB418,  # push r3, r4
    0x2002,  # mov  r0, 0x02
    0x0600,  # lsl  r0, r0, 0x18
    0x3070,  # add  r0, 0x70
    0x1C04,  # add  r4, r0, 0x00
    # Get the map XY coordinates of the player's current room.
    0x7820,  # ldrb r0, [r4]
    0x7861,  # ldrb r1, [r4, 0x01]
    # The left half of the map's "uncovered" flags begin at 0200008C. Set our current address to load from there.
    0x341C,  # add  r4, 0x1C
    # Left-shift the X coord by 1 to get the true value. The lowest bit in this value is actually what the game uses to
    # tell which castle we are in.
    0x0842,  # lsr  r2, r0, 0x01
    # If the X coord is 0x20 or higher, set the start address to 020001CC and subtract 0x20 from the X coord.
    # 020001CC is where the flags for the right half of the map begin.
    0x2A20,  # cmp  r2, 0x20
    0xDB02,  # blt  [forward 0x03]
    0x34FF,  # add  r4, 0xFF
    0x3441,  # add  r4, 0x41
    0x3A20,  # sub  r2, 0x20
    # Left-shift the y coord by 3 to allow us to offset to the word pair that we need to check.
    0x00C9,  # lsl  r1, r1, 0x03
    0x1864,  # add  r4, r4, r1
    # The value still left in our X coord is the index for what bit in the word to check.
    # With that in mind, prepare the bitfield to compare.
    0x2301,  # mov  r3, 0x01
    0x4093,  # lsl  r3, r2
    # The first word is for Castle A, and the second is for Castle B. If we are in Castle A, check Castle B's flags
    # or vice versa.
    0x2101,  # mov  r1, 0x01
    0x4001,  # and  r1, r0
    0x2901,  # cmp  r1, 0x01
    0xD000,  # beq  [forward 0x01]
    0x3404,  # add  r4, 0x04
    0x6820,  # ldr  r0, [r4]
    0x4018,  # and  r0, r3
    0xBC18,  # pop  r3, r4
    0x2800,  # cmp  r0, 0x00
    0xD101,  # bne  [forward 0x02]
    # Abort the "activate round gate" function.
    0x4902,  # ldr  r1, 0x801BCB8
    0x468F,  # mov  r15, r1
    # Return to the function like normal.
    0x4901,  # ldr  r1, 0x1848C
    0x1858,  # add  r0, r3, r1
    0x6802,  # ldr  r2, [r0]
    0x7A90,  # ldrb r0, [r2, 0x0A]
    0x4900,  # ldr  r1, 0x801BC3C
    0x468F,  # mov  r15, r1
]
double_sided_cross_castle_warp_blocker_ldr = [
    0x0801BC3C,
    0x0001848C,
    0x0801BCB8,
    0x0200031B,
]

unvisited_warp_destination_blocker_asm = [
    # Normally, when warping from one warp room to a different one in the current castle, if the player has been in the
    # destination warp room in the other castle, they will be warped to that room in the current castle regardless of
    # whether they've actually been in it in the current castle or not. This will prevent that if the cross-castle warp
    # condition is not satisfied yet, continuing the destination search loop if the player hasn't been to the chosen
    # destination room in the castle they are currently in.
    0x4802,  # ldr  r0, 0x200031B
    0x7800,  # ldrb r0, [r0]
    0x2120,  # mov  r1, 0x20
    0x4008,  # and  r0, r1
    0x2800,  # cmp  r0, 0x00
    0xD10F,  # bne  [forward 0x10]
    0x1C31,  # add  r1, r6, 0x00
    0x3144,  # add  r1, 0x44
    0x1889,  # add  r1, r1, r2
    0x4803,  # ldr  r0, 0x2000070
    0x7800,  # ldrb r0, [r0]
    0x2201,  # mov  r2, 0x01
    0x4010,  # and  r0, r2
    0x2800,  # cmp  r0, 0x00
    0xD000,  # beq  [forward 0x01]
    0x3104,  # add  r1, 0x04
    0x6808,  # ldr  r0, [r1]
    0x4018,  # and  r0, r3
    0x2800,  # cmp  r0, 0x00
    0xD101,  # bne  [forward 0x02]
    0x4B01,  # ldr  r3, 0x8009BD4
    0x469F,  # mov  r15, r3
    0x4640,  # mov  r0, r8
    0x7801,  # ldrb r1, [r0]
    0x07C9,  # lsl  r1, r1, 0x1F
    0x0FC9,  # lsr  r1, r1, 0x1F
    0x0089,  # lsl  r1, r1, 0x02
    0x4B00,  # ldr  r3, 0x8009C38
    0x469F,  # mov  r15, r3
]
unvisited_warp_destination_blocker_ldr = [
    0x08009C38,
    0x08009BD4,
    0x0200031B,
    0x02000070,
]

start_spawn_setter_asm = [
    # While saving (through either a save room or the pause menu), if the player is holding down R, their map spawn
    # coordinates will be set to 0E 17 (the first interior room of Entrance A) instead of wherever their last save room
    # save was. Very important feature to have for softlock prevention in the event that the player saves at a save room
    # in a location they cannot return from, like in Castle Treasury A if they made it there through the skull door
    # without double jump with the vanilla area layout.

    # Check if the player is holding R.
    0xB401,  # push r0
    0x2102,  # mov  r1, 0x02
    0x0609,  # lsl  r1, r1, 0x18
    0x7D4A,  # ldrb r2, [r1, 0x15]
    0x2301,  # mov  r3, 0x01
    0x401A,  # and  r2, r3
    0x2A01,  # cmp  r2, 0x01
    0xD110,  # bne  [forward 0x11]
    # If they were, set 0E 17 as their spawn room coordinates.
    0x2203,  # mov  r2, 0x03
    0x0212,  # lsl  r2, r2, 0x08
    0x1852,  # add  r2, r2, r1
    0x230E,  # mov  r3, 0x0E
    0x7313,  # strb r3, [r2, 0x0C]
    0x2317,  # mov  r3, 0x17
    # Careful not to un-set the "Castle A + B maps viewable" flags!
    0x7B50,  # ldrb r0, [r2, 0x0D]
    0x21C0,  # mov  r1, 0xC0
    0x4008,  # and  r0, r1
    0x4303,  # orr  r3, r0
    0x7353,  # strb r3, [r2, 0x0D]
    # Run the "play sound" function with sound 0x35 to indicate the set was successful.
    0x2035,  # mov  r0, 0x35
    0x4A02,  # ldr  r2, 0x80BB120
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Return to the save function like normal.
    0xBC01,  # pop  r0
    0x4F01,  # ldr  r7, 0x8494580
    0x01F0,  # lsl  r0, r6, 0x07
    0x1B80,  # sub  r0, r0, r6
    0x00C5,  # lsl  r5, r0, 0x03
    0x4B00,  # ldr  r3, 0x800BA60
    0x469F,  # mov  r15, r3
]
start_spawn_setter_ldr = [
    0x0800BA60,
    0x08494580,
    0x080BB120,
]

post_intro_autosave_asm = [
    # Autosaves the game after Talos dies in the intro sequence so there's no need to go out of your way to save to use
    # the warp-to-start feature.

    # "Force-hold" R on this frame to trigger the start spawn setter hack.
    0xB404,  # push r2
    0x2102,  # mov  r1, 0x02
    0x0609,  # lsl  r1, r1, 0x18
    0x7D4A,  # ldrb r2, [r1, 0x15]
    0x2301,  # mov  r3, 0x01
    0x431A,  # orr  r2, r3
    0x754A,  # strb r2, [r1, 0x15]
    # Run the "update file metadata" function.
    0x2002,  # mov  r0, 0x02
    0x0600,  # lsl  r0, r0, 0x18
    0x3048,  # add  r0, 0x48
    0x4A03,  # ldr  r2, 0x800BA0C
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Run the save game function with the current save file number in r0.
    0x2002,  # mov  r0, 0x02
    0x0400,  # lsl  r0, r0, 0x10
    0x3004,  # add  r0, 0x04
    0x0200,  # lsl  r0, r0, 0x08
    0x78C0,  # ldrb r0, [r0, 0x03]
    0x4A01,  # ldr  r2, 0x800BA54
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Run the "display green corner textbox" with our custom "saved" text ID.
    0x2002,  # mov  r0, 0x02
    0x0200,  # lsl  r0, r0, 0x08
    0x3046,  # add  r0, 0x46
    0x4A02,  # ldr  r2, 0x8008330
    0x467B,  # mov  r3, r15
    0x3305,  # add  r3, 0x05
    0x469E,  # mov  r14, r3
    0x4697,  # mov  r15, r2
    # Return to the "delete intro Talos" function.
    0xBC04,  # pop  r2
    0x3261,  # add  r2, 0x61
    0x7810,  # ldrb r0, [r2]
    0x2108,  # mov  r1, 0x08
    0x4308,  # orr  r0, r1
    0x4B00,  # ldr  r3, 0x8095554
    0x469F,  # mov  r15, r3
]
post_intro_autosave_ldr = [
    0x08095554,
    0x0800BA54,
    0x08008330,
    0x0800BA0C,
]

extra_item_sprites = {
    # The GFX data for any inserted extra item sprites, including the Archipelago Items. Graphics in this game are
    # arranged very differently from how they are in Circle of the Moon, with each VRAM tile row being separated out in
    # a way that makes it easier to see in a standard VRAM viewer instead of just every row grouped with the sprite.

    # NOTE: The Archipelago logo is © 2022 by Krista Corkos and Christopher Wilson
    # and licensed under Attribution-NonCommercial 4.0 International.
    # See LICENSES.txt at the root of this apworld's directory for more licensing information.

    # Archipelago Filler top half
    0xEF794: [0x00, 0x00, 0x00, 0x33, 0x00, 0x00, 0x30, 0x44, 0x00, 0x33, 0x43, 0x44, 0x30, 0x66, 0x36, 0x44,
              0x63, 0x66, 0x63, 0x43, 0x63, 0x66, 0x66, 0x43, 0x63, 0x33, 0x63, 0x33, 0x30, 0xEE, 0x3E, 0x00,
              0x03, 0x00, 0x00, 0x00, 0x34, 0x00, 0x00, 0x00, 0x43, 0x33, 0x03, 0x00, 0x34, 0xCC, 0x3C, 0x00,
              0xC3, 0xCC, 0xC3, 0x03, 0xC3, 0xCC, 0xCC, 0x03, 0xC3, 0x33, 0xC3, 0x03, 0x30, 0x99, 0x39, 0x00],
    # Archipelago Progression top half
    0xEF7D4: [0x00, 0x00, 0x00, 0x33, 0x00, 0x00, 0x30, 0x44, 0x00, 0x33, 0x43, 0x44, 0x30, 0x66, 0x36, 0x44,
              0x63, 0x66, 0x63, 0x43, 0x63, 0x66, 0x66, 0x43, 0x63, 0x33, 0x63, 0x33, 0x30, 0xEE, 0x3E, 0x00,
              0x03, 0xF0, 0x00, 0x00, 0x34, 0x5F, 0x0F, 0x00, 0xF3, 0x55, 0xF5, 0x00, 0x5F, 0x55, 0x55, 0x0F,
              0xFF, 0x55, 0xF5, 0x0F, 0xF3, 0x55, 0xF5, 0x03, 0xF3, 0xFF, 0xFF, 0x03, 0x30, 0x99, 0x39, 0x00],
    # Archipelago Filler bottom half
    0xEF994: [0xE3, 0xEE, 0xE3, 0x03, 0xE3, 0xEE, 0xEE, 0x33, 0xE3, 0xEE, 0x3E, 0x55, 0x30, 0xEE, 0x53, 0x55,
              0x00, 0x33, 0x53, 0x55, 0x00, 0x00, 0x53, 0x55, 0x00, 0x00, 0x30, 0x55, 0x00, 0x00, 0x00, 0x33,
              0x93, 0x99, 0x93, 0x03, 0x93, 0x99, 0x99, 0x03, 0x35, 0x99, 0x99, 0x03, 0x53, 0x93, 0x39, 0x00,
              0x55, 0x33, 0x03, 0x00, 0x55, 0x03, 0x00, 0x00, 0x35, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00],
    # Archipelago Progression bottom half
    0xEF9D4: [0xE3, 0xEE, 0xE3, 0x03, 0xE3, 0xEE, 0xEE, 0x33, 0xE3, 0xEE, 0x3E, 0x55, 0x30, 0xEE, 0x53, 0x55,
              0x00, 0x33, 0x53, 0x55, 0x00, 0x00, 0x53, 0x55, 0x00, 0x00, 0x30, 0x55, 0x00, 0x00, 0x00, 0x33,
              0x93, 0x99, 0x93, 0x03, 0x93, 0x99, 0x99, 0x03, 0x35, 0x99, 0x99, 0x03, 0x53, 0x93, 0x39, 0x00,
              0x55, 0x33, 0x03, 0x00, 0x55, 0x03, 0x00, 0x00, 0x35, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00],
    # Archipelago Useful top half
    0xEFA14: [0x00, 0x00, 0x00, 0x33, 0x00, 0x00, 0x30, 0x44, 0x00, 0x33, 0x43, 0x44, 0x30, 0x66, 0x36, 0x44,
              0x63, 0x66, 0x63, 0x43, 0x63, 0x66, 0x66, 0x43, 0x63, 0x33, 0x63, 0x33, 0x30, 0xEE, 0x3E, 0x00,
              0x03, 0xEE, 0x0E, 0x00, 0x34, 0xDE, 0x0E, 0x00, 0xEE, 0xDE, 0xEE, 0x0E, 0xDE, 0xDD, 0xDD, 0x0E,
              0xEE, 0xDE, 0xEE, 0x0E, 0xC3, 0xDE, 0xCE, 0x03, 0xC3, 0xEE, 0xCE, 0x03, 0x30, 0x99, 0x39, 0x00],
    # Archipelago Progression + Useful top half
    0xEFA54: [0x00, 0x00, 0x00, 0x33, 0x00, 0x00, 0x30, 0x44, 0x00, 0x33, 0x43, 0x44, 0x30, 0x66, 0x36, 0x44,
              0x63, 0x66, 0x63, 0x43, 0x63, 0x66, 0x66, 0x43, 0x63, 0x33, 0x63, 0x33, 0x30, 0xEE, 0x3E, 0x00,
              0x03, 0xF0, 0x00, 0x00, 0x34, 0x5F, 0x0F, 0x00, 0xF3, 0x55, 0xF5, 0x00, 0x5F, 0x55, 0x55, 0x0F,
              0xFF, 0x55, 0xF5, 0x0F, 0xF3, 0x55, 0xF5, 0x03, 0xF3, 0xFF, 0xFF, 0x03, 0x30, 0x99, 0x39, 0x00],
    # Archipelago Trap top half
    0xEFA94: [0x00, 0x00, 0x00, 0x33, 0x00, 0x00, 0x30, 0x44, 0x00, 0x33, 0x43, 0x43, 0x30, 0x66, 0x36, 0x44,
              0x63, 0x63, 0x66, 0x43, 0x63, 0x66, 0x66, 0x43, 0x63, 0x33, 0x63, 0x33, 0x30, 0xEE, 0x3E, 0x00,
              0x03, 0xF0, 0x00, 0x00, 0x34, 0x5F, 0x0F, 0x00, 0xF4, 0x55, 0xF5, 0x00, 0x5F, 0x55, 0x55, 0x0F,
              0xFF, 0x55, 0xF5, 0x0F, 0xF3, 0x55, 0xF5, 0x03, 0xF3, 0xFF, 0xFF, 0x03, 0x30, 0x99, 0x39, 0x00],
    # Archipelago Useful bottom half
    0xEFC14: [0xE3, 0xEE, 0xE3, 0x03, 0xE3, 0xEE, 0xEE, 0x33, 0xE3, 0xEE, 0x3E, 0x55, 0x30, 0xEE, 0x53, 0x55,
              0x00, 0x33, 0x53, 0x55, 0x00, 0x00, 0x53, 0x55, 0x00, 0x00, 0x30, 0x55, 0x00, 0x00, 0x00, 0x33,
              0x93, 0x99, 0x93, 0x03, 0x93, 0x99, 0x99, 0x03, 0x35, 0x99, 0x99, 0x03, 0x53, 0x93, 0x39, 0x00,
              0x55, 0x33, 0x03, 0x00, 0x55, 0x03, 0x00, 0x00, 0x35, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00],
    # Archipelago Progression + Useful bottom half
    0xEFC54: [0xE3, 0xEE, 0xE3, 0x03, 0xE3, 0xEE, 0xEE, 0x33, 0xE3, 0xEE, 0x3E, 0x55, 0x30, 0xEE, 0x53, 0x55,
              0x00, 0x33, 0x53, 0x55, 0x00, 0x00, 0x53, 0x55, 0x00, 0x00, 0x30, 0x55, 0x00, 0x00, 0x00, 0x33,
              0x93, 0x99, 0x93, 0x03, 0x93, 0xEE, 0x9E, 0x03, 0x35, 0xDE, 0x9E, 0x03, 0xEE, 0xDE, 0xEE, 0x0E,
              0xDE, 0xDD, 0xDD, 0x0E, 0xEE, 0xDE, 0xEE, 0x0E, 0x35, 0xDE, 0x0E, 0x00, 0x03, 0xEE, 0x0E, 0x00],
    # Archipelago Trap bottom half
    0xEFC94: [0xE3, 0xE3, 0xEE, 0x03, 0xE3, 0xEE, 0xEE, 0x33, 0xE3, 0xEE, 0x3E, 0x55, 0x30, 0xEE, 0x53, 0x53,
              0x00, 0x33, 0x53, 0x55, 0x00, 0x00, 0x53, 0x55, 0x00, 0x00, 0x30, 0x55, 0x00, 0x00, 0x00, 0x33,
              0x93, 0x93, 0x99, 0x03, 0x93, 0x99, 0x99, 0x03, 0x35, 0x99, 0x99, 0x03, 0x55, 0x93, 0x39, 0x00,
              0x55, 0x33, 0x03, 0x00, 0x55, 0x03, 0x00, 0x00, 0x35, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00]
}
