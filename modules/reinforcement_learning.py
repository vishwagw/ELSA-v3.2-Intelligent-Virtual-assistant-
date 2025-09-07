# V 2.0.0 - Trinity AI Assistant with Reinforcement Learning
# Enhanced with user learning, preference storage, and adaptive responses

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
import numpy as np
from collections import defaultdict, deque
import pickle
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

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

# Enhanced speak function with learning
def speak(text, response_type="default", get_feedback=False):
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
    
    # Get user feedback if requested
    if get_feedback:
        return get_user_feedback()
    
    return 0

def get_user_feedback():
    """Get user feedback on the response"""
    print("Was this helpful? Say 'good', 'bad', or 'okay'")
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=3)
        
        feedback_text = recognizer.recognize_google(audio).lower()
        
        if any(word in feedback_text for word in ["good", "great", "excellent", "perfect", "yes"]):
            return 1
        elif any(word in feedback_text for word in ["bad", "wrong", "no", "terrible", "awful"]):
            return -1
        else:
            return 0
            
    except:
        return 0

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

# Function to greet the user with personalization
def greet_user():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    
    # Check for personalized greeting preference
    personalized_response = rl_engine.get_personalized_response("hello", {"time": current_hour})
    
    if personalized_response != "default":
        greeting += " I've learned that you prefer detailed responses in the morning."
    
    speak(greeting, "greeting")
    print(greeting)

# Enhanced system check with learning
def check_system():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_available = memory.available // (1024 * 1024)
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_free = disk.free // (1024 * 1024 * 1024)

    # Check for personalized response style
    personalized_response = rl_engine.get_personalized_response("system check", {})
    
    if personalized_response != "default":
        # Detailed response if user prefers it
        report = (
            f"Comprehensive system analysis: CPU utilization stands at {cpu_usage} percent. "
            f"Memory consumption is {memory_usage} percent with {memory_available} megabytes remaining. "
            f"Storage utilization is {disk_usage} percent with {disk_free} gigabytes of free space available. "
            f"All systems are operating within normal parameters."
        )
    else:
        # Standard response
        report = (
            f"System check: CPU usage is at {cpu_usage} percent. "
            f"Memory usage is at {memory_usage} percent, with {memory_available} megabytes available. "
            f"Disk usage is at {disk_usage} percent, with {disk_free} gigabytes free."
        )
    
    feedback = speak(report, "system_check", get_feedback=True)
    rl_engine.record_interaction("system check", "system_check", feedback, 
                                {"cpu": cpu_usage, "memory": memory_usage}, True)

