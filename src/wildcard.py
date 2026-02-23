import re

class WildcardProcessor:
    def __init__(self, vocab):
        self.vocab = set(vocab)
        self.k = 2  # Bigrams (k=2) as required by the assignment
        self.kgram_index = self.build_kgram_index()

    def build_kgram_index(self):
        index = {}
        for term in self.vocab:
            modified_term = f"${term}$"
            for i in range(len(modified_term) - self.k + 1):
                gram = modified_term[i : i + self.k]
                if gram not in index:
                    index[gram] = set()
                index[gram].add(term)
        return index

    def get_wildcard_matches(self, query):
        """Finds words matching a wildcard query like 'भार*'"""
        parts = query.split('*')
        if len(parts) != 2: 
            return [] # Basic support for single wildcard
        
        prefix, suffix = parts[0], parts[1]
        grams_to_search = []
        
        if prefix:
            mod_pref = f"${prefix}"
            grams_to_search.extend([mod_pref[i:i+self.k] for i in range(len(mod_pref)-self.k+1)])
        if suffix:
            mod_suff = f"{suffix}$"
            grams_to_search.extend([mod_suff[i:i+self.k] for i in range(len(mod_suff)-self.k+1)])
        
        if not grams_to_search:
            return list(self.vocab)

        # Intersect all matching grams
        match_sets = [self.kgram_index.get(g, set()) for g in grams_to_search]
        if not match_sets: return []
        
        candidates = set.intersection(*match_sets) if match_sets else set()
        
        # Post-filter with regex to avoid false positives
        regex = re.compile(f"^{query.replace('*', '.*')}$")
        return [c for c in candidates if regex.match(c)]