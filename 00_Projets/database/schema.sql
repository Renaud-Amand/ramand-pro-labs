-- =============================================================================
-- FILE: database/schema.sql
-- PURPOSE: Create the `profiles` table linked to Supabase Auth users.
-- HOW TO RUN: Paste this file in the Supabase Dashboard > SQL Editor > Run.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- TABLE: profiles
-- One row per authenticated user (mirrors auth.users via foreign key).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    -- Primary key: same UUID as auth.users to allow easy joins
    id          UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Automatically set on insert; never updated
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Display name chosen by the user
    username    TEXT,

    -- URL to the user's avatar (Supabase Storage or external)
    avatar_url  TEXT
);


-- -----------------------------------------------------------------------------
-- COMMENTS (optional but good practice for future maintainers)
-- -----------------------------------------------------------------------------
COMMENT ON TABLE  public.profiles              IS 'Public profile data for each authenticated user.';
COMMENT ON COLUMN public.profiles.id           IS 'FK to auth.users.id — set at registration.';
COMMENT ON COLUMN public.profiles.created_at   IS 'Timestamp of profile creation (UTC).';
COMMENT ON COLUMN public.profiles.username     IS 'Display name chosen by the user.';
COMMENT ON COLUMN public.profiles.avatar_url   IS 'URL to the user avatar image.';


-- -----------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS)
-- Always enable RLS on public tables in Supabase.
-- -----------------------------------------------------------------------------
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can read their own profile
CREATE POLICY "users_select_own_profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Policy 2: Users can insert their own profile (on first login)
CREATE POLICY "users_insert_own_profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Policy 3: Users can update their own profile
CREATE POLICY "users_update_own_profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);


-- -----------------------------------------------------------------------------
-- TRIGGER: auto-create a profile row when a new user signs up in auth.users
-- This avoids manual profile creation after each registration.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, created_at, username, avatar_url)
    VALUES (
        NEW.id,
        NOW(),
        NEW.raw_user_meta_data ->> 'username',   -- pulled from signup metadata
        NEW.raw_user_meta_data ->> 'avatar_url'  -- pulled from signup metadata
    );
    RETURN NEW;
END;
$$;

-- Attach the trigger to auth.users
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
