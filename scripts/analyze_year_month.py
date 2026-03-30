import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

# 1. 데이터 로드
conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
query = """
SELECT 
    arrival_date_year, 
    arrival_date_month, 
    is_canceled, 
    adr, 
    (stays_in_weekend_nights + stays_in_week_nights) as total_nights
FROM bookings
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 2. 전처리: 매출 계산 및 날짜 정렬용 컬럼 생성
df['revenue'] = df.apply(lambda x: x['adr'] * x['total_nights'] if x['is_canceled'] == 0 else 0, axis=1)

# 월 이름을 숫자로 매핑하여 정렬에 사용
month_map = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
}
df['month_num'] = df['arrival_date_month'].map(month_map)

# 3. 년-월별 집계
stats = df.groupby(['arrival_date_year', 'month_num', 'arrival_date_month'], observed=True).agg(
    전체예약건수=('is_canceled', 'count'),
    취소건수=('is_canceled', 'sum'),
    실제매출=('revenue', 'sum')
).reset_index()

# 취소율 계산
stats['취소율(%)'] = (stats['취소건수'] / stats['전체예약건수'] * 100).round(2)
stats['년월'] = stats['arrival_date_year'].astype(str) + "-" + stats['month_num'].astype(str).str.zfill(2)

# 시간순 정렬
stats = stats.sort_values(['arrival_date_year', 'month_num'])

# 4. 시각화 (Dual Axis)
fig, ax1 = plt.subplots(figsize=(16, 8))

# 매출: 막대 그래프
bars = ax1.bar(stats['년월'], stats['실제매출'], color='skyblue', alpha=0.7, label='실제 매출')
ax1.set_xlabel('년-월', fontsize=12)
ax1.set_ylabel('실제 발생 매출 (수익)', fontsize=12, color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
plt.xticks(rotation=45)

# 취소율: 선 그래프 (우측 축)
ax2 = ax1.twinx()
line = ax2.plot(stats['년월'], stats['취소율(%)'], color='red', marker='o', linewidth=2, label='취소율(%)')
ax2.set_ylabel('예약 취소율 (%)', fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')

# 범례 통합
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='upper left')

plt.title('년-월별 실제 매출 및 예약 취소율 추이 분석', fontsize=16)
plt.tight_layout()
plt.savefig('hotel_booking/revenue_vs_cancellation_trend.png')

# 5. 데이터 표 출력 및 저장
output_table = stats[['년월', '전체예약건수', '취소건수', '취소율(%)', '실제매출']]
output_table.to_csv("hotel_booking/revenue_vs_cancellation_table.csv", index=False, encoding='utf-8-sig')

print("\n[년-월별 예약 취소율 및 매출 통계표]")
print(output_table.to_string(index=False))
print(f"\n시각화 저장 완료: hotel_booking/revenue_vs_cancellation_trend.png")
