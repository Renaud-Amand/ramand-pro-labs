"""
Script: test_supabase_conn.py
Layer: 3 - Execution (deterministic tool)
Role: Anon key (client-side read only)
Purpose: Verify that Supabase credentials are valid and the connection works.
Returns: stdout message + exit code (0=success, 1=failure)
"""

import io
import os
import sys
from pathlib import Path

# Force UTF-8 output so emojis render correctly on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def load_env(env_path: Path = None) -> dict:
    """
    Load environment variables from a .env file into a dictionary.
    Does NOT override existing system environment variables.

    Args:
        env_path: Path to the .env file. Defaults to <project_root>/.env.

    Returns:
        A dict with the loaded key-value pairs.

    Raises:
        FileNotFoundError: If the .env file does not exist.
        ValueError: If a required variable is missing or empty.
    """
    if env_path is None:
        # Resolve path: execution/ -> project root -> .env
        env_path = Path(__file__).resolve().parent.parent / ".env"

    if not env_path.exists():
        raise FileNotFoundError(
            f".env file not found at: {env_path}\n"
            "Please create it with SUPABASE_URL and SUPABASE_KEY."
        )

    loaded = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                print(f"[WARNING] Malformed line {line_num} in .env: '{line}' — skipped.")
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Do not override system env vars
            if key not in os.environ:
                os.environ[key] = value
            loaded[key] = os.environ[key]

    return loaded


def get_supabase_credentials() -> tuple[str, str]:
    """
    Load and validate SUPABASE_URL and SUPABASE_KEY from the environment.

    Returns:
        Tuple (SUPABASE_URL, SUPABASE_KEY)

    Raises:
        ValueError: If either variable is missing or still holding a placeholder.
    """
    load_env()

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()

    if not url:
        raise ValueError("SUPABASE_URL is not set in the .env file.")
    if not key:
        raise ValueError("SUPABASE_KEY is not set in the .env file.")

    # Guard against unmodified placeholder values
    if "your-project-ref" in url or "your-anon-key" in key:
        raise ValueError(
            "Placeholder values detected in .env.\n"
            "Please replace SUPABASE_URL and SUPABASE_KEY with your real credentials."
        )

    return url, key


def _ping_rest_api(url: str, key: str) -> bool:
    """
    Perform a lightweight HTTP GET on the PostgREST root endpoint.
    Returns True if HTTP 200, False otherwise.
    """
    try:
        import httpx
        resp = httpx.get(
            url.rstrip("/") + "/rest/v1/",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"   [ping error] {type(e).__name__}: {e}")
        return False


def main() -> None:
    """
    Main entry point. Two-phase connectivity test:
      Phase 1 — HTTP REST ping (validates URL + key).
      Phase 2 — Table query on 'profiles' (validates DB access + RLS).
    Exits with code 0 on success, 1 on any failure.
    """
    # --- Step 1: Load credentials ---
    try:
        url, key = get_supabase_credentials()
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # --- Step 2: Import Supabase client ---
    try:
        from supabase import create_client, Client
    except ImportError:
        print(
            "❌ 'supabase' package is not installed.\n"
            "   Run: pip install supabase"
        )
        sys.exit(1)

    # --- Step 3: Phase 1 — HTTP REST ping ---
    print(f"[1/2] Pinging Supabase REST API at {url} ...")
    if not _ping_rest_api(url, key):
        print(
            "❌ Supabase REST API is unreachable.\n"
            "   Check your SUPABASE_URL and network connectivity."
        )
        sys.exit(1)
    print("      REST API responded HTTP 200. Credentials are valid.")

    # --- Step 4: Initialize the Supabase client ---
    try:
        client: Client = create_client(url, key)
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client:\n   {type(e).__name__}: {e}")
        sys.exit(1)

    # --- Step 5: Phase 2 — Table query probe ---
    print("[2/2] Querying table 'profiles' ...")
    try:
        response = client.table("profiles").select("*").limit(1).execute()
        row_count = len(response.data)
        print(f"      Query succeeded — returned {row_count} row(s).")
        print("")
        print("✅ Connexion Supabase réussie !")

    except Exception as e:
        error_msg = str(e)
        # PGRST205: table not in schema cache (table doesn't exist yet)
        is_table_missing = (
            "PGRST205" in error_msg
            or "Could not find the table" in error_msg
            or ("relation" in error_msg and "does not exist" in error_msg)
        )
        if is_table_missing:
            print(
                "      [WARNING] Table 'profiles' does not exist yet — this is expected\n"
                "      on a fresh project. The connection itself is healthy.\n"
            )
            print("✅ Connexion Supabase réussie ! (table 'profiles' not yet created)")
        else:
            print(
                f"❌ Supabase query failed:\n"
                f"   {type(e).__name__}: {error_msg}\n\n"
                f"Possible causes:\n"
                f"  - RLS (Row Level Security) is blocking the anon key.\n"
                f"  - The table name is misspelled.\n"
                f"  - Invalid SUPABASE_URL or SUPABASE_KEY."
            )
            sys.exit(1)



if __name__ == "__main__":
    main()

