# Architecture

## Overview
- FastAPI app with SQLAlchemy models
- PostgreSQL database
- JWT-based auth for protected routes

## Data flow
HTTP request -> FastAPI route -> SQLAlchemy -> Postgres -> response

## Key decisions
- Create tables at startup for MVP simplicity
- Seed demo data on boot
