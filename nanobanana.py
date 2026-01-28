"""
나노바나나 - AI 이미지 생성 모듈

지원 서비스:
1. OpenAI DALL-E 3 (기본) - 고품질, 유료
2. Pollinations.ai (무료 대안) - API 키 불필요
"""

import requests
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 기본 이미지 저장 디렉토리
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")


def generate_image_dalle(prompt, output_path=None, size="1024x1024", quality="standard", style="vivid"):
    """
    OpenAI DALL-E 3로 이미지 생성
    
    Args:
        prompt: 이미지 생성 프롬프트
        output_path: 저장 경로 (None이면 자동 생성)
        size: 이미지 크기 (1024x1024, 1792x1024, 1024x1792)
        quality: 품질 (standard, hd)
        style: 스타일 (vivid, natural)
    
    Returns:
        저장된 이미지 경로 또는 None
    """
    if not OPENAI_API_KEY:
        print("  ✗ OPENAI_API_KEY가 설정되지 않았습니다")
        return None
    
    print(f"이미지 생성 중 (DALL-E 3): {prompt[:50]}...")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1
        )
        
        image_url = response.data[0].url
        
        # 이미지 다운로드
        img_response = requests.get(image_url, timeout=60)
        
        if img_response.status_code == 200:
            if output_path is None:
                timestamp = int(time.time() * 1000)
                os.makedirs(IMAGES_DIR, exist_ok=True)
                output_path = os.path.join(IMAGES_DIR, f"dalle_{timestamp}.png")
            else:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            
            print(f"  ✓ 이미지 저장: {output_path}")
            return output_path
        else:
            print(f"  ✗ 이미지 다운로드 실패: {img_response.status_code}")
            return None
            
    except Exception as e:
        error_msg = str(e)
        if "billing" in error_msg.lower() or "quota" in error_msg.lower():
            print("  ✗ API 할당량 초과 또는 결제 필요")
        elif "content_policy" in error_msg.lower():
            print("  ✗ 콘텐츠 정책 위반 - 프롬프트 수정 필요")
        else:
            print(f"  ✗ DALL-E 오류: {e}")
        return None


def generate_image_pollinations(prompt, output_path=None, width=1024, height=1024, style=None):
    """
    Pollinations.ai로 이미지 생성 (무료 대안)
    
    Args:
        prompt: 이미지 생성 프롬프트
        output_path: 저장 경로
        width: 이미지 너비
        height: 이미지 높이
        style: 추가 스타일 프롬프트
    
    Returns:
        저장된 이미지 경로 또는 None
    """
    style_prompts = {
        "realistic": "photorealistic, high quality, detailed",
        "illustration": "digital illustration, clean lines, vibrant colors",
        "cartoon": "cartoon style, simple, colorful",
        "blog": "modern blog image, clean, professional, high quality"
    }
    
    if style and style in style_prompts:
        full_prompt = f"{prompt}, {style_prompts[style]}"
    else:
        full_prompt = prompt
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    
    print(f"이미지 생성 중 (Pollinations): {prompt[:50]}...")
    
    try:
        response = requests.get(url, timeout=180)
        
        if response.status_code == 200 and len(response.content) > 1000:
            if output_path is None:
                timestamp = int(time.time() * 1000)
                os.makedirs(IMAGES_DIR, exist_ok=True)
                output_path = os.path.join(IMAGES_DIR, f"poll_{timestamp}.png")
            else:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"  ✓ 이미지 저장: {output_path}")
            return output_path
        else:
            print(f"  ✗ 실패: status={response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ✗ Pollinations 오류: {e}")
        return None


# 기본 함수 - DALL-E 3 사용
def generate_image(prompt, output_path=None, style="blog", provider="dalle"):
    """
    이미지 생성 (기본 함수)
    
    Args:
        prompt: 이미지 생성 프롬프트
        output_path: 저장 경로
        style: 이미지 스타일 (realistic, illustration, cartoon, blog)
        provider: 서비스 제공자 (dalle, pollinations)
    
    Returns:
        저장된 이미지 경로 또는 None
    """
    # 스타일별 프롬프트 보강
    style_enhancements = {
        "realistic": "photorealistic, high quality photograph, detailed",
        "illustration": "digital illustration, clean artistic style, vibrant colors",
        "cartoon": "cartoon style illustration, friendly and colorful",
        "blog": "professional blog header image, modern and clean design, visually appealing"
    }
    
    enhanced_prompt = f"{prompt}. {style_enhancements.get(style, style_enhancements['blog'])}"
    
    if provider == "pollinations":
        return generate_image_pollinations(enhanced_prompt, output_path, style=style)
    else:
        # DALL-E 3 사용 (기본)
        return generate_image_dalle(enhanced_prompt, output_path)


def generate_blog_images(sections, output_dir=None, provider="dalle"):
    """
    블로그 섹션별 이미지 생성
    
    Args:
        sections: 섹션 정보 리스트 [{"title": "제목", "prompt": "이미지 프롬프트"}, ...]
        output_dir: 출력 디렉토리
        provider: 서비스 제공자 (dalle, pollinations)
    
    Returns:
        생성된 이미지 경로 리스트
    """
    if output_dir is None:
        output_dir = IMAGES_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    
    image_paths = []
    
    for i, section in enumerate(sections):
        title = section.get("title", f"섹션 {i+1}")
        prompt = section.get("prompt", title)
        
        output_path = os.path.join(output_dir, f"section_{i+1}.png")
        
        print(f"\n[{i+1}/{len(sections)}] {title}")
        result = generate_image(prompt, output_path=output_path, style="blog", provider=provider)
        
        image_paths.append(result)
        
        # API 속도 제한 대응
        if i < len(sections) - 1:
            time.sleep(2)
    
    return image_paths


def generate_image_with_fallback(prompt, output_path=None, style="blog"):
    """
    폴백 지원 이미지 생성 (DALL-E 실패시 Pollinations 시도)
    
    Args:
        prompt: 이미지 생성 프롬프트
        output_path: 저장 경로
        style: 이미지 스타일
    
    Returns:
        저장된 이미지 경로 또는 None
    """
    # 1. DALL-E 3 시도 (기본)
    result = generate_image(prompt, output_path, style, provider="dalle")
    
    if result:
        return result
    
    # 2. Pollinations 시도 (무료 폴백)
    print("  → Pollinations로 재시도...")
    return generate_image(prompt, output_path, style, provider="pollinations")


if __name__ == "__main__":
    print("=== 나노바나나 이미지 생성 테스트 ===\n")
    
    test_prompt = "A modern office workspace with laptop, coffee cup, and green plants, bright natural lighting"
    
    # DALL-E 3 테스트
    print("--- DALL-E 3 테스트 ---")
    result = generate_image(test_prompt, style="realistic")
    
    if result:
        print(f"\n✓ 테스트 성공: {result}")
    else:
        print("\n✗ DALL-E 실패 - Pollinations 시도")
        result = generate_image(test_prompt, style="realistic", provider="pollinations")
        
        if result:
            print(f"\n✓ Pollinations 성공: {result}")
        else:
            print("\n✗ 모든 서비스 실패")
