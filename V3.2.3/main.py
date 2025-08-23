# version 3.2.3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import psutil
import os
import subprocess
import platform
import pygame
import tempfile
import time
import requests
import re
import random
import cv2
import numpy as np
import pyaudio
import plyer
import websockets
import asyncio
import threading
import json
import pickle
import pyttsx3
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from queue import Queue
from ultralytics import YOLO

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Set to a male voice (0) or female voice (1)
engine.setProperty('rate', 150)  # Speed of speech

def speak(text: str):
    """Speak the given text using text-to-speech."""
    engine.say(text)
    engine.runAndWait()

from bs4 import BeautifulSoup
from gtts import gTTS
from dateutil import parser
from dateutil.relativedelta import relativedelta

# importing surveillance system:
from surv_sys import MultiSurveillanceSystem

# random sentences approach 1:
#RANDOM_SEN = []

# random sentences approach 2:
RANDOM_SEN = ["Hello there!", "How's it going?", "Nice weather today, isn't it?", "What's on your mind?"]

# =============================================================================
# EMOTIONAL INTELLIGENCE
# =============================================================================

# Emotional Intelligence keywords and responses
EMOTION_KEYWORDS = {
    'sad': ['sad', 'depressed', 'down', 'upset', 'crying', 'miserable', 'unhappy', 'heartbroken'],
    'happy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'awesome', 'joyful'],
    'angry': ['angry', 'mad', 'furious', 'frustrated', 'annoyed', 'irritated', 'rage'],
    'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'panic', 'overwhelmed', 'scared'],
    'tired': ['tired', 'exhausted', 'sleepy', 'weary', 'drained', 'fatigued'],
    'lonely': ['lonely', 'alone', 'isolated', 'abandoned', 'empty'],
    'confused': ['confused', 'lost', 'uncertain', 'puzzled', 'bewildered'],
    'grateful': ['grateful', 'thankful', 'blessed', 'appreciative']
}

EMOTIONAL_RESPONSES = {
    'sad': [
        "I'm sorry to hear you're feeling sad. Sometimes it helps to talk about what's bothering you. I'm here to listen.",
        "It sounds like you're going through a tough time. Remember that it's okay to feel sad sometimes. Would you like to talk about it?",
        "I can sense you're feeling down. Your feelings are valid. Is there anything specific that's making you feel this way?"
    ],
    'happy': [
        "That's wonderful! I'm so glad to hear you're feeling happy. Your positive energy is contagious!",
        "It makes me happy to know you're in such good spirits! What's been bringing you joy?",
        "Your happiness is beautiful! I love hearing when you're feeling great."
    ],
    'angry': [
        "I can hear that you're feeling frustrated. It's completely normal to feel angry sometimes. Take a deep breath with me.",
        "It sounds like something really upset you. Anger is a valid emotion. Would it help to talk through what happened?",
        "I understand you're feeling angry right now. Sometimes expressing these feelings can help. I'm here to listen without judgment."
    ],
    'anxious': [
        "I can sense you're feeling anxious. Remember to breathe slowly and deeply. You're not alone in this.",
        "Anxiety can be overwhelming, but you're stronger than you know. Let's take this one step at a time.",
        "I hear the worry in your voice. It's okay to feel anxious. Would some calming techniques or distractions help?"
    ],
    'tired': [
        "You sound exhausted. Rest is so important for your wellbeing. Have you been getting enough sleep?",
        "It seems like you're really tired. Sometimes our bodies and minds need time to recharge. Be gentle with yourself.",
        "I can hear the fatigue in your voice. Maybe it's time to take a break and focus on self-care?"
    ],
    'lonely': [
        "I'm sorry you're feeling lonely. Please remember that you're not truly alone - I'm here with you right now.",
        "Loneliness can be really difficult. Even though I'm an AI, I want you to know that you matter and you're valued.",
        "I hear that you're feeling isolated. Would you like to talk about what's making you feel this way? Sometimes connection can help."
    ],
    'confused': [
        "It's okay to feel confused sometimes. Life can be complicated. Would you like to talk through what's puzzling you?",
        "I can sense your uncertainty. Confusion is often a sign that we're processing something important. I'm here to help if you need clarity.",
        "Feeling lost or confused is part of being human. Take your time, and remember that clarity often comes with patience."
    ],
    'grateful': [
        "It's beautiful to hear gratitude in your voice. Appreciation is such a positive force in life.",
        "Your thankfulness is touching. Gratitude has a wonderful way of brightening both our own lives and others'.",
        "I love hearing when you're feeling grateful. It reminds me of all the good things in the world."
    ]
}

