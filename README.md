# SecureAI Vault

SecureAI Vault is a desktop security application that combines multi-factor authentication (Voice + Password) with machine learning-powered threat detection tools. It is designed to secure local files and analyze external threats such as phishing emails, malicious links, and scam numbers.

## Features

### Authentication & Core System
* **Dual-Factor Login:** Requires both a text password and a vocal "Magic Word" using speech recognition.
* **Secure Setup:** Initial setup wizard hashes credentials (SHA-256) and stores them locally.
* **Account Recovery:** Built-in password recovery system using security questions.
* **Interactive Dashboard:** Centralized hub to access all security modules.

### Security Tools
1.  **File Encryptor:**
    * Encrypts files using AES (Fernet) encryption.
    * Automatically moves encrypted files to a secure `SecureAI_Vault` directory.
    * Decrypts files back to their original state upon password verification.

2.  **Phishing Email Detector (ML):**
    * Analyzes email content using Natural Language Processing (NLTK).
    * Classifies emails as "Safe" or "Phishing/Spam" with a confidence percentage.

3.  **Malicious Link Analyzer (ML):**
    * Scans URLs to detect threats.
    * Categorizes links into four types: Benign, Phishing, Malware, or Defacement.

4.  **Scam Call Analyzer (ML):**
    * Analyzes phone numbers and suspicious text messages.
    * Identifies input as "Safe" or "Scam" based on text vectorization.

## ETL Pipeline Architecture

The application implements a real-time Extract, Transform, Load (ETL) pipeline to process raw user inputs for machine learning inference.

### 1. Extraction
* **Source:** Raw text data (URLs, email bodies, phone numbers) is extracted directly from the Tkinter GUI input fields in real-time.

### 2. Transformation (Preprocessing)
* **Text Cleaning:** The Phishing Detector module utilizes NLTK for lowercasing, punctuation removal, and string translation.
* **Tokenization & Filtering:** Stopwords are removed using the NLTK corpus, and words are reduced to their root form using the Porter Stemmer algorithm.
* **Vectorization:** Preprocessed text is transformed into numerical vectors using pre-trained `TfidfVectorizer` or `CountVectorizer` objects (loaded via Pickle), ensuring input dimensions match the training phase.

### 3. Load & Inference
* **Model Loading:** Serialized Scikit-learn models (`.pkl`) are loaded into memory upon application initialization.
* **Prediction:** The transformed vectors are passed to the classifiers (e.g., Naive Bayes, Random Forest) to generate class labels and probability scores for user confidence display.

## Dependencies

* Python 3.x
* tkinter (standard library)
* Pillow (PIL)
* SpeechRecognition
* cryptography
* nltk
* scikit-learn
* pyaudio (required for microphone input)

## Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/yourusername/SecureAI-Vault.git](https://github.com/yourusername/SecureAI-Vault.git)
    cd SecureAI-Vault
    ```

2.  Install the required Python packages:
    ```bash
    pip install pillow speechrecognition cryptography nltk scikit-learn pyaudio
    ```

3.  Download NLTK data (required for Phishing Detector):
    ```python
    import nltk
    nltk.download('stopwords')
    ```

## Usage

1.  **Run the Application:**
    Execute the main script to start the application.
    ```bash
    python logincorect.py
    ```

2.  **First-Time Setup:**
    If no credentials are found, the application will launch `setup.py`. You will be asked to create a password, record a "Magic Word," and answer security questions.

3.  **Login:**
    * Click "Speak Magic Word" and speak your passphrase.
    * Enter your password.
    * Click "Unlock" to access the dashboard.

## File Structure

* `logincorect.py`: Main application entry point and dashboard.
* `setup.py`: Configuration script for creating credentials.
* `file_encryptor.py`: Module for file encryption/decryption.
* `phishing_detector.py`: Module for email analysis and NLTK preprocessing.
* `link_analyzer.py`: Module for URL scanning.
* `scam_call_analyzer.py`: Module for scam detection.
* `credentials.json`: Generated file storing hashed user data.
* `SecureAI_Vault/`: Generated directory for storing encrypted files.

## Required Model Files

Ensure the following pre-trained model files are present in the root directory:
* `model.pkl` & `vectorizer.pkl` (Phishing Detector)
* `link_model.pkl` & `link_vectorizer.pkl` (Link Analyzer)
* `scam_detector.pkl` & `scam_vectorizer.pkl` (Scam Analyzer)
