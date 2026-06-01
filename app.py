"""
Cat Health Copilot - Main Streamlit Application

ESP32 기반 스마트 화장실 모니터링 시스템
"""

import streamlit as st
import json
from datetime import datetime, timedelta
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.data.receiver import SensorDataReceiver
from src.data.schema import CatProfile, EventType, DataSourceMode, SimulationScenario, SimulationConfig
from src.preprocessing.filter import SensorPreprocessor
from src.preprocessing.baseline import BaselineManager
from src.events.detector import EventDetector
from src.events.classifier import EventClassifier
from src.identification.cat_identifier import CatIdentifier
from src.storage.database import Database
from src.analysis.health_monitor import HealthMonitor
from src.tracking.weight_tracker import WeightTracker
from src.alerts.alert_generator import AlertGenerator
from src.simulation import (
    DataSourceInterface, SimulationGenerator, BaselineSimulator, LongTermSimulator
)
from src.ui.weight_tracking_page import render_weight_tracking_page
from src.ui.long_term_simulation_page import render_long_term_simulation_page
from src.ui.baseline_history_page import render_baseline_history_page
from config.config import get_config

# Page configuration
st.set_page_config(
    page_title="고양이 건강 코파일럿",
    page_icon="🐱",
    layout="wide"
)

def _simulate_time_passing(seconds: int, cat_weight: float, baseline_weight: float):
    """
    Simulate time passing while cat is on pad by adding weight data points
    
    Args:
        seconds: Number of seconds to simulate
        cat_weight: Weight of the cat
        baseline_weight: Baseline weight
    """
    if st.session_state.event_detector.current_event is None:
        st.error("진행 중인 이벤트가 없습니다!")
        return
    
    # Add weight data points to the ongoing event
    entry_time = st.session_state.sim_entry_time
    current_virtual_seconds = st.session_state.sim_virtual_seconds
    total_weight = baseline_weight + cat_weight
    
    for i in range(seconds):
        virtual_time = entry_time + timedelta(seconds=current_virtual_seconds + i + 1)
        st.session_state.event_detector.current_event.weights.append(total_weight)
        st.session_state.event_detector.current_event.timestamps.append(virtual_time)
    
    # Update accumulated virtual seconds
    st.session_state.sim_virtual_seconds += seconds

