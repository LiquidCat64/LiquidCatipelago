// Written by Moisés originally, further modified by Liquid Cat
#include "textbox.h"
#include "save.h"
#include "cvlod.h"
#include "object.h"
#include "memory.h"

#define GAMEPLAYMGR_ID         0x0007
#define NUMBER_OF_DIGITS       2

extern textboxObject* COUNTDOWN_TEXTBOX;
extern GameplayMenuMgr* gameplay_menu_mgr;

f32 default_x_pos = -108.5;
f32 default_y_pos = 88.5;
u16 flags[2] = {0, 0};
u16* countdown_flags[50] = {flags, flags, flags, flags, flags, flags, flags, flags, flags, flags,
			    flags, flags, flags, flags, flags, flags, flags, flags, flags, flags,
			    flags, flags, flags, flags, flags, flags, flags, flags, flags, flags,
			    flags, flags, flags, flags, flags, flags, flags, flags, flags, flags,
			    flags, flags, flags, flags, flags, flags, flags, flags, flags, flags};

// Creates the countdown textbox. Should only be called during the map loading process.
void countdown_createTextboxAndLoadMapOverlays(ObjectHeader* mapSetup) {
    COUNTDOWN_TEXTBOX = createTextboxObject(objectList_findFirstObjectByID(GAMEPLAYMGR_ID));
    (*mapSetup_loadMapRelatedOverlays)(mapSetup);
}

// Updates the countdown textbox. Should be called once per frame. Whether the textbox is created or not shouldn't matter.
void countdown_updateNumber() {
    u32 set_flags = 0;
    u32 total_flags = 0;

    loadFilesFromFileLoadArray();
    // If the number textbox object is not created, or if it is but its textboxData struct is not created, return.
    if (COUNTDOWN_TEXTBOX == NULL) {
        return;
    }
    if (COUNTDOWN_TEXTBOX->data == NULL) {
        return;
    }
    
    // Tally up the total number of countdown flags for the current map and which ones are currently set.
    // A flag value of 0 in the array means we've reached the end of it.
    while (countdown_flags[SaveStruct_gameplay.map_ID][total_flags]) {
        if ((*checkBitflag)(SaveStruct_gameplay.event_flags, countdown_flags[SaveStruct_gameplay.map_ID][total_flags])) {
            set_flags++;
        }
        total_flags++;
    }

    // Initialize the number textbox if it's not currently (no pointer to the custom-formatted text string) and return.
    if (COUNTDOWN_TEXTBOX->text_custom_format == NULL) {
        textboxObject_setParams_number(COUNTDOWN_TEXTBOX, (total_flags - set_flags), 0, default_x_pos, default_y_pos, NUMBER_OF_DIGITS, TEXT_FONT_GOLD_COUNTER);
        return;
    }

    // Update the number to be the number of unset flags.
    textboxObject_setNumber(COUNTDOWN_TEXTBOX, (total_flags - set_flags));

    // Set the color of the number depending on how many flags are set.
    // If all flags are set, the number will be dark brown.
    if (set_flags == total_flags) {
        textboxObject_setColorPalette(COUNTDOWN_TEXTBOX, TEXT_COLOR_DARK_BROWN);
    }
    // If no flags are set, the number will be green.
    else if (!set_flags) {
        textboxObject_setColorPalette(COUNTDOWN_TEXTBOX, TEXT_COLOR_GREEN);
    }
    // Otherwise, it'll be mid-brown.
    else {
        textboxObject_setColorPalette(COUNTDOWN_TEXTBOX, TEXT_COLOR_MID_BROWN);
    }
    
    // Determine where on-screen the number should be depending on the HUD's screen configuration.
    // First tho, check if the gameplay menu manager and the HUD info it points to exists. If both don't, return.
    if (gameplay_menu_mgr == NULL) {
        return;
    }
    if (gameplay_menu_mgr->hud_state_info == NULL) {
        return;
    }
    // If the HUD is not visible, hide the number offscreen.
    if (gameplay_menu_mgr->hud_state_info->screen_arrangement_flags & HUD_ARRANGEMENT_INVISIBLE) {
        textboxObject_setPos(COUNTDOWN_TEXTBOX, default_x_pos, 354.0);
    }
    // If the HUD is in its pause menu configuration, place the number in the top-right corner, where perpendicular "lines" going right from the status and top from the jewel count would intersect.
    else if (gameplay_menu_mgr->hud_state_info->screen_arrangement_flags & HUD_ARRANGEMENT_PAUSE) {
        textboxObject_setPos(COUNTDOWN_TEXTBOX, 112.5, 102.0);
    }
    // Otherwise, place it below the left side of the health bar.
    else {
        textboxObject_setPos(COUNTDOWN_TEXTBOX, default_x_pos, default_y_pos);
    }
    return;
}