SUPPORTIVE_PHRASES = [
    "You're doing great, and I believe in you.",
    "Remember, every day is a new opportunity.",
    "You have overcome challenges before, and you can do it again.",
    "Your feelings are valid and important.",
    "I'm here for you whenever you need support.",
    "You're stronger than you realize.",
    "It's okay to take things one step at a time.",
    "You deserve kindness, especially from yourself."
]

# Function to detect emotion in text
def detect_emotion(text):
    text_lower = text.lower()
    detected_emotions = []
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_emotions.append(emotion)
                break
    
    return detected_emotions

# Function to provide emotional response
def provide_emotional_response(emotions):
    if not emotions:
        return None
    
    # Prioritize certain emotions (e.g., sad, anxious over happy)
    priority_emotions = ['sad', 'anxious', 'angry', 'lonely']
    
    for emotion in priority_emotions:
        if emotion in emotions:
            return random.choice(EMOTIONAL_RESPONSES[emotion])
    
    # If no priority emotions, respond to the first detected emotion
    emotion = emotions[0]
    return random.choice(EMOTIONAL_RESPONSES[emotion])

# Function to offer emotional support
def offer_support():
    support_options = [
        "Would you like me to play some calming music or sounds?",
        "Would you like to hear an inspirational quote?",
        "Would you like me to guide you through a brief breathing exercise?",
        "Would you like to talk about something positive or uplifting?",
        "Would you like me to suggest some self-care activities?"
    ]
    
    speak("I want to help you feel better. Here are some things I can do:")
    for i, option in enumerate(support_options, 1):
        speak(f"{i}. {option}")
    
    speak("Just tell me the number of what sounds helpful, or describe what you need.")

# Function for breathing exercise
def breathing_exercise():
    speak("Let's do a simple breathing exercise together. This will help you relax and center yourself.")
    speak("Just follow my guidance and breathe naturally.")
    
    for cycle in range(3):
        speak(f"Cycle {cycle + 1} of 3.")
        speak("Breathe in slowly through your nose for 4 counts. In... 2... 3... 4...")
        time.sleep(4)
        speak("Hold your breath for 4 counts. Hold... 2... 3... 4...")
        time.sleep(4)
        speak("Now breathe out slowly through your mouth for 6 counts. Out... 2... 3... 4... 5... 6...")
        time.sleep(6)
        
        if cycle < 2:
            time.sleep(1)
    
    speak("Great job! How are you feeling now? Remember, you can do this breathing exercise anytime you need to relax.")

# Function to share inspirational quote
# NOTE: This function can be modified with random quotes in the future:
def share_inspirational_quote():
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Life is what happens to you while you're busy making other plans. - John Lennon",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "The only impossible journey is the one you never begin. - Tony Robbins",
        "In the middle of difficulty lies opportunity. - Albert Einstein",
        "You are never too old to set another goal or to dream a new dream. - C.S. Lewis",
        "The way to get started is to quit talking and begin doing. - Walt Disney"
    ]
    
    quote = random.choice(quotes)
    speak(f"Here's an inspirational quote for you: {quote}")

# Function to suggest self-care activities
def suggest_self_care():
    activities = [
        "Take a warm bath or shower",
        "Go for a walk in nature",
        "Listen to your favorite music",
        "Call a friend or family member",
        "Write in a journal about your thoughts and feelings",
        "Practice meditation or mindfulness",
        "Do some gentle stretching or yoga",
        "Read a good book",
        "Cook or bake something you enjoy",
        "Watch a funny movie or TV show"
    ]
    
    speak("Here are some self-care activities that might help you feel better:")
    selected_activities = random.sample(activities, 5)
    
    for i, activity in enumerate(selected_activities, 1):
        speak(f"{i}. {activity}")
    
    speak("Choose something that feels right for you in this moment. Self-care is so important!")

# =============================================================================
# ROUTINE PLANNING MODE
# =============================================================================

