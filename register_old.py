from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
from data_read import check_duplicate_in_db


def run_register(driver, test_data, fields, db_config, idx, result_file=None):
    #✅ BƯỚC 0: Check trùng dữ liệu trong DB (bật nếu cần)
    # duplicate_msg = check_duplicate_in_db(test_data, db_config)
    # if duplicate_msg:
    #     if result_file:
    #         result_file.write(f"[FAIL] [{idx}] Email hoặc SĐT đã tồn tại: {duplicate_msg}\n")
    #     return None

    # try:
    #     driver.get(url)
    #
    #     # ✅ Click nút "Đăng ký" (trên trang chủ nếu cần)
    #     WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Đăng ký']"))
    #     ).click()
    #     if result_file:
    #         result_file.write(f"[PASS] [{idx}] Click nút Đăng ký thành công\n")
    #
    # except Exception as e:
    #     if result_file:
    #         result_file.write(f"[FAIL] [{idx}] Không click được nút Đăng ký - {str(e)}\n")
    #     driver.quit()
    #     return None
    #driver.get(url)
    try:
        wait = WebDriverWait(driver, 15)

        # ✅ 1. Chọn loại tài khoản
        if result_file:
            result_file.write("[STEP] Chọn loại tài khoản\n")

        account_type = test_data.get('account_type')
        if not account_type:
            raise ValueError("Thiếu trường account_type trong test_data")
        # ⚠️ Chuẩn hóa chuỗi account_type để loại bỏ khoảng trắng và ký tự ẩn
        account_type = account_type.strip().replace('\u200b', '')  # Loại bỏ ký tự zero-width space nếu có

        # DEBUG: Ghi lại giá trị account_type để kiểm tra lỗi ký tự/khoảng trắng
        print(f"[DEBUG] Giá trị account_type được đọc: '{account_type}'")
        if result_file:
            result_file.write(f"[DEBUG] Giá trị account_type được đọc: '{account_type}'\n")

        # Click dropdown chọn loại tài khoản
        select_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']")))
        select_btn.click()
        time.sleep(1)
        # print(111)
        # try:
        #     select_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']")))
        #     select_btn.click()
        #     if result_file:
        #         result_file.write("[PASS] Click dropdown 'Chọn loại tài khoản' thành công\n")
        # except:
        #     if result_file:
        #         result_file.write("[WARN] Không thể click dropdown bằng XPath role, thử lại với text\n")
        #     select_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Doanh nghiệp']")))
        #     select_btn.click()
        #     if result_file:
        #         result_file.write("[PASS] Click dropdown 'Chọn loại tài khoản' thành công bằng XPath text\n")
        #
        # time.sleep(1)  # Thêm một chút delay để chắc chắn dropdown hiện ra
        # 2b. Chờ cho container chứa các options xuất hiện
        # ID này có thể thay đổi, nên chúng ta sẽ chờ một cách tổng quát hơn
        options_container_xpath = "//div[@role='listbox']"
        wait.until(EC.presence_of_element_located((By.XPATH, options_container_xpath)))
        if result_file:
            result_file.write("[PASS] Container chứa các tùy chọn đã xuất hiện\n")

        # Click vào lựa chọn phù hợp
        account_type_key = f"account_type_option_{account_type}"
        if account_type_key not in fields:
            raise ValueError(f"Không tìm thấy XPath cho loại tài khoản: {account_type}")

        option_elem = wait.until(EC.element_to_be_clickable((By.XPATH, fields[account_type_key])))
        option_elem.click()
        if result_file:
            result_file.write("[PASS] Chọn loại tài khoản thành công\n")

        # ✅ 2. Nhập mã số thuế nếu có
        if test_data.get('tax_code'):
            if result_file:
                result_file.write("[STEP] Nhập mã số thuế\n")

            tax_input = wait.until(EC.presence_of_element_located((By.XPATH, fields['register.tax_code_input_xpath'])))
            tax_input.send_keys(test_data['tax_code'])

            # Đợi tên công ty autofill
            wait.until(lambda d: d.find_element(By.XPATH, fields['register.company_name_input_xpath']).get_attribute(
                "value") != "")
            if result_file:
                result_file.write("[PASS] Nhập mã số thuế và đợi autofill tên công ty\n")

        # ✅ 3. Nhập tên công ty nếu chưa được autofill
        if test_data.get('company_name'):
            company_input = wait.until(
                EC.presence_of_element_located((By.XPATH, fields['register.company_name_input_xpath'])))
            if not company_input.get_attribute("value"):
                company_input.send_keys(test_data['company_name'])
            if result_file:
                result_file.write("[PASS] Nhập tên công ty\n")

        # ✅ 4. Nhập họ tên
        name_input = wait.until(EC.presence_of_element_located((By.XPATH, fields['register.name_input_xpath'])))
        name_input.send_keys(test_data['fullname'])
        if result_file:
            result_file.write("[PASS] Nhập họ tên\n")

        # ✅ 5. Nhập số điện thoại
        phone_input = wait.until(EC.presence_of_element_located((By.XPATH, fields['register.phone_input_xpath'])))
        phone_input.send_keys(test_data['phone'])
        if result_file:
            result_file.write("[PASS] Nhập số điện thoại\n")

        # ✅ 6. Nhập email
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, fields['register.email_input_xpath'])))
        email_input.send_keys(test_data['email'])
        if result_file:
            result_file.write("[PASS] Nhập email\n")

        # ✅ 7. Nhập mật khẩu
        pass_input = wait.until(EC.presence_of_element_located((By.XPATH, fields['register.password_input_xpath'])))
        pass_input.send_keys(test_data['password'])
        if result_file:
            result_file.write("[PASS] Nhập mật khẩu\n")

        # ✅ 8. Nhập lại mật khẩu
        confirm_input = wait.until(
            EC.presence_of_element_located((By.XPATH, fields['register.confirm_password_input_xpath'])))
        confirm_input.send_keys(test_data['password_confirmation'])
        if result_file:
            result_file.write("[PASS] Nhập lại mật khẩu\n")

        # ✅ 9. Tick đồng ý chính sách
        if result_file:
            result_file.write("[STEP] Tick đồng ý chính sách\n")
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, fields['register.privacy_checkbox_id'])))
        if not checkbox.is_selected():
            checkbox.click()
        if result_file:
            result_file.write("[PASS] Đã tick đồng ý chính sách\n")

        # ✅ 10. Click nút Đăng ký
        register_btn = wait.until(EC.element_to_be_clickable((By.XPATH, fields['register.register_button_xpath'])))
        register_btn.click()
        if result_file:
            result_file.write("[PASS] Click nút Đăng ký\n")

        # ✅ 11. Đợi điều hướng trang
        wait.until(EC.url_changes(driver.current_url))
        return driver.current_url

    except Exception as e:
        if result_file:
            result_file.write(f"[❌ ERROR] [{idx}] Lỗi khi đăng ký: {str(e)}\n")
            result_file.write(traceback.format_exc())
        return None
