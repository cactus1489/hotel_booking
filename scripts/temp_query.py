import sqlite3
import pandas as pd

conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
df = pd.read_sql_query("SELECT lead_time, is_canceled FROM bookings", conn)
conn.close()

bins = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 360, 1000]
labels = ['0-30일', '31-60일', '61-90일', '91-120일', '121-150일', '151-180일', 
          '181-210일', '211-240일', '241-270일', '271-300일', '301-360일', '360일+']
df['range'] = pd.cut(df['lead_time'], bins=bins, labels=labels, right=False)

res = df.groupby('range', observed=True).agg(
    total=('is_canceled', 'count'),
    canceled=('is_canceled', 'sum')
)
res['rate'] = (res['canceled'] / res['total'] * 100).round(1)

print(res.to_string())
