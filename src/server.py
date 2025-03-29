from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
import httpx  # Make sure to install httpx for making HTTP requests
import os

from generate_form import generate_form_background
from refine_form import refine_form_background

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/api/generate-form")
async def generate_form(company_id: str, background_tasks: BackgroundTasks):
    # Add the form generation to background tasks
    background_tasks.add_task(generate_form_background, company_id)
    
    # Return immediately with a 201 Created status
    return JSONResponse(
        content={"message": "Form generation started in the background"},
        status_code=201
    )

@app.get("/api/fetch-company-list")
async def fetch_company_list():
    url = "https://tatch.retool.com/url/company-query"
    headers = {
        'Content-Type': 'application/json',
        'X-Workflow-Api-Key': os.getenv('X-Workflow-Api-Key-COMP-LIST')
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    
    return JSONResponse(content=response.json())

@app.get("/api/refine-form")
async def refine_form(company_id: str, refine_task: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(refine_form_background, company_id, refine_task)
    return JSONResponse(
        content={"message": "Form refinement started in the background"},
        status_code=201
    )

@app.post("/api/transcribe-audio")
async def transcribe_audio(request: Request):
    deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
    if not deepgram_api_key:
        return JSONResponse(content={"error": "DEEPGRAM_API_KEY environment variable not set"}, status_code=500)
    file = await request.body()
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        'Authorization': f'Token {deepgram_api_key}',
        'Content-Type': 'audio/wav'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=file)
        if response.status_code != 200:
            return JSONResponse(content={"error": "Error transcribing audio"}, status_code=response.status_code)

        response_data = response.json()
        transcription = response_data.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')

    return JSONResponse(content={"transcription": transcription})
