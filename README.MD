# Simple Vietnam Stock Multi-agent System

## 1. Tạo Virtual Environment (venv)

Chạy lệnh sau để tạo môi trường ảo:
```bash
python -m venv .venv
```

**Kích hoạt môi trường ảo**:
- Linux/macOS:
  ```bash
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

## 2. Thiết lập API Keys

Thêm API keys vào file `activate` trong môi trường ảo:

1. Mở file kích hoạt:
   ```bash
   nano .venv/bin/activate
   ```

2. Thêm 2 dòng này vào **cuối file**:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key_here"
   ```

3. Lưu file và chạy:
   ```bash
   source .venv/bin/activate
   ```

⚠️ **Cảnh báo**: Không commit file activate lên Git/Github khi chứa API keys!

## 3. Lấy API Keys Miễn Phí

### 🔑 Google API Key
1. Truy cập [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API Key** 
3. Copy key và dán vào file activate

**Free Tier**: Free

## 4. Cài đặt Thư viện

Cài đặt các dependencies từ file requirements.txt:
```bash
pip install -r requirements.txt
```
## 5. Chạy demo

```bash
chmod +x run.sh
./run.sh
```
## 📝 Lưu Ý
- API keys sẽ tự động được load mỗi khi kích hoạt môi trường ảo
- Để hủy kích hoạt môi trường: `deactivate`
- Đối với Windows, dùng `set` thay cho `export` trong file activate
## Lời cảm ơn
Xin gửi lời cảm ơn chân thành đến nhà phát triển dự án [vnquant](https://github.com/phamdinhkhanh/vnquant). Dự án đã cung cấp một nguồn tài liệu và công cụ hữu ích, giúp tôi rất nhiều trong việc phân tích và xử lý dữ liệu tài chính. Sự đóng góp của các bạn là vô cùng quý báu và đáng trân trọng.


