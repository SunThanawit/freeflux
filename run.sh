#!/bin/bash

# ตรวจสอบว่ามี API key หรือไม่
if [ -z "$TOGETHER_API_KEY" ]; then
    echo "❌ ไม่พบ TOGETHER_API_KEY"
    echo "กรุณาตั้งค่า API key ก่อน:"
    echo "export TOGETHER_API_KEY='your_api_key_here'"
    exit 1
fi

echo "=== FLUX Image Generator ==="
echo "🚀 กำลังเริ่มต้น web server..."

# เปิดใช้งาน virtual environment
source venv/bin/activate

# รัน Flask app
python app.py