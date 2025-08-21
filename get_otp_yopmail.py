import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_yopmail_otp(email_address: str) -> str | None:
    """
    Sử dụng Selenium để truy cập Yopmail và lấy mã OTP từ email mới nhất.
    Phiên bản đã được cập nhật để chủ động click vào email mới nhất.

    Args:
        email_address: Địa chỉ email Yopmail (không bao gồm @yopmail.com).

    Returns:
        Một chuỗi chứa mã OTP (6 chữ số) nếu tìm thấy, ngược lại trả về None.
    """
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--log-level=3")
    # options.add_argument("--headless")  # bật chế độ headless
    options.add_argument("--disable-gpu")  # khuyến nghị cho Windows
    options.add_argument("--window-size=1920,1080")  # đặt kích thước cửa sổ
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    print(f"🚀 Bắt đầu quá trình lấy OTP cho email: {email_address}")

    try:
        # 1. Truy cập trang chủ Yopmail
        driver.get("https://yopmail.com")

        # 2. Nhập email và truy cập hộp thư
        login_input = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_input.send_keys(email_address)
        check_button = driver.find_element(By.XPATH, '//*[@id="refreshbut"]/button')
        check_button.click()
        # print("✅ Đã nhập email và truy cập hộp thư.")

        # 3. Kiểm tra xem hộp thư có trống không
        try:
            # Chờ cho đến khi iframe danh sách mail (#ifinbox) hoặc thông báo trống xuất hiện
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "ifinbox")),
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//*[div[@id='nodiv' and contains(text(), 'This inbox is empty')]]",
                        )
                    ),
                )
            )
            if driver.find_elements(
                By.XPATH,
                "//*[div[@id='nodiv' and contains(text(), 'This inbox is empty')]]",
            ):
                print("❌ Hộp thư đến trống.")
                return None
        except TimeoutException:
            print("❌ Không thể tải hộp thư đến hoặc hộp thư trống.")
            return None

        # 4. # MỚI: Chuyển sang iframe chứa DANH SÁCH email (bên trái)
        driver.switch_to.frame("ifinbox")
        # print("✅ Đã chuyển sang khung chứa danh sách email.")

        # 5. # MỚI: Chờ và click vào email đầu tiên trong danh sách (email mới nhất)
        latest_email = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.m"))
        )
        latest_email.click()
        # print("✅ Đã click vào email mới nhất.")

        # 6. # MỚI: Chuyển về context mặc định trước khi chuyển sang iframe khác
        driver.switch_to.default_content()

        # 7. Chuyển sang iframe chứa NỘI DUNG email (bên phải)
        driver.switch_to.frame("ifmail")
        # print("✅ Đã chuyển sang khung chứa nội dung email.")

        # 8. Lấy nội dung và trích xuất OTP
        email_body_element = wait.until(EC.presence_of_element_located((By.ID, "mail")))
        email_body_text = email_body_element.text

        otp_match = re.search(r"\b\d{6}\b", email_body_text)

        if otp_match:
            otp = otp_match.group(0)
            print(f"🎉 Đã tìm thấy mã OTP: {otp}")
            return otp
        else:
            print("❌ Không tìm thấy mã OTP (6 chữ số) trong email.")
            return None

    except TimeoutException:
        print(f"⏳ Đã hết thời gian chờ. Vui lòng kiểm tra lại.")
        return None
    except Exception as e:
        print(f"🐞 Đã xảy ra lỗi không mong muốn: {e}")
        return None
    finally:
        driver.quit()
        # print("🔒 Đã đóng trình duyệt.")


# --- VÍ DỤ SỬ DỤNG ---
if __name__ == "__main__":
    test_email_user = "testotpsmemoney02"

    # Gửi một email chứa mã OTP (ví dụ: 987654) đến địa chỉ trên trước khi chạy
    otp_code = get_yopmail_otp(test_email_user)

    if otp_code:
        print(f"\nKết quả cuối cùng: Mã OTP là: {otp_code}")
    else:
        print("\nKết quả cuối cùng: Không thể lấy OTP.")
