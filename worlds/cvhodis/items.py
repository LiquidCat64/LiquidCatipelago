from BaseClasses import Item, ItemClassification
from .data import item_names
from .data.enums import PickupTypes, FillerTypes, EventFlags, SubWeaponPickups
from .data.misc_names import GAME_NAME
from .locations import CVHODIS_LOCATIONS_INFO

import logging
from typing import TYPE_CHECKING, NamedTuple

from .options import GateItems, FillerPool

if TYPE_CHECKING:
    from . import CVHoDisWorld


class CVHoDisItem(Item):
    game: str = GAME_NAME


class CVHoDisItemData(NamedTuple):
    pickup_index: int
    gfx_id: int
    palette_id: int
    default_classification: ItemClassification = ItemClassification.filler
    filler_type: str = ""
# "pickup_index" = The lower half of the unique part of the Item's AP code attribute, as well as the value to write
#                  in-game to insert that Item on a Location alongside its pickup type value. Add this + its pickup type
#                  right-shifted by 8 + base_id to get the Item's final AP code.
# "gfx_id" = The in-game ID for the Item's sprite's GFX data in the sprite sheets.
#            Used for changing an Item's appearance independent of what it really is.
# "palette_id" = The in-game ID for what palette the Item's sprite uses.
#                Used for changing an Item's appearance independent of what it really is.
# "default_classification" = The AP Item Classification that gets assigned to instances of that Item in create_item
#                            by default, unless I deliberately override it (as is the case for the Cleansing on the
#                            Ignore Cleansing option).
# "filler_type" = What group of filler it belongs to, for the purposes of the Mystery Item Pool Fill.


class CVHoDisFillerCategoryData(NamedTuple):
    weight: int
    choices: list[str]
    renewable: bool = False
# "weight" = The weight value associated with the category when a category is randomly chosen.
# "choices" = List of the names of the Items associated with the category.
#             When the category is chosen, an Item from this list will be randomly chosen.
# "renewable" = Whether Items in this category can be chosen multiple times. If not, chosen Items will be
#               removed from the list so a slot cannot add multiple instances of the same Item.

HEARTS: dict[str, CVHoDisItemData] = {
    item_names.heart_s:   CVHoDisItemData(0x00, 0x00, 0x00),
    item_names.heart_b:   CVHoDisItemData(0x01, 0x00, 0x00),
}

MONEY: dict[str, CVHoDisItemData] = {
    item_names.money_1:   CVHoDisItemData(0x00, 0x09, 0x01, filler_type=FillerTypes.MONEY),
    item_names.money_5:   CVHoDisItemData(0x01, 0x07, 0x01, filler_type=FillerTypes.MONEY),
    item_names.money_25:  CVHoDisItemData(0x02, 0x08, 0x01, filler_type=FillerTypes.MONEY),
    item_names.money_100: CVHoDisItemData(0x03, 0x8C, 0x01, filler_type=FillerTypes.MONEY),
    item_names.money_250: CVHoDisItemData(0x04, 0x8D, 0x01, filler_type=FillerTypes.MONEY),
    item_names.money_400: CVHoDisItemData(0x05, 0x8E, 0x01, filler_type=FillerTypes.MONEY),
}

SUB_WEAPONS: dict[str, CVHoDisItemData] = {
    item_names.sub_book:  CVHoDisItemData(SubWeaponPickups.HOLY_BOOK.value,   0x01, 0x01),
    item_names.sub_cross: CVHoDisItemData(SubWeaponPickups.CROSS.value,       0x02, 0x01),
    item_names.sub_axe:   CVHoDisItemData(SubWeaponPickups.AXE.value,         0x03, 0x01),
    item_names.sub_holy:  CVHoDisItemData(SubWeaponPickups.HOLY_WATER.value,  0x04, 0x01),
    item_names.sub_fist:  CVHoDisItemData(SubWeaponPickups.SACRED_FIST.value, 0x05, 0x01),
    item_names.sub_knife: CVHoDisItemData(SubWeaponPickups.KNIFE.value,       0x06, 0x01),
}

