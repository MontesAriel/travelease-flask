from models.model import Usuario
from config import db

def test_crear_usuario(app):
    with app.app_context():
        usuario = Usuario(
            nombre="Ariel",
            email="test@example.com",
            contrasena="123456"
        )

        db.session.add(usuario)
        db.session.commit()

        saved = Usuario.query.filter_by(email="test@example.com").first()

        assert saved is not None
        assert saved.nombre == "Ariel"
