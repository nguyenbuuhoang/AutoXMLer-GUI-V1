import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import time
import threading
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import json
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

USERNAME = os.getenv("HIS_USERNAME")
PASSWORD = os.getenv("HIS_PASSWORD")
LOG_DIR = os.getenv("LOG_DIR")
SETTINGS_PATH = os.getenv("SETTINGS_PATH")


class AutoReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tool đẩy dữ liệu XML lên hệ thống")
        self.root.minsize(400, 300)  # Flexible size with minimum
        
        # Environment variables
        self.log_dir = LOG_DIR
        self.settings_path = SETTINGS_PATH
        
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        
        self.setup_logging()
        
        self.scheduled_time = None
        self.countdown_thread = None
        self.stop_countdown = threading.Event()
        
        self.create_widgets()
        self.load_schedule()

    def setup_logging(self):
        log_file = os.path.join(self.log_dir, f"log_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='{{%(asctime)s}} - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        self.log_handler = None

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        time_frame = ttk.LabelFrame(main_frame, text="Thời gian chạy script", padding="10")
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="Giờ:").grid(row=0, column=0, padx=5)
        self.hour_var = tk.StringVar(value="00")
        ttk.Spinbox(time_frame, from_=0, to=23, width=5, 
                   textvariable=self.hour_var, format="%02.0f").grid(row=0, column=1, padx=5)
        
        ttk.Label(time_frame, text="Phút:").grid(row=0, column=2, padx=5)
        self.minute_var = tk.StringVar(value="01")
        ttk.Spinbox(time_frame, from_=0, to=59, width=5, 
                   textvariable=self.minute_var, format="%02.0f").grid(row=0, column=3, padx=5)
        
        self.schedule_btn = ttk.Button(main_frame, text="Lên lịch chạy", command=self.schedule_job)
        self.schedule_btn.pack(pady=10)
        
        self.stop_btn = ttk.Button(main_frame, text="Dừng lịch", command=self.stop_job, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)
        
        self.status_var = tk.StringVar(value="Chưa lên lịch")
        ttk.Label(main_frame, textvariable=self.status_var).pack(pady=5)
        
        self.countdown_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=self.countdown_var, font=('Arial', 12, 'bold')).pack(pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="Báo cáo tải file", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH)
        
        self.log_handler = TextHandler(self.log_text)
        logging.getLogger().addHandler(self.log_handler)

    def load_schedule(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
                self.hour_var.set(f"{settings.get('hour', 0):02d}")
                self.minute_var.set(f"{settings.get('minute', 0):02d}")
                self.schedule_job()

    def save_schedule(self):
        settings = {
            'hour': int(self.hour_var.get()),
            'minute': int(self.minute_var.get())
        }
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f)

    def setup_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': 'C:\\GMedAgent\\Pending',
            'download.prompt_for_download': False,
            'download.extensions_to_open': 'xml',
            'safebrowsing.enabled': True
        })
        chrome_options.add_argument("start-maximized")
        return webdriver.Chrome(options=chrome_options)

    def schedule_job(self):
        if self.countdown_thread and self.countdown_thread.is_alive():
            messagebox.showinfo("Thông báo", "Đang có lịch chạy, vui lòng dừng trước khi lên lịch mới!")
            return
        
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            
            now = datetime.now()
            self.scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if self.scheduled_time < now:
                self.scheduled_time += timedelta(days=1)
                
            self.stop_countdown.clear()
            self.schedule_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Đã lên lịch chạy vào: {self.scheduled_time.strftime('%d/%m/%Y %H:%M:%S')}")
            
            self.countdown_thread = threading.Thread(target=self.run_countdown, daemon=True)
            self.countdown_thread.start()
            
            logging.info(f"Đã lên lịch chạy vào {self.scheduled_time.strftime('%d/%m/%Y %H:%M:%S')}")
            self.save_schedule()
            
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giờ/phút hợp lệ!")
            logging.error("Nhập giờ/phút không hợp lệ")

    def stop_job(self):
        self.stop_countdown.set()
        self.schedule_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Đã dừng lịch chạy")
        self.countdown_var.set("")
        logging.info("Đã dừng lịch chạy")

    def run_countdown(self):
        while not self.stop_countdown.is_set():
            now = datetime.now()
            if now >= self.scheduled_time:
                self.execute_script()
                self.scheduled_time += timedelta(days=1)
                self.status_var.set(f"Đã lên lịch chạy vào: {self.scheduled_time.strftime('%d/%m/%Y %H:%M:%S')}")
                logging.info(f"Tự động lên lịch cho {self.scheduled_time.strftime('%d/%m/%Y %H:%M:%S')}")
                
            time_diff = self.scheduled_time - now
            if time_diff.total_seconds() > 0:
                hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.countdown_var.set(f"Sẽ chạy sau: {hours:02d}:{minutes:02d}:{seconds:02d}")
            time.sleep(1)

    def login(self, driver):
        driver.get("https://angiang.vncare.vn/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "login-username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
        driver.find_element(By.ID, "btn-login").click()

    def navigate_to_export(self, driver):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Viện phí và bảo hiểm')]"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Bảo hiểm 4210')]"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Xuất file bảo hiểm 4210')]"))).click()

    def fill_export_form(self, driver, start_date, end_date):
        wait = WebDriverWait(driver, 10)
        Select(wait.until(EC.presence_of_element_located((By.ID, "cboLoaiXML")))).select_by_visible_text("Chuẩn 130")
        date_format = "%d/%m/%Y %H:%M:%S"
        driver.find_element(By.ID, "txtTU_NGAY").clear()
        driver.find_element(By.ID, "txtTU_NGAY").send_keys(start_date.strftime(date_format))
        driver.find_element(By.ID, "txtDEN_NGAY").clear()
        driver.find_element(By.ID, "txtDEN_NGAY").send_keys(end_date.strftime(date_format))
        driver.find_element(By.ID, "btnSearch").click()

    def execute_script(self):
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59)
        file_prefix = f"-{start_date.strftime('%Y%m%d%H%M%S')}-{end_date.strftime('%Y%m%d%H%M%S')}"
        expected_path = os.path.join(self.download_dir, f"{file_prefix}.xml")
        
        if os.path.exists(expected_path):
            file_size = os.path.getsize(expected_path) / 1024
            logging.info(f"File {file_prefix}.xml đã tồn tại, dung lượng {file_size:.2f} KB")
            return
        
        driver = self.setup_chrome_driver()
        try:
            self.login(driver)
            self.navigate_to_export(driver)
            self.fill_export_form(driver, start_date, end_date)
            
            wait = WebDriverWait(driver, 10)
            Select(wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ui-pg-selbox")))).select_by_visible_text("300")
            wait.until(EC.element_to_be_clickable((By.ID, "chkEXP_REPORT_XML_BHYT"))).click()
            
            # Wait for file download (timeout 30s)
            for _ in range(30):
                if os.path.exists(expected_path):
                    file_size = os.path.getsize(expected_path) / 1024
                    logging.info(f"File {file_prefix}.xml đã được tải, dung lượng {file_size:.2f} KB")
                    return
                time.sleep(1)
            logging.warning(f"Không tìm thấy file {file_prefix}.xml sau 30 giây, file có thể chưa được tải.")
            
        except Exception as e:
            logging.error(f"Lỗi khi tải file: {type(e).__name__} - {str(e)}")
        finally:
            driver.quit()


class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoReportApp(root)
    root.mainloop()