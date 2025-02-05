#!/bin/bash

# Hàm để xử lý tín hiệu và dừng toàn bộ process con
cleanup() {
    echo "Shutting down..."
    pkill -P $$  # Tắt toàn bộ các process con của script
    exit 0
}

# Đăng ký hàm xử lý tín hiệu cho Ctrl+C
trap cleanup SIGINT

# Khởi động FastAPI
uvicorn api:app --reload --port 8000 &

# Đợi 2 giây để FastAPI khởi động xong
sleep 2

# Khởi động Streamlit trên port khác và chế độ headless
streamlit run fe.py --server.port 8501

# Giữ script chạy, chờ tín hiệu Ctrl+C
wait
