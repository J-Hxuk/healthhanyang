"""
Weight Tracking Page

체중 추적 및 시각화 페이지
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd


def render_weight_tracking_page(db, weight_tracker):
    """Render weight tracking page"""
    st.title("📊 체중 추적")
    
    # Get all cat profiles
    profiles = db.get_all_cat_profiles()
    
    if not profiles:
        st.warning("⚠️ 등록된 고양이가 없습니다. 먼저 고양이 프로필을 추가하세요.")
        return
    
    # Cat selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_cats = st.multiselect(
            "고양이 선택",
            options=[p.name for p in profiles],
            default=[profiles[0].name] if profiles else []
        )
    
    with col2:
        date_range = st.selectbox(
            "기간",
            ["7일", "30일", "90일", "전체"],
            index=0
        )
    
    if not selected_cats:
        st.info("표시할 고양이를 선택하세요.")
        return
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == "7일":
        start_date = end_date - timedelta(days=7)
    elif date_range == "30일":
        start_date = end_date - timedelta(days=30)
    elif date_range == "90일":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = None
    
    # Get weight history for selected cats
    cat_data = {}
    for profile in profiles:
        if profile.name in selected_cats:
            measurements = weight_tracker.get_weight_history(
                profile.cat_id,
                start_date=start_date,
                end_date=end_date
            )
            if measurements:
                cat_data[profile.name] = {
                    'profile': profile,
                    'measurements': measurements
                }
    
    if not cat_data:
        st.info("선택한 기간에 체중 측정 데이터가 없습니다.")
        return
    
    # Create weight chart
    st.subheader("📈 체중 변화 추이")
    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for idx, (cat_name, data) in enumerate(cat_data.items()):
        profile = data['profile']
        measurements = data['measurements']
        
        # Extract data
        timestamps = [m.timestamp for m in measurements]
        weights = [m.measured_weight for m in measurements]
        
        # Add line trace
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=weights,
            mode='lines+markers',
            name=cat_name,
            line=dict(color=colors[idx % len(colors)], width=2),
            marker=dict(size=8),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '시간: %{x}<br>' +
                         '체중: %{y:.2f}kg<br>' +
                         '<extra></extra>'
        ))
        
        # Add profile weight reference line
        fig.add_trace(go.Scatter(
            x=[timestamps[0], timestamps[-1]],
            y=[profile.baseline_weight, profile.baseline_weight],
            mode='lines',
            name=f'{cat_name} 기준 체중',
            line=dict(color=colors[idx % len(colors)], width=1, dash='dash'),
            showlegend=True,
            hovertemplate=f'<b>{cat_name} 기준 체중</b><br>' +
                         f'{profile.baseline_weight:.2f}kg<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="체중 (kg)",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Weight statistics
    st.markdown("---")
    st.subheader("📊 체중 통계")
    
    stat_cols = st.columns(len(cat_data))
    
    for idx, (cat_name, data) in enumerate(cat_data.items()):
        with stat_cols[idx]:
            profile = data['profile']
            measurements = data['measurements']
            
            st.write(f"**{cat_name}**")
            
            if len(measurements) >= 2:
                latest = measurements[-1]
                earliest = measurements[0]
                
                change = latest.measured_weight - earliest.measured_weight
                change_pct = (change / earliest.measured_weight) * 100
                
                st.metric(
                    "최근 체중",
                    f"{latest.measured_weight:.2f}kg",
                    f"{change:+.2f}kg ({change_pct:+.1f}%)"
                )
                
                # Calculate 7-day change rate
                change_rate_7d = weight_tracker.calculate_weight_change_rate(profile.cat_id, 7)
                if change_rate_7d is not None:
                    st.metric(
                        "7일 변화율",
                        f"{change_rate_7d:+.1f}%"
                    )
            else:
                latest = measurements[0]
                st.metric("최근 체중", f"{latest.measured_weight:.2f}kg")
    
    # Data table
    st.markdown("---")
    st.subheader("📋 체중 측정 기록")
    
    # Combine all measurements into a table
    table_data = []
    for cat_name, data in cat_data.items():
        for m in data['measurements']:
            table_data.append({
                '날짜': m.timestamp.strftime('%Y-%m-%d %H:%M'),
                '고양이': cat_name,
                '측정 체중': f"{m.measured_weight:.2f}kg",
                '기준 체중': f"{m.profile_weight:.2f}kg",
                '차이': f"{m.weight_difference:+.2f}kg",
                '데이터 소스': '시뮬레이션' if m.data_source.value == 'simulation' else '센서'
            })
    
    if table_data:
        df = pd.DataFrame(table_data)
        df = df.sort_values('날짜', ascending=False)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export button
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV로 내보내기",
            data=csv,
            file_name=f"weight_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
