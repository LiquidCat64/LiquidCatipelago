custom_code_loader = [
    # On boot, when the company logos show up, this will trigger and load most of the custom ASM data
    # from ROM offsets 0xFFC000-0xFFFFFF and into the 803FC000-803FFFFF range in RAM.
    0x3C088040,  # LUI   T0, 0x8040
    0x9108C000,  # LBU   T0, 0xC000 (T0)
    0x15000007,  # BNEZ  T0,     [forward 0x07]
    0x3C0400FF,  # LUI   A0, 0x00FF
    0x3484C000,  # ORI	A0, A0, 0xC000
    0x3C058040,  # LUI   A1, 0x8040
    0x24A5C000,  # ADDIU A1, A1, 0xC000
    0x24064000,  # ADDIU A2, R0, 0x4000
    0x0800690B,  # J     0x8001A42C
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
]

remote_item_giver = [
    # The essential multiworld function. Every frame wherein the player is in control and not looking at a text box,
    # this thing will check some bytes in RAM to see if an item or DeathLink has been received and trigger the right
    # functions accordingly to either reward items or kill the player.

    # Primary checks
    # In a demo?
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA4A,  # LBU   T1, 0xAA4A (T0)
    # In a cutscene?
    0x910AAE8B,  # LBU   T2, 0xAE8B (T0)
    0x012A4821,  # ADDU  T1, T1, T2
    # Will be in a cutscene on next map transition?
    0x910AAE8F,  # LBU   T2, 0xAE8F (T0)
    0x012A4821,  # ADDU  T1, T1, T2
    # Reading text while frozen?
    0x910AABCB,  # LBU   T2, 0xABCB (T0)
    0x012A4821,  # ADDU	 T1, T1, T2
    # Paused the game or in Renon's shop?
    0x910AAE0F,  # LBU	 T2, 0xAE0F (T0)
    0x012A4821,  # ADDU	 T1, T1, T2
    # In a fade transition?
    0x910A8354,  # LBU	 T2, 0x8354 (T0)
    0x012A4821,  # ADDU	 T1, T1, T2
    # One of the pointers to the player object not 00000000?
    0x8D0AAC1C,  # LW	 T2, 0xAC1C (T0)
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x25290001,  # ADDIU T1, T1, 0x0001
    # Timer till next item at 00?
    0x3C0B801D,  # LUI	 T3, 0x801D
    0x916AAA4E,  # LBU	 T2, 0xAA4E (T3)
    0x012A4821,  # ADDU  T1, T1, T2
    0x1120000C,  # BEQZ	 T1,     [forward 0x0C]
    # If it isn't, decrement it by 1 frame and return.
    0x8D6CAC0C,  # LW    T4, 0xAC0C (T3)
    0x11400008,  # BEQZ  T2,     [forward 0x08]
    0x254AFFFF,  # ADDIU T2, T2, 0xFFFF
    # If the player is holding C-Left while the delay timer has more than 0x10 frames left in it, set the timer to 0x10.
    # This will allow the player to turbo through the received item queue if they so desire.
    0x910D87F7,  # LBU   T5, 0x87F7 (T0)
    0x31AD0002,  # ANDI  T5, T5, 0x0002
    0x11A00003,  # BEQZ  T5,     [forward 0x03]
    0x294E0010,  # SLTI  T6, T2, 0x0010
    0x51C00001,  # BEQZL T6,     [forward 0x01]
    0x340A0010,  # ORI   T2, R0, 0x0010
    0xA16AAA4E,  # SB	 T2, 0xAA4E (T3)
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    # Item-specific checks
    # Textbox in its "map text" state?
    0x1180FFFD,  # BEQZ  T4,     [backward 0x03]
    0x00000000,  # NOP
    0x8D8F005C,  # LW    T7, 0x005C (T4)
    0x11E0FFFA,  # BEQZ  T7,     [backward 0x06]
    0x95980000,  # LHU   T8, 0x0000 (T4)
    0x1300FFF8,  # BGTZ  T8,     [backward 0x08]
    0x00000000,  # NOP
    0x8DED0038,  # LW    T5, 0x0038 (T7)
    0x11A0FFF5,  # BEQZ  T5,     [backward 0x0B]
    0x00000000,  # NOP
    0x91AE0026,  # LBU   T6, 0x0026 (T5)
    # Non-multiworld item byte occupied?
    0x9164AA4C,  # LBU	 A0, 0xAA4C (T3)
    0x10800007,  # BEQZ	 A0,     [forward 0x07]
    # Grab the DeathLink byte now for later comparisons.
    0x9178AA4F,  # LBU   T8, 0xAA4F (T3)
    # If the textbox state is not 0, call the prepare item textbox function without setting the timer nor clearing the
    # buffer. It will have to be called again on the subsequent frame(s) if that's the case.
    0x15C00004,  # BNEZ  T6,     [forward 0x04]
    0x24090090,  # ADDIU T1, R0, 0x0090
    # If the DeathLink byte is set, don't set the delay timer so that we can properly get killed on the next frame.
    0x53000001,  # BEQZL T8,     [forward 0x01]
    0xA169AA4E,  # SB	 T1, 0xAA4E (T3)
    0xA160AA4C,  # SB	 R0, 0xAA4C (T3)
    0x08021C1C,  # J     0x80087070
    0x00000000,  # NOP
    # Multiworld item byte occupied?
    0x9164AA4D,  # LBU	 A0, 0xAA4D (T3)
    0x10800025,  # BEQZ	 A0,     [forward 0x25]
    0x00000000,  # NOP
    # If we're receiving a subweapon (see: ID is between 0x0D-0x10), check if the player is above an abyss or instant
    # death floor type. If they are, don't give the subweapon on that frame so the player's old subweapon can drop to
    # a safe spot.
    0x2408000D,  # ADDIU T0, R0, 0x000D
    0x11040006,  # BEQ   T0, A0, [forward 0x06]
    0x2409000E,  # ADDIU T1, R0, 0x000E
    0x11240004,  # BEQ   T1, A0, [forward 0x04]
    0x2408000F,  # ADDIU T0, R0, 0x000F
    0x11040002,  # BEQ   T0, A0, [forward 0x02]
    0x24090010,  # ADDIU T1, R0, 0x0010
    0x1524000A,  # BNE   T1, A0, [forward 0x0A]
    # Check the floor type beneath the player for 00 (no floor), 07 (floor that kills by being in a distance above it),
    # or 0A (floor that kills by being on it).
    0x3C0A800F,  # LUI   T2, 0x800F
    0x914A393D,  # LBU   T2, 0x393D (T2)
    0x11400005,  # BEQZ  T2,     [forward 0x05]
    0x24080007,  # ADDIU T0, R0, 0x0007
    0x110A0003,  # BEQ   T0, T2, [forward 0x03]
    0x2409000A,  # ADDIU T1, R0, 0x000A
    0x152A0003,  # BNE   T1, T2, [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    # If the textbox state is not 0, again, call the item textbox without setting the timer, clearing the buffer, nor
    # increment the multiworld item index. Don't copy the incoming multiworld item text buffer either.
    0x15C00010,  # BNEZ  T6,     [forward 0x10]
    0x24090090,  # ADDIU T1, R0, 0x0090
    # If the DeathLink byte is set, don't set the delay timer so that we can properly get killed on the next frame.
    0x53000001,  # BEQZL T8,     [forward 0x01]
    0xA169AA4E,  # SB	 T1, 0xAA4E (T3)
    0xA160AA4D,  # SB	 R0, 0xAA4D (T3)
    # Increment the multiworld received item index here.
    0x956AABBE,  # LHU   T2, 0xABBE (T3)
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0xA56AABBE,  # SH    T2, 0xABBE (T3)
    # Copy the "incoming multiworld text buffer" into the primary one used for hijacking the item textbox.
    0x3C088002,  # LUI   T0, 0x8002
    0x34090000,  # ORI   T1, R0, 0x0000
    0x340B0042,  # ORI   T3, R0, 0x0042
    0x112B0005,  # BEQ   T1, T3, [forward 0x05]
    0x8D0AE6DC,  # LW    T2, 0xE6DC (T0)
    0xAD0AE5CC,  # SW    T2, 0xE5CC (T0)
    0x25290001,  # ADDIU T1, T1, 0x0001
    0x1000FFFB,  # B             [backward 0x05]
    0x25080004,  # ADDIU T0, T0, 0x0004
    0x08021C1C,  # J     0x80087070
    0x00000000,  # NOP
    # DeathLink-specific checks
    # Received any DeathLinks?
    0x17000002,  # BNEZ  T8,     [forward 0x02]
    # Is the player already dead?
    0x9169AB84,  # LBU   T1, 0xAB84 (T3)
    0x03E00008,  # JR    RA TODO: Ice Traps
    0x312A0080,  # ANDI  T2, T1, 0x0080
    0x11400002,  # BEQZ  T2,     [forward 0x02]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    # If we make it all the way here, kill the player. If Explosive Deathlink is enabled, this is where the Nitro part
    # will begin.
    # Set the delay timer to further ensure we don't get killed again on subsequent frames.
    0x24080010,  # ADDIU T0, R0, 0x0010
    0xA168AA4E,  # SB    T0, 0xAA4E (T3)
    # Give the player the "Death" status and return.
    0x35290080,  # ORI   T1, T1, 0x0080
    0x03E00008,  # JR    RA
    0xA169AB84,  # SB    T1, 0xAB84 (T3)
]

deathlink_nitro_edition = [
    # Alternative to the end of the above DeathLink-specific checks that kills the player with the Nitro explosion
    # instead of the normal death.

    # Check to see if the player is in an alright state before exploding them. If not, then the Nitro explosion spawn
    # code will be aborted, and they should eventually explode after getting out of that state.
    # Start by trying to get the player's state flags. If we find that something about the player object is not
    # currently created, abort now so we don't try pulling from a null pointer.
    0x8D64ABDC,  # LW    A0, 0xABDC (T3)
    0x14800003,  # BNEZ  A0,      [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    0x94880000,  # LHU   T0, 0x0000 (A0)
    0x15000003,  # BNEZ  T0,      [forward 0x03]
    0x8C880034,  # LW    T0, 0x0034 (A0)
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    0x15000003,  # BNEZ  T0,      [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    # Now that we have the player flags, check them for any unsafe states. Unsafe states so far include:
    # interacting/going through a door (00200000), knocked back or grabbed by something (00008000),
    # having iframes (20000000).
    0x8D080000,  # LW    T0, 0x0000 (T0)
    0x3C092020,  # LUI   T1, 0x2020
    0x35298000,  # ORI   T1, T1, 0x8000
    0x01095024,  # AND   T2, T0, T1
    0x1540FFF9,  # BNEZ  T2,     [backward 0x07]
    # If we make it all the way here, explode the player.
    # Set the delay timer to further ensure we don't get exploded again on subsequent frames.
    0x24080010,  # ADDIU T0, R0, 0x0010
    0xA168AA4E,  # SB    T0, 0xAA4E (T3)
    # Create the Nitro explosion actor with the player actor as its parent.
    0x08000904,  # J     0x80002410
    0x240500A8,  # ADDIU A1, R0, 0x00A8
]

warp_menu_opener = [
    # Enables warping by pausing while holding Z + R. Un-sets the Henry escort begins flag if you warp during it.

    # Check if the player is holding Z and R when the game wants to pause. If they aren't, pause like normal.
    # If they are, run some additional checks to see if the warp menu can be opened at the moment.
    0x3C08800F,  # LUI   T0, 0x800F
    0x9508FBA0,  # LHU   T0, 0xFBA0 (T0)
    0x24093010,  # ADDIU T1, R0, 0x3010
    0x15090013,  # BNE   T0, T1, [forward 0x13]
    # Check our custom "can warp" byte for a non-zero value. If zero, don't warp.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA4B,  # LBU   T1, 0xAA4B (T0)
    0x15200010,  # BNEZ  T1,     [forward 0x10]
    # Check if a "Dracula 1 intro cutscene" flag is set. If it is, don't warp as we're likely in the escape sequence.
    0x9109AA8F,  # LBU   T1, 0xAA4B (T0)
    0x312A0018,  # ANDI  T2, T1, 0x0018
    0x1540000D,  # BNEZ  T2,     [forward 0x0D]
    0x00000000,  # NOP
    # Push T9 and A2 to the stack (since we'll be needing those once we return) and jump to the "Change Game State"
    # function with 2 as the A0 argument (the unused Game State 2 is where the warp menu will be handled).
    0x27BDFFF8,  # ADDIU SP, SP, -0x08
    0xAFB90000,  # SW    T9, 0x0000 (SP)
    0xAFA60004,  # SW    A2, 0x0004 (SP)
    # Kill the Gameplay Menu Manager pointer and set the delay timer to ensure the remote item giver hack doesn't try
    # reading garbage data from the aftermentioned pointer when coming out of the warp menu. Then change the game state.
    0xAD00AC0C,  # SW    R0, 0xAC0C (T0)
    0x3419003E,  # ORI   T9, R0, 0x003E
    0xA119278E,  # SB    T9, 0x278E (T0)
    0x0C00014F,  # JAL   0x8000053C
    0x24040002,  # ADDIU A0, R0, 0x0002
    # Pop T9 and A2's numbers back into their registers and return without storing the pause value.
    0x8FB90000,  # LW    T9, 0x0000 (SP)
    0x8FA60004,  # LW    A2, 0x0004 (SP)
    0x080218FB,  # J     0x800863EC
    0x27BD0008,  # ADDIU SP, SP, 0x08
    # Return storing the pause value as normal.
    0x080218FB,  # J     0x800863EC
    0xA4782B4E   # SH    T8, 0x2B4E (V1)
]

give_subweapon_stopper = [
    # Extension to "give subweapon" function to not change the player's weapon if the received item is a Stake or Rose.
    # Can also increment the Ice Trap counter if getting a Rose or jump to prev_subweapon_dropper if applicable.
    0x24090011,  # ADDIU T1, R0, 0x0011
    0x11240009,  # BEQ   T1, A0, [forward 0x09]
    0x24090012,  # ADDIU T1, R0, 0x0012
    0x11240003,  # BEQ   T1, A0, [forward 0x03]
    0x9465618A,  # LHU   A1, 0x618A (V1)
    0xA46D618A,  # SH    T5, 0x618A (V1)
    0x0804F0BF,  # J     0x8013C2FC
    0x3C098039,  # LUI   T1, 0x8039
    0x912A9BE2,  # LBU   T2, 0x9BE2 (T1)
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0xA12A9BE2,  # SB    T2, 0x9BE2 (T1)
    0x0804F0BF,  # J     0x8013C2FC
]

