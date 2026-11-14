# Profile maintenance

The README uses self-contained SVG artwork generated from the existing Tofu
mascot and local badge files. No image host, external font or frontend runtime
is required. Python 3.10+ is sufficient for the generation scripts.

## Room clock

The hero selects daytime from 06:00 inclusive until 18:00 exclusive in Hanoi
(UTC+7), and nighttime otherwise. Other panels use the viewer's light/dark
preference. Reduced-motion viewers receive static variants.

[room-time.yml](../.github/workflows/room-time.yml) schedules synchronization and
supports manual runs. Actions can start late, and an open page needs reloading;
this is not continuous realtime. Only the marked hero block is rewritten.

```sh
python scripts/update-room-time.py
python scripts/test-room-time.py
```

## Artwork

Edit the source generator and rebuild, rather than hand-editing generated SVGs:

```sh
python scripts/build-pixel-world.py
```

The builder also selects the current Hanoi scene. Every picture variant is local,
so moving from the private design repository to the public profile does not rely
on private asset URLs.

## Contribution calendar

[contribution-snake.yml](../.github/workflows/contribution-snake.yml) maintains
the real contribution animation and its paused copies. It retains the original
snake generator, account owner and schedule. To refresh only paused variants:

```sh
python scripts/build-pixel-world.py --snake-stills-only
```

The LinkedIn destination is preserved from the original profile, including its
`undefined` segment. Replace it only with a destination confirmed by the owner.
