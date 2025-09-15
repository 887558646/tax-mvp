import json
from pathlib import Path


def load_rules(path: str | Path) -> dict:
    """讀取規則 JSON"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_exemption(filing_status: str, dependents: int, elders70: int, rules: dict) -> int:
    """計算免稅額"""
    persons = 1 + (1 if filing_status == "夫妻合併" else 0) + dependents
    base = persons * rules["exemption"]["per_person"]
    extra = elders70 * (rules["exemption"]["elder70"] - rules["exemption"]["per_person"])
    return base + extra


def calc_general_deduction(filing_status: str, itemized: int, rules: dict) -> int:
    """計算一般扣除：標準 vs 列舉取高"""
    standard = (
        rules["deduction"]["standard_couple"]
        if filing_status == "夫妻合併"
        else rules["deduction"]["standard_single"]
    )
    return max(standard, itemized)


def calc_special_deductions(inputs: dict, filing_status: str, rules: dict) -> int:
    """計算特別扣除"""
    s = rules["special"]
    special = 0
    salary_people = 1 if filing_status == "單身" else 2

    # 薪資特別扣除
    special += min(inputs.get("salary", 0), salary_people * s["salary"])

    # 儲蓄投資
    special += min(inputs.get("savings_invest", 0), s["savings_investment"])

    # 幼兒學前
    special += inputs.get("preschool_first", 0) * s["preschool_first"]
    special += inputs.get("preschool_more", 0) * s["preschool_second_plus"]

    # 身障 / 長照
    special += inputs.get("disabled", 0) * s["disability"]
    special += inputs.get("ltc", 0) * s["long_term_care"]

    # 房租特別扣除
    special += min(inputs.get("rent_special", 0), s["rent"])

    return special


def calc_tax(net_income: int, rules: dict) -> int:
    """計算應納稅額"""
    for bracket in rules["brackets"]:
        up_to = bracket["up_to"]
        if up_to == -1 or net_income <= up_to:
            return max(0, int(net_income * bracket["rate"] - bracket["diff"]))
    return 0


def calc_all(inputs: dict, filing_status: str, dependents: int, elders70: int, rules: dict) -> dict:
    """整合計算流程，回傳完整結果 dict"""

    total_income = inputs.get("salary", 0) + inputs.get("other_income", 0)

    exemption = calc_exemption(filing_status, dependents, elders70, rules)

    itemized = (
        inputs.get("donation", 0)
        + inputs.get("insurance", 0)
        + inputs.get("medical_birth", 0)
        + inputs.get("disaster_loss", 0)
        + inputs.get("mortgage_interest", 0)
        + inputs.get("house_rent_itemized", 0)
    )
    general_deduction = calc_general_deduction(filing_status, itemized, rules)

    special = calc_special_deductions(inputs, filing_status, rules)

    net_income = max(0, total_income - exemption - general_deduction - special)

    tax_payable = calc_tax(net_income, rules)
    withheld = inputs.get("withheld", 0)

    final_tax = max(0, tax_payable - withheld)
    refund = max(0, withheld - tax_payable)

    return {
        "total_income": total_income,
        "exemption": exemption,
        "general_deduction": general_deduction,
        "special": special,
        "net_income": net_income,
        "tax_payable": tax_payable,
        "final_tax": final_tax,
        "refund": refund,
        # 🔑 加上年度資訊
        "income_year": rules.get("income_year", "-"),
        "filing_year": rules.get("year", "-"),
    }
