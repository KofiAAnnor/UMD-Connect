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