# ROUTINES SYSTEM - NEW FUNCTIONALITY
class RoutineManager:
    def __init__(self):
        self.routines_file = "trinity_routines.json"
        self.active_routines = {}
        self.routine_timers = {}
        self.load_routines()
        self.start_routine_checker()
    
    def load_routines(self):
        """Load routines from JSON file"""
        try:
            if os.path.exists(self.routines_file):
                with open(self.routines_file, 'r') as f:
                    self.active_routines = json.load(f)
                speak(f"Loaded {len(self.active_routines)} existing routines.")
            else:
                self.active_routines = {}
        except Exception as e:
            speak("Error loading routines file. Starting with empty routines.")
            self.active_routines = {}
    
    def save_routines(self):
        """Save routines to JSON file"""
        try:
            with open(self.routines_file, 'w') as f:
                json.dump(self.active_routines, f, indent=2)
        except Exception as e:
            speak("Error saving routines file.")
    
    def create_routine(self):
        """Create a new routine interactively"""
        speak("Let's create a new routine. What would you like to call this routine?")
        routine_name = listen()
        
        if not routine_name:
            speak("I didn't catch the routine name. Please try again.")
            return
        
        speak(f"Great! What should the routine remind you to do?")
        routine_message = listen()
        
        if not routine_message:
            speak("I didn't catch the reminder message. Please try again.")
            return
        
        speak("What time should I remind you? Please say the hour first, then minutes. For example, say 'nine thirty PM' or 'fourteen fifteen' for 24-hour format.")
        time_input = listen()
        
        if not time_input:
            speak("I didn't catch the time. Please try again.")
            return
        
        # Parse the time
        parsed_time = self.parse_time(time_input)
        if not parsed_time:
            speak("I couldn't understand that time format. Please try again with a different format.")
            return
        
        speak("How often should this routine repeat? Say 'daily', 'weekly', or 'once'.")
        frequency = listen()
        
        if frequency not in ['daily', 'weekly', 'once']:
            frequency = 'daily'  # Default to daily
            speak("I'll set this as a daily routine.")
        
        # Create the routine
        routine_id = f"{routine_name}_{int(time.time())}"
        routine_data = {
            'name': routine_name,
            'message': routine_message,
            'time': parsed_time,
            'frequency': frequency,
            'active': True,
            'created': datetime.datetime.now().isoformat()
        }
        
        self.active_routines[routine_id] = routine_data
        self.save_routines()
        
        speak(f"Routine '{routine_name}' created successfully! I'll remind you to {routine_message} at {parsed_time} {frequency}.")
    
    def parse_time(self, time_input):
        """Parse various time formats"""
        time_input = time_input.lower().replace(':', ' ')
        
        # Handle AM/PM format
        if 'pm' in time_input or 'am' in time_input:
            try:
                # Remove pm/am and clean up
                time_str = time_input.replace('pm', '').replace('am', '').strip()
                
                # Handle common spoken formats
                time_str = time_str.replace('thirty', '30').replace('fifteen', '15').replace('forty five', '45')
                time_str = time_str.replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4')
                time_str = time_str.replace('five', '5').replace('six', '6').replace('seven', '7').replace('eight', '8')
                time_str = time_str.replace('nine', '9').replace('ten', '10').replace('eleven', '11').replace('twelve', '12')
                
                parts = time_str.split()
                hour = int(parts[0])
                minute = 0 if len(parts) == 1 else int(parts[1])
                
                if 'pm' in time_input and hour != 12:
                    hour += 12
                elif 'am' in time_input and hour == 12:
                    hour = 0
                
                return f"{hour:02d}:{minute:02d}"
                
            except (ValueError, IndexError):
                return None
        
        # Handle 24-hour format
        try:
            time_str = time_input.replace('fifteen', '15').replace('thirty', '30').replace('forty five', '45')
            time_str = time_str.replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4')
            time_str = time_str.replace('five', '5').replace('six', '6').replace('seven', '7').replace('eight', '8')
            time_str = time_str.replace('nine', '9').replace('ten', '10').replace('eleven', '11').replace('twelve', '12')
            time_str = time_str.replace('thirteen', '13').replace('fourteen', '14').replace('sixteen', '16')
            time_str = time_str.replace('seventeen', '17').replace('eighteen', '18').replace('nineteen', '19')
            time_str = time_str.replace('twenty', '20').replace('twenty one', '21').replace('twenty two', '22')
            time_str = time_str.replace('twenty three', '23')
            
            parts = time_str.split()
            hour = int(parts[0])
            minute = 0 if len(parts) == 1 else int(parts[1])
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
                
        except (ValueError, IndexError):
            pass
        
        return None
    
    def list_routines(self):
        """List all active routines"""
        if not self.active_routines:
            speak("You don't have any routines set up yet.")
            return
        
        speak(f"You have {len(self.active_routines)} routines:")
        for routine_id, routine in self.active_routines.items():
            status = "active" if routine['active'] else "inactive"
            speak(f"Routine '{routine['name']}': {routine['message']} at {routine['time']} {routine['frequency']}. Status: {status}")
    
    def delete_routine(self):
        """Delete a routine"""
        if not self.active_routines:
            speak("You don't have any routines to delete.")
            return
        
        speak("Which routine would you like to delete? Please say the routine name.")
        routine_to_delete = listen()
        
        if not routine_to_delete:
            speak("I didn't catch the routine name.")
            return
        
        # Find routine by name
        found_routine = None
        for routine_id, routine in self.active_routines.items():
            if routine_to_delete.lower() in routine['name'].lower():
                found_routine = routine_id
                break
        
        if found_routine:
            routine_name = self.active_routines[found_routine]['name']
            del self.active_routines[found_routine]
            
            # Cancel timer if exists
            if found_routine in self.routine_timers:
                self.routine_timers[found_routine].cancel()
                del self.routine_timers[found_routine]
            
            self.save_routines()
            speak(f"Routine '{routine_name}' has been deleted.")
        else:
            speak("I couldn't find a routine with that name.")
    
    def start_routine_checker(self):
        """Start the background routine checker"""
        def check_routines():
            current_time = datetime.datetime.now().strftime("%H:%M")
            current_day = datetime.datetime.now().weekday()  # 0 = Monday, 6 = Sunday
            
            for routine_id, routine in self.active_routines.items():
                if routine['active'] and routine['time'] == current_time:
                    # Check if it's time to trigger
                    should_trigger = False
                    
                    if routine['frequency'] == 'daily':
                        should_trigger = True
                    elif routine['frequency'] == 'weekly':
                        # Trigger once per week (same day as created)
                        created_day = datetime.datetime.fromisoformat(routine['created']).weekday()
                        should_trigger = (current_day == created_day)
                    elif routine['frequency'] == 'once':
                        should_trigger = True
                        # Deactivate after triggering once
                        routine['active'] = False
                        self.save_routines()
                    
                    if should_trigger:
                        self.trigger_routine(routine)
            
            # Schedule next check in 60 seconds
            threading.Timer(60.0, check_routines).start()
        
        # Start the checker
        check_routines()
    
    def trigger_routine(self, routine):
        """Trigger a routine reminder"""
        reminder_message = f"Routine reminder: {routine['message']}"
        speak(reminder_message)
        
        # Also create a visual notification if possible
        try:
            if platform.system() == "Windows":
                import win11toast
                toaster = win11toast.ToastNotifier()
                toaster.show_toast("Trinity Routine Reminder", routine['message'], duration=10)
        except:
            pass  # Visual notification failed, but audio worked