file_select_stage_position_setter = [
    # Sets a custom string on a File Select file for the stage number for that stage's actual randomizer position.
    # Rando stage positions can have more than just numbers, so setting the text using a text pool instead of a given
    # number is necessary.

    # Call the "get message from pool" function with A0 = the start of the pool at 0x0F003A80, and A1 = the stage number
    # minus 1.
    0x3C198008,  # LUI   T9, 0x8008
    0x37393FA0,  # ORI   T9, T9, 0x3FA0
    0x3C08801D,  # LUI   T0, 0x801D
    0x8D088D8C,  # LW    T0, 0x8D8C (T0)
    0x0320F809,  # JALR  RA, T9
    0x25043A80,  # ADDIU A0, T0, 0x3A80
    # Call the "set custom formatted text" function on the stage number textbox using the resulting pointer from the
    # above call, and then jump back.
    0x3C198008,  # LUI   T9, 0x8008
    0x37393864,  # ORI   T9, T9, 0x3864
    0x8E040014,  # LW    A0, 0x0014 (S0)
    0x0320F809,  # JALR  RA, T9
    0x00022825,  # OR    A1, R0, V0
    0x0BC00493,  # J     0x0F00124C
]

pause_menu_stage_position_setter = [
    # Sets a custom string on the Pause Menu for the stage number for that scene's stage's actual randomizer position.
    # Rando stage positions can have more than just numbers, so setting the text using a text pool instead of a given
    # number is necessary.

    # Call the "get message from pool" function with A0 = the start of the pool at 0x0F003A80, and A1 = the stage number
    # minus 1.
    0x3C0F0F00,  # LUI   T7, 0x0F00
    0x25EF4D28,  # ADDIU T7, T7, 0x4D28
    0x030F1821,  # ADDU  V1, T8, T7
    0x90650000,  # LBU   A1, 0x0000 (V1)
    0x3C198008,  # LUI   T9, 0x8008
    0x37393FA0,  # ORI   T9, T9, 0x3FA0
    0x27BDFFF8,  # ADDIU SP, SP, -0x08
    0xAFA80000,  # SW    T0, 0x0000 (SP)
    0x3C08801D,  # LUI   T0, 0x801D
    0x8D088D4C,  # LW    T0, 0x8D4C (T0)
    0x0320F809,  # JALR  RA, T9
    0x25044FB0,  # ADDIU A0, T0, 0x4FB0
    # Jump ahead to the "textboxObject_setParams_customFormattedString" block of Reinhardt/Carrie-specific code with
    # the resulting pointer from the above call in A1.
    0x8FA80000,  # LW    T0, 0x0000 (SP)
    0x27BD0008,  # ADDIU SP, SP, 0x08
    0x0BC00220,  # J     0x0F000880
    0x00022825,  # OR    A1, R0, V0
]

pause_menu_extra_scene_checks = [
    # Additional scene-specific checks for displaying the Pause Menu's stage number. Specifically, for the
    # Medusa/Algenie Arena and Fan Meeting Rooms to check which stage's setup it's using.
    0x3C02801D,  # LUI   V0, 0x801D
    0x9042AAB4,  # LBU   V0, 0xAAB4 (V0)
    # If we're in the Algenie/Medusa Arena scene, check which alt setup flag is set and consider ourselves actually in
    # either Tunnel or Waterway.
    0x34010013,  # ORI   AT, R0, 0x0013
    0x14610007,  # BNE   V1, AT, [forward 0x07]
    0x304F0040,  # ANDI  T7, V0, 0x0040
    0x55E00004,  # BNEZL T7,     [forward 0x04]
    0x34080007,  # ORI   T0, R0, 0x0007  <- Tunnel scene ID
    0x304F0020,  # ANDI  T7, V0, 0x0020
    0x55E00001,  # BNEZL T7,     [forward 0x01]
    0x34080008,  # ORI   T0, R0, 0x0008  <- Waterway scene ID
    0x0BC001FA,  # J     0x0F0007E8
    # If we're in the Fan Meeting Room scene, check which alt setup flag is set and consider ourselves actually in
    # either Castle Center Basement or The Outer Wall.
    0x34010019,  # ORI   AT, R0, 0x0019
    0x14610006,  # BNE   V1, AT, [forward 0x06]
    0x304F0040,  # ANDI  T7, V0, 0x0040
    0x55E00004,  # BNEZL T7,     [forward 0x04]
    0x34080009,  # ORI   T0, R0, 0x0009  <- CC Basement scene ID
    0x304F0010,  # ANDI  T7, V0, 0x0010
    0x55E00001,  # BNEZL T7,     [forward 0x01]
    0x3408002A,  # ORI   T0, R0, 0x002A  <- Outer Wall scene ID
    0x0BC001FA,  # J     0x0F0007E8
    0x00000000,  # NOP
]

npc_item_rework = [
    # Hack to make NPC items show item textboxes when received.
    0x00180000,
    0x00240000,  # Item values
    0x001B0000,
    0x001F0000,
    0x00200000,
    0x00000000,
    0x3C088040,  # LUI   T0, 0x8040
    0x00044880,  # SLL   T1, A0, 2
    0x01094021,  # ADDIU T0, T0, T1
    0x950AC6E8,  # LHU   T2, 0xC6E8 (T0)
    0x9519C6EA,  # LHU   T9, 0xC6EA (T0)
    0x314B00FF,  # ANDI  T3, T2, 0x00FF
    0x3C0C801D,  # LUI   T4, 0x801D
    0xA18BAA4C,  # SB    T3, 0xAA4C (T4)
    # Decrement the Countdown if applicable.
    0x314D8000,  # ANDI  T5, T2, 0x8000
    0x11A00008,  # BEQZ  T5,     [forward 0x08]
    0x918AAE79,  # LBU   T2, 0xAE79 (T4)
    0x3C088040,  # LUI   T0, 0x8040
    0x010A5821,  # ADDU  T3, T0, T2
    0x916EC4D0,  # LBU   T6, 0xC4D0 (T3)
    0x018E7821,  # ADDU  T7, T4, T6
    0x91F8ABA0,  # LBU   T8, 0xABA0 (T7)
    0x2718FFFF,  # ADDIU T8, T8, 0xFFFF
    0xA1F8ABA0,  # SB    T8, 0xABA0 (T7)
    # Copy from the ROM the off-world Item string corresponding to that NPC Item.
    0x3C0B00FA,  # LUI   T3, 0x00FA
    # Shift the flag ID up by 8 and add it to 0xFA0000 to get the start address for this NPC Item's string.
    0x00194A00,  # SLL   T1, T9, 8
    0x01692021,  # ADDU  A0, T3, T1
    0x3C058001,  # LUI   A1, 0x8001
    0x34A5E5CC,  # ORI   A1, A1, 0xE5CC
    # Run the "rom copy" function with all necessary arguments. We should return to the NPC code right after that.
    0x0800690B,  # J     0x8001A42C
    0x34060100,  # ORI   A2, R0, 0x0100
]

double_component_checker = [
    # When checking to see if a bomb component can be placed at a cracked wall, this will run if the code lands at the
    # "no need to set 2" outcome to see if the other can be set.

    # Mandragora checker
    # Check the "set Mandragora" flag for the wall we are currently looking at.
    0x8E080054,  # LW    T0, 0x0054 (S0)
    0x15000004,  # BNEZ  T0,     [forward 0x04]
    0x3C09801D,  # LUI   T1, 0x801D
    0x912AAA7E,  # LBU   T2, 0xAA7E (T1)
    0x10000003,  # B             [forward 0x03]
    0x314A0040,  # ANDI  T2, T2, 0x0040
    0x912AAA84,  # LBU   T2, 0xAA84 (T1)
    0x314A0080,  # ANDI  T2, T2, 0x0080
    0x15400005,  # BNEZ  T2,     [forward 0x05]
    # If the flag is not set, check to see if we have Mandragora in the inventory.
    0x912BAB56,  # LBU   T3, 0xAB56 (T1)
    0x11600003,  # BEQZ  T3,     [forward 0x03]
    0x240C0001,  # ADDIU T4, R0, 0x0001
    0x03E00008,  # JR    RA
    0xA60C004C,  # SH    T4, 0x004C (S0)
    0x3C0A8000,  # LUI   T2, 0x8000
    0x354A1E30,  # ORI   T2, T2, 0x1E30
    0x01400008,  # JR    T2
    0x00000000,  # NOP
    # Nitro checker
    # Check the "set Magical Nitro" flag for the wall we are currently looking at.
    0x8E080054,  # LW    T0, 0x0054 (S0)
    0x15000004,  # BNEZ  T0,     [forward 0x04]
    0x3C09801D,  # LUI   T1, 0x801D
    0x912AAA7E,  # LBU   T2, 0xAA7E (T1)
    0x10000003,  # B             [forward 0x03]
    0x314A0080,  # ANDI  T2, T2, 0x0080
    0x912AAA83,  # LBU   T2, 0xAA83 (T1)
    0x314A0001,  # ANDI  T2, T2, 0x0001
    0x15400005,  # BNEZ  T2,     [forward 0x05]
    # If the flag is not set, check to see if we have Magical Nitro in the inventory.
    0x912BAB55,  # LBU   T3, 0xAB55 (T1)
    0x11600003,  # BEQZ  T3,     [forward 0x03]
    0x240C0001,  # ADDIU T4, R0, 0x0001
    0x03E00008,  # JR    RA
    0xA60C004E,  # SH    T4, 0x004E (S0)
    0x3C0A8000,  # LUI   T2, 0x8000
    0x354A1E30,  # ORI   T2, T2, 0x1E30
    0x01400008,  # JR    T2
    0x00000000,  # NOP
]

basement_seal_checker = [
    # This will run specifically for the downstairs crack to see if the seal has been removed before then deciding to
    # let the player set the bomb components or not, giving them the "Furious Nerd Curse" message if not. Unlike in the
    # vanilla game, Magical Nitro and Mandragora is not replenish-able, so an anti-softlock measure is necessary to
    # ensure they aren't wasted trying to blow up a currently-impervious wall.
    0x8E080054,  # LW    T0, 0x0054 (S0)
    0x1500000B,  # BNEZ  T0,     [forward 0x0B]
    0x3C09801D,  # LUI   T1, 0x801D
    0x9129AA7D,  # LBU   T1, 0xAA7D (T1)
    0x31290001,  # ANDI  T1, T1, 0x0001
    0x15200007,  # BNEZ  T1,     [forward 0x07]
    0x00000000,  # NOP
    0x26040008,  # ADDIU A0, S0, 0x0008
    0x2605000E,  # ADDIU A1, S0, 0x000E
    0x3C0A8000,  # LUI   T2, 0x8000
    0x354A1E30,  # ORI   T2, T2, 0x1E30
    0x01400008,  # JR    T2
    0x24060008,  # ADDIU A2, R0, 0x0008
    0x0B8000B0,  # J     0x0E0002C0
    0x00000000,  # NOP
]

mandragora_with_nitro_setter = [
    # When setting a Nitro, if Mandragora is in the inventory too and the wall's "Mandragora set" flag is not set, this
    # will automatically subtract a Mandragora from the inventory and set its flag so the wall can be blown up in just
    # one interaction instead of two.
    0x8E080054,  # LW    T0, 0x0054 (S0)
    0x15000004,  # BNEZ  T0,     [forward 0x04]
    0x3C09801C,  # LUI   T1, 0x801C
    0x340AAA7E,  # ORI   T2, R0, 0xAA7E
    0x10000003,  # B             [forward 0x03]
    0x240B0040,  # ADDIU T3, R0, 0x0040
    0x340AAA84,  # ORI   T2, R0, 0xAA84
    0x240B0080,  # ADDIU T3, R0, 0x0080
    0x012A6025,  # OR    T4, T1, T2
    0x918D0000,  # LBU   T5, 0x0000 (T4)
    0x01AB7024,  # AND   T6, T5, T3
    0x15C00007,  # BNEZ  T6,     [forward 0x07]
    0x3C09801D,  # LUI   T1, 0x801D
    0x912FAB56,  # LBU   T7, 0xAB56 (T1)
    0x11E00004,  # BEQZ  T7,     [forward 0x04]
    0x25EFFFFF,  # ADDIU T7, T7, 0xFFFF
    0xA12FAB56,  # SB    T7, 0xAB56 (T1)
    0x016DC025,  # OR    T8, T3, T5
    0xA1980000,  # SB    T8, 0x0000 (T4)
    0x3C0A8000,  # LUI   T2, 0x8000
    0x354A48C4,  # ORI   T2, T2, 0x48C4
    0x01400008,  # JR    T2
    0x00000000,  # NOP
]

cutscene_active_checkers = [
    # Returns True (1) if we are NOT currently in a cutscene or False (0) if we are in V0. Custom actor spawn condition
    # for things like the Cornell intro actors in Castle Center.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AE8B,  # LBU   T1, 0xAE8B (T0)
    0x11200002,  # BEQZ  T1,     [forward 0x02]
    0x24020000,  # ADDIU V0, R0, 0x0000
    0x24020001,  # ADDIU V0, R0, 0x0001
    0x03E00008,  # JR    RA
    0x00000000,
    # Returns True (1) if we are currently in a cutscene or False (0) if we are NOT in V0. Custom actor spawn condition
    # for things like the Cornell intro actors in Castle Center.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AE8B,  # LBU   T1, 0xAE8B (T0)
    0x11200002,  # BEQZ  T1,     [forward 0x02]
    0x24020001,  # ADDIU V0, R0, 0x0001
    0x24020000,  # ADDIU V0, R0, 0x0000
    0x03E00008,  # JR    RA
    0x00000000,
]

