
import streamlit as st
import pandas as pd
import time
from datetime import date, timedelta

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="STUDY FLOW",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f7f7ff, #eef7ff);
}
.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}
h1, h2, h3 {
    color: #28264d;
}
div.stButton > button {
    border-radius: 12px;
    border: none;
    min-height: 42px;
    font-weight: 600;
}
div.stButton > button[kind="primary"] {
    background: #6658e8;
    color: white;
}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e8e6ff;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 데이터 초기화
# -------------------------
if "subjects" not in st.session_state:
    st.session_state.subjects = [
        "국어", "영어", "수학", "과학", "정보"
    ]

if "records" not in st.session_state:
    st.session_state.records = []

if "timer" not in st.session_state:
    st.session_state.timer = {
        "running": False,
        "subject": "",
        "goal": 30,
        "started_at": None,
        "elapsed": 0
    }

if "notice" not in st.session_state:
    st.session_state.notice = ""

# -------------------------
# 타이머 계산
# -------------------------
def get_elapsed():
    timer = st.session_state.timer
    elapsed = timer["elapsed"]

    if timer["running"] and timer["started_at"] is not None:
        elapsed += time.monotonic() - timer["started_at"]

    return max(0, int(elapsed))


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def save_record(seconds, subject, goal, focus):
    minutes = seconds / 60

    if minutes <= 0:
        st.session_state.notice = "공부 시간이 없어 기록하지 않았어요."
        return

    achievement = min(minutes / goal * 100, 100) if goal > 0 else 0

    # 공부 시간과 집중도를 함께 반영한 참고용 지표
    efficiency = achievement * 0.5 + focus * 10 * 0.5

    if focus >= 8 and achievement >= 80:
        advice = "집중도와 목표 달성이 모두 좋았어요!"
    elif focus < 5:
        advice = "짧은 공부 단위로 나누고 방해 요소를 줄여 보세요."
    elif achievement < 50:
        advice = "목표 시간을 조금 줄여 꾸준히 달성해 보세요."
    else:
        advice = "잘하고 있어요. 다음에도 비슷한 공부 습관을 유지해 보세요."

    st.session_state.records.append({
        "날짜": date.today().isoformat(),
        "과목": subject,
        "공부 시간(분)": round(minutes, 1),
        "목표 시간(분)": goal,
        "목표 달성률(%)": round(achievement, 1),
        "집중도": focus,
        "참고 효율 점수": round(efficiency, 1),
        "조언": advice
    })

    st.session_state.notice = f"{subject} 공부 기록을 저장했어요!"


# -------------------------
# 제목과 메뉴
# -------------------------
st.title("📚 STUDY FLOW")
st.caption("나만의 공부 시간을 기록하고 공부 습관을 분석해 보세요.")

page = st.sidebar.radio(
    "메뉴",
    [
        "🏠 홈",
        "⏱️ 공부 타이머",
        "📊 공부 기록",
        "📅 주간 분석",
        "📘 과목 관리"
    ]
)

if st.session_state.notice:
    st.info(st.session_state.notice)
    st.session_state.notice = ""

