import os
import pickle
import glob
from collections import defaultdict
import sys

# Ensure it can find preprocessing.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from preprocessing import HindiPreprocessor

class InvertedIndex:
    def __init__(self, index_path="index.pkl"):
        # Dictionary structure: term -> { doc_id: [pos1, pos2, ...] }
        self.index = defaultdict(lambda: defaultdict(list))
        self.doc_lengths = {} # doc_id -> total_tokens
        self.index_path = index_path
        self.preprocessor = HindiPreprocessor()

    def add_document(self, doc_id, text):
        """Tokenizes text and adds it to the positional index."""
        tokens = self.preprocessor.preprocess(text, remove_stop=True, stem_words=True)
        self.doc_lengths[doc_id] = len(tokens)

        for position, term in enumerate(tokens):
            self.index[term][doc_id].append(position)

    def build_from_folder(self, data_dir, limit=None):
        """Iterates over all .txt files in data_dir and builds the index."""
        print(f"Looking for data in: {os.path.abspath(data_dir)}")
        file_paths = glob.glob(os.path.join(data_dir, "*.txt"))
        
        if not file_paths:
            print(f"[ERROR] No .txt files found in {data_dir}")
            return

        print(f"Building index from {len(file_paths)} documents...")
        count = 0
        for fp in file_paths:
            doc_id = os.path.basename(fp)
            with open(fp, 'r', encoding='utf-8') as f:
                text = f.read()
                self.add_document(doc_id, text)
            
            count += 1
            if count % 100 == 0:
                print(f"  -> Indexed {count} docs...")
            if limit and count >= limit:
                break
        print("Indexing complete.")

    def save(self):
        """Serializes the index to disk using Pickle."""
        clean_index = {k: dict(v) for k, v in self.index.items()}
        data = {
            "index": clean_index,
            "doc_lengths": self.doc_lengths
        }
        with open(self.index_path, "wb") as f:
            pickle.dump(data, f)
        print(f"[SUCCESS] Index saved to {os.path.abspath(self.index_path)}")

    def load(self):
        """Loads the index from disk."""
        if not os.path.exists(self.index_path):
            print(f"[WARNING] Index file not found at {self.index_path}")
            return False
        
        with open(self.index_path, "rb") as f:
            data = pickle.load(f)
            self.index = data["index"]
            self.doc_lengths = data["doc_lengths"]
        print(f"Index loaded with {len(self.index)} terms.")
        return True

    def get_postings(self, term):
        """Returns the dictionary of {doc_id: [positions]} for a term."""
        return self.index.get(term, {})
    def get_postings(self, term):
        """Returns the dictionary of {doc_id: [positions]} for a term."""
        return self.index.get(term, {})
# THE TRIGGER BLOCK
if __name__ == "__main__":
    print("--- Starting Inverted Index Builder ---")
    
    # Calculate absolute paths so it never gets lost
    project_root = os.path.join(current_dir, '..')
    data_path = os.path.join(project_root, 'data', 'hi')
    index_output_path = os.path.join(project_root, 'index.pkl')
    
    idx = InvertedIndex(index_path=index_output_path)
    
    # Build from the 500 documents
    idx.build_from_folder(data_path) 
    idx.save()