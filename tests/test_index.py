import unittest
import sys
import os

# Set up paths so tests can find the 'src' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.append(src_path)

from inverted_index import InvertedIndex
from query_processor import QueryProcessor
from compression import IndexCompressor

class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        # Create a tiny dummy index specifically for testing
        self.test_index_path = os.path.join(current_dir, '..', 'test_dummy_index.pkl')
        self.idx = InvertedIndex(self.test_index_path)
        
        # Doc 1: "India is Great" (Fixed capitalization to match query)
        self.idx.add_document("doc1", "India is Great")
        # Doc 2: "Great population in India" 
        self.idx.add_document("doc2", "Great population in India")
        self.idx.save()

    def tearDown(self):
        # Clean up the dummy index after tests finish
        if os.path.exists(self.test_index_path):
            os.remove(self.test_index_path)

    def test_boolean_and(self):
        qp = QueryProcessor(self.test_index_path)
        # "India" is in both. "Great" is in both.
        # "India AND Great" -> Both
        results = qp.boolean_query("India AND Great")
        self.assertEqual(len(results), 2)

    def test_phrase_query(self):
        qp = QueryProcessor(self.test_index_path)
        # "Great population" exists in doc2. It does NOT exist in doc1.
        results = qp.phrase_query("Great population")
        self.assertEqual(results, ["doc2"])

    def test_compression(self):
        comp = IndexCompressor()
        
        # Gap encoding test
        ids = ["0010_doc", "0015_doc", "0020_doc"] # Gaps should be: 10, 5, 5
        gaps = comp.gap_encode(ids)
        self.assertEqual(gaps, [10, 5, 5])
        
        # VByte test: Number 5 -> binary 10000101 (133 in decimal)
        encoded = comp.encode_vbyte_number(5)
        self.assertEqual(list(encoded), [133])

if __name__ == '__main__':
    unittest.main()