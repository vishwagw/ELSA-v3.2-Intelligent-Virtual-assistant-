# V 1.9.15 - Added Personalization Features
# adding a deep internet search:
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
from collections import defaultdict, Counter
import hashlib

# Personalization class to handle user profiles and preferences
class PersonalizationEngine:
    def __init__(self):
        self.user_profile_file = "trinity_user_profile.json"
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
            return "Hello! I'm Trinity, your virtual assistant."
        
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
            return f"{time_greeting}, {username}. I'm Trinity, ready to assist you today."
        elif greeting_style == 'casual':
            return f"Hey {username}! Trinity here. What's up?"
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

# Function for speaking with gTTS (now with personalization)
def speak(text):
    # Adapt response length based on user preferences
    text = personalization.adapt_response_length(text)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_filename = fp.name
    
    # Determine speech speed based on user preference
    speed = False  # Default normal speed
    if personalization.current_user:
        profile = personalization.get_current_profile()
        if profile and profile['preferences']['voice_speed'] == 'slow':
            speed = True
    
    # Generate speech
    tts = gTTS(text=text, lang='en', slow=speed)
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

# Function to handle user login/identification
def handle_user_identification():
    speak("Hello! To provide you with a personalized experience, may I know your name?")
    username = listen()
    
    if username:
        # Clean up the username
        username = username.replace("my name is ", "").replace("i am ", "").replace("i'm ", "").strip()
        personalization.set_current_user(username)
        
        # Check if this is a returning user
        profile = personalization.get_current_profile()
        if profile['usage_stats']['session_count'] > 1:
            speak(f"Welcome back, {username}! I remember you.")
            
            # Suggest common commands
            suggestions = personalization.get_command_suggestions()
            if suggestions:
                speak(f"Based on your usage, you often use: {', '.join(suggestions[:2])}")
        else:
            speak(f"Nice to meet you, {username}! I'll learn your preferences as we interact.")
            setup_user_preferences(username)
        
        return True
    else:
        speak("I'll continue without personalization for now.")
        return False

def setup_user_preferences(username):
    """Set up initial user preferences"""
    speak("Let me quickly set up your preferences. Would you prefer formal, casual, or friendly responses?")
    style = listen()
    
    if "formal" in style:
        personalization.update_preferences('greeting_style', 'formal')
    elif "casual" in style:
        personalization.update_preferences('greeting_style', 'casual')
    elif "friendly" in style:
        personalization.update_preferences('greeting_style', 'friendly')
    
    speak("Would you prefer short, medium, or detailed responses?")
    length = listen()
    
    if "short" in length:
        personalization.update_preferences('response_length', 'short')
    elif "detailed" in length or "long" in length:
        personalization.update_preferences('response_length', 'detailed')
    else:
        personalization.update_preferences('response_length', 'medium')
    
    speak("Great! I'll adapt to your preferences. You can change these anytime by saying 'update preferences'.")

# Function to greet the user (now personalized)
def greet_user():
    greeting = personalization.get_personalized_greeting()
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
        personalization.log_command(f"open folder {folder_path}", success=False)
        return
    
    if not os.path.isdir(folder_path):
        speak(f"Sorry, {folder_path} is not a folder.")
        personalization.log_command(f"open folder {folder_path}", success=False)
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
        personalization.log_command(f"open folder {folder_path}", success=True)
    except Exception as e:
        speak(f"An error occurred while trying to open the folder: {str(e)}")
        personalization.log_command(f"open folder {folder_path}", success=False)

