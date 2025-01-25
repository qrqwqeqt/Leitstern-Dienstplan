import json
from datetime import datetime
from .data import names
import random
import copy


def getNames():
    return dict(names)

def addPoints(points_count, name):
    """Add points to a specific person's total"""
    if name in names:
        names[name] += points_count
        return True
    return False

def saveData():
    """Save current names data to a JSON file"""
    with open('app/data_backup.json', 'w') as f:
        json.dump(names, f)

def sortData():
    """Sort names by points in descending order"""
    return dict(sorted(names.items(), key=lambda x: x[1], reverse=True))

import itertools
from datetime import datetime


def getPlan(names_data=None):
    """
    Generate a weekly duty schedule considering point-based priority
    
    Priority rules:
    - Weekends: 3 people if possible (+3 points)
    - Weekdays (except Tuesday): 3 people if possible, else 2 (+2 points)
    - Tuesday: Lowest priority, 2 people, optional 3rd if extra people available
    """
    if names_data is None:
        names_data = names.copy()
    
    # Create a deep copy to avoid modifying original data
    names_copy = copy.deepcopy(names_data)
    
    # Sort people by current points (ascending)
    sorted_people = sorted(names_copy.items(), key=lambda x: x[1])
    
    # Prepare days of week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedule = {day: [] for day in days}
    
    # Helper to assign people
    def assign_people(day, count, priority_points):
        nonlocal sorted_people
        
        # Find available people not already scheduled
        available = [
            (name, points) for (name, points) in sorted_people 
            if name not in [person for day_schedule in schedule.values() for person in day_schedule]
        ]
        
        # Select top people based on lowest points
        selected = available[:count]
        
        # Update points and schedule
        for name, points in selected:
            names_copy[name] += priority_points
            schedule[day].append(name)
        
        # Recompute sorted people after updates
        sorted_people = sorted(names_copy.items(), key=lambda x: x[1])
        
        return selected
    
    # Weekend scheduling (Saturday, Sunday)
    assign_people('Saturday', 3, 3)
    assign_people('Sunday', 3, 3)
    
    # Weekday scheduling
    day_priorities = [
        ('Monday', 3, 2),
        ('Tuesday', 2, 2),  # Lowest priority
        ('Wednesday', 3, 2),
        ('Thursday', 3, 2),
        ('Friday', 3, 2)
    ]
    
    for day, ideal_count, points in day_priorities:
        # Try to assign ideal number of people
        remaining_people = len(sorted_people)
        count = min(ideal_count, remaining_people)
        assign_people(day, count, points)
    
    reordered_schedule = {
        day: schedule[day] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }
    return {
        'schedule': reordered_schedule
    }

def distributePoints():
    """Distribute points based on day of week"""
    today = datetime.now().weekday()
    
    # Weekends (5, 6 are Saturday, Sunday)
    if today in [5, 6]:
        for name in names:
            names[name] += 3
    else:
        # Weekdays
        for name in names:
            names[name] += 2
    
    return names