import streamlit as st
import plotly.graph_objects as go
from datetime import date, datetime
from . import api


def _months_to_goal(target: float, current: float, income: float) -> str:
    remaining = target - current
    if remaining <= 0:
        return "✅ Цель достигнута!"
    if income <= 0:
        return "Укажи доход в профиле"
    # Assume saving 20% of income
    monthly_save = income * 0.2
    if monthly_save <= 0:
        return "—"
    months = remaining / monthly_save
    return f"~{months:.1f} мес. (при откладывании 20% дохода)"


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#e2e8f0;">
            🎯 Финансовые цели
        </div>
        <div style="color:#64748b; font-size:.9rem;">Ставь цели и отслеживай прогресс накоплений</div>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_goals = st.columns([1, 1.6])

    # ── Add Goal ──────────────────────────────────────────────────────────────
    with col_form:
        st.markdown("#### ➕ Новая цель")
        with st.form("add_goal_form", clear_on_submit=True):
            g_title = st.text_input("Название цели", placeholder="Новый ноутбук 💻")
            g_target = st.number_input("Целевая сумма (сом)", min_value=1.0,
                                        value=50000.0, step=1000.0, format="%.0f")
            g_deadline = st.date_input("Дедлайн (необязательно)",
                                        value=None, min_value=date.today())
            submitted = st.form_submit_button("Создать цель →", use_container_width=True)

            if submitted:
                if not g_title:
                    st.error("Введи название цели")
                else:
                    deadline_str = str(g_deadline) if g_deadline else None
                    ok, data = api.add_goal(g_title, g_target, deadline_str)
                    if ok:
                        st.success(f"🎯 Цель создана: {g_title}")
                        st.rerun()
                    else:
                        st.error(f"❌ {data}")

        # ── Tips ──────────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        for icon, tip in [
            ("💡", "Откладывай минимум 20% дохода каждый месяц"),
            ("📅", "Ставь реалистичный дедлайн для мотивации"),
            ("🚀", "Разбивай большую цель на маленькие этапы"),
            ("🏆", "Отмечай каждое пополнение как победу"),
        ]:
            st.markdown(f"""
            <div style="display:flex; gap:10px; align-items:flex-start; margin-bottom:.6rem;
                        padding:.6rem .9rem; border-radius:10px;
                        background:rgba(99,102,241,.07); border:1px solid rgba(99,102,241,.15);">
                <span style="font-size:1rem;">{icon}</span>
                <span style="font-size:.82rem; color:#94a3b8; line-height:1.4;">{tip}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Goals List ────────────────────────────────────────────────────────────
    with col_goals:
        st.markdown("#### 📋 Мои цели")

        profile = api.get_profile()
        income = float(profile.get("income", 0))

        with st.spinner("Загружаем цели..."):
            goals = api.get_goals()

        if not goals:
            st.markdown("""
            <div class="akcha-card" style="text-align:center; padding:2.5rem; color:#64748b;">
                <div style="font-size:2.5rem; margin-bottom:.8rem;">🎯</div>
                <div style="font-family:'Syne',sans-serif; font-size:1rem; margin-bottom:.4rem;">
                    Нет целей
                </div>
                <div style="font-size:.82rem;">Создай первую финансовую цель слева!</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Summary
        total_target = sum(float(g.get("target_amount", 0)) for g in goals)
        total_current = sum(float(g.get("current_amount", 0)) for g in goals)
        overall_pct = (total_current / total_target * 100) if total_target > 0 else 0

        st.markdown(f"""
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:.8rem; margin-bottom:1.2rem;">
            <div class="akcha-card" style="padding:.9rem; text-align:center;">
                <div class="akcha-card-title">Всего целей</div>
                <div class="akcha-card-value" style="font-size:1.5rem;">{len(goals)}</div>
            </div>
            <div class="akcha-card" style="padding:.9rem; text-align:center;">
                <div class="akcha-card-title">Накоплено</div>
                <div class="akcha-card-value" style="font-size:1.3rem;">{total_current:,.0f} с</div>
            </div>
            <div class="akcha-card" style="padding:.9rem; text-align:center;">
                <div class="akcha-card-title">Прогресс</div>
                <div class="akcha-card-value" style="font-size:1.5rem;">{overall_pct:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for goal in goals:
            g_id = goal.get("id")
            g_title = goal.get("title", "—")
            g_target = float(goal.get("target_amount", 0))
            g_current = float(goal.get("current_amount", 0))
            g_pct = float(goal.get("progress_percent", 0))
            g_deadline = goal.get("deadline", "")
            g_remaining = max(0, g_target - g_current)

            # Color based on progress
            if g_pct >= 100:
                accent = "#10b981"
                pill_class = "pill-green"
                pill_text = "✅ Готово"
            elif g_pct >= 50:
                accent = "#6366f1"
                pill_class = "pill-purple"
                pill_text = "🔥 На пути"
            else:
                accent = "#f59e0b"
                pill_class = "pill-amber"
                pill_text = "⏳ Начало"

            months_str = _months_to_goal(g_target, g_current, income)

            with st.expander(f"{g_title}  —  {g_pct:.1f}%", expanded=True):
                st.markdown(f"""
                <div style="margin-bottom:.6rem;">
                    <div style="display:flex; justify-content:space-between;
                                align-items:center; margin-bottom:.8rem;">
                        <span class="pill {pill_class}">{pill_text}</span>
                        {'<span style="font-family:Space Mono,monospace; font-size:.72rem; color:#64748b;">📅 ' + g_deadline + '</span>' if g_deadline else ''}
                    </div>
                    <div style="display:flex; justify-content:space-between;
                                font-size:.82rem; color:#94a3b8; margin-bottom:.3rem;">
                        <span>{g_current:,.0f} с накоплено</span>
                        <span>цель: {g_target:,.0f} с</span>
                    </div>
                    <div class="goal-bar-wrap">
                        <div class="goal-bar-fill"
                             style="width:{min(g_pct,100):.1f}%;
                                    background:linear-gradient(90deg,{accent},{'#059669' if accent=='#10b981' else '#4f46e5' if accent=='#6366f1' else '#d97706'})">
                        </div>
                    </div>
                    <div style="font-size:.78rem; color:#64748b; margin-top:.4rem;">
                        {f'Осталось: <b style="color:#e2e8f0">{g_remaining:,.0f} с</b>' if g_pct < 100 else ''}
                        &nbsp;·&nbsp; {months_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if g_pct < 100:
                    top_up_col, del_col = st.columns([3, 1])
                    with top_up_col:
                        deposit = st.number_input(
                            "Пополнить (сом)", min_value=0.0, step=100.0,
                            format="%.0f", key=f"dep_{g_id}", label_visibility="collapsed"
                        )
                    with del_col:
                        if st.button("➕ Пополнить", key=f"topup_{g_id}", use_container_width=True):
                            if deposit > 0:
                                new_amount = g_current + deposit
                                ok, _ = api.update_goal(g_id, new_amount)
                                if ok:
                                    st.success(f"Пополнено на {deposit:,.0f} с! 🎉")
                                    st.rerun()
                                else:
                                    st.error("Ошибка")
                            else:
                                st.warning("Введи сумму пополнения")

                if st.button("🗑 Удалить цель", key=f"del_goal_{g_id}"):
                    if api.delete_goal(g_id):
                        st.rerun()

        # Radial progress overview
        if len(goals) > 1:
            st.markdown("<br>**Общий обзор целей**")
            fig = go.Figure()
            for i, g in enumerate(goals[:6]):  # max 6
                pct = float(g.get("progress_percent", 0))
                fig.add_trace(go.Indicator(
                    mode="gauge",
                    value=pct,
                    domain={"row": 0, "column": i},
                    title={"text": g["title"][:12], "font": {"size": 9, "color": "#64748b"}},
                    gauge={
                        "axis": {"range": [0, 100], "visible": False},
                        "bar": {"color": "#00d4aa" if pct >= 100 else "#6366f1"},
                        "bgcolor": "#1e2d45", "borderwidth": 0,
                    },
                ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                height=130,
                margin=dict(l=5, r=5, t=20, b=5),
                grid={"rows": 1, "columns": min(len(goals), 6)},
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})