import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import os
import sys
from tkinter import messagebox

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
female_voice = None
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower():
        female_voice = voice.id
        break
if female_voice:
    engine.setProperty('voice', female_voice)
else:
    print("Warning: Female voice not found, using default voice.")
    engine.setProperty('voice', voices[0].id)

# UI callback placeholders
update_ui_output = None
update_ui_user_command = None

def talk(text):
    """Speak and update UI output."""
    if update_ui_output:
        update_ui_output(text)
    engine.say(text)
    engine.runAndWait()

def take_voice_command():
    """Listen for a voice command and return it as text."""
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        if update_ui_output:
            update_ui_output("Listening...")
        listener.adjust_for_ambient_noise(source)
        voice = listener.listen(source)
    try:
        command = listener.recognize_google(voice)
        command = command.lower()
        if update_ui_user_command:
            update_ui_user_command(command)
    except sr.UnknownValueError:
        talk("Sorry, I didn’t catch that.")
        return ""
    except sr.RequestError:
        talk("Network issue with Google service.")
        return ""
    return command

def run_tuesday_logic(command_input=None):
    """Main logic for Tuesday assistant."""
    if command_input is None:
        command = take_voice_command()
    else:
        command = command_input.lower().strip()
        if update_ui_user_command:
            update_ui_user_command(command)
    if not command:
        return

    if "play" in command:
        song = command.replace("play", "").strip()
        talk(f"Playing {song} on YouTube ")
        try:
            pywhatkit.playonyt(song)
        except Exception as e:
            talk(f"Could not play {song}. Error: {e}")

    elif "what's the time" in command or "what is the time" in command or "tell me the time" in command or "current time" in command or "time" in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f"It’s {time} ⏰")

    elif "who is your creator" in command or "who is your developer" in command:
        info = (
            "Arjun, Jagadeesh, Vinod are the developers of me and the investor is Madhu. "
            "They are studying in AANM&VVRSR polytechnic in Gudlavalleru college 💻"
        )
        talk(info)

    elif "who is" in command or "what is" in command:
        person = command.replace("who is", "").strip()
        if person:
            try:
                info = wikipedia.summary(person, sentences=1)
                talk(info)
            except wikipedia.exceptions.PageError:
                talk(f"Sorry, I couldn’t find information about {person}.")
            except wikipedia.exceptions.DisambiguationError as e:
                talk(f"There are multiple results for {person}. Can you be more specific? For example: {e.options[0]}.")
            except Exception as e:
                talk(f"An error occurred while searching Wikipedia: {e}")
        else:
            talk("Please tell me who you want to know about.")

    elif "search for" in command:
        query = command.replace("search for", "").strip()
        if query:
            talk(f"Searching for {query} on Google Chrome 🌐")
            try:
                from selenium import webdriver
                from selenium.webdriver.common.keys import Keys
                from selenium.webdriver.common.by import By
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager

                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service)
                driver.maximize_window()
                driver.get("https://www.google.com")
                search_box = driver.find_element(By.NAME, "q")
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
            except Exception as e:
                talk(f"Could not perform the search in Chrome. Error: {e}")
                messagebox.showerror("Error", f"Could not open Chrome for search. Make sure ChromeDriver is correctly set up. Error: {e}")

    elif "open file manager" in command or "open explorer" in command or "files" in command:
        try:

            talk("Opening File Manager 🗂️")
            os.startfile(os.getcwd())
        except Exception as e:
            talk(f"Could not open File Manager. Error: {e}")

    elif "joke" in command or "tell me a joke" in command:
        talk(pyjokes.get_joke())

    elif "open chrome" in command:
        chrome_path = "C:\\Users\\DELL\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
        if os.path.exists(chrome_path):
            talk("Opening Chrome 🚀")
            os.startfile(chrome_path)
        else:
            talk("Chrome path not found. Please check the path in the code. ")
            messagebox.showerror("Error", "Chrome path not found. Please update 'chrome_path' in the code.")

    elif "open code" in command or "open vs code" in command:
        talk("Opening VS Code 💻")
        try:
            os.system("code")
        except Exception as e:
            talk(f"Could not open VS Code. Make sure 'code' command is in your system's PATH. Error: {e}")
            messagebox.showerror("Error", f"Could not open VS Code. Error: {e}")
    elif "hi" in command or "hello" in command or "hey" in command:
        talk("hello! what can i do for you")
    

    elif "exit" in command or "stop" in command or "quit" in command:
        talk("Okay, see you later ")
        sys.exit()
    else:
        talk("I heard you, but I don’t understand that yet..")