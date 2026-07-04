# WECC County-Solar 5-Cluster Validation Outputs

## Main result
- The generated output preserves all expected county-region groups.
- The county-name lookup issue was a display/traceability issue, not a missing-cluster issue.
- A 5 MW capacity threshold appears to be the safest tested threshold if we want to preserve every county-region group.

## Files included
- `gen_info_wecc_county_solar_5clusters_with_county.csv` — 3,514 rows: Generated gen_info rows with county_group and readable county name columns added.
- `county_region_5cluster_validation.csv` — 739 rows: Expected-vs-actual county-region cluster validation table.
- `missing_county_name_rows.csv` — 5 rows: Rows that were missing county names before the manual display-name patch.
- `cluster_count_mismatches.csv` — 2 rows: County-region groups where actual cluster count did not match min(candidate rows, 5).
- `cluster_mismatch_candidate_rows.csv` — 8 rows: Original candidate solar rows for the mismatch county-region groups.
- `cluster_mismatch_actual_gen_info_rows.csv` — 6 rows: Generated gen_info rows for the mismatch county-region groups.
- `capacity_threshold_summary.csv` — 8 rows: Summary of how different gen_capacity_limit_mw thresholds affect retained rows, county-region groups, and counties.
- `low_capacity_utilitypv_rows.csv` — 3,514 rows: Generated UtilityPV rows with low gen_capacity_limit_mw values.
- `resources_wecc_county_solar_5clusters.yml`: resources.yml file used for the 5-cluster county-solar run.

## Files not written automatically
- `threshold_setting_search_matches.csv` was not written because none of these variables existed: ['threshold_setting_search_matches', 'setting_matches', 'threshold_matches']