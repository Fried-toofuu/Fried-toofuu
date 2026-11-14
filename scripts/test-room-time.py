"""Verify time boundaries and ensure synchronization changes only the hero."""
from datetime import datetime
from pathlib import Path
import runpy
import unittest

ROOM = runpy.run_path(str(Path(__file__).with_name('update-room-time.py')))


class RoomTimeTests(unittest.TestCase):
    def test_local_boundaries_and_utc_conversion(self):
        for timestamp, expected in [
            ('2026-11-14T05:59:59+07:00', 'night'),
            ('2026-11-14T06:00:00+07:00', 'day'),
            ('2026-11-14T17:59:59+07:00', 'day'),
            ('2026-11-14T18:00:00+07:00', 'night'),
            ('2026-11-14T00:00:00+07:00', 'night'),
            ('2026-11-13T23:00:00+00:00', 'day'),
            ('2026-11-14T11:00:00+00:00', 'night'),
        ]:
            with self.subTest(timestamp=timestamp):
                self.assertEqual(ROOM['room_period'](datetime.fromisoformat(timestamp)), expected)

    def test_only_hero_changes_and_same_period_is_idempotent(self):
        before = 'prefix\n'+ROOM['START']+'\nold hero\n'+ROOM['END']+'\nplayer, inventory, snake, footer'
        now = datetime.fromisoformat('2026-11-14T12:00:00+07:00')
        after, period = ROOM['update_readme'](before, now)
        self.assertEqual(period, 'day')
        self.assertTrue(after.startswith('prefix\n'+ROOM['START']))
        self.assertTrue(after.endswith(ROOM['END']+'\nplayer, inventory, snake, footer'))
        self.assertIn('prefers-color-scheme', after)
        self.assertIn('prefers-reduced-motion', after)
        self.assertEqual(ROOM['update_readme'](after, now)[0], after)

    def test_each_period_offers_both_themes_and_motion_sizes(self):
        for period in ['day', 'night']:
            markup = ROOM['hero_markup'](period)
            other = 'night' if period == 'day' else 'day'
            self.assertNotIn('hero-animated-'+other+'-', markup)
            for theme in ['light', 'dark']:
                for variant in ['', 'mobile-', 'still-', 'still-mobile-']:
                    self.assertIn(f'assets/hero-animated-{period}-{variant}{theme}.svg', markup)

    def test_missing_markers_and_naive_time_fail(self):
        with self.assertRaises(ValueError):
            ROOM['room_period'](datetime(2026, 11, 14, 12))
        with self.assertRaises(ValueError):
            ROOM['update_readme']('unmarked README', datetime.fromisoformat('2026-11-14T12:00:00+00:00'))


if __name__ == '__main__':
    unittest.main()
