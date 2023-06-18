from time import sleep
from django.test import TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from .views import HomePageView, TeamView


class PagesUnitTest(TestCase):
    def setUp(self):
        self.home_url = reverse('home')
        self.team_url = reverse('team')

    def tearDown(self):
        del self.home_url
        del self.team_url

    # Status Code
    def test_homePageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.home_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_teamPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.team_url)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)
    
    # Template Used
    def test_baseTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'base.html'

        # Act
        response = self.client.get(self.home_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_footerTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'footer.html'

        # Act
        response = self.client.get(self.home_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_homePageTemplateUsed_returnTrue(self):
        # Arrage
        expected_template = 'index.html'

        # Act
        response = self.client.get(self.home_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_navigationBarTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'navbar.html'

        # Act
        response = self.client.get(self.home_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_teamPageTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'team.html'

        # Act
        response = self.client.get(self.team_url)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    # Resolve Views
    def test_homePageView_returnTrue(self):
        # Arrange
        expected_result = HomePageView.as_view().__name__
        
        # Act
        view = resolve(self.home_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_teamPageView_returnTrue(self):
        # Arrange
        expected_result = TeamView.as_view().__name__

        # Act
        view = resolve(self.team_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)


class PagesUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_navigationBarLinks_chromeDriver(self):
        # Arrage
        username = 'newuser'
        password = 'KVTLB@d^6LEf'

        # Act
        btn_basic_search = self.driver.find_element(By.XPATH, '//*[@id="search-bar"]/form/div/button')
        btn_basic_search.click()

        link_home = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[1]/a')
        link_home.click()

        num_services_links = len(self.driver.find_elements(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/ul/li'))
        for i in range(num_services_links):
            dropdown_services = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[3]/a')
            dropdown_services.click()
            link = self.driver.find_element(By.XPATH, f'//*[@id="navcol-1"]/ul[1]/li[3]/ul/li[{i + 1}]/a')
            link.click()

        link_team = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[4]/a')
        link_team.click()

        link_contact_us = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[5]/a')
        link_contact_us.click()
        
        link_cart = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li/a')
        link_cart.click()

        link_signup = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[2]')
        link_signup.click()

        link_login = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/a[1]')
        link_login.click()

        field_username = self.driver.find_element(By.XPATH, '//*[@id="id_username"]')
        field_username.send_keys(username)

        field_password = self.driver.find_element(By.XPATH, '//*[@id="id_password"]')
        field_password.send_keys(password)

        btn_login = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_login.click()

        num_user_links = len(self.driver.find_elements(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/ul/li'))
        for i in range(num_user_links):
            dropdown_user = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[2]/li[3]/a')
            dropdown_user.click()
            link = self.driver.find_element(By.XPATH, f'//*[@id="navcol-1"]/ul[2]/li[3]/ul/li[{i + 1}]/a')
            link.click()

        # Assert
        # Title
        expected_title = 'Home | Tenner'
        self.assertEqual(self.driver.title, expected_title)

        # Text
        self.assertIn('Tenner', self.driver.page_source)
        self.assertIn('Services', self.driver.page_source)
        self.assertIn('Cart', self.driver.page_source)

    def test_footerLinks_chromeDriver(self):
        # Arrange

        # Act
        num_services_links = len(self.driver.find_elements(By.XPATH, '/html/body/footer/div/div[1]/div[1]/ul/li'))
        for i in range(num_services_links):
            link = self.driver.find_element(By.XPATH, f'/html/body/footer/div/div[1]/div[1]/ul/li[{i + 1}]/a')
            self.driver.execute_script('arguments[0].click();', link)

        link_team = self.driver.find_element(By.XPATH, '/html/body/footer/div/div[1]/div[2]/ul/li[2]/a')
        link_team.click()

        link_contact_us = self.driver.find_element(By.XPATH, '/html/body/footer/div/div[1]/div[3]/ul/li/a')
        self.driver.execute_script('arguments[0].click();', link_contact_us)

        link_logo_home = self.driver.find_element(By.XPATH, '//*[@id="mainNav"]/div/a')
        link_logo_home.click()

        num_socials_links = len(self.driver.find_elements(By.XPATH, '/html/body/footer/div/div[2]/ul/li'))
        main_tab = self.driver.window_handles[0]
        for i in range(num_socials_links):
            link = self.driver.find_element(By.XPATH, f'/html/body/footer/div/div[2]/ul/li[{i + 1}]/a')
            sleep(.3)
            self.driver.execute_script('arguments[0].click();', link)

            new_tab = self.driver.window_handles[1]
            sleep(.3)
            self.driver.switch_to.window(window_name=new_tab)
            sleep(.3)
            self.driver.close()
            self.driver.switch_to.window(window_name=main_tab)

        # Assert
        # Title
        expected_title = 'Home | Tenner'
        self.assertEqual(self.driver.title, expected_title)

        # Text
        self.assertIn('About', self.driver.page_source)
        self.assertIn('Copyright © 2023 Tenner', self.driver.page_source)
        self.assertIn('Year 2 project for Computing with Software Development course from Technological University Dublin - Tallaght.', 
                      self.driver.page_source)
