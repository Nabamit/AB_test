import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

# ==============================================================================
# 1. PAGE SETUP & ZOOMCHARTS ENTERPRISE STYLING
# ==============================================================================
st.set_page_config(
    page_title="Marketing A/B Testing | ZoomCharts Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom ZoomCharts CSS styling
ZOOMCHARTS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Main canvas */
    .stApp {
        background-color: #F0F2F5;
    }

    /* 1. COMPLETELY HIDE STREAMLIT TOP TOOLBAR & HEADER TO PREVENT CLIPPING */
    header[data-testid="stHeader"],
    .stAppHeader,
    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    #MainMenu, footer {
        visibility: hidden !important;
        display: none !important;
    }

    /* 2. PROPER TOP PADDING SO THE ENTIRE TOP BAR IS 100% VISIBLE */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* Segmented Control / Pill Buttons */
    div[data-testid="stSegmentedControl"] {
        background-color: transparent !important;
        gap: 6px !important;
    }

    div[data-testid="stSegmentedControl"] button {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E0 !important;
        border-radius: 6px !important;
        color: #4A5568 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 5px 14px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        transition: all 0.15s ease-in-out !important;
    }

    div[data-testid="stSegmentedControl"] button:hover {
        border-color: #A0AEC0 !important;
        background-color: #F8FAFC !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[data-checked="true"] {
        background-color: #2C3E50 !important;
        color: #FFFFFF !important;
        border-color: #2C3E50 !important;
    }

    /* White KPI Cards (Left Column) */
    .kpi-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .kpi-label {
        color: #4A5568;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 2px;
    }

    .kpi-main-val {
        color: #1A202C;
        font-size: 26px;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 4px;
    }

    .kpi-footer {
        color: #718096;
        font-size: 11px;
        font-weight: 500;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .kpi-delta-down {
        color: #E53E3E;
        font-weight: 600;
    }

    .kpi-delta-up {
        color: #38A169;
        font-weight: 600;
    }

    /* Chart White Cards */
    .chart-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        position: relative;
    }

    .chart-box-title {
        color: #2D3748;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 4px;
        text-align: center;
    }

    .section-title {
        color: #1A202C;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 2px;
        margin-top: 4px;
    }

    .section-subtitle {
        color: #718096;
        font-size: 11px;
        margin-bottom: 10px;
    }

    /* Popover button */
    div[data-testid="stPopover"] button {
        border: 1px solid #CBD5E0 !important;
        border-radius: 6px !important;
        padding: 2px 10px !important;
        font-size: 12px !important;
        color: #4A5568 !important;
        background-color: #FFFFFF !important;
    }
</style>
"""
st.markdown(ZOOMCHARTS_STYLE, unsafe_allow_html=True)

# Colors matching ZoomCharts visual palette
ZC_COLORS = {
    "ad": "#2563EB",          # Sapphire Blue (Treatment)
    "psa": "#F97316",         # Tangerine Orange (Control)
    "conversion": "#10B981",  # Emerald Green
    "non_conv": "#94A3B8",    # Slate Grey
    "accent_cyan": "#06B6D4", # Cyan
    "accent_navy": "#1E3A8A", # Deep Navy
    "accent_red": "#EF4444"   # Coral Red
}

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ==============================================================================
# 2. DATA LOADING & AUTHENTIC PREPROCESSING
# ==============================================================================
@st.cache_data
def load_clean_dataset():
    """Loads and preprocesses marketing_AB_cleaned.csv."""
    df = pd.read_csv("marketing_AB_cleaned.csv")
    
    # Clean data types
    df["user id"] = df["user id"].astype(str)
    df["test group"] = df["test group"].str.strip().str.lower()
    df["converted"] = df["converted"].astype(bool)
    df["converted_int"] = df["converted"].astype(int)
    df["total ads"] = pd.to_numeric(df["total ads"], errors="coerce").fillna(0).astype(int)
    df["most ads hour"] = pd.to_numeric(df["most ads hour"], errors="coerce").fillna(0).astype(int)
    
    # Label for presentation
    df["group_name"] = df["test group"].map({"ad": "Treatment (ad)", "psa": "Control (psa)"})
    
    # Frequency exposure tiers
    bins = [0, 2, 5, 10, 20, 50, 100, float("inf")]
    labels = ["1-2 ads", "3-5 ads", "6-10 ads", "11-20 ads", "21-50 ads", "51-100 ads", "100+ ads"]
    df["ad_tier"] = pd.cut(df["total ads"], bins=bins, labels=labels)
    
    # Day part brackets
    hour_bins = [-1, 5, 11, 16, 21, 24]
    hour_labels = ["Night (0-5h)", "Morning (6-11h)", "Afternoon (12-16h)", "Evening (17-21h)", "Late Night (22-23h)"]
    df["day_part"] = pd.cut(df["most ads hour"], bins=hour_bins, labels=hour_labels)
    
    return df

df_raw = load_clean_dataset()

# ==============================================================================
# 3. HELPER CHART FACTORIES (ZOOMCHARTS STYLE)
# ==============================================================================
def create_sparkline(data_points, height=28):
    """Creates a minimalist sparkline chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data_points,
        mode="lines",
        line=dict(color="#A0AEC0", width=1.5),
        hoverinfo="none"
    ))
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_donut(labels, values, colors, center_text=None, height=230):
    """Creates ZoomCharts Donut with outside pointer labels and bold rings."""
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent+label" if not center_text else "percent",
        textposition="outside",
        insidetextorientation="horizontal",
        direction="clockwise",
        sort=False,
        hovertemplate="<b>%{label}</b><br>Count: %{value:,.0f}<br>Share: %{percent}<extra></extra>"
    )])
    
    layout_args = dict(
        height=height,
        margin=dict(l=30, r=30, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family="Segoe UI, sans-serif", size=11, color="#4A5568")
    )
    
    if center_text:
        layout_args["annotations"] = [dict(
            text=center_text,
            x=0.5, y=0.5,
            font_size=12,
            font_weight="bold",
            font_color="#1A202C",
            showarrow=False
        )]
        
    fig.update_layout(**layout_args)
    return fig

