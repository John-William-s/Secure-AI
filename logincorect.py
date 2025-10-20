import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
import speech_recognition as sr
import threading
import json
import hashlib
import os
import subprocess
import sys

# --- Import your actual UI classes ---
from phishing_detector import PhishingDetectorUI
from file_encryptor import FileEncryptorUI
from link_analyzer import LinkAnalyzerUI
from scam_call_analyzer import ScamCallAnalyzerUI


# --- Constants and Configuration ---
WINDOW_BG = "#212121"
FRAME_BG = "#2c2c2c"
TEXT_COLOR = "#FFFFFF"
ENTRY_BG = "#373737"
BUTTON_BG = "#007BFF"
BUTTON_FG = "#FFFFFF"
SUCCESS_COLOR = "#28a745" # Green for success
LISTENING_COLOR = "#ffc107" # Yellow for listening
CLOSE_BUTTON_BG = "#c9302c" # Red for close button
FONT_FAMILY = "Helvetica"
CREDENTIALS_FILE = "credentials.json"

# --- MainDashboard Class (Unchanged) ---
class MainDashboard(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Security Dashboard")
        self.geometry("1000x1000")
        self.configure(bg=WINDOW_BG)
        self.button_font = font.Font(family=FONT_FAMILY, size=14)
        self.desc_font = font.Font(family=FONT_FAMILY, size=10, slant="italic")
        main_frame = tk.Frame(self, bg=WINDOW_BG)
        main_frame.pack(pady=40, padx=60, fill="both", expand=True)
        try:
            logo_image = Image.open("logo.png").resize((400, 300), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(main_frame, image=self.logo_photo, bg=WINDOW_BG)
            logo_label.pack(pady=(0,0))
        except FileNotFoundError:
            print("Dashboard: logo.png not found. Skipping logo display.")
        features_grid = tk.Frame(main_frame, bg=WINDOW_BG)
        features_grid.pack(fill="both", expand=True)
        features_grid.grid_columnconfigure((0, 1), weight=1)
        features_grid.grid_rowconfigure((0, 1), weight=1)
        features = [
            {"icon": "📁", "title": "File Encryptor", "desc": "Securely encrypt and decrypt your files.", "command": self.open_file_encryptor},
            {"icon": "🎣", "title": "Phishing Detector", "desc": "Analyze emails for phishing attempts.", "command": self.open_phishing_detector},
            {"icon": "🔗", "title": "Link Analyzer", "desc": "Check URLs for malicious content.", "command": self.open_link_analyzer},
            {"icon": "📞", "title": "Scam Call Check", "desc": "Verify phone numbers for potential scams.", "command": self.open_scam_checker}
        ]
        for i, feature in enumerate(features):
            row, col = divmod(i, 2)
            button_frame = self.create_feature_button(features_grid, feature)
            button_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
        close_button = tk.Button(main_frame, text="Close Application", font=self.button_font, bg=BUTTON_BG, fg=TEXT_COLOR, activebackground=CLOSE_BUTTON_BG, activeforeground=TEXT_COLOR, relief="flat", cursor="hand2", command=self.master.destroy)
        close_button.pack(side="bottom", pady=(30, 0), ipady=10, fill='x')

    def create_feature_button(self, parent, feature_data):
        frame = tk.Frame(parent, bg=FRAME_BG, relief="raised", borderwidth=2, highlightbackground=BUTTON_BG, highlightthickness=1)
        icon_label = tk.Label(frame, text=feature_data["icon"], font=("Arial", 40), bg=FRAME_BG, fg=BUTTON_BG)
        icon_label.pack(pady=(20, 10))
        title_label = tk.Label(frame, text=feature_data["title"], font=self.button_font, bg=FRAME_BG, fg=TEXT_COLOR)
        title_label.pack(pady=(0, 5))
        desc_label = tk.Label(frame, text=feature_data["desc"], font=self.desc_font, bg=FRAME_BG, fg="#cccccc", wraplength=200)
        desc_label.pack(pady=(0, 20), padx=10)
        for widget in [frame, icon_label, title_label, desc_label]:
            widget.bind("<Button-1>", lambda e, cmd=feature_data["command"]: cmd())
            widget.config(cursor="hand2")
        return frame

    def open_file_encryptor(self):
        encryptor_window = FileEncryptorUI(self)
        encryptor_window.grab_set()

    def open_phishing_detector(self):
        phishing_window = PhishingDetectorUI(self)
        phishing_window.grab_set()

    def open_link_analyzer(self):
        link_analyzer_window = LinkAnalyzerUI(self)
        link_analyzer_window.grab_set()
        
    def open_scam_checker(self): 
        scam_window = ScamCallAnalyzerUI(self)
        scam_window.grab_set()


# --- SecurityApp Class ---
class SecurityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.credentials = self.load_credentials()
        if not self.credentials:
            self.destroy()
            return

        self.title("Security App - Voice Login")
        self.geometry("400x750")
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)

        self.transcribed_word = tk.StringVar()

        # --- Font Definitions ---
        self.title_font = font.Font(family=FONT_FAMILY, size=20, weight="bold")
        self.label_font = font.Font(family=FONT_FAMILY, size=12)
        self.entry_font = font.Font(family=FONT_FAMILY, size=12)
        self.button_font = font.Font(family=FONT_FAMILY, size=14, weight="bold")
        self.status_font = font.Font(family=FONT_FAMILY, size=10, slant="italic")
        self.link_font = font.Font(family=FONT_FAMILY, size=10, underline=True)

        # --- Logo ---
        try:
            logo_image = Image.open("logo.png").resize((400, 300), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(self, image=self.logo_photo, bg=WINDOW_BG)
            logo_label.pack(pady=(20, 10))
        except FileNotFoundError:
            placeholder_label = tk.Label(self, text="🛡️", font=("Arial", 60), bg=WINDOW_BG, fg=BUTTON_BG)
            placeholder_label.pack(pady=(20, 10))

        # --- Login Frame ---
        login_frame = tk.Frame(self, bg=WINDOW_BG)
        login_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # --- Voice Input Section (Unchanged) ---
        magic_word_label = tk.Label(login_frame, text="Magic Word", font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR)
        magic_word_label.pack(anchor="w")

        self.speak_button = tk.Button(
            login_frame, text="🎤 Speak Magic Word", font=self.label_font, bg="#555555",
            fg=TEXT_COLOR, cursor="hand2", relief="flat", command=self.start_listening_thread
        )
        self.speak_button.pack(fill="x", pady=(5, 5), ipady=8)

        self.status_label = tk.Label(
            login_frame, text="Status: Waiting for you to speak...", font=self.status_font, bg=WINDOW_BG, fg=TEXT_COLOR
        )
        self.status_label.pack(anchor="w", pady=(0, 15))

        # --- Password Section ---
        password_label = tk.Label(login_frame, text="Password", font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR)
        password_label.pack(anchor="w")

        self.password_entry = tk.Entry(
            login_frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR, borderwidth=2, relief="flat"
        )
        self.password_entry.pack(fill="x", pady=5, ipady=8)
        self.password_entry.focus_set()

        # --- Show/Hide Password Checkbox ---
        self.show_password_var = tk.BooleanVar()
        show_password_check = tk.Checkbutton(
            login_frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            bg=WINDOW_BG, fg=TEXT_COLOR, selectcolor=ENTRY_BG,
            activebackground=WINDOW_BG, activeforeground=TEXT_COLOR,
            highlightthickness=0, borderwidth=0
        )
        show_password_check.pack(anchor="w")

        # --- Login and Forgot Password Buttons ---
        login_button = tk.Button(
            login_frame, text="Unlock", font=self.button_font, bg=BUTTON_BG, fg=BUTTON_FG,
            activebackground=BUTTON_BG, activeforeground=BUTTON_FG, borderwidth=0,
            relief="flat", cursor="hand2", command=self.attempt_login
        )
        login_button.pack(fill="x", pady=(20, 10), ipady=10)
        
        forgot_password_button = tk.Label(
            login_frame, text="Forgot Password?", font=self.link_font, bg=WINDOW_BG,
            fg="#cccccc", cursor="hand2"
        )
        forgot_password_button.pack(pady=10)
        forgot_password_button.bind("<Button-1>", lambda e: self.show_forgot_password_window())

        self.bind("<Return>", lambda event: self.attempt_login())

    def toggle_password_visibility(self):
        """Changes the password entry field's show property."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def load_credentials(self):
        if not os.path.exists(CREDENTIALS_FILE):
            self.withdraw()
            messagebox.showinfo("First-Time Setup", "Credentials not found. The setup process will now begin.")
            subprocess.run([sys.executable, "setup.py"])
            messagebox.showinfo("Setup Complete", "Setup is complete. Please restart the application.")
            return None

        try:
            with open(CREDENTIALS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Failed to load or parse credentials: {e}")
            return None

    def start_listening_thread(self):
        self.speak_button.config(state=tk.DISABLED, text="🎤 Listening...")
        self.status_label.config(text="Status: Listening...", fg=LISTENING_COLOR)
        threading.Thread(target=self.listen_for_magic_word, daemon=True).start()

    def listen_for_magic_word(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                self.status_label.config(text="Status: Processing...", fg=LISTENING_COLOR)
                recognized_text = recognizer.recognize_google(audio).lower()
                self.transcribed_word.set(recognized_text)
                self.status_label.config(text=f"Status: Word '{recognized_text}' captured!", fg=SUCCESS_COLOR)
            except sr.WaitTimeoutError:
                self.status_label.config(text="Status: No speech detected. Try again.", fg="red")
            except sr.UnknownValueError:
                self.status_label.config(text="Status: Could not understand audio. Try again.", fg="red")
            except sr.RequestError:
                self.status_label.config(text="Status: API unavailable. Check connection.", fg="red")
            finally:
                self.speak_button.config(state=tk.NORMAL, text="🎤 Speak Magic Word")

    def attempt_login(self):
        magic_word = self.transcribed_word.get()
        password = self.password_entry.get()
        
#  and not magic_word
        if not password:
            messagebox.showerror("Login Failed", "Password is required.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        

        # magic_word == self.credentials.get('magic_word') and 
        if (hashed_password == self.credentials['password']):
            self.open_main_dashboard()
        else:
            # --- MODIFIED: More specific error ---
            messagebox.showerror("Login Failed", "Invalid password.")
            self.password_entry.delete(0, tk.END)
            self.status_label.config(text="Status: Waiting for you to speak...", fg=TEXT_COLOR)
            self.transcribed_word.set("")

    def show_forgot_password_window(self):
        recovery_window = tk.Toplevel(self)
        recovery_window.title("Password Recovery")
        
        width, height = 500, 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        recovery_window.geometry(f"{width}x{height}+{x}+{y}")
        
        recovery_window.configure(bg=WINDOW_BG)
        recovery_window.resizable(False, False)
        recovery_window.grab_set()

        frame = tk.Frame(recovery_window, bg=WINDOW_BG, padx=30, pady=20)
        frame.pack(fill="both", expand=True)
        
        try:
            logo_image = Image.open("logo.png").resize((200, 150), Image.LANCZOS)
            recovery_window.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(frame, image=recovery_window.logo_photo, bg=WINDOW_BG)
            logo_label.pack(pady=(0, 20))
        except FileNotFoundError:
            pass 

        tk.Label(frame, text="Answer Security Questions", font=self.title_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(pady=(0, 25))

        q1_label = tk.Label(frame, text=self.credentials['security_questions'][0], font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR)
        q1_label.pack(anchor="w", pady=(10, 5))
        answer1_entry = tk.Entry(frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat", show="*")
        answer1_entry.pack(fill="x", ipady=8, pady=(0, 15))

        q2_label = tk.Label(frame, text=self.credentials['security_questions'][1], font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR)
        q2_label.pack(anchor="w", pady=(10, 5))
        answer2_entry = tk.Entry(frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat", show="*")
        answer2_entry.pack(fill="x", ipady=8, pady=(0, 15))

        submit_button = tk.Button(
            frame, text="Submit Answers", font=self.button_font, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", cursor="hand2",
            command=lambda: self.verify_security_answers(recovery_window, answer1_entry.get(), answer2_entry.get())
        )
        submit_button.pack(fill="x", pady=30, ipady=12)

    def verify_security_answers(self, window, answer1, answer2):
        if not answer1 or not answer2:
            messagebox.showerror("Error", "Both answers are required.", parent=window)
            return
            
        hashed_answer1 = hashlib.sha256(answer1.encode()).hexdigest()
        hashed_answer2 = hashlib.sha256(answer2.encode()).hexdigest()

        if (hashed_answer1 == self.credentials['security_answers'][0] and
            hashed_answer2 == self.credentials['security_answers'][1]):
            window.destroy()
            self.show_reset_password_window() # This will now open the new, improved window
        else:
            messagebox.showerror("Verification Failed", "One or more answers are incorrect.", parent=window)



    def show_reset_password_window(self):
        """
        Shows the redesigned password reset window with logo, 
        show/hide, and magic word input.
        """
        reset_window = tk.Toplevel(self)
        reset_window.title("Reset Password & Magic Word")

        width, height = 500, 900 
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        reset_window.geometry(f"{width}x{height}+{x}+{y}")
        
        reset_window.configure(bg=WINDOW_BG)
        reset_window.resizable(False, False)
        reset_window.grab_set() # Fixed typo here

        frame = tk.Frame(reset_window, bg=WINDOW_BG, padx=30, pady=30)
        frame.pack(fill="both", expand=True)

        # --- Logo ---
        try:
            logo_image = Image.open("logo.png").resize((200, 150), Image.LANCZOS)
            reset_window.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(frame, image=reset_window.logo_photo, bg=WINDOW_BG)
            logo_label.pack(pady=(0, 20))
        except FileNotFoundError:
            pass

        tk.Label(frame, text="Reset Credentials", font=self.title_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(pady=(0, 20))

        tk.Label(frame, text="New Password", font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        new_pass_entry = tk.Entry(frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        new_pass_entry.pack(fill="x", ipady=8, pady=(0, 10))

        # --- Confirm New Password ---
        tk.Label(frame, text="Confirm New Password", font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        confirm_pass_entry = tk.Entry(frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        confirm_pass_entry.pack(fill="x", ipady=8, pady=(0, 10))

        # --- Show/Hide Checkbox ---
        show_pass_var = tk.BooleanVar()
        show_pass_check = tk.Checkbutton(
            frame,
            text="Show Passwords",
            variable=show_pass_var,
            command=lambda: self.toggle_reset_password_visibility(show_pass_var, new_pass_entry, confirm_pass_entry),
            bg=WINDOW_BG, fg=TEXT_COLOR, selectcolor=ENTRY_BG,
            activebackground=WINDOW_BG, activeforeground=TEXT_COLOR,
            highlightthickness=0, borderwidth=0
        )
        show_pass_check.pack(anchor="w", pady=(5, 15))

        # --- New Magic Word ---
        tk.Label(frame, text="New Magic Word (Vocal)", font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        new_magic_entry = tk.Entry(frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        new_magic_entry.pack(fill="x", ipady=8, pady=(0, 10))
        new_magic_entry.insert(0, self.credentials.get('magic_word', '')) # Pre-fill with old word

        # --- Confirm New Magic Word ---
        tk.Label(frame, text="Confirm New Magic Word", font=self.label_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        confirm_magic_entry = tk.Entry(frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        confirm_magic_entry.pack(fill="x", ipady=8, pady=(0, 15))

        # --- Reset Button ---
        reset_button = tk.Button(
            frame, text="Reset Credentials", font=self.button_font, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", cursor="hand2",
            command=lambda: self.perform_password_reset(
                reset_window, 
                new_pass_entry.get(), confirm_pass_entry.get(),
                new_magic_entry.get(), confirm_magic_entry.get()
            )
        )
        reset_button.pack(fill="x", pady=20, ipady=12)

    def toggle_reset_password_visibility(self, var, pass_entry, confirm_entry):
        """Toggles visibility for the password fields in the reset window."""
        if var.get():
            pass_entry.config(show="")
            confirm_entry.config(show="")
        else:
            pass_entry.config(show="*")
            confirm_entry.config(show="*")

    def perform_password_reset(self, window, new_password, confirm_password, new_magic, confirm_magic):
        """
        Validates and saves BOTH the new password and new magic word.
        """
        # --- Password Validation ---
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Both password fields are required.", parent=window)
            return
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=window)
            return
        
        # --- Magic Word Validation ---
        if not new_magic or not confirm_magic:
            messagebox.showerror("Error", "Both magic word fields are required.", parent=window)
            return
        if new_magic.lower() != confirm_magic.lower():
            messagebox.showerror("Error", "Magic words do not match.", parent=window)
            return
        
        # --- Update Credentials ---
        self.credentials['password'] = hashlib.sha256(new_password.encode()).hexdigest()
        self.credentials['magic_word'] = new_magic.lower().strip() # Save as lowercase
        
        try:
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(self.credentials, f, indent=4)
            messagebox.showinfo("Success", "Password and Magic Word have been reset.", parent=window)
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save new credentials: {e}", parent=window)



    def open_main_dashboard(self):
        self.withdraw()
        dashboard = MainDashboard(self)
        dashboard.protocol("WM_DELETE_WINDOW", self.destroy)

if __name__ == "__main__":
    app = SecurityApp()
    if app.credentials:
        app.mainloop()