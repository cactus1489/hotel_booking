import sqlite3
import pandas as pd

conn = sqlite3.connect("hotel_booking/hotel_bookings.db")
df = pd.read_sql_query("SELECT * FROM bookings LIMIT 1", conn)
conn.close()

print(df.columns.tolist())
