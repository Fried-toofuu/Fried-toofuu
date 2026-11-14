"""Select the README hero for Hanoi's fixed UTC+7 clock, without a server."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HANOI = timezone(timedelta(hours=7), 'Asia/Ho_Chi_Minh')
START = '<!-- room-time:start -->'
END = '<!-- room-time:end -->'


def room_period(now):
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('An explicit timezone is required')
    return 'day' if 6 <= now.astimezone(HANOI).hour < 18 else 'night'


def hero_markup(period):
    if period not in ('day', 'night'):
        raise ValueError('Expected day or night')
    stem = 'hero-animated-'+period
    return f'''<p align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce) and (max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{stem}-still-mobile-dark.svg" />
    <source media="(prefers-reduced-motion: reduce) and (max-width: 600px)" srcset="assets/{stem}-still-mobile-light.svg" />
    <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="assets/{stem}-still-dark.svg" />
    <source media="(prefers-reduced-motion: reduce)" srcset="assets/{stem}-still-light.svg" />
    <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{stem}-mobile-dark.svg" />
    <source media="(max-width: 600px)" srcset="assets/{stem}-mobile-light.svg" />
    <source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark.svg" />
    <img src="assets/{stem}-light.svg" alt="Tofu's coding corner. Hi, I'm Khanh. Developer in progress at PTIT Hanoi. {period.capitalize()} scene selected by Hanoi time; colors follow viewer theme." width="100%" />
  </picture>
</p>'''


def update_readme(readme, now):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError('Expected exactly one marked hero block')
    period = room_period(now)
    updated = re.sub(re.escape(START)+r'.*?'+re.escape(END),
                     lambda _: START+'\n'+hero_markup(period)+'\n'+END,
                     readme, count=1, flags=re.DOTALL)
    return updated, period


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--at', help='Timezone-aware ISO timestamp for preview/testing')
    parser.add_argument('--print', action='store_true', dest='print_only', help='Print selected hero without writing files')
    args = parser.parse_args()
    now = datetime.fromisoformat(args.at) if args.at else datetime.now(timezone.utc)
    if args.print_only:
        print(hero_markup(room_period(now)))
        return
    path = ROOT/'README.md'
    before = path.read_text(encoding='utf-8')
    after, period = update_readme(before, now)
    if after != before:
        path.write_text(after, encoding='utf-8')
    print(f'Hanoi {now.astimezone(HANOI):%H:%M}: {period} hero; '+('updated' if after != before else 'already current'))


if __name__ == '__main__':
    main()
