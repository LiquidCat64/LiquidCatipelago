#include "memory.h"
#include "fade.h"
#include "controller.h"
#include "gamestate.h"
#include "save.h"
#include "cvlod.h"
#include "extendedStageSelect.h"

/*
 * Extended Stage Select mod for Castlevania: Legacy of Darkness, originally written by moisesPC and then modified with permission by Liquid Cat to fit the randomizer's needs.
 * Original repo at: https://github.com/moisesPC/cvlod_extendedStageSelect
 * 
 * - The overlay file replaces the unused debug font assets file in the vanilla ROM
 * - The overlay is mapped to 0x0F000000 by the TLB, since we're gonna allocate it dynamically
 * - Handled by object 0x20FD (0x00FD in the vanila ROM) and gamestate 2 (unused in the final game)
 */


// Entrypoint function. Executed every frame as long as the object is active
// Used to branch to the other functions
void extendedStageSelect_entrypoint(extendedStageSelect* self) {
    ENTER(self, extendedStageSelect_functions);
}

// The textboxes must be created in a separate function to ensure that
// the textboxData field associated to each textbox is created.
// Otherwise textboxObject_setParams_ASCIIFormattedString() will fail
// because it checks whether the textboxData isn't NULL before proceeding
void extendedStageSelect_createTextboxes(extendedStageSelect* self) {
    u32 i = 0;

    // Headers
    self->headerNamesTextboxes = (*heap_alloc)(HEAP_KIND_MULTIPURPOSE, sizeof(textboxObject* [NUMBER_OF_HEADERS]));
    for (i = 0; i < NUMBER_OF_HEADERS; i++) {
        self->headerNamesTextboxes[i] = (*createTextboxObject)(self);
    }
    // Map names
    self->mapNamesTextboxes = (*heap_alloc)(HEAP_KIND_MULTIPURPOSE, sizeof(textboxObject* [OPTION_MAX]));
    for (i = 0; i < OPTION_MAX; i++) {
        self->mapNamesTextboxes[i] = (*createTextboxObject)(self);
    }
    // Convenience warp names
    self->convenienceWarpTextboxes = (*heap_alloc)(HEAP_KIND_MULTIPURPOSE, sizeof(textboxObject* [NUMBER_OF_CONVENIENCE_WARPS]));
    for (i = 0; i < NUMBER_OF_CONVENIENCE_WARPS; i++) {
        self->convenienceWarpTextboxes[i] = (*createTextboxObject)(self);
    }
    // Character names
    self->characterNamesTextbox = (*createTextboxObject)(self);
    // Yes / No
    self->YesNoTextbox = (*createTextboxObject)(self);
    // Difficulty
    self->DifficultyTextbox = (*createTextboxObject)(self);
    // Special1 count
    self->SpecialCountTextbox = (*createTextboxObject)(self);
    // Selection arrow
    self->ArrowTextbox = (*createTextboxObject)(self);

    // Go to extendedStageSelect_init()
    (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
}

void extendedStageSelect_init(extendedStageSelect* self) {
    u32 i, j;

    // Get selection variable values from common memory.
    // The map number and specials per warp will always be referred to from the object to make it easier for the rando to dynamically patch these.
    self->num_maps = NUM_MAPS;
    self->specials_per_warp = SPECIALS_PER_WARP;
    self->option = MOD_SELECTED_OPTION;
    self->map = MOD_SELECTED_MAP;
    self->character = SaveStruct_gameplay.character;
    self->alternate_costume = SaveStruct_gameplay.alternate_costume;
    self->first_string_ID = MOD_SELECTED_FIRST_STRING_ID;
    self->confirmed = 0;
    self->convenience_warp = 0;

    // Set the difficulty index depending on which difficulty flag is set in the save file.
    if (SaveStruct_gameplay.flags & EASY) {
        self->difficulty = 0;
    }
    else if (SaveStruct_gameplay.flags & NORMAL) {
        self->difficulty = 1;
    }
    else {
        self->difficulty = 2;
    }


    // Prevent cutscene borders from being active if warping to this menu while a cutscene was active
    if (expansion_pak_enabled) {
        screen_letterbox_pos_left = 24;
        screen_letterbox_pos_up = 16;
        screen_letterbox_pos_right = 472;
        screen_letterbox_pos_down = 352;
    }
    else {
        screen_letterbox_pos_left = 12;
        screen_letterbox_pos_up = 8;
        screen_letterbox_pos_right = 308;
        screen_letterbox_pos_down = 232;
    }

    /////////////// Headers ///////////////
    // Where to...?
    (*textboxObject_setParams_CustomFormattedString)(self->headerNamesTextboxes[0], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(header_names_pool, 0)), 1, -100.0f, 107.f, 16, 0);
    // Difficulty:
    (*textboxObject_setParams_CustomFormattedString)(self->headerNamesTextboxes[1], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(header_names_pool, 1)), 1, -140.0f, -70.f, 16, 1);
    (*textboxObject_setTextScale)(self->headerNamesTextboxes[1], 0.8f, 1.0f);
    // Character:
    (*textboxObject_setParams_CustomFormattedString)(self->headerNamesTextboxes[2], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(header_names_pool, 2)), 1, -100.0f, -90.f, 16, 1);
    (*textboxObject_setTextScale)(self->headerNamesTextboxes[2], 0.8f, 1.0f);
    // Alt. Costume:
    (*textboxObject_setParams_CustomFormattedString)(self->headerNamesTextboxes[3], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(header_names_pool, 3)), 1, 10.0f, -70.f, 16, 1);
    (*textboxObject_setTextScale)(self->headerNamesTextboxes[3], 0.8f, 1.0f);
    // Specials x
    (*textboxObject_setParams_CustomFormattedString)(self->headerNamesTextboxes[4], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(header_names_pool, 4)), 1, 90.0f, 107.f, 16, 1);
    (*textboxObject_setTextScale)(self->headerNamesTextboxes[4], 1.5f, 1.5f);

    for (i = 0; i < NUMBER_OF_HEADERS-1; i++) {
        (*textboxObject_setColorPalette)(self->headerNamesTextboxes[i], TEXT_COLOR_YELLOW);
    }

    /////////////// Map Names ///////////////
    for (i = 0, j = self->first_string_ID + i; i < OPTION_MAX; i++, j++) {
        // Y pos varies by 20.0f, starting from 90.0f
        (*textboxObject_setParams_CustomFormattedString)(self->mapNamesTextboxes[i], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(stage_names_pool, j)), 0, -130.0f, 90.f - (20.0f * i), 16, 1);
    }
    // Set the color of the first option to red
    (*textboxObject_setColorPalette)(self->mapNamesTextboxes[self->option], TEXT_COLOR_RED);

    /////////////// Character names ///////////////
    (*textboxObject_setParams_ASCIIFormattedString)(self->characterNamesTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, characterNames[self->character]), 0, 10.0f, -90.f, 16, 1);

    /////////////// Yes / No (Alternate costume) ///////////////
    (*textboxObject_setParams_ASCIIFormattedString)(self->YesNoTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, YesNoSelection[self->alternate_costume]), 0, 115.0f, -70.f, 16, 1);

    /////////////// Difficulty ///////////////
    (*textboxObject_setParams_ASCIIFormattedString)(self->DifficultyTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, DifficultySelection[self->difficulty]), 0, -55.0f, -70.f, 16, 1);

    /////////////// Special count ///////////////
    (*textboxObject_setParams_number)(self->SpecialCountTextbox, SaveStruct_gameplay.inventory_item_amount[3], 1, 115.0f, 107.0f, 2, TEXT_FONT_DEFAULT);
    (*textboxObject_setTextScale)(self->SpecialCountTextbox, 1.5f, 1.5f);

    /////////////// Convenience warps ///////////////
    for (i = 0; i < NUMBER_OF_CONVENIENCE_WARPS; i++) {
	// Skip if convenience warp flag(s) are not set.
        if ((*checkBitflag)(SaveStruct_gameplay.event_flags, convenience_warp_flags[i])) {
            // Y pos varies by 50.0f, starting from 75.0f
            (*textboxObject_setParams_CustomFormattedString)(self->convenienceWarpTextboxes[i], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(convenience_warp_names_pool, i)), 1, 85.0f, 75.f - (50.0f * i), 16, 3);
            (*textboxObject_setTextScale)(self->convenienceWarpTextboxes[i], 0.8f, 1.0f);
            (*textboxObject_setColorPalette)(self->convenienceWarpTextboxes[i], TEXT_COLOR_YELLOW);
        }
	
    }
    (*textboxObject_setParams_number)(self->SpecialCountTextbox, SaveStruct_gameplay.inventory_item_amount[3], 1, 115.0f, 107.0f, 2, TEXT_FONT_DEFAULT);

    /////////////// Selection arrow textbox ///////////////
    // The arrow will start next to whichever option is selected by default.
    (*textboxObject_setParams_CustomFormattedString)(self->ArrowTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, arrow_textbox_pool), 0, -140.0f, 91.f - (20.0f * self->option), 16, 1);
    (*textboxObject_setColorPalette)(self->ArrowTextbox, TEXT_COLOR_RED);


    // Set background color to dark red.
    background_color.color_u32 = 0x300000FF;
    // Cancel any previous fades
    (*fade_setSettings)(FADE_IN, 1, 0, 0, 0);

    // Silence any ambience noises that might be playing.
    // Foggy Lake ship noises.
    if ((*isSoundPlaying)(0x1A0)) {
        (*playSound)(0x81A0);
    }
    if ((*isSoundPlaying)(0x1A1)) {
        (*playSound)(0x81A1);
    }
    // Common wind ambience
    if ((*isSoundPlaying)(0x136)) {
        (*playSound)(0x8136);
    }
    // Henry escort song additional strings
    if ((*isSoundPlaying)(0x371)) {
        (*playSound)(0x8371);
    }
    if ((*isSoundPlaying)(0x372)) {
        (*playSound)(0x8372);
    }
    // Gardener's proximity chainsaw
    if ((*isSoundPlaying)(0x358)) {
        (*playSound)(0x8358);
    }
    // Outer Wall wind ambience
    if ((*isSoundPlaying)(0x1BF)) {
        (*playSound)(0x81BF);
    }
    if ((*isSoundPlaying)(0x172)) {
        (*playSound)(0x8172);
    }
    // Fan Meeting Room fans
    if ((*isSoundPlaying)(0x1ED)) {
        (*playSound)(0x81ED);
    }
    // Tower of Execution lava
    if ((*isSoundPlaying)(0x1BB)) {
        (*playSound)(0x81BB);
    }
    if ((*isSoundPlaying)(0x369)) {
        (*playSound)(0x8369);
    }
    // Tower of Science machinery humming
    if ((*isSoundPlaying)(0x368)) {
        (*playSound)(0x8368);
    }
    // Tower of Science/Clock Tower gears
    if ((*isSoundPlaying)(0x188)) {
        (*playSound)(0x8188);
    }
    // Go to extendedStageSelect_loop()
    (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
}

