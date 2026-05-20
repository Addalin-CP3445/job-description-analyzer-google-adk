# CV Matchmaker AI (Job Description Analyzer)

CV Matchmaker AI is a sophisticated multi-agent application powered by Google's Agent Development Kit (ADK) and Vertex AI. It intelligently cross-references a candidate's Curriculum Vitae (CV) against a target Job Description (JD) to provide a comprehensive gap analysis and a personalized career advisory report. 

It features a sleek, modern Web UI for easy file uploads and result visualization.

## Features

- **Multi-Agent Pipeline**: 
  - **ParserAgent**: Extracts hard skills, soft skills, and certifications strictly based on a Pydantic schema.
  - **MatchmakerAgent**: Performs a gap analysis to identify matched and missing skills, mapping missing skills to remediation strategies (e.g., courses, certifications, or CV rewrites).
  - **CareerCoachAgent**: Translates the gap analysis into a professional, human-readable advisory report.
- **Dynamic Web Search**: Automatically searches the web (using `googlesearch-python`) for the best real-world courses or certifications to fill identified skill gaps.
- **Modern Web Interface**: A beautifully designed, responsive FastAPI frontend featuring dark-mode aesthetics, glassmorphism, and drag-and-drop PDF/TXT file upload support.
- **PDF Parsing**: Robustly extracts text from uploaded PDF resumes using `PyMuPDF`.

## Prerequisites

- **Python 3.10+**
- **Google Cloud Platform (GCP) Account** with **Vertex AI API** enabled.
- **Service Account Key**: A GCP Service Account with the `Vertex AI User` role.

## Installation & Setup

1. **Clone the repository** and navigate to the directory.

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install the dependencies**:
   ```powershell
   pip install -r requirements.txt
   pip install PyMuPDF python-multipart vertexai
   ```

4. **Configure Authentication**:
   - Download your Service Account JSON key from the Google Cloud Console.
   - Rename it to `gdg-project.json` (or any name you prefer) and place it in the root folder.
   - Open `.env` (create one if it doesn't exist) and add the following line to set your application default credentials:
     ```env
     GOOGLE_APPLICATION_CREDENTIALS="gdg-project.json"
     ```

5. **Configure your Project ID**:
   Open `main.py` and ensure the `VERTEX_MODEL_NAME` on line 49 points to your specific Google Cloud Project ID and Region:
   ```python
   VERTEX_MODEL_NAME = "projects/your-project-id/locations/us-central1/publishers/google/models/gemini-2.5-flash"
   ```

## Running the Application

### Option 1: Web UI (Recommended)
Start the FastAPI server:
```powershell
python -m uvicorn app:app --reload
```
Open your browser and navigate to [http://localhost:8000](http://localhost:8000). You can upload a `.pdf` or `.txt` CV, paste your job description, and view the generated report seamlessly.

### Option 2: Command Line Interface
You can also run the agent pipeline headlessly via the CLI:
1. Ensure you have `cv.txt` and `jd.txt` files in the root directory.
2. Run the script:
   ```powershell
   python main.py
   ```
   The final report will be printed directly to your console.
