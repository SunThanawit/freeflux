# FLUX Image Generator

โปรแกรมสำหรับสร้างรูปภาพจาก text prompt โดยใช้ Together AI FLUX.1-schnell-Free API

## การติดตั้ง

### วิธีง่าย (แนะนำ)
```bash
./setup.sh
```

### วิธีแมนนวล
1. สร้าง virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

3. ตั้งค่า API key:
```bash
export TOGETHER_API_KEY='your_api_key_here'
```

## การใช้งาน

### CLI Version
รันโปรแกรม command line:
```bash
python image_generator.py
```

### Web App Version

**วิธีง่าย:**
```bash
export TOGETHER_API_KEY='your_api_key_here'
./run.sh
```

**วิธีแมนนวล:**
```bash
source venv/bin/activate
export TOGETHER_API_KEY='your_api_key_here'
python app.py
```

จากนั้นเปิดเบราว์เซอร์ไปที่: http://localhost:5000

### Production Deployment
สำหรับการ deploy จริง:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## ตัวอย่าง Prompts

- "A beautiful sunset over the mountains"
- "A cat wearing a hat sitting on a chair"
- "A futuristic city with flying cars"
- "A serene Japanese garden with cherry blossoms"

## Features

- 🌐 Web interface ที่ใช้งานง่าย
- 🎨 รองรับภาษาไทยและอังกฤษ
- 📱 Responsive design
- 🔄 Real-time image generation
- 💾 ดาวน์โหลดรูปได้
- 🎯 ตัวอย่าง prompts

## API Key

สมัครและรับ API key ฟรีได้ที่: https://api.together.ai/

FLUX.1-schnell-Free ให้ใช้ฟรี 3 เดือน!

## Rate Limits

- Free tier: 10 รูป/นาที
- คุณภาพสูง เวลาประมวลผลเร็ว