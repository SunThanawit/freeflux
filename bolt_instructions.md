# FLUX Image Generator - Bolt.new Instructions

คำสั่งสำหรับสร้าง FLUX Image Generator บน Bolt.new ในครั้งเดียว

## คำสั่งหลัก (ส่งให้ Bolt.new)

```
สร้าง Web Application สำหรับสร้างรูปภาพด้วย AI โดยใช้ Together AI FLUX.1-schnell-Free API ด้วยฟีเจอร์ต่อไปนี้:

## ฟีเจอร์หลัก:
1. Web interface สวยงามใช้ Bootstrap 5 และ Font Awesome icons
2. ช่องใส่ API Key พร้อมบันทึกใน localStorage
3. ช่องใส่ prompt สำหรับสร้างรูป
4. เลือกสัดส่วนรูปภาพ (1:1, 4:3, 3:4, 16:9, 9:16, 21:9, 9:21, และกำหนดเอง)
5. แสดงรูปที่สร้างได้พร้อมดาวน์โหลด
6. ตัวอย่าง prompts คลิกได้
7. Real-time validation และ error handling

## เทคโนโลยี:
- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- API: Together AI FLUX.1-schnell-Free

## รายละเอียดการทำงาน:

### Backend (app.py):
- Flask web server
- รับ prompt, API key, width, height จาก frontend
- เรียก Together AI API endpoint: https://api.together.xyz/v1/images/generations
- ส่งคืน image URL
- Validation: ขนาดรูป 256-2048px, รวมไม่เกิน 2MP
- Support ทั้ง API key จาก frontend และ environment variable

### Frontend:
- ดีไซน์สวยด้วย gradient background
- API Key section พร้อมปุ่มแสดง/ซ่อน
- Aspect ratio selector ด้วย dropdown:
  * สี่เหลี่ยมจัตุรัส (1:1) - 1024x1024
  * แนวนอน (4:3) - 1024x768
  * แนวตั้ง (3:4) - 768x1024
  * แนวนอนกว้าง (16:9) - 1344x768
  * แนวตั้งยาว (9:16) - 768x1344
  * พาโนรามา (21:9) - 1536x640
  * แนวตั้งพิเศษ (9:21) - 640x1536
  * กำหนดเอง (custom input)
- ตัวอย่าง prompts: sunset mountains, cat wizard, futuristic city, japanese garden
- Loading indicator พร้อม spinner
- Download button ที่ดาวน์โหลดจริงด้วย blob API
- ชื่อไฟล์: flux_[prompt]_[date].png

### API Integration:
- Model: "black-forest-labs/FLUX.1-schnell-Free"
- Parameters: prompt, width, height, n=1
- Authorization: Bearer token
- Response format: JSON with data[0].url

### UX Features:
- Auto-save API key ใน localStorage
- แสดงสถานะ "บันทึกแล้ว" เมื่อมี API key
- Error handling ที่ชัดเจน
- Responsive design สำหรับมือถือ
- การแจ้งเตือนแบบ toast
- แสดงขนาดรูปในผลลัพธ์

สร้างให้เป็น complete working application พร้อมใช้งานเลย โดยใช้ชื่อไฟล์มาตรฐาน Flask (app.py, templates/index.html, requirements.txt)
```

## ไฟล์ทั้งหมดที่ต้องสร้าง:

### 1. requirements.txt
```
requests>=2.25.1
flask>=2.0.0
gunicorn>=20.1.0
```

