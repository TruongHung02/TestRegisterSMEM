from login_smemoney import run_login_smemoney
from login_santaichinh import run_login_santaichinh
from register_sme import run_register_smemoney
from register_santaichinh import run_register_santaichinh
data_file = "data_test.txt"
config = ("config.json")
#result = "result.txt"
result ="result.txt"
url = "https://uat.smemoney.vn/vi"

# Xoá log cũ nếu muốn
with open(result, "w", encoding="utf-8") as f:
     f.write("KẾT QUẢ AUTO TEST:\n")

#
#run_login_smemoney(data_file, config, result)
#run_login_santaichinh(data_file, config, result)
run_register_smemoney(data_file, config, url, result)

print("✅ Đã chạy xong toàn bộ test cho cả 2 hệ thống!")