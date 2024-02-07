extras_unlocker = [
    # Sets the appropriate flags in the save file to unlock all Henry child rewards from the start.
    0x3C08801D,  # LUI   T0, 0x801D
    0x240900FF,  # ADDIU T1, 0x00FF
    0xA109AB19,  # SB    T1, 0xAB19 (T0)
    0x03E00008,  # JR    RA
    0xA109AB1A,  # SB    T1, 0xAB1A (T0)
]

ct_door_code = [
    0x3C0A8039,  # LUI   T2, 0x8039
    0x8D429BF8,  # LW    V0, 0x9BF8 (T2)
    0x01465021,  # ADDU  T2, T2, A2
    0x814A9C60,  # LB    T2, 0x9C60 (T2)
    0x00495824,  # AND   T3, V0, T1
    0x55600001,  # BNEZL T3,     [forward 0x01]
    0x27FF0010,  # ADDIU RA, RA, 0x0010
    0x03E00008   # JR    RA
]

stage_select_overwrite = [
    # Replacement for the "wipe world state" function when using the warp menu. Now it's the "Special1 jewel checker"
    # to see how many destinations can be selected on it with the current count.
    0x8FA60018,  # LW	 A2, 0x0018 (SP)
    0xA0606437,  # SB	 R0, 0x6437 (V1)
    0x10000029,  # B	         [forward 0x29]
    0x00000000,  # NOP
    0x3C0A8039,  # LUI	 T2, 0x8039
    0x254A9C4B,  # ADDIU T2, T2, 0x9C4B
    0x814B0000,  # LB	 T3, 0x0000 (T2)
    0x240C000A,  # ADDIU T4, R0, 0x000A
    0x016C001B,  # DIVU	 T3, T4
    0x00003012,  # MFLO	 A2
    0x24C60001,  # ADDIU A2, A2, 0x0001
    0x28CA0009,  # SLTI	 T2, A2, 0x0009
    0x51400001,  # BEQZL T2, 0x8012AC7C
    0x24060008,  # ADDIU A2, R0, 0x0008
    0x3C0A800D,  # LUI   T2, 0x800D
    0x914A5E20,  # LBU   T2, 0x5E20 (T2)
    0x314A0040,  # ANDI  T2, T2, 0x0040
    0x11400003,  # BEQZ  T2,     [forward 0x03]
    0x240BFFFE,  # ADDIU T3, R0, 0xFFFE
    0x3C0C8034,  # LUI   T4, 0x8034
    0xAD8B2084,  # SW    T3, 0x2084 (T4)
    0x03200008,  # JR    T9
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
]

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
    # Timer till next item at 00?
    0x3C0B801D,  # LUI	 T3, 0x801D
    0x916AAA4E,  # LBU	 T2, 0xAA4E (T3)
    0x012A4821,  # ADDU  T1, T1, T2
    0x11200006,  # BEQZ	 T1,     [forward 0x06]
    0x8D6CAC0C,  # LW    T4, 0xAC0C (T3)
    0x11400002,  # BEQZ  T2,     [forward 0x02]
    0x254AFFFF,  # ADDIU T2, T2, 0xFFFF
    0xA16AAA4E,  # SB	 T2, 0xAA4E (T3)
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    # Item-specific checks
    # Textbox in its "map text" state?
    0x1180FFFD,  # BEQZ  T4,     [backward 0x03]
    0x00000000,  # NOP
    0x8D8F005C,  # LW    T7, 0x005C (T4)
    0x11E0FFFA,  # BEQZ  T7,     [backward 0x06]
    0x00000000,  # NOP
    0x1DE0FFF8,  # BGTZ  T7,     [backward 0x08]
    0x00000000,  # NOP
    0x8DED0038,  # LW    T5, 0x0038 (T7)
    0x91AE0026,  # LBU   T6, 0x0026 (T5)
    # Non-multiworld item byte occupied?
    0x9164AA4C,  # LBU	 A0, 0xAA4C (T3)
    0x10800007,  # BEQZ	 A0,     [forward 0x07]
    0x00000000,  # NOP
    # If the textbox state is not 0, don't set the timer nor clear the buffer.
    0x15C00003,  # BNEZ  T6,     [forward 0x03]
    0x24090090,  # ADDIU T1, R0, 0x0090
    0xA169AA4E,  # SB	 T1, 0xAA4E (T3)
    0xA160AA4C,  # SB	 R0, 0xAA4C (T3)
    0x08021C1C,  # J     0x80087070
    0x00000000,  # NOP
    # Multiworld item byte occupied?
    0x9164AA4D,  # LBU	 A0, 0xAA4D (T3)
    0x1080000A,  # BEQZ	 A0,     [forward 0x0A]
    0x00000000,  # NOP
    # If the textbox state is not 0, don't set the timer, clear the buffer, nor increment the multiworld item index.
    0x15C00006,  # BNEZ  T6,     [forward 0x06]
    0x24090090,  # ADDIU T1, R0, 0x0090
    0xA169AA4E,  # SB	 T1, 0xAA4E (T3)
    0xA160AA4D,  # SB	 R0, 0xAA4D (T3)
    # Increment the multiworld received item index here
    0x956AABBE,  # LHU   T2, 0xABBE (T3)
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0xA56AABBE,  # SH    T2, 0xABBE (T3)
    0x08021C1C,  # J     0x80087070 TODO: Detect the surface below the player for sub-weapon dropping.
    0x00000000,  # NOP
    # DeathLink-specific checks
    # Received any DeathLinks?
    0x9164AA4F,  # LBU   A0, 0xAA4F (T3)
    0x14800002,  # BNEZ  A0,     [forward 0x02]
    # Is the player dead?
    0x9169AB84,  # LBU   T1, 0xAB84 (T3)
    0x03E00008,  # JR    RA TODO: Ice Traps
    0x312A0080,  # ANDI  T2, T1, 0x0080
    0x11400002,  # BEQZ  T2,     [forward 0x02]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x35290080,  # ORI   T1, T1, 0x0080
    0xA169AB84,  # SB    T1, 0xAB84 (T3)
    0x2484FFFF,  # ADDIU A0, A0, 0xFFFF
    0x24080001,  # ADDIU T0, R0, 0x0001
    0x03E00008,  # JR    RA
    0xA168AA4B,  # SB    T0, 0xAA4B (T3)
]

deathlink_nitro_edition = [
    # Alternative to the end of the above DeathLink-specific checks that kills the player with the Nitro explosion
    # instead of the normal death.
    0x91690043,  # LBU   T1, 0x0043 (T3)
    0x080FF076,  # J     0x803FC1D8
    0x3C088034,  # LUI   T0, 0x8034
    0x91082BFE,  # LBU   T0, 0x2BFE (T0)
    0x11000002,  # BEQZ  T0,     [forward 0x02]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x35290080,  # ORI   T1, T1, 0x0080
    0xA1690043,  # SB    T1, 0x0043 (T3)
    0x2484FFFF,  # ADDIU A0, A0, 0xFFFF
    0x24080001,  # ADDIU T0, R0, 0x0001
    0x03E00008,  # JR    RA
    0xA168FFFD,  # SB    T0, 0xFFFD (T3)
]

nitro_fall_killer = [
    # Custom code to force the instant fall death if at a high enough falling speed after getting killed by the Nitro
    # explosion, since the game doesn't run the checks for the fall death after getting hit by said explosion and could
    # result in a softlock when getting blown into an abyss.
    0x3C0C8035,  # LUI   T4, 0x8035
    0x918807E2,  # LBU   T0, 0x07E2 (T4)
    0x2409000C,  # ADDIU T1, R0, 0x000C
    0x15090006,  # BNE   T0, T1, [forward 0x06]
    0x3C098035,  # LUI   T1, 0x8035
    0x91290810,  # LBU   T1, 0x0810 (T1)
    0x240A00C1,  # ADDIU T2, R0, 0x00C1
    0x152A0002,  # BNE   T1, T2, [forward 0x02]
    0x240B0001,  # ADDIU T3, R0, 0x0001
    0xA18B07E2,  # SB    T3, 0x07E2 (T4)
    0x03E00008   # JR    RA
]

