import json
import sys
from fastapi import FastAPI, HTTPException, Request
import asyncio
import random
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
import logging
app = FastAPI()

# allow all origins
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def unhandled_exception_handler(request: Request, exc: Exception) -> PlainTextResponse:
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
    """

    # gather the request information
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)

    # save the log
    logging.error(
        f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}> - Stack trace: {exception_traceback}',
    )

    return PlainTextResponse(str(exc), status_code=500)

app.add_exception_handler(Exception, unhandled_exception_handler)

def to_ndjson(data):
    return json.dumps(data).encode() + b"\n"

async def mock_chat_generator(user_input: str):
    base_response = f"Ok, I got your input: {user_input}\n---"
    
    paragraphs = [
        "\n---\nHi, I'm working ...",
        "\n---\nProcessing your data request ...",
        "\n---\nSystem just got {} records".format(random.randint(1,24)),
        "\n---\nDone! Return code {}%".format(random.randint(50,100))
    ]
    
    full_response = base_response + "".join(paragraphs)
    
    for i in range(0, len(full_response), 10):
        chunk = full_response[i:i+10]
        await asyncio.sleep(random.uniform(0.1, 0.5))
        yield to_ndjson({"content": chunk, "event": "stream"})
    
    # Send a final message to signal completion
    yield to_ndjson({"content": "", "event": "complete"})
    

@app.get("/")
async def index(request: Request):
    return {"message": "Hello, World"}


@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()

    return StreamingResponse(
        mock_chat_generator(data["message"]),
        media_type="application/x-ndjson"
    )

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

