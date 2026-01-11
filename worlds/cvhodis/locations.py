import logging

from BaseClasses import Location
from .data import loc_names, item_names
from .options import CVHoDisOptions, CastleWarpCondition

from typing import NamedTuple

BASE_ID = 0xD15500000


class CVHoDisLocation(Location):
    game: str = "Castlevania - Harmony of Dissonance"


class CVHoDisLocationData(NamedTuple):
    code: int # The Location object's unique code attribute, as well as the in-game pickup flag ID. The 6th and higher
              # bits in the number represent which word starting from 0x02000330 the bitflag is in, and the 5 lower
              # bits represent which bit in said word is the bitflag.
    offset: int # Where in the ROM the placement data for that Location's in-game pickup actor begins. DSVania Editor
                # can be used to easily verify these.
    # countdown: int | None # Coming soon(tm)
    item: str # What Item to add to the AP itempool if that Location is added. Usually but not always, this is the Item
              # that's normally there in the vanilla game.


CVHODIS_LOCATIONS_INFO: dict[str, CVHoDisLocationData] = {
    # Various areas
    loc_names.portals_rt: CVHoDisLocationData(0x2F, 0x49BE14, item_names.equip_l_charm),
    loc_names.portals_lw: CVHoDisLocationData(0x88, 0x69E118, item_names.equip_glove_s),

    # Entrance A
    loc_names.eta2:  CVHoDisLocationData(0xB2, 0x499794, item_names.use_prism_b),
    loc_names.eta3:  CVHoDisLocationData(0x2E, 0x4997E8, item_names.equip_armor_ma),
    loc_names.eta5a: CVHoDisLocationData(0xB5, 0x499890, item_names.use_potion),
    loc_names.eta5b: CVHoDisLocationData(0xB6, 0x499908, item_names.use_potion),
    loc_names.eta7:  CVHoDisLocationData(0x64, 0x4999BC, item_names.max_heart),
    loc_names.eta9:  CVHoDisLocationData(0x2B, 0x499A04, item_names.whip_plat),
    loc_names.eta10: CVHoDisLocationData(0xAC, 0x499A28, item_names.equip_boots_l),
    loc_names.eta11: CVHoDisLocationData(0x0F, 0x499A7C, item_names.relic_orb),
    loc_names.eta13: CVHoDisLocationData(0x46, 0x499B54, item_names.max_life),
    loc_names.eta17: CVHoDisLocationData(0x08, 0x499CA4, item_names.use_hint_3),
    loc_names.eta18: CVHoDisLocationData(0x3C, 0x69E058, item_names.equip_bracelet_jb),
    loc_names.eta19: CVHoDisLocationData(0x82, 0x499CF8, item_names.equip_armor_l),

    # Entrance B
    loc_names.etb0:   CVHoDisLocationData(0xA2, 0x49A714, item_names.equip_w_fatigues),
    loc_names.etb2a:  CVHoDisLocationData(0xE0, 0x49A750, item_names.furn_urn_a),
    loc_names.etb2b:  CVHoDisLocationData(0xE1, 0x49A75C, item_names.use_prism_b),
    loc_names.etb3:   CVHoDisLocationData(0x14, 0x49A798, item_names.relic_v_rib),
    loc_names.etb9:   CVHoDisLocationData(0x0A, 0x49A948, item_names.use_key_l),
    loc_names.etb11:  CVHoDisLocationData(0x77, 0x49A9B4, item_names.max_heart),
    loc_names.etb13a: CVHoDisLocationData(0xE3, 0x49AA8C, item_names.furn_vase),
    loc_names.etb13b: CVHoDisLocationData(0xE4, 0x49AAB0, item_names.use_potion_h),
    loc_names.etb13c: CVHoDisLocationData(0xE7, 0x49AAF8, item_names.use_prism_b),

    # Marble Corridor A
    loc_names.mca2a:  CVHoDisLocationData(0x65, 0x49B7C0, item_names.max_heart),
    loc_names.mca2b:  CVHoDisLocationData(0x19, 0x49B7CC, item_names.book_ice),
    loc_names.mca4:   CVHoDisLocationData(0x23, 0x49B82C, item_names.use_map_1),
    loc_names.mca7:   CVHoDisLocationData(0xA7, 0x49B994, item_names.equip_glove_l),
    loc_names.mca9a:  CVHoDisLocationData(0x18, 0x49B9E8, item_names.book_fire),
    loc_names.mca9b:  CVHoDisLocationData(0x9C, 0x49B9F4, item_names.equip_summer),
    loc_names.mca10:  CVHoDisLocationData(0x26, 0x49BA6C, item_names.whip_red),
    loc_names.mca11a: CVHoDisLocationData(0xB7, 0x49BAD8, item_names.use_a_venom),
    loc_names.mca11b: CVHoDisLocationData(0x67, 0x49BAE4, item_names.max_heart),
    loc_names.mca11c: CVHoDisLocationData(0xB9, 0x49BB68, item_names.use_potion),
    loc_names.mca11d: CVHoDisLocationData(0xB8, 0x49BB8C, item_names.use_a_venom),
    loc_names.mca11e: CVHoDisLocationData(0x17, 0x49BB98, item_names.relic_v_ring),
    loc_names.mca11f: CVHoDisLocationData(0x66, 0x49BBA4, item_names.max_heart),
    loc_names.mca12:  CVHoDisLocationData(0x48, 0x49BBF8, item_names.max_life),
    loc_names.mca13:  CVHoDisLocationData(0x10, 0x49BC28, item_names.relic_journal),
    loc_names.mca14:  CVHoDisLocationData(0xBB, 0x49BC4C, item_names.use_potion),

    # Room of Illusion A
    loc_names.ria15: CVHoDisLocationData(0x90, 0x49BC94, item_names.equip_bandana),
    loc_names.ria16: CVHoDisLocationData(0x47, 0x49BD0C, item_names.max_life),
    loc_names.ria17: CVHoDisLocationData(0x68, 0x49BD54, item_names.max_heart),

    # Marble Corridor B
    loc_names.mcb2:  CVHoDisLocationData(0x59, 0x49CA1C, item_names.max_life),
    loc_names.mcb9:  CVHoDisLocationData(0xA6, 0x49CB84, item_names.equip_cloak_t),
    loc_names.mcb10: CVHoDisLocationData(0xEB, 0x49CBD8, item_names.use_potion_h),
    loc_names.mcb11: CVHoDisLocationData(0x9B, 0x49CCA4, item_names.equip_helm_v),
    loc_names.mcb12: CVHoDisLocationData(0x78, 0x49CCEC, item_names.max_heart),

    # Room of Illusion B
    loc_names.rib16: CVHoDisLocationData(0xED, 0x49CDD0, item_names.furn_curtain),
    loc_names.rib19: CVHoDisLocationData(0x5B, 0x49CE6C, item_names.max_life),

    # The Wailing Way A
    loc_names.wwa0a: CVHoDisLocationData(0xA3, 0x49D8AC, item_names.equip_cloak_s),
    loc_names.wwa0b: CVHoDisLocationData(0x11, 0x49D8B8, item_names.relic_tome),
    loc_names.wwa0c: CVHoDisLocationData(0x49, 0x49D8DC, item_names.max_life),
    loc_names.wwa0d: CVHoDisLocationData(0xBC, 0x49D900, item_names.use_drumstick),
    loc_names.wwa1:  CVHoDisLocationData(0xBA, 0x49D954, item_names.use_prism),
    loc_names.wwa3:  CVHoDisLocationData(0x83, 0x49DA74, item_names.use_potion),
    loc_names.wwa4a: CVHoDisLocationData(0x30, 0x49DAA4, item_names.equip_ring_lo),
    loc_names.wwa4b: CVHoDisLocationData(0x9D, 0x49DB1C, item_names.equip_clothes_f),
    loc_names.wwa8:  CVHoDisLocationData(0x69, 0x49DC90, item_names.max_heart),

    # Shrine of the Apostates A
    loc_names.saa6a:  CVHoDisLocationData(0xBE, 0x49DBF4, item_names.use_drumstick),
    loc_names.saa6b:  CVHoDisLocationData(0xBF, 0x49DC30, item_names.use_gem_o),
    loc_names.saa7:   CVHoDisLocationData(0x2C, 0x49DC48, item_names.whip_circle),
    loc_names.saa10:  CVHoDisLocationData(0xBD, 0x49DCE4, item_names.use_potion),
    loc_names.saa12:  CVHoDisLocationData(0x4A, 0x49DD5C, item_names.max_life),
    loc_names.saa15:  CVHoDisLocationData(0x01, 0x49DE64, item_names.relic_tail),
    loc_names.saa16:  CVHoDisLocationData(0x4B, 0x49DF00, item_names.max_life),

    # The Wailing Way B
    loc_names.wwb0a:  CVHoDisLocationData(0x5A, 0x49E8F8, item_names.max_life),
    loc_names.wwb0b:  CVHoDisLocationData(0xEE, 0x49E910, item_names.use_a_venom),
    loc_names.wwb3:   CVHoDisLocationData(0xF0, 0x49EA78, item_names.furn_candle_h),
    loc_names.wwb4a:  CVHoDisLocationData(0x04, 0x49EAB4, item_names.equip_boots_c),
    loc_names.wwb4b:  CVHoDisLocationData(0xF2, 0x49EB20, item_names.furn_statue_sm),
    loc_names.wwb4c:  CVHoDisLocationData(0xF3, 0x49EB38, item_names.use_potion),

    # Shrine of the Apostates B
    loc_names.sab5:   CVHoDisLocationData(0xF5, 0x49EB98, item_names.use_turkey),
    loc_names.sab7:   CVHoDisLocationData(0x7A, 0x49EC7C, item_names.max_heart),
    loc_names.sab11:  CVHoDisLocationData(0xF6, 0x49ED78, item_names.use_drumstick),
    loc_names.sab12:  CVHoDisLocationData(0xF7, 0x49EDFC, item_names.use_elixir),
    loc_names.sab15:  CVHoDisLocationData(0x79, 0x49EF1C, item_names.max_heart),

    # Castle Treasury A
    loc_names.cya0a:  CVHoDisLocationData(0xCB, 0x4AD824, item_names.furn_teacup),
    loc_names.cya0b:  CVHoDisLocationData(0xCC, 0x4AD830, item_names.furn_teapot),
    loc_names.cya1:   CVHoDisLocationData(0x52, 0x4AD8A8, item_names.max_life),
    loc_names.cya4:   CVHoDisLocationData(0x3D, 0x69E098, item_names.equip_mail_ce),
    loc_names.cya6:   CVHoDisLocationData(0x34, 0x4AD98C, item_names.equip_g_amulet),
    loc_names.cya8:   CVHoDisLocationData(0xCD, 0x4AD9EC, item_names.use_potion),
    loc_names.cya9:   CVHoDisLocationData(0xCE, 0x4ADA58, item_names.furn_closet),
    loc_names.cya10:  CVHoDisLocationData(0x8C, 0x4ADAAC, item_names.equip_mail_p),
    loc_names.cya11:  CVHoDisLocationData(0x71, 0x4ADAC4, item_names.max_heart),
    loc_names.cya12:  CVHoDisLocationData(0x32, 0x4ADB18, item_names.equip_ring_he),
    loc_names.cya18:  CVHoDisLocationData(0x31, 0x4ADD40, item_names.equip_ring_ho),
    loc_names.cya19:  CVHoDisLocationData(0xCF, 0x4ADD64, item_names.furn_chan),
    loc_names.cya20a: CVHoDisLocationData(0x85, 0x4ADDF4, item_names.equip_p_shoes),
    loc_names.cya20b: CVHoDisLocationData(0x33, 0x4ADE00, item_names.equip_armor_mo),

    # Castle Treasury B
    loc_names.cyb0a:  CVHoDisLocationData(0x1F,  0x4AF188, item_names.equip_wristband),
    loc_names.cyb0b:  CVHoDisLocationData(0x102, 0x4AF218, item_names.use_uncurse),
    loc_names.cyb1:   CVHoDisLocationData(0x7B,  0x4AF230, item_names.max_heart),
    loc_names.cyb5:   CVHoDisLocationData(0x5D,  0x4AF2D8, item_names.max_life),
    loc_names.cyb8:   CVHoDisLocationData(0x24,  0x4AF380, item_names.use_potion),
    loc_names.cyb11:  CVHoDisLocationData(0x103, 0x4AF464, item_names.furn_chair),
    loc_names.cyb12:  CVHoDisLocationData(0x84,  0x4AF4DC, item_names.equip_tunic),
    loc_names.cyb18a: CVHoDisLocationData(0x86,  0x4AF728, item_names.equip_armor_pad),
    loc_names.cyb18b: CVHoDisLocationData(0x7C,  0x4AF734, item_names.max_heart),
    loc_names.cyb20:  CVHoDisLocationData(0x42,  0x4AF7A0, item_names.equip_armor_su),

    # Skeleton Cave A
    loc_names.sca1a:  CVHoDisLocationData(0xA1, 0x4A151C, item_names.equip_robe_l),
    loc_names.sca1b:  CVHoDisLocationData(0xC8, 0x4A1534, item_names.furn_phono),
    loc_names.sca2:   CVHoDisLocationData(0xC9, 0x4A15AC, item_names.furn_shelf),
    loc_names.sca4:   CVHoDisLocationData(0x72, 0x4A16CC, item_names.max_heart),
    loc_names.sca5:   CVHoDisLocationData(0x54, 0x4A16FC, item_names.max_life),
    loc_names.sca10:  CVHoDisLocationData(0x36, 0x4A1918, item_names.equip_cipher),
    loc_names.sca11:  CVHoDisLocationData(0x35, 0x4A1930, item_names.equip_ring_r),
    loc_names.sca12a: CVHoDisLocationData(0xCA, 0x4A1954, item_names.use_prism_b),
    loc_names.sca12b: CVHoDisLocationData(0x53, 0x4A1960, item_names.max_life),
    loc_names.sca13:  CVHoDisLocationData(0x02, 0x4A1984, item_names.use_key_f),
    loc_names.sca19:  CVHoDisLocationData(0x21, 0x4A1A8C, item_names.use_hint_5),

    # Skeleton Cave B
    loc_names.scb1a:  CVHoDisLocationData(0xFC, 0x4A264C, item_names.use_potion),
    loc_names.scb1b:  CVHoDisLocationData(0xAD, 0x4A2664, item_names.equip_guard_a),
    loc_names.scb2:   CVHoDisLocationData(0x7D, 0x4A26C4, item_names.max_heart),
    loc_names.scb3:   CVHoDisLocationData(0x2D, 0x4A2754, item_names.whip_bullet),
    loc_names.scb4:   CVHoDisLocationData(0xFD, 0x4A2820, item_names.furn_table_s),
    loc_names.scb5:   CVHoDisLocationData(0xFE, 0x4A28B0, item_names.furn_stag),
    loc_names.scb10:  CVHoDisLocationData(0x06, 0x4A2A90, item_names.relic_feather),
    loc_names.scb11:  CVHoDisLocationData(0x5E, 0x4A2AA8, item_names.max_life),
    loc_names.scb12a: CVHoDisLocationData(0x1C, 0x4A2ACC, item_names.book_summon),
    loc_names.scb12b: CVHoDisLocationData(0xFF, 0x4A2AD8, item_names.furn_urn_w),
    loc_names.scb13:  CVHoDisLocationData(0x92, 0x4A2B44, item_names.equip_cap),

    # Luminous Cavern A
    loc_names.lca3:   CVHoDisLocationData(0xD0, 0x4A3E30, item_names.use_drumstick),
    loc_names.lca7a:  CVHoDisLocationData(0x76, 0x4A3F2C, item_names.max_heart),
    loc_names.lca7b:  CVHoDisLocationData(0x99, 0x4A3F38, item_names.equip_helm_f),
    loc_names.lca8a:  CVHoDisLocationData(0x6B, 0x4A3FC8, item_names.max_heart),
    loc_names.lca8b:  CVHoDisLocationData(0x58, 0x4A3FD4, item_names.max_life),
    loc_names.lca8c:  CVHoDisLocationData(0x6C, 0x4A3FE0, item_names.max_heart),
    loc_names.lca10:  CVHoDisLocationData(0x09, 0x4A404C, item_names.use_key_s),
    loc_names.lca11:  CVHoDisLocationData(0x3E, 0x69E0D8, item_names.equip_crown),
    loc_names.lca14:  CVHoDisLocationData(0x1D, 0x4A4100, item_names.use_hint_1),
    loc_names.lca17:  CVHoDisLocationData(0xAB, 0x4A4244, item_names.equip_arm_p),
    loc_names.lca18:  CVHoDisLocationData(0xB0, 0x4A428C, item_names.equip_leggings),
    loc_names.lca22:  CVHoDisLocationData(0xD2, 0x4A440C, item_names.use_medicine),
    loc_names.lca23:  CVHoDisLocationData(0x03, 0x4A44FC, item_names.relic_wing),

    # Luminous Cavern B
    loc_names.lcb3:   CVHoDisLocationData(0x104, 0x4A5574, item_names.use_gem_t),
    loc_names.lcb7a:  CVHoDisLocationData(0x10B, 0x4A56AC, item_names.use_prism),
    loc_names.lcb7b:  CVHoDisLocationData(0x10C, 0x4A56B8, item_names.furn_statue_sa),
    loc_names.lcb8a:  CVHoDisLocationData(0x44,  0x4A5778, item_names.equip_armor_w),
    loc_names.lcb8b:  CVHoDisLocationData(0x10D, 0x4A57D8, item_names.use_elixir),
    loc_names.lcb10a: CVHoDisLocationData(0x28,  0x4A5910, item_names.whip_yellow),
    loc_names.lcb10b: CVHoDisLocationData(0x10F, 0x4A591C, item_names.furn_mirror),
    loc_names.lcb13:  CVHoDisLocationData(0x10E, 0x4A59DC, item_names.furn_dishes),
    loc_names.lcb16:  CVHoDisLocationData(0x63,  0x4A5AD8, item_names.max_life),
    loc_names.lcb17:  CVHoDisLocationData(0x81,  0x4A5B2C, item_names.max_heart),
    loc_names.lcb18:  CVHoDisLocationData(0x110, 0x4A5B44, item_names.use_potion_h),
    loc_names.lcb22a: CVHoDisLocationData(0x111, 0x4A5BEC, item_names.use_potion),
    loc_names.lcb22b: CVHoDisLocationData(0x112, 0x4A5C58, item_names.use_uncurse),

    # Sky Walkway A
    loc_names.swa7:   CVHoDisLocationData(0x07, 0x69E00C, item_names.equip_bracelet_mk),
    loc_names.swa10a: CVHoDisLocationData(0xD6, 0x4A7FD0, item_names.use_a_venom),
    loc_names.swa10b: CVHoDisLocationData(0xD7, 0x4A7FF4, item_names.use_potion_h),
    loc_names.swa10c: CVHoDisLocationData(0x56, 0x4A8030, item_names.max_life),
    loc_names.swa12a: CVHoDisLocationData(0xD9, 0x4A8114, item_names.furn_trinket_s),
    loc_names.swa12b: CVHoDisLocationData(0xDA, 0x4A8120, item_names.furn_trinket_g),
    loc_names.swa12c: CVHoDisLocationData(0xDB, 0x4A8174, item_names.use_elixir),
    loc_names.swa14:  CVHoDisLocationData(0x3A, 0x4A81D4, item_names.equip_goggles),
    loc_names.swa15a: CVHoDisLocationData(0xDC, 0x4A8228, item_names.use_medicine),
    loc_names.swa15b: CVHoDisLocationData(0xDD, 0x4A8234, item_names.use_medicine),
    loc_names.swa17:  CVHoDisLocationData(0x94, 0x4A82B8, item_names.equip_guard_f),
    loc_names.swa18a: CVHoDisLocationData(0x3B, 0x4A8354, item_names.equip_ring_c),
    loc_names.swa18b: CVHoDisLocationData(0x1E, 0x4A8390, item_names.use_hint_2),

    # Chapel of Dissonance A
    loc_names.cda0a: CVHoDisLocationData(0x4D, 0x4A7D0C, item_names.max_life),
    loc_names.cda0b: CVHoDisLocationData(0xD3, 0x4A7D18, item_names.use_potion),
    loc_names.cda0c: CVHoDisLocationData(0xA4, 0x4A7D48, item_names.equip_cloak_e),
    loc_names.cda0d: CVHoDisLocationData(0x12, 0x4A7D60, item_names.relic_v_eye),
    loc_names.cda0e: CVHoDisLocationData(0x6A, 0x4A7D78, item_names.max_heart),
    loc_names.cda2:  CVHoDisLocationData(0xD5, 0x4A7DE4, item_names.use_a_venom),

    # Sky Walkway B
    loc_names.swb8:   CVHoDisLocationData(0x60,  0x4A9170, item_names.max_life),
    loc_names.swb10a: CVHoDisLocationData(0x9F,  0x4A9200, item_names.equip_robe_b),
    loc_names.swb10b: CVHoDisLocationData(0x118, 0x4A9218, item_names.furn_radio),
    loc_names.swb10c: CVHoDisLocationData(0x119, 0x4A9224, item_names.furn_chair_r),
    loc_names.swb12a: CVHoDisLocationData(0x80,  0x4A9314, item_names.max_heart),
    loc_names.swb12b: CVHoDisLocationData(0x11A, 0x4A9320, item_names.furn_bed),
    loc_names.swb14:  CVHoDisLocationData(0x8A,  0x4A93BC, item_names.use_prism),
    loc_names.swb15:  CVHoDisLocationData(0x13,  0x4A9410, item_names.relic_v_heart),
    loc_names.swb16:  CVHoDisLocationData(0x11B, 0x4A9428, item_names.use_turkey),
    loc_names.swb19:  CVHoDisLocationData(0x7F,  0x4A9524, item_names.max_heart),

    # Chapel of Dissonance B
    loc_names.cdb0a: CVHoDisLocationData(0x115, 0x4A8F24, item_names.use_prism_b),
    loc_names.cdb0b: CVHoDisLocationData(0x6F,  0x4A8F54, item_names.max_heart),
    loc_names.cdb0c: CVHoDisLocationData(0x4F,  0x4A8F78, item_names.max_life),
    loc_names.cdb0d: CVHoDisLocationData(0x22,  0x4A8F84, item_names.use_hint_6),
    loc_names.cdb0e: CVHoDisLocationData(0x116, 0x4A8FA8, item_names.furn_statue_h),
    loc_names.cdb4:  CVHoDisLocationData(0x117, 0x4A9080, item_names.use_potion_h),

    # Aqueduct of Dragons A
    loc_names.ada1:   CVHoDisLocationData(0x15, 0x4A6370, item_names.relic_v_nail),
    loc_names.ada2:   CVHoDisLocationData(0xA9, 0x4A63D0, item_names.equip_glove_h),
    loc_names.ada4:   CVHoDisLocationData(0x74, 0x4A64E4, item_names.max_heart),
    loc_names.ada8:   CVHoDisLocationData(0x27, 0x4A6718, item_names.whip_blue),
    loc_names.ada10a: CVHoDisLocationData(0x57, 0x4A6778, item_names.max_life),
    loc_names.ada10b: CVHoDisLocationData(0x75, 0x4A6790, item_names.max_heart),

    # Aqueduct of Dragons B
    loc_names.adb0: CVHoDisLocationData(0x43,  0x4A6E64, item_names.equip_ring_e),
    loc_names.adb1: CVHoDisLocationData(0x61,  0x4A6E7C, item_names.max_life),
    loc_names.adb2: CVHoDisLocationData(0x113, 0x4A6EDC, item_names.use_uncurse),
    loc_names.adb4: CVHoDisLocationData(0x114, 0x4A6F18, item_names.use_elixir),
    loc_names.adb8: CVHoDisLocationData(0x62,  0x4A70EC, item_names.max_life),

    # Clock Tower A
    loc_names.cra0:   CVHoDisLocationData(0x95, 0x4AA614, item_names.equip_bagonette),
    loc_names.cra1:   CVHoDisLocationData(0x20, 0x4AA644, item_names.use_hint_4),
    loc_names.cra2:   CVHoDisLocationData(0x55, 0x4AA698, item_names.max_life),
    loc_names.cra3:   CVHoDisLocationData(0x89, 0x4AA770, item_names.equip_armor_sc),
    loc_names.cra9:   CVHoDisLocationData(0x73, 0x4AA8F0, item_names.max_heart),
    loc_names.cra10:  CVHoDisLocationData(0x25, 0x4AA95C, item_names.use_map_3),
    loc_names.cra14:  CVHoDisLocationData(0xDE, 0x4AAB6C, item_names.furn_table_a),
    loc_names.cra17a: CVHoDisLocationData(0x0D, 0x4AAC68, item_names.equip_guardian_g),
    loc_names.cra17b: CVHoDisLocationData(0x0E, 0x4AAC74, item_names.equip_guardian_b),
    loc_names.cra17c: CVHoDisLocationData(0x0C, 0x4AAC80, item_names.equip_guardian_h),
    # NOTE: For some reason, DSVania Editor has the wrong address for cra17d. 0x4AAC98 is for the top gear in this room.
    loc_names.cra17d: CVHoDisLocationData(0x0B, 0x4AAC8C, item_names.equip_guardian_a),
    loc_names.cra20:  CVHoDisLocationData(0x29, 0x4AAD70, item_names.whip_green),
    loc_names.cra22a: CVHoDisLocationData(0xDF, 0x4AAEF0, item_names.furn_cat),
    loc_names.cra22b: CVHoDisLocationData(0x1A, 0x4AAEFC, item_names.book_bolt),
    loc_names.cra22c: CVHoDisLocationData(0x4E, 0x4AAF08, item_names.max_life),
    loc_names.cra22d: CVHoDisLocationData(0x6E, 0x4AAF14, item_names.max_heart),
    loc_names.cra23:  CVHoDisLocationData(0x16, 0x4AAF2C, item_names.relic_v_fang),

    # Clock Tower B
    loc_names.crb1:   CVHoDisLocationData(0x45,  0x4ABFB8, item_names.equip_kaiser),
    loc_names.crb2:   CVHoDisLocationData(0xA5,  0x4AC000, item_names.equip_cloak_w),
    loc_names.crb3:   CVHoDisLocationData(0x105, 0x4AC0CC, item_names.use_elixir),
    loc_names.crb4:   CVHoDisLocationData(0x4C,  0x4AC120, item_names.max_life),
    loc_names.crb6a:  CVHoDisLocationData(0x106, 0x4AC1B0, item_names.use_prism_b),
    loc_names.crb6b:  CVHoDisLocationData(0x107, 0x4AC1F8, item_names.use_potion_h),
    loc_names.crb8:   CVHoDisLocationData(0x108, 0x4AC264, item_names.use_medicine),
    loc_names.crb10:  CVHoDisLocationData(0x05,  0x4AC294, item_names.whip_crush),
    loc_names.crb13:  CVHoDisLocationData(0x109, 0x4AC36C, item_names.furn_clock),
    # NOTE: DSVania Editor has the wrong address for crb17 as well. 0x4AC5A0 is for the White Dragon Lv2.
    loc_names.crb17:  CVHoDisLocationData(0x7E,  0x4AC594, item_names.max_heart),
    loc_names.crb20:  CVHoDisLocationData(0x5F,  0x4AC648, item_names.max_life),
    loc_names.crb22a: CVHoDisLocationData(0x37,  0x4AC7A4, item_names.equip_h_choker),
    loc_names.crb22b: CVHoDisLocationData(0x38,  0x4AC7B0, item_names.equip_mail_h),
    loc_names.crb23a: CVHoDisLocationData(0x10A, 0x4AC7C8, item_names.furn_raccoon),
    loc_names.crb23b: CVHoDisLocationData(0x39,  0x4AC7D4, item_names.equip_ring_lu),

    # Castle Top Floor A
    loc_names.tfa0a: CVHoDisLocationData(0xC0, 0x49F8C4, item_names.use_elixir),
    loc_names.tfa0b: CVHoDisLocationData(0xC1, 0x49F8D0, item_names.use_turkey),
    loc_names.tfa0c: CVHoDisLocationData(0xC2, 0x49F8DC, item_names.furn_candle_s),
    loc_names.tfa0d: CVHoDisLocationData(0x50, 0x49F8E8, item_names.max_life),
    loc_names.tfa0e: CVHoDisLocationData(0xC3, 0x49F8F4, item_names.use_prism_b),
    loc_names.tfa1a: CVHoDisLocationData(0x51, 0x49F90C, item_names.max_life),
    loc_names.tfa1b: CVHoDisLocationData(0x70, 0x49F918, item_names.max_heart),
    loc_names.tfa7:  CVHoDisLocationData(0xC4, 0x49FB34, item_names.furn_drawing),
    loc_names.tfa8:  CVHoDisLocationData(0xC5, 0x49FB88, item_names.use_elixir),
    loc_names.tfa9:  CVHoDisLocationData(0x8E, 0x49FC48, item_names.equip_armor_si),
    loc_names.tfa11: CVHoDisLocationData(0x2A, 0x49FC9C, item_names.whip_steel),
    loc_names.tfa15: CVHoDisLocationData(0x87, 0x49FCFC, item_names.equip_brooch),

    # Castle Top Floor B
    loc_names.tfb0a:  CVHoDisLocationData(0x8F, 0x4A05B4, item_names.equip_mail_k),
    loc_names.tfb0b:  CVHoDisLocationData(0x40, 0x4A05D8, item_names.use_medicine),
    loc_names.tfb0c:  CVHoDisLocationData(0x41, 0x4A05E4, item_names.use_medicine),
    loc_names.tfb0d:  CVHoDisLocationData(0x6D, 0x4A05F0, item_names.max_heart),
    loc_names.tfb0e:  CVHoDisLocationData(0xF9, 0x4A05FC, item_names.furn_glass),
    loc_names.tfb3:   CVHoDisLocationData(0x3F, 0x4A0668, item_names.equip_robe_m),
    loc_names.tfb5:   CVHoDisLocationData(0xFA, 0x4A0704, item_names.use_potion),
    loc_names.tfb7:   CVHoDisLocationData(0xFB, 0x4A080C, item_names.use_potion_h),
    loc_names.tfb11a: CVHoDisLocationData(0x5C, 0x4A095C, item_names.max_life),
    loc_names.tfb11b: CVHoDisLocationData(0x1B, 0x4A0968, item_names.book_wind),
}

