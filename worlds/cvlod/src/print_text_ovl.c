// Written by Moisés
#include "textbox.h"
#include "save.h"

#define GAMEPLAYMGR_ID         0x0007
#define NUMBER_OF_DIGITS       2
#define NUMBER_OF_RANDO_STAGES 19

f32 X_pos = 1.0f;
f32 Y_pos = 2.0f;
extern u8 number[NUMBER_OF_RANDO_STAGES];      // 0x801CABA0

// 1. Call this function first
textboxModule* printNumber_createTextbox() {
    return createTextboxModule(moduleList_findFirstModuleByID(GAMEPLAYMGR_ID));
}

// 2. Afterwards, call this function every frame until it returns 1 (TRUE)
// A0 = textbox module pointer
u32 printNumber_isTextboxDataCreated(textboxModule* self) {
    return self->data != NULL;
}

// 3. Call this function once
// A0 = textbox module pointer
// A1 = Rando stage ID
void printNumber_init(textboxModule* self, u32 stage_ID) {
    textboxModule_setParams_number(self, number[stage_ID], 0, X_pos, Y_pos, NUMBER_OF_DIGITS, TEXT_FONT_GOLD_COUNTER);
}

// Once the functions above are called,
// you can now call the following functions once, whenever needed

// A0 = textbox module pointer
// A1 = Rando stage ID
void printNumber_updateNumber(textboxModule* self, u32 stage_ID) {
    textboxModule_setNumber(self, number[stage_ID]);
}

// A0 = textbox module pointer
void printNumber_setPosition(textboxModule* self) {
    textboxModule_setPos(self, X_pos, Y_pos);
}

// A0 = textbox module pointer
// A1 = Color
void printNumber_setColor(textboxModule* self, u32 color_palette) {
    textboxModule_setColorPalette(self, color_palette);
}
