from enum import IntEnum
from BaseClasses import Item, ItemClassification
from .data import item_names
from .data.enums import PickupTypes
from .locations import BASE_ID, CVHODIS_LOCATIONS_INFO

from typing import TYPE_CHECKING, NamedTuple
from collections import Counter

from .options import CastleWarpCondition

if TYPE_CHECKING:
    from . import CVHoDisWorld

class CVHoDisItem(Item):
    game: str = "Castlevania - Harmony of Dissonance"


class CVHoDisItemData(NamedTuple):
    pickup_index: int
    default_classification: ItemClassification = ItemClassification.filler
# "pickup_index" = The lower half of the unique part of the Item's AP code attribute, as well as the value to write
#                  in-game to insert that Item on a Location alongside its pickup type value. Add this + its pickup type
#                  right-shifted by 8 + base_id to get the Item's final AP code.
# "default_classification" = The AP Item Classification that gets assigned to instances of that Item in create_item
#                            by default, unless I deliberately override it (as is the case for the Cleansing on the
#                            Ignore Cleansing option).


USE_ITEMS: dict[str, CVHoDisItemData] = {
    item_names.use_potion:    CVHoDisItemData(0x00),
    item_names.use_potion_h:  CVHoDisItemData(0x01),
    item_names.use_elixir:    CVHoDisItemData(0x02, ItemClassification.useful),
    item_names.use_prism:     CVHoDisItemData(0x03),
    item_names.use_prism_b:   CVHoDisItemData(0x04, ItemClassification.useful),
    item_names.use_drumstick: CVHoDisItemData(0x05),
    item_names.use_turkey:    CVHoDisItemData(0x06),
    item_names.use_a_venom:   CVHoDisItemData(0x07),
    item_names.use_uncurse:   CVHoDisItemData(0x08),
    item_names.use_medicine:  CVHoDisItemData(0x09, ItemClassification.useful),
    item_names.use_key_l:     CVHoDisItemData(0x0A, ItemClassification.progression),
    item_names.use_key_s:     CVHoDisItemData(0x0B, ItemClassification.progression),
    item_names.use_key_f:     CVHoDisItemData(0x0C, ItemClassification.progression),
    item_names.use_map_1:     CVHoDisItemData(0x0D),
    item_names.use_map_2:     CVHoDisItemData(0x0E),
    item_names.use_map_3:     CVHoDisItemData(0x0F),
    item_names.use_hint_1:    CVHoDisItemData(0x10, ItemClassification.useful),
    item_names.use_hint_2:    CVHoDisItemData(0x11, ItemClassification.useful),
    item_names.use_hint_3:    CVHoDisItemData(0x12, ItemClassification.useful),
    item_names.use_hint_4:    CVHoDisItemData(0x13, ItemClassification.useful),
    item_names.use_hint_5:    CVHoDisItemData(0x14, ItemClassification.useful),
    item_names.use_hint_6:    CVHoDisItemData(0x15, ItemClassification.useful),
    item_names.use_n_star:    CVHoDisItemData(0x16, ItemClassification.useful),
    item_names.use_gem_o:     CVHoDisItemData(0x17),
    item_names.use_gem_t:     CVHoDisItemData(0x18),
    item_names.use_gem_s:     CVHoDisItemData(0x19),
    item_names.use_gem_r:     CVHoDisItemData(0x1A, ItemClassification.useful),
    item_names.use_gem_d:     CVHoDisItemData(0x1B, ItemClassification.useful),
}

WHIP_ATTACHMENTS: dict[str, CVHoDisItemData] = {
    item_names.whip_crush:  CVHoDisItemData(0x00, ItemClassification.progression | ItemClassification.useful),
    item_names.whip_steel:  CVHoDisItemData(0x01, ItemClassification.useful),
    item_names.whip_plat:   CVHoDisItemData(0x02, ItemClassification.useful),
    item_names.whip_circle: CVHoDisItemData(0x03, ItemClassification.useful),
    item_names.whip_bullet: CVHoDisItemData(0x04, ItemClassification.useful),
    item_names.whip_red:    CVHoDisItemData(0x05, ItemClassification.useful),
    item_names.whip_blue:   CVHoDisItemData(0x06, ItemClassification.useful),
    item_names.whip_yellow: CVHoDisItemData(0x07, ItemClassification.useful),
    item_names.whip_green:  CVHoDisItemData(0x08, ItemClassification.useful),
}

