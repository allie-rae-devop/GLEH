#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build script to populate the database with course and e-book content.
Includes generative fallback for missing e-book covers.
"""

import os
import sys
import re
import json
import hashlib
import shutil
import textwrap
import ffmpeg
import urllib.request
import urllib.error
import urllib.parse
# REMOVED: ebooklib and BeautifulSoup - Migrated to Calibre-Web for ebook management
# from ebooklib import epub, ITEM_IMAGE
# from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from flask_migrate import upgrade as db_upgrade # Import upgrade command

from .app import app
from .database import db
from .models import Course, Ebook

# --- Global Category Patterns ---
CATEGORY_PATTERNS = {
    'Python': re.compile(r'[Pp]ython', re.IGNORECASE),
    'Java': re.compile(r'[Jj]ava', re.IGNORECASE),
    'C++': re.compile(r'C\+\+', re.IGNORECASE),
    'JavaScript': re.compile(r'[Jj]avascript|JS', re.IGNORECASE),
    'DevOps': re.compile(r'DevOps|Docker|Ansible|Argo|Kubernetes|GitLab', re.IGNORECASE),
    'Data Structures': re.compile(r'Data Structures|Algorithms|LeetCode', re.IGNORECASE),
    'Rust': re.compile(r'Rust', re.IGNORECASE),
    'Linux': re.compile(r'Linux', re.IGNORECASE),
    'AI': re.compile(r'AI|Artificial Intelligence|Machine Learning', re.IGNORECASE),
}

def categories_from_name(name):
    """Derives categories from a name using regex matching."""
    found_categories = []
    for category, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(name):
            found_categories.append(category)
    return list(set(found_categories))

def parse_course_metadata(html_path, course_dir, course_name_for_categories):
    """Parses metadata for a course."""
    metadata = {
        'title': os.path.basename(course_dir).replace('_', ' ').replace('-', ' ').title(),
        'path': html_path.replace('\\', '/'),
        'description': '',
        'categories': [],
        'intro_video_path': None
    }
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception:
        return metadata

    if title_tag := soup.select_one('div.intro h1'):
        metadata['title'] = title_tag.get_text(strip=True)

    if first_section := soup.select_one('#content-main > ul > li'):
        if desc_tag := first_section.find('p'):
            metadata['description'] = desc_tag.get_text(strip=True)

    if first_video_tag := soup.select_one('div.chapter .watch[data-video]'):
        relative_video_path = first_video_tag['data-video']
        metadata['intro_video_path'] = os.path.join(course_dir, relative_video_path)

    metadata['categories'] = categories_from_name(course_name_for_categories)
    return metadata

def generate_thumbnail(course_dir, metadata_dict):
    """Generates a thumbnail only if it doesn't already exist."""
    metadata_dict['thumbnail'] = 'images/default_course.jpg'
    video_file = metadata_dict.get('intro_video_path')
    if not video_file or not os.path.isfile(video_file):
        return

    static_thumb_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'thumbnails')
    os.makedirs(static_thumb_dir, exist_ok=True)
    output_path = os.path.join(static_thumb_dir, f"{metadata_dict['uid']}.jpg")

    if os.path.exists(output_path):
        metadata_dict['thumbnail'] = f"thumbnails/{metadata_dict['uid']}.jpg"
        return

    web_path = f"thumbnails/{metadata_dict['uid']}.jpg"
    try:
        probe = ffmpeg.probe(video_file)
        duration = float(probe['format']['duration'])
        timestamp = min(5, duration / 10)
        (
            ffmpeg.input(video_file, ss=timestamp)
            .output(output_path, vframes=1)
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
        metadata_dict['thumbnail'] = web_path
    except (ffmpeg.Error, KeyError, FileNotFoundError):
        pass

def fetch_cover_from_google_books(title, author=None, isbn=None):
    """
    Fetches a book cover from Google Books API.
    Tries ISBN first, then title+author search.
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

            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get('items'):
                        for item in data['items']:
                            image_links = item.get('volumeInfo', {}).get('imageLinks', {})
                            if image_links.get('thumbnail'):
                                return image_links['thumbnail'].replace('http://', 'https://')
            except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
                pass

        # Fallback: search by title and author
        if title:
            search_terms = [title]
            if author:
                search_terms.append(author)
            query = ' '.join(search_terms[:2])

            url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(query)}&maxResults=5"

            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get('items'):
                        for item in data['items']:
                            image_links = item.get('volumeInfo', {}).get('imageLinks', {})
                            if image_links.get('thumbnail'):
                                return image_links['thumbnail'].replace('http://', 'https://')
            except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
                pass

    except Exception:
        pass

    return None


def download_cover_image(cover_url, save_path):
    """
    Download a cover image from URL and save it.
    Returns: True if successful and >= 5KB, False otherwise
    """
    try:
        with urllib.request.urlopen(cover_url, timeout=5) as response:
            cover_data = response.read()

            # Validate size (at least 5KB for meaningful cover)
            if len(cover_data) >= 5120:
                with open(save_path, 'wb') as f:
                    f.write(cover_data)
                return True

    except (urllib.error.URLError, TimeoutError):
        pass

    return False


def fetch_cover_from_openlibrary(title, save_path):
    """
    Fetches a book cover from Open Library API using the book title.

    Open Library has covers for millions of books with no API key required.
    Returns True if cover was successfully downloaded and saved, False otherwise.
    """
    try:
        # Clean the title (remove extra words common in tech books)
        clean_title = re.sub(r'\s*(by|for|study|guide|handbook|hands?-?on|tutorial|manual|companion)\s*', ' ', title, flags=re.IGNORECASE)
        clean_title = clean_title.strip().split()[0:3]  # Use first 3 words for better matching
        search_query = ' '.join(clean_title)

        # Open Library search API endpoint
        search_url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(search_query)}&limit=5"

        # Fetch search results with timeout
        with urllib.request.urlopen(search_url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

            # Look for a book with a cover
            if data.get('docs'):
                for doc in data['docs']:
                    if doc.get('has_fulltext') and doc.get('cover_i'):
                        # Found a book with a cover
                        cover_id = doc['cover_i']
                        # Use medium size cover (400x600 pixels)
                        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"

                        # Download the cover image
                        with urllib.request.urlopen(cover_url, timeout=5) as cover_response:
                            cover_data = cover_response.read()

                            # Verify it's a reasonable image (at least 1KB)
                            if len(cover_data) >= 1024:
                                with open(save_path, 'wb') as f:
                                    f.write(cover_data)
                                return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, json.JSONDecodeError):
        # Network error, API error, or invalid response - fail gracefully
        pass
    except Exception as e:
        # Log unexpected errors but don't crash
        pass

    return False

def generate_cover_image(title, save_path):
    """Generates a placeholder cover image with the book title."""
    width, height = 400, 600
    bg_color = (26, 26, 26)
    text_color = (224, 224, 224)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", size=32)
    except IOError:
        font = ImageFont.load_default()

    lines = textwrap.wrap(title, width=20)

    total_text_height = sum([font.getbbox(line)[3] for line in lines])
    y_text = (height - total_text_height) / 2

    for line in lines:
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        draw.text(((width - line_width) / 2, y_text), line, font=font, fill=text_color)
        y_text += font.getbbox(line)[3] + 5

    img.save(save_path)

# REMOVED: Migrated to Calibre-Web for ebook management
# def extract_epub_metadata(epub_path):
#     """
#     Extract metadata from an EPUB file.
#     Returns: dict with title, author, isbn
#     """
#     metadata = {
#         'title': os.path.splitext(os.path.basename(epub_path))[0],
#         'author': None,
#         'isbn': None
#     }
#
#     try:
#         book = epub.read_epub(epub_path)
#
#         # Extract title
#         if title := book.get_metadata('DC', 'title'):
#             if isinstance(title, list) and title:
#                 title_val = title[0]
#             else:
#                 title_val = title
#
#             # Handle tuples from ebooklib
#             if isinstance(title_val, tuple):
#                 metadata['title'] = title_val[0]
#             else:
#                 metadata['title'] = str(title_val)
#
#         # Extract author
#         if author := book.get_metadata('DC', 'creator'):
#             if isinstance(author, list) and author:
#                 author_val = author[0]
#             else:
#                 author_val = author
#
#             # Handle tuples from ebooklib
#             if isinstance(author_val, tuple):
#                 metadata['author'] = author_val[0]
#             else:
#                 metadata['author'] = str(author_val)
#
#         # Try to extract ISBN from identifiers
#         if identifiers := book.get_metadata('DC', 'identifier'):
#             if isinstance(identifiers, list):
#                 for identifier in identifiers:
#                     if isinstance(identifier, tuple):
#                         id_type, id_value = identifier
#                         if 'isbn' in str(id_type).lower():
#                             clean_isbn = str(id_value).replace('-', '')
#                             if len(clean_isbn) in [10, 13]:
#                                 metadata['isbn'] = clean_isbn
#                                 break
#
#     except Exception:
#         pass
#
#     return metadata


# REMOVED: Migrated to Calibre-Web for ebook management
# Ebooks are now fetched via Calibre-Web API instead of scanning filesystem
# def process_ebooks(epub_dir):
#     """Scans for .epub files, extracts or generates covers, and returns a list of metadata."""
#     ebook_metadata_list = []
#     if not os.path.isdir(epub_dir):
#         return ebook_metadata_list
#
#     COVER_SAVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'ebook_covers')
#     os.makedirs(COVER_SAVE_DIR, exist_ok=True)
#
#     print("\n--- Processing E-books ---")
#     for filename in os.listdir(epub_dir):
#         if filename.lower().endswith('.epub'):
#             clean_title = os.path.splitext(filename)[0].replace('_', ' ').title()
#             epub_path = os.path.join(epub_dir, filename)
#             uid = hashlib.md5(filename.encode()).hexdigest()
#
#             cover_filename = f"{uid}.jpg"
#             cover_save_path = os.path.join(COVER_SAVE_DIR, cover_filename)
#             web_path = f'ebook_covers/{cover_filename}'
#
#             ebook_metadata = {
#                 'uid': uid, 'title': clean_title, 'path': epub_path.replace('\\', '/'),
#                 'cover_path': web_path, 'categories': categories_from_name(clean_title)
#             }
#
#             if os.path.exists(cover_save_path):
#                 ebook_metadata_list.append(ebook_metadata)
#                 continue
#
#             cover_found = False
#
#             # Step 1: Try to extract cover from EPUB
#             try:
#                 book = epub.read_epub(epub_path)
#                 cover_content = None
#                 if item := book.get_item_with_id('cover-image'):
#                     cover_content = item.get_content()
#                 if not cover_content and (images := list(book.get_items_of_type(ITEM_IMAGE))):
#                     cover_content = images[0].get_content()
#
#                 # Only use extracted cover if it's a reasonable size (at least 10KB)
#                 if cover_content and len(cover_content) >= 10240:
#                     with open(cover_save_path, 'wb') as f:
#                         f.write(cover_content)
#                     cover_found = True
#             except Exception as e:
#                 pass  # Silently fail, will try fallbacks
#
#             # Step 2: If extraction failed, try Google Books API (high success rate, no API key needed)
#             if not cover_found:
#                 epub_meta = extract_epub_metadata(epub_path)
#                 cover_url = fetch_cover_from_google_books(epub_meta['title'], epub_meta['author'], epub_meta['isbn'])
#                 if cover_url and download_cover_image(cover_url, cover_save_path):
#                     print(f"  Info: Downloaded cover from Google Books for '{clean_title}'")
#                     cover_found = True
#
#             # Step 3: If Google Books failed, try Open Library API
#             if not cover_found:
#                 if fetch_cover_from_openlibrary(clean_title, cover_save_path):
#                     print(f"  Info: Downloaded cover from Open Library for '{clean_title}'")
#                     cover_found = True
#
#             # Step 4: If still no cover, generate one
#             if not cover_found:
#                 print(f"  Info: Generated placeholder cover for '{clean_title}'")
#                 generate_cover_image(clean_title, cover_save_path)
#
#             ebook_metadata_list.append(ebook_metadata)
#     return ebook_metadata_list

def package_context(content_dir):
    """Creates a 'context' directory with essential project files."""
    print("\n--- Packaging Project Context ---")
    CONTEXT_PACKAGE_DIR = os.path.join(content_dir, 'context')
    CHAT_LOG_SRC = os.path.join(content_dir, 'chat_log.md')

    os.makedirs(CONTEXT_PACKAGE_DIR, exist_ok=True)

    if not os.path.exists(CHAT_LOG_SRC):
        with open(CHAT_LOG_SRC, 'w', encoding='utf-8') as f:
            f.write("# Project Chat History\n\nPlease copy and paste the conversation here.\n")

    files_to_copy = {
        'app.py': os.path.join(content_dir, 'app.py'),
        'models.py': os.path.join(content_dir, 'models.py'),
        'build.py': os.path.join(content_dir, 'build.py'),
        'requirements.txt': os.path.join(content_dir, 'requirements.txt'),
        'index.html': os.path.join(content_dir, 'templates', 'index.html'),
        'course.html': os.path.join(content_dir, 'templates', 'course.html'),
        'main.js': os.path.join(content_dir, 'static', 'js', 'main.js'),
        'style.css': os.path.join(content_dir, 'static', 'css', 'style.css'),
        'chat_log.md': CHAT_LOG_SRC
    }

    for name, src_path in files_to_copy.items():
        if os.path.exists(src_path):
            try:
                shutil.copy2(src_path, os.path.join(CONTEXT_PACKAGE_DIR, name))
            except Exception as e:
                print(f"Error copying '{name}': {e}", file=sys.stderr)
        else:
            print(f"Warning: Source file not found, skipping: {src_path}")

def main():
    """Main execution function."""
    CONTENT_DIR = sys.argv[1] if len(sys.argv) > 1 else '.'
    COURSES_DIR = os.path.join(CONTENT_DIR, 'courses')
    EPUB_DIR = os.path.join(CONTENT_DIR, 'ebooks')

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        # --- Process Courses ---
        if os.path.isdir(COURSES_DIR):
            for course_name in os.listdir(COURSES_DIR):
                course_dir = os.path.join(COURSES_DIR, course_name)
                if os.path.isdir(course_dir):
                    package_dir = os.path.join(course_dir, 'package')
                    course_html_path = os.path.join(package_dir, 'index.html')
                    if os.path.isfile(course_html_path):
                        uid = hashlib.md5(course_name.encode()).hexdigest()
                        metadata = parse_course_metadata(course_html_path, package_dir, course_name)
                        metadata['uid'] = uid
                        generate_thumbnail(package_dir, metadata)

                        course = Course.query.filter_by(uid=uid).first()
                        if course is None:
                            course = Course(uid=uid)
                            db.session.add(course)

                        course.title = metadata['title']
                        course.path = metadata['path']
                        course.description = metadata['description']
                        course.categories = ','.join(metadata['categories'])
                        course.thumbnail = metadata['thumbnail']

        # --- Process E-books ---
        # REMOVED: Migrated to Calibre-Web for ebook management
        # Ebooks are now fetched via Calibre-Web API instead of scanning filesystem
        # ebooks_data = process_ebooks(EPUB_DIR)
        # for data in ebooks_data:
        #     ebook = Ebook.query.filter_by(uid=data['uid']).first()
        #     if ebook is None:
        #         ebook = Ebook(uid=data['uid'])
        #         db.session.add(ebook)
        #
        #     ebook.title = data['title']
        #     ebook.path = data['path']
        #     ebook.cover_path = data['cover_path']
        #     ebook.categories = ','.join(data['categories'])

        db.session.commit()
        print("\nDatabase population complete.")

if __name__ == '__main__':
    main()
