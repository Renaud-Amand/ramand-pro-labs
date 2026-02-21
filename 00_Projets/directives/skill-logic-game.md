# SKILL: GAME LOGIC & STATE MANAGEMENT

## Granular Architecture

- **Micro-Functions:** Every game action (scoring, leveling, validation) must be its own independent function.
- **Atomic State:** Track the game state through small, observable variables rather than one massive object.
- **Zero-UI Dependency:** Game logic scripts must be able to run in a terminal without any Kivy or UI components attached.

## Debug & Monitoring

- **State Hooks:** Each state change (e.g., START -> PLAYING) must be logged or trigger a specific event.
- **Unit Testing Ready:** Functions must be "pure" (Input -> Transformation -> Output) to allow surgical debugging of specific bugs.

## Evolution & Scalability

- **Decoupled Features:** New game mechanics must be added as new modules, not by modifying existing core logic.
