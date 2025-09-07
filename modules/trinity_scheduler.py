# V 1.9.16
# Added comprehensive scheduling and reminder system
# modifiying the wikipedia function in deep internet search
# version 1.7.5
# using gTTS
# importing libs
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import psutil
import os
import subprocess
import platform
from gtts import gTTS
import pygame
import tempfile
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import threading
from dateutil import parser
from dateutil.relativedelta import relativedelta

# Scheduler-related imports
SCHEDULE_FILE = "trinity_schedule.json"
REMINDER_CHECK_INTERVAL = 30  # Check for reminders every 30 seconds

# Global variables for scheduling
schedule_data = {}
reminder_thread = None
scheduler_active = False

# random sentences:
RANDOM_SEN = [""]

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

# Function for speaking with gTTS
def speak(text):
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
    
    print(text)

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
    # Add more applications as needed
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

# the command function for interaction:
def process_command(command):
    global deep_search_mode
    
    # Check if deep search mode is active
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True
    
    # Scheduling commands
    if any(phrase in command for phrase in ["create schedule", "schedule", "add event", "create event", "make plan", "plan"]):
        handle_create_schedule()
        
    elif any(phrase in command for phrase in ["list schedule", "show schedule", "my schedule", "upcoming events", "what's planned"]):
        handle_list_schedule()
        
    elif any(phrase in command for phrase in ["delete event", "remove event", "cancel event"]):
        handle_delete_event()
        
    elif "start reminder" in command or "activate reminder" in command:
        start_reminder_system()
        
    elif "stop reminder" in command or "deactivate reminder" in command:
        stop_reminder_system()
        
    elif "hello" in command:
        speak("Hello! How can I assist you today?")
    
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}")
    
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    
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
        speak("Checking all systems. please wait.")
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

    elif "exit" in command or "stop" in command:
        # Reset deep search mode if it's active
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
        stop_reminder_system()
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
        # Example: "C backslash users" becomes "C:\users"
        return path
    return ""

# Main loop
def virtual_assistant():
    # Load existing schedule data
    load_schedule()
    
    # Start reminder system automatically
    start_reminder_system()
    
    greet_user()
    speak("I am Trinity, your virtual assistant. I can help you with scheduling, reminders, and much more. How can I help you?")
    
    # Quick tip about scheduling
    if not schedule_data:
        speak("Pro tip: You can create schedules by saying 'create schedule' or 'make plan'.")
    
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

# main program initializing:
if __name__ == "__main__":
    virtual_assistant()