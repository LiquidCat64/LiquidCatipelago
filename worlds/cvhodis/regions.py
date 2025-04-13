from .data import loc_names
from typing import TypedDict


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
                        "entrances": {"Entrance B Main": "Entrance A Upper Warp Gate",
                                      "Shrine A End Room": "Entrance A Middle Door",
                                      "Corridor A Main": "Entrance A Top Door",
                                      "Entrance A Sub Shaft": "Entrance A Upper Crush Wall Left"}},

    "Entrance A Sub Shaft": {"locations": [loc_names.eta17],
                             "entrances": {"Entrance B Sub Shaft": "Entrance A Lower Warp Gate",
                                           "Entrance A Main": "Entrance A Upper Crush Wall Right",
                                           "Entrance A Sub Shaft Bottom": "Entrance A Lower Crush Wall Left"}},

    "Entrance A Sub Shaft Bottom": {"entrances": {"Skeleton A Left": "Entrance A Bottom Floor Transition",
                                                  "Entrance A Sub Shaft": "Entrance A Lower Crush Wall Right"}},

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
                                      loc_names.mca13],
                        "entrances": {"Entrance A Main": "Corridor A Left Door",
                                      "Room A Left": "Corridor A Left Shaft Transition",
                                      "Room A Right": "Corridor A Right Shaft Transition",
                                      "Wailing A Main": "Corridor A Bottom Door",
                                      "Top A Super Jump Passage": "Corridor A Right Skull Door"}},

    # Room of Illusion A regions
    "Room A Left": {"locations": [loc_names.ria16]},

    "Room A Right": {"locations": [loc_names.ria15],
                     "entrances": {"Corridor A Main": "Room A Right Transition",
                                   "Room A Past Slide Space": "Room A Slide Space Right"}},

    "Room A Past Slide Space": {"locations": [loc_names.ria17],
                                "entrances": {"Room A Right": "Room A Slide Space Left",
                                              "Room and Treasury Portal": "Room A Portal Room Entrance"}},

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
                       "entrances": {"Corridor A Main": "Wailing A Top Door",
                                     "Treasury A Upper": "Wailing A Right Skull Door",
                                     "Shrine A Main": "Wailing A Bottom Transition"}},

    # Shrine of the Apostates A regions
    "Shrine A Main": {"locations": [loc_names.saa10,
                                    loc_names.saa16,
                                    loc_names.saa6b,
                                    loc_names.saa6a,
                                    loc_names.saa7,
                                    loc_names.saa12,
                                    loc_names.saa15],
                      "entrances": {"Wailing A Main": "Shrine A Top Transition",
                                    "Shrine A End Room": "Shrine A Button Gate"}},

    "Shrine A End Room": {"entrances": {"Entrance A Main": "Shrine A Left Door"}},

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
                         "entrances": {"Treasury B Lower": "Treasury A Warp Gates",
                                       "Skeleton A Right": "Treasury A Bottom Left Door",
                                       "Luminous A Main": "Treasury A Bottom Right Door",
                                       "Treasury A Upper": "Treasury A Double Jumps",
                                       "The Empty Room": "Treasury A Empty Room Entrance"}},

    "Treasury A Upper": {"locations": [loc_names.cya18,
                                       loc_names.cya19,
                                       loc_names.event_ending_m],
                         "entrances": {"Wailing A Main": "Treasury A Top Skull Door",
                                       "Top A Lower": "Treasury A Top Ceiling Transition",
                                       "Treasury A Lower": "Treasury A Elevator Descent"}},

    # Skeleton Cave A regions
    "Skeleton A Right": {"locations": [loc_names.sca1b,
                                       loc_names.sca1a,
                                       loc_names.sca2,
                                       loc_names.sca4],
                         "entrances": {"Treasury A Lower": "Skeleton A Right Door",
                                       "Skeleton A Left": "Skeleton A Crate Rooms from Right"}},

    "Skeleton A Left": {"locations": [loc_names.sca5,
                                      loc_names.sca12a,
                                      loc_names.sca12b,
                                      loc_names.sca10,
                                      loc_names.sca19,
                                      loc_names.sca11,
                                      loc_names.sca13,
                                      loc_names.event_wall_skeleton],
                        "entrances": {"Entrance A Sub Shaft Bottom": "Skeleton A Left Ceiling Transition",
                                      "Skeleton A Right": "Skeleton A Crate Rooms from Left"}},

    # Luminous Cavern A regions
    "Luminous A Main": {"locations": [loc_names.lca3,
                                      loc_names.lca7a,
                                      loc_names.lca7b,
                                      loc_names.lca11,
                                      loc_names.lca22,
                                      loc_names.lca14],
                        "entrances": {"Treasury A Lower": "Luminous A Left Door",
                                      "Luminous B Main": "Luminous A Warp Gate",
                                      "Luminous A Underwater": "Luminous A Floodgate Keyhole",
                                      "Luminous A Post Talos": "Luminous A Talos's Arena",
                                      "Luminous A Top Shortcut Room": "Luminous A Top Super Jump from Left"}},

    "Luminous A Top Shortcut Room": {"entrances": {"Aqueduct A Bottom Shortcut Room": "Luminous A Top Door",
                                                   "Luminous A Main": "Luminous A Top Super Jump from Right"}},

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
                                 "entrances": {"Luminous and Walkway Portal": "Walkway A Portal Hallway End",
                                               "Walkway A Main": "Walkway A Double Jump from Portal Hall"}},

    "Walkway A Main": {"locations": [loc_names.swa10a,
                                     loc_names.swa7,
                                     loc_names.swa15a,
                                     loc_names.swa15b,
                                     loc_names.swa12c,
                                     loc_names.swa12a,
                                     loc_names.swa12b],
                       "entrances": {"Chapel A Bottom": "Walkway A Top Transition",
                                     "Walkway A Portal Hallway": "Walkway A Main Down-Leftward",
                                     "Walkway A Clock Exit Room": "Walkway A Past Devil",
                                     "Walkway A Dark Rooms": "Walkway A Main Downward"}},

    "Walkway A Clock Exit Room": {"locations": [loc_names.swa14],
                                  "entrances": {"Clock A Pendulum Area": "Walkway A Right Door",
                                                "Walkway A Main": "Walkway A Double Jump from Clock Exit"}},

    "Walkway A Dark Rooms": {"locations": [loc_names.swa17,
                                           loc_names.swa18b,
                                           loc_names.swa18a],
                             "entrances": {"Walkway A Dark Rooms Near Door": "Walkway A Downward Dark Navigation",
                                           "Walkway A Main": "Walkway A Upward Dark Navigation"}},

    "Walkway A Dark Rooms Near Door": {"entrances": {"Aqueduct A Top": "Walkway A Bottom Door",
                                                     "Walkway A Dark Rooms": "Walkway A Press Onwards in Darkness"}},

    # Chapel of Dissonance A regions
    "Chapel A Bottom": {"entrances": {"Walkway A Main": "Chapel A Bottom Transition",
                                      "Chapel A Top": "Chapel A Upward Hall Climb"}},

    "Chapel A Top": {"locations": [loc_names.cda2,
                                   loc_names.cda0e,
                                   loc_names.cda0c,
                                   loc_names.cda0d,
                                   loc_names.cda0a,
                                   loc_names.cda0b],
                     "entrances": {"Top A Throne Room Entrance Area": "Chapel A Top MK Door"}},

    # Aqueduct A regions
    "Aqueduct A Top": {"entrances": {"Walkway A Dark Rooms Near Door": "Aqueduct A Top-Left Door",
                                     "Aqueduct A Main": "Aqueduct A Down from Top"}},

    "Aqueduct A Main": {"locations": [loc_names.ada4,
                                      loc_names.ada8,
                                      loc_names.ada2,
                                      loc_names.ada1],
                        "entrances": {"Aqueduct A Top": "Aqueduct A Main Left Double Jump",
                                      "Aqueduct A Bottom Shortcut Room": "Aqueduct A Crush Wall Right",
                                      "Aqueduct A Merman Lair": "Aqueduct A Main Right Double Jump"}},

    "Aqueduct A Bottom Shortcut Room": {"entrances": {"Luminous A Top Shortcut Room": "Aqueduct A Bottom-Left Door",
                                                      "Aqueduct A Main": "Aqueduct A Crush Wall Left"}},

    "Aqueduct A Merman Lair": {"locations": [loc_names.ada10a,
                                             loc_names.ada10b],
                               "entrances": {"Clock A Bottom Entrance Room": "Aqueduct A Top-Right Door",
                                             "Aqueduct A Main": "Aqueduct A Down from Merman Lair"}},

    # Clock Tower A regions
    "Clock A Bottom Entrance Room": {"entrances": {"Aqueduct A Merman Lair": "Clock A Bottom Door",
                                                   "Clock A Lower Area": "Clock A Double Jump from Bottom"}},

    "Clock A Lower Area": {"locations": [loc_names.cra9,
                                         loc_names.event_button_clock],
                           "entrances": {"Clock A Pendulum Area": "Clock A Lower Button Press"}},

    "Clock A Pendulum Area": {"locations": [loc_names.cra10,
                                            loc_names.cra0],
                              "entrances": {"Walkway A Clock Exit Room": "Clock A Top Door",
                                            "Clock A Main": "Clock A Double Jumps from Pendulum Area"}},

    "Clock A Main": {"locations": [loc_names.cra1,
                                   loc_names.cra3,
                                   loc_names.cra2,
                                   loc_names.cra14,
                                   loc_names.cra17a,
                                   loc_names.cra17b,
                                   loc_names.cra17c,
                                   loc_names.cra17d],
                     "entrances": {"Clock A Pendulum Area": "Clock A Down from Main",
                                   "Clock A Ball Race": "Clock A Slide Space",
                                   "Clock A Right of Slimer": "Clock A Max Slimer's Arena Left"}},

    "Clock A Right of Slimer": {"locations": [loc_names.cra20],
                     "entrances": {"Clock A Main": "Clock A Max Slimer's Arena Right",
                                   "Clock B Right of Peeper": "Clock A Warp Gate"}},

    "Clock A Ball Race": {"locations": [loc_names.cra23,
                                        loc_names.cra22a,
                                        loc_names.cra22d,
                                        loc_names.cra22c,
                                        loc_names.cra22b]},

    # Castle Top Floor A regions
    "Top A Throne Room Entrance Area": {"entrances": {"Chapel A Top": "Top A Top MK Door",
                                                      "Top A Throne Room": "Top A Crush Wall Right"}},

    "Top A Throne Room": {"locations": [loc_names.tfa15],
                          "entrances": {"Top B Throne Room": "Top A Warp Gate",
                                        "Top A Attic": "Top A Crush Blocks",
                                        "Top A Throne Room Entrance Area": "Top A Crush Wall Left",
                                        "Top A Lydie's Room": "Top A Pazuzu's Arena"}},

    "Top A Lydie's Room": {"locations": [loc_names.event_button_top,
                                         loc_names.tfa1a,
                                         loc_names.tfa1b],
                           "entrances": {"Top A Middle": "Top A Throne Button Press"}},

    "Top A Attic": {"locations": [loc_names.tfa0b,
                                  loc_names.tfa0e,
                                  loc_names.tfa0a,
                                  loc_names.tfa0c,
                                  loc_names.tfa0d,
                                  loc_names.event_hand]},

    "Top A Middle": {"entrances": {"Top A Lower": "Top A Down from Middle"}},

    "Top A Lower": {"locations": [loc_names.tfa7,
                                  loc_names.tfa8,
                                  loc_names.tfa11],
                    "entrances": {"Treasury A Upper": "Top A Bottom Floor Transition",
                                  "Top A Super Jump Passage": "Top A Lower Super Jump from Right"}},

    "Top A Super Jump Passage": {"locations": [loc_names.tfa9],
                                 "entrances": {"Corridor A Main": "Top A Bottom Skull Door",
                                               "Top A Lower": "Top A Lower Super Jump from Left"}},

    # # # Castle B # # #
    # Entrance B regions
    "Entrance B Main": {"locations": [loc_names.etb0,
                                      loc_names.etb2b,
                                      loc_names.etb2a,
                                      loc_names.etb3,
                                      loc_names.etb11,
                                      loc_names.etb9],
                        "entrances": {"Shrine B End Room": "Entrance B Middle Door",
                                      "Corridor B Main": "Entrance B Top Door",
                                      "Entrance A Main": "Entrance B Upper Warp Gate",
                                      "Entrance B Sub Shaft": "Entrance B Upper Crush Wall Left"}},

    "Entrance B Sub Shaft": {"locations": [loc_names.etb13a,
                                           loc_names.etb13b,
                                           loc_names.etb13c],
                             "entrances": {"Entrance A Sub Shaft": "Entrance B Lower Warp Gate",
                                           "Entrance B Main": "Entrance B Upper Crush Wall Right",
                                           "Entrance B Sub Shaft Bottom": "Entrance B Lower Crush Wall Left"}},

    "Entrance B Sub Shaft Bottom": {"entrances": {"Skeleton B Left Exit Area": "Entrance B Bottom Floor Transition",
                                                  "Entrance B Sub Shaft": "Entrance B Lower Crush Wall Right"}},

    # Marble Corridor B region
    "Corridor B Main": {"locations": [loc_names.mcb2,
                                      loc_names.mcb9,
                                      loc_names.mcb10,
                                      loc_names.mcb11,
                                      loc_names.mcb12],
                        "entrances": {"Entrance B Main": "Corridor B Left Door",
                                      "Room B Left": "Corridor B Left Shaft Transition",
                                      "Room B Right": "Corridor B Right Shaft Transition",
                                      "Wailing B Main": "Corridor B Bottom Door",
                                      "Top B Super Jump Passage": "Corridor B Right Skull Door"}},

    # Room of Illusion B regions
    "Room B Left": {"locations": [loc_names.rib16]},

    "Room B Right": {"locations": [loc_names.rib19]},

    # The Wailing Way B region
    "Wailing B Main": {"locations": [loc_names.wwb0a,
                                     loc_names.wwb0b,
                                     loc_names.wwb3,
                                     loc_names.wwb4c,
                                     loc_names.wwb4b,
                                     loc_names.wwb4a],
                       "entrances": {"Corridor B Main": "Wailing B Top Door",
                                     "Treasury B Upper": "Wailing B Right Skull Door",
                                     "Shrine B Main": "Wailing B Bottom Transition"}},

    # Shrine of the Apostates B region
    "Shrine B Main": {"locations": [loc_names.sab5,
                                    loc_names.sab7,
                                    loc_names.sab11,
                                    loc_names.sab12],
                      "entrances": {"Wailing B Main": "Shrine B Top Transition",
                                    "Shrine B End Room": "Shrine B Cyclops's Arena Right"}},

    "Shrine B End Room": {"locations": [loc_names.sab15],
                          "entrances": {"Shrine B Main": "Shrine B Cyclops's Arena Left",
                                        "Entrance B Main": "Shrine B Left Door"}},

    # Castle Treasury B regions
    "Treasury B Lower": {"locations": [loc_names.cyb8,
                                       loc_names.cyb5,
                                       loc_names.cyb0a,
                                       loc_names.cyb0b,
                                       loc_names.cyb1,
                                       loc_names.cyb11,
                                       loc_names.cyb12,
                                       loc_names.cyb20],
                         "entrances": {"Room and Treasury Portal": "Treasury B Portal Hallway End",
                                       "Treasury A Lower": "Treasury B Warp Gates",
                                       "Skeleton B Main": "Treasury B Bottom Left Door",
                                       "Luminous B Main": "Treasury B Bottom Right Door",
                                       "Treasury B Upper": "Treasury B Double Jumps",
                                       "The Empty Room": "Treasury B Empty Room Entrance"}},

    "Treasury B Upper": {"locations": [loc_names.cyb18a,
                                       loc_names.cyb18b,
                                       loc_names.event_ending_b,
                                       loc_names.event_ending_g],
                         "entrances": {"Wailing B Main": "Treasury B Top Skull Door",
                                       "Top B Lower": "Treasury B Top Ceiling Transition",
                                       "Treasury B Lower": "Treasury B Elevator Descent"}},

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
                        "entrances": {"Treasury B Lower": "Skeleton B Right Door",
                                      "Skeleton B Left Exit Area": "Skeleton B Right Collapsing Rock"}},

    "Skeleton B Left Exit Area": {"locations": [loc_names.scb13],
                                  "entrances": {"Entrance A Sub Shaft Bottom": "Skeleton B Left Ceiling Transition"}},

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
                        "entrances": {"Treasury B Lower": "Luminous B Left Door",
                                      "Luminous and Walkway Portal": "Luminous B Portal Area Double Jump",
                                      "Luminous B Top Shortcut Room": "Luminous B Top Super Jump from Left"}},

    "Luminous B Top Shortcut Room": {"entrances": {"Aqueduct B Bottom Shortcut Room": "Luminous B Top Door",
                                                   "Luminous B Main": "Luminous B Top Super Jump from Right"}},

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
                       "entrances": {"Chapel B Bottom": "Walkway B Top Transition",
                                     "Walkway B Clock Exit Room": "Walkway B Past Legion (saint)",
                                     "Walkway B Hall of Mirrors": "Walkway B Main Downward"}},

    "Walkway B Clock Exit Room": {"locations": [loc_names.swb14],
                                  "entrances": {"Clock B Pendulum Area": "Walkway B Right Door",
                                                "Walkway B Main": "Walkway B Double Jump from Clock Exit"}},

    "Walkway B Hall of Mirrors": {"entrances": {"Aqueduct B Top": "Walkway B Bottom Door",
                                                "Walkway B Main": "Walkway B Hall of Mirrors Double Jumps"}},

    # Chapel of Dissonance B regions
    "Chapel B Bottom": {"entrances": {"Walkway B Main": "Chapel B Bottom Transition",
                                      "Chapel B Top": "Chapel B Upward Hall Climb"}},

    "Chapel B Top": {"locations": [loc_names.cdb4,
                                   loc_names.cdb0e,
                                   loc_names.cdb0b,
                                   loc_names.cdb0d,
                                   loc_names.cdb0c,
                                   loc_names.cdb0a],
                     "entrances": {"Top B Throne Room": "Chapel B Top MK Door",
                                   "Chapel B Bottom": "Chapel B Downward Hall Descent"}},

    # Aqueduct B regions
    "Aqueduct B Top": {"entrances": {"Walkway B Hall of Mirrors": "Aqueduct B Top-Left Door",
                                     "Aqueduct B Main": "Aqueduct B Down from Top"}},

    "Aqueduct B Main": {"locations": [loc_names.adb4,
                                      loc_names.adb8,
                                      loc_names.adb2,
                                      loc_names.adb1],
                        "entrances": {"Aqueduct B Top": "Aqueduct B Main Left Double Jump",
                                      "Aqueduct B Bottom Shortcut Room": "Aqueduct B Crush Wall Right",
                                      "Aqueduct B Merman Lair": "Aqueduct B Main Right Double Jump"}},

    "Aqueduct B Bottom Shortcut Room": {"locations": [loc_names.adb0],
                                        "entrances": {"Luminous B Top Shortcut Room": "Aqueduct B Bottom-Left Door",
                                                      "Aqueduct B Main": "Aqueduct B Crush Wall Left"}},

    "Aqueduct B Merman Lair": {"entrances": {"Clock B Bottom Entrance Room": "Aqueduct B Top-Right Door",
                                             "Aqueduct B Main": "Aqueduct B Down from Merman Lair"}},

    # Clock Tower B regions
    "Clock B Bottom Entrance Room": {"entrances": {"Aqueduct B Merman Lair": "Clock B Bottom Door",
                                                   "Clock B Lower Area": "Clock B Double Jump from Bottom"}},

    "Clock B Lower Area": {"locations": [loc_names.crb8,
                                         loc_names.event_crank],
                           "entrances": {"Clock B Pendulum Area": "Clock B Lower Alt-button Press from Bottom"}},

    "Clock B Pendulum Area": {"locations": [loc_names.crb6b,
                                            loc_names.crb6a,
                                            loc_names.crb10],
                              "entrances": {"Walkway B Clock Exit Room": "Clock B Top Door",
                                            "Clock B Lower Area": "Clock B Lower Alt-button Press from Top",
                                            "Clock B Main": "Clock B Double Jumps from Pendulum Area"}},

    "Clock B Main": {"locations": [loc_names.crb1,
                                   loc_names.crb3,
                                   loc_names.crb2,
                                   loc_names.crb4],
                     "entrances": {"Clock B Pendulum Area": "Clock B Down from Main",
                                   "Clock B Right of Peeper": "Clock B Peeping Big's Arena Left"}},

    "Clock B Right of Peeper": {"locations": [loc_names.crb13,
                                              loc_names.event_guarder,
                                              loc_names.crb17,
                                              loc_names.crb20],
                                "entrances": {"Clock B Main": "Clock B Peeping Big's Arena Right",
                                              "Clock B Ball Race": "Clock B Slide Space",
                                              "Clock A Right of Slimer": "Clock B Warp Gate"}},

    "Clock B Ball Race": {"locations": [loc_names.crb23b,
                                        loc_names.crb23a,
                                        loc_names.crb22b,
                                        loc_names.crb22a]},

    # Castle Top Floor B regions
    "Top B Throne Room": {"locations": [loc_names.tfb3],
                          "entrances": {"Chapel B Top": "Top B Top MK Door",
                                        "Top A Throne Room": "Top B Warp Gate",
                                        "Top B Attic": "Top B Crush Blocks",
                                        "Top B Middle": "Top B Throne Alt-button Press from Top"}},

    "Top B Attic": {"locations": [loc_names.tfb0a,
                                  loc_names.tfb0b,
                                  loc_names.tfb0c,
                                  loc_names.tfb0d,
                                  loc_names.tfb0e]},

    "Top B Middle": {"locations": [loc_names.tfb5],
                     "entrances": {"Top B Throne Room": "Top B Throne Alt-button Press from Bottom",
                                   "Top B Lower": "Top B Down from Middle"}},

    "Top B Lower": {"locations": [loc_names.tfb7,
                                  loc_names.tfb11a,
                                  loc_names.tfb11b],
                    "entrances": {"Treasury B Upper": "Top B Bottom Floor Transition",
                                  "Top B Super Jump Passage": "Top B Lower Super Jump from Left"}},

    "Top B Super Jump Passage": {"entrances": {"Corridor B Main": "Top B Bottom Skull Door",
                                               "Top B Lower": "Top B Lower Super Jump from Right"}},

    # # # Misc. # # #
    "Room and Treasury Portal": {"locations": [loc_names.portals_rt],
                                 "entrances": {"Room A Past Slide Space": "Room A Portal Room Exit",
                                               "Treasury B Lower": "Treasury B Exit Side"}},

    "Luminous and Walkway Portal": {"locations": [loc_names.portals_lw],
                                    "entrances": {"Luminous B Main": "Portal Luminous Side",
                                                  "Walkway A Portal Hallway": "Portal Walkway Side"}},

    "The Empty Room": {"locations": [loc_names.event_furniture]}
}


def get_region_info(region: str, info: str) -> list[str] | dict[str, str] | None:
    return ALL_CVHODIS_REGIONS[region].get(info, None)


def get_all_region_names() -> list[str]:
    return [reg_name for reg_name in ALL_CVHODIS_REGIONS]
