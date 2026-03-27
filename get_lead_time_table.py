import sqlite3
import pandas as pd

# SQLite 연결
db_path = "hotel_booking/hotel_bookings.db"
conn = sqlite3.connect(db_path)

# 데이터 로드 (필요한 컬럼만)
query = "SELECT lead_time, is_canceled FROM bookings"
df = pd.read_sql_query(query, conn)
conn.close()

# 1. 리드타임 구간(Bin) 생성 (30일 단위)
bins = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 360, float('inf')]
labels = ['0-30일', '31-60일', '61-90일', '91-120일', '121-150일', '151-180일', 
          '181-210일', '211-240일', '241-270일', '271-300일', '301-360일', '360일 초과']

df['lead_time_range'] = pd.cut(df['lead_time'], bins=bins, labels=labels, right=False)

# 2. 구간별 취소율 계산
range_analysis = df.groupby('lead_time_range', observed=True).agg(
    전체_예약건수=('is_canceled', 'count'),
    취소건수=('is_canceled', 'sum')
).reset_index()

range_analysis['취소율(%)'] = (range_analysis['취소건수'] / range_analysis['전체_예약건수'] * 100).round(2)

# 3. 리드타임 기본 통계 (취소 여부별)
stats_analysis = df.groupby('is_canceled').agg(
    평균_리드타임=('lead_time', 'mean'),
    중간값_리드타임=('lead_time', 'median'),
    최대_리드타임=('lead_time', 'max'),
    최소_리드타임=('lead_time', 'min')
).reset_index()
stats_analysis['is_canceled'] = stats_analysis['is_canceled'].map({0: '정상 예약', 1: '취소됨'})

# 결과 출력용 포맷팅
print("\n[표 1] 리드타임 구간별 취소율 분석")
print(range_analysis.to_string(index=False))

print("\n" + "="*50)
print("[표 2] 취소 여부에 따른 리드타임 통계 지표")
print(stats_analysis.to_string(index=False))

# CSV로도 저장 (필요시 확인 가능)
range_analysis.to_csv("hotel_booking/lead_time_analysis_table.csv", index=False, encoding='utf-8-sig')
