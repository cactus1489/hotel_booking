import sqlite3
import pandas as pd

conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
df = pd.read_sql_query("SELECT arrival_date_year, is_repeated_guest, previous_cancellations, is_canceled, adr, (stays_in_weekend_nights + stays_in_week_nights) as total_nights FROM bookings", conn)
conn.close()

df['revenue'] = df.apply(lambda x: x['adr'] * x['total_nights'] if x['is_canceled'] == 0 else 0, axis=1)

def classify(row):
    if row['is_repeated_guest'] == 0: return 'A.New'
    elif row['previous_cancellations'] == 0: return 'B.Loyal_Repeat'
    else: return 'C.Risky_Repeat'

df['segment'] = df.apply(classify, axis=1)
stats = df.groupby(['arrival_date_year', 'segment'], observed=True).agg(
    count=('is_canceled', 'count'),
    revenue=('revenue', 'sum'),
    cancel_rate=('is_canceled', 'mean')
).reset_index()

print(stats.to_string())
