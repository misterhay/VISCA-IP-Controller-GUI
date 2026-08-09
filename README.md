# VISCA-IP-Controller-GUI
A graphical program for controlling PTZ cameras using VISCA commands over a local network.

This uses code from [VISCA-IP-Controller](https://github.com/misterhay/VISCA-IP-Controller).

Ensure you have [Python](https://www.python.org/) installed, along with [Tkinter](https://www.tutorialspoint.com/how-to-install-tkinter-in-python).

## Running

```bash
pip install visca-over-ip
python gui.py
```

Edit the camera IP at the top of `gui.py` before running.

## Camera compatibility

| Script | Protocol | Port | Camera types |
|---|---|---|---|
| `gui.py` / `visca_control_gui.py` | VISCA-over-IP (UDP, Sony envelope) | 52381 | Sony, BirdDog, many others |
| `ptzoptics_gui.py` | Raw VISCA over TCP | 5678 | PTZOptics cameras |
| `camera-controller.py` | Raw VISCA-over-IP (UDP, no library) | 52381 | Sony, BirdDog, many others |

### PTZOptics cameras (PT12X-SDI, PT20X-SDI, etc.)

PTZOptics cameras speak plain VISCA over a persistent TCP connection on port 5678 rather than the UDP-with-envelope protocol that `visca_over_ip` uses.

**Run:**
```bash
# No pip dependencies needed
python ptzoptics_gui.py
```

Edit `camera_ip` at the top of `ptzoptics_gui.py` to match your camera's IP address.

**Functional differences from `gui.py`:**
- `info_display` — not implemented on PTZOptics cameras; calls are silently ignored
- `set_autofocus_mode` — not implemented on PTZOptics cameras; calls are silently ignored
- Presets 0–127 supported (vs 0–15 shown in the GUI buttons)

**To find your camera's IP:** check your router's DHCP client list, or open the camera's OSD menu via the included IR remote and navigate to Network settings.

**To test your camera connection** before running the GUI:
```bash
python ptzoptics_tcp_camera.py <camera-ip>
```