# -------------------------
# 홈
# -------------------------
if page == "🏠 홈":
    st.subheader("오늘의 공부 현황")

    today_records = [
        r for r in st.session_state.records
        if r["날짜"] == date.today().isoformat()
    ]

    total_minutes = sum(r["공부 시간(분)"] for r in today_records)
    total_sessions = len(today_records)

    col1, col2, col3 = st.columns(3)
    col1.metric("오늘 공부 시간", f"{total_minutes:.0f}분")
    col2.metric("공부 기록", f"{total_sessions}회")
    col3.metric("등록 과목", f"{len(st.session_state.subjects)}개")

    st.divider()
    st.subheader("🚀 바로 시작하기")

    if st.session_state.subjects:
        subject = st.selectbox(
            "공부할 과목",
            st.session_state.subjects,
            key="home_subject"
        )
        goal = st.number_input(
            "목표 공부 시간(분)",
            min_value=1,
            max_value=600,
            value=30,
            key="home_goal"
        )

        if st.button("타이머 설정하기", type="primary"):
            if st.session_state.timer["running"]:
                st.warning("실행 중인 타이머를 먼저 종료해 주세요.")
            else:
                st.session_state.timer = {
                    "running": False,
                    "subject": subject,
                    "goal": int(goal),
                    "started_at": None,
                    "elapsed": 0
                }
                st.session_state.notice = "타이머 메뉴에서 공부를 시작하세요."
                st.rerun()
    else:
        st.info("과목 관리 메뉴에서 공부할 과목을 먼저 추가해 주세요.")

    st.divider()
    st.subheader("💡 공부 팁")
    st.write("목표는 현실적으로 설정하고, 공부가 끝난 뒤 기록을 확인해 보세요.")

