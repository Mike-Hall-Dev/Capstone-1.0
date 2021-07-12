from app import app
from flask import session
from unittest import TestCase


class MovieViewsTestCase(TestCase):
    def test_signup_redirect(self):
        with app.test_client() as client:
            res = client.get('/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(
                '<h2 class="join-message">Welcome to Cinema Search!</h2>', html)

    def test_view_home_page(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['curr_user'] = 28

        res = client.get('/')
        html = res.get_data(as_text=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn('<title> Popular </title>', html)

    def test_view_upcoming(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['curr_user'] = 28

        res = client.get('/upcoming')
        html = res.get_data(as_text=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn('<title> Upcoming </title>', html)