def render_simulator(show_chart=True):
    """Render the cat visit simulator UI"""
    
    # Initialize simulation state
    if 'sim_weight' not in st.session_state:
        st.session_state.sim_weight = 4.5
    if 'sim_baseline_weight' not in st.session_state:
        st.session_state.sim_baseline_weight = 2.0
    if 'sim_baseline_set' not in st.session_state:
        st.session_state.sim_baseline_set = False
    if 'sim_cat_on_pad' not in st.session_state:
        st.session_state.sim_cat_on_pad = False
    if 'sim_entry_time' not in st.session_state:
        st.session_state.sim_entry_time = None
    if 'sim_virtual_seconds' not in st.session_state:
        st.session_state.sim_virtual_seconds = 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ 시뮬레이션 설정")
        
        # Cat weight setting
        sim_weight = st.number_input(
            "고양이 체중 (kg)",
            min_value=2.0,
            max_value=10.0,
            value=st.session_state.sim_weight,
            step=0.1,
            help="시뮬레이션할 고양이의 체중을 설정하세요",
            key="sim_weight_input"
        )
        st.session_state.sim_weight = sim_weight
        
        # Baseline weight (pad + litter)
        baseline_weight = st.number_input(
            "기준 무게 (패드 + 모래, kg)",
            min_value=1.0,
            max_value=5.0,
            value=st.session_state.sim_baseline_weight,
            step=0.1,
            help="빈 패드와 모래의 무게",
            key="sim_baseline_input"
        )
        st.session_state.sim_baseline_weight = baseline_weight
        
        st.markdown("---")
        
        # Set baseline button
        if st.button("🔧 기준선 설정", use_container_width=True, key="set_baseline_btn"):
            # Directly set baseline without complex processing
            st.session_state.baseline_manager.update_baseline(baseline_weight, "user_reset")
            st.session_state.sim_baseline_set = True
            st.success(f"✅ 기준선 설정 완료: {baseline_weight:.2f}kg")
            st.rerun()
    
    with col2:
        st.subheader("🎯 방문 시뮬레이션")
        
        if st.session_state.sim_baseline_set:
            st.success("✅ 기준선 설정됨")
            baseline_value = st.session_state.baseline_manager.current_baseline
            if baseline_value is not None:
                st.metric("현재 기준선", f"{baseline_value:.2f}kg")
            else:
                st.metric("현재 기준선", "설정 필요")
        else:
            st.warning("⚠️ 먼저 기준선을 설정하세요")
        
        # Show current status
        if st.session_state.sim_cat_on_pad:
            st.success(f"🟢 **무게 감지 중**")
            st.metric("가상 경과 시간", f"{st.session_state.sim_virtual_seconds}초")
        else:
            st.info("⚪ **대기 중 (무게 감지 안됨)**")
        
        st.markdown("---")
        
        # Control buttons
        col_entry, col_exit = st.columns(2)
        
        with col_entry:
            if st.button("⚖️ 무게 감지됨", 
                        disabled=st.session_state.sim_cat_on_pad or not st.session_state.sim_baseline_set,
                        use_container_width=True,
                        key="btn_cat_entry"):
                # Record entry - FORCE START EVENT
                entry_time = datetime.now()
                total_weight = baseline_weight + sim_weight
                
                # Force start event by creating it directly
                import uuid
                from src.events.detector import OngoingEvent
                
                st.session_state.event_detector.current_event = OngoingEvent(
                    event_id=str(uuid.uuid4()),
                    device_id="PAD_001",
                    start_time=entry_time,
                    baseline_before=st.session_state.baseline_manager.current_baseline,
                    weights=[total_weight],
                    timestamps=[entry_time]
                )
                
                st.session_state.sim_cat_on_pad = True
                st.session_state.sim_entry_time = entry_time
                st.session_state.sim_virtual_seconds = 0
                st.success(f"✅ 무게 감지 시작: {total_weight:.2f}kg")
                st.rerun()
        
        with col_exit:
            if st.button("⚖️ 무게 감지 안됨", 
                        disabled=not st.session_state.sim_cat_on_pad,
                        use_container_width=True,
                        key="btn_cat_exit"):
                # FORCE END EVENT
                duration = st.session_state.sim_virtual_seconds
                
                # Check if event exists
                if st.session_state.event_detector.current_event is None:
                    st.error("⚠️ 진행 중인 이벤트가 없습니다!")
                    st.session_state.sim_cat_on_pad = False
                    st.rerun()
                    return
                
                # Store weights before finalizing (for statistics)
                event_weights = list(st.session_state.event_detector.current_event.weights)
                
                # Force finalize the event
                baseline = st.session_state.baseline_manager.current_baseline
                event = st.session_state.event_detector._finalize_event(baseline, None)
                st.session_state.event_detector.current_event = None
                
                # Classify event
                event_type, confidence = st.session_state.classifier.classify(event)
                event.event_type = event_type
                event.confidence_score = confidence
                
                # Identify cat if it's a cat visit
                cat_name = "알 수 없음"
                id_confidence = 0.0
                measured_weight = 0.0
                
                if event_type == EventType.CAT_VISIT:
                    profiles = st.session_state.db.get_all_cat_profiles()
                    if profiles:
                        cat_id, id_confidence = st.session_state.identifier.identify(event, profiles)
                        event.cat_id = cat_id
                        
                        # Calculate measured cat weight
                        measured_weight = event.avg_weight - event.baseline_before
                        
                        # Find cat name
                        if cat_id:
                            for profile in profiles:
                                if profile.cat_id == cat_id:
                                    cat_name = profile.name
                                    break
                
                # Save event
                st.session_state.db.save_event(event)
                
                st.success(f"🎉 이벤트 기록 완료!")
                
                # Show detailed results
                result_text = f"**이벤트 유형**: {event_type.value}\n\n"
                result_text += f"**지속시간**: {duration}초\n\n"
                result_text += f"**평균 무게**: {event.avg_weight:.3f}kg\n\n"
                
                if event_weights and len(event_weights) > 0:
                    min_weight = min(event_weights)
                    max_weight = max(event_weights)
                    weight_range = max_weight - min_weight
                    result_text += f"**무게 범위**: {min_weight:.3f}kg ~ {max_weight:.3f}kg (변동: {weight_range:.3f}kg)\n\n"
                
                result_text += f"**체중 증가**: {event.weight_gain:.3f}kg\n\n"
                result_text += f"**안정성 점수**: {event.stability_score:.2f}\n\n"
                result_text += f"**기준선**: {baseline:.3f}kg\n\n"
                
                if event_type == EventType.CAT_VISIT:
                    result_text += f"---\n\n"
                    result_text += f"**🐱 고양이 식별 결과**\n\n"
                    result_text += f"**측정된 고양이 체중**: {measured_weight:.3f}kg\n\n"
                    result_text += f"**식별된 고양이**: {cat_name}\n\n"
                    result_text += f"**식별 신뢰도**: {id_confidence:.2%}\n\n"
                    
                    if id_confidence > 0.8:
                        result_text += f"✅ 높은 신뢰도 - 거의 확실합니다"
                    elif id_confidence > 0.5:
                        result_text += f"🟡 중간 신뢰도 - 가능성이 높습니다"
                    elif id_confidence > 0:
                        result_text += f"⚠️ 낮은 신뢰도 - 불확실합니다"
                    else:
                        result_text += f"❌ 등록된 고양이와 체중 차이가 큽니다"
                
                st.info(result_text)
                
                st.session_state.sim_cat_on_pad = False
                st.session_state.sim_entry_time = None
                st.session_state.sim_virtual_seconds = 0
                
                # Force refresh to update dashboard
                import time
                time.sleep(0.5)
                st.rerun()
        
        # Time simulation buttons (only when cat is on pad)
        if st.session_state.sim_cat_on_pad:
            st.markdown("---")
            st.write("**⏱️ 시간 경과 시뮬레이션:**")
            st.caption("고양이가 올라가 있는 동안 일정한 무게로 데이터를 기록합니다")
            
            col_10s, col_30s, col_60s = st.columns(3)
            
            with col_10s:
                if st.button("+ 10초", use_container_width=True, key="btn_add_10s"):
                    _simulate_time_passing(10, sim_weight, baseline_weight)
                    st.success("10초 경과 시뮬레이션 완료")
                    st.rerun()
            
            with col_30s:
                if st.button("+ 30초", use_container_width=True, key="btn_add_30s"):
                    _simulate_time_passing(30, sim_weight, baseline_weight)
                    st.success("30초 경과 시뮬레이션 완료")
                    st.rerun()
            
            with col_60s:
                if st.button("+ 60초", use_container_width=True, key="btn_add_60s"):
                    _simulate_time_passing(60, sim_weight, baseline_weight)
                    st.success("60초 경과 시뮬레이션 완료")
                    st.rerun()
            
            # Weight adjustment buttons
            st.markdown("---")
            st.write("**⚖️ 무게 조정:**")
            st.caption("고양이가 움직이거나 자세를 바꿀 때 발생하는 무게 변화를 시뮬레이션합니다")
            
            col_add, col_sub = st.columns(2)
            
            with col_add:
                weight_increase = st.number_input(
                    "무게 증가 (kg)",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.3,
                    step=0.1,
                    key="weight_increase_input"
                )
                if st.button("➕ 무게 추가", use_container_width=True, key="btn_add_weight"):
                    if st.session_state.event_detector.current_event:
                        # Add a heavier weight data point
                        virtual_time = st.session_state.sim_entry_time + timedelta(seconds=st.session_state.sim_virtual_seconds + 1)
                        new_weight = baseline_weight + sim_weight + weight_increase
                        st.session_state.event_detector.current_event.weights.append(new_weight)
                        st.session_state.event_detector.current_event.timestamps.append(virtual_time)
                        st.session_state.sim_virtual_seconds += 1
                        st.success(f"무게 추가: +{weight_increase}kg (총 {new_weight:.2f}kg)")
                        st.rerun()
            
            with col_sub:
                weight_decrease = st.number_input(
                    "무게 감소 (kg)",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.3,
                    step=0.1,
                    key="weight_decrease_input"
                )
                if st.button("➖ 무게 감소", use_container_width=True, key="btn_sub_weight"):
                    if st.session_state.event_detector.current_event:
                        # Add a lighter weight data point
                        virtual_time = st.session_state.sim_entry_time + timedelta(seconds=st.session_state.sim_virtual_seconds + 1)
                        new_weight = max(baseline_weight, baseline_weight + sim_weight - weight_decrease)
                        st.session_state.event_detector.current_event.weights.append(new_weight)
                        st.session_state.event_detector.current_event.timestamps.append(virtual_time)
                        st.session_state.sim_virtual_seconds += 1
                        st.success(f"무게 감소: -{weight_decrease}kg (총 {new_weight:.2f}kg)")
                        st.rerun()

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'receiver' not in st.session_state:
    st.session_state.receiver = SensorDataReceiver()

