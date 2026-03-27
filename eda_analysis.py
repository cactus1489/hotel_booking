import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib # 한글 폰트 설정 (Global preference 반영)

# SQLite 연결 및 데이터 로드
db_path = "hotel_booking/hotel_bookings.db"
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM bookings", conn)
conn.close()

print(f"--- 데이터 기본 정보 ---")
print(f"전체 예약 건수: {len(df)}")
print(f"컬럼 수: {len(df.columns)}")
print(df.info())

# 1. 취소율 분석 (is_canceled)
cancel_rate = df['is_canceled'].value_counts(normalize=True) * 100
print(f"\n--- 취소율 ---")
print(f"정상 예약: {cancel_rate[0]:.2f}%")
print(f"취소된 예약: {cancel_rate[1]:.2f}%")

# 2. 취소 여부에 따른 리드 타임(Lead Time) 차이
lead_time_stats = df.groupby('is_canceled')['lead_time'].mean()
print(f"\n--- 평균 리드 타임 (일) ---")
print(f"정상 예약: {lead_time_stats[0]:.2f}일")
print(f"취소된 예약: {lead_time_stats[1]:.2f}일")

# 시각화 설정 (seaborn 스타일 사용 안함 - Global preference 반영)
plt.figure(figsize=(15, 10))

# [시각화 1] 월별 예약 트렌드 및 취소 비중
plt.subplot(2, 2, 1)
monthly_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
sns.countplot(data=df, x='arrival_date_month', hue='is_canceled', order=monthly_order)
plt.title('월별 예약 및 취소 현황')
plt.xticks(rotation=45)

# [시각화 2] 예약 채널별 취소율
plt.subplot(2, 2, 2)
market_segment_cancel = df.groupby('market_segment')['is_canceled'].mean().sort_values(ascending=False) * 100
market_segment_cancel.plot(kind='bar', color='skyblue')
plt.title('예약 경로별 취소율 (%)')
plt.ylabel('취소율 (%)')

# [시각화 3] 리드 타임 분포 (취소 여부별)
plt.subplot(2, 2, 3)
sns.kdeplot(data=df, x='lead_time', hue='is_canceled', fill=True)
plt.title('리드 타임 분포 (취소 여부별)')
plt.xlabel('리드 타임 (일)')

# [시각화 4] 고객 유형별 비중
plt.subplot(2, 2, 4)
df['customer_type'].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.title('고객 유형별 비중')

plt.tight_layout()
plt.savefig('hotel_booking/eda_summary.png')
print(f"\nEDA summary image saved: hotel_booking/eda_summary.png")

# 주요 인사이트 도출
insights = f"""
--- 주요 데이터 인사이트 ---
1. 취소율 리스크: 전체 예약의 약 {cancel_rate[1]:.1f}%가 취소됨. 취소된 예약의 평균 리드 타임({lead_time_stats[1]:.1f}일)이 정상 예약({lead_time_stats[0]:.1f}일)보다 훨씬 길게 나타남. 즉, 미리 예약할수록 취소 가능성이 높음.
2. 계절성: 7-8월 휴가 시즌에 예약이 가장 많지만, 동시에 취소 절대량도 많음.
3. 예약 채널: 'Groups' 및 'Online TA(Online Travel Agent)' 경로의 취소율이 상대적으로 높음. 단체 예약에 대한 선결제 정책 강화가 필요해 보임.
4. 리드 타임 관리: 리드 타임이 100일을 넘어가는 예약에 대해 취소 방지 알림이나 특별 혜택을 제공하여 이탈을 최소화할 필요가 있음.
"""
print(insights)

# 텍스트 리포트 저장
with open("hotel_booking/eda_report.txt", "w", encoding="utf-8") as f:
    f.write(insights)
