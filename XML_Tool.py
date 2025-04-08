import os
import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Load biến từ file .env
load_dotenv()

USERNAME = os.getenv("HIS_USERNAME")
PASSWORD = os.getenv("HIS_PASSWORD")
LOG_DIR = os.getenv("LOG_DIR")

# Logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

# Ngày tháng xử lý
today = datetime.today()
start_date = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0)
end_date = (today - timedelta(days=1)).replace(hour=23, minute=59, second=59)
date_format = "%d/%m/%Y %H:%M:%S"
start_date_str = start_date.strftime(date_format)
end_date_str = end_date.strftime(date_format)

# Cấu hình Chrome
prefs = {
    'download.default_directory': 'C:\\GMedAgent\\Pending',
    'download.prompt_for_download': False,
    'download.extensions_to_open': 'xml',
    'safebrowsing.enabled': True
}

chrome_options = Options()
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--safebrowsing-disable-download-protection")
chrome_options.add_argument("safebrowsing-disable-extension-blacklist")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://angiang.vncare.vn/")
    time.sleep(3)

    driver.find_element(By.ID, "login-username").send_keys(USERNAME)
    driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
    driver.find_element(By.ID, "btn-login").click()
    time.sleep(5)

    driver.find_element(By.XPATH, "//a[contains(text(), 'Viện phí và bảo hiểm')]").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//a[contains(text(), 'Bảo hiểm 4210')]").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//a[contains(text(), 'Xuất file bảo hiểm 4210')]").click()
    time.sleep(3)

    Select(driver.find_element(By.ID, "cboLoaiXML")).select_by_visible_text("Chuẩn 130")

    driver.find_element(By.ID, "txtTU_NGAY").clear()
    driver.find_element(By.ID, "txtTU_NGAY").send_keys(start_date_str)

    driver.find_element(By.ID, "txtDEN_NGAY").clear()
    driver.find_element(By.ID, "txtDEN_NGAY").send_keys(end_date_str)

    driver.find_element(By.ID, "btnSearch").click()
    time.sleep(3)

    Select(driver.find_element(By.CLASS_NAME, "ui-pg-selbox")).select_by_visible_text("300")
    time.sleep(3)

    driver.find_element(By.ID, "chkEXP_REPORT_XML_BHYT").click()
    time.sleep(10)

    # Kiểm tra file
    file_prefix = f"-{start_date.strftime('%Y%m%d%H%M%S')}-{end_date.strftime('%Y%m%d%H%M%S')}"
    expected_filename = f"{file_prefix}.xml"
    file_path = os.path.join('C:\\GMedAgent\\Pending', expected_filename)

    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / 1024
        logging.info(f"File {expected_filename} đã được khởi tạo với dung lượng {file_size:.2f} KB")
    else:
        logging.error(f"File {expected_filename} không được tải về.")

finally:
    driver.quit()
