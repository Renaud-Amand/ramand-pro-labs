# SKILL: GAME LOGIC & STATE MANAGEMENT

## 🧩 Granular Architecture

- **Micro-Functions:** Every game action (scoring, leveling, validation) must be an independent, single-purpose function.
- **Atomic State:** Track game states through small, observable variables rather than monolithic objects.
- **Zero-UI Dependency:** Game logic MUST run in a terminal/headless mode without Kivy or any UI components.

## 🔍 Debug & Monitoring

- **State Hooks:** Every transition (e.g., `START -> PLAYING`) must be logged or trigger a specific event.
- **Pure Functions:** Maintain (Input -> Transformation -> Output) purity for surgical unit testing.

## 🎯 MISSION: DYS PEDAGOGY EXPERT

Transform clinical methods into valid exercises for dyslexic children (syllabic decomposition, phonology, visual memory).

## 🛡️ GOLDEN RULES

1. **Scaffolding:** Always move from simple to complex (The Scaffolding Principle).
2. **Positive Feedback:** Provide immediate positive reinforcement; never use frustrating penalties.
3. **Targeted Logic:** Ensure each exercise targets a specific deficit (e.g., b/d confusion).

## 🚨 CRITICAL RULE: FAILURE PROTOCOL

Upon identifying a lack of pedagogical clarity or a logical inconsistency: **HALT PRODUCTION.** Analyze the root cause, document it in the "LEARNING LOG" below, and refine the method before resuming.

## 🧠 LEARNING LOG (REtex)

### ❌ Past Failures & Solutions:

- (To be populated by Agent)
