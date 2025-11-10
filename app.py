from flask import render_template, session, request, redirect, url_for
from config import create_app
from models.model import *

app = create_app()
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

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect(url_for('home'))
#     return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('home'))

# @app.route('/register')
# def register():
#     return 'register'

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

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/accommodations')
def accommodations():
    return 'alojamientos'


@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/payment-successful')
def paymentSuccessful():
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
