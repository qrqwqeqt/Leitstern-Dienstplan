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
        logger.info(f"Получены данные для обновления расписания: {data}")
        
        if not data:
            return jsonify({"status": "error", "message": "Отсутствуют данные для обновления"}), 400
            
        # Получаем текущее расписание для сохранения его дат
        current_schedule = getCurrentSchedule()
        
        if isinstance(data, dict) and "schedule" in data:
            new_schedule = data["schedule"]
        else:
            new_schedule = data
        
        # Проверяем, что new_schedule содержит все дни недели
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_of_week:
            if day not in new_schedule:
                new_schedule[day] = []
        
        # Сбрасываем все баллы
        for name in names:
            names[name] = 0
        
        # Распределяем баллы на основе нового расписания
        for day, day_names in new_schedule.items():
            points = 3 if day in ['Saturday', 'Sunday'] else 2
            for name in day_names:
                if name in names:  # Проверяем, есть ли имя в словаре
                    names[name] += points
        
        # Определяем, какую дату использовать
        if current_schedule and "start_date" in current_schedule:
            start_date = current_schedule["start_date"]
            # Проверяем, не истёк ли период текущего расписания
            current_end_date = current_schedule.get("end_date")
            if current_end_date:
                # Если сегодня позже конечной даты текущего расписания, 
                # то переходим на следующую неделю
                today = datetime.now().date()
                if datetime.fromisoformat(current_end_date).date() < today:
                    # Найти следующий понедельник
                    days_until_monday = (7 - today.weekday()) % 7
                    if days_until_monday == 0:  # сегодня понедельник
                        start_date = today.isoformat()
                    else:
                        start_date = (today + timedelta(days=days_until_monday)).isoformat()
        else:
            # Если нет текущего расписания, используем следующий понедельник
            today = datetime.now().date()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:  # сегодня понедельник
                start_date = today.isoformat()
            else:
                start_date = (today + timedelta(days=days_until_monday)).isoformat()
        
        logger.info(f"Сохраняем расписание: {new_schedule} с начальной датой {start_date}")
        
        # Сохраняем новое расписание с датами
        if saveCurrentSchedule(new_schedule, start_date):
            logger.info("Расписание успешно сохранено")
            end_date = (datetime.fromisoformat(start_date) + timedelta(days=6)).isoformat()
            return jsonify({
                "status": "success", 
                "message": "Schedule saved successfully",
                "start_date": start_date,
                "end_date": end_date
            }), 200
        else:
            logger.error("Не удалось сохранить расписание")
            return jsonify({"status": "error", "message": "Failed to save schedule"}), 500
            
    except Exception as e:
        logger.exception(f"Ошибка при обновлении расписания: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
    
@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        # Попытка генерации нового расписания
        names_dict = getNames()
        
        # Log names for debugging
        logger.info(f"Generating schedule with names: {list(names_dict.keys())}")
        
        new_schedule = getPlan(names_dict)
        
        if new_schedule:
            logger.info(f"Schedule generated successfully: {new_schedule}")
            return jsonify(new_schedule), 200
        else:
            # If schedule is empty, return error
            logger.error("Generated schedule is empty")
            return jsonify({
                "status": "error", 
                "message": "Не удалось сгенерировать расписание"
            }), 500
    except Exception as e:
        logger.exception(f"Ошибка при генерации расписания: {str(e)}")
        # Return detailed error message
        return jsonify({
            "status": "error", 
            "message": f"Ошибка при генерации расписания: {str(e)}"
        }), 500