stone_dog_cutscene_checker = [
    # Extension to the custom spawn condition on the Stone Dog actors that checks to see if we are in the
    # "meeting Malus" cutscene and, if we are, allows the Stone Dogs to spawn. Otherwise, the Stone Dogs' other spawn
    # checks will proceed as normal. This fixes an edge case wherein they don't spawn if we entered the scene through
    # the servant entrance door, enabling the Malus chase to be done without the dogs involved.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AE8B,  # LBU   T1, 0xAE8B (T0)
    0x340A000E,  # ORI   T2, R0, 0x000E  <- Meeting Malus cutscene ID
    # Jump to the flag check function if we are not in the cutscene. Return now with 1 in V0 if we are.
    0x112A0003,  # BEQ   T1, T2, [forward 0x03]
    0x00000000,  # NOP
    0x03200008,  # JR    T9
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x24020001,  # ADDIU V0, R0, 0x0001
]

renon_cutscene_checker = [
    # Custom spawn condition that blocks the Renon's departure/pre-fight cutscene trigger from spawning if the player
    # did not spend the required 30K to fight him.
    0x3C08801D,  # LUI   T0, 0x801D
    0x8D08ABC0,  # LW    T0, 0xABC0 (T0)
    0x29097531,  # SLTI  T1, T0, 0x7531
    0x15200002,  # BNEZ  T1,     [forward 0x02]
    0x24020000,  # ADDIU V0, R0, 0x0000
    0x24020001,  # ADDIU V0, R0, 0x0001
    0x03E00008,  # JR   RA
    0x00000000,
]

ck_door_music_player = [
    # Plays Castle Keep's song if you spawn in front of the main Castle Keep entrance or Dracula's door (teleporting via
    # the warp menu), haven't started the escape sequence yet (the way this is hooked means checking for the latter
    # shouldn't be necessary), and if we're not in a cutscene (fun fact: this entrance is used in Cornell's intro when
    # Gilles De Rais is climbing the stairs).

    # Check for spawn entrance 0 or 1. If neither, put us on the routine that doesn't play the song.
    0x10400005,  # BEQZ  V0,     [forward 0x05]
    0x34080001,  # ORI   T0, R0, 0x0001
    0x10480003,  # BEQ   V0, T0, [forward 0x03]
    0x00000000,  # NOP
    0x080B931D,  # J     0x802E4C74
    0x00000000,  # NOP
    # Check if there's a cutscene playing. If there isn't, allow Castle Keep's song to play.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AE8B,  # LBU   T1, 0xAE8B (T0)
    0x11200003,  # BEQZ  T1,     [forward 0x03]
    0x00000000,  # NOP
    0x080B931D,  # J     0x802E4C74
    0x00000000,  # NOP
    0x080B931A,  # J     0x802E4C68
    0x00000000,  # NOP
]

drac_condition_checker = [
    # Checks the Special2 counter to see if the required amount of the goal item has been reached and disallows opening
    # Dracula's doors if not.
    0x24020000,  # ADDIU V0, R0, 0x0000
    0x3C0A801D,  # LUI   T2, 0x801D
    0x914BAB48,  # LBU   T3, 0xAB48 (T2)
    0x296A0000,  # SLTI  T2, T3, 0x0000
    0x55400001,  # BNEZL T2,     [forward 0x01]
    0x24020001,  # ADDIU V0, R0, 0x0001
    0x03E00008,  # JR    RA
    0x00000000   # NOP
]

bad_ending_time_checker = [
    # Extra spawn condition for the White Jewel in Dracula's chamber that checks to see if too many days have passed
    # to receive the Good Ending. If so, the Bad Ending flag will be set. The jewel will be allowed to spawn regardless.
    # This should account for being able to completely avoid vampire Vincent's trigger if you get the Castle Keep warp.

    # Multiply the weeks counter by 7 and add that to the "current day of the week" counter to get the total days
    # passed. If less than 16, don't set the Bad Ending flag.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9509AB1C,  # LHU   T1, 0xAB1C (T0)
    0x950AAB1E,  # LHU   T2, 0xAB1E (T0)
    0x340B0007,  # ORI   T3, R0, 0x0007
    0x012B0019,  # MULTU T1, T3
    0x00004812,  # MFLO  T1
    0x012A4821,  # ADDU  T1, T1, T2
    0x292C0010,  # SLTI  T4, T1, 0x0010
    0x15800003,  # BNEZ  T4,     [forward 0x03]
    0x9109AA95,  # LBU   T1, 0xAA95 (T0)
    0x35290080,  # ORI   T1, T1, 0x0080
    0xA109AA95,  # SB    T1, 0xAA95 (T0)
    0x03E00008,  # JR    RA
    0x34020001,  # ORI   V0, R0, 0x0001
]

continue_cursor_start_checker = [
    # This is used to improve the Game Over screen's "Continue" menu by starting the cursor on whichever checkpoint
    # is most recent instead of always on "Previously saved". If a menu has a cursor start value of 0xFF in its text
    # data, this will read the byte at 0x801CAA31 to determine which option to start the cursor on.
    0x240A00FF,  # ADDIU T2, R0, 0x00FF
    0x15480008,  # BNE   T2, T0, [forward 0x08]
    0x286B0002,  # SLTI  T3, V1, 0x0002
    0x15600006,  # BNEZ  T3,     [forward 0x05]
    0x8CAA0014,  # LW    T2, 0x0014 (A1)
    0x8D4B0014,  # LW    T3, 0x0014 (T2)
    0x3C0A801D,  # LUI   T2, 0x801D
    0x9148AA31,  # LBU   T0, 0xAA31 (T2)
    0x01003021,  # ADDU  A2, T0, R0
    0xA1680073,  # SB    T0, 0x0073 (T3)
    0x03E00008,  # JR    RA
    0x30CF00FF   # ANDI  T7, A2, 0x00FF
]

savepoint_cursor_updater = [
    # Sets the value at 0x801CAA31 to 0x00 after saving to let the Game Over screen's "Continue" menu know to start the
    # cursor on "Previously saved" as well as updates the entrance variable for B warping.
    0x3C08801D,  # LUI    T0, 0x801D
    0x9109AB95,  # LBU    T1, 0xAB95 (T0)
    0x000948C0,  # SLL    T1, T1, 3
    0x3C0A800C,  # LUI    T2, 0x800C
    0x01495021,  # ADDU   T2, T2, T1
    0x914B82EF,  # LBU    T3, 0x82EF (T2)
    0xA10BAB93,  # SB     T3, 0xAB93 (T0)
    0xA10BAE7B,  # SB     T3, 0xAE7B (T0)
    0xA100AA31,  # SB     R0, 0xAA31 (T0)
    0x03E00008,  # JR    RA
]

stage_start_cursor_updater = [
    # Sets the value at 0x801CAA31 to 0x01 after entering a stage to let the Game Over screen's "Continue" menu know to
    # start the cursor on "Restart this stage".
    0x3C08801D,  # LUI    T0, 0x801D
    0x24090001,  # ADDIU  T1, R0, 0x0001
    0xA109AA31,  # SB     T1, 0xAA31 (T0)
    0x03E00008   # JR     RA
]

load_clearer = [
    # Un-sets the Death status bitflag when loading either a save or stage beginning state and sets health to full if
    # it's empty, as well as clearing the multiworld buffers so things don't get mucked up on that front. Also updates
    # the "Continue" menu cursor depending on which state was loaded.
    0x3C08801D,  # LUI   T0, 0x801D
    0xFD00AA48,  # SD    R0, 0xAA48 (T0)
    0xA104AA31,  # SB    A0, 0xAA31 (T0)
    0x9109AB84,  # LBU   T1, 0xAB84 (T0)
    0x3129007F,  # ANDI  T1, T1, 0x007F
    0xA109AB84,  # SB    T1, 0xAB84 (T0)
    0x950AAB3A,  # LHU   T2, 0xAB3A (T0)
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x240A2710,  # ADDIU T2, R0, 0x2710
    0x03E00008,  # JR    RA
    0xA50AAB3A   # SH    T2, 0xAB3A (T0)
]

elevator_flag_checker = [
    # Extension to the map-specific elevator checks code that prevents the top elevator in Castle Center from
    # activating if the bottom elevator switch is not turned on.

    # Check if we are in Scene 0x0F (Castle Center Top Elevator Room). If we aren't, skip to the jump back.
    0x2408000F,  # ADDIU T1, R0, 0x000F
    0x15030005,  # BNE   T0, V1, [forward 0x05]
    # Check if Flag 0x105 is set (Castle Center elevator activated). If it isn't, replace the return value 0
    # (elevator awaiting player) with 2 (elevator will not work at all).
    0x3C09801D,  # LUI   T1, 0x801D
    0x9129AA80,  # LBU   T1, 0xAA80 (T1)
    0x312A0004,  # ANDI  T2, T1, 0x0004
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x24020002,  # ADDIU V0, R0, 0x0002
    0x08055CFC   # J     0x801573F0
]

special2_giver = [
    # Gives a Special2/Crystal/Trophy through the multiworld system, and clears the byte preventing warping.
    # Can be hooked into anything; just make sure the JR T9 is replaced with a jump back to where it should be.
    # It may be further modified to remove the Special2 giving part depending on what Dracula's Condition is.
    0x3C09801D,  # LUI   T1, 0x801D
    0x24080005,  # ADDIU T0, R0, 0x0005
    0xA128AA4C,  # SB    T0, 0xAA4C (T1)
    0x03200008,  # JR    T9
    0xA120AA4B,  # SB    R0, 0xAA4B (T1)
]

special2_giver_lizard_edition = [
    # Special version of the above hack specifically for the Waterway Lizard-man Trio. It turns out the code that
    # resumes the waterway music after they are dead is very spaghetti, so we are instead opting to hook into the code
    # that depletes their combined health bar whenever they get hit.

    # If the value being stored for the bar's new length value is 0, give their Trophy. Otherwise, return like normal.
    0x15400008,  # BNEZ  T2,     [forward 0x08]
    0xA46A0000,  # SH    T2, 0x0000 (V1)
    0x3C09801D,  # LUI   T1, 0x801D
    # Set flag 0x2F7 (normally unused) so we know the lizards were properly exterminated.
    0x9128AABE,  # LBU   T0, 0xAABE (T1)
    0x34080001,  # ORI   T0, R0, 0x0001
    0xA128AABE,  # SB    T0, 0xAABE (T1)
    # Give a Special2 and un-set the "can't warp" byte.
    0x24080005,  # ADDIU T0, R0, 0x0005
    0xA120AA4B,  # SB    R0, 0xAA4B (T1)
    0xA128AA4C,  # SB    T0, 0xAA4C (T1)
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
]

boss_save_stopper = [
    # Prevents usage of a White Jewel if in a boss fight. Important for the lizard-man trio in Waterway as escaping
    # their fight by saving/reloading can render a Special2 permanently missable.
    0x24080001,  # ADDIU T0, R0, 0x0001
    0x15030005,  # BNE   T0, V1, [forward 0x05]
    0x3C088035,  # LUI   T0, 0x8035
    0x9108F7D8,  # LBU   T0, 0xF7D8 (T0)
    0x24090020,  # ADDIU T1, R0, 0x0020
    0x51090001,  # BEQL  T0, T1, [forward 0x01]
    0x24020000,  # ADDIU V0, R0, 0x0000
    0x03E00008   # JR    RA
]

music_modifier = [
    # Uses the ID of a song about to be played to pull a switcheroo by grabbing a new ID from a custom table to play
    # instead. A hacky way to circumvent song IDs in the compressed overlays' "play song" function calls, but it works!
    0xAFBF001C,  # SW    RA, 0x001C (SP)
    0x0C004A6B,  # JAL   0x800129AC
    0x44800000,  # MTC1  R0, F0
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x3C088040,  # LUI   T0, 0x8040
    0x01044821,  # ADDU  T1, T0, A0
    0x9124CD20,  # LBU   A0, 0xCD20 (T1)
    0x08004E64   # J     0x80013990
]

music_comparer_modifier = [
    # The same as music_modifier, but for the function that compares the "song to play" ID with the one that's currently
    # playing. This will ensure the randomized music doesn't reset when going through a loading zone in Villa or CC.
    0x3C088040,  # LUI   T0, 0x8040
    0x01044821,  # ADDU  T1, T0, A0
    0x9124CD20,  # LBU   A0, 0xCD20 (T1)
    0x08004A60,  # J     0x80012980
]

item_customizer = [
    # Allows changing an item's appearance settings independent of what it actually is by changing things in the item
    # actor's data as it's being created for some other custom functions to then utilize.
    0x000F4202,  # SRL   T0, T7, 8
    0x31090080,  # ANDI  T1, T0, 0x0080
    0x01094023,  # SUBU  T0, T0, T1
    0xA0C80044,  # SB    T0, 0x0044 (A2)
    0xA0C90045,  # SB    T1, 0x0045 (A2)
    0x31EF00FF,  # ANDI  T7, T7, 0x00FF
    0x03E00008,  # JR    RA
    0xA4CF0038   # SH    T7, 0x0038 (A2)
]

pickup_model_switcher = [
    # Determines a pickup's model appearance by checking to see if a different "appearance pickup" ID was written in a
    # specific spot in the actor's data; if one wasn't, then the appearance value will be grabbed from the pickup's
    # entry in the pickup property table like normal instead.
    0x92080044,  # LBU   T0, 0x0044 (S0)
    0x55000001,  # BNEZL T0,     [forward 0x01]
    0x01004825,  # OR    T1, T0, R0
    0x03E00008,  # JR    RA
    0xAFA7002C,  # SW    A3, 0x002C (SP)
]

pickup_spawn_height_switcher = [
    # Same as the above, but for the pickup spawn height if it's taking the appearance of a higher-spawning Item instead
    # of the model.
    0x92180044,  # LBU   T8, 0x0044 (S0)
    0x57000001,  # BNEZL T8,     [forward 0x01]
    0x03007825,  # OR    T7, T8, R0
    0x03E00008,  # JR    RA
    0x01E40019,  # MULTU T7, A0
]

pickup_spin_speed_switcher = [
    # Same as the above, but for the pickup spin speed.
    0x92080044,  # LBU   T0, 0x0044 (S0)
    0x55000001,  # BNEZL T0,     [forward 0x01]
    0x01004825,  # OR    T1, T0, R0
    0x03E00008,  # JR    RA
    0x3C028019,  # LUI   V0, 0x8019
]

pickup_shine_size_switcher = [
    # Same as the above, but for the size of the shine on the pickup.
    0x92080044,  # LBU   T0, 0x0044 (S0)
    0x55000001,  # BNEZL T0,     [forward 0x01]
    0x01007825,  # OR    T7, T0, R0
    0x03E00008,  # JR    RA
    0x3C048019,  # LUI   A0, 0x8019
]

