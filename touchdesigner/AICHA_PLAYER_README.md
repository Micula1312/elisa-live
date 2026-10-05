# AICHA / ELISA MEDIA PLAYER — TD builder

This builder creates a new `/project1/AICHA_PLAYER` component inside the existing TouchDesigner project without touching the current `screengrab1 → switch1 → FINAL` visual chain.

## Run once

1. `git pull`
2. Open `touchdesigner/elisa-live.toe` in TouchDesigner 2023 Pro.
3. In `/project1`, create a **Text DAT**.
4. Open `aicha_player_builder.py`, copy all its contents into the Text DAT.
5. Click **Run Script**.
6. Save the `.toe`.

You should now have `AICHA_PLAYER`.

## What it creates

- ELISA MASTER file input
- LIVE INPUT from the audio interface / mixer
- source switch
- unified AUDIO_OUT
- LOW / MID / HIGH analysis outputs
- a deliberately trash-magical AICHA / ELISA player panel
- PLAY / RESTART / SENSITIVITY custom controls

The master path defaults to:

`web/public/audio/elisa_master.mp3`

If the actual backup track has a different filename, change **AICHA_PLAYER → AICHA → MASTER FILE**.

## Important

TouchDesigner builds can expose slightly different Audio Filter parameter names. The builder deliberately leaves the generated LOW/MID/HIGH nodes visible and editable. After creation, verify the three bands once in your TD 2023 build.

The LIVE INPUT device itself should be selected directly on the generated `LIVE_INPUT` Audio Device In CHOP once the interface/mixer is connected.
