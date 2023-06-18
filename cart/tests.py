from time import sleep
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from services.models import Category, Service
from .models import Cart, CartItem
from .views import add_cart, cart_detail, full_remove


class CartUnitTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='unittest',
            email='unittest@email.com',
            first_name='John',
            last_name='Smith',
            password='testuser1212',
        )

        self.user_group = Group.objects.create(name='User')
        self.user_group.user_set.add(self.user)

        self.category = Category.objects.create(name='Programming & Tech')
        self.service = Service.objects.create(
            name='I will build you a website',
            category=self.category,
            provider=self.user,
            image='../static/images/husky_pug.jpg',
            job_limit=3,
            price=500.00
        )
        
        self.cart = Cart.objects.create()
        self.cart_item = CartItem.objects.create(
            service=self.service,
            cart=self.cart,
            quantity=1,
            active=True,
        )

        self.factory = RequestFactory()
        get_response = MagicMock()
        self.session_middleware = SessionMiddleware(get_response)

        self.cart_detail_url = reverse('cart:cart_detail')
        self.cart_add_url = reverse('cart:add_cart', args=[self.service.id])
        self.cart_full_remove = reverse('cart:full_remove', args=[self.service.id])

    def tearDown(self):
        del self.cart_detail_url
        del self.cart_add_url
        del self.cart_full_remove
        del self.user
        del self.user_group
        del self.category
        del self.service
        del self.cart
        del self.cart_item

    def test_addServiceToCart_returnTrue(self):
        # Arrange
        request = self.factory.post(self.cart_add_url)
        self.session_middleware.process_request(request)
        request.session.save()
        expected_status_code = 302
        
        # Act
        response = add_cart(request, self.service.id)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(len(CartItem.objects.filter(cart=self.cart)), 1)
        self.assertEqual(CartItem.objects.filter(cart=self.cart, service=self.service).count(), 1)

    # Status Code
    def test_cartDetailPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.cart_detail_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_cartAddPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.cart_add_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_cartRemovePageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        self.client.get(self.cart_add_url, follow=True)
        response = self.client.get(self.cart_full_remove, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    # Template Used
    def test_cartDetailPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'cart.html'

        # Act
        response = self.client.get(self.cart_detail_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    # Resolve Views
    def test_cartDetailPageResolveView_returnTrue(self):
        # Arrange
        expected_result = cart_detail.__name__

        # Arrange
        view = resolve(self.cart_detail_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_cartAddPageResolveView_returnTrue(self):
        # Arrange
        expected_result = add_cart.__name__

        # Arrange
        view = resolve(self.cart_add_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)
    
    def test_cartRemovePageResolveView_returnTrue(self):
        # Arrange
        expected_result = full_remove.__name__

        # Arrange
        view = resolve(self.cart_full_remove)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)


class CartUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_addServiceToCart_chromeDriver(self):
        # Arrange
        add_cart_service = 'Poem Writer'
        username = 'user'
        password = 'testuser1212'

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

        option_all_services = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/ul/li[1]/a')
        option_all_services.click()

        all_services = self.driver.find_elements(By.XPATH, '/html/body/div[2]/div[1]/div/div')
        WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '/html/body/div[2]/div[1]/div/div')))
        for service in all_services:
            if add_cart_service in service.text:
                service.click()
                break

        btn_add_cart = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/a[1]')
        self.driver.execute_script('arguments[0].click();', btn_add_cart)

        # Assert
        # Title
        expected_title = 'Your Cart | Tenner'
        self.assertEqual(self.driver.title, expected_title)

        # Text
        self.assertIn('Your Cart', self.driver.page_source)
        self.assertIn('Your Services', self.driver.page_source)
        self.assertIn('Checkout', self.driver.page_source)

    def test_removeServiceFromCart_chromeDriver(self):
        # Arrange
        self.test_addServiceToCart_chromeDriver()

        # Act
        btn_remove_cart = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/table/tbody/tr/td[4]/a')
        btn_remove_cart.click()

        # Assert
        # Title
        expected_title = 'Your Cart | Tenner'
        self.assertEqual(self.driver.title, expected_title)

        # Text
        self.assertIn('Your cart is empty', self.driver.page_source)
        self.assertIn('Please click', self.driver.page_source)
        self.assertIn('continue browsing our services.', self.driver.page_source)

    def test_checkoutService_chromeDriver(self):
        # Arrange
        self.test_addServiceToCart_chromeDriver()
        email  = 'user@email.com'
        name = 'John Smith'
        address = '123 Fake Street'
        city = 'Dublin'
        card_cvc = '123'

        # Act
        btn_checkout = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/form/button/span')
        btn_checkout.click()
        
        frame = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/iframe')))
        self.driver.switch_to.frame(frame)

        field_email = self.driver.find_element(By.XPATH, '//*[@id="email"]')
        field_email.send_keys(email)

        field_name = self.driver.find_element(By.XPATH, '//*[@id="billing-name"]')
        field_name.send_keys(name)

        field_address = self.driver.find_element(By.XPATH, '//*[@id="billing-street"]')
        field_address.send_keys(address)

        field_city = self.driver.find_element(By.XPATH, '//*[@id="billing-city"]')
        field_city.send_keys(city)

        btn_payment_info = self.driver.find_element(By.XPATH, '//*[@id="submitButton"]/span/span')
        btn_payment_info.click()

        field_card_num = self.driver.find_element(By.XPATH, '//*[@id="card_number"]')
        for i in range(8): 
            field_card_num.send_keys(4)
            field_card_num.send_keys(2)

        field_card_exp = self.driver.find_element(By.XPATH, '//*[@id="cc-exp"]')
        field_card_exp.send_keys(4)
        field_card_exp.send_keys(2)
        field_card_exp.send_keys(4)


        field_card_cvc = self.driver.find_element(By.XPATH, '//*[@id="cc-csc"]')
        field_card_cvc.send_keys(card_cvc)

        btn_submit_payment = self.driver.find_element(By.XPATH, '//*[@id="submitButton"]/span/span')
        self.driver.execute_script('arguments[0].click();', btn_submit_payment)
        sleep(7)

        # Assert
        # Title
        expected_title = 'Thanks - Tenner | Tenner'
        self.assertEqual(self.driver.title, expected_title)

        # Text
        self.assertIn('Your order has been confirmed!', self.driver.page_source)
        self.assertIn('Your order number is', self.driver.page_source)
        self.assertIn('Thank you for choosing Tenner!', self.driver.page_source)
