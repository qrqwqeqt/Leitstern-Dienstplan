# scripts.py

import json
from datetime import datetime, timedelta
import random
import copy
import os
from .data import names

# Получаем абсолютный путь к директории приложения
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_SCHEDULE_FILE = os.path.join(BASE_DIR, 'current_schedule.json')
SPECIAL_USERS = {'Sofia S.', 'Alikhan'}

def getNames():
    return dict(names)

def getCurrentSchedule():
    try:
        if os.path.exists(CURRENT_SCHEDULE_FILE):
            with open(CURRENT_SCHEDULE_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "schedule" in data:
                    return data
                # Обработка случая, когда в файле неправильный формат
                return {
                    "schedule": {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
                    "start_date": datetime.now().date().isoformat(),
                    "end_date": (datetime.now().date() + timedelta(days=6)).isoformat()
                }
        # Если файл не существует, создаем пустое расписание
        empty_schedule = {
            "schedule": {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
            "start_date": datetime.now().date().isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=6)).isoformat()
        }
        # Создаем директорию, если не существует
        os.makedirs(os.path.dirname(CURRENT_SCHEDULE_FILE), exist_ok=True)
        with open(CURRENT_SCHEDULE_FILE, 'w') as f:
            json.dump(empty_schedule, f)
        return empty_schedule
    except Exception as e:
        print(f"Ошибка при чтении расписания: {e}")
        # Возвращаем пустое расписание при ошибке
        return {
            "schedule": {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
            "start_date": datetime.now().date().isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=6)).isoformat()
        }

def saveCurrentSchedule(schedule, start_date=None):
    try:
        # If no start_date is provided, use the current date
        if start_date is None:
            today = datetime.now().date()
            # If today is not Monday, find the next Monday
            if today.weekday() != 0:  # 0 = Monday
                days_until_monday = (7 - today.weekday()) % 7
                start_date = (today + timedelta(days=days_until_monday)).isoformat()
            else:
                start_date = today.isoformat()
        
        # Убедимся, что директория существует
        os.makedirs(os.path.dirname(CURRENT_SCHEDULE_FILE), exist_ok=True)
        
        # Проверим, является ли schedule уже словарем с schedule
        if isinstance(schedule, dict) and "schedule" in schedule:
            schedule_data = schedule
        else:
            # Add the start date and calculate end date (7 days later)
            schedule_data = {
                "schedule": schedule,
                "start_date": start_date,
                "end_date": (datetime.fromisoformat(start_date) + timedelta(days=6)).isoformat()
            }
        
        # Записываем данные в файл с ярким форматированием для удобства чтения
        with open(CURRENT_SCHEDULE_FILE, 'w') as f:
            json.dump(schedule_data, f, indent=2)
        print(f"Расписание успешно сохранено в {CURRENT_SCHEDULE_FILE}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении расписания: {e}")
        return False

def distribute_duties(name_list):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedule = {day: [] for day in days}
    
    # Создаём список людей и случайно перемешиваем
    people = list(name_list.keys()) if isinstance(name_list, dict) else list(name_list)
    random.shuffle(people)
    people_copy = people.copy()  # Сохраняем копию списка для дальнейшего использования
    
    # Распределяем выходные (Сб, Вс) – по 3 человека
    for day in ['Saturday', 'Sunday']:
        if len(people) >= 3:
            schedule[day] = [people.pop() for _ in range(3)]
        else:
            print(f"Недостаточно людей для выходного дня {day}")
            return None
    
    # Назначаем вторник (2 человека, исключая Софию и Алихана)
    tuesday_people = [p for p in people if p not in ["Sofia S.", "Alikhan"]]
    if len(tuesday_people) >= 2:
        # Выбираем 2 человека для вторника
        tuesday_assigned = [tuesday_people[i] for i in range(2)]
        schedule['Tuesday'] = tuesday_assigned
        # Удаляем выбранных людей из основного списка
        for p in tuesday_assigned:
            people.remove(p)
    else:
        print("Недостаточно людей для вторника (исключая специальных пользователей)")
        return None
    
    # Распределяем остальные будние дни (Пн, Ср, Чт, Пт) по 2 человека
    weekdays = ['Monday', 'Wednesday', 'Thursday', 'Friday']
    for day in weekdays:
        if len(people) >= 2:
            schedule[day] = [people.pop(), people.pop()]
        else:
            print(f"Недостаточно людей для буднего дня {day}")
            return None
    
    # Если остаются незадействованные люди, добавляем их в рабочие дни третьими
    for day in weekdays:
        if people:
            schedule[day].append(people.pop())
    
    # Проверяем, не стоят ли София и Алихан вместе
    for day in days:
        if "Sofia S." in schedule[day] and "Alikhan" in schedule[day]:
            # Ищем день, в котором можно заменить Алихана
            for swap_day in days:
                if swap_day != day and len(schedule[swap_day]) > 2:
                    for i, person in enumerate(schedule[swap_day]):
                        if person not in ["Sofia S.", "Alikhan"]:
                            # Находим индекс Алихана в текущем дне
                            alikhan_index = schedule[day].index("Alikhan")
                            # Меняем Алихана местами с найденным человеком
                            schedule[day][alikhan_index], schedule[swap_day][i] = schedule[swap_day][i], schedule[day][alikhan_index]
                            break
                    break
    
    return schedule

def getPlan(names_data=None, attempt=0):
    """
    Генерация нового расписания дежурств на неделю по упрощенному алгоритму
    names_data: словарь имен или список имен
    """
    try:
        # If no names data provided, get the current schedule first
        if attempt == 0:
            current_schedule = getCurrentSchedule()
            if current_schedule and names_data is None:
                return current_schedule
        
        # Initialize names_data if not provided
        if names_data is None:
            names_data = getNames()
        
        # Генерируем новое расписание
        schedule = distribute_duties(names_data)
        
        if not schedule:
            raise Exception("Не удалось сгенерировать расписание")
        
        # Calculate the start date based on the current date
        today = datetime.now().date()
        
        # Если сегодня понедельник, начинаем с сегодня, иначе берем следующий понедельник
        if today.weekday() == 0:  # 0 = Monday
            start_date = today.isoformat()
        else:
            # Находим следующий понедельник
            days_until_monday = (7 - today.weekday()) % 7
            start_date = (today + timedelta(days=days_until_monday)).isoformat()
        
        saveCurrentSchedule(schedule, start_date)
        
        result = {
            "schedule": schedule,
            "start_date": start_date,
            "end_date": (datetime.fromisoformat(start_date) + timedelta(days=6)).isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"Ошибка при генерации расписания: {str(e)}")
        raise Exception(f"Не удалось сгенерировать расписание: {str(e)}")
