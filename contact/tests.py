from django.test import TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from .forms import ContactForm
from .views import contact_success, contact_us


class ContactUnitTest(TestCase):
    def setUp(self):
        self.contact_us_url = reverse('contact:contact_us')
        self.contact_success_url = reverse('contact:contact_success')

    def test_contact(self):
        del self.contact_us_url
        del self.contact_success_url

    def test_contactFormValidation_returnTrue(self):
        # Arrange
        name = 'Jane Doe'
        email = 'test@email.com'
        subject = 'Service Enquiry'
        content = 'I would like to know more about your service.'
        expected_status_code = 200

        # Act
        data = {
            'name': name,
            'email': email,
            'subject': subject,
            'content': content
        }
        form = ContactForm(data=data)
        response = self.client.post(self.contact_us_url, data, follow=True)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, expected_status_code)

    # Status Code
    def test_contactUsStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.contact_us_url, follow=True)


        self.assertEqual(response.status_code, expected_status_code)

    def test_contactSuccessStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.contact_success_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    # Template Used
    def test_contactUsTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'contact_us_form.html'

        # Act
        response = self.client.get(self.contact_us_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_contactSuccessTemplateUsed_returnTrue(self):
        # Arrange
        expected_template = 'contact_success.html'

        # Act
        response = self.client.get(self.contact_success_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)
    
    # Resolve Views
    def test_contactUsView_returnTrue(self):
        # Arrange
        expected_result = contact_us.__name__

        # Act
        view = resolve(self.contact_us_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_contactSuccessView_returnTrue(self):
        # Arrange
        expected_result = contact_success.__name__

        # Act
        view = resolve(self.contact_success_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)


class ContactUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_submitContactUs_chromeDriver(self):
        # Arrange
        name = 'Jane Doe'
        email = 'jane.doe@email.com'
        subject = 'Service Enquiry'
        message = 'I would like to know more about your service.'

        # Act
        link_contact_us = self.driver.find_element(By.XPATH, '//*[@id="navcol-1"]/ul[1]/li[5]/a')
        link_contact_us.click()

        field_name = self.driver.find_element(By.XPATH, '//*[@id="id_name"]')
        field_name.send_keys('Test Name')

        field_email = self.driver.find_element(By.XPATH, '//*[@id="id_email"]')
        field_email.send_keys(email)

        field_subject = self.driver.find_element(By.XPATH, '//*[@id="id_subject"]')
        field_subject.send_keys(subject)

        field_message = self.driver.find_element(By.XPATH, '//*[@id="id_content"]')
        field_message.send_keys(message)

        btn_submit = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/button')
        btn_submit.click()

        # Assert
        # Title
        expected_title = 'Contact Us - Success | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Contact Us', self.driver.page_source)
        self.assertIn('Message sent', self.driver.page_source)
        self.assertIn('Thank you for your message. We will get back to you as soon as possible.', self.driver.page_source)
