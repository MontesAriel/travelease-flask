from flask import render_template, session, request, redirect, url_for, flash, abort
from config import create_app
from models.model import *
from datetime import datetime
from flask_bcrypt import Bcrypt


app = create_app()
bcrypt = Bcrypt(app)
app.secret_key = '6f740d75bb1d3727008056ed8f028205e82b000c9ab12bbf324805ecb5d83e50'


@app.template_filter("precio")
def formato_precio(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# RUTAS 
@app.route('/')
def home():
    destinos = Destino.query.limit(3).all()
    if 'username' in session:
        return render_template('index.html', username=session['username'], destinos=destinos)
    return render_template('index.html', destinos=destinos)


@app.route('/destino/<int:destino_id>')
def destino_detalle(destino_id):
    destino = Destino.query.get_or_404(destino_id)
    alojamiento = Alojamiento.query.filter_by(destino_id=destino_id).first()
    vuelos = [pv.vuelo for pv in destino.vuelos]

    return render_template(
        "destino/destino_id.html",
        destino=destino,
        imagenes=destino.imagenes,
        destacados=destino.destacados,
        incluye=destino.incluye,
        itinerario=destino.itinerario,
        alojamiento=alojamiento,
        vuelos=vuelos
    )

@app.route('/reserva/<int:destino_id>', methods=["POST"])
def crear_reserva(destino_id):
    if "usuario_id" not in session:
        flash("Debes iniciar sesión para realizar una reserva.")
        return redirect(url_for("login"))

    destino = Destino.query.get_or_404(destino_id)
    alojamiento = Alojamiento.query.filter_by(destino_id=destino_id).first()
    vuelos = [pv.vuelo for pv in destino.vuelos]

    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")
    pasajeros = int(request.form.get("pasajeros", 1))
    precio_total = float(request.form.get("precio_total", 0))

    if not fecha_inicio or not fecha_fin or precio_total <= 0:
        abort(400, "Datos de reserva inválidos")

    reserva = Reserva(
        usuario_id=session["usuario_id"],
        alojamiento_id=alojamiento.alojamiento_id if alojamiento else None,
        vuelo_ida_id=vuelos[0].vuelo_id if len(vuelos) > 0 else None,
        vuelo_vuelta_id=vuelos[1].vuelo_id if len(vuelos) > 1 else None,
        fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d"),
        fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d"),
        pasajeros=pasajeros,
        precio_total=precio_total,
        estado="pendiente"
    )

    db.session.add(reserva)
    db.session.commit()
    session["reserva_id"] = reserva.reserva_id

    flash("Reserva creada con éxito. Continuá con el pago.")
    return redirect(url_for("payment"))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    contrasena = request.form['contrasena']

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and bcrypt.check_password_hash(usuario.contrasena, contrasena):
        session['usuario_id'] = usuario.usuario_id
        session['username'] = usuario.nombre
        flash('Inicio de sesión exitoso.')
        return redirect(url_for('home'))
    else:
        flash('Credenciales incorrectas.')
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    email = request.form['email']
    contrasena = request.form['contrasena']
    confirmar = request.form['confirmar']

    # Validaciones básicas
    if contrasena != confirmar:
        flash('Las contraseñas no coinciden.')
        return redirect(url_for('home'))

    if Usuario.query.filter_by(email=email).first():
        flash('El email ya está registrado.')
        return redirect(url_for('home'))

    hash_pw = bcrypt.generate_password_hash(contrasena).decode('utf-8')
    nuevo_usuario = Usuario(nombre=nombre, email=email, contrasena=hash_pw)
    db.session.add(nuevo_usuario)
    db.session.commit()

    flash('Registro exitoso. Ahora puedes iniciar sesión.')
    return redirect(url_for('home'))


@app.route('/panel-admin')
def panelAdmin():
    return 'admin'

@app.route('/destinations')
def destinations():
    return render_template('packages.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/flights')
def flights():
    return 'vuelos'

@app.route('/payment')
def payment():
    reserva_id = session.get("reserva_id")
    usuario_id = session.get("usuario_id")

    if not reserva_id or not usuario_id:
        flash("No hay una reserva activa o usuario logueado.")
        return redirect(url_for("home"))

    reserva = Reserva.query.get_or_404(reserva_id)
    alojamiento = Alojamiento.query.get(reserva.alojamiento_id)
    vuelo_ida = Vuelo.query.get(reserva.vuelo_ida_id)
    vuelo_vuelta = Vuelo.query.get(reserva.vuelo_vuelta_id)
    usuario = Usuario.query.get(usuario_id)

    return render_template(
        "payment.html",
        reserva=reserva,
        alojamiento=alojamiento,
        vuelo_ida=vuelo_ida,
        vuelo_vuelta=vuelo_vuelta,
        usuario=usuario
    )

@app.route('/payment/process', methods=["POST"])
def procesar_pago():
    reserva_id = session.get("reserva_id")
    if not reserva_id:
        flash("No hay una reserva activa.")
        return redirect(url_for("home"))

    metodo = request.form.get("metodo_pago")
    if not metodo:
        flash("Debes seleccionar un método de pago.")
        return redirect(url_for("payment"))

    reserva = Reserva.query.get_or_404(reserva_id)

    # Crear el pago
    pago = Pago(
        reserva_id=reserva.reserva_id,
        metodo=metodo,
        monto=reserva.precio_total,
        estado="exitoso"
    )
    db.session.add(pago)

    # Cambiar estado de la reserva
    reserva.estado = "pagado"
    db.session.commit()

    flash("Pago realizado con éxito.")
    return redirect(url_for("payment_successful"))


@app.route('/accommodations')
def accommodations():
    return 'alojamientos'


@app.route('/payment-successful')
def payment_successful():
    return render_template('payment-successful.html')

@app.route('/destinations/<origin>/<destination>/<start_date>/<end_date>', methods=['POST'])
def view_destinations(origin, destination, start_date, end_date):
    return render_template(
        'destinations.html',
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


#PANEL ADMIN

@app.route('/admin/destinos')
def admin_destinos():
    destinos = Destino.query.all()
    return render_template('admin/destinos_list.html', destinos=destinos)

@app.route('/admin/destinos/new')
def admin_destino_new():
    return render_template('admin/destino_form.html')

@app.route('/admin/destinos/create', methods=["POST"])
def admin_destino_create():
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    imagen = request.form["imagen"]

    destino = Destino(nombre=nombre, precio_base=precio, imagen=imagen)
    db.session.add(destino)
    db.session.commit()

    return redirect(url_for("admin_destinos"))

# ---------- ADMIN DESTINOS CRUD ----------

@app.route('/admin/destinos/editar/<int:destino_id>')
def admin_destinos_editar(destino_id):
    destino = Destino.query.get_or_404(destino_id)
    return render_template("admin/destino_form.html", destino=destino)


@app.route('/admin/destinos/update/<int:destino_id>', methods=["POST"])
def admin_destinos_update(destino_id):
    destino = Destino.query.get_or_404(destino_id)

    destino.nombre = request.form["nombre"]
    destino.precio_base = request.form["precio"]
    destino.imagen = request.form["imagen"]

    db.session.commit()

    return redirect(url_for("admin_destinos"))


@app.route('/admin/destinos/eliminar/<int:destino_id>')
def admin_destinos_eliminar(destino_id):
    destino = Destino.query.get_or_404(destino_id)
    db.session.delete(destino)
    db.session.commit()
    return redirect(url_for("admin_destinos"))



if __name__ == "__main__":
    app.run(debug=True)
