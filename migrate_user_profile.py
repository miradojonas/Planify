"""
Script de migration pour ajouter les nouveaux champs de profil à la table users
"""

from app import app, db
from models.user import User

def migrate_user_table():
    """Ajouter les nouveaux champs à la table users"""
    
    with app.app_context():
        # Obtenir la connexion à la base de données
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        try:
            # Ajouter les nouveaux champs un par un
            new_columns = [
                ("profile_photo", "VARCHAR(255)"),
                ("bio", "TEXT"),
                ("phone", "VARCHAR(20)"),
                ("birth_date", "DATE"),
                ("email_notifications", "BOOLEAN DEFAULT 1"),
                ("homework_reminders", "BOOLEAN DEFAULT 1"),
                ("theme", "VARCHAR(10) DEFAULT 'light'"),
                ("language", "VARCHAR(5) DEFAULT 'fr'"),
                ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
            ]
            
            for column_name, column_type in new_columns:
                try:
                    # Vérifier si la colonne existe déjà
                    cursor.execute(f"PRAGMA table_info(users)")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    if column_name not in columns:
                        # Ajouter la colonne
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                        print(f"✅ Colonne '{column_name}' ajoutée avec succès")
                    else:
                        print(f"ℹ️  Colonne '{column_name}' existe déjà")
                        
                except Exception as e:
                    print(f"❌ Erreur pour la colonne '{column_name}': {e}")
            
            # Valider les changements
            connection.commit()
            print("\n✅ Migration terminée avec succès!")
            
        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la migration: {e}")
            
        finally:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    migrate_user_table()