#!/usr/bin/env python3.10
from __future__ import annotations

import json

import uvicorn
from fastapi import FastAPI
from fastapi import status
from fastapi.param_functions import Header
from fastapi.requests import Request
from fastapi.responses import Response

import events
import paypal
import settings

app = FastAPI()


@app.post("/paypal/webhooks")
async def paypal_webhooks(
    request: Request,
    paypal_transmission_sig: str = Header(...),
    paypal_auth_algo: str = Header(...),
    paypal_cert_url: str = Header(...),
    paypal_transmission_id: str = Header(...),
    paypal_transmission_time: str = Header(...),
) -> Response:
    request_data = (await request.body()).decode()

    verified = await paypal.verify_signature(
        paypal_transmission_id,
        paypal_transmission_time,
        settings.PAYPAL_WEBHOOK_ID,
        request_data,
        paypal_cert_url,
        paypal_transmission_sig,
        paypal_auth_algo,
    )
    if not verified:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    webhook_data = json.loads(request_data)
    await events.handle(webhook_data)

    return Response(status_code=status.HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run(
        app,  # type: ignore
        port=1234,
    )
