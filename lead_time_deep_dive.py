import sqlite3
import pandas as pd

conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
df = pd.read_sql_query("SELECT lead_time, is_canceled, arrival_date_month, market_segment, adr FROM bookings", conn)
conn.close()

# 1. 월별 평균 리드타임 분석
monthly_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
monthly_lead = df.groupby('arrival_date_month')['lead_time'].mean().reindex(monthly_order)
monthly_cancel = df.groupby('arrival_date_month')['is_canceled'].mean().reindex(monthly_order)

# 2. 예약 채널별 리드타임 분석
segment_lead = df.groupby('market_segment')['lead_time'].mean().sort_values(ascending=False)
segment_cancel = df.groupby('market_segment')['is_canceled'].mean().reindex(segment_lead.index)

print("--- 월별 리드타임 및 취소율 ---")
for month in monthly_order:
    print(f"{month}: LeadTime={monthly_lead[month]:.1f}, CancelRate={monthly_cancel[month]*100:.1f}%")

print("\n--- 채널별 리드타임 및 취소율 ---")
for seg in segment_lead.index:
    print(f"{seg}: LeadTime={segment_lead[seg]:.1f}, CancelRate={segment_cancel[seg]*100:.1f}%")
