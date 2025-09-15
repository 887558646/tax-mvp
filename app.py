import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# ✅ 設定中文字型
font_path = Path("assets/NotoSansTC-Regular.ttf")
if font_path.exists():
    matplotlib.rcParams['font.sans-serif'] = [str(font_path)]  # 使用專案內的字型
else:
    # fallback: Windows / macOS 常見中文字型
    matplotlib.rcParams['font.sans-serif'] = ["Microsoft JhengHei", "Heiti TC", "STSong"]

# 避免負號變成方塊
matplotlib.rcParams['axes.unicode_minus'] = False


from pathlib import Path
import json
import matplotlib.font_manager as fm


from engine.calculator import load_rules, calc_all
from engine.pdf_report import build_tax_pdf

# --- 設定 ---
RULES_PATH = Path("rules/2025.json")
rules = load_rules(RULES_PATH)

st.set_page_config(page_title="綜所稅試算系統", layout="wide")
st.title("📑 個人綜所稅試算系統")

# ==============================
# 載入範例資料
# ==============================
st.sidebar.header("📂 範例資料")
sample_choice = st.sidebar.radio("選擇範例", ["不使用", "單身案例", "家庭案例"])
prefill = {}

if sample_choice == "單身案例":
    with open("samples/case_single.json", "r", encoding="utf-8") as f:
        prefill = json.load(f)
elif sample_choice == "家庭案例":
    with open("samples/case_family.json", "r", encoding="utf-8") as f:
        prefill = json.load(f)

# ==============================
# 基本資料輸入
# ==============================
st.header("👤 基本資料")

# --- 家庭狀況 ---
st.markdown("### 🏠 家庭狀況")
col1, col2, col3 = st.columns(3)

with col1:
    filing_status = st.radio(
        "申報方式", ["單身", "夫妻合併"], horizontal=True,
        index=0 if prefill.get("filing_status", "單身") == "單身" else 1
    )
    st.caption("可選擇單身申報或夫妻合併申報。")

with col2:
    dependents = st.number_input("👶 受扶養人數（一般）", 0, 10, prefill.get("dependents", 0))
    st.caption("每位受扶養親屬：免稅額 97,000 元。")

    elders70 = st.number_input("👴 70 歲以上直系尊親屬", 0, 5, prefill.get("elders70", 0))
    st.caption("70 歲以上直系尊親屬：免稅額 145,000 元。")

with col3:
    disabled = st.number_input("♿ 身心障礙人數", 0, 5, prefill.get("disabled", 0))
    st.caption("每位：特別扣除 217,000 元。")

    ltc = st.number_input("🧓 長照特別扣除人數", 0, 5, prefill.get("ltc", 0))
    st.caption("每位長照需求者：特別扣除 120,000 元。")

# 幼兒扣除
col4, col5 = st.columns(2)
with col4:
    preschool_first = st.number_input("👦 幼兒學前（≤6歲）第1名", 0, 1, prefill.get("preschool_first", 0))
    st.caption("第一名：150,000 元特別扣除。")

with col5:
    preschool_more = st.number_input("👧 幼兒學前（≤6歲）第2名起", 0, 5, prefill.get("preschool_more", 0))
    st.caption("每位：225,000 元特別扣除。")

st.markdown("---")

# --- 所得資料 ---
st.markdown("### 💰 所得資料")
col6, col7 = st.columns(2)

with col6:
    salary = st.number_input("💼 薪資所得", 0, 900_000_000, prefill.get("salary", 0), step=1000)
    st.caption("薪資可享特別扣除 218,000 元/人。")

    other_income = st.number_input("📄 其他所得", 0, 900_000_000, prefill.get("other_income", 0), step=1000)
    st.caption("稿費、租金、利息等其他綜合所得。")

with col7:
    withheld = st.number_input("💳 全年預扣稅額＋抵減稅額", 0, 900_000_000, prefill.get("withheld", 0), step=1000)
    st.caption("已由公司預扣或可抵減的稅額。")

st.markdown("---")

# --- 扣除支出（用 expander 收納） ---
with st.expander("📉 扣除支出（可展開調整）", expanded=False):
    col8, col9 = st.columns(2)

    with col8:
        donation_input = st.number_input("🎁 捐贈金額", 0, 900_000_000, prefill.get("donation", 0), step=1000)
        st.caption("上限：綜所總額的 20%。")

        insurance_input = st.number_input("🛡️ 人身保險費", 0, 900_000_000, prefill.get("insurance", 0), step=1000)
        st.caption("每位被保險人：上限 24,000 元。")

    with col9:
        mortgage_input = st.number_input("🏠 房貸利息", 0, 900_000_000, prefill.get("mortgage_interest", 0), step=1000)
        st.caption("自用住宅：上限 300,000 元。")

        rent_input = st.number_input("🏡 房租扣除", 0, 900_000_000, prefill.get("rent_special", 0), step=1000)
        st.caption("無自住房產：上限 180,000 元。")


