from fastapi import FastAPI, HTTPException
from backend import (
    process_country_count,
    extract_authors,
    generate_country_count,
)
from goodreads_scraper.scrape import process_profile
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.wsgi import WSGIMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware
from setup import setup_db

class ProfileRequest(BaseModel):
    profile_url: HttpUrl


app = FastAPI()

setup_db()
# Add Werkzeug Profiler Middleware
app_with_profiler = WSGIMiddleware(
    ProfilerMiddleware(app, restrictions=[30], profile_dir="./profile")
)


@app.post("/process-profile/")
def profile(request: ProfileRequest):
    try:
        books = process_profile(str(request.profile_url))
        cont = extract_authors(books)
        cc = generate_country_count(cont)
        full_count = process_country_count(cc)
        return {"data": full_count}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
