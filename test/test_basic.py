import unittest
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


class BasicTest(unittest.TestCase):

    def setUp(self):
        from flaskapp import db
        db.drop_all()
        db.create_all()

    def test_create_user(self):
        from flaskapp import User, db, bcrypt
        # Add a user
        admin = User(username='admin', email='admin@admin.com', password=bcrypt.generate_password_hash("admin").decode('utf-8'))
        db.session.add(admin)
        db.session.commit()
        # Check that the user was added.
        user = User.query.filter_by(username="admin").first()
        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "admin@admin.com")

    def test_view_user_profile(self):
        from flaskapp import User, db, bcrypt, app
        from bs4 import BeautifulSoup
        # Add 2 users
        admin = User(username='admin', email='admin@admin.com', password=bcrypt.generate_password_hash("admin").decode('utf-8'))
        susan = User(username='susan', email='susan@example.com', password=bcrypt.generate_password_hash("susan").decode('utf-8'))
        db.session.add(admin)
        db.session.add(susan)
        db.session.commit()
        # Try to view susan's profile without logging in
        test_client = app.test_client()
        response = test_client.get('/user/susan/profile', follow_redirects=True)
        response_soup = BeautifulSoup(response.data, 'html.parser')
        # Unsuccessful
        self.assertEqual(response_soup.title.string, u'Login - UMD Connect')
