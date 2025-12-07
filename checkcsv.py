import pandas as pd

# Load your exported CSV
df = pd.read_csv("data/actuals_latest.csv")

# Row count in CSV
print("CSV row count:", len(df))

# Same top 5 SKUs by sales & units
print(
    df.groupby("sku")[["total_units_sold", "total_order_value"]]
    .sum()
    .sort_values("total_order_value", ascending=False)
    .head()
)
