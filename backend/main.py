from fastapi import FastAPI, UploadFile, File
from typing import List
import shutil
import os

app = FastAPI()

# Temporary directory to store uploaded files and output files
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

# Create the directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_files(files):
    output_files = []

    for uploaded_file in files:
        # Save the uploaded file to a temporary directory
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
        with open(file_path, "wb") as file:
            shutil.copyfileobj(uploaded_file.file, file)

    return {"message": "Files uploaded and processed successfully", "output_files": output_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, log_level="debug", reload=True,)
