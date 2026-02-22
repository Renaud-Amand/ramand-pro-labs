import asyncio
# Python trouve maintenant 'database' naturellement car ils sont dans le même dossier !
from database.auth_manager import login_user, check_local_session, logout_user

async def run_tests():
    print("--- DÉBUT DES TESTS DU FLUX D'AUTHENTIFICATION ---")
    
    has_session = await check_local_session()
    print(f"1. Session locale existante au démarrage ? {has_session}")

    print("\n2. Tentative de connexion à Supabase...")
    # On utilise ton compte de test
    success, msg, data = await login_user("test@dys.fr", "test")
    print(f"   Résultat : {success} | Message : {msg}")
    
    if success:
        has_session = await check_local_session()
        print(f"\n3. Session locale sauvegardée après connexion ? {has_session}")
        
        print("\n4. Test de déconnexion...")
        out_success, out_msg = await logout_user()
        print(f"   Résultat : {out_success} | Message : {out_msg}")
        
        has_session = await check_local_session()
        print(f"\n5. Session locale supprimée après déconnexion ? {not has_session}")

if __name__ == "__main__":
    asyncio.run(run_tests())