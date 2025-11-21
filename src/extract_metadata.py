#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extract metadata from EPUB files and attempt to fetch covers from multiple sources.
Supports: Google Books, ISBNdb, archive.org, and other sources.
"""

import os
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import urllib.parse
import re
from ebooklib import epub

def extract_epub_metadata(epub_path):
    """
    Extract metadata from an EPUB file.
    Returns: dict with title, author, isbn, publisher, language
    """
    metadata = {
        'title': os.path.splitext(os.path.basename(epub_path))[0],
        'author': None,
        'isbn': None,
        'isbn10': None,
        'isbn13': None,
        'publisher': None,
        'language': 'en'
    }

    try:
        book = epub.read_epub(epub_path)

        # Extract title
        if title := book.get_metadata('DC', 'title'):
            if isinstance(title, list) and title:
                title_val = title[0]
            else:
                title_val = title

            # Handle tuples from ebooklib
            if isinstance(title_val, tuple):
                metadata['title'] = title_val[0]
            else:
                metadata['title'] = str(title_val)

        # Extract author
        if author := book.get_metadata('DC', 'creator'):
            if isinstance(author, list) and author:
                author_val = author[0]
            else:
                author_val = author

            # Handle tuples from ebooklib
            if isinstance(author_val, tuple):
                metadata['author'] = author_val[0]
            else:
                metadata['author'] = str(author_val)

        # Extract publisher
        if publisher := book.get_metadata('DC', 'publisher'):
            if isinstance(publisher, list) and publisher:
                pub_val = publisher[0]
            else:
                pub_val = publisher

            # Handle tuples
            if isinstance(pub_val, tuple):
                metadata['publisher'] = pub_val[0]
            else:
                metadata['publisher'] = str(pub_val)

        # Try to extract ISBN from identifiers
        if identifiers := book.get_metadata('DC', 'identifier'):
            if isinstance(identifiers, list):
                for identifier in identifiers:
                    if isinstance(identifier, tuple):
                        id_type, id_value = identifier
                        if 'isbn' in str(id_type).lower():
                            clean_isbn = str(id_value).replace('-', '')
                            if len(clean_isbn) == 10:
                                metadata['isbn10'] = clean_isbn
                            elif len(clean_isbn) == 13:
                                metadata['isbn13'] = clean_isbn
                            metadata['isbn'] = clean_isbn
                    elif isinstance(identifier, str):
                        # Try to parse ISBN from string
                        isbn_match = re.search(r'(978|979)?(\d{9}[\dxX]|\d{10})', identifier)
                        if isbn_match:
                            metadata['isbn'] = identifier

        # Fallback: search in OPF file
        if not metadata['isbn']:
            try:
                with zipfile.ZipFile(epub_path, 'r') as zip_ref:
                    # Find OPF file
                    for name in zip_ref.namelist():
                        if name.endswith('.opf'):
                            opf_content = zip_ref.read(name).decode('utf-8', errors='ignore')

                            # Extract ISBN from OPF
                            isbn_match = re.search(r'isbn["\']?\s*[=:]\s*["\']?([0-9\-X]+)', opf_content, re.IGNORECASE)
                            if isbn_match:
                                clean_isbn = isbn_match.group(1).replace('-', '')
                                if len(clean_isbn) in [10, 13]:
                                    metadata['isbn'] = clean_isbn
                                    if len(clean_isbn) == 10:
                                        metadata['isbn10'] = clean_isbn
                                    else:
                                        metadata['isbn13'] = clean_isbn
                            break
            except Exception:
                pass

    except Exception as e:
        print(f"  Warning: Could not fully parse {epub_path}: {e}")

    return metadata


def fetch_cover_from_google_books(title, author=None, isbn=None):
    """
    Fetch book cover from Google Books API.
    Try ISBN first, then title+author.
    Returns: cover URL if found, None otherwise
    """
    try:
        # Validate ISBN - skip if not a proper string number
        valid_isbn = None
        if isbn and isinstance(isbn, str) and isbn.replace('-', '').isdigit():
            if len(isbn.replace('-', '')) in [10, 13]:
                valid_isbn = isbn

        # Try ISBN first if available and valid
        if valid_isbn:
            query = f"isbn:{valid_isbn}"
            url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(query)}"

            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('items'):
                    for item in data['items']:
                        image_links = item.get('volumeInfo', {}).get('imageLinks', {})
                        if image_links.get('thumbnail'):
                            return image_links['thumbnail'].replace('http://', 'https://')

        # Fallback: search by title and author
        if title:
            search_terms = [title]
            if author:
                search_terms.append(author)
            query = ' '.join(search_terms[:2])

            url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(query)}&maxResults=5"

            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('items'):
                    for item in data['items']:
                        image_links = item.get('volumeInfo', {}).get('imageLinks', {})
                        if image_links.get('thumbnail'):
                            return image_links['thumbnail'].replace('http://', 'https://')

    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        pass

    return None


def fetch_cover_from_archive_org(title, author=None, isbn=None):
    """
    Fetch book cover from archive.org.
    Returns: cover URL if found, None otherwise
    """
    try:
        # Validate ISBN - skip if not a proper string number
        valid_isbn = None
        if isbn and isinstance(isbn, str) and isbn.replace('-', '').isdigit():
            if len(isbn.replace('-', '')) in [10, 13]:
                valid_isbn = isbn

        # Search by ISBN first
        if valid_isbn:
            url = f"https://archive.org/services/img/{valid_isbn}"
            # Check if image exists
            try:
                with urllib.request.urlopen(url, timeout=3) as response:
                    if response.code == 200 and int(response.headers.get('Content-Length', 0)) > 5000:
                        return url
            except urllib.error.HTTPError:
                pass

        # Search by title
        if title:
            search_title = title.replace(' ', '_')
            url = f"https://archive.org/advancedsearch.php?output=json&q=title:({search_title})+mediatype:texts&fl=identifier"

            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('response', {}).get('docs'):
                    identifier = data['response']['docs'][0].get('identifier')
                    if identifier:
                        cover_url = f"https://archive.org/services/img/{identifier}"
                        return cover_url

    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        pass

    return None


def fetch_cover_from_bookcovers_io(title, author=None, isbn=None):
    """
    Attempt to fetch from bookcovers.io (no API key required).
    Returns: cover URL if found, None otherwise
    """
    try:
        if isbn:
            # Try different sizes
            for size in ['M', 'L']:
                url = f"https://bookcovers.io/isbn/{isbn}?&size={size}"
                try:
                    with urllib.request.urlopen(url, timeout=3) as response:
                        if response.code == 200:
                            return url
                except urllib.error.HTTPError:
                    pass

    except Exception:
        pass

    return None


def download_cover(url, save_path):
    """
    Download a cover image from URL and save it.
    Returns: True if successful and >= 5KB, False otherwise
    """
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            cover_data = response.read()

            # Validate size (at least 5KB for meaningful cover)
            if len(cover_data) >= 5120:
                with open(save_path, 'wb') as f:
                    f.write(cover_data)
                return True

    except (urllib.error.URLError, TimeoutError):
        pass

    return False


def process_all_ebooks(epub_dir, output_file=None):
    """
    Extract metadata from all EPUB files and attempt to find covers.
    """
    results = []

    if not os.path.isdir(epub_dir):
        print(f"Error: Directory not found: {epub_dir}")
        return results

    epub_files = [f for f in os.listdir(epub_dir) if f.lower().endswith('.epub')]
    epub_files.sort()

    print(f"\nProcessing {len(epub_files)} EPUB files...\n")

    for i, filename in enumerate(epub_files, 1):
        epub_path = os.path.join(epub_dir, filename)
        print(f"[{i}/{len(epub_files)}] {filename}")

        # Extract metadata
        metadata = extract_epub_metadata(epub_path)
        print(f"  Title: {metadata['title']}")
        if metadata['author']:
            print(f"  Author: {metadata['author']}")
        if metadata['isbn']:
            print(f"  ISBN: {metadata['isbn']}")

        # Try to fetch covers from multiple sources
        cover_url = None
        cover_source = None

        # Priority order: Google Books -> archive.org -> bookcovers.io
        sources = [
            ('Google Books', fetch_cover_from_google_books),
            ('archive.org', fetch_cover_from_archive_org),
            ('bookcovers.io', fetch_cover_from_bookcovers_io),
        ]

        for source_name, fetch_func in sources:
            print(f"  Trying {source_name}...", end=' ', flush=True)
            cover_url = fetch_func(metadata['title'], metadata['author'], metadata['isbn'])

            if cover_url:
                print(f"Found")
                cover_source = source_name
                break
            else:
                print("Not found")

        result = {
            'filename': filename,
            'title': metadata['title'],
            'author': metadata['author'],
            'isbn': metadata['isbn'],
            'cover_url': cover_url,
            'cover_source': cover_source
        }
        results.append(result)

    # Save results to JSON
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")

    # Print summary
    found_covers = sum(1 for r in results if r['cover_url'])
    print(f"\n--- Summary ---")
    print(f"Total books: {len(results)}")
    print(f"Covers found: {found_covers}/{len(results)}")

    # Group by source
    by_source = {}
    for result in results:
        source = result['cover_source'] or 'None'
        by_source[source] = by_source.get(source, 0) + 1

    print(f"\nCovers by source:")
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count}")

    return results


if __name__ == '__main__':
    EPUB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'epub')
    OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'ebook_metadata.json')

    process_all_ebooks(EPUB_DIR, OUTPUT_FILE)
