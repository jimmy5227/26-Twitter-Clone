import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app


db.create_all()

class UserViewTestCase(TestCase):
    """Test views for user view."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD", None)
        u1id = 1
        u1.id = u1id

        u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        u2id = 2
        u2.id = u2id

        u3 = User.signup("testuser3", "test3@test.com", "HASHED_PASSWORD", None)
        u3id = 3
        u3.id = u3id

        db.session.commit()

        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)
        u3 = User.query.get(u3id)

        self.u1 = u1
        self.u1id = u1id
        self.u2 = u2
        self.u2id = u2id
        self.u3 = u3
        self.u3id = u3id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_users_index(self):
        """Does user appear in main index?"""
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))
    
    def test_user_search(self):
        """Does user appear in search?"""
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))

    def test_user_profile(self):
        """Does user profile display the correct corresponding user"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
    
    def setup_likes(self):
        """This will create messages and have the test users like them"""
        m1 = Message(id=1, text="test message1", user_id=self.u1id)
        m2 = Message(id=2, text="test message2", user_id=self.u2id)
        m3 = Message(id=3, text="test message3", user_id=self.u3id)

        l1 = Likes(user_id=self.u1id, message_id=1)
        l2 = Likes(user_id=self.u2id, message_id=2)
        l3 = Likes(user_id=self.u3id, message_id=3)

        db.session.add_all([m1, m2, m3, l1, l2, l3])
        db.session.commit()

    def test_user_likes(self):
        """"""
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.u1id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser1", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("1", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)