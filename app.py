from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import fitz  # PyMuPDF
from pydantic import BaseModel
import os

from main import run_analysis

app = FastAPI(title="CV Analyzer UI")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount the static directory to serve HTML, CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def analyze_cv(cv_file: UploadFile = File(...), jd_text: str = Form(...)):
    if not cv_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    cv_text = ""
    file_bytes = await cv_file.read()
    
    if cv_file.filename.lower().endswith(".pdf"):
        try:
            # Read PDF from bytes
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                cv_text += page.get_text()
            doc.close()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
    elif cv_file.filename.lower().endswith(".txt"):
        cv_text = file_bytes.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")
    
    if not cv_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from CV file")
    
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is empty")
        
    try:
        report = run_analysis(cv_text, jd_text)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
