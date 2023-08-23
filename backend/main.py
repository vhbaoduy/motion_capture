from fastapi import FastAPI, File, UploadFile

import requests

url = "http://localhost:8000/uploadfile/"
files = {"file": open("example.mp4", "rb")}
response = requests.post(url, files=files)

print(response.json())

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}