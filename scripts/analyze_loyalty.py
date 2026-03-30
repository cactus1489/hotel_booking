import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

# 1. 데이터 로드
conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
query = """
SELECT 
    is_repeated_guest, 
    previous_cancellations, 
    previous_bookings_not_canceled, 
    is_canceled 
FROM bookings
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 2. 고객 그룹 정의
# 그룹 A: 처음 방문 고객 (is_repeated_guest == 0)
# 그룹 B: 재방문 고객 (is_repeated_guest == 1)
# 그룹 C: 과거 취소 이력이 있는 재방문 고객 (is_repeated_guest == 1 & previous_cancellations > 0)

def classify_guest(row):
    if row['is_repeated_guest'] == 0:
        return '신규 고객'
    else:
        if row['previous_cancellations'] > 0:
            return '재방문 고객 (취소 이력 있음)'
        else:
            return '재방문 고객 (취소 이력 없음)'

df['guest_segment'] = df.apply(classify_guest, axis=1)

# 3. 그룹별 취소율 분석
segment_analysis = df.groupby('guest_segment').agg(
    전체예약건수=('is_canceled', 'count'),
    현재취소건수=('is_canceled', 'sum')
).reset_index()

segment_analysis['취소율(%)'] = (segment_analysis['현재취소건수'] / segment_analysis['전체예약건수'] * 100).round(2)

# 4. 시각화
plt.figure(figsize=(12, 6))
sns.barplot(data=segment_analysis, x='guest_segment', y='취소율(%)', palette='viridis')
plt.title('고객 이력(재방문 및 과거 취소)에 따른 현재 예약 취소율 비교', fontsize=15)
plt.ylabel('현재 예약 취소율 (%)')
plt.ylim(0, 100)

for i, row in segment_analysis.iterrows():
    plt.text(i, row['취소율(%)'] + 2, f"{row['취소율(%)']}%", ha='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('hotel_booking/guest_loyalty_analysis.png')

print("--- 고객 세그먼트별 취소 리스크 분석 ---")
print(segment_analysis)
