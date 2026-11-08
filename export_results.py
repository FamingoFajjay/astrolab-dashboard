from pathlib import Path
import json

import pandas as pd

from data_utils import (
    load_csv,
    get_lightcurve_stats,
    get_summary_values,
)

lc = load_csv("lightcurve")
summary_df = load_csv("summary")

stats = get_lightcurve_stats(lc)
results = get_summary_values(summary_df)

reference = 6.27
difference = abs(results["best_period_days"] - reference)

report = {
    "target": "Pi Mensae",
    "tic_id": "261136679",
    "mission": "TESS",
    "sector": 1,
    "observations": stats["count"],
    "time_span_days": stats["time_span_days"],
    "median_flux": stats["median_flux"],
    "best_bls_period_days": results["best_period_days"],
    "transit_duration_days": results["best_duration_days"],
    "transit_depth_fraction": results["best_depth"],
    "transit_depth_percent": results["best_depth"] * 100,
    "reference_period_approx_days": reference,
    "absolute_period_difference_days": difference,
    "relative_period_difference_percent": (
        difference / reference * 100
    ),
}

output = Path("results.json")

output.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print(json.dumps(report, indent=2))
print(f"Saved: {output}")