EQUIPMENT: dict[str, CVHoDisItemData] = {
    item_names.equip_armor_l:     CVHoDisItemData(0x00),
    item_names.equip_armor_r:     CVHoDisItemData(0x01),
    item_names.equip_armor_f:     CVHoDisItemData(0x02),
    item_names.equip_coat_pl:     CVHoDisItemData(0x03),
    item_names.equip_tunic:       CVHoDisItemData(0x04),
    item_names.equip_armor_br:    CVHoDisItemData(0x05),
    item_names.equip_leather:     CVHoDisItemData(0x06),
    item_names.equip_armor_c:     CVHoDisItemData(0x07),
    item_names.equip_armor_pad:   CVHoDisItemData(0x08),
    item_names.equip_coat_pu:     CVHoDisItemData(0x09),
    item_names.equip_armor_par:   CVHoDisItemData(0x0A),
    item_names.equip_mail_ch:     CVHoDisItemData(0x0B),
    item_names.equip_armor_sc:    CVHoDisItemData(0x0C),
    item_names.equip_mail_h:      CVHoDisItemData(0x0D, ItemClassification.useful),
    item_names.equip_guardian_a:  CVHoDisItemData(0x0E),
    item_names.equip_mail_f:      CVHoDisItemData(0x0F, ItemClassification.useful),
    item_names.equip_brigan:      CVHoDisItemData(0x10),
    item_names.equip_armor_a:     CVHoDisItemData(0x11, ItemClassification.useful),
    item_names.equip_armor_h:     CVHoDisItemData(0x12, ItemClassification.useful),
    item_names.equip_mail_p:      CVHoDisItemData(0x13, ItemClassification.useful),
    item_names.equip_mail_d:      CVHoDisItemData(0x14, ItemClassification.useful),
    item_names.equip_armor_su:    CVHoDisItemData(0x15, ItemClassification.useful),
    item_names.equip_armor_mo:    CVHoDisItemData(0x16, ItemClassification.useful),
    item_names.equip_armor_ba:    CVHoDisItemData(0x17, ItemClassification.useful),
    item_names.equip_armor_w:     CVHoDisItemData(0x18, ItemClassification.useful),
    item_names.equip_armor_si:    CVHoDisItemData(0x19, ItemClassification.useful),
    item_names.equip_mail_ce:     CVHoDisItemData(0x1A, ItemClassification.useful),
    item_names.equip_armor_ma:    CVHoDisItemData(0x1B, ItemClassification.useful),
    item_names.equip_mail_k:      CVHoDisItemData(0x1C, ItemClassification.useful),
    item_names.equip_casual:      CVHoDisItemData(0x1D),
    item_names.equip_summer:      CVHoDisItemData(0x1E),
    item_names.equip_shirt:       CVHoDisItemData(0x1F),
    item_names.equip_robe_t:      CVHoDisItemData(0x20),
    item_names.equip_clothes_f:   CVHoDisItemData(0x21),
    item_names.equip_clothes_l:   CVHoDisItemData(0x22),
    item_names.equip_ramil:       CVHoDisItemData(0x23),
    item_names.equip_robe_b:      CVHoDisItemData(0x24, ItemClassification.useful),
    item_names.equip_robe_n:      CVHoDisItemData(0x25),
    item_names.equip_robe_m:      CVHoDisItemData(0x26, ItemClassification.useful),
    item_names.equip_robe_l:      CVHoDisItemData(0x27, ItemClassification.useful),
    item_names.equip_w_fatigues:  CVHoDisItemData(0x28, ItemClassification.useful),
    item_names.equip_robe_a:      CVHoDisItemData(0x29, ItemClassification.useful),
    item_names.equip_bracelet_jb: CVHoDisItemData(0x2A, ItemClassification.progression),
    item_names.equip_goggles:     CVHoDisItemData(0x2B, ItemClassification.progression),
    item_names.equip_bracelet_mk: CVHoDisItemData(0x2C, ItemClassification.progression),
    item_names.equip_boots_c:     CVHoDisItemData(0x2D, ItemClassification.progression),
    item_names.equip_bandana:     CVHoDisItemData(0x2E),
    item_names.equip_turban:      CVHoDisItemData(0x2F),
    item_names.equip_circlet:     CVHoDisItemData(0x30),
    item_names.equip_cap:         CVHoDisItemData(0x31),
    item_names.equip_helm_c:      CVHoDisItemData(0x32),
    item_names.equip_helm_l:      CVHoDisItemData(0x33),
    item_names.equip_sallet:      CVHoDisItemData(0x34),
    item_names.equip_bicocette:   CVHoDisItemData(0x35),
    item_names.equip_helm_gr:     CVHoDisItemData(0x36),
    item_names.equip_guard_f:     CVHoDisItemData(0x37),
    item_names.equip_helm_pi:     CVHoDisItemData(0x38),
    item_names.equip_bagonette:   CVHoDisItemData(0x39),
    item_names.equip_barbuta:     CVHoDisItemData(0x3A),
    item_names.equip_guardian_h:  CVHoDisItemData(0x3B),
    item_names.equip_armet:       CVHoDisItemData(0x3C),
    item_names.equip_bascinet:    CVHoDisItemData(0x3D),
    item_names.equip_hat_s:       CVHoDisItemData(0x3E),
    item_names.equip_helm_b:      CVHoDisItemData(0x3F),
    item_names.equip_morion:      CVHoDisItemData(0x40),
    item_names.equip_hat_k:       CVHoDisItemData(0x41, ItemClassification.useful),
    item_names.equip_helm_i:      CVHoDisItemData(0x42, ItemClassification.useful),
    item_names.equip_helm_f:      CVHoDisItemData(0x43, ItemClassification.useful),
    item_names.equip_cabacete:    CVHoDisItemData(0x44, ItemClassification.useful),
    item_names.equip_helm_po:     CVHoDisItemData(0x45, ItemClassification.useful),
    item_names.equip_tiara:       CVHoDisItemData(0x46, ItemClassification.useful),
    item_names.equip_helm_s:      CVHoDisItemData(0x47, ItemClassification.useful),
    item_names.equip_helm_v:      CVHoDisItemData(0x48, ItemClassification.useful),
    item_names.equip_headband:    CVHoDisItemData(0x49, ItemClassification.useful),
    item_names.equip_crown:       CVHoDisItemData(0x4A, ItemClassification.useful),
    item_names.equip_hat_rs:      CVHoDisItemData(0x4B, ItemClassification.useful),
    item_names.equip_glove_l:     CVHoDisItemData(0x4C),
    item_names.equip_gauntlets:   CVHoDisItemData(0x4D),
    item_names.equip_glove:       CVHoDisItemData(0x4E),
    item_names.equip_glove_h:     CVHoDisItemData(0x4F),
    item_names.equip_guardian_g:  CVHoDisItemData(0x50),
    item_names.equip_arm_g:       CVHoDisItemData(0x51),
    item_names.equip_arm_p:       CVHoDisItemData(0x52, ItemClassification.useful),
    item_names.equip_glove_b:     CVHoDisItemData(0x53, ItemClassification.useful),
    item_names.equip_glove_s:     CVHoDisItemData(0x54, ItemClassification.useful),
    item_names.equip_boots_l:     CVHoDisItemData(0x55),
    item_names.equip_guard_s:     CVHoDisItemData(0x56),
    item_names.equip_guard_a:     CVHoDisItemData(0x57),
    item_names.equip_boots_b:     CVHoDisItemData(0x58),
    item_names.equip_guardian_b:  CVHoDisItemData(0x59),
    item_names.equip_boots_ir:    CVHoDisItemData(0x5A),
    item_names.equip_greaves:     CVHoDisItemData(0x5B),
    item_names.equip_leggings:    CVHoDisItemData(0x5C),
    item_names.equip_boots_s:     CVHoDisItemData(0x5D, ItemClassification.useful),
    item_names.equip_boots_f:     CVHoDisItemData(0x5E, ItemClassification.progression | ItemClassification.useful),
    item_names.equip_p_shoes:     CVHoDisItemData(0x5F, ItemClassification.useful),
    item_names.equip_boots_in:    CVHoDisItemData(0x60, ItemClassification.progression | ItemClassification.useful),
    item_names.equip_cloak_s:     CVHoDisItemData(0x61),
    item_names.equip_cloak_v:     CVHoDisItemData(0x62),
    item_names.equip_cloak_e:     CVHoDisItemData(0x63),
    item_names.equip_cloak_w:     CVHoDisItemData(0x64, ItemClassification.useful),
    item_names.equip_cloak_c:     CVHoDisItemData(0x65, ItemClassification.useful),
    item_names.equip_cloak_n:     CVHoDisItemData(0x66, ItemClassification.useful),
    item_names.equip_cloak_t:     CVHoDisItemData(0x67, ItemClassification.useful),
    item_names.equip_wristband:   CVHoDisItemData(0x68),
    item_names.equip_bangle:      CVHoDisItemData(0x69),
    item_names.equip_kaiser:      CVHoDisItemData(0x6A, ItemClassification.useful),
    item_names.equip_bangle_s:    CVHoDisItemData(0x6B, ItemClassification.useful),
    item_names.equip_c_band:      CVHoDisItemData(0x6C, ItemClassification.useful),
    item_names.equip_pendant:     CVHoDisItemData(0x6D),
    item_names.equip_l_charm:     CVHoDisItemData(0x6E),
    item_names.equip_necklace_g:  CVHoDisItemData(0x6F),
    item_names.equip_necklace_m:  CVHoDisItemData(0x70),
    item_names.equip_pendant_med: CVHoDisItemData(0x71, ItemClassification.useful),
    item_names.equip_h_choker:    CVHoDisItemData(0x72, ItemClassification.useful),
    item_names.equip_g_amulet:    CVHoDisItemData(0x73, ItemClassification.useful),
    item_names.equip_brooch:      CVHoDisItemData(0x74, ItemClassification.useful),
    item_names.equip_cipher:      CVHoDisItemData(0x75, ItemClassification.useful),
    item_names.equip_pendant_mir: CVHoDisItemData(0x76, ItemClassification.useful),
    item_names.equip_ring_lu:     CVHoDisItemData(0x77),
    item_names.equip_ring_ho:     CVHoDisItemData(0x78, ItemClassification.useful),
    item_names.equip_ring_r:      CVHoDisItemData(0x79, ItemClassification.useful),
    item_names.equip_ring_c:      CVHoDisItemData(0x7A, ItemClassification.useful),
    item_names.equip_ring_n:      CVHoDisItemData(0x7B, ItemClassification.useful),
    item_names.equip_ring_lo:     CVHoDisItemData(0x7C, ItemClassification.useful),
    item_names.equip_ring_he:     CVHoDisItemData(0x7D, ItemClassification.useful),
    item_names.equip_ring_a:      CVHoDisItemData(0x7E, ItemClassification.useful),
    item_names.equip_ring_e:      CVHoDisItemData(0x7F, ItemClassification.useful),
}

