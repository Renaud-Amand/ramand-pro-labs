# SKILL: SUPABASE & DATA INTEGRATION

## 🔐 Security & Environment

- **Zero Hardcoding:** Never write API keys in code. Use `get_env()` to fetch from `.env`.
- **Role Awareness:** Explicitly define usage of `anon_key` (client) vs `service_role` (admin/backend).

## 📊 Data Layer (Layer 3)

- **Isolation:** Database logic lives ONLY in `execution/db_scripts/`.
- **Atomic Operations:** One script = one specific task (e.g., `upsert_user_score.py`).
- **Standardized Output:** Return clean JSON: `{"success": bool, "data": obj, "error": str}`.

## 💻 Windows & Environment Optimization

- **UTF-8 Enforcement:** Force UTF-8 encoding to prevent `UnicodeEncodeError` by adding `sys.stdout.reconfigure(encoding='utf-8')` at script startup.
- **Error Codes:** Handle Supabase `PGRST205` specifically as "Database Not Initialized."

## 🎯 MISSION: SECURITY & RGPD GUARDIAN

Ensure technical integrity, sensitive data protection (COPPA/RGPD), and legal compliance.

## 🛡️ GOLDEN RULES

1. **Privacy by Design:** Maximum anonymization of user data.
2. **Auth:** Use only secure Supabase protocols.
3. **Audit:** Verify every SQL query to prevent data leakage.

## 🚨 CRITICAL RULE: FAILURE PROTOCOL

If a potential vulnerability, DB error, or access issue occurs: **HALT PRODUCTION.** Document the vulnerability in the "LEARNING LOG" and patch the system before continuing.

## 🧠 LEARNING LOG (REtex)

### ❌ Past Failures & Solutions:

- (To be populated by Agent)
