"""
Pipeline skeleton for cstati event analytics.

The full research workflow is implemented in notebooks:

01_data_audit.ipynb
02_identity_resolution.ipynb
03_portfolio_overview.ipynb
04_deep_dive_events.ipynb
05_recommendations.ipynb

This module documents the intended production-style order of steps.
"""


def run_pipeline():
    """
    Placeholder for future production pipeline.

    Planned steps:
    1. Load raw private CSV files.
    2. Validate manual metadata.
    3. Build identity layer.
    4. Build clean identity layer.
    5. Calculate event-level metrics.
    6. Calculate family-level metrics.
    7. Build event transitions and retention proxies.
    8. Export public aggregate outputs.
    """
    raise NotImplementedError(
        "The analysis pipeline is currently implemented in notebooks. "
        "Reusable logic is stored in src modules."
    )


if __name__ == "__main__":
    run_pipeline()


