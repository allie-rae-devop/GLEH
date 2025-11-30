#!/usr/bin/env python
"""Clear testuser's profile data"""
from src.app import app, db
from src.models import User, CourseProgress, CourseNote, ReadingProgress, EbookNote

with app.app_context():
    testuser = User.query.filter_by(username='testuser').first()

    if testuser:
        # Delete all old data
        CourseProgress.query.filter_by(user_id=testuser.id).delete()
        CourseNote.query.filter_by(user_id=testuser.id).delete()
        ReadingProgress.query.filter_by(user_id=testuser.id).delete()
        # Keep EbookNote - that's the new one we want to test

        db.session.commit()
        print(f'Cleared old profile data for testuser (user_id={testuser.id})')
        print('- Deleted course progress')
        print('- Deleted course notes')
        print('- Deleted old reading progress')
        print('- Kept new ebook notes')
        print('Testuser profile cleared successfully!')
    else:
        print('Testuser not found')
