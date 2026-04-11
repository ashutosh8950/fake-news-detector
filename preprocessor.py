"""
Advanced text preprocessing for fake news detection.
Improvements over original:
  - Combines title + text (original dropped title!)
  - NLTK lemmatization + stopword removal
  - Proper raw strings for regex (fixes SyntaxWarning)
"""

import re
import string
import nltk

# Download NLTK resources on first run
def ensure_nltk_data():
    for resource in ['stopwords', 'wordnet', 'omw-1.4']:
        try:
            nltk.data.find(f'corpora/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)

ensure_nltk_data()

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)           # Remove [brackets]
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(r'<.*?>+', '', text)             # Remove HTML tags
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\w*\d\w*', '', text)           # Remove words with numbers
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def lemmatize_text(text: str) -> str:
    """Apply lemmatization and stopword removal."""
    tokens = text.split()
    tokens = [LEMMATIZER.lemmatize(t) for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return ' '.join(tokens)

def preprocess(title: str = "", text: str = "") -> str:
    """
    Full preprocessing pipeline.
    Combines title + text for richer signal (key improvement over original).
    """
    combined = f"{title} {title} {text}"  # double title weight
    cleaned = clean_text(combined)
    return lemmatize_text(cleaned)
