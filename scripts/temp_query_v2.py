import sqlite3
import pandas as pd

conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
df = pd.read_sql_query("SELECT lead_time, is_canceled FROM bookings", conn)
conn.close()

bins = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 360, 1000]
df['range_idx'] = pd.cut(df['lead_time'], bins=bins, labels=False, right=False)

res = df.groupby('range_idx').agg(
    total=('is_canceled', 'count'),
    canceled=('is_canceled', 'sum')
).reset_index()

res['rate'] = (res['canceled'] / res['total'] * 100).round(1)

for idx, row in res.iterrows():
    print(f"Index {int(row['range_idx'])}: Total={int(row['total'])}, Canceled={int(row['canceled'])}, Rate={row['rate']}%")
