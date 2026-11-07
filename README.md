# ⚡ Marketing A/B Campaign Analysis Dashboard (ZoomCharts Style)

An enterprise-grade, interactive A/B testing analytics dashboard built with **Python**, **Streamlit**, and **Plotly**, styled and structured according to **[ZoomCharts](https://zoomcharts.com)** design standards and grounded 100% on the authentic **`marketing_AB_cleaned.csv`** dataset.

---

## 📊 Grounded on `marketing_AB_cleaned.csv`

Every chart, KPI metric, and filter is calculated directly from the real columns in your dataset:
* **`user id`**: 588,101 unique experiment participants.
* **`test group`**: Treatment (`ad`, 564,577 users) vs. Control (`psa`, 23,524 users).
* **`converted`**: Conversion outcome (`True` vs. `False`), totaling 14,843 purchases.
* **`total ads`**: Exact number of ads seen by each user (14,597,182 total impressions; average 24.8 ads/user).
* **`most ads day`**: Day of week (`Monday` to `Sunday`).
* **`most ads hour`**: Hour of peak exposure (`0` to `23`h).

---

## 🌟 Dashboard Structure (ZoomCharts Visual Architecture)

### 1. **Overview (A/B Test Executive Cockpit)**
- **Left Column**: 5 Executive KPI Scorecard Cards with live dynamic sparklines:
  - **Audience Population**: `588.1K` (Treatment: 96.0% | Control: 4.0%).
  - **Total Impressions**: `14.60M` (Average: 24.8 ads/user).
  - **Conversions**: `14,843` (Overall Conversion Rate: 2.52%).
  - **Treatment CR (`ad`)**: `2.55%` vs Baseline PSA `1.79%` (+0.77% pts).
  - **Relative Lift**: `+43.1%` (**Reject $H_0$**, $p < 0.0001$).
- **Main Area Visuals**:
  - **Donut 1: Audience Allocation by Test Group** (`ad` 96.0% vs. `psa` 4.0%).
  - **Horizontal Combo: Conversions & CR by Day of Week** (Navy CR % bars + Cyan Conversion volume bars).
  - **Donut 2: Conversion Share by Test Group** (`ad` 97.2% vs. `psa` 2.8%).
  - **Hourly Trend (0–23h)**: Dual-axis trend of Total Ads vs. Conversions across the day.
  - **Day-of-Week Dual-Line Chart**: Direct conversion rate comparison between `ad` and `psa` across Monday through Sunday.
  - **Stacked Donuts**: Total impressions by group and conversion share by day part.

---

### 2. **Ad Frequency & Saturation (Dose-Response & Fatigue)**
- **Inflection Point Analysis**: Conversion rate across exposure brackets:
  - `1–2 ads`: 0.19% CR (Ad) vs 0.14% (PSA)
  - `3–5 ads`: 0.32% CR
  - `6–10 ads`: 0.49% CR
  - `11–20 ads`: 0.84% CR
  - `21–50 ads`: **2.92% CR** (sharp acceleration zone!)
  - `51–100 ads`: **11.63% CR** in Ad vs. 5.77% in PSA
  - `100+ ads`: 17.14% CR
- **Log-Scale Exposure Boxplots**: Distribution of ads seen comparing converted vs. non-converted users.
- **Summary Statistics**: Median, 75th percentile, and max ads seen.

---

### 3. **Day & Hour Patterns (Temporal Matrix & Golden Hours)**
- **2D Heatmap Matrix**: Day of Week (Monday–Sunday) $\times$ Hour of Day (0–23h) showing Conversion Rate %.
- **Hourly Bar Chart**: Visualizes conversion efficiency across 24 hours (Green highlights for hours with $\ge 2.8\%$ CR).
- **Dayparting Table**: Breakdown across Night (0–5h), Morning (6–11h), Afternoon (12–16h), Evening (17–21h), and Late Night (22–23h).

---

### 4. **Statistical & ROAS Lab (ROI & Hypothesis Testing)**
- **Frequentist Hypothesis Testing**:
  - Two-proportion Z-test: $Z = 7.37$, $P\text{-value} = 1.7 \times 10^{-13}$.
  - Bell curve visualization with standard normal distribution and observed test statistic.
- **Financial Simulation & ROAS Calculator**:
  - Live input for **CPM** ($ Cost per 1,000 Ads) and **AOV** ($ Average Order Value).
  - Calculates Total Ad Spend, Incremental Conversions, Incremental Revenue, Net Profit, and ROAS %.
  - Sensitivity matrix for varying CPM and AOV scenarios.
- **Raw Respondent Explorer**: In-app search for User ID with CSV download.

---

## 🚀 How to Run

### Option 1: Double-Click Launcher (Windows)
Double-click `launch_dashboard.bat` or run:
```powershell
.\launch_dashboard.ps1
```

### Option 2: Run via Virtual Environment
```powershell
.venv\Scripts\streamlit.exe run app.py
```

The app will open automatically at `http://localhost:8501`.
