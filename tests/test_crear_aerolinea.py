from models.model import Pais, Aerolinea
from config import db

def test_crear_aerolinea(app):
    with app.app_context():
        pais = Pais(nombre="Brasil")
        db.session.add(pais)
        db.session.commit()

        linea = Aerolinea(nombre="LATAM", codigo="LA", pais_id=pais.pais_id)
        db.session.add(linea)
        db.session.commit()

        saved = Aerolinea.query.filter_by(codigo="LA").first()

        assert saved is not None
        assert saved.pais.nombre == "Brasil"
