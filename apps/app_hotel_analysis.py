import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="호텔 운영 효율성 분석 리포트", layout="wide")

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 경로 수정: data 폴더 내의 db 참조
    conn = sqlite3.connect("hotel_booking/data/hotel_bookings.db")
    query = """
    SELECT 
        hotel,
        arrival_date_month, 
        is_canceled, 
        adr, 
        (stays_in_weekend_nights + stays_in_week_nights) as total_nights
    FROM bookings
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # 월 순서 정렬
    monthly_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
    df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=monthly_order, ordered=True)
    
    # 매출 계산
    df['revenue'] = df.apply(lambda x: x['adr'] * x['total_nights'] if x['is_canceled'] == 0 else 0, axis=1)
    return df

df = load_data()

# 사이드바 설정
st.sidebar.title("🏨 분석 필터")
selected_hotel = st.sidebar.selectbox("호텔 유형 선택", df['hotel'].unique())

# 호텔별 데이터 필터링
hotel_df = df[df['hotel'] == selected_hotel]

# 월별 집계
stats = hotel_df.groupby('arrival_date_month', observed=True).agg(
    예약건수=('is_canceled', 'count'),
    취소건수=('is_canceled', 'sum'),
    실제매출=('revenue', 'sum'),
    평균ADR=('adr', 'mean')
).reset_index()

stats['취소율(%)'] = (stats['취소건수'] / stats['예약건수'] * 100).round(1)
stats['건당평균수익'] = (stats['실제매출'] / stats['예약건수']).round(1)

# 메인 화면 구성
st.title(f"📊 {selected_hotel} 운영 효율성 및 수익성 분석")
st.markdown("---")

# KPI 지표 (상단)
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 예약 건수", f"{stats['예약건수'].sum():,}건")
col2.metric("총 실제 매출", f"{stats['실제매출'].sum():,.0f}")
col3.metric("평균 취소율", f"{(stats['취소건수'].sum()/stats['예약건수'].sum()*100):.1f}%")
col4.metric("최고 매출 월", stats.loc[stats['실제매출'].idxmax(), 'arrival_date_month'])

# 데이터 테이블 표시
st.subheader("📅 월별 운영 지표 상세")
st.dataframe(stats.style.highlight_max(axis=0, subset=['실제매출', '건당평균수익'], color='#D4E6F1'), use_container_width=True)

# 시각화 (Dual Axis 컨셉)
st.subheader("📈 예약 건수 vs 실제 매출 추이")
fig = px.bar(stats, x='arrival_date_month', y='예약건수', title="월별 예약 건수 (Volume)", 
             labels={'예약건수': '예약 건수', 'arrival_date_month': '월'}, color_discrete_sequence=['#BDC3C7'])
fig_line = px.line(stats, x='arrival_date_month', y='실제매출', title="월별 실제 매출 (Value)",
                   labels={'실제매출': '실제 매출'}, markers=True)
fig_line.update_traces(line_color='#2E86C1', line_width=4)

st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig_line, use_container_width=True)

# 문제 정의 및 원인 분석 섹션
st.markdown("---")
col_a, col_b = st.columns(2)

if selected_hotel == "City Hotel":
    with col_a:
        st.error("❗ 문제 정의 (Problem Definition)")
        st.write("""
        **"질적 성장 정체 구간(2분기) 발생"**
        - 4~6월 예약 건수는 연중 최고치에 달하지만, 실제 매출은 7~8월 성수기보다 낮음.
        - 특히 5월은 업무 부하(예약 건수)는 최대이나 수익 효율은 현저히 저하됨.
        """)
        
    with col_b:
        st.info("🔍 원인 분석 (Root Cause Analysis)")
        st.write("""
        1. **높은 취소율 (허수 예약):** 2분기 취소율이 44%를 상회하며 운영 리소스의 절반이 낭비됨.
        2. **리드타임의 역설:** 여름 휴가 전 '비교 예약' 고객이 몰리며 발생한 일시적 팽창.
        3. **낮은 ADR:** 물량 확보를 위한 과도한 할인 정책이 수익성을 악화시킴.
        """)
else:
    with col_a:
        st.warning("❗ 문제 정의 (Problem Definition)")
        st.write("""
        **"극심한 계절적 수익 불균형"**
        - 7~8월에 전체 매출의 상당 부분이 집중되어 있으며, 비수기(11월~1월) 가동률이 현저히 낮음.
        - 비수기에도 고정비(인건비, 시설 유지비)는 계속 발생하여 연간 수익성을 저해함.
        """)
        
    with col_b:
        st.info("🔍 원인 분석 (Root Cause Analysis)")
        st.write("""
        1. **목적성 예약의 한계:** 휴양 목적이 강해 가족 단위 고객의 방학/휴가 시즌 의존도가 지나치게 높음.
        2. **비수기 매력도 부족:** 비수기용 특화 상품(MICE, 스파, 장기 투숙 등)의 부재.
        3. **가격 탄력성 대응 부족:** 비수기 낮은 ADR 전략에도 불구하고 예약 건수 확보에 실패함.
        """)

st.success("💡 권장 전략: " + ("4-6월 예약 보증금 강화 및 선결제 유도" if selected_hotel == "City Hotel" else "비수기 연박 할인 및 테마 패키지 강화"))