routine_manager = RoutineManager()

# =============================================================================
# SCHEDULER
# =============================================================================

# Scheduler-related imports
SCHEDULE_FILE = "trinity_schedule.json"
REMINDER_CHECK_INTERVAL = 30  # Check for reminders every 30 seconds

# Global variables for scheduling
schedule_data = {}
reminder_thread = None
scheduler_active = False

# Load existing schedule data
def load_schedule():
    global schedule_data
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                schedule_data = json.load(f)
                # Convert string dates back to datetime objects for processing
                for event_id, event in schedule_data.items():
                    if isinstance(event['datetime'], str):
                        event['datetime'] = datetime.datetime.fromisoformat(event['datetime'])
    except Exception as e:
        print(f"Error loading schedule: {e}")
        schedule_data = {}

# Save schedule data
def save_schedule():
    try:
        # Convert datetime objects to strings for JSON serialization
        save_data = {}
        for event_id, event in schedule_data.items():
            save_data[event_id] = event.copy()
            if isinstance(event['datetime'], datetime.datetime):
                save_data[event_id]['datetime'] = event['datetime'].isoformat()
        
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(save_data, f, indent=2)
    except Exception as e:
        print(f"Error saving schedule: {e}")

# Parse natural language time/date input
def parse_datetime_input(time_str):
    """Parse natural language datetime input"""
    try:
        # Handle relative times
        now = datetime.datetime.now()
        time_str = time_str.lower().strip()
        
        # Handle "in X minutes/hours/days"
        if time_str.startswith("in "):
            parts = time_str[3:].split()
            if len(parts) >= 2:
                try:
                    amount = int(parts[0])
                    unit = parts[1].lower()
                    
                    if "minute" in unit:
                        return now + datetime.timedelta(minutes=amount)
                    elif "hour" in unit:
                        return now + datetime.timedelta(hours=amount)
                    elif "day" in unit:
                        return now + datetime.timedelta(days=amount)
                    elif "week" in unit:
                        return now + datetime.timedelta(weeks=amount)
                    elif "month" in unit:
                        return now + relativedelta(months=amount)
                except:
                    pass
        
        # Handle "tomorrow at X"
        if "tomorrow" in time_str:
            tomorrow = now + datetime.timedelta(days=1)
            if "at" in time_str:
                time_part = time_str.split("at")[1].strip()
                try:
                    time_obj = parser.parse(time_part).time()
                    return datetime.datetime.combine(tomorrow.date(), time_obj)
                except:
                    return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Handle "today at X"
        if "today" in time_str and "at" in time_str:
            time_part = time_str.split("at")[1].strip()
            try:
                time_obj = parser.parse(time_part).time()
                return datetime.datetime.combine(now.date(), time_obj)
            except:
                pass
        
        # Handle "next Monday", "next Tuesday", etc.
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(weekdays):
            if f"next {day}" in time_str:
                days_ahead = i - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                target_date = now + datetime.timedelta(days=days_ahead)
                if "at" in time_str:
                    time_part = time_str.split("at")[1].strip()
                    try:
                        time_obj = parser.parse(time_part).time()
                        return datetime.datetime.combine(target_date.date(), time_obj)
                    except:
                        pass
                return target_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Try to parse with dateutil parser
        parsed_dt = parser.parse(time_str, fuzzy=True)
        
        # If the parsed date is in the past, assume it's for tomorrow or next occurrence
        if parsed_dt < now:
            if parsed_dt.date() == now.date():
                # Same day but past time, assume tomorrow
                parsed_dt = parsed_dt + datetime.timedelta(days=1)
            elif parsed_dt.year == now.year and parsed_dt.month == now.month:
                # Same month, might need to adjust to next month
                parsed_dt = parsed_dt + relativedelta(months=1)
        
        return parsed_dt
        
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return None

