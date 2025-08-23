from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
import time
import traceback
from data_read import check_duplicate_in_db
from get_otp_yopmail import get_yopmail_otp


def run_register(driver, test_data, fields, db_config, idx, result_file=None):

    try:
        duplicate_msg = check_duplicate_in_db(test_data, db_config)

        if duplicate_msg is not None:
            if result_file:
                result_file.write(
                    f"[❌ FAIL] [{idx}] {duplicate_msg}\n"
                )
            return
        wait = WebDriverWait(driver, 15)

        # ✅ 1) Chọn loại tài khoản
        if result_file:
            result_file.write("[STEP] Chọn loại tài khoản\n")

        account_type = (
            (test_data.get("account_type") or "").strip().replace("\u200b", "")
        )
        if not account_type:
            raise ValueError("Thiếu trường account_type trong test_data")
        if result_file:
            result_file.write(f"[DEBUG] account_type: '{account_type}'\n")

        # Mở dropdown
        select_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, fields["register.account_type_button_xpath"])
            )
        )
        if select_btn.get_attribute("aria-expanded") != "true":
            select_btn.click()
            wait.until(lambda d: select_btn.get_attribute("aria-expanded") == "true")

        # Chờ listbox xuất hiện
        options_container_xpath = "//div[@role='listbox']"
        wait.until(EC.presence_of_element_located((By.XPATH, options_container_xpath)))
        if result_file:
            result_file.write("[PASS] Container tùy chọn đã xuất hiện\n")

        # Chọn option (click cha role='option' thay vì span)
        account_type_key = f"register.account_type_option_{account_type}"
        if account_type_key not in fields:
            raise ValueError(f"Không tìm thấy XPath cho loại tài khoản: {account_type}")

        raw_xpath = fields[account_type_key]
        clickable_xpath = f"({raw_xpath})/ancestor-or-self::*[@role='option'][1]"
        option_elem = wait.until(
            EC.presence_of_element_located((By.XPATH, clickable_xpath))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", option_elem
        )

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, clickable_xpath)))
            option_elem.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", option_elem)

        # Đợi dropdown đóng lại để đảm bảo form đã render theo loại tài khoản
        try:
            wait.until(lambda d: select_btn.get_attribute("aria-expanded") != "true")
        except Exception:
            pass

        if result_file:
            result_file.write("[PASS] Chọn loại tài khoản thành công\n")

        # ✅ 2) Nhập mã số thuế (nếu có & field tồn tại)
        if test_data.get("tax_code"):
            if result_file:
                result_file.write("[STEP] Nhập mã số thuế (nếu có trường)\n")

            tax_xpath = fields["register.tax_code_input_xpath"]
            try:
                tax_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, tax_xpath))
                )
                # scroll + cố gắng visible (nếu có)
                try:
                    tax_input = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, tax_xpath))
                    )
                except TimeoutException:
                    # Nếu không visible vẫn có thể send_keys được tùy UI, thử scroll và nhập
                    pass

                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", tax_input
                )
                tax_input.clear()
                tax_input.send_keys(test_data["tax_code"])

                # Chờ autofill tên công ty (nếu có)
                try:
                    wait.until(
                        lambda d: (
                            d.find_element(
                                By.XPATH, fields["register.company_name_input_xpath"]
                            ).get_attribute("value")
                            or ""
                        ).strip()
                        != ""
                    )
                    if result_file:
                        result_file.write(
                            "[PASS] Nhập MST & đợi autofill tên công ty\n"
                        )
                except Exception:
                    # Không bắt buộc phải autofill
                    if result_file:
                        result_file.write(
                            "[INFO] Không thấy autofill tên công ty (bỏ qua)\n"
                        )

            except TimeoutException:
                if result_file:
                    result_file.write(
                        "[WARN] Không tìm thấy ô Mã số thuế cho loại tài khoản hiện tại. Bỏ qua MST.\n"
                    )

        # ✅ 3) Nhập tên công ty (nếu có dữ liệu và chưa có autofill)
        if test_data.get("company_name"):
            try:
                company_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, fields["register.company_name_input_xpath"])
                    )
                )
                if not (company_input.get_attribute("value") or "").strip():
                    company_input.send_keys(test_data["company_name"])
                if result_file:
                    result_file.write("[PASS] Nhập tên công ty\n")
            except TimeoutException:
                if result_file:
                    result_file.write("[WARN] Không tìm thấy ô Tên công ty, bỏ qua.\n")

        # ✅ 4) Nhập họ tên
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, fields["register.name_input_xpath"])
            )
        ).send_keys(test_data["fullname"])
        if result_file:
            result_file.write("[PASS] Nhập họ tên\n")

        # ✅ 5) Nhập SĐT
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, fields["register.phone_input_xpath"])
            )
        ).send_keys(test_data["phone"])
        if result_file:
            result_file.write("[PASS] Nhập số điện thoại\n")

        # ✅ 6) Nhập email
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, fields["register.email_input_xpath"])
            )
        ).send_keys(test_data["email"])
        if result_file:
            result_file.write("[PASS] Nhập email\n")

        # ✅ 7) Nhập mật khẩu
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, fields["register.password_input_xpath"])
            )
        ).send_keys(test_data["password"])
        if result_file:
            result_file.write("[PASS] Nhập mật khẩu\n")

        # ✅ 8) Nhập xác nhận mật khẩu (nếu có key)
        if "confirm_password" in test_data and test_data["confirm_password"]:
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, fields["register.confirm_password_input_xpath"])
                )
            ).send_keys(test_data["confirm_password"])
            if result_file:
                result_file.write("[PASS] Nhập xác nhận mật khẩu\n")
        else:
            if result_file:
                result_file.write(
                    "[FAIL] Không có dữ liệu xác nhận mật khẩu. Bỏ qua.\n"
                )

        # # ✅ 9) Tick đồng ý chính sách
        # if result_file:
        #     result_file.write("[STEP] Tick đồng ý chính sách\n")
        # checkbox = wait.until(EC.element_to_be_clickable(
        #     (By.ID, fields['register.privacy_checkbox_id'])
        # ))
        # if not checkbox.is_selected():
        #     checkbox.click()
        # if result_file:
        #     result_file.write("[PASS] Đã tick đồng ý chính sách\n")

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, fields["register.register_button_xpath"])
            )
        ).click()
        result_file.write(f"[PASS] [{idx}] Click nút Đăng ký\n")

        current_url = driver.current_url

        # Chờ điều hướng hoặc thông báo lỗi
        try:
            wait.until(
                lambda d: d.current_url != current_url
                or len(
                    d.find_elements(By.XPATH, fields["register.error_message_xpath"])
                )
                > 0
            )
        except TimeoutException:
            result_file.write(
                f"[WARN] [{idx}] Hết thời gian chờ, không điều hướng và không thấy thông báo lỗi\n"
            )

        # Check DB sau submit
        time.sleep(10)  # Chờ backend commit

        if driver.current_url != current_url:
            # Có điều hướng → có thể là thành công
            if duplicate_msg is None:
                result_file.write(f"[✅ PASS] [{idx}] Đăng ký thành công - DB lưu OK\n")
            else:
                result_file.write(
                    f"[❌ FAIL] [{idx}] Điều hướng nhưng DB báo: {duplicate_msg}\n"
                )
        else:
            # Không điều hướng → kiểm tra thông báo lỗi
            try:
                error_elem = driver.find_element(
                    By.XPATH, fields["register.error_message_xpath"]
                )
                error_text = error_elem.text.strip()
                result_file.write(
                    f"[FAIL] [{idx}] Đăng ký thất bại, thông báo: {error_text}\n"
                )
            except:
                result_file.write(
                    f"[FAIL] [{idx}] Không điều hướng và không tìm thấy thông báo lỗi\n"
                )

            if duplicate_msg:
                result_file.write(
                    f"[INFO] [{idx}] DB kiểm tra sau submit: {duplicate_msg}\n"
                )

        # Nếu đăng ký lưu DB thành công, lấy mã OTP
        if (driver.current_url != current_url) and (duplicate_msg is None):
            OTP = get_yopmail_otp(email_address=test_data["email"], email_subject="Send Otp User")
            if OTP is not None:
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, fields["register.otp_input_xpath"])
                    )
                ).send_keys(OTP)

                # Ấn tiếp tục
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, fields["register.otp_confirm_button_xpath"])
                    )
                ).click()
                time.sleep(5)
            if result_file:
                if OTP is not None:
                    result_file.write("[PASS] Nhập OTP thành công\n")
                else:
                    result_file.write("[FAIL] Lấy mã OTP thất bại\n")

    except Exception as e:
        if result_file:
            result_file.write(f"[❌ ERROR] [{idx}] Lỗi khi đăng ký: {str(e)}\n")
            result_file.write(traceback.format_exc())
        return None


# ✅ BƯỚC 0: Check trùng dữ liệu trong DB (bật nếu cần)
#     duplicate_msg = check_duplicate_in_db(test_data, db_config)
#     if duplicate_msg:
#         if result_file:
#             result_file.write(f"[FAIL] [{idx}] Email hoặc SĐT đã tồn tại: {duplicate_msg}\n")
#         return None
