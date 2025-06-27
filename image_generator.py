#!/usr/bin/env python3
"""
โปรแกรมรับคำสั่ง prompt แล้วเจนรูป
ใช้ Together AI FLUX.1-schnell-Free API
"""

import os
import requests
import json
from typing import Optional

class FluxImageGenerator:
    def __init__(self):
        self.api_key = os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("กรุณาตั้งค่า TOGETHER_API_KEY environment variable")
        
        self.base_url = "https://api.together.xyz/v1"
        self.model = "black-forest-labs/FLUX.1-schnell-Free"
    
    def generate_image(self, prompt: str, n: int = 1) -> Optional[str]:
        """
        สร้างรูปภาพจาก prompt
        
        Args:
            prompt: คำสั่งสำหรับสร้างรูป
            n: จำนวนรูปที่ต้องการ (default: 1)
        
        Returns:
            URL ของรูปที่สร้างได้
        """
        url = f"{self.base_url}/images/generations"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "n": n
        }
        
        try:
            print(f"กำลังสร้างรูปจาก prompt: {prompt}")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            image_url = result["data"][0]["url"]
            
            print(f"สร้างรูปสำเร็จ! URL: {image_url}")
            return image_url
            
        except requests.exceptions.RequestException as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            if hasattr(e.response, 'text'):
                print(f"รายละเอียด: {e.response.text}")
            return None

def main():
    """ฟังก์ชันหลักสำหรับรันโปรแกรม"""
    try:
        generator = FluxImageGenerator()
        
        print("=== FLUX Image Generator ===")
        print("พิมพ์ 'quit' หรือ 'exit' เพื่อออกจากโปรแกรม")
        print("-" * 40)
        
        while True:
            prompt = input("\nใส่ prompt สำหรับสร้างรูป: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'ออก']:
                print("ขออบคุณที่ใช้บริการ!")
                break
            
            if not prompt:
                print("กรุณาใส่ prompt")
                continue
            
            image_url = generator.generate_image(prompt)
            
            if image_url:
                print(f"\n✅ รูปของคุณพร้อมแล้ว!")
                print(f"🔗 URL: {image_url}")
                print(f"💡 คุณสามารถคัดลอก URL นี้ไปเปิดในเบราว์เซอร์เพื่อดูรูป")
            else:
                print("❌ ไม่สามารถสร้างรูปได้ กรุณาลองใหม่")
    
    except ValueError as e:
        print(f"❌ {e}")
        print("วิธีตั้งค่า API key:")
        print("export TOGETHER_API_KEY='your_api_key_here'")
    except KeyboardInterrupt:
        print("\n\nขออบคุณที่ใช้บริการ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดไม่คาดคิด: {e}")

if __name__ == "__main__":
    main()