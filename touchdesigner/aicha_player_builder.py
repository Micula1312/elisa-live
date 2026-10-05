# AICHA / ELISA MEDIA PLAYER — TouchDesigner 2023 builder
# Run this once from a Text DAT inside your existing elisa-live.toe.
# It creates /project1/AICHA_PLAYER without touching your existing visual chain.

ROOT = op('/project1')
NAME = 'AICHA_PLAYER'

old = ROOT.op(NAME)
if old:
    old.destroy()

a = ROOT.create(baseCOMP, NAME)
a.nodeX = -650
a.nodeY = 250
a.color = (0.35, 0.08, 0.42)

page = a.appendCustomPage('AICHA')
sourcePar = page.appendMenu('Source', label='SOURCE')[0]
sourcePar.menuNames = ['master', 'live']
sourcePar.menuLabels = ['ELISA MASTER', 'LIVE INPUT']
masterPar = page.appendStr('Masterfile', label='MASTER FILE')[0]
masterPar.val = project.folder + '/web/public/audio/elisa_master.mp3'
page.appendToggle('Play', label='PLAY / PAUSE')
page.appendPulse('Restart', label='RESTART')
sens = page.appendFloat('Sensitivity', label='SENSITIVITY')
sens[0].val = 1.0

# --- AUDIO SOURCES -----------------------------------------------------------
master = a.create(audiofileinCHOP, 'MASTER_TRACK')
master.nodeX, master.nodeY = -520, 120
master.par.file.expr = "parent().par.Masterfile"
# play is driven by the component's Play parameter
if hasattr(master.par, 'play'):
    master.par.play.expr = "parent().par.Play"

live = a.create(audiodeviceinCHOP, 'LIVE_INPUT')
live.nodeX, live.nodeY = -520, -20

switch = a.create(switchCHOP, 'SOURCE_SWITCH')
switch.nodeX, switch.nodeY = -280, 70
master.outputConnectors[0].connect(switch.inputConnectors[0])
live.outputConnectors[0].connect(switch.inputConnectors[1])
switch.par.index.expr = "0 if parent().par.Source == 'master' else 1"

out = a.create(nullCHOP, 'AUDIO_OUT')
out.nodeX, out.nodeY = -60, 70
switch.outputConnectors[0].connect(out.inputConnectors[0])

# --- ANALYSIS: LOW / MID / HIGH ---------------------------------------------
def band(name, lo, hi, x):
    f = a.create(audiofilterCHOP, name + '_FILTER')
    f.nodeX, f.nodeY = x, -100
    out.outputConnectors[0].connect(f.inputConnectors[0])
    # Audio Filter parameter names can vary slightly between TD builds.
    # Set what is available; leave node editable for tuning.
    for parname, val in [('lowcutoff', lo), ('highcutoff', hi), ('lowcut', lo), ('highcut', hi)]:
        par = getattr(f.par, parname, None)
        if par is not None:
            par.val = val
    ana = a.create(analyzeCHOP, name)
    ana.nodeX, ana.nodeY = x, -230
    f.outputConnectors[0].connect(ana.inputConnectors[0])
    if hasattr(ana.par, 'function'):
        try: ana.par.function = 'rms'
        except: pass
    return ana

low = band('LOW', 40, 180, -420)
mid = band('MID', 180, 2200, -190)
high = band('HIGH', 2200, 12000, 40)

merge = a.create(mergeCHOP, 'ELISA_AUDIO')
merge.nodeX, merge.nodeY = 300, -180
for n in (low, mid, high):
    n.outputConnectors[0].connect(merge.inputConnectors[len(merge.inputs)])

analysis = a.create(nullCHOP, 'ANALYSIS_OUT')
analysis.nodeX, analysis.nodeY = 500, -180
merge.outputConnectors[0].connect(analysis.inputConnectors[0])

# --- SIMPLE CONTROL PANEL ----------------------------------------------------
panel = a.create(containerCOMP, 'PLAYER_UI')
panel.nodeX, panel.nodeY = 160, 160
panel.par.w = 760
panel.par.h = 430
panel.par.bgcolorr = 0.025
panel.par.bgcolorg = 0.018
panel.par.bgcolorb = 0.035

title = panel.create(textCOMP, 'TITLE')
title.par.w = 700
title.par.h = 85
title.par.text = 'AICHA / ELISA MEDIA PLAYER'
title.par.textcolorr = 1
title.par.textcolorg = 0.35
title.par.textcolorb = 0.9

status = panel.create(textCOMP, 'STATUS')
status.nodeY = -100
status.par.w = 700
status.par.h = 90
status.par.text = '✦ MEDIA SOUL : ONLINE ✦\nSIGNAL POSSESSED / WAITING FOR ELISA'
status.par.textcolorr = 0.75
status.par.textcolorg = 0.9
status.par.textcolorb = 1

hint = panel.create(textCOMP, 'HINT')
hint.nodeY = -210
hint.par.w = 700
hint.par.h = 100
hint.par.text = 'SOURCE  [ ELISA MASTER / LIVE INPUT ]\nPLAY  ·  RESTART  ·  SENSITIVITY\nLOW / MID / HIGH → ANALYSIS_OUT'

# Component viewer shows PLAYER_UI when you open AICHA_PLAYER.
a.par.viewer = True

# --- RESTART pulse callback DAT ----------------------------------------------
cb = a.create(parameterexecuteDAT, 'CONTROLS')
cb.nodeX, cb.nodeY = -50, 260
cb.par.comp = a.path
cb.par.pars = 'Restart'
cb.par.pulse = True
cb.text = """def onPulse(par):
    if par.name == 'Restart':
        m = parent().op('MASTER_TRACK')
        if m:
            if hasattr(m.par, 'cuepulse'):
                m.par.cuepulse.pulse()
            elif hasattr(m.par, 'cue'):
                try: m.par.cue = 0
                except: pass
        parent().par.Play = True
    return
"""

print('✦ AICHA / ELISA MEDIA PLAYER created at', a.path)
print('Open AICHA_PLAYER parameters → AICHA page.')
print('Set LIVE_INPUT device in its Audio Device In CHOP when your interface is connected.')
