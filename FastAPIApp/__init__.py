from fastapi import FastAPI, Request, Header
from linebot.exceptions import InvalidSignatureError
from starlette.exceptions import HTTPException
from FastAPIApp.handler import handler

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request, x_line_signature=Header(None)):
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="InvalidSignatureError")
    
    return "OK"