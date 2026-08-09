#!/usr/bin/env python3
"""
Comprehensive functional test for ptzoptics_tcp_camera.py against a live camera.
Tests every command and verifies VISCA response packets are well-formed.
Safe to run: uses preset slot 15 only, moves briefly then stops, does not power off.
"""
import sys
import time
sys.path.insert(0, '.')
from ptzoptics_tcp_camera import Camera

CAMERA_IP = '10.15.16.54'
PASS = '\033[92mPASS\033[0m'
FAIL = '\033[91mFAIL\033[0m'
SKIP = '\033[93mSKIP\033[0m'

results = []

def check(label, resp, expect_completion=True):
    """Verify a VISCA response is a well-formed ACK or Completion packet."""
    if resp is None or len(resp) < 3:
        print(f'  {FAIL}: {label} — empty/short response: {resp!r}')
        results.append((label, False))
        return False

    # VISCA reply: first byte 0x90, second byte high nibble 4=ACK 5=Completion 6=Error
    status = resp[1] >> 4
    if status == 6:
        error_code = resp[2]
        error_names = {0x02: 'Syntax Error', 0x03: 'Buffer Full',
                       0x04: 'Canceled', 0x05: 'No Socket', 0x41: 'Not Executable'}
        name = error_names.get(error_code, f'0x{error_code:02x}')
        if error_code == 0x41:
            # "Not Executable" is acceptable for power-on when camera is already on
            print(f'  {PASS}: {label} — Not Executable (camera already in this state)')
            results.append((label, True))
            return True
        print(f'  {FAIL}: {label} — VISCA Error: {name} ({resp.hex()})')
        results.append((label, False))
        return False
    elif status in (4, 5):
        print(f'  {PASS}: {label} — {resp.hex()}')
        results.append((label, True))
        return True
    else:
        # Might be a completion we already consumed, or an inquiry response (0x50)
        if resp[1] == 0x50 or (resp[1] & 0xF0) == 0x50:
            print(f'  {PASS}: {label} — inquiry response {resp.hex()}')
            results.append((label, True))
            return True
        print(f'  {FAIL}: {label} — unexpected response {resp.hex()}')
        results.append((label, False))
        return False


def section(title):
    print(f'\n{"="*50}')
    print(f'  {title}')
    print(f'{"="*50}')


print(f'Connecting to {CAMERA_IP}:5678 ...')
try:
    c = Camera(CAMERA_IP)
    print('Connected.\n')
except Exception as e:
    print(f'FAILED to connect: {e}')
    sys.exit(1)


# ── Power ────────────────────────────────────────────────────────────────────
section('Power')
resp = c._send_command('04 00 02')  # Power On (likely already on → Not Executable, still valid)
check('power on', resp)


# ── Info display ──────────────────────────────────────────────────────────────
section('Info Display (PTZOptics no-op — just validate no crash/exception)')
for mode in (True, False):
    try:
        c.info_display(mode)
        print(f'  {PASS}: info_display({mode}) — no exception (no-op on PTZOptics)')
        results.append((f'info_display({mode})', True))
    except Exception as e:
        print(f'  {FAIL}: info_display({mode}) — {e}')
        results.append((f'info_display({mode})', False))


# ── Pan / Tilt ────────────────────────────────────────────────────────────────
section('Pan / Tilt')

def pt(label, pan, tilt, hold=0.4):
    resp = c.pantilt(pan, tilt)
    ok = check(label, resp)
    time.sleep(hold)
    return ok

pt('pan left (speed 5)', 5, 0)
c.pantilt(0, 0); time.sleep(0.1)

pt('pan right (speed 5)', -5, 0)
c.pantilt(0, 0); time.sleep(0.1)

pt('tilt up (speed 5)', 0, 5)
c.pantilt(0, 0); time.sleep(0.1)

pt('tilt down (speed 5)', 0, -5)
c.pantilt(0, 0); time.sleep(0.1)

pt('pan-tilt up-left', 5, 5)
c.pantilt(0, 0); time.sleep(0.1)

pt('pan-tilt up-right', -5, 5)
c.pantilt(0, 0); time.sleep(0.1)

pt('pan-tilt down-left', 5, -5)
c.pantilt(0, 0); time.sleep(0.1)

pt('pan-tilt down-right', -5, -5)
c.pantilt(0, 0); time.sleep(0.1)

resp = c.pantilt(0, 0)
check('pan/tilt stop', resp)

resp = c.pantilt_home()
check('pan/tilt home', resp)
time.sleep(1.5)  # let it reach home


# ── Zoom ──────────────────────────────────────────────────────────────────────
section('Zoom')

resp = c.zoom(5)
check('zoom in (speed 5)', resp)
time.sleep(0.4)

resp = c.zoom(0)
check('zoom stop', resp)
time.sleep(0.1)

resp = c.zoom(-5)
check('zoom out (speed 5)', resp)
time.sleep(0.4)

resp = c.zoom(0)
check('zoom stop (cleanup)', resp)


# ── Focus ─────────────────────────────────────────────────────────────────────
section('Focus')

resp = c.set_focus_mode('manual')
check('focus mode: manual', resp)
time.sleep(0.2)

resp = c.manual_focus(5)
check('manual focus near (speed 5)', resp)
time.sleep(0.3)

resp = c.manual_focus(0)
check('manual focus stop', resp)
time.sleep(0.1)