pickup_shine_height_switcher = [
    # Same as the above, but for the height of the shine on the pickup.
    0x92080044,  # LBU   T0, 0x0044 (S0)
    0x55000001,  # BNEZL T0,     [forward 0x01]
    0x0100C825,  # OR    T9, T0, R0
    0x03E00008,  # JR    RA
    0x24050015,  # ADDIU A1, R0, 0x0015
]

three_hit_item_flags_setter = [
    # As the function to create items from the 3HB item lists iterates through said item lists, this will pass unique
    # flag values to each item when calling the "create item instance" function by adding to the flag value the number
    # of passed iterations so far.
    0x96E8000A,  # LHU   T0, 0x000A (S7)
    0x01124021,  # ADDU  T0, T0, S2
    0xAFA80010,  # SW    T0, 0x0010
    0x96E90008,  # LHU   T1, 0x0008 (S7)
    0x02495006,  # SRLV  T2, T1, S2
    0x314B0001,  # ANDI  T3, T2, 0x0001
    0x55600001,  # BNEZL T3,     [forward 0x01]
    0x34E70800,  # ORI   A3, A3, 0x0800
    0x08058E56,  # J     0x80163958
]

chandelier_item_flags_setter = [
    # Same as the above, but for the unique function made specifically and ONLY for the Villa foyer chandelier's item
    # list. KCEK, why the heck did you have to do this to me!?
    0x96C8000A,  # LHU   T0, 0x000A (S6)
    0x01144021,  # ADDU  T0, T0, S4
    0xAFA80010,  # SW    T0, 0x0010
    0x96C90008,  # LHU   T1, 0x0008 (S6)
    0x02895006,  # SRLV  T2, T1, S4
    0x314B0001,  # ANDI  T3, T2, 0x0001
    0x55600001,  # BNEZL T3,     [forward 0x01]
    0x34E70800,  # ORI   A3, A3, 0x0800
    0x08058E56,  # J     0x80163958
]

prev_subweapon_spawn_checker = [
    # When picking up a subweapon, this will check to see if it's different from the one the player already had (if
    # they did have one) and jump to the prev_subweapon_dropper hack, which will spawn a subweapon actor of what they
    # had before directly behind them as well as save the player's old subweapon level to it. Also increases the
    # weapon level by multiples if picking up a subweapon with a level higher than 0 saved to it.

    0x100D0E0F,  # Previous sub-weapon pickup IDs.
    # Check if the player's old subweapon ID is 0 or the same as the new one. If the former is true, skip the weapon
    # drop routine entirely. If the latter is true, branch to where we will increment the weapon level.
    0x1180000E,  # BEQZ  T4,     [forward 0x0E]
    0x00000000,  # NOP
    0x11850008,  # BEQ   T4, A1, [forward 0x08]
    # Set the subweapon level to 0 and drop the old subweapon with said old level saved to it.
    0x3C0A8040,  # LUI   T2, 0x8040
    0x014C5021,  # ADDU  T2, T2, T4
    0x9144D23F,  # LBU   A0, 0xD23F (T2)
    0x3C08801D,  # LUI   T0, 0x801D
    0x9505AE26,  # LHU   A1, 0xAE26 (T0)
    0x0C0FF4C0,  # JAL   0x803FD300
    0xA500AE26,  # SH    R0, 0xAE26 (T0)
    0x10000005,  # B             [forward 0x05]
    # If picking up an instance of the same weapon, increase the weapon level by 1.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9509AE26,  # LHU   T1, 0xAE26 (T0)
    0x25290001,  # ADDIU T1, T1, 0x0001
    0xA509AE26,  # SH    T1, 0xAE26 (T0)
    # Increase the player's subweapon level by the amount we grabbed from the new subweapon pickup and then clear that
    # value for the next Item we receive. This will happen regardless of whether we dropped a subweapon or not.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9509AE26,  # LHU   T1, 0xAE26 (T0)
    0x910AAA20,  # LBU   T2, 0xAA20 (T0)
    0x012A4821,  # ADDU  T1, T1, T2
    # Cap the weapon level at 02.
    0x292B0003,  # SLTI  T3, T1, 0x0003
    0x51600001,  # BEQZL T3,     [forward 0x01]
    0x34090002,  # ORI   T1, R0, 0x0002
    0xA509AE26,  # SH    T1, 0xAE26 (T0)
    0xA500AA20,  # SH    R0, 0xAA20 (T0)
    # Play the subweapon pickup sound since we hooked into that function call.
    0x0C0059BE,  # JAL   0x800166F8
    0x240401F5,  # ADDIU A0, R0, 0x01F5
    # Return to the "give subweapon" routine.
    0x08023E9E,  # J     0x8008FA78
]

subweapon_surface_checker = [
    # During the process of remotely giving an item received via multiworld, this will check to see if the item being
    # received is a subweapon and, if it is, wait until the player is not above an abyss or instant kill surface before
    # giving it. This is to ensure dropped previous subweapons won't land somewhere inaccessible.
    0x2408000D,  # ADDIU T0, R0, 0x000D
    0x11040006,  # BEQ   T0, A0, [forward 0x06]
    0x2409000E,  # ADDIU T1, R0, 0x000E
    0x11240004,  # BEQ   T1, A0, [forward 0x04]
    0x2408000F,  # ADDIU T0, R0, 0x000F
    0x11040002,  # BEQ   T0, A0, [forward 0x02]
    0x24090010,  # ADDIU T1, R0, 0x0010
    0x1524000B,  # BNE   T1, A0, [forward 0x0B]
    0x3C0A800D,  # LUI   T2, 0x800D
    0x8D4A7B5C,  # LW    T2, 0x7B5C (T2)
    0x1140000E,  # BEQZ  T2,     [forward 0x0E]
    0x00000000,  # NOP
    0x914A0001,  # LBU   T2, 0x0001 (T2)
    0x240800A2,  # ADDIU T0, R0, 0x00A2
    0x110A000A,  # BEQ   T0, T2, [forward 0x0A]
    0x24090092,  # ADDIU T1, R0, 0x0092
    0x112A0008,  # BEQ   T1, T2, [forward 0x08]
    0x24080080,  # ADDIU T0, R0, 0x0080
    0x110A0006,  # BEQ   T0, T2, [forward 0x06]
    0x956C00DD,  # LHU   T4, 0x00DD (T3)
    0xA1600000,  # SB    R0, 0x0000 (T3)
    0x258C0001,  # ADDIU T4, T4, 0x0001
    0x080FF8D0,  # J     0x803FE340
    0xA56C00DD,  # SH    T4, 0x00DD (T3)
    0x00000000,  # NOP
    0x03E00008   # JR    RA
]

countdown_number_displayer = [
    # Displays a number below the HUD health of however many items are left to find in whichever stage the player is in.
    # Which number in the save file to display depends on which stage map the player is currently on. It can track
    # either items marked progression only or all locations in the stage.
    # Courtesy of Moisés; see print_text_ovl.c in the src folder for the C source code.
    0x27BDFFE8,
    0xAFBF0014,
    0x0C000958,
    0x24040007,
    0x0C020BF8,
    0x00402025,
    0x8FBF0014,
    0x27BD0018,
    0x03E00008,
    0x00000000,
    0x8C820038,
    0x03E00008,
    0x0002102B,
    0x27BDFFD8,
    0xAFA5002C,
    0x00A07025,
    0x3C018040,
    0xC424C4C4,
    0x3C05801D,
    0xAFBF0024,
    0x00AE2821,
    0x3C078040,
    0x240F0002,
    0xAFAF0014,
    0x8CE7C4C0,
    0x90A5ABA0,
    0xAFA00018,
    0x00003025,
    0x0C020D74,
    0xE7A40010,
    0x8FBF0024,
    0x27BD0028,
    0x03E00008,
    0x00000000,
    0x00A03025,
    0x27BDFFE8,
    0x3C05801D,
    0xAFBF0014,
    0x00A62821,
    0x0C020E69,
    0x90A5ABA0,
    0x8FBF0014,
    0x27BD0018,
    0x03E00008,
    0x00000000,
    0x27BDFFE8,
    0xAFBF0014,
    0x3C058040,
    0x3C068040,
    0x8CC6C4C4,
    0x0C020ECF,
    0x8CA5C4C0,
    0x8FBF0014,
    0x27BD0018,
    0x03E00008,
    0x00000000,
    0x27BDFFE8,
    0xAFBF0014,
    0x0C020FC8,
    0x00000000,
    0x8FBF0014,
    0x27BD0018,
    0x03E00008,
    0x00000000,
    0xC2D90000,
    0x42B10000,
    0x00000000,
    0x00000000]

countdown_number_manager = [
    # Updates the Countdown number every frame. Which number in the save file it refers to depends on the map ID.
    0x01020203,  # Map ID offset table start
    0x03031104,
    0x05090909,
    0x12121209,
    0x00000013,
    0x1010130F,
    0x1009110E,
    0x130D0B0B,
    0x0B0C0C08,
    0x0807070A,
    0x0F0F0613,
    0x13131013,
    0x13130000,  # Table end
    # Creates the textbox object and saves the pointer to it.
    0x0C0FF0F0,  # JAL   0x803FC3C0
    0x00000000,  # NOP
    0x3C08801D,  # LUI   T0, 0x801D
    0xA100AA44,  # SB    R0, 0xAA44 (T0)
    0x08006DDA,  # J     0x8001B768
    0xAD02AA40,  # SW    V0, 0xAA40 (T0)
    # Initializes the countdown number after checking if the textbox data is created.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA44,  # LBU   T1, 0xAA44 (T0)
    0x15200010,  # BNEZ  T1,     [forward 0x10]
    0x8D04AA40,  # LW    A0, 0xAA40 (T0)
    0x1080000C,  # BEQZ  A0,     [forward 0x0C]
    0x00000000,  # NOP
    0x0C0FF0F9,  # JAL   0x803FC3E4
    0x00000000,  # NOP
    0x10400008,  # BEQZ  V0,     [forward 0x08]
    0x00000000,  # NOP
    0x3C08801D,  # LUI   T0, 0x801D
    0xA102AA44,  # SB    V0, 0xAA44 (T0)
    0x9109AE79,  # LBU   T1, 0xAE79 (T0)
    0x3C0A8040,  # LUI   T2, 0x8040
    0x01495021,  # ADDU  T2, T2, T1
    0x0C0FF0FD,  # JAL   0x803FC3F4
    0x9145C4D0,  # LBU   A1, 0xC4D0 (T2)
    0x08005F33,  # J     0x80017CCC
    0x00000000,  # NOP
    # Updates the color of the number depending on what it currently is.
    # 0 = Dark brown    Same as the initial count = Green     Otherwise = Light brown
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AB91,  # LBU   T1, 0xAB91 (T0)
    0x3C0A8040,  # LUI   T2, 0x8040
    0x01495021,  # ADDU  T2, T2, T1
    0x914BC4D0,  # LBU   T3, 0xC4D0 (T2)
    0x010B6821,  # ADDU  T5, T0, T3
    0x91ACABA0,  # LBU   T4, 0xABA0 (T5)
    0x3C0A8040,  # LUI   T2, 0x8040
    0x016A5021,  # ADDU  T2, T3, T2
    0x914EC7D0,  # LBU   T6, 0xC7D0 (T2)
    0x11800009,  # BEQZ  T4,     [forward 0x09]
    0x24050007,  # ADDIU A1, R0, 0x0007
    0x118E0007,  # BEQ   T4, T6, [forward 0x07]
    0x24050002,  # ADDIU A1, R0, 0x0002
    0x24050006,  # ADDIU A1, R0, 0x0006
    0x00000000,  # NOP
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x0C0FF128,  # JAL   0x803FC4A0
    0x8D04AA40,  # LW    A0, 0xAA40 (T0)
    # Updates the number being displayed.
    0x3C04801D,  # LUI   A0, 0x801D
    0x8C84AA40,  # LW    A0, 0xAA40 (A0)
    0x0C0FF112,  # JAL   0x803FC448
    0x000B2821,  # ADDU  A1, R0, T3
    # Updates the position of the number depending on what our "demo number" currently is.
    0x3C08801D,  # LUI   T0, 0x801D
    0x8D04AA40,  # LW    A0, 0xAA40 (T0)
    0x9109AA4A,  # LBU   T1, 0xAA4A (T0)
    0x340AC2D9,  # ORI   T2, R0, 0xC2D9
    0x11200009,  # BEQZ  T1,     [forward 0x09]
    0x340B42B1,  # ORI   T3, R0, 0x42B1
    0x312C0001,  # ANDI  T4, T1, 0x0001
    0x55800006,  # BNEZL T4,     [forward 0x06]
    0x340B43B1,  # ORI   T3, R0, 0x43B1
    0x312C0002,  # ANDI  T4, T1, 0x0002
    0x11800003,  # BEQZ  T4,     [forward 0x02]
    0x00000000,  # NOP
    0x340A42E1,  # ORI   T2, R0, 0x42E1
    0x340B42CC,  # ORI   T3, R0, 0x42CC
    0x3C0D8040,  # LUI   T5, 0x8040
    0xA5AAC4C0,  # SH    T2, 0xC4C0 (T5)
    0x0C0FF11D,  # JAL   0x803FC474
    0xA5ABC4C4,  # SH    T3, 0xC4C4 (T5)
    0x08005F33,  # J     0x80017CCC
    0x00000000,  # NOP
    # Changes the number's position when pausing.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA4A,  # LBU   T1, 0xAA4A (T0)
    0x35290002,  # ORI   T1, T1, 0x0002
    0x08021BA6,  # J     0x80086E98
    0xA109AA4A,  # SB    T1, 0xAA4A (T0)
    # Changes the number's position when un-pausing.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA4A,  # LBU   T1, 0xAA4A (T0)
    0x312900FD,  # ANDI  T1, T1, 0x00FD
    0x08021B0A,  # J     0x80086C28
    0xA109AA4A,  # SB    T1, 0xAA4A (T0)
    # Hides the number whenever the HUD vanishes (during cutscenes, etc.)
    0xA20A0001,  # SB    T2, 0x0001 (S0)
    0x3C0B801D,  # LUI   T3, 0x801D
    0x916CAA4A,  # LBU   T4, 0xAA4A (T3)
    0x358C0001,  # ORI   T4, T4, 0x0001
    0x03E00008,  # JR    RA
    0xA16CAA4A,  # SB    T4, 0xAA4A (T3)
    0x00000000,  # NOP
    # Un-hides the number whenever the HUD re-appears (after a cutscene ends, etc.)
    0xA2000001,  # SB    R0, 0x0001 (S0)
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA4A,  # LBU   T1, 0xAA4A (T0)
    0x312900FE,  # ANDI  T1, T1, 0x00FE
    0x03E00008,  # JR    RA
    0xA109AA4A,  # SB    T1, 0xAA4A (T0)
    0x00000000,  # NOP
    # Decrements the Countdown number if the item picked up has a non-zero set in its field 0x45.
    0x92080045,  # LBU   T0, 0x0045 (S0)
    0x11000009,  # BEQZ  T0,     [forward 0x09]
    0x3C09801D,  # LUI   T1, 0x801D
    0x912AAE79,  # LBU   T2, 0xAE79 (T1)
    0x3C0B8040,  # LUI   T3, 0x8040
    0x016A5821,  # ADDU  T3, T3, T2
    0x916CC4D0,  # LBU   T4, 0xC4D0 (T3)
    0x01896821,  # ADDU  T5, T4, T1
    0x91AEABA0,  # LBU   T6, 0xABA0 (T5)
    0x25CEFFFF,  # ADDIU T6, T6, 0xFFFF
    0xA1AEABA0,  # SB    T6, 0xABA0 (T5)
    0x03200008   # JR    T9
]

