from flask import jsonify, request, render_template, current_app
import logging
from datetime import datetime, timedelta
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
        data = request.json
        new_schedule = data.get('schedule', {}) if isinstance(data, dict) else data
        
        # Сбрасываем все баллы
        for name in names:
            names[name] = 0
        
        # Распределяем баллы на основе нового расписания
        for day, day_names in new_schedule.items():
            points = 3 if day in ['Saturday', 'Sunday'] else 2
            for name in day_names:
                names[name] += points
        
        # Calculate the start date (next Monday)
        today = datetime.now().date()
        days_to_monday = (0 - today.weekday()) % 7
        if days_to_monday == 0:  # If today is Monday
            start_date = today.isoformat()
        else:
            start_date = (today + timedelta(days=days_to_monday)).isoformat()
        
        # Сохраняем новое расписание с датами
        if saveCurrentSchedule(new_schedule, start_date):
            return jsonify({
                "status": "success", 
                "message": "Schedule saved successfully",
                "start_date": start_date,
                "end_date": (datetime.fromisoformat(start_date) + timedelta(days=6)).isoformat()
            }), 200
        else:
            return jsonify({"status": "error", "message": "Failed to save schedule"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        # Попытка генерации нового расписания
        new_schedule = getPlan(getNames())
        if new_schedule:
            return jsonify(new_schedule), 200
        else:
            # Если не удалось сгенерировать - создаем пустое расписание
            schedule = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
            today = datetime.now().date()
            days_to_monday = (0 - today.weekday()) % 7
            start_date = (today + timedelta(days=days_to_monday)).isoformat()
            result = {
                "schedule": schedule,
                "start_date": start_date,
                "end_date": (datetime.fromisoformat(start_date) + timedelta(days=6)).isoformat()
            }
            return jsonify(result), 200
    except Exception as e:
        logger.exception("Ошибка при генерации расписания")
        # Возвращаем конкретное сообщение об ошибке для отладки
        return jsonify({
            "status": "error", 
            "message": f"Ошибка при генерации расписания: {str(e)}"
        }), 500