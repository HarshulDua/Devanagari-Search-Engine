import unittest
import sys
import os

# 1. Setup the path to find the 'src' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.append(src_path)

from preprocessing import HindiPreprocessor

class TestHindiPreprocessing(unittest.TestCase):
    
    def setUp(self):
        # This runs before EVERY test function
        self.processor = HindiPreprocessor()
        # Mock stopwords to avoid file dependency issues in testing
        self.processor.stopwords = {'का', 'है'}

    def test_tokenization(self):
        # MUST start with 'test_'
        text = "भारत एक विशाल देश है।"
        tokens = self.processor.tokenize(text)
        expected = ['भारत', 'एक', 'विशाल', 'देश', 'है']
        self.assertEqual(tokens, expected)

    def test_normalization(self):
        # MUST start with 'test_'
        # Test Nukta removal (Example: क़ -> क)
        text_with_nukta = "क़िला" 
        normalized = self.processor.normalize(text_with_nukta)
        self.assertEqual(normalized, "किला")

    def test_stopwords_removal(self):
        # MUST start with 'test_'
        tokens = ['भारत', 'का', 'इतिहास']
        filtered = self.processor.remove_stopwords(tokens)
        # 'का' should be removed based on our setUp mock
        self.assertEqual(filtered, ['भारत', 'इतिहास'])

    def test_stemming(self):
        # MUST start with 'test_'
        words = ['लड़कियों', 'भारतीयों']
        stems = [self.processor.stem(w) for w in words]
        self.assertEqual(stems, ['लड़क', 'भारतीय'])

if __name__ == '__main__':
    unittest.main()