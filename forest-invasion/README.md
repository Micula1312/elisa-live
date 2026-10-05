# FOREST INVASION

Desktop-native image invasion for **ELISA**.

By default it reads the existing archive in `web/public/feed` recursively and progressively opens its images as borderless always-on-top windows. They move, pulse and bounce over the real Windows desktop, so TouchDesigner can capture the result as part of the performance.

## First run

Double-click `INSTALL.bat` once.

Then double-click `START_FOREST_INVASION.bat`.

## Live controls

- `SPACE` — burst: release up to 8 more images and increase chaos
- `UP` — more chaos
- `DOWN` — less chaos
- `ESC` — KILL all floating windows

The default launcher uses up to 42 images from the feed archive and accelerates the spawning progressively.

## Desktop icon

Create a Windows shortcut to `START_FOREST_INVASION.bat` and drag the shortcut to the desktop. Rename it e.g. `FOREST.exe` or `FOREST INVASION`.

## Custom folder

You can point it to any folder:

`py forest_invasion.py --source "C:\path\to\images" --max 60 --interval 1.2`

No files are modified or moved.