USE_ITEMS: dict[str, CVHoDisItemData] = {
    item_names.use_potion:    CVHoDisItemData(0x00, 0x15, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_potion_h:  CVHoDisItemData(0x01, 0x16, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_elixir:    CVHoDisItemData(0x02, 0x80, 0x01, ItemClassification.useful,
                                              filler_type=FillerTypes.GOOD_CONSUMABLE),
    item_names.use_prism:     CVHoDisItemData(0x03, 0x17, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_prism_b:   CVHoDisItemData(0x04, 0x18, 0x01, ItemClassification.useful,
                                              filler_type=FillerTypes.GOOD_CONSUMABLE),
    item_names.use_drumstick: CVHoDisItemData(0x05, 0x0A, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_turkey:    CVHoDisItemData(0x06, 0x0B, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_a_venom:   CVHoDisItemData(0x07, 0x0E, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_uncurse:   CVHoDisItemData(0x08, 0x0F, 0x01, filler_type=FillerTypes.CONSUMABLE),
    item_names.use_medicine:  CVHoDisItemData(0x09, 0x82, 0x01, ItemClassification.useful,
                                              filler_type=FillerTypes.GOOD_CONSUMABLE),
    item_names.use_key_l:     CVHoDisItemData(0x0A, 0x1F, 0x02, ItemClassification.progression),
    item_names.use_key_s:     CVHoDisItemData(0x0B, 0x7F, 0x02, ItemClassification.progression),
    item_names.use_key_f:     CVHoDisItemData(0x0C, 0x20, 0x08, ItemClassification.progression),
    item_names.use_map_1:     CVHoDisItemData(0x0D, 0x7E, 0x02),
    item_names.use_map_2:     CVHoDisItemData(0x0E, 0x7E, 0x02),
    item_names.use_map_3:     CVHoDisItemData(0x0F, 0x7E, 0x02),
    item_names.use_hint_1:    CVHoDisItemData(0x10, 0x10, 0x01, ItemClassification.useful),
    item_names.use_hint_2:    CVHoDisItemData(0x11, 0x10, 0x01, ItemClassification.useful),
    item_names.use_hint_3:    CVHoDisItemData(0x12, 0x10, 0x01, ItemClassification.useful),
    item_names.use_hint_4:    CVHoDisItemData(0x13, 0x10, 0x01, ItemClassification.useful),
    item_names.use_hint_5:    CVHoDisItemData(0x14, 0x10, 0x01, ItemClassification.useful),
    item_names.use_hint_6:    CVHoDisItemData(0x15, 0x10, 0x01, ItemClassification.useful),
    item_names.use_n_star:    CVHoDisItemData(0x16, 0x92, 0x01, ItemClassification.useful),
    item_names.use_gem_o:     CVHoDisItemData(0x17, 0x90, 0x05, filler_type=FillerTypes.MONEY),
    item_names.use_gem_t:     CVHoDisItemData(0x18, 0x8F, 0x05, filler_type=FillerTypes.MONEY),
    item_names.use_gem_s:     CVHoDisItemData(0x19, 0x12, 0x03, filler_type=FillerTypes.MONEY),
    item_names.use_gem_r:     CVHoDisItemData(0x1A, 0x11, 0x02, filler_type=FillerTypes.MONEY),
    item_names.use_gem_d:     CVHoDisItemData(0x1B, 0x91, 0x05, filler_type=FillerTypes.MONEY),
}

WHIP_ATTACHMENTS: dict[str, CVHoDisItemData] = {
    item_names.whip_crush:  CVHoDisItemData(0x00, 0x1D, 0x01, ItemClassification.progression |
                                            ItemClassification.useful),
    item_names.whip_steel:  CVHoDisItemData(0x01, 0xA4, 0x02, ItemClassification.useful),
    item_names.whip_plat:   CVHoDisItemData(0x02, 0xA5, 0x02, ItemClassification.useful),
    item_names.whip_circle: CVHoDisItemData(0x03, 0xA6, 0x02, ItemClassification.useful),
    item_names.whip_bullet: CVHoDisItemData(0x04, 0xA7, 0x02, ItemClassification.useful),
    item_names.whip_red:    CVHoDisItemData(0x05, 0x1E, 0x02, ItemClassification.useful),
    item_names.whip_blue:   CVHoDisItemData(0x06, 0xA1, 0x03, ItemClassification.useful),
    item_names.whip_yellow: CVHoDisItemData(0x07, 0xA2, 0x04, ItemClassification.useful),
    item_names.whip_green:  CVHoDisItemData(0x08, 0xA3, 0x05, ItemClassification.useful),
}

EQUIPMENT: dict[str, CVHoDisItemData] = {
    item_names.equip_armor_l:     CVHoDisItemData(0x00, 0xCF, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_r:     CVHoDisItemData(0x01, 0xCE, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_f:     CVHoDisItemData(0x02, 0xC7, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_coat_pl:     CVHoDisItemData(0x03, 0xD6, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_tunic:       CVHoDisItemData(0x04, 0xC4, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_br:    CVHoDisItemData(0x05, 0xCA, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_leather:     CVHoDisItemData(0x06, 0xD0, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_c:     CVHoDisItemData(0x07, 0xD5, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_pad:   CVHoDisItemData(0x08, 0xD1, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_coat_pu:     CVHoDisItemData(0x09, 0xD7, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_par:   CVHoDisItemData(0x0A, 0xD4, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_mail_ch:     CVHoDisItemData(0x0B, 0xC8, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_sc:    CVHoDisItemData(0x0C, 0xD2, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_mail_h:      CVHoDisItemData(0x0D, 0xCC, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_guardian_a:  CVHoDisItemData(0x0E, 0xC9, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_mail_f:      CVHoDisItemData(0x0F, 0x24, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_brigan:      CVHoDisItemData(0x10, 0xDD, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_a:     CVHoDisItemData(0x11, 0xD8, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_h:     CVHoDisItemData(0x12, 0x23, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_mail_p:      CVHoDisItemData(0x13, 0xC6, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_mail_d:      CVHoDisItemData(0x14, 0xD3, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_su:    CVHoDisItemData(0x15, 0xDA, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_armor_mo:    CVHoDisItemData(0x16, 0xD9, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_armor_ba:    CVHoDisItemData(0x17, 0x22, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_armor_w:     CVHoDisItemData(0x18, 0xCD, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_armor_si:    CVHoDisItemData(0x19, 0x21, 0x09, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_mail_ce:     CVHoDisItemData(0x1A, 0xDB, 0x04, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_armor_ma:    CVHoDisItemData(0x1B, 0xDE, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_mail_k:      CVHoDisItemData(0x1C, 0xCB, 0x04, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_casual:      CVHoDisItemData(0x1D, 0xA8, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_summer:      CVHoDisItemData(0x1E, 0x45, 0x09, filler_type=FillerTypes.ARMOR),
    item_names.equip_shirt:       CVHoDisItemData(0x1F, 0x41, 0x09, filler_type=FillerTypes.ARMOR),
    item_names.equip_robe_t:      CVHoDisItemData(0x20, 0x47, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_clothes_f:   CVHoDisItemData(0x21, 0x43, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_clothes_l:   CVHoDisItemData(0x22, 0x42, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_ramil:       CVHoDisItemData(0x23, 0xAA, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_robe_b:      CVHoDisItemData(0x24, 0xAB, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_robe_n:      CVHoDisItemData(0x25, 0x44, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_robe_m:      CVHoDisItemData(0x26, 0x48, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_robe_l:      CVHoDisItemData(0x27, 0xAC, 0x04, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_w_fatigues:  CVHoDisItemData(0x28, 0xA9, 0x06, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_robe_a:      CVHoDisItemData(0x29, 0x46, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_bracelet_jb: CVHoDisItemData(0x2A, 0x14, 0x02, ItemClassification.progression),
    item_names.equip_goggles:     CVHoDisItemData(0x2B, 0x77, 0x02, ItemClassification.progression),
    item_names.equip_bracelet_mk: CVHoDisItemData(0x2C, 0x13, 0x02, ItemClassification.progression),
    item_names.equip_boots_c:     CVHoDisItemData(0x2D, 0x30, 0x02, ItemClassification.progression),
    item_names.equip_bandana:     CVHoDisItemData(0x2E, 0x40, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_turban:      CVHoDisItemData(0x2F, 0x8A, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_circlet:     CVHoDisItemData(0x30, 0x3E, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_cap:         CVHoDisItemData(0x31, 0x35, 0x08, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_c:      CVHoDisItemData(0x32, 0xC2, 0x04, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_l:      CVHoDisItemData(0x33, 0xB5, 0x04, filler_type=FillerTypes.ARMOR),
    item_names.equip_sallet:      CVHoDisItemData(0x34, 0xC1, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_bicocette:   CVHoDisItemData(0x35, 0x37, 0x04, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_gr:     CVHoDisItemData(0x36, 0xBA, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_guard_f:     CVHoDisItemData(0x37, 0x2C, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_pi:     CVHoDisItemData(0x38, 0xBB, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_bagonette:   CVHoDisItemData(0x39, 0xBC, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_barbuta:     CVHoDisItemData(0x3A, 0x2B, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_guardian_h:  CVHoDisItemData(0x3B, 0xC3, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_armet:       CVHoDisItemData(0x3C, 0xB6, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_bascinet:    CVHoDisItemData(0x3D, 0xB7, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_hat_s:       CVHoDisItemData(0x3E, 0xDC, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_b:      CVHoDisItemData(0x3F, 0xB8, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_morion:      CVHoDisItemData(0x40, 0xC0, 0x05, filler_type=FillerTypes.ARMOR),
    item_names.equip_hat_k:       CVHoDisItemData(0x41, 0xBD, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_i:      CVHoDisItemData(0x42, 0x36, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_f:      CVHoDisItemData(0x43, 0x29, 0x09, filler_type=FillerTypes.ARMOR),
    item_names.equip_cabacete:    CVHoDisItemData(0x44, 0xBF, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_helm_po:     CVHoDisItemData(0x45, 0xBE, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_tiara:       CVHoDisItemData(0x46, 0x3D, 0x09, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_helm_s:      CVHoDisItemData(0x47, 0x2A, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_helm_v:      CVHoDisItemData(0x48, 0xB9, 0x05, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_headband:    CVHoDisItemData(0x49, 0x3F, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_crown:       CVHoDisItemData(0x4A, 0x8B, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_hat_rs:      CVHoDisItemData(0x4B, 0x38, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_glove_l:     CVHoDisItemData(0x4C, 0x96, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_gauntlets:   CVHoDisItemData(0x4D, 0x4A, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_glove:       CVHoDisItemData(0x4E, 0x4B, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_glove_h:     CVHoDisItemData(0x4F, 0x49, 0x08, filler_type=FillerTypes.ARMOR),
    item_names.equip_guardian_g:  CVHoDisItemData(0x50, 0x9A, 0x04, filler_type=FillerTypes.ARMOR),
    item_names.equip_arm_g:       CVHoDisItemData(0x51, 0x99, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_arm_p:       CVHoDisItemData(0x52, 0x4C, 0x04, filler_type=FillerTypes.ARMOR),
    item_names.equip_glove_b:     CVHoDisItemData(0x53, 0x98, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_glove_s:     CVHoDisItemData(0x54, 0x97, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_boots_l:     CVHoDisItemData(0x55, 0x27, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_guard_s:     CVHoDisItemData(0x56, 0x26, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_guard_a:     CVHoDisItemData(0x57, 0xB0, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_boots_b:     CVHoDisItemData(0x58, 0xAE, 0x03, filler_type=FillerTypes.ARMOR),
    item_names.equip_guardian_b:  CVHoDisItemData(0x59, 0xAD, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_boots_ir:    CVHoDisItemData(0x5A, 0xAF, 0x02, filler_type=FillerTypes.ARMOR),
    item_names.equip_greaves:     CVHoDisItemData(0x5B, 0xB1, 0x04, filler_type=FillerTypes.ARMOR),
    item_names.equip_leggings:    CVHoDisItemData(0x5C, 0xB2, 0x06, filler_type=FillerTypes.ARMOR),
    item_names.equip_boots_s:     CVHoDisItemData(0x5D, 0x25, 0x09, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_boots_f:     CVHoDisItemData(0x5E, 0xB4, 0x03, ItemClassification.progression |
                                                  ItemClassification.useful),
    item_names.equip_p_shoes:     CVHoDisItemData(0x5F, 0xB3, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.GOOD_ARMOR),
    item_names.equip_boots_in:    CVHoDisItemData(0x60, 0x28, 0x02, ItemClassification.progression |
                                                  ItemClassification.useful),
    item_names.equip_cloak_s:     CVHoDisItemData(0x61, 0x19, 0x09, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cloak_v:     CVHoDisItemData(0x62, 0x95, 0x03, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cloak_e:     CVHoDisItemData(0x63, 0x1C, 0x05, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cloak_w:     CVHoDisItemData(0x64, 0x94, 0x05, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cloak_c:     CVHoDisItemData(0x65, 0x1A, 0x02, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cloak_n:     CVHoDisItemData(0x66, 0x1B, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cloak_t:     CVHoDisItemData(0x67, 0x93, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_wristband:   CVHoDisItemData(0x68, 0x89, 0x02, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_bangle:      CVHoDisItemData(0x69, 0x33, 0x02, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_kaiser:      CVHoDisItemData(0x6A, 0x34, 0x04, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_bangle_s:    CVHoDisItemData(0x6B, 0x31, 0x09, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_c_band:      CVHoDisItemData(0x6C, 0x32, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_pendant:     CVHoDisItemData(0x6D, 0x39, 0x02, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_l_charm:     CVHoDisItemData(0x6E, 0x84, 0x05, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_necklace_g:  CVHoDisItemData(0x6F, 0x85, 0x02, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_necklace_m:  CVHoDisItemData(0x70, 0x3C, 0x05, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_pendant_med: CVHoDisItemData(0x71, 0x87, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_h_choker:    CVHoDisItemData(0x72, 0x86, 0x00, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_g_amulet:    CVHoDisItemData(0x73, 0x3B, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_brooch:      CVHoDisItemData(0x74, 0x3A, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_cipher:      CVHoDisItemData(0x75, 0x83, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_pendant_mir: CVHoDisItemData(0x76, 0x88, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_lu:     CVHoDisItemData(0x77, 0x2E, 0x02, filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_ho:     CVHoDisItemData(0x78, 0x2F, 0x08, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_r:      CVHoDisItemData(0x79, 0x2D, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_c:      CVHoDisItemData(0x7A, 0x9B, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_n:      CVHoDisItemData(0x7B, 0x9C, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_lo:     CVHoDisItemData(0x7C, 0x9D, 0x05, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_he:     CVHoDisItemData(0x7D, 0x9E, 0x04, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_a:      CVHoDisItemData(0x7E, 0x9F, 0x03, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
    item_names.equip_ring_e:      CVHoDisItemData(0x7F, 0xA0, 0x02, ItemClassification.useful,
                                                  filler_type=FillerTypes.ACCESSORY),
}

SPELLBOOKS: dict[str, CVHoDisItemData] = {
    item_names.book_fire:   CVHoDisItemData(0x00, 0x58, 0x02, ItemClassification.useful),
    item_names.book_ice:    CVHoDisItemData(0x01, 0x58, 0x03, ItemClassification.useful),
    item_names.book_bolt:   CVHoDisItemData(0x02, 0x58, 0x04, ItemClassification.useful),
    item_names.book_wind:   CVHoDisItemData(0x03, 0x58, 0x05, ItemClassification.useful),
    item_names.book_summon: CVHoDisItemData(0x04, 0x58, 0x06, ItemClassification.useful),
}

RELICS: dict[str, CVHoDisItemData] = {
    item_names.relic_tail:    CVHoDisItemData(0x00, 0x59, 0x04, ItemClassification.progression |
                                              ItemClassification.useful),
    item_names.relic_feather: CVHoDisItemData(0x01, 0x4F, 0x02, ItemClassification.progression |
                                              ItemClassification.useful),
    item_names.relic_wing:    CVHoDisItemData(0x02, 0x4E, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    item_names.relic_orb:     CVHoDisItemData(0x03, 0x4D, 0x02, ItemClassification.useful),
    item_names.relic_journal: CVHoDisItemData(0x04, 0x56, 0x05, ItemClassification.useful),
    item_names.relic_tome:    CVHoDisItemData(0x05, 0x57, 0x01, ItemClassification.useful),
    item_names.relic_v_eye:   CVHoDisItemData(0x06, 0x50, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    item_names.relic_v_heart: CVHoDisItemData(0x07, 0x51, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    item_names.relic_v_rib:   CVHoDisItemData(0x08, 0x52, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    item_names.relic_v_nail:  CVHoDisItemData(0x09, 0x53, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    item_names.relic_v_fang:  CVHoDisItemData(0x0A, 0x54, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    item_names.relic_v_ring:  CVHoDisItemData(0x0B, 0x55, 0x02, ItemClassification.progression_skip_balancing |
                                              ItemClassification.useful),
    # Rando exclusive
    item_names.relic_height:  CVHoDisItemData(0x0C, 0xE7, 0x01, ItemClassification.progression |
                                              ItemClassification.useful),
}

FURNITURE: dict[str, CVHoDisItemData] = {
    item_names.furn_chan:      CVHoDisItemData(0x00, 0x5A, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_clock:     CVHoDisItemData(0x01, 0x5B, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_shelf:     CVHoDisItemData(0x02, 0x5C, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_radio:     CVHoDisItemData(0x03, 0x5D, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_dishes:    CVHoDisItemData(0x04, 0x5E, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_table_a:   CVHoDisItemData(0x05, 0x5F, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_chair:     CVHoDisItemData(0x06, 0x60, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_chair_r:   CVHoDisItemData(0x07, 0x61, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_curtain:   CVHoDisItemData(0x08, 0x62, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_urn_a:     CVHoDisItemData(0x09, 0x63, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_urn_w:     CVHoDisItemData(0x0A, 0x64, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_vase:      CVHoDisItemData(0x0B, 0x65, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_table_s:   CVHoDisItemData(0x0C, 0x66, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_teacup:    CVHoDisItemData(0x0D, 0x67, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_teapot:    CVHoDisItemData(0x0E, 0x68, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_glass:     CVHoDisItemData(0x0F, 0x69, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_statue_h:  CVHoDisItemData(0x10, 0x6A, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_statue_sm: CVHoDisItemData(0x11, 0x6B, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_statue_sa: CVHoDisItemData(0x12, 0x6C, 0x01,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_raccoon:   CVHoDisItemData(0x13, 0x6D, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_cat:       CVHoDisItemData(0x14, 0x6E, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_phono:     CVHoDisItemData(0x15, 0x6F, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_stag:      CVHoDisItemData(0x16, 0x70, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_candle_h:  CVHoDisItemData(0x17, 0x71, 0x09,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_candle_s:  CVHoDisItemData(0x18, 0x71, 0x08,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_trinket_s: CVHoDisItemData(0x19, 0x72, 0x09,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_trinket_g: CVHoDisItemData(0x1A, 0x72, 0x08,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_mirror:    CVHoDisItemData(0x1B, 0x73, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_drawing:   CVHoDisItemData(0x1C, 0x74, 0x05,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_bed:       CVHoDisItemData(0x1D, 0x75, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    item_names.furn_closet:    CVHoDisItemData(0x1E, 0x76, 0x02,
                                               ItemClassification.progression_deprioritized_skip_balancing),
    # Rando exclusive
    item_names.misc_key_la:    CVHoDisItemData(0x1F, 0xE4, 0x02, ItemClassification.progression),
    item_names.misc_key_c:     CVHoDisItemData(0x20, 0xE5, 0x02, ItemClassification.progression),
    item_names.misc_key_t:     CVHoDisItemData(0x21, 0xE6, 0x02, ItemClassification.progression),
}

MAX_UPS: dict[str, CVHoDisItemData] = {
    item_names.max_life:  CVHoDisItemData(0x00, 0x0C, 0x01, ItemClassification.useful),
    item_names.max_heart: CVHoDisItemData(0x01, 0x0D, 0x01, ItemClassification.useful),
}

PICKUP_TYPE_MAPPINGS = {
    PickupTypes.MONEY:  MONEY,
    PickupTypes.USE_ITEM: USE_ITEMS,
    PickupTypes.WHIP_ATTACHMENT: WHIP_ATTACHMENTS,
    PickupTypes.EQUIPMENT: EQUIPMENT,
    PickupTypes.SPELLBOOK: SPELLBOOKS,
    PickupTypes.RELIC: RELICS,
    PickupTypes.FURNITURE: FURNITURE,
    PickupTypes.MAX_UP: MAX_UPS
}

ALL_CVHODIS_ITEMS: dict[str, CVHoDisItemData] = {item: PICKUP_TYPE_MAPPINGS[pickup_type][item] for pickup_type in
                                                 PICKUP_TYPE_MAPPINGS for item in PICKUP_TYPE_MAPPINGS[pickup_type]}

VLADS = frozenset({item_names.relic_v_eye, item_names.relic_v_rib, item_names.relic_v_fang, item_names.relic_v_nail,
                   item_names.relic_v_heart, item_names.relic_v_ring})

HEIGHTS = frozenset({item_names.relic_feather, item_names.relic_wing})

HINT_CARDS = frozenset({item_names.use_hint_1, item_names.use_hint_2, item_names.use_hint_3, item_names.use_hint_4,
                        item_names.use_hint_5, item_names.use_hint_6})

# All Gate Keys mapped to the event flags corresponding to them.
GATE_KEYS = {item_names.misc_key_la: EventFlags.PRESSED_SHRINE_A_BUTTON,
             item_names.misc_key_c: EventFlags.PRESSED_CLOCK_A_BUTTON,
             item_names.misc_key_t: EventFlags.PRESSED_TOP_A_BUTTON}

CVHODIS_FILLER_CATEGORIES: dict[str, CVHoDisFillerCategoryData] = {
    FillerTypes.ACCESSORY:       CVHoDisFillerCategoryData(18, [name for name, data in ALL_CVHODIS_ITEMS.items()
                                                                if data.filler_type == FillerTypes.ACCESSORY]),
    FillerTypes.GOOD_CONSUMABLE: CVHoDisFillerCategoryData(10, [name for name, data in ALL_CVHODIS_ITEMS.items()
                                                                if data.filler_type == FillerTypes.GOOD_CONSUMABLE],
                                                           renewable=True),
    FillerTypes.GOOD_ARMOR:      CVHoDisFillerCategoryData(15, [name for name, data in ALL_CVHODIS_ITEMS.items()
                                                                if data.filler_type == FillerTypes.GOOD_ARMOR]),
    FillerTypes.MONEY:           CVHoDisFillerCategoryData(10, [name for name, data in ALL_CVHODIS_ITEMS.items()
                                                                if data.filler_type == FillerTypes.MONEY],
                                                           renewable=True),
    FillerTypes.ARMOR:           CVHoDisFillerCategoryData(40, [name for name, data in ALL_CVHODIS_ITEMS.items()
                                                                if data.filler_type == FillerTypes.ARMOR]),
    FillerTypes.CONSUMABLE:      CVHoDisFillerCategoryData(60, [name for name, data in ALL_CVHODIS_ITEMS.items()
                                                                if data.filler_type == FillerTypes.CONSUMABLE],
                                                           renewable=True),
}


def get_pickup_type(item_name: str) -> int | None:
    """ Given the name of an Item, checks to see if it is in any of the Item data dicts mapped to a pickup type ID in
    the pickup types dict and, if it is, returns that items pickup type ID. If it's not in any mapped dict, then None
    will be returned."""
    for pickup_type in PICKUP_TYPE_MAPPINGS:
        if item_name in PICKUP_TYPE_MAPPINGS[pickup_type]:
            return pickup_type
    return None

def get_item_names_to_ids() -> dict[str, int]:
    return {item: PICKUP_TYPE_MAPPINGS[pickup_type][item].pickup_index + (pickup_type << 8)
            for pickup_type in PICKUP_TYPE_MAPPINGS for item in PICKUP_TYPE_MAPPINGS[pickup_type]}


def get_item_pool(world: "CVHoDisWorld") -> list[CVHoDisItem]:
    """Builds the player's entire Item pool based on a number of factors, including what Locations are created, chosen
    Options, etc."""

    active_locations = world.multiworld.get_unfilled_locations(world.player)

    tier_1_filler = []
    tier_2_filler = []
    tier_3_filler = []
    non_filler = []

    def replace_filler(replacement_items: list[CVHoDisItem]) -> None:
        """Replaces filler Items in the already-created Item pool with specified, different Items. Tier 1 filler will
        be replaced first, and then tier 2 when the less valuable tier 1 has run out, and then tier 3.
        If there's no filler left, the replacement Item(s) will be pushed precollected."""
        nonlocal non_filler, tier_1_filler, tier_2_filler

        # Check if we're trying to replace more filler Items than we currently have. If we are, throw a warning and
        # push the Items precollected. We are unlikely to ever hit this, but if we do, we might as well let the player
        # just start with the Item...
        if len(replacement_items) > len(tier_1_filler) + len(tier_2_filler) + len(tier_3_filler):

            logging.warning(f"[{world.player_name}] Ran out of replaceable filler. The following Items will be forced "
                            "into your starting inventory: "
                            f"{[replacement_item.name for replacement_item in replacement_items]}.")
            for item_to_precollect in replacement_items:
                world.push_precollected(item_to_precollect)
            return

        # Replace the filler Items one by one.
        for _ in range(len(replacement_items)):
            # If the tier 1 filler list has stuff in it, remove a random Item from it.
            if tier_1_filler:
                del tier_1_filler[world.random.randrange(0, len(tier_1_filler))]
            # Otherwise, if the tier 2 filler list has stuff in it, remove a random Item from it instead.
            elif tier_2_filler:
                del tier_2_filler[world.random.randrange(0, len(tier_2_filler))]
            # Otherwise, meaning the tier 3 filler list has to have stuff in it, remove a random Item from it instead.
            else:
                del tier_3_filler[world.random.randrange(0, len(tier_3_filler))]

        # Add the replacement Item to the non-Filler list.
        non_filler += replacement_items


    # Generate an Item for each Location that we are creating.
    for loc in active_locations:
        if loc.address is None:
            continue

        # Get the vanilla Item name defined for the Location. If it's an Item with a filler type and Item Pool Fill is
        # Mystery, or if it's a piece of Furniture when Remove Furniture is enabled, draw a random filler for the
        # Location instead. Otherwise, we'll add the vanilla Item as-is.
        item_name = CVHODIS_LOCATIONS_INFO[loc.name].item
        if (ALL_CVHODIS_ITEMS[item_name].filler_type and world.options.filler_pool == FillerPool.option_mystery) or \
                item_name in FURNITURE and ALL_CVHODIS_ITEMS[item_name].pickup_index < 0x1F and \
                world.options.remove_furniture:
            item_name = world.get_filler_item_name()
        # If the Item is the Lure Key, and we are opting to start with it, push it precollected and draw a random
        # filler Item instead.
        elif world.options.start_with_lure_key and item_name == item_names.use_key_l:
            world.push_precollected(world.create_item(item_names.use_key_l))
            item_name = world.get_filler_item_name()
        # If the Item is JB's Bracelet, check to see if Add JB's Bracelet is on. if it isn't, draw a random filler
        # instead and push the bracelet precollected.
        elif not world.options.add_jbs_bracelet and item_name == item_names.equip_bracelet_jb:
            world.push_precollected(world.create_item(item_names.equip_bracelet_jb))
            item_name = world.get_filler_item_name()
        # If the Item is a Height Relic, check to see if Progressive Heights is on. If it is, add a Progressive Height
        # to the pool instead.
        elif world.options.progressive_heights and item_name in HEIGHTS:
            item_name = item_names.relic_height

        # Get the final Item's default classification.
        item_class = ALL_CVHODIS_ITEMS[item_name].default_classification

        # If the Item is a piece of furniture and no furniture amount is required for goal completion at all, submit
        # it as Filler instead of Progression Skip Balancing. Be wary of the gate keys!
        if (item_name in FURNITURE and ALL_CVHODIS_ITEMS[item_name].pickup_index < 0x1F) and \
                not world.furniture_amount_required:
            item_class = ItemClassification.filler
        # If the Item is a spell book, and Spellbound Boss Logic is not disabled, submit it as Progression + Useful
        # instead of just Useful.
        elif item_name in SPELLBOOKS and world.options.spellbound_boss_logic:
            item_class = ItemClassification.useful | ItemClassification.progression
        # If the Item is a Hint Card, check some additional things to get its actual classification.
        elif item_name in HINT_CARDS:
            # If Cardbound Boss Logic and/or Card Amount Warp Requirement are on, classify it as Progression.
            if world.options.cardbound_boss_logic or world.options.card_amount_warp_requirement:
                item_class = ItemClassification.progression
            # Otherwise, meaning they were both off, check if Hint Card Hints are on. If they aren't, then classify it
            # as Filler. Otherwise, leave it as Useful.
            elif not world.options.hint_card_hints:
                item_class = ItemClassification.filler
        # If the Item is a Vlad Relic and neither the Worst nor Best Ending is required, submit it as just Useful
        # instead of Useful + Progression Skip Balancing.
        elif item_name in VLADS and not world.options.worst_ending_required and not \
                world.options.best_ending_required:
            item_class = ItemClassification.useful
        # If the Item is JB's Bracelet and the Bracelet Warp Requirement is off, submit it as Progression Skip
        # Balancing instead of just Progression.
        elif item_name == item_names.equip_bracelet_jb and not world.options.bracelet_warp_requirement:
            item_class = ItemClassification.progression_skip_balancing

        # Create the Item object.
        item_to_add = world.create_item(item_name, force_classification=item_class)

        # If the Item's classification is Progression, or it's a Spellbook, Whip Tip, Furniture, Max Up, or Relic, add
        # it to the Non-Filler list. These Items should NEVER be replaced.
        if item_to_add.advancement or item_name in SPELLBOOKS or item_name in WHIP_ATTACHMENTS or \
                item_name in FURNITURE or item_name in MAX_UPS or item_name in RELICS:
            non_filler.append(item_to_add)
        # Otherwise, add it to one of the three Filler lists. If it's Good Armor or a Useful Accessory, put it in
        # Tier 3. These are most desired and as such shouldn't be replaced until there's nothing else to replace.
        elif ALL_CVHODIS_ITEMS[item_name].filler_type == FillerTypes.GOOD_ARMOR or \
                (ALL_CVHODIS_ITEMS[item_name].filler_type == FillerTypes.ACCESSORY and
                 item_to_add.classification & ItemClassification.useful):
            tier_3_filler.append(item_to_add)
        # Otherwise, if it's regular armor/accessory or a Good Consumable, put it in Tier 2 so it won't be replaced
        # until all of Tier 1 is replaced.
        elif item_name in EQUIPMENT or ALL_CVHODIS_ITEMS[item_name].filler_type == FillerTypes.GOOD_CONSUMABLE:
            tier_2_filler.append(item_to_add)
        # Otherwise, meaning it has to either be a regular Consumable or Money Item, put it in Tier 1.
        # We care the least about these, and as such prefer replacing them first and foremost.
        else:
            tier_1_filler.append(item_to_add)

    # # # ITEM POOL REPLACEMENTS BEGIN HERE # # #
    # If Gate Keys is Add Keys (NOT full Buttonsanity, which causes the keys to be added with their unfilled Locations),
    # add a set of gate keys to be in the pool separate from the locked ones we placed on the button Locations.
    if world.options.gate_items == GateItems.option_add_keys:
        replace_filler([world.create_item(item_names.misc_key_la),
                        world.create_item(item_names.misc_key_c),
                        world.create_item(item_names.misc_key_t)])

    # If Add Floating Boots is on, add them.
    if world.options.add_floating_boots:
        replace_filler([world.create_item(item_names.equip_boots_f)])

    # If Add Infinite Boots is on, add them.
    if world.options.add_floating_boots:
        replace_filler([world.create_item(item_names.equip_boots_in)])

    # If Add Noon Star is on, add it.
    if world.options.add_floating_boots:
        replace_filler([world.create_item(item_names.use_n_star)])

    # Find all Progression Items that are not Furniture, and save them for the purposes of later making Hint Card text.
    final_item_list = tier_1_filler + tier_2_filler + tier_3_filler + non_filler
    for item in final_item_list:
        if item.advancement and item.name not in FURNITURE:
            world.possible_hint_card_items.append(item)

    # Return the final complete list of created Item objects.
    return final_item_list
