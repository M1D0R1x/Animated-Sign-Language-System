import json
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.staticfiles import finders
from django.shortcuts import redirect
from django.shortcuts import render
from spacy.lang.en.stop_words import STOP_WORDS

import spacy
from pathlib import Path

model_name = "en"
if not spacy.util.is_package(model_name):
    spacy.cli.download(model_name)

nlp = spacy.load(model_name)


# Load custom synonyms from synonyms.json
try:
    with open(settings.SYNONYM_PATH, 'r', encoding='utf-8') as f:
        custom_synonyms = json.load(f)
except Exception as e:
    custom_synonyms = {}
    logging.getLogger(__name__).error(f"Could not load synonyms.json: {e}")

# Logging
logger = logging.getLogger(__name__)

def home_view(request):
    logger.info("Rendering home view")
    return render(request, 'home.html')

def about_view(request):
    logger.info("Rendering about view")
    return render(request, 'about.html')

def contact_view(request):
    logger.info("Rendering contact view")
    return render(request, 'contact.html')

def load_custom_synonyms():
    """Loads custom synonym dictionary from a JSON file."""
    try:
        with open(settings.SYNONYM_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("Error: synonyms.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON format in synonyms.json.")
        return {}

custom_synonyms = load_custom_synonyms()

def find_synonym(word):
    """Finds synonyms of a word using Custom Dictionary."""
    if word in custom_synonyms:
        return custom_synonyms[word]
    return None

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Adjust "home" to the name of your home URL
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def error_500_view(request):
    return render(request, '500.html', status=500)

# Placeholder for synonym function (define this based on your needs)
def find_synonym(word):
    # Example: return a synonym if available, else None
    synonyms = {"walk": "stroll", "run": "jog"}  # Replace with actual synonym lookup
    return synonyms.get(word.lower())

def detect_tense(doc):
    """
    Detect tense using spaCy dependency parsing for more accuracy.
    Returns the probable tense and counts for debugging.
    """
    tense = {"future": 0, "present": 0, "past": 0, "present_continuous": 0}
    for token in doc:
        if token.dep_ == "aux" and token.text.lower() in ["will", "shall"]:
            tense["future"] += 1
        elif token.pos_ == "VERB":
            if token.text.lower().endswith("ed") or token.tag_ == "VBD":  # Past tense verbs
                tense["past"] += 1
            elif token.text.lower().endswith("ing") and any(t.text.lower() in ["is", "am", "are"] for t in token.children):
                tense["present_continuous"] += 1
            else:
                tense["present"] += 1
    probable_tense = max(tense, key=tense.get) if any(tense.values()) else "present"
    logger.info(f"Detected tense: {probable_tense} with counts: {tense}")
    return probable_tense, tense

@login_required(login_url="login")
def animation_view(request):
    """
    Process text input and convert it to ISL animation representations.
    """
    logger.info("Entering animation_view")
    if request.method == 'POST':
        try:
            text = request.POST.get('sen')
            logger.info(f"Received text: '{text}'")
            if not text:
                raise ValueError("No input text provided.")

            # Clean text
            logger.info("Cleaning text...")
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()
            logger.info(f"Cleaned text: '{text}'")

            # Tokenize and process with spaCy
            logger.info("Processing text with spaCy...")
            doc = nlp(text)
            tagged = [(token.text, token.pos_) for token in doc]
            logger.info(f"Tagged words: {tagged}")

            # Detect tense
            logger.info("Detecting tense...")
            probable_tense, tense_counts = detect_tense(doc)
            logger.info(f"Probable tense: {probable_tense}")

            # Filter and adjust for ISL
            logger.info("Filtering and adjusting for ISL...")
            important_words = {
                "i", "he", "she", "they", "we", "what", "where", "how", "you", "your", "my",
                "name", "hear", "book", "sign", "me", "yes", "no", "not", "this", "it",
                "we", "us", "our", "that", "when"
            }
            stop_words = STOP_WORDS - important_words
            isl_replacements = {
                "i": "me",
                "hear": "listen",
                # Add more ISL-specific replacements here based on dictionary or rules
            }

            filtered_words = []
            for token in doc:
                word = token.text.lower()
                if word not in stop_words:
                    word = isl_replacements.get(word, word)
                    filtered_words.append(word)
            logger.info(f"Filtered words: {filtered_words}")

            # Insert ISL tense markers (lowercase to match animation filenames)
            logger.info("Inserting ISL tense markers...")
            if probable_tense == "past" and tense_counts["past"] > 0:
                filtered_words.insert(0, "before")
            elif probable_tense == "future" and tense_counts["future"] > 0:
                filtered_words.insert(0, "will")
            elif probable_tense == "present_continuous" and tense_counts["present_continuous"] > 0:
                filtered_words.insert(0, "now")
            logger.info(f"Words with tense: {filtered_words}")

            # Process words for animations
            logger.info("Processing words for animations...")
            synonym_mapping = {}
            processed_words = []
            for w in filtered_words:
                path = w + ".mp4"
                animation_path = finders.find(path)
                logger.info(f"Checking for {path}, found: {animation_path}")

                if animation_path:
                    processed_words.append(w)
                    logger.info(f"Found animation for '{w}' at {animation_path}")
                else:
                    synonym = find_synonym(w)
                    if synonym and finders.find(synonym + ".mp4"):
                        processed_words.append(synonym)
                        synonym_mapping[w] = synonym
                        logger.info(f"Using synonym '{synonym}' for '{w}'")
                    else:
                        logger.warning(f"No animation for '{w}', breaking into letters: {list(w)}")
                        processed_words.extend(list(w))

            logger.info(f"Final processed words: {processed_words}")
            if not processed_words:
                logger.warning("No words to display after processing.")

            return render(request, 'animation.html', {
                'words': processed_words,
                'text': text,
                'synonym_mapping': synonym_mapping
            })

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return render(request, 'animation.html', {'error': str(ve)})

        except Exception as e:
            logger.error(f"Unexpected error in animation_view: {e}")
            raise  # Re-raise for full traceback in logs

    return render(request, 'animation.html', {'words': [], 'text': '', 'synonym_mapping': {}})