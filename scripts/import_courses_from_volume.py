#!/usr/bin/env python3
"""
Import Courses from Docker Volume

Scans courses in the gleh-courses Docker volume and imports metadata to database.
Courses should be uploaded to the volume at: /app/data/courses/Course-Name/
"""
import sys
import json
import os
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Load environment variables
from dotenv import load_dotenv  # noqa: E402
load_dotenv(root_dir / '.env')

from src.app import app, db  # noqa: E402
from src.models import Course  # noqa: E402


def extract_instructors(instructors_data):
    """Extract instructor names from instructors array"""
    if not instructors_data:
        return None

    names = []
    for instructor in instructors_data:
        if 'title' in instructor and instructor['title']:
            names.append(instructor['title'])
        else:
            # Build from first/last name
            first = instructor.get('first_name', '')
            last = instructor.get('last_name', '')
            if first or last:
                names.append(f"{first} {last}".strip())

    return ', '.join(names) if names else None


def import_courses():
    """Import courses from Docker volume to database"""

    print("=" * 80)
    print("Course Importer - Docker Volume")
    print("=" * 80)
    print()

    # For Docker: volume is mounted at /app/data/courses
    # For local testing: use a local path
    courses_base = os.getenv('COURSES_BASE_PATH', '/app/data/courses')

    # Check if running in Docker
    if not os.path.exists(courses_base):
        print(f"[WARN] Courses directory not found: {courses_base}")
        print()
        print("This script should be run inside the Docker container:")
        print("  docker exec gleh-web python scripts/import_courses_from_volume.py")
        print()
        return False

    print(f"[1/4] Scanning courses directory: {courses_base}")

    # Find all course directories
    course_dirs = []
    try:
        for item in os.listdir(courses_base):
            item_path = os.path.join(courses_base, item)
            if os.path.isdir(item_path):
                # Check if it has index.html or data.json
                index_path = os.path.join(item_path, 'index.html')
                data_path = os.path.join(item_path, 'data.json')
                if os.path.exists(index_path) or os.path.exists(data_path):
                    course_dirs.append(item)
    except Exception as e:
        print(f"[ERROR] Failed to scan directory: {e}")
        return False

    print(f"[OK] Found {len(course_dirs)} course directories")
    print()

    # Process each course
    print("[2/4] Extracting course metadata...")
    courses_data = []

    for idx, course_dir in enumerate(sorted(course_dirs), 1):
        print(f"  [{idx}/{len(course_dirs)}] {course_dir}...")

        try:
            course_path = os.path.join(courses_base, course_dir)
            data_json_path = os.path.join(course_path, 'data.json')

            # Try to load metadata from data.json if it exists
            course_info = {
                'uid': course_dir,
                'title': course_dir.replace('-', ' ').replace('_', ' '),
                'path': f"{course_dir}/index.html",
                'description': '',
                'instructor': None,
                'course_number': None,
                'term': None,
                'year': None,
                'level': None,
                'department': None,
                'license_url': None,
                'thumbnail': None,
                'learning_resources': None,
                'categories': None,
            }

            # Parse data.json if available (MIT OCW courses)
            # Check that it's actually a file, not a directory
            if os.path.exists(data_json_path) and os.path.isfile(data_json_path):
                with open(data_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                course_info.update({
                    'title': data.get('course_title', course_dir),
                    'description': data.get('course_description', ''),
                    'instructor': extract_instructors(data.get('instructors')),
                    'course_number': data.get('primary_course_number', ''),
                    'term': data.get('term', ''),
                    'year': data.get('year', ''),
                    'level': ', '.join(data.get('level', [])),
                    'department': ', '.join(data.get('department_numbers', [])),
                    'license_url': (
                        data.get('course_image_metadata', {})
                        .get('license', '')
                    ),
                    'learning_resources': json.dumps(
                        data.get('learning_resource_types', [])
                    ),
                })

                # Handle thumbnail
                image_src = data.get('image_src', '')
                if image_src:
                    # Convert ./static_resources/image.jpg to course_dir/static_resources/image.jpg
                    if image_src.startswith('./'):
                        course_info['thumbnail'] = f"{course_dir}/{image_src[2:]}"
                    else:
                        course_info['thumbnail'] = f"{course_dir}/{image_src}"

                # Extract topics/categories
                topics = data.get('topics', [])
                if topics:
                    categories = set()
                    for topic_path in topics:
                        if isinstance(topic_path, list):
                            categories.update(topic_path)
                    course_info['categories'] = ', '.join(sorted(categories))

            courses_data.append(course_info)
            print(f"      Title: {course_info['title']}")
            if course_info['course_number']:
                print(f"      Number: {course_info['course_number']}")

        except Exception as e:
            print(f"      [ERROR] Failed to parse metadata: {e}")
            continue

    print()
    print(f"[OK] Successfully extracted {len(courses_data)} courses")
    print()

    # Save to database
    print("[3/4] Importing courses to database...")

    with app.app_context():
        # Count existing courses
        existing_count = Course.query.count()
        print(f"  Existing courses in database: {existing_count}")
        print()

        imported = 0
        updated = 0

        for course_data in courses_data:
            # Check if course already exists
            existing = Course.query.filter_by(
                uid=course_data['uid']
            ).first()

            if existing:
                # Update existing course
                for key, value in course_data.items():
                    setattr(existing, key, value)
                updated += 1
                print(f"  [UPDATE] {course_data['title']}")
            else:
                # Create new course
                course = Course(**course_data)
                db.session.add(course)
                imported += 1
                print(f"  [NEW] {course_data['title']}")

        # Commit all changes
        db.session.commit()

        print()
        print("[OK] Database import complete!")
        print(f"  New courses: {imported}")
        print(f"  Updated courses: {updated}")
        print(f"  Total courses in database: {Course.query.count()}")
        print()

        # Summary
        print("[4/4] Import Summary")
        print("=" * 80)
        print(f"Courses scanned: {len(course_dirs)}")
        print(f"Metadata extracted: {len(courses_data)}")
        print(f"New imports: {imported}")
        print(f"Updates: {updated}")
        print()
        print("=" * 80)
        print("Courses are now available in GLEH!")
        print("=" * 80)
        print()
        print("View courses at: http://localhost/")
        print()

    return True


if __name__ == '__main__':
    success = import_courses()
    sys.exit(0 if success else 1)
