from fastapi import FastAPI, HTTPException
from backend import (
    process_country_count,
    process_profile,
    extract_authors,
    generate_country_count,
)
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.wsgi import WSGIMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware


class ProfileRequest(BaseModel):
    profile_url: HttpUrl


app = FastAPI()


# Add Werkzeug Profiler Middleware
app.add_middleware(
    WSGIMiddleware,
    app=ProfilerMiddleware(
        app=app,
        restrictions=[30],  # Adjust the restrictions as needed
        profile_dir="profile",  # Directory to save profiling results
    ),
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
