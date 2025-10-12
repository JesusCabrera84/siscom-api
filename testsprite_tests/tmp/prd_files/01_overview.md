# SISCOM API - Product Requirements Document

## Overview

SISCOM API is a RESTful API built with FastAPI for managing GPS device communications from Suntech and Queclink manufacturers. The system provides both historical data access and real-time streaming capabilities using Server-Sent Events (SSE).

## Purpose

Enable efficient querying and real-time monitoring of GPS device communications for tracking vehicles and assets.

## Target Users

- Fleet management systems
- Tracking platform integrators
- Real-time monitoring dashboards
- Analytics and reporting systems

## Key Value Propositions

1. **Dual-brand support**: Works with both Suntech and Queclink GPS devices
2. **Real-time streaming**: SSE support for live tracking updates
3. **Secure access**: JWT authentication for protected endpoints
4. **Scalable**: Async architecture with connection pooling
5. **Well-documented**: OpenAPI/Swagger documentation included
