"""
TrackTalk Bridge — Voice to REAPER via OSC
===========================================
Takes text commands (from any speech-to-text source) and routes them to REAPER.

Usage:
    python tracktalk_bridge.py                # Interactive: type commands
    python tracktalk_bridge.py --listen       # Listen on stdin (pipe from dictation)
    python tracktalk_bridge.py "louder vocals"  # One-shot command

Architecture:
    Any STT → TrackTalk parse → OSC → REAPER

No transcription models. No cloud. No GPU. Just the bridge.
"""

import os, sys, json, re, time, logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("TrackTalk")

try:
    from pythonosc import udp_client
    OSC_AVAILABLE = True
except ImportError:
    logger.warning("python-osc not installed. Run: pip install python-osc")
    OSC_AVAILABLE = False

class ReaperOSC:
    def __init__(self, host="127.0.0.1", port=8000):
        self.client = udp_client.SimpleUDPClient(host, port) if OSC_AVAILABLE else None
        logger.info(f"OSC {'connected' if self.client else 'UNAVAILABLE'} {host}:{port}")

    def send(self, address, *args):
        if self.client: self.client.send_message(address, args)
        logger.info(f"  OSC: {address} {args}")

    def set_volume(self, track, db):
        norm = max(0, min(1, (db + 60) / 72))
        self.send(f"/track/{track}/volume", norm)

    def set_pan(self, track, pan): self.send(f"/track/{track}/pan", pan)
    def mute(self, track): self.send(f"/track/{track}/mute", 1)
    def solo(self, track): self.send(f"/track/{track}/solo", 1)
    def select(self, track): self.send(f"/track/{track}/select", 1)
    def run_action(self, aid): self.send("/action", aid)

class TrackTalk:
    TRACK_MAP = {
        "rhythm_left":3,"rhythm left":3,"rhythm_right":4,"rhythm right":4,
        "lead":5,"lead guitar":5,"bass":6,"drums":8,
        "vocals":7,"vocal":7,"master":0,
    }
    KEYWORDS = {
        "louder|turn up|boost": ("gain_up", None),
        "quieter|turn down|cut": ("gain_down", None),
        "mute|silence": ("mute", None),
        "solo|isolate": ("solo", None),
        "pan left": ("pan_left", None),
        "pan right": ("pan_right", None),
        "reverb": ("fx_reverb", 40271),
        "delay|echo": ("fx_delay", 40271),
    }

    def __init__(self, port=8000): self.reaper = ReaperOSC(port=port)

    def parse(self, text):
        text = text.lower().strip()
        for keys, (action, aid) in self.KEYWORDS.items():
            for kw in keys.split("|"):
                if kw in text:
                    target = None
                    for tn in self.TRACK_MAP:
                        if tn in text: target = tn; break
                    nums = re.findall(r"(\d+(?:\.\d+)?)\s*(?:db|dB|DB|%| times)?", text)
                    param = float(nums[0]) if nums else 2.0
                    return {"action":action,"target":target,"param":param,"raw":text}
        return None

    def execute(self, cmd):
        action, target, param = cmd["action"], cmd.get("target"), cmd.get("param",2.0)
        tn = (target or "").lower().replace("_"," ")
        track = self.TRACK_MAP.get(tn, 1)
        if action == "gain_up": self.reaper.set_volume(track, param)
        elif action == "gain_down": self.reaper.set_volume(track, -param)
        elif action == "mute": self.reaper.mute(track)
        elif action == "solo": self.reaper.solo(track)
        elif action == "pan_left": self.reaper.set_pan(track, -0.5)
        elif action == "pan_right": self.reaper.set_pan(track, 0.5)
        elif action == "fx_reverb": self.reaper.select(track); self.reaper.run_action(40271)
        elif action == "fx_delay": self.reaper.select(track); self.reaper.run_action(40271)

def main():
    import argparse
    p = argparse.ArgumentParser(description="TrackTalk — Voice to REAPER bridge")
    p.add_argument("command", nargs="?", help="One-shot command text")
    p.add_argument("--listen", action="store_true", help="Listen on stdin")
    p.add_argument("--port", type=int, default=8000, help="OSC port (default 8000)")
    args = p.parse_args()
    tt = TrackTalk(port=args.port)
    if args.command:
        c = tt.parse(args.command)
        if c: tt.execute(c)
        else: print(f"? {args.command}")
        return
    if args.listen:
        logger.info("TrackTalk listening... (Ctrl+C to stop)")
        try:
            for line in sys.stdin:
                if line.strip():
                    c = tt.parse(line.strip())
                    if c: tt.execute(c)
                    else: logger.info(f"  ? {line.strip()}")
        except KeyboardInterrupt: pass
        return
    logger.info('TrackTalk — type commands. Examples: "louder vocals" "mute drums"')
    try:
        while True:
            text = input("> ")
            if text.lower() in ("quit","exit","q"): break
            c = tt.parse(text)
            if c: tt.execute(c)
            else: print(f"  ? {text}")
    except (KeyboardInterrupt,EOFError): pass
    logger.info("TrackTalk stopped.")

if __name__ == "__main__": main()