# Create a new event/reminder
def create_event(title, datetime_obj, description="", reminder_minutes=15):
    event_id = str(int(time.time() * 1000))  # Unique timestamp-based ID
    
    event = {
        'id': event_id,
        'title': title,
        'description': description,
        'datetime': datetime_obj,
        'reminder_minutes': reminder_minutes,
        'notified': False,
        'completed': False,
        'created_at': datetime.datetime.now()
    }
    
    schedule_data[event_id] = event
    save_schedule()
    return event_id

# List upcoming events
def list_upcoming_events(days_ahead=7):
    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(days=days_ahead)
    
    upcoming = []
    for event in schedule_data.values():
        if (not event['completed'] and 
            now <= event['datetime'] <= end_date):
            upcoming.append(event)
    
    # Sort by datetime
    upcoming.sort(key=lambda x: x['datetime'])
    return upcoming

# Check for due reminders
def check_reminders():
    now = datetime.datetime.now()
    
    for event in schedule_data.values():
        if (not event['notified'] and 
            not event['completed'] and 
            event['datetime'] > now):
            
            # Check if reminder time has arrived
            reminder_time = event['datetime'] - datetime.timedelta(minutes=event['reminder_minutes'])
            
            if now >= reminder_time:
                # Trigger reminder
                reminder_text = f"Reminder: {event['title']} is scheduled for {event['datetime'].strftime('%I:%M %p on %B %d')}"
                if event['description']:
                    reminder_text += f". Description: {event['description']}"
                
                speak(reminder_text)
                event['notified'] = True
                save_schedule()

