"""
Baseline History Page

기준선 히스토리 타임라인 페이지
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd


def render_baseline_history_page(baseline_manager, db):
    """Render baseline history timeline page"""
    st.title("📊 기준선 히스토리")
    
    st.write("화장실 기준 무게(패드 + 모래)의 변화 이력을 확인합니다.")
    
    # Get baseline history
    history = baseline_manager.get_baseline_history(limit=None)
    
    if not history:
        st.info("아직 기준선 변경 이력이 없습니다.")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        date_range = st.selectbox(
            "기간",
            ["24시간", "7일", "30일", "전체"],
            index=1
        )
    
    with col2:
        reason_filter = st.multiselect(
            "변경 이유 필터",
            ["stable", "urination", "defecation", "cleaning", "litter_refill", "user_reset", "auto_adjust"],
            default=[]
        )
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == "24시간":
        start_date = end_date - timedelta(hours=24)
    elif date_range == "7일":
        start_date = end_date - timedelta(days=7)
    elif date_range == "30일":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = None
    
    # Filter history
    filtered_history = []
    for h in history:
        # Date filter
        if start_date and h.timestamp < start_date:
            continue
        
        # Reason filter
        if reason_filter and h.reason not in reason_filter:
            continue
        
        filtered_history.append(h)
    
    if not filtered_history:
        st.info("선택한 필터에 해당하는 기록이 없습니다.")
        return
    
    # Timeline visualization
    st.subheader("📈 기준선 변화 타임라인")
    
    fig = go.Figure()
    
    # Extract data
    timestamps = [h.timestamp for h in filtered_history]
    weights = [h.baseline_weight for h in filtered_history]
    reasons = [h.reason for h in filtered_history]
    changes = [h.change_amount for h in filtered_history]
    
    # Color mapping for reasons
    reason_colors = {
        'stable': '#2ca02c',  # green
        'urination': '#ffff00',  # yellow
        'defecation': '#ff7f0e',  # orange
        'cleaning': '#1f77b4',  # blue
        'litter_refill': '#2ca02c',  # green
        'user_reset': '#9467bd',  # purple
        'auto_adjust': '#d62728'  # red
    }
    
    reason_names = {
        'stable': '안정',
        'urination': '배뇨',
        'defecation': '배변',
        'cleaning': '청소',
        'litter_refill': '모래 보충',
        'user_reset': '사용자 재설정',
        'auto_adjust': '자동 조정'
    }
    
    # Add step line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=weights,
        mode='lines+markers',
        name='기준선',
        line=dict(color='#1f77b4', width=2, shape='hv'),
        marker=dict(
            size=10,
            color=[reason_colors.get(r, '#gray') for r in reasons],
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>기준선 변경</b><br>' +
                     '시간: %{x}<br>' +
                     '무게: %{y:.3f}kg<br>' +
                     '<extra></extra>',
        customdata=list(zip(reasons, changes)),
        text=[f"{reason_names.get(r, r)}<br>{c:+.3f}kg" for r, c in zip(reasons, changes)]
    ))
    
    fig.update_layout(
        xaxis_title="시간",
        yaxis_title="기준선 무게 (kg)",
        hovermode='closest',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    st.markdown("**변경 이유 범례:**")
    legend_cols = st.columns(4)
    
    legend_items = [
        ("🟢 보충", "litter_refill"),
        ("🔵 청소", "cleaning"),
        ("🟡 배뇨", "urination"),
        ("🟠 배변", "defecation")
    ]
    
    for idx, (label, reason) in enumerate(legend_items):
        with legend_cols[idx]:
            st.write(label)
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_24h = sum(h.baseline_weight for h in filtered_history if h.timestamp > end_date - timedelta(hours=24)) / max(1, len([h for h in filtered_history if h.timestamp > end_date - timedelta(hours=24)]))
        st.metric("평균 기준선 (24시간)", f"{avg_24h:.3f}kg")
    
    with col2:
        refills = len([h for h in filtered_history if h.reason == 'litter_refill'])
        st.metric("총 보충 횟수", refills)
    
    with col3:
        cleanings = len([h for h in filtered_history if h.reason == 'cleaning'])
        st.metric("총 청소 횟수", cleanings)
    
    with col4:
        if filtered_history:
            current = filtered_history[-1].baseline_weight
            oldest = filtered_history[0].baseline_weight
            stability = 100 - (abs(current - oldest) / oldest * 100)
            st.metric("기준선 안정성", f"{stability:.1f}%")
    
    # Data table
    st.markdown("---")
    st.subheader("📋 변경 이력")
    
    table_data = []
    for h in reversed(filtered_history):
        table_data.append({
            '시간': h.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            '기준선': f"{h.baseline_weight:.3f}kg",
            '이전 무게': f"{h.previous_weight:.3f}kg",
            '변경량': f"{h.change_amount:+.3f}kg",
            '이유': reason_names.get(h.reason, h.reason),
            '데이터 소스': '시뮬레이션' if h.data_source.value == 'simulation' else '센서'
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export button
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV로 내보내기",
        data=csv,
        file_name=f"baseline_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
