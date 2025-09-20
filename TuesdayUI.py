import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
import queue
import pyttsx3
from tuesdaylogic import run_tuesday_logic, talk, update_ui_output, update_ui_user_command
import tuesdaylogic

# TTS queue for main-thread speech
tts_queue = queue.Queue()
tts_engine = None

def init_tts_engine():
    global tts_engine
    if tts_engine is None:
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 170)
        voices = tts_engine.getProperty('voices')
        female_voice = None
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                female_voice = voice.id
                break
        if female_voice:
            tts_engine.setProperty('voice', female_voice)
        else:
            tts_engine.setProperty('voice', voices[0].id)

def process_tts_queue():
    """Continuously processes the TTS queue to speak responses."""
    while not tts_queue.empty():
        text = tts_queue.get()
        if tts_engine:
            tts_engine.say(text)
           # tts_engine.runAndWait()
    root.after(100, process_tts_queue)  # Re-run every 100ms to keep the queue processing.

def wake_word_listener(root, activate_callback):
    """Listen for the wake word 'wake up buddy' to activate the assistant."""
    def listen_for_wake_word():
        recognizer = sr.Recognizer()
        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("Listening for wake word...")
                    audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                if "wake up buddy" in text:
                    print("Wake word detected!")
                    root.after(0, activate_callback)
                    break
            except Exception as e:
                print(f"Wake word error: {e}")

    # Start listening in a background thread
    threading.Thread(target=listen_for_wake_word, daemon=True).start()

def main():
    global root
    root = tk.Tk()
    root.title("Tuesday Voice Assistant")
    root.geometry("700x540")
    root.configure(bg="#181818")
    root.withdraw()

    # Initialize the TTS engine
    init_tts_engine()

    # Header
    header = tk.Frame(root, bg="#232323", height=60)
    header.pack(fill=tk.X)
    icon = tk.Label(header, text="🟣", font=("Arial", 28), bg="#232323", fg="#b366ff")
    icon.pack(side=tk.LEFT, padx=15, pady=10)
    title = tk.Label(header, text="Tuesday Voice Assistant", font=("Arial", 18, "bold"), bg="#232323", fg="#e6e6e6")
    title.pack(side=tk.LEFT, padx=5)

    # Chat Box
    chat_frame = tk.Frame(root, bg="#232323", bd=2, relief="groove")
    chat_frame.pack(padx=18, pady=(18,8), fill=tk.BOTH, expand=True)

    chat_box = scrolledtext.ScrolledText(chat_frame, height=15, font=("Consolas", 12), wrap=tk.WORD,
                                         bg="#1a1a1a", fg="#e6e6e6", insertbackground="white", bd=0, relief="flat")
    chat_box.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
    chat_box.tag_config("user", foreground="#00ccff", font=("Consolas", 12, "bold"))
    chat_box.tag_config("assistant", foreground="#b366ff", font=("Consolas", 12, "bold"))
    chat_box.tag_config("system", foreground="#ffcc00", font=("Consolas", 11, "italic"))

    # Input area for user text
    input_frame = tk.Frame(root, bg="#181818")
    input_frame.pack(fill=tk.X, padx=18, pady=(0,8))

    user_box = tk.Text(input_frame, height=3, font=("Consolas", 12), bg="#232323", fg="#888888", insertbackground="white", bd=0, relief="flat")
    user_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
    user_box.insert("1.0", "Type your command here...")

    # Placeholder functions for text input behavior
    def on_entry_click(event):
        if user_box.get("1.0", tk.END).strip() == "Type your command here...":
            user_box.delete("1.0", tk.END)
            user_box.config(fg="#ffffff")

    def on_focusout(event):
        if user_box.get("1.0", tk.END).strip() == "":
            user_box.insert("0.5", "Type your command here...")
            user_box.config(fg="#888888")

    user_box.bind('<FocusIn>', on_entry_click)
    user_box.bind('<FocusOut>', on_focusout)

    # Button panel for Send and Microphone
    button_frame = tk.Frame(input_frame, bg="#181818")
    button_frame.pack(side=tk.RIGHT)

    def update_ui_output_func(text):
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"\n🟣 Tuesday: {text}\n", "assistant")
        chat_box.see(tk.END)
        chat_box.config(state=tk.DISABLED)
        tts_queue.put(text)  # Add response to TTS queue

    def update_ui_user_command_func(text):
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"\n🗣️ You said: {text}\n", "user")
        chat_box.see(tk.END)
        chat_box.config(state=tk.DISABLED)

    # Connect UI callbacks to logic
    tuesdaylogic.update_ui_output = update_ui_output_func
    tuesdaylogic.update_ui_user_command = update_ui_user_command_func

    # Send button to submit text command
    def send_command():
        user_text = user_box.get(1.0, tk.END).strip()
        if user_text and user_text != "Type your command here...":
            threading.Thread(target=run_tuesday_logic, args=(user_text,)).start()
            user_box.delete(1.0, tk.END)
            user_box.insert("0.5", "Type your command here...")
            user_box.config(fg="#888888")

    # Mic button to listen to voice command
    def listen_command():
        threading.Thread(target=run_tuesday_logic).start()

    mic_button = tk.Button(button_frame, text="🎙️ Speak", font=("Arial", 12, "bold"), bg="#232323", fg="#00ccff",
                           activebackground="#262626", activeforeground="#00e6e6", command=listen_command, bd=0, relief="flat", padx=16, pady=6)
    mic_button.grid(row=0, column=0, padx=4)

    send_button = tk.Button(button_frame, text="➡️ Send", font=("Arial", 12, "bold"), bg="#232323", fg="#b366ff",
                            activebackground="#262626", activeforeground="#b366ff", command=send_command, bd=0, relief="flat", padx=16, pady=6)
    send_button.grid(row=0, column=1, padx=4)

    def activate_ui():
        root.deiconify()
        talk("I'm Tuesday – your personal voice and text assistant.")

    # Start wake word listener
    wake_word_listener(root, activate_ui)

    # Process TTS queue continuously
    process_tts_queue()

    root.mainloop()

if __name__ == "__main__":
    main()