new_game_extras = [
    # Upon starting a new game, this will write anything extra to the save file data that the run should have at the
    # start.

    # The initial Countdown numbers begin here.
    0x24080000,  # ADDIU T0, R0, 0x0000
    0x24090014,  # ADDIU T1, R0, 0x0014
    0x11090008,  # BEQ   T0, T1, [forward 0x08]
    0x3C0A8040,  # LUI   T2, 0x8040
    0x01485021,  # ADDU  T2, T2, T0
    0x8D4AC7D0,  # LW    T2, 0xC7D0 (T2)
    0x3C0B801D,  # LUI   T3, 0x801D
    0x01685821,  # ADDU  T3, T3, T0
    0xAD6AABA0,  # SW    T2, 0xABA0 (T3)
    0x1000FFF8,  # B             [backward 0x08]
    0x25080004,  # ADDIU T0, T0, 0x0004
    # start_inventory begins here.
    0x3C08801D,  # LUI   T0, 0x801D
    # Clear the multiworld buffers and set the "received item index" to 0
    0xA500ABBE,  # SH    R0, 0xABBE (T0)
    0xFD00AA48,  # SD    R0, 0xAA48 (T0)
    0x3C0A8040,  # LUI   T2, 0x8040
    0x3C0B0000,  # LUI   T3, 0x0000      <- Starting money (upper half)
    0x356B0000,  # ORI   T3, T3, 0x0000  <- Starting money (lower half)
    0xAD0BAB40,  # SW    T3, 0xAB40 (T0)
    0x24090000,  # ADDIU T1, R0, 0x0000  <- Starting PowerUps
    0xA109AE23,  # SB    T1, 0xAE23 (T0)
    0x24090000,  # ADDIU T1, R0, 0x0000  <- Starting sub-weapon
    0xA109AB3F,  # SB    T1, 0xAB3F (T0)
    0x24090000,  # ADDIU T1, R0, 0x0000  <- Starting sub-weapon level
    0xA109AE27,  # SB    T1, 0xAE27 (T0)
    0x24090000,  # ADDIU T1, R0, 0x0000  <- Starting Ice Traps
    0xA109AA49,  # SB    T1, 0xAA49 (T0)
    0x240C0000,  # ADDIU T4, R0, 0x0000
    0x240D0030,  # ADDIU T5, R0, 0x0030
    0x11AC0007,  # BEQ   T5, T4, [forward 0x07]
    0x3C0A8040,  # LUI   T2, 0x8040
    0x014C5021,  # ADDU  T2, T2, T4
    0x814AC7A0,  # LB    T2, 0xC7A0      <- Starting inventory items
    0xA10AAB44,  # SB    T2, 0xAB44 (T0)
    0x25080001,  # ADDIU T0, T0, 0x0001
    0x1000FFF9,  # B             [backward 0x07]
    0x258C0001,  # ADDIU T4, T4, 0x0001
    0x03E00008   # JR    RA
]

shopsanity_stuff = [
    # Everything related to shopsanity.
    # Flag table (in bytes) start
    0x80402010,
    0x08000000,
    0x00000000,
    0x00000000,
    0x00040200,
    # Replacement item table (in halfwords) start
    0x00030003,
    0x00030003,
    0x00030000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000003,
    0x00030000,
    # Switches the vanilla item being bought with the randomized one, if its flag is un-set, and sets its flag.
    0x3C088040,  # LUI   T0, 0x8040
    0x01044021,  # ADDU  T0, T0, A0
    0x9109D8CA,  # LBU   T1, 0xD8CA (T0)
    0x3C0B8039,  # LUI   T3, 0x8039
    0x916A9C1D,  # LBU   T2, 0x9C1D (T3)
    0x01496024,  # AND   T4, T2, T1
    0x15800005,  # BNEZ  T4,     [forward 0x05]
    0x01495025,  # OR    T2, T2, T1
    0xA16A9C1D,  # SB    T2, 0x9C1D (T3)
    0x01044021,  # ADDU  T0, T0, A0
    0x9504D8D8,  # LHU   A0, 0xD8D8 (T0)
    0x308400FF,  # ANDI  A0, A0, 0x00FF
    0x0804EFFB,  # J     0x8013BFEC
    0x00000000,  # NOP
    # Switches the vanilla item model on the buy menu with the randomized item if the randomized item isn't purchased.
    0x3C088040,  # LUI   T0, 0x8040
    0x01044021,  # ADDU  T0, T0, A0
    0x9109D8CA,  # LBU   T1, 0xD8CA (T0)
    0x3C0B8039,  # LUI   T3, 0x8039
    0x916A9C1D,  # LBU   T2, 0x9C1D (T3)
    0x01495024,  # AND   T2, T2, T1
    0x15400005,  # BNEZ  T2,     [forward 0x05]
    0x01044021,  # ADDU  T0, T0, A0
    0x9504D8D8,  # LHU   A0, 0xD8D8 (T0)
    0x00046202,  # SRL   T4, A0, 8
    0x55800001,  # BNEZL T4,     [forward 0x01]
    0x01802021,  # ADDU  A0, T4, R0
    0x0804F180,  # J     0x8013C600
    0x00000000,  # NOP
    # Replacement item names table start.
    0x00010203,
    0x04000000,
    0x00000000,
    0x00000000,
    0x00050600,
    0x00000000,
    # Switches the vanilla item name in the shop menu with the randomized item if the randomized item isn't purchased.
    0x3C088040,  # LUI   T0, 0x8040
    0x01064021,  # ADDU  T0, T0, A2
    0x9109D8CA,  # LBU   T1, 0xD8CA (T0)
    0x3C0B8039,  # LUI   T3, 0x8039
    0x916A9C1D,  # LBU   T2, 0x9C1D (T3)
    0x01495024,  # AND   T2, T2, T1
    0x15400004,  # BNEZ  T2,     [forward 0x04]
    0x00000000,  # NOP
    0x9105D976,  # LBU   A1, 0xD976 (T0)
    0x3C048001,  # LUI   A0, 8001
    0x3484A100,  # ORI   A0, A0, 0xA100
    0x0804B39F,  # J     0x8012CE7C
    0x00000000,  # NOP
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    # Displays "Not purchased." if the selected randomized item is nor purchased, or the current holding amount of that
    # slot's vanilla item if it is.
    0x3C0C8040,  # LUI   T4, 0x8040
    0x018B6021,  # ADDU  T4, T4, T3
    0x918DD8CA,  # LBU   T5, 0xD8CA (T4)
    0x3C0E8039,  # LUI   T6, 0x8039
    0x91D89C1D,  # LBU   T8, 0x9C1D (T6)
    0x030DC024,  # AND   T8, T8, T5
    0x13000003,  # BEQZ  T8,     [forward 0x03]
    0x00000000,  # NOP
    0x0804E819,  # J     0x8013A064
    0x00000000,  # NOP
    0x0804E852,  # J     0x8013A148
    0x820F0061,  # LB    T7, 0x0061 (S0)
    0x00000000,  # NOP
    # Displays a custom item description if the selected randomized item is not purchased.
    0x3C088040,  # LUI   T0, 0x8040
    0x01054021,  # ADDU  T0, T0, A1
    0x9109D8D0,  # LBU   T1, 0xD8D0 (T0)
    0x3C0A8039,  # LUI   T2, 0x8039
    0x914B9C1D,  # LBU   T3, 0x9C1D (T2)
    0x01695824,  # AND   T3, T3, T1
    0x15600003,  # BNEZ  T3,     [forward 0x03]
    0x00000000,  # NOP
    0x3C048002,  # LUI   A0, 0x8002
    0x24849C00,  # ADDIU A0, A0, 0x9C00
    0x0804B39F   # J     0x8012CE7C
]

special_sound_notifs = [
    # Plays a distinct sound whenever you get enough Special1s to unlock a new location or enough Special2s to unlock
    # Dracula's door.

    # Special2 (should play Fake Dracula's hurt voice clip if the new number of them is equal to the amount required
    # for Dracula's door).
    0x24080000,  # ADDIU T0, R0, 0x0000   <- Special2s required
    0x15030003,  # BNE   T0, V1, [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166f8
    0x240402E4,  # ADDIU A0, R0, 0x02E4
    0x08023F25,  # J     0x8008FC94
    0x24020001,  # ADDIU V0, R0, 0x0001
    # Special1 (Should play the teleport sound if the new number of them is equal to an amount that would unlock a new
    # warp destination).
    0x24080000,  # ADDIU T0, R0, 0x0000   <- Special1s per warp
    0x0068001B,  # DIVU  V1, T0
    # After dividing the S1s per warp by our current S1 count, if the remainder is not 0, don't play the warp notif.
    0x00005010,  # MFHI  T2
    0x15400006,  # BNEZ  T2,     [forward 0x06]
    # If the quotient is a higher number than the total number of warps the slot has, don't play the warp notif.
    0x00005812,  # MFLO  T3
    0x296C0008,  # SLTI  T4, T3, 0x0000   <- Total warps
    0x11800003,  # BEQZ  T4,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166f8
    0x2404019B,  # ADDIU A0, R0, 0x019B
    0x08023F25,  # J     0x8008FC94
    0x24020001   # ADDIU V0, R0, 0x0001
]

stage_intro_cs_player = [
    # Plays the Foggy Lake or Villa intro cutscene after transitioning to a different map if the map being transitioned
    # to is the start of their levels respectively. Gets around the fact that they have to be set on the previous
    # loading zone for them to play normally.

    # If we're going to Foggy Lake's start, and the custom flag we're using to see if we've seen it (0x2F6) isn't set,
    # prime the Foggy Lake ferryman cutscene to play and set the flag.
    0x3C08801D,  # LUI   T0, 0x801D
    0x8D09AE78,  # LW    T1, 0xAE78 (T0)
    0x3C0A0010,  # LUI   T2, 0x0010
    0x152A0008,  # BNE   T1, T2, [forward 0x08]
    0x910BAABE,  # LBU   T3, 0xAABE (T0)
    0x316C0004,  # ANDI  T4, T3, 0x0004
    0x15800004,  # BNEZ  T4,     [forward 0x04]
    0x356B0004,  # ORI   T3, T3, 0x0004
    0xA10BAABE,  # SB    T3, 0xAABE (T0)
    0x340D0010,  # ORI   T5, R0, 0x0010
    0xA50DAE8E,  # SH    T5, 0xAE8E (T0)
    0x08006A31,  # J     0x8001A8C4
    # If we're going to Villa's start, the Villa intro cutscene flag isn't set (flag 0x55), and the "Dog Wave 3 beaten"
    # flag (0x58) isn't set, prime the Villa intro cutscene to play and set the flag.
    0x3C0A0003,  # LUI   T2, 0x0003
    0x152A000A,  # BNE   T1, T2, [forward 0x0A]
    0x910BAA6B,  # LBU   T3, 0xAA6B (T0)
    0x316C0080,  # ANDI  T4, T3, 0x0080
    0x15800007,  # BNEZ  T4,     [forward 0x07]
    0x910BAA6A,  # LBU   T3, 0xAA6A (T0)
    0x316C0004,  # ANDI  T4, T3, 0x0004
    0x15800004,  # BNEZ  T4,     [forward 0x04]
    0x356B0004,  # ORI   T3, T3, 0x0004
    0xA10BAA6A,  # SB    T3, 0xAA6A (T0)
    0x340D0009,  # ORI   T5, R0, 0x0009
    0xA50DAE8E,  # SH    T5, 0xAE8E (T0)
    0x08006A31   # J     0x8001A8C4
]