SPELLBOOKS: dict[str, CVHoDisItemData] = {
    item_names.book_fire:   CVHoDisItemData(0x00, ItemClassification.useful),
    item_names.book_ice:    CVHoDisItemData(0x01, ItemClassification.useful),
    item_names.book_bolt:   CVHoDisItemData(0x02, ItemClassification.useful),
    item_names.book_wind:   CVHoDisItemData(0x03, ItemClassification.useful),
    item_names.book_summon: CVHoDisItemData(0x04, ItemClassification.useful),
}

RELICS: dict[str, CVHoDisItemData] = {
    item_names.relic_tail:    CVHoDisItemData(0x00, ItemClassification.progression | ItemClassification.useful),
    item_names.relic_feather: CVHoDisItemData(0x01, ItemClassification.progression | ItemClassification.useful),
    item_names.relic_wing:    CVHoDisItemData(0x02, ItemClassification.progression | ItemClassification.useful),
    item_names.relic_orb:     CVHoDisItemData(0x03, ItemClassification.useful),
    item_names.relic_journal: CVHoDisItemData(0x04, ItemClassification.useful),
    item_names.relic_tome:    CVHoDisItemData(0x05, ItemClassification.useful),
    item_names.relic_v_eye:   CVHoDisItemData(0x06, ItemClassification.progression_skip_balancing |
                                         ItemClassification.useful),
    item_names.relic_v_heart: CVHoDisItemData(0x07, ItemClassification.progression_skip_balancing |
                                         ItemClassification.useful),
    item_names.relic_v_rib:   CVHoDisItemData(0x08, ItemClassification.progression_skip_balancing |
                                         ItemClassification.useful),
    item_names.relic_v_nail:  CVHoDisItemData(0x09, ItemClassification.progression_skip_balancing |
                                         ItemClassification.useful),
    item_names.relic_v_fang:  CVHoDisItemData(0x0A, ItemClassification.progression_skip_balancing |
                                         ItemClassification.useful),
    item_names.relic_v_ring:  CVHoDisItemData(0x0B, ItemClassification.progression_skip_balancing |
                                         ItemClassification.useful),
}

