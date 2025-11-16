from flask import render_template, session, request, redirect, url_for, flash, abort
from config import create_app
from models.model import *
from datetime import datetime
from flask_bcrypt import Bcrypt


app = create_app()
bcrypt = Bcrypt(app)
app.secret_key = '6f740d75bb1d3727008056ed8f028205e82b000c9ab12bbf324805ecb5d83e50'

@app.context_processor
def inject_user():
    return dict(username=session.get('username'))


@app.template_filter("precio")
def formato_precio(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# RUTAS 
@app.route('/')
def home():
    destinos = Destino.query.limit(3).all()

    if 'username' in session:
        return render_template('index.html',
                               username=session['username'],
                               destinos=destinos)

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('usuario_id', None)

    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    email = request.form['email']
    contrasena = request.form['contrasena']
    confirmar = request.form['confirmar']

    if contrasena != confirmar:
        flash("Las contraseñas no coinciden.")
        session['show_modal'] = 'register'
        return redirect(url_for('home'))

    if Usuario.query.filter_by(email=email).first():
        flash("El email ya está registrado.")
        session['show_modal'] = 'register'
        return redirect(url_for('home'))

    hashed = bcrypt.generate_password_hash(contrasena).decode('utf-8')

    usuario = Usuario(
        nombre=nombre,
        email=email,
        contrasena=hashed
    )

    db.session.add(usuario)
    db.session.commit()

    flash("Cuenta creada con éxito. ¡Ya puedes iniciar sesión!")
    session['show_modal'] = 'login'
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    contrasena = request.form['contrasena']

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and bcrypt.check_password_hash(usuario.contrasena, contrasena):
        session['usuario_id'] = usuario.usuario_id
        session['username'] = usuario.nombre

        return redirect(url_for('home'))

    flash('Credenciales incorrectas.')
    session['show_modal'] = 'login'
    return redirect(url_for('home'))

@app.route('/clear_modal_flag')
def clear_modal_flag():
    session.pop('show_modal', None)
    return '', 204

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
    provincias = Provincia.query.all()
    return render_template('admin/destino_form.html', provincias=provincias)

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
    provincias = Provincia.query.all()
    return render_template("admin/destino_form.html", destino=destino, provincias=provincias)


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

# ---------- ADMIN ALOJAMIENTOS CRUD ----------

@app.route('/admin/alojamientos')
def admin_alojamientos():
    alojamientos = Alojamiento.query.all()
    return render_template('admin/alojamientos_list.html', alojamientos=alojamientos)


@app.route('/admin/alojamientos/new')
def admin_alojamiento_new():
    destinos = Destino.query.all()
    return render_template('admin/alojamiento_form.html', destinos=destinos)


@app.route('/admin/alojamientos/create', methods=["POST"])
def admin_alojamiento_create():
    destino_id = request.form["destino_id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio_noche = request.form["precio_noche"]
    imagen = request.form["imagen"]

    alojamiento = Alojamiento(
        destino_id=destino_id,
        nombre=nombre,
        descripcion=descripcion,
        precio_noche=precio_noche,
        imagen=imagen
    )

    db.session.add(alojamiento)
    db.session.commit()

    return redirect(url_for("admin_alojamientos"))


@app.route('/admin/alojamientos/editar/<int:alojamiento_id>')
def admin_alojamientos_editar(alojamiento_id):
    alojamiento = Alojamiento.query.get_or_404(alojamiento_id)
    destinos = Destino.query.all()
    return render_template("admin/alojamiento_form.html", alojamiento=alojamiento, destinos=destinos)


@app.route('/admin/alojamientos/update/<int:alojamiento_id>', methods=["POST"])
def admin_alojamientos_update(alojamiento_id):
    alojamiento = Alojamiento.query.get_or_404(alojamiento_id)

    alojamiento.destino_id = request.form["destino_id"]
    alojamiento.nombre = request.form["nombre"]
    alojamiento.descripcion = request.form["descripcion"]
    alojamiento.precio_noche = request.form["precio_noche"]
    alojamiento.imagen = request.form["imagen"]

    db.session.commit()

    return redirect(url_for("admin_alojamientos"))


@app.route('/admin/alojamientos/eliminar/<int:alojamiento_id>')
def admin_alojamientos_eliminar(alojamiento_id):
    alojamiento = Alojamiento.query.get_or_404(alojamiento_id)
    db.session.delete(alojamiento)
    db.session.commit()
    return redirect(url_for("admin_alojamientos"))

# ---------- ADMIN VUELOS CRUD ----------

@app.route('/admin/vuelos')
def admin_vuelos():
    vuelos = Vuelo.query.all()
    aerolineas = Aerolinea.query.all()
    aeropuertos = Aeropuerto.query.all()
    return render_template('admin/vuelos_list.html', vuelos=vuelos)


@app.route('/admin/vuelos/new')
def admin_vuelo_new():
    aerolineas = Aerolinea.query.all()
    aeropuertos = Aeropuerto.query.all()
    return render_template('admin/vuelo_form.html', aerolineas=aerolineas, aeropuertos=aeropuertos)


@app.route('/admin/vuelos/create', methods=["POST"])
def admin_vuelo_create():
    vuelo = Vuelo(
        aerolinea_id=request.form["aerolinea_id"],
        origen_id=request.form["origen_id"],
        destino_id=request.form["destino_id"],
        fecha_salida=request.form["fecha_salida"],
        fecha_llegada=request.form["fecha_llegada"],
        precio=request.form["precio"]
    )

    db.session.add(vuelo)
    db.session.commit()

    return redirect(url_for("admin_vuelos"))


@app.route('/admin/vuelos/edit/<int:vuelo_id>')
def admin_vuelo_edit(vuelo_id):
    vuelo = Vuelo.query.get_or_404(vuelo_id)
    aerolineas = Aerolinea.query.all()
    aeropuertos = Aeropuerto.query.all()
    return render_template('admin/vuelo_form.html', vuelo=vuelo, aerolineas=aerolineas, aeropuertos=aeropuertos)


@app.route('/admin/vuelos/update/<int:vuelo_id>', methods=["POST"])
def admin_vuelos_update(vuelo_id):
    vuelo = Vuelo.query.get_or_404(vuelo_id)

    vuelo.aerolinea_id = request.form["aerolinea_id"]
    vuelo.origen_id = request.form["origen_id"]
    vuelo.destino_id = request.form["destino_id"]
    vuelo.fecha_salida = request.form["fecha_salida"]
    vuelo.fecha_llegada = request.form["fecha_llegada"]
    vuelo.precio = request.form["precio"]

    db.session.commit()

    return redirect(url_for("admin_vuelos"))


@app.route('/admin/vuelos/delete/<int:vuelo_id>')
def admin_vuelo_delete(vuelo_id):
    vuelo = Vuelo.query.get_or_404(vuelo_id)
    db.session.delete(vuelo)
    db.session.commit()
    return redirect(url_for("admin_vuelos"))

# ---------- ADMIN PAISES CRUD ----------

@app.route('/admin/paises')
def admin_paises():
    paises = Pais.query.all()
    return render_template("admin/paises_list.html", paises=paises)


@app.route('/admin/paises/new')
def admin_pais_new():
    return render_template("admin/pais_form.html")


@app.route('/admin/paises/create', methods=["POST"])
def admin_pais_create():
    nuevo = Pais(nombre=request.form["nombre"])
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for("admin_paises"))


@app.route('/admin/paises/edit/<int:pais_id>')
def admin_pais_edit(pais_id):
    pais = Pais.query.get_or_404(pais_id)
    return render_template("admin/pais_form.html", pais=pais)


@app.route('/admin/paises/update/<int:pais_id>', methods=["POST"])
def admin_pais_update(pais_id):
    pais = Pais.query.get_or_404(pais_id)
    pais.nombre = request.form["nombre"]
    db.session.commit()
    return redirect(url_for("admin_paises"))


@app.route('/admin/paises/delete/<int:pais_id>')
def admin_pais_delete(pais_id):
    pais = Pais.query.get_or_404(pais_id)
    db.session.delete(pais)
    db.session.commit()
    return redirect(url_for("admin_paises"))


# ---------- ADMIN PROVINCIAS CRUD ----------
@app.route('/admin/provincias')
def admin_provincias():
    provincias = Provincia.query.all()
    return render_template('admin/provincias_list.html', provincias=provincias)

@app.route('/admin/provincias/new')
def admin_provincia_new():
    paises = Pais.query.all()
    return render_template('admin/provincia_form.html', paises=paises)

@app.route('/admin/provincias/create', methods=['POST'])
def admin_provincia_create():
    nombre = request.form['nombre']
    pais_id = request.form.get('pais_id') or None

    provincia = Provincia(nombre=nombre, pais_id=pais_id)
    db.session.add(provincia)
    db.session.commit()
    return redirect(url_for('admin_provincias'))

@app.route('/admin/provincias/editar/<int:provincia_id>')
def admin_provincia_editar(provincia_id):
    provincia = Provincia.query.get_or_404(provincia_id)
    paises = Pais.query.all()
    return render_template('admin/provincia_form.html', provincia=provincia, paises=paises)

@app.route('/admin/provincias/update/<int:provincia_id>', methods=['POST'])
def admin_provincia_update(provincia_id):
    provincia = Provincia.query.get_or_404(provincia_id)
    provincia.nombre = request.form['nombre']
    provincia.pais_id = request.form.get('pais_id') or None
    db.session.commit()
    return redirect(url_for('admin_provincias'))

@app.route('/admin/provincias/eliminar/<int:provincia_id>')
def admin_provincia_eliminar(provincia_id):
    provincia = Provincia.query.get_or_404(provincia_id)
    db.session.delete(provincia)
    db.session.commit()
    return redirect(url_for('admin_provincias'))

# ---------- ADMIN AEROPUERTOS CRUD ----------

@app.route('/admin/aeropuertos')
def admin_aeropuertos():
    aeropuertos = Aeropuerto.query.all()
    provincias = Provincia.query.all()
    return render_template("admin/aeropuertos_list.html", aeropuertos=aeropuertos)


@app.route('/admin/aeropuertos/new')
def admin_aeropuerto_new():
    provincias = Provincia.query.all()
    return render_template("admin/aeropuerto_form.html", provincias=provincias)


@app.route('/admin/aeropuertos/create', methods=["POST"])
def admin_aeropuerto_create():
    aeropuerto = Aeropuerto(
        codigo=request.form["codigo"],
        nombre=request.form["nombre"],
        ciudad=request.form["ciudad"],
        provincia_id=request.form["provincia_id"]
    )

    db.session.add(aeropuerto)
    db.session.commit()

    return redirect(url_for("admin_aeropuertos"))


@app.route('/admin/aeropuertos/edit/<int:aeropuerto_id>')
def admin_aeropuerto_edit(aeropuerto_id):
    aeropuerto = Aeropuerto.query.get_or_404(aeropuerto_id)
    provincias = Provincia.query.all()
    return render_template("admin/aeropuerto_form.html", aeropuerto=aeropuerto, provincias=provincias)


@app.route('/admin/aeropuertos/update/<int:aeropuerto_id>', methods=["POST"])
def admin_aeropuerto_update(aeropuerto_id):
    aeropuerto = Aeropuerto.query.get_or_404(aeropuerto_id)

    aeropuerto.codigo = request.form["codigo"]
    aeropuerto.nombre = request.form["nombre"]
    aeropuerto.ciudad = request.form["ciudad"]
    aeropuerto.provincia_id = request.form["provincia_id"]

    db.session.commit()

    return redirect(url_for("admin_aeropuertos"))


@app.route('/admin/aeropuertos/delete/<int:aeropuerto_id>')
def admin_aeropuerto_delete(aeropuerto_id):
    aeropuerto = Aeropuerto.query.get_or_404(aeropuerto_id)
    db.session.delete(aeropuerto)
    db.session.commit()
    return redirect(url_for("admin_aeropuertos"))


# ---------- ADMIN AEROLINEAS CRUD ----------

@app.route('/admin/aerolineas')
def admin_aerolineas():
    aerolineas = Aerolinea.query.all()
    return render_template("admin/aerolineas_list.html", aerolineas=aerolineas)


@app.route('/admin/aerolineas/new')
def admin_aerolinea_new():
    paises = Pais.query.all()
    return render_template("admin/aerolinea_form.html", paises=paises)


@app.route('/admin/aerolineas/create', methods=["POST"])
def admin_aerolinea_create():
    aerolinea = Aerolinea(
        nombre=request.form["nombre"],
        codigo=request.form["codigo"],
        pais_id=request.form["pais_id"]
    )

    db.session.add(aerolinea)
    db.session.commit()

    return redirect(url_for("admin_aerolineas"))


@app.route('/admin/aerolineas/edit/<int:aerolinea_id>')
def admin_aerolinea_edit(aerolinea_id):
    aerolinea = Aerolinea.query.get_or_404(aerolinea_id)
    paises = Pais.query.all()
    return render_template("admin/aerolinea_form.html", aerolinea=aerolinea, paises=paises)


@app.route('/admin/aerolineas/update/<int:aerolinea_id>', methods=["POST"])
def admin_aerolineas_update(aerolinea_id):
    aerolinea = Aerolinea.query.get_or_404(aerolinea_id)

    aerolinea.nombre = request.form["nombre"]
    aerolinea.codigo = request.form["codigo"]
    aerolinea.pais_id = request.form["pais_id"]

    db.session.commit()

    return redirect(url_for("admin_aerolineas"))


@app.route('/admin/aerolineas/delete/<int:aerolinea_id>')
def admin_aerolinea_delete(aerolinea_id):
    aerolinea = Aerolinea.query.get_or_404(aerolinea_id)
    db.session.delete(aerolinea)
    db.session.commit()
    return redirect(url_for("admin_aerolineas"))


# ---------- ADMIN RESERVAS CRUD ----------

@app.route('/admin/reservas')
def admin_reservas():
    reservas = Reserva.query.all()
    return render_template("admin/reservas_list.html", reservas=reservas)


@app.route('/admin/reservas/new')
def admin_reserva_new():
    usuarios = Usuario.query.all()
    alojamientos = Alojamiento.query.all()
    vuelos = Vuelo.query.all()
    return render_template(
        "admin/reserva_form.html",
        usuarios=usuarios,
        alojamientos=alojamientos,
        vuelos=vuelos
    )


@app.route('/admin/reservas/create', methods=["POST"])
def admin_reserva_create():
    reserva = Reserva(
        usuario_id=request.form["usuario_id"],
        alojamiento_id=request.form["alojamiento_id"],
        vuelo_ida_id=request.form["vuelo_ida_id"],
        vuelo_vuelta_id=request.form["vuelo_vuelta_id"],
        fecha_inicio=request.form["fecha_inicio"],
        fecha_fin=request.form["fecha_fin"],
        pasajeros=request.form["pasajeros"],
        precio_total=request.form["precio_total"],
        estado=request.form["estado"]
    )

    db.session.add(reserva)
    db.session.commit()

    return redirect(url_for("admin_reservas"))


@app.route('/admin/reservas/edit/<int:reserva_id>')
def admin_reserva_edit(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    usuarios = Usuario.query.all()
    alojamientos = Alojamiento.query.all()
    vuelos = Vuelo.query.all()
    return render_template(
        "admin/reserva_form.html",
        reserva=reserva,
        usuarios=usuarios,
        alojamientos=alojamientos,
        vuelos=vuelos
    )


@app.route('/admin/reservas/update/<int:reserva_id>', methods=["POST"])
def admin_reserva_update(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    reserva.usuario_id = request.form["usuario_id"]
    reserva.alojamiento_id = request.form["alojamiento_id"]
    reserva.vuelo_ida_id = request.form["vuelo_ida_id"]
    reserva.vuelo_vuelta_id = request.form["vuelo_vuelta_id"]
    reserva.fecha_inicio = request.form["fecha_inicio"]
    reserva.fecha_fin = request.form["fecha_fin"]
    reserva.pasajeros = request.form["pasajeros"]
    reserva.precio_total = request.form["precio_total"]
    reserva.estado = request.form["estado"]

    db.session.commit()

    return redirect(url_for("admin_reservas"))


@app.route('/admin/reservas/delete/<int:reserva_id>')
def admin_reserva_delete(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    db.session.delete(reserva)
    db.session.commit()
    return redirect(url_for("admin_reservas"))


# ---------- ADMIN PAGOS CRUD ----------

@app.route('/admin/pagos')
def admin_pagos():
    pagos = Pago.query.all()
    return render_template("admin/pagos_list.html", pagos=pagos)


@app.route('/admin/pagos/new')
def admin_pago_new():
    reservas = Reserva.query.all()
    return render_template("admin/pago_form.html", reservas=reservas)


@app.route('/admin/pagos/create', methods=["POST"])
def admin_pago_create():
    pago = Pago(
        reserva_id=request.form["reserva_id"],
        metodo=request.form["metodo"],
        estado=request.form["estado"],
        monto=request.form["monto"]
    )

    db.session.add(pago)
    db.session.commit()

    return redirect(url_for("admin_pagos"))


@app.route('/admin/pagos/edit/<int:pago_id>')
def admin_pago_edit(pago_id):
    pago = Pago.query.get_or_404(pago_id)
    reservas = Reserva.query.all()
    return render_template("admin/pago_form.html", pago=pago, reservas=reservas)


@app.route('/admin/pagos/update/<int:pago_id>', methods=["POST"])
def admin_pago_update(pago_id):
    pago = Pago.query.get_or_404(pago_id)

    pago.reserva_id = request.form["reserva_id"]
    pago.metodo = request.form["metodo"]
    pago.estado = request.form["estado"]
    pago.monto = request.form["monto"]

    db.session.commit()

    return redirect(url_for("admin_pagos"))


@app.route('/admin/pagos/delete/<int:pago_id>')
def admin_pago_delete(pago_id):
    pago = Pago.query.get_or_404(pago_id)
    db.session.delete(pago)
    db.session.commit()
    return redirect(url_for("admin_pagos"))


if __name__ == "__main__":
    app.run(debug=True)
