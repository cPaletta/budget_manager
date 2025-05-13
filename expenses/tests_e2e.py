from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from .models import Expense
from datetime import datetime
from decimal import Decimal
import time 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException


class ExpenseE2ETest(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') 

        cls.selenium = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        cls.selenium.implicitly_wait(10) 


    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
        

    def setUp(self):
        self.user = User.objects.create_user(username='e2euser', password='e2epassword')
        self.selenium.get(f'{self.live_server_url}{reverse("account_login")}')
        
        username_input = self.selenium.find_element(By.NAME, "username") 
        username_input.send_keys('e2euser')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('e2epassword')

        self.selenium.find_element(By.XPATH, '//button[@type="submit"]').click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[text()='Your expenses']"))
        )
        self.assertTrue(reverse('expense_list') in self.selenium.current_url)



    def test_add_and_view_expense(self):
        self.selenium.get(f'{self.live_server_url}{reverse("add_expense")}')

        date_input = self.selenium.find_element(By.NAME, "date")
        date_input.send_keys(datetime.now().strftime('%d-%m-%Y')) 
        
        category_input = self.selenium.find_element(By.NAME, "category")
        category_input.send_keys('E2E Test Category')
        
        title_input = self.selenium.find_element(By.NAME, "title")
        title_input.send_keys('E2E Test Expense Title')
        
        amount_input = self.selenium.find_element(By.NAME, "amount")
        amount_input.send_keys('123.45')
        time.sleep(2)
        
        submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()
        time.sleep(2)

        try:
            WebDriverWait(self.selenium, 15).until( 
                EC.presence_of_element_located((By.XPATH, "//h2[text()='Your expenses']"))
            )
        except TimeoutException: 
            raise TimeoutException("No element: '//h2[text()='Your expenses']' found after 15 seconds.")

        self.assertTrue(reverse('expense_list') in self.selenium.current_url)
        
        expense_category_text = "E2E Test Category"
        expense_amount_text = "123.45" 

        try:
            WebDriverWait(self.selenium, 10).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), expense_category_text)
            )
            WebDriverWait(self.selenium, 10).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), expense_amount_text)
            )
        except TimeoutException:
            raise TimeoutException(f"Text '{expense_category_text}' or '{expense_amount_text}' not found in the body after 10 seconds.")
        
        self.assertTrue(Expense.objects.filter(title='E2E Test Expense Title', amount=Decimal('123.45')).exists())



    def test_delete_expense(self):
        expense_to_delete = Expense.objects.create(
            user=self.user,
            date=datetime.now(),
            category='To Delete',
            title='Expense For Deletion',
            currency='PLN',
            amount=Decimal('99.99')
        )
        
        self.selenium.get(f'{self.live_server_url}{reverse("expense_list")}')
        
        try:
            WebDriverWait(self.selenium, 15).until(
                EC.presence_of_element_located((By.XPATH, "//h2[text()='Your expenses']"))
            )
        except TimeoutException: 
            raise TimeoutException("No element: '//h2[text()='Your expenses']' found after 15 seconds.")

        delete_link_xpath = f"//a[contains(@href, '{reverse('delete_expense', args=[expense_to_delete.id])}')]"
        
        try:
            WebDriverWait(self.selenium, 15).until(
                EC.element_to_be_clickable((By.XPATH, delete_link_xpath)) 
            )
        except TimeoutException:
            raise TimeoutException(f"Delete link not clickable after 15 seconds: {delete_link_xpath}")
        
        delete_link = self.selenium.find_element(By.XPATH, delete_link_xpath)
        delete_link.click()
        
        submit_button_xpath = '//button[@type="submit"]' 
        try:
            WebDriverWait(self.selenium, 15).until(
                EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
            )
        except TimeoutException: 
            raise TimeoutException("Submit button not clickable after 15 seconds.")
        
        self.selenium.find_element(By.XPATH, submit_button_xpath).click()
        
        try:
            WebDriverWait(self.selenium, 15).until( 
                EC.presence_of_element_located((By.XPATH, "//h2[text()='Your expenses']"))
            )
        except TimeoutException: 
            raise TimeoutException("No element: '//h2[text()='Your expenses']' found after 15 seconds.")
        
        self.assertTrue(reverse('expense_list') in self.selenium.current_url)
        

        list_items = self.selenium.find_elements(By.TAG_NAME, "li")
        deleted_expense_found_on_page = False
        for item in list_items:
            if "Expense For Deletion" in item.text and "99.99" in item.text:
                deleted_expense_found_on_page = True
                break
        self.assertFalse(deleted_expense_found_on_page, "Deleted expense still found on the page.")
        
        self.assertFalse(Expense.objects.filter(id=expense_to_delete.id).exists())