FURNITURE: dict[str, CVHoDisItemData] = {
    item_names.furn_chan:      CVHoDisItemData(0x00, ItemClassification.progression_skip_balancing),
    item_names.furn_clock:     CVHoDisItemData(0x01, ItemClassification.progression_skip_balancing),
    item_names.furn_shelf:     CVHoDisItemData(0x02, ItemClassification.progression_skip_balancing),
    item_names.furn_radio:     CVHoDisItemData(0x03, ItemClassification.progression_skip_balancing),
    item_names.furn_dishes:    CVHoDisItemData(0x04, ItemClassification.progression_skip_balancing),
    item_names.furn_table_a:   CVHoDisItemData(0x05, ItemClassification.progression_skip_balancing),
    item_names.furn_chair:     CVHoDisItemData(0x06, ItemClassification.progression_skip_balancing),
    item_names.furn_chair_r:   CVHoDisItemData(0x07, ItemClassification.progression_skip_balancing),
    item_names.furn_curtain:   CVHoDisItemData(0x08, ItemClassification.progression_skip_balancing),
    item_names.furn_urn_a:     CVHoDisItemData(0x09, ItemClassification.progression_skip_balancing),
    item_names.furn_urn_w:     CVHoDisItemData(0x0A, ItemClassification.progression_skip_balancing),
    item_names.furn_vase:      CVHoDisItemData(0x0B, ItemClassification.progression_skip_balancing),
    item_names.furn_table_s:   CVHoDisItemData(0x0C, ItemClassification.progression_skip_balancing),
    item_names.furn_teacup:    CVHoDisItemData(0x0D, ItemClassification.progression_skip_balancing),
    item_names.furn_teapot:    CVHoDisItemData(0x0E, ItemClassification.progression_skip_balancing),
    item_names.furn_glass:     CVHoDisItemData(0x0F, ItemClassification.progression_skip_balancing),
    item_names.furn_statue_h:  CVHoDisItemData(0x10, ItemClassification.progression_skip_balancing),
    item_names.furn_statue_sm: CVHoDisItemData(0x11, ItemClassification.progression_skip_balancing),
    item_names.furn_statue_sa: CVHoDisItemData(0x12, ItemClassification.progression_skip_balancing),
    item_names.furn_raccoon:   CVHoDisItemData(0x13, ItemClassification.progression_skip_balancing),
    item_names.furn_cat:       CVHoDisItemData(0x14, ItemClassification.progression_skip_balancing),
    item_names.furn_phono:     CVHoDisItemData(0x15, ItemClassification.progression_skip_balancing),
    item_names.furn_stag:      CVHoDisItemData(0x16, ItemClassification.progression_skip_balancing),
    item_names.furn_candle_h:  CVHoDisItemData(0x17, ItemClassification.progression_skip_balancing),
    item_names.furn_candle_s:  CVHoDisItemData(0x18, ItemClassification.progression_skip_balancing),
    item_names.furn_trinket_s: CVHoDisItemData(0x19, ItemClassification.progression_skip_balancing),
    item_names.furn_trinket_g: CVHoDisItemData(0x1A, ItemClassification.progression_skip_balancing),
    item_names.furn_mirror:    CVHoDisItemData(0x1B, ItemClassification.progression_skip_balancing),
    item_names.furn_drawing:   CVHoDisItemData(0x1C, ItemClassification.progression_skip_balancing),
    item_names.furn_bed:       CVHoDisItemData(0x1D, ItemClassification.progression_skip_balancing),
    item_names.furn_closet:    CVHoDisItemData(0x1E, ItemClassification.progression_skip_balancing),
}

