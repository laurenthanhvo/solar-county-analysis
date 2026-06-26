from pathlib import Path
import pandas as pd
import yaml

resources_in = Path("clustering_county/inputs/melek_46regions/resources.yml")
solar_path = Path("clustering_county/outputs/solar_lcoe_resource_groups_wecc_with_county.parquet")

resources_out = Path("clustering_county/outputs/resources_county_all_regions_test.yml")
summary_out = Path("clustering_county/outputs/expected_county_clusters_by_region.csv")

solar = pd.read_parquet(solar_path)

# Regions that have county-enriched solar rows
regions_with_counties = sorted(solar["region"].dropna().unique())

with open(resources_in, "r") as f:
    resources = yaml.safe_load(f)

changed = []

for block in resources["renewables_clusters"]:
    region = block.get("region")
    tech = block.get("technology")

    # Only modify utility-scale solar blocks that have county-enriched rows
    if tech == "utilitypv" and region in regions_with_counties:
        old_bin = block.get("bin", [{}])[0]
        old_mw_per_bin = old_bin.get("mw_per_bin", None)

        block["group"] = ["county_group"]

        # Loose LCOE cutoff so every county remains represented
        block["filter"] = [
            {"feature": "lcoe", "max": 999}
        ]

        # One LCOE bin per county for first strict county-preserving test
        new_bin = {
            "feature": "lcoe",
            "weights": "capacity_mw",
            "q": 1,
        }
        if old_mw_per_bin is not None:
            new_bin["mw_per_bin"] = old_mw_per_bin

        block["bin"] = [new_bin]

        # One capacity-factor cluster per county
        block["cluster"] = [
            {"feature": "cf", "n_clusters": 1, "method": "agg"}
        ]

        changed.append(region)

with open(resources_out, "w") as f:
    yaml.safe_dump(resources, f, sort_keys=False)

summary = (
    solar.groupby("region")
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

summary["q"] = 1
summary["n_clusters_per_county"] = 1
summary["expected_solar_clusters"] = summary["n_counties"]

summary.to_csv(summary_out, index=False)

print("Wrote:", resources_out)
print("Wrote:", summary_out)
print()
print("Modified utilitypv regions:")
for r in changed:
    print("-", r)
print()
print("Number of modified regions:", len(changed))