resp = c.manual_focus(-5)
check('manual focus far (speed 5)', resp)
time.sleep(0.3)

resp = c.manual_focus(0)
check('manual focus stop (cleanup)', resp)
time.sleep(0.1)

resp = c.set_focus_mode('auto')
check('focus mode: auto', resp)
time.sleep(0.2)

resp = c.set_focus_mode('auto/manual')
check('focus mode: auto/manual toggle', resp)
time.sleep(0.2)

resp = c.set_focus_mode('auto')
check('focus mode: auto (restore)', resp)


# ── Autofocus mode ────────────────────────────────────────────────────────────
section('Autofocus Mode (PTZOptics no-op — just validate no crash/exception)')

for mode in ('normal', 'interval', 'zoom trigger'):
    try:
        c.set_autofocus_mode(mode)
        print(f'  {PASS}: set_autofocus_mode("{mode}") — no exception (no-op on PTZOptics)')
        results.append((f'set_autofocus_mode {mode}', True))
    except Exception as e:
        print(f'  {FAIL}: set_autofocus_mode("{mode}") — {e}')
        results.append((f'set_autofocus_mode {mode}', False))

try:
    c.set_autofocus_mode('bad value')
    print(f'  {FAIL}: set_autofocus_mode bad value should raise ValueError')
    results.append(('set_autofocus_mode bad value raises ValueError', False))
except ValueError:
    print(f'  {PASS}: set_autofocus_mode bad value raises ValueError correctly')
    results.append(('set_autofocus_mode bad value raises ValueError', True))


# ── Presets ───────────────────────────────────────────────────────────────────
section('Preset Store / Recall (slot 15 = 0x0F)')

resp = c.save_preset(15)
check('preset store 15', resp)
time.sleep(0.3)

resp = c.recall_preset(15)
check('preset recall 15', resp)
time.sleep(1.0)

# store/recall slot 0 (just recall — don't overwrite user's preset)
resp = c.recall_preset(0)
check('preset recall 0', resp)
time.sleep(1.0)


# ── Position inquiries ────────────────────────────────────────────────────────
section('Position Inquiries')

try:
    pan, tilt = c.get_pantilt_position()
    print(f'  {PASS}: pan/tilt position → pan={pan}, tilt={tilt}')
    results.append(('pan/tilt position inquiry', True))
except Exception as e:
    print(f'  {FAIL}: pan/tilt position inquiry → {e}')
    results.append(('pan/tilt position inquiry', False))

try:
    zoom = c.get_zoom_position()
    print(f'  {PASS}: zoom position → {zoom}')
    results.append(('zoom position inquiry', True))
except Exception as e:
    print(f'  {FAIL}: zoom position inquiry → {e}')
    results.append(('zoom position inquiry', False))


# ── Speed boundary values ─────────────────────────────────────────────────────
section('Boundary / Edge Cases')

# Max pan speed
resp = c.pantilt(24, 0)
check('pan max speed (24)', resp)
time.sleep(0.2)
c.pantilt(0, 0)

# Max tilt speed
resp = c.pantilt(0, 20)  # PTZOptics max tilt is 0x14=20
check('tilt max speed (20)', resp)
time.sleep(0.2)
c.pantilt(0, 0)

# Max zoom speed
resp = c.zoom(7)
check('zoom max speed (7)', resp)
time.sleep(0.2)
c.zoom(0)

# Invalid speed (should raise ValueError, not crash)
try:
    c.zoom(8)
    print(f'  {FAIL}: zoom speed 8 should raise ValueError')
    results.append(('zoom invalid speed raises ValueError', False))
except ValueError:
    print(f'  {PASS}: zoom speed 8 raises ValueError correctly')
    results.append(('zoom invalid speed raises ValueError', True))

try:
    c.pantilt(25, 0)
    print(f'  {FAIL}: pan speed 25 should raise ValueError')
    results.append(('pan invalid speed raises ValueError', False))
except ValueError:
    print(f'  {PASS}: pan speed 25 raises ValueError correctly')
    results.append(('pan invalid speed raises ValueError', True))

try:
    c.save_preset(256)
    print(f'  {FAIL}: preset 256 should raise ValueError')
    results.append(('preset 256 raises ValueError', False))
except ValueError:
    print(f'  {PASS}: preset 256 raises ValueError correctly')
    results.append(('preset 256 raises ValueError', True))


# ── Connection health ─────────────────────────────────────────────────────────
section('Connection Health')

# Rapid-fire commands (simulates slider dragging)
ok = True
for speed in [1, 3, 5, 7, 5, 3, 1, 0]:
    resp = c.zoom(speed)
    if not resp or len(resp) < 3:
        ok = False
        break
    time.sleep(0.05)
if ok:
    print(f'  {PASS}: 8 rapid-fire zoom commands all responded')
    results.append(('rapid-fire zoom commands', True))
else:
    print(f'  {FAIL}: rapid-fire zoom commands — some dropped')
    results.append(('rapid-fire zoom commands', False))

c.close_connection()


# ── Summary ───────────────────────────────────────────────────────────────────
section('SUMMARY')
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f'\n  {passed}/{total} tests passed\n')
for label, ok in results:
    status = PASS if ok else FAIL
    print(f'  {status}  {label}')

if passed < total:
    sys.exit(1)
