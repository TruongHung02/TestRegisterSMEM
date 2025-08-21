from register import run_register
from selenium import webdriver
import json
import datetime
from data_read import read_data, read_fields
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_register_santaichinh(data_file, config_file, url, result_file):

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)[3]  # Sàn tài chính là hệ thống thứ 4
    fields = read_fields("fields.txt")
    test_cases = read_data(data_file, "register")

    with open(result_file, "a", encoding="utf-8") as result:
        result.write(f"\n=== TEST ĐĂNG KÝ - SAN TAI CHINH - {datetime.datetime.now()} ===\n")

        for idx, test in enumerate(test_cases, 1):
            result.write(f"\n--- Test Case {idx} ---\n")
            driver = webdriver.Chrome()
            try:
                driver.get(url)

                # ✅ Click nút "Đăng ký" (trên trang chủ nếu cần)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Đăng ký']"))
                ).click()
                if result:
                    result.write(f"[PASS] [{idx}] Click nút Đăng ký thành công\n")

            except Exception as e:
                if result:
                    result.write(f"[FAIL] [{idx}] Không click được nút Đăng ký - {str(e)}\n")
                driver.quit()
                return None

            try:
                WebDriverWait(driver, 10).until(EC.url_contains("sign-up"))
                run_register(driver, test, fields, config["db"], idx, result)
                current_url = driver.current_url

                # Đánh giá kết quả
                if test["expected"] == "success" and "verify-otp?type=auth" in current_url:
                    result.write("[✅ PASS] Đăng ký thành công\n")
                elif test["expected"] == "fail" and "sign-up" in current_url:
                    result.write("[✅ PASS] Đăng ký thất bại như mong đợi\n")
                else:
                    result.write("[❌ FAIL] Kết quả không đúng kỳ vọng\n")
            except Exception as e:
                result.write(f"[❌ ERROR] - {str(e)}\n")
            driver.quit()