# Function to describe a topic
def describe_topic(topic):
    try:
        # Use Wikipedia for a short description (2 sentences)
        summary = wikipedia.summary(topic, sentences=2)
        speak(f"Here's a short description of {topic}: {summary}")
        personalization.log_command(f"describe {topic}", success=True)
        
        # Learn user's interests
        if personalization.current_user:
            profile = personalization.get_current_profile()
            if topic not in profile['preferences']['favorite_topics']:
                profile['preferences']['favorite_topics'].append(topic)
                # Keep only top 10 topics
                if len(profile['preferences']['favorite_topics']) > 10:
                    profile['preferences']['favorite_topics'] = profile['preferences']['favorite_topics'][-10:]
                personalization.save_profiles()
                
    except wikipedia.exceptions.DisambiguationError:
        speak(f"There are multiple entries for {topic}. Please be more specific.")
        personalization.log_command(f"describe {topic}", success=False)
    except wikipedia.exceptions.PageError:
        speak(f"Sorry, I couldn't find information about {topic} on Wikipedia.")
        personalization.log_command(f"describe {topic}", success=False)
    except Exception as e:
        speak("An error occurred while fetching the description.")
        personalization.log_command(f"describe {topic}", success=False)

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
                                    personalization.log_command(f"open {app_name}", success=True)
                                    
                                    # Track favorite apps
                                    if personalization.current_user:
                                        profile = personalization.get_current_profile()
                                        if app_name not in profile['preferences']['favorite_apps']:
                                            profile['preferences']['favorite_apps'].append(app_name)
                                            if len(profile['preferences']['favorite_apps']) > 10:
                                                profile['preferences']['favorite_apps'] = profile['preferences']['favorite_apps'][-10:]
                                            personalization.save_profiles()
                                    return
                        
                        # If we still can't find it, try running directly as a command
                        subprocess.Popen(app_name)
                        
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", "-a", executable])
                elif system == "Linux":
                    subprocess.Popen([executable])
                    
                personalization.log_command(f"open {app_name}", success=True)
                
                # Track favorite apps
                if personalization.current_user:
                    profile = personalization.get_current_profile()
                    if app_name not in profile['preferences']['favorite_apps']:
                        profile['preferences']['favorite_apps'].append(app_name)
                        if len(profile['preferences']['favorite_apps']) > 10:
                            profile['preferences']['favorite_apps'] = profile['preferences']['favorite_apps'][-10:]
                        personalization.save_profiles()
            else:
                speak(f"Sorry, I don't know how to open {app_name} on your operating system.")
                personalization.log_command(f"open {app_name}", success=False)
        else:
            # Try to open the application directly by name
            speak(f"Trying to open {app_name}")
            
            if system == "Windows":
                try:
                    subprocess.Popen([f"{app_name}.exe"])
                    personalization.log_command(f"open {app_name}", success=True)
                except:
                    speak(f"I couldn't find the application {app_name}.")
                    personalization.log_command(f"open {app_name}", success=False)
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["open", "-a", f"{app_name}"])
                    personalization.log_command(f"open {app_name}", success=True)
                except:
                    speak(f"I couldn't find the application {app_name}.")
                    personalization.log_command(f"open {app_name}", success=False)
            elif system == "Linux":
                try:
                    subprocess.Popen([app_name])
                    personalization.log_command(f"open {app_name}", success=True)
                except:
                    speak(f"I couldn't find the application {app_name}.")
                    personalization.log_command(f"open {app_name}", success=False)
            else:
                speak("Sorry, I don't support opening applications on this operating system yet.")
                personalization.log_command(f"open {app_name}", success=False)
    except Exception as e:
        speak(f"An error occurred while trying to open {app_name}: {str(e)}")
        personalization.log_command(f"open {app_name}", success=False)

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
    personalization.log_command(f"deep search {query}", success=True)

