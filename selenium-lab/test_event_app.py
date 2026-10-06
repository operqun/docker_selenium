# Experiment 12: Selenium test cases for the containerized Event Registration App
# Run against Docker:      docker run -d -p 3000:3000 event-app:1.0   (BASE_URL defaults to localhost:3000)
# Run against Kubernetes:  BASE_URL=$(minikube service event-app-service --url) pytest -v
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
UNIQUE = str(int(time.time()))          # unique emails for every test run


@pytest.fixture(scope="module")
def driver():
    drv = webdriver.Chrome()
    drv.set_window_size(1280, 1050)
    yield drv
    drv.quit()


@pytest.fixture
def page(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "regForm")))
    return driver


def fill_form(d, name="", email="", phone="", college="", event=None):
    d.find_element(By.ID, "name").send_keys(name)
    d.find_element(By.ID, "email").send_keys(email)
    d.find_element(By.ID, "phone").send_keys(phone)
    d.find_element(By.ID, "college").send_keys(college)
    if event:
        Select(d.find_element(By.ID, "event")).select_by_visible_text(event)
    d.find_element(By.ID, "registerBtn").click()


def text_of(d, element_id):
    WebDriverWait(d, 10).until(lambda drv: drv.find_element(By.ID, element_id).text != "")
    return d.find_element(By.ID, element_id).text


def test_tc01_page_loads(page):
    assert page.title == "TechFest 2026 - Registration"
    assert page.find_element(By.TAG_NAME, "h1").text == "TechFest 2026"


def test_tc02_form_fields_present(page):
    for field in ["name", "email", "phone", "college", "event", "registerBtn"]:
        assert page.find_element(By.ID, field).is_displayed()


def test_tc03_health_endpoint(driver):
    driver.get(BASE_URL + "/health")
    assert '"status":"UP"' in driver.find_element(By.TAG_NAME, "body").text


def test_tc04_empty_form_rejected(page):
    page.find_element(By.ID, "registerBtn").click()
    assert text_of(page, "error") == "Name and College are required."


def test_tc05_invalid_email(page):
    fill_form(page, "Ravi Kumar", "ravi.gmail.com", "9876543210", "ABC Engineering College", "Hackathon")
    assert text_of(page, "error") == "Please enter a valid email address."


def test_tc06_invalid_phone(page):
    fill_form(page, "Ravi Kumar", "ravi@gmail.com", "12345", "ABC Engineering College", "Hackathon")
    assert text_of(page, "error") == "Mobile number must be 10 digits starting with 6-9."


def test_tc07_event_not_selected(page):
    fill_form(page, "Ravi Kumar", "ravi@gmail.com", "9876543210", "ABC Engineering College")
    assert text_of(page, "error") == "Please select an event."


def test_tc08_valid_registration(page):
    before = int(page.find_element(By.ID, "count").text)
    fill_form(page, "Ravi Kumar", f"ravi{UNIQUE}@gmail.com", "9876543210",
              "ABC Engineering College", "Hackathon")
    assert text_of(page, "success") == "Thank you Ravi Kumar! You are registered for Hackathon."
    WebDriverWait(page, 10).until(
        lambda d: int(d.find_element(By.ID, "count").text) == before + 1)
    last_row = page.find_elements(By.CSS_SELECTOR, "#regTable tbody tr")[-1]
    assert "Ravi Kumar" in last_row.text and "Hackathon" in last_row.text


def test_tc09_duplicate_email_rejected(page):
    fill_form(page, "Ravi Kumar", f"ravi{UNIQUE}@gmail.com", "9876543210",
              "ABC Engineering College", "Hackathon")
    assert text_of(page, "error") == "This email is already registered."


def test_tc10_clear_button(page):
    page.find_element(By.ID, "name").send_keys("Test User")
    page.find_element(By.CSS_SELECTOR, "button.reset").click()
    assert page.find_element(By.ID, "name").get_attribute("value") == ""