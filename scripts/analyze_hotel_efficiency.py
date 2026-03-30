import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

# 1. 데이터 로드
conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
query = """
SELECT 
    hotel,
    arrival_date_year, 
    arrival_date_month, 
    is_canceled, 
    adr, 
    (stays_in_weekend_nights + stays_in_week_nights) as total_nights
FROM bookings
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 2. 전처리
df['revenue'] = df.apply(lambda x: x['adr'] * x['total_nights'] if x['is_canceled'] == 0 else 0, axis=1)
monthly_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=monthly_order, ordered=True)

# 3. 호텔별/월별 집계
hotel_stats = df.groupby(['hotel', 'arrival_date_month'], observed=True).agg(
    예약건수=('is_canceled', 'count'),
    실제매출=('revenue', 'sum'),
    취소율=('is_canceled', 'mean'),
    평균단가_ADR=('adr', 'mean')
).reset_index()

# 4. 시각화 (호텔별 비교)
fig, axes = plt.subplots(2, 1, figsize=(15, 12))

hotels = hotel_stats['hotel'].unique()

for i, hotel in enumerate(hotels):
    data = hotel_stats[hotel_stats['hotel'] == hotel]
    
    # 좌측 축: 예약 건수
    ax1 = axes[i]
    sns.barplot(data=data, x='arrival_date_month', y='예약건수', alpha=0.3, color='gray', ax=ax1)
    ax1.set_ylabel(f'{hotel} 예약 건수', color='gray', fontsize=12)
    
    # 우측 축: 실제 매출
    ax2 = ax1.twinx()
    sns.lineplot(data=data, x='arrival_date_month', y='실제매출', marker='o', color='blue', linewidth=3, ax=ax2)
    ax2.set_ylabel(f'{hotel} 실제 매출', color='blue', fontsize=12)
    
    ax1.set_title(f'[{hotel}] 예약 건수 vs 실제 매출 트렌드', fontsize=15)

plt.tight_layout()
plt.savefig('hotel_booking/hotel_efficiency_comparison.png')

# 5. 인사이트 도출을 위한 데이터 출력
print("--- 호텔별 운영 효율성 분석 ---")
for hotel in hotels:
    print(f"\n[{hotel}] 상위 취소율 달 (저효율 구간):")
    low_eff = hotel_stats[hotel_stats['hotel'] == hotel].sort_values('취소율', ascending=False).head(3)
    print(low_eff[['arrival_date_month', '예약건수', '실제매출', '취소율', '평균단가_ADR']])
