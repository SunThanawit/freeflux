#!/usr/bin/env python3
"""
FLUX Image Generator Web App
ใช้ Together AI FLUX.1-schnell-Free API
"""

import os
import requests
from flask import Flask, render_template, request, jsonify, flash
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