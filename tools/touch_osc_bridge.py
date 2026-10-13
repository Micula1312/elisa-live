"""ELISA phone -> OSC bridge. Python 3 standard library only.
Run: python tools/touch_osc_bridge.py
Phone: http://PC-LAN-IP:8765/touch-control (serves a link to Astro dev site).
Astro page: http://PC-LAN-IP:4321/touch-control
TouchDesigner: OSC In CHOP port 9000, OSC addresses /elisa/fx/<name>.
"""
import json
import os
import socket
import struct
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.getenv("ELISA_BRIDGE_HOST", "0.0.0.0")
PORT = int(os.getenv("ELISA_BRIDGE_PORT", "8765"))
OSC_HOST = os.getenv("ELISA_OSC_HOST", "127.0.0.1")
OSC_PORT = int(os.getenv("ELISA_OSC_PORT", "9000"))
ALLOWED = {"glitch", "feedback", "pixel", "blur", "displace", "audio",
           "blend", "master", "freeze", "invert", "bypass", "blackout", "strobe"}
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def osc_string(value):
    raw = value.encode("utf-8") + b"\x00"
    return raw + b"\x00" * ((-len(raw)) % 4)


def send_osc(name, value):
    message = osc_string("/elisa/fx/" + name) + osc_string(",f") + struct.pack(">f", value)
    udp.sendto(message, (OSC_HOST, OSC_PORT))


class Handler(BaseHTTPRequestHandler):
    def send_response_headers(self, code=200, mime="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response_headers(204)

    def do_GET(self):
        if self.path == "/health":
            self.send_response_headers()
            self.wfile.write(b'{"ok":true}')
        elif self.path in ("/", "/touch-control"):
            self.send_response_headers(200, "text/html; charset=utf-8")
            ip = self.headers.get("Host", "localhost").split(":")[0]
            html = ('<meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<body style="font:20px Arial;background:#090909;color:#39ff14;padding:30px">'
                    '<h1>ELISA / LIVE FX II</h1><p>Bridge OSC attivo.</p>'
                    '<a style="color:#39ff14" href="http://' + ip + ':4321/touch-control">'
                    'APRI IL CONTROLLER</a></body>')
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        if self.path != "/control":
            self.send_response_headers(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1024:
                raise ValueError("invalid length")
            payload = json.loads(self.rfile.read(length))
            name = payload["name"]
            value = float(payload["value"])
            if name not in ALLOWED or not (0 <= value <= 1):
                raise ValueError("invalid control")
            send_osc(name, value)
            self.send_response_headers()
            self.wfile.write(b'{"ok":true}')
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            self.send_response_headers(400)
            self.wfile.write(b'{"error":"invalid command"}')


if __name__ == "__main__":
    print(f"ELISA OSC bridge: http://0.0.0.0:{PORT}")
    print(f"OSC -> {OSC_HOST}:{OSC_PORT} | TouchDesigner OSC In CHOP")
    print("Use only on a trusted private Wi-Fi network.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
