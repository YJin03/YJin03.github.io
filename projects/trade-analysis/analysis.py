from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 학습용 가상 데이터: 실제 무역 통계가 아닙니다.
months = pd.date_range("2025-01-01", periods=12, freq="MS")
countries = ["미국", "중국", "일본", "베트남"]
products = ["반도체", "자동차", "화학제품"]
rows = []

for month_idx, month in enumerate(months):
    for country_idx, country in enumerate(countries):
        for product_idx, product in enumerate(products):
            base = 90 + country_idx * 18 + product_idx * 24
            seasonal = 1 + 0.12 * ((month_idx % 4) / 3)
            export_value = round(base * seasonal + month_idx * 2.5, 2)
            import_value = round(
                base * 0.78 + country_idx * 5 + (11 - month_idx) * 1.2, 2
            )
            rows.append(
                {
                    "month": month,
                    "country": country,
                    "product": product,
                    "export_musd": export_value,
                    "import_musd": import_value,
                }
            )

df = pd.DataFrame(rows)
df.to_csv(DATA_DIR / "trade_sample.csv", index=False, encoding="utf-8-sig")

# 기본 점검
df["month"] = pd.to_datetime(df["month"])
print("행/열:", df.shape)
print("결측치 수:", int(df.isna().sum().sum()))
print("중복 행 수:", int(df.duplicated().sum()))

# 파생 지표 및 집계
df["trade_balance_musd"] = df["export_musd"] - df["import_musd"]
monthly = (
    df.groupby("month")[["export_musd", "import_musd"]]
    .sum()
    .sort_index()
)
monthly["export_mom_pct"] = monthly["export_musd"].pct_change() * 100

country_balance = (
    df.groupby("country")["trade_balance_musd"]
    .sum()
    .sort_values()
)

# 시각화 1: 월별 수출입 추이
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly["export_musd"], marker="o", label="Export")
plt.plot(monthly.index, monthly["import_musd"], marker="o", label="Import")
plt.title("Monthly Export and Import (Synthetic Data)")
plt.xlabel("Month")
plt.ylabel("Value (million USD, synthetic)")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monthly_trade.png", dpi=160)
plt.close()

# 시각화 2: 교역국별 무역수지
plt.figure(figsize=(8, 5))
country_balance.plot(kind="bar")
plt.title("Trade Balance by Country (Synthetic Data)")
plt.xlabel("Country")
plt.ylabel("Trade balance (million USD, synthetic)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "balance_by_country.png", dpi=160)
plt.close()

print("\n월별 집계 미리보기")
print(monthly.round(2).head())
print("\n교역국별 무역수지 (가상 수치)")
print(country_balance.round(2))
print("\n완료: data/ 및 outputs/ 폴더를 확인하세요.")