### 2. app.py
```python
#!/usr/bin/env python3
"""
FLUX Image Generator Web App
ใช้ Together AI FLUX.1-schnell-Free API
"""

import os
import requests
from flask import Flask, render_template, request, jsonify
from typing import Optional

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'flux-secret-key-change-in-production')

class FluxImageGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("กรุณาตั้งค่า TOGETHER_API_KEY environment variable")
        
        self.base_url = "https://api.together.xyz/v1"
        self.model = "black-forest-labs/FLUX.1-schnell-Free"
    
    def generate_image(self, prompt: str, api_key: str = None, width: int = 1024, height: int = 1024, n: int = 1) -> tuple[Optional[str], Optional[str]]:
        """
        สร้างรูปภาพจาก prompt
        
        Returns:
            tuple: (image_url, error_message)
        """
        # Use provided API key or fallback to instance API key
        use_api_key = api_key or self.api_key
        if not use_api_key:
            return None, "ไม่พบ API Key"
        
        url = f"{self.base_url}/images/generations"
        
        headers = {
            "Authorization": f"Bearer {use_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "width": width,
            "height": height,
            "n": n
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            image_url = result["data"][0]["url"]
            
            return image_url, None
            
        except requests.exceptions.RequestException as e:
            error_msg = f"เกิดข้อผิดพลาด: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
                except:
                    error_msg += f" - {e.response.text}"
            return None, error_msg

# Initialize default generator (optional, will use API key from frontend if available)
try:
    generator = FluxImageGenerator()
except ValueError as e:
    generator = None
    print(f"Info: No default API key found, will use API key from frontend")

@app.route('/')
def index():
    """หน้าหลัก"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """API endpoint สำหรับสร้างรูป"""
    prompt = request.json.get('prompt', '').strip()
    api_key = request.json.get('api_key', '').strip()
    width = request.json.get('width', 1024)
    height = request.json.get('height', 1024)
    
    if not prompt:
        return jsonify({
            'success': False,
            'error': 'กรุณาใส่ prompt'
        }), 400
    
    # Validate dimensions
    if not (256 <= width <= 2048 and 256 <= height <= 2048):
        return jsonify({
            'success': False,
            'error': 'ขนาดรูปต้องอยู่ระหว่าง 256-2048 พิกเซล'
        }), 400
    
    # Check total pixels (2MP limit)
    if width * height > 2097152:
        return jsonify({
            'success': False,
            'error': 'ขนาดรูปใหญ่เกิน 2MP กรุณาลดขนาด'
        }), 400
    
    # Try to use provided API key or fallback to server-side API key
    if api_key:
        # Create temporary generator with provided API key
        try:
            temp_generator = FluxImageGenerator(api_key)
            image_url, error = temp_generator.generate_image(prompt, width=width, height=height)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'API Key ไม่ถูกต้อง: {str(e)}'
            }), 400
    elif generator:
        # Use server-side generator
        image_url, error = generator.generate_image(prompt, width=width, height=height)
    else:
        return jsonify({
            'success': False,
            'error': 'กรุณาใส่ API Key หรือตั้งค่า TOGETHER_API_KEY บนเซิร์ฟเวอร์'
        }), 500
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 500
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'prompt': prompt,
        'width': width,
        'height': height
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'server_api_key_configured': generator is not None,
        'supports_frontend_api_key': True
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("=== FLUX Image Generator Web App ===")
    print(f"🌐 เปิดใช้งานที่: http://localhost:{port}")
    print("📝 API Key ถูกต้อง:" if generator else "❌ ไม่พบ API Key")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### 3. templates/index.html (ต้องสร้างโฟลเดอร์ templates ก่อน)
```html
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLUX Image Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .container {
            max-width: 800px;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.9);
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 15px;
            font-size: 16px;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .generated-image {
            max-width: 100%;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .generated-image:hover {
            transform: scale(1.02);
        }
        .loading {
            display: none;
        }
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
        .alert {
            border-radius: 10px;
            border: none;
        }
        .example-prompts {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .example-prompt {
            background: rgba(255,255,255,0.8);
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            margin: 5px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .example-prompt:hover {
            background: rgba(255,255,255,1);
            transform: translateY(-1px);
        }
        .api-key-section {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px dashed rgba(255,255,255,0.3);
        }
        .api-key-saved {
            border-color: #28a745;
            background: rgba(40, 167, 69, 0.1);
        }
        .input-group {
            position: relative;
        }
        .password-toggle {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            border: none;
            background: none;
            color: #6c757d;
            cursor: pointer;
            z-index: 10;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header text-center py-4">
                        <h1 class="mb-0">
                            <i class="fas fa-magic text-primary"></i>
                            FLUX Image Generator
                        </h1>
                        <p class="text-muted mt-2">สร้างรูปภาพสวยๆ ด้วย AI จาก prompt ของคุณ</p>
                    </div>
                    <div class="card-body p-4">
                        <!-- API Key Section -->
                        <div class="api-key-section" id="apiKeySection">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h6 class="mb-0">
                                    <i class="fas fa-key text-warning"></i> 
                                    Together AI API Key
                                </h6>
                                <div>
                                    <span class="badge bg-success" id="apiKeyStatus" style="display: none;">
                                        <i class="fas fa-check"></i> บันทึกแล้ว
                                    </span>
                                    <button class="btn btn-sm btn-outline-secondary" id="toggleApiKey" onclick="toggleApiKeySection()">
                                        <i class="fas fa-cog"></i> ตั้งค่า
                                    </button>
                                </div>
                            </div>
                            
                            <div id="apiKeyForm" style="display: none;">
                                <div class="mb-3">
                                    <label for="apiKey" class="form-label">
                                        <small>API Key (จะบันทึกในเบราว์เซอร์ของคุณ)</small>
                                    </label>
                                    <div class="input-group">
                                        <input type="password" class="form-control" id="apiKey" 
                                               placeholder="กรุณาใส่ Together AI API Key ของคุณ">
                                        <button type="button" class="password-toggle" onclick="toggleApiKeyVisibility()">
                                            <i class="fas fa-eye" id="toggleIcon"></i>
                                        </button>
                                    </div>
                                    <small class="text-muted">
                                        <i class="fas fa-info-circle"></i> 
                                        รับ API key ฟรีได้ที่ 
                                        <a href="https://api.together.ai/" target="_blank">api.together.ai</a>
                                    </small>
                                </div>
                                <div class="text-end">
                                    <button type="button" class="btn btn-outline-secondary btn-sm me-2" onclick="clearApiKey()">
                                        <i class="fas fa-trash"></i> ลบ
                                    </button>
                                    <button type="button" class="btn btn-success btn-sm" onclick="saveApiKey()">
                                        <i class="fas fa-save"></i> บันทึก
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Example Prompts -->
                        <div class="example-prompts">
                            <small class="text-muted">ตัวอย่าง prompts (คลิกเพื่อใช้):</small>
                            <div class="mt-2">
                                <button class="btn btn-sm example-prompt" onclick="setPrompt('A beautiful sunset over the mountains with reflection in the lake')">
                                    🌅 ภูเขายามพระอาทิตย์ตก
                                </button>
                                <button class="btn btn-sm example-prompt" onclick="setPrompt('A cute cat wearing a wizard hat sitting on a stack of books')">
                                    🐱 แมวใส่หมวกพ่อมด
                                </button>
                                <button class="btn btn-sm example-prompt" onclick="setPrompt('A futuristic city with flying cars and neon lights')">
                                    🚗 เมืองอนาคต
                                </button>
                                <button class="btn btn-sm example-prompt" onclick="setPrompt('A serene Japanese garden with cherry blossoms and koi fish')">
                                    🌸 สวนญี่ปุ่น
                                </button>
                            </div>
                        </div>

                        <!-- Prompt Input Form -->
                        <form id="generateForm">
                            <div class="mb-3">
                                <label for="prompt" class="form-label">
                                    <i class="fas fa-pencil-alt"></i> ใส่ prompt ที่ต้องการสร้างรูป
                                </label>
                                <textarea class="form-control" id="prompt" rows="3" 
                                    placeholder="เช่น: A beautiful landscape with mountains and a lake at sunset"
                                    required></textarea>
                            </div>
                            
                            <!-- Aspect Ratio Section -->
                            <div class="mb-3">
                                <label class="form-label">
                                    <i class="fas fa-expand-arrows-alt"></i> สัดส่วนรูปภาพ
                                </label>
                                <div class="row">
                                    <div class="col-md-8">
                                        <select class="form-select" id="aspectRatio" onchange="updateDimensions()">
                                            <option value="1024x1024">สี่เหลี่ยมจัตุรัส (1:1) - 1024x1024</option>
                                            <option value="1024x768">แนวนอน (4:3) - 1024x768</option>
                                            <option value="768x1024">แนวตั้ง (3:4) - 768x1024</option>
                                            <option value="1344x768">แนวนอนกว้าง (16:9) - 1344x768</option>
                                            <option value="768x1344">แนวตั้งยาว (9:16) - 768x1344</option>
                                            <option value="1536x640">พาโนรามา (21:9) - 1536x640</option>
                                            <option value="640x1536">แนวตั้งพิเศษ (9:21) - 640x1536</option>
                                            <option value="custom">กำหนดเอง</option>
                                        </select>
                                    </div>
                                    <div class="col-md-4">
                                        <button type="button" class="btn btn-outline-info btn-sm w-100" onclick="toggleCustomSize()">
                                            <i class="fas fa-cog"></i> ปรับแต่ง
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- Custom Size Section -->
                                <div id="customSizeSection" class="mt-3" style="display: none;">
                                    <div class="row">
                                        <div class="col-6">
                                            <label for="customWidth" class="form-label">ความกว้าง (px)</label>
                                            <input type="number" class="form-control" id="customWidth" 
                                                   value="1024" min="256" max="2048" step="64" onchange="updateCustomDimensions()">
                                        </div>
                                        <div class="col-6">
                                            <label for="customHeight" class="form-label">ความสูง (px)</label>
                                            <input type="number" class="form-control" id="customHeight" 
                                                   value="1024" min="256" max="2048" step="64" onchange="updateCustomDimensions()">
                                        </div>
                                    </div>
                                    <small class="text-muted">
                                        <i class="fas fa-info-circle"></i> 
                                        แนะนำ: ใช้ค่าที่หารด้วย 64 ลงตัว, ขนาดรวม ≤ 2MP
                                    </small>
                                </div>
                            </div>

                            <div class="text-center">
                                <button type="submit" class="btn btn-primary btn-lg" id="generateBtn">
                                    <i class="fas fa-magic"></i> สร้างรูป
                                </button>
                            </div>
                        </form>

                        <!-- Loading Indicator -->
                        <div class="text-center mt-4 loading" id="loading">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">กำลังสร้าง...</span>
                            </div>
                            <p class="mt-2 text-muted">กำลังสร้างรูปภาพ กรุณารอสักครู่...</p>
                        </div>

                        <!-- Alert Messages -->
                        <div id="alertContainer" class="mt-3"></div>

                        <!-- Generated Image -->
                        <div id="imageContainer" class="mt-4 text-center" style="display: none;">
                            <h5><i class="fas fa-image"></i> รูปที่สร้างได้</h5>
                            <div class="mt-3">
                                <img id="generatedImage" class="generated-image" alt="Generated Image">
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">
                                    Prompt: <span id="usedPrompt"></span><br>
                                    ขนาด: <span id="usedSize"></span> พิกเซล
                                </small>
                            </div>
                            <div class="mt-2">
                                <button id="downloadBtn" class="btn btn-outline-primary" onclick="downloadImage()">
                                    <i class="fas fa-download"></i> ดาวน์โหลด
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Info Card -->
                <div class="card mt-4">
                    <div class="card-body">
                        <h6><i class="fas fa-info-circle text-info"></i> ข้อมูลเพิ่มเติม</h6>
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-success"></i> ใช้ FLUX.1-schnell-Free API</li>
                            <li><i class="fas fa-check text-success"></i> ฟรี 3 เดือน</li>
                            <li><i class="fas fa-check text-success"></i> รองรับภาษาไทยและอังกฤษ</li>
                            <li><i class="fas fa-exclamation-triangle text-warning"></i> Rate limit: 10 รูป/นาที</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // API Key Management
        function loadApiKey() {
            const savedApiKey = localStorage.getItem('together_api_key');
            if (savedApiKey) {
                document.getElementById('apiKey').value = savedApiKey;
                document.getElementById('apiKeyStatus').style.display = 'inline-block';
                document.getElementById('apiKeySection').classList.add('api-key-saved');
            }
        }

        function saveApiKey() {
            const apiKey = document.getElementById('apiKey').value.trim();
            if (!apiKey) {
                showAlert('กรุณาใส่ API Key');
                return;
            }
            
            // Basic API key validation
            if (apiKey.length < 20) {
                showAlert('API Key สั้นเกินไป กรุณาตรวจสอบ', 'warning');
                return;
            }

            localStorage.setItem('together_api_key', apiKey);
            document.getElementById('apiKeyStatus').style.display = 'inline-block';
            document.getElementById('apiKeySection').classList.add('api-key-saved');
            document.getElementById('apiKeyForm').style.display = 'none';
            showAlert('บันทึก API Key สำเร็จ! 🎉', 'success');
        }

        function clearApiKey() {
            localStorage.removeItem('together_api_key');
            document.getElementById('apiKey').value = '';
            document.getElementById('apiKeyStatus').style.display = 'none';
            document.getElementById('apiKeySection').classList.remove('api-key-saved');
            showAlert('ลบ API Key แล้ว', 'info');
        }

        function toggleApiKeySection() {
            const form = document.getElementById('apiKeyForm');
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        function toggleApiKeyVisibility() {
            const input = document.getElementById('apiKey');
            const icon = document.getElementById('toggleIcon');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        function setPrompt(prompt) {
            document.getElementById('prompt').value = prompt;
        }

        // Aspect Ratio Management
        function updateDimensions() {
            const aspectRatio = document.getElementById('aspectRatio').value;
            const customSection = document.getElementById('customSizeSection');
            
            if (aspectRatio === 'custom') {
                customSection.style.display = 'block';
            } else {
                customSection.style.display = 'none';
                // Update custom inputs to match selected ratio
                const [width, height] = aspectRatio.split('x').map(Number);
                document.getElementById('customWidth').value = width;
                document.getElementById('customHeight').value = height;
            }
        }

        function toggleCustomSize() {
            const customSection = document.getElementById('customSizeSection');
            const aspectRatio = document.getElementById('aspectRatio');
            
            if (customSection.style.display === 'none') {
                customSection.style.display = 'block';
                aspectRatio.value = 'custom';
            } else {
                customSection.style.display = 'none';
                aspectRatio.value = '1024x1024';
            }
        }

        function updateCustomDimensions() {
            const width = parseInt(document.getElementById('customWidth').value);
            const height = parseInt(document.getElementById('customHeight').value);
            const aspectRatio = document.getElementById('aspectRatio');
            
            // Check if total pixels exceed 2MP (2,097,152 pixels)
            const totalPixels = width * height;
            const maxPixels = 2097152; // 2MP
            
            if (totalPixels > maxPixels) {
                showAlert('ขนาดรูปใหญ่เกิน 2MP กรุณาลดขนาด', 'warning');
                return;
            }
            
            // Update the select to show custom
            aspectRatio.value = 'custom';
        }

        function getCurrentDimensions() {
            const aspectRatio = document.getElementById('aspectRatio').value;
            
            if (aspectRatio === 'custom') {
                return {
                    width: parseInt(document.getElementById('customWidth').value),
                    height: parseInt(document.getElementById('customHeight').value)
                };
            } else {
                const [width, height] = aspectRatio.split('x').map(Number);
                return { width, height };
            }
        }

        // Download image function
        async function downloadImage() {
            const imageUrl = document.getElementById('generatedImage').src;
            const prompt = document.getElementById('usedPrompt').textContent;
            
            if (!imageUrl) {
                showAlert('ไม่พบรูปภาพให้ดาวน์โหลด');
                return;
            }

            try {
                // Show loading on download button
                const downloadBtn = document.getElementById('downloadBtn');
                const originalText = downloadBtn.innerHTML;
                downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> กำลังดาวน์โหลด...';
                downloadBtn.disabled = true;

                // Fetch the image
                const response = await fetch(imageUrl);
                const blob = await response.blob();
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Generate filename from prompt (clean up for filename)
                const cleanPrompt = prompt.replace(/[^\w\s-]/g, '').replace(/\s+/g, '_').substring(0, 50);
                const timestamp = new Date().toISOString().slice(0, 10);
                a.download = `flux_${cleanPrompt}_${timestamp}.png`;
                
                // Trigger download
                document.body.appendChild(a);
                a.click();
                
                // Clean up
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showAlert('ดาวน์โหลดสำเร็จ! 📁', 'success');
                
            } catch (error) {
                console.error('Download error:', error);
                showAlert('ไม่สามารถดาวน์โหลดได้ กรุณาลองใหม่');
            } finally {
                // Reset button
                const downloadBtn = document.getElementById('downloadBtn');
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> ดาวน์โหลด';
                downloadBtn.disabled = false;
            }
        }

        function showAlert(message, type = 'danger') {
            const alertContainer = document.getElementById('alertContainer');
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            alertContainer.innerHTML = '';
            alertContainer.appendChild(alertDiv);
        }

        document.getElementById('generateForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) {
                showAlert('กรุณาใส่ prompt');
                return;
            }

            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('imageContainer').style.display = 'none';
            document.getElementById('alertContainer').innerHTML = '';

            // Get API key from localStorage
            const apiKey = localStorage.getItem('together_api_key');
            if (!apiKey) {
                showAlert('กรุณาตั้งค่า API Key ก่อน', 'warning');
                document.getElementById('apiKeyForm').style.display = 'block';
                return;
            }

            // Get current dimensions
            const dimensions = getCurrentDimensions();

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        prompt: prompt,
                        api_key: apiKey,
                        width: dimensions.width,
                        height: dimensions.height
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Show generated image
                    document.getElementById('generatedImage').src = data.image_url;
                    document.getElementById('usedPrompt').textContent = data.prompt;
                    document.getElementById('usedSize').textContent = `${data.width} × ${data.height}`;
                    document.getElementById('imageContainer').style.display = 'block';
                    
                    showAlert('สร้างรูปสำเร็จ! 🎉', 'success');
                } else {
                    showAlert(`เกิดข้อผิดพลาด: ${data.error}`);
                    
                    // If API key error, show API key form
                    if (data.error.includes('API Key') || data.error.includes('api_key')) {
                        document.getElementById('apiKeyForm').style.display = 'block';
                    }
                }
            } catch (error) {
                showAlert(`เกิดข้อผิดพลาด: ${error.message}`);
            } finally {
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
            }
        });

        // Load API key on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadApiKey();
        });
    </script>
</body>
</html>
```

## วิธีใช้งานบน Bolt.new:

1. **คัดลอกคำสั่งหลัก** ด้านบนไปส่งให้ Bolt.new
2. **ตรวจสอบไฟล์** ที่ Bolt สร้างให้ตรงกับโครงสร้างที่ต้องการ
3. **รัน** และทดสอบการทำงาน
4. **ใส่ API Key** จาก https://api.together.ai/

Bolt.new จะสร้างโปรแกรมให้พร้อมใช้งานเลย! 🚀