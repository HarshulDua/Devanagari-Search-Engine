import re
import unicodedata
import os

class HindiPreprocessor:
    def __init__(self, stopwords_path=None):
        self.stopwords = set()
        if stopwords_path and os.path.exists(stopwords_path):
            self.load_stopwords(stopwords_path)
        elif stopwords_path:
            print(f"Warning: Stopwords file not found at {stopwords_path}")

    def load_stopwords(self, path):
        """Load stopwords from a file."""
        with open(path, 'r', encoding='utf-8') as f:
            self.stopwords = set(word.strip() for word in f.readlines())

    def tokenize(self, text):
            """
            Tokenize text keeping Hindi characters and valid numbers.
            Explicitly removes Hindi punctuation like danda (।) and double danda (॥).
            """
            if not text:
                return []
            
            # Explicitly remove Hindi full stops by replacing them with spaces
            text = text.replace('।', ' ').replace('॥', ' ')
            
            # Pattern matches Hindi characters and English alphanumeric
            pattern = r'[\u0900-\u097F\w]+'
            tokens = re.findall(pattern, text)
            return tokens

    def normalize(self, text):
        """
        1. Unicode NFC Normalization
        2. Nukta Removal (e.g., क़ -> क)
        3. Chandra Bindu normalization (maaa -> maa)
        """
        if not text:
            return ""

        # 1. Unicode NFC
        text = unicodedata.normalize('NFC', text)

        # 2. Nukta Removal (U+093C)
        text = text.replace('\u093C', '')

        # 3. Chandra Bindu (ँ) to Anusvara (ं)
        # This helps match variations of the same word
        text = text.replace('\u0901', '\u0902')
        
        # 4. Zwj/Zwnj removal (Optional but recommended)
        text = text.replace('\u200D', '').replace('\u200C', '')

        return text

    def remove_stopwords(self, tokens):
        """Remove tokens present in the stopword list."""
        return [t for t in tokens if t not in self.stopwords]

    def stem(self, word):
        """
        Simple rule-based stemmer for Hindi (Bonus Task).
        Removes common suffixes.
        """
        # Suffixes ordered by length (longest first)
        suffixes = [
            'ियों', 'ाइयों', 'ियाँ', 'ाइय',  # Plural/Oblique
            'िओं', 'ियां', '्यों', 
            'ों', 'ae', 'िए', 'ai',           
            'ी', 'े', 'ू', 'ु', 'ा',          # Gender/Number
            'कर', 'ao', 'aa'                  # Verb endings
        ]
        
        # Only stem words longer than 3 chars to avoid over-stemming
        if len(word) > 3:
            for suffix in suffixes:
                if word.endswith(suffix):
                    return word[:-len(suffix)]
        return word

    def preprocess(self, text, remove_stop=True, stem_words=False):
        """Full pipeline: Normalize -> Tokenize -> Stop removal -> Stem"""
        normalized_text = self.normalize(text)
        tokens = self.tokenize(normalized_text)
        
        if remove_stop:
            tokens = self.remove_stopwords(tokens)
            
        if stem_words:
            tokens = [self.stem(t) for t in tokens]
            
        return tokens