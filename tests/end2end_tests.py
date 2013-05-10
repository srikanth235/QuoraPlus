import unittest
import random
import string
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC        

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def getRandomString(self, length=10):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

    def testPostQuestion(self):
        driver = self.driver        
        driver.get("http://quoraplus498.appspot.com/static/Login.html")
        driver.find_element_by_id("email").send_keys("srikanth235@gmail.com")
        driver.find_element_by_id("password").send_keys("123")
        driver.find_element_by_id("login").send_keys("\n")
        time.sleep(1) # let the page load

        driver.find_element_by_id("content").send_keys("\n")
        time.sleep(1) # let the page load
        
        rand_text =  self.getRandomString()
        driver.find_element_by_id("description").send_keys(rand_text)
        driver.find_element_by_class_name("createButton").send_keys("\n")
        time.sleep(1) # let the page load
        
        question_text = driver.find_element_by_css_selector(".description a")
        assert question_text, rand_text
        
    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()