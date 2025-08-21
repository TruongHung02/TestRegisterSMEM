from test_login import run_login
from selenium import webdriver
import json
import datetime
from data_read import read_data, read_fields


def run_login_santaichinh(data_file, config_file, result_file):
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)[1]  # 👉 Cấu hình cho hệ thống Sàn Tài Chính

    test_cases = read_data(data_file, "login")
    fields = read_fields("fields.txt")

    with open(result_file, "a", encoding="utf-8") as result:
        result.write(f"\n=== TEST SÀN TÀI CHÍNH - {datetime.datetime.now()} ===\n")

        for idx, test in enumerate(test_cases, 1):
            email = test["email"]
            password = test["password"]
            result.write(f"\n--- Test Case {idx} ---\n")
            result.write(f"Email: {email} | Password: {password} | Expect: {test['expected']}\n")

            driver = webdriver.Chrome()
            try:
                run_login(driver, config["url_home"], fields, result, idx, test)
                current_url = driver.current_url

                if test["expected"] == "success" and "vi/home" in current_url:
                    result.write("[✅ PASS] Đăng nhập thành công\n")
                elif test["expected"] == "fail" and "sign-in" in current_url:
                    result.write("[✅ PASS] Đăng nhập thất bại \n")
                else:
                    result.write("[❌ FAIL] Kết quả không đúng mong đợi\n")

            except Exception as e:
                result.write(f"[❌ ERROR] Không xác minh được kết quả - {str(e)}\n")
            finally:
                driver.quit()