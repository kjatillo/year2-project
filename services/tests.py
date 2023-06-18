import os
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .models import Category, Review, Service
from .views import (ServiceCreateView, ServiceDeleteView, ServiceUpdateView,
                    service_detail, service_list, submit_review)


class ServiceUnitTest(TestCase):
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

        self.category = Category.objects.create(name='Programming & Tech')
        self.service = Service.objects.create(
            name='I will build you a website',
            category=self.category,
            provider=self.user,
            image='../static/images/husky_pug.jpg',
            job_limit=3,
            price=500.00
        )

        self.service_list_url = reverse('services:all_services')
        self.service_list_by_category_url = reverse('services:services_by_category', args=[self.category.id])
        self.service_detail_url = reverse('services:service_detail', args=[self.category.id, self.service.id])
        self.post_service_url = reverse('services:post_service')
        self.edit_service_url = reverse('services:edit_service', args=[self.service.id])
        self.delete_service_url = reverse('services:delete_service', args=[self.service.id])
        self.submit_review_url = reverse('services:submit_review', args=[self.service.id])
    
    def tearDown(self):
        del self.user
        del self.category
        del self.service
        del self.service_list_url
        del self.service_list_by_category_url
        del self.service_detail_url
        del self.post_service_url
        del self.edit_service_url
        del self.delete_service_url
        del self.submit_review_url

    def test_submitNewReview_returnTrue(self):
        # Arrange
        subject = 'Test Review'
        rating = 5
        user = self.user
        review_str = f"{subject} ({rating}) by {user}"

        # Act
        if not Review.objects.filter(service=self.service, user=self.user).exists():
            review = Review.objects.create(
                service=self.service,
                user=user,
                subject=subject,
                review='This is a test comment',
                rating=rating
            )
        
        # Assert
        self.assertTrue(isinstance(review, Review))
        self.assertEqual(review.__str__(), review_str)

    def test_updateReview_returnTrue(self):
        # Arrange
        review = Review.objects.create(
            service=self.service,
            user=self.user,
            subject='Test Review',
            review='This is a test comment',
            rating=5
        )
        review_str = f"{review.subject} ({review.rating}) by {review.user}"

        # Act
        if Review.objects.filter(service=self.service, user=self.user).exists():
            review.rating = 5
            review.review = 'This is a test comment'
            review.save()
        
        # Assert
        self.assertTrue(isinstance(review, Review))
        self.assertEqual(review.__str__(), review_str)

    def test_formValid_returnTrue(self):
        # Arrange
        form_data = {
            'name': 'I will build you a website',
            'provider': self.user.id,
            'category': self.category.id,
            'price': 500.00,
            'image': '../static/images/husky_pug.jpg',
            'job_limit': 3,
        }
        expected_status_code = 200

        # Act
        response = self.client.post(self.post_service_url, form_data)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_serviceCreation_returnTrue(self):
        # Assert
        self.assertTrue(isinstance(self.service, Service))
        self.assertEqual(self.service.__str__(), self.service.name)

    # Status Code
    def test_categoryPageStatusCode_return200(self):
        # Assert
        expected_status_code = 200

        # Act
        response = self.client.get(self.service_list_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_serviceDeletePageStatusCode_return200(self):
        # Assert
        expected_status_code = 200

        # Act
        response = self.client.get(self.delete_service_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_serviceEditPageStatusCode_return200(self):
        # Assert
        expected_status_code = 200

        # Act
        response = self.client.get(self.edit_service_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_serviceNewPageStatusCode_return200(self):
        # Assert
        expected_status_code = 200

        # Act
        response = self.client.get(self.post_service_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_serviceDetailPageStatusCode_return200(self):
        # Assert
        expected_status_code = 200

        # Act
        response = self.client.get(self.service_detail_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    # Template Used
    def test_categoryPageTemplateUsed_returnTrue(self):
        # Assert
        expected_template = 'category.html'

        # Act
        response = self.client.get(self.service_list_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_serviceDeletePageTemplateUsed_returnTrue(self):
        # Assert
        expected_template = 'service_delete.html'

        # Act
        response = self.client.get(self.delete_service_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_serviceEditPageTemplateUsed_returnTrue(self):
        # Assert
        expected_template = 'service_edit.html'

        # Act
        response = self.client.get(self.edit_service_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_serviceNewPageTemplateUsed_returnTrue(self):
        # Assert
        expected_template = 'service_new.html'

        # Act
        response = self.client.get(self.post_service_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_serviceDetailPageTemplateUsed_returnTrue(self):
        # Assert
        expected_template = 'service.html'

        # Act
        response = self.client.get(self.service_detail_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    # Resolve Views
    def test_serviceCreateView_resolveView_returnTrue(self):
        # Assert
        expected_result = ServiceCreateView.as_view().__name__

        # Act
        view = resolve(self.post_service_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_serviceDeleteView_resolveView_returnTrue(self):
        # Assert
        expected_result = ServiceDeleteView.as_view().__name__

        # Act
        view = resolve(self.delete_service_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_serviceUpdateView_resolveView_returnTrue(self):
        # Assert
        expected_result = ServiceUpdateView.as_view().__name__

        # Act
        view = resolve(self.edit_service_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_serviceDetailView_resolveView_returnTrue(self):
        # Assert
        expected_result = service_detail.__name__

        # Act
        view = resolve(self.service_detail_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_serviceListView_resolveView_returnTrue(self):
        # Assert
        expected_result = service_list.__name__

        # Act
        view = resolve(self.service_list_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_submitReview_resolveView_returnTrue(self):
        # Assert
        expected_result = submit_review.__name__

        # Act
        view = resolve(self.submit_review_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)


class ServiceUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_a_postService_chromeDriver(self):
        # Arrage
        username = 'provider'
        password = 'testuser1212'
        service_name = 'Test Service'
        service_description = 'Test Description'
        service_price = 1500
        service_limit = 3
        img_name = 'husky_pug.jpg'
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images', img_name))

        # Act
        btn_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        btn_login.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(username)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_password.send_keys(password)

        btn_login_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login_account.click()

        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
        dropdown_menu.click()

        option_post_service = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li[2]/a')
        option_post_service.click()

        field_service_name = self.driver.find_element(By.XPATH, '//*[@id="id_name"]')
        field_service_name.send_keys(service_name)

        field_service_description = self.driver.find_element(By.XPATH, '//*[@id="id_description"]')
        field_service_description.send_keys(service_description)

        option_category = self.driver.find_element(By.XPATH, '//*[@id="id_category"]/option[4]')
        option_category.click()
        
        field_service_price = self.driver.find_element(By.XPATH, '//*[@id="id_price"]')
        field_service_price.send_keys(service_price)

        field_image = self.driver.find_element(By.XPATH, '//*[@id="id_image"]')
        field_image.send_keys(img_path)

        field_service_limit = self.driver.find_element(By.XPATH, '//*[@id="id_job_limit"]')
        field_service_limit.send_keys(service_limit)

        btn_post_service = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        self.driver.execute_script("arguments[0].click();", btn_post_service)

        # Assert
        # Title
        expected_title = service_name + ' - Tenner | Tenner'
        self.assertEqual(self.driver.title, expected_title)

        # Text
        self.assertIn(service_name, self.driver.page_source)
        self.assertIn('Edit Service', self.driver.page_source)
        self.assertIn('Delete Service', self.driver.page_source)

    def test_b_editService_chromeDriver(self):
        # Arrage
        username = 'provider'
        password = 'testuser1212'
        service_names = ['Song Composer', 'Song Writer']
        service_descriptions = ['Writing great songs for you', 'Composing great songs for you']
        service_prices = [2000.00, 3000.00]
        service_limits = [5, 7]
        new_service_name = ''
        new_service_description = ''
        
        # Act
        btn_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        btn_login.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(username)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_password.send_keys(password)

        btn_login_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login_account.click()

        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/a')
        dropdown_menu.click()

        option_services = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/ul/li[1]/a')
        option_services.click()

        all_services = self.driver.find_elements(By.XPATH, '/html/body/div[2]/div[1]/div/div')
        WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '/html/body/div[2]/div[1]/div/div')))
        for service in all_services:
            if service_names[0] in service.text:
                service.click()
                break
            elif service_names[1] in service.text:
                service.click()
                break
        
        btn_edit_service = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/p[4]/a')
        btn_edit_service.click()

        field_service_name = self.driver.find_element(By.XPATH, '//*[@id="id_name"]')
        if service_names[0] in field_service_name.get_attribute('value'):
            field_service_name.clear()
            field_service_name.send_keys(service_names[1])
            new_service_name = service_names[1]
        else:
            field_service_name.clear()
            field_service_name.send_keys(service_names[0])
            new_service_name = service_names[0]

        field_service_description = self.driver.find_element(By.XPATH, '//*[@id="id_description"]')
        if service_descriptions[0] in field_service_description.get_attribute('value'):
            field_service_description.clear()
            field_service_description.send_keys(service_descriptions[1])
            new_service_description = service_descriptions[1]
        else:
            field_service_description.clear()
            field_service_description.send_keys(service_descriptions[0])
            new_service_description = service_descriptions[0]

        field_service_price = self.driver.find_element(By.XPATH, '//*[@id="id_price"]')
        if str(service_prices[0]) in field_service_price.get_attribute('value'):
            field_service_price.clear()
            field_service_price.send_keys(service_prices[1])
        else:
            field_service_price.clear()
            field_service_price.send_keys(service_prices[0])

        field_service_limit = self.driver.find_element(By.XPATH, '//*[@id="id_job_limit"]')
        if str(service_limits[0]) in field_service_limit.get_attribute('value'):
            field_service_limit.clear()
            field_service_limit.send_keys(service_limits[1])
        else:
            field_service_limit.clear()
            field_service_limit.send_keys(service_limits[0])

        btn_save_changes = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        self.driver.execute_script("arguments[0].click();", btn_save_changes)

        # Assert
        # Title
        self.assertIn(new_service_name, self.driver.title)

        # Text
        self.assertIn(new_service_name, self.driver.page_source)
        self.assertIn(new_service_description, self.driver.page_source)
        self.assertIn('Edit Service', self.driver.page_source)

    def test_c_deleteService_chromeDriver(self):
        # Arrage
        username = 'provider'
        password = 'testuser1212'
        service_name = 'Test Service'

        # Act
        btn_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        btn_login.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(username)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_password.send_keys(password)

        btn_login_account = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login_account.click()

        dropdown_menu = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/a')
        dropdown_menu.click()

        option_services = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/ul/li[1]/a')
        option_services.click()

        all_services = self.driver.find_elements(By.XPATH, '/html/body/div[2]/div[1]/div/div')
        for service in all_services:
            if service_name in service.text:
                service.click()
                break

        btn_delete_service = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/p[5]/a')
        btn_delete_service.click()

        # Assert
        # Title
        expected_title = 'Delete Service | Tenner'
        self.assertEqual(expected_title, self.driver.title)

        # Text
        self.assertIn('Delete Service', self.driver.page_source)
        self.assertIn('This process cannot be reverted.', self.driver.page_source)
        self.assertIn('Cancel', self.driver.page_source)

        btn_delete_confirm = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/div[2]/button')
        btn_delete_confirm.click()
