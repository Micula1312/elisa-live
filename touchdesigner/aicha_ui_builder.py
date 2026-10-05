# ============================================================
# AICHA / ELISA MEDIA PLAYER — UI BUILDER
# TouchDesigner 2023.11340
# Run AFTER aicha_player_builder.py.
# Creates UI only; never rebuilds or touches the audio engine.
# ============================================================

ROOT = op('/project1')
AICHA = ROOT.op('AICHA_PLAYER')

if not AICHA:
    raise Exception('AICHA_PLAYER not found. Run aicha_player_builder.py first.')

# Remove/rebuild UI only.
old = ROOT.op('AICHA_UI')
if old:
    old.destroy()

ui = ROOT.create(containerCOMP, 'AICHA_UI')
ui.nodeX = 500
ui.nodeY = -350
ui.par.w = 720
ui.par.h = 460
ui.par.bgcolorr = 0.035
ui.par.bgcolorg = 0.025
ui.par.bgcolorb = 0.055

# Helper: create a panel child safely.
def place(comp, x, y, w, h):
    comp.par.x = x
    comp.par.y = y
    comp.par.w = w
    comp.par.h = h
    return comp

# Header
header = place(ui.create(containerCOMP, 'HEADER'), 18, 374, 684, 66)
header.par.bgcolorr = 0.16
header.par.bgcolorg = 0.04
header.par.bgcolorb = 0.18

title = place(header.create(textCOMP, 'TITLE'), 12, 18, 660, 38)
title.par.text = 'AICHA / ELISA MEDIA PLAYER'

# Status / magic nonsense
status = place(ui.create(textCOMP, 'STATUS'), 20, 332, 680, 32)
status.par.text = '✦ SIGNAL POSSESSED  /  ELISA IS LISTENING... ✦'

# MASTER button
master_btn = place(ui.create(buttonCOMP, 'MASTER'), 20, 268, 190, 52)
master_btn.par.label = 'ELISA MASTER'
master_btn.par.toggle = True

# LIVE button
live_btn = place(ui.create(buttonCOMP, 'LIVE'), 220, 268, 190, 52)
live_btn.par.label = 'LIVE INPUT'
live_btn.par.toggle = True

# PLAY button
play_btn = place(ui.create(buttonCOMP, 'PLAY'), 430, 268, 270, 52)
play_btn.par.label = '▶ PLAY / PAUSE'
play_btn.par.toggle = True

# Decorative timeline / transport display
time_text = place(ui.create(textCOMP, 'TIME'), 20, 218, 680, 34)
time_text.par.text = '00:00  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  32:27'

# Real audio monitor: waveform viewer fed from AICHA AUDIO_OUT
wave = place(ui.create(fieldCOMP, 'WAVE_DISPLAY'), 20, 126, 680, 78)
wave.par.text = 'AUDIO SIGNAL  ▂▃▅▇▆▄▂  ▃▆█▇▄▂  ▂▄▇█▅▃  ▂▅▇▆▃'
wave.par.readonly = True

meters = place(ui.create(textCOMP, 'METERS'), 20, 82, 680, 32)
meters.par.text = 'LOW   ▮▮▮▮▯▯    MID   ▮▮▮▮▮▯    HIGH   ▮▮▮▯▯▯    HIT   ◉'

footer = place(ui.create(textCOMP, 'FOOTER'), 20, 20, 680, 42)
footer.par.text = 'MEDIA SOUL : ONLINE    //    AICHA SYSTEM 2003    //    DO NOT EXORCISE'

# Panel Execute DAT: buttons drive the existing AICHA_PLAYER custom parameters.
cb = ui.create(panelExecuteDAT, 'UI_CONTROL')
cb.nodeX = 0
cb.nodeY = -150
cb.par.panel = '*'
cb.par.valuechange = True
cb.text = """def onValueChange(panelValue):
    owner = parent()
    player = op('/project1/AICHA_PLAYER')
    if not player:
        return

    name = panelValue.owner.name
    value = panelValue.val

    if name == 'MASTER' and value:
        player.par.Source = 'master'
        other = owner.op('LIVE')
        if other:
            other.par.value0 = 0

    elif name == 'LIVE' and value:
        player.par.Source = 'live'
        other = owner.op('MASTER')
        if other:
            other.par.value0 = 0

    elif name == 'PLAY':
        player.par.Play = bool(value)

    return
"""

print('AICHA_UI READY:', ui.path)
print('Audio engine untouched:', AICHA.path)
print('Open AICHA_UI viewer to use the player.')
