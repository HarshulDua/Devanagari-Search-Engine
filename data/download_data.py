#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download and extract Wikipedia/Wikisource dumps for Indian languages

This script helps students download a subset of Wikipedia articles
for their Information Retrieval assignment.

Usage:
    python download_data.py --lang hi --num-articles 500 --output data/hindi
    python download_data.py --lang ta --num-articles 500 --output data/tamil
    python download_data.py --list-languages
    python download_data.py --lang sa --all-articles --output data/sanskrit
    python download_data.py --lang bn --all-articles --max-bytes 2000000000 --output data/bengali

Supported languages:
    hi  - Hindi (हिन्दी)
    ta  - Tamil (தமிழ்)
    te  - Telugu (తెలుగు)
    bn  - Bengali (বাংলা)
    mr  - Marathi (मराठी)
    kn  - Kannada (ಕನ್ನಡ)
    ml  - Malayalam (മലയാളം)
    gu  - Gujarati (ગુજરાતી)
    or  - Odia (ଓଡ଼ିଆ)
    pa  - Punjabi (ਪੰਜਾਬੀ)
    sa  - Sanskrit (संस्कृत)

Created on Mon Jan 26 02:01:08 2026

@author: Hrishikesh Terdalkar
"""

###############################################################################


import argparse
import bz2
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

# Wikipedia dump URLs (articles dump - smaller than full dump)
WIKI_DUMPS = {
    'hi': 'https://dumps.wikimedia.org/hiwiki/latest/hiwiki-latest-pages-articles.xml.bz2',
    'ta': 'https://dumps.wikimedia.org/tawiki/latest/tawiki-latest-pages-articles.xml.bz2',
    'te': 'https://dumps.wikimedia.org/tewiki/latest/tewiki-latest-pages-articles.xml.bz2',
    'bn': 'https://dumps.wikimedia.org/bnwiki/latest/bnwiki-latest-pages-articles.xml.bz2',
    'as': 'https://dumps.wikimedia.org/aswiki/latest/aswiki-latest-pages-articles.xml.bz2',
    'mr': 'https://dumps.wikimedia.org/mrwiki/latest/mrwiki-latest-pages-articles.xml.bz2',
    'kn': 'https://dumps.wikimedia.org/knwiki/latest/knwiki-latest-pages-articles.xml.bz2',
    'ml': 'https://dumps.wikimedia.org/mlwiki/latest/mlwiki-latest-pages-articles.xml.bz2',
    'gu': 'https://dumps.wikimedia.org/guwiki/latest/guwiki-latest-pages-articles.xml.bz2',
    'or': 'https://dumps.wikimedia.org/orwiki/latest/orwiki-latest-pages-articles.xml.bz2',
    'pa': 'https://dumps.wikimedia.org/pawiki/latest/pawiki-latest-pages-articles.xml.bz2',
    'sa': 'https://dumps.wikimedia.org/sawiki/latest/sawiki-latest-pages-articles.xml.bz2',
    'ur': 'https://dumps.wikimedia.org/urwiki/latest/urwiki-latest-pages-articles.xml.bz2',
    'ne': 'https://dumps.wikimedia.org/newiki/latest/newiki-latest-pages-articles.xml.bz2',
}

# Wikisource dumps (literary texts - good for classical content)
WIKISOURCE_DUMPS = {
    'hi': 'https://dumps.wikimedia.org/hiwikisource/latest/hiwikisource-latest-pages-articles.xml.bz2',
    'ta': 'https://dumps.wikimedia.org/tawikisource/latest/tawikisource-latest-pages-articles.xml.bz2',
    'te': 'https://dumps.wikimedia.org/tewikisource/latest/tewikisource-latest-pages-articles.xml.bz2',
    'bn': 'https://dumps.wikimedia.org/bnwikisource/latest/bnwikisource-latest-pages-articles.xml.bz2',
    'as': 'https://dumps.wikimedia.org/aswikisource/latest/aswikisource-latest-pages-articles.xml.bz2',
    'mr': 'https://dumps.wikimedia.org/mrwikisource/latest/mrwikisource-latest-pages-articles.xml.bz2',
    'kn': 'https://dumps.wikimedia.org/knwikisource/latest/knwikisource-latest-pages-articles.xml.bz2',
    'ml': 'https://dumps.wikimedia.org/mlwikisource/latest/mlwikisource-latest-pages-articles.xml.bz2',
    'sa': 'https://dumps.wikimedia.org/sawikisource/latest/sawikisource-latest-pages-articles.xml.bz2',
    'or': 'https://dumps.wikimedia.org/orwikisource/latest/orwikisource-latest-pages-articles.xml.bz2',
}

LANGUAGE_NAMES = {
    'hi': 'Hindi (हिन्दी)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'bn': 'Bengali (বাংলা)',
    'as': 'Assamese (অসমীয়া)',
    'mr': 'Marathi (मराठी)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'ml': 'Malayalam (മലയാളം)',
    'gu': 'Gujarati (ગુજરાતી)',
    'or': 'Odia (ଓଡ଼ିଆ)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)',
    'sa': 'Sanskrit (संस्कृत)',
    'ur': 'Urdu (اردو)',
    'ne': 'Nepali (नेपाली)',
}

# Minimum requirements
MIN_ARTICLES = 500
MIN_WORDS = 20000
RECOMMENDED_ARTICLES = 1500
DEFAULT_OUTPUT_DIR = 'data'


def clean_wiki_text(text):
    """Remove wiki markup from text."""
    if not text:
        return ""

    # Remove comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Remove templates {{...}}
    text = re.sub(r'\{\{[^}]*\}\}', '', text)

    # Remove tables {| ... |}
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)

    # Remove file/image links
    text = re.sub(r'\[\[(?:File|Image|फ़ाइल|चित्र|છબી|ಫೈಲ್|ചിത്രം|படம்|파일):[^\]]*\]\]',
                  '', text, flags=re.IGNORECASE)

    # Remove categories [[Category:...]]
    text = re.sub(r'\[\[(?:Category|श्रेणी|వర్గం|பகுப்பு|বিষয়শ্রেণী|ವರ್ಗ|വർഗ്ഗം):[^\]]*\]\]', '', text, flags=re.IGNORECASE)

    # Convert links [[text|display]] to display, [[text]] to text
    text = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)

    # Remove external links [http://...]
    text = re.sub(r'\[https?://[^\]]*\]', '', text)

    # Remove references <ref>...</ref>
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^/]*/>', '', text)

    # Remove gallery tags
    text = re.sub(r'<gallery[^>]*>.*?</gallery>', '', text, flags=re.DOTALL)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove wiki formatting
    text = re.sub(r"'''?", '', text)  # Bold/italic
    text = re.sub(r'={2,}[^=]+={2,}', '', text)  # Headers

    # Remove multiple newlines/spaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


def count_words(text):
    """Count words in text (handles Indian scripts)."""
    # Split on whitespace and punctuation
    words = re.findall(r'[\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF'
                       r'\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF'
                       r'\u0D00-\u0D7F\u0D80-\u0DFFa-zA-Z]+', text)
    return len(words)


def download_with_progress(url, dest_path):
    """Download a file with progress indication."""
    print(f"Downloading from {url}")
    print(f"This may take a while for large dumps...")

    def progress_hook(count, block_size, total_size):
        mb_downloaded = count * block_size / (1024 * 1024)
        if total_size and total_size > 0:
            percent = min(100, count * block_size * 100 // total_size)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\rProgress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
        else:
            sys.stdout.write(f"\rProgress: {mb_downloaded:.1f} MB downloaded")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, progress_hook)
    print()  # Newline after progress


def stream_wiki_dump(dump_path, max_articles=None):
    """
    Stream articles from a Wikipedia XML dump (compressed or not).
    Yields (title, text) tuples.
    """
    ns = '{http://www.mediawiki.org/xml/export-0.11/}'

    # Open file (handle both .bz2 and plain XML)
    if dump_path.endswith('.bz2'):
        f = bz2.open(dump_path, 'rt', encoding='utf-8')
    else:
        f = open(dump_path, 'r', encoding='utf-8')

    count = 0
    try:
        # Use iterparse for memory efficiency
        context = ET.iterparse(f, events=('end',))

        for event, elem in context:
            if elem.tag == f'{ns}page':
                # Extract title and text
                title_elem = elem.find(f'{ns}title')
                text_elem = elem.find(f'.//{ns}text')

                if title_elem is not None and text_elem is not None:
                    title = title_elem.text or ""
                    text = text_elem.text or ""

                    # Skip non-article pages (talk, user, etc.)
                    ns_elem = elem.find(f'{ns}ns')
                    if ns_elem is not None and ns_elem.text != '0':
                        elem.clear()
                        continue

                    # Skip redirects
                    text_l = text.lstrip().lower()
                    if text_l.startswith('#redirect') or text.startswith('#अनुप्रेषित') or text.startswith('#पुनर्निर्देशन'):
                        elem.clear()
                        continue

                    # Clean and yield
                    clean_text = clean_wiki_text(text)
                    if clean_text and len(clean_text) > 100:  # Skip very short articles
                        yield title, clean_text
                        count += 1

                        if max_articles and count >= max_articles:
                            break

                # Clear element to save memory
                elem.clear()
    finally:
        f.close()


def extract_articles(dump_path, output_dir, num_articles=500, min_words_per_article=50, max_bytes=None):
    """
    Extract articles from dump to individual text files.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    articles_extracted = 0
    total_words = 0
    bytes_written = 0

    if num_articles is None:
        print("Extracting all articles...")
    else:
        print(f"Extracting up to {num_articles} articles...")

    # Create metadata file
    metadata = []

    max_articles = None if num_articles is None else num_articles * 2
    for title, text in stream_wiki_dump(dump_path, max_articles=max_articles):
        word_count = count_words(text)

        # Skip articles that are too short
        if word_count < min_words_per_article:
            continue

        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
        safe_title = re.sub(r'\s+', '_', safe_title).strip('_')
        if not safe_title:
            safe_title = f"doc_{articles_extracted:04d}"
        filename = f"{articles_extracted:04d}_{safe_title}.txt"

        # Write article
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            content = f"# {title}\n\n{text}"
            f.write(content)
        bytes_written += len(content.encode('utf-8'))

        # Track metadata
        metadata.append({
            'id': articles_extracted,
            'title': title,
            'filename': filename,
            'word_count': word_count
        })

        articles_extracted += 1
        total_words += word_count

        if articles_extracted % 50 == 0:
            print(f"  Extracted {articles_extracted} articles ({total_words} words)...")

        if max_bytes and bytes_written >= max_bytes:
            print(f"\n[STOP] Reached --max-bytes limit ({max_bytes} bytes).")
            break

        if num_articles is not None and articles_extracted >= num_articles:
            break

    # Write metadata
    metadata_path = output_path / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_articles': articles_extracted,
            'total_words': total_words,
            'articles': metadata
        }, f, ensure_ascii=False, indent=2)

    print(f"\nExtraction complete!")
    print(f"  Articles: {articles_extracted}")
    print(f"  Total words: {total_words}")
    print(f"  Output directory: {output_path}")
    print(f"  Metadata: {metadata_path}")

    return articles_extracted, total_words