warp_menu_opener = [
    # Enables warping by pausing while holding Z + R. Un-sets the Henry escort begins flag if you warp during it.
    # TODO: Restrict this to not work when not in a boss fight, the castle crumbling sequence following Fake Dracula, or Renon's arena (in the few seconds after his health bar vanishes).
    0x3C08800F,  # LUI   T0, 0x800F
    0x9508FBA0,  # LHU   T0, 0xFBA0 (T0)
    0x24093010,  # ADDIU T1, R0, 0x3010
    0x15090013,  # BNE   T0, T1, [forward 0x13]
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AB47,  # LBU   T1, 0xAB47 (T0)
    0x11200006,  # BEQZ  T1,     [forward 0x06]
    0x910AAA48,  # LBU   T2, 0xAA48 (T0)
    0x15400004,  # BNEZ  T2,     [forward 0x04]
    0x3C0B0005,  # LUI   T3, 0x0005
    0x256B0004,  # ADDIU T3, T3, 0x0004
    0x10000003,  # B             [forward 0x03]
    0x240C0001,  # ADDIU T4, R0, 0x0001
    0x3C0B0002,  # LUI   T3, 0x0002
    0x240C0000,  # ADDIU T4, R0, 0x0000
    0xAD0BAE78,  # SW    T3, 0xAE78 (T0)
    0x910DAA72,  # LBU   T5, 0xAA72 (T0)
    0x31AE0008,  # ANDI  T6, T5, 0x0008
    0x15C00002,  # BNEZ  T6,     [forward 0x02]
    0x31AE00EF,  # ANDI  T6, T5, 0x00EF
    0xA10EAA72,  # SB    T6, 0xAA72 (T0)
    0x03E00008,  # JR    RA
    0xA10CAA48,  # SB    T4, 0xAA48 (T0)
    0x03E00008,  # JR    RA
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

give_powerup_stopper = [
    # Extension to "give PowerUp" function to not increase the player's PowerUp count beyond 2
    0x240D0002,  # ADDIU T5, R0, 0x0002
    0x556D0001,  # BNEL  T3, T5, [forward 0x01]
    0xA46C6234,  # SH    T4, 0x6234 (V1)
    0x0804F0BF   # J     0x8013C2FC
]

npc_item_hack = [
    # Hack to make NPC items show item textboxes when received.
    0x00180024,  # Item values
    0x001B001F,
    0x00200000,
    0x00000000,
    0x3C088040,  # LUI   T0, 0x8040
    0x00044840,  # SLL   T1, A0, 1
    0x01094021,  # ADDIU T0, T0, T1
    0x950AC6F0,  # LHU   T2, 0xC6F0 (T0)
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
    0x03E00008,  # JR    RA
]

overlay_modifiers = [
    # Whenever a compressed overlay gets decompressed and mapped in the 0F or 0E domains, this thing will check the
    # number ID in the T0 register to tell which one it is and overwrite some instructions in it on-the-fly accordingly
    # to said number before it runs. Confirmed to NOT be a foolproof solution on console and Simple64; the instructions
    # may not be properly overwritten on the first execution of the overlay.

    # Prevent being able to throw Nitro into the Hazardous Waste Disposals
    0x3C0A2402,  # LUI   T2, 0x2402
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0x24090023,  # ADDIU T1, R0, 0x0023
    0x15090003,  # BNE   T0, T1, [forward 0x03]
    0x00000000,  # NOP
    0x03200008,  # JR    T9
    0xAF2A01D4,  # SW    T2, 0x01D4 (T9)
    # Make it so nothing can be taken from the Nitro or Mandragora shelves through the textboxes
    0x24090022,  # ADDIU T1, R0, 0x0022
    0x11090002,  # BEQ   T0, T1, [forward 0x02]
    0x24090021,  # ADDIU T1, R0, 0x0021
    0x15090003,  # BNE   T0, T1, [forward 0x03]
    0x254AFFFF,  # ADDIU T2, T2, 0xFFFF
    0x03200008,  # JR    T9
    0xAF2A0194,  # SW    T2, 0x0194 (T9)
    # Fix to allow placing both bomb components at a cracked wall at once while having multiple copies of each, and
    # prevent placing them at the downstairs crack altogether until the seal is removed. Also enables placing both in
    # one interaction.
    0x24090024,  # ADDIU T1, R0, 0x0024
    0x15090012,  # BNE   T0, T1, [forward 0x12]
    0x240A0040,  # ADDIU T2, R0, 0x0040
    0x240BC338,  # ADDIU T3, R0, 0xC338
    0x240CC3D4,  # ADDIU T4, R0, 0xC3D4
    0x240DC38C,  # ADDIU T5, R0, 0xC38C
    0xA32A030F,  # SB    T2, 0x030F (T9)
    0xA72B0312,  # SH    T3, 0x0312 (T9)
    0xA32A033F,  # SB    T2, 0x033F (T9)
    0xA72B0342,  # SH    T3, 0x0342 (T9)
    0xA32A03E3,  # SB    T2, 0x03E3 (T9)
    0xA72C03E6,  # SH    T4, 0x03E6 (T9)
    0xA32A039F,  # SB    T2, 0x039F (T9)
    0xA72D03A2,  # SH    T5, 0x03A2 (T9)
    0xA32A03CB,  # SB    T2, 0x03CB (T9)
    0xA72D03CE,  # SH    T5, 0x03CE (T9)
    0xA32A05CF,  # SB    T2, 0x05CF (T9)
    0x240EE074,  # ADDIU T6, R0, 0xE074
    0xA72E05D2,  # SH    T6, 0x05D2 (T9)
    0x03200008,  # JR    T9
    # Disable the costume and Hard Mode flag checks so that pressing Up on the Player Select screen will always allow
    # the characters' alternate costumes to be used as well as Hard Mode being selectable without creating save data.
    0x2409012E,  # ADDIU T1, R0, 0x012E
    0x1509000A,  # BNE   T0, T1, [forward 0x0A]
    0x3C0A3C0B,  # LUI   T2, 0x3C0B
    0x254A8000,  # ADDIU T2, T2, 0x8000
    0x240B240E,  # ADDIU T3, R0, 0x240E
    0x240C240F,  # ADDIU T4, R0, 0x240F
    0x240D0024,  # ADDIU T5, R0, 0x0024
    0xAF2A0C78,  # SW    T2, 0x0C78 (T9)
    0xA72B0CA0,  # SH    T3, 0x0CA0 (T9)
    0xA72C0CDC,  # SH    T4, 0x0CDC (T9)
    0xA32D0168,  # SB    T5, 0x0024 (T9)
    0x03200008,  # JR    T9
    # Overwrite instructions in the Forest end cutscene script to store a spawn position ID instead of a cutscene ID.
    0x2409002E,  # ADDIU T1, R0, 0x002E
    0x15090005,  # BNE   T0, T1, [forward 0x05]
    0x3C0AA058,  # LUI   T2, 0xA058
    0x254A642B,  # ADDIU T2, T2, 0x642B
    0xAF2A0D88,  # SW    T2, 0x0D88 (T9)
    0xAF200D98,  # SW    R0, 0x0D98 (T9)
    0x03200008,  # JR    T9
    # Disable the rapid flashing effect in the CC planetarium cutscene to ensure it won't trigger seizures.
    0x2409003E,  # ADDIU T1, R0, 0x003E
    0x1509000C,  # BNE   T0, T1, [forward 0x0C]
    0x00000000,  # NOP
    0xAF200C5C,  # SW    R0, 0x0C5C
    0xAF200CD0,  # SW    R0, 0x0CD0
    0xAF200C64,  # SW    R0, 0x0C64
    0xAF200C74,  # SW    R0, 0x0C74
    0xAF200C80,  # SW    R0, 0x0C80
    0xAF200C88,  # SW    R0, 0x0C88
    0xAF200C90,  # SW    R0, 0x0C90
    0xAF200C9C,  # SW    R0, 0x0C9C
    0xAF200CB4,  # SW    R0, 0x0CB4
    0xAF200CC8,  # SW    R0, 0x0CC8
    0x03200008,  # JR    T9
    0x24090134,  # ADDIU T1, R0, 0x0134
    0x15090005,  # BNE   T0, T1, [forward 0x05]
    0x340B8040,  # ORI   T3, R0, 0x8040
    0x340CDD20,  # ORI   T4, R0, 0xDD20
    0xA72B1D1E,  # SH    T3, 0x1D1E (T9)
    0xA72C1D22,  # SH    T4, 0x1D22 (T9)
    0x03200008,  # JR    T9
    # Make the Ice Trap model check branch properly
    0x24090125,  # ADDIU T1, R0, 0x0125
    0x15090003,  # BNE   T0, T1, [forward 0x03]
    0x3C0B3C19,  # LUI   T3, 0x3C19
    0x356B803F,  # ORI   T3, T3, 0x803F
    0xAF2B04D0,  # SW    T3, 0x04D0 (T9)
    0x03200008   # JR    T9
]

double_component_checker = [
    # When checking to see if a bomb component can be placed at a cracked wall, this will run if the code lands at the
    # "no need to set 2" outcome to see if the other can be set.

    # Mandragora checker
    0x10400007,  # BEQZ  V0,     [forward 0x07]
    0x3C0A8039,  # LUI   T2, 0x8039
    0x31098000,  # ANDI  T1, T0, 0x8000
    0x15200008,  # BNEZ  T1,     [forward 0x08]
    0x91499C5D,  # LBU   T1, 0x9C5D (T2)
    0x11200006,  # BEQZ  T1, 0x80183938
    0x00000000,  # NOP
    0x10000007,  # B     [forward 0x07]
    0x31E90100,  # ANDI  T1, T7, 0x0100
    0x15200002,  # BNEZ  T1,     [forward 0x02]
    0x91499C5D,  # LBU   T1, 0x9C5D (T2)
    0x15200003,  # BNEZ  T1,     [forward 0x03]
    0x3C198000,  # LUI   T9, 0x8000
    0x27391590,  # ADDIU T9, T9, 0x1590
    0x03200008,  # JR    T9
    0x24090001,  # ADDIU T1, R0, 0x0001
    0xA4E9004C,  # SH    T1, 0x004C (A3)
    0x3C190E00,  # LUI   T9, 0x0E00
    0x273903E0,  # ADDIU T9, T9, 0x03E0
    0x03200008,  # JR    T9
    0x00000000,  # NOP
    # Nitro checker
    0x10400007,  # BEQZ  V0,     [forward 0x07]
    0x3C0A8039,  # LUI   T2, 0x8039
    0x31694000,  # ANDI  T1, T3, 0x4000
    0x15200008,  # BNEZ  T1,     [forward 0x08]
    0x91499C5C,  # LBU   T1, 0x9C5C
    0x11200006,  # BEQZ  T1,     [forward 0x06]
    0x00000000,  # NOP
    0x1000FFF4,  # B     [backward 0x0B]
    0x914F9C18,  # LBU   T7, 0x9C18 (T2)
    0x31E90002,  # ANDI  T1, T7, 0x0002
    0x1520FFEC,  # BNEZ  T1,     [backward 0x13]
    0x91499C5C,  # LBU   T1, 0x9C5C (T2)
    0x1520FFEF,  # BNEZ  T1,     [backward 0x15]
    0x00000000,  # NOP
    0x1000FFE8,  # B             [backward 0x17]
    0x00000000,  # NOP
]

downstairs_seal_checker = [
    # This will run specifically for the downstairs crack to see if the seal has been removed before then deciding to
    # let the player set the bomb components or not. An anti-dick measure, since there is a limited number of each
    # component per world.
    0x14400004,  # BNEZ  V0,     [forward 0x04]
    0x3C0A8039,  # LUI   T2, 0x8039
    0x914A9C18,  # LBU   T2, 0x9C18 (T2)
    0x314A0001,  # ANDI  T2, T2, 0x0001
    0x11400003,  # BEQZ  T2,     [forward 0x03]
    0x3C198000,  # LUI   T9, 0x8000
    0x27391448,  # ADDIU T9, T9, 0x1448
    0x03200008,  # JR    T9
    0x3C190E00,  # LUI   T9, 0x0E00
    0x273902B4,  # ADDIU T9, T9, 0x02B4
    0x03200008,  # JR    T9
    0x00000000,  # NOP
]

renon_cutscene_checker = [
    # Prevents Renon's departure/pre-fight cutscene from playing if the player is either in the escape sequence or both
    # did not spend the required 30K to fight him and lacks the required Special2s to fight Dracula.
    0x15810002,  # BNE   T4, AT, [forward 0x02]
    0x00000000,  # NOP
    0x08049EB3,  # J     0x80127ACC
    0x24090016,  # ADDIU T1, R0, 0x0016
    0x11C90002,  # BEQ   T6, T1, [forward 0x02]
    0x00000000,  # NOP
    0x08049ECA,  # J     0x80127B28
    0x24190000,  # ADDIU T9, R0, 0x0000
    0x8C696208,  # LW    T1, 0x6208 (V1)
    0x292A7531,  # SLTI  T2, T1, 0x7531
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x24190001,  # ADDIU T9, R0, 0x0001
    0x3C0B8013,  # LUI   T3, 0x8013
    0x916BAC9F,  # LBU   T3, 0xAC9F (T3)
    0x906C6194,  # LBU   T4, 0x6194 (V1)
    0x018B502A,  # SLT   T2, T4, T3
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x24190001,  # ADDIU T9, R0, 0x0001
    0x90696142,  # LBU   T1, 0x6142 (V1)
    0x31290002,  # ANDI  T1, T1, 0x0002
    0x55200001,  # BNEZL T1,     [forward 0x01]
    0x24190000,  # ADDIU T9, R0, 0x0000
    0x17200003,  # BNEZ  T9,     [forward 0x03]
    0x00000000,  # NOP
    0x08049ECC,  # J     0x80127B30
    0x00000000,  # NOP
    0x08049ECA   # J     0x80127B28
]

renon_cutscene_checker_jr = [
    # Like renon_cutscene_checker, but without the checks for the Special2 and spent money counters. Inserted instead if
    # the player chooses to guarantee or disable the Renon fight on their YAML.
    0x15810002,  # BNE   T4, AT, [forward 0x02]
    0x00000000,  # NOP
    0x08049EB3,  # J     0x80127ACC
    0x24090016,  # ADDIU T1, R0, 0x0016
    0x11C90002,  # BEQ   T6, T1, [forward 0x02]
    0x00000000,  # NOP
    0x08049ECA,  # J     0x80127B28
    0x24190001,  # ADDIU T9, R0, 0x0001
    0x90696142,  # LBU   T1, 0x6142 (V1)
    0x31290002,  # ANDI  T1, T1, 0x0002
    0x55200001,  # BNEZL T1,     [forward 0x01]
    0x24190000,  # ADDIU T9, R0, 0x0000
    0x17200003,  # BNEZ  T9,     [forward 0x03]
    0x00000000,  # NOP
    0x08049ECC,  # J     0x80127B30
    0x00000000,  # NOP
    0x08049ECA   # J     0x80127B28
]

ck_door_music_player = [
    # Plays Castle Keep's song if you spawn in front of Dracula's door (teleporting via the warp menu) and haven't
    # started the escape sequence yet.
    0x17010002,  # BNE   T8, AT, [forward 0x02]
    0x00000000,  # NOP
    0x08063DF9,  # J     0x8018F7E4
    0x240A0000,  # ADDIU T2, R0, 0x0000
    0x3C088039,  # LUI   T0, 0x8039
    0x91089BFA,  # LBU   T0, 0x9BFA (T0)
    0x31080002,  # ANDI  T0, T0, 0x0002
    0x51090001,  # BEQL  T0, T1, [forward 0x01]
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0x24080003,  # ADDIU T0, R0, 0x0003
    0x51180001,  # BEQL  T0, T8, [forward 0x01]
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0x240B0002,  # ADDIU T3, R0, 0x0002
    0x114B0002,  # BEQ   T2, T3, [forward 0x02]
    0x00000000,  # NOP
    0x08063DFD,  # J     0x8018F7F4
    0x00000000,  # NOP
    0x08063DF9   # J     0x8018F7E4
]

dracula_door_text_redirector = [
    # Switches the standard pointer to the map text with one to a custom message for Dracula's chamber door if the
    # current scene is Castle Keep exterior (Scene 0x14).
    0x3C088039,  # LUI   T0, 0x8039
    0x91089EE1,  # LBU   T0, 0x9EE1 (T0)
    0x24090014,  # ADDIU T1, R0, 0x0014
    0x15090006,  # BNE   T0, T1, [forward 0x06]
    0x3C088014,  # LUI   T0, 0x8014
    0x2508B9F4,  # ADDIU T0, T0, 0xB9F4
    0x151F0003,  # BNE   T0, RA, [forward 0x03]
    0x00000000,  # NOP
    0x3C028040,  # LUI   V0, 0x8040
    0x2442CC48,  # ADDIU V0, V0, 0xCC48
    0x03E00008   # JR    RA
]

coffin_time_checker = [
    # When entering the Villa coffin, this will check to see whether it's day or night and send you to either the Tunnel
    # or Underground Waterway level slot accordingly regardless of which character you are
    0x28490006,  # SLTI  T1, V0, 0x0006
    0x15200005,  # BNEZ  T1,     [forward 0x05]
    0x28490012,  # SLTI  T1, V0, 0x0012
    0x11200003,  # BEQZ  T1,     [forward 0x03]
    0x00000000,  # NOP
    0x08055AEB,  # J     0x80156BAC
    0x00000000,  # NOP
    0x08055AED   # J     0x80156BB4
]

boss_special2_giver = [
    # Enables the rewarding of Special2s upon the vanishing of a boss's health bar when defeating it.

    # Also sets a flag in the case of the Castle Wall White Dragons' health bar going away. Their defeat flag in vanilla
    # is tied to hitting the lever after killing them, so this alternate flag is used to track them for the "All Bosses"
    # goal in the event someone kills them and then warps out opting to not be a Konami pachinko champ.
    0x3C118035,  # LUI   S1, 0x8035
    0x962DF834,  # LHU   T5, 0xF834 (S1)
    0x240E3F73,  # ADDIU T6, R0, 0x3F73
    0x15AE0012,  # BNE   T5, T6, [forward 0x12]
    0x3C118039,  # LUI   S1, 0x8039
    0x922D9EE1,  # LBU   T5, 0x9EE1 (S1)
    0x240E0013,  # ADDIU T6, R0, 0x0013
    0x11AE000E,  # BEQ   T5, T6, [forward 0x0E]
    0x922F9BFA,  # LBU   T7, 0x9BFA (S1)
    0x31EF0001,  # ANDI  T7, T7, 0x0001
    0x15E0000B,  # BNEZ  T7,     [forward 0x0B]
    0x240E0002,  # ADDIU T6, R0, 0x0002
    0x15AE0006,  # BNE   T5, T6, [forward 0x06]
    0x00000000,  # NOP
    0x862F9BF4,  # LH    T7, 0x9BF4 (S1)
    0x31ED0080,  # ANDI  T5, T7, 0x0080
    0x15A00005,  # BNEZ  T5,     [forward 0x05]
    0x35EF0080,  # ORI   T7, T7, 0x0080
    0xA62F9BF4,  # SH    T7, 0x9BF4 (S1)
    0x240D0005,  # ADDIU T5, R0, 0x0005
    0xA22D9BDF,  # SB    T5, 0x9BDF (S1)
    0xA22D9BE0,  # SB    T5, 0x9BE0 (S1)
    0x03E00008   # JR    RA
]

boss_goal_checker = [
    # Checks each boss flag to see if every boss with a health meter has been defeated and puts 0x0004 in V0 to
    # disallow opening Dracula's door if not all have been.
    0x3C0A8039,  # LUI   T2, 0x8039
    0x954B9BF4,  # LHU   T3, 0x9BF4 (T2)
    0x316D0BA0,  # ANDI  T5, T3, 0x0BA0
    0x914B9BFB,  # LBU   T3, 0x9BFB (T2)
    0x000B6182,  # SRL   T4, T3, 6
    0x11800010,  # BEQZ  T4,     [forward 0x10]
    0x240C00C0,  # ADDIU T4, R0, 0x00C0
    0x01AC6821,  # ADDU  T5, T5, T4
    0x914B9BFD,  # LBU   T3, 0x9BFD (T2)
    0x316C0020,  # ANDI  T4, T3, 0x0020
    0x01AC6821,  # ADDU  T5, T5, T4
    0x914B9BFE,  # LBU   T3, 0x9BFE (T2)
    0x316C0010,  # ANDI  T4, T3, 0x0010
    0x01AC6821,  # ADDU  T5, T5, T4
    0x914B9C18,  # LBU   T3, 0x9C18 (T2)
    0x316C0010,  # ANDI  T4, T3, 0x0010
    0x01AC6821,  # ADDU  T5, T5, T4
    0x914B9C1B,  # LBU   T3, 0x9C1B (T2)
    0x000B6102,  # SRL   T4, T3, 4
    0x11800005,  # BEQZ  T4,     [forward 0x05]
    0x240C0050,  # ADDIU T4, R0, 0x0050
    0x01AC6821,  # ADDU  T5, T5, T4
    0x240E0CF0,  # ADDIU T6, R0, 0x0CF0
    0x55CD0001,  # BNEL  T6, T5, [forward 0x01]
    0x24020004,  # ADDIU V0, R0, 0x0004
    0x03E00008   # JR    RA
]

special_goal_checker = [
    # Checks the Special2 counter to see if the specified threshold has been reached and puts 0x0001 in V0 to disallow
    # opening Dracula's door if it hasn't been.
    0x3C0A8039,  # LUI   T2, 0x8039
    0x914B9C4C,  # LBU   T3, 0x9C4C (T2)
    0x296A001E,  # SLTI  T2, T3, 0x001E
    0x55400001,  # BNEZL T2, 0x8012AC8C
    0x24020001,  # ADDIU V0, R0, 0x0001
    0x03E00008   # JR    RA
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

deathlink_counter_decrementer = [
    # Decrements the DeathLink counter if it's above zero upon loading a previous state. Checking this number will be
    # how the client will tell if a player's cause of death was something in-game or a DeathLink (and send a DeathLink
    # to the server if it was the former). Also resets the remote item values to 00 so the player's received items don't
    # get mucked up in-game.
    0x3C088039,  # LUI   T0, 0x8039
    0x91099BE3,  # LBU   T1, 0x9BE3 (T0)
    0x11200002,  # BEQZ  T1, 0x803FC154
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0xA1099BE3,  # SB    T1, 0x9BE3
    0x240900FF,  # ADDIU T1, R0, 0x00FF
    0xA1099BE0,  # SB    T1, 0x9BE0 (T0)
    0xA1009BDF,  # SB	 R0, 0x9BDF (T0)
    0xA1009BE1,  # SB	 R0, 0x9BE1 (T0)
    0x91099BDE,  # LBU   T1, 0x9BDE (T0)
    0x55200001,  # BNEZL T1,     [forward 0x01]
    0x24090000,  # ADDIU T1, R0, 0x0000
    0xA1099BDE,  # SB    T1, 0x9BDE (T0)
    0x91099C24,  # LBU   T1, 0x9C24 (T0)
    0x312A0080,  # ANDI  T2, T1, 0x0080
    0x55400001,  # BNEZL T2,     [forward 0x01]
    0x3129007F,  # ANDI  T1, T1, 0x007F
    0x03E00008,  # JR    RA
    0xA1099C24   # SB    T1, 0x9C24 (T0)
]

load_clearer = [
    # Un-sets the Death status bitflag when loading either a save or stage beginning state and sets health to full if
    # it's empty, as well as clearing the multiworld buffers so things don't get mucked up on that front. Also updates
    # the "Continue" menu cursor depending on which state was loaded.
    0x3C08801D,  # LUI   T0, 0x801D
    0xFD00AA48,  # SD    R0, 0xAA48 (T0)
    0xA104AA31,  # SB    A0, 0xAA31 (T0)
    0x9109ABA4,  # LBU   T1, 0xABA4 (T0)
    0x3129007F,  # ANDI  T1, T1, 0x007F
    0xA109ABA4,  # SB    T1, 0xABA4 (T0)
    0x950AAB42,  # LHU   T2, 0xAB42 (T0)
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x240A2710,  # ADDIU T2, R0, 0x2710
    0x03E00008,  # JR    RA
    0xA50AAB42   # SH    T2, 0xAB42 (T0)
]

elevator_flag_checker = [
    # Prevents the top elevator in Castle Center from activating if the bottom elevator switch is not turned on.
    0x3C088039,  # LUI   T0, 0x8039
    0x91089C07,  # LBU   T0, 0x9C07 (T0)
    0x31080002,  # ANDI  T0, T0, 0x0002
    0x15000002,  # BNEZ  T0,     [forward 0x02]
    0x848E004C,  # LH    T6, 0x004C (A0)
    0x240E0000,  # ADDIU T6, R0, 0x0000
    0x03E00008   # JR    RA
]

crystal_special2_giver = [
    # Gives a Special2 upon activating the big crystal in CC basement.
    0x3C098039,  # LUI   T1, 0x8039
    0x24190005,  # ADDIU T9, R0, 0x0005
    0xA1399BDF,  # SB    T9, 0x9BDF (T1)
    0x03E00008,  # JR    RA
    0x3C198000   # LUI   T9, 0x8000
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

item_appearance_switcher = [
    # Determines an item's model appearance by checking to see if a different item appearance ID was written in a
    # specific spot in the actor's data; if one wasn't, then the appearance value will be grabbed from the item's entry
    # in the item property table like normal instead.
    0x92080044,  # LBU   T0, 0x0044 (S0)
    0x55000001,  # BNEZL T0, T1, [forward 0x01]
    0x01002025,  # OR    A0, T0, R0
    0x08023D78,  # J     0x8008F5E0
]

item_model_visibility_switcher = [
    # If 80 is written one byte ahead of the appearance switch value in the item's actor data, parse 0C00 to the
    # function that checks if an item should be invisible or not. Otherwise, grab that setting from the item property
    # table like normal.
    0x920B0041,  # LBU   T3, 0x0041 (S0)
    0x316E0080,  # ANDI  T6, T3, 0x0080
    0x11C00003,  # BEQZ  T6,     [forward 0x03]
    0x240D0C00,  # ADDIU T5, R0, 0x0C00
    0x03E00008,  # JR    RA
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x958D0004   # LHU   T5, 0x0004 (T4)
]

item_shine_visibility_switcher = [
    # Same as the above, but for item shines instead of the model.
    0x920B0041,  # LBU   T3, 0x0041 (S0)
    0x31690080,  # ANDI  T1, T3, 0x0080
    0x11200003,  # BEQZ  T1,     [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0x240C0C00,  # ADDIU T4, R0, 0x0C00
    0x03E00008,  # JR    RA
    0x958CA908   # LHU   T4, 0xA908 (T4)
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
    # When picking up a sub-weapon this will check to see if it's different from the one the player already had (if they
    # did have one) and jump to prev_subweapon_dropper, which will spawn a subweapon actor of what they had before
    # directly behind them.
    0x322F3031,  # Previous sub-weapon bytes
    0x10A00009,  # BEQZ  A1,     [forward 0x09]
    0x00000000,  # NOP
    0x10AD0007,  # BEQ   A1, T5, [forward 0x07]
    0x3C088040,  # LUI   T0, 0x8040
    0x01054021,  # ADDU  T0, T0, A1
    0x0C0FF418,  # JAL   0x803FD060
    0x9104CFC3,  # LBU   A0, 0xCFC3 (T0)
    0x2484FF9C,  # ADDIU A0, A0, 0xFF9C
    0x3C088039,  # LUI   T0, 0x8039
    0xAD049BD4,  # SW    A0, 0x9BD4 (T0)
    0x0804F0BF,  # J     0x8013C2FC
    0x24020001   # ADDIU V0, R0, 0x0001
]

prev_subweapon_fall_checker = [
    # Checks to see if a pointer to a previous sub-weapon drop actor spawned by prev_subweapon_dropper is in 80389BD4
    # and calls the function in prev_subweapon_dropper to lower the weapon closer to the ground on the next frame if a
    # pointer exists and its actor ID is 0x0027. Once it hits the ground or despawns, the connection to the actor will
    # be severed by 0-ing out the pointer.
    0x3C088039,  # LUI   T0, 0x8039
    0x8D049BD4,  # LW    A0, 0x9BD4 (T0)
    0x10800008,  # BEQZ  A0,     [forward 0x08]
    0x00000000,  # NOP
    0x84890000,  # LH    T1, 0x0000 (A0)
    0x240A0027,  # ADDIU T2, R0, 0x0027
    0x152A0004,  # BNE   T1, T2, [forward 0x04]
    0x00000000,  # NOP
    0x0C0FF452,  # JAL   0x803FD148
    0x00000000,  # NOP
    0x50400001,  # BEQZL V0,     [forward 0x01]
    0xAD009BD4,  # SW    R0, 0x9BD4 (T0)
    0x080FF40F   # J     0x803FD03C
]

prev_subweapon_dropper = [
    # Spawns a pickup actor of the sub-weapon the player had before picking up a new one behind them at their current
    # position like in other CVs. This will enable them to pick it back up again if they still want it.
    # Courtesy of Moisés; see derp.c in the src folder for the C source code.
    0x27BDFFC8,
    0xAFBF001C,
    0xAFA40038,
    0xAFB00018,
    0x0C0006B4,
    0x2404016C,
    0x00402025,
    0x0C000660,
    0x24050027,
    0x1040002B,
    0x00408025,
    0x3C048035,
    0x848409DE,
    0x00042023,
    0x0C0230D4,
    0x3084FFFF,
    0x44822000,
    0x3C018040,
    0xC428D370,
    0x468021A0,
    0x3C048035,
    0x848409DE,
    0x00042023,
    0x46083282,
    0x3084FFFF,
    0x0C01FFAC,
    0xE7AA0024,
    0x44828000,
    0x3C018040,
    0xC424D374,
    0x468084A0,
    0x27A40024,
    0x00802825,
    0x3C064100,
    0x46049182,
    0x0C004562,
    0xE7A6002C,
    0x3C058035,
    0x24A509D0,
    0x26040064,
    0x0C004530,
    0x27A60024,
    0x3C018035,
    0xC42809D4,
    0x3C0140A0,
    0x44815000,
    0x00000000,
    0x460A4400,
    0xE6100068,
    0xC6120068,
    0xE6120034,
    0x8FAE0038,
    0xA60E0038,
    0x8FBF001C,
    0x8FB00018,
    0x27BD0038,
    0x03E00008,
    0x00000000,
    0x3C068040,
    0x24C6D368,
    0x90CE0000,
    0x27BDFFE8,
    0xAFBF0014,
    0x15C00027,
    0x00802825,
    0x240400DB,
    0x0C0006B4,
    0xAFA50018,
    0x44802000,
    0x3C038040,
    0x2463D364,
    0x3C068040,
    0x24C6D368,
    0x8FA50018,
    0x1040000A,
    0xE4640000,
    0x8C4F0024,
    0x3C013F80,
    0x44814000,
    0xC5E60044,
    0xC4700000,
    0x3C018040,
    0x46083280,
    0x460A8480,
    0xE432D364,
    0x94A20038,
    0x2401000F,
    0x24180001,
    0x10410006,
    0x24010010,
    0x10410004,
    0x2401002F,
    0x10410002,
    0x24010030,
    0x14410005,
    0x3C014040,
    0x44813000,
    0xC4640000,
    0x46062200,
    0xE4680000,
    0xA0D80000,
    0x10000023,
    0x24020001,
    0x3C038040,
    0x2463D364,
    0xC4600000,
    0xC4A20068,
    0x3C038039,
    0x24639BD0,
    0x4600103E,
    0x00001025,
    0x45000006,
    0x00000000,
    0x44808000,
    0xE4A00068,
    0xA0C00000,
    0x10000014,
    0xE4700000,
    0x3C038039,
    0x24639BD0,
    0x3C018019,
    0xC42AC870,
    0xC4600000,
    0x460A003C,
    0x00000000,
    0x45000006,
    0x3C018019,
    0xC432C878,
    0x46120100,
    0xE4640000,
    0xC4600000,
    0xC4A20068,
    0x46001181,
    0x24020001,
    0xE4A60068,
    0xC4A80068,
    0xE4A80034,
    0x8FBF0014,
    0x27BD0018,
    0x03E00008,
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x0000001B,
    0x060048E0,
    0x40000000,
    0x06AEFFD3,
    0x06004B30,
    0x40000000,
    0x00000000,
    0x06004CB8,
    0x0000031A,
    0x002C0000,
    0x060059B8,
    0x40000248,
    0xFFB50186,
    0x06005B68,
    0xC00001DF,
    0x00000000,
    0x06005C88,
    0x80000149,
    0x00000000,
    0x06005DC0,
    0xC0000248,
    0xFFB5FE7B,
    0x06005F70,
    0xC00001E0,
    0x00000000,
    0x06006090,
    0x8000014A,
    0x00000000,
    0x06007D28,
    0x4000010E,
    0xFFF100A5,
    0x06007F60,
    0xC0000275,
    0x00000000,
    0x06008208,
    0x800002B2,
    0x00000000,
    0x060083B0,
    0xC000010D,
    0xFFF2FF5C,
    0x060085E8,
    0xC0000275,
    0x00000000,
    0x06008890,
    0x800002B2,
    0x00000000,
    0x3D4CCCCD,
    0x3FC00000,
    0x00000000,
    0x00000000,
    0x00000000,
    0x00000000,
    0xB8000100,
    0xB8000100,
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
    0x9109AE79,  # LBU   T1, 0xAE79 (T0)
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
    # start. The initial Countdown numbers begin here.
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
    # start_inventory begins here
    0x3C08801D,  # LUI   T0, 0x801D
    0x24090000,  # ADDIU T1, R0, 0x0000  <- Starting jewels
    0xA109AB45,  # SB    T1, 0xAB45
    0x3C0A8040,  # LUI   T2, 0x8040
    0x8D4BC7EC,  # LW    T3, 0xC7EC (T2) <- Starting money
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
    0x240D002A,  # ADDIU T5, R0, 0x002A
    0x11AC0007,  # BEQ   T5, T4, [forward 0x07]
    0x3C0A8040,  # LUI   T2, 0x8040
    0x014C5021,  # ADDU  T2, T2, T4
    0x814AC7A0,  # LB    T2, 0xC7A0      <- Starting inventory items
    0x25080001,  # ADDIU T0, T0, 0x0001
    0xA10AAB46,  # SB    T2, 0xAB46 (T0)
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
    0x3C088013,  # LUI   A0, 0x8013
    0x9108AC9F,  # LBU   T0, 0xAC57 (T0)
    0x3C098039,  # LUI   T1, 0x8039
    0x91299C4C,  # LBU   T1, 0x9C4B (T1)
    0x15090003,  # BNE   T0, T1, [forward 0x03]
    0x00000000,  # NOP
    0x0C004FAB,  # JAL   0x80013EAC
    0x24040162,  # ADDIU A0, R0, 0x0162
    0x0804F0BF,  # J     0x8013C2FC
    0x00000000,  # NOP
    0x3C088013,  # LUI   T0, 0x8013
    0x9108AC57,  # LBU   T0, 0xAC57 (T0)
    0x3C098039,  # LUI   T1, 0x8039
    0x91299C4B,  # LBU   T1, 0x9C4B (T1)
    0x0128001B,  # DIVU  T1, T0
    0x00005010,  # MFHI
    0x15400006,  # BNEZ  T2,     [forward 0x06]
    0x00005812,  # MFLO  T3
    0x296C0008,  # SLTI  T4, T3, 0x0008
    0x11800003,  # BEQZ  T4,     [forward 0x03]
    0x00000000,  # NOP
    0x0C004FAB,  # JAL   0x80013EAC
    0x2404019E,  # ADDIU A0, R0, 0x019E
    0x0804F0BF   # J     0x8013C2FC
]

map_text_redirector = [
    # Checks for Map Texts 06 or 08 if in the Forest or Castle Wall Main maps respectively and redirects the text
    # pointer to a blank string, skipping all the yes/no prompt text for pulling levers.
    0x0002FFFF,  # Dummy text string
    0x3C0B8039,  # LUI   T3, 0x8039
    0x91689EE1,  # LBU   T0, 0x9EE1 (T3)
    0x1100000F,  # BEQZ  T0,     [forward 0x0F]
    0x24090006,  # ADDIU T1, R0, 0x0006
    0x240A0002,  # ADDIU T2, R0, 0x0002
    0x110A000C,  # BEQ   T0, T2, [forward 0x0C]
    0x24090008,  # ADDIU T1, R0, 0x0008
    0x240A0009,  # ADDIU T2, R0, 0x0009
    0x110A0009,  # BEQ   T0, T2, [forward 0x09]
    0x24090004,  # ADDIU T1, R0, 0x0004
    0x240A000A,  # ADDIU T2, R0, 0x000A
    0x110A0006,  # BEQ   T0, T2, [forward 0x06]
    0x24090001,  # ADDIU T1, R0, 0x0001
    0x240A000C,  # ADDIU T2, R0, 0x000C
    0x110A0003,  # BEQ   T0, T2, [forward 0x03]
    0x2409000C,  # ADDIU T1, R0, 0x000C
    0x10000008,  # B     0x803FDB34
    0x00000000,  # NOP
    0x15250006,  # BNE   T1, A1, [forward 0x06]
    0x00000000,  # NOP
    0x3C04803F,  # LUI   A0, 0x803F
    0x3484DACC,  # ORI   A0, A0, 0xDACC
    0x24050000,  # ADDIU A1, R0, 0x0000
    0x0804B39F,  # J     0x8012CE7C
    0x00000000,  # NOP
    # Redirects to a custom message if you try placing the bomb ingredients at the bottom CC crack before deactivating
    # the seal.
    0x24090009,  # ADDIU T1, R0, 0x0009
    0x15090009,  # BNE   T0, T1, [forward 0x09]
    0x240A0002,  # ADDIU T2, R0, 0x0002
    0x15450007,  # BNE   T2, A1, [forward 0x07]
    0x916A9C18,  # LBU   T2, 0x9C18 (T3)
    0x314A0001,  # ANDI  T2, T2, 0x0001
    0x15400004,  # BNEZ  T2,     [forward 0x04]
    0x00000000,  # NOP
    0x3C04803F,  # LUI   A0, 0x803F
    0x3484DBAC,  # ORI   A0, A0, 0xDBAC
    0x24050000,  # ADDIU A1, R0, 0x0000
    0x0804B39F,  # J     0x8012CE7C
    0x00000000,  # NOP
    # Checks for Map Texts 02 or 00 if in the Villa hallway or CC lizard lab maps respectively and redirects the text
    # pointer to a blank string, skipping all the NPC dialogue mandatory for checks.
    0x3C088039,  # LUI   T0, 0x8039
    0x91089EE1,  # LBU   T0, 0x9EE1 (T0)
    0x240A0005,  # ADDIU T2, R0, 0x0005
    0x110A0006,  # BEQ   T0, T2, [forward 0x06]
    0x24090002,  # ADDIU T1, R0, 0x0002
    0x240A000C,  # ADDIU T2, R0, 0x000C
    0x110A0003,  # BEQ   T0, T2, [forward 0x03]
    0x24090000,  # ADDIU T1, R0, 0x0000
    0x0804B39F,  # J     0x8012CE7C
    0x00000000,  # NOP
    0x15250004,  # BNE   T1, A1, [forward 0x04]
    0x00000000,  # NOP
    0x3C04803F,  # LUI   A0, 0x803F
    0x3484DACC,  # ORI   A0, A0, 0xDACC
    0x24050000,  # ADDIU A1, R0, 0x0000
    0x0804B39F   # J     0x8012CE7C
]

special_descriptions_redirector = [
    # Redirects the menu description when looking at the Special1 and 2 items to different, custom strings that tell
    # how many are needed per warp and to fight Dracula respectively, and how many there are of both in the whole seed.
    0x240A0003,  # ADDIU T2, R0, 0x0003
    0x10AA0005,  # BEQ   A1, T2, [forward 0x05]
    0x240A0004,  # ADDIU T2, R0, 0x0004
    0x10AA0003,  # BEQ   A1, T2, [forward 0x03]
    0x00000000,  # NOP
    0x0804B39F,  # J     0x8012CE7C
    0x00000000,  # NOP
    0x3C04803F,  # LUI   A0, 0x803F
    0x3484E53C,  # ORI   A0, A0, 0xE53C
    0x24A5FFFD,  # ADDIU A1, A1, 0xFFFD
    0x0804B39F   # J     0x8012CE7C
]

forest_cw_villa_intro_cs_player = [
    # Plays the Forest, Castle Wall, or Villa intro cutscene after transitioning to a different map if the map being
    # transitioned to is the start of their levels respectively. Gets around the fact that they have to be set on the
    # previous loading zone for them to play normally.
    0x3C088039,  # LUI   T0, 0x8039
    0x8D099EE0,  # LW    T1, 0x9EE0 (T0)
    0x1120000B,  # BEQZ  T1  T1, [forward 0x0B]
    0x240B0000,  # ADDIU T3, R0, 0x0000
    0x3C0A0002,  # LUI   T2, 0x0002
    0x112A0008,  # BEQ   T1, T2, [forward 0x08]
    0x240B0007,  # ADDIU T3, R0, 0x0007
    0x254A0007,  # ADDIU T2, T2, 0x0007
    0x112A0005,  # BEQ   T1, T2, [forward 0x05]
    0x3C0A0003,  # LUI   T2, 0x0003
    0x112A0003,  # BEQ   T1, T2, [forward 0x03]
    0x240B0003,  # ADDIU T3, R0, 0x0003
    0x08005FAA,  # J     0x80017EA8
    0x00000000,  # NOP
    0x010B6021,  # ADDU  T4, T0, T3
    0x918D9C08,  # LBU   T5, 0x9C08 (T4)
    0x31AF0001,  # ANDI  T7, T5, 0x0001
    0x15E00009,  # BNEZ  T7,     [forward 0x09]
    0x240E0009,  # ADDIU T6, R0, 0x0009
    0x3C180003,  # LUI   T8, 0x0003
    0x57090001,  # BNEL  T8, T1, [forward 0x01]
    0x240E0004,  # ADDIU T6, R0, 0x0004
    0x15200003,  # BNEZ  T1,     [forward 0x03]
    0x240F0001,  # ADDIU T7, R0, 0x0001
    0xA18F9C08,  # SB    T7, 0x9C08 (T4)
    0x240E003C,  # ADDIU T6, R0, 0x003C
    0xA10E9EFF,  # SB    T6, 0x9EFF (T0)
    0x08005FAA   # J     0x80017EA8
]

map_id_refresher = [
    # After transitioning to a different map, if this detects the map ID being transitioned to as FF, it will write back
    # the past map ID so that the map will reset. Useful for thngs like getting around a bug wherein the camera fixes in
    # place if you enter a loading zone that doesn't actually change the map, which can happen in a seed that gives you
    # any character tower stage at the very start.
    0x240800FF,  # ADDIU T0, R0, 0x00FF
    0x110E0003,  # BEQ   T0, T6, [forward 0x03]
    0x00000000,  # NOP
    0x03E00008,  # JR    RA
    0xA44E61D8,  # SH    T6, 0x61D8
    0x904961D9,  # LBU   T1, 0x61D9
    0xA0496429,  # SB    T1, 0x6429
    0x03E00008   # JR    RA
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

gondola_skipper = [
    # Upon stepping on one of the gondolas in Tunnel to activate it, this will instantly teleport you to the other end
    # of the gondola course depending on which one activated, skipping the entire 3-minute wait to get there.
    0x3C088039,  # LUI   T0, 0x8039
    0x240900FF,  # ADDIU T1, R0, 0x00FF
    0xA1099EE1,  # SB    T1, 0x9EE1 (T0)
    0x31EA0020,  # ANDI  T2, T7, 0x0020
    0x3C0C3080,  # LUI   T4, 0x3080
    0x358C9700,  # ORI   T4, T4, 0x9700
    0x154B0003,  # BNE   T2, T3, [forward 0x03]
    0x24090002,  # ADDIU T1, R0, 0x0002
    0x24090003,  # ADDIU T1, R0, 0x0003
    0x3C0C7A00,  # LUI   T4, 0x7A00
    0xA1099EE3,  # SB    T1, 0x9EE3 (T0)
    0xAD0C9EE4,  # SW    T4, 0x9EE4 (T0)
    0x3C0D0010,  # LUI   T5, 0x0010
    0x25AD0010,  # ADDIU T5, T5, 0x0010
    0xAD0D9EE8,  # SW    T5, 0x9EE8 (T0)
    0x08063E68   # J     0x8018F9A0
]

mandragora_with_nitro_setter = [
    # When setting a Nitro, if Mandragora is in the inventory too and the wall's "Mandragora set" flag is not set, this
    # will automatically subtract a Mandragora from the inventory and set its flag so the wall can be blown up in just
    # one interaction instead of two.
    0x3C088039,  # LUI   T0, 0x8039
    0x81099EE1,  # LB    T1, 0x9EE1 (T0)
    0x240A000C,  # ADDIU T2, R0, 0x000C
    0x112A000E,  # BEQ   T1, T2, [forward 0x0E]
    0x81099C18,  # LB    T1, 0x9C18 (T0)
    0x31290002,  # ANDI  T1, T1, 0x0002
    0x11200009,  # BEQZ  T1,     [forward 0x09]
    0x91099C5D,  # LBU   T1, 0x9C5D (T0)
    0x11200007,  # BEQZ  T1,     [forward 0x07]
    0x910B9C1A,  # LBU   T3, 0x9C1A (T0)
    0x316A0001,  # ANDI  T2, T3, 0x0001
    0x15400004,  # BNEZ  T2,     [forward 0x04]
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0xA1099C5D,  # SB    T1, 0x9C5D (T0)
    0x356B0001,  # ORI   T3, T3, 0x0001
    0xA10B9C1A,  # SB    T3, 0x9C1A (T0)
    0x08000512,  # J     0x80001448
    0x00000000,  # NOP
    0x810B9BF2,  # LB    T3, 0x9BF2 (T0)
    0x31690040,  # ANDI  T1, T3, 0x0040
    0x11200008,  # BEQZ  T1,     [forward 0x08]
    0x91099C5D,  # LBU   T1, 0x9C5D (T0)
    0x11200006,  # BEQZ  T1,     [forward 0x06]
    0x316A0080,  # ANDI  T2, T3, 0x0080
    0x15400004,  # BNEZ  T2, 0x803FE0E8
    0x2529FFFF,  # ADDIU T1, T1, 0xFFFF
    0xA1099C5D,  # SB    T1, 0x9C5D (T0)
    0x356B0080,  # ORI   T3, T3, 0x0080
    0xA10B9BF2,  # SB    T3, 0x9BF2 (T0)
    0x08000512   # J     0x80001448
]

ambience_silencer = [
    # Silences map-specific ambience when loading into a different map, so we don't have to live with, say, Tower of
    # Science/Clock Tower machinery noises everywhere until either resetting, dying, or going into a map that is
    # normally set up to disable said noises. We can only silence three sounds at a time, so we will silence different
    # things depending on which map we're leaving.
    0x0C004156,  # JAL   0x80010558
    0x00000000,  # NOP
    0x3C08801D,  # LUI   T0, 0x801D
    0x9109AB91,  # LBU   T1, 0xAB91 (T0)
    # Foggy Lake ship noises
    0x240A0010,  # ADDIU T2, R0, 0x0010
    0x112A0003,  # BEQ   T1, T2, [forward 0x03]
    0x240A0011,  # ADDIU T2, R0, 0x0011
    0x152A0007,  # BNE   T1, T2, [froward 0x07]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x340481A0,  # ORI   A0, R0, 0x81A0
    0x0C0059BE,  # JAL   0x800166F8
    0x340481A1,  # ORI   A0, R0, 0x81A1
    0x08006BCA,  # J     0x8001AF28
    0x00000000,  # NOP
    # Child Henry escort noises
    0x240A0006,  # ADDIU T2, R0, 0x0006
    0x152A0009,  # BNE   T1, T2, [forward 0x09]
    0x00000000,  # NOP
    0x0C0059BE,  # JAL   0x800166F8
    0x34048371,  # ORI   A0, R0, 0x8371
    0x0C0059BE,  # JAL   0x800166F8
    0x34048372,  # ORI   A0, R0, 0x8372
    0x0C0059BE,  # JAL   0x800166F8
    0x34048358,  # ORI   A0, R0, 0x8358
    0x08006BCA,  # J     0x8001AF28
    0x00000000,  # NOP
    # Clock Tower/Tower of Science machinery
    0x0C0059BE,  # JAL   0x800166F8
    0x34048188,  # ORI   A0, R0, 0x8188
    0x0C0059BE,  # JAL   0x800166F8
    0x34048368,  # ORI   A0, R0, 0x8368
    0x08006BCA   # J     0x8001AF28
]

multiworld_item_name_loader = [
    # When picking up an item from another world, this will load from ROM the custom message for that item explaining
    # in the item textbox what the item is and who it's for. The flag index it calculates determines from what part of
    # the ROM to load the item name from. If the item being picked up is a white jewel or a contract, it will always
    # load from a part of the ROM that has nothing in it to ensure their set "flag" values don't yield unintended names.
    0x3C088040,  # LUI   T0, 0x8040
    0xAD03E238,  # SW    V1, 0xE238 (T0)
    0x92080039,  # LBU   T0, 0x0039 (S0)
    0x11000003,  # BEQZ  T0,     [forward 0x03]
    0x24090012,  # ADDIU T1, R0, 0x0012
    0x15090003,  # BNE   T0, T1, [forward 0x03]
    0x24080000,  # ADDIU T0, R0, 0x0000
    0x10000010,  # B             [forward 0x10]
    0x24080000,  # ADDIU T0, R0, 0x0000
    0x920C0055,  # LBU   T4, 0x0055 (S0)
    0x8E090058,  # LW    T1, 0x0058 (S0)
    0x1120000C,  # BEQZ  T1,     [forward 0x0C]
    0x298A0011,  # SLTI  T2, T4, 0x0011
    0x51400001,  # BEQZL T2,     [forward 0x01]
    0x258CFFED,  # ADDIU T4, T4, 0xFFED
    0x240A0000,  # ADDIU T2, R0, 0x0000
    0x00094840,  # SLL   T1, T1, 1
    0x5520FFFE,  # BNEZL T1,     [backward 0x02]
    0x254A0001,  # ADDIU T2, T2, 0x0001
    0x240B0020,  # ADDIU T3, R0, 0x0020
    0x018B0019,  # MULTU T4, T3
    0x00004812,  # MFLO  T1
    0x012A4021,  # ADDU  T0, T1, T2
    0x00084200,  # SLL   T0, T0, 8
    0x3C0400BB,  # LUI   A0, 0x00BB
    0x24847164,  # ADDIU A0, A0, 0x7164
    0x00882020,  # ADD   A0, A0, T0
    0x3C058018,  # LUI   A1, 0x8018
    0x34A5BF98,  # ORI   A1, A1, 0xBF98
    0x0C005DFB,  # JAL   0x800177EC
    0x24060100,  # ADDIU A2, R0, 0x0100
    0x3C088040,  # LUI   T0, 0x8040
    0x8D03E238,  # LW    V1, 0xE238 (T0)
    0x3C1F8012,  # LUI   RA, 0x8012
    0x27FF5BA4,  # ADDIU RA, RA, 0x5BA4
    0x0804EF54,  # J     0x8013BD50
    0x94640002,  # LHU   A0, 0x0002 (V1)
    # Changes the Y screen position of the textbox depending on how many line breaks there are.
    0x3C088019,  # LUI   T0, 0x8019
    0x9108C097,  # LBU   T0, 0xC097 (T0)
    0x11000005,  # BEQZ  T0,     [forward 0x05]
    0x2508FFFF,  # ADDIU T0, T0, 0xFFFF
    0x11000003,  # BEQZ  T0,     [forward 0x03]
    0x00000000,  # NOP
    0x1000FFFC,  # B             [backward 0x04]
    0x24C6FFF1,  # ADDIU A2, A2, 0xFFF1
    0x0804B33F,  # J     0x8012CCFC
    # Changes the length and number of lines on the textbox if there's a multiworld message in the buffer.
    0x3C088019,  # LUI   T0, 0x8019
    0x9108C097,  # LBU   T0, 0xC097 (T0)
    0x11000003,  # BEQZ  T0, [forward 0x03]
    0x00000000,  # NOP
    0x00082821,  # ADDU  A1, R0, T0
    0x240600B6,  # ADDIU A2, R0, 0x00B6
    0x0804B345,  # J     0x8012CD14
    0x00000000,  # NOP
    # Redirects the text to the multiworld message buffer if a message exists in it.
    0x3C088019,  # LUI   T0, 0x8019
    0x9108C097,  # LBU   T0, 0xC097 (T0)
    0x11000004,  # BEQZ  T0,     [forward 0x04]
    0x00000000,  # NOP
    0x3C048018,  # LUI   A0, 0x8018
    0x3484BF98,  # ORI   A0, A0, 0xBF98
    0x24050000,  # ADDIU A1, R0, 0x0000
    0x0804B39F,  # J     0x8012CE7C
    # Copy the "item from player" text when being given an item through the multiworld via the game's copy function.
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x00000000,  # NOP
    0x3C088040,  # LUI   T0, 0x8040
    0xAD1FE33C,  # SW    RA, 0xE33C (T0)
    0xA104E338,  # SB    A0, 0xE338 (T0)
    0x3C048019,  # LUI   A0, 0x8019
    0x2484C0A8,  # ADDIU A0, A0, 0xC0A8
    0x3C058019,  # LUI   A1, 0x8019
    0x24A5BF98,  # ADDIU A1, A1, 0xBF98
    0x0C000234,  # JAL   0x800008D0
    0x24060100,  # ADDIU A2, R0, 0x0100
    0x3C088040,  # LUI   T0, 0x8040
    0x8D1FE33C,  # LW    RA, 0xE33C (T0)
    0x0804EDCE,  # J     0x8013B738
    0x9104E338,  # LBU   A0, 0xE338 (T0)
    0x00000000,  # NOP
    # Neuters the multiworld item text buffer if giving a non-multiworld item through the in-game remote item rewarder
    # byte before then jumping to item_prepareTextbox.
    0x24080011,  # ADDIU T0, R0, 0x0011
    0x10880004,  # BEQ   A0, T0, [forward 0x04]
    0x24080012,  # ADDIU T0, R0, 0x0012
    0x10880002,  # BEQ   A0, T0, [forward 0x02]
    0x3C088019,  # LUI   T0, 0x8019
    0xA100C097,  # SB    R0, 0xC097 (T0)
    0x0804EDCE   # J     0x8013B738
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


always_actor_edits = {
    # Castle Wall Main
    0x7822BC: 0x00,
    0x78271C: 0x00,
    0x78273C: 0x00,
    0x78275E: 0x08,
    0x78277E: 0x08,
    0x78279C: 0x00,
    0x7827BE: 0x08,
    0x7827DC: 0x00,
    0x78281E: 0x08,
    0x78283C: 0x00,
    0x78285C: 0x00,
    0x78287E: 0x08,
    0x78289C: 0x00,
    0x7828BE: 0x08,
    0x7828DC: 0x00,
    0x7828FE: 0x08,
    0x78291C: 0x00,
    0x78293E: 0x08,
    0x78295C: 0x00,
    0x78297E: 0x08,
    0x78299E: 0x08,
    0x7829BC: 0x00,
    0x7829DE: 0x08,
    0x782AFE: 0x08,
    # Castle Wall Towers
    0x77D63E: 0x08,
    0x77D83C: 0x00,
    0x77D85C: 0x00,
    0x77D87E: 0x08,
    0x77D89E: 0x08,
    0x77D8BC: 0x00,
    0x77D8DE: 0x08,
    0x77D8FC: 0x00,
    0x77D91E: 0x08,
    # Villa front yard
    0x7851B6: 0x08,
    0x785254: 0x00,
    0x785A74: 0x00,
    0x785A96: 0x08,
    0x785AB4: 0x00,
    0x785AD6: 0x08,
    0x785B14: 0x00,
    0x785B36: 0x08,
    0x785B74: 0x00,
    0x785B96: 0x08,
    0x785BB4: 0x00,
    0x785BD4: 0x00,
    0x785BF4: 0x00,
    0x785C36: 0x08,
    0x785C56: 0x08,
    0x785C76: 0x08,
    # Villa foyer
    0x7892E4: 0x00,
    0x789304: 0x00,
    0x789326: 0x08,
    0x789346: 0x08,
    0x789366: 0x08,
    0x789386: 0x08,
    0x7893A6: 0x08,
    0x7893C6: 0x08,
    0x7893E6: 0x08,
    0x789404: 0x00,
    0x789426: 0x08,
    0x789446: 0x08,
    0x789466: 0x08,
    0x789484: 0x00,
    0x7894A4: 0x00,
    0x7894C4: 0x00,
    0x7894E4: 0x00,
    0x789504: 0x00,
    0x789524: 0x00,
    0x789546: 0x08,
    0x789BC4: 0x00,
    0x789BE6: 0x08,
    # Villa living area
    0x78FF34: 0x00,
    0x7902F4: 0x00,
    0x790356: 0x08,
    0x790994: 0x00,
    0x7909B6: 0x08,
    0x790ED4: 0x00,
    0x790EF4: 0x00,
    0x790F16: 0x08,
    0x790F36: 0x08,
    0x790F54: 0x00,
    0x790F76: 0x08,
    0x790F94: 0x00,
    0x790FB6: 0x08,
    0x791834: 0x00,
    0x791856: 0x08,
    0x791C34: 0x00,
    0x791C76: 0x08,
    0x791C94: 0x00,
    0x791CB6: 0x08,
    0x791CD4: 0x00,
    0x791CF6: 0x08,
    0x7923B4: 0x00,
    0x7923D4: 0x00,
    0x7923F4: 0x00,
    0x792416: 0x08,
    0x792436: 0x08,
    0x792456: 0x08,
    0x792A14: 0x00,
    0x792A34: 0x00,
    0x792B36: 0x08,
    0x792B54: 0x00,
    0x792B74: 0x00,
    0x792B96: 0x08,
    # Villa maze
    0x798A88: 0x00,
    0x798AA8: 0x00,
    0x798CE8: 0x00,
    0x798DEA: 0x08,
    0x798E0A: 0x08,
    0x798E2A: 0x08,
    0x798FC8: 0x00,
    0x798FEA: 0x08,
    0x799008: 0x00,
    0x799028: 0x00,
    0x79904A: 0x08,
    0x799068: 0x00,
    0x799088: 0x00,
    0x7990CA: 0x08,
    0x7990EA: 0x08,
    0x79910A: 0x08,
    0x79912A: 0x08,
    0x79914A: 0x08,
    0x799168: 0x00,
    0x79918A: 0x08,
    0x7991A8: 0x00,
    0x7991CA: 0x08,
    0x7991E8: 0x00,
    0x799208: 0x00,
    0x799228: 0x00,
    0x79924A: 0x08,
    0x799268: 0x00,
    0x799288: 0x00,
    0x7992AA: 0x08,
    0x7992CA: 0x08,
    0x7992EA: 0x08,
    0x79930A: 0x08,
    0x799328: 0x00,
    0x79934A: 0x08,
    0x79936A: 0x08,
    0x79938A: 0x08,
    0x7993A8: 0x00,
    0x7993C8: 0x00,
    0x7993EA: 0x08,
    0x799408: 0x00,
    0x79942A: 0x08,
    0x799448: 0x00,
    0x79946A: 0x08,
    0x799488: 0x00,
    0x7994A8: 0x00,
    0x799608: 0x00,
    0x799628: 0x00,
    0x799648: 0x00,
    0x799668: 0x00,
    0x79974A: 0x08,
    0x79976A: 0x08,
    # Villa vampire crypt
    0x7D66AA: 0x08,
    0x7D66CA: 0x08,
    0x7D66EA: 0x08,
    0x7D670A: 0x08,
    0x7D6728: 0x00,
    0x7D6768: 0x00,
    0x7D6788: 0x00,
    0x7D67AA: 0x08,
    0x7D67C8: 0x00,
    0x7D67E8: 0x00,
    0x7D680A: 0x08,
    0x7D684A: 0x08,
    0x7D686A: 0x08,
    0x7D688A: 0x08,
    0x7D68A8: 0x00,
}

cw_combined_edits = {
    # Main
    0x78229E: 0x08,
    0x7822DC: 0x00,
    0x78233C: 0x00,
    0x78235E: 0x08,
    0x782A1E: 0x08,
    0x782A3C: 0x00,
    0x782A5C: 0x00,
    0x782A7C: 0x00,
    0x782A9C: 0x00,
    0x782ABE: 0x08,
    0x782ADE: 0x08,
    # Towers
    0x77DC5E: 0x08,
    0x77DC7C: 0x00,
    0x77DCDE: 0x08,
    0x77DCFC: 0x00,
}

villa_combined_edits = {
    # Front yard
    0x7851D6: 0x08,
    0x7851F6: 0x08,
    0x785216: 0x08,
    0x785236: 0x08,
    0x785376: 0x08,
    0x785394: 0x00,
    0x7853D4: 0x00,
    0x7853F4: 0x00,
    0x785C94: 0x00,
    0x785CB4: 0x00,
    0x785CD4: 0x00,
    0x785CF4: 0x00,
    0x785D14: 0x00,
    0x785D34: 0x00,
    # Foyer
    0x7887E4: 0x00,
    0x788826: 0x08,
    0x788866: 0x08,
    0x788BC6: 0x08,
    0x788BE6: 0x08,
    0x788C06: 0x08,
    0x788C24: 0x00,
    0x788C44: 0x00,
    0x788C64: 0x00,
    # Living area
    0x78FF54: 0x00,
    0x78FF74: 0x00,
    0x78FF94: 0x00,
    0x791434: 0x00,
    0x791C54: 0x00,
    # Maze
    0x79812A: 0x08,
    0x79814A: 0x08,
    0x798248: 0x00,
    0x798A48: 0x00,
    0x798A6A: 0x08,
    0x798AE8: 0x00,
    0x798B08: 0x02,
    0x798B28: 0x02,
    0x798B48: 0x04,
    0x798B68: 0x04,
    0x798B88: 0x06,
    0x798BA8: 0x06,
    0x798BC8: 0x06,
    0x798BE8: 0x04,
    0x798C08: 0x04,
    0x798C28: 0x07,
    0x798C48: 0x07,
    0x798C68: 0x04,
    0x798C88: 0x02,
    0x798CA8: 0x04,
    0x798CC8: 0x07,
    0x798D08: 0x00,
    0x798D28: 0x00,
    0x798D48: 0x00,
    0x798D68: 0x00,
    0x798D88: 0x00,
    0x798DA8: 0x00,
    0x798DC8: 0x00,
    0x798E48: 0x07,
    0x798E68: 0x01,
    0x798E88: 0x02,
    0x798EA8: 0x04,
    0x798EC8: 0x01,
    0x798EE8: 0x02,
    0x798F08: 0x04,
    0x798F28: 0x07,
    0x798F48: 0x07,
    0x798F68: 0x07,
    0x7994CA: 0x08,
    0x7994EA: 0x08,
    0x79950A: 0x08,
    0x79952A: 0x08,
    0x79954A: 0x08,
    0x79956A: 0x08,
    0x79958A: 0x08,
    0x7995AA: 0x08,
    0x7995CA: 0x08,
    0x7995EA: 0x08,
    0x799688: 0x00,
    0x7996A8: 0x00,
    0x7996C8: 0x00,
    0x7996E8: 0x00,
    0x799708: 0x00,
    0x799728: 0x00,
    # Vampire crypt
    0x7D6568: 0x00,
    0x7D6588: 0x00,
}