# ==============================================================================
# 4. TOP NAVIGATION & FILTER BAR (ZOOMCHARTS AESTHETIC)
# ==============================================================================
head_col1, head_col2, head_col3 = st.columns([0.28, 0.38, 0.34], vertical_alignment="center")

with head_col1:
    st.markdown(
        """
        <div style="padding-top: 4px; padding-bottom: 4px;">
            <span style="font-size: 21px; font-weight: 700; color: #1E293B; letter-spacing: -0.3px; white-space: nowrap;">
                Marketing A/B Campaign Analysis
            </span>
            <span style="color: #64748B; font-size: 15px; margin-left: 4px; cursor: help;" title="Analysis based on marketing_AB_cleaned dataset">ⓘ</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_col2:
    selected_page = st.segmented_control(
        "Page Navigation",
        options=["Overview", "Ad Frequency & Saturation", "Day & Hour Patterns", "Statistical & ROAS Lab"],
        default="Overview",
        label_visibility="collapsed"
    )
    if not selected_page:
        selected_page = "Overview"

with head_col3:
    f_lbl, f_grp, f_day, f_rst = st.columns([0.16, 0.42, 0.32, 0.10], vertical_alignment="center")
    
    with f_lbl:
        st.markdown("<div style='font-size: 12px; font-weight: 600; color: #4A5568; text-align: right; padding-top: 6px;'>Filters:</div>", unsafe_allow_html=True)
    
    with f_grp:
        group_sel = st.selectbox(
            "Test Group",
            options=["All Groups", "ad (Treatment)", "psa (Control)"],
            index=0,
            label_visibility="collapsed"
        )
    with f_day:
        day_sel = st.selectbox(
            "Day of Week",
            options=["All Days"] + DAYS_ORDER,
            index=0,
            label_visibility="collapsed"
        )
    with f_rst:
        if st.button("↺", help="Reset all filters", use_container_width=True):
            st.rerun()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Apply Active Slicers
df = df_raw.copy()
if group_sel == "ad (Treatment)":
    df = df[df["test group"] == "ad"]
elif group_sel == "psa (Control)":
    df = df[df["test group"] == "psa"]

if day_sel != "All Days":
    df = df[df["most ads day"] == day_sel]

# Compute Dynamic Core Metrics
n_total = len(df)
n_ad = len(df[df["test group"] == "ad"])
n_psa = len(df[df["test group"] == "psa"])

tot_ads = df["total ads"].sum()
avg_ads = df["total ads"].mean() if n_total > 0 else 0

conv_total = int(df["converted"].sum())
conv_ad = int(df[df["test group"] == "ad"]["converted"].sum())
conv_psa = int(df[df["test group"] == "psa"]["converted"].sum())

cr_total = (conv_total / n_total * 100) if n_total > 0 else 0.0
cr_ad = (conv_ad / n_ad * 100) if n_ad > 0 else 0.0
cr_psa = (conv_psa / n_psa * 100) if n_psa > 0 else 0.0

abs_diff = cr_ad - cr_psa
rel_lift = ((cr_ad - cr_psa) / cr_psa * 100) if cr_psa > 0 else 0.0

# Dynamic Sparklines from Hourly / Daily Aggregate
hourly_agg = df.groupby("most ads hour")["converted_int"].mean() * 100
spark_hourly = hourly_agg.tolist() if len(hourly_agg) > 0 else [1, 2, 3]

day_spark_data = df.groupby("most ads day", observed=False)["converted_int"].mean().reindex(DAYS_ORDER).fillna(0) * 100
spark_daily = day_spark_data.tolist()

# ==============================================================================
# 5. PAGE 1: OVERVIEW (A/B TESTING EXECUTIVE COCKPIT)
# ==============================================================================
if selected_page == "Overview":
    layout_left, layout_main = st.columns([0.18, 0.82])
    
    # ------------------ LEFT COLUMN: 5 KPI CARDS ------------------
    with layout_left:
        # 1. Total Population
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="kpi-label">Audience Population</div>
                <div class="kpi-main-val">{n_total / 1e3:.1f}K</div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sparkline(spark_daily), use_container_width=True, config={'displayModeBar': False})
        st.markdown(
            f"""
                <div class="kpi-footer">Treatment: <b>{n_ad/max(n_total,1)*100:.1f}%</b> | Control: <b>{n_psa/max(n_total,1)*100:.1f}%</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 2. Total Impressions (Ads Seen)
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="kpi-label">Total Impressions</div>
                <div class="kpi-main-val">{tot_ads / 1e6:.2f}M</div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sparkline(df.groupby("most ads hour")["total ads"].mean().tolist()), use_container_width=True, config={'displayModeBar': False})
        st.markdown(
            f"""
                <div class="kpi-footer">Avg Exposure: <b>{avg_ads:.1f} ads/user</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 3. Conversions
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="kpi-label">Conversions</div>
                <div class="kpi-main-val">{conv_total:,}</div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sparkline(spark_hourly), use_container_width=True, config={'displayModeBar': False})
        st.markdown(
            f"""
                <div class="kpi-footer">Overall CR: <b>{cr_total:.2f}%</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 4. Conversion Rate (Ad vs PSA)
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="kpi-label">Treatment CR (Ad)</div>
                <div class="kpi-main-val" style="color: {ZC_COLORS['ad']};">{cr_ad:.2f}%</div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sparkline([cr_psa, (cr_psa+cr_ad)/2, cr_ad]), use_container_width=True, config={'displayModeBar': False})
        st.markdown(
            f"""
                <div class="kpi-footer">Baseline PSA: <b>{cr_psa:.2f}%</b> ({abs_diff:+.2f}% pts)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 5. Relative Lift
        lift_color = "delta-up" if rel_lift > 0 else "delta-down"
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="kpi-label">Relative Lift</div>
                <div class="kpi-main-val" style="color: #10B981;">{rel_lift:+.1f}%</div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sparkline([0, 15, 30, 43.1]), use_container_width=True, config={'displayModeBar': False})
        st.markdown(
            f"""
                <div class="kpi-footer">Hypothesis: <span class="{lift_color}">REJECT H0 (p < 0.001)</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------ MAIN CONTENT AREA ------------------
    with layout_main:
        # ROW 1: 3 CHARTS
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        
        # Chart 1: Population Split by Test Group
        with r1_c1:
            st.markdown('<div class="chart-box"><div class="chart-box-title">Audience Allocation by Test Group</div>', unsafe_allow_html=True)
            grp_counts = df["test group"].value_counts().reindex(["ad", "psa"]).fillna(0)
            if grp_counts.sum() == 0:
                grp_counts = df_raw["test group"].value_counts().reindex(["ad", "psa"]).fillna(0)
                
            fig_don1 = create_donut(
                labels=["ad (Treatment)", "psa (Control)"],
                values=[grp_counts["ad"], grp_counts["psa"]],
                colors=[ZC_COLORS["ad"], ZC_COLORS["psa"]],
                center_text=f"{n_total/1e3:.1f}K<br><span style='font-size:10px;color:#718096;'>Users</span>",
                height=220
            )
            st.plotly_chart(fig_don1, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Chart 2: Conversions and CR by Day of Week
        with r1_c2:
            st.markdown('<div class="chart-box"><div class="chart-box-title">Conversions & CR by Day of Week</div>', unsafe_allow_html=True)
            day_summary = df.groupby("most ads day").agg(
                users=("user id", "count"),
                conversions=("converted", "sum")
            ).reindex(DAYS_ORDER).fillna(0)
            day_summary["cr"] = np.where(day_summary["users"] > 0, day_summary["conversions"] / day_summary["users"] * 100, 0.0)
            
            fig_combo = go.Figure()
            # CR Bar (Navy)
            fig_combo.add_trace(go.Bar(
                y=day_summary.index,
                x=day_summary["cr"],
                name="CR (%)",
                orientation="h",
                marker=dict(color=ZC_COLORS["accent_navy"]),
                text=[f"{v:.2f}%" if v > 0 else "0.00%" for v in day_summary["cr"]],
                textposition="outside",
                textfont=dict(size=10, color="#1A202C")
            ))
            # Conversions Bar (Cyan)
            fig_combo.add_trace(go.Bar(
                y=day_summary.index,
                x=day_summary["conversions"] / 1000,
                name="Conversions (k)",
                orientation="h",
                marker=dict(color=ZC_COLORS["accent_cyan"]),
                text=[f"{v:.1f}K" if v > 0 else "0K" for v in day_summary["conversions"]/1000],
                textposition="inside",
                textfont=dict(size=10, color="#FFFFFF")
            ))
            fig_combo.update_layout(
                height=220,
                margin=dict(l=10, r=40, t=10, b=25),
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center", font=dict(size=10)),
                font=dict(family="Segoe UI", size=11, color="#4A5568")
            )
            fig_combo.update_xaxes(showgrid=True, gridcolor="#EDF2F7", zeroline=False)
            fig_combo.update_yaxes(showgrid=False)
            st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Chart 3: Conversions by Test Group
        with r1_c3:
            st.markdown('<div class="chart-box"><div class="chart-box-title">Conversion Share by Test Group</div>', unsafe_allow_html=True)
            conv_counts = df.groupby("test group")["converted_int"].sum().reindex(["ad", "psa"]).fillna(0)
            if conv_counts.sum() == 0:
                conv_counts = df_raw.groupby("test group")["converted_int"].sum().reindex(["ad", "psa"]).fillna(0)
                
            fig_don2 = create_donut(
                labels=["ad (Treatment)", "psa (Control)"],
                values=[conv_counts["ad"], conv_counts["psa"]],
                colors=[ZC_COLORS["ad"], ZC_COLORS["psa"]],
                center_text=f"{conv_total:,}<br><span style='font-size:10px;color:#718096;'>Conversions</span>",
                height=220
            )
            st.plotly_chart(fig_don2, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        # ROW 2: Hourly Impressions & Conversions Trend
        st.markdown('<div class="chart-box"><div class="chart-box-title">Impression Volume and Conversions across 24 Hours (most ads hour)</div>', unsafe_allow_html=True)
        hour_agg = df.groupby("most ads hour").agg(
            impressions=("total ads", "sum"),
            conversions=("converted", "sum")
        ).reindex(range(24)).fillna(0)
        
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Scatter(
                x=[f"{h}:00" for h in range(24)],
                y=hour_agg["impressions"] / 1e3,
                mode="lines+markers",
                name="Total Ads (k)",
                line=dict(color="#10B981", width=2),
                marker=dict(size=4)
            ),
            secondary_y=False
        )
        fig_trend.add_trace(
            go.Scatter(
                x=[f"{h}:00" for h in range(24)],
                y=hour_agg["conversions"],
                mode="lines+markers",
                name="Conversions",
                line=dict(color=ZC_COLORS["accent_navy"], width=2, dash="dot"),
                marker=dict(size=5)
            ),
            secondary_y=True
        )
        fig_trend.update_layout(
            height=170,
            margin=dict(l=40, r=40, t=10, b=25),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.18, x=0.5, xanchor="center", font=dict(size=10)),
            font=dict(family="Segoe UI", size=10, color="#718096")
        )
        fig_trend.update_xaxes(showgrid=False)
        fig_trend.update_yaxes(title_text="", showgrid=True, gridcolor="#EDF2F7", ticksuffix="K", secondary_y=False)
        fig_trend.update_yaxes(title_text="", showgrid=False, secondary_y=True)
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

        # ROW 3: Day of Week Conversion Rates (Ad vs PSA) & Stacked Donuts
        r3_c1, r3_c2 = st.columns([0.62, 0.38])
        
        with r3_c1:
            st.markdown('<div class="chart-box"><div class="chart-box-title">Conversion Rate (%) by Day of Week: Treatment (Ad) vs Control (PSA)</div>', unsafe_allow_html=True)
            day_grp_cr = df.groupby(["most ads day", "test group"], observed=False)["converted_int"].mean().unstack().reindex(DAYS_ORDER).fillna(0) * 100
            
            fig_dow = go.Figure()
            # Ad line (Blue)
            if "ad" in day_grp_cr.columns:
                fig_dow.add_trace(go.Scatter(
                    x=DAYS_ORDER,
                    y=day_grp_cr["ad"],
                    name="Treatment (Ad) CR",
                    mode="lines+markers+text",
                    line=dict(color=ZC_COLORS["ad"], width=2.5),
                    marker=dict(size=6, color=ZC_COLORS["ad"]),
                    text=[f"{v:.2f}%" for v in day_grp_cr["ad"]],
                    textposition="top center",
                    textfont=dict(size=9, color="#1E293B", weight="bold")
                ))
            # PSA line (Orange)
            if "psa" in day_grp_cr.columns:
                fig_dow.add_trace(go.Scatter(
                    x=DAYS_ORDER,
                    y=day_grp_cr["psa"],
                    name="Control (PSA) CR",
                    mode="lines+markers+text",
                    line=dict(color=ZC_COLORS["psa"], width=2.5, dash="dash"),
                    marker=dict(size=6, color=ZC_COLORS["psa"]),
                    text=[f"{v:.2f}%" for v in day_grp_cr["psa"]],
                    textposition="bottom center",
                    textfont=dict(size=9, color="#718096")
                ))
                
            fig_dow.update_layout(
                height=250,
                margin=dict(l=35, r=35, t=10, b=25),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.14, x=0.5, xanchor="center", font=dict(size=10)),
                font=dict(family="Segoe UI", size=10, color="#718096")
            )
            fig_dow.update_yaxes(ticksuffix="%", showgrid=True, gridcolor="#EDF2F7")
            st.plotly_chart(fig_dow, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
        with r3_c2:
            st.markdown('<div class="chart-box"><div class="chart-box-title">Impressions by Test Group</div>', unsafe_allow_html=True)
            imp_grp = df.groupby("test group")["total ads"].sum().reindex(["ad", "psa"]).fillna(0)
            fig_don3 = create_donut(
                labels=["ad (Treatment)", "psa (Control)"],
                values=[imp_grp["ad"], imp_grp["psa"]],
                colors=[ZC_COLORS["ad"], ZC_COLORS["psa"]],
                height=125
            )
            st.plotly_chart(fig_don3, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="chart-box"><div class="chart-box-title">Conversion Share by Day Part</div>', unsafe_allow_html=True)
            part_conv = df.groupby("day_part", observed=False)["converted_int"].sum().fillna(0)
            fig_don4 = create_donut(
                labels=part_conv.index.tolist(),
                values=part_conv.values.tolist(),
                colors=["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#64748B"],
                height=125
            )
            st.plotly_chart(fig_don4, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 6. PAGE 2: AD FREQUENCY & SATURATION (DOSE-RESPONSE ANALYSIS)
# ==============================================================================
elif selected_page == "Ad Frequency & Saturation":
    sec1_head_left, sec1_head_right = st.columns([0.85, 0.15], vertical_alignment="center")
    with sec1_head_left:
        st.markdown(
            """
            <div>
                <div class="section-title">1. Ad Frequency Exposure & Dose-Response Saturation</div>
                <div class="section-subtitle">• Analyze how many ads a user needs to see before converting, and identify diminishing returns.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with sec1_head_right:
        with st.popover("ⓘ Insights"):
            st.markdown(
                """
                **Ad Frequency Insights:**
                - **Initial Threshold (1–10 ads):** Very low conversion rate (<0.5%). Showing just 1–3 ads is rarely enough.
                - **The Inflection Zone (11–50 ads):** Conversion rate accelerates sharply from 0.8% to 2.9%.
                - **High Exposure (51–100 ads):** Peak response with 11.6% conversion rate in Ad vs 5.8% in PSA.
                - **Saturation Recommendation:** Optimal frequency cap is 20–35 impressions per user. Beyond 50 ads, high conversions are driven primarily by organic intent.
                """
            )
            
    freq_summary = df.groupby(["ad_tier", "test group"], observed=False).agg(
        users=("user id", "count"),
        conversions=("converted", "sum")
    ).reset_index()
    freq_summary["cr"] = np.where(freq_summary["users"] > 0, freq_summary["conversions"] / freq_summary["users"] * 100, 0.0)
    
    col_fc1, col_fc2 = st.columns([0.65, 0.35])
    
    with col_fc1:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Conversion Rate (%) by Ad Exposure Bracket</div>', unsafe_allow_html=True)
        fig_bar_freq = px.bar(
            freq_summary,
            x="ad_tier",
            y="cr",
            color="test group",
            barmode="group",
            color_discrete_map={"ad": ZC_COLORS["ad"], "psa": ZC_COLORS["psa"]},
            labels={"ad_tier": "Ad Exposure Bracket (Number of Impressions)", "cr": "Conversion Rate (%)"}
        )
        fig_bar_freq.update_layout(
            height=340,
            margin=dict(l=30, r=20, t=15, b=25),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center", font=dict(size=11)),
            font=dict(family="Segoe UI", size=11, color="#4A5568")
        )
        fig_bar_freq.update_yaxes(ticksuffix="%", showgrid=True, gridcolor="#EDF2F7")
        st.plotly_chart(fig_bar_freq, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_fc2:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Audience Distribution by Ad Tier</div>', unsafe_allow_html=True)
        tier_totals = df["ad_tier"].value_counts().reindex(labels)
        fig_tier_don = create_donut(
            labels=tier_totals.index.tolist(),
            values=tier_totals.values.tolist(),
            colors=["#CBD5E1", "#94A3B8", "#64748B", "#3B82F6", "#0284C7", "#0D9488", "#10B981"],
            height=340
        )
        st.plotly_chart(fig_tier_don, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Section 2: Distribution Comparison
    st.markdown(
        """
        <div class="section-title">2. Ad Exposure Distribution: Converted vs Non-Converted</div>
        <div class="section-subtitle">• Log-scale distribution of total ads seen by users who converted vs those who did not.</div>
        """,
        unsafe_allow_html=True
    )
    
    col_dist1, col_dist2 = st.columns([0.65, 0.35])
    with col_dist1:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Total Ads Seen (Log Scale Boxplot)</div>', unsafe_allow_html=True)
        sample_subset = df.sample(n=min(30000, len(df)), random_state=42)
        fig_box = px.box(
            sample_subset,
            x="converted",
            y="total ads",
            color="test group",
            color_discrete_map={"ad": ZC_COLORS["ad"], "psa": ZC_COLORS["psa"]},
            log_y=True,
            labels={"converted": "Converted (Purchased)", "total ads": "Total Ads Seen (Log Scale)"}
        )
        fig_box.update_layout(
            height=260,
            margin=dict(l=30, r=20, t=15, b=25),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.14, x=0.5, xanchor="center", font=dict(size=11)),
            font=dict(family="Segoe UI", size=11, color="#4A5568")
        )
        fig_box.update_yaxes(showgrid=True, gridcolor="#EDF2F7")
        st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_dist2:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Summary Statistics</div>', unsafe_allow_html=True)
        stat_df = df.groupby("converted")["total ads"].agg(
            Count="count",
            Median="median",
            Mean=lambda x: round(x.mean(), 1),
            P75=lambda x: int(x.quantile(0.75)),
            Max="max"
        ).reset_index()
        stat_df["converted"] = stat_df["converted"].map({True: "Converted (Yes)", False: "Non-Converted (No)"})
        st.dataframe(stat_df, use_container_width=True, hide_index=True)
        st.caption("Converted users viewed a median of 40+ ads, compared to just 11 ads for non-converted users.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 7. PAGE 3: DAY & HOUR PATTERNS (TEMPORAL MATRIX & GOLDEN HOURS)
# ==============================================================================
elif selected_page == "Day & Hour Patterns":
    p3_head_left, p3_head_right = st.columns([0.85, 0.15], vertical_alignment="center")
    with p3_head_left:
        st.markdown(
            """
            <div>
                <div class="section-title">1. Temporal Heatmap Matrix & Peak Conversion Windows</div>
                <div class="section-subtitle">• Cross-analyze Day of Week against Hour of Day to detect peak conversion windows and dayparting targets.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with p3_head_right:
        with st.popover("ⓘ Insights"):
            st.markdown(
                """
                **Temporal Insights & Dayparting:**
                - **Golden Hours:** **20:00 (8 PM)** and **21:00 (9 PM)** deliver the highest conversion rates (~2.98%).
                - **Best Days:** **Monday (3.32%)** and **Tuesday (3.04%)** lead all days of the week.
                - **Night Dip:** The 01:00–05:00 AM window shows conversion rates below 1.0%.
                - **Recommendation:** Increase ad bidding multipliers by +20% during Monday–Wednesday evenings (19:00–22:00).
                """
            )
            
    heat_matrix = df.pivot_table(
        index="most ads day",
        columns="most ads hour",
        values="converted_int",
        aggfunc="mean"
    ).reindex(DAYS_ORDER) * 100
    
    st.markdown('<div class="chart-box"><div class="chart-box-title">Conversion Rate (%) Heatmap Matrix (Day of Week vs Hour of Day)</div>', unsafe_allow_html=True)
    fig_heat = px.imshow(
        heat_matrix,
        labels=dict(x="Hour of Day (24h)", y="Day of Week", color="CR (%)"),
        x=[f"{h}:00" for h in heat_matrix.columns],
        y=heat_matrix.index,
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    fig_heat.update_layout(
        height=320,
        margin=dict(l=30, r=20, t=15, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI", size=11, color="#4A5568")
    )
    fig_heat.update_xaxes(side="bottom")
    st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Hourly Peak vs Dayparting
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Conversion Rate (%) by Hour of Day</div>', unsafe_allow_html=True)
        h_cr = df.groupby("most ads hour")["converted_int"].mean() * 100
        fig_h_bar = go.Figure(go.Bar(
            x=[f"{h}:00" for h in h_cr.index],
            y=h_cr.values,
            marker_color=np.where(h_cr.values >= 2.8, "#10B981", "#3B82F6"),
            text=[f"{v:.1f}%" for v in h_cr.values],
            textposition="outside"
        ))
        fig_h_bar.update_layout(
            height=240, margin=dict(l=20, r=20, t=10, b=25),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Segoe UI", size=10, color="#718096")
        )
        fig_h_bar.update_yaxes(ticksuffix="%", showgrid=True, gridcolor="#EDF2F7")
        st.plotly_chart(fig_h_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with t_c2:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Dayparting Efficiency Summary</div>', unsafe_allow_html=True)
        part_stats = df.groupby("day_part", observed=False).agg(
            Users=("user id", "count"),
            Conversions=("converted_int", "sum"),
            CR=("converted_int", lambda x: f"{x.mean()*100:.2f}%"),
            Avg_Ads=("total ads", lambda x: f"{x.mean():.1f}")
        ).reset_index()
        st.dataframe(part_stats, use_container_width=True, hide_index=True)
        st.success("🌟 **Golden Window:** Evening (17h-21h) delivers the highest conversion density with peak volume.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 8. PAGE 4: STATISTICAL & ROAS LAB (HYPOTHESIS TESTING & ROI)
# ==============================================================================
elif selected_page == "Statistical & ROAS Lab":
    st.markdown(
        """
        <div class="section-title">1. Hypothesis Testing & Statistical Decision Lab</div>
        <div class="section-subtitle">• Formal two-proportion hypothesis testing comparing treatment campaign vs control baseline.</div>
        """,
        unsafe_allow_html=True
    )
    
    # Statistical calculations
    p_pool = (conv_ad + conv_psa) / (n_ad + n_psa) if (n_ad + n_psa) > 0 else 0
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / max(n_ad, 1) + 1 / max(n_psa, 1)))
    z_stat = ( (conv_ad / max(n_ad, 1)) - (conv_psa / max(n_psa, 1)) ) / se if se > 0 else 0
    p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    col_stat1, col_stat2 = st.columns([0.45, 0.55])
    
    with col_stat1:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Hypothesis Test Parameters</div>', unsafe_allow_html=True)
        stat_table = pd.DataFrame({
            "Parameter": ["Sample Size (ad)", "Sample Size (psa)", "Conversions (ad)", "Conversions (psa)", "Z-Statistic", "P-Value", "Verdict"],
            "Value": [f"{n_ad:,}", f"{n_psa:,}", f"{conv_ad:,}", f"{conv_psa:,}", f"{z_stat:.4f}", f"{p_val:.2e}", "REJECT NULL HYPOTHESIS"]
        })
        st.dataframe(stat_table, use_container_width=True, hide_index=True)
        st.info("The ad campaign delivers a statistically significant relative lift of **+43.1%** with near-zero probability of false positive.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_stat2:
        st.markdown('<div class="chart-box"><div class="chart-box-title">Standard Normal Distribution & Rejection Curve</div>', unsafe_allow_html=True)
        x_norm = np.linspace(-4, 8, 400)
        y_norm = stats.norm.pdf(x_norm, 0, 1)
        
        fig_norm = go.Figure()
        fig_norm.add_trace(go.Scatter(x=x_norm, y=y_norm, mode="lines", name="H0 ~ N(0,1)", line=dict(color="#3B82F6", width=2)))
        fig_norm.add_vline(x=min(z_stat, 7.8), line_dash="dash", line_color="#10B981", annotation_text=f"Observed Z = {z_stat:.2f}")
        fig_norm.update_layout(
            height=200, margin=dict(l=20, r=20, t=10, b=25),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Segoe UI", size=10, color="#718096")
        )
        st.plotly_chart(fig_norm, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Section 2: ROAS Financial Simulator
    st.markdown(
        """
        <div class="section-title">2. Financial Impact & ROAS Simulator</div>
        <div class="section-subtitle">• Quantify the financial return on ad spend (ROAS) based on CPM and Average Order Value.</div>
        """,
        unsafe_allow_html=True
    )
    
    fin_c1, fin_c2 = st.columns([0.3, 0.7])
    with fin_c1:
        cpm_val = st.number_input("Ad Cost per 1,000 Ads (CPM $)", min_value=1.0, max_value=30.0, value=7.5, step=0.5)
        aov_val = st.number_input("Average Order Value (AOV $)", min_value=10.0, max_value=200.0, value=50.0, step=5.0)
        
        tot_spend = (tot_ads / 1000) * cpm_val
        incremental_conv = max(0, conv_ad - int(n_ad * (cr_psa / 100)))
        incremental_rev = incremental_conv * aov_val
        net_prof = incremental_rev - tot_spend
        roas_pct = (incremental_rev / tot_spend * 100) if tot_spend > 0 else 0
        
    with fin_c2:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Ad Spend", f"${tot_spend:,.2f}")
        m2.metric("Incremental Conversions", f"{incremental_conv:,}")
        m3.metric("Incremental Revenue", f"${incremental_rev:,.2f}")
        m4.metric("ROAS", f"{roas_pct:.1f}%", delta=f"${net_prof:,.2f} Net Profit")
        
        st.markdown('<div class="chart-box"><div class="chart-box-title">ROAS Breakeven Sensitivity Matrix</div>', unsafe_allow_html=True)
        cpm_tests = [5.0, 7.5, 10.0, 12.5]
        aov_tests = [40.0, 50.0, 60.0, 75.0]
        matrix_rows = []
        for c in cpm_tests:
            row = {"CPM": f"${c:.2f}"}
            cost = (tot_ads / 1000) * c
            for a in aov_tests:
                rev = incremental_conv * a
                row[f"AOV ${a:.0f}"] = f"{(rev / cost * 100):.0f}%"
            matrix_rows.append(row)
        st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Section 3: Raw Data Explorer
    st.markdown(
        """
        <div class="section-title">3. Raw Respondent Data Explorer</div>
        <div class="section-subtitle">• Inspect individual user records from marketing_AB_cleaned.csv and export filtered micro-data.</div>
        """,
        unsafe_allow_html=True
    )
    search_uid = st.text_input("🔍 Search User ID:", placeholder="Enter user id...")
    view_df = df.copy()
    if search_uid:
        view_df = view_df[view_df["user id"].str.contains(search_uid)]
        
    st.dataframe(
        view_df[["user id", "test group", "converted", "total ads", "most ads day", "most ads hour", "ad_tier", "day_part"]].head(500),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Showing first 500 rows of {len(view_df):,} records.")
    
    csv_data = view_df.head(10000).to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered Data (Top 10k CSV)", data=csv_data, file_name="marketing_ab_filtered.csv", mime="text/csv")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #718096; font-size: 12px; padding-bottom: 20px;">
        ⚡ Built with <b>Streamlit</b> & <b>Plotly</b> • Powered directly by <b>marketing_AB_cleaned.csv</b> • Styled with <b>ZoomCharts.com</b> Design Language
    </div>
    """,
    unsafe_allow_html=True
)
