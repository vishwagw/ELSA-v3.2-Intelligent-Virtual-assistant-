# V 1.9.15
# Added smart home device control mode
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

# Smart Home Device Control System
class SmartHomeController:
    def __init__(self):
        # Configuration file for smart home devices
        self.config_file = "smart_home_config.json"
        self.devices = self.load_device_config()
        
    def load_device_config(self):
        """Load device configuration from JSON file"""
        default_config = {
            "lights": {
                "living_room": {"status": "off", "brightness": 50, "color": "white"},
                "bedroom": {"status": "off", "brightness": 50, "color": "white"},
                "kitchen": {"status": "off", "brightness": 70, "color": "white"},
                "bathroom": {"status": "off", "brightness": 40, "color": "white"}
            },
            "thermostat": {
                "temperature": 72,
                "mode": "auto",
                "fan": "auto"
            },
            "security": {
                "alarm": "disarmed",
                "cameras": "off",
                "door_locks": "locked"
            },
            "entertainment": {
                "tv": {"status": "off", "channel": 1, "volume": 50},
                "music_system": {"status": "off", "volume": 30, "source": "bluetooth"}
            },
            "appliances": {
                "coffee_maker": "off",
                "dishwasher": "off",
                "washing_machine": "off",
                "garage_door": "closed"
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                self.save_device_config(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def save_device_config(self, config=None):
        """Save device configuration to JSON file"""
        try:
            config_to_save = config if config else self.devices
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def control_lights(self, room, action, value=None):
        """Control smart lights"""
        if room not in self.devices["lights"]:
            speak(f"I don't recognize the {room}. Available rooms are: {', '.join(self.devices['lights'].keys())}")
            return
        
        if action in ["on", "turn on"]:
            self.devices["lights"][room]["status"] = "on"
            speak(f"Turning on the {room} lights")
        elif action in ["off", "turn off"]:
            self.devices["lights"][room]["status"] = "off"
            speak(f"Turning off the {room} lights")
        elif action in ["dim", "brightness"]:
            if value:
                try:
                    brightness = int(value)
                    if 0 <= brightness <= 100:
                        self.devices["lights"][room]["brightness"] = brightness
                        self.devices["lights"][room]["status"] = "on" if brightness > 0 else "off"
                        speak(f"Setting {room} lights to {brightness} percent brightness")
                    else:
                        speak("Brightness should be between 0 and 100 percent")
                except ValueError:
                    speak("Please specify a valid brightness level")
            else:
                speak("Please specify the brightness level")
        elif action in ["color", "change color"]:
            if value:
                self.devices["lights"][room]["color"] = value
                self.devices["lights"][room]["status"] = "on"
                speak(f"Changing {room} lights to {value}")
            else:
                speak("Please specify a color")
        
        self.save_device_config()
    
    def control_thermostat(self, action, value=None):
        """Control smart thermostat"""
        if action in ["temperature", "set temperature"]:
            if value:
                try:
                    temp = int(value)
                    if 60 <= temp <= 85:
                        self.devices["thermostat"]["temperature"] = temp
                        speak(f"Setting thermostat to {temp} degrees")
                    else:
                        speak("Temperature should be between 60 and 85 degrees")
                except ValueError:
                    speak("Please specify a valid temperature")
            else:
                speak("Please specify the temperature")
        elif action in ["mode"]:
            if value and value in ["heat", "cool", "auto", "off"]:
                self.devices["thermostat"]["mode"] = value
                speak(f"Setting thermostat mode to {value}")
            else:
                speak("Available modes are: heat, cool, auto, or off")
        elif action in ["status", "check"]:
            temp = self.devices["thermostat"]["temperature"]
            mode = self.devices["thermostat"]["mode"]
            speak(f"Thermostat is set to {temp} degrees in {mode} mode")
        
        self.save_device_config()
    
    def control_security(self, device, action):
        """Control security devices"""
        if device == "alarm":
            if action in ["arm", "activate"]:
                self.devices["security"]["alarm"] = "armed"
                speak("Security alarm is now armed")
            elif action in ["disarm", "deactivate"]:
                self.devices["security"]["alarm"] = "disarmed"
                speak("Security alarm is now disarmed")
        elif device == "cameras":
            if action in ["on", "activate"]:
                self.devices["security"]["cameras"] = "on"
                speak("Security cameras are now active")
            elif action in ["off", "deactivate"]:
                self.devices["security"]["cameras"] = "off"
                speak("Security cameras are now off")
        elif device in ["doors", "door locks"]:
            if action in ["lock"]:
                self.devices["security"]["door_locks"] = "locked"
                speak("All doors are now locked")
            elif action in ["unlock"]:
                self.devices["security"]["door_locks"] = "unlocked"
                speak("All doors are now unlocked")
        
        self.save_device_config()
    
    def control_entertainment(self, device, action, value=None):
        """Control entertainment devices"""
        if device == "tv":
            if action in ["on", "turn on"]:
                self.devices["entertainment"]["tv"]["status"] = "on"
                speak("Turning on the TV")
            elif action in ["off", "turn off"]:
                self.devices["entertainment"]["tv"]["status"] = "off"
                speak("Turning off the TV")
            elif action in ["volume"]:
                if value:
                    try:
                        vol = int(value)
                        if 0 <= vol <= 100:
                            self.devices["entertainment"]["tv"]["volume"] = vol
                            speak(f"Setting TV volume to {vol}")
                        else:
                            speak("Volume should be between 0 and 100")
                    except ValueError:
                        speak("Please specify a valid volume level")
            elif action in ["channel"]:
                if value:
                    try:
                        ch = int(value)
                        self.devices["entertainment"]["tv"]["channel"] = ch
                        speak(f"Changing TV to channel {ch}")
                    except ValueError:
                        speak("Please specify a valid channel number")
        
        elif device in ["music", "music system"]:
            if action in ["on", "turn on", "play"]:
                self.devices["entertainment"]["music_system"]["status"] = "on"
                speak("Turning on the music system")
            elif action in ["off", "turn off", "stop"]:
                self.devices["entertainment"]["music_system"]["status"] = "off"
                speak("Turning off the music system")
            elif action in ["volume"]:
                if value:
                    try:
                        vol = int(value)
                        if 0 <= vol <= 100:
                            self.devices["entertainment"]["music_system"]["volume"] = vol
                            speak(f"Setting music volume to {vol}")
                        else:
                            speak("Volume should be between 0 and 100")
                    except ValueError:
                        speak("Please specify a valid volume level")
        
        self.save_device_config()
    
    def control_appliances(self, appliance, action):
        """Control smart appliances"""
        appliance_map = {
            "coffee maker": "coffee_maker",
            "coffee": "coffee_maker",
            "dishwasher": "dishwasher",
            "washing machine": "washing_machine",
            "washer": "washing_machine",
            "garage door": "garage_door",
            "garage": "garage_door"
        }
        
        device_key = appliance_map.get(appliance, appliance)
        
        if device_key in self.devices["appliances"]:
            if action in ["on", "start", "turn on"]:
                if device_key == "garage_door":
                    self.devices["appliances"][device_key] = "open"
                    speak("Opening garage door")
                else:
                    self.devices["appliances"][device_key] = "on"
                    speak(f"Starting the {appliance}")
            elif action in ["off", "stop", "turn off"]:
                if device_key == "garage_door":
                    self.devices["appliances"][device_key] = "closed"
                    speak("Closing garage door")
                else:
                    self.devices["appliances"][device_key] = "off"
                    speak(f"Stopping the {appliance}")
        else:
            speak(f"I don't recognize the {appliance}")
        
        self.save_device_config()
    
    def get_device_status(self, category=None):
        """Get status of all devices or specific category"""
        if category:
            if category in self.devices:
                speak(f"Here's the status of your {category}:")
                for device, status in self.devices[category].items():
                    if isinstance(status, dict):
                        status_str = ", ".join([f"{k}: {v}" for k, v in status.items()])
                        speak(f"{device}: {status_str}")
                    else:
                        speak(f"{device}: {status}")
            else:
                speak(f"I don't have information about {category}")
        else:
            speak("Here's the status of all your smart home devices:")
            for category, devices in self.devices.items():
                speak(f"{category}:")
                for device, status in devices.items():
                    if isinstance(status, dict):
                        key_status = status.get('status', list(status.values())[0])
                        speak(f"  {device}: {key_status}")
                    else:
                        speak(f"  {device}: {status}")

# Variables to track modes
deep_search_mode = False
smart_home_mode = False
smart_home_controller = SmartHomeController()

# Enhanced command function with smart home integration
def process_command(command):
    global deep_search_mode, smart_home_mode, smart_home_controller
    
    # Check if smart home mode is active
    if smart_home_mode and not any(x in command for x in ["deactivate smart home", "exit smart home", "stop smart home", "exit", "stop"]):
        process_smart_home_command(command)
        return True
    
    # Check if deep search mode is active
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True
        
    if "hello" in command:
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
    
    # Smart Home commands
    elif "activate smart home" in command or "smart home mode" in command:
        smart_home_mode = True
        speak("Smart home control mode activated. You can now control your smart devices. Say 'help' for available commands.")
    
    elif "deactivate smart home" in command or "exit smart home" in command or "stop smart home" in command:
        if smart_home_mode:
            smart_home_mode = False
            speak("Smart home control mode deactivated.")
        else:
            speak("Smart home control mode is not currently active.")

    elif "exit" in command or "stop" in command:
        # Reset modes if they're active
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
        if smart_home_mode:
            smart_home_mode = False
            speak("Smart home control mode deactivated.")
        speak("Goodbye!")
        return False
    else:
        speak("I'm not sure how to help with that yet. Try asking something else!")
    return True

def process_smart_home_command(command):
    """Process smart home specific commands"""
    global smart_home_controller
    
    if "help" in command:
        help_text = """
        Smart Home Commands:
        Lights: 'turn on living room lights', 'dim bedroom lights to 50', 'change kitchen lights to blue'
        Thermostat: 'set temperature to 72', 'change mode to heat', 'check thermostat'
        Security: 'arm alarm', 'turn on cameras', 'lock doors'
        TV: 'turn on TV', 'change channel to 5', 'set TV volume to 30'
        Music: 'play music', 'set music volume to 50'
        Appliances: 'start coffee maker', 'open garage door'
        Status: 'device status', 'light status', 'security status'
        """
        speak(help_text)
    
    # Light controls
    elif any(word in command for word in ["light", "lights"]):
        rooms = ["living room", "bedroom", "kitchen", "bathroom"]
        room = None
        for r in rooms:
            if r in command:
                room = r.replace(" ", "_")
                break
        
        if not room:
            speak("Which room's lights would you like to control?")
            room_response = listen()
            if room_response:
                for r in rooms:
                    if r in room_response:
                        room = r.replace(" ", "_")
                        break
        
        if room:
            if "on" in command or "turn on" in command:
                smart_home_controller.control_lights(room, "on")
            elif "off" in command or "turn off" in command:
                smart_home_controller.control_lights(room, "off")
            elif "dim" in command or "brightness" in command:
                # Extract brightness value
                words = command.split()
                brightness = None
                for i, word in enumerate(words):
                    if word.isdigit():
                        brightness = word
                        break
                    elif i < len(words) - 1 and words[i+1].isdigit():
                        brightness = words[i+1]
                        break
                
                if not brightness:
                    speak("What brightness level? Say a number between 0 and 100.")
                    brightness_response = listen()
                    if brightness_response:
                        words = brightness_response.split()
                        for word in words:
                            if word.isdigit():
                                brightness = word
                                break
                
                smart_home_controller.control_lights(room, "brightness", brightness)
            elif "color" in command or "change color" in command:
                colors = ["red", "blue", "green", "yellow", "purple", "orange", "white", "warm white"]
                color = None
                for c in colors:
                    if c in command:
                        color = c
                        break
                
                if not color:
                    speak("What color would you like? Available colors are red, blue, green, yellow, purple, orange, white, or warm white.")
                    color_response = listen()
                    if color_response:
                        for c in colors:
                            if c in color_response:
                                color = c
                                break
                
                smart_home_controller.control_lights(room, "color", color)
        else:
            speak("I couldn't identify which room you're referring to.")
    
    # Thermostat controls
    elif "thermostat" in command or "temperature" in command:
        if "set" in command or "change" in command:
            # Extract temperature value
            words = command.split()
            temp = None
            for word in words:
                if word.isdigit():
                    temp = word
                    break
            
            if not temp:
                speak("What temperature would you like to set?")
                temp_response = listen()
                if temp_response:
                    words = temp_response.split()
                    for word in words:
                        if word.isdigit():
                            temp = word
                            break
            
            smart_home_controller.control_thermostat("temperature", temp)
        elif "mode" in command:
            modes = ["heat", "cool", "auto", "off"]
            mode = None
            for m in modes:
                if m in command:
                    mode = m
                    break
            
            if not mode:
                speak("What mode would you like? Heat, cool, auto, or off?")
                mode_response = listen()
                if mode_response:
                    for m in modes:
                        if m in mode_response:
                            mode = m
                            break
            
            smart_home_controller.control_thermostat("mode", mode)
        elif "check" in command or "status" in command:
            smart_home_controller.control_thermostat("status")
    
    # Security controls
    elif "alarm" in command:
        if "arm" in command or "activate" in command:
            smart_home_controller.control_security("alarm", "arm")
        elif "disarm" in command or "deactivate" in command:
            smart_home_controller.control_security("alarm", "disarm")
    
    elif "camera" in command or "cameras" in command:
        if "on" in command or "activate" in command:
            smart_home_controller.control_security("cameras", "on")
        elif "off" in command or "deactivate" in command:
            smart_home_controller.control_security("cameras", "off")
    
    elif "door" in command or "doors" in command or "lock" in command:
        if "lock" in command:
            smart_home_controller.control_security("doors", "lock")
        elif "unlock" in command:
            smart_home_controller.control_security("doors", "unlock")
    
    # TV controls
    elif "tv" in command or "television" in command:
        if "on" in command or "turn on" in command:
            smart_home_controller.control_entertainment("tv", "on")
        elif "off" in command or "turn off" in command:
            smart_home_controller.control_entertainment("tv", "off")
        elif "volume" in command:
            words = command.split()
            volume = None
            for word in words:
                if word.isdigit():
                    volume = word
                    break
            
            if not volume:
                speak("What volume level?")
                volume_response = listen()
                if volume_response:
                    words = volume_response.split()
                    for word in words:
                        if word.isdigit():
                            volume = word
                            break
            
            smart_home_controller.control_entertainment("tv", "volume", volume)
        elif "channel" in command:
            words = command.split()
            channel = None
            for word in words:
                if word.isdigit():
                    channel = word
                    break
            
            if not channel:
                speak("What channel number?")
                channel_response = listen()
                if channel_response:
                    words = channel_response.split()
                    for word in words:
                        if word.isdigit():
                            channel = word
                            break
            
            smart_home_controller.control_entertainment("tv", "channel", channel)
    
    # Music controls
    elif "music" in command:
        if "play" in command or "on" in command or "turn on" in command:
            smart_home_controller.control_entertainment("music", "on")
        elif "stop" in command or "off" in command or "turn off" in command:
            smart_home_controller.control_entertainment("music", "off")
        elif "volume" in command:
            words = command.split()
            volume = None
            for word in words:
                if word.isdigit():
                    volume = word
                    break
            
            if not volume:
                speak("What volume level?")
                volume_response = listen()
                if volume_response:
                    words = volume_response.split()
                    for word in words:
                        if word.isdigit():
                            volume = word
                            break
            
            smart_home_controller.control_entertainment("music", "volume", volume)
    
    # Appliance controls
    elif "coffee" in command:
        if "start" in command or "on" in command or "make" in command:
            smart_home_controller.control_appliances("coffee", "on")
        elif "stop" in command or "off" in command:
            smart_home_controller.control_appliances("coffee", "off")
    
    elif "dishwasher" in command:
        if "start" in command or "on" in command:
            smart_home_controller.control_appliances("dishwasher", "on")
        elif "stop" in command or "off" in command:
            smart_home_controller.control_appliances("dishwasher", "off")
    
    elif "washing machine" in command or "washer" in command:
        if "start" in command or "on" in command:
            smart_home_controller.control_appliances("washing machine", "on")
        elif "stop" in command or "off" in command:
            smart_home_controller.control_appliances("washing machine", "off")
    
    elif "garage" in command:
        if "open" in command:
            smart_home_controller.control_appliances("garage", "on")
        elif "close" in command:
            smart_home_controller.control_appliances("garage", "off")
    
    # Status commands
    elif "status" in command:
        if "light" in command:
            smart_home_controller.get_device_status("lights")
        elif "security" in command:
            smart_home_controller.get_device_status("security")
        elif "thermostat" in command:
            smart_home_controller.get_device_status("thermostat")
        elif "entertainment" in command:
            smart_home_controller.get_device_status("entertainment")
        elif "appliance" in command:
            smart_home_controller.get_device_status("appliances")
        elif "device" in command or "all" in command:
            smart_home_controller.get_device_status()
        else:
            smart_home_controller.get_device_status()
    
    # Scene controls (bonus feature)
    elif "good night" in command or "bedtime" in command:
        speak("Activating bedtime scene")
        smart_home_controller.control_lights("living_room", "off")
        smart_home_controller.control_lights("kitchen", "off")
        smart_home_controller.control_lights("bedroom", "dim", "20")
        smart_home_controller.control_entertainment("tv", "off")
        smart_home_controller.control_entertainment("music", "off")
        smart_home_controller.control_security("doors", "lock")
        smart_home_controller.control_security("alarm", "arm")
        smart_home_controller.control_thermostat("temperature", "68")
        speak("Good night scene activated. All lights dimmed, doors locked, alarm armed, and temperature lowered.")
    
    elif "good morning" in command or "wake up" in command:
        speak("Activating morning scene")
        smart_home_controller.control_lights("bedroom", "on")
        smart_home_controller.control_lights("kitchen", "on")
        smart_home_controller.control_lights("bathroom", "on")
        smart_home_controller.control_security("alarm", "disarm")
        smart_home_controller.control_appliances("coffee", "on")
        smart_home_controller.control_thermostat("temperature", "72")
        speak("Good morning scene activated. Lights turned on, alarm disarmed, coffee maker started, and temperature adjusted.")
    
    elif "movie time" in command or "movie mode" in command:
        speak("Activating movie mode")
        smart_home_controller.control_lights("living_room", "dim", "10")
        smart_home_controller.control_lights("kitchen", "off")
        smart_home_controller.control_entertainment("tv", "on")
        speak("Movie mode activated. Living room lights dimmed and TV turned on.")
    
    elif "party mode" in command:
        speak("Activating party mode")
        smart_home_controller.control_lights("living_room", "on")
        smart_home_controller.control_lights("kitchen", "on")
        smart_home_controller.control_lights("living_room", "color", "blue")
        smart_home_controller.control_entertainment("music", "on")
        smart_home_controller.control_entertainment("music", "volume", "70")
        speak("Party mode activated. Lights are on with colorful ambiance and music is playing.")
    
    else:
        speak("I didn't understand that smart home command. Say 'help' to see available commands.")

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
    speak("I am Trinity, your virtual assistant. How can I help you?")
    speak("You can activate smart home mode by saying 'activate smart home' or deep search mode by saying 'activate deep search'.")
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

if __name__ == "__main__":
    virtual_assistant()