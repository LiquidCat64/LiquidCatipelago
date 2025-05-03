from . import CVHoDisTestBase
from ..data import item_names, loc_names, ent_names
from ..options import SpellboundBossLogic


class Sphere1FromEntranceATest(CVHoDisTestBase):

    def test_always_accessible(self) -> None:
        self.assertTrue(self.can_reach_location(loc_names.eta5a))
        self.assertTrue(self.can_reach_location(loc_names.eta5b))
        self.assertTrue(self.can_reach_location(loc_names.eta7))
        self.assertTrue(self.can_reach_location(loc_names.eta10))
        self.assertTrue(self.can_reach_location(loc_names.eta11))
        self.assertTrue(self.can_reach_location(loc_names.eta19))
        self.assertTrue(self.can_reach_location(loc_names.mca2a))
        self.assertTrue(self.can_reach_location(loc_names.mca2b))
        self.assertTrue(self.can_reach_location(loc_names.mca4))
        self.assertTrue(self.can_reach_location(loc_names.mca7))
        self.assertTrue(self.can_reach_location(loc_names.mca10))
        self.assertTrue(self.can_reach_location(loc_names.mca11a))
        self.assertTrue(self.can_reach_location(loc_names.mca11c))
        self.assertTrue(self.can_reach_location(loc_names.mca11f))
        self.assertTrue(self.can_reach_location(loc_names.mca12))
        self.assertTrue(self.can_reach_location(loc_names.mca13))
        self.assertTrue(self.can_reach_location(loc_names.mca14))
        self.assertTrue(self.can_reach_location(loc_names.ria15))
        self.assertTrue(self.can_reach_location(loc_names.ria16))
        self.assertTrue(self.can_reach_location(loc_names.wwa0a))
        self.assertTrue(self.can_reach_location(loc_names.wwa0b))
        self.assertTrue(self.can_reach_location(loc_names.wwa0d))
        self.assertTrue(self.can_reach_location(loc_names.wwa1))
        self.assertTrue(self.can_reach_location(loc_names.wwa3))
        self.assertTrue(self.can_reach_location(loc_names.wwa8))
        self.assertTrue(self.can_reach_location(loc_names.saa6a))
        self.assertTrue(self.can_reach_location(loc_names.saa6b))
        self.assertTrue(self.can_reach_location(loc_names.saa7))
        self.assertTrue(self.can_reach_location(loc_names.saa10))
        self.assertTrue(self.can_reach_location(loc_names.saa12))
        self.assertTrue(self.can_reach_location(loc_names.saa15))


class TreasuryAAccessibilityTest(CVHoDisTestBase):
    options = {
        "spellbound_boss_logic": SpellboundBossLogic.option_normal,
    }

    def test_treasury_a_access(self) -> None:
        self.assertFalse(self.can_reach_location(loc_names.cya1))

        self.collect_by_name([item_names.relic_wing, item_names.relic_tail, item_names.book_fire, item_names.book_ice, item_names.equip_bracelet_mk])

        self.assertFalse(self.can_reach_location(loc_names.cya1))

        self.collect_by_name([item_names.use_key_s])

        self.assertTrue(self.can_reach_location(loc_names.cya1))

# TODO: Add more tests
