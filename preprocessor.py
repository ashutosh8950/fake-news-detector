"""
Advanced text preprocessing for fake news detection.
Improvements:
  - Uses spaCy for faster, production-grade lemmatization and stopword removal.
  - Combines title + text.
  - Proper raw strings for regex.
  - 3x title weighting for stronger headline signal.
  - Aggressive removal of numbers and special characters.
"""

import re
import string
import spacy

# Load spaCy model at module level, disabling unused components for speed
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)                    # Remove [brackets]
    text = re.sub(r'https?://\S+|www\.\S+', '', text)      # Remove URLs
    text = re.sub(r'<.*?>+', '', text)                     # Remove HTML tags
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\w*\d\w*', '', text)                   # Remove words with numbers
    text = re.sub(r'\b\d+\b', '', text)                    # Remove standalone numbers
    text = re.sub(r'[^a-z\s]', '', text)                   # Remove remaining special chars
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def lemmatize_text(text: str) -> str:
    """Apply lemmatization and stopword removal using spaCy."""
    doc = nlp(text)
    # Filter out stopwords and very short tokens, then lemmatize
    tokens = [token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2]
    return ' '.join(tokens)

def preprocess(title: str = "", text: str = "") -> str:
    """
    Full preprocessing pipeline.
    Combines title + text for richer signal.
    Title is repeated 3x for stronger headline weighting.
    """
    combined = f"{title} {title} {title} {text}"  # triple title weight
    cleaned = clean_text(combined)
    return lemmatize_text(cleaned)
