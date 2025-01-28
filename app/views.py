from flask import jsonify, request, render_template, current_app
import logging
from datetime import datetime
from . import app
from .scripts import getNames, getPlan, getCurrentSchedule, saveCurrentSchedule
from .data import names



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'schedule-app'
    }), 200
    
    
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
    try:
        new_schedule = request.json
        
        # Сбрасываем все баллы
        for name in names:
            names[name] = 0
        
        # Распределяем баллы на основе нового расписания
        for day, day_names in new_schedule.items():
            points = 3 if day in ['Saturday', 'Sunday'] else 2
            for name in day_names:
                names[name] += points
        
        # Сохраняем новое расписание
        if saveCurrentSchedule(new_schedule):
            return jsonify({"status": "success", "message": "Schedule saved successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to save schedule"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        # Генерируем новое расписание
        new_schedule = getPlan(names)
        return jsonify(new_schedule), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500