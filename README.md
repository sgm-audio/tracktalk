# TrackTalk

A small Python script that takes text commands like "mute drums" and sends them to REAPER over OSC. It doesn't do speech-to-text. You feed it text from whatever dictation or STT you already use, or you type.

```
any speech-to-text (or typing) -> tracktalk_bridge.py -> OSC -> REAPER
```

One file, one dependency (`python-osc`). No model, no cloud, no GPU.

## Setup

```
pip install -r requirements.txt
python tracktalk_bridge.py                  # type commands
python tracktalk_bridge.py --listen         # read lines from stdin
python tracktalk_bridge.py "mute drums"     # one shot
python tracktalk_bridge.py --port 9000      # OSC port (default 8000)
```

In REAPER: Options > Preferences > Control/OSC/Web, add an OSC device listening on the same port.

## What it actually does

Parsing is keyword matching. The first keyword it finds picks the action, and the first track name it finds picks the track. Track names map to fixed track numbers in `TRACK_MAP` (`tracktalk_bridge.py:50-53`), so edit that for your session.

| Text contains | Sends |
|---|---|
| louder / turn up / boost | `/track/N/volume`, fader set to +N dB (default +2 dB) |
| quieter / turn down / cut | `/track/N/volume`, fader set to -N dB |
| mute / silence | `/track/N/mute 1` |
| solo / isolate | `/track/N/solo 1` |
| pan left / pan right | `/track/N/pan -0.5` or `0.5` |
| reverb, delay / echo | selects the track, then runs action 40271 |

## Known issues

I ran the parser by hand against the commands above. These don't behave the way you'd expect yet:

- Volume is absolute, not relative. "Louder vocals" sets the vocal fader to +2 dB, it doesn't add 2 dB. The dB-to-OSC scaling (`(db + 60) / 72`, line 40) is my approximation, not REAPER's fader curve.
- "Pan bass left" returns nothing. The pan keyword has to be the exact phrase "pan left" or "pan right".
- "Add reverb to rhythm" falls back to track 1, because `TRACK_MAP` only knows "rhythm left" and "rhythm right".
- Reverb and delay both run action 40271. I haven't checked that ID against REAPER's action list.
- Anything with no matching track name goes to track 1.
- There are no tests yet.

Not tested against a live REAPER session in this pass.

## License

MIT. See [LICENSE](LICENSE).