if 'preprocessor' not in st.session_state:
    st.session_state.preprocessor = SensorPreprocessor()

if 'baseline_manager' not in st.session_state:
    st.session_state.baseline_manager = BaselineManager("PAD_001", st.session_state.db, DataSourceMode.SIMULATION)

if 'event_detector' not in st.session_state:
    st.session_state.event_detector = EventDetector("PAD_001", DataSourceMode.SIMULATION)

if 'classifier' not in st.session_state:
    st.session_state.classifier = EventClassifier()

if 'identifier' not in st.session_state:
    st.session_state.identifier = CatIdentifier()

if 'health_monitor' not in st.session_state:
    st.session_state.health_monitor = HealthMonitor()

if 'weight_tracker' not in st.session_state:
    st.session_state.weight_tracker = WeightTracker(st.session_state.db)

if 'alert_generator' not in st.session_state:
    st.session_state.alert_generator = AlertGenerator(st.session_state.db, st.session_state.weight_tracker)

if 'simulation_generator' not in st.session_state:
    st.session_state.simulation_generator = SimulationGenerator("PAD_001")

if 'baseline_simulator' not in st.session_state:
    st.session_state.baseline_simulator = BaselineSimulator(st.session_state.baseline_manager)

if 'long_term_simulator' not in st.session_state:
    st.session_state.long_term_simulator = LongTermSimulator(
        st.session_state.db,
        st.session_state.baseline_simulator,
        st.session_state.simulation_generator
    )

