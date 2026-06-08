# TrackTalk

**Voice control for REAPER via OSC. Talk to your tracks.**

TrackTalk bridges voice commands to REAPER using OSC (Open Sound Control). It doesn't do transcription itself — it consumes text from any speech-to-text source and converts it into DAW commands.

## How It Works

```
Any speech-to-text → TrackTalk → OSC → REAPER
```

You supply the transcription (Windows dictation, macOS dictation, a local model, whatever). TrackTalk handles the rest:
- Parses natural language into DAW actions
- Routes commands to REAPER tracks via OSC
- Supports custom track name mappings

## Quick Start

```powershell
pip install python-osc
python tracktalk_bridge.py
```

Configure REAPER:
1. Options → Preferences → Control/OSC/Web
2. Add OSC device on port 8000

## Commands

| Say | Does |
|---|---|
| "Louder vocals" | +2dB on vocal track |
| "Mute drums" | Mute drum track |
| "Solo lead" | Solo lead guitar |
| "Pan bass left" | Pan bass track left |
| "Add reverb to rhythm" | Insert reverb on rhythm track |

## Why Not Whisper/Vertex AI

TrackTalk is intentionally lightweight. No cloud dependencies, no GPU requirements, no model downloads. The voice engine is your choice — use whatever works on your system.

## License

MIT — see LICENSE file