# Function to open a folder (unchanged but with learning)
def open_folder(folder_path):
    system = platform.system()
    if not os.path.exists(folder_path):
        speak(f"Sorry, the folder {folder_path} does not exist.")
        rl_engine.record_interaction(f"open folder {folder_path}", "error", -1, 
                                    {"folder_exists": False}, False)
        return
    
    if not os.path.isdir(folder_path):
        speak(f"Sorry, {folder_path} is not a folder.")
        rl_engine.record_interaction(f"open folder {folder_path}", "error", -1, 
                                    {"is_directory": False}, False)
        return
    
    try:
        if system == "Windows":
            os.startfile(folder_path)
        elif system == "Darwin":
            subprocess.run(["open", folder_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            speak("Sorry, I don't support opening folders on this operating system yet.")
            return
        
        feedback = speak(f"Opening folder {folder_path}", "folder_open", get_feedback=True)
        rl_engine.record_interaction(f"open folder {folder_path}", "folder_open", feedback, 
                                    {"system": system}, True)
    except Exception as e:
        speak(f"An error occurred while trying to open the folder: {str(e)}")
        rl_engine.record_interaction(f"open folder {folder_path}", "error", -1, 
                                    {"error": str(e)}, False)

# Enhanced describe topic with learning
def describe_topic(topic):
    try:
        # Check user preference for description length
        personalized_response = rl_engine.get_personalized_response("describe", {"topic": topic})
        
        if personalized_response != "default":
            sentences = 4 if "detailed" in personalized_response else 2
        else:
            sentences = 2
        
        summary = wikipedia.summary(topic, sentences=sentences)
        feedback = speak(f"Here's information about {topic}: {summary}", "description", get_feedback=True)
        rl_engine.record_interaction(f"describe {topic}", "description", feedback, 
                                    {"sentences": sentences, "topic": topic}, True)
    except wikipedia.exceptions.DisambiguationError:
        speak(f"There are multiple entries for {topic}. Please be more specific.")
        rl_engine.record_interaction(f"describe {topic}", "disambiguation", 0, 
                                    {"topic": topic}, False)
    except wikipedia.exceptions.PageError:
        speak(f"Sorry, I couldn't find information about {topic} on Wikipedia.")
        rl_engine.record_interaction(f"describe {topic}", "not_found", -1, 
                                    {"topic": topic}, False)
    except Exception as e:
        speak("An error occurred while fetching the description.")
        rl_engine.record_interaction(f"describe {topic}", "error", -1, 
                                    {"error": str(e)}, False)

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
    
    speak(report, "learning_stats")

# Function to open applications (enhanced with learning)
def open_application(app_name):
    app_name = app_name.lower()
    system = platform.system()
    
    app_dict = {
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
        "safari": {"Darwin": "Safari.app"},
        "terminal": {"Darwin": "Terminal.app", "Linux": "gnome-terminal"},
        "finder": {"Darwin": "Finder.app"},
        "gedit": {"Linux": "gedit"}
    }
    
    try:
        if app_name in app_dict:
            if system in app_dict[app_name]:
                executable = app_dict[app_name][system]
                feedback = speak(f"Opening {app_name}", "app_open", get_feedback=True)
                
                if system == "Windows":
                    try:
                        subprocess.Popen(executable)
                        success = True
                    except:
                        program_files = os.environ.get('ProgramFiles')
                        program_files_x86 = os.environ.get('ProgramFiles(x86)')
                        
                        possible_paths = []
                        if program_files:
                            possible_paths.append(program_files)
                        if program_files_x86:
                            possible_paths.append(program_files_x86)
                        
                        success = False
                        for path in possible_paths:
                            for root, dirs, files in os.walk(path):
                                if executable.lower() in [f.lower() for f in files]:
                                    full_path = os.path.join(root, executable)
                                    subprocess.Popen(full_path)
                                    success = True
                                    break
                            if success:
                                break
                        
                        if not success:
                            subprocess.Popen(app_name)
                            success = True
                            
                elif system == "Darwin":
                    subprocess.run(["open", "-a", executable])
                    success = True
                elif system == "Linux":
                    subprocess.Popen([executable])
                    success = True
                
                rl_engine.record_interaction(f"open {app_name}", "app_open", feedback, 
                                           {"app": app_name, "system": system}, success)
            else:
                speak(f"Sorry, I don't know how to open {app_name} on your operating system.")
                rl_engine.record_interaction(f"open {app_name}", "unsupported_os", -1, 
                                           {"app": app_name, "system": system}, False)
        else:
            feedback = speak(f"Trying to open {app_name}", "app_open_attempt", get_feedback=True)
            
            success = False
            if system == "Windows":
                try:
                    subprocess.Popen([f"{app_name}.exe"])
                    success = True
                except:
                    pass
            elif system == "Darwin":
                try:
                    subprocess.run(["open", "-a", f"{app_name}"])
                    success = True
                except:
                    pass
            elif system == "Linux":
                try:
                    subprocess.Popen([app_name])
                    success = True
                except:
                    pass
            
            if not success:
                speak(f"I couldn't find the application {app_name}.")
                feedback = -1
            
            rl_engine.record_interaction(f"open {app_name}", "app_open_attempt", feedback, 
                                       {"app": app_name, "system": system}, success)
            
    except Exception as e:
        speak(f"An error occurred while trying to open {app_name}: {str(e)}")
        rl_engine.record_interaction(f"open {app_name}", "error", -1, 
                                   {"app": app_name, "error": str(e)}, False)

# Enhanced deep search with learning
def deep_search(query):
    feedback = speak(f"Initiating deep search for {query}", "deep_search_start", get_feedback=True)
    
    try:
        wiki_summary = wikipedia.summary(query, sentences=4)
        speak(f"From Wikipedia: {wiki_summary}")
    except:
        speak("No Wikipedia information found for this query.")
    
    google_url = f"https://www.google.com/search?q={query}"
    speak("Opening Google search results")
    webbrowser.open(google_url)
    
    linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={query}"
    speak("Opening LinkedIn search results")
    webbrowser.open(linkedin_url)
    
    twitter_url = f"https://twitter.com/search?q={query}"
    speak("Opening Twitter search results")
    webbrowser.open(twitter_url)
    
    final_feedback = speak("Deep search completed.", "deep_search_complete", get_feedback=True)
    
    rl_engine.record_interaction(f"deep search {query}", "deep_search", 
                               (feedback + final_feedback) / 2, {"query": query}, True)

# Variable to track deep search mode
deep_search_mode = False

# Enhanced command processing with learning
def process_command(command):
    global deep_search_mode
    
    context = {
        "timestamp": datetime.datetime.now().isoformat(),
        "deep_search_mode": deep_search_mode
    }
    
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True
        
    if "hello" in command:
        feedback = speak("Hello! How can I assist you today?", "greeting", get_feedback=True)
        rl_engine.record_interaction(command, "greeting", feedback, context, True)
    
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        feedback = speak(f"The current time is {current_time}", "time_info", get_feedback=True)
        rl_engine.record_interaction(command, "time_info", feedback, context, True)
    
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        feedback = get_user_feedback()
        rl_engine.record_interaction(command, "open_website", feedback, context, True)
    
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
        feedback = get_user_feedback()
        rl_engine.record_interaction(command, "open_website", feedback, context, True)
    
    elif "search on google" in command or "on google" in command:
        speak("What would you like me to search for?")
        query = listen()
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            feedback = speak(f"Searching for {query} on the web.", "web_search", get_feedback=True)
            rl_engine.record_interaction(f"{command} {query}", "web_search", feedback, 
                                       {**context, "query": query}, True)
    
    elif "on youtube" in command or "search on youtube" in command:
        speak("What would you like to watch on YouTube?")
        query = listen()
        if query:
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            feedback = speak(f"Searching for {query} on YouTube.", "youtube_search", get_feedback=True)
            rl_engine.record_interaction(f"{command} {query}", "youtube_search", feedback, 
                                       {**context, "query": query}, True)

    elif "on wikipedia" in command or "search on wikipedia" in command:
        speak("What would you like to know about?")
        query = listen()
        if query:
            try:
                result = wikipedia.summary(query, sentences=2)
                feedback = speak(result, "wikipedia_search", get_feedback=True)
                rl_engine.record_interaction(f"{command} {query}", "wikipedia_search", feedback, 
                                           {**context, "query": query}, True)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("There are multiple results. Please be more specific.")
                rl_engine.record_interaction(f"{command} {query}", "disambiguation", 0, 
                                           {**context, "query": query}, False)
            except wikipedia.exceptions.PageError as e:
                speak("I couldn't find any information on that topic.")
                rl_engine.record_interaction(f"{command} {query}", "not_found", -1, 
                                           {**context, "query": query}, False)
    
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
        app_name = None
        
        for phrase in ["open application", "open app", "launch"]:
            if phrase in command:
                parts = command.split(phrase)
                if len(parts) > 1 and parts[1].strip():
                    app_name = parts[1].strip()
                    break
        
        if not app_name:
            speak("Which application would you like me to open?")
            app_name = listen()
            
        if app_name:
            open_application(app_name)
            
    elif command.startswith("open ") and "folder" not in command and "youtube" not in command and "google" not in command:
        app_name = command.replace("open ", "").strip()
        open_application(app_name)

    elif "describe" in command or "tell me about" in command:
        speak("What topic would you like me to describe?")
        topic = listen()
        if topic:
            describe_topic(topic)
    
    elif "learning stats" in command or "show learning" in command or "my stats" in command:
        show_learning_stats()
    
    elif "activate deep search" in command:
        deep_search_mode = True
        speak("Deep search mode activated. What would you like to search for?")
        rl_engine.record_interaction(command, "mode_change", 1, context, True)
    
    elif "deactivate deep search" in command or "exit deep search" in command or "stop deep search" in command:
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
            rl_engine.record_interaction(command, "mode_change", 1, context, True)
        else:
            speak("Deep search mode is not currently active.")
            rl_engine.record_interaction(command, "mode_change", 0, context, False)
            
    elif "deep search" in command and not deep_search_mode:
        query = None
        parts = command.split("deep search")
        if len(parts) > 1 and parts[1].strip():
            query = parts[1].strip()
        
        if not query:
            speak("What would you like me to search for?")
            query = listen()
            
        if query:
            deep_search(query)
    
    elif "reset learning" in command or "clear learning" in command:
        rl_engine.q_table.clear()
        rl_engine.user_preferences.clear()
        rl_engine.interaction_history.clear()
        speak("Learning data has been reset. I'll start learning fresh.")
        rl_engine.record_interaction(command, "reset", 1, context, True)

    elif "exit" in command or "stop" in command:
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
        
        # Save learning data before exit
        rl_engine.save_learning_data()
        speak("Goodbye! I've saved everything I learned from our conversation.")
        return False
    else:
        feedback = speak("I'm not sure how to help with that yet. Try asking something else!", "unknown", get_feedback=True)
        rl_engine.record_interaction(command, "unknown", feedback, context, False)
    
    return True

# Function to hear and process folder path
def hear_folder_path():
    path = listen()
    if path:
        path = path.replace("backslash", "\\").replace("slash", "/").replace("dot", ".")
        return path
    return ""

# Enhanced main loop with learning initialization
def virtual_assistant():
    print("Initializing Trinity AI Assistant with Reinforcement Learning...")
    
    # Load existing learning data
    if os.path.exists(rl_engine.data_dir):
        stats = rl_engine.get_learning_summary()
        if stats['total_interactions'] > 0:
            print(f"Loaded {stats['total_interactions']} previous interactions and {stats['learned_preferences']} preferences.")
    
    greet_user()
    speak("I am Trinity, your AI assistant with learning capabilities. I remember our past interactions and adapt to your preferences. How can I help you?")
    
    running = True
    
    # Auto-save learning data every 5 minutes
    def auto_save():
        while running:
            time.sleep(300)  # 5 minutes
            if running:
                rl_engine.save_learning_data()
                print("Auto-saved learning data...")
    
    # Start auto-save thread
    save_thread = threading.Thread(target=auto_save, daemon=True)
    save_thread.start()
    
    while running:
        command = listen()
        if command:
            running = process_command(command)
    
    # Final save on exit
    rl_engine.save_learning_data()
    print("Learning data saved successfully.")

if __name__ == "__main__":
    virtual_assistant()