alt_setup_flag_setter = [
    # While loading into a scene, when the game checks to see which entrance to spawn the player at, this will check for
    # the 0x40 and/or 0x80 bits in the spawn ID and, if they are, set one of the three "alternate setup" flags
    # (0x2A1, 0x2A2, or 0x2A3) while un-setting the other two. This allows for scenes to load with different setups,
    # almost as if they were separate scenes entirely, and is useful for things like the Algenie/Medusa arena and the
    # fan meeting room being able to exist as separate scenes in separate stages. Also handles other rando-specific
    # things that should be handled upon scene transition, like setting the remote receive delay timer.

    # Un-set the "can't warp" byte and set our remote receive delay timer to 30 frames (1 second).
    0x340F003E,  # ORI   T7, R0, 0x003E
    0xA04F278E,  # SB    T7, 0x278E (V0)
    0xA040278B,  # SB    R0, 0x278B (V0)
    # If the "began Malus chase" flag is set and the "finished Malus chase" flag is not, un-set the former so the chase
    # can be re-triggered later.
    0x3C0F801D,  # LUI   T7, 0x801D
    0x91EAAA72,  # LBU   T2, 0xAA72 (T7)
    0x314B0020,  # ANDI  T3, T2, 0x0020
    0x15600004,  # BNEZ  T3,     [forward 0x04]
    0x91ECAA72,  # LBU   T4, 0xAA72 (T7)
    0x318D0040,  # ANDI  T5, T4, 0x0040
    0x018D6023,  # SUBU  T4, T4, T5
    0xA1ECAA72,  # SB    T4, 0xAA72 (T7)
    # If the "began Henry escort" flag is set and the "finished Henry escort" flag is not, un-set the former so the
    # escort can be re-triggered later.
    0x91EAAA72,  # LBU   T2, 0xAA72 (T7)
    0x314B0008,  # ANDI  T3, T2, 0x0008
    0x15600004,  # BNEZ  T3,     [forward 0x04]
    0x91ECAA72,  # LBU   T4, 0xAA72 (T7)
    0x318D0010,  # ANDI  T5, T4, 0x0010
    0x018D6023,  # SUBU  T4, T4, T5
    0xA1ECAA72,  # SB    T4, 0xAA72 (T7)
    # If the "Waterway Lizard man trio cutscene" flag is set and the custom "defeated Lizard trio" flag is not,
    # un-set the former so the cutscene can be re-triggered later.
    0x91EAAABE,  # LBU   T2, 0xAABE (T7)
    0x314B0001,  # ANDI  T3, T2, 0x0001
    0x15600004,  # BNEZ  T3,     [forward 0x04]
    0x91ECAA7B,  # LBU   T4, 0xAA7B (T7)
    0x318D0080,  # ANDI  T5, T4, 0x0080
    0x018D6023,  # SUBU  T4, T4, T5
    0xA1ECAA7B,  # SB    T4, 0xAA7B (T7)
    # Check if the 0x40 AND 0x80 bits are both set in the spawn ID (it should be exactly 0xC0). If it is, set flag 0x2A3
    # and un-set the other two.
    0x904F2BBB,  # LBU   T7, 0x2BBB (V0)
    0x31EA00C0,  # ANDI  T2, T7, 0x00C0
    0x340B00C0,  # ORI   T3, R0, 0x00C0
    0x154B0008,  # BNE   T2, T3, [forward 0x08]
    0x904B27F4,  # LBU   T3, 0x27F4 (V0)
    0x316B009F,  # ANDI  T3, T3, 0x009F
    0x356B0010,  # ORI   T3, T3, 0x0010
    0xA04B27F4,  # SB    T3, 0x27F4 (V0)
    # Un-set the alternate setup bits from the spawn ID and write it back.
    0x31EF003F,  # ANDI  T7, T7, 0x003F
    0xA04F2BBB,  # SB    T7, 0x2BBB (V0)
    0x03E00008,  # JR    RA
    0xA44E28D0,  # SH    T6, 0x28D0 (V0)
    # Check if the 0x40 bit is set in the spawn ID. If it is, set flag 0x2A1 and un-set the other two.
    0x31EA0040,  # ANDI  T2, T7, 0x0040
    0x11400008,  # BEQZ  T2,     [forward 0x08]
    0x904B27F4,  # LBU   T3, 0x27F4 (V0)
    0x316B00CF,  # ANDI  T3, T3, 0x00CF
    0x356B0040,  # ORI   T3, T3, 0x0040
    0xA04B27F4,  # SB    T3, 0x27F4 (V0)
    # Un-set the alternate setup bits from the spawn ID and write it back.
    0x31EF003F,  # ANDI  T7, T7, 0x003F
    0xA04F2BBB,  # SB    T7, 0x2BBB (V0)
    0x03E00008,  # JR    RA
    0xA44E28D0,  # SH    T6, 0x28D0 (V0)
    # Check if the 0x80 bit is set in the spawn ID. If it is, set flag 0x2A2 and un-set the other two.
    0x31EA0080,  # ANDI  T2, T7, 0x0080
    0x11400006,  # BEQZ  T2,     [forward 0x06]
    0x904B27F4,  # LBU   T3, 0x27F4 (V0)
    0x316B00AF,  # ANDI  T3, T3, 0x00AF
    0x356B0020,  # ORI   T3, T3, 0x0020
    0xA04B27F4,  # SB    T3, 0x27F4 (V0)
    # Un-set the alternate setup bits from the spawn ID and write it back.
    0x31EF003F,  # ANDI  T7, T7, 0x003F
    0xA04F2BBB,  # SB    T7, 0x2BBB (V0)
    0x03E00008,  # JR    RA
    0xA44E28D0,  # SH    T6, 0x28D0 (V0)
]

character_changer = [
    # Changes the character being controlled if the player is holding L while loading into a map by swapping the
    # character ID.
    0x3C08800D,  # LUI   T0, 0x800D
    0x910B5E21,  # LBU   T3, 0x5E21 (T0)
    0x31680020,  # ANDI  T0, T3, 0x0020
    0x3C0A8039,  # LUI   T2, 0x8039
    0x1100000B,  # BEQZ  T0,     [forward 0x0B]
    0x91499C3D,  # LBU   T1, 0x9C3D (T2)
    0x11200005,  # BEQZ  T1,     [forward 0x05]
    0x24080000,  # ADDIU T0, R0, 0x0000
    0xA1489C3D,  # SB    T0, 0x9C3D (T2)
    0x25080001,  # ADDIU T0, T0, 0x0001
    0xA1489BC2,  # SB    T0, 0x9BC2 (T2)
    0x10000004,  # B             [forward 0x04]
    0x24080001,  # ADDIU T0, R0, 0x0001
    0xA1489C3D,  # SB    T0, 0x9C3D (T2)
    0x25080001,  # ADDIU T0, T0, 0x0001
    0xA1489BC2,  # SB    T0, 0x9BC2 (T2)
    # Changes the alternate costume variables if the player is holding C-up.
    0x31680008,  # ANDI  T0, T3, 0x0008
    0x11000009,  # BEQZ  T0,     [forward 0x09]
    0x91499C24,  # LBU   T1, 0x9C24 (T2)
    0x312B0040,  # ANDI  T3, T1, 0x0040
    0x2528FFC0,  # ADDIU T0, T1, 0xFFC0
    0x15600003,  # BNEZ  T3,     [forward 0x03]
    0x240C0000,  # ADDIU T4, R0, 0x0000
    0x25280040,  # ADDIU T0, T1, 0x0040
    0x240C0001,  # ADDIU T4, R0, 0x0001
    0xA1489C24,  # SB    T0, 0x9C24 (T2)
    0xA14C9CEE,  # SB    T4, 0x9CEE (T2)
    0x080062AA,  # J     0x80018AA8
    0x00000000,  # NOP
    # Plays the attack sound of the character being changed into to indicate the change was successful.
    0x3C088039,  # LUI   T0, 0x8039
    0x91099BC2,  # LBU   T1, 0x9BC2 (T0)
    0xA1009BC2,  # SB    R0, 0x9BC2 (T0)
    0xA1009BC1,  # SB    R0, 0x9BC1 (T0)
    0x11200006,  # BEQZ  T1,     [forward 0x06]
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0x240402F6,  # ADDIU A0, R0, 0x02F6
    0x55200001,  # BNEZL T1,     [forward 0x01]
    0x240402F8,  # ADDIU A0, R0, 0x02F8
    0x08004FAB,  # J     0x80013EAC
    0x00000000,  # NOP
    0x03E00008   # JR    RA
]

panther_dash = [
    # Changes various movement parameters when holding C-right so the player will move way faster.
    # Increases movement speed and speeds up the running animation.
    0x3C08800D,  # LUI   T0, 0x800D
    0x91085E21,  # LBU   T0, 0x5E21 (T0)
    0x31080001,  # ANDI  T0, T0, 0x0001
    0x24093FEA,  # ADDIU T1, R0, 0x3FEA
    0x11000004,  # BEQZ  T0,     [forward 0x04]
    0x240B0010,  # ADDIU T3, R0, 0x0010
    0x3C073F20,  # LUI   A3, 0x3F20
    0x240940AA,  # ADDIU T1, R0, 0x40AA
    0x240B000A,  # ADDIU T3, R0, 0x000A
    0x3C0C8035,  # LUI   T4, 0x8035
    0xA18B07AE,  # SB    T3, 0x07AE (T4)
    0xA18B07C2,  # SB    T3, 0x07C2 (T4)
    0x3C0A8034,  # LUI   T2, 0x8034
    0x03200008,  # JR    T9
    0xA5492BD8,  # SH    T1, 0x2BD8 (T2)
    0x00000000,  # NOP
    # Increases the turning speed so that handling is better.
    0x3C08800D,  # LUI   T0, 0x800D
    0x91085E21,  # LBU   T0, 0x5E21 (T0)
    0x31080001,  # ANDI  T0, T0, 0x0001
    0x11000002,  # BEQZ  T0,     [forward 0x02]
    0x240A00D9,  # ADDIU T2, R0, 0x00D9
    0x240A00F0,  # ADDIU T2, R0, 0x00F0
    0x3C0B8039,  # LUI   T3, 0x8039
    0x916B9C3D,  # LBU   T3, 0x9C3D (T3)
    0x11600003,  # BEQZ  T3,     [forward 0x03]
    0xD428DD58,  # LDC1  F8, 0xDD58 (AT)
    0x03E00008,  # JR    RA
    0xA02ADD59,  # SB    T2, 0xDD59 (AT)
    0xD428D798,  # LDC1  F8, 0xD798 (AT)
    0x03E00008,  # JR    RA
    0xA02AD799,  # SB    T2, 0xD799 (AT)
    0x00000000,  # NOP
    # Increases crouch-walking x and z speed.
    0x3C08800D,  # LUI   T0, 0x800D
    0x91085E21,  # LBU   T0, 0x5E21 (T0)
    0x31080001,  # ANDI  T0, T0, 0x0001
    0x11000002,  # BEQZ  T0,     [forward 0x02]
    0x240A00C5,  # ADDIU T2, R0, 0x00C5
    0x240A00F8,  # ADDIU T2, R0, 0x00F8
    0x3C0B8039,  # LUI   T3, 0x8039
    0x916B9C3D,  # LBU   T3, 0x9C3D (T3)
    0x15600005,  # BNEZ  T3,     [forward 0x05]
    0x00000000,  # NOP
    0xA02AD801,  # SB    T2, 0xD801 (AT)
    0xA02AD809,  # SB    T2, 0xD809 (AT)
    0x03E00008,  # JR    RA
    0xD430D800,  # LDC1  F16, 0xD800 (AT)
    0xA02ADDC1,  # SB    T2, 0xDDC1 (AT)
    0xA02ADDC9,  # SB    T2, 0xDDC9 (AT)
    0x03E00008,  # JR    RA
    0xD430DDC0   # LDC1  F16, 0xDDC0 (AT)
]

panther_jump_preventer = [
    # Optional hack to prevent jumping while moving at the increased panther dash speed as a way to prevent logic
    # sequence breaks that would otherwise be impossible without it. Such sequence breaks are never considered in logic
    # either way.

    # Decreases a "can running jump" value by 1 per frame unless it's at 0, or while in the sliding state. When the
    # player lets go of C-right, their running speed should have returned to a normal amount by the time it hits 0.
    0x9208007F,  # LBU   T0, 0x007F (S0)
    0x24090008,  # ADDIU T1, R0, 0x0008
    0x11090005,  # BEQ   T0, T1, [forward 0x05]
    0x3C088039,  # LUI   T0, 0x8039
    0x91099BC1,  # LBU   T1, 0x9BC1 (T0)
    0x11200002,  # BEQZ  T1,     [forward 0x02]
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0xA1099BC1,  # SB    T1, 0x9BC1 (T0)
    0x080FF413,  # J     0x803FD04C
    0x00000000,  # NOP
    # Increases the "can running jump" value by 2 per frame while panther dashing unless it's at 8 or higher, at which
    # point the player should be at the max panther dash speed.
    0x00074402,  # SRL   T0, A3, 16
    0x29083F7F,  # SLTI  T0, T0, 0x3F7F
    0x11000006,  # BEQZ  T0,     [forward 0x06]
    0x3C098039,  # LUI   T1, 0x8039
    0x912A9BC1,  # LBU   T2, 0x9BC1 (T1)
    0x254A0002,  # ADDIU T2, T2, 0x0002
    0x294B0008,  # SLTI  T3, T2, 0x0008
    0x55600001,  # BNEZL T3,     [forward 0x01]
    0xA12A9BC1,  # SB    T2, 0x9BC1 (T1)
    0x03200008,  # JR    T9
    0x00000000,  # NOP
    # Makes running jumps only work while the "can running jump" value is at 0. Otherwise, their state won't change.
    0x3C010001,  # LUI   AT, 0x0001
    0x3C088039,  # LUI   T0, 0x8039
    0x91089BC1,  # LBU   T0, 0x9BC1 (T0)
    0x55000001,  # BNEZL T0,     [forward 0x01]
    0x3C010000,  # LUI   AT, 0x0000
    0x03E00008   # JR    RA
]

shimmy_speed_modifier = [
    # Increases the player's speed while shimmying as long as they are not holding down Z. If they are holding Z, it
    # will be the normal speed, allowing it to still be used to set up any tricks that might require the normal speed
    # (like Left Tower Skip in original CV64).
    0x3C08801D,  # LUI   T0, 0x801D
    0x910887F6,  # LBU   T0, 0x87F6 (T0)
    0x31090020,  # ANDI  T1, T0, 0x0020
    0x3C0A800C,  # LUI   T2, 0x800C
    0x340B4580,  # ORI   T3, R0, 0x4580
    0x55200001,  # BNEZL T1,     [forward 0x01]
    0x340B46FF,  # ORI   T3, R0, 0x46FF
    0xA54BE170,  # SH    T3, 0xE170 (T2)
    0x08028E94,  # J     0x800A3A50
    0xA54BE174,  # SH    T3, 0xE174 (T2)
]

gondola_spider_cutscene_checker = [
    # Checks for flag 0xAD (the Spider Women cutscene flag) before activating the Tunnel gondolas, restoring their
    # original behavior from CV64.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA75,  # LBU   T1, 0xAA75 (T0)
    0x312A0004,  # ANDI  T2, T1, 0x0004
    0x15400003,  # BNEZ  T2,     [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    0x08051DBF,  # J     0x801476FC
    0x00000000,  # NOP
]

