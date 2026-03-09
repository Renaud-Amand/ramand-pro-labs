-- SPRINT 0 : Migration Child Profiles (Logic & Security)

-- 1. Ajout des colonnes de données et de sécurité
ALTER TABLE public.child_profiles 
ADD COLUMN IF NOT EXISTS age INTEGER DEFAULT 6,
ADD COLUMN IF NOT EXISTS avatar_config JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS dys_settings JSONB DEFAULT '{"font": "OpenDyslexic", "contrast": "default"}'::jsonb,
ADD COLUMN IF NOT EXISTS pin_salt TEXT; -- Indispensable pour le hachage sécurisé

-- 2. Renommage sécurisé de la colonne PIN
-- On vérifie si pin_code existe pour le transformer en pin_hash
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='child_profiles' AND column_name='pin_code') THEN
    ALTER TABLE public.child_profiles RENAME COLUMN pin_code TO pin_hash;
  ELSE
    ALTER TABLE public.child_profiles ADD COLUMN IF NOT EXISTS pin_hash TEXT;
  END IF;
END $$;