# -------------------------
# 타이머
# -------------------------
elif page == "⏱️ 공부 타이머":
    st.subheader("⏱️ 집중 타이머")

    timer = st.session_state.timer

    if not timer["subject"]:
        st.info("홈 메뉴에서 과목과 목표 시간을 먼저 설정해 주세요.")
    else:
        st.write(f"**과목:** {timer['subject']}")
        st.write(f"**목표 시간:** {timer['goal']}분")

        remaining = max(
            0,
            timer["goal"] * 60 - get_elapsed()
        )

        # Streamlit 최신 버전의 주기적 화면 갱신 기능
        @st.fragment(run_every="1s")
        def timer_display():
            elapsed = get_elapsed()
            goal_seconds = st.session_state.timer["goal"] * 60
            remaining_seconds = max(0, goal_seconds - elapsed)

            st.markdown(
                f"<div style='text-align:center; background:white;"
                f"padding:28px; border-radius:20px; "
                f"border:1px solid #e5e2ff;'>"
                f"<div style='font-size:14px;color:#777;'>"
                f"{'공부 중' if st.session_state.timer['running'] else '누적 공부 시간'}"
                f"</div>"
                f"<div style='font-size:48px;font-weight:700;color:#6658e8;'>"
                f"{format_time(elapsed)}</div>"
                f"<div style='font-size:16px;color:#555;'>"
                f"남은 목표 시간 {format_time(remaining_seconds)}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

            if goal_seconds > 0:
                st.progress(min(elapsed / goal_seconds, 1.0))

        timer_display()

        focus = st.slider(
            "오늘 이 공부의 집중도",
            min_value=1,
            max_value=10,
            value=7,
            help="1은 매우 낮음, 10은 매우 높음",
            key="timer_focus"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "▶️ 시작 / 재개",
                type="primary",
                disabled=timer["running"]
            ):
                timer["started_at"] = time.monotonic()
                timer["running"] = True
                st.rerun()

        with col2:
            if st.button(
                "⏸️ 일시정지",
                disabled=not timer["running"]
            ):
                timer["elapsed"] = get_elapsed()
                timer["running"] = False
                timer["started_at"] = None
                st.rerun()

        with col3:
            if st.button("⏹️ 공부 종료"):
                seconds = get_elapsed()
                was_running = timer["running"]

                save_record(
                    seconds,
                    timer["subject"],
                    timer["goal"],
                    focus
                )

                st.session_state.timer = {
                    "running": False,
                    "subject": "",
                    "goal": 30,
                    "started_at": None,
                    "elapsed": 0
                }
                st.rerun()

        if get_elapsed() >= timer["goal"] * 60:
            st.success("🎉 목표 시간에 도달했어요! 원할 때 종료할 수 있어요.")

        st.caption(
            "※ 일시정지 중에는 시간이 늘어나지 않아요. "
            "공부 종료를 누르면 현재까지의 시간이 기록됩니다."
        )

# -------------------------
# 전체 공부 기록
# -------------------------
elif page == "📊 공부 기록":
    st.subheader("📊 공부 기록")

    if not st.session_state.records:
        st.info("아직 기록이 없어요. 타이머로 공부를 기록해 보세요.")
    else:
        df = pd.DataFrame(st.session_state.records)
        df["날짜"] = pd.to_datetime(df["날짜"]).dt.date

        selected_date = st.date_input(
            "조회할 날짜",
            value=date.today(),
            key="record_date"
        )

        filtered = df[df["날짜"] == selected_date]

        if filtered.empty:
            st.info("선택한 날짜에는 기록이 없어요.")
        else:
            st.metric(
                "선택한 날짜의 총 공부 시간",
                f"{filtered['공부 시간(분)'].sum():.0f}분"
            )
            st.dataframe(
                filtered.sort_values("과목"),
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        st.subheader("전체 기록")
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 기록 CSV 다운로드",
            data=csv,
            file_name="study_records.csv",
            mime="text/csv"
        )

# -------------------------
# 주간 분석
# -------------------------
elif page == "📅 주간 분석":
    st.subheader("📅 최근 7일 공부 분석")

    today = date.today()
    start_date = today - timedelta(days=6)

    if not st.session_state.records:
        st.info("기록이 쌓이면 주간 분석을 볼 수 있어요.")
    else:
        df = pd.DataFrame(st.session_state.records)
        df["날짜"] = pd.to_datetime(df["날짜"]).dt.date

        week = df[
            (df["날짜"] >= start_date) &
            (df["날짜"] <= today)
        ]

        daily = (
            week.groupby("날짜")["공부 시간(분)"]
            .sum()
            .reindex(
                [start_date + timedelta(days=i) for i in range(7)],
                fill_value=0
            )
        )

        st.metric("최근 7일 총 공부 시간", f"{daily.sum():.0f}분")
        st.bar_chart(daily)

        if not week.empty:
            st.subheader("과목별 공부 시간")
            subject_totals = week.groupby("과목")["공부 시간(분)"].sum()
            st.bar_chart(subject_totals)

            st.subheader("집중도 평균")
            st.metric("평균 집중도", f"{week['집중도'].mean():.1f} / 10")
        else:
            st.info("최근 7일 동안 기록된 공부가 없어요.")

# -------------------------
# 과목 관리
# -------------------------
elif page == "📘 과목 관리":
    st.subheader("📘 나만의 과목 관리")

    with st.form("add_subject_form"):
        new_subject = st.text_input(
            "추가할 과목 이름",
            placeholder="예: 프로그래밍"
        )
        submitted = st.form_submit_button("과목 추가")

        if submitted:
            name = new_subject.strip()

            if not name:
                st.warning("과목 이름을 입력해 주세요.")
            elif name in st.session_state.subjects:
                st.warning("이미 등록된 과목이에요.")
            else:
                st.session_state.subjects.append(name)
                st.success(f"{name} 과목을 추가했어요!")
                st.rerun()

    st.divider()
    st.write("**등록된 과목**")

    if not st.session_state.subjects:
        st.info("등록된 과목이 없어요.")
    else:
        for subject in st.session_state.subjects:
            col1, col2 = st.columns([4, 1])
            col1.write(f"📚 {subject}")

            if col2.button("삭제", key=f"delete_{subject}"):
                if (
                    st.session_state.timer["subject"] == subject
                    and st.session_state.timer["running"]
                ):
                    st.error("공부 중인 과목은 타이머를 종료한 뒤 삭제해 주세요.")
                else:
                    st.session_state.subjects.remove(subject)
                    st.rerun()

    st.caption(
        "참고: 현재 버전의 기록은 앱 세션에 저장돼요. "
        "CSV로 다운로드해 보관할 수 있지만, 앱을 완전히 종료하면 "
        "세션 기록이 유지되지 않을 수 있어요."
    )