gondola_skipper = [
    # Upon stepping on one of the gondolas in Tunnel to activate it, this will instantly teleport you to the other end
    # of the gondola course depending on which one activated, skipping the entire 3-minute wait to get there.

    # Access the gondola's actor list entry and check to see if it's the blue one specifically. This will determine
    # what spawn spot we send the player to and what color to make the fade transition.
    0x8CA80070,  # LW    T0, 0x0070 (A1)
    0x95090018,  # LHU   T1, 0x0018 (T0)
    # If it's gondola number 5 (the blue one), que up the blue gondola's transition settings.
    0x240A0005,  # ADDIU T2, R0, 0x0005  <- Blue gondola's palette ID
    0x152A0004,  # BNE   T1, T2, [forward 0x04]
    0x3C0C3080,  # LUI   T4, 0x3080      <- Blue gondola fade color
    0x358C9700,  # ORI   T4, T4, 0x9700
    0x10000003,  # B             [forward 0x03]
    0x240B000A,  # ADDIU T3, R0, 0x000A  <- Blue gondola destination ID
    # If not number 5, que up the red gondola's transition settings.
    0x3C0C7A00,  # LUI   T4, 0x7A00      <- Red gondola fade color
    0x240B000B,  # ADDIU T3, R0, 0x000B  <- Red gondola destination ID
    # Store the values.
    0x2409000C,  # ADDIU T5, R0, 0x000C  <- Fade out and in time
    0x3C08801D,  # LUI   T0, 0x801D
    0xA509AE80,  # SH    T1, 0xAE80 (T0)
    0xA509AE82,  # SH    T1, 0xAE82 (T0)
    0xAD0CAE7C,  # SW    T4, 0xAE7C (T0)
    0x08051DBF,  # J     0x801476FC
    0xA50BAE7A,  # SH    T3, 0xAE7A (T0)
]

ambience_silencer = [
    # Silences scene-specific ambience when loading into a different scene, so we don't have to live with, say, Tower of
    # Science/Clock Tower machinery noises everywhere until either resetting, dying, or going into a scene that is
    # normally set up to disable said noises. We can only silence a few sounds at a time, so we will be very selective
    # about it by checking to see if said sounds are actually playing.

    # In addition, during the map loading process, if this detects the scene ID being transitioned to as FF, it will
    # write back the past spawn ID so that the map will still reload while keeping the scene and spawn IDs unchanged.
    # Useful for things like setting a transition to lead back to itself.

    # Run the "set fade settings" function like normal upon beginning a scene transition.
    0x0C004156,  # JAL   0x80010558
    0x00000000,  # NOP
    # Check if the scene ID being transitioned to is 0xFF. If it is, write back the scene ID being transitioned from.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AB91,  # LBU   T1, 0xAB91 (T0)
    0x910CAE79,  # LBU   T4, 0xAE79 (T0)
    0x340B00FF,  # ORI   T3, R0, 0x00FF
    0x518B0001,  # BEQL  T4, T3, [forward 0x01]
    0xA109AE79,  # SB    T1, 0xAE79 (T0)
    0x9110AE79,  # LBU   S0, 0xAE79 (T0)
    # Silence the Foggy Lake ship noises if we're not transitioning to the above or below decks scenes.
    0x240A0010,  # ADDIU T2, R0, 0x0010
    0x120A000F,  # BEQ   S0, T2, [forward 0x0F]
    0x240A0011,  # ADDIU T2, R0, 0x0011
    0x120A000D,  # BEQ   S0, T2, [froward 0x0D]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x240401A0,  # ADDIU A0, R0, 0x01A0
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x340481A0,  # ORI   A0, R0, 0x81A0
    0x0C00545C,  # JAL   0x80015170
    0x240401A1,  # ADDIU A0, R0, 0x01A1
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x340481A1,  # ORI   A0, R0, 0x81A1
    # Silence the common "wind ambience" noise if we're transitioning to a non-Castle Wall scene.
    0x240A0001,  # ADDIU T2, R0, 0x0001
    0x120A0009,  # BEQ   S0, T2, [forward 0x09]
    0x240A0002,  # ADDIU T2, R0, 0x0002
    0x120A0007,  # BEQ   S0, T2, [froward 0x07]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x24040136,  # ADDIU A0, R0, 0x0136
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048136,  # ORI   A0, R0, 0x8136
    # Silence all Gardener and Child Henry escort noises in case we're transitioning from the Maze Garden scene
    # (the "Jaws Theme" instruments that are separate sounds and the Gardener's proximity chainsaw sound).
    # No need to check this scene because they should always be silenced no matter what.
    0x0C00545C,  # JAL   0x80015170
    0x24040371,  # ADDIU A0, R0, 0x0371
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048371,  # ORI   A0, R0, 0x8371
    0x0C00545C,  # JAL   0x80015170
    0x24040372,  # ADDIU A0, R0, 0x0372
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048372,  # ORI   A0, R0, 0x8372
    0x0C00545C,  # JAL   0x80015170
    0x24040358,  # ADDIU A0, R0, 0x0358
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048358,  # ORI   A0, R0, 0x8358
    # Silence the Outer Wall wind noises if we're transitioning to a scene that's not Outer Wall.
    0x240A002A,  # ADDIU T2, R0, 0x002A
    0x120A000D,  # BEQ   S0, T2, [froward 0x0D]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x240401BF,  # ADDIU A0, R0, 0x01BF
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x340481BF,  # ORI   A0, R0, 0x81BF
    0x0C00545C,  # JAL   0x80015170
    0x24040172,  # ADDIU A0, R0, 0x0172
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048172,  # ORI   A0, R0, 0x8172
    # Silence the Fan Meeting Room fans if we're transitioning to a scene that's not the Fan Meeting Room.
    0x240A0019,  # ADDIU T2, R0, 0x0019
    0x120A0007,  # BEQ   S0, T2, [froward 0x07]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x240401ED,  # ADDIU A0, R0, 0x01ED
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x340481ED,  # ORI   A0, R0, 0x81ED
    # Silence the Tower of Execuiton lava noises if we're transitioning to a non-Tower of Execution scene.
    0x240A001E,  # ADDIU T2, R0, 0x001E
    0x120A0011,  # BEQ   S0, T2, [forward 0x11]
    0x240A001F,  # ADDIU T2, R0, 0x001F
    0x120A000F,  # BEQ   S0, T2, [forward 0x0F]
    0x240A0020,  # ADDIU T2, R0, 0x0020
    0x120A000D,  # BEQ   S0, T2, [froward 0x0D]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x240401BB,  # ADDIU A0, R0, 0x01BB
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x340481BB,  # ORI   A0, R0, 0x81BB
    0x0C00545C,  # JAL   0x80015170
    0x24040369,  # ADDIU A0, R0, 0x0369
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048369,  # ORI   A0, R0, 0x8369
    # Silence the machinery humming from Tower of Science if we're transitioning to a non-Tower of Science scene.
    0x240A0021,  # ADDIU T2, R0, 0x0021
    0x120A0009,  # BEQ   S0, T2, [forward 0x09]
    0x240A0022,  # ADDIU T2, R0, 0x0022
    0x120A0007,  # BEQ   S0, T2, [forward 0x07]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x24040368,  # ADDIU A0, R0, 0x0368
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048368,  # ORI   A0, R0, 0x8368
    # Silence the gear noises from Clock Tower and Tower of Science if we're transitioning to a
    # non-Tower of Science/Clock Tower scene.
    0x240A0021,  # ADDIU T2, R0, 0x0021
    0x120A000F,  # BEQ   S0, T2, [forward 0x0F]
    0x240A0022,  # ADDIU T2, R0, 0x0022
    0x120A000D,  # BEQ   S0, T2, [forward 0x0D]
    0x240A0017,  # ADDIU T2, R0, 0x0017
    0x120A000B,  # BEQ   S0, T2, [forward 0x0B]
    0x240A0028,  # ADDIU T2, R0, 0x0028
    0x120A0009,  # BEQ   S0, T2, [forward 0x09]
    0x240A0029,  # ADDIU T2, R0, 0x0029
    0x120A0007,  # BEQ   S0, T2, [froward 0x07]
    0x00000000,  # NOP
    0x0C00545C,  # JAL   0x80015170
    0x24040188,  # ADDIU A0, R0, 0x0188
    0x10400003,  # BEQZ  V0,     [forward 0x03]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048188,  # ORI   A0, R0, 0x8188
    0x08006BCA   # J     0x8001AF28
]

multiworld_item_name_loader = [
    # When picking up an item from another world, this will load from ROM the custom message for that item explaining
    # in the item textbox what the item is and who it's for. The flag index it calculates determines from what part of
    # the ROM to load the item name from. If the item being picked up is a white jewel or a contract, it will always
    # load from a part of the ROM that has nothing in it to ensure their set "flag" values don't yield unintended names.
    # If picking up a subweapon, this will also grab the custom "subweapon levels to increase" value from said weapon
    # and store it somewhere easy to read later.

    # As we're picking up a pickup, before running the prepare item textbox function, copy from the ROM the off-world
    # Item string corresponding to that pickup.
    0x3C0800FA,  # LUI   T0, 0x00FA
    0x9609005A,  # LHU   T1, 0x005A (S0)
    # Shift the flag ID up by 8 and add it to 0xFA0000 to get the start address for this pickup's string.
    0x00094A00,  # SLL   T1, T1, 8
    0x01092021,  # ADDU  A0, T0, T1
    0x3C058001,  # LUI   A1, 0x8001
    0x34A5E5CC,  # ORI   A1, A1, 0xE5CC
    # Run the "rom copy" function with all necessary arguments.
    0x0C00690B,  # JAL   0x8001A42C
    0x34060100,  # ORI   A2, R0, 0x0100
    # Grab and store the subweapon level we stored on the pickup.
    0x3C08801D,  # LUI   T0, 0x801D
    0x92090053,  # LBU   T1, 0x0053 (S0)
    0xA109AA20,  # SB    T1, 0xAA20 (T0)
    0x96030038,  # LHU   V1, 0x0038 (S0)
    # Return to and continue the pickup routine like normal.
    0x3C048019,  # LUI   A0, 0x8019
    0x00037880,  # SLL   T7, T7, V1
    0x01E37821,  # ADDU  T7, T7, V1
    0x08061F2A,  # J     0x80187CA8
    0x000F7880,  # SLL   T7, T7, 2
    0x00000000,
    0x00000000,
    # Redirect the text to the multiworld message buffer if a message exists in it. Skip this if we're looking at a
    # White Jewel, as White Jewel identifiers occupy the same value as event flag IDs on other pickups.
    0x10A00007,  # BEQZ  A1,     [forward 0x07]
    0x3C088002,  # LUI   T0, 0x8002
    0x9108E5CC,  # LBU   T0, 0xE5CD (T0)
    0x11000004,  # BEQZ  T0,     [forward 0x04]
    0x00000000,  # NOP
    0x3C048001,  # LUI   A0, 0x8001
    0x3484E5CE,  # ORI   A0, A0, 0xE5CE
    0x24050000,  # ADDIU A1, R0, 0x0000
    0x08020FE8,  # J     0x80083FA0
    0x00000000,
    # Change the Y screen position and number of lines of the textbox depending on how many line breaks there are.
    # If we have a value of 0 lines, skip this routine entirely and go straight to the set text function.
    0x3C088002,  # LUI   T0, 0x8002
    0x9108E5CC,  # LBU   T0, 0xE5CC (T0)
    0x1100000C,  # BEQZ  T0,     [forward 0x0C]
    # If the number of lines is 5 or higher, set it down to the max of 4.
    0x29090005,  # SLTI  T1, T0, 0x0005
    0x51200001,  # BEQZL T1,     [forward 0x01]
    0x34080004,  # ORI   T0, R0, 0x0004
    0xAFA80018,  # SW    T0, 0x0018 (SP)
    # Add 16.0f times the number of lines we have to the textbox Y value to raise it higher on-screen.
    0x3C0A4180,  # LUI   T2, 0x4180
    0x448A1800,  # MTC1  T2, F3
    0x2508FFFF,  # ADDIU T0, T0, 0xFFFF
    0x44885000,  # MTC1  T0, F10
    0x468052A0,  # CVT.S.W   F10, F10
    0x460A18C2,  # MUL.S F3, F3, F10
    0x46032100,  # ADD.S F4, F4, F3
    0xE7A40010,  # SWC1  F4, 0x0010 (SP)
    0x08020C02,  # J     0x80083008
    0x00000000,
    # Change the textbox's background X and Y size depending on how many line breaks there are.
    # If we have a value of 0 lines, skip this routine entirely and go straight to the set background size function.
    0x3C088002,  # LUI   T0, 0x8002
    0x9108E5CC,  # LBU   T0, 0xE5CC (T0)
    0x1100000D,  # BEQZ  T0,     [forward 0x0D]
    # If the number of lines is 5 or higher, set it down to the max of 4.
    0x29090005,  # SLTI  T1, T0, 0x0005
    0x51200001,  # BEQZL T1,     [forward 0x01]
    0x34080004,  # ORI   T0, R0, 0x0004
    # Extend the background X size from 150.0f to 190.0f (its PAL version size)
    0x3C05433E,  # LUI   A1, 0x433E
    # Add 16.0f times the number of lines we have to the background Y size to extend it further downward.
    0x3C0A4180,  # LUI   T2, 0x4180
    0x448A1800,  # MTC1  T2, F3
    0x44862000,  # MTC1  A2, F4
    0x2508FFFF,  # ADDIU T0, T0, 0xFFFF
    0x44885000,  # MTC1  T0, F10
    0x468052A0,  # CVT.S.W   F10, F10
    0x460A18C2,  # MUL.S F3, F3, F10
    0x46032100,  # ADD.S F4, F4, F3
    0x44062000,  # MFC1  A2, F4
    0x08020F94,  # J     0x80083E50
    0x00000000,
    # Change the textbox's "open" timer depending on how many line breaks there are.
    # If we have a value of 0 lines, skip this routine entirely.
    0x3C098002,  # LUI   T1, 0x8002
    0x9128E5CC,  # LBU   T0, 0xE5CC (T1)
    0x11000008,  # BEQZ  T0,     [forward 0x08]
    0x44814000,  # MTC1  AT, F8
    # Add 0.75 seconds to the "textbox remaining open timer" for every line there is minus 1.
    0x3C0A3F40,  # LUI   T2, 0x3F40
    0x448A1800,  # MTC1  T2, F3
    0x2508FFFF,  # ADDIU T0, T0, 0xFFFF
    0x44885000,  # MTC1  T0, F10
    0x468052A0,  # CVT.S.W   F10, F10
    0x460A18C2,  # MUL.S F3, F3, F10
    0x46034200,  # ADD.S F8, F8, F3
    0x03E00008,  # JR    RA
    # At this point, neuter the multiworld text buffer by clearing the lines counter, since it's no longer needed.
    0xA120E5CC,  # SB    R0, 0xE5CC (T1)
]

