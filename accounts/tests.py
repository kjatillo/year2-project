import os
from datetime import datetime
from time import sleep
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from .models import Profile
from .views import (AccountDeleteView, ProfileEditView, ProfilePageView,
                    SignUpView)


class AccountUnitTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='unittest',
            email='unittest@email.com',
            first_name='John',
            last_name='Smith',
            password='testuser1212',
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='admin@superuser.com',
            password='testadmin1212'
        )
        
        self.user_group = Group.objects.create(name='User')
        self.service_provider_group = Group.objects.create(name='Service Provider')
        self.service_provider_group.permissions.add(Permission.objects.get(name='Can add service'))
        self.service_provider_group.user_set.add(self.user)
        self.user_group.user_set.add(self.superuser)
        self.client.login(username='unittest', password='testuser1212')
        self.client.login(username='superuser', password='testadmin1212')

        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.pass_reset_url = reverse('password_reset')
        self.pass_reset_done_url = reverse('password_reset_done')
        self.pass_reset_complete_url = reverse('password_reset_complete')
        self.account_delete_url = reverse('account_delete', kwargs={'pk': self.user.pk})
        self.user_profile_url = reverse('view_profile', kwargs={'username': self.user.username})
        self.edit_profile_url = reverse('edit_profile', kwargs={'username': self.user.username})

    def tearDown(self):
        del self.user
        del self.superuser
        del self.signup_url
        del self.login_url
        del self.account_delete_url
        del self.user_profile_url
        del self.edit_profile_url
        del self.pass_reset_url
        del self.pass_reset_done_url
        del self.pass_reset_complete_url

    def test_customUserAccountCreation_returnTrue(self):
        # Assert
        self.assertTrue(self.user)

    def test_superuserAccountCreation_returnTrue(self):
        # Assert
        self.assertTrue(self.superuser)

    def test_customUserSignUpInputDetails_returnTrue(self):
        # Arrange
        username = 'unittest'
        email = 'unittest@email.com'
        first_name = 'John'
        last_name = 'Smith'

        # Assert
        self.assertEqual(self.user.username, username)
        self.assertEqual(self.user.email, email)
        self.assertEqual(self.user.first_name, first_name)
        self.assertEqual(self.user.last_name, last_name)
        
    def test_customUserNotStaff_returnTrue(self):
        # Assert
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_customUserNotSuperUser_returnTrue(self):
        # Assert
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_superuser)

    def test_accountIsSuperUser_returnTrue(self):
        # Arrange
        username = 'superuser'
        email = 'admin@superuser.com'

        # Assert
        self.assertEqual(self.superuser.username, username)
        self.assertEqual(self.superuser.email, email)
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_accountNotSuperUser_returnTrue(self):
        # Arrange
        username = 'unittest'
        email = 'unittest@email.com'

        # Assert
        self.assertNotEqual(self.superuser.username, username)
        self.assertNotEqual(self.superuser.email, email)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_userProfileCreation_returnTrue(self):
        # Assert
        self.assertEqual(self.user.profile, Profile.objects.get(user=self.user))

    def test_profileModelStrRepresentation_returnUsername(self):
        # Arrange
        username = 'unittest'

        # Assert
        self.assertEqual(self.user.profile.__str__(), username)
        
    # Resolve Views
    def test_signUpView_returnTrue(self):
        # Arrange
        expected_result = SignUpView.as_view().__name__

        # Act
        view = resolve(self.signup_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_profilePageView_returnTrue(self):
        # Arrange
        expected_result = ProfilePageView.as_view().__name__
        
        # Act
        view = resolve(self.user_profile_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_profileEditView_returnTrue(self):
        # Arrange
        expected_result = ProfileEditView.as_view().__name__

        # Act
        view = resolve(self.edit_profile_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_accountDeleteView_returnTrue(self):
        # Arrange
        expected_result = AccountDeleteView.as_view().__name__

        # Act
        view = resolve(self.account_delete_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    # Status Code
    def test_signUpPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.signup_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_loginPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.login_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_userProfileStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.user_profile_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_editProfileStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        self.client.login(username='unittest', password='testuser1212')
        response = self.client.get(self.edit_profile_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_passwordResetFormPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.pass_reset_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_accountDeleteStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.account_delete_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_passwordResetDoneStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.pass_reset_done_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_passwordResetCompleteStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.pass_reset_complete_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_passwordEmailSentStatusCode_return200(self):
        # Arrange
        email = 'unittest@email.com'
        expected_status_code = 200

        # Act
        response = self.client.post(self.pass_reset_url, {'email': email}, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_formNotValid_returnForm(self):
        # Arrange
        username = 'unittest'
        email = 'unittest@email.com'
        first_name = 'Jane'
        last_name = 'Doe'
        password = 'testuser1212'
        expected_status_code = 200

        # Act
        data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
        }
        response = self.client.post(self.signup_url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    # Template Used
    def test_signUpTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/signup.html'

        # Act
        response = self.client.get(self.signup_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_loginPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/login.html'

        # Act
        response = self.client.get(self.login_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)
    
    def test_userProfileTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/user_profile.html'

        # Act
        response = self.client.get(self.user_profile_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_editProfileTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/edit_profile.html'

        # Act
        self.client.login(username='unittest', password='testuser1212')
        response = self.client.get(self.edit_profile_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)
    
    def test_passwordResetFormTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/password_reset_form.html'

        # Act
        response = self.client.get(self.pass_reset_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)  

    def test_passwordResetDoneTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/password_reset_done.html'

        # Act
        response = self.client.get(self.pass_reset_done_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)
        
    def test_passwordResetCompleteTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'registration/password_reset_complete.html'

        # Act
        response = self.client.get(self.pass_reset_complete_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)


class AccountUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_registerAccount_chromeDriver(self):
        # Arrange
        ts = datetime.timestamp(datetime.now())
        input_username = f'newuser{str(ts)[:10]}'
        input_email = f'newuser{ts}@email.com'
        input_fname = 'John'
        input_lname = 'Smith'
        input_password = 'KVTLB@d^6LEf'

        # Act
        btn_signup = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[2]')
        btn_signup.click()

        # Assert
        # Title
        expected_title_signup = 'Create a New Account | Tenner'
        self.assertEqual(self.driver.title, expected_title_signup)

        # Text
        self.assertIn('Sign up', self.driver.page_source)
        self.assertIn('Welcome', self.driver.page_source)
        self.assertIn('Register Account', self.driver.page_source)

        # Fields
        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(input_username)

        field_email = self.driver.find_element(By.XPATH, '//*[@id="id_email"]')
        field_email.send_keys(input_email)

        field_fname = self.driver.find_element(By.XPATH, '//*[@id="id_first_name"]')
        field_fname.send_keys(input_fname)

        field_lname = self.driver.find_element(By.XPATH, '//*[@id="id_last_name"]')
        field_lname.send_keys(input_lname)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password1"]')
        field_password.send_keys(input_password)

        field_password_confirm = self.driver.find_element(By.XPATH, '//*[@id="id_password2"]')
        field_password_confirm.send_keys(input_password)

        option_account_type  = self.driver.find_element(By.XPATH, '//*[@id="id_group"]/option[2]')
        option_account_type.click()

        sleep(1)
        btn_register_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_register_account.click()

        # Assert
        # Title
        expected_title = 'Login | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Login', self.driver.page_source)
        self.assertIn('Welcome back', self.driver.page_source)
        self.assertIn('Forgot password?', self.driver.page_source)

    def test_loginAccount_chromeDriver(self):
        # Arrange
        input_username = 'newuser'
        input_password = 'KVTLB@d^6LEf'

        # Act
        btn_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        btn_login.click()

        # Assert
        # Title
        expected_title_login = 'Login | Tenner'
        self.assertEqual(self.driver.title, expected_title_login)

        # Text
        self.assertIn('Login', self.driver.page_source)
        self.assertIn('Welcome back', self.driver.page_source)
        self.assertIn('Don\'t have an account?', self.driver.page_source)

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(input_username)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_password.send_keys(input_password)

        sleep(1)
        btn_login = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login.click()

        # Assert
        # Title
        expected_title = 'Home | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn(input_username, self.driver.page_source)
        self.assertIn('Logout', self.driver.page_source)
        self.assertIn('Delete Account', self.driver.page_source)

    def test_logoutAccount_chromeDriver(self):
        # Arrange
        self.test_loginAccount_chromeDriver()

        # Act
        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
        dropdown_menu.click()

        btn_logout = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li[9]/a')
        btn_logout.click()

        # Assert
        # Title
        expected_title = 'Home | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Log in', self.driver.page_source)
        self.assertIn('Sign Up', self.driver.page_source)
        self.assertIn('Tenner', self.driver.page_source)

    def test_viewUserProfile_chromeDriver(self):
        # Arrange
        self.test_loginAccount_chromeDriver()

        # Act
        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
        dropdown_menu.click()

        dropdown_option_view_profile = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li[5]/a')
        dropdown_option_view_profile.click()
    
        # Assert
        # Title
        expected_title = 'User Profile | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('User Profile', self.driver.page_source)
        self.assertIn('My details', self.driver.page_source)
        self.assertIn('Last Login', self.driver.page_source)

    def test_editUserProfile_chromeDriver(self):
        # Arrange
        self.test_loginAccount_chromeDriver()
        img_name = 'husky_pug.jpg'
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images', img_name))
        input_email = 'newuser@email.com'
        input_fname = 'Johnny'
        input_lname = 'Smithy'

        # Act
        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
        dropdown_menu.click()

        dropdown_option_edit_profile = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li[6]/a')
        dropdown_option_edit_profile.click()

        field_email = self.driver.find_element(By.XPATH, '//*[@id="id_email"]')
        field_email.clear()
        field_email.send_keys(input_email)

        field_fname = self.driver.find_element(By.XPATH, '//*[@id="id_first_name"]')
        field_fname.clear()
        field_fname.send_keys(input_fname)

        field_lname = self.driver.find_element(By.XPATH, '//*[@id="id_last_name"]')
        field_lname.clear()
        field_lname.send_keys(input_lname)

        upload_image = self.driver.find_element(By.XPATH, '//*[@id="id_image"]')
        upload_image.clear()
        upload_image.send_keys(img_path)

        btn_save_changes = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_save_changes.click()
        
        # Assert
        # Title
        expected_title = 'User Profile | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('User Profile', self.driver.page_source)
        self.assertIn(input_fname, self.driver.page_source)
        self.assertIn(input_lname, self.driver.page_source)

    def test_changeAccountPassword_chromeDriver(self):
        # Arrange
        ts = datetime.timestamp(datetime.now())
        input_username = f'newuser{str(ts)[:10]}'
        input_email = f'newuser{ts}@email.com'
        input_fname = 'John'
        input_lname = 'Smith'
        input_password = 'KVTLB@d^6LEf'
        new_password = 'yWW&Y%3vpB^!'

        # Act
        btn_signup = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[2]')
        btn_signup.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(input_username)

        field_email = self.driver.find_element(By.XPATH, '//*[@id="id_email"]')
        field_email.send_keys(input_email)

        field_fname = self.driver.find_element(By.XPATH, '//*[@id="id_first_name"]')
        field_fname.send_keys(input_fname)

        field_lname = self.driver.find_element(By.XPATH, '//*[@id="id_last_name"]')
        field_lname.send_keys(input_lname)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password1"]')
        field_password.send_keys(input_password)

        field_password_confirm = self.driver.find_element(By.XPATH, '//*[@id="id_password2"]')
        field_password_confirm.send_keys(input_password)

        option_account_type  = self.driver.find_element(By.XPATH, '//*[@id="id_group"]/option[2]')
        option_account_type.click()

        sleep(1)
        btn_register_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_register_account.click()

        btn_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        btn_login.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(input_username)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_password.send_keys(input_password)

        sleep(1)
        btn_login = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login.click()
        
        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
        self.driver.execute_script("arguments[0].click();", dropdown_menu)

        dropdown_option_change_password = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li[5]/a')
        dropdown_option_change_password.click()
        
        field_old_password = self.driver.find_element(By.XPATH, '//*[@id="id_old_password"]')
        field_old_password.send_keys(input_password)

        field_new_password1 = self.driver.find_element(By.XPATH, '//*[@id="id_new_password1"]')
        field_new_password1.send_keys(new_password)

        field_new_password2 = self.driver.find_element(By.XPATH, '//*[@id="id_new_password2"]')
        field_new_password2.send_keys(new_password)

        btn_change_password = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_change_password.click()

        # Assert
        # Title
        expected_title = 'Password Change Done | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Password change', self.driver.page_source)
        self.assertIn('Password change success!', self.driver.page_source)
        self.assertIn('Your password has been changed successfully.', self.driver.page_source)

    def test_passwordReset_chromeDriver(self):
        # Arrange
        input_email = 'newuser@email.com'

        # Act
        btn_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        btn_login.click()

        btn_reset = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/p/a')
        btn_reset.click()

        field_email = self.driver.find_element(By.XPATH, '//*[@id="id_email"]')
        field_email.send_keys(input_email)

        btn_reset_password = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_reset_password.click()

        # Assert
        # Title
        expected_title = 'Password Reset Sent | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Password reset', self.driver.page_source)
        self.assertIn('Password reset link sent', self.driver.page_source)
        self.assertIn('We\'ve emailed you instructions for setting your password.', self.driver.page_source)

    def test_deleteAccount_chromeDriver(self):
        # Arrange
        input_username = 'testuser'
        input_email = 'test@email.com'
        input_fname = 'Jane'
        input_lname = 'Doe'
        input_password = 'KVTLB@d^6LEf'
        input_password_confirm = 'KVTLB@d^6LEf'

        # Act
        btn_signup = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[2]')
        btn_signup.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(input_username)

        field_email = self.driver.find_element(By.XPATH, '//*[@id="id_email"]')
        field_email.send_keys(input_email)

        field_fname = self.driver.find_element(By.XPATH, '//*[@id="id_first_name"]')
        field_fname.send_keys(input_fname)

        field_lname = self.driver.find_element(By.XPATH, '//*[@id="id_last_name"]')
        field_lname.send_keys(input_lname)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password1"]')
        field_password.send_keys(input_password)

        field_password_confirm = self.driver.find_element(By.XPATH, '//*[@id="id_password2"]')
        field_password_confirm.send_keys(input_password_confirm)

        option_account_type  = self.driver.find_element(By.XPATH, '//*[@id="id_group"]/option[3]')
        option_account_type.click()

        sleep(1)
        btn_register_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_register_account.click()

        field_login_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_login_username.send_keys(input_username)

        field_login_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_login_password.send_keys(input_password)

        sleep(1)
        btn_login = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login.click()

        sleep(1)
        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
        dropdown_menu.click()

        num_dropdown_options = self.driver.find_elements(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li')
        for option in num_dropdown_options:
            if option.text == 'Delete Account':
                option.click()
                break

        # Assert
        # Title
        expected_title = 'Account Delete | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Account Delete', self.driver.page_source)
        self.assertIn('Delete your account', self.driver.page_source)
        self.assertIn('This process cannot be reverted.', self.driver.page_source)
    
        btn_delete_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/div[2]/button')
        btn_delete_account.click()
