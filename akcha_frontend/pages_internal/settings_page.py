import streamlit as st
from . import api


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#e2e8f0;">
            ⚙️ Настройки
        </div>
        <div style="color:#64748b; font-size:.9rem;">Управляй профилем и параметрами</div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # ── Profile ───────────────────────────────────────────────────────────
        st.markdown("#### 👤 Профиль")
        with st.spinner("Загружаем профиль..."):
            profile = api.get_profile()

        if profile:
            st.markdown(f"""
            <div class="akcha-card" style="margin-bottom:1rem;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:52px; height:52px; border-radius:50%;
                                background:linear-gradient(135deg,#00d4aa,#6366f1);
                                display:flex; align-items:center; justify-content:center;
                                font-size:1.3rem; font-weight:800; color:#0a0e1a; font-family:'Syne'">
                        {profile.get('username', '?')[0].upper()}
                    </div>
                    <div>
                        <div style="font-family:'Syne',sans-serif; font-size:1.1rem;
                                    font-weight:700; color:#e2e8f0;">
                            {profile.get('username', '—')}
                        </div>
                        <div style="font-size:.8rem; color:#64748b; margin-top:.1rem;">
                            {profile.get('email', '—')}
                        </div>
                        <span class="pill pill-green" style="margin-top:.3rem; display:inline-block;">
                            Доход: {float(profile.get('income', 0)):,.0f} с/мес
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Update income
            st.markdown("**Обновить доход**")
            with st.form("update_income"):
                new_income = st.number_input(
                    "Ежемесячный доход (сом)",
                    value=float(profile.get("income", 0)),
                    min_value=0.0, step=500.0, format="%.0f"
                )
                new_email = st.text_input(
                    "Email",
                    value=profile.get("email", ""),
                    placeholder="your@email.com"
                )
                if st.form_submit_button("Сохранить →", use_container_width=True):
                    ok, data = api.update_profile(
                        {"income": new_income, "email": new_email}
                    )
                    if ok:
                        st.success("✅ Профиль обновлён!")
                    else:
                        st.error(f"❌ {data}")
        else:
            st.warning("Не удалось загрузить профиль")

        # ── API Settings ──────────────────────────────────────────────────────
        st.markdown("<br>#### 🔌 Подключение к API")
        with st.form("api_settings"):
            new_base = st.text_input(
                "URL бэкенда",
                value=st.session_state.api_base,
                placeholder="http://localhost:8000"
            )
            if st.form_submit_button("Сохранить URL →", use_container_width=True):
                st.session_state.api_base = new_base.rstrip("/")
                st.success(f"✅ URL обновлён: {st.session_state.api_base}")

    with col_right:
        # ── Budget calculator ─────────────────────────────────────────────────
        st.markdown("#### 🧮 Калькулятор бюджета 50/30/20")
        calc_income = st.number_input(
            "Твой доход (сом)", min_value=0.0, value=15000.0,
            step=500.0, format="%.0f", key="calc_inc"
        )
        if calc_income > 0:
            needs = calc_income * 0.5
            wants = calc_income * 0.3
            savings = calc_income * 0.2

            for label, amount, pct, color, desc in [
                ("🏠 Нужды (50%)", needs, 50, "#00d4aa",
                 "Еда, аренда, транспорт, коммуналка"),
                ("🎮 Желания (30%)", wants, 30, "#6366f1",
                 "Развлечения, кафе, одежда"),
                ("💰 Накопления (20%)", savings, 20, "#f59e0b",
                 "Сбережения, инвестиции, цели"),
            ]:
                st.markdown(f"""
                <div class="akcha-card" style="margin-bottom:.7rem; padding:1rem 1.2rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:.4rem;">
                        <span style="font-family:'Syne',sans-serif; font-size:.9rem;
                                     font-weight:700; color:#e2e8f0;">{label}</span>
                        <span style="font-family:'Space Mono',monospace; font-size:.95rem;
                                     color:{color}; font-weight:700;">{amount:,.0f} с</span>
                    </div>
                    <div class="goal-bar-wrap">
                        <div class="goal-bar-fill" style="width:{pct}%;
                             background:linear-gradient(90deg,{color},{color}88);">
                        </div>
                    </div>
                    <div style="font-size:.76rem; color:#64748b; margin-top:.3rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── About ─────────────────────────────────────────────────────────────
        st.markdown("<br>#### ℹ️ О приложении")
        st.markdown("""
        <div class="akcha-card" style="padding:1.2rem;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;
                        color:#e2e8f0; margin-bottom:.6rem;">Akcha AI v1.0</div>
            <div style="font-size:.83rem; color:#94a3b8; line-height:1.7;">
                🎯 Финансовый ассистент для молодёжи<br>
                🤖 AI на базе Claude (Anthropic)<br>
                🔧 Backend: Django REST Framework<br>
                ⚛️ Frontend: Streamlit<br>
                🔒 Авторизация: JWT<br>
                🌏 Локализация: KG / RU / EN
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Danger zone ───────────────────────────────────────────────────────
        st.markdown("<br>#### 🚨 Выход из аккаунта")
        if st.button("🚪 Выйти из системы", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.rerun()