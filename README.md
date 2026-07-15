# Streamlit Google Sheet Viewer

Project scaffold để bạn xem nhanh app web lấy dữ liệu từ Google Sheets.

## Phân tích link gốc
- Google Sheet ID: `15Hpk_d8G2UFtiOzNcd-CqtidzIZPoRwLXt5dXU1jjas`
- GID mặc định: `0`
- Link hiện tại yêu cầu đăng nhập Google / chưa public nên không thể tải trực tiếp bằng CSV export.

## Cách dùng
1. Chuyển đến thư mục dự án:
   ```bash
   cd ~/streamlit-google-sheet-viewer
   ```
2. Tạo môi trường ảo và cài dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Chạy app:
   ```bash
   streamlit run app.py
   ```

## Cấu hình dữ liệu
### Nếu sheet public
- Đảm bảo chia sẻ `Anyone with the link can view`.
- Mở app, để nguyên giá trị `Google Sheet ID` và bỏ chọn `Dùng Google Sheets API`.

### Nếu sheet private
- Tạo Google Service Account và tải file JSON credentials.
- Đặt file đó vào `credentials.json` trong thư mục dự án,
  hoặc dùng biến môi trường `GOOGLE_APPLICATION_CREDENTIALS` hoặc `GOOGLE_SERVICE_ACCOUNT_JSON`.
- Bật `Dùng Google Sheets API` trong sidebar.

## Tính năng scaffold
- Hiển thị bảng dữ liệu từ Google Sheet
- Lọc theo `Shop` và `Brand` nếu có cột tương ứng
- Tìm kiếm nhanh toàn cột
- Chọn cột hiển thị trong bảng
- Thống kê nhanh số dòng, số shop và số brand
- Biểu đồ cột nhanh cho Shop hoặc Brand
- Hỗ trợ public CSV export và private Google Sheets API

## Ghi chú
- App đã được hoàn thiện để xem nhanh và dùng dễ dàng.
- Nếu bạn muốn mở rộng thêm, mình có thể thêm bộ lọc trạng thái, ngày, và chi tiết task riêng cho mỗi shop.

## Deploy lên Streamlit Cloud
1. Tạo repo GitHub từ thư mục này:
   ```bash
   cd ~/streamlit-google-sheet-viewer
   git init
   git add .
   git commit -m "Initial deploy-ready commit"
   git branch -M main
   git remote add origin <YOUR_GITHUB_REPO_URL>
   git push -u origin main
   ```
2. Vào Streamlit Cloud, chọn `New app` và chọn repo + branch `main`.
3. Đặt `Main file` là `app.py`.
4. Nếu Google Sheet private, thêm `GOOGLE_SERVICE_ACCOUNT_JSON` trong Streamlit Cloud Secrets.
