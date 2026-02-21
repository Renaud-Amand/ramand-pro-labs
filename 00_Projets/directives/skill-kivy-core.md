# SKILL: KIVY CORE ARCHITECTURE

## Framework Specifics

- Version: Kivy 2.3.0+
- Pattern: Mandatory use of the **Observer Pattern** (via Kivy Properties & Bindings).
- Separation: UI logic in `.kv` files (Layer 1/3) vs Business Logic in Python (Layer 2/3).

## UI/UX Rules

- Responsive: Use `dp()` and `sp()` for all dimensions/fonts.
- Navigation: Use `ScreenManager` for transitions.
- Feedback: Every action must have a visual or haptic feedback.
