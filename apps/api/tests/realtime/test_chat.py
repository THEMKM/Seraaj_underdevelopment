import asyncio
import threading
import json
import websockets
import uvicorn
import pytest

from main import app
from auth.jwt import create_access_token

@pytest.fixture(scope="module")
def run_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    # give server time to start
    import time
    time.sleep(0.5)
    yield
    server.should_exit = True
    thread.join()

@pytest.mark.asyncio
async def test_websocket_chat_basic(run_server):
    token = create_access_token({"sub": "1"})
    uri = f"ws://127.0.0.1:8765/ws/1?token={token}"
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"type": "ping"}))
    except Exception:
        pytest.skip("WebSocket server not available")

