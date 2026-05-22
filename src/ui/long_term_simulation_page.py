"""
Long-Term Simulation Page

장기 시뮬레이션 구성 및 실행 페이지
"""

import streamlit as st
from datetime import datetime, timedelta
from src.data.schema import SimulationScenario, SimulationConfig


def render_long_term_simulation_page(db, long_term_simulator):
    """Render long-term simulation configuration page"""
    st.title("🎮 장기 시뮬레이션")
    
    st.write("여러 날에 걸친 고양이 방문 패턴을 시뮬레이션하여 건강 모니터링 기능을 테스트합니다.")
    
    # Get all cat profiles
    profiles = db.get_all_cat_profiles()
    
    if not profiles:
        st.warning("⚠️ 등록된 고양이가 없습니다. 먼저 고양이 프로필을 추가하세요.")
        return
    
    # Configuration section
    st.subheader("⚙️ 시뮬레이션 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration_days = st.selectbox(
            "시뮬레이션 기간",
            [7, 14, 30],
            index=0,
            help="시뮬레이션할 일수를 선택하세요"
        )
    
    with col2:
        start_date = st.date_input(
            "시작 날짜",
            value=datetime.now().date() - timedelta(days=duration_days),
            help="시뮬레이션 시작 날짜"
        )
        start_time = st.time_input(
            "시작 시간",
            value=datetime.now().time().replace(hour=0, minute=0, second=0)
        )
    
    start_datetime = datetime.combine(start_date, start_time)
    
    # Cat configuration
    st.markdown("---")
    st.subheader("🐱 고양이별 시나리오 설정")
    
    scenario_options = {
        "정상 패턴": SimulationScenario.NORMAL,
        "다뇨 발병 (3일 후)": SimulationScenario.POLYURIA_ONSET,
        "점진적 체중 감소": SimulationScenario.GRADUAL_WEIGHT_LOSS,
        "복합 (다뇨 + 체중 감소)": SimulationScenario.COMBINED
    }
    
    selected_cats = []
    
    for profile in profiles:
        with st.expander(f"🐱 {profile.name} ({profile.baseline_weight}kg)"):
            col_include, col_scenario = st.columns([1, 2])
            
            with col_include:
                include = st.checkbox(
                    "포함",
                    value=True,
                    key=f"include_{profile.cat_id}"
                )
            
            with col_scenario:
                if include:
                    scenario_name = st.selectbox(
                        "시나리오",
                        list(scenario_options.keys()),
                        key=f"scenario_{profile.cat_id}"
                    )
                    scenario = scenario_options[scenario_name]
                    selected_cats.append((profile.cat_id, scenario))
                    
                    # Show scenario description
                    if scenario == SimulationScenario.NORMAL:
                        st.caption("📝 하루 2-4회 방문, 30-120초 지속")
                    elif scenario == SimulationScenario.POLYURIA_ONSET:
                        st.caption("📝 3일간 정상 → 하루 6-10회 방문, 15-45초 지속")
                    elif scenario == SimulationScenario.GRADUAL_WEIGHT_LOSS:
                        st.caption("📝 하루 0.5-1.0% 체중 감소")
                    elif scenario == SimulationScenario.COMBINED:
                        st.caption("📝 다뇨 발병 + 점진적 체중 감소")
    
    if not selected_cats:
        st.warning("⚠️ 최소 한 마리의 고양이를 선택하세요.")
        return
    
    # Preview section
    st.markdown("---")
    st.subheader("📋 시뮬레이션 미리보기")
    
    # Calculate expected events
    total_expected_events = 0
    for cat_id, scenario in selected_cats:
        if scenario == SimulationScenario.NORMAL:
            avg_visits_per_day = 3
        elif scenario == SimulationScenario.POLYURIA_ONSET:
            # 3 days normal + rest polyuria
            normal_days = 3
            polyuria_days = duration_days - normal_days
            avg_visits_per_day = (normal_days * 3 + polyuria_days * 8) / duration_days
        else:
            avg_visits_per_day = 3
        
        total_expected_events += int(avg_visits_per_day * duration_days)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("선택된 고양이", len(selected_cats))
    
    with col2:
        st.metric("예상 이벤트 수", f"약 {total_expected_events}개")
    
    with col3:
        estimated_time = total_expected_events * 0.1  # Rough estimate
        st.metric("예상 실행 시간", f"약 {estimated_time:.1f}초")
    
    # Execution button
    st.markdown("---")
    
    col_run, col_cancel = st.columns([1, 1])
    
    with col_run:
        if st.button("🚀 시뮬레이션 실행", type="primary", use_container_width=True):
            # Create configuration
            config = SimulationConfig(
                duration_days=duration_days,
                start_datetime=start_datetime,
                cats=selected_cats
            )
            
            # Run simulation with progress
            with st.spinner("시뮬레이션 실행 중..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Run simulation
                    result = long_term_simulator.run_simulation(config)
                    
                    progress_bar.progress(100)
                    status_text.success("✅ 시뮬레이션 완료!")
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📊 시뮬레이션 결과")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("생성된 이벤트", result.events_generated)
                    
                    with col2:
                        st.metric("생성된 알림", result.alerts_created)
                    
                    with col3:
                        st.metric("기준선 변경", result.baseline_changes)
                    
                    with col4:
                        st.metric("실행 시간", f"{result.execution_time:.1f}초")
                    
                    # Weight changes per cat
                    if result.weight_changes:
                        st.markdown("---")
                        st.subheader("🐱 고양이별 체중 변화")
                        
                        for cat_id, (start_weight, end_weight, change_rate) in result.weight_changes.items():
                            # Find cat name
                            cat_name = "알 수 없음"
                            for profile in profiles:
                                if profile.cat_id == cat_id:
                                    cat_name = profile.name
                                    break
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**{cat_name}**")
                            
                            with col2:
                                st.write(f"시작: {start_weight:.2f}kg → 종료: {end_weight:.2f}kg")
                            
                            with col3:
                                if change_rate > 0:
                                    st.write(f"변화율: :red[+{change_rate:.1f}%]")
                                else:
                                    st.write(f"변화율: :green[{change_rate:.1f}%]")
                    
                    # Errors
                    if result.errors:
                        st.markdown("---")
                        st.subheader("⚠️ 오류")
                        for error in result.errors:
                            st.error(error)
                    
                    st.success("🎉 시뮬레이션이 완료되었습니다! '체중 추적' 페이지에서 결과를 확인하세요.")
                    
                except Exception as e:
                    st.error(f"❌ 시뮬레이션 실행 중 오류 발생: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with col_cancel:
        if st.button("❌ 취소", use_container_width=True):
            st.info("시뮬레이션이 취소되었습니다.")
