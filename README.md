
# 🛠️ Tool Đẩy Dữ Liệu XML Lên Hệ Thống BHYT

Đây là công cụ **tự động hóa** được phát triển bằng **Python**, kết hợp GUI với `tkinter` và tự động hóa trình duyệt bằng `Selenium`. Mục tiêu của tool là lên lịch và tải file XML chuẩn 130 từ hệ thống BHYT [https://angiang.vncare.vn/](https://angiang.vncare.vn/), sau đó lưu file về thư mục định sẵn.

---

## 🚀 Tính Năng Chính

- 🕒 **Lên lịch tự động:** Đặt giờ/phút để tool chạy tự động hằng ngày.
- 🧭 **Tự động hóa trình duyệt:** Đăng nhập, điều hướng và tải file XML bằng `Selenium`.
- 🪟 **Giao diện đồ họa:** Dễ sử dụng với `tkinter`, thao tác đơn giản.
- 📜 **Quản lý log:** Ghi log đầy đủ các thao tác và lỗi nếu có.
- ✅ **Kiểm tra file tải:** Không tải lại nếu file đã tồn tại.

---

## 🖥️ Yêu Cầu Hệ Thống

- **Hệ điều hành:** Windows (đường dẫn mặc định `C:\GMedAgent\Pending`)
- **Python:** 3.6+
- **Trình duyệt:** Google Chrome

---

## ⚙️ Cài Đặt

### 1. Cài Python

Tải Python từ [https://www.python.org/](https://www.python.org/)  
👉 **tick "Add Python to PATH"** khi cài đặt.

---

### 2. Cài các thư viện cần thiết

Mở Terminal và chạy lệnh:

```bash
pip install selenium python-dotenv
```

(Lưu ý: `tkinter` đã đi kèm với Python trên Windows)

---

### 3. Tạo file `.env`

Trong thư mục dự án, tạo file `.env` và điền:

```env
HIS_USERNAME=<tên_người_dùng>
HIS_PASSWORD=<mật_khẩu>
LOG_DIR=C:\GMedAgent\Logs
SETTINGS_PATH=C:\GMedAgent\Settings\settings.json
```

> 🔐 Thay thế `<...>` bằng thông tin thực tế của bạn.

---

### 4. Tạo thư mục lưu file

Đảm bảo thư mục `C:\GMedAgent\Pending` tồn tại để chứa file XML tải về.  
👉 Nếu chưa có, tạo thủ công hoặc sửa đường dẫn trong source code.

---

## 🧑‍💻 Cách Sử Dụng

Chạy chương trình bằng terminal:

```bash
python GUI.py
```

---

### 🔧 Giao Diện Bao Gồm:

- **Thời gian chạy:** Chọn giờ và phút.
- **Nút lên lịch:** Bắt đầu tự động.
- **Nút dừng:** Hủy lịch đã đặt.
- **Trạng thái:** Hiển thị đang chạy hay chờ.
- **Đếm ngược:** Thời gian còn lại.
- **Bảng log:** Hiển thị log thao tác trực tiếp.

---

### ⚙️ Tự Động Chạy Gồm:

1. Đăng nhập vào [angiang.vncare.vn](https://angiang.vncare.vn/)
2. Truy cập "Xuất file bảo hiểm 4210"
3. Chọn ngày hôm trước (00:00:00 → 23:59:59)
4. Tải file XML và lưu tại `C:\GMedAgent\Pending`  
   📁 Tên file có chứa ngày giờ để dễ quản lý.

---

## 📁 Log & Xử Lý Lỗi

- Tên file log: `log_YYYYMMDD.log`
- Vị trí lưu: trong thư mục bạn đã chỉ định ở biến `LOG_DIR`
- Ghi nhận tất cả hoạt động và lỗi (nếu có)

---

## ⚠️ Lưu Ý

- Phải kết nối internet ổn định khi chạy.
- Nếu file XML đã tồn tại, sẽ **không tải lại**.
- Thời gian chờ tải file tối đa: **30 giây** → nếu quá sẽ log cảnh báo.

---