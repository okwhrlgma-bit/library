"""Polar webhook receiver (Cycle 698·Vercel serverless function·Python).

Vercel functions Python 표준 = `from http.server import BaseHTTPRequestHandler` + `class handler`.
endpoint: https://kormarc-auto-landing.vercel.app/api/webhook

Polar webhook 표준 (https://docs.polar.sh/api-reference/webhooks-events):
    headers:
        webhook-signature: t=timestamp,v1=hex_sig
        webhook-id: msg_*
        webhook-timestamp: unix_seconds
    body: JSON event payload
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler


def _verify_polar(payload: bytes, sig_header: str, secret: str) -> bool:
    """Polar webhook 서명 검증 (HMAC SHA256·t=...,v1=... 형식)."""
    if not (payload and sig_header and secret):
        return False
    timestamp = ""
    sig = ""
    for part in sig_header.strip().split(","):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip() == "t":
            timestamp = v.strip()
        elif k.strip() == "v1":
            sig = v.strip().lower()
    if not (timestamp and sig):
        return False
    signed = f"{timestamp}.".encode() + payload
    try:
        expected = hmac.new(
            secret.encode("utf-8"), signed, hashlib.sha256
        ).hexdigest()
    except (AttributeError, TypeError):
        return False
    return hmac.compare_digest(expected, sig)


def _classify_polar_event(event_type: str) -> str:
    """이벤트 분류 (paid·refund·license·other)."""
    if not event_type:
        return "other"
    if event_type in {
        "order.created",
        "subscription.created",
        "subscription.uncanceled",
    }:
        return "paid"
    if event_type in {
        "order.refunded",
        "subscription.canceled",
        "subscription.revoked",
        "refund.created",
    }:
        return "refund"
    if event_type.startswith("benefit_grant."):
        return "license"
    return "other"


class handler(BaseHTTPRequestHandler):
    """Vercel Python serverless handler (POST·GET 둘 다)."""

    def do_GET(self):
        """헬스 체크."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "ok": True,
                    "service": "kormarc-auto-webhook",
                    "version": "0.1.0",
                    "supported": ["polar"],
                },
                ensure_ascii=False,
            ).encode("utf-8")
        )

    def do_POST(self):
        """Polar webhook 수신·검증·로그."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        secret = os.environ.get("POLAR_WEBHOOK_SECRET", "")
        sig_header = self.headers.get("webhook-signature", "")

        # 검증 (개발 모드 = secret 없으면 skip·운영 = 의무)
        verified = False
        if secret:
            verified = _verify_polar(body, sig_header, secret)
            if not verified:
                self.send_response(401)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b'{"error": "invalid signature"}'
                )
                return

        # 파싱
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"error": "invalid json"}')
            return

        event_type = payload.get("type", "")
        category = _classify_polar_event(event_type)

        # MongoDB 로그 (선택·환경변수 있으면 시도)
        mongo_logged = False
        mongo_uri = os.environ.get("MONGODB_URI", "")
        if mongo_uri and category == "paid":
            try:
                from pymongo import MongoClient  # type: ignore[import-not-found]

                client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
                db_name = os.environ.get("MONGODB_DB_NAME", "kormarc_auto")
                client[db_name]["polar_webhooks"].insert_one(
                    {
                        "event_type": event_type,
                        "category": category,
                        "payload": payload,
                        "received_at": datetime.now(UTC).isoformat(),
                    }
                )
                mongo_logged = True
            except Exception:
                mongo_logged = False

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "ok": True,
                    "event_type": event_type,
                    "category": category,
                    "verified": verified,
                    "mongo_logged": mongo_logged,
                },
                ensure_ascii=False,
            ).encode("utf-8")
        )
