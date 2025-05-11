from fastapi import FastAPI, HTTPException
from src.backend import (
    process_country_count,
    extract_authors,
    generate_country_count,
)
from goodreads_scraper.scrape import process_goodreads_url
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.wsgi import WSGIMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware
from src.setup import setup_db
from graph_db import create_constraints
from contextlib import asynccontextmanager
from logger import logger
import os

class ProfileRequest(BaseModel):
    profile_url: HttpUrl


@asynccontextmanager
async def lifespan(app: FastAPI):
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    setup_db(uri=neo4j_uri,password=neo4j_password)
    create_constraints()
    yield

app = FastAPI(lifespan=lifespan)
# Add Werkzeug Profiler Middleware
app_with_profiler = WSGIMiddleware(
    ProfilerMiddleware(app, restrictions=[30], profile_dir="./profile")
)


@app.post("/process-profile/")
def profile(request: ProfileRequest):
    try:
        logger.info(f"[Process Profile Request]: Starting for {request.profile_url}!")
        books = process_goodreads_url(str(request.profile_url))
        logger.info("[Process Profile] Extracted books!")
        cont = extract_authors(books)
        logger.info("[Process Profile] Extracted authors!")
        cc = generate_country_count(cont)
        logger.info("[Process Profile] Counted countries!")
        full_count = process_country_count(cc)
        logger.info("[Process Profile] Processed country count!")
        return {"data": full_count}
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))