ice_trap_initializer = [
    # During a map load, creates the module that allows the ice block model to appear while in the frozen state if not
    # on the intro narration map (map 0x16).
    0x3C088039,  # LUI   T0, 0x8039
    0x91089EE1,  # LBU   T0, 0x9EE1 (T0)
    0x24090016,  # ADDIU T1, R0, 0x0016
    0x11090004,  # BEQ   T0, T1, [forward 0x04]
    0x3C048034,  # LUI   A0, 0x8034
    0x24842ACC,  # ADDIU A0, A0, 0x2ACC
    0x08000660,  # J     0x80001980
    0x24052125,  # ADDIU A1, R0, 0x2125
    0x03E00008   # JR    RA
]

the_deep_freezer = [
    # Writes 000C0000 into the player state to freeze the player on the spot if Ice Traps have been received, writes the
    # Ice Trap code into the pointer value (0x20B8, which is also Camilla's boss code),and decrements the Ice Traps
    # remaining counter.
    0x3C0B8039,  # LUI   T3, 0x8039
    0x91699BE2,  # LBU   T3, 0x9BE2 (T0)
    0x1120000F,  # BEQZ  T1,     [forward 0x0F]
    0x3C088034,  # LUI   T0, 0x8034
    0x910827A9,  # LBU   T0, 0x27A9 (T0)
    0x240A000C,  # ADDIU T2, R0, 0x000C
    0x110A000B,  # BEQ   T0, T2, [forward 0x0B]
    0x240A0002,  # ADDIU T2, R0, 0x0002
    0x110A0009,  # BEQ   T0, T2, [forward 0x09]
    0x240A0008,  # ADDIU T2, R0, 0x0008
    0x110A0007,  # BEQ   T0, T2, [forward 0x07]
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0xA1699BE2,  # SB    T1, 0x9BE2 (T3)
    0x3C088034,  # LUI   T0, 0x8034
    0x3C09000C,  # LUI   T1, 0x000C
    0xAD0927A8,  # SW    T1, 0x27A8 (T0)
    0x240820B8,  # ADDIU T0, R0, 0x20B8
    0xA5689E6E,  # SH    T0, 0x9E6E (T3)
    0x03E00008   # JR    RA
]

freeze_verifier = [
    # Verifies for the ice chunk module that a freeze should spawn the ice model. The player must be in the frozen state
    # (0x000C) and 0x20B8 must be in either the freeze pointer value or the current boss ID (Camilla's); otherwise, we
    # weill assume that the freeze happened due to a vampire grab or Actrise shard tornado and not spawn the ice chunk.
    0x8C4E000C,  # LW    T6, 0x000C (V0)
    0x00803025,  # OR    A2, A0, R0
    0x8DC30008,  # LW    V1, 0x0008 (T6)
    0x3C088039,  # LUI   T0, 0x8039
    0x240920B8,  # ADDIU T1, R0, 0x20B8
    0x950A9E72,  # LHU   T2, 0x9E72 (T0)
    0x3C0C8034,  # LUI   T4, 0x8034
    0x918C27A9,  # LBU   T4, 0x27A9 (T4)
    0x240D000C,  # ADDIU T5, R0, 0x000C
    0x158D0004,  # BNE   T4, T5, [forward 0x04]
    0x3C0B0F00,  # LUI   T3, 0x0F00
    0x112A0005,  # BEQ   T1, T2, [forward 0x05]
    0x950A9E78,  # LHU   T2, 0x9E78 (T0)
    0x112A0003,  # BEQ   T1, T2, [forward 0x03]
    0x357996A0,  # ORI   T9, T3, 0x96A0
    0x03200008,  # JR    T9
    0x00000000,  # NOP
    0x35799640,  # ORI   T9, T3, 0x9640
    0x03200008,  # JR    T9
]

sea_monster_sunk_path_flag_unsetter = [
    # Un-sets the "debris path sunk" flag that gets set when the Sea Monster battle begins to normally ensure you cannot
    # escape back to the save platform, allowing it to be traversed again if the player leaves and comes back.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AA8B,  # LBU   T1, 0xAA8B (T0)
    0x312900F7,  # ANDI  T1, T1, 0x00F7
    0x03200008,  # JR    T9
    0xA109AA8B   # SB    T1, 0xAA8B (T0)
]

door_map_music_player = [
    # Put this in a door's extra check condition to open, and it will play the current map's song while always returning
    # that it's fine for the door to open. Good for the locked Tower of Science control room doors to start the music
    # when going backwards from the end of the stage, since killing the Security Crystal stops it.
    0x27BDFFE0,  # ADDIU SP, SP, -0x20
    0xAFBF0014,  # SW    RA, 0x0014 (SP)
    0x0C006938,  # JAL   0x8001A4E0
    0xAFA40004,  # SW    A0, 0x0004 (SP)
    0x0C053DF2,  # JAL   0x8014F7C8
    0x8FA40004,  # LW    A0, 0x0004 (SP)
    0x8FBF0014,  # LW    RA, 0x0014 (SP)
    0x27BD0020,  # ADDIU SP, SP, 0x20
    0x03E00008,  # JR    RA
]

pink_sorcery_diamond_customizer = [
    # Gives each item that drops from the pink Tower of Sorcery diamond its own unique flag and additional settings
    # attributes.
    0x03104000,
    0x03114000,
    0x03124000,
    0x00000000,
    0x00104080,  # SLL   T0, S0, 2
    0x3C09802F,  # LUI   T1, 0x802F
    0x01094821,  # ADDU  T1, T0, T1
    0x952AAC30,  # LHU   T2, 0xAC30 (T1)
    0x9527AC32,  # LHU   A3, 0xAC32 (T1)
    0x08058E56,  # J     0x80163958
    0xAFAA0010   # SW    T2, 0x0010 (SP)
]

crypt_crests_checker = [
    # Checks if the player is able to open the Villa crypt door from the inside by looking at the "crest inserted" flags
    # and the inventory Crest Half A and B counters. If they are, then will also determine which crests should be
    # subtracted from the inventory and have their flag be set.

    # Verify that we are able to open the door.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AB5B,  # LBU   T1, 0xAB5B (T0)
    0x910AAB5C,  # LBU   T2, 0xAB5C (T0)
    0x910BAA73,  # LBU   T3, 0xAA73 (T0)
    0x316C0080,  # ANDI  T4, T3, 0x0080
    0x316D0040,  # ANDI  T5, T3, 0x0040
    # Check to see if either the Crest A flag is set or we have Crest A. If neither are true, we can't open it.
    0x15800005,  # BNEZ  T4,     [forward 0x05]
    0x00000000,  # NOP
    0x15200003,  # BNEZ  T1,     [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x34020001,  # ORI   V0, R0, 0x0001
    # Check to see if either the Crest B flag is set or we have Crest B. If neither are true, we can't open it.
    0x15A00005,  # BNEZ  T5,     [forward 0x05]
    0x00000000,  # NOP
    0x15400003,  # BNEZ  T2,     [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x34020001,  # ORI   V0, R0, 0x0001
    # If we made it here, we can open the door. Before exiting the routine, however, see if there are crests we can be
    # "placing" from here.
    # If the Crest A flag is not set, subtract Crest A from the inventory and set its flag.
    0x15800004,  # BNEZ  T4,     [forward 0x04]
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0xA109AB5B,  # SB    T1, 0xAB5B (T0)
    0x356B0080,  # ORI   T3, T3, 0x0080
    0xA10BAA73,  # SB    T3, 0xAA73 (T0)
    # If the Crest B flag is not set, subtract Crest B from the inventory and set its flag.
    0x15A00004,  # BNEZ  T5,     [forward 0x04]
    0x254AFFFF,  # ADDIU T2, T2, 0xFFFF
    0xA10AAB5C,  # SB    T2, 0xAB5C (T0)
    0x356B0040,  # ORI   T3, T3, 0x0040
    0xA10BAA73,  # SB    T3, 0xAA73 (T0)
    0x03E00008,  # JR    RA
    0x34020000   # ORI   V0, R0, 0x0000
]

art_tower_knight_spawn_check = [
    # Checks if the player's current Z position is higher than -476.375f and, if it is, returns 0 to allow an actor
    # assigned to this check to spawn. Used for the Hell Knights in Art Tower's hallway between the two key doors to
    # ensure they don't lock the doors with the player behind Door 2 in our new spawn spot there.
    0x3C088019,  # LUI   T0, 0x8019
    0x8D0860E8,  # LW    T0, 0x60E8 (T0)
    0x3C09C3EE,  # LUI   T1, 0xC3EE
    0x35293000,  # ORI   T1, T1, 0x3000
    0x0128502A,  # SLT   T2, T1, T0
    0x24020000,  # ADDIU V0, R0, 0x0000
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x24020001,  # ADDIU V0, R0, 0x0001
    0x03E00008,  # JR    RA
    0x00000000
]

castle_sitting_henry_checker = [
    # Teleports Henry to his "all children rescued" cutscene during the "sitting to watch the castle crumble"
    # cutscene after beating Dracula instead of the usual castle crumbling sequence. This cutscene also opens with the
    # castle crumbling, so it feels more natural for him to go directly here.

    # Check the current character value for Henry. If true, switch the spawn point for the current map to 1
    # (for blue skies) and play his cutscene.
    0x3C0B801D,  # LUI   T3, 0x801D
    0x8568AB34,  # LH    T0, 0xAB34 (T3)
    0x34090003,  # ORI   T1, R0, 0x00003
    0x15090006,  # BNE   T0, T1, [forward 0x06]
    0x340A0031,  # ORI   T2, R0, 0x0031
    0xA56AAE8E,  # SH    T2, 0xAE8E (T3)
    0x340A001C,  # ORI   T2, R0, 0x001C
    0xA56AAE78,  # SH    T2, 0xAE78 (T3)
    0x340A0002,  # ORI   T2, R0, 0x0002
    0xA56AAE7A,  # SH    T2, 0xAE7A (T3)
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
]

castle_crumbling_cornell_checker = [
    # Teleports Cornell to his regular ending cutscene during the castle crumbling sequence after beating Centipede
    # Dracula.

    # Check the current character value for Cornell. If true, switch the scene to Cornell's ending forest and play
    # his cutscene.
    0x84482874,  # LH    T0, 0x2874 (V0)
    0x34090002,  # ORI   T1, R0, 0x00002
    0x15090005,  # BNE   T0, T1, [forward 0x05]
    0x34090003,  # ORI   T1, R0, 0x0003
    0x340A002D,  # ORI   T2, R0, 0x002D
    0xA44A2BB8,  # SH    T2, 0x2BB8 (V0)
    0x340A0030,  # ORI   T2, R0, 0x0030
    0xA44A2BCE,  # SH    T2, 0x2BCE (V0)
    0x0B8007A0,  # J     0x0E001E80
    0x00000000,  # NOP
]

malus_bad_end_cornell_henry_checker = [
    # Teleports Cornell and Henry to their respective "bad ending" cutscenes after Malus appears following Fake
    # Dracula's defeat.  Cornell doesn't have a bad ending normally, so we'll just give him Reinhardt's. Henry will
    # have his usual ending but with no children rescued.

    # Check the current character value for Cornell. If true, play his cutscene.
    0x340A0002,  # ORI   T2, R0, 0x0002
    0x14CA0003,  # BNE   A2, T2, [forward 0x03]
    0x340A0003,  # ORI   T2, R0, 0x0003
    0x0B8002FA,  # J     0x0E000BE8
    0xAC482BCC,  # SW    T0, 0x2BCC (V0)
    # Check the current character value for Henry. If true, play his cutscene.
    0x14CA0002,  # BNE   A2, T2, [forward 0x02]
    0x34090031,  # ORI   T1, R0, 0x0031
    0xAC492BCC,  # SW    T1, 0x2BCC (V0)
    0x0B8002FA,  # J     0x0E000BE8
    0x00000000   # NOP
]

dracula_ultimate_non_cornell_checker = [
    # Teleports all non-Cornell characters to their respective "good ending" cutscenes during the Dracula Ultimate
    # Defeated cutscene.

    # Check the current character value for Reinhardt. If true, switch the scene to Reinhardt/Carrie/Henry's endings and
    # play his cutscene.
    0x3C08801D,  # LUI   T0, 0x801D
    0x9509AB34,  # LHU   T1, 0xAB34 (T0)
    0x340A0000,  # ORI   T2, R0, 0x0000
    0x152A0004,  # BNE   T1, T2, [forward 0x04]
    0x340B001C,  # ORI   T3, R0, 0x001C
    0x340C0000,  # ORI   T4, R0, 0x0000
    0x1000000C,  # B             [forward 0x0C]
    0x340D002E,  # ORI   T5, R0, 0x002E
    # Check the current character value for Carrie. If true, switch the scene to Reinhardt/Carrie/Henry's endings and
    # play her cutscene.
    0x340A0001,  # ORI   T2, R0, 0x0001
    0x152A0004,  # BNE   T1, T2, [forward 0x04]
    0x340B001C,  # ORI   T3, R0, 0x001C
    0x340C0002,  # ORI   T4, R0, 0x0012
    0x10000006,  # B             [forward 0x06]
    0x340D002C,  # ORI   T5, R0, 0x002C
    # Check the current character value for Henry. If true, switch the scene to Reinhardt/Carrie/Henry's endings and
    # play his cutscene.
    0x340A0003,  # ORI   T2, R0, 0x0003
    0x152A0006,  # BNE   T1, T2, [forward 0x06]
    0x340B001C,  # ORI   T3, R0, 0x001C
    0x340C0002,  # ORI   T4, R0, 0x0002
    0x340D0031,  # ORI   T5, R0, 0x0031
    0xA50BAE78,  # SH    T3, 0xAE78 (T0)
    0xA50CAE7A,  # SH    T4, 0xAE7A (T0)
    0xA50DAE8E,  # SH    T5, 0xAE8E (T0)
    0x03E00008,  # JR    RA
    0x00000000   # NOP
]
