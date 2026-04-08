"""Tests unitarios para streaming WebSocket y routing por device_id."""

import asyncio

import pytest

from app.api.routes.stream import (
    WebSocketManager,
    _extract_device_id_from_alerts,
    _extract_device_id_from_positions,
    _normalize_alert_message,
    _resolve_websocket_event_name,
)


@pytest.mark.unit
class TestWebSocketManager:
    """Valida suscripciones y publicación por device_id."""

    def test_publish_to_subscribed_device(self):
        async def run_test():
            manager = WebSocketManager()
            queues = await manager.subscribe(["dev-1", "dev-2"])

            assert len(queues) == 1

            message = {"data": {"device_id": "dev-1", "lat": 19.21}}
            await manager.publish(message, "dev-1")

            received = await queues[0].get()
            assert received == message

        asyncio.run(run_test())

    def test_publish_ignores_unsubscribed_device(self):
        async def run_test():
            manager = WebSocketManager()
            queues = await manager.subscribe(["dev-1"])

            await manager.publish({"data": {"device_id": "dev-2"}}, "dev-2")

            assert queues[0].qsize() == 0

        asyncio.run(run_test())

    def test_unsubscribe_removes_subscription(self):
        async def run_test():
            manager = WebSocketManager()
            queues = await manager.subscribe(["dev-1"])

            await manager.unsubscribe(["dev-1"], queues)
            await manager.publish({"data": {"device_id": "dev-1"}}, "dev-1")

            assert queues[0].qsize() == 0

        asyncio.run(run_test())


@pytest.mark.unit
class TestPayloadExtraction:
    """Valida extracción de device_id para ambos tipos de mensaje."""

    def test_extract_device_id_from_positions_nested_data(self):
        payload = {"data": {"device_id": "pos-dev-1"}}
        assert _extract_device_id_from_positions(payload) == "pos-dev-1"

    def test_extract_device_id_from_alerts_root(self):
        payload = {"device_id": "alert-dev-1", "alert_type": "Engine OFF"}
        assert _extract_device_id_from_alerts(payload) == "alert-dev-1"

    def test_extract_device_id_from_alerts_nested_payload(self):
        payload = {
            "payload": {
                "device_id": "alert-dev-2",
                "engine_status": "OFF",
            }
        }
        assert _extract_device_id_from_alerts(payload) == "alert-dev-2"

    def test_normalize_alert_message(self):
        raw = {"device_id": "alert-dev-1", "alert_type": "Engine OFF"}
        normalized = _normalize_alert_message(raw, "tracking/alerts")

        assert normalized["message_type"] == "alert"
        assert normalized["source_topic"] == "tracking/alerts"
        assert normalized["data"] == raw

    def test_resolve_websocket_event_name_for_alert(self):
        payload = {"message_type": "alert", "data": {"device_id": "dev-1"}}
        assert _resolve_websocket_event_name(payload) == "alert"

    def test_resolve_websocket_event_name_for_standard_message(self):
        payload = {"data": {"device_id": "dev-1"}}
        assert _resolve_websocket_event_name(payload) == "message"
