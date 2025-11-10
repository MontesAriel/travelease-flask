from flask import Blueprint, render_template
from models.model import Destino

destinations_bp = Blueprint('destinations', __name__)

@destinations_bp.route('/destinos')
def destinos():
    destinos = Destino.query.all()
    return render_template("destinations.html", destinos=destinos)
