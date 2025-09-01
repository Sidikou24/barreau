import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_batonnier_sql():
    try:
        # Paramètres de connexion
        connection_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'barreau_niger',
            'user': 'postgres',
            'password': 'sidik'
        }
        
        print("Création d'un utilisateur batonnier via SQL direct...")
        
        # Connexion à la base de données
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id, nom, prenom FROM users WHERE email = %s", ('sidik@gmail.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"❌ L'utilisateur existe déjà: ID {existing_user[0]}, {existing_user[1]} {existing_user[2]}")
            return
        
        # Créer l'utilisateur batonnier
        mot_de_passe_temp = '1234'
        password_hash = generate_password_hash(mot_de_passe_temp)
        
        cursor.execute("""
            INSERT INTO users (
                nom, prenom, email, date_naissance, password_hash, 
                telephone, adresse, role, statut, date_creation, must_change_password
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            'sidik', 'dari', 'sidikoudari@gmail.com', 
            datetime(1980, 1, 1).date(), password_hash,
            '+1234567890', '123 Rue du Barreau, Niamey', 
            'batonnier', 'actif', datetime.now(), True
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        print("✅ Utilisateur batonnier créé avec succès!")
        print(f"ID: {user_id}")
                
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Erreur PostgreSQL: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_batonnier_sql()
