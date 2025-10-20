import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
import json
import hashlib
import os

# --- Constants and Configuration ---
WINDOW_BG = "#212121"
FRAME_BG = "#2c2c2c"
TEXT_COLOR = "#FFFFFF"
ENTRY_BG = "#373737"
BUTTON_BG = "#007BFF"
BUTTON_FG = "#FFFFFF"
FONT_FAMILY = "Helvetica"
CREDENTIALS_FILE = "credentials.json"

def hash_data(data):
    """Hashes the input data using SHA-256."""
    return hashlib.sha256(data.encode()).hexdigest()

class SetupApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("First-Time Setup - SecureAI Vault")
        # Adjusted window size for a 2-column layout
        width, height = 800, 950
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)

        # --- Font Definitions ---
        self.title_font = font.Font(family=FONT_FAMILY, size=20, weight="bold")
        self.label_font = font.Font(family=FONT_FAMILY, size=12)
        self.entry_font = font.Font(family=FONT_FAMILY, size=12)
        self.button_font = font.Font(family=FONT_FAMILY, size=14, weight="bold")
        self.sub_heading_font = font.Font(family=FONT_FAMILY, size=14, weight="bold", underline=True)

        # --- Main Frame ---
        main_frame = tk.Frame(self, bg=WINDOW_BG, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        # --- Logo ---
        try:
            logo_image = Image.open("logo.png").resize((150, 112), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(main_frame, image=self.logo_photo, bg=WINDOW_BG)
            logo_label.pack(pady=(0, 15))
        except FileNotFoundError:
            pass # Silently ignore if logo is not found

        # --- HEADING ---
        tk.Label(main_frame, text="Initial Setup", font=self.title_font, bg=WINDOW_BG, fg=TEXT_COLOR).pack(pady=(0, 20))

        # --- 2-Column Container ---
        columns_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        columns_frame.pack(fill="both", expand=True)

        # --- COLUMN 1: Passwords & Magic Word ---
        self.left_frame = tk.Frame(columns_frame, bg=FRAME_BG, bd=2, relief="solid", padx=20, pady=20)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5))

        tk.Label(self.left_frame, text="Passwords", font=self.sub_heading_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 15))

        tk.Label(self.left_frame, text="New Password", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.pass_entry = tk.Entry(self.left_frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.pass_entry.pack(fill="x", ipady=8, pady=(0, 10))

        tk.Label(self.left_frame, text="Confirm New Password", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.confirm_pass_entry = tk.Entry(self.left_frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.confirm_pass_entry.pack(fill="x", ipady=8, pady=(0, 10))

        self.show_pass_var = tk.BooleanVar()
        show_pass_check = tk.Checkbutton(
            self.left_frame,
            text="Show Passwords",
            variable=self.show_pass_var,
            command=self.toggle_password_visibility,
            bg=FRAME_BG, fg=TEXT_COLOR, selectcolor=ENTRY_BG,
            activebackground=FRAME_BG, activeforeground=TEXT_COLOR,
            highlightthickness=0, borderwidth=0
        )
        show_pass_check.pack(anchor="w", pady=(0, 20))

        tk.Label(self.left_frame, text="Magic Word (Vocal)", font=self.sub_heading_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 15))

        tk.Label(self.left_frame, text="New Magic Word", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.magic_entry = tk.Entry(self.left_frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.magic_entry.pack(fill="x", ipady=8, pady=(0, 10))

        tk.Label(self.left_frame, text="Confirm Magic Word", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.confirm_magic_entry = tk.Entry(self.left_frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.confirm_magic_entry.pack(fill="x", ipady=8, pady=(0, 15))


        # --- COLUMN 2: Security Questions ---
        self.right_frame = tk.Frame(columns_frame, bg=FRAME_BG, bd=2, relief="solid", padx=20, pady=20)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10))

        tk.Label(self.right_frame, text="Security Questions", font=self.sub_heading_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 15))

        tk.Label(self.right_frame, text="Security Question 1", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.q1_entry = tk.Entry(self.right_frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.q1_entry.pack(fill="x", ipady=8, pady=(0, 10))
        self.q1_entry.insert(0, "What was your first pet's name?")

        tk.Label(self.right_frame, text="Answer 1", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.a1_entry = tk.Entry(self.right_frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.a1_entry.pack(fill="x", ipady=8, pady=(0, 10))

        tk.Label(self.right_frame, text="Security Question 2", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        self.q2_entry = tk.Entry(self.right_frame, font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.q2_entry.pack(fill="x", ipady=8, pady=(0, 10))
        self.q2_entry.insert(0, "What city were you born in?")

        tk.Label(self.right_frame, text="Answer 2", font=self.label_font, bg=FRAME_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 5))
        self.a2_entry = tk.Entry(self.right_frame, show="*", font=self.entry_font, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat")
        self.a2_entry.pack(fill="x", ipady=8, pady=(0, 10))

        self.show_ans_var = tk.BooleanVar()
        show_ans_check = tk.Checkbutton(
            self.right_frame,
            text="Show Answers",
            variable=self.show_ans_var,
            command=self.toggle_answer_visibility,
            bg=FRAME_BG, fg=TEXT_COLOR, selectcolor=ENTRY_BG,
            activebackground=FRAME_BG, activeforeground=TEXT_COLOR,
            highlightthickness=0, borderwidth=0
        )
        show_ans_check.pack(anchor="w", pady=(10, 0))

        # --- Submit Button (Bottom) ---
        submit_button = tk.Button(
            main_frame,
            text="Create Credentials",
            font=self.button_font,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            relief="flat",
            cursor="hand2",
            command=self.save_credentials
        )
        submit_button.pack(fill="x", pady=25, ipady=12)

    def toggle_password_visibility(self):
        """Toggles visibility for password fields."""
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
            self.confirm_pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")
            self.confirm_pass_entry.config(show="*")

    def toggle_answer_visibility(self):
        """Toggles visibility for answer fields."""
        if self.show_ans_var.get():
            self.a1_entry.config(show="")
            self.a2_entry.config(show="")
        else:
            self.a1_entry.config(show="*")
            self.a2_entry.config(show="*")

    def save_credentials(self):
        """Validates inputs, hashes data, and saves to the JSON file."""
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()
        magic_word = self.magic_entry.get().lower().strip()
        confirm_magic = self.confirm_magic_entry.get().lower().strip()
        q1 = self.q1_entry.get()
        a1 = self.a1_entry.get()
        q2 = self.q2_entry.get()
        a2 = self.a2_entry.get()

        # Validation
        if not all([password, confirm_password, magic_word, confirm_magic, q1, a1, q2, a2]):
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            return
        
        if magic_word != confirm_magic:
            messagebox.showerror("Error", "Magic words do not match.", parent=self)
            return

        # Prepare data
        credentials = {
            "password": hash_data(password),
            "magic_word": magic_word, # Magic word is stored in plain text for speech recognition
            "security_questions": [q1, q2],
            "security_answers": [hash_data(a1), hash_data(a2)]
        }

        # Save to file
        try:
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=4)
            
            messagebox.showinfo("Success", "Credentials file created successfully! You can now run the main application.", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {e}", parent=self)


if __name__ == "__main__":
    if os.path.exists(CREDENTIALS_FILE):
        # Create a temporary root to show the messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Setup Already Run", f"'{CREDENTIALS_FILE}' already exists. Setup will not run again.")
        root.destroy()
    else:
        # Run the setup application
        app = SetupApp()
        app.mainloop()