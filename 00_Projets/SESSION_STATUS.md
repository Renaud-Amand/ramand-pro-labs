# 🧭 SESSION STATUS & PROGRESS TRACKER: Dys-Pédagogie (Mobile App Kivy)

> **Last Update:** 2026-02-23 23:23
> **Global State:** ✅ Phase 2 Complete — Circular-import crash and session-token blocker both resolved. App launches and authenticates end-to-end. Phase 3 (Core Pedagogy) is next.

## [DONE] - COMPLETED TASKS

### 1. Environment & Config

- Python `.venv` active at project root.
- Kivy installed and verified.
- Supabase connection validated via `execution/test_supabase_conn.py`.
- `.gitignore` configured (`.venv`, `.env`, `__pycache__` excluded).

### 2. UI Architecture & Accessibility (DYS-Ready)

- `DysScreen`: Base class implemented for global accessibility inheritance.
- `DysButton` & `DysTextInput`: Reusable KV components (min 56dp height, high contrast).
- OpenDyslexic font registered with `os.path.exists()` fallback.
- **Rule Enforced:** Absolute paths only via `BASE_DIR = os.path.dirname(os.path.abspath(__file__))`.

### 3. Navigation Flow (Functional)

- `SplashScreen` (3s auto-transition) ──▶ `LoginScreen` (prenom check) ──▶ `DashboardScreen` (dynamic greeting + stats).

### 4. Phase 2 — Supabase Integration (Complete)

- `database/supabase_client.py`: `SupabaseManager` singleton. Offline-First, Zero-Trust (ANON_KEY only), graceful `.env`-missing fallback.
- `main.py`: `check_login(prenom)` queries `users` table; `load_user_data(prenom, app)` fetches `progress` table. Both Offline-First.
- `screens/login_screen.py`: `submit_login()` calls `check_login()` in daemon thread; result dispatched via `Clock.schedule_once`; success stores `user_prenom` on `DysApp` and navigates to `dashboard`.
- `screens/dashboard_screen.py`: `on_enter()` calls `load_user_data()` in daemon thread; callback updates `welcome_message`, `score_label`, `sessions_label` StringProperties. Logout clears app state.

### 5. Bug Fixes (2026-02-23)

- **Circular Import (`ImportError`):** Moved `from main import check_login` and `from main import load_user_data` from module-level to local scope inside their respective daemon-thread workers. App no longer crashes on startup.
- **Session Token Blocker ("Session expirée"):** `login_screen.py` now calls `auth_manager.login_user(email, password)` (Supabase Auth) instead of the prenom-only `check_login`. Real JWT written to `session.json` and `app.session_data`, unblocking `create_child_profile` and `verify_child_pin_db`.

---

## [CURRENT] - ACTIVE PHASE (PHASE 3: CORE PEDAGOGY)

**Priority:** High. Build the first learning module and connect it to Supabase progress tracking.

- [x] **Task 1:** Patch `dashboard.kv` — add `score_label` / `sessions_label` display widgets (companion to Phase 2 Python changes).
- [x] **Task 2 (Bug):** Fix circular `ImportError` — deferred `from main import` calls to local scope in daemon-thread workers.
- [x] **Task 3 (Bug):** Fix "Session expirée" blocker — `login_screen.py` now performs full Supabase Auth (email + password → JWT) and populates `app.session_data`.
- [ ] **Task 4:** Execute `database/schema.sql` on Supabase to create `users` and `progress` tables (if not already done).
- [ ] **Task 5:** Create `screens/exercice_screen.py` — `ExerciceScreen(DysScreen)` template with difficulty routing.
- [ ] **Task 6:** Implement first module: Syllable / Letter reading logic.
- [ ] **Task 7:** On exercise completion, call `load_user_data()` to refresh progress stats on `DashboardScreen`.

---

## [NEXT] - UPCOMING PHASES

### Phase 4: UI Polish & Accessibility

- [ ] Replace placeholder emoji (🌟) with actual image asset in `assets/images/`.
- [ ] Create child Profile management screen.
- [ ] Full DYS accessibility audit (contrast ratios, tap-target sizes, font scaling).

### Phase 5: Build & Distribution

- [ ] Configure `buildozer.spec` for Android target.
- [ ] Build and sign APK via Buildozer.
- [ ] Smoke-test on physical Android device.

---

## 🛑 STRICT DIRECTIVES FOR AI AGENTS (READ BEFORE CODING)

1. **Separation of Concerns:** DO NOT modify `02_mobile_app_kivy/dys_style.kv` to implement backend logic. All Supabase logic belongs in Python files.
2. **Hook Points:** Look for `# SUPABASE HOOK` comments in `main.py`. These are the designated injection points.
3. **Pathing:** NEVER use relative paths. Always construct from `BASE_DIR`.
4. **Inheritance:** Any new screen MUST inherit from `DysScreen`.
5. **Zero-Trust Rule:** Never hardcode secrets. Always use `os.getenv()` for Supabase credentials.

---

## 🚀 QUICK LAUNCH COMMANDS (Windows PowerShell)

**Activate Env:**

```powershell
& c:/Users/Dev_Renaud/Documents/00_Dev/00_Projets/.venv/Scripts/Activate.ps1
```
