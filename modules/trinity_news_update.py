# V 1.9.16
# Added news updates feature - morning briefing and on-demand news
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

# random sentences:
RANDOM_SEN = [""]

# News API configuration (you'll need to get a free API key from newsapi.org)
NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"  # Replace with your actual API key
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

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

# the command function for interaction:
def process_command(command):
    global deep_search_mode
    
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
            wiki_result = search_wikipedia(query, sentences=2)
            if wiki_result:
                speak(wiki_result)
            else:
                speak("I couldn't find any information on that topic.")
    
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
    speak("I am Trinity, your virtual assistant. How can I help you?")
    
    # Check for morning briefing
    briefing_offered = check_morning_briefing()
    
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

# main program initializing:
if __name__ == "__main__":
    virtual_assistant()