void extendedStageSelect_loop(extendedStageSelect* self) {
    u32 i = 0;

    // Map selection
    // Disallow pressing down if we don't have enough Special1s to select the option below our current one, or if pressing down would increase the map number beyond what was defined for the limit.
    if (((controllers[0].buttons_pressed & BTN_DDOWN || (*selection_moveCursor)(BTN_DDOWN)) && SaveStruct_gameplay.inventory_item_amount[3] / ((self->map + 1) * self->specials_per_warp)) && self->map + 1 < self->num_maps) {
        // If the cursor is at the bottom of the list, scroll down
        if (self->option == (OPTION_MAX - 1) && self->map < self->num_maps - 1) {
            self->option = (OPTION_MAX - 1);
            self->first_string_ID++;
            // Go through the list of options and update the strings with the next one immediatly below it,
            // simulating the user scrolling down by one in the list
            for (i = 0; i < OPTION_MAX; i++) {
                if (self->first_string_ID >= self->num_maps) {
                    self->first_string_ID = self->num_maps - 1;
                }
                (*textboxObject_setCustomFormattedText)(self->mapNamesTextboxes[i], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(stage_names_pool, self->first_string_ID + i)));
            }
        }
        else if (self->option < (OPTION_MAX - 1)) {
            self->option++;
            // Set current option to red, and previous option to white
            (*textboxObject_setColorPalette)(self->mapNamesTextboxes[self->option], TEXT_COLOR_RED);
            (*textboxObject_setColorPalette)(self->mapNamesTextboxes[self->option - 1], TEXT_COLOR_WHITE);
            // Update the position of the selection arrow.
            (*textboxObject_setPos)(self->ArrowTextbox, -140.0f, 91.f - (20.0f * self->option));
        }
        self->map++;
    }
    if (controllers[0].buttons_pressed & BTN_DUP || (*selection_moveCursor)(BTN_DUP)) {
        // If the cursor is at the top of the list, scroll up
        if (self->option == 0 && self->map > 0) {
            self->option = 0;
            self->first_string_ID--;
            // Go through the list of options and update the strings with the next one immediatly before it,
            // simulating the user scrolling up by one in the list
            for (i = 0; i < OPTION_MAX; i++) {
                if (self->first_string_ID < 0) {
                    self->first_string_ID = 0;
                }
                (*textboxObject_setCustomFormattedText)(self->mapNamesTextboxes[i], GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, (*text_getMessageFromPool)(stage_names_pool, self->first_string_ID + i)));
            }
        }
        else if (self->option > 0) {
            self->option--;
            // Set current option to red, and option below to white
            (*textboxObject_setColorPalette)(self->mapNamesTextboxes[self->option], TEXT_COLOR_RED);
            (*textboxObject_setColorPalette)(self->mapNamesTextboxes[self->option + 1], TEXT_COLOR_WHITE);
            // Update the position of the selection arrow.
            (*textboxObject_setPos)(self->ArrowTextbox, -140.0f, 91.f - (20.0f * self->option));
        }
        self->map--;
    }

    // Stop moving if reaching either the bottom or top of the whole list
    if (self->map >= self->num_maps) {
        self->map = self->num_maps - 1;
    }
    else if (self->map < 0) {
        self->map = 0;
    }

    // Character selection
    if (controllers[0].buttons_pressed & BTN_Z) {
        if (self->character == HENRY) {
            self->character = REINHARDT;
        }
        else {
            self->character++;
        }
        // Update the character name string to show the selected character name
        (*textboxObject_setASCIIText)(self->characterNamesTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, characterNames[self->character]));
	// Play a voice clip associated with the new character
        (*playSound)(character_sound_ids[self->character]); 
    }

    // Alternate costume selection
    if (controllers[0].buttons_pressed & BTN_R) {
        if (self->alternate_costume == TRUE) {
            self->alternate_costume = FALSE;
        }
        else {
            self->alternate_costume = TRUE;
        }
        (*textboxObject_setASCIIText)(self->YesNoTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, YesNoSelection[self->alternate_costume]));
    }

    // Difficulty selection
    if (controllers[0].buttons_pressed & BTN_L) {
        if (self->difficulty == 2) {  // HARD
            self->difficulty = 0;  // EASY
        }
        else {
            self->difficulty++;
        }
        // Update the difficulty name string to show the selected difficulty name
        (*textboxObject_setASCIIText)(self->DifficultyTextbox, GET_UNMAPPED_ADDRESS(EXTENDED_STAGE_SELECT_OVERLAY_ID, DifficultySelection[self->difficulty]));
    }

    // Go to extendedStageSelect_warpToMap() when selecting an option with A
    if (controllers[0].buttons_pressed & BTN_A) {
        self->confirmed = 1;
        (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
    }

    // Go to extendedStageSelect_warpToMap() while skipping some functionality when backing out wiht B
    if (controllers[0].buttons_pressed & BTN_B) {
        (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
    }

    // Go to extendedStageSelect_warpToMap() if pressing C-Left, Right, or Up when its respective convenience warp flag is set.
    if (controllers[0].buttons_pressed & BTN_CLEFT && (*checkBitflag)(SaveStruct_gameplay.event_flags, convenience_warp_flags[0])) {
        self->convenience_warp = 1;
        (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
    }

    if (controllers[0].buttons_pressed & BTN_CRIGHT && (*checkBitflag)(SaveStruct_gameplay.event_flags, convenience_warp_flags[1])) {
        self->convenience_warp = 2;
        (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
    }

    if (controllers[0].buttons_pressed & BTN_CUP && (*checkBitflag)(SaveStruct_gameplay.event_flags, convenience_warp_flags[2])) {
        self->convenience_warp = 3;
        (*object_curLevel_goToNextFuncAndClearTimer)(self->header.current_function, &self->header.functionInfo_ID);
    }
}

void extendedStageSelect_warpToMap(extendedStageSelect* self) {
    // If player is dead, revive them, and force their health to be 1.
    // This prevents a crash that happens if the player warps while they're marked as dead
    if ((SaveStruct_gameplay.health <= 0) || (SaveStruct_gameplay.player_status & DEAD)) {
        SaveStruct_gameplay.health = 1;
        SaveStruct_gameplay.player_status &= ~DEAD;
    }

    // If the player presssed A, warp to the map they were hovering on.
    if (self->confirmed) {
        // Save default selection variables.
        MOD_SELECTED_MAP = self->map;
        MOD_SELECTED_OPTION = self->option;
        MOD_SELECTED_FIRST_STRING_ID = self->first_string_ID;
        map_ID = destMapIDs[self->map];
        map_entrance_ID = destSpawnIDs[self->map];
        (*playSound)(411); 				// Play the "teleport" sound.
    }
    //  If using a convenience warp, warp to that destination.
    else if (self->convenience_warp) {
	// Reset the default selection variables.
        MOD_SELECTED_MAP = 0;
        MOD_SELECTED_OPTION = 0;
        MOD_SELECTED_FIRST_STRING_ID = 0;
        map_ID = convenience_warp_maps[self->convenience_warp-1];
        map_entrance_ID = convenience_warp_spawns[self->convenience_warp-1];
        (*playSound)(411); 				// Play the "teleport" sound.
    }
    //  Otherwise, we will merely return to the map we entered the menu from.

    // Set the new difficulty.
    SaveStruct_gameplay.flags &= ~(EASY | NORMAL | HARD);
    if (self->difficulty == 0) {
        SaveStruct_gameplay.flags |= EASY;
    }
    else if (self->difficulty == 1) {
        SaveStruct_gameplay.flags |= NORMAL;
    }
    else {
        SaveStruct_gameplay.flags |= HARD;
    }

    SaveStruct_gameplay.character = self->character;
    SaveStruct_gameplay.alternate_costume = self->alternate_costume;
    current_opened_menu = NOT_ON_MENU;          // Prevent any menu to open all of the sudden after warping
    (*changeGameState)(GAMEPLAY);               // Restart the gameplay state with the selected options
}
