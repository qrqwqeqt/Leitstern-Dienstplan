# scripts.py

import json
from datetime import datetime
import random
import copy
import os
from .data import names

CURRENT_SCHEDULE_FILE = 'app/current_schedule.json'
SPECIAL_USERS = {'Sofia S.', 'Alihan'}
MAX_ATTEMPTS = 100  # Максимальное количество попыток генерации

def getNames():
    return dict(names)

def getCurrentSchedule():
    try:
        if os.path.exists(CURRENT_SCHEDULE_FILE):
            with open(CURRENT_SCHEDULE_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Ошибка при чтении расписания: {e}")
        return None

def saveCurrentSchedule(schedule):
    try:
        with open(CURRENT_SCHEDULE_FILE, 'w') as f:
            json.dump(schedule, f)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении расписания: {e}")
        return False

def get_available_users(used_users, all_users, require_three=False):
    available = [user for user in all_users if user not in used_users]
    if not require_three:
        available = [user for user in available if user not in SPECIAL_USERS]
    return available

def assign_users_to_day(day, count, available_users, used_users):
    if not available_users:
        return []
        
    day_schedule = []
    temp_available = available_users.copy()
    special_user_added = False
    
    while len(day_schedule) < count and temp_available:
        if not temp_available:  # Дополнительная проверка
            break
            
        user = random.choice(temp_available)
        is_special = user in SPECIAL_USERS
        
        if (not is_special) or (count == 3 and not special_user_added):
            day_schedule.append(user)
            used_users.add(user)
            if is_special:
                special_user_added = True
        
        temp_available.remove(user)
    
    return day_schedule

def getPlan(names_data=None, attempt=0):
    """
    Генерация нового расписания дежурств на неделю
    attempt: текущая попытка генерации
    """
    if attempt >= MAX_ATTEMPTS:
        raise Exception("Превышено максимальное количество попыток генерации расписания")
        
    try:
        current_schedule = getCurrentSchedule()
        if current_schedule and names_data is None:
            return {'schedule': current_schedule}
        
        if names_data is None:
            names_data = list(names.keys())
        else:
            names_data = list(names_data.keys())
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule = {day: [] for day in days}
        used_users = set()
        
        # Выходные (по 3 человека)
        for weekend_day in ['Saturday', 'Sunday']:
            available_users = get_available_users(used_users, names_data, require_three=True)
            if len(available_users) < 3:
                return getPlan(names_data, attempt + 1)
            weekend_schedule = assign_users_to_day(weekend_day, 3, available_users, used_users)
            if len(weekend_schedule) < 3:
                return getPlan(names_data, attempt + 1)
            schedule[weekend_day] = weekend_schedule
        
        # Вторник (2 человека)
        available_users = get_available_users(used_users, names_data, require_three=False)
        if len(available_users) < 2:
            return getPlan(names_data, attempt + 1)
        tuesday_schedule = assign_users_to_day('Tuesday', 2, available_users, used_users)
        if len(tuesday_schedule) < 2:
            return getPlan(names_data, attempt + 1)
        schedule['Tuesday'] = tuesday_schedule
        
        # Остальные будние дни
        weekdays = ['Monday', 'Wednesday', 'Thursday', 'Friday']
        random.shuffle(weekdays)
        
        for day in weekdays:
            available_users = get_available_users(used_users, names_data, require_three=True)
            target_count = 3 if len(available_users) >= 3 else 2
            if len(available_users) < 2:
                return getPlan(names_data, attempt + 1)
            day_schedule = assign_users_to_day(day, target_count, available_users, used_users)
            if len(day_schedule) < 2:
                return getPlan(names_data, attempt + 1)
            schedule[day] = day_schedule
        
        saveCurrentSchedule(schedule)
        return {'schedule': schedule}
        
    except Exception as e:
        if attempt < MAX_ATTEMPTS:
            return getPlan(names_data, attempt + 1)
        raise Exception(f"Ошибка генерации расписания: {str(e)}")