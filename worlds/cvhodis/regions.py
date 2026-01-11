from BaseClasses import Region
from .data import loc_names, ent_names, reg_names
from .entrances import CVHoDisEntrance
from typing import TypedDict, ClassVar


class CVHoDisRegion(Region):
    entrance_type: ClassVar[type[CVHoDisEntrance]] = CVHoDisEntrance


class CVHoDisRegionData(TypedDict):
    locations: list[str]  # List of Locations to add to the Region when the Region is added.
    entrances: list[str]  # List of Entrances to add to the Region when the Region is added.


ALL_CVHODIS_REGIONS: dict[str, CVHoDisRegionData] = {
    # # # Castle A # # #
    # Entrance A regions
    reg_names.eta_main: CVHoDisRegionData(locations=[loc_names.eta2,
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
                                          entrances=[ent_names.eta_warp_u,
                                                     ent_names.eta_exit_saa,
                                                     ent_names.eta_exit_mca,
                                                     ent_names.eta_cstone_ul]),

    reg_names.eta_sub: CVHoDisRegionData(locations=[loc_names.eta17],
                                         entrances=[ent_names.eta_warp_l,
                                                    ent_names.eta_cstone_ur,
                                                    ent_names.eta_cstone_ll]),

    reg_names.eta_sub_bottom: CVHoDisRegionData(locations=[],
                                                entrances=[ent_names.eta_exit_sca,
                                                           ent_names.eta_cstone_lr]),

    # Marble Corridor A region
    reg_names.mca: CVHoDisRegionData(locations=[loc_names.mca4,
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
                                     entrances=[ent_names.mca_exit_eta,
                                                ent_names.mca_exit_ria_l,
                                                ent_names.mca_exit_ria_r,
                                                ent_names.mca_exit_wwa,
                                                ent_names.mca_exit_tfa]),

    # Room of Illusion A regions
    reg_names.ria_left: CVHoDisRegionData(locations=[loc_names.ria16],
                                          entrances=[ent_names.ria_exit_mca_l]),

    reg_names.ria_right: CVHoDisRegionData(locations=[loc_names.ria15],
                                           entrances=[ent_names.ria_exit_mca_r,
                                                      ent_names.ria_slide_r]),

    reg_names.ria_right_slide: CVHoDisRegionData(locations=[loc_names.ria17],
                                                 entrances=[ent_names.ria_slide_l,
                                                            ent_names.ria_portal]),

    # The Wailing Way A region
    reg_names.wwa: CVHoDisRegionData(locations=[loc_names.wwa0b,
                                                loc_names.wwa1,
                                                loc_names.wwa3,
                                                loc_names.wwa4b,
                                                loc_names.wwa4a,
                                                loc_names.wwa0a,
                                                loc_names.wwa0d,
                                                loc_names.wwa0c,
                                                loc_names.wwa8],
                                     entrances=[ent_names.wwa_exit_mca,
                                                ent_names.wwa_exit_cya,
                                                ent_names.wwa_exit_saa]),

    # Shrine of the Apostates A regions
    reg_names.saa_main: CVHoDisRegionData(locations=[loc_names.saa10,
                                                     loc_names.saa16,
                                                     loc_names.saa6b,
                                                     loc_names.saa6a,
                                                     loc_names.saa7,
                                                     loc_names.saa12,
                                                     loc_names.saa15],
                                          entrances=[ent_names.saa_exit_wwa,
                                                     ent_names.saa_button]),

    reg_names.saa_end: CVHoDisRegionData(locations=[],
                                         entrances=[ent_names.saa_exit_eta]),

    # Castle Treasury A regions
    reg_names.cya_lower: CVHoDisRegionData(locations=[loc_names.cya6,
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
                                           entrances=[ent_names.cya_warp,
                                                      ent_names.cya_exit_sca,
                                                      ent_names.cya_exit_lca,
                                                      ent_names.cya_djumps,
                                                      ent_names.cya_room]),

    reg_names.cya_upper: CVHoDisRegionData(locations=[loc_names.cya18,
                                                      loc_names.cya19,
                                                      loc_names.event_ending_m],
                                           entrances=[ent_names.cya_exit_wwa,
                                                      ent_names.cya_exit_tfa,
                                                      ent_names.cya_down]),

    # Skeleton Cave A regions
    reg_names.sca_right: CVHoDisRegionData(locations=[loc_names.sca1b,
                                                      loc_names.sca1a,
                                                      loc_names.sca2,
                                                      loc_names.sca4],
                                           entrances=[ent_names.sca_exit_cya,
                                                      ent_names.sca_crates_r]),

    reg_names.sca_left: CVHoDisRegionData(locations=[loc_names.sca5,
                                                     loc_names.sca12a,
                                                     loc_names.sca12b,
                                                     loc_names.sca10,
                                                     loc_names.sca19,
                                                     loc_names.sca11,
                                                     loc_names.sca13,
                                                     loc_names.event_wall_skeleton],
                                          entrances=[ent_names.sca_exit_eta,
                                                     ent_names.sca_crates_l]),

    # Luminous Cavern A regions
    reg_names.lca_main: CVHoDisRegionData(locations=[loc_names.lca3,
                                                     loc_names.lca7a,
                                                     loc_names.lca7b,
                                                     loc_names.lca11,
                                                     loc_names.lca22,
                                                     loc_names.lca14],
                                          entrances=[ent_names.lca_exit_cya,
                                                     ent_names.lca_warp,
                                                     ent_names.lca_floodgate,
                                                     ent_names.lca_talos,
                                                     ent_names.lca_sjump_l]),

    reg_names.lca_top: CVHoDisRegionData(locations=[],
                                         entrances=[ent_names.lca_exit_ada,
                                                    ent_names.lca_sjump_r]),

    reg_names.lca_talos: CVHoDisRegionData(locations=[loc_names.lca8b,
                                                      loc_names.lca8c,
                                                      loc_names.lca8a,
                                                      loc_names.lca10],
                                           entrances=[]),

    reg_names.lca_death: CVHoDisRegionData(locations=[loc_names.lca17,
                                                      loc_names.lca18,
                                                      loc_names.lca23],
                                           entrances=[]),

    # Sky Walkway A regions
    reg_names.swa_portal: CVHoDisRegionData(locations=[loc_names.swa10c,
                                                       loc_names.swa10b],
                                            entrances=[ent_names.swa_portal,
                                                       ent_names.swa_djump_p]),

    reg_names.swa_main: CVHoDisRegionData(locations=[loc_names.swa10a,
                                                     loc_names.swa7,
                                                     loc_names.swa15a,
                                                     loc_names.swa15b,
                                                     loc_names.swa12c,
                                                     loc_names.swa12a,
                                                     loc_names.swa12b],
                                          entrances=[ent_names.swa_exit_cda,
                                                     ent_names.swa_down_p,
                                                     ent_names.swa_devil,
                                                     ent_names.swa_goggles_u]),

    reg_names.swa_right_exit: CVHoDisRegionData(locations=[loc_names.swa14],
                                                entrances=[ent_names.swa_exit_cra,
                                                           ent_names.swa_djump_c]),

    reg_names.swa_dark: CVHoDisRegionData(locations=[loc_names.swa17,
                                                     loc_names.swa18b,
                                                     loc_names.swa18a],
                                          entrances=[ent_names.swa_dark_d,
                                                     ent_names.swa_dark_u]),

    reg_names.swa_dark_exit: CVHoDisRegionData(locations=[],
                                               entrances=[ent_names.swa_exit_ada,
                                                          ent_names.swa_goggles_l]),

    # Chapel of Dissonance A regions
    reg_names.cda_lower: CVHoDisRegionData(locations=[],
                                           entrances=[ent_names.cda_exit_swa,
                                                      ent_names.cda_djump]),

    reg_names.cda_upper: CVHoDisRegionData(locations=[loc_names.cda2,
                                                      loc_names.cda0e,
                                                      loc_names.cda0c,
                                                      loc_names.cda0d,
                                                      loc_names.cda0a,
                                                      loc_names.cda0b],
                                           entrances=[ent_names.cda_exit_tfa,
                                                      ent_names.cda_down]),

    # Aqueduct A regions
    reg_names.ada_top: CVHoDisRegionData(locations=[],
                                         entrances=[ent_names.ada_exit_swa,
                                                    ent_names.ada_down_u]),

    reg_names.ada_main: CVHoDisRegionData(locations=[loc_names.ada4,
                                                     loc_names.ada8,
                                                     loc_names.ada2,
                                                     loc_names.ada1],
                                          entrances=[ent_names.ada_djump_l,
                                                     ent_names.ada_cstone_r,
                                                     ent_names.ada_djump_r]),

    reg_names.ada_lower: CVHoDisRegionData(locations=[],
                                           entrances=[ent_names.ada_exit_lca,
                                                      ent_names.ada_cstone_l]),

    reg_names.ada_merman: CVHoDisRegionData(locations=[loc_names.ada10a,
                                                       loc_names.ada10b],
                                            entrances=[ent_names.ada_exit_cra,
                                                       ent_names.ada_down_m]),

    # Clock Tower A regions
    reg_names.cra_lower_exit: CVHoDisRegionData(locations=[],
                                                entrances=[ent_names.cra_exit_ada,
                                                           ent_names.cra_djump_l]),

    reg_names.cra_lower: CVHoDisRegionData(locations=[loc_names.cra9,
                                                      loc_names.event_button_clock],
                                           entrances=[ent_names.cra_button]),

    reg_names.cra_pendulums: CVHoDisRegionData(locations=[loc_names.cra10,
                                                          loc_names.cra0],
                                               entrances=[ent_names.cra_exit_swa,
                                                          ent_names.cra_djump_p]),

    reg_names.cra_main: CVHoDisRegionData(locations=[loc_names.cra1,
                                                     loc_names.cra3,
                                                     loc_names.cra2,
                                                     loc_names.cra14,
                                                     loc_names.cra17a,
                                                     loc_names.cra17b,
                                                     loc_names.cra17c,
                                                     loc_names.cra17d],
                                          entrances=[ent_names.cra_down,
                                                     ent_names.cra_slide,
                                                     ent_names.cra_slimer_l]),

    reg_names.cra_slimer: CVHoDisRegionData(locations=[loc_names.cra20,
                                                       loc_names.event_death],
                                            entrances=[ent_names.cra_slimer_r,
                                                       ent_names.cra_warp]),

    reg_names.cra_ball: CVHoDisRegionData(locations=[loc_names.cra23,
                                                     loc_names.cra22a,
                                                     loc_names.cra22d,
                                                     loc_names.cra22c,
                                                     loc_names.cra22b],
                                          entrances=[]),

    # Castle Top Floor A regions
    reg_names.tfa_throne_door: CVHoDisRegionData(locations=[],
                                                 entrances=[ent_names.tfa_exit_cda,
                                                            ent_names.tfa_cstone_r]),

    reg_names.tfa_throne: CVHoDisRegionData(locations=[loc_names.tfa15],
                                            entrances=[ent_names.tfa_warp,
                                                       ent_names.tfa_cboots,
                                                       ent_names.tfa_cstone_l,
                                                       ent_names.tfa_pazuzu]),

    reg_names.tfa_lydie: CVHoDisRegionData(locations=[loc_names.event_button_top,
                                                      loc_names.tfa1a,
                                                      loc_names.tfa1b],
                                           entrances=[ent_names.tfa_button]),

    reg_names.tfa_attic: CVHoDisRegionData(locations=[loc_names.tfa0b,
                                                      loc_names.tfa0e,
                                                      loc_names.tfa0a,
                                                      loc_names.tfa0c,
                                                      loc_names.tfa0d,
                                                      loc_names.event_hand],
                                           entrances=[]),

    reg_names.tfa_middle: CVHoDisRegionData(locations=[],
                                            entrances=[ent_names.tfa_down]),

    reg_names.tfa_lower: CVHoDisRegionData(locations=[loc_names.tfa7,
                                                      loc_names.tfa8,
                                                      loc_names.tfa11],
                                           entrances=[ent_names.tfa_exit_cya,
                                                      ent_names.tfa_sjump_r]),

    reg_names.tfa_sjumps: CVHoDisRegionData(locations=[loc_names.tfa9],
                                            entrances=[ent_names.tfa_exit_mca,
                                                       ent_names.tfa_sjump_l]),

    # # # Castle B # # #
    # Entrance B regions
    reg_names.etb_main: CVHoDisRegionData(locations=[loc_names.etb0,
                                                     loc_names.etb2b,
                                                     loc_names.etb2a,
                                                     loc_names.etb3,
                                                     loc_names.etb11,
                                                     loc_names.etb9],
                                          entrances=[ent_names.etb_exit_sab,
                                                     ent_names.etb_exit_mcb,
                                                     ent_names.etb_warp_u,
                                                     ent_names.etb_cstone_ul]),

    reg_names.etb_sub: CVHoDisRegionData(locations=[loc_names.etb13a,
                                                    loc_names.etb13b,
                                                    loc_names.etb13c],
                                         entrances=[ent_names.etb_warp_l,
                                                    ent_names.etb_cstone_ur,
                                                    ent_names.etb_cstone_ll]),

    reg_names.etb_sub_bottom: CVHoDisRegionData(locations=[],
                                                entrances=[ent_names.etb_exit_scb,
                                                           ent_names.etb_cstone_lr]),

    # Marble Corridor B region
    reg_names.mcb: CVHoDisRegionData(locations=[loc_names.mcb2,
                                                loc_names.mcb9,
                                                loc_names.mcb10,
                                                loc_names.mcb11,
                                                loc_names.mcb12],
                                     entrances=[ent_names.mcb_exit_etb,
                                                ent_names.mcb_exit_rib_l,
                                                ent_names.mcb_exit_rib_r,
                                                ent_names.mcb_exit_wwb,
                                                ent_names.mcb_exit_tfb]),

    # Room of Illusion B regions
    reg_names.rib_left: CVHoDisRegionData(locations=[loc_names.rib16],
                                          entrances=[ent_names.rib_exit_mcb_l]),

    reg_names.rib_right: CVHoDisRegionData(locations=[loc_names.rib19],
                                           entrances=[ent_names.rib_exit_mcb_r]),

    # The Wailing Way B region
    reg_names.wwb: CVHoDisRegionData(locations=[loc_names.wwb0a,
                                                loc_names.wwb0b,
                                                loc_names.wwb3,
                                                loc_names.wwb4c,
                                                loc_names.wwb4b,
                                                loc_names.wwb4a],
                                     entrances=[ent_names.wwb_exit_mcb,
                                                ent_names.wwb_exit_cyb,
                                                ent_names.wwb_exit_sab]),

    # Shrine of the Apostates B region
    reg_names.sab_main: CVHoDisRegionData(locations=[loc_names.sab5,
                                                     loc_names.sab7,
                                                     loc_names.sab11,
                                                     loc_names.sab12],
                                          entrances=[ent_names.sab_exit_wwb,
                                                     ent_names.sab_cyclops_r]),

    reg_names.sab_end: CVHoDisRegionData(locations=[loc_names.sab15],
                                         entrances=[ent_names.sab_cyclops_l,
                                                    ent_names.sab_exit_etb]),

    # Castle Treasury B regions
    reg_names.cyb_lower: CVHoDisRegionData(locations=[loc_names.cyb8,
                                                      loc_names.cyb5,
                                                      loc_names.cyb0a,
                                                      loc_names.cyb0b,
                                                      loc_names.cyb1,
                                                      loc_names.cyb11,
                                                      loc_names.cyb12,
                                                      loc_names.cyb20],
                                           entrances=[ent_names.cyb_portal,
                                                      ent_names.cyb_warp,
                                                      ent_names.cyb_exit_scb,
                                                      ent_names.cyb_exit_lcb,
                                                      ent_names.cyb_djump,
                                                      ent_names.cyb_room]),

    reg_names.cyb_upper: CVHoDisRegionData(locations=[loc_names.cyb18a,
                                                      loc_names.cyb18b,
                                                      loc_names.event_ending_b,
                                                      loc_names.event_ending_g],
                                           entrances=[ent_names.cyb_exit_wwb,
                                                      ent_names.cyb_exit_tfb,
                                                      ent_names.cyb_down]),

    # Skeleton Cave B regions
    reg_names.scb_main: CVHoDisRegionData(locations=[loc_names.scb1b,
                                                     loc_names.scb1a,
                                                     loc_names.scb3,
                                                     loc_names.scb2,
                                                     loc_names.scb4,
                                                     loc_names.scb5,
                                                     loc_names.scb12a,
                                                     loc_names.scb12b,
                                                     loc_names.scb10,
                                                     loc_names.scb11],
                                          entrances=[ent_names.scb_exit_cyb,
                                                     ent_names.scb_rock]),

    reg_names.scb_left_exit: CVHoDisRegionData(locations=[loc_names.scb13],
                                               entrances=[ent_names.scb_exit_etb]),

    # Luminous Cavern B regions
    reg_names.lcb_main: CVHoDisRegionData(locations=[loc_names.lcb3,
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
                                          entrances=[ent_names.lcb_exit_cyb,
                                                     ent_names.lcb_portal,
                                                     ent_names.lcb_sjump_l]),

    reg_names.lcb_top: CVHoDisRegionData(locations=[],
                                         entrances=[ent_names.lcb_exit_adb,
                                                    ent_names.lcb_sjump_r]),

    # Sky Walkway B regions
    reg_names.swb_main: CVHoDisRegionData(locations=[loc_names.swb8,
                                                     loc_names.event_wall_sky,
                                                     loc_names.swb19,
                                                     loc_names.swb10c,
                                                     loc_names.swb10b,
                                                     loc_names.swb10a,
                                                     loc_names.swb15,
                                                     loc_names.swb12a,
                                                     loc_names.swb12b,
                                                     loc_names.swb16],
                                          entrances=[ent_names.swb_exit_cdb,
                                                     ent_names.swb_legion,
                                                     ent_names.swb_down]),

    reg_names.swb_right_exit: CVHoDisRegionData(locations=[loc_names.swb14],
                                                entrances=[ent_names.swb_exit_crb,
                                                           ent_names.swb_djump_c]),

    reg_names.swb_mirrors: CVHoDisRegionData(locations=[],
                                             entrances=[ent_names.swb_exit_adb,
                                                        ent_names.swb_djump_m]),

    # Chapel of Dissonance B regions
    reg_names.cdb_lower: CVHoDisRegionData(locations=[],
                                           entrances=[ent_names.cdb_exit_swb,
                                                      ent_names.cdb_djump]),

    reg_names.cdb_upper: CVHoDisRegionData(locations=[loc_names.cdb4,
                                                      loc_names.cdb0e,
                                                      loc_names.cdb0b,
                                                      loc_names.cdb0d,
                                                      loc_names.cdb0c,
                                                      loc_names.cdb0a],
                                           entrances=[ent_names.cdb_exit_tfb,
                                                      ent_names.cdb_down]),

    # Aqueduct B regions
    reg_names.adb_top: CVHoDisRegionData(locations=[],
                                         entrances=[ent_names.adb_exit_swb,
                                                    ent_names.adb_down_u]),

    reg_names.adb_main: CVHoDisRegionData(locations=[loc_names.adb4,
                                                     loc_names.adb8,
                                                     loc_names.adb2,
                                                     loc_names.adb1],
                                          entrances=[ent_names.adb_djump_l,
                                                     ent_names.adb_cstone_r,
                                                     ent_names.adb_djump_r]),

    reg_names.adb_lower: CVHoDisRegionData(locations=[loc_names.adb0],
                                           entrances=[ent_names.adb_exit_lcb,
                                                      ent_names.adb_cstone_l]),

    reg_names.adb_merman: CVHoDisRegionData(locations=[],
                                            entrances=[ent_names.adb_exit_crb,
                                                       ent_names.adb_down_m]),

    # Clock Tower B regions
    reg_names.crb_lower_exit: CVHoDisRegionData(locations=[],
                                                entrances=[ent_names.crb_exit_adb,
                                                           ent_names.crb_djump_l]),

    reg_names.crb_lower: CVHoDisRegionData(locations=[loc_names.crb8,
                                                      loc_names.event_crank],
                                           entrances=[ent_names.crb_abutton_b]),

    reg_names.crb_pendulums: CVHoDisRegionData(locations=[loc_names.crb6b,
                                                          loc_names.crb6a,
                                                          loc_names.crb10],
                                               entrances=[ent_names.crb_exit_swb,
                                                          ent_names.crb_abutton_t,
                                                          ent_names.crb_djump_p]),

    reg_names.crb_main: CVHoDisRegionData(locations=[loc_names.crb1,
                                                     loc_names.crb3,
                                                     loc_names.crb2,
                                                     loc_names.crb4],
                                          entrances=[ent_names.crb_down,
                                                     ent_names.crb_peep_l]),

    reg_names.crb_peeper: CVHoDisRegionData(locations=[loc_names.crb13,
                                                       loc_names.event_guarder,
                                                       loc_names.crb17,
                                                       loc_names.crb20],
                                            entrances=[ent_names.crb_peep_r,
                                                       ent_names.crb_slide,
                                                       ent_names.crb_warp]),

    reg_names.crb_ball: CVHoDisRegionData(locations=[loc_names.crb23b,
                                                     loc_names.crb23a,
                                                     loc_names.crb22b,
                                                     loc_names.crb22a],
                                          entrances=[]),

    # Castle Top Floor B regions
    reg_names.tfb_throne: CVHoDisRegionData(locations=[loc_names.tfb3],
                                            entrances=[ent_names.tfb_exit_cdb,
                                                       ent_names.tfb_warp,
                                                       ent_names.tfb_cboots,
                                                       ent_names.tfb_abutton_t]),

    reg_names.tfb_attic: CVHoDisRegionData(locations=[loc_names.tfb0a,
                                                      loc_names.tfb0b,
                                                      loc_names.tfb0c,
                                                      loc_names.tfb0d,
                                                      loc_names.tfb0e],
                                           entrances=[]),

    reg_names.tfb_middle: CVHoDisRegionData(locations=[loc_names.tfb5],
                                            entrances=[ent_names.tfb_abutton_b,
                                                       ent_names.tfb_down]),

    reg_names.tfb_lower: CVHoDisRegionData(locations=[loc_names.tfb7,
                                                      loc_names.tfb11a,
                                                      loc_names.tfb11b],
                                           entrances=[ent_names.tfb_exit_cyb,
                                                      ent_names.tfb_sjump_r]),

    reg_names.tfb_sjumps: CVHoDisRegionData(locations=[],
                                            entrances=[ent_names.tfb_exit_mcb,
                                                       ent_names.tfb_sjump_l]),

    # # # Misc. # # #
    reg_names.rt_portal: CVHoDisRegionData(locations=[loc_names.portals_rt],
                                           entrances=[ent_names.rt_portal_exit_r,
                                                      ent_names.rt_portal_exit_t]),

    reg_names.lw_portal: CVHoDisRegionData(locations=[loc_names.portals_lw],
                                           entrances=[ent_names.lw_portal_exit_l,
                                                      ent_names.lw_portal_exit_w]),

    reg_names.the_room: CVHoDisRegionData(locations=[loc_names.event_furniture],
                                          entrances=[])
}


def get_all_region_names() -> list[str]:
    return [reg_name for reg_name in ALL_CVHODIS_REGIONS]