if 'data_source_interface' not in st.session_state:
    st.session_state.data_source_interface = DataSourceInterface()
    st.session_state.data_source_interface.set_mode(DataSourceMode.SIMULATION)
    st.session_state.data_source_interface.set_simulation_generator(st.session_state.simulation_generator)

if 'config' not in st.session_state:
    st.session_state.config = get_config()

# Sidebar navigation
st.sidebar.title("🐱 고양이 건강 코파일럿")

# Admin mode toggle
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

with st.sidebar.expander("🔐 관리자 모드"):
    if not st.session_state.admin_mode:
        admin_password = st.text_input("비밀번호", type="password", key="admin_pw")
        if st.button("로그인", key="admin_login"):
            if admin_password == "admin1234":  # 비밀번호 설정
                st.session_state.admin_mode = True
                st.success("관리자 모드 활성화")
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    else:
        st.success("✅ 관리자 모드 활성화됨")
        if st.button("로그아웃", key="admin_logout"):
            st.session_state.admin_mode = False
            st.rerun()

# Data source indicator (only in admin mode)
if st.session_state.admin_mode:
    data_source = st.session_state.data_source_interface.mode
    if data_source == DataSourceMode.SIMULATION:
        st.sidebar.info("📊 시뮬레이션 모드")
    else:
        conn_status = st.session_state.data_source_interface.get_connection_status()
        if conn_status.value == "connected":
            st.sidebar.success("📡 센서 모드 (연결됨)")
        elif conn_status.value == "disconnected":
            st.sidebar.warning("📡 센서 모드 (연결 끊김)")
        else:
            st.sidebar.error("📡 센서 모드 (오류)")

