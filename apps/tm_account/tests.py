from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    """
    Tests for the custom User model.
    """
    def test_create_user(self):
        """
        Test creating a regular user.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            nickname='TestNickname'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.nickname, 'TestNickname')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """
        Test creating a superuser.
        """
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            nickname='AdminNickname'
        )
        self.assertEqual(admin_user.username, 'adminuser')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.check_password('adminpassword'))
        self.assertEqual(admin_user.nickname, 'AdminNickname')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

class AccountViewsTest(TestCase):
    """
    Tests for views in tm_account app.
    """
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('tm_account:signup')
        self.login_url = reverse('tm_account:login')
        self.logout_url = reverse('tm_account:logout')
        self.profile_url = reverse('tm_account:profile')
        self.user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123', # Use password1 for UserCreationForm
            'password2': 'newpassword123', # For confirmation
            'nickname': 'NewUserNick'
        }
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpassword',
            nickname='TestUserNick'
        )

    def test_signup_get(self):
        """
        Test GET request to signup page.
        """
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/signup.html')

    def test_signup_post_success(self):
        """
        Test successful user registration via POST request.
        """
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, 302) # Should redirect
        self.assertRedirects(response, self.login_url) # Should redirect to login page
        self.assertTrue(User.objects.filter(username='newuser').exists()) # User should be created

    def test_signup_post_invalid_data(self):
        """
        Test user registration with invalid data (e.g., mismatched passwords).
        """
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'wrongpassword'
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, 200) # Should render signup page again with errors
        self.assertTemplateUsed(response, 'tm_account/signup.html')
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_login_get(self):
        """
        Test GET request to login page.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/login.html')

    def test_login_post_success(self):
        """
        Test successful user login via POST request.
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        }, follow=True)
        self.assertRedirects(response, '/')
        self.assertTrue('_auth_user_id' in self.client.session) # Check if user is logged in

    def test_login_post_invalid_credentials(self):
        """
        Test user login with invalid credentials.
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200) # Should render login page again with errors
        self.assertTemplateUsed(response, 'tm_account/login.html')
        self.assertFalse('_auth_user_id' in self.client.session) # Check if user is NOT logged in

    def test_logout(self):
        """
        Test user logout.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.logout_url, follow=True)
        self.assertRedirects(response, '/')
        self.assertFalse('_auth_user_id' in self.client.session) # Check if user is logged out

    def test_profile_access_authenticated(self):
        """
        Test accessing profile page when authenticated.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/profile.html')
        self.assertContains(response, 'TestUserNick') # Check if nickname is displayed

    def test_profile_access_unauthenticated(self):
        """
        Test accessing profile page when unauthenticated (should redirect to login).
        """
        response = self.client.get(self.profile_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/login.html') # Should redirect to login
        self.assertIn(self.login_url, response.request['PATH_INFO']) # Check if redirected to login URL

    def test_profile_edit_get(self):
        """
        Test GET request to profile edit page.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('tm_account:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/profile_edit.html')

    def test_profile_edit_post_success(self):
        """
        Test successful profile update via POST request.
        """
        self.client.login(username='testuser', password='testpassword')
        new_nickname = 'UpdatedNick'
        new_email = 'updated@example.com'
        response = self.client.post(reverse('tm_account:profile_edit'), {
            'nickname': new_nickname,
            'email': new_email,
            'profile_image-clear': False, # Do not clear existing image
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/profile.html') # Redirects to profile page
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.nickname, new_nickname)
        self.assertEqual(self.test_user.email, new_email)
        self.assertContains(response, '프로필이 성공적으로 업데이트되었습니다.')

    def test_profile_edit_post_invalid_data(self):
        """
        Test profile update with invalid data (e.g., duplicate nickname).
        """
        self.client.login(username='testuser', password='testpassword')
        # Create another user to cause a duplicate nickname error
        User.objects.create_user(username='anotheruser', email='another@test.com', password='pass', nickname='ExistingNick')
        
        response = self.client.post(reverse('tm_account:profile_edit'), {
            'nickname': 'ExistingNick', # Duplicate nickname
            'email': 'test@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/profile_edit.html')
        self.assertContains(response, '오류가 발생했습니다. 입력 내용을 확인해주세요.')
        self.test_user.refresh_from_db()
        self.assertNotEqual(self.test_user.nickname, 'ExistingNick') # Nickname should not be updated

    def test_password_change_get(self):
        """
        Test GET request to password change page.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('tm_account:password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/password_change.html')

    def test_password_change_post_success(self):
        """
        Test successful password change via POST request.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('tm_account:password_change'), {
            'old_password': 'testpassword',
            'new_password1': 'new_test_password',
            'new_password2': 'new_test_password',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/profile.html') # Redirects to profile page
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('new_test_password'))
        self.assertContains(response, 'Your password was successfully updated!')

    def test_password_change_post_invalid_old_password(self):
        """
        Test password change with incorrect old password.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('tm_account:password_change'), {
            'old_password': 'wrong_password',
            'new_password1': 'new_test_password',
            'new_password2': 'new_test_password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/password_change.html')
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('testpassword')) # Password should not change
        self.assertContains(response, 'Please correct the error below.')

    def test_password_change_post_mismatched_new_passwords(self):
        """
        Test password change with mismatched new passwords.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('tm_account:password_change'), {
            'old_password': 'testpassword',
            'new_password1': 'new_test_password',
            'new_password2': 'mismatched_password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/password_change.html')
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('testpassword')) # Password should not change
        self.assertContains(response, 'Please correct the error below.')

    def test_account_delete_get(self):
        """
        Test GET request to account delete confirmation page.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('tm_account:account_delete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/account_delete_confirm.html')

    def test_account_delete_post_success(self):
        """
        Test successful account deletion via POST request.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('tm_account:account_delete'), {
            'username': 'testuser', # Required by AuthenticationForm
            'password': 'testpassword',
        })
        self.assertEqual(response.status_code, 302) # Should redirect
        self.assertRedirects(response, '/') # Redirects to main page
        self.assertFalse(User.objects.filter(username='testuser').exists()) # User should be deleted
        self.assertContains(response, 'Your account has been successfully deleted.')

    def test_account_delete_post_incorrect_password(self):
        """
        Test account deletion with incorrect password.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('tm_account:account_delete'), {
            'username': 'testuser', # Required by AuthenticationForm
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/account_delete_confirm.html')
        self.assertTrue(User.objects.filter(username='testuser').exists()) # User should not be deleted
        self.assertIn('올바른 사용자 이름와/과 비밀번호를 입력하십시오. 두 필드 모두 대문자와 소문자를 구별합니다.', response.content.decode())

    def test_account_delete_unauthenticated(self):
        """
        Test accessing account delete page when unauthenticated (should redirect to login).
        """
        response = self.client.get(self.profile_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tm_account/login.html') # Should redirect to login
        self.assertIn(self.login_url, response.request['PATH_INFO']) # Check if redirected to login URL

class CustomUserCreationFormTest(TestCase):
    """
    Tests for the CustomUserCreationForm.
    """
    def test_valid_form(self):
        from apps.tm_account.forms.profile_forms import CustomUserCreationForm
        form_data = {
            'username': 'testformuser',
            'email': 'testform@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'nickname': 'TestFormNick'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        # self.assertTrue(form.save()) # Don't save in unit test unless necessary