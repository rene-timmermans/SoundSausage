"""Inspect user-provided SES fixtures and retain byte differences as local evidence."""
import argparse
import json
import math
from pathlib import Path

from soundsausage.legacy import inspect_ses


parser = argparse.ArgumentParser()
parser.add_argument("folder", type=Path)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
reports = []
previous = None
differences = []
for path in sorted(args.folder.glob("*.ses")):
    report = inspect_ses(path)
    (args.out / (path.name + ".json")).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    raw = path.read_bytes()
    if previous:
        name, old = previous
        differences.append(dict(before=name, after=path.name, before_size=len(old), after_size=len(raw),
            changed_offsets=[i for i, (a, b) in enumerate(zip(old, raw)) if a != b]))
    previous = (path.name, raw)
    reports.append(dict(file=path.name, version=report["version"], sample_rate=report["sample_rate"],
        tracks=len(report["tracks"]), warnings=report["warnings"],
        clips=[dict(source=next(x["basename"] for x in report["files"] if x["id"] == clip["source_id"]),
            start_frame=clip["start"], start_seconds=clip["start"] / report["sample_rate"],
            frames=clip["frames"], left=clip["left"], right=clip["right"],
            left_db=20 * math.log10(clip["left"]) if clip["left"] > 0 else None,
            right_db=20 * math.log10(clip["right"]) if clip["right"] > 0 else None) for clip in report["blocks"]]))
(args.out / "summary.json").write_text(json.dumps(reports, indent=2, ensure_ascii=False) + "\n")
(args.out / "differences.json").write_text(json.dumps(differences, indent=2) + "\n")
print(json.dumps(reports, indent=2, ensure_ascii=False))