# All event Locations mapped to their respective event Items.
# Because this is the only info we need for them, they are kept separate from the regular Item checks for nicer typing.
CVHODIS_EVENT_MAPPING: dict[str, str] = {
    loc_names.event_ending_m: item_names.event_ending_m,
    loc_names.event_ending_b: item_names.event_ending_b,
    loc_names.event_ending_g: item_names.event_ending_g,
    loc_names.event_furniture: item_names.event_furniture,
    loc_names.event_death: item_names.event_death,
    loc_names.event_wall_skeleton: item_names.event_wall_skeleton,
    loc_names.event_wall_sky: item_names.event_wall_sky,
    loc_names.event_button_clock: item_names.event_button_clock,
    loc_names.event_crank: item_names.event_crank,
    loc_names.event_guarder: item_names.event_guarder,
    loc_names.event_hand: item_names.event_hand,
    loc_names.event_button_top: item_names.event_button_top,
    loc_names.event_giant_bat: item_names.event_giant_bat,
}

# Any Locations with alternate pickup actors in alternate room states that should also be modified, like the flooded
# room items in Luminous Cavern A (the flooded and non-flooded versions of those rooms are separate room states with
# their own actor lists).
ALT_PICKUP_OFFSETS: dict[str, int] = {
    loc_names.lca17: 0x4A425C,
    loc_names.lca18: 0x4A42A4,
    loc_names.lcb8a: 0x4A5868,
    loc_names.lcb8b: 0x4A5874,
}

