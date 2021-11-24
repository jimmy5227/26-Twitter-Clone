"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
# from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD", None)
        u1id = 1
        u1.id =u1id

        m1 = Message(text='hi, this is a test', user_id=u1id)
        m1id = 1
        m1.id = m1id

        db.session.add(m1)
        db.session.commit()

        m1 = Message.query.get(m1id)
        u1 = User.query.get(u1id)

        self.m1 = m1
        self.m1id = m1id
        self.u1 = u1
        self.u1id = u1id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        m = Message(
            text="Does basic model work?",
            user_id=1
        )
        m.id = 2

        db.session.add(m)
        db.session.commit()

        self.assertIsNotNone(m)
        self.assertEqual(m.user.id, 1)
        self.assertEqual(len(self.u1.messages), 2)
        self.assertEqual(self.u1.messages[1].text, "Does basic model work?")


    def test_message_likes(self):
        """Does liking a message work?"""

        u2 = User.signup("like_user", "like@email.com", "password", None)
        u2id = 2
        u2.id = u2id
        db.session.add_all([u2])
        db.session.commit()

        u2.likes.append(self.m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == u2id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, self.m1.id)