MAX_UPS: dict[str, CVHoDisItemData] = {
    item_names.max_life:  CVHoDisItemData(0x00),
    item_names.max_heart: CVHoDisItemData(0x01),
}

PICKUP_TYPE_MAPPINGS = {
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

FILLER_ITEM_NAMES = [item_names.use_potion, item_names.use_potion_h, item_names.use_prism, item_names.use_a_venom,
                     item_names.use_uncurse, item_names.use_drumstick, item_names.use_turkey]


def get_pickup_type(item_name: str) -> int | None:
    """ Given the name of an Item, checks to see if it is in any of the Item data dicts mapped to a pickup type ID in
    the pickup types dict and, if it is, returns that items pickup type ID. If it's not in any mapped dict, then None
    will be returned."""
    for pickup_type in PICKUP_TYPE_MAPPINGS:
        if item_name in PICKUP_TYPE_MAPPINGS[pickup_type]:
            return pickup_type
    return None

def get_item_names_to_ids() -> dict[str, int]:
    return {item: PICKUP_TYPE_MAPPINGS[pickup_type][item].pickup_index + (pickup_type << 8) + BASE_ID
            for pickup_type in PICKUP_TYPE_MAPPINGS for item in PICKUP_TYPE_MAPPINGS[pickup_type]}


def get_item_counts(world: "CVHoDisWorld") -> dict[ItemClassification, dict[str, int]]:

    active_locations = world.multiworld.get_unfilled_locations(world.player)

    item_counts: dict[ItemClassification, Counter[str, int]] = {
        ItemClassification.progression: Counter(),
        ItemClassification.progression_skip_balancing: Counter(),
        ItemClassification.useful | ItemClassification.progression: Counter(),
        ItemClassification.useful | ItemClassification.progression_skip_balancing: Counter(),
        ItemClassification.useful: Counter(),
        ItemClassification.filler: Counter(),
    }
    total_items = 0

    # Get from each Location its vanilla Item and add it to the default Item counts.
    for loc in active_locations:
        if loc.address is None:
            continue

        item_to_add = CVHODIS_LOCATIONS_INFO[loc.name].item

        # If the Item is a piece of furniture and no furniture amount is required for goal completion at all, submit
        # it as Filler instead of Progression Skip Balancing.
        if item_to_add in FURNITURE and not world.furniture_amount_required:
            item_class = ItemClassification.filler
        # If the Item is a spell book, and Spellbound Boss Logic is not disabled, submit it as Progression + Useful
        # instead of just Useful.
        elif item_to_add in SPELLBOOKS and world.options.spellbound_boss_logic:
            item_class = ItemClassification.useful | ItemClassification.progression
        # If the Item is a Vlad Relic and neither the Worst nor Best Ending is required, submit it as just Useful
        # instead of Useful + Progression Skip Balancing.
        elif "Vlad" in item_to_add and not world.options.worst_ending_required and not \
                world.options.best_ending_required:
            item_class = ItemClassification.useful
        # If the Item is JB's Bracelet and the Castle Warp Condition is not Bracelet, submit it as Progression Skip
        # Balancing instead of just Progression.
        elif item_to_add == item_names.equip_bracelet_jb and \
                world.options.castle_warp_condition != CastleWarpCondition.option_bracelet:
            item_class = ItemClassification.progression_skip_balancing
        # Otherwise, submit the Item as its specified default classification.
        else:
            item_class = ALL_CVHODIS_ITEMS[item_to_add].default_classification

        item_counts[item_class][item_to_add] += 1
        total_items += 1

    return item_counts
