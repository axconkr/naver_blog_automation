import google.generativeai as genai
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# Gemini API Key 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(".env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)

# 모델 설정 (gemini-1.5-pro)
model = genai.GenerativeModel('gemini-1.5-pro')

def generate_text(prompt):
    """
    Gemini API를 사용하여 텍스트 생성
    
    Args:
        prompt (str): 생성할 텍스트에 대한 프롬프트
    
    Returns:
        str: 생성된 텍스트
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def chat(prompt, history=None):
    """
    Gemini API를 사용하여 채팅 형식으로 대화
    
    Args:
        prompt (str): 사용자 메시지
        history (list): 대화 기록 (선택사항)
    
    Returns:
        str: 모델의 응답
    """
    try:
        if history:
            # 대화 기록이 있는 경우
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(prompt)
        else:
            # 새로운 대화 시작
            chat_session = model.start_chat()
            response = chat_session.send_message(prompt)
        
        return response.text
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def stream_generate(prompt):
    """
    Gemini API를 사용하여 스트리밍 방식으로 텍스트 생성
    
    Args:
        prompt (str): 생성할 텍스트에 대한 프롬프트
    
    Yields:
        str: 생성된 텍스트 청크
    """
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"오류 발생: {e}")

# 예제 사용
if __name__ == "__main__":
    # 기본 텍스트 생성 예제
    print("=== 기본 텍스트 생성 예제 ===")
    prompt = "안녕하세요! 간단히 자기소개를 해주세요."
    result = generate_text(prompt)
    if result:
        print(f"프롬프트: {prompt}")
        print(f"응답: {result}\n")
    
    # 채팅 예제
    print("=== 채팅 예제 ===")
    chat_result = chat("파이썬에 대해 간단히 설명해주세요.")
    if chat_result:
        print(f"응답: {chat_result}\n")
    
    # 스트리밍 예제
    print("=== 스트리밍 생성 예제 ===")
    stream_prompt = "블로그 포스팅을 위한 제목 3개를 제안해주세요."
    print(f"프롬프트: {stream_prompt}")
    print("응답: ", end="", flush=True)
    for chunk in stream_generate(stream_prompt):
        print(chunk, end="", flush=True)
    print("\n")
