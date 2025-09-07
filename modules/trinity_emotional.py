# V 1.9.16
# Added Emotional Intelligence Mode
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
import random

# random sentences:
RANDOM_SEN = [""]

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

# Variables to track modes
deep_search_mode = False
emotional_intelligence_mode = False

# the command function for interaction:
def process_command(command):
    global deep_search_mode, emotional_intelligence_mode
    
    # Check for emotional content first if EI mode is active
    if emotional_intelligence_mode:
        emotions = detect_emotion(command)
        if emotions:
            emotional_response = provide_emotional_response(emotions)
            if emotional_response:
                speak(emotional_response)
                
                # Offer additional support for negative emotions
                negative_emotions = ['sad', 'anxious', 'angry', 'lonely', 'confused', 'tired']
                if any(emotion in negative_emotions for emotion in emotions):
                    speak("I'm here to support you. Would you like me to help you feel better?")
                    return True
    
    # Check if deep search mode is active
    if deep_search_mode and not any(x in command for x in ["deactivate deep search", "exit deep search", "stop deep search", "exit", "stop"]):
        deep_search(command)
        return True
        
    if "hello" in command:
        if emotional_intelligence_mode:
            speak("Hello! I'm here to help and support you. How are you feeling today?")
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
    
    elif "how are you" in command:
        if emotional_intelligence_mode:
            speak("Thank you for asking! I'm doing well and I'm here to support you. More importantly, how are you feeling today? I care about your wellbeing.")
        else:
            speak("I'm functioning well, thank you! How can I help you today?")

    elif "exit" in command or "stop" in command:
        # Reset all modes if they're active
        if deep_search_mode:
            deep_search_mode = False
            speak("Deep search mode deactivated.")
        if emotional_intelligence_mode:
            emotional_intelligence_mode = False
            speak("Thank you for sharing this time with me. Remember to take care of yourself.")
        else:
            speak("Goodbye!")
        return False
    else:
        if emotional_intelligence_mode:
            speak("I'm not sure how to help with that specific request, but I'm here for you. Is there something else I can assist you with, or would you like to talk about how you're feeling?")
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
    speak("I am Trinity, your virtual assistant. I can help you with tasks and provide emotional support when needed. How can I help you?")
    speak("You can say 'activate emotional intelligence' to enable empathetic responses, or 'activate deep search' for comprehensive research.")
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

# main program initializing:
if __name__ == "__main__":
    virtual_assistant()