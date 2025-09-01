# seed_fonds.py
from app import create_app, db
from app.models.fond import Fond

fonds = [
    "Fond de Solidarité",
    "Fonds Droits de plaidoirie",
    "Fonds Cotisations",
    "Fonds Externe",
    "Fond Assistance Juridique",
]

app = create_app()
with app.app_context():
    for nom in fonds:
        if not Fond.query.filter_by(nom=nom).first():
            f = Fond(nom=nom, montant=0)
            db.session.add(f)
            print(f"Fond créé : {nom}")
    db.session.commit()
    print("✅ Tous les fonds ont été créés (si manquants).")
