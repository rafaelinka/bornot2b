"""Locate the numbered issues available in both reader languages."""

from pathlib import Path
import re


def available_editions(site: Path) -> list[str]:
    def numbers(directory: Path) -> set[str]:
        return {
            child.name
            for child in directory.glob('issue-*')
            if re.fullmatch(r'issue-\d{2,}', child.name)
            and child.name != 'issue-00'
            and (child / 'index.html').is_file()
        }

    english = numbers(site)
    russian = numbers(site / 'ru')
    if not english or english != russian:
        raise SystemExit('Numbered issues must have matching English and Russian pages')
    return sorted(english, key=lambda name: int(name.removeprefix('issue-')))