# New personalization commands
def handle_personalization_commands(command):
    """Handle personalization-specific commands"""
    
    if "update preferences" in command or "change preferences" in command:
        speak("What would you like to update? You can change your greeting style, response length, or voice speed.")
        pref_command = listen()
        
        if "greeting" in pref_command:
            speak("Would you prefer formal, casual, or friendly greetings?")
            style = listen()
            if "formal" in style:
                personalization.update_preferences('greeting_style', 'formal')
                speak("Updated to formal greetings.")
            elif "casual" in style:
                personalization.update_preferences('greeting_style', 'casual')
                speak("Updated to casual greetings.")
            elif "friendly" in style:
                personalization.update_preferences('greeting_style', 'friendly')
                speak("Updated to friendly greetings.")
        
        elif "response" in pref_command or "length" in pref_command:
            speak("Would you prefer short, medium, or detailed responses?")
            length = listen()
            if "short" in length:
                personalization.update_preferences('response_length', 'short')
                speak("Updated to short responses.")
            elif "detailed" in length or "long" in length:
                personalization.update_preferences('response_length', 'detailed')
                speak("Updated to detailed responses.")
            else:
                personalization.update_preferences('response_length', 'medium')
                speak("Updated to medium length responses.")
        
        elif "voice" in pref_command or "speed" in pref_command:
            speak("Would you prefer slow, normal, or fast speech speed?")
            speed = listen()
            if "slow" in speed:
                personalization.update_preferences('voice_speed', 'slow')
                speak("Updated to slow speech speed.")
            elif "fast" in speed:
                personalization.update_preferences('voice_speed', 'fast')
                speak("Updated to fast speech speed.")
            else:
                personalization.update_preferences('voice_speed', 'normal')
                speak("Updated to normal speech speed.")
        
        return True
    
    elif "show my stats" in command or "my statistics" in command:
        if personalization.current_user:
            profile = personalization.get_current_profile()
            stats = profile['usage_stats']
            
            speak(f"Here are your statistics: You've used {stats['total_commands']} commands across {stats['session_count']} sessions.")
            
            if stats['most_used_commands']:
                top_command = max(stats['most_used_commands'], key=stats['most_used_commands'].get)
                speak(f"Your most used command is: {top_command}")
            
            if profile['preferences']['favorite_apps']:
                speak(f"Your favorite apps are: {', '.join(profile['preferences']['favorite_apps'][:3])}")
        else:
            speak("Please identify yourself first to see your statistics.")
        return True
    
    elif "forget me" in command or "delete my profile" in command:
        if personalization.current_user:
            username = personalization.current_user
            speak(f"Are you sure you want me to forget everything about {username}? Say yes to confirm.")
            confirmation = listen()
            if "yes" in confirmation:
                del personalization.user_profiles[username]
                personalization.save_profiles()
                personalization.current_user = None
                speak("I've forgotten your profile. Nice meeting you!")
            else:
                speak("Profile deletion cancelled.")
        return True
    
    elif "who am i" in command or "my profile" in command:
        if personalization.current_user:
            profile = personalization.get_current_profile()
            speak(f"You are {profile['username']}. Your greeting style is {profile['preferences']['greeting_style']}, and you prefer {profile['preferences']['response_length']} responses.")
        else:
            speak("I don't know who you are yet. Please tell me your name.")
        return True
    
    return False

# Variable to track deep search mode
deep_search_mode = False

# the command function for interaction (updated with personalization):
def process_command(command):
    global deep_search_mode
    
    # Log the command for learning
    personalization.log_command(command, success=True)
    
    # Check for personalization commands first
    if handle_personalization_commands(command):
        return True
    
    # Check if deep search mode is active
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True
        
    if "hello" in command:
        if personalization.current_user:
            greeting = personalization.get_personalized_greeting()
            speak(greeting)
        else:
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
        
        # Personalized goodbye
        if personalization.current_user:
            speak(f"Goodbye, {personalization.current_user}! It was great helping you today.")
        else:
            speak("Goodbye!")
        return False
    else:
        # Check if this might be a misunderstood command
        if personalization.current_user:
            profile = personalization.get_current_profile()
            # Check if user has used similar commands before
            similar_commands = [cmd for cmd in profile['learning_data']['successful_tasks'] 
                              if any(word in cmd for word in command.split())]
            
            if similar_commands:
                speak(f"I'm not sure about that. Did you mean something like: {similar_commands[0]}?")
            else:
                speak("I'm not sure how to help with that yet. Try asking something else!")
        else:
            speak("I'm not sure how to help with that yet. Try asking something else!")
    return True