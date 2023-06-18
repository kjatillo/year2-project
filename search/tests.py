from datetime import datetime
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from accounts.models import CustomUser
from services.models import Category, Service
from .views import SearchResultsListView, filterView


class SearchUnitTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='testuser1')
        self.user2 = CustomUser.objects.create_user(username='testuser2')
        self.client.login(username='testuser1', password='testuser1')
        self.client.login(username='testuser2', password='testuser2')

        self.service1 = Service.objects.create(
            name='Test Service1',
                description='Test Description1',
                category=Category.objects.create(
                    name='Test Category1',
                    description='Test Description1'
                ),
                provider=self.user1,
                price=100,
                job_limit=5,
                created=timezone.now(),
        )
        self.service2 = Service.objects.create(
            name='Test Service2',
                description='Test Description2',
                category=Category.objects.create(
                    name='Test Category2',
                    description='Test Description2'
                ),
                provider=self.user2,
                price=200,
                job_limit=5
        )

        self.search_url = reverse('search:search_result')
        self.advanced_search_url = reverse('search:advanced_search_result')
        self.url_pattern = '/search/?q='

    def tearDown(self):
        del self.user1
        del self.user2
        del self.service1
        del self.service2
        del self.search_url
        del self.url_pattern
        del self.advanced_search_url

    def test_filterServiceContainsQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        service_contains_query = 'service1'

        # Act
        qs = qs.filter(name__icontains=service_contains_query)

        # Assert
        self.assertIn(self.service1, qs)
        self.assertNotIn(self.service2, qs)

    def test_filterProviderContainsQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        provider_contains_query = 'testuser2'

        # Act
        qs = qs.filter(provider__username__icontains=provider_contains_query)

        # Assert
        self.assertNotIn(self.service1, qs)
        self.assertIn(self.service2, qs)

    def test_filterServiceOrProviderContainsQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        query = 'test'

        # Act
        qs = qs.filter(name__icontains=query) | qs.filter(provider__username__icontains=query)

        # Assert
        self.assertIn(self.service1, qs)
        self.assertIn(self.service2, qs)

    def test_filterCategoryQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        category_contains_query = 'category1'

        # Act
        qs = qs.filter(category__name__icontains=category_contains_query)

        # Assert
        self.assertIn(self.service1, qs)
        self.assertNotIn(self.service2, qs)

    def test_filterPriceGreaterOrEqualThanQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        price_greater_than_query = 150

        # Act
        qs = qs.filter(price__gte=price_greater_than_query)

        # Assert
        self.assertNotIn(self.service1, qs)
        self.assertIn(self.service2, qs)

    def test_filterPriceLessThanOrEqualThanQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        price_less_than_query = 150

        # Act
        qs = qs.filter(price__lte=price_less_than_query)

        # Assert
        self.assertIn(self.service1, qs)
        self.assertNotIn(self.service2, qs)

    def test_filterDatePostedGreaterOrEqualThanQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        date_posted_greater_than_query = datetime(2023, 2, 12)

        # Act
        qs = qs.filter(created__gte=date_posted_greater_than_query)

        # Assert
        self.assertIn(self.service1, qs)
        self.assertIn(self.service2, qs)

    def test_filterDatePostedLessThanOrEqualThanQuery_returnTrue(self):
        # Arrange
        qs = Service.objects.all()
        date_posted_less_than_query = datetime(2023, 2, 12)

        # Act
        qs = qs.filter(created__lte=date_posted_less_than_query)

        # Assert
        self.assertNotIn(self.service1, qs)
        self.assertNotIn(self.service2, qs)

    # Status Code
    def test_searchPageStatusCode_return200(self):
        # Arrange
        query = 'test'
        expected_status_code = 200

        # Act
        response = self.client.get(self.url_pattern + query)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)
        self.assertContains(response, query)
    
    def test_advancedSearchPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.advanced_search_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    # Template Used
    def test_searchResultPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'search_result.html'

        # Act
        response = self.client.get(self.url_pattern)

        # Assert
        self.assertTemplateUsed(response, expected_template)
    
    def test_advancedSearchPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'advanced_search_result.html'

        # Act
        response = self.client.get(self.advanced_search_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def advancedSearchFormTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'advanced_search_form.html'

        # Act
        response = self.client.get(self.advanced_search_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    # Resolve Views
    def test_searchResultsListView_returnTrue(self):
        # Arrange
        expected_result = SearchResultsListView.as_view().__name__

        # Act
        view = resolve(self.search_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_filterView_returnTrue(self):
        # Arrange
        expected_result = filterView.__name__

        # Act
        view = resolve(self.advanced_search_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)


class SearchUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_basicSearch_chromeDriver(self):
        # Arrange
        query = 'writer'

        # Act
        search_bar = self.driver.find_element(By.XPATH, '//*[@id="search-bar"]/form/div/input')
        search_bar.send_keys(query)

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="search-bar"]/form/div/button')
        btn_search.click()

        # Assert
        # Title
        expected_title = 'Basic Search | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn(query, self.driver.page_source)
        self.assertIn('You have searched for', self.driver.page_source)
        self.assertIn('Results found', self.driver.page_source)

    def test_advancedSearch_chromeDriver(self):
        # Arrange
        q_composer = 'composer'
        q_provider = 'provider'
        q_animator = 'animator'

        # Act
        btn_basic_search = self.driver.find_element(By.XPATH, '//*[@id="search-bar"]/form/div/button')
        btn_basic_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_service_title = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/div[1]/div/div/input')
        field_service_title.send_keys(q_composer)

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_service_provider = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/div[2]/div/div/input')
        field_service_provider.send_keys(q_provider)

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_service_title_or_provider = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/div[3]/div/div/input')
        field_service_title_or_provider.send_keys(q_animator)

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        dropdown_category = self.driver.find_element(By.XPATH, '//*[@id="category"]')
        dropdown_category.click()

        option_music_audio = self.driver.find_element(By.XPATH, '//*[@id="category"]/option[3]')
        option_music_audio.click()

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_price_min = self.driver.find_element(By.XPATH, '//*[@id="priceMin"]')
        field_price_min.send_keys(300)

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_price_max = self.driver.find_element(By.XPATH, '//*[@id="priceMax"]')
        field_price_max.send_keys(300)

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()
        
        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_date_min = self.driver.find_element(By.XPATH, '//*[@id="dateAddedMin"]')
        field_date_min.clear()
        field_date_min.send_keys('12/02/2023')

        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()

        btn_advanced_search = self.driver.find_element(By.XPATH, '//*[@id="advance-search"]/a')
        btn_advanced_search.click()

        field_date_max = self.driver.find_element(By.XPATH, '//*[@id="dateAddedMax"]')
        field_date_max.clear()
        field_date_max.send_keys('12/02/2023')
        
        btn_search = self.driver.find_element(By.XPATH, '//*[@id="advanceSearch"]/div/main/form/button')
        btn_search.click()
        
        # Assert
        # Title
        expected_title = 'Advanced Search | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('You have used advanced filter search', self.driver.page_source)
        self.assertIn('Category', self.driver.page_source)
        self.assertIn('Price Max', self.driver.page_source)
