from selenium import webdriver
from register import run_register
# from register_test_data import test_cases


def main():
    result_file = open("register_results.txt", "w", encoding="utf-8")

    for i, test in enumerate(test_cases):
        result_file.write(f"\n=== Test Case {i + 1} ===\n")
        driver = webdriver.Chrome()
        driver.get("https://uat.smemoney.vn/vi/user/sign-up")  # 🔁 Thay link nếu cần
        url_result = run_register(driver, test, result_file)
        if url_result:
            result_file.write(f"[INFO] URL sau khi đăng ký: {url_result}\n")
        driver.quit()

    result_file.close()


if __name__ == "__main__":
    main()
