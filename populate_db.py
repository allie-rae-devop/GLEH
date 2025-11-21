#!/usr/bin/env python
"""Populate database with course metadata from the courses directory."""
import os
import sys
from dotenv import load_dotenv

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load .env file to get CONTENT_DIR
load_dotenv()
os.environ['FLASK_ENV'] = 'development'

sys.path.insert(0, os.getcwd())

from src.app import app
from src.build import main as build_main

print('='*60)
print('Populating Database with Course Metadata')
print('='*60)
content_dir = os.environ.get("CONTENT_DIR", os.getcwd())
print(f'Content Directory: {content_dir}')

# Debug: Check directories
courses_dir = os.path.join(content_dir, 'courses')
ebooks_dir = os.path.join(content_dir, 'ebooks')
print(f'Courses Directory: {courses_dir}')
print(f'  Exists: {os.path.isdir(courses_dir)}')
if os.path.isdir(courses_dir):
    course_count = len([d for d in os.listdir(courses_dir) if os.path.isdir(os.path.join(courses_dir, d))])
    print(f'  Found: {course_count} course directories')
print(f'Ebooks Directory: {ebooks_dir}')
print(f'  Exists: {os.path.isdir(ebooks_dir)}')
print()

try:
    # Pass content directory to build script via sys.argv
    sys.argv = [sys.argv[0], content_dir]
    build_main()
    print('\n' + '='*60)
    print('[SUCCESS] Database populated with courses!')
    print('='*60)
except Exception as e:
    print(f'\n[ERROR] {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
