from pathlib import Path
import pandas as pd

BASE = Path("clustering_county")

solar_path = BASE / "inputs/melek_46regions/solar_lcoe_resource_groups.parquet"
county_path = BASE / "inputs/county_outputs/cpa_primary_county_assignment.csv"

out_parquet = BASE / "outputs/solar_lcoe_resource_groups_with_county.parquet"
out_summary = BASE / "outputs/county_counts_by_46region.csv"
out_missing = BASE / "outputs/solar_rows_missing_county.csv"

solar = pd.read_parquet(solar_path)
county = pd.read_csv(county_path)
county = county.rename(columns={"CPA_ID": "cpa_id"})

if "county_fips" in county.columns:
    county["county_fips"] = (
        county["county_fips"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(5)
    )

print("Solar rows:", len(solar))
print("Solar columns:", list(solar.columns))
print("County rows:", len(county))
print("County columns:", list(county.columns))

if "cpa_id" not in solar.columns:
    raise ValueError("Melek solar parquet does not have cpa_id.")

if "cpa_id" not in county.columns:
    raise ValueError("County assignment CSV does not have cpa_id.")

solar["cpa_id"] = solar["cpa_id"].astype(str)
county["cpa_id"] = county["cpa_id"].astype(str)

county_cols = [
    c for c in county.columns
    if c == "cpa_id"
    or "county" in c.lower()
    or "fips" in c.lower()
    or "geoid" in c.lower()
    or "state" in c.lower()
    or "overlap" in c.lower()
]

county_small = county[county_cols].drop_duplicates(subset=["cpa_id"])

merged = solar.merge(
    county_small,
    on="cpa_id",
    how="left",
    validate="many_to_one",
)

if len(merged) != len(solar):
    raise ValueError("Row count changed after merge. Check duplicate cpa_id rows.")

# Pick a county identifier column and standardize it for PowerGenome grouping.
preferred_county_cols = [
    "primary_county_fips",
    "primary_county_geoid",
    "county_fips",
    "county_geoid",
    "GEOID",
    "geoid",
    "county_id",
    "county_name",
    "county",
]

county_col = None
for c in preferred_county_cols:
    if c in merged.columns:
        county_col = c
        break

if county_col is None:
    possible = [c for c in merged.columns if "county" in c.lower() or "fips" in c.lower() or "geoid" in c.lower()]
    raise ValueError(f"Could not identify county column. Possible columns: {possible}")

if county_col == "county_fips":
    merged["county_group"] = (
        merged[county_col]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(5)
    )
else:
    merged["county_group"] = merged[county_col].astype(str)

merged.loc[
    merged["county_group"].isin(["nan", "None", ""]),
    "county_group"
] = pd.NA

missing = merged[merged["county_group"].isna() | (merged["county_group"] == "nan")]
print("Rows missing county:", len(missing))

if len(missing) > 0:
    missing.to_csv(out_missing, index=False)

summary = (
    merged[~(merged["county_group"].isna() | (merged["county_group"] == "nan"))]
    .groupby("region")
    .agg(
        n_counties=("county_group", "nunique"),
        n_sites=("cpa_id", "count"),
        capacity_mw=("capacity_mw", "sum"),
        min_lcoe=("lcoe", "min"),
        avg_lcoe=("lcoe", "mean"),
        max_lcoe=("lcoe", "max"),
    )
    .reset_index()
    .sort_values("region")
)

out_parquet.parent.mkdir(parents=True, exist_ok=True)

merged.to_parquet(out_parquet, index=False)
summary.to_csv(out_summary, index=False)

print("County column used:", county_col)
print("Wrote:", out_parquet)
print("Wrote:", out_summary)
print(summary.to_string(index=False))