from test_login import run_login
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import datetime
from data_read import read_data, read_fields

def run_login_smemoney(data_file, config_file, result_file):
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)[0]  # SME Money là hệ thống đầu tiên trong config
    fields = read_fields("fields.txt")
    test_cases = read_data(data_file, "login")


    with open(result_file, "a", encoding="utf-8") as result:
        result.write(f"\n=== TEST SME MONEY - {datetime.datetime.now()} ===\n")

        for idx, test in enumerate(test_cases, 1):
            email = test["email"]
            password = test["password"]
            expected = test["expected"]
            result.write(f"\n--- Test Case {idx} ---\n")
            result.write(f"Email: {email} | Password: {password} | Expect: {test['expected']}\n")

            driver = webdriver.Chrome()
            try:
                run_login(driver, config["url_home"], fields, result, idx, test)
                current_url = driver.current_url

                if test["expected"] == "success" and "change-workspace" in current_url:
                    result.write("[✅ PASS] Đăng nhập thành công\n")
                elif test["expected"] == "fail" and "sign-in" in current_url:
                    result.write("[✅ PASS] Đăng nhập thất bại \n")
                else:
                    result.write("[❌ FAIL] Kết quả đăng nhập không khớp mong đợi\n")

            except Exception as e:
                result.write(f"[❌ ERROR] Không xác minh được kết quả - {str(e)}\n")

            driver.quit()
