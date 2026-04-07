import streamlit as st
from . import api


def render():
    # Hero section
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0 1rem;">
        <div style="font-family:'Syne',sans-serif; font-size:3.5rem; font-weight:800;
                    background:linear-gradient(135deg,#00d4aa,#6366f1);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text; line-height:1.1; margin-bottom:.5rem;">
            Akcha AI
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:.75rem;
                    color:#64748b; letter-spacing:.2em; text-transform:uppercase;">
            Умный финансовый ассистент
        </div>
        <div style="margin-top:1rem; color:#94a3b8; font-size:.95rem; max-width:420px; margin-inline:auto;">
            Управляй расходами, ставь цели и получай персональные советы от AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    with col_center:
        tab_login, tab_reg = st.tabs(["🔐 Войти", "🚀 Регистрация"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Имя пользователя", placeholder="akcha_user")
                password = st.text_input("Пароль", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Войти →", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("Заполни все поля")
                    else:
                        with st.spinner("Входим..."):
                            ok, data = api.login(username, password)
                        if ok:
                            st.session_state.token = data.get("access")
                            st.session_state.username = username
                            st.success("Добро пожаловать! 🎉")
                            st.rerun()
                        else:
                            err = data.get("detail", "Неверный логин или пароль")
                            st.error(f"❌ {err}")

        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    reg_username = st.text_input("Имя пользователя", placeholder="my_name", key="ru")
                with col_b:
                    reg_email = st.text_input("Email", placeholder="you@email.com", key="re")

                reg_income = st.number_input(
                    "Ежемесячный доход (сом)", min_value=0.0, value=15000.0,
                    step=500.0, format="%.0f"
                )
                reg_pass = st.text_input("Пароль", type="password",
                                         placeholder="Минимум 8 символов", key="rp1")
                reg_pass2 = st.text_input("Повтори пароль", type="password",
                                          placeholder="••••••••", key="rp2")
                submitted2 = st.form_submit_button("Создать аккаунт →", use_container_width=True)

                if submitted2:
                    if not all([reg_username, reg_email, reg_pass, reg_pass2]):
                        st.error("Заполни все поля")
                    elif reg_pass != reg_pass2:
                        st.error("Пароли не совпадают")
                    else:
                        with st.spinner("Регистрируем..."):
                            ok, data = api.register(
                                reg_username, reg_email,
                                reg_pass, reg_pass2, reg_income
                            )
                        if ok:
                            st.success("Аккаунт создан! Теперь войди 👆")
                        else:
                            for field, errors in data.items():
                                if isinstance(errors, list):
                                    for e in errors:
                                        st.error(f"**{field}**: {e}")
                                else:
                                    st.error(f"**{field}**: {errors}")

    # Features strip
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, desc in [
        (c1, "📊", "Аналитика", "Следи за расходами в реальном времени"),
        (c2, "🎯", "Цели", "Ставь и достигай финансовых целей"),
        (c3, "🤖", "AI Советы", "Персональный финансовый советник"),
        (c4, "🔒", "Безопасность", "Данные защищены JWT-токеном"),
    ]:
        with col:
            st.markdown(f"""
            <div class="akcha-card" style="text-align:center; padding:1.2rem .8rem;">
                <div style="font-size:1.8rem; margin-bottom:.5rem;">{icon}</div>
                <div style="font-family:'Syne',sans-serif; font-weight:700;
                            font-size:.95rem; color:#e2e8f0; margin-bottom:.3rem;">{title}</div>
                <div style="font-size:.78rem; color:#64748b; line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)