# Computed executive summary — SYNTHETIC

{
  "project": "manufacturing",
  "synthetic": true,
  "rows": 720,
  "planned_minutes": 323929.0,
  "downtime_minutes": 23997.97,
  "downtime_rate": 0.07408404310821198,
  "defect_rate": 0.029189937910341343,
  "primary_effect": 0.04366743595922673,
  "ci95": [
    0.03645582175262803,
    0.05050068594364208
  ],
  "p_value": 0.0001999600079984003,
  "spearman_downtime_defects": 0.33485916752649403,
  "decision": "Investigate Line C; require measured pilot before claiming savings.",
  "data_quality": {
    "raw_rows": 722,
    "accepted_rows": 720,
    "rejected_rows": 1,
    "identical_duplicates_removed": 1
  },
  "source_sha256": "5861a7d02dfc95a95293606c4d9152c44c4c4e9e75d44bcdcf20dab5c2ca82d8"
}

Across 720 simulated line-days, downtime consumed 7.4% of planned time. Line C's mean daily downtime rate exceeded the mean of the other three lines by 4.37 percentage points (95% paired-day bootstrap interval 3.65 to 5.05). Prioritize root-cause logging and a controlled maintenance pilot. This generator deliberately makes Line C worse; the result validates the analytical workflow, not an external operational discovery.
