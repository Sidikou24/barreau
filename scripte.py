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
            'password': 'hama'
        }
        
        print("Création d'un utilisateur batonnier via SQL direct...")
        
        # Connexion à la base de données
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # S'assurer que la colonne must_change_password existe (compatibilité avec schémas existants)
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT TRUE NOT NULL
        """)
        conn.commit()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id, nom, prenom FROM users WHERE email = %s", ('hamaamadou@gmail.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f" L'utilisateur existe déjà: ID {existing_user[0]}, {existing_user[1]} {existing_user[2]}")
            return
        
        # Créer l'utilisateur batonnier
        mot_de_passe_temp = '12345'
        password_hash = generate_password_hash(mot_de_passe_temp)
        
        cursor.execute("""
            INSERT INTO users (
                nom, prenom, email, date_naissance, password_hash, 
                telephone, adresse, role, statut, date_creation, must_change_password
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            'hama', 'amadou', 'hamaamadou@gmail.com', 
            datetime(1980, 1, 1).date(), password_hash,
            '+1234567890', '123 Rue du Barreau, Niamey', 
            'batonnier', 'actif', datetime.now(), True
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        print("Utilisateur batonnier créé avec succès!")
        print(f"ID: {user_id}")
                
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Erreur PostgreSQL: {e}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

def create_assistant_admin_sql():
    try:
        connection_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'barreau_niger',
            'user': 'postgres',
            'password': 'hama'
        }
        
        print("Création d'un Assistant Administratif via SQL direct...")
        
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT TRUE NOT NULL
        """)
        conn.commit()

        cursor.execute("SELECT id, nom, prenom FROM users WHERE email = %s", ('admin@barreau.ne',))
        existing_user = cursor.fetchone()
        if existing_user:
            print(f" L'utilisateur existe déjà: ID {existing_user[0]}, {existing_user[1]} {existing_user[2]}")
            return

        mot_de_passe_temp = '12345'
        password_hash = generate_password_hash(mot_de_passe_temp)

        cursor.execute("""
            INSERT INTO users (
                nom, prenom, email, date_naissance, password_hash, 
                telephone, adresse, role, statut, date_creation, must_change_password
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            'Admin', 'Assistant', 'admin@barreau.ne',
            datetime(1990, 1, 1).date(), password_hash,
            '+22700000000', 'Barreau du Niger',
            'assistant_administratif', 'actif', datetime.now(), True
        ))

        user_id = cursor.fetchone()[0]
        conn.commit()

        print("Assistant Administratif créé avec succès!")
        print(f"ID: {user_id}")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Erreur PostgreSQL: {e}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

def create_avocat_sql():
    try:
        connection_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'barreau_niger',
            'user': 'postgres',
            'password': 'hama'
        }
        print("Création d'un Avocat via SQL direct...")
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # S'assurer de la colonne must_change_password
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT TRUE NOT NULL
        """)
        conn.commit()

        # Vérifier si l'utilisateur existe
        email = 'avocat1@barreau.ne'
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
            print(f"Utilisateur avocat déjà existant (id={user_id}).")
        else:
            pwd_hash = generate_password_hash('12345')
            cursor.execute("""
                INSERT INTO users (nom, prenom, email, date_naissance, password_hash, telephone, adresse, role, statut, date_creation, must_change_password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                'Ali', 'Issa', email, datetime(1992,5,20).date(), pwd_hash,
                '+22790000000', 'Niamey', 'avocat', 'actif', datetime.now(), True
            ))
            user_id = cursor.fetchone()[0]
            conn.commit()
            print(f"Utilisateur avocat créé (id={user_id}).")

        # Créer l'entrée dans avocats si manquante
        cursor.execute("SELECT avocat_id FROM avocats WHERE user_id = %s", (user_id,))
        a = cursor.fetchone()
        if a:
            print(f"Profil Avocat déjà existant (avocat_id={a[0]}).")
        else:
            cursor.execute("""
                INSERT INTO avocats (user_id, nom, naissance, sexe, statut, date_creation)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING avocat_id
            """, (
                user_id, 'ALI ISSA', datetime(1992,5,20).date(), 'M', 'actif', datetime.now()
            ))
            avocat_id = cursor.fetchone()[0]
            conn.commit()
            print(f"Profil Avocat créé (avocat_id={avocat_id}).")

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Erreur PostgreSQL: {e}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    #create_batonnier_sql()
    #create_assistant_admin_sql()
    create_avocat_sql()
    