"""Build an installable addon ZIP and checksum using only the standard library."""
import hashlib
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
toc = root / "ForeverIcyVeins" / "ForeverIcyVeins.toc"
version = re.search(r"^## Version: (\S+)$", toc.read_text(), re.MULTILINE).group(1)
destination = root / "dist" / f"ForeverFrostAlert-{version}-forever.zip"
destination.parent.mkdir(exist_ok=True)
with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
    files = {
        "ForeverIcyVeins.toc": toc,
        "ForeverIcyVeins.lua": toc.with_suffix(".lua"),
        "LICENSE.txt": root / "LICENSE",
        "NOTICE.txt": root / "NOTICE",
    }
    for name, path in files.items():
        archive.write(path, f"ForeverIcyVeins/{name}")
checksum = hashlib.sha256(destination.read_bytes()).hexdigest()
destination.with_suffix(".zip.sha256").write_text(
    f"{checksum}  {destination.name}\n", encoding="ascii"
)
print(destination)
