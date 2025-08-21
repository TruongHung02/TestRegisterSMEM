
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_login(driver, url, fields, result_file, idx, test):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Đăng nhập')]"))
        ).click()
        result_file.write(f"[PASS] [{idx}] Click nút Đăng nhập thành công\n")
    except Exception as e:
        result_file.write(f"[FAIL] [{idx}] Không click được nút Đăng nhập - {str(e)}\n")
        driver.quit()
        return None

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("sign-in"))

        # Điền Email
        email_field_name = fields.get('login.email_input_name')
        if email_field_name:
            email_input = driver.find_element(By.NAME, email_field_name)
            email_input.clear()
            email_input.send_keys(test["email"])
            result_file.write(f"[PASS] [{idx}] Nhập email thành công\n")
        else:
            result_file.write(f"[WARNING] [{idx}] Không tìm thấy trường 'login.email_input_name' trong fields\n")

        # Điền Password
        pw_field_name = fields.get('login.password_input_name')
        if pw_field_name:
            pw_input = driver.find_element(By.NAME, pw_field_name)
            pw_input.clear()
            pw_input.send_keys(test["password"])
            result_file.write(f"[PASS] [{idx}] Nhập password thành công\n")
        else:
            result_file.write(f"[WARNING] [{idx}] Không tìm thấy trường 'login.password_input_name' trong fields\n")

        # Click nút Đăng nhập
        if login_button_xpath:
            driver.find_element(By.XPATH, login_button_xpath).click()
            result_file.write(f"[PASS] [{idx}] Click nút đăng nhập thành công\n")

        time.sleep(5)
        return driver.current_url

    except Exception as e:
        result_file.write(f"[ERROR] [{idx}] Lỗi khi thao tác đăng nhập - {str(e)}\n")
        return None
