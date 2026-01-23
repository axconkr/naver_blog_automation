from openpyxl import Workbook
from datetime import datetime
import os

# 현재 작업 디렉토리 확인
current_dir = os.getcwd()
print(f"현재 작업 디렉토리: {current_dir}")

# 날짜 형식: YYYYMMDD
date_str = datetime.now().strftime("%Y%m%d")
filename = f"blog{date_str}.xlsx"
filepath = os.path.join(current_dir, filename)

# 새 워크북 생성
wb = Workbook()
ws = wb.active

# 헤더 작성
ws['A1'] = "제목"
ws['B1'] = "본문"

# 블로그 포스팅 제목 샘플 5개 (많은 사용자가 검색할 법한 제목들)
blog_titles = [
    "파이썬 초보자를 위한 완벽 가이드 2026",
    "맛집 추천 베스트 10 - 서울 강남구 핫플레이스",
    "집에서 할 수 있는 간단한 운동 루틴 5가지",
    "주식 투자 시작하기 - 초보자를 위한 종목 추천",
    "여행 준비 체크리스트 - 해외여행 필수 준비물"
]

# A2 ~ A6에 제목 입력
for i, title in enumerate(blog_titles, start=2):
    ws[f'A{i}'] = title

# B2 ~ B6은 비워둠 (기본값이 None이므로 별도 처리 불필요)

# 파일 저장
wb.save(filepath)
print(f"엑셀 파일 생성 완료: {filepath}")
print(f"파일명: {filename}")

# 워크북 닫기
wb.close()

print("작업 완료!")
