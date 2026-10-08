"""Fetch and verify the original public Figshare workbook for local analysis."""

import hashlib
from pathlib import Path
from urllib.request import urlopen

URL = "https://ndownloader.figshare.com/files/28199136"
MD5 = "d7733d01c6982a3f68e77817f5666276"
OUTPUT = Path("data/breast_qlq_c30.xlsx")


def main():
    if OUTPUT.exists():
        existing = hashlib.md5(OUTPUT.read_bytes()).hexdigest()
        if existing == MD5:
            print(f"Already verified: {OUTPUT}")
            return
        raise ValueError(f"Existing {OUTPUT} failed checksum; move it aside before retrying")
    with urlopen(URL, timeout=60) as response:
        content = response.read()
    digest = hashlib.md5(content).hexdigest()
    if digest != MD5:
        raise ValueError(f"Download checksum mismatch: {digest}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(content)
    print(f"Downloaded and verified: {OUTPUT} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
