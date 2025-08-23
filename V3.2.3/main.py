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

# =============================================================================
# NEWS UPDATE
# =============================================================================

# News API configuration (you'll need to get a free API key from newsapi.org)
NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"  # Replace with your actual API key
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# Function to get news from NewsAPI
def get_news_from_api(category=None, country='us', num_articles=5):
    """
    Get news from NewsAPI
    category: business, entertainment, general, health, science, sports, technology
    country: us, gb, ca, au, etc.
    """
    try:
        params = {
            'apiKey': NEWS_API_KEY,
            'country': country,
            'pageSize': num_articles
        }
        
        if category:
            params['category'] = category
            
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ok' and data['articles']:
                return data['articles']
        return None
    except Exception as e:
        print(f"News API error: {e}")
        return None

# Fallback function to scrape news from BBC (if NewsAPI fails)
def get_news_fallback():
    """
    Fallback method to get news by scraping BBC News
    """
    try:
        response = requests.get('https://www.bbc.com/news', timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find news headlines
        headlines = []
        
        # BBC News structure (may need adjustment if BBC changes their layout)
        news_items = soup.find_all('h3', class_=re.compile('gs-c-promo-heading__title'))
        
        for item in news_items[:5]:  # Get top 5 headlines
            headline_text = item.get_text().strip()
            if headline_text and len(headline_text) > 10:  # Filter out very short text
                headlines.append(headline_text)
        
        # If the above doesn't work, try a more general approach
        if not headlines:
            all_headlines = soup.find_all(['h1', 'h2', 'h3'])
            for h in all_headlines[:10]:
                text = h.get_text().strip()
                if len(text) > 20 and len(text) < 200:  # Reasonable headline length
                    headlines.append(text)
                    if len(headlines) >= 5:
                        break
        
        return headlines[:5] if headlines else None
        
    except Exception as e:
        print(f"Fallback news scraping error: {e}")
        return None

# Function to deliver news
def get_news(category=None, morning_briefing=False):
    """
    Get and speak news headlines
    """
    if morning_briefing:
        speak("Good morning! Here's your morning news briefing.")
    else:
        speak("Fetching the latest news for you...")
    
    # Try NewsAPI first (if API key is configured)
    articles = None
    if NEWS_API_KEY != "YOUR_NEWS_API_KEY_HERE":
        articles = get_news_from_api(category=category)
    
    # If NewsAPI fails or isn't configured, use fallback
    if not articles:
        speak("Using alternative news source...")
        headlines = get_news_fallback()
        
        if headlines:
            speak("Here are the top headlines:")
            for i, headline in enumerate(headlines, 1):
                speak(f"Headline {i}: {headline}")
            
            # Ask if user wants to open BBC News
            if not morning_briefing:
                speak("Would you like me to open BBC News for more details?")
                response = listen()
                if response and any(word in response for word in ['yes', 'sure', 'okay', 'open']):
                    webbrowser.open('https://www.bbc.com/news')
        else:
            speak("Sorry, I couldn't fetch the news at the moment. Let me open Google News for you.")
            webbrowser.open('https://news.google.com')
        return
    
    # Process NewsAPI results
    speak("Here are the top headlines:")
    for i, article in enumerate(articles[:5], 1):
        title = article.get('title', 'No title')
        # Clean up the title (remove source info that sometimes appears)
        if ' - ' in title:
            title = title.split(' - ')[0]
        speak(f"Headline {i}: {title}")
    
    # Ask if user wants more details (only if not morning briefing)
    if not morning_briefing:
        speak("Would you like me to open the full articles or get news from a specific category?")
        response = listen()
        if response:
            if any(word in response for word in ['yes', 'sure', 'okay', 'open', 'full']):
                # Open first few article URLs
                for article in articles[:3]:
                    if article.get('url'):
                        webbrowser.open(article['url'])
                        time.sleep(1)  # Small delay between opening tabs
            elif any(word in response for word in ['category', 'specific', 'business', 'sports', 'technology', 'health', 'entertainment']):
                speak("Which category would you like? You can choose from business, entertainment, health, science, sports, or technology.")
                category_response = listen()
                if category_response:
                    # Extract category from response
                    categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
                    for cat in categories:
                        if cat in category_response:
                            get_news(category=cat)
                            return

# Function to check if it's morning and deliver briefing
def check_morning_briefing():
    """
    Check if it's morning (6 AM - 10 AM) and offer news briefing
    """
    current_hour = datetime.datetime.now().hour
    
    # Morning hours: 6 AM to 10 AM
    if 6 <= current_hour <= 10:
        speak("It's morning! Would you like your daily news briefing?")
        response = listen()
        if response and any(word in response for word in ['yes', 'sure', 'okay', 'briefing']):
            get_news(morning_briefing=True)
            return True
    return False

# =============================================================================
# REINFORCEMENT LEARNING
# =============================================================================

# Data structures for learning
@dataclass
class UserInteraction:
    timestamp: str
    command: str
    response_type: str
    user_feedback: float  # -1 (negative), 0 (neutral), 1 (positive)
    context: Dict[str, Any]
    success: bool

@dataclass
class UserPreference:
    preference_type: str
    value: Any
    confidence: float
    last_updated: str

class ReinforcementLearningEngine:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        
        # Q-table for state-action values
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # User interaction history
        self.interaction_history = deque(maxlen=1000)
        
        # User preferences
        self.user_preferences = {}
        
        # Response patterns and their success rates
        self.response_patterns = defaultdict(list)
        
        # Learning data file paths
        self.data_dir = "trinity_learning_data"
        self.q_table_file = os.path.join(self.data_dir, "q_table.pkl")
        self.preferences_file = os.path.join(self.data_dir, "user_preferences.json")
        self.history_file = os.path.join(self.data_dir, "interaction_history.pkl")
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data
        self.load_learning_data()
    
    def save_learning_data(self):
        """Save all learning data to files"""
        try:
            # Save Q-table
            with open(self.q_table_file, 'wb') as f:
                pickle.dump(dict(self.q_table), f)
            
            # Save preferences
            preferences_data = {k: asdict(v) for k, v in self.user_preferences.items()}
            with open(self.preferences_file, 'w') as f:
                json.dump(preferences_data, f, indent=2)
            
            # Save interaction history
            with open(self.history_file, 'wb') as f:
                pickle.dump(list(self.interaction_history), f)
                
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def load_learning_data(self):
        """Load existing learning data from files"""
        try:
            # Load Q-table
            if os.path.exists(self.q_table_file):
                with open(self.q_table_file, 'rb') as f:
                    loaded_q_table = pickle.load(f)
                    self.q_table = defaultdict(lambda: defaultdict(float), loaded_q_table)
            
            # Load preferences
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    preferences_data = json.load(f)
                    for k, v in preferences_data.items():
                        self.user_preferences[k] = UserPreference(**v)
            
            # Load interaction history
            if os.path.exists(self.history_file):
                with open(self.history_file, 'rb') as f:
                    history_data = pickle.load(f)
                    self.interaction_history = deque(history_data, maxlen=1000)
                    
        except Exception as e:
            print(f"Error loading learning data: {e}")
    
    def get_state_representation(self, command, context):
        """Convert command and context into a state representation"""
        # Extract key features from command
        command_words = command.lower().split()
        command_type = self.classify_command_type(command)
        
        # Time-based features
        current_hour = datetime.datetime.now().hour
        time_of_day = "morning" if current_hour < 12 else "afternoon" if current_hour < 18 else "evening"
        
        # Context features
        recent_commands = [interaction.command for interaction in list(self.interaction_history)[-5:]]
        
        state = f"{command_type}_{time_of_day}_{len(command_words)}"
        return state
    
    def classify_command_type(self, command):
        """Classify the type of command"""
        command = command.lower()
        
        if any(word in command for word in ["open", "launch", "start"]):
            return "open_action"
        elif any(word in command for word in ["search", "find", "look"]):
            return "search_action"
        elif any(word in command for word in ["time", "date", "weather"]):
            return "info_query"
        elif any(word in command for word in ["system", "check", "status"]):
            return "system_action"
        elif any(word in command for word in ["hello", "hi", "hey"]):
            return "greeting"
        else:
            return "other"
    
    def choose_action(self, state, available_actions):
        """Choose action using epsilon-greedy strategy"""
        if np.random.random() < self.exploration_rate:
            # Explore: choose random action
            return np.random.choice(available_actions)
        else:
            # Exploit: choose best known action
            q_values = [self.q_table[state][action] for action in available_actions]
            best_action_idx = np.argmax(q_values)
            return available_actions[best_action_idx]
    
    def update_q_value(self, state, action, reward, next_state, next_actions):
        """Update Q-value using Q-learning algorithm"""
        current_q = self.q_table[state][action]
        
        if next_actions:
            max_next_q = max([self.q_table[next_state][next_action] for next_action in next_actions])
        else:
            max_next_q = 0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def record_interaction(self, command, response_type, user_feedback, context, success):
        """Record user interaction for learning"""
        interaction = UserInteraction(
            timestamp=datetime.datetime.now().isoformat(),
            command=command,
            response_type=response_type,
            user_feedback=user_feedback,
            context=context,
            success=success
        )
        
        self.interaction_history.append(interaction)
        
        # Update Q-values based on feedback
        state = self.get_state_representation(command, context)
        reward = user_feedback
        
        # Simple reward shaping
        if success:
            reward += 0.5
        
        self.update_q_value(state, response_type, reward, state, [response_type])
        
        # Update user preferences
        self.update_preferences(command, response_type, user_feedback)
        
        # Save data periodically
        if len(self.interaction_history) % 10 == 0:
            self.save_learning_data()
    
    def update_preferences(self, command, response_type, feedback):
        """Update user preferences based on feedback"""
        command_type = self.classify_command_type(command)
        
        preference_key = f"{command_type}_preference"
        
        if preference_key in self.user_preferences:
            # Update existing preference
            pref = self.user_preferences[preference_key]
            pref.confidence = pref.confidence * 0.9 + feedback * 0.1
            pref.last_updated = datetime.datetime.now().isoformat()
        else:
            # Create new preference
            self.user_preferences[preference_key] = UserPreference(
                preference_type=command_type,
                value=response_type,
                confidence=feedback,
                last_updated=datetime.datetime.now().isoformat()
            )
    
    def get_personalized_response(self, command, context):
        """Get personalized response based on learned preferences"""
        command_type = self.classify_command_type(command)
        preference_key = f"{command_type}_preference"
        
        if preference_key in self.user_preferences:
            pref = self.user_preferences[preference_key]
            if pref.confidence > 0.5:
                return f"personalized_{pref.value}"
        
        return "default"
    
    def get_learning_summary(self):
        """Get summary of learning progress"""
        total_interactions = len(self.interaction_history)
        positive_feedback = sum(1 for i in self.interaction_history if i.user_feedback > 0)
        success_rate = sum(1 for i in self.interaction_history if i.success) / max(total_interactions, 1)
        
        return {
            "total_interactions": total_interactions,
            "positive_feedback_count": positive_feedback,
            "success_rate": success_rate,
            "learned_preferences": len(self.user_preferences),
            "q_table_size": len(self.q_table)
        }

# Global RL engine instance
rl_engine = ReinforcementLearningEngine()

# Learning analytics function
def show_learning_stats():
    """Show learning statistics to the user"""
    stats = rl_engine.get_learning_summary()
    
    report = (
        f"Learning Statistics: I've had {stats['total_interactions']} interactions with you. "
        f"You've given positive feedback {stats['positive_feedback_count']} times. "
        f"My success rate is {stats['success_rate']:.1%}. "
        f"I've learned {stats['learned_preferences']} preferences about how you like me to respond."
    )
    
    speak(report)


# =============================================================================
# SURVEILLANCE MODE
# =============================================================================

# Object detection variables
surveillance_system = None
object_recognition_mode = False
yolo_model = None
cap = None
detection_thread = None
detection_queue = Queue()
stop_event = threading.Event()

def run_surveillance():
    surveillance_system.run()

surveillance_thread = None

def start_surveillance_thread():
    global surveillance_thread
    if surveillance_thread is None or not surveillance_thread.is_alive():
        surveillance_thread = threading.Thread(target=run_surveillance, daemon=True)
        surveillance_thread.start()
        speak("Surveillance system started in the background.")
    else:
        speak("Surveillance system is already running.")

def detection_loop():
    """Run continuous object detection and display in a window"""
    global yolo_model, cap, detection_queue, stop_event
    while not stop_event.is_set():
        if cap is None or not cap.isOpened():
            break
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Perform object detection
        results = yolo_model(frame)
        detected_objects = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                label = yolo_model.names[cls]
                conf = float(box.conf)
                if conf > 0.5:  # Confidence threshold
                    detected_objects.append(label)
                    # Draw bounding box and label
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Update detection queue
        detection_queue.put(detected_objects)
        
        # Display frame
        cv2.imshow("YOLOv8 Object Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Allow manual window close
            stop_event.set()
        
        # Small delay to avoid overloading CPU
        time.sleep(0.03)  # ~30 FPS
    
    # Clean up
    cleanup_object_recognition()

def init_object_recognition():
    """Initialize YOLOv8 model, webcam, and detection window"""
    global yolo_model, cap, detection_thread, object_recognition_mode, stop_event
    try:
        yolo_model = YOLO("yolov8n.pt")  # Load YOLOv8 nano model
        cap = cv2.VideoCapture(0)  # Open default webcam
        if not cap.isOpened():
            speak("Error: Could not access webcam.")
            return False
        stop_event.clear()  # Reset stop event
        object_recognition_mode = True
        # Start detection thread
        detection_thread = threading.Thread(target=detection_loop, daemon=True)
        detection_thread.start()
        return True
    except Exception as e:
        speak(f"Error initializing object recognition: {str(e)}")
        return False

def describe_objects():
    """Describe objects from the latest detection"""
    global object_recognition_mode, detection_queue
    if not object_recognition_mode:
        return "Object recognition mode is not active."
    
    try:
        # Get latest detected objects from queue
        if detection_queue.empty():
            return "I don't see any objects right now."
        detected_objects = detection_queue.get()
        
        if not detected_objects:
            return "I don't see any objects right now."
        
        # Create a natural language description
        unique_objects = list(set(detected_objects))
        object_count = len(detected_objects)
        if object_count == 1:
            return f"I see one {unique_objects[0]}."
        else:
            objects_str = ", ".join(unique_objects[:-1]) + f" and {unique_objects[-1]}" if len(unique_objects) > 1 else unique_objects[0]
            return f"I see {object_count} objects: {objects_str}."
    except Exception as e:
        return f"Error detecting objects: {str(e)}"

def cleanup_object_recognition():
    """Release webcam, stop detection thread, and close window"""
    global cap, detection_thread, object_recognition_mode, stop_event
    stop_event.set()  # Signal detection thread to stop
    if detection_thread is not None:
        detection_thread.join()
        detection_thread = None
    if cap is not None:
        cap.release()
        cap = None
    object_recognition_mode = False
    cv2.destroyAllWindows()

# =============================================================================
# VIRTUAL ASSSISTANT
# =============================================================================

def virtual_assistant():
    global surveillance_system, surveillance_thread, emotional_intelligence_mode
    try:
        greet_user()
        speak("I am Elsa, your virtual assistant. How can I help you?")
        surveillance_system = MultiSurveillanceSystem(camera_source=0, output_folder="surveillance_output", speak_callback=speak)
        running = True
        while running:
            command = listen()
            if command:
                running = process_command(command)
    finally:
        if surveillance_system:
            surveillance_system.cleanup()
        if surveillance_thread and surveillance_thread.is_alive():
            surveillance_thread.join(timeout=1.0)
        cleanup_object_recognition()

# =============================================================================
# SPEAKING AND LISTENING
# =============================================================================


# Function for speaking with gTTS
""" def speak(text):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_filename = fp.name
    
    # Generate speech
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(temp_filename)
    
    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(temp_filename)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    
    # Remove temporary file
    try:
        os.unlink(temp_filename)
    except:
        pass
    
    print(text)"""

# Function to listen to voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        return ""
    except sr.RequestError:
        speak("Sorry, there was an error with the speech recognition service.")
        return ""

# Function to greet the user
def greet_user():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    
    speak(greeting)
    print(greeting)

# =============================================================================
# PERSONALIZED EXPERIENCE
# =============================================================================

class PersonalizationEngine:
    def __init__(self):
        self.user_profile_file = "ELSA_user_profile.json"
        self.current_user = None
        self.user_profiles = self.load_profiles()
        self.session_commands = []

    def load_profiles(self):
        """Load user profiles from file"""
        try:
            if os.path.exists(self.user_profile_file):
                with open(self.user_profile_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profiles: {e}")
        return {}
    
    def save_profiles(self):
        """Save user profiles to file"""
        try:
            with open(self.user_profile_file, 'w') as f:
                json.dump(self.user_profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def create_user_profile(self, username):
        """Create a new user profile"""
        profile = {
            'username': username,
            'created_date': datetime.datetime.now().isoformat(),
            'last_active': datetime.datetime.now().isoformat(),
            'preferences': {
                'greeting_style': 'formal',  # formal, casual, friendly
                'response_length': 'medium',  # short, medium, detailed
                'voice_speed': 'normal',  # slow, normal, fast
                'favorite_apps': [],
                'favorite_topics': [],
                'preferred_search_engines': ['google'],
                'work_schedule': None,
                'time_zone': None
            },
            'usage_stats': {
                'total_commands': 0,
                'most_used_commands': {},
                'session_count': 0,
                'average_session_length': 0,
                'favorite_time_of_day': None
            },
            'command_history': [],
            'learning_data': {
                'common_phrases': {},
                'correction_count': 0,
                'successful_tasks': [],
                'failed_tasks': []
            }
        }
        self.user_profiles[username] = profile
        self.save_profiles()
        return profile
    
    def set_current_user(self, username):
        """Set the current active user"""
        if username not in self.user_profiles:
            self.create_user_profile(username)
        
        self.current_user = username
        # Update last active time
        self.user_profiles[username]['last_active'] = datetime.datetime.now().isoformat()
        self.user_profiles[username]['usage_stats']['session_count'] += 1
        self.save_profiles()
    
    def get_current_profile(self):
        """Get current user's profile"""
        if self.current_user and self.current_user in self.user_profiles:
            return self.user_profiles[self.current_user]
        return None
    
    def update_preferences(self, key, value):
        """Update user preferences"""
        if self.current_user:
            self.user_profiles[self.current_user]['preferences'][key] = value
            self.save_profiles()
    
    def log_command(self, command, success=True):
        """Log a command for learning purposes"""
        if not self.current_user:
            return
            
        profile = self.user_profiles[self.current_user]
        
        # Update command statistics
        profile['usage_stats']['total_commands'] += 1
        if command in profile['usage_stats']['most_used_commands']:
            profile['usage_stats']['most_used_commands'][command] += 1
        else:
            profile['usage_stats']['most_used_commands'][command] = 1
        
        # Add to command history (keep last 100)
        profile['command_history'].append({
            'command': command,
            'timestamp': datetime.datetime.now().isoformat(),
            'success': success
        })
        if len(profile['command_history']) > 100:
            profile['command_history'] = profile['command_history'][-100:]
        
        # Track successful/failed tasks
        if success:
            profile['learning_data']['successful_tasks'].append(command)
        else:
            profile['learning_data']['failed_tasks'].append(command)
        
        # Keep only last 50 of each
        for task_type in ['successful_tasks', 'failed_tasks']:
            if len(profile['learning_data'][task_type]) > 50:
                profile['learning_data'][task_type] = profile['learning_data'][task_type][-50:]
        
        self.session_commands.append(command)
        self.save_profiles()
    
    def get_personalized_greeting(self):
        """Generate a personalized greeting"""
        if not self.current_user:
            return "Hello! I'm Elsa, your virtual assistant."
        
        profile = self.get_current_profile()
        username = profile['username']
        greeting_style = profile['preferences']['greeting_style']
        
        current_hour = datetime.datetime.now().hour
        if current_hour < 12:
            time_greeting = "Good morning"
        elif 12 <= current_hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        if greeting_style == 'formal':
            return f"{time_greeting}, {username}. I'm Elsa, ready to assist you today."
        elif greeting_style == 'casual':
            return f"Hey {username}! Elsa here. What's up?"
        else:  # friendly
            return f"{time_greeting}, {username}! Great to see you again. How can I help?"
    
    def get_command_suggestions(self):
        """Suggest commands based on usage patterns"""
        if not self.current_user:
            return []
        
        profile = self.get_current_profile()
        most_used = profile['usage_stats']['most_used_commands']
        
        # Get top 3 most used commands
        if most_used:
            sorted_commands = sorted(most_used.items(), key=lambda x: x[1], reverse=True)
            return [cmd for cmd, count in sorted_commands[:3]]
        return []
    
    def adapt_response_length(self, text):
        """Adapt response length based on user preference"""
        if not self.current_user:
            return text
        
        profile = self.get_current_profile()
        length_pref = profile['preferences']['response_length']
        
        sentences = text.split('. ')
        
        if length_pref == 'short' and len(sentences) > 2:
            return '. '.join(sentences[:2]) + '.'
        elif length_pref == 'detailed':
            return text  # Keep full length
        
        return text  # Medium is default
    
    def learn_from_correction(self, original_command, corrected_command):
        """Learn from user corrections"""
        if not self.current_user:
            return
        
        profile = self.user_profiles[self.current_user]
        profile['learning_data']['correction_count'] += 1
        
        # Store common phrase corrections
        if original_command not in profile['learning_data']['common_phrases']:
            profile['learning_data']['common_phrases'][original_command] = corrected_command
        
        self.save_profiles()

# Global personalization engine
personalization = PersonalizationEngine()

# function to check the computer system status:
def check_system():
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    # Memory usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_available = memory.available // (1024 * 1024)  # Convert to MB
    # Disk usage
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_free = disk.free // (1024 * 1024 * 1024)  # Convert to GB

    report = (
        f"System check: CPU usage is at {cpu_usage} percent. "
        f"Memory usage is at {memory_usage} percent, with {memory_available} megabytes available. "
        f"Disk usage is at {disk_usage} percent, with {disk_free} gigabytes free."
    )
    speak(report)

# Function to open a folder
def open_folder(folder_path):
    system = platform.system()
    if not os.path.exists(folder_path):
        speak(f"Sorry, the folder {folder_path} does not exist.")
        return
    
    if not os.path.isdir(folder_path):
        speak(f"Sorry, {folder_path} is not a folder.")
        return
    
    try:
        if system == "Windows":
            os.startfile(folder_path)  # Windows
        elif system == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            speak("Sorry, I don't support opening folders on this operating system yet.")
            return
        speak(f"Opening folder {folder_path}")
    except Exception as e:
        speak(f"An error occurred while trying to open the folder: {str(e)}")

# Function to describe a topic
def describe_topic(topic):
    try:
        # Use Wikipedia for a short description (2 sentences)
        summary = wikipedia.summary(topic, sentences=2)
        speak(f"Here's a short description of {topic}: {summary}")
    except wikipedia.exceptions.DisambiguationError:
        speak(f"There are multiple entries for {topic}. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak(f"Sorry, I couldn't find information about {topic} on Wikipedia.")
    except Exception as e:
        speak("An error occurred while fetching the description.")

# Function to open applications
def open_application(app_name):
    app_name = app_name.lower()
    system = platform.system()
    
    # Dictionary mapping common application names to their executable names
    app_dict = {
        # Windows applications
        "notepad": {"Windows": "notepad.exe"},
        "calculator": {"Windows": "calc.exe", "Darwin": "Calculator.app", "Linux": "gnome-calculator"},
        "word": {"Windows": "winword.exe"},
        "excel": {"Windows": "excel.exe"},
        "powerpoint": {"Windows": "powerpnt.exe"},
        "chrome": {"Windows": "chrome.exe", "Darwin": "Google Chrome.app", "Linux": "google-chrome"},
        "firefox": {"Windows": "firefox.exe", "Darwin": "Firefox.app", "Linux": "firefox"},
        "edge": {"Windows": "msedge.exe"},
        "zoom": {"Windows": "Zoom.exe", "Darwin": "zoom.us.app", "Linux": "zoom"},
        "spotify": {"Windows": "Spotify.exe", "Darwin": "Spotify.app", "Linux": "spotify"},
        "vlc": {"Windows": "vlc.exe", "Darwin": "VLC.app", "Linux": "vlc"},
        # Mac applications
        "safari": {"Darwin": "Safari.app"},
        "terminal": {"Darwin": "Terminal.app", "Linux": "gnome-terminal"},
        "finder": {"Darwin": "Finder.app"},
        # Linux applications
        "gedit": {"Linux": "gedit"}
    }
    
    try:
        # Check if the application is in our dictionary
        if app_name in app_dict:
            if system in app_dict[app_name]:
                executable = app_dict[app_name][system]
                speak(f"Opening {app_name}")
                
                if system == "Windows":
                    try:
                        subprocess.Popen(executable)
                    except:
                        # Try from Program Files if direct execution fails
                        program_files = os.environ.get('ProgramFiles')
                        program_files_x86 = os.environ.get('ProgramFiles(x86)')
                        
                        possible_paths = []
                        if program_files:
                            possible_paths.append(program_files)
                        if program_files_x86:
                            possible_paths.append(program_files_x86)
                            
                        for path in possible_paths:
                            # Recursive search for the executable
                            for root, dirs, files in os.walk(path):
                                if executable.lower() in [f.lower() for f in files]:
                                    full_path = os.path.join(root, executable)
                                    subprocess.Popen(full_path)
                                    return
                        
                        # If we still can't find it, try running directly as a command
                        subprocess.Popen(app_name)
                        
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", "-a", executable])
                elif system == "Linux":
                    subprocess.Popen([executable])
            else:
                speak(f"Sorry, I don't know how to open {app_name} on your operating system.")
        else:
            # Try to open the application directly by name
            speak(f"Trying to open {app_name}")
            
            if system == "Windows":
                try:
                    subprocess.Popen([f"{app_name}.exe"])
                except:
                    speak(f"I couldn't find the application {app_name}.")
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["open", "-a", f"{app_name}"])
                except:
                    speak(f"I couldn't find the application {app_name}.")
            elif system == "Linux":
                try:
                    subprocess.Popen([app_name])
                except:
                    speak(f"I couldn't find the application {app_name}.")
            else:
                speak("Sorry, I don't support opening applications on this operating system yet.")
    except Exception as e:
        speak(f"An error occurred while trying to open {app_name}: {str(e)}")

# Improved Wikipedia search function
def search_wikipedia(query, sentences=4):
    try:
        # First try direct summary
        summary = wikipedia.summary(query, sentences=sentences)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # If disambiguation error, try the first option
        try:
            options = e.options
            if options:
                summary = wikipedia.summary(options[0], sentences=sentences)
                return f"Found information about {options[0]}: {summary}"
            else:
                return None
        except:
            return None
    except wikipedia.exceptions.PageError:
        # If page not found, try search
        try:
            search_results = wikipedia.search(query, results=1)
            if search_results:
                summary = wikipedia.summary(search_results[0], sentences=sentences)
                return f"Found information about {search_results[0]}: {summary}"
            else:
                return None
        except:
            return None
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return None

# New function for deep search
def deep_search(query):
    speak(f"Initiating deep search for {query}")
    
    # Search in Wikipedia (3-5 sentences)
    wiki_result = search_wikipedia(query, sentences=4)
    if wiki_result:
        speak(f"From Wikipedia: {wiki_result}")
    else:
        speak("No Wikipedia information found for this query.")
    
    # Open LinkedIn search
    linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={query}"
    speak("Opening LinkedIn search results")
    webbrowser.open(linkedin_url)
    
    # Open Twitter/X search
    twitter_url = f"https://twitter.com/search?q={query}"
    speak("Opening Twitter search results")
    webbrowser.open(twitter_url)

    # Open Google search
    google_url = f"https://www.google.com/search?q={query}"
    speak("Opening Google search results")
    webbrowser.open(google_url)
    
    speak("Deep search completed.")

# Variable to track deep search mode
deep_search_mode = False

# =============================================================================
# ADDITIONAL HOME AI FEATURES
# =============================================================================

# Weather API key (replace with your OpenWeatherMap API key)
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY_HERE"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city="London"):  # Default to London, change as needed
    try:
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric'  # Celsius
        }
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"The weather in {city} is {description} with a temperature of {temp} degrees Celsius."
        else:
            return "Sorry, I couldn't fetch the weather information."
    except Exception as e:
        print(f"Weather error: {e}")
        return "Sorry, there was an error getting the weather."

# Function to play music (opens YouTube search for song)
def play_music(song):
    url = f"https://www.youtube.com/results?search_query={song}"
    webbrowser.open(url)
    speak(f"Playing {song} on YouTube.")

# Function to set a timer
def set_timer(minutes):
    try:
        time.sleep(int(minutes) * 60)
        speak("Timer finished!")
    except:
        speak("Invalid timer duration.")

# Function to tell a joke
def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call fake spaghetti? An impasta!"
    ]
    speak(random.choice(jokes))

# Simulate smart home control (e.g., lights)
def control_lights(action):
    if action == "on":
        speak("Turning the lights on.")
    elif action == "off":
        speak("Turning the lights off.")
    else:
        speak("Invalid light command.")

# Math calculation (simple eval, be careful with security)
def calculate(expression):
    try:
        result = eval(expression)
        speak(f"The result is {result}.")
    except:
        speak("Invalid calculation.")


# =============================================================================
# COMMAND PROCESSING
# =============================================================================

emotional_intelligence_mode = False

# the command function for interaction:
def process_command(command):
    global deep_search_mode, object_recognition_mode, emotional_intelligence_mode
    
    # Integrate emotional detection if mode is active
    if emotional_intelligence_mode:
        emotions = detect_emotion(command)
        emotional_response = provide_emotional_response(emotions)
        if emotional_response:
            speak(emotional_response)
            offer_support()
            # Continue to process the command if needed

    # Check if deep search mode is active
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True

    # Scheduling commands
    if any(phrase in command for phrase in ["create schedule", "schedule", "add event", "create event", "make a plan", "new plan", "plan"]):
        handle_create_schedule()
        
    elif any(phrase in command for phrase in ["list schedule", "show schedule", "my schedule", "upcoming events", "what's planned"]):
        handle_list_schedule()
        
    elif any(phrase in command for phrase in ["delete event", "remove event", "cancel event"]):
        handle_delete_event()
        
    elif "start reminder" in command or "activate reminder" in command:
        start_reminder_system()
        
    elif "stop reminder" in command or "deactivate reminder" in command:
        stop_reminder_system()

    elif "did you activate the reminder" in command or "schedule activated" in command:
        speak("Yes, it is activated. I have reminded you 24 hours ago.")

    if "hello" in command:
        speak("Hello! How can I assist you today?")
    
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}")
    
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "open openai" in command:
        speak("Opening OpenAI ChatGPT server.")
        webbrowser.open("https://chatgpt.com/")

    elif "open deepseek" in command:
        speak("Opening DeepSeek server")
        webbrowser.open("https://chat.deepseek.com/")
    
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    
    elif "search on google" in command or "on google" in command:
        speak("What would you like me to search for?")
        query = listen()
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            speak(f"Searching for {query} on the web.")
    
    elif "on youtube" in command or "search on youtube" in command:
        speak("What would you like to watch on YouTube?")
        query = listen()
        if query:
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            speak(f"Searching for {query} on YouTube.")

    elif "on wikipedia" in command or "search on wikipedia" in command:
        speak("What would you like to know about?")
        query = listen()
        if query:
            wiki_result = search_wikipedia(query, sentences=2)
            if wiki_result:
                speak(wiki_result)
            else:
                speak("I couldn't find any information on that topic.")
    
    elif "system check" in command or "check system" in command:
        speak("Checking all systems. Please wait.")
        speak("This may take a few seconds.")
        check_system()
    
    elif "open folder" in command:
        speak("Please tell me the full path of the folder you want to open.")
        folder_path = hear_folder_path()
        if folder_path:
            open_folder(folder_path)
            
    elif "open application" in command or "open app" in command or "launch" in command:
        # Extract application name if provided in the command
        app_name = None
        
        for phrase in ["open application", "open app", "launch"]:
            if phrase in command:
                # Try to extract the app name after the phrase
                parts = command.split(phrase)
                if len(parts) > 1 and parts[1].strip():
                    app_name = parts[1].strip()
                    break
        
        # If not found in the command, ask the user
        if not app_name:
            speak("Which application would you like me to open?")
            app_name = listen()
            
        if app_name:
            open_application(app_name)
            
    # Specific app commands for direct opening
    elif command.startswith("open ") and "folder" not in command and "youtube" not in command and "google" not in command:
        app_name = command.replace("open ", "").strip()
        open_application(app_name)

    elif "describe" in command or "tell me about" in command:
        speak("What topic would you like me to describe?")
        topic = listen()
        if topic:
            wiki_result = search_wikipedia(topic, sentences=2)
            if wiki_result:
                speak(wiki_result)
            else:
                speak("I couldn't find any information on that topic.")
            
    # New deep search commands
    elif "activate deep search" in command:
        deep_search_mode = True
        speak("Deep search mode activated. What would you like to search for?")
    
    elif "deactivate deep search" in command or "exit deep search" in command or "stop deep search" in command:
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
        else:
            speak("Deep search mode is not currently active.")
            
    elif "deep search" in command and not deep_search_mode:
        # Extract query if provided in the command
        query = None
        parts = command.split("deep search")
        if len(parts) > 1 and parts[1].strip():
            query = parts[1].strip()
        
        # If not found in the command, ask the user
        if not query:
            speak("What would you like me to search for?")
            query = listen()
            
        if query:
            deep_search(query)

    # start / stop surveillance system:
    elif "start surveillance" in command:
        if not surveillance_system.cap or not surveillance_system.cap.isOpened():
            try:
                surveillance_system.start()
                start_surveillance_thread()
            except ValueError as e:
                speak(f"Failed to start surveillance: {str(e)}")
        else:
            speak("Surveillance system is already running.")

    elif "stop surveillance" in command:
        if surveillance_system.cap and surveillance_system.cap.isOpened():
            surveillance_system.cleanup()
            speak("Surveillance system stopped.")
        else:
            speak("Surveillance system is not running.")

    # surveillance modes:
    elif "toggle motion detection" in command:
        surveillance_system.toggle_detection_method("motion")
        speak("Motion detection toggled.")

    elif "toggle person detection" in command:
        surveillance_system.toggle_detection_method("person")
        speak("Person detection toggled.")
    
    elif "toggle face detection" in command:
        surveillance_system.toggle_detection_method("face")
        speak("Face detection toggled.")
    
    elif "toggle noise detection" in command:
        surveillance_system.toggle_detection_method("noise")
        speak("Noise detection toggled.")
    
    elif "toggle object detection" in command:
        surveillance_system.toggle_detection_method("yolo")
        speak("Object detection toggled.")

    # recording the footage:
    elif "start recording" in command:
        if not surveillance_system.is_recording:
            ret, frame = surveillance_system.cap.read()
            if ret:
                surveillance_system.start_recording(frame)
                speak("Started recording video.")
            else:
                speak("Failed to capture frame for recording.")
        else:
            speak("Recording is already in progress.")

    elif "stop recording" in command:
        if surveillance_system.is_recording:
            surveillance_system.stop_recording()
            speak("Recording stopped.")
        else:
            speak("No recording is in progress.")

    # taking screenshots:
    elif "take screenshot" in command:
        if surveillance_system.cap and surveillance_system.cap.isOpened():
            ret, frame = surveillance_system.cap.read()
            if ret:
                frame = cv2.resize(frame, (1100, 600))
                annotated_frames = {method: surveillance_system.current_detections.get(method, ([], frame))[1]
                                for method in surveillance_system.active_methods}
                display_frame = surveillance_system.combine_detections(frame, annotated_frames)
                display_frame = surveillance_system.add_status_overlay(display_frame)
                surveillance_system.save_screenshot(display_frame)
                speak("Screenshot saved.")
            else:
                speak("Failed to capture frame for screenshot.")
        else:
            speak("Surveillance system is not running.")

    # reporting any detections:
    elif "report detections" in command:
        if surveillance_system.cap and surveillance_system.cap.isOpened():
            detection_summary = []
            for method_name in surveillance_system.active_methods:
                detections, _ = surveillance_system.current_detections.get(method_name, ([], None))
                if detections:
                    status_text = surveillance_system.detection_methods[method_name].get_status_text(detections)
                    detection_summary.append(status_text)
            if detection_summary:
                speak("Current detections: " + ", ".join(detection_summary))
            else:
                speak("No detections at the moment.")
        else:
            speak("Surveillance system is not running.")

    # web socket command:
    elif "check websocket alerts" in command:
        if surveillance_system.websocket_clients:
            speak("WebSocket server is active with connected clients.")
        else:
            speak("No WebSocket clients are currently connected.")

    # Object recognition commands
    elif "activate object recognition" in command or "start object recognition" in command or "vision mode" in command:
        if not object_recognition_mode:
            if init_object_recognition():
                speak("Object recognition mode activated. Detection window opened. Ask me what I see!")
            else:
                speak("Failed to activate object recognition mode.")
        else:
            speak("Object recognition mode is already active.")
    
    elif "deactivate object recognition" in command or "stop object recognition" in command or "stop vision mode" in command:
        if object_recognition_mode:
            cleanup_object_recognition()
            speak("Object recognition mode deactivated. Detection window closed.")
        else:
            speak("Object recognition mode is not active.")
    
    elif "what do you see" in command or "describe what you see" in command:
        result = describe_objects()
        speak(result)

    # NEWS COMMANDS
    elif "news" in command or "headlines" in command:
        if any(word in command for word in ["morning", "briefing", "update"]):
            get_news(morning_briefing=True)
        elif "business" in command:
            get_news(category="business")
        elif "sports" in command:
            get_news(category="sports")
        elif "technology" in command or "tech" in command:
            get_news(category="technology")
        elif "health" in command:
            get_news(category="health")
        elif "entertainment" in command:
            get_news(category="entertainment")
        elif "science" in command:
            get_news(category="science")
        else:
            get_news()  # General news
    
    elif "morning briefing" in command:
        get_news(morning_briefing=True)

    # Emotional Intelligence Mode commands
    elif "activate emotional intelligence" in command or "activate ei mode" in command:
        emotional_intelligence_mode = True
        speak("Emotional intelligence mode activated. I'll now pay attention to your emotional state and provide appropriate support. How are you feeling right now?")
    
    elif "deactivate emotional intelligence" in command or "exit ei mode" in command or "stop emotional intelligence" in command:
        if emotional_intelligence_mode:
            emotional_intelligence_mode = False
            speak("Emotional intelligence mode deactivated. I'm still here to help with your regular tasks.")
        else:
            speak("Emotional intelligence mode is not currently active.")
    
    # Emotional support commands
    elif "i need support" in command or "help me feel better" in command or "i'm not okay" in command:
        offer_support()
    
    elif "breathing exercise" in command or "help me breathe" in command or "breathing" in command:
        breathing_exercise()
    
    elif "inspirational quote" in command or "inspire me" in command or "motivate me" in command:
        share_inspirational_quote()
    
    elif "self care" in command or "self-care" in command or "what should i do" in command:
        suggest_self_care()

    # ROUTINE COMMANDS
    if "create routine" in command or "new routine" in command or "add routine" in command:
        routine_manager.create_routine()
    
    elif "list routines" in command or "show routines" in command or "my routines" in command:
        routine_manager.list_routines()
    
    elif "delete routine" in command or "remove routine" in command:
        routine_manager.delete_routine()
    
    elif "routine help" in command:
        speak("""Routine commands available: 
        Create routine - to set up a new reminder or task
        List routines - to see all your current routines  
        Delete routine - to remove a routine
        You can set daily, weekly, or one-time routines for any time of day.""")

    elif "learning stats" in command or "show learning" in command or "my stats" in command:
        show_learning_stats()

    elif "reset learning" in command or "clear learning" in command:
        rl_engine.q_table.clear()
        rl_engine.user_preferences.clear()
        rl_engine.interaction_history.clear()
        speak("Learning data has been reset. I'll start learning fresh.")
        rl_engine.record_interaction(command, "reset", 1, {}, True)

    # Additional Home AI commands
    elif "weather" in command:
        city = command.replace("weather", "").strip() or "London"
        weather_report = get_weather(city)
        speak(weather_report)
    
    elif "play music" in command or "play song" in command:
        song = command.replace("play music", "").replace("play song", "").strip()
        if not song:
            speak("What song would you like to play?")
            song = listen()
        if song:
            play_music(song)
    
    elif "set timer" in command:
        minutes = ''.join(filter(str.isdigit, command))
        if minutes:
            speak(f"Setting timer for {minutes} minutes.")
            threading.Thread(target=set_timer, args=(minutes,)).start()
        else:
            speak("How many minutes for the timer?")
            minutes = listen()
            if minutes.isdigit():
                speak(f"Setting timer for {minutes} minutes.")
                threading.Thread(target=set_timer, args=(minutes,)).start()
    
    elif "tell joke" in command or "joke" in command:
        tell_joke()
    
    elif "turn lights on" in command:
        control_lights("on")
    
    elif "turn lights off" in command:
        control_lights("off")
    
    elif "calculate" in command:
        expression = command.replace("calculate", "").strip()
        if expression:
            calculate(expression)
        else:
            speak("What would you like to calculate?")
            expression = listen()
            if expression:
                calculate(expression)
    
    elif "exit" in command or "stop" in command:
        # Reset deep search mode if it's active
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
        speak("Goodbye!")
        return False
    else:
        speak("I'm not sure how to help with that yet. Try asking something else!")
    return True

# Function to hear and process folder path
def hear_folder_path():
    path = listen()
    if path:
        # Replace common spoken separators with proper ones
        path = path.replace("backslash", "\\").replace("slash", "/").replace("dot", ".")
        return path
    return ""

# =============================
# CLI MODE SUPPORT
# =============================
import sys

def cli_assistant():
    global surveillance_system, surveillance_thread, emotional_intelligence_mode
    greet_user()
    speak("I am Elsa, your virtual assistant (CLI mode). Type 'exit' to quit.")
    surveillance_system = MultiSurveillanceSystem(camera_source=0, output_folder="surveillance_output", speak_callback=speak)
    running = True
    while running:
        try:
            command = input("You: ").strip()
            if command.lower() in ("exit", "quit"):  # Allow user to exit
                speak("Shutting down. Goodbye!")
                break
            if command:
                running = process_command(command)
        except (KeyboardInterrupt, EOFError):
            speak("Shutting down. Goodbye!")
            break
    if surveillance_system:
        surveillance_system.cleanup()
    if surveillance_thread and surveillance_thread.is_alive():
        surveillance_thread.join(timeout=1.0)
    cleanup_object_recognition()

# main program initializing:
if __name__ == "__main__":
    emotional_intelligence_mode = False  # Ensure defined
    load_schedule()  # Load schedule on start
    start_reminder_system()  # Start reminders automatically
    check_morning_briefing()  # Check for morning briefing
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--cli":
            cli_assistant()
        else:
            virtual_assistant()
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye!")
        cleanup_object_recognition()
        if surveillance_system:
            surveillance_system.cleanup()
        if surveillance_thread and surveillance_thread.is_alive():
            surveillance_thread.join(timeout=1.0)
        stop_reminder_system()