# Menu items - show simulation pages only in admin mode
menu_items = ["홈 대시보드", "체중 추적", "기준선 히스토리", 
              "이벤트 타임라인", "고양이 프로필", "설정"]

if st.session_state.admin_mode:
    menu_items.insert(2, "장기 시뮬레이션")
    menu_items.insert(4, "실시간 시뮬레이션")

page = st.sidebar.radio("메뉴", menu_items)

# Main content based on selected page
if page == "홈 대시보드":
    st.title("🏠 홈 대시보드")
    
    # Get all profiles for cat-specific stats
    profiles = st.session_state.db.get_all_cat_profiles()
    
    # Overall stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("현재 기준선", 
                 f"{st.session_state.baseline_manager.current_baseline or 0:.2f} kg")
    
    with col2:
        # Count today's events
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_events = st.session_state.db.get_events(
            start_date=today_start,
            event_type=EventType.CAT_VISIT
        )
        st.metric("오늘 총 방문 횟수", len(today_events))
    
    with col3:
        recent_alerts = st.session_state.db.get_recent_alerts(limit=5)
        st.metric("최근 알림", len(recent_alerts))
    
    # Cat-specific visit counts
    if profiles:
        st.markdown("---")
        st.subheader("🐱 고양이별 오늘 방문 횟수")
        
        cat_cols = st.columns(min(len(profiles), 4))  # Max 4 columns
        
        for idx, profile in enumerate(profiles):
            with cat_cols[idx % 4]:
                # Count today's visits for this cat
                cat_today_events = st.session_state.db.get_events(
                    cat_id=profile.cat_id,
                    start_date=today_start,
                    event_type=EventType.CAT_VISIT
                )
                st.metric(
                    f"{profile.name}",
                    f"{len(cat_today_events)}회",
                    help=f"기준 체중: {profile.baseline_weight}kg"
                )
        
        # Unknown cats
        unknown_events = [e for e in today_events if e.cat_id is None]
        if unknown_events:
            with cat_cols[len(profiles) % 4]:
                st.metric(
                    "알 수 없음",
                    f"{len(unknown_events)}회",
                    help="식별되지 않은 방문"
                )
        
        # Health Alerts Section
        st.markdown("---")
        st.subheader("🏥 건강 알림")
        
        # Check each cat for health issues
        alerts = []
        for profile in profiles:
            # Get today's events for this cat
            cat_today_events = st.session_state.db.get_events(
                cat_id=profile.cat_id,
                start_date=today_start,
                event_type=EventType.CAT_VISIT
            )
            
            # Get recent events (last 7 days) for baseline
            week_ago = today_start - timedelta(days=7)
            cat_recent_events = st.session_state.db.get_events(
                cat_id=profile.cat_id,
                start_date=week_ago,
                end_date=today_start,
                event_type=EventType.CAT_VISIT
            )
            
            # Check for frequent urination
            alert = st.session_state.health_monitor.check_frequent_urination(
                profile, cat_today_events, cat_recent_events
            )
            
            if alert:
                alerts.append(alert)
        
        # Display alerts
        if alerts:
            for alert in alerts:
                if alert.severity == "critical":
                    st.error(f"🚨 **{alert.message}**")
                    with st.expander("상세 정보 보기"):
                        st.write(alert.details)
                elif alert.severity == "warning":
                    st.warning(f"⚠️ **{alert.message}**")
                    with st.expander("상세 정보 보기"):
                        st.write(alert.details)
                else:
                    st.info(f"ℹ️ **{alert.message}**")
                    with st.expander("상세 정보 보기"):
                        st.write(alert.details)
        else:
            st.success("✅ 모든 고양이가 정상 패턴을 보이고 있습니다")
    
    # Simulator on home dashboard (only in admin mode)
    if st.session_state.admin_mode:
        st.markdown("---")
        st.subheader("🎮 빠른 시뮬레이션")
        render_simulator(show_chart=False)
    
    # Recent events
    st.markdown("---")
    st.subheader("최근 이벤트")
    recent_events = st.session_state.db.get_events()[:10]
    
    if recent_events:
        for event in recent_events:
            # Get cat name if identified
            cat_display = "알 수 없음"
            if event.cat_id:
                for profile in profiles:
                    if profile.cat_id == event.cat_id:
                        cat_display = f"{profile.name} ({profile.baseline_weight}kg)"
                        break
            
            with st.expander(f"{event.event_type.value} - {event.start_time.strftime('%Y-%m-%d %H:%M:%S')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**지속시간:** {event.duration:.1f}초")
                    st.write(f"**체중 증가:** {event.weight_gain:.3f}kg")
                with col2:
                    st.write(f"**고양이:** {cat_display}")
                    st.write(f"**안정성:** {event.stability_score:.2f}")
                with col3:
                    st.write(f"**신뢰도:** {event.confidence_score:.2f}")
                    st.write(f"**기준선 변화:** {event.baseline_shift:.3f}kg")
    else:
        st.info("아직 기록된 이벤트가 없습니다. 위의 시뮬레이션을 사용해보세요.")

