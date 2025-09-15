def make_advice(inputs: dict, filing_status: str, results: dict, rules: dict) -> list[str]:
    """
    根據輸入與計算結果，回傳節稅建議（符合台灣現行規則）。
    """

    tips = []

    # -----------------------------
    # 標準 vs 列舉
    # -----------------------------
    itemized = (
        inputs.get("donation", 0)
        + inputs.get("insurance", 0)
        + inputs.get("medical_birth", 0)
        + inputs.get("disaster_loss", 0)
        + min(inputs.get("mortgage_interest", 0), 300000)  # 房貸利息上限
        + min(inputs.get("house_rent_itemized", 0), 120000)  # 房屋租金列舉上限
    )
    standard = (
        rules["deduction"]["standard_couple"]
        if filing_status == "夫妻合併"
        else rules["deduction"]["standard_single"]
    )
    if itemized < standard:
        tips.append("你的列舉扣除低於標準扣除，建議改採標準扣除。")

    # -----------------------------
    # 捐贈上限：20% 綜所總額
    # -----------------------------
    donation_limit = results["total_income"] * 0.2
    if inputs.get("donation", 0) > donation_limit:
        tips.append(f"捐贈超過總所得 20% 上限（{donation_limit:,.0f}），超過部分不予扣除。")

    # -----------------------------
    # 保險費：每人 24,000
    # -----------------------------
    if inputs.get("insurance", 0) > 24000:
        tips.append("保險費列舉扣除每人上限 24,000 元，超過部分不計。")

    # -----------------------------
    # 房貸利息：上限 300,000
    # -----------------------------
    if inputs.get("mortgage_interest", 0) > 300000:
        tips.append("購屋借款利息列舉扣除上限為 300,000 元，超過部分不計。")

    # -----------------------------
    # 房租排他條件
    # -----------------------------
    if inputs.get("rent_special", 0) > 0 and inputs.get("mortgage_interest", 0) > 0:
        tips.append("房屋租金特別扣除與房貸利息列舉不可同時使用，請依資格擇一。")
    if inputs.get("rent_special", 0) > 0 and inputs.get("house_rent_itemized", 0) > 0:
        tips.append("房屋租金特別扣除與房屋租金列舉不可同時使用，請擇一申報。")

    # -----------------------------
    # 薪資特別扣除
    # -----------------------------
    salary_people = 1 if filing_status == "單身" else 2
    if inputs.get("salary", 0) > salary_people * rules["special"]["salary"]:
        tips.append(f"薪資特別扣除上限為每人 {rules['special']['salary']:,} 元，已達上限。")

    # -----------------------------
    # 儲蓄投資
    # -----------------------------
    if inputs.get("savings_invest", 0) > rules["special"]["savings_investment"]:
        tips.append(f"儲蓄投資特別扣除上限為 {rules['special']['savings_investment']:,} 元，超過部分不計。")

    # -----------------------------
    # 幼兒學前
    # -----------------------------
    if inputs.get("preschool_more", 0) > 0:
        tips.append("幼兒學前第 2 名起，每名上限 225,000 元，已自動套用。")

    # -----------------------------
    # 長照 / 身障
    # -----------------------------
    if inputs.get("disabled", 0) > 0 or inputs.get("ltc", 0) > 0:
        tips.append("請記得備妥長照或身障相關證明文件，以便適用特別扣除。")

    # -----------------------------
    # 補退稅提醒
    # -----------------------------
    if results["final_tax"] > 0:
        tips.append("你的預扣稅額不足，可能需要補稅，建議下年度檢討預扣方式。")
    if results["refund"] > 0:
        tips.append("你有退稅可能，建議下年度調整預扣額，減少政府無息借款。")

    if not tips:
        tips.append("你的扣除配置已接近最有利狀態，建議僅檢查是否有遺漏可用的特別扣除。")

    return tips