# --- 現況輸入 ---
base_inputs = {
    "salary": salary,
    "other_income": other_income,
    "withheld": withheld,
    "disabled": disabled,
    "ltc": ltc,
    "preschool_first": preschool_first,
    "preschool_more": preschool_more,
    "donation": donation_input,
    "insurance": insurance_input,
    "mortgage_interest": mortgage_input,
    "rent_special": rent_input,
}

# ==============================
# 現況計算
# ==============================
results_now = calc_all(base_inputs, filing_status, dependents, elders70, rules)

# --- 各項上限（提早算好，節稅建議與模擬都要用） ---
donation_limit = int(results_now["total_income"] * rules["deduction"].get("donation_limit_rate", 0))
insurance_limit = rules["deduction"].get("insurance_per_person", 0) * (
    1 + dependents + (1 if filing_status == "夫妻合併" else 0)
)
mortgage_limit = rules["deduction"].get("mortgage_interest", 0)
rent_limit = rules["special"].get("rent", 0)

# ==============================
# 節稅建議
# ==============================
st.header("💡 節稅建議")

tips = []

# 免稅額相關
if elders70 == 0:
    tips.append("若有 70 歲以上直系尊親屬，可申報較高的免稅額。")
if dependents == 0:
    tips.append("檢查是否有可扶養親屬，若有可增加免稅額。")

# 特別扣除相關
if salary > 0:
    tips.append("確認薪資特別扣除是否已達上限（218,000 元/人）。")
if preschool_first == 0 and preschool_more == 0:
    tips.append("若有 6 歲以下子女，可申報幼兒學前特別扣除。")
if disabled == 0:
    tips.append("若有身心障礙親屬，可申報身障特別扣除（217,000 元/人）。")
if ltc == 0:
    tips.append("若有長照需求親屬，可申報長照特別扣除（120,000 元/人）。")

# 列舉 / 標準扣除比較
standard_single = rules["deduction"]["standard_single"]
standard_couple = rules["deduction"]["standard_couple"]
standard = standard_couple if filing_status == "夫妻合併" else standard_single
if results_now["general_deduction"] == standard:
    tips.append("目前使用標準扣除額，若列舉支出較高可改採列舉。")
else:
    tips.append("目前使用列舉扣除，若支出較少可改採標準扣除。")

# 房租 / 房貸檢查
if rent_input > 0 and mortgage_input > 0:
    tips.append("房租扣除與房貸利息扣除不可同時使用，請確認選擇最有利方案。")

# 捐贈 / 保險提醒
if donation_limit > 0 and donation_input < donation_limit:
    tips.append(f"捐贈扣除額上限為綜所總額 20%（{donation_limit:,} 元），尚有可申報空間。")
if insurance_limit > 0 and insurance_input < insurance_limit:
    tips.append(f"人身保險費扣除上限為 {insurance_limit:,} 元，可再增加保險費用。")

# 退稅提醒
if results_now["refund"] > 0:
    tips.append(f"你有退稅 {results_now['refund']:,} 元，建議調整預扣稅率，避免資金被政府佔用。")

# 顯示建議
if tips:
    for t in tips:
        st.markdown(f"- {t}")
else:
    st.info("目前無額外節稅建議。")

# 👉 存進 session_state，避免 PDF 區塊 rerun 時丟失
st.session_state["tips"] = tips



# ==============================
# 情境模擬
# ==============================
st.header("🎯 情境模擬")

# --- 模擬拉桿（帶入欄位數值，再可調整） ---
col1, col2 = st.columns(2)
with col1:
    if donation_limit <= 0:
        sim_donation = donation_input
        st.caption("⚠️ 綜合所得總額為 0，捐贈無法抵稅。")
    else:
        default_donation = min(donation_input, donation_limit)
        sim_donation = st.slider(
            "捐贈金額（模擬）",
            0,
            donation_limit,
            default_donation,
            step=10_000 if donation_limit >= 10_000 else 1_000
        )
        st.caption(f"💡 捐贈扣除額上限：綜所總額 20%（上限 {donation_limit:,} 元）")

with col2:
    if insurance_limit <= 0:
        sim_insurance = insurance_input
        st.caption("⚠️ 無可適用的被保險人，保險費無法抵稅。")
    else:
        default_insurance = min(insurance_input, insurance_limit)
        sim_insurance = st.slider(
            "人身保險費（模擬）",
            0,
            insurance_limit,
            default_insurance,
            step=1_000 if insurance_limit >= 1_000 else 100
        )
        st.caption(f"💡 保險費扣除上限：每人 24,000 元（上限 {insurance_limit:,} 元）")

