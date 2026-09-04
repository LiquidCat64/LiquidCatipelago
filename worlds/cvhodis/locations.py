import logging

from BaseClasses import Location
from .data.misc_names import GAME_NAME
from .data import loc_names, item_names
from .options import CVHoDisOptions, CastleWarpCondition

from typing import NamedTuple


class CVHoDisLocation(Location):
    game: str = GAME_NAME


class CVHoDisLocationData(NamedTuple):
    code: int # The Location object's unique code attribute, as well as the in-game pickup flag ID. The 6th and higher
              # bits in the number represent which word starting from 0x02000330 the bitflag is in, and the 5 lower
              # bits represent which bit in said word is the bitflag.
    # countdown: int | None # Coming soon(tm)
    item: str # What Item to add to the AP itempool if that Location is added. Usually but not always, this is the Item
              # that's normally there in the vanilla game.


CVHODIS_LOCATIONS_INFO: dict[str, CVHoDisLocationData] = {
    # Various areas
    loc_names.portals_rt: CVHoDisLocationData(0x2F, item_names.equip_l_charm),
    loc_names.portals_lw: CVHoDisLocationData(0x88, item_names.equip_glove_s),

    # Entrance A
    loc_names.eta2:  CVHoDisLocationData(0xB2, item_names.use_prism_b),
    loc_names.eta3:  CVHoDisLocationData(0x2E, item_names.equip_armor_ma),
    loc_names.eta5a: CVHoDisLocationData(0xB5, item_names.use_potion),
    loc_names.eta5b: CVHoDisLocationData(0xB6, item_names.use_potion),
    loc_names.eta7:  CVHoDisLocationData(0x64, item_names.max_heart),
    loc_names.eta9:  CVHoDisLocationData(0x2B, item_names.whip_plat),
    loc_names.eta10: CVHoDisLocationData(0xAC, item_names.equip_boots_l),
    loc_names.eta11: CVHoDisLocationData(0x0F, item_names.relic_orb),
    loc_names.eta13: CVHoDisLocationData(0x46, item_names.max_life),
    loc_names.eta17: CVHoDisLocationData(0x08, item_names.use_hint_3),
    loc_names.eta18: CVHoDisLocationData(0x3C, item_names.equip_bracelet_jb),
    loc_names.eta19: CVHoDisLocationData(0x82, item_names.equip_armor_l),

    # Entrance B
    loc_names.etb0:   CVHoDisLocationData(0xA2, item_names.equip_w_fatigues),
    loc_names.etb2a:  CVHoDisLocationData(0xE0, item_names.furn_urn_a),
    loc_names.etb2b:  CVHoDisLocationData(0xE1, item_names.use_prism_b),
    loc_names.etb3:   CVHoDisLocationData(0x14, item_names.relic_v_rib),
    loc_names.etb9:   CVHoDisLocationData(0x0A, item_names.use_key_l),
    loc_names.etb11:  CVHoDisLocationData(0x77, item_names.max_heart),
    loc_names.etb13a: CVHoDisLocationData(0xE3, item_names.furn_vase),
    loc_names.etb13b: CVHoDisLocationData(0xE4, item_names.use_potion_h),
    loc_names.etb13c: CVHoDisLocationData(0xE7, item_names.use_prism_b),

    # Marble Corridor A
    loc_names.mca2a:  CVHoDisLocationData(0x65, item_names.max_heart),
    loc_names.mca2b:  CVHoDisLocationData(0x19, item_names.book_ice),
    loc_names.mca4:   CVHoDisLocationData(0x23, item_names.use_map_1),
    loc_names.mca7:   CVHoDisLocationData(0xA7, item_names.equip_glove_l),
    loc_names.mca9a:  CVHoDisLocationData(0x18, item_names.book_fire),
    loc_names.mca9b:  CVHoDisLocationData(0x9C, item_names.equip_summer),
    loc_names.mca10:  CVHoDisLocationData(0x26, item_names.whip_red),
    loc_names.mca11a: CVHoDisLocationData(0xB7, item_names.use_a_venom),
    loc_names.mca11b: CVHoDisLocationData(0x67, item_names.max_heart),
    loc_names.mca11c: CVHoDisLocationData(0xB9, item_names.use_potion),
    loc_names.mca11d: CVHoDisLocationData(0xB8, item_names.use_a_venom),
    loc_names.mca11e: CVHoDisLocationData(0x17, item_names.relic_v_ring),
    loc_names.mca11f: CVHoDisLocationData(0x66, item_names.max_heart),
    loc_names.mca12:  CVHoDisLocationData(0x48, item_names.max_life),
    loc_names.mca13:  CVHoDisLocationData(0x10, item_names.relic_journal),
    loc_names.mca14:  CVHoDisLocationData(0xBB, item_names.use_potion),

    # Room of Illusion A
    loc_names.ria15: CVHoDisLocationData(0x90, item_names.equip_bandana),
    loc_names.ria16: CVHoDisLocationData(0x47, item_names.max_life),
    loc_names.ria17: CVHoDisLocationData(0x68, item_names.max_heart),

    # Marble Corridor B
    loc_names.mcb2:  CVHoDisLocationData(0x59, item_names.max_life),
    loc_names.mcb9:  CVHoDisLocationData(0xA6, item_names.equip_cloak_t),
    loc_names.mcb10: CVHoDisLocationData(0xEB, item_names.use_potion_h),
    loc_names.mcb11: CVHoDisLocationData(0x9B, item_names.equip_helm_v),
    loc_names.mcb12: CVHoDisLocationData(0x78, item_names.max_heart),

    # Room of Illusion B
    loc_names.rib16: CVHoDisLocationData(0xED, item_names.furn_curtain),
    loc_names.rib19: CVHoDisLocationData(0x5B, item_names.max_life),

    # The Wailing Way A
    loc_names.wwa0a: CVHoDisLocationData(0xA3, item_names.equip_cloak_s),
    loc_names.wwa0b: CVHoDisLocationData(0x11, item_names.relic_tome),
    loc_names.wwa0c: CVHoDisLocationData(0x49, item_names.max_life),
    loc_names.wwa0d: CVHoDisLocationData(0xBC, item_names.use_drumstick),
    loc_names.wwa1:  CVHoDisLocationData(0xBA, item_names.use_prism),
    loc_names.wwa3:  CVHoDisLocationData(0x83, item_names.use_potion),
    loc_names.wwa4a: CVHoDisLocationData(0x30, item_names.equip_ring_lo),
    loc_names.wwa4b: CVHoDisLocationData(0x9D, item_names.equip_clothes_f),
    loc_names.wwa8:  CVHoDisLocationData(0x69, item_names.max_heart),

    # Shrine of the Apostates A
    loc_names.saa6a:  CVHoDisLocationData(0xBE, item_names.use_drumstick),
    loc_names.saa6b:  CVHoDisLocationData(0xBF, item_names.use_gem_o),
    loc_names.saa7:   CVHoDisLocationData(0x2C, item_names.whip_circle),
    loc_names.saa10:  CVHoDisLocationData(0xBD, item_names.use_potion),
    loc_names.saa12:  CVHoDisLocationData(0x4A, item_names.max_life),
    loc_names.saa15:  CVHoDisLocationData(0x01, item_names.relic_tail),
    loc_names.saa16:  CVHoDisLocationData(0x4B, item_names.max_life),

    # The Wailing Way B
    loc_names.wwb0a:  CVHoDisLocationData(0x5A, item_names.max_life),
    loc_names.wwb0b:  CVHoDisLocationData(0xEE, item_names.use_a_venom),
    loc_names.wwb3:   CVHoDisLocationData(0xF0, item_names.furn_candle_h),
    loc_names.wwb4a:  CVHoDisLocationData(0x04, item_names.equip_boots_c),
    loc_names.wwb4b:  CVHoDisLocationData(0xF2, item_names.furn_statue_sm),
    loc_names.wwb4c:  CVHoDisLocationData(0xF3, item_names.use_potion),

    # Shrine of the Apostates B
    loc_names.sab5:   CVHoDisLocationData(0xF5, item_names.use_turkey),
    loc_names.sab7:   CVHoDisLocationData(0x7A, item_names.max_heart),
    loc_names.sab11:  CVHoDisLocationData(0xF6, item_names.use_drumstick),
    loc_names.sab12:  CVHoDisLocationData(0xF7, item_names.use_elixir),
    loc_names.sab15:  CVHoDisLocationData(0x79, item_names.max_heart),

    # Castle Treasury A
    loc_names.cya0a:  CVHoDisLocationData(0xCB, item_names.furn_teacup),
    loc_names.cya0b:  CVHoDisLocationData(0xCC, item_names.furn_teapot),
    loc_names.cya1:   CVHoDisLocationData(0x52, item_names.max_life),
    loc_names.cya4:   CVHoDisLocationData(0x3D, item_names.equip_mail_ce),
    loc_names.cya6:   CVHoDisLocationData(0x34, item_names.equip_g_amulet),
    loc_names.cya8:   CVHoDisLocationData(0xCD, item_names.use_potion),
    loc_names.cya9:   CVHoDisLocationData(0xCE, item_names.furn_closet),
    loc_names.cya10:  CVHoDisLocationData(0x8C, item_names.equip_mail_p),
    loc_names.cya11:  CVHoDisLocationData(0x71, item_names.max_heart),
    loc_names.cya12:  CVHoDisLocationData(0x32, item_names.equip_ring_he),
    loc_names.cya18:  CVHoDisLocationData(0x31, item_names.equip_ring_ho),
    loc_names.cya19:  CVHoDisLocationData(0xCF, item_names.furn_chan),
    loc_names.cya20a: CVHoDisLocationData(0x85, item_names.equip_p_shoes),
    loc_names.cya20b: CVHoDisLocationData(0x33, item_names.equip_armor_mo),

    # Castle Treasury B
    loc_names.cyb0a:  CVHoDisLocationData(0x1F,  item_names.equip_wristband),
    loc_names.cyb0b:  CVHoDisLocationData(0x102, item_names.use_uncurse),
    loc_names.cyb1:   CVHoDisLocationData(0x7B,  item_names.max_heart),
    loc_names.cyb5:   CVHoDisLocationData(0x5D,  item_names.max_life),
    loc_names.cyb8:   CVHoDisLocationData(0x24,  item_names.use_potion),
    loc_names.cyb11:  CVHoDisLocationData(0x103, item_names.furn_chair),
    loc_names.cyb12:  CVHoDisLocationData(0x84,  item_names.equip_tunic),
    loc_names.cyb18a: CVHoDisLocationData(0x86,  item_names.equip_armor_pad),
    loc_names.cyb18b: CVHoDisLocationData(0x7C,  item_names.max_heart),
    loc_names.cyb20:  CVHoDisLocationData(0x42,  item_names.equip_armor_su),

    # Skeleton Cave A
    loc_names.sca1a:  CVHoDisLocationData(0xA1, item_names.equip_robe_l),
    loc_names.sca1b:  CVHoDisLocationData(0xC8, item_names.furn_phono),
    loc_names.sca2:   CVHoDisLocationData(0xC9, item_names.furn_shelf),
    loc_names.sca4:   CVHoDisLocationData(0x72, item_names.max_heart),
    loc_names.sca5:   CVHoDisLocationData(0x54, item_names.max_life),
    loc_names.sca10:  CVHoDisLocationData(0x36, item_names.equip_cipher),
    loc_names.sca11:  CVHoDisLocationData(0x35, item_names.equip_ring_r),
    loc_names.sca12a: CVHoDisLocationData(0xCA, item_names.use_prism_b),
    loc_names.sca12b: CVHoDisLocationData(0x53, item_names.max_life),
    loc_names.sca13:  CVHoDisLocationData(0x02, item_names.use_key_f),
    loc_names.sca19:  CVHoDisLocationData(0x21, item_names.use_hint_5),

    # Skeleton Cave B
    loc_names.scb1a:  CVHoDisLocationData(0xFC, item_names.use_potion),
    loc_names.scb1b:  CVHoDisLocationData(0xAD, item_names.equip_guard_a),
    loc_names.scb2:   CVHoDisLocationData(0x7D, item_names.max_heart),
    loc_names.scb3:   CVHoDisLocationData(0x2D, item_names.whip_bullet),
    loc_names.scb4:   CVHoDisLocationData(0xFD, item_names.furn_table_s),
    loc_names.scb5:   CVHoDisLocationData(0xFE, item_names.furn_stag),
    loc_names.scb10:  CVHoDisLocationData(0x06, item_names.relic_feather),
    loc_names.scb11:  CVHoDisLocationData(0x5E, item_names.max_life),
    loc_names.scb12a: CVHoDisLocationData(0x1C, item_names.book_summon),
    loc_names.scb12b: CVHoDisLocationData(0xFF, item_names.furn_urn_w),
    loc_names.scb13:  CVHoDisLocationData(0x92, item_names.equip_cap),

    # Luminous Cavern A
    loc_names.lca3:   CVHoDisLocationData(0xD0, item_names.use_drumstick),
    loc_names.lca7a:  CVHoDisLocationData(0x76, item_names.max_heart),
    loc_names.lca7b:  CVHoDisLocationData(0x99, item_names.equip_helm_f),
    loc_names.lca8a:  CVHoDisLocationData(0x6B, item_names.max_heart),
    loc_names.lca8b:  CVHoDisLocationData(0x58, item_names.max_life),
    loc_names.lca8c:  CVHoDisLocationData(0x6C, item_names.max_heart),
    loc_names.lca10:  CVHoDisLocationData(0x09, item_names.use_key_s),
    loc_names.lca11:  CVHoDisLocationData(0x3E, item_names.equip_crown),
    loc_names.lca14:  CVHoDisLocationData(0x1D, item_names.use_hint_1),
    loc_names.lca17:  CVHoDisLocationData(0xAB, item_names.equip_arm_p),
    loc_names.lca18:  CVHoDisLocationData(0xB0, item_names.equip_leggings),
    loc_names.lca22:  CVHoDisLocationData(0xD2, item_names.use_medicine),
    loc_names.lca23:  CVHoDisLocationData(0x03, item_names.relic_wing),

    # Luminous Cavern B
    loc_names.lcb3:   CVHoDisLocationData(0x104, item_names.use_gem_t),
    loc_names.lcb7a:  CVHoDisLocationData(0x10B, item_names.use_prism),
    loc_names.lcb7b:  CVHoDisLocationData(0x10C, item_names.furn_statue_sa),
    loc_names.lcb8a:  CVHoDisLocationData(0x44,  item_names.equip_armor_w),
    loc_names.lcb8b:  CVHoDisLocationData(0x10D, item_names.use_elixir),
    loc_names.lcb10a: CVHoDisLocationData(0x28,  item_names.whip_yellow),
    loc_names.lcb10b: CVHoDisLocationData(0x10F, item_names.furn_mirror),
    loc_names.lcb13:  CVHoDisLocationData(0x10E, item_names.furn_dishes),
    loc_names.lcb16:  CVHoDisLocationData(0x63,  item_names.max_life),
    loc_names.lcb17:  CVHoDisLocationData(0x81,  item_names.max_heart),
    loc_names.lcb18:  CVHoDisLocationData(0x110, item_names.use_potion_h),
    loc_names.lcb22a: CVHoDisLocationData(0x111, item_names.use_potion),
    loc_names.lcb22b: CVHoDisLocationData(0x112, item_names.use_uncurse),

    # Sky Walkway A
    loc_names.swa7:   CVHoDisLocationData(0x07, item_names.equip_bracelet_mk),
    loc_names.swa10a: CVHoDisLocationData(0xD6, item_names.use_a_venom),
    loc_names.swa10b: CVHoDisLocationData(0xD7, item_names.use_potion_h),
    loc_names.swa10c: CVHoDisLocationData(0x56, item_names.max_life),
    loc_names.swa12a: CVHoDisLocationData(0xD9, item_names.furn_trinket_s),
    loc_names.swa12b: CVHoDisLocationData(0xDA, item_names.furn_trinket_g),
    loc_names.swa12c: CVHoDisLocationData(0xDB, item_names.use_elixir),
    loc_names.swa14:  CVHoDisLocationData(0x3A, item_names.equip_goggles),
    loc_names.swa15a: CVHoDisLocationData(0xDC, item_names.use_medicine),
    loc_names.swa15b: CVHoDisLocationData(0xDD, item_names.use_medicine),
    loc_names.swa17:  CVHoDisLocationData(0x94, item_names.equip_guard_f),
    loc_names.swa18a: CVHoDisLocationData(0x3B, item_names.equip_ring_c),
    loc_names.swa18b: CVHoDisLocationData(0x1E, item_names.use_hint_2),

    # Chapel of Dissonance A
    loc_names.cda0a: CVHoDisLocationData(0x4D, item_names.max_life),
    loc_names.cda0b: CVHoDisLocationData(0xD3, item_names.use_potion),
    loc_names.cda0c: CVHoDisLocationData(0xA4, item_names.equip_cloak_e),
    loc_names.cda0d: CVHoDisLocationData(0x12, item_names.relic_v_eye),
    loc_names.cda0e: CVHoDisLocationData(0x6A, item_names.max_heart),
    loc_names.cda2:  CVHoDisLocationData(0xD5, item_names.use_a_venom),

    # Sky Walkway B
    loc_names.swb8:   CVHoDisLocationData(0x60,  item_names.max_life),
    loc_names.swb10a: CVHoDisLocationData(0x9F,  item_names.equip_robe_b),
    loc_names.swb10b: CVHoDisLocationData(0x118, item_names.furn_radio),
    loc_names.swb10c: CVHoDisLocationData(0x119, item_names.furn_chair_r),
    loc_names.swb12a: CVHoDisLocationData(0x80,  item_names.max_heart),
    loc_names.swb12b: CVHoDisLocationData(0x11A, item_names.furn_bed),
    loc_names.swb14:  CVHoDisLocationData(0x8A,  item_names.use_prism),
    loc_names.swb15:  CVHoDisLocationData(0x13,  item_names.relic_v_heart),
    loc_names.swb16:  CVHoDisLocationData(0x11B, item_names.use_turkey),
    loc_names.swb19:  CVHoDisLocationData(0x7F,  item_names.max_heart),

    # Chapel of Dissonance B
    loc_names.cdb0a: CVHoDisLocationData(0x115, item_names.use_prism_b),
    loc_names.cdb0b: CVHoDisLocationData(0x6F,  item_names.max_heart),
    loc_names.cdb0c: CVHoDisLocationData(0x4F,  item_names.max_life),
    loc_names.cdb0d: CVHoDisLocationData(0x22,  item_names.use_hint_6),
    loc_names.cdb0e: CVHoDisLocationData(0x116, item_names.furn_statue_h),
    loc_names.cdb4:  CVHoDisLocationData(0x117, item_names.use_potion_h),

    # Aqueduct of Dragons A
    loc_names.ada1:   CVHoDisLocationData(0x15, item_names.relic_v_nail),
    loc_names.ada2:   CVHoDisLocationData(0xA9, item_names.equip_glove_h),
    loc_names.ada4:   CVHoDisLocationData(0x74, item_names.max_heart),
    loc_names.ada8:   CVHoDisLocationData(0x27, item_names.whip_blue),
    loc_names.ada10a: CVHoDisLocationData(0x57, item_names.max_life),
    loc_names.ada10b: CVHoDisLocationData(0x75, item_names.max_heart),

    # Aqueduct of Dragons B
    loc_names.adb0: CVHoDisLocationData(0x43,  item_names.equip_ring_e),
    loc_names.adb1: CVHoDisLocationData(0x61,  item_names.max_life),
    loc_names.adb2: CVHoDisLocationData(0x113, item_names.use_uncurse),
    loc_names.adb4: CVHoDisLocationData(0x114, item_names.use_elixir),
    loc_names.adb8: CVHoDisLocationData(0x62,  item_names.max_life),

    # Clock Tower A
    loc_names.cra0:   CVHoDisLocationData(0x95, item_names.equip_bagonette),
    loc_names.cra1:   CVHoDisLocationData(0x20, item_names.use_hint_4),
    loc_names.cra2:   CVHoDisLocationData(0x55, item_names.max_life),
    loc_names.cra3:   CVHoDisLocationData(0x89, item_names.equip_armor_sc),
    loc_names.cra9:   CVHoDisLocationData(0x73, item_names.max_heart),
    loc_names.cra10:  CVHoDisLocationData(0x25, item_names.use_map_3),
    loc_names.cra14:  CVHoDisLocationData(0xDE, item_names.furn_table_a),
    loc_names.cra17a: CVHoDisLocationData(0x0D, item_names.equip_guardian_g),
    loc_names.cra17b: CVHoDisLocationData(0x0E, item_names.equip_guardian_b),
    loc_names.cra17c: CVHoDisLocationData(0x0C, item_names.equip_guardian_h),
    # NOTE: For some reason, DSVania Editor has the wrong address for cra17d. 0x4AAC98 is for the top gear in this room.
    loc_names.cra17d: CVHoDisLocationData(0x0B, item_names.equip_guardian_a),
    loc_names.cra20:  CVHoDisLocationData(0x29, item_names.whip_green),
    loc_names.cra22a: CVHoDisLocationData(0xDF, item_names.furn_cat),
    loc_names.cra22b: CVHoDisLocationData(0x1A, item_names.book_bolt),
    loc_names.cra22c: CVHoDisLocationData(0x4E, item_names.max_life),
    loc_names.cra22d: CVHoDisLocationData(0x6E, item_names.max_heart),
    loc_names.cra23:  CVHoDisLocationData(0x16, item_names.relic_v_fang),

    # Clock Tower B
    loc_names.crb1:   CVHoDisLocationData(0x45,  item_names.equip_kaiser),
    loc_names.crb2:   CVHoDisLocationData(0xA5,  item_names.equip_cloak_w),
    loc_names.crb3:   CVHoDisLocationData(0x105, item_names.use_elixir),
    loc_names.crb4:   CVHoDisLocationData(0x4C,  item_names.max_life),
    loc_names.crb6a:  CVHoDisLocationData(0x106, item_names.use_prism_b),
    loc_names.crb6b:  CVHoDisLocationData(0x107, item_names.use_potion_h),
    loc_names.crb8:   CVHoDisLocationData(0x108, item_names.use_medicine),
    loc_names.crb10:  CVHoDisLocationData(0x05,  item_names.whip_crush),
    loc_names.crb13:  CVHoDisLocationData(0x109, item_names.furn_clock),
    # NOTE: DSVania Editor has the wrong address for crb17 as well. 0x4AC5A0 is for the White Dragon Lv2.
    loc_names.crb17:  CVHoDisLocationData(0x7E,  item_names.max_heart),
    loc_names.crb20:  CVHoDisLocationData(0x5F,  item_names.max_life),
    loc_names.crb22a: CVHoDisLocationData(0x37,  item_names.equip_h_choker),
    loc_names.crb22b: CVHoDisLocationData(0x38,  item_names.equip_mail_h),
    loc_names.crb23a: CVHoDisLocationData(0x10A, item_names.furn_raccoon),
    loc_names.crb23b: CVHoDisLocationData(0x39,  item_names.equip_ring_lu),

    # Castle Top Floor A
    loc_names.tfa0a: CVHoDisLocationData(0xC0, item_names.use_elixir),
    loc_names.tfa0b: CVHoDisLocationData(0xC1, item_names.use_turkey),
    loc_names.tfa0c: CVHoDisLocationData(0xC2, item_names.furn_candle_s),
    loc_names.tfa0d: CVHoDisLocationData(0x50, item_names.max_life),
    loc_names.tfa0e: CVHoDisLocationData(0xC3, item_names.use_prism_b),
    loc_names.tfa1a: CVHoDisLocationData(0x51, item_names.max_life),
    loc_names.tfa1b: CVHoDisLocationData(0x70, item_names.max_heart),
    loc_names.tfa7:  CVHoDisLocationData(0xC4, item_names.furn_drawing),
    loc_names.tfa8:  CVHoDisLocationData(0xC5, item_names.use_elixir),
    loc_names.tfa9:  CVHoDisLocationData(0x8E, item_names.equip_armor_si),
    loc_names.tfa11: CVHoDisLocationData(0x2A, item_names.whip_steel),
    loc_names.tfa15: CVHoDisLocationData(0x87, item_names.equip_brooch),

    # Castle Top Floor B
    loc_names.tfb0a:  CVHoDisLocationData(0x8F, item_names.equip_mail_k),
    loc_names.tfb0b:  CVHoDisLocationData(0x40, item_names.use_medicine),
    loc_names.tfb0c:  CVHoDisLocationData(0x41, item_names.use_medicine),
    loc_names.tfb0d:  CVHoDisLocationData(0x6D, item_names.max_heart),
    loc_names.tfb0e:  CVHoDisLocationData(0xF9, item_names.furn_glass),
    loc_names.tfb3:   CVHoDisLocationData(0x3F, item_names.equip_robe_m),
    loc_names.tfb5:   CVHoDisLocationData(0xFA, item_names.use_potion),
    loc_names.tfb7:   CVHoDisLocationData(0xFB, item_names.use_potion_h),
    loc_names.tfb11a: CVHoDisLocationData(0x5C, item_names.max_life),
    loc_names.tfb11b: CVHoDisLocationData(0x1B, item_names.book_wind),
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

def get_location_names_to_ids() -> dict[str, int]:
    return {name: CVHODIS_LOCATIONS_INFO[name].code for name in CVHODIS_LOCATIONS_INFO}


def get_location_name_groups() -> dict[str, set[str]]:
    loc_name_groups: dict[str, set[str]] = dict()

    for loc_name in CVHODIS_LOCATIONS_INFO:
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

        # Check to see if the Location is in the Locations Info dict.
        # If it is, then handle it like a regular check Location.
        if loc in CVHODIS_LOCATIONS_INFO:
            # Grab its code from the Locations Info and add the base ID to it.
            loc_code = CVHODIS_LOCATIONS_INFO[loc].code
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
