# V 1.9.15
# Adding special routines mode for personalized tasks and reminders
# version 1.7.4
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
from threading import Timer

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

# New function for deep search
def deep_search(query):
    speak(f"Initiating deep search for {query}")
    
    # Search in Wikipedia (3-5 sentences)
    try:
        wiki_summary = wikipedia.summary(query, sentences=4)
        speak(f"From Wikipedia: {wiki_summary}")
    except:
        speak("No Wikipedia information found for this query.")
    
    # Open Google search
    google_url = f"https://www.google.com/search?q={query}"
    speak("Opening Google search results")
    webbrowser.open(google_url)
    
    # Open LinkedIn search
    linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={query}"
    speak("Opening LinkedIn search results")
    webbrowser.open(linkedin_url)
    
    # Open Twitter/X search
    twitter_url = f"https://twitter.com/search?q={query}"
    speak("Opening Twitter search results")
    webbrowser.open(twitter_url)
    
    speak("Deep search completed.")

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
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast("Trinity Routine Reminder", routine['message'], duration=10)
        except:
            pass  # Visual notification failed, but audio worked

# Global variables
deep_search_mode = False
routine_manager = RoutineManager()

# the command function for interaction:
def process_command(command):
    global deep_search_mode
    
    # Check if deep search mode is active
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True
    
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
            try:
                result = wikipedia.summary(query, sentences=2)
                speak(result)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("There are multiple results. Please be more specific.")
            except wikipedia.exceptions.PageError as e:
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
            describe_topic(topic)
            
    # Deep search commands
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
    greet_user()
    speak("I am Trinity, your virtual assistant. I now have routines capability! You can create personalized reminders and tasks. How can I help you?")
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

if __name__ == "__main__":
    virtual_assistant()