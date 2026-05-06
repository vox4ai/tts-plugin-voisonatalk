# tts-plugin-voisonatalk

**Plugin for VoiSona Talk Editor REST API (direct speaker output)**

## KEY FILES
| File | Role |
|------|------|
| `tts_plugin_voisonatalk/connector.py` | VoiSonaTalkConnector implementation |

## ENTRY POINT
```python
# pyproject.toml
[project.entry-points."tts_bridge.connectors"]
voisonatalk = "tts_plugin_voisonatalk.connector:VoiSonaTalkConnector"
```

## IMPORTANT
- `synthesize()` returns `audio_data=None` (direct speaker output only)
- Requires BasicAuth for Windows REST API server
- Set env vars: `VOISONA_USER`, `VOISONA_PASS`

## SUPPORTED PARAMS
`alp`, `huskiness`, `intonation`, `pitch`, `speed`, `volume`, `style_weights`

## CONVENTIONS
- Depends on: `tts-plugin-bridge` (core)
- Uses `aiohttp` with BasicAuth
- Polls for synthesis completion with async wait