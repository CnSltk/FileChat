from fastapi import FastAPI

app = FastAPI(title="FileChat")


@app.get("/health")
def health():
    return {"status": "ok"}
