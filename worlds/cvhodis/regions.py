from BaseClasses import Region
from .data import loc_names, ent_names
from .entrances import CVHoDisEntrance
from typing import TypedDict, ClassVar


class CVHoDisRegion(Region):
    entrance_type: ClassVar[type[CVHoDisEntrance]] = CVHoDisEntrance


class RegionInfo(TypedDict, total=False):
    locations: list[str]
    entrances: dict[str, str]


# # #    KEY    # # #
# "locations" = A list of the Locations to add to that Region when adding said Region.
# "entrances" = A dict of the connecting Regions to the Entrances' names to add to that Region when adding said Region.
ALL_CVHODIS_REGIONS: dict[str, RegionInfo] = {
    # # # Castle A # # #
    # Entrance A regions
    "Entrance A Main": {"locations": [loc_names.eta2,
                                      loc_names.eta3,
                                      loc_names.eta10,
                                      loc_names.eta11,
                                      loc_names.eta19,
                                      loc_names.eta5b,
                                      loc_names.eta5a,
                                      loc_names.eta7,
                                      loc_names.eta9,
                                      loc_names.eta18,
                                      loc_names.eta13],
                        "entrances": {"Entrance B Main": ent_names.eta_warp_u,
                                      "Shrine A End Room": ent_names.eta_exit_saa,
                                      "Corridor A Main": ent_names.eta_exit_mca,
                                      "Entrance A Sub Shaft": ent_names.eta_cstone_ul}},

    "Entrance A Sub Shaft": {"locations": [loc_names.eta17],
                             "entrances": {"Entrance B Sub Shaft": ent_names.eta_warp_l,
                                           "Entrance A Main": ent_names.eta_cstone_ur,
                                           "Entrance A Sub Shaft Bottom": ent_names.eta_cstone_ll}},

    "Entrance A Sub Shaft Bottom": {"entrances": {"Skeleton A Left": ent_names.eta_exit_sca,
                                                  "Entrance A Sub Shaft": ent_names.eta_cstone_lr}},

    # Marble Corridor A region
    "Corridor A Main": {"locations": [loc_names.mca4,
                                      loc_names.mca2b,
                                      loc_names.mca2a,
                                      loc_names.mca14,
                                      loc_names.mca7,
                                      loc_names.mca9a,
                                      loc_names.mca9b,
                                      loc_names.mca10,
                                      loc_names.mca11c,
                                      loc_names.mca11d,
                                      loc_names.mca11a,
                                      loc_names.mca11b,
                                      loc_names.mca11f,
                                      loc_names.mca11e,
                                      loc_names.mca12,
                                      loc_names.mca13,
                                      loc_names.event_giant_bat],
                        "entrances": {"Entrance A Main": ent_names.mca_exit_eta,
                                      "Room A Left": ent_names.mca_exit_ria_l,
                                      "Room A Right": ent_names.mca_exit_ria_r,
                                      "Wailing A Main": ent_names.mca_exit_wwa,
                                      "Top A Super Jump Passage": ent_names.mca_exit_tfa}},

    # Room of Illusion A regions
    "Room A Left": {"locations": [loc_names.ria16],
                    "entrances": {"Corridor A Main": ent_names.ria_exit_mca_l}},

    "Room A Right": {"locations": [loc_names.ria15],
                     "entrances": {"Corridor A Main": ent_names.ria_exit_mca_r,
                                   "Room A Past Slide Space": ent_names.ria_slide_r}},

    "Room A Past Slide Space": {"locations": [loc_names.ria17],
                                "entrances": {"Room A Right": ent_names.ria_slide_l,
                                              "Room and Treasury Portal": ent_names.ria_portal}},

    # The Wailing Way A region
    "Wailing A Main": {"locations": [loc_names.wwa0b,
                                     loc_names.wwa1,
                                     loc_names.wwa3,
                                     loc_names.wwa4b,
                                     loc_names.wwa4a,
                                     loc_names.wwa0a,
                                     loc_names.wwa0d,
                                     loc_names.wwa0c,
                                     loc_names.wwa8],
                       "entrances": {"Corridor A Main": ent_names.wwa_exit_mca,
                                     "Treasury A Upper": ent_names.wwa_exit_cya,
                                     "Shrine A Main": ent_names.wwa_exit_saa}},

    # Shrine of the Apostates A regions
    "Shrine A Main": {"locations": [loc_names.saa10,
                                    loc_names.saa16,
                                    loc_names.saa6b,
                                    loc_names.saa6a,
                                    loc_names.saa7,
                                    loc_names.saa12,
                                    loc_names.saa15],
                      "entrances": {"Wailing A Main": ent_names.saa_exit_wwa,
                                    "Shrine A End Room": ent_names.saa_button}},

    "Shrine A End Room": {"entrances": {"Entrance A Main": ent_names.saa_exit_eta}},

    # Castle Treasury A regions
    "Treasury A Lower": {"locations": [loc_names.cya6,
                                       loc_names.cya8,
                                       loc_names.cya4,
                                       loc_names.cya0a,
                                       loc_names.cya0b,
                                       loc_names.cya1,
                                       loc_names.cya10,
                                       loc_names.cya9,
                                       loc_names.cya12,
                                       loc_names.cya11,
                                       loc_names.cya20b,
                                       loc_names.cya20a],
                         "entrances": {"Treasury B Lower": ent_names.cya_warp,
                                       "Skeleton A Right": ent_names.cya_exit_sca,
                                       "Luminous A Main": ent_names.cya_exit_lca,
                                       "Treasury A Upper": ent_names.cya_djumps,
                                       "The Empty Room": ent_names.cya_room}},

    "Treasury A Upper": {"locations": [loc_names.cya18,
                                       loc_names.cya19,
                                       loc_names.event_ending_m],
                         "entrances": {"Wailing A Main": ent_names.cya_exit_wwa,
                                       "Top A Lower": ent_names.cya_exit_tfa,
                                       "Treasury A Lower": ent_names.cya_down}},

    # Skeleton Cave A regions
    "Skeleton A Right": {"locations": [loc_names.sca1b,
                                       loc_names.sca1a,
                                       loc_names.sca2,
                                       loc_names.sca4],
                         "entrances": {"Treasury A Lower": ent_names.sca_exit_cya,
                                       "Skeleton A Left": ent_names.sca_crates_r}},

    "Skeleton A Left": {"locations": [loc_names.sca5,
                                      loc_names.sca12a,
                                      loc_names.sca12b,
                                      loc_names.sca10,
                                      loc_names.sca19,
                                      loc_names.sca11,
                                      loc_names.sca13,
                                      loc_names.event_wall_skeleton],
                        "entrances": {"Entrance A Sub Shaft Bottom": ent_names.sca_exit_eta,
                                      "Skeleton A Right": ent_names.sca_crates_l}},

    # Luminous Cavern A regions
    "Luminous A Main": {"locations": [loc_names.lca3,
                                      loc_names.lca7a,
                                      loc_names.lca7b,
                                      loc_names.lca11,
                                      loc_names.lca22,
                                      loc_names.lca14],
                        "entrances": {"Treasury A Lower": ent_names.lca_exit_cya,
                                      "Luminous B Main": ent_names.lca_warp,
                                      "Luminous A Underwater": ent_names.lca_floodgate,
                                      "Luminous A Post Talos": ent_names.lca_talos,
                                      "Luminous A Top Shortcut Room": ent_names.lca_sjump_l}},

    "Luminous A Top Shortcut Room": {"entrances": {"Aqueduct A Bottom Shortcut Room": ent_names.lca_exit_ada,
                                                   "Luminous A Main": ent_names.lca_sjump_r}},

    "Luminous A Post Talos": {"locations": [loc_names.lca8b,
                                            loc_names.lca8c,
                                            loc_names.lca8a,
                                            loc_names.lca10]},

    "Luminous A Underwater": {"locations": [loc_names.lca17,
                                            loc_names.lca18,
                                            loc_names.lca23]},

    # Sky Walkway A regions
    "Walkway A Portal Hallway": {"locations": [loc_names.swa10c,
                                               loc_names.swa10b],
                                 "entrances": {"Luminous and Walkway Portal": ent_names.swa_portal,
                                               "Walkway A Main": ent_names.swa_djump_p}},

    "Walkway A Main": {"locations": [loc_names.swa10a,
                                     loc_names.swa7,
                                     loc_names.swa15a,
                                     loc_names.swa15b,
                                     loc_names.swa12c,
                                     loc_names.swa12a,
                                     loc_names.swa12b],
                       "entrances": {"Chapel A Bottom": ent_names.swa_exit_cda,
                                     "Walkway A Portal Hallway": ent_names.swa_down_p,
                                     "Walkway A Clock Exit Room": ent_names.swa_devil,
                                     "Walkway A Dark Rooms": ent_names.swa_goggles_u}},

    "Walkway A Clock Exit Room": {"locations": [loc_names.swa14],
                                  "entrances": {"Clock A Pendulum Area": ent_names.swa_exit_cra,
                                                "Walkway A Main": ent_names.swa_djump_c}},

    "Walkway A Dark Rooms": {"locations": [loc_names.swa17,
                                           loc_names.swa18b,
                                           loc_names.swa18a],
                             "entrances": {"Walkway A Dark Rooms Near Door": ent_names.swa_dark_d,
                                           "Walkway A Main": ent_names.swa_dark_u}},

    "Walkway A Dark Rooms Near Door": {"entrances": {"Aqueduct A Top": ent_names.swa_exit_ada,
                                                     "Walkway A Dark Rooms": ent_names.swa_goggles_l}},

    # Chapel of Dissonance A regions
    "Chapel A Bottom": {"entrances": {"Walkway A Main": ent_names.cda_exit_swa,
                                      "Chapel A Top": ent_names.cda_djump}},

    "Chapel A Top": {"locations": [loc_names.cda2,
                                   loc_names.cda0e,
                                   loc_names.cda0c,
                                   loc_names.cda0d,
                                   loc_names.cda0a,
                                   loc_names.cda0b],
                     "entrances": {"Top A Throne Room Entrance Area": ent_names.cda_exit_tfa,
                                   "Chapel A Bottom": ent_names.cda_down}},

    # Aqueduct A regions
    "Aqueduct A Top": {"entrances": {"Walkway A Dark Rooms Near Door": ent_names.ada_exit_swa,
                                     "Aqueduct A Main": ent_names.ada_down_u}},

    "Aqueduct A Main": {"locations": [loc_names.ada4,
                                      loc_names.ada8,
                                      loc_names.ada2,
                                      loc_names.ada1],
                        "entrances": {"Aqueduct A Top": ent_names.ada_djump_l,
                                      "Aqueduct A Bottom Shortcut Room": ent_names.ada_cstone_r,
                                      "Aqueduct A Merman Lair": ent_names.ada_djump_r}},

    "Aqueduct A Bottom Shortcut Room": {"entrances": {"Luminous A Top Shortcut Room": ent_names.ada_exit_lca,
                                                      "Aqueduct A Main": ent_names.ada_cstone_l}},

    "Aqueduct A Merman Lair": {"locations": [loc_names.ada10a,
                                             loc_names.ada10b],
                               "entrances": {"Clock A Bottom Entrance Room": ent_names.ada_exit_cra,
                                             "Aqueduct A Main": ent_names.ada_down_m}},

    # Clock Tower A regions
    "Clock A Bottom Entrance Room": {"entrances": {"Aqueduct A Merman Lair": ent_names.cra_exit_ada,
                                                   "Clock A Lower Area": ent_names.cra_djump_l}},

    "Clock A Lower Area": {"locations": [loc_names.cra9,
                                         loc_names.event_button_clock],
                           "entrances": {"Clock A Pendulum Area": ent_names.cra_button}},

    "Clock A Pendulum Area": {"locations": [loc_names.cra10,
                                            loc_names.cra0],
                              "entrances": {"Walkway A Clock Exit Room": ent_names.cra_exit_swa,
                                            "Clock A Main": ent_names.cra_djump_p}},

    "Clock A Main": {"locations": [loc_names.cra1,
                                   loc_names.cra3,
                                   loc_names.cra2,
                                   loc_names.cra14,
                                   loc_names.cra17a,
                                   loc_names.cra17b,
                                   loc_names.cra17c,
                                   loc_names.cra17d],
                     "entrances": {"Clock A Pendulum Area": ent_names.cra_down,
                                   "Clock A Ball Race": ent_names.cra_slide,
                                   "Clock A Right of Slimer": ent_names.cra_slimer_l}},

    "Clock A Right of Slimer": {"locations": [loc_names.cra20,
                                              loc_names.event_death],
                     "entrances": {"Clock A Main": ent_names.cra_slimer_r,
                                   "Clock B Right of Peeper": ent_names.cra_warp}},

    "Clock A Ball Race": {"locations": [loc_names.cra23,
                                        loc_names.cra22a,
                                        loc_names.cra22d,
                                        loc_names.cra22c,
                                        loc_names.cra22b]},

    # Castle Top Floor A regions
    "Top A Throne Room Entrance Area": {"entrances": {"Chapel A Top": ent_names.tfa_exit_cda,
                                                      "Top A Throne Room": ent_names.tfa_cstone_r}},

    "Top A Throne Room": {"locations": [loc_names.tfa15],
                          "entrances": {"Top B Throne Room": ent_names.tfa_warp,
                                        "Top A Attic": ent_names.tfa_cboots,
                                        "Top A Throne Room Entrance Area": ent_names.tfa_cstone_l,
                                        "Top A Lydie's Room": ent_names.tfa_pazuzu}},

    "Top A Lydie's Room": {"locations": [loc_names.event_button_top,
                                         loc_names.tfa1a,
                                         loc_names.tfa1b],
                           "entrances": {"Top A Middle": ent_names.tfa_button}},

    "Top A Attic": {"locations": [loc_names.tfa0b,
                                  loc_names.tfa0e,
                                  loc_names.tfa0a,
                                  loc_names.tfa0c,
                                  loc_names.tfa0d,
                                  loc_names.event_hand]},

    "Top A Middle": {"entrances": {"Top A Lower": ent_names.tfa_down}},

    "Top A Lower": {"locations": [loc_names.tfa7,
                                  loc_names.tfa8,
                                  loc_names.tfa11],
                    "entrances": {"Treasury A Upper": ent_names.tfa_exit_cya,
                                  "Top A Super Jump Passage": ent_names.tfa_sjump_r}},

    "Top A Super Jump Passage": {"locations": [loc_names.tfa9],
                                 "entrances": {"Corridor A Main": ent_names.tfa_exit_mca,
                                               "Top A Lower": ent_names.tfa_sjump_l}},

    # # # Castle B # # #
    # Entrance B regions
    "Entrance B Main": {"locations": [loc_names.etb0,
                                      loc_names.etb2b,
                                      loc_names.etb2a,
                                      loc_names.etb3,
                                      loc_names.etb11,
                                      loc_names.etb9],
                        "entrances": {"Shrine B End Room": ent_names.etb_exit_sab,
                                      "Corridor B Main": ent_names.etb_exit_mcb,
                                      "Entrance A Main": ent_names.etb_warp_u,
                                      "Entrance B Sub Shaft": ent_names.etb_cstone_ul}},

    "Entrance B Sub Shaft": {"locations": [loc_names.etb13a,
                                           loc_names.etb13b,
                                           loc_names.etb13c],
                             "entrances": {"Entrance A Sub Shaft": ent_names.etb_warp_l,
                                           "Entrance B Main": ent_names.etb_cstone_ur,
                                           "Entrance B Sub Shaft Bottom": ent_names.etb_cstone_ll}},

    "Entrance B Sub Shaft Bottom": {"entrances": {"Skeleton B Left Exit Area": ent_names.etb_exit_scb,
                                                  "Entrance B Sub Shaft": ent_names.etb_cstone_lr}},

    # Marble Corridor B region
    "Corridor B Main": {"locations": [loc_names.mcb2,
                                      loc_names.mcb9,
                                      loc_names.mcb10,
                                      loc_names.mcb11,
                                      loc_names.mcb12],
                        "entrances": {"Entrance B Main": ent_names.mcb_exit_etb,
                                      "Room B Left": ent_names.mcb_exit_rib_l,
                                      "Room B Right": ent_names.mcb_exit_rib_r,
                                      "Wailing B Main": ent_names.mcb_exit_wwb,
                                      "Top B Super Jump Passage": ent_names.mcb_exit_tfb}},

    # Room of Illusion B regions
    "Room B Left": {"locations": [loc_names.rib16],
                    "entrances": {"Corridor B Main": ent_names.rib_exit_mcb_l}},

    "Room B Right": {"locations": [loc_names.rib19],
                     "entrances": {"Corridor B Main": ent_names.rib_exit_mcb_r}},

    # The Wailing Way B region
    "Wailing B Main": {"locations": [loc_names.wwb0a,
                                     loc_names.wwb0b,
                                     loc_names.wwb3,
                                     loc_names.wwb4c,
                                     loc_names.wwb4b,
                                     loc_names.wwb4a],
                       "entrances": {"Corridor B Main": ent_names.wwb_exit_mcb,
                                     "Treasury B Upper": ent_names.wwb_exit_cyb,
                                     "Shrine B Main": ent_names.wwb_exit_sab}},

    # Shrine of the Apostates B region
    "Shrine B Main": {"locations": [loc_names.sab5,
                                    loc_names.sab7,
                                    loc_names.sab11,
                                    loc_names.sab12],
                      "entrances": {"Wailing B Main": ent_names.sab_exit_wwb,
                                    "Shrine B End Room": ent_names.sab_cyclops_r}},

    "Shrine B End Room": {"locations": [loc_names.sab15],
                          "entrances": {"Shrine B Main": ent_names.sab_cyclops_l,
                                        "Entrance B Main": ent_names.sab_exit_etb}},

    # Castle Treasury B regions
    "Treasury B Lower": {"locations": [loc_names.cyb8,
                                       loc_names.cyb5,
                                       loc_names.cyb0a,
                                       loc_names.cyb0b,
                                       loc_names.cyb1,
                                       loc_names.cyb11,
                                       loc_names.cyb12,
                                       loc_names.cyb20],
                         "entrances": {"Room and Treasury Portal": ent_names.cyb_portal,
                                       "Treasury A Lower": ent_names.cyb_warp,
                                       "Skeleton B Main": ent_names.cyb_exit_scb,
                                       "Luminous B Main": ent_names.cyb_exit_lcb,
                                       "Treasury B Upper": ent_names.cyb_djump,
                                       "The Empty Room": ent_names.cyb_room}},

    "Treasury B Upper": {"locations": [loc_names.cyb18a,
                                       loc_names.cyb18b,
                                       loc_names.event_ending_b,
                                       loc_names.event_ending_g],
                         "entrances": {"Wailing B Main": ent_names.cyb_exit_wwb,
                                       "Top B Lower": ent_names.cyb_exit_tfb,
                                       "Treasury B Lower": ent_names.cyb_down}},

    # Skeleton Cave B regions
    "Skeleton B Main": {"locations": [loc_names.scb1b,
                                      loc_names.scb1a,
                                      loc_names.scb3,
                                      loc_names.scb2,
                                      loc_names.scb4,
                                      loc_names.scb5,
                                      loc_names.scb12a,
                                      loc_names.scb12b,
                                      loc_names.scb10,
                                      loc_names.scb11],
                        "entrances": {"Treasury B Lower": ent_names.scb_exit_cyb,
                                      "Skeleton B Left Exit Area": ent_names.scb_rock}},

    "Skeleton B Left Exit Area": {"locations": [loc_names.scb13],
                                  "entrances": {"Entrance B Sub Shaft Bottom": ent_names.scb_exit_etb}},

    # Luminous Cavern B regions
    "Luminous B Main": {"locations": [loc_names.lcb3,
                                      loc_names.lcb7a,
                                      loc_names.lcb7b,
                                      loc_names.lcb22a,
                                      loc_names.lcb22b,
                                      loc_names.lcb13,
                                      loc_names.lcb16,
                                      loc_names.lcb8a,
                                      loc_names.lcb8b,
                                      loc_names.lcb10b,
                                      loc_names.lcb10a,
                                      loc_names.lcb17,
                                      loc_names.lcb18],
                        "entrances": {"Treasury B Lower": ent_names.lcb_exit_cyb,
                                      "Luminous and Walkway Portal": ent_names.lcb_portal,
                                      "Luminous B Top Shortcut Room": ent_names.lcb_sjump_l}},

    "Luminous B Top Shortcut Room": {"entrances": {"Aqueduct B Bottom Shortcut Room": ent_names.lcb_exit_adb,
                                                   "Luminous B Main": ent_names.lcb_sjump_r}},

    # Sky Walkway B regions
    "Walkway B Main": {"locations": [loc_names.swb8,
                                     loc_names.event_wall_sky,
                                     loc_names.swb19,
                                     loc_names.swb10c,
                                     loc_names.swb10b,
                                     loc_names.swb10a,
                                     loc_names.swb15,
                                     loc_names.swb12a,
                                     loc_names.swb12b,
                                     loc_names.swb16],
                       "entrances": {"Chapel B Bottom": ent_names.swb_exit_cdb,
                                     "Walkway B Clock Exit Room": ent_names.swb_legion,
                                     "Walkway B Hall of Mirrors": ent_names.swb_down}},

    "Walkway B Clock Exit Room": {"locations": [loc_names.swb14],
                                  "entrances": {"Clock B Pendulum Area": ent_names.swb_exit_crb,
                                                "Walkway B Main": ent_names.swb_djump_c}},

    "Walkway B Hall of Mirrors": {"entrances": {"Aqueduct B Top": ent_names.swb_exit_adb,
                                                "Walkway B Main": ent_names.swb_djump_m}},

    # Chapel of Dissonance B regions
    "Chapel B Bottom": {"entrances": {"Walkway B Main": ent_names.cdb_exit_swb,
                                      "Chapel B Top": ent_names.cdb_djump}},

    "Chapel B Top": {"locations": [loc_names.cdb4,
                                   loc_names.cdb0e,
                                   loc_names.cdb0b,
                                   loc_names.cdb0d,
                                   loc_names.cdb0c,
                                   loc_names.cdb0a],
                     "entrances": {"Top B Throne Room": ent_names.cdb_exit_tfb,
                                   "Chapel B Bottom": ent_names.cdb_down}},

    # Aqueduct B regions
    "Aqueduct B Top": {"entrances": {"Walkway B Hall of Mirrors": ent_names.adb_exit_swb,
                                     "Aqueduct B Main": ent_names.adb_down_u}},

    "Aqueduct B Main": {"locations": [loc_names.adb4,
                                      loc_names.adb8,
                                      loc_names.adb2,
                                      loc_names.adb1],
                        "entrances": {"Aqueduct B Top": ent_names.adb_djump_l,
                                      "Aqueduct B Bottom Shortcut Room": ent_names.adb_cstone_r,
                                      "Aqueduct B Merman Lair": ent_names.adb_djump_r}},

    "Aqueduct B Bottom Shortcut Room": {"locations": [loc_names.adb0],
                                        "entrances": {"Luminous B Top Shortcut Room": ent_names.adb_exit_lcb,
                                                      "Aqueduct B Main": ent_names.adb_cstone_l}},

    "Aqueduct B Merman Lair": {"entrances": {"Clock B Bottom Entrance Room": ent_names.adb_exit_crb,
                                             "Aqueduct B Main": ent_names.adb_down_m}},

    # Clock Tower B regions
    "Clock B Bottom Entrance Room": {"entrances": {"Aqueduct B Merman Lair": ent_names.crb_exit_adb,
                                                   "Clock B Lower Area": ent_names.crb_djump_l}},

    "Clock B Lower Area": {"locations": [loc_names.crb8,
                                         loc_names.event_crank],
                           "entrances": {"Clock B Pendulum Area": ent_names.crb_abutton_b}},

    "Clock B Pendulum Area": {"locations": [loc_names.crb6b,
                                            loc_names.crb6a,
                                            loc_names.crb10],
                              "entrances": {"Walkway B Clock Exit Room": ent_names.crb_exit_swb,
                                            "Clock B Lower Area": ent_names.crb_abutton_t,
                                            "Clock B Main": ent_names.crb_djump_p}},

    "Clock B Main": {"locations": [loc_names.crb1,
                                   loc_names.crb3,
                                   loc_names.crb2,
                                   loc_names.crb4],
                     "entrances": {"Clock B Pendulum Area": ent_names.crb_down,
                                   "Clock B Right of Peeper": ent_names.crb_peep_l}},

    "Clock B Right of Peeper": {"locations": [loc_names.crb13,
                                              loc_names.event_guarder,
                                              loc_names.crb17,
                                              loc_names.crb20],
                                "entrances": {"Clock B Main": ent_names.crb_peep_r,
                                              "Clock B Ball Race": ent_names.crb_slide,
                                              "Clock A Right of Slimer": ent_names.crb_warp}},

    "Clock B Ball Race": {"locations": [loc_names.crb23b,
                                        loc_names.crb23a,
                                        loc_names.crb22b,
                                        loc_names.crb22a]},

    # Castle Top Floor B regions
    "Top B Throne Room": {"locations": [loc_names.tfb3],
                          "entrances": {"Chapel B Top": ent_names.tfb_exit_cdb,
                                        "Top A Throne Room": ent_names.tfb_warp,
                                        "Top B Attic": ent_names.tfb_cboots,
                                        "Top B Middle": ent_names.tfb_abutton_t}},

    "Top B Attic": {"locations": [loc_names.tfb0a,
                                  loc_names.tfb0b,
                                  loc_names.tfb0c,
                                  loc_names.tfb0d,
                                  loc_names.tfb0e]},

    "Top B Middle": {"locations": [loc_names.tfb5],
                     "entrances": {"Top B Throne Room": ent_names.tfb_abutton_b,
                                   "Top B Lower": ent_names.tfb_down}},

    "Top B Lower": {"locations": [loc_names.tfb7,
                                  loc_names.tfb11a,
                                  loc_names.tfb11b],
                    "entrances": {"Treasury B Upper": ent_names.tfb_exit_cyb,
                                  "Top B Super Jump Passage": ent_names.tfb_sjump_r}},

    "Top B Super Jump Passage": {"entrances": {"Corridor B Main": ent_names.tfb_exit_mcb,
                                               "Top B Lower": ent_names.tfb_sjump_l}},

    # # # Misc. # # #
    "Room and Treasury Portal": {"locations": [loc_names.portals_rt],
                                 "entrances": {"Room A Past Slide Space": ent_names.rt_portal_exit_r,
                                               "Treasury B Lower": ent_names.rt_portal_exit_t}},

    "Luminous and Walkway Portal": {"locations": [loc_names.portals_lw],
                                    "entrances": {"Luminous B Main": ent_names.lw_portal_exit_l,
                                                  "Walkway A Portal Hallway": ent_names.lw_portal_exit_w}},

    "The Empty Room": {"locations": [loc_names.event_furniture]}
}


def get_region_info(region: str, info: str) -> list[str] | dict[str, str] | None:
    return ALL_CVHODIS_REGIONS[region].get(info, None)


def get_all_region_names() -> list[str]:
    return [reg_name for reg_name in ALL_CVHODIS_REGIONS]
