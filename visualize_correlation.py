import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib # 한글 폰트 설정

# 1. 데이터 로드
db_path = "hotel_booking/hotel_bookings.db"
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT lead_time, is_canceled FROM bookings", conn)
conn.close()

# 2. 통계적 상관계수 계산
correlation = df['lead_time'].corr(df['is_canceled'])
print(f"리드타임과 취소 여부 간의 상관계수: {correlation:.4f}")

# 3. 시각화 준비 (리드타임을 10일 단위로 묶어서 취소율 계산)
df['lead_time_bin'] = (df['lead_time'] // 10) * 10
# 데이터가 너무 적은 구간(리드타임 300일 초과)은 노이즈를 줄이기 위해 제외하거나 합침
df_trend = df[df['lead_time'] <= 350].groupby('lead_time_bin')['is_canceled'].mean() * 100

# 시각화 시작
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# [시각화 1] 리드타임 증가에 따른 취소율 변화 (Trend Line)
sns.lineplot(x=df_trend.index, y=df_trend.values, ax=axes[0], color='red', marker='o')
axes[0].set_title(f'리드타임 증가에 따른 취소율 변화 트렌드\n(상관계수: {correlation:.4f})', fontsize=15)
axes[0].set_xlabel('리드타임 (일 단위)', fontsize=12)
axes[0].set_ylabel('평균 취소율 (%)', fontsize=12)
axes[0].grid(True, linestyle='--', alpha=0.6)

# [시각화 2] 예약 상태별 리드타임 분포 (Box Plot)
sns.boxplot(data=df, x='is_canceled', y='lead_time', ax=axes[1], palette='Set2')
axes[1].set_xticklabels(['정상 예약', '취소됨'])
axes[1].set_title('예약 상태별 리드타임 분포 비교', fontsize=15)
axes[1].set_xlabel('예약 상태', fontsize=12)
axes[1].set_ylabel('리드타임 (일)', fontsize=12)

# 레이아웃 조정 및 저장
plt.tight_layout()
plt.savefig('hotel_booking/lead_time_correlation_visual.png')
print("시각화 결과가 'hotel_booking/lead_time_correlation_visual.png'에 저장되었습니다.")
