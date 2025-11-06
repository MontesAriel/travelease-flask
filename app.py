from flask import Flask, render_template, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = '6f740d75bb1d3727008056ed8f028205e82b000c9ab12bbf324805ecb5d83e50'

# GET
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html'), session['username']
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('home'))

@app.route('/register')
def register():
    return 'login'

@app.route('/panel-admin')
def panelAdmin():
    return 'admin'

@app.route('/destinations')
def destinations():
    return 'destinos'

@app.route('/flights')
def flights():
    return 'vuelos'

@app.route('/accommodations')
def accommodations():
    return 'alojamientos'

# parametros: <nombre> <int:edad>

@app.route('/reservation-detail')
def reservationDetail():
    return 'detalle reserva'

# POST
@app.route('/destinations/<origin>/<destination>/<start_date>/<end_date>', methods=['POST'])
def view_destinations(origin, destination, start_date, end_date):
    return destinations(origin, destination, start_date, end_date)


# NOT FOUND
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404