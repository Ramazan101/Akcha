import streamlit as st
import anthropic
import json
from . import api

SYSTEM_PROMPT = """Ты — Akcha AI, умный персональный финансовый ассистент для молодёжи Кыргызстана.

Твоя задача:
- Давать конкретные, практичные советы по управлению личными финансами
- Объяснять финансовые концепции простым языком (пользователи — школьники и студенты)
- Применять правило 50/30/20 и другие базовые принципы личных финансов
- Отвечать на кыргызском, русском или английском — в зависимости от языка пользователя
- Валюта — кыргызский сом (с), если не указано иное

Стиль общения:
- Дружелюбный, позитивный, мотивирующий
- Конкретный: давай числа, примеры, шаги
- Никогда не более 200 слов в ответе, если пользователь не просит подробно
- Используй эмодзи умеренно для живости

При анализе финансовых данных:
- Всегда объясняй ПОЧЕМУ это важно
- Давай 1-2 конкретных действия на следующую неделю
- Будь честным, но мотивирующим

Ты НЕ: банк, финансовый советник с лицензией, не даёшь гарантий инвестиций."""

QUICK_QUESTIONS = [
    "💡 Как начать копить деньги?",
    "📊 Объясни правило 50/30/20",
    "🎓 Как студенту управлять бюджетом?",
    "🏦 Куда откладывать деньги?",
    "💳 Как избавиться от долгов?",
    "🚀 Как быстро накопить на крупную покупку?",
]


