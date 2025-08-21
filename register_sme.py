from register import run_register
from selenium import webdriver
import json
import datetime
from data_read import read_data, read_fields
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_register_smemoney(data_file, config_file, url , result_file):
    # Load config của SME Money (vị trí thứ 3 trong file config)
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)[2]  # SME Money là hệ thống thứ 3 (index = 2)

    # Đọc field mapping và test case đăng ký
    fields = read_fields("fields.txt")
    test_cases = read_data(data_file, "register")

    # Mở file kết quả để ghi log
    with open(result_file, "a", encoding="utf-8") as result:
        result.write(f"\n=== TEST ĐĂNG KÝ - SME MONEY - {datetime.datetime.now()} ===\n")

        # Duyệt từng test case
        for idx, test in enumerate(test_cases, 1):
            result.write(f"\n--- Test Case {idx} ---\n")

            driver = webdriver.Chrome()
            try:
                driver.get(url)

                # ✅ Click nút "Đăng ký" (trên trang chủ nếu cần)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Đăng ký')]"))
                ).click()
                if result:
                    result.write(f"[PASS] [{idx}] Click nút Đăng ký thành công\n")

            except Exception as e:
                if result:
                    result.write(f"[FAIL] [{idx}] Không click được nút Đăng ký - {str(e)}\n")
                driver.quit()
                return None
            try:
                WebDriverWait(driver, 10).until(EC.url_contains("sign-in"))
                driver.find_element(By.XPATH, "//b[text()='Đăng ký ngay']").click()
                #result_file.write(f"[PASS] [{idx}] Click nút đăng ký thành công\n")
                run_register(driver, test, fields, config["db"], idx, result)
                # current_url = driver.current_url

                # Đánh giá kết quả
                # if test["expected"] == "success" and "verify-otp?type=auth" in current_url:
                #     result.write("[✅ PASS] Đăng ký thành công\n")
                # elif test["expected"] == "fail" and "sign-up" in current_url:
                #     result.write("[✅ PASS] Đăng ký thất bại như mong đợi\n")
                # else:
                #     result.write("[❌ FAIL] Kết quả không đúng kỳ vọng\n")

            except Exception as e:
                result.write(f"[❌ ERROR] - {str(e)}\n")

            driver.quit()
