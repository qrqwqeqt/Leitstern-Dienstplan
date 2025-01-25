from flask import jsonify, request, render_template
from . import app
from .scripts import getNames, getPlan
from .data import names

@app.route('/', methods=['GET'])
def index():
    return render_template('schedule.html')

@app.route('/names', methods=['GET'])
def get_names():
    return jsonify(getNames())

@app.route('/schedule', methods=['GET'])
def get_schedule():
    return jsonify(getPlan())

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    new_schedule = request.json
    
    # Reset all points
    for name in names:
        names[name] = 0
    
    # Distribute points based on new schedule
    for day, day_names in new_schedule.items():
        points = 3 if day in ['Saturday', 'Sunday'] else 2
        for name in day_names:
            names[name] += points
    
    return jsonify({"status": "success"}), 200