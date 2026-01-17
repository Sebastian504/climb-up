# Product Requirements Document (PRD)

## Title
**Climb Up**

## Objective
The player must reach the top of the screen while avoiding being caught by opponent figures.

---

## Basic Setup

- **Genre**: 2D platform puzzle game
- **Platform**: PC
- **Framework**: Python with Pygame
- **Screen Type**: Static (non-scrolling)
- **Grid Dimensions**: 60 blocks wide × 40 blocks high
- **Block Size**: Fixed (e.g. 16x16 pixels, TBD)

---

## World Elements

Each block in the grid can be one of the following types:

1. **Air** – Empty space; player and opponents can fall through.
2. **Earth** – Solid ground; blocks movement and can be dug away by the player.
3. **Stone** – Solid, unmovable block; indestructible.
4. **Ladder** – Allows vertical movement.

---

## Game Mechanics

### Player

- **Abilities**:
  - Move **left** and **right**
  - Climb **up** if standing on a ladder or if a ladder is directly in front
  - **Fall** vertically through air blocks when not supported from below
  - **Dig** in the **opposite direction** of the last horizontal movement to remove adjacent **earth** blocks
- **Restrictions**:
  - **Cannot jump**
  - Can fall from any height **without taking damage**
- **Win Condition**:
  - Reach any block in the **top row** of the screen
- **Lose Condition**:
  - Be caught by an opponent

### Digging Mechanic

- **Direction**: Always in the **opposite** direction of the last horizontal movement (left or right)
- **Valid Targets**: Only **earth** blocks directly adjacent in that direction
- **Effect**: Turns an earth block into air, potentially creating new paths
- **Input**: Pressing the `SPACE` key triggers a dig

### Opponents

- **Quantity**: At least two active opponents per game
- **Behavior**:
  - **Automatically controlled**
  - Move **toward the player** using the same movement rules (left, right, up if on a ladder, down if unsupported)
  - If **no move reduces distance** to the player, they **remain still**
- **Limitations**:
  - **Cannot dig**

---

## Controls

- **Arrow Keys** (or WASD):
  - Left/Right: Move horizontally
  - Up: Climb ladder
- **Dig**:
  - `SPACE`: Dig in the direction opposite the last horizontal movement

---

## Technical Specifications

- **Language**: Python
- **Framework**: Pygame
- **Game Loop**:
  - Runs at 60 FPS
  - Handles input, updates movement logic, resolves collisions, and redraws screen
- **Asset Storage**:
  - Grayscale sprite sheet or block-based texture mapping
- **AI**:
  - Simple heuristic pathfinding (e.g., greedy move toward player)

---

## Graphics & Audio

- **Visual Style**:
  - 2D Side-view perspective
  - **Grayscale only**
  - Low-resolution pixel art
- **Animation**:
  - Minimalist (idle, move, climb, dig)
- **Audio**:
  - None initially (optional future feature)

---

## Future Considerations (Optional/Stretch Goals)

- Level editor
- Procedural level generation
- Power-ups or tools (e.g., place ladders, temporary blocks)
- Score or time tracking

---

## MVP Scope

- Static map loaded from a file or hardcoded
- Basic player controls and movement (including dig mechanic)
- Basic AI opponent movement
- Win/Lose conditions
- Minimalist grayscale graphics
