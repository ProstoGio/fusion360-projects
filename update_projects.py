#!/usr/bin/env python3
"""
update_projects.py

Scans the `projects/` folder and rebuilds the auto-generated projects table
in README.md, between the PROJECTS:START / PROJECTS:END markers.

Convention for each project folder (projects/<name>/):
  - README.md   -> first line: "# Project Title"
                   next non-empty line: one-line description
  - a .stl file -> used as the "Preview" link (first .stl found, alphabetically)

Usage:
    python update_projects.py

Run this from the repo root (same folder as README.md and projects/).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECTS_DIR = ROOT / "projects"
README_PATH = ROOT / "README.md"

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"

TABLE_HEADER = "| Project | Description | Preview |\n|---|---|---|\n"


def read_project_info(project_dir: Path):
    """Extract (title, description) from a project's README.md."""
    readme = project_dir / "README.md"
    title = project_dir.name.replace("-", " ").title()
    description = ""

    if readme.exists():
        lines = [l.strip() for l in readme.read_text(encoding="utf-8").splitlines()]
        # First line: "# Title"
        for line in lines:
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
        # First non-empty, non-heading line after the title = description
        found_title = False
        for line in lines:
            if line.startswith("#"):
                found_title = True
                continue
            if found_title and line:
                description = line
                break

    return title, description


def find_stl(project_dir: Path):
    stl_files = sorted(project_dir.glob("*.stl"))
    return stl_files[0].name if stl_files else None


def build_table_rows():
    rows = []
    if not PROJECTS_DIR.exists():
        return rows

    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        title, description = read_project_info(project_dir)
        stl_name = find_stl(project_dir)

        link = f"./projects/{project_dir.name}"
        preview = f"[STL]({link}/{stl_name})" if stl_name else "—"
        desc = description if description else "*No description yet — add one to this project's README.md*"

        rows.append(f"| [{title}]({link}) | {desc} | {preview} |")

    return rows


def update_readme(rows):
    if not README_PATH.exists():
        raise FileNotFoundError(f"README.md not found at {README_PATH}")

    content = README_PATH.read_text(encoding="utf-8")

    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError(
            f"Could not find {START_MARKER} / {END_MARKER} markers in README.md. "
            "Add them around the projects table first."
        )

    table_block = TABLE_HEADER + ("\n".join(rows) if rows else "*(No projects yet.)*")

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    replacement = f"{START_MARKER}\n{table_block}\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)

    README_PATH.write_text(new_content, encoding="utf-8")


def main():
    rows = build_table_rows()
    update_readme(rows)
    print(f"Updated README.md with {len(rows)} project(s).")


if __name__ == "__main__":
    main()
