#!/bin/bash

echo "=== FLUX Image Generator Setup ==="
echo "กำลังติดตั้ง virtual environment และ dependencies..."

# สร้าง virtual environment
python3 -m venv venv

# เปิดใช้งาน virtual environment
source venv/bin/activate

# อัปเกรด pip
pip install --upgrade pip

# ติดตั้ง dependencies
pip install -r requirements.txt

echo ""
echo "✅ ติดตั้งเสร็จแล้ว!"
echo ""
echo "วิธีเริ่มใช้งาน:"
echo "1. source venv/bin/activate"
echo "2. export TOGETHER_API_KEY='your_api_key_here'"
echo "3. python app.py"
echo ""
echo "หรือใช้คำสั่งด่วน:"
echo "./run.sh"