# All Locations spat out by Guardian Armor when he gets ground up into scrap spaghetti, mapped to their hardcoded
# numbers in the code that runs during that. Leaving and reentering the room puts it in an alternate state that has
# these pickups just naturally placed in it, which are handled by the regular pickup placement system, but they have to
# be handled separately for when the cutscene spawns them specifically.
GUARDIAN_GRINDER_LOCATIONS: dict[str, int] = {
    loc_names.cra17a: 0x1A2DA,
    loc_names.cra17b: 0x1A304,
    loc_names.cra17c: 0x1A2AE,
    loc_names.cra17d: 0x1A280,
}

def get_location_names_to_ids() -> dict[str, int]:
    return {name: CVHODIS_LOCATIONS_INFO[name].code+BASE_ID for name in CVHODIS_LOCATIONS_INFO}


def get_location_name_groups() -> dict[str, dict[str]]:
    loc_name_groups: dict[str, set[str]] = dict()

    for loc_name in CVHODIS_LOCATIONS_INFO:
        # If we are looking at an event Location, don't include it.
        if isinstance(CVHODIS_LOCATIONS_INFO[loc_name].code, str):
            continue

        # The part of the Location name's string before the colon is its area name.
        area_name = loc_name.split(":")[0]

        # Add each Location to its corresponding area name group.
        if area_name not in loc_name_groups:
            loc_name_groups[area_name] = {loc_name}
        else:
            loc_name_groups[area_name].add(loc_name)

    return loc_name_groups


