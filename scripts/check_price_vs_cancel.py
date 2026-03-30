import sqlite3
import pandas as pd

conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
query = "SELECT hotel, adr, is_canceled FROM bookings"
df = pd.read_sql_query(query, conn)
conn.close()

# 호텔별 평균 지표 산출
analysis = df.groupby('hotel').agg(
    평균단가=('adr', 'mean'),
    취소율=('is_canceled', 'mean')
).reset_index()

analysis['취소율(%)'] = (analysis['취소율'] * 100).round(1)
analysis['평균단가'] = analysis['평균단가'].round(1)

print("--- 호텔 유형별 단가 및 취소율 비교 ---")
print(analysis.to_string(index=False))

# ADR 구간별 취소율 분석 (저가 vs 고가)
df['price_range'] = pd.qcut(df['adr'], q=4, labels=['저가', '중저가', '중고가', '고가'])
price_analysis = df.groupby(['hotel', 'price_range'], observed=True)['is_canceled'].mean().unstack() * 100

print("\n--- 호텔별 가격 구간에 따른 취소율 (%) ---")
print(price_analysis.round(1))
