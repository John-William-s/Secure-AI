import tkinter as tk
from tkinter import font, messagebox
import pickle
import os
from PIL import Image, ImageTk

# --- Constants ---
WINDOW_BG = "#212121"
FRAME_BG = "#2c2c2c"
TEXT_COLOR = "#FFFFFF"
ENTRY_BG = "#373737"
BUTTON_BG = "#007BFF"
BUTTON_FG = "#FFFFFF"
FONT_FAMILY = "Helvetica"

# --- Result Styling Dictionaries ---
# These labels MUST match the logic in analyze_number
RESULT_COLORS = {
    "safe": "#28a745",      # Green
    "scam": "#dc3545"      # Red
}
ICON_MAP = {
    "safe": "✅",
    "scam": "❌"
}
DEFAULT_COLOR = "#444444" # Darker grey for initial state

class ScamCallAnalyzerUI(tk.Toplevel):
    """
    A UI window for the Scam Call Analyzer feature.
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Scam Call Analyzer (ML)")

        width, height = 700, 520
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)

        try:
            # Load the model and the corresponding vectorizer
            self.model = pickle.load(open('scam_detector.pkl', 'rb'))
            self.vectorizer = pickle.load(open('scam_vectorizer.pkl', 'rb'))
        except FileNotFoundError:
            messagebox.showerror("Error", "Model files not found.\nEnsure 'scam_detector.pkl' and 'scam_vectorizer.pkl' are present.")
            self.destroy()
            return
        except Exception as e:
            # This is likely where your error is happening
            messagebox.showerror("Model Loading Error", f"An error occurred loading model files:\n{e}\n\nThis is often caused by a scikit-learn version mismatch.")
            self.destroy()
            return

        # --- Fonts ---
        self.title_font = font.Font(family=FONT_FAMILY, size=20, weight="bold")
        self.label_font = font.Font(family=FONT_FAMILY, size=12)
        self.button_font = font.Font(family=FONT_FAMILY, size=12, weight="bold")
        self.result_status_font = font.Font(family=FONT_FAMILY, size=11, slant="italic")
        self.result_icon_font = font.Font(family="Arial", size=40)
        self.result_text_font = font.Font(family=FONT_FAMILY, size=26, weight="bold")
        self.confidence_font = font.Font(family=FONT_FAMILY, size=11)

        main_frame = tk.Frame(self, bg=WINDOW_BG, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)

        self.create_header(main_frame)
        self.create_input_widgets(main_frame)
        self.create_result_display(main_frame)

    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=WINDOW_BG)
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(header_frame, text="                ML Scam Call Analyzer", font=self.title_font, bg=WINDOW_BG, fg=TEXT_COLOR)
        title_label.pack(side="left")
        
        try:
            logo_image = Image.open("logoonly.png").resize((60, 60), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(header_frame, image=self.logo_photo, bg=WINDOW_BG)
            logo_label.pack(side="right")
        except FileNotFoundError:
            print("logo.jpg not found.")

    def create_input_widgets(self, parent):
        # Your model was trained on text data (TfidfVectorizer), so the label should reflect that.
        info_label = tk.Label(parent, text="Enter the phone number or suspicious text to analyze:", font=self.label_font, bg=WINDOW_BG, fg="#cccccc")
        info_label.pack(fill='x', pady=(0, 10))
        
        self.number_entry = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=self.label_font, borderwidth=2, relief="flat")
        self.number_entry.pack(fill="x", ipady=10, pady=(0, 20))
        self.number_entry.focus_set()
        
        analyze_button = tk.Button(parent, text="Analyze", font=self.button_font, bg=BUTTON_BG, fg=BUTTON_FG, cursor="hand2", relief="flat", command=self.analyze_number)
        analyze_button.pack(ipady=10, fill='x')

    def create_result_display(self, parent):
        result_container = tk.Frame(parent, bg=WINDOW_BG)
        result_container.pack(pady=(30, 0), fill="x")

        status_label = tk.Label(result_container, text="STATUS", font=self.result_status_font, bg=WINDOW_BG, fg="#cccccc")
        status_label.pack(pady=(0, 5))

        self.result_card = tk.Frame(result_container, bg=DEFAULT_COLOR, relief="solid", bd=1)
        self.result_card.pack(fill="x", ipady=1) 
        
        self.result_card.grid_rowconfigure(0, weight=1)
        self.result_card.grid_columnconfigure(0, weight=1)
        content_frame = tk.Frame(self.result_card, bg=DEFAULT_COLOR)
        content_frame.grid(row=0, column=0)

        self.icon_label = tk.Label(content_frame, text="", font=self.result_icon_font, bg=DEFAULT_COLOR, fg=TEXT_COLOR)
        self.icon_label.pack(side="left", padx=(0, 20))

        self.result_text_label = tk.Label(content_frame, text="Enter Input", font=self.result_text_font, bg=DEFAULT_COLOR, fg=TEXT_COLOR)
        self.result_text_label.pack(side="left")
        
        self.confidence_label = tk.Label(result_container, text="Awaiting input for analysis...", font=self.confidence_font, bg=WINDOW_BG, fg="#cccccc")
        self.confidence_label.pack(pady=(10, 0))

    def analyze_number(self):
        input_text = self.number_entry.get().strip()
        if not input_text:
            messagebox.showwarning("Empty Input", "Please enter a number or text to analyze.")
            return

        try:
            # 1. Transform the input text using the loaded TfidfVectorizer
            # The vectorizer automatically applies the same rules (lowercase, stop_words)
            text_vector = self.vectorizer.transform([input_text])
            
            # 2. Predict using the loaded MultinomialNB model
            prediction = self.model.predict(text_vector)[0]
            prediction_proba = self.model.predict_proba(text_vector)[0]
            confidence = max(prediction_proba) * 100

            # 3. Interpret the prediction based on your scam.py
            # 0 = 'ham' (safe)
            # 1 = 'scam'
            if prediction == 0:
                result_label = "safe"
            else:
                result_label = "scam"

            result_color = RESULT_COLORS.get(result_label, DEFAULT_COLOR)
            result_icon = ICON_MAP.get(result_label, "?")
            
            self.update_result_card(result_color, result_icon, result_label, confidence)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{e}")
            self.update_result_card("#8B0000", "!", "ANALYSIS ERROR", 0)

    def update_result_card(self, color, icon, text, confidence):
        """Helper function to update all visual elements of the result card."""
        self.result_card.config(bg=color)
        self.result_card.winfo_children()[0].config(bg=color)
        
        self.icon_label.config(text=icon, bg=color)
        self.result_text_label.config(text=text.upper(), bg=color)
        
        if confidence > 0:
            self.confidence_label.config(text=f"Model Confidence: {confidence:.2f}%")
        else:
            self.confidence_label.config(text="Could not determine confidence.")

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = ScamCallAnalyzerUI(root)
    app.mainloop()