def get_locations_to_create(locations: list[str], options: CVHoDisOptions) -> \
        tuple[dict[str, int | None], dict[str, str]]:
    """Verifies which Locations in a given list should be created. A dict will be returned with verified Location names
    mapped to their IDs, ready to be created with Region.add_locations, as well as a dict of Locations that should have
    corresponding locked Items placed on them."""
    locations_with_ids = {}
    locked_pairs = {}

    for loc in locations:

        # Don't place the Medium Ending Location if we don't have it required.
        if loc == loc_names.event_ending_m and not options.medium_ending_required:
            continue

        # Don't place the Worst Ending Location if we don't have it required.
        if loc == loc_names.event_ending_b and not options.worst_ending_required:
            continue

        # Don't place the Best Ending Location if we don't have it required.
        if loc == loc_names.event_ending_g and not options.best_ending_required:
            continue

        # Don't place the Furniture Event Location if no furniture amount is required.
        if loc == loc_names.event_furniture and not options.furniture_amount_required:
            continue

        # Don't place the Death Event Location if the Castle Warp Condition is not Death.
        if loc == loc_names.event_death and options.castle_warp_condition != CastleWarpCondition.option_death:
            continue

        # Check to see if the Location is in the Checks Info dict.
        # If it is, then handle it like a regular check Location.
        if loc in CVHODIS_LOCATIONS_INFO:
            # Grab its code from the Checks Info and add the base ID to it.
            loc_code = CVHODIS_LOCATIONS_INFO[loc].code + BASE_ID
        # Check to see if the Location is in the Events Mapping dict.
        # If it is, then handle it like an event Location.
        elif loc in CVHODIS_EVENT_MAPPING:
            # Set its code to None and lock its associated event Item on it.
            loc_code = None
            locked_pairs[loc] = CVHODIS_EVENT_MAPPING[loc]
        else:
            # If we make it here, meaning the Location is undefined in both dicts, throw an error and skip creating it.
            logging.error(f"The Location \"{loc}\" is not in either CVHODIS_LOCATIONS_INFO or CVHODIS_EVENT_MAPPING. "
                          f"Please add it to one or the other to create it properly.")
            continue

        # Update the dict containing our Locations to create for the Region.
        locations_with_ids.update({loc: loc_code})

    return locations_with_ids, locked_pairs
