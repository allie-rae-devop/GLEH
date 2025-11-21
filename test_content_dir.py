#!/usr/bin/env python
import os
import sys

# Set the content directory to the project root
os.environ['CONTENT_DIR'] = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import app

with app.app_context():
    print('=== Content Directory Configuration Test ===\n')
    print(f'CONTENT_DIR (from config): {repr(app.config.get("CONTENT_DIR"))}')
    print(f'App Root Path: {repr(app.root_path)}\n')

    content_dir = app.config.get('CONTENT_DIR')
    if content_dir:
        courses_dir = os.path.join(content_dir, 'courses')
        print(f'Courses Directory: {repr(courses_dir)}')
        print(f'Courses Directory Exists: {os.path.isdir(courses_dir)}\n')

        if os.path.isdir(courses_dir):
            courses = sorted(os.listdir(courses_dir))[:5]
            total_courses = len(os.listdir(courses_dir))
            print(f'[OK] Found {total_courses} courses')
            print('\nFirst 5 courses:')
            for c in courses:
                print(f'  - {c}')
            print(f'\n[SUCCESS] Content directory configuration is WORKING!')
        else:
            print('[ERROR] Courses directory not found!')
    else:
        print('[ERROR] CONTENT_DIR not configured!')
