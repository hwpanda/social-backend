from django.test import TestCase
from rest_framework.test import APIClient
from testing.testcases import TestCase
from accounts.models import UserProfile


# Create your tests here.
LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username='testing001',
            email='testing001@testing.com'
            password='correct password'
        )
    
    def test_login(self):
        # This api only takes post. Test expected to fail
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 400)
        
        # wrong username with post
        response = self.client.post(LOGIN_URL, {
            'username': 'wrong username',
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['errors']['username'][0]), 'User does not exist.')
        
        # not logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        
        # logging in
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['id'], self.user.id)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
    
    def test_logout(self):
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
    
    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@testing.com',
            'password': 'any password',
        }

        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@testing.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@testing.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)


        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
    