def main():
    parser = argparse.ArgumentParser(
        description='Download Wikipedia/Wikisource dumps for Indian languages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--list-languages', action='store_true',
                        help='List available languages')
    parser.add_argument('--lang', '-l', type=str,
                        help='Language code (e.g., hi, mr, ta, te)')
    parser.add_argument('--source', '-s', choices=['wikipedia', 'wikisource'],
                        default='wikipedia',
                        help='Source: wikipedia or wikisource (default: wikipedia)')
    parser.add_argument('--num-articles', '-n', type=int, default=RECOMMENDED_ARTICLES,
                        help=f'Number of articles to extract (default: {RECOMMENDED_ARTICLES}, min: {MIN_ARTICLES})')
    parser.add_argument('--all-articles', action='store_true',
                        help='Extract all articles from the dump (overrides --num-articles)')
    parser.add_argument('--max-bytes', type=int, default=None,
                        help='Stop extraction after writing this many bytes (approx, uncompressed)')
    parser.add_argument('--output', '-o', type=str, default='data',
                        help='Output directory (default: data)')
    parser.add_argument('--download-only', action='store_true',
                        help='Only download dump, do not extract')
    parser.add_argument('--extract-only', type=str, metavar='DUMP_FILE',
                        help='Only extract from existing dump file')
    parser.add_argument('--remove-dump', action='store_true',
                        help='Remove downloaded dump file after extraction')
    parser.add_argument('--min-words', type=int, default=50,
                        help='Minimum words per article (default: 50)')
    parser.add_argument('--yes', action='store_true',
                        help='Skip safety prompt for --all-articles')

    args = parser.parse_args()

    if args.list_languages:
        print("Available languages:")
        print("-" * 40)
        for code, name in sorted(LANGUAGE_NAMES.items()):
            wiki = "Y" if code in WIKI_DUMPS else "N"
            source = "Y" if code in WIKISOURCE_DUMPS else "N"
            print(f"  {code}  {name:30s} [Wiki:{wiki}] [Source:{source}]")
        print("\nUsage: python download_data.py --lang hi --num-articles 500")
        return

    if args.extract_only:
        # Extract from existing dump
        if not os.path.exists(args.extract_only):
            print(f"Error: Dump file not found: {args.extract_only}")
            sys.exit(1)

        if args.all_articles and not args.yes:
            resp = input("You requested --all-articles (may be very large). Continue? [y/N] ").strip().lower()
            if resp not in ('y', 'yes'):
                print("Aborted.")
                sys.exit(0)
        num_articles = None if args.all_articles else args.num_articles
        extract_articles(args.extract_only, args.output, num_articles, args.min_words, args.max_bytes)
        return

    if not args.lang:
        parser.print_help()
        print("\nError: --lang is required. Use --list-languages to see options.")
        sys.exit(1)

    if args.lang not in LANGUAGE_NAMES:
        print(f"Error: Unknown language code '{args.lang}'")
        print("Use --list-languages to see available options.")
        sys.exit(1)

    if not args.all_articles and args.num_articles < MIN_ARTICLES:
        print(f"Warning: Minimum {MIN_ARTICLES} articles required for assignment.")
        print(f"Using {MIN_ARTICLES} articles.")
        args.num_articles = MIN_ARTICLES

    # Select dump URL
    if args.source == 'wikisource':
        if args.lang not in WIKISOURCE_DUMPS:
            print(f"Error: Wikisource not available for {args.lang}")
            print("Available: " + ", ".join(WIKISOURCE_DUMPS.keys()))
            sys.exit(1)
        dump_url = WIKISOURCE_DUMPS[args.lang]
    else:
        dump_url = WIKI_DUMPS[args.lang]

    # Create output directory
    if args.output == DEFAULT_OUTPUT_DIR:
        output_dir = Path(args.output) / args.lang
    else:
        output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download dump
    source_tag = 'wiki' if args.source == 'wikipedia' else 'wikisource'
    dump_filename = f"{args.lang}-{source_tag}-dump.xml.bz2"
    dump_path = output_dir / dump_filename

    print(f"Language: {LANGUAGE_NAMES[args.lang]}")
    print(f"Source: {args.source}")
    print(f"Output: {output_dir}")
    print()

    if not dump_path.exists():
        download_with_progress(dump_url, str(dump_path))
    else:
        print(f"Using existing dump: {dump_path}")

    if args.download_only:
        print(f"Dump downloaded to: {dump_path}")
        return

    # Extract articles
    if args.all_articles and not args.yes:
        resp = input("You requested --all-articles (may be very large). Continue? [y/N] ").strip().lower()
        if resp not in ('y', 'yes'):
            print("Aborted.")
            sys.exit(0)
    num_articles = None if args.all_articles else args.num_articles
    articles, words = extract_articles(str(dump_path), str(output_dir), num_articles, args.min_words, args.max_bytes)

    # Cleanup
    if args.remove_dump and dump_path.exists():
        print(f"\nRemoving dump file...")
        os.remove(dump_path)

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Language: {LANGUAGE_NAMES[args.lang]}")
    print(f"Articles extracted: {articles}")
    print(f"Total words: {words}")
    print(f"Output directory: {output_dir}")

    if articles >= MIN_ARTICLES and words >= MIN_WORDS:
        print("\n[OK] Dataset meets minimum requirements for assignment!")
    else:
        print(f"\n[WARNING] Dataset may be too small.")
        print(f"  Minimum: {MIN_ARTICLES} articles, {MIN_WORDS} words")
        print(f"  Try increasing --num-articles or using a different source.")


if __name__ == '__main__':
    main()
