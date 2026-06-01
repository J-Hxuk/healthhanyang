"""
Demo Mode Page - Real-time Weight Visualization

시제품 시연용 실시간 무게 감지 페이지
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
from collections import deque

from src.data.schema import EventType


def add_noise(value: float, noise_range: float = 0.005) -> float:
    """
    Add realistic sensor noise to weight value
    
    Args:
        value: Base weight value
        noise_range: Noise range in kg (default: ±5g)
    
    Returns:
        Weight with noise added
    """
    return value + random.uniform(-noise_range, noise_range)


def render_demo_mode_page(db, event_detector, classifier, identifier, baseline_manager):
    """
    Render demo mode page with real-time weight visualization
    
    Args:
        db: Database instance
        event_detector: EventDetector instance
        classifier: EventClassifier instance
        identifier: CatIdentifier instance
        baseline_manager: BaselineManager instance
    """
    st.title("📊 실시간 그래프 - 무게 감지")
    
    st.info("""
    **📹 시제품 시연 가이드**
    
    1. **기준선 설정**: 빈 패드 + 화장실 무게 입력 후 '기준선 설정' 클릭
    2. **시연 시작**: '실시간 감지 시작' 버튼 클릭
    3. **물체 올리기**: 패드 위에 3kg 물체 올리기 (고양이 입실 시뮬레이션)
    4. **배변 시뮬레이션**: 500g 물체 추가 (배변)
    5. **물체 내리기**: 3kg 물체만 제거 (고양이 퇴실, 배변물 500g 남음)
    6. **감지 중지**: '감지 중지' 클릭 → 자동으로 300g 청소 시뮬레이션 후 10초간 빈 패드 표시
    7. **결과 확인**: 자동으로 이벤트 감지 및 분류
    
    💡 그래프에 실시간 무게 변화가 표시되며, ±5g 노이즈가 자동 반영됩니다.
    """)
    
    st.info(f"""
    💡 **노이즈 반영**: ±5g 센서 노이즈 자동 추가 (실제 센서처럼)
    """)
    
    st.info(f"""
    💡 **그래프에 실시간 무게 변화가 표시되며, ±5g 노이즈가 자동 반영됩니다.**
    """)
    
    # Initialize session state
    if 'demo_running' not in st.session_state:
        st.session_state.demo_running = False
    if 'demo_weights' not in st.session_state:
        st.session_state.demo_weights = deque(maxlen=100)  # Last 100 readings
    if 'demo_timestamps' not in st.session_state:
        st.session_state.demo_timestamps = deque(maxlen=100)
    if 'demo_baseline' not in st.session_state:
        st.session_state.demo_baseline = None
    if 'demo_event_started' not in st.session_state:
        st.session_state.demo_event_started = False
    if 'demo_last_weight' not in st.session_state:
        st.session_state.demo_last_weight = 0.0
    if 'demo_cleanup_mode' not in st.session_state:
        st.session_state.demo_cleanup_mode = False
    if 'demo_cleanup_counter' not in st.session_state:
        st.session_state.demo_cleanup_counter = 0
    if 'demo_cleanup_weight' not in st.session_state:
        st.session_state.demo_cleanup_weight = 0.0
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ 설정")
        
        baseline_weight = st.number_input(
            "기준 무게 (패드 + 화장실, kg)",
            min_value=1.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help="빈 패드와 화장실의 무게",
            key="demo_baseline_input"
        )
        
        if st.button("🔧 기준선 설정", use_container_width=True):
            st.session_state.demo_baseline = baseline_weight
            baseline_manager.update_baseline(baseline_weight, "user_reset")
            st.success(f"✅ 기준선 설정: {baseline_weight:.2f}kg")
            st.rerun()
        
        if st.session_state.demo_baseline:
            st.metric("현재 기준선", f"{st.session_state.demo_baseline:.2f}kg")
    
    with col2:
        st.subheader("🎮 제어")
        
        if not st.session_state.demo_running:
            if st.button("▶️ 실시간 감지 시작", 
                        use_container_width=True,
                        disabled=st.session_state.demo_baseline is None,
                        type="primary"):
                st.session_state.demo_running = True
                st.session_state.demo_weights.clear()
                st.session_state.demo_timestamps.clear()
                st.session_state.demo_event_started = False
                st.session_state.demo_last_weight = st.session_state.demo_baseline
                st.rerun()
        else:
            if st.button("⏹️ 감지 중지", use_container_width=True, type="secondary"):
                # Start cleanup mode instead of stopping immediately
                st.session_state.demo_cleanup_mode = True
                st.session_state.demo_cleanup_counter = 0
                # Remove 300g from current weight for cleanup simulation
                st.session_state.demo_cleanup_weight = st.session_state.demo_last_weight - 0.3
                st.rerun()
        
        if st.session_state.demo_running:
            if st.session_state.demo_cleanup_mode:
                st.warning(f"🧹 **청소 중** ({st.session_state.demo_cleanup_counter}/20)")
                st.caption("배변물 제거 후 빈 패드 상태 확인 중...")
            else:
                st.success("🟢 **실시간 감지 중**")
                st.caption("패드 위에 물체를 올리거나 내려보세요")
        else:
            st.info("⚪ **대기 중**")
    
    # Real-time chart
    st.markdown("---")
    st.subheader("📊 실시간 무게 그래프")
    
    chart_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Manual weight input for testing without actual sensor
    with st.expander("🔧 수동 무게 입력 (테스트용)"):
        st.caption("실제 센서 없이 테스트할 때 사용")
        manual_weight = st.number_input(
            "현재 무게 (kg)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.demo_last_weight,
            step=0.1,
            key="manual_weight_input"
        )
        if st.button("무게 업데이트", key="manual_update"):
            st.session_state.demo_last_weight = manual_weight
    
    # Real-time monitoring loop
    if st.session_state.demo_running:
        # Cleanup mode: simulate removing waste (300g) and showing empty pad for 10 seconds
        if st.session_state.demo_cleanup_mode:
            st.session_state.demo_cleanup_counter += 1
            
            # For first 10 readings (5 seconds): show cleanup weight (baseline + 200g remaining)
            if st.session_state.demo_cleanup_counter <= 10:
                current_weight = st.session_state.demo_cleanup_weight
                noisy_weight = add_noise(current_weight, noise_range=0.005)
                
                now = datetime.now()
                st.session_state.demo_weights.append(noisy_weight)
                st.session_state.demo_timestamps.append(now)
                
                # Add to event if still ongoing
                if st.session_state.demo_event_started and event_detector.current_event:
                    event_detector.current_event.weights.append(noisy_weight)
                    event_detector.current_event.timestamps.append(now)
                
                status_placeholder.warning(f"🧹 **청소 중** - 배변물 제거: {noisy_weight:.3f}kg")
            
            # For next 10 readings (5 seconds): show baseline (empty pad)
            elif st.session_state.demo_cleanup_counter <= 20:
                current_weight = st.session_state.demo_baseline
                noisy_weight = add_noise(current_weight, noise_range=0.005)
                
                now = datetime.now()
                st.session_state.demo_weights.append(noisy_weight)
                st.session_state.demo_timestamps.append(now)
                
                status_placeholder.success(f"✅ **빈 패드 확인 중** - 무게: {noisy_weight:.3f}kg (기준선: {st.session_state.demo_baseline:.3f}kg)")
            
            # After 20 readings (10 seconds total): finalize event and stop
            else:
                # Finalize event
                if st.session_state.demo_event_started and event_detector.current_event:
                    baseline = baseline_manager.current_baseline
                    event = event_detector._finalize_event(baseline, None)
                    event_detector.current_event = None
                    
                    # Classify event
                    event_type, confidence = classifier.classify(event)
                    event.event_type = event_type
                    event.confidence_score = confidence
                    
                    # Identify cat if it's a cat visit
                    if event_type == EventType.CAT_VISIT:
                        profiles = db.get_all_cat_profiles()
                        if profiles:
                            cat_id, id_confidence = identifier.identify(event, profiles)
                            event.cat_id = cat_id
                    
                    # Save event
                    db.save_event(event)
                    
                    status_placeholder.success(f"🎉 이벤트 기록 완료: {event_type.value}")
                    st.session_state.demo_event_started = False
                
                # Stop demo
                st.session_state.demo_running = False
                st.session_state.demo_cleanup_mode = False
                st.session_state.demo_cleanup_counter = 0
                st.rerun()
        
        # Normal monitoring mode
        else:
            # In a real scenario, this would read from the sensor
            # For demo, we'll use the manual input or simulate
            current_weight = st.session_state.demo_last_weight
            
            # Add noise to simulate real sensor
            noisy_weight = add_noise(current_weight, noise_range=0.005)
            
            # Record timestamp and weight
            now = datetime.now()
            st.session_state.demo_weights.append(noisy_weight)
            st.session_state.demo_timestamps.append(now)
            
            # Detect weight change (event detection)
            baseline = st.session_state.demo_baseline
            weight_diff = noisy_weight - baseline
            
            # Event detection logic
            if not st.session_state.demo_event_started and abs(weight_diff) > 0.5:
                # Event started
                st.session_state.demo_event_started = True
                
                import uuid
                from src.events.detector import OngoingEvent
                
                event_detector.current_event = OngoingEvent(
                    event_id=str(uuid.uuid4()),
                    device_id="PAD_001",
                    start_time=now,
                    baseline_before=baseline,
                    weights=[noisy_weight],
                    timestamps=[now]
                )
                
                status_placeholder.success(f"🟢 **이벤트 감지 시작** - 무게 변화: {weight_diff:+.3f}kg")
            
            elif st.session_state.demo_event_started and event_detector.current_event:
                # Event ongoing - add data point
                event_detector.current_event.weights.append(noisy_weight)
                event_detector.current_event.timestamps.append(now)
                
                duration = (now - event_detector.current_event.start_time).total_seconds()
                status_placeholder.info(f"⏱️ **이벤트 진행 중** - 지속시간: {duration:.1f}초 | 현재 무게: {noisy_weight:.3f}kg")
            
            else:
                status_placeholder.info(f"⚪ **대기 중** - 현재 무게: {noisy_weight:.3f}kg | 기준선: {baseline:.3f}kg")
        
        # Create chart
        if len(st.session_state.demo_weights) > 0:
            fig = go.Figure()
            
            # Weight line
            fig.add_trace(go.Scatter(
                x=list(st.session_state.demo_timestamps),
                y=list(st.session_state.demo_weights),
                mode='lines+markers',
                name='측정 무게',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))
            
            # Baseline line
            if st.session_state.demo_baseline:
                fig.add_hline(
                    y=st.session_state.demo_baseline,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="기준선",
                    annotation_position="right"
                )
            
            # Event detection threshold lines
            if st.session_state.demo_baseline:
                fig.add_hline(
                    y=st.session_state.demo_baseline + 0.5,
                    line_dash="dot",
                    line_color="orange",
                    annotation_text="감지 임계값 (+0.5kg)",
                    annotation_position="right"
                )
                fig.add_hline(
                    y=st.session_state.demo_baseline - 0.5,
                    line_dash="dot",
                    line_color="orange",
                    annotation_text="감지 임계값 (-0.5kg)",
                    annotation_position="right"
                )
            
            fig.update_layout(
                title="실시간 무게 변화",
                xaxis_title="시간",
                yaxis_title="무게 (kg)",
                height=400,
                hovermode='x unified',
                showlegend=True
            )
            
            chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Auto-refresh every 0.5 seconds
        time.sleep(0.5)
        st.rerun()
    
    else:
        # Show empty chart when not running
        if len(st.session_state.demo_weights) > 0:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=list(st.session_state.demo_timestamps),
                y=list(st.session_state.demo_weights),
                mode='lines+markers',
                name='측정 무게',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))
            
            if st.session_state.demo_baseline:
                fig.add_hline(
                    y=st.session_state.demo_baseline,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="기준선"
                )
            
            fig.update_layout(
                title="무게 변화 기록",
                xaxis_title="시간",
                yaxis_title="무게 (kg)",
                height=400,
                hovermode='x unified'
            )
            
            chart_placeholder.plotly_chart(fig, use_container_width=True)
        else:
            chart_placeholder.info("실시간 감지를 시작하면 그래프가 표시됩니다")
    
    # Recent events
    st.markdown("---")
    st.subheader("📋 최근 감지된 이벤트")
    
    recent_events = db.get_events()[:5]
    
    if recent_events:
        for event in recent_events:
            profiles = db.get_all_cat_profiles()
            cat_display = "알 수 없음"
            if event.cat_id:
                for profile in profiles:
                    if profile.cat_id == event.cat_id:
                        cat_display = f"{profile.name}"
                        break
            
            with st.expander(f"{event.event_type.value} - {event.start_time.strftime('%H:%M:%S')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("지속시간", f"{event.duration:.1f}초")
                    st.metric("체중 증가", f"{event.weight_gain:.3f}kg")
                with col2:
                    st.metric("고양이", cat_display)
                    st.metric("평균 무게", f"{event.avg_weight:.3f}kg")
                with col3:
                    st.metric("신뢰도", f"{event.confidence_score:.2%}")
                    st.metric("안정성", f"{event.stability_score:.2f}")
    else:
        st.info("아직 감지된 이벤트가 없습니다")
