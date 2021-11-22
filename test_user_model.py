"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows
from flask_bcrypt import Bcrypt

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u1id = 1
        u1.id =u1id

        u2 = User(email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        u2id = 2
        u2.id =u2id

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)

        self.u1 = u1
        self.u1id = u1id
        self.u2 = u2
        self.u2id = u2id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    # My tests:
    def test_repr(self):
        """Does __repr__ method work?"""

        self.assertEqual(str(self.u1), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

        self.u1.following.append(self.u2)
        db.session.commit

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_not_followed(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        self.assertFalse(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.assertFalse(self.u1.is_followed_by(self.u2))
        self.assertFalse(self.u2.is_followed_by(self.u1))
    
    def test_create_user(self):
        """Does User.create successfully create a new user given valid credentials?"""

        user = User.signup('test', 'test@fake.com', "HASHED_PASSWORD", None)
        user.id = 3
        db.session.commit()

        self.assertIsNotNone(user)
        self.assertEqual(user.id, 3)
        self.assertEqual(user.email, 'test@fake.com')
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.image_url, '/static/images/default-pic.png')
        self.assertTrue(user.password.startswith("$2b$"))

    def test_create_failed_user(self):
        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        empty_username = User.signup(None, 'test@fake.com', "HASHED_PASSWORD", None)
        empty_username.id = 4

        empty_email = User.signup("test", None, "HASHED_PASSWORD", None)
        empty_email.id = 5

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

        with self.assertRaises(ValueError) as context:
            User.signup('test', 'test@fake.com', None, None)

        with self.assertRaises(ValueError) as context:
            User.signup('test', 'test@fake.com', "", None)

    def test_authenticate_user(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        
        auth = User.authenticate(self.u1.username, "HASHED_PASSWORD")
        self.assertIsNotNone(auth)
        self.assertEqual(auth.id, 1)
        self.assertEqual(auth.email, 'test@fake.com')
        self.assertEqual(auth.username, 'test')
        self.assertEqual(auth.image_url, '/static/images/default-pic.png')
        self.assertTrue(auth.password.startswith("$2b$"))

    def test_fail_authenticate_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""

        self.assertFalse(User.authenticate('fakeusername', 'password'))

    def test_fail_authenticate_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
    
        self.assertFalse(User.authenticate(self.u1.username, 'BAD_PASSWORD'))