elif page == "이벤트 타임라인":
    st.title("📅 이벤트 타임라인")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        profiles = st.session_state.db.get_all_cat_profiles()
        cat_filter = st.selectbox(
            "고양이 필터",
            ["전체"] + [p.name for p in profiles]
        )
    
    with col2:
        event_type_filter = st.selectbox(
            "이벤트 유형 필터",
            ["전체", "cat_visit", "cleaning", "litter_refill", "noise", "unknown"]
        )
    
    with col3:
        days_back = st.number_input("표시할 일수", min_value=1, max_value=30, value=7)
    
    # Get filtered events
    start_date = datetime.now() - timedelta(days=days_back)
    
    cat_id = None
    if cat_filter != "전체":
        for p in profiles:
            if p.name == cat_filter:
                cat_id = p.cat_id
                break
    
    event_type = None if event_type_filter == "전체" else EventType(event_type_filter)
    
    events = st.session_state.db.get_events(
        cat_id=cat_id,
        start_date=start_date,
        event_type=event_type
    )
    
    st.write(f"**총 이벤트:** {len(events)}")
    
    # Display events
    for event in events:
        color = {
            EventType.CAT_VISIT: "🟢",
            EventType.CLEANING: "🔵",
            EventType.LITTER_REFILL: "🟡",
            EventType.NOISE: "⚪",
            EventType.UNKNOWN: "⚫"
        }.get(event.event_type, "⚫")
        
        # Get cat name if identified
        cat_display = "알 수 없음"
        if event.cat_id:
            for profile in profiles:
                if profile.cat_id == event.cat_id:
                    cat_display = f"{profile.name} ({profile.baseline_weight}kg)"
                    break
        
        st.write(f"{color} **{event.event_type.value}** - {event.start_time.strftime('%Y-%m-%d %H:%M:%S')} - 지속시간: {event.duration:.1f}초 - 고양이: {cat_display}")

