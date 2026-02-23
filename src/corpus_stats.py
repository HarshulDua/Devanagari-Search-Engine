import os
import glob
import matplotlib.pyplot as plt
from collections import Counter
import sys
import numpy as np

# Ensure it can find preprocessing.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from preprocessing import HindiPreprocessor

def get_paths():
    """Helper to get absolute paths based on project structure"""
    project_root = os.path.join(current_dir, '..')
    data_dir = os.path.join(project_root, 'data', 'hi') 
    stopwords_path = os.path.join(project_root, 'data', 'stopwords_hi.txt')
    return data_dir, stopwords_path

def analyze_corpus(data_dir, stopwords_path):
    preprocessor = HindiPreprocessor(stopwords_path)
    
    term_freqs = Counter()
    vocab_growth = [] 
    total_tokens = 0
    doc_count = 0
    
    # Find all .txt files in the data directory
    file_paths = glob.glob(os.path.join(data_dir, "*.txt"))
    
    if not file_paths:
        print(f"\n[ERROR] No .txt files found in: {os.path.abspath(data_dir)}")
        print("Did you run the download_data.py script first?")
        return None, None

    print(f"\nFound {len(file_paths)} documents. Starting analysis...")

    for fp in file_paths:
        with open(fp, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Full preprocessing including stemming
        tokens = preprocessor.preprocess(text, remove_stop=True, stem_words=True)
        
        if tokens:
            term_freqs.update(tokens)
            total_tokens += len(tokens)
            vocab_growth.append((total_tokens, len(term_freqs)))
        
        doc_count += 1
        if doc_count % 100 == 0:
            print(f"  -> Processed {doc_count} docs...")

    return term_freqs, vocab_growth

def plot_stats(term_freqs, vocab_growth):
    print("\nGenerating plots...")
    
    # 1. Zipf's Law Plot
    sorted_freqs = [count for term, count in term_freqs.most_common()]
    ranks = range(1, len(sorted_freqs) + 1)
    
    plt.figure(figsize=(10, 6))
    plt.loglog(ranks, sorted_freqs, marker='.', linestyle='none', color='blue', markersize=2)
    plt.title("Zipf's Law (Log-Log): Rank vs Frequency")
    plt.xlabel("Log Rank")
    plt.ylabel("Log Frequency")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.savefig('../zipf_plot.png')
    print("[SUCCESS] Saved zipf_plot.png in the root folder")

    # 2. Heaps' Law Plot
    N = [x[0] for x in vocab_growth]
    M = [x[1] for x in vocab_growth]
    
    plt.figure(figsize=(10, 6))
    plt.loglog(N, M, marker='.', linestyle='none', color='red', markersize=2)
    plt.title("Heaps' Law (Log-Log): Tokens vs Vocabulary")
    plt.xlabel("Log Tokens (N)")
    plt.ylabel("Log Vocabulary Size (M)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.savefig('../heaps_plot.png')
    print("[SUCCESS] Saved heaps_plot.png in the root folder")

# THIS IS THE TRIGGER - IT MUST BE FLUSH LEFT
if __name__ == "__main__":
    print("--- Starting Corpus Statistics Script ---")
    data_dir, stopwords_path = get_paths()
    
    print(f"Looking for data in: {os.path.abspath(data_dir)}")
    freqs, growth = analyze_corpus(data_dir, stopwords_path)
    
    if freqs:
        print(f"\n--- Analysis Complete ---")
        print(f"Total Tokens: {growth[-1][0]}")
        print(f"Vocabulary Size: {growth[-1][1]}")
        plot_stats(freqs, growth)
    else:
        print("\n[WARNING] Analysis failed. Check your data folder.")