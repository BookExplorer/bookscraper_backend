from fastapi import FastAPI, HTTPException
from backend import (
    process_country_count,
    process_profile,
    extract_authors,
    generate_country_count,
)
from pydantic import BaseModel, HttpUrl
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ProfileRequest(BaseModel):
    profile_url: HttpUrl


app = FastAPI()


@app.post("/process-profile/")
def profile(request: ProfileRequest):
    logging.info(f"Received profile URL: {request.profile_url}")
    try:
        books = process_profile(str(request.profile_url))
        logging.info("Profile processed successfully.")
        cont = extract_authors(books)
        logging.info("Authors extracted!")
        cc = generate_country_count(cont)
        logging.info("Country count generated")
        full_count = process_country_count(cc)
        logging.info("Full country count ready")
        return {"data": full_count}
    except Exception as e:
        logging.error(f"Error processing profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
