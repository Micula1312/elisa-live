# AICHA UI

Run `aicha_player_builder.py` first. Once `/project1/AICHA_PLAYER` is working and connected to the existing audio-analysis patch, run `aicha_ui_builder.py`.

The UI builder creates only `/project1/AICHA_UI`. Re-running it deletes/rebuilds only that UI container; it never deletes or rewires `AICHA_PLAYER` or the existing audio-analysis network.

Target: TouchDesigner 2023.11340.