elif page == "고양이 프로필":
    st.title("🐱 고양이 프로필")
    
    # Add new cat
    with st.expander("➕ 새 고양이 추가"):
        with st.form("add_cat_form"):
            name = st.text_input("이름")
            baseline_weight = st.number_input("기준 체중 (kg)", min_value=1.0, max_value=15.0, value=4.0, step=0.1)
            age = st.number_input("나이 (년)", min_value=0, max_value=25, value=3)
            sex = st.selectbox("성별", ["M", "F"])
            breed = st.text_input("품종 (선택사항)")
            notes = st.text_area("메모 (선택사항)")
            
            if st.form_submit_button("고양이 추가"):
                import uuid
                profile = CatProfile(
                    cat_id=str(uuid.uuid4()),
                    name=name,
                    baseline_weight=baseline_weight,
                    age=age,
                    sex=sex,
                    breed=breed if breed else None,
                    notes=notes if notes else None
                )
                st.session_state.db.save_cat_profile(profile)
                st.success(f"고양이 추가됨: {name}")
                st.rerun()
    
    # Display existing cats
    profiles = st.session_state.db.get_all_cat_profiles()
    
    if profiles:
        for profile in profiles:
            with st.expander(f"🐱 {profile.name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**체중:** {profile.baseline_weight}kg")
                    st.write(f"**나이:** {profile.age}세")
                    st.write(f"**성별:** {profile.sex}")
                with col2:
                    st.write(f"**품종:** {profile.breed or '없음'}")
                    st.write(f"**ID:** {profile.cat_id[:8]}...")
                if profile.notes:
                    st.write(f"**메모:** {profile.notes}")
                
                st.markdown("---")
                
                # Edit and Delete buttons
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button(f"✏️ 수정", key=f"edit_{profile.cat_id}", use_container_width=True):
                        st.session_state[f'editing_{profile.cat_id}'] = True
                        st.rerun()
                
                with col_delete:
                    if st.button(f"🗑️ 삭제", key=f"delete_{profile.cat_id}", type="secondary", use_container_width=True):
                        # Delete profile file
                        import os
                        profile_path = st.session_state.db.data_dir / "profiles" / f"{profile.cat_id}.json"
                        if profile_path.exists():
                            os.remove(profile_path)
                            st.success(f"{profile.name} 프로필이 삭제되었습니다")
                            st.rerun()
                        else:
                            st.error("프로필 파일을 찾을 수 없습니다")
                
                # Edit form (shown when edit button is clicked)
                if st.session_state.get(f'editing_{profile.cat_id}', False):
                    st.markdown("---")
                    st.subheader("프로필 수정")
                    
                    with st.form(f"edit_cat_form_{profile.cat_id}"):
                        edit_name = st.text_input("이름", value=profile.name)
                        edit_weight = st.number_input("기준 체중 (kg)", min_value=1.0, max_value=15.0, value=profile.baseline_weight, step=0.1)
                        edit_age = st.number_input("나이 (년)", min_value=0, max_value=25, value=profile.age)
                        edit_sex = st.selectbox("성별", ["M", "F"], index=0 if profile.sex == "M" else 1)
                        edit_breed = st.text_input("품종 (선택사항)", value=profile.breed or "")
                        edit_notes = st.text_area("메모 (선택사항)", value=profile.notes or "")
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            if st.form_submit_button("💾 저장", use_container_width=True):
                                # Update profile
                                profile.name = edit_name
                                profile.baseline_weight = edit_weight
                                profile.age = edit_age
                                profile.sex = edit_sex
                                profile.breed = edit_breed if edit_breed else None
                                profile.notes = edit_notes if edit_notes else None
                                profile.updated_at = datetime.now()
                                
                                st.session_state.db.save_cat_profile(profile)
                                st.session_state[f'editing_{profile.cat_id}'] = False
                                st.success(f"{edit_name} 프로필이 수정되었습니다")
                                st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ 취소", use_container_width=True):
                                st.session_state[f'editing_{profile.cat_id}'] = False
                                st.rerun()
    else:
        st.info("아직 고양이 프로필이 없습니다. 위에서 첫 번째 고양이를 추가하세요!")

elif page == "체중 추적":
    render_weight_tracking_page(st.session_state.db, st.session_state.weight_tracker)

elif page == "장기 시뮬레이션":
    render_long_term_simulation_page(st.session_state.db, st.session_state.long_term_simulator)

elif page == "기준선 히스토리":
    render_baseline_history_page(st.session_state.baseline_manager, st.session_state.db)

