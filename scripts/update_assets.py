#!/usr/bin/env python3
"""Regenerate all README profile assets in the right order."""
import os
import subprocess
import sys


def find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [script_dir, os.getcwd(), os.path.abspath(os.path.join(script_dir, ".."))]
    for candidate in candidates:
        if (
            os.path.isdir(candidate)
            and os.path.isdir(os.path.join(candidate, "scripts"))
            and os.path.isfile(os.path.join(candidate, "README.md"))
        ):
            return os.path.abspath(candidate)
    return os.path.abspath(os.path.join(script_dir, ".."))


ROOT = find_project_root()

STEPS = [
    "fetch_contributions.py",
    "render_heatmap_svg.py",
    "make_ascii_svg.py",
    "make_info_card.py",
]


def run_step(script):
    path = os.path.join(ROOT, "scripts", script)
    print(f"Running {script}...", flush=True)
    subprocess.run([sys.executable, path], cwd=ROOT, check=True)


if __name__ == "__main__":
    os.environ.setdefault("GH_PROFILE_USER", "Darpan-Maurya")
    os.environ.setdefault("STATIC", "1")

    for step in STEPS:
        run_step(step)

    print("Profile assets updated.", flush=True)
