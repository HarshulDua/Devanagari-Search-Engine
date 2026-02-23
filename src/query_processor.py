import os
import sys

# Ensure it can find other src files
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from inverted_index import InvertedIndex
from preprocessing import HindiPreprocessor

class QueryProcessor:
    def __init__(self, index_file="index.pkl"):
        self.inv_index = InvertedIndex(index_file)
        if not self.inv_index.load():
            print(f"[WARNING] Index not loaded from {index_file}. Build it first.")
        
        self.preprocessor = HindiPreprocessor()

    def get_docs(self, term):
        """Helper: Get set of DocIDs for a term."""
        postings = self.inv_index.get_postings(term)
        return set(postings.keys())

    def boolean_query(self, query):
        """Handles simple Boolean queries: AND, OR, NOT."""
        tokens = query.split()
        
        if "AND" in tokens:
            op = "AND"
            terms = [t for t in tokens if t != "AND"]
        elif "OR" in tokens:
            op = "OR"
            terms = [t for t in tokens if t != "OR"]
        elif "NOT" in tokens:
            op = "NOT"
            idx = tokens.index("NOT")
            include_terms = tokens[:idx]
            exclude_terms = tokens[idx+1:]
            terms = include_terms + exclude_terms 
        else:
            op = "OR"
            terms = tokens

        # Preprocess terms
        clean_terms = []
        for t in terms:
            processed = self.preprocessor.preprocess(t, remove_stop=True, stem_words=True)
            if processed:
                clean_terms.extend(processed)
        
        if not clean_terms:
            return []

        if op == "AND":
            # Sort by Document Frequency (optimization)
            clean_terms.sort(key=lambda t: len(self.get_docs(t)))
            result_set = self.get_docs(clean_terms[0])
            for t in clean_terms[1:]:
                result_set = result_set.intersection(self.get_docs(t))
                
        elif op == "OR":
            result_set = set()
            for t in clean_terms:
                result_set = result_set.union(self.get_docs(t))
                
        elif op == "NOT":
            include_processed = []
            for t in include_terms:
                p = self.preprocessor.preprocess(t, remove_stop=True, stem_words=True)
                if p: include_processed.extend(p)
            
            exclude_processed = []
            for t in exclude_terms:
                p = self.preprocessor.preprocess(t, remove_stop=True, stem_words=True)
                if p: exclude_processed.extend(p)
            
            if include_processed:
                result_set = self.get_docs(include_processed[0])
                for t in include_processed[1:]:
                    result_set = result_set.intersection(self.get_docs(t))
                for t in exclude_processed:
                    result_set = result_set.difference(self.get_docs(t))
            else:
                result_set = set()

        return list(result_set)

    def phrase_query(self, query):
        """Handles Phrase Queries (Exact Match) using Positional Index."""
        tokens = self.preprocessor.preprocess(query, remove_stop=True, stem_words=True)
        
        if not tokens: return []
        if len(tokens) == 1: return list(self.get_docs(tokens[0]))

        common_docs = self.get_docs(tokens[0])
        for t in tokens[1:]:
            common_docs = common_docs.intersection(self.get_docs(t))

        result_docs = []
        for doc_id in common_docs:
            term_positions = [self.inv_index.index[t][doc_id] for t in tokens]
            if self.has_phrase(term_positions):
                result_docs.append(doc_id)

        return result_docs

    def has_phrase(self, positions_list):
        for p1 in positions_list[0]:
            current_pos = p1
            match = True
            for i in range(1, len(positions_list)):
                next_positions = positions_list[i]
                if (current_pos + 1) in next_positions:
                    current_pos += 1
                else:
                    match = False
                    break
            if match:
                return True
        return False