def _stream_response(messages: list) -> str:
    """Stream response directly from Anthropic API."""
    client = anthropic.Anthropic()
    full_text = ""

    with client.messages.stream(
        model="claude-opus-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        placeholder = st.empty()
        for text in stream.text_stream:
            full_text += text
            # Render incrementally
            placeholder.markdown(f"""
            <div class="chat-msg ai">
                <div class="chat-avatar ai-avatar">🤖</div>
                <div class="chat-bubble">{full_text}▌</div>
            </div>
            """, unsafe_allow_html=True)
        # Final render without cursor
        placeholder.markdown(f"""
        <div class="chat-msg ai">
            <div class="chat-avatar ai-avatar">🤖</div>
            <div class="chat-bubble">{full_text}</div>
        </div>
        """, unsafe_allow_html=True)
    return full_text


def _get_financial_context() -> str:
    """Fetch user's current stats to inject as context."""
    try:
        stats = api.get_stats()
        if not stats:
            return ""
        income = float(stats.get("income", 0))
        total_expense = float(stats.get("total_expense", 0))
        balance = float(stats.get("balance", 0))
        by_cat = stats.get("by_category", {})
        cat_summary = ", ".join(
            f"{k}: {float(v.get('amount',0)):,.0f} с"
            for k, v in by_cat.items() if float(v.get("amount", 0)) > 0
        )
        return (
            f"\n\n[Контекст пользователя: доход={income:,.0f} с, "
            f"расходы={total_expense:,.0f} с, баланс={balance:,.0f} с"
            + (f", по категориям: {cat_summary}" if cat_summary else "")
            + "]"
        )
    except Exception:
        return ""


def render():
    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#e2e8f0;">
            🤖 AI Финансовый советник
        </div>
        <div style="color:#64748b; font-size:.9rem;">
            Задай любой вопрос о личных финансах — отвечаю на русском, кыргызском и английском
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_side = st.columns([1.8, 1])

    with col_chat:
        # ── Chat history ──────────────────────────────────────────────────────
        chat_container = st.container()

        with chat_container:
            if not st.session_state.chat_history:
                # Welcome message
                st.markdown("""
                <div class="chat-msg ai">
                    <div class="chat-avatar ai-avatar">🤖</div>
                    <div class="chat-bubble">
                        <b>Привет! Я Akcha AI 👋</b><br><br>
                        Я твой личный финансовый советник. Могу помочь тебе:
                        <br>• 📊 Разобраться с расходами
                        <br>• 🎯 Накопить на цель
                        <br>• 💡 Научиться управлять деньгами
                        <br><br>Что тебя интересует?
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_history:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "user":
                        st.markdown(f"""
                        <div class="chat-msg user">
                            <div class="chat-avatar user-avatar">👤</div>
                            <div class="chat-bubble">{content}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-msg ai">
                            <div class="chat-avatar ai-avatar">🤖</div>
                            <div class="chat-bubble">{content}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # ── Input ─────────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        input_col, send_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_input(
                "Сообщение",
                placeholder="Напиши вопрос о финансах...",
                label_visibility="collapsed",
                key="chat_input"
            )
        with send_col:
            send = st.button("Отправить →", use_container_width=True)

        if (send or user_input) and user_input.strip():
            _handle_message(user_input.strip())

        # Clear
        if st.session_state.chat_history:
            if st.button("🗑 Очистить чат", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with col_side:
        st.markdown("#### 💬 Быстрые вопросы")
        for q in QUICK_QUESTIONS:
            if st.button(q, use_container_width=True, key=f"quick_{q}"):
                _handle_message(q)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Анализ по твоим данным")
        if st.button("🔍 Проанализируй мои расходы", use_container_width=True):
            ctx = _get_financial_context()
            msg = f"Проанализируй мои текущие расходы и дай конкретные советы по улучшению.{ctx}"
            _handle_message(msg, display_as="🔍 Проанализируй мои расходы")

        if st.button("💡 Дай план накоплений", use_container_width=True):
            ctx = _get_financial_context()
            msg = f"Составь для меня персональный план накоплений на 3 месяца.{ctx}"
            _handle_message(msg, display_as="💡 Дай план накоплений")

        if st.button("⚠️ Где я перерасходую?", use_container_width=True):
            ctx = _get_financial_context()
            msg = f"Посмотри на мои данные и скажи, где я трачу больше нормы.{ctx}"
            _handle_message(msg, display_as="⚠️ Где я перерасходую?")

        # Stats mini panel
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🎯 Твоя статистика")
        stats = api.get_stats()
        if stats:
            income = float(stats.get("income", 0))
            expense = float(stats.get("total_expense", 0))
            balance = float(stats.get("balance", 0))
            for label, val, color in [
                ("💰 Доход", f"{income:,.0f} с", "#00d4aa"),
                ("💸 Расходы", f"{expense:,.0f} с", "#ef4444"),
                ("🏦 Остаток", f"{balance:,.0f} с",
                 "#10b981" if balance >= 0 else "#ef4444"),
            ]:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between;
                            padding:.5rem .8rem; border-radius:8px; margin-bottom:.3rem;
                            background:rgba(21,29,46,.8);">
                    <span style="font-size:.82rem; color:#94a3b8;">{label}</span>
                    <span style="font-family:'Space Mono',monospace; font-size:.82rem;
                                color:{color}; font-weight:700;">{val}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Нет данных для отображения")


def _handle_message(user_msg: str, display_as: str = None):
    """Add user message to history, stream AI response, update state."""
    display_msg = display_as or user_msg

    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": display_msg
    })

    # Prepare messages for API (strip context markers from display)
    api_messages = []
    for m in st.session_state.chat_history:
        api_messages.append({"role": m["role"], "content": m["content"]})
    # Replace last user message with full context version
    if display_as:
        api_messages[-1]["content"] = user_msg

    # Show user message immediately
    st.markdown(f"""
    <div class="chat-msg user">
        <div class="chat-avatar user-avatar">👤</div>
        <div class="chat-bubble">{display_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Stream AI response
    try:
        ai_reply = _stream_response(api_messages)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": ai_reply
        })
    except Exception as e:
        err_msg = f"⚠️ Не удалось получить ответ: {str(e)}"
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": err_msg
        })

    st.rerun()