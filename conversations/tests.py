from time import sleep
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import resolve, reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from accounts import tests as accounts_tests
from services.models import Category, Service
from .models import Conversation, ConversationMessage
from .views import detail, inbox, new_conversation
from .forms import ConversationMessageForm


class ConversationUnitTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.service_provider = User.objects.create_user(
            username='testprovider',
            email='provider@email.com',
            first_name='John',
            last_name='Smith',
            password='testuser1212',
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='user@email.com',
            first_name='Jane',
            last_name='Doe',
            password='testuser1212',
        )

        self.user_group = Group.objects.create(name='User')
        self.service_provider_group = Group.objects.create(name='Service Provider')
        self.service_provider_group.permissions.add(Permission.objects.get(name='Can add service'))
        self.service_provider_group.user_set.add(self.service_provider)
        self.user_group.user_set.add(self.user)

        self.conversation = Conversation.objects.create(
            service=Service.objects.create(
                name='Test Service',
                description='Test Description',
                category=Category.objects.create(
                    name='Test Category',
                    description='Test Description'
                ),
                provider=self.service_provider,
                price=100,
                job_limit=5
            )
        )
        self.conversation.members.add(self.service_provider, self.user)   
    
        self.conversation_message = ConversationMessage.objects.create(
            conversation=self.conversation,
            content='Test Message',
            created_by=self.user,
        )

        self.conversation_url = reverse('conversation:inbox')
        self.new_conversation_url = reverse('conversation:new_conversation', args=[self.conversation.service.id])
        self.conversation_detail_url = reverse('conversation:conversation_detail', args=[self.conversation.id])

    def tearDown(self):
        del self.service_provider
        del self.user
        del self.conversation
        del self.conversation_message
        del self.conversation_url
        del self.new_conversation_url
        del self.conversation_detail_url

    def test_conversationMessageFormValidation_returnTrue(self):
        # Arrange
        self.conversation.delete()
        self.conversation_message.delete()
        content = 'Hello world!'
        expected_status_code = 200

        # Act
        data = {'content': content}
        form = ConversationMessageForm(data=data)
        response = self.client.post(self.conversation_detail_url, data, follow=True)

        # Assert
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, expected_status_code)

    def test_createNewConversationAsServiceOwner_redirectHome(self):
        # Arrange
        provider_username = 'testprovider'
        provider_password = 'testuser1212'
        home_page_url = reverse('home')

        # Act
        self.client.login(username=provider_username, password=provider_password) 
        response = self.client.get(self.new_conversation_url, follow=True)

        # Assert
        self.assertRedirects(response, home_page_url)

    def test_createNewConversationNotServiceOwner_redirectConversationDetail(self):
        # Arrange
        user_username = 'testuser'
        user_password = 'testuser1212'

        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.get(self.new_conversation_url, follow=True)

        # Assert
        self.assertRedirects(response, self.conversation_detail_url)

    def test_conversationCreation_returnTrue(self):
        # Assert
        self.assertTrue(self.conversation)

    def test_conversationMessageCreation_returnTrue(self):
        # Assert
        self.assertTrue(self.conversation_message)

    def test_usersAuthenticated_returnTrue(self):
        # Arrange
        user_username = 'testuser'
        user_password = 'testuser1212'
        provider_username = 'testprovider'
        provider_password = 'testuser1212'

        # Act
        self.client.login(username=user_username, password=user_password)
        self.client.login(username=provider_username, password=provider_password)

        # Assert
        self.assertTrue(self.service_provider.is_authenticated)
        self.assertTrue(self.user.is_authenticated)

    def test_newConversationMessageFormValidation_redirectConversationDetail(self):
        # Arrange
        self.conversation.delete()
        self.conversation_message.delete()
        user_username = 'testuser'
        user_password = 'testuser1212'
        message = 'Test Message'
        conversation = Conversation.objects.create(
            service=Service.objects.create(
                name='New Test Service',
                description='Test Description',
                category=Category.objects.create(
                    name='New Test Category',
                    description='Test Description'
                ),
                provider=self.service_provider,
                price=100,
                job_limit=5
            )
        )
        conversation.members.add(self.service_provider, self.user)
        new_conversation_url = reverse('conversation:new_conversation', args=[conversation.service.id])
        conversation_detail_url = reverse('conversation:conversation_detail', args=[conversation.id])
        
        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.post(new_conversation_url, {'content': message}, follow=True)

        # Assert
        self.assertRedirects(response, conversation_detail_url)

    def test_conversationDetailFormValidation_redirectConversationDetail(self):
        # Arrange
        user_username = 'testuser'
        user_password = 'testuser1212'
        message = 'Test Message'

        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.post(self.conversation_detail_url, {'content': message}, follow=True)

        # Assert
        self.assertRedirects(response, self.conversation_detail_url)

    def test_conversationDeleteActionUserIsMemberOfConveration_returnTrue(self):
        # Arrange
        user_username = 'testuser'
        user_password = 'testuser1212'

        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.post(self.conversation_detail_url, {'delete_conversation': 'Delete Conversation'}, follow=True)

        # Assert
        self.assertTrue(response.context['conversation'].members.filter(id=self.user.id).exists())

    # Status Code
    def test_inboxPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.conversation_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_newConversationPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.new_conversation_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)

    def test_conversationDetailPageStatusCode_return200(self):
        # Arrange
        expected_status_code = 200

        # Act
        response = self.client.get(self.conversation_detail_url, follow=True)

        # Assert
        self.assertEqual(response.status_code, expected_status_code)
    
    # Template Used
    def test_inboxTemplateUsed_returnTrue(self):
        # Arrange
        user_username = 'testuser'
        user_password = 'testuser1212'
        expected_template = 'conversation/inbox.html'

        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.get(self.conversation_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_newConversationTemplateUsed_returnTrue(self):
        # Arrange
        self.conversation.delete()
        user_username = 'testuser'
        user_password = 'testuser1212'
        expected_template = 'conversation/new_conversation.html'

        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.get(self.new_conversation_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    def test_conversationDetailTemplateUsed_returnTrue(self):
        # Arrange
        user_username = 'testuser'
        user_password = 'testuser1212'
        expected_template = 'conversation/conversation_detail.html'

        # Act
        self.client.login(username=user_username, password=user_password)
        response = self.client.get(self.conversation_detail_url, follow=True)

        # Assert
        self.assertTemplateUsed(response, expected_template)

    # Resolve Views
    def test_inboxView_returnTrue(self):
        # Arrange
        expected_result = inbox.__name__

        # Act
        view = resolve(self.conversation_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_newConversationView_returnTrue(self):
        # Arrange
        expected_result = new_conversation.__name__

        # Act
        view = resolve(self.new_conversation_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)

    def test_conversationDetailView_returnTrue(self):
        # Arrange
        expected_result = detail.__name__

        # Act
        view = resolve(self.conversation_detail_url)

        # Assert
        self.assertEqual(view.func.__name__, expected_result)


class ConversationUATChrome(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')

        self.webpage_url = 'http://localhost:8000/'
        self.driver.get(self.webpage_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

        accounts_tests.AccountUATChrome.test_loginAccount_chromeDriver(self)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_contactServiceProvider_chromeDriver(self):
        # Arrange
        message = 'Test Message'
        service_url = 'http://localhost:8000/services/789dabac-77e6-49f0-a040-9399ed806b73/2f060620-5fac-40c7-abb5-29faf23cee4a/'
        new_conversation_url = 'http://localhost:8000/conversation/new/2f060620-5fac-40c7-abb5-29faf23cee4a/'

        # Act
        self.driver.get(service_url)
        
        btn_contact_provider = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/a[2]')
        btn_contact_provider.click()
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_content"]')))
        field_message = self.driver.find_element(By.XPATH, '//*[@id="id_content"]')
        field_message.send_keys(message)

        if self.driver.current_url == new_conversation_url:
            btn_send_message = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div/div/form/div[2]/button')
            self.driver.execute_script('arguments[0].click();', btn_send_message)
        else:
            btn_send_message = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/form/div[2]/button')
            self.driver.execute_script('arguments[0].click();', btn_send_message)

        # Assert
        # Title
        expected_title = 'Inbox - Message Detail | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn(message, self.driver.page_source)
        self.assertIn('Inbox', self.driver.page_source)
        self.assertIn('Message detail', self.driver.page_source)

    def test_deleteConversation_chromeDriver(self):
        # Arrange
        self.test_contactServiceProvider_chromeDriver()
        service_url = 'http://localhost:8000/services/789dabac-77e6-49f0-a040-9399ed806b73/2f060620-5fac-40c7-abb5-29faf23cee4a/'

        # Act
        self.driver.get(service_url)

        btn_contact_provider = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div/a[2]')
        btn_contact_provider.click()

        sleep(1)
        btn_delete_conversation = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/form/div[2]/a[2]')
        self.driver.execute_script('arguments[0].click();', btn_delete_conversation)

        # Assert
        # Title
        expected_title = 'Conversation Delete | Tenner'
        self.assertIn(expected_title, self.driver.title)

        # Text
        self.assertIn('Conversation Delete', self.driver.page_source)
        self.assertIn('Delete your conversation', self.driver.page_source)
        self.assertIn('You are about to delete a conversation permanently.', self.driver.page_source)

        btn_delete = self.driver.find_element(By.XPATH, '/html/body/section/div/div[2]/div/div/div/form/div[2]/button')
        btn_delete.click()
