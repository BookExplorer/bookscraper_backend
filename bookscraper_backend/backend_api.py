from fastapi import FastAPI, HTTPException
from bookscraper_backend.backend import (
    process_country_count,
    extract_authors,
    generate_country_count,
)
from goodreads_scraper.scrape import process_profile
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.wsgi import WSGIMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware
from bookscraper_backend.setup import setup_db
from graph_db import create_constraints
from contextlib import asynccontextmanager
from logger import logger
class ProfileRequest(BaseModel):
    profile_url: HttpUrl


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_db(uri = "bolt://neo4j@graph_db:7687") # If I pass the actual docker url, this should be fine, right? 
    create_constraints()
    yield

app = FastAPI(lifespan=lifespan)



@app.post("/process-profile/")
def profile(request: ProfileRequest):
    try:
        logger.info(f"[Process Profile Request]: Starting for {request.profile_url}!")
        books = process_profile(str(request.profile_url))
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
