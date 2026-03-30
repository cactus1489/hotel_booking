import sqlite3
import pandas as pd

# 1. DB 연결
db_path = "hotel_booking/hotel_bookings.db"
conn = sqlite3.connect(db_path)

# 2. 데이터 불러오기
query = """
SELECT 
    hotel,
    lead_time,
    is_canceled,
    market_segment,
    customer_type,
    reservation_status,
    reservation_status_date as last_status_date
FROM bookings
"""
df = pd.read_sql_query(query, conn)

# 3. 예약 확정 시간(confirmed_date)과 취소 시간(canceled_date) 분리
# is_canceled 가 0이면 정상 예약된 날짜로 confirmed_date에 할당
# is_canceled 가 1이면 취소된 날짜로 canceled_date에 할당
df['confirmed_date'] = df.apply(lambda x: x['last_status_date'] if x['is_canceled'] == 0 else None, axis=1)
df['canceled_date'] = df.apply(lambda x: x['last_status_date'] if x['is_canceled'] == 1 else None, axis=1)

# 4. 새로운 테이블로 저장
df.to_sql('processed_bookings', conn, if_exists='replace', index=False)

# 5. 결과 확인용 출력
print("--- 새 테이블 생성 완료: processed_bookings ---")
print(df[['is_canceled', 'last_status_date', 'confirmed_date', 'canceled_date']].head(10))

conn.close()
print(f"\nDB 업데이트 완료: {db_path}")
