import re
import unicodedata
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Ensure required NLTK resources are downloaded
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

def is_real_word(token):
    """
    Returns True if token is considered a real word:
      - After removing hyphens and apostrophes, it should contain only alphabetic characters.
      - Must be longer than one character.
    """
    cleaned = token.replace('-', '').replace("'", "")
    return cleaned.isalpha() and len(token) > 1

def advanced_text_processing(text, do_lemmatization=True, remove_stopwords=True):
    """
    Processes raw text by:
      - Unicode normalization
      - Removing LaTeX math delimiters and commands
      - Lowercasing the text
      - Tokenizing
      - Filtering out tokens that look like math artifacts, are just punctuation, single characters,
        or are not "real words" (i.e. contain non-alphabetic characters after removing hyphens/apostrophes)
      - Optional stopword removal and lemmatization

    Returns a list of processed tokens.
    """
    # Normalize Unicode to NFKC form
    text = unicodedata.normalize("NFKC", text)
    
    # Remove LaTeX math delimiters (inline and display)
    text = re.sub(r'\$\$(.*?)\$\$', r' \1 ', text, flags=re.DOTALL)
    text = re.sub(r'\$(.*?)\$', r' \1 ', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r' \1 ', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r' \1 ', text, flags=re.DOTALL)
    
    # Replace LaTeX commands (remove the leading backslash)
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    # Remove curly braces used in LaTeX formatting
    text = re.sub(r'[{}]', '', text)
    
    # Lowercase the text
    text = text.lower()
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Tokenize text (this preserves hyphenated words)
    tokens = word_tokenize(text)
    
    # Remove tokens that likely represent math artifacts (containing ^, (, ), +, or |)
    tokens = [token for token in tokens if not re.search(r'[\^\(\)\+\|]', token)]
    
    # Remove tokens that are exactly punctuation symbols
    punctuation_tokens = set(string.punctuation)
    punctuation_tokens.update({"``", "''"})
    tokens = [token for token in tokens if token not in punctuation_tokens]
    
    # Remove tokens that are only one character long
    tokens = [token for token in tokens if len(token) > 1]
    
    # Filter to keep only real words (alphabetic after removing hyphens/apostrophes)
    tokens = [token for token in tokens if is_real_word(token)]
    
    # Optionally remove stopwords
    if remove_stopwords:
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
    
    # Optionally perform lemmatization
    if do_lemmatization:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return tokens