from config import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = "usuario"
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    creado = db.Column(db.DateTime, default=datetime.utcnow)


class Pais(db.Model):
    __tablename__ = "pais"
    pais_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)


class Provincia(db.Model):
    __tablename__ = "provincia"
    provincia_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    pais_id = db.Column(db.Integer, db.ForeignKey("pais.pais_id"))
    pais = db.relationship("Pais") 
    destinos = db.relationship("Destino", back_populates="provincia")


class Destino(db.Model):
    __tablename__ = "destino"
    destino_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey("provincia.provincia_id"))
    descripcion = db.Column(db.String(200))
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)
    imagen = db.Column(db.String(255), nullable=False)
    imagenes = db.relationship("ImagenDestino", backref="destino", cascade="all, delete")
    destacados = db.relationship("DestacadoDestino", backref="destino", cascade="all, delete")
    incluye = db.relationship("IncluyeDestino", backref="destino", cascade="all, delete")
    itinerario = db.relationship("ItinerarioDestino", backref="destino", cascade="all, delete")
    vuelos = db.relationship("PaqueteVuelo", backref="destino")
    alojamientos = db.relationship("Alojamiento", back_populates="destino")
    provincia = db.relationship("Provincia", back_populates="destinos")



class ItinerarioDestino(db.Model):
    __tablename__ = "itinerario_paquete"
    itinerario_id = db.Column(db.Integer, primary_key=True)
    destino_id = db.Column(db.Integer, db.ForeignKey("destino.destino_id"))
    dia = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

class IncluyeDestino(db.Model):
    __tablename__ = "incluye_destino"
    incluye_id = db.Column(db.Integer, primary_key=True)
    destino_id = db.Column(db.Integer, db.ForeignKey("destino.destino_id"))
    texto = db.Column(db.String(255), nullable=False)

class DestacadoDestino(db.Model):
    __tablename__ = "destacado_destino"
    destacado_id = db.Column(db.Integer, primary_key=True)
    destino_id = db.Column(db.Integer, db.ForeignKey("destino.destino_id"))
    texto = db.Column(db.String(255), nullable=False)

class ImagenDestino(db.Model):
    __tablename__ = "imagen_destino"
    imagen_id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), nullable=False)
    destino_id = db.Column(db.Integer, db.ForeignKey("destino.destino_id"))


class Aeropuerto(db.Model):
    __tablename__ = "aeropuerto"
    aeropuerto_id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey("provincia.provincia_id"))
    provincia = db.relationship("Provincia")

class Aerolinea(db.Model):
    __tablename__ = "aerolinea"
    aerolinea_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    pais_id = db.Column(db.Integer, db.ForeignKey("pais.pais_id"))
    pais = db.relationship("Pais")

class Vuelo(db.Model):
    __tablename__ = "vuelo"
    
    vuelo_id = db.Column(db.Integer, primary_key=True)
    aerolinea_id = db.Column(db.Integer, db.ForeignKey("aerolinea.aerolinea_id"))
    origen_id = db.Column(db.Integer, db.ForeignKey("aeropuerto.aeropuerto_id"))
    destino_id = db.Column(db.Integer, db.ForeignKey("aeropuerto.aeropuerto_id"))
    fecha_salida = db.Column(db.DateTime, nullable=False)
    fecha_llegada = db.Column(db.DateTime, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

    aerolinea = db.relationship("Aerolinea")
    origen = db.relationship("Aeropuerto", foreign_keys=[origen_id])
    destino = db.relationship("Aeropuerto", foreign_keys=[destino_id])
    @property
    def codigo(self):
        return f"{self.aerolinea.codigo}{self.vuelo_id}"
    

class PaqueteVuelo(db.Model):
    __tablename__ = "paquete_vuelo"
    
    id = db.Column(db.Integer, primary_key=True)
    destino_id = db.Column(db.Integer, db.ForeignKey("destino.destino_id"))
    vuelo_id = db.Column(db.Integer, db.ForeignKey("vuelo.vuelo_id"))
    tipo = db.Column(db.String(10), nullable=False)
    vuelo = db.relationship("Vuelo")


class Alojamiento(db.Model):
    __tablename__ = "alojamiento"
    alojamiento_id = db.Column(db.Integer, primary_key=True)
    destino_id = db.Column(db.Integer, db.ForeignKey("destino.destino_id"))
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio_noche = db.Column(db.Numeric(10, 2), nullable=False)
    imagen = db.Column(db.String(255), nullable=False)
    imagenes = db.relationship("ImagenAlojamiento", backref="alojamiento", cascade="all, delete")
    destino = db.relationship("Destino", back_populates="alojamientos")


class ImagenAlojamiento(db.Model):
    __tablename__ = "imagen_alojamiento"
    imagen_id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), nullable=False)
    alojamiento_id = db.Column(db.Integer, db.ForeignKey("alojamiento.alojamiento_id"))


class Reserva(db.Model):
    __tablename__ = "reserva"
    reserva_id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.usuario_id"))
    alojamiento_id = db.Column(db.Integer, db.ForeignKey("alojamiento.alojamiento_id"))
    vuelo_ida_id = db.Column(db.Integer, db.ForeignKey("vuelo.vuelo_id"))
    vuelo_vuelta_id = db.Column(db.Integer, db.ForeignKey("vuelo.vuelo_id"))
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    pasajeros = db.Column(db.Integer)
    precio_total = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.String(30), default="pendiente")
    usuario = db.relationship("Usuario", backref="reservas")
    alojamiento = db.relationship("Alojamiento", backref="reservas")
    vuelo_ida = db.relationship("Vuelo", foreign_keys=[vuelo_ida_id])
    vuelo_vuelta = db.relationship("Vuelo", foreign_keys=[vuelo_vuelta_id])


class Pago(db.Model):
    __tablename__ = "pago"
    pago_id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey("reserva.reserva_id"))
    metodo = db.Column(db.String(30), nullable=False)
    estado = db.Column(db.String(30), default="pendiente")
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
