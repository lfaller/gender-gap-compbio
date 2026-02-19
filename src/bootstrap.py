"""
Bootstrap statistical analysis for P_female estimates.

Replicates the original Bonham & Stefan (2017) statistical approach.
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd


def bootstrap_pfemale(
    probabilities: List[float],
    n_iterations: int = 1000
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Estimate P_female using bootstrap resampling.

    Given a list of P_female values (0.0–1.0) for a set of authors,
    returns (mean_pfemale, ci_lower, ci_upper) via bootstrap.
    Excludes None and NaN (unknown) values.

    Args:
        probabilities: List of P_female values in [0.0, 1.0] or None/NaN for unknown
        n_iterations: Number of bootstrap iterations (default 1000)

    Returns:
        Tuple of (mean, ci_lower, ci_upper) or (None, None, None) if empty
    """
    # Filter out None and NaN values
    probs = [p for p in probabilities if p is not None and not (isinstance(p, float) and np.isnan(p))]

    if not probs:
        return (None, None, None)

    probs = np.array(probs)
    means = []

    # Bootstrap resampling
    for _ in range(n_iterations):
        sample = np.random.choice(probs, size=len(probs), replace=True)
        means.append(np.mean(sample))

    means = np.array(means)

    return (
        np.mean(means),
        np.percentile(means, 2.5),
        np.percentile(means, 97.5)
    )


def bootstrap_by_group(
    df: pd.DataFrame,
    group_col: str,
    prob_col: str = "p_female",
    n_iterations: int = 1000
) -> pd.DataFrame:
    """
    Run bootstrap analysis grouped by a column.

    Args:
        df: DataFrame with data
        group_col: Column to group by (e.g., 'position', 'year', 'dataset')
        prob_col: Column containing P_female values
        n_iterations: Number of bootstrap iterations

    Returns:
        DataFrame with columns: group, mean, ci_lower, ci_upper, n_samples
    """
    results = []

    for group_val, group_df in df.groupby(group_col):
        probs = group_df[prob_col].tolist()
        mean, ci_lower, ci_upper = bootstrap_pfemale(probs, n_iterations)

        results.append({
            "group": group_val,
            "mean": mean,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "n_samples": len([p for p in probs if p is not None])
        })

    return pd.DataFrame(results)


def bootstrap_by_multiple_groups(
    df: pd.DataFrame,
    group_cols: List[str],
    prob_col: str = "p_female",
    n_iterations: int = 1000
) -> pd.DataFrame:
    """
    Run bootstrap analysis grouped by multiple columns.

    Args:
        df: DataFrame with data
        group_cols: Columns to group by (e.g., ['dataset', 'position', 'year'])
        prob_col: Column containing P_female values
        n_iterations: Number of bootstrap iterations

    Returns:
        DataFrame with results grouped by combinations of group_cols
    """
    results = []

    for group_vals, group_df in df.groupby(group_cols):
        probs = group_df[prob_col].tolist()
        mean, ci_lower, ci_upper = bootstrap_pfemale(probs, n_iterations)

        # Handle both single and multiple grouping columns
        if len(group_cols) == 1:
            row = {group_cols[0]: group_vals}
        else:
            row = {col: val for col, val in zip(group_cols, group_vals)}

        row.update({
            "mean": mean,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "n_samples": len([p for p in probs if p is not None])
        })

        results.append(row)

    return pd.DataFrame(results)


def calculate_trend(
    df: pd.DataFrame,
    year_col: str = "year",
    prob_col: str = "p_female"
) -> Tuple[float, float]:
    """
    Calculate linear trend in P_female over time.

    Args:
        df: DataFrame with data
        year_col: Column containing year
        prob_col: Column containing P_female values

    Returns:
        Tuple of (slope, intercept) for linear fit
    """
    # Filter out None values
    valid_df = df[[year_col, prob_col]].dropna()

    if len(valid_df) < 2:
        return (None, None)

    # Linear fit
    coeffs = np.polyfit(valid_df[year_col], valid_df[prob_col], 1)
    return (coeffs[0], coeffs[1])
