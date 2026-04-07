import streamlit as st
import pandas as pd
import plotly.express as px
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

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter"),
    margin=dict(l=0, r=0, t=30, b=0),
)


def _insight_html(insight: dict) -> str:
    t = insight.get("type", "warning")
    icons = {"success": "✅", "warning": "⚠️", "danger": "🚨"}
    css = {"success": "insight-success", "warning": "insight-warning", "danger": "insight-danger"}
    return f"""
    <div class="insight-card {css.get(t,'insight-warning')}">
        <span style="font-size:1.1rem">{icons.get(t,'💡')}</span>
        <span style="color:#e2e8f0">{insight.get('message','')}</span>
    </div>"""


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#e2e8f0;">
            Дашборд
        </div>
        <div style="color:#64748b; font-size:.9rem;">Твоя финансовая картина за всё время</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Загружаем данные..."):
        stats = api.get_stats()
        expenses_raw = api.get_expenses()

    if not stats:
        st.warning("Не удалось загрузить данные. Проверь подключение к API.")
        return

    income = float(stats.get("income", 0))
    total_expense = float(stats.get("total_expense", 0))
    balance = float(stats.get("balance", 0))
    total_saved = float(stats.get("total_saved", 0))
    by_category = stats.get("by_category", {})
    insights = stats.get("insights", [])

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💰 Доход", f"{income:,.0f} с")
    with c2:
        st.metric("💸 Расходы", f"{total_expense:,.0f} с",
                  delta=f"-{total_expense:,.0f}" if total_expense else None,
                  delta_color="inverse")
    with c3:
        delta_label = "остаток" if balance >= 0 else "дефицит"
        st.metric("🏦 Баланс", f"{balance:,.0f} с",
                  delta=delta_label, delta_color="normal" if balance >= 0 else "inverse")
    with c4:
        st.metric("🎯 Накоплено", f"{total_saved:,.0f} с")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Budget rule 50/30/20 ──────────────────────────────────────────────────
    if income > 0:
        st.markdown("### 📐 Правило 50/30/20")

        needs_pct = round(total_expense / income * 100, 1) if income else 0
        savings_pct = round(balance / income * 100, 1) if income > 0 and balance > 0 else 0

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=needs_pct,
            title={"text": "% расходов от дохода", "font": {"color": "#94a3b8", "size": 13}},
            delta={"reference": 70, "increasing": {"color": "#ef4444"},
                   "decreasing": {"color": "#10b981"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                "bar": {"color": "#00d4aa"},
                "bgcolor": "#111827",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(16,185,129,.15)"},
                    {"range": [50, 70], "color": "rgba(245,158,11,.15)"},
                    {"range": [70, 100], "color": "rgba(239,68,68,.15)"},
                ],
                "threshold": {
                    "line": {"color": "#6366f1", "width": 3},
                    "thickness": .8, "value": 70
                }
            },
            number={"suffix": "%", "font": {"color": "#e2e8f0", "size": 28}}
        ))
        fig_gauge.update_layout(**DARK_LAYOUT, height=220)

        col_gauge, col_rule = st.columns([1, 1])
        with col_gauge:
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
        with col_rule:
            st.markdown("<br>", unsafe_allow_html=True)
            for label, target, actual in [
                ("🟢 Нужды (50%)", 50, needs_pct),
                ("🟡 Желания (30%)", 30, 30 - max(0, needs_pct - 50)),
                ("🔵 Накопления (20%)", 20, savings_pct),
            ]:
                color = "#10b981" if actual <= target else "#ef4444"
                st.markdown(f"""
                <div style="margin-bottom:.8rem;">
                    <div style="display:flex; justify-content:space-between;
                                font-size:.82rem; color:#94a3b8; margin-bottom:.3rem;">
                        <span>{label}</span>
                        <span style="color:{color}; font-family:'Space Mono',monospace;">
                            {actual:.1f}% / {target}%
                        </span>
                    </div>
                    <div class="goal-bar-wrap">
                        <div class="goal-bar-fill" style="width:{min(actual/target*100,100):.1f}%;
                            background:{'linear-gradient(90deg,#10b981,#059669)' if actual<=target
                                        else 'linear-gradient(90deg,#ef4444,#dc2626)'}">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Charts Row ────────────────────────────────────────────────────────────
    st.markdown("### 📊 Расходы по категориям")
    col_pie, col_bar = st.columns([1, 1.3])

    cat_data = [(CATEGORY_LABELS.get(k, k), float(v.get("amount", 0)), k)
                for k, v in by_category.items() if float(v.get("amount", 0)) > 0]

    if cat_data:
        labels, amounts, keys = zip(*cat_data)
        colors = [CATEGORY_COLORS.get(k, "#64748b") for k in keys]

        with col_pie:
            fig_pie = go.Figure(go.Pie(
                labels=labels,
                values=amounts,
                hole=.55,
                marker=dict(colors=colors, line=dict(color="#0a0e1a", width=2)),
                textinfo="percent",
                textfont=dict(color="#e2e8f0", size=11),
                hovertemplate="<b>%{label}</b><br>%{value:,.0f} с<br>%{percent}<extra></extra>",
            ))
            fig_pie.update_layout(**DARK_LAYOUT, height=260,
                                  legend=dict(font=dict(color="#94a3b8", size=11),
                                              bgcolor="rgba(0,0,0,0)"))
            fig_pie.add_annotation(
                text=f"<b>{total_expense:,.0f}</b><br>сом",
                x=.5, y=.5, showarrow=False,
                font=dict(size=14, color="#e2e8f0", family="Syne")
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

        with col_bar:
            df_bar = pd.DataFrame({"Категория": labels, "Сумма": amounts, "Color": colors})
            df_bar = df_bar.sort_values("Сумма", ascending=True)
            fig_bar = go.Figure(go.Bar(
                x=df_bar["Сумма"],
                y=df_bar["Категория"],
                orientation="h",
                marker=dict(color=df_bar["Color"], opacity=.85,
                            line=dict(color="rgba(0,0,0,0)", width=0)),
                text=[f"{v:,.0f} с" for v in df_bar["Сумма"]],
                textposition="outside",
                textfont=dict(color="#94a3b8", size=11),
                hovertemplate="%{y}: %{x:,.0f} с<extra></extra>",
            ))
            fig_bar.update_layout(
                **DARK_LAYOUT, height=260,
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(tickfont=dict(color="#94a3b8", size=11)),
                bargap=.35,
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Добавь расходы, чтобы увидеть аналитику")

    # ── Timeline ──────────────────────────────────────────────────────────────
    if expenses_raw:
        st.markdown("### 📈 История расходов")
        df = pd.DataFrame(expenses_raw)
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = df["amount"].astype(float)
        df_day = df.groupby("date")["amount"].sum().reset_index()
        df_day = df_day.sort_values("date")

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_day["date"], y=df_day["amount"],
            mode="lines+markers",
            line=dict(color="#00d4aa", width=2.5),
            marker=dict(color="#00d4aa", size=6),
            fill="tozeroy",
            fillcolor="rgba(0,212,170,.08)",
            hovertemplate="%{x|%d %b}: %{y:,.0f} с<extra></extra>",
        ))
        fig_line.update_layout(
            **DARK_LAYOUT, height=200,
            xaxis=dict(showgrid=False, tickfont=dict(color="#64748b", size=10)),
            yaxis=dict(showgrid=True, gridcolor="rgba(30,45,69,.5)",
                       tickfont=dict(color="#64748b", size=10), ticksuffix=" с"),
        )
        st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    # ── Insights ──────────────────────────────────────────────────────────────
    if insights:
        st.markdown("### 💡 Инсайты")
        for insight in insights:
            st.markdown(_insight_html(insight), unsafe_allow_html=True)

    # ── Quick add expense ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("➕ Быстро добавить расход"):
        with st.form("quick_expense"):
            qc1, qc2, qc3 = st.columns([2, 1, 1])
            with qc1:
                q_title = st.text_input("Название", placeholder="Обед в кафе")
            with qc2:
                q_amount = st.number_input("Сумма", min_value=0.0, step=50.0, format="%.0f")
            with qc3:
                q_cat = st.selectbox("Категория",
                                     ["food", "transport", "fun", "education", "other"],
                                     format_func=lambda x: CATEGORY_LABELS[x])
            if st.form_submit_button("Добавить ✓", use_container_width=True):
                if q_title and q_amount > 0:
                    ok, _ = api.add_expense(q_title, q_amount, q_cat)
                    if ok:
                        st.success("Расход добавлен! 🎉")
                        st.rerun()
                    else:
                        st.error("Ошибка при добавлении")
                else:
                    st.warning("Заполни название и сумму")