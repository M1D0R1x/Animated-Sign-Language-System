import json
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect
from django.shortcuts import render
from django.templatetags.static import static
from textblob import TextBlob

logger = logging.getLogger(__name__)


# Load custom synonyms from synonyms.json
try:
    with open(settings.SYNONYM_PATH, 'r', encoding='utf-8') as f:
        custom_synonyms = json.load(f)
except Exception as e:
    custom_synonyms = {}
    logger.error(f"Could not load synonyms.json: {e}")

def home_view(request):
    logger.info("Rendering home view")
    return render(request, 'home.html', {
        'entered_text': '',
        'keywords': [],
    })

def about_view(request):
    logger.info("Rendering about view")
    return render(request, 'about.html')

def contact_view(request):
    logger.info("Rendering contact view")
    return render(request, 'contact.html')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
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
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def error_500_view(request):
    return render(request, '500.html', status=500)

def find_synonym(word):
    """Finds synonyms of a word using Custom Dictionary."""
    return custom_synonyms.get(word.lower())

def detect_tense_with_blob(text):
    """Detect tense using TextBlob for lightweight NLP."""
    blob = TextBlob(text)
    tags = blob.tags
    tense = {"future": 0, "present": 0, "past": 0, "present_continuous": 0}

    for word, tag in tags:
        if tag in ["MD"]:
            tense["future"] += 1
        elif tag in ["VBD", "VBN"]:
            tense["past"] += 1
        elif tag in ["VBG"]:
            tense["present_continuous"] += 1
        else:
            tense["present"] += 1

    probable_tense = max(tense, key=tense.get)
    return probable_tense, tense


@login_required(login_url="login")
def animation_view(request):
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

            # Detect tense with fallback
            logger.info("Detecting tense...")
            try:
                probable_tense, tense_counts = detect_tense_with_blob(text)
            except Exception as e:
                logger.error(f"Error detecting tense with TextBlob: {e}")
                probable_tense = "present"  # Fallback to present tense
                tense_counts = {"past": 0, "future": 0, "present_continuous": 0}
            logger.info(f"Probable tense: {probable_tense}")

            # Filter and adjust for ISL
            logger.info("Filtering and adjusting for ISL...")
            important_words = {
                "i", "he", "she", "they", "we", "what", "where", "how", "you", "your", "my",
                "name", "hear", "book", "sign", "me", "yes", "no", "not", "this", "it",
                "we", "us", "our", "that", "when"
            }
            isl_replacements = {
                "i": "me",
                "hear": "listen",
            }

            words = text.split()
            filtered_words = []

            for word in words:
                word = isl_replacements.get(word, word)
                if word in important_words or word.isalnum():
                    filtered_words.append(word)

            logger.info(f"Filtered words: {filtered_words}")

            # Insert ISL tense markers
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
            animation_urls = []

            for w in filtered_words:
                animation_path = f"animations/{w}.mp4"
                animation_url = static(animation_path)
                logger.info(f"Generated animation URL for '{w}': {animation_url}")

                # Assume the animation exists; let the browser handle 404 if it doesn't
                processed_words.append(w)
                animation_urls.append(animation_url)

                # Check for synonyms if needed (optional, since we're not verifying file existence)
                synonym = find_synonym(w)
                if synonym and w != synonym:  # Only if synonym is different
                    synonym_path = f"animations/{synonym}.mp4"
                    synonym_url = static(synonym_path)
                    logger.info(f"Using synonym '{synonym}' for '{w}', URL: {synonym_url}")
                    processed_words[-1] = synonym  # Replace the last word with the synonym
                    animation_urls[-1] = synonym_url  # Replace the URL
                    synonym_mapping[w] = synonym

            logger.info(f"Final processed words: {processed_words}")
            logger.info(f"Animation URLs: {animation_urls}")

            return render(request, 'animation.html', {
                'words': processed_words,
                'text': text,
                'synonym_mapping': synonym_mapping,
                'animation_urls': animation_urls
            })

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return render(request, 'animation.html', {
                'error': str(ve),
                'words': [],
                'text': '',
                'synonym_mapping': {},
                'animation_urls': []
            })

        except Exception as e:
            logger.error(f"Unexpected error in animation_view: {e}")
            raise

    return render(request, 'animation.html', {
        'words': [],
        'text': '',
        'synonym_mapping': {},
        'animation_urls': []
    })