col3, col4 = st.columns(2)
with col3:
    if mortgage_limit <= 0:
        sim_mortgage = mortgage_input
        st.caption("⚠️ 房貸利息無法抵稅。")
    else:
        default_mortgage = min(mortgage_input, mortgage_limit)
        sim_mortgage = st.slider(
            "房貸利息（模擬）",
            0,
            mortgage_limit,
            default_mortgage,
            step=10_000 if mortgage_limit >= 10_000 else 1_000
        )
        st.caption("💡 房貸利息扣除上限：300,000 元")

with col4:
    if rent_limit <= 0:
        sim_rent = rent_input
        st.caption("⚠️ 房租特別扣除不可用。")
    else:
        default_rent = min(rent_input, rent_limit)
        sim_rent = st.slider(
            "房租扣除（模擬）",
            0,
            rent_limit,
            default_rent,
            step=10_000 if rent_limit >= 10_000 else 1_000
        )
        st.caption("💡 房租特別扣除上限：180,000 元（無自住房產才可用）")

# --- 模擬計算（覆蓋拉桿值）
inputs_sim = base_inputs.copy()
inputs_sim.update({
    "donation": sim_donation,
    "insurance": sim_insurance,
    "mortgage_interest": sim_mortgage,
    "rent_special": sim_rent,
})
results_sim = calc_all(inputs_sim, filing_status, dependents, elders70, rules)

# ==============================
# 節稅效果
# ==============================
diff_tax = results_now["tax_payable"] - results_sim["tax_payable"]
diff_net = results_sim["net_income"] - results_now["net_income"]

if diff_tax > 0:
    if diff_net >= 0:
        st.success(f"✅ 模擬情境下，應納稅額比現況少 **{diff_tax:,.0f} 元**，淨所得增加 {diff_net:,.0f} 元。")
    else:
        st.success(f"✅ 模擬情境下，應納稅額比現況少 **{diff_tax:,.0f} 元**，但淨所得減少 {abs(diff_net):,.0f} 元。")
elif diff_tax == 0:
    if diff_net == 0:
        st.info("ℹ️ 模擬情境下，應納稅額與淨所得皆與現況相同。")
    elif diff_net > 0:
        st.info(f"ℹ️ 模擬情境下，應納稅額相同，但淨所得增加 {diff_net:,.0f} 元。")
    else:
        st.info(f"ℹ️ 模擬情境下，應納稅額相同，但淨所得減少 {abs(diff_net):,.0f} 元。")
else:
    if diff_net >= 0:
        st.warning(f"⚠️ 模擬情境下，應納稅額反而增加 **{abs(diff_tax):,.0f} 元**，但淨所得增加 {diff_net:,.0f} 元。")
    else:
        st.warning(f"⚠️ 模擬情境下，應納稅額反而增加 **{abs(diff_tax):,.0f} 元**，且淨所得減少 {abs(diff_net):,.0f} 元。")


# ==============================
# 圖表 (6:4)
# ==============================
import matplotlib.ticker as ticker  
from matplotlib import font_manager as fm

# ✅ 改成字型檔案路徑（不是字型名稱）
font_path = "assets/NotoSansTC-Regular.ttf"  
font_prop = fm.FontProperties(fname=font_path)

col1, col2 = st.columns([0.6, 0.4])

with col1:
    labels = ["現況_應納稅額", "模擬_應納稅額", "現況_淨所得", "模擬_淨所得"]
    values = [
        results_now["tax_payable"], results_sim["tax_payable"],
        results_now["net_income"], results_sim["net_income"]
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=["#1f77b4", "#ff7f0e", "#1f77b4", "#ff7f0e"])

    # ✅ 用字型檔案指定中文字型
    ax.set_ylabel("金額 (NT$)", fontproperties=font_prop)
    ax.set_title("現況 vs 模擬", fontproperties=font_prop)

    # ✅ X 軸標籤也套字型
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontproperties=font_prop)

    # ✅ 關閉科學記號顯示
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

    # Y 軸範圍
    ymax = max(values) * 1.1 if max(values) > 0 else 1
    ax.set_ylim(0, ymax)

    # 在柱狀圖上顯示數字（同樣套字型）
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontproperties=font_prop)

    st.pyplot(fig)
    
with col2:
    df = pd.DataFrame({
        "項目": ["應納稅額", "淨所得"],
        "現況": [results_now["tax_payable"], results_now["net_income"]],
        "模擬": [results_sim["tax_payable"], results_sim["net_income"]],
        "差異": [diff_tax, diff_net]
    })
    st.table(df)

# ==============================
# PDF 下載
# ==============================
st.header("📥 產出 PDF 報告")

tips_for_pdf = st.session_state.get("tips", [])

pdf_bytes, filename = build_tax_pdf(results_now, tips_for_pdf)

st.download_button(
    label="📥 下載 PDF",
    data=pdf_bytes,
    file_name=filename,
    mime="application/pdf",
)

