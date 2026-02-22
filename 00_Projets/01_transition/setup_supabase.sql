-- ==========================================
-- SCRIPT DE CONFIGURATION SUPABASE COMPLET
-- Projet : Alphabet Kids (Charlène)
-- Version : 2.0 (Avec politiques RLS complètes)
-- ==========================================

-- 1. Création de la table pour le contenu pédagogique
CREATE TABLE IF NOT EXISTS public.educational_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,                           
    type TEXT NOT NULL CHECK (type IN ('letter', 'number')),
    word TEXT,                                       
    image_url TEXT,                                  
    sound_url TEXT,                                  
    is_active BOOLEAN DEFAULT true,                  
    created_at TIMESTAMPTZ DEFAULT now()             
);

-- 2. Configuration des Buckets de Stockage
INSERT INTO storage.buckets (id, name, public)
VALUES ('images', 'images', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public)
VALUES ('sounds', 'sounds', true)
ON CONFLICT (id) DO NOTHING;

-- 3. Activation et Configuration de Row Level Security (RLS)
ALTER TABLE public.educational_content ENABLE ROW LEVEL SECURITY;

-- Suppression des anciennes politiques si elles existent pour éviter les doublons
DROP POLICY IF EXISTS "Lecture publique pour tous" ON public.educational_content;
DROP POLICY IF EXISTS "Autoriser l'insertion pour tous" ON public.educational_content;
DROP POLICY IF EXISTS "Autoriser la modification pour tous" ON public.educational_content;

-- Création des nouvelles politiques
CREATE POLICY "Lecture publique pour tous" 
ON public.educational_content FOR SELECT USING (true);

CREATE POLICY "Autoriser l'insertion pour tous" 
ON public.educational_content FOR INSERT WITH CHECK (true);

CREATE POLICY "Autoriser la modification pour tous" 
ON public.educational_content FOR UPDATE USING (true);

-- Politique pour le stockage (lecture publique)
DROP POLICY IF EXISTS "Images publiques" ON storage.objects;
DROP POLICY IF EXISTS "Sons publics" ON storage.objects;

CREATE POLICY "Images publiques" 
ON storage.objects FOR SELECT USING (bucket_id = 'images');

CREATE POLICY "Sons publics" 
ON storage.objects FOR SELECT USING (bucket_id = 'sounds');