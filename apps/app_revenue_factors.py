import streamlit as st
import pandas as pd
import sqlite3

# 페이지 설정
st.set_page_config(page_title="매출 핵심 요인 6대 전략 보고서", layout="wide")

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 경로 수정: data 폴더 내의 db 참조
    conn = sqlite3.connect("hotel_booking/data/hotel_bookings.db")
    query = """
    SELECT 
        hotel, is_canceled, lead_time, market_segment, deposit_type, adr, 
        arrival_date_month, (stays_in_weekend_nights + stays_in_week_nights) as total_nights
    FROM bookings
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # 월 순서 정렬
    monthly_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
    df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=monthly_order, ordered=True)
    
    # 매출 계산 (is_canceled가 0인 경우만)
    df['revenue'] = df.apply(lambda x: x['adr'] * x['total_nights'] if x['is_canceled'] == 0 else 0, axis=1)
    return df

df = load_data()

st.title("🚀 호텔 실제 발생 매출(Actual Revenue) 핵심 요인 분석")
st.markdown("데이터 기반의 문제 정의부터 기대효과까지 6가지 핵심 차원을 심층 분석합니다.")
st.info("💡 모든 지표는 2015-2017 전체 기간 데이터를 테이블 형식으로 산출한 결과입니다.")

# 5대 핵심 요인 탭 생성
tabs = st.tabs([
    "1. 취소 리스크", "2. 객실 단가(ADR)", "3. 리드 타임", 
    "4. 예약 채널", "5. 숙박 기간"
])

# --- 공통 스타일 함수 ---
def show_analysis(prob, cause, solution, effect):
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"❗ 문제 정의: {prob}")
        st.info(f"🔍 원인 분석: {cause}")
    with col2:
        st.success(f"🛠️ 해결 방안: {solution}")
        st.warning(f"✨ 기대 효과: {effect}")

# --- Tab 1: 취소 리스크 ---
with tabs[0]:
    st.header("📉 예약 취소율과 매출의 상관관계")
    
    col_stat1, col_stat2 = st.columns(2)
    
    # 1. 월별 취소율 테이블
    with col_stat1:
        cancel_table = df.groupby(['hotel', 'arrival_date_month'], observed=True).agg(
            취소율=('is_canceled', 'mean')
        ).reset_index()
        cancel_table['취소율(%)'] = (cancel_table['취소율'] * 100).round(1)
        st.subheader("📊 [데이터 1-1] 호텔별 월별 취소율 (%)")
        st.dataframe(cancel_table.pivot(index='arrival_date_month', columns='hotel', values='취소율(%)'), use_container_width=True)
    
    # 2. 월별 매출액 테이블 추가
    with col_stat2:
        revenue_monthly = df.groupby(['hotel', 'arrival_date_month'], observed=True).agg(
            총매출=('revenue', 'sum')
        ).reset_index()
        st.subheader("💰 [데이터 1-2] 호텔별 월별 총 매출액")
        # 가독성을 위해 정수형으로 변환 후 표시
        rev_pivot = revenue_monthly.pivot(index='arrival_date_month', columns='hotel', values='총매출')
        st.dataframe(rev_pivot.style.format("{:,.0f}"), use_container_width=True)
    
    # 3. 예약 채널 및 ADR & 매출액 결합 분석 테이블
    st.subheader("📊 [데이터 2] 호텔별 예약 채널 & 평균 ADR & 취소율 & 총매출 결합 분석")
    channel_adr_stats = df.groupby(['hotel', 'market_segment']).agg(
        예약건수=('is_canceled', 'count'),
        평균ADR=('adr', 'mean'),
        취소율=('is_canceled', 'mean'),
        총매출액=('revenue', 'sum')
    ).reset_index()
    
    channel_adr_stats['평균ADR'] = channel_adr_stats['평균ADR'].round(1)
    channel_adr_stats['취소율(%)'] = (channel_adr_stats['취소율'] * 100).round(1)
    channel_adr_stats['총매출액'] = channel_adr_stats['총매출액'].astype(int)
    
    col_city, col_resort = st.columns(2)
    with col_city:
        st.write("**🏨 City Hotel 채널별 상세 성과**")
        city_stats = channel_adr_stats[channel_adr_stats['hotel'] == 'City Hotel'].sort_values('예약건수', ascending=False)
        st.table(city_stats.style.format({'총매출액': '{:,.0f}'}))
    with col_resort:
        st.write("**🏖️ Resort Hotel 채널별 상세 성과**")
        resort_stats = channel_adr_stats[channel_adr_stats['hotel'] == 'Resort Hotel'].sort_values('예약건수', ascending=False)
        st.table(resort_stats.style.format({'총매출액': '{:,.0f}'}))
    
    show_analysis(
        "City Hotel은 취소율이 40%를 상회함에도 불구하고 절대적인 예약 볼륨 덕분에 매출 규모는 Resort Hotel의 특정 비수기보다 큼.",
        "City Hotel의 높은 취소율은 곧 '잠재 매출의 공중분해'를 의미하며, 이를 10%만 개선해도 월 수억 원의 추가 매출 확보 가능.",
        "취소율이 높은 채널(Online TA)의 매출 비중이 큰 만큼, 해당 채널 고객 대상의 리텐션 캠페인 우선 순위 배정.",
        "투숙 확정률 상승을 통한 실제 현금 흐름(Cash Flow) 개선 및 마케팅 효율 극대화."
    )

# --- Tab 2: 객실 단가(ADR) ---
with tabs[1]:
    st.header("💰 객실 단가(ADR) 전략 분석")
    adr_table = df.groupby(['hotel', 'arrival_date_month'], observed=True)['adr'].mean().reset_index()
    adr_table['평균단가(ADR)'] = adr_table['adr'].round(1)
    
    st.subheader("📊 [데이터] 호텔별 월평균 객실 단가(ADR) 추이")
    st.dataframe(adr_table.pivot(index='arrival_date_month', columns='hotel', values='평균단가(ADR)'), use_container_width=True)
    
    show_analysis(
        "비수기 시즌의 ADR 하락 폭이 커서 고정비 감당이 어려운 수익 구조.",
        "시즌별 수요 예측 실패로 인한 과도한 가격 할인 경쟁.",
        "AI 기반 동적 가격 책정(Dynamic Pricing) 도입으로 가동률과 단가의 최적점 도출.",
        "연간 평균 ADR 10% 상승 및 비수기 매출 방어."
    )

# --- Tab 3: 리드 타임 ---
with tabs[2]:
    st.header("⏰ 리드 타임과 예약 불확실성")
    df['lead_time_bin'] = pd.cut(df['lead_time'], bins=[0, 30, 90, 180, 360, 1000], labels=['0-30일', '31-90일', '91-180일', '181-360일', '360일+'])
    lt_table = df.groupby('lead_time_bin', observed=True).agg(
        예약건수=('is_canceled', 'count'),
        취소율=('is_canceled', 'mean')
    ).reset_index()
    lt_table['취소율(%)'] = (lt_table['취소율'] * 100).round(1)
    
    st.subheader("📊 [데이터] 리드 타임 구간별 취소 위험도")
    st.table(lt_table)
    
    show_analysis(
        "리드 타임이 90일을 초과하는 시점부터 취소율이 40% 이상으로 급격히 상승함.",
        "예약 시점이 멀수록 고객의 변심 및 일정 변경 리스크가 기하급수적으로 증가.",
        "리드 타임 90일 이상 예약 고객 대상 '재확정(Re-confirm)' 시스템 및 얼리버드 전용 혜택 강화.",
        "장기 리드 타임 예약의 취소율 20% 감소 및 안정적인 객실 재고 확보."
    )

# --- Tab 4: 예약 채널 ---
with tabs[3]:
    st.header("🌐 예약 채널별 수익 효율성")
    ch_table = df.groupby('market_segment').agg(
        예약건수=('is_canceled', 'count'),
        취소건수=('is_canceled', 'sum'),
        평균ADR=('adr', 'mean'),
        취소율=('is_canceled', 'mean')
    ).reset_index()
    ch_table['평균ADR'] = ch_table['평균ADR'].round(1)
    ch_table['취소율(%)'] = (ch_table['취소율'] * 100).round(1)
    
    st.subheader("📊 [데이터] 채널별 수익성, 취소 건수 및 리스크 지표")
    # 취소건수 기준으로 내림차순 정렬하여 가장 큰 손실 채널 우선 표시
    st.table(ch_table.sort_values('취소건수', ascending=False))
    
    show_analysis(
        "Groups 채널은 취소율(61%)도 높지만, 실제 취소된 예약 건수가 압도적으로 많아 객실 재고 관리에 치명적임.",
        "단체 예약의 특성상 'All-or-Nothing' 식의 전량 취소가 빈번하며, 보증금 정책의 부재로 인해 취소 장벽이 낮음.",
        "취소 건수가 많은 상위 채널(Groups, Online TA)에 대해 예약 확정 마감일(Cut-off)을 엄격히 적용.",
        "허수 예약의 사전 제거를 통한 공실률 10% 개선 및 성수기 객실 판매 기회비용 확보."
    )

# --- Tab 5: 숙박 기간 ---
with tabs[4]:
    st.header("📅 숙박 기간(Duration)과 운영 효율")
    df['stay_bin'] = pd.cut(df['total_nights'], bins=[0, 2, 4, 7, 14, 100], labels=['1-2박', '3-4박', '5-7박', '8-14박', '15박+'])
    st_table = df.groupby('stay_bin', observed=True).agg(
        예약건수=('is_canceled', 'count'),
        평균수익=('revenue', 'mean'),
        취소율=('is_canceled', 'mean')
    ).reset_index()
    st_table['평균수익'] = st_table['평균수익'].round(1)
    st_table['취소율(%)'] = (st_table['취소율'] * 100).round(1)
    
    st.subheader("📊 [데이터] 숙박 기간별 건당 수익성 비교")
    st.table(st_table)
    
    show_analysis(
        "단기 숙박(1-2박) 위주의 예약 구조로 인해 체크인/아웃 업무 부하 및 세탁비 등 운영비용 과다.",
        "장기 투숙 고객을 유인할 수 있는 연박 할인 또는 부가 서비스 패키지 부족.",
        "3박 이상 투숙 시 조식 무료 또는 F&B 크레딧 제공 등 'Long-stay' 프로모션 강화.",
        "평균 숙박 기간 0.5일 연장 및 턴오버(객실 정비) 비용 10% 절감."
    )
