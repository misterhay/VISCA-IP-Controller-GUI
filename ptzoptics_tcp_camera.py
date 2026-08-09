#!/usr/bin/env python3
"""
Drop-in replacement for visca_over_ip.Camera for cameras (e.g. PTZOptics)
that expose plain/raw VISCA over a persistent TCP socket (port 5678) instead
of the Sony VISCA-over-IP UDP envelope protocol (port 52381) that
visca_over_ip speaks.

Same method names/signatures as visca_over_ip.Camera are provided so it can
be swapped in with just an import + instantiation change.
"""

import socket
import time


class Camera:
    def __init__(self, ip: str, port: int = 5678, timeout: float = 2.0):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((ip, port))
        self._buffer = b''

    def _read_frame(self):
        """Reads one VISCA reply frame (up to and including the 0xFF terminator),
        using any bytes already buffered from a previous over-read first."""
        while b'\xff' not in self._buffer:
            chunk = self._sock.recv(1024)
            if not chunk:
                break
            self._buffer += chunk
        if b'\xff' not in self._buffer:
            return b''
        end = self._buffer.index(b'\xff') + 1
        frame, self._buffer = self._buffer[:end], self._buffer[end:]
        return frame

    def _send_command(self, command_hex: str, query: bool = False):
        preamble = b'\x81' + (b'\x09' if query else b'\x01')
        payload = preamble + bytearray.fromhex(command_hex) + b'\xff'
        self._sock.sendall(payload)
        try:
            frame = self._read_frame()
            # Non-query commands reply with an ACK (90 4y FF) then a Completion
            # (90 5y FF); grab the completion too so it doesn't linger and get
            # misread as the response to a later command.
            if not query and len(frame) >= 2 and (frame[1] >> 4) == 4:
                frame = self._read_frame()
            return frame
        except socket.timeout:
            return b''

    def close_connection(self):
        self._sock.close()

    def set_power(self, power_state: bool):
        return self._send_command('04 00 02' if power_state else '04 00 03')

    def info_display(self, display_mode: bool):
        # PTZOptics cameras (including PT12X-SDI) do not implement the
        # CAM_InfoDisplay command — silently ignored for drop-in compatibility.
        pass

    def pantilt(self, pan_speed: int, tilt_speed: int):
        """
        :param pan_speed: -24 to 24. Positive = pan left, negative = pan right, 0 = stop.
        :param tilt_speed: -24 to 24. Positive = tilt up, negative = tilt down, 0 = stop.
        (Same sign convention as visca_over_ip.Camera.pantilt)
        """
        if abs(pan_speed) > 24 or abs(tilt_speed) > 24:
            raise ValueError('pan_speed and tilt_speed must be between -24 and 24 inclusive')

        def direction_hex(speed):
            # VISCA: 01=left/up, 02=right/down, 03=stop
            if speed > 0:
                return '01'
            if speed < 0:
                return '02'
            return '03'

        pan_hex = f'{abs(pan_speed):02x}'
        tilt_hex = f'{abs(tilt_speed):02x}'
        return self._send_command(
            f'06 01 {pan_hex} {tilt_hex} {direction_hex(pan_speed)} {direction_hex(tilt_speed)}'
        )

    def pantilt_home(self):
        return self._send_command('06 04')

    def pantilt_reset(self):
        return self._send_command('06 05')

    def zoom(self, speed: int):
        """speed: -7 to 7. Positive zooms in, negative zooms out, 0 stops."""
        if not isinstance(speed, int) or abs(speed) > 7:
            raise ValueError('zoom speed must be an integer from -7 to 7 inclusive')
        speed_hex = f'{abs(speed):x}'
        if speed == 0:
            dir_hex = '0'
        elif speed > 0:
            dir_hex = '2'
        else:
            dir_hex = '3'
        return self._send_command(f'04 07 {dir_hex}{speed_hex}')

    def manual_focus(self, speed: int):
        """speed: -7 to 7. Positive focuses near, negative focuses far, 0 stops."""
        if not isinstance(speed, int) or abs(speed) > 7:
            raise ValueError('focus speed must be an integer from -7 to 7 inclusive')
        speed_hex = f'{abs(speed):x}'
        if speed == 0:
            dir_hex = '0'
        elif speed > 0:
            dir_hex = '3'
        else:
            dir_hex = '2'
        return self._send_command(f'04 08 {dir_hex}{speed_hex}')

    def set_focus_mode(self, mode: str):
        """mode: 'auto', 'manual', or 'auto/manual' (toggle)."""
        modes = {'auto': '38 02', 'manual': '38 03', 'auto/manual': '38 10'}
        mode = mode.lower()
        if mode not in modes:
            raise ValueError(f'"{mode}" is not a valid mode. Valid modes: {", ".join(modes.keys())}')
        return self._send_command('04 ' + modes[mode])

    def set_autofocus_mode(self, mode: str):
        """mode: 'normal', 'interval', 'zoom trigger', or 'one push trigger'.
        Note: PTZOptics cameras do not support this command; it is a no-op here
        for drop-in compatibility with visca_over_ip.Camera.
        """
        modes = {'normal', 'interval', 'zoom trigger', 'one push trigger'}
        if mode.lower() not in modes:
            raise ValueError(f'"{mode}" is not a valid mode. Valid modes: {", ".join(sorted(modes))}')
        # PTZOptics does not implement the Sony AF mode / one-push AF commands — silently ignored
    def save_preset(self, preset_num: int):
        """Save current camera position/settings to preset slot 0-127."""
        if not 0 <= preset_num <= 127:
            raise ValueError('Preset number must be 0-127 inclusive')
        return self._send_command(f'04 3F 01 {preset_num:02x}')

    def recall_preset(self, preset_num: int):
        """Recall a previously saved preset slot 0-127."""
        if not 0 <= preset_num <= 127:
            raise ValueError('Preset number must be 0-127 inclusive')
        return self._send_command(f'04 3F 02 {preset_num:02x}')

    @staticmethod
    def _zero_padded_to_int(zero_padded: bytes, signed=True) -> int:
        """Converts bytes like 0x0Y 0x0Y 0x0Y 0x0Y (one nibble of data per byte) to an int."""
        unpadded = bytes.fromhex(zero_padded.hex()[1::2])
        return int.from_bytes(unpadded, 'big', signed=signed)

    def get_pantilt_position(self):
        response = self._send_command('06 12', query=True)
        return self._zero_padded_to_int(response[2:6]), self._zero_padded_to_int(response[6:10])

    def get_zoom_position(self):
        response = self._send_command('04 47', query=True)
        return self._zero_padded_to_int(response[2:6], signed=False)


if __name__ == '__main__':
    import sys
    ip = sys.argv[1] if len(sys.argv) > 1 else '10.15.16.54'
    c = Camera(ip)
    print('Connected. Testing pan/tilt stop, zoom stop, position inquiries...')
    c.pantilt(0, 0)
    c.zoom(0)
    time.sleep(0.3)
    print('Pan/Tilt position:', c.get_pantilt_position())
    print('Zoom position:', c.get_zoom_position())
    c.close_connection()
