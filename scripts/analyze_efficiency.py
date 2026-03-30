import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

# 1. 데이터 로드
conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
# 매출 계산을 위해 ADR과 숙박 기간(주말+평일)을 가져옴
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

# 2. 월별 정렬을 위한 설정
monthly_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=monthly_order, ordered=True)

# 3. 월별 지표 계산
# 매출은 취소되지 않은(is_canceled == 0) 데이터만 합산
df['revenue'] = df.apply(lambda x: x['adr'] * x['total_nights'] if x['is_canceled'] == 0 else 0, axis=1)

monthly_stats = df.groupby(['arrival_date_year', 'arrival_date_month'], observed=True).agg(
    예약건수=('is_canceled', 'count'),
    실제매출=('revenue', 'sum'),
    평균단가_ADR=('adr', 'mean'),
    취소율=('is_canceled', 'mean')
).reset_index()

# 4. 시각화 (이중 축 사용)
fig, ax1 = plt.subplots(figsize=(15, 7))

# 좌측 축: 예약 건수 (막대 그래프)
sns.barplot(data=monthly_stats, x='arrival_date_month', y='예약건수', alpha=0.3, color='blue', ax=ax1, label='예약 건수')
ax1.set_ylabel('총 예약 건수 (건)', color='blue', fontsize=12)
ax1.tick_params(axis='y', labelcolor='blue')

# 우측 축: 실제 매출 (선 그래프)
ax2 = ax1.twinx()
sns.lineplot(data=monthly_stats, x='arrival_date_month', y='실제매출', marker='o', color='red', ax=ax2, label='실제 매출')
ax2.set_ylabel('실제 발생 매출 (수익)', color='red', fontsize=12)
ax2.tick_params(axis='y', labelcolor='red')

plt.title('월별 예약 건수 vs 실제 매출 추이 비교 (2015-2017)', fontsize=16)
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig('hotel_booking/booking_vs_revenue.png')

# 5. 인사이트 도출을 위한 데이터 출력
print("--- 월별 효율성 분석 (최근 데이터 기준) ---")
print(monthly_stats[['arrival_date_month', '예약건수', '실제매출', '취소율', '평균단가_ADR']].tail(5))
