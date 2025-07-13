#!/usr/bin/env python3
"""
Script pour créer la migration initiale de la base de données MySQL.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Exécuter une commande et afficher le résultat."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} terminé")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return None

def main():
    """Fonction principale."""
    print("🚀 Création de la migration initiale pour MySQL")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("alembic.ini").exists():
        print("❌ Fichier alembic.ini non trouvé. Assurez-vous d'être dans le répertoire backend.")
        sys.exit(1)
    
    # Initialiser Alembic si pas déjà fait
    if not Path("alembic").exists():
        print("🔄 Initialisation d'Alembic...")
        run_command("alembic init alembic", "Initialisation d'Alembic")
    
    # Créer la migration initiale
    print("🔄 Création de la migration initiale...")
    result = run_command("alembic revision --autogenerate -m 'Initial migration for MySQL'", 
                        "Création de la migration initiale")
    
    if result:
        print("\n📝 Migration créée avec succès!")
        print("📋 Pour appliquer la migration, exécutez:")
        print("   alembic upgrade head")
        print("\n📋 Pour vérifier le statut des migrations:")
        print("   alembic current")
        print("   alembic history")
    else:
        print("❌ Échec de la création de la migration")
        sys.exit(1)

if __name__ == "__main__":
    main()