import asyncio
import os
import aiohttp
from typing import AsyncIterator, Optional
from tts_plugin_bridge.protocol import TTSConnector, TTSRequest, TTSResponse


class VoiSonaTalkConnector(TTSConnector):
    ENGINE_NAME = "voisonatalk"
    # Voisona Talk API parameters (global_parameters)
    SUPPORTED_PARAMS = [
        "alp",
        "huskiness",
        "intonation",
        "pitch",
        "speed",
        "volume",
        "style_weights",
    ]

    def __init__(
        self,
        server_url: str = "http://localhost:32766",
        user: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 30.0,
        max_wait: float = 60.0,
        poll_interval: float = 0.2,
    ):
        self.server_url = server_url.rstrip("/")
        self.api_url = f"{self.server_url}/api/talk/v1"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_wait = max_wait
        self.poll_interval = poll_interval

        # Use provided auth or environment variables
        auth_user = user or os.getenv("VOISONA_USER", "")
        auth_pass = password or os.getenv("VOISONA_PASS", "")
        self.auth = aiohttp.BasicAuth(auth_user, auth_pass) if auth_user else None

        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(auth=self.auth, timeout=self.timeout)
        return self._session

    async def is_available(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/languages", timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def synthesize(self, req: TTSRequest) -> TTSResponse:
        """
        Voisona Talk 本体で音声を発声させます。
        注意: このコネクタは audio_data を返却しません (audio_data=None)。
        """
        try:
            # Additional validation
            if "alp" in req.extra and not (-1 <= req.extra["alp"] <= 1):
                return TTSResponse.fail("alp must be between -1 and 1")
            if "pitch" in req.extra and not (-600 <= req.extra["pitch"] <= 600):
                return TTSResponse.fail("pitch must be between -600 and 600")

            session = await self._get_session()

            # Voisona Talk API payload
            # speed: 話速 (0.2~5), pitch: ピッチシフト (cent, -600~600)
            global_params = {
                "speed": req.speed,
                "volume": req.volume if req.volume is not None else 0.0,
            }
            if req.pitch is not None:
                global_params["pitch"] = req.pitch

            # Merge extra parameters (alp, huskiness, intonation, style_weights)
            for key in self.SUPPORTED_PARAMS:
                if key in req.extra and key not in global_params:
                    global_params[key] = req.extra[key]

            payload = {
                "text": req.text,
                "language": req.extra.get("language", "ja_JP"),
                "destination": "audio_device",
                "force_enqueue": True,
                "global_parameters": global_params,
            }

            if "voice_name" in req.extra:
                payload["voice_name"] = req.extra["voice_name"]
            if "voice_version" in req.extra:
                payload["voice_version"] = req.extra["voice_version"]

            # Request synthesis
            async with session.post(
                f"{self.api_url}/speech-syntheses", json=payload
            ) as resp:
                if resp.status not in (201, 200):
                    error_text = await resp.text()
                    return TTSResponse.fail(f"HTTP {resp.status}: {error_text}")

                data = await resp.json()
                uuid = data["uuid"]

            # Poll for completion
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < self.max_wait:
                async with session.get(
                    f"{self.api_url}/speech-syntheses/{uuid}"
                ) as resp:
                    if resp.status != 200:
                        break

                    info = await resp.json()
                    state = info.get("state")
                    if state == "succeeded":
                        return TTSResponse(success=True, audio_data=None)
                    elif state == "failed":
                        return TTSResponse.fail(
                            "VoiSona Talk reported synthesis failure"
                        )

                await asyncio.sleep(self.poll_interval)

            return TTSResponse.fail("Synthesis timeout")

        except aiohttp.ClientError as e:
            return TTSResponse.fail(f"Connection error: {e}")
        except Exception as e:
            return TTSResponse.fail(f"Unexpected error: {type(e).__name__}: {e}")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def synthesize_stream(self, req: TTSRequest) -> AsyncIterator[bytes]:
        result = await self.synthesize(req)
        if result.success:
            yield b""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
