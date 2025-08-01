from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Test server working"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("test_server:app", host="127.0.0.1", port=8001, reload=False)
