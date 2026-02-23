from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class TransliterationEngine:
    def transliterate_to_hindi(self, text, scheme_name="itrans"):
        """Converts Latin text to Devanagari with modern normalization."""
        
        # 1. Protect Boolean Operators so 'AND' doesn't become 'अन्द्'
        operators = ["AND", "OR", "NOT"]
        words = text.split()
        translated_words = []

        for word in words:
            if word.upper() in operators:
                translated_words.append(word.upper())
                continue
            
            # 2. Select Scheme
            source = sanscript.HK if scheme_name == "hk" else sanscript.ITRANS
            
            # 3. Transliterate (convert to lowercase first for consistency)
            hindi_word = transliterate(word.lower(), source, sanscript.DEVANAGARI)
            
            # 4. THE CURE: Remove trailing Halants
            # Converts 'नम्' (nam) -> 'नम' (nam) which matches more documents
            if hindi_word.endswith('्'):
                hindi_word = hindi_word[:-1]
            
            translated_words.append(hindi_word)
        
        return " ".join(translated_words)