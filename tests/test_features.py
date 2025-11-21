"""
Test script to verify user profile and ebook reader features
"""
from src.app import app
from src.database import db
from src.models import User, Ebook, ReadingProgress

def test_features():
    with app.app_context():
        print("=" * 60)
        print("TESTING USER PROFILE AND EBOOK READER FEATURES")
        print("=" * 60)

        # Test 1: Check if User model has new profile fields
        print("\n[TEST 1] Checking User model fields...")
        user = User.query.filter_by(username='admin').first()
        if user:
            print(f"  Admin user found: {user.username}")
            print(f"  - Avatar: {user.avatar}")
            print(f"  - About me: {user.about_me or '(empty)'}")
            print(f"  - Gender: {user.gender or '(not set)'}")
            print(f"  - Pronouns: {user.pronouns or '(not set)'}")
            print(f"  - Created at: {user.created_at}")
            print(f"  - Is admin: {user.is_admin}")
            print("  PASS: User profile fields exist")
        else:
            print("  WARNING: Admin user not found")

        # Test 2: Check ReadingProgress model
        print("\n[TEST 2] Checking ReadingProgress model...")
        try:
            progress_count = ReadingProgress.query.count()
            print(f"  Found {progress_count} reading progress entries")
            print("  PASS: ReadingProgress model accessible")
        except Exception as e:
            print(f"  FAIL: {e}")

        # Test 3: Check ebook data
        print("\n[TEST 3] Checking ebook data...")
        ebook = Ebook.query.first()
        if ebook:
            print(f"  Sample ebook: {ebook.title}")
            print(f"  - UID: {ebook.uid}")
            print(f"  - Path: {ebook.path}")
            print(f"  - Cover: {ebook.cover_path}")
            print("  PASS: Ebook data accessible")
        else:
            print("  WARNING: No ebooks found")

        # Test 4: Check routes
        print("\n[TEST 4] Checking routes...")
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))

        critical_routes = [
            '/profile',
            '/api/profile',
            '/api/profile/avatar',
            '/reader/<uid>',
            '/api/reading-progress/<uid>'
        ]

        for route in critical_routes:
            # Check if route exists (with or without parameters)
            route_exists = any(route.replace('<uid>', '<') in r for r in routes)
            status = "PASS" if route_exists else "FAIL"
            print(f"  {status}: {route}")

        # Test 5: Check static files
        print("\n[TEST 5] Checking static files...")
        import os
        files_to_check = [
            'static/js/profile.js',
            'static/avatars/default_avatar.svg',
            'templates/profile.html',
            'templates/reader.html'
        ]

        for file_path in files_to_check:
            full_path = os.path.join(app.root_path, file_path)
            exists = os.path.exists(full_path)
            status = "PASS" if exists else "FAIL"
            print(f"  {status}: {file_path}")

        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)

if __name__ == '__main__':
    test_features()
