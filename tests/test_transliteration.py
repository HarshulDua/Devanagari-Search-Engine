import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.append(src_path)

from wildcard import WildcardProcessor
from transliterate import TransliterationEngine

class TestTolerantRetrieval(unittest.TestCase):
    
    def test_wildcard(self):
        vocab = ["भारत", "भारतीय", "भवन", "महान"]
        wp = WildcardProcessor(vocab)
        res = wp.get_wildcard_matches("भार*")
        
        self.assertIn("भारत", res)
        self.assertIn("भारतीय", res)
        self.assertNotIn("भवन", res)

    def test_transliteration(self):
        engine = TransliterationEngine()
        
        # FIX: Using "bhaarata" yields "भारत" perfectly in ITRANS
        hindi_word = engine.transliterate_to_hindi("bhaarata", scheme_name="itrans")
        self.assertEqual(hindi_word, "भारत")

if __name__ == '__main__':
    unittest.main()