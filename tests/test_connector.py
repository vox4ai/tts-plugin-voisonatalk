import pytest
from aioresponses import aioresponses
from tts_plugin_voisonatalk.connector import VoiSonaTalkConnector
from tts_plugin_bridge.protocol import TTSRequest


@pytest.mark.asyncio
async def test_connector_is_available():
    connector = VoiSonaTalkConnector(server_url="http://localhost:32766")
    with aioresponses() as m:
        m.get("http://localhost:32766/api/talk/v1/languages", status=200)
        assert await connector.is_available() is True
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_success():
    connector = VoiSonaTalkConnector(server_url="http://localhost:32766")
    req = TTSRequest(text="hello", speed=1.0)

    with aioresponses() as m:
        # Request synthesis
        m.post(
            "http://localhost:32766/api/talk/v1/speech-syntheses",
            status=201,
            payload={"uuid": "test-uuid"},
        )

        # Poll for status (once)
        m.get(
            "http://localhost:32766/api/talk/v1/speech-syntheses/test-uuid",
            status=200,
            payload={"state": "succeeded"},
        )

        res = await connector.synthesize(req)

        assert res.success is True
        assert res.audio_data is None
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_failure():
    connector = VoiSonaTalkConnector(server_url="http://localhost:32766")
    req = TTSRequest(text="hello")

    with aioresponses() as m:
        m.post(
            "http://localhost:32766/api/talk/v1/speech-syntheses",
            status=201,
            payload={"uuid": "test-uuid"},
        )

        m.get(
            "http://localhost:32766/api/talk/v1/speech-syntheses/test-uuid",
            status=200,
            payload={"state": "failed"},
        )

        res = await connector.synthesize(req)

        assert res.success is False
        assert "failure" in res.error
    await connector.close()


@pytest.mark.asyncio
async def test_connector_context_manager():
    async with VoiSonaTalkConnector() as connector:
        assert connector.ENGINE_NAME == "voisonatalk"

    if connector._session:
        assert connector._session.closed
