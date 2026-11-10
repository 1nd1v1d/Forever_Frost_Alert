"""Collect the prepared files into one author upload kit (not an addon ZIP)."""
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
metadata = json.loads((root / "docs/publication/project-metadata.json").read_text())
destination = root / "dist" / f"ForeverFrostAlert-{metadata['version']}-publication-kit.zip"
files = [
    root / metadata["uploadFile"],
    root / metadata["checksumFile"],
    root / metadata["projectIcon"],
    root / "README.md",
    root / "CHANGELOG.md",
    root / "LICENSE",
    root / "NOTICE",
    *sorted((root / "docs/publication").glob("*")),
]
with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, path.relative_to(root).as_posix())
print(destination)
