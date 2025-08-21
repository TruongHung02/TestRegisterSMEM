import pymysql
from pymysql.cursors import DictCursor

def read_data(file_path, data_type):
    data = []  # Tạo danh sách để lưu các test case

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("#") or line.strip() == "":
            continue  # Bỏ qua dòng comment và dòng trống

        parts = line.strip().split('|')

        # Login: 5 cột -> mã TC, mô tả, email, password, expected
        if data_type == "login" and len(parts) == 5:
            testcase_id, scenario, email, password, expected = parts
            data.append({
                "testcase_id": testcase_id,
                "scenario": scenario,
                "email": "" if email == "none" else email,
                "password": "" if password == "none" else password,
                "expected": expected
            })

        # Register: 11 cột -> mã TC, mô tả, loại TK, MST, công ty, họ tên, sdt, email, pass, confirm_pass, expected
        elif data_type == "register" and len(parts) == 11:
            testcase_id, scenario, account_type, tax_code, company_name, fullname, phone, email, password, confirm_password, expected = parts
            data.append({
                "testcase_id": testcase_id,
                "scenario": scenario,
                "account_type": account_type,
                "tax_code": "" if tax_code == "none" else tax_code,
                "company_name": "" if company_name == "none" else company_name,
                "fullname": fullname,
                "phone": phone,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
                "expected": expected
            })

    return data



def read_fields(file_path='fields.txt'):
    fields = {}
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                if line.startswith('#'):
                    current_section = line[1:].strip().lower()
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Lưu dạng login.email_input_name, register.account_type_button_xpath
                section_key = f"{current_section}.{key}" if current_section else key
                fields[section_key] = value

    return fields

import pymysql

def check_duplicate_in_db(test_data, db_config):
    try:
        connection = pymysql.connect(
            host=db_config["host"],
            port=int(db_config["port"]),
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Check email
            cursor.execute("SELECT * FROM users WHERE email = %s", (test_data["email"],))
            if cursor.fetchone():
                return "Email đã tồn tại"

            # Check phone
            # cursor.execute("SELECT * FROM users WHERE phone = %s", (test_data["phone"],))
            # if cursor.fetchone():
            #     return "Số điện thoại đã tồn tại"

        connection.close()
        return None

    except Exception as e:
        return f"Lỗi kết nối DB: {e}"

