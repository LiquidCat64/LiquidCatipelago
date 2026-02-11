// Written by Moises
#include "object.h"
#include "math.h"
#include "cvlod.h"

extern u32 cutscene_mgr;
extern vec3s player_angle;      // player_angle.y = Player's facing angle (yaw)
extern f32 player_nearest_floor_height;
extern u8 player_nearest_floor_type;
extern Interactable* player_actor;


#define SHT_MAX 32767.0f
#define SHT_MINV (1.0f / SHT_MAX)
#define ACTOR_CREATOR 430
#define ACTOR_ITEM 39

void spawn_item_behind_player(s32 item, u8 weapon_level) {
    Interactable* pickable_item = NULL;
    InteractableExtraInfo* pickable_extra_info = NULL;
    const f32 spawnDistance = 8.0f;
    vec3f player_backwards_dir;

    pickable_item = (Interactable*)object_createAndSetChild(cutscene_mgr, ACTOR_ITEM);
    if (pickable_item != NULL) {
        // Allocate the extra data for the pickup.
        pickable_extra_info = (*object_allocEntryInListAndClear)(pickable_item, 0, 0x20, 0xF);
        // If we were not able to allocate the data, delete the pickup and exit.
        if (pickable_extra_info == NULL) {
            pickable_item->header.destroy(pickable_item);
        }
        else {
            // Convert facing angle to a vec3f
            // SHT_MINV needs to be negative here for the item to be spawned properly on the character's back
            player_backwards_dir.x = coss(-player_actor->model->model_angle.yaw) * -SHT_MINV;
            player_backwards_dir.z = sins(-player_actor->model->model_angle.yaw) * -SHT_MINV;
            // Multiply facing vector with distance away from the player
            vec3f_multiplyScalar(&player_backwards_dir, &player_backwards_dir, spawnDistance);
            // Assign the position of the item relative to the player's current position.
            vec3f_add(&pickable_extra_info->start_position, &player_actor->model->position, &player_backwards_dir);
            // The starting Y position of the item will be the player's current height plus 5.
            pickable_extra_info->start_position.y = player_actor->model->position.y + 5.0f;
            // If the player has a floor beneath them (see: the nearest floor type is not 0), set the height to drop down to to that floor's height.
            // Otherwise, set it down to some arbitrairly large negative number.
            if (player_nearest_floor_type) {
                pickable_item->item_falling_target_height = player_nearest_floor_height;
            }
            else {
                pickable_item->item_falling_target_height = -1000000.0f;
            }
            // Assign item ID and other info.
            pickable_item->field_0x52 |= weapon_level;
            pickable_extra_info->idx = item;
            pickable_extra_info->interactable_type = 0x8000;  // Item pickup
            pickable_extra_info->pickup_flags = 0x4001;  // Affected by gravity and expires.
        }
    }
}
