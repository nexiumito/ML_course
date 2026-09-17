import argparse
import pathlib
import re
import datetime
from typing import Optional
from datetime import timezone, datetime

import pandas as pd
import plydata as ply
import git


def get_repo_remote_url(repo_path: pathlib.Path) -> Optional[str]:
    """Get the remote URL of the repository."""
    try:
        repo = git.Repo(repo_path)
        # Get the first (origin) remote's URL
        return next(repo.remotes.origin.urls)
    except:
        return None


def is_classroom_link(repo_path: pathlib.Path) -> bool:
    """Check if the repository is from GitHub Classroom."""
    remote_url = get_repo_remote_url(repo_path)
    if remote_url:
        # Handle both HTTPS and SSH URLs
        if remote_url.startswith("git@github.com:"):
            # Convert SSH URL to HTTPS format for consistent checking
            org_path = remote_url.split("git@github.com:")[-1].replace(".git", "")
            return org_path.startswith("CS-433/")
        else:
            # Direct check for HTTPS URL
            return remote_url.startswith("https://github.com/CS-433/")
    return False


def get_last_commit_date(repo_path: pathlib.Path) -> Optional[datetime]:
    """Get the date of the last commit in the repository."""
    try:
        repo = git.Repo(repo_path)
        return repo.head.commit.committed_datetime
    except:
        return None


def calculate_pass_rate(row):
    """Calculate percentage of passed tests, rounded to nearest percent."""
    test_columns = [
        col
        for col in row.index
        if col not in ["submission_id", "pass_rate", "is_classroom", "on_time"]
    ]
    total_tests = len(test_columns)
    passed_tests = sum(1 for val in row[test_columns] if val == "P")
    return round((passed_tests / total_tests) * 100) if total_tests > 0 else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument(
        "--repos_dir", help="Directory containing the cloned repositories"
    )
    parser.add_argument(
        "--deadline", help="Deadline in ISO format (e.g., 2024-11-01T16:05:00+01:00)"
    )
    args = parser.parse_args()

    directory = pathlib.Path(args.directory)
    repos_dir = pathlib.Path(args.repos_dir) if args.repos_dir else None
    deadline = datetime.fromisoformat(args.deadline) if args.deadline else None

    # Read and combine all CSV files
    dfs = []
    for file in directory.glob("*.csv"):
        df = pd.read_csv(file, index_col=0) >> ply.define(
            submission_id=f"'{file.stem}'"
        )
        dfs.append(df)

    df_concat = pd.concat(dfs)
    df_pivot = df_concat.reset_index() >> ply.tidy.pivot_wider(
        names_from="id", values_from="status", id_cols="submission_id"
    )

    # Replace status values with single letters
    df_pivot = df_pivot.applymap(
        lambda s: (
            "F"
            if s == "failed"
            else ("E" if s == "error" else ("P" if s == "passed" else s))
        )
    )

    # Simplify column names
    def simplify_column_names(name: str) -> str:
        name = re.sub(r"-extra_args.*]", "]", name)
        name = re.sub(r"test_project1_", "", name)
        name = re.sub(r".py::test", "", name)
        return name

    df_pivot.columns = [simplify_column_names(c) for c in df_pivot.columns]

    # Add analysis columns
    df_pivot["pass_rate"] = df_pivot.apply(calculate_pass_rate, axis=1)
    df_pivot["is_classroom"] = False
    df_pivot["on_time"] = None

    # Add repository information if repos directory is provided
    if repos_dir:
        for idx, row in df_pivot.iterrows():
            submission_id = row["submission_id"].strip("'")
            repo_path = repos_dir / submission_id

            if repo_path.exists():
                df_pivot.at[idx, "is_classroom"] = is_classroom_link(repo_path)

                if deadline:
                    last_commit = get_last_commit_date(repo_path)
                    if last_commit is not None:
                        df_pivot.at[idx, "on_time"] = last_commit <= deadline

    # Reorder columns
    analysis_cols = ["submission_id", "pass_rate", "is_classroom", "on_time"]
    test_cols = [col for col in df_pivot.columns if col not in analysis_cols]
    df_pivot = df_pivot[analysis_cols + test_cols]

    # Write results
    results_file = directory.with_suffix(".csv")
    df_pivot.to_csv(results_file, index=False)
    print(f"Written aggregated results to {results_file}")

    # Print summary statistics
    print("\nSummary:")
    print(f"Total submissions: {len(df_pivot)}")
    print(f"Average pass rate: {df_pivot['pass_rate'].mean():.1f}%")
    print(f"Classroom submissions: {df_pivot['is_classroom'].sum()}")
    if deadline:
        on_time = df_pivot["on_time"].sum()
        print(f"On-time submissions: {on_time} ({on_time/len(df_pivot)*100:.1f}%)")


if __name__ == "__main__":
    main()
