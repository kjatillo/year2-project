from time import sleep
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from services.models import Category, Service
from .models import Order, OrderItem
from .views import orderDetail, orderHistory, thanks


class OrderUnitTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='unittest',
            email='unittest@email.com',
            first_name='John',
            last_name='Smith',
            password='testuser1212',
        )
        
        self.service_provider_group = Group.objects.create(name='Service Provider')
        self.service_provider_group.permissions.add(Permission.objects.get(name='Can add service'))
        self.service_provider_group.user_set.add(self.user)
        self.client.login(username='unittest', password='testuser1212')

        self.category = Category.objects.create(name='Programming & Tech')
        self.service = Service.objects.create(
            name='I will build you a website',
            category=self.category,
            provider=self.user,
            image='../static/images/husky_pug.jpg',
            job_limit=3,
            price=500.00
        )

        self.order = Order.objects.create(
            token='1234567890',
            total=500.00,
            emailAddress='unittest@email.com',
            billingName='John Smith',
            billingAddress1='123 Main St',
            billingCity='Dublin',
            billingPostcode='12345',
            billingCountry='Ireland'
        )
            
        self.order_item = OrderItem.objects.create(
            service=self.service,
            quantity=1,
            price=500.00,
            order=self.order
        )

        self.order_history_url = reverse('order:order_history')
        self.order_detail_url = reverse('order:order_detail', args=[self.order.id])
        self.order_thank_you_url = reverse('order:thanks', args=[self.order.id])

    def tearDown(self):
        del self.order_history_url
        del self.order_detail_url
        del self.order_thank_you_url
        del self.order
        del self.order_item
        del self.service
        del self.category
        del self.user
        del self.service_provider_group

    def test_orderModelStrRepresentation_returnOrderID(self):
        # Arrange
        expected_str = str(self.order.id)

        # Assert
        self.assertEqual(self.order.__str__(), expected_str)

    def test_orderItemModelStrRepresentation_returnServiceName(self):
        # Arrange
        expected_str = self.service.name
        
        # Assert
        self.assertEqual(str(self.order_item.__str__()), expected_str)

    # Status Code
    def test_orderHistoryPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.order_history_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_orderDetailPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.order_detail_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_thankYouPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.order_thank_you_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    # Template Used
    def test_orderHistoryPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'order/orders_list.html'

        # Act
        response = self.client.get(self.order_history_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_orderDetailPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'order/order_detail.html'

        # Act
        response = self.client.get(self.order_detail_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_thankYouPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'thanks.html'

        # Act
        response = self.client.get(self.order_thank_you_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    # Resolve Views
    def test_orderHistoryPageResolveView_returnTrue(self):
        # Arrange
        expected_result = orderHistory.as_view().__name__

        # Act
        view = resolve(self.order_history_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)
    
    def test_orderDetailPageResolveView_returnTrue(self):
        # Arrange
        expected_result = orderDetail.as_view().__name__

        # Act
        view = resolve(self.order_detail_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_thankYouPageResolveView_returnTrue(self):
        # Arrange
        expected_result = thanks.__name__

        # Act
        view = resolve(self.order_thank_you_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)
