# SKILL: SUPABASE & DATA INTEGRATION

## 🔐 Security & Env

- **Zero Hardcoding:** Never write API keys in code. Use `get_env()` tool to fetch from `.env`.
- **Role Awareness:** Always specify if a script uses `anon_key` (client-side) or `service_role` (admin/backend only).

## 📊 Data Layer (Layer 3)

- **Isolation:** Database logic must live ONLY in `execution/db_scripts/`.
- **Atomic Operations:** One script = one task (ex: `upsert_user_score.py`, `get_level_data.py`).
- **Return Format:** Scripts must return a clear JSON: `{"success": bool, "data": obj, "error": str}`.

## 📡 Offline & Performance

- **Offline First:** Before any write, check connectivity. If offline, cache the action in a local `.tmp/pending_sync.json`.
- **Error Logging:** Every Supabase error must be caught and logged in `logs/db_errors.log` with: Timestamp, Script Name, Error Code, and Context.

### 📝 AGENT LEARNINGS & WINDOWS OPTIMIZATION

- **Encoding:** On Windows environments, always force UTF-8 to prevent UnicodeEncodeError by adding `sys.stdout.reconfigure(encoding='utf-8')` at the start of scripts.
- **Error Codes:** Note that Supabase returns `PGRST205` when a table is missing. This should be handled as a "Database not initialized" state rather than a connection failure.
