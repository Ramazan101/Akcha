import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from . import api

CATEGORY_LABELS = {
    "food": "🍔 Еда",
    "transport": "🚌 Транспорт",
    "fun": "🎮 Развлечения",
    "education": "📚 Образование",
    "other": "📦 Другое",
}
CATEGORY_COLORS = {
    "food": "#00d4aa",
    "transport": "#6366f1",
    "fun": "#f59e0b",
    "education": "#3b82f6",
    "other": "#8b5cf6",
}


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#e2e8f0;">
            💳 Расходы
        </div>
        <div style="color:#64748b; font-size:.9rem;">Добавляй и отслеживай все траты</div>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_list = st.columns([1, 1.6])

    # ── Add Expense Form ───────────────────────────────────────────────────────
    with col_form:
        st.markdown("#### ➕ Новый расход")
        with st.form("add_expense_form", clear_on_submit=True):
            title = st.text_input("Название", placeholder="Продукты в магазине")
            amount = st.number_input("Сумма (сом)", min_value=0.01, value=500.0,
                                     step=10.0, format="%.2f")
            category = st.selectbox(
                "Категория",
                options=list(CATEGORY_LABELS.keys()),
                format_func=lambda x: CATEGORY_LABELS[x]
            )
            note = st.text_area("Заметка (необязательно)", placeholder="Доп. информация...",
                                height=80)
            submitted = st.form_submit_button("Добавить расход →", use_container_width=True)

            if submitted:
                if not title:
                    st.error("Введи название")
                elif amount <= 0:
                    st.error("Сумма должна быть больше 0")
                else:
                    ok, data = api.add_expense(title, amount, category, note)
                    if ok:
                        st.success(f"✅ Добавлено: {title} — {amount:,.0f} с")
                        st.rerun()
                    else:
                        st.error(f"❌ Ошибка: {data}")

        # ── Category tips ──────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Нормы по категориям")
        norms = [
            ("food", "Еда", "~30% дохода"),
            ("transport", "Транспорт", "~10% дохода"),
            ("fun", "Развлечения", "~10% дохода"),
            ("education", "Образование", "~5% дохода"),
        ]
        for k, lbl, tip in norms:
            color = CATEGORY_COLORS[k]
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px;
                        padding:.5rem .8rem; border-radius:8px; margin-bottom:.4rem;
                        background:rgba(30,45,69,.4); border-left:3px solid {color};">
                <span style="font-size:.85rem; color:#e2e8f0; flex:1;">{CATEGORY_LABELS[k]}</span>
                <span style="font-family:'Space Mono',monospace; font-size:.72rem; color:{color};">{tip}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Expense List ───────────────────────────────────────────────────────────
    with col_list:
        st.markdown("#### 📋 История расходов")

        # Filter
        filter_col1, filter_col2 = st.columns([1, 1])
        with filter_col1:
            filter_cat = st.selectbox(
                "Фильтр по категории",
                ["Все"] + list(CATEGORY_LABELS.keys()),
                format_func=lambda x: "Все категории" if x == "Все" else CATEGORY_LABELS.get(x, x),
                label_visibility="collapsed"
            )
        with filter_col2:
            search = st.text_input("Поиск", placeholder="🔍 Поиск по названию...",
                                   label_visibility="collapsed")

        with st.spinner("Загружаем..."):
            expenses = api.get_expenses(filter_cat if filter_cat != "Все" else None)

        if not expenses:
            st.markdown("""
            <div class="akcha-card" style="text-align:center; padding:2.5rem; color:#64748b;">
                <div style="font-size:2.5rem; margin-bottom:.8rem;">💸</div>
                <div style="font-family:'Syne',sans-serif; font-size:1rem; margin-bottom:.4rem;">
                    Нет расходов
                </div>
                <div style="font-size:.82rem;">Добавь первый расход слева</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Apply search
        if search:
            expenses = [e for e in expenses
                        if search.lower() in e.get("title", "").lower()]

        # Summary bar
        total = sum(float(e.get("amount", 0)) for e in expenses)
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:.6rem 1rem; background:rgba(0,212,170,.08);
                    border:1px solid rgba(0,212,170,.2); border-radius:10px; margin-bottom:1rem;">
            <span style="color:#64748b; font-size:.83rem;">Показано: <b style="color:#e2e8f0">{len(expenses)}</b> записей</span>
            <span style="font-family:'Space Mono',monospace; font-size:.85rem; color:#00d4aa; font-weight:700;">
                Итого: {total:,.0f} с
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Expense cards
        for exp in expenses:
            exp_id = exp.get("id")
            title_e = exp.get("title", "—")
            amount_e = float(exp.get("amount", 0))
            cat_e = exp.get("category", "other")
            date_e = exp.get("date", "")
            note_e = exp.get("note", "")
            color_e = CATEGORY_COLORS.get(cat_e, "#64748b")
            label_e = CATEGORY_LABELS.get(cat_e, cat_e)

            with st.container():
                row1, row2 = st.columns([5, 1])
                with row1:
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; gap:12px;
                                padding:.8rem 1rem; background:var(--card);
                                border:1px solid var(--border); border-radius:12px;
                                border-left:3px solid {color_e}; margin-bottom:.4rem;">
                        <div style="flex:1;">
                            <div style="font-size:.9rem; font-weight:600; color:#e2e8f0;">
                                {title_e}
                            </div>
                            <div style="font-size:.75rem; color:#64748b; margin-top:.15rem;">
                                <span style="color:{color_e};">{label_e}</span>
                                {'&nbsp;·&nbsp;' + note_e[:40] if note_e else ''}
                                &nbsp;·&nbsp; {date_e}
                            </div>
                        </div>
                        <div style="font-family:'Space Mono',monospace; font-size:.95rem;
                                    font-weight:700; color:#e2e8f0; white-space:nowrap;">
                            {amount_e:,.0f} с
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with row2:
                    if st.button("🗑", key=f"del_{exp_id}", help="Удалить"):
                        if api.delete_expense(exp_id):
                            st.rerun()
                        else:
                            st.error("Ошибка")

        # Mini chart of this filtered set
        if len(expenses) > 1:
            st.markdown("<br>**Топ по категориям**")
            df = pd.DataFrame(expenses)
            df["amount"] = df["amount"].astype(float)
            df_cat = df.groupby("category")["amount"].sum().reset_index()
            df_cat["label"] = df_cat["category"].map(CATEGORY_LABELS)
            df_cat["color"] = df_cat["category"].map(CATEGORY_COLORS)
            df_cat = df_cat.sort_values("amount", ascending=False)

            fig = go.Figure(go.Bar(
                x=df_cat["label"], y=df_cat["amount"],
                marker=dict(color=df_cat["color"].tolist(), opacity=.8),
                text=[f"{v:,.0f}" for v in df_cat["amount"]],
                textposition="outside",
                textfont=dict(color="#94a3b8", size=10),
                hovertemplate="%{x}: %{y:,.0f} с<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                height=180,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(tickfont=dict(size=10, color="#64748b"), showgrid=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                bargap=.3,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})