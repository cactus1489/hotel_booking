import sqlite3
import pandas as pd

# 1. 원본 DB 연결 및 전체 데이터 로드
source_db = "hotel_booking/hotel_bookings.db"
target_db = "hotel_booking/processed_data.db"

conn_src = sqlite3.connect(source_db)

# 요청하신 핵심 컬럼들 (리드타임, 예약정보, 날짜 등) 추출
query = """
SELECT 
    hotel,
    is_canceled,
    lead_time,
    arrival_date_year,
    arrival_date_month,
    arrival_date_day_of_month,
    market_segment,
    distribution_channel,
    customer_type,
    adr,
    reservation_status,
    reservation_status_date as last_status_date
FROM bookings
"""
df = pd.read_sql_query(query, conn_src)
conn_src.close()

# 2. 확정 시간 및 취소 시간 컬럼 생성 (전체 데이터 대상)
df['confirmed_date'] = df.apply(lambda x: x['last_status_date'] if x['is_canceled'] == 0 else None, axis=1)
df['canceled_date'] = df.apply(lambda x: x['last_status_date'] if x['is_canceled'] == 1 else None, axis=1)

# 3. 새로운 SQLite 파일로 저장
conn_tgt = sqlite3.connect(target_db)
df.to_sql('processed_bookings', conn_tgt, if_exists='replace', index=False)
conn_tgt.close()

print(f"--- 파일 생성 완료: {target_db} ---")
print(f"전체 행 수: {len(df)}")
print(f"포함된 컬럼: {df.columns.tolist()}")