# Background reminder checker
def reminder_checker():
    global scheduler_active
    while scheduler_active:
        check_reminders()
        time.sleep(REMINDER_CHECK_INTERVAL)

# Start the reminder system
def start_reminder_system():
    global reminder_thread, scheduler_active
    if not scheduler_active:
        scheduler_active = True
        reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
        reminder_thread.start()
        speak("Reminder system activated.")

# Stop the reminder system
def stop_reminder_system():
    global scheduler_active
    scheduler_active = False
    speak("Reminder system deactivated.")

# Scheduling command handlers
def handle_create_schedule():
    speak("What would you like to schedule?")
    title = listen()
    if not title:
        speak("I didn't catch the event title. Please try again.")
        return
    
    speak("When would you like to schedule this? You can say things like 'tomorrow at 3 PM', 'in 2 hours', or 'next Monday at 9 AM'")
    time_input = listen()
    if not time_input:
        speak("I didn't catch the time. Please try again.")
        return
    
    datetime_obj = parse_datetime_input(time_input)
    if not datetime_obj:
        speak("I couldn't understand the date and time. Please try again with a different format.")
        return
    
    speak("Would you like to add a description? Say 'no' if you don't want one.")
    desc_input = listen()
    description = "" if not desc_input or "no" in desc_input else desc_input
    
    speak("How many minutes before the event would you like to be reminded? Say a number, or 'default' for 15 minutes.")
    reminder_input = listen()
    reminder_minutes = 15  # default
    
    if reminder_input and reminder_input.isdigit():
        reminder_minutes = int(reminder_input)
    elif reminder_input and any(word in reminder_input for word in ["hour", "hours"]):
        try:
            hours = int(''.join(filter(str.isdigit, reminder_input)))
            reminder_minutes = hours * 60
        except:
            reminder_minutes = 15
    
    event_id = create_event(title, datetime_obj, description, reminder_minutes)
    
    formatted_datetime = datetime_obj.strftime("%I:%M %p on %B %d, %Y")
    speak(f"Event '{title}' scheduled for {formatted_datetime} with a {reminder_minutes}-minute reminder.")

def handle_list_schedule():
    speak("How many days ahead would you like to see? Say a number or 'all' for everything.")
    days_input = listen()
    
    days_ahead = 7  # default
    if days_input:
        if "all" in days_input:
            days_ahead = 365  # Show everything for the next year
        else:
            try:
                days_ahead = int(''.join(filter(str.isdigit, days_input)))
            except:
                days_ahead = 7
    
    upcoming = list_upcoming_events(days_ahead)
    
    if not upcoming:
        speak("You have no upcoming events scheduled.")
        return
    
    speak(f"You have {len(upcoming)} upcoming events:")
    for i, event in enumerate(upcoming[:10], 1):  # Limit to 10 events for voice output
        formatted_datetime = event['datetime'].strftime("%I:%M %p on %B %d")
        event_text = f"{i}. {event['title']} scheduled for {formatted_datetime}"
        if event['description']:
            event_text += f". {event['description']}"
        speak(event_text)
        
        if i >= 5:  # After 5 events, ask if they want to continue
            speak("Would you like to hear more events?")
            response = listen()
            if not response or "no" in response:
                break

def handle_delete_event():
    upcoming = list_upcoming_events(30)  # Next 30 days
    
    if not upcoming:
        speak("You have no upcoming events to delete.")
        return
    
    speak("Here are your upcoming events. Which one would you like to delete?")
    for i, event in enumerate(upcoming[:10], 1):
        formatted_datetime = event['datetime'].strftime("%I:%M %p on %B %d")
        speak(f"{i}. {event['title']} on {formatted_datetime}")
    
    speak("Say the number of the event you want to delete.")
    choice = listen()
    
    try:
        choice_num = int(''.join(filter(str.isdigit, choice)))
        if 1 <= choice_num <= len(upcoming):
            event_to_delete = upcoming[choice_num - 1]
            event_to_delete['completed'] = True  # Mark as completed instead of deleting
            save_schedule()
            speak(f"Event '{event_to_delete['title']}' has been deleted.")
        else:
            speak("Invalid choice. Please try again.")
    except:
        speak("I didn't understand the number. Please try again.")


