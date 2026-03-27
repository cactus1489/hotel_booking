import pandas as pd
import sqlite3
import os

def csv_to_sqlite(csv_path, db_path):
    # CSV 로드
    df = pd.read_csv(csv_path)
    
    # SQLite 연결
    conn = sqlite3.connect(db_path)
    
    # 테이블로 저장 (기존 테이블이 있으면 교체)
    df.to_sql('bookings', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Successfully converted {csv_path} to {db_path}")

if __name__ == "__main__":
    csv_file = "hotel_booking/hotel_bookings.csv"
    db_file = "hotel_booking/hotel_bookings.db"
    csv_to_sqlite(csv_file, db_file)
