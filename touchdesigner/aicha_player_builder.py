# ============================================================
# AICHA / ELISA MEDIA PLAYER
# TouchDesigner 2023.11340
# Minimal, compatibility-safe audio front-end.
# Does NOT touch the existing audioAnalysis network.
# ============================================================

ROOT = op('/project1')
NAME = 'AICHA_PLAYER'

old = ROOT.op(NAME)
if old:
    old.destroy()

a = ROOT.create(baseCOMP, NAME)
a.nodeX = 100
a.nodeY = -350
a.color = (0.55, 0.12, 0.48)

# Custom controls
page = a.appendCustomPage('AICHA')

source = page.appendMenu('Source', label='SOURCE')[0]
source.menuNames = ['master', 'live']
source.menuLabels = ['ELISA MASTER', 'LIVE INPUT']

masterfile = page.appendStr('Masterfile', label='MASTER FILE')[0]
masterfile.val = project.folder + '/web/public/audio/elisa_master.mp3'

page.appendToggle('Play', label='PLAY MASTER')

volume = page.appendFloat('Volume', label='MASTER VOLUME')[0]
volume.val = 1.0
volume.min = 0
volume.max = 1

# ELISA master
master = a.create(audiofileinCHOP, 'MASTER_TRACK')
master.nodeX = -400
master.nodeY = 120
master.par.file.expr = "parent().par.Masterfile"
if hasattr(master.par, 'play'):
    master.par.play.expr = "parent().par.Play"

# Mixer / audio-interface input
live = a.create(audiodeviceinCHOP, 'LIVE_INPUT')
live.nodeX = -400
live.nodeY = -40

# Select MASTER or LIVE
switch = a.create(switchCHOP, 'SOURCE_SWITCH')
switch.nodeX = -150
switch.nodeY = 60
master.outputConnectors[0].connect(switch.inputConnectors[0])
live.outputConnectors[0].connect(switch.inputConnectors[1])
switch.par.index.expr = "0 if parent().par.Source == 'master' else 1"

# Master level
gain = a.create(mathCHOP, 'MASTER_VOLUME')
gain.nodeX = 80
gain.nodeY = 60
switch.outputConnectors[0].connect(gain.inputConnectors[0])
if hasattr(gain.par, 'gain'):
    gain.par.gain.expr = "parent().par.Volume"
elif hasattr(gain.par, 'mult'):
    gain.par.mult.expr = "parent().par.Volume"

# One clean output to feed the existing audio-reactive network
audioout = a.create(nullCHOP, 'AUDIO_OUT')
audioout.nodeX = 320
audioout.nodeY = 60
gain.outputConnectors[0].connect(audioout.inputConnectors[0])
audioout.color = (0.8, 0.15, 0.65)

print('AICHA_PLAYER READY:', a.path)
print('MASTER_TRACK + LIVE_INPUT -> SOURCE_SWITCH -> MASTER_VOLUME -> AUDIO_OUT')
print('Existing audioAnalysis network untouched.')