elif page == "실시간 시뮬레이션":
    st.title("🎮 실시간 시뮬레이션")
    
    st.write("실제 센서가 무게를 감지하는 것을 시뮬레이션합니다.")
    st.info("💡 **사용법**: 체중과 무게 변동 범위를 설정하고 '무게 감지됨' 버튼을 누르세요. 시간 버튼(+10초/+30초/+60초)으로 시간을 경과시킨 후 '무게 감지 안됨' 버튼을 누르면 프로그램이 자동으로 이벤트 유형을 판단합니다.")
    
    render_simulator(show_chart=False)

elif page == "설정":
    st.title("⚙️ 설정")
    
    st.subheader("임계값 설정")
    
    config = st.session_state.config
    
    with st.expander("전처리"):
        st.number_input("이동평균 윈도우", value=config.moving_average_window, key="ma_window")
        st.number_input("노이즈 임계값 (kg)", value=config.noise_threshold, key="noise_thresh")
    
    with st.expander("이벤트 감지"):
        st.number_input("체중 변화 임계값 (kg)", value=config.weight_change_threshold, key="weight_thresh")
        st.number_input("최소 이벤트 지속시간 (초)", value=config.min_event_duration, key="min_dur")
        st.number_input("최대 이벤트 지속시간 (초)", value=config.max_event_duration, key="max_dur")
    
    with st.expander("분류"):
        st.number_input("고양이 최소 체중 (kg)", value=config.cat_min_weight, key="cat_min")
        st.number_input("고양이 최대 체중 (kg)", value=config.cat_max_weight, key="cat_max")
        st.number_input("최소 방문 지속시간 (초)", value=config.min_visit_duration, key="visit_min")
        st.number_input("최대 방문 지속시간 (초)", value=config.max_visit_duration, key="visit_max")
    
    st.markdown("---")
    st.subheader("🔧 시스템 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 기준선 초기화", use_container_width=True):
            st.session_state.baseline_manager.reset_baseline()
            st.success("기준선 초기화 요청됨")
    
    with col2:
        if st.button("🗑️ 전체 데이터 초기화", type="secondary", use_container_width=True):
            st.session_state['confirm_reset'] = True
    
    # Confirmation dialog for data reset
    if st.session_state.get('confirm_reset', False):
        st.warning("⚠️ **경고**: 모든 데이터가 삭제됩니다!")
        st.write("다음 데이터가 삭제됩니다:")
        st.write("- 모든 이벤트 기록")
        st.write("- 모든 센서 데이터 (raw, processed)")
        st.write("- 고양이 프로필은 유지됩니다")
        
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.button("✅ 확인 - 삭제", type="primary", use_container_width=True):
                import shutil
                import os
                
                # Delete event files
                events_dir = st.session_state.db.data_dir / "events"
                if events_dir.exists():
                    shutil.rmtree(events_dir)
                    os.makedirs(events_dir)
                
                # Delete raw data files
                raw_dir = st.session_state.db.data_dir / "raw"
                if raw_dir.exists():
                    shutil.rmtree(raw_dir)
                    os.makedirs(raw_dir)
                
                # Delete processed data files
                processed_dir = st.session_state.db.data_dir / "processed"
                if processed_dir.exists():
                    shutil.rmtree(processed_dir)
                    os.makedirs(processed_dir)
                
                # Delete alerts
                alerts_dir = st.session_state.db.data_dir / "alerts"
                if alerts_dir.exists():
                    shutil.rmtree(alerts_dir)
                    os.makedirs(alerts_dir)
                
                # Reset baseline
                st.session_state.baseline_manager.current_baseline = None
                st.session_state.baseline_manager.history = []
                st.session_state.baseline_manager.stability_window.clear()
                
                # Reset event detector
                st.session_state.event_detector.current_event = None
                
                st.session_state['confirm_reset'] = False
                st.success("✅ 전체 데이터가 초기화되었습니다!")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ 취소", use_container_width=True):
                st.session_state['confirm_reset'] = False
                st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.info("고양이 건강 코파일럿 v1.0\n\nESP32 기반 스마트 화장실 모니터링")
