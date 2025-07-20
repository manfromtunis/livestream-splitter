"""FastAPI backend for livestream splitter web interface"""

import os
import asyncio
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our splitter components
from stream_splitter.config import Config, OutputConfig, ProcessingConfig
from stream_splitter.splitter import Splitter


app = FastAPI(title="Livestream Splitter Web UI", version="1.0.0")

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
from pathlib import Path
static_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global variables for job tracking
jobs = {}
job_counter = 0


class SplitRequest(BaseModel):
    """Request model for video splitting"""
    max_length: int = 1200  # 20 minutes
    quality: str = "high"
    format: str = "mp4"
    naming_pattern: str = "{title}_part{index:02d}_{date}"
    

class JobStatus(BaseModel):
    """Job status model"""
    id: int
    status: str  # "pending", "processing", "completed", "failed"
    progress: int = 0
    message: str = ""
    created_at: str
    completed_at: Optional[str] = None
    output_files: List[str] = []
    error: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>Livestream Splitter</h1><p>Frontend not found. Please check installation.</p>")


@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file for processing"""
    if not file.filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.ts')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # Create uploads directory
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save uploaded file in chunks to handle large files
    file_path = upload_dir / file.filename
    total_size = 0
    
    try:
        with open(file_path, "wb") as buffer:
            while True:
                # Read file in chunks (1MB at a time)
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
                total_size += len(chunk)
    except Exception as e:
        # Clean up partial file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return {"filename": file.filename, "path": str(file_path), "size": total_size}


@app.post("/api/split")
async def split_video(
    background_tasks: BackgroundTasks,
    filename: str,
    request: SplitRequest
):
    """Start video splitting process"""
    global job_counter, jobs
    
    job_counter += 1
    job_id = job_counter
    
    # Create job entry
    job = JobStatus(
        id=job_id,
        status="pending",
        message="Initializing video splitting...",
        created_at=datetime.now().isoformat()
    )
    jobs[job_id] = job
    
    # Start background task
    background_tasks.add_task(process_video, job_id, filename, request)
    
    return {"job_id": job_id, "status": "started"}


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: int):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    return list(jobs.values())


@app.get("/api/download/{job_id}/{filename}")
async def download_file(job_id: int, filename: str):
    """Download a processed file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if filename not in job.output_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path("outputs") / str(job_id) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(file_path, filename=filename)


async def process_video(job_id: int, filename: str, request: SplitRequest):
    """Background task to process video"""
    try:
        job = jobs[job_id]
        job.status = "processing"
        job.message = "Setting up video processing..."
        
        # Setup paths
        input_path = Path("uploads") / filename
        output_dir = Path("outputs") / str(job_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create configuration
        output_config = OutputConfig(
            directory=output_dir,
            format=request.format,
            naming_pattern=request.naming_pattern,
            max_segment_length=request.max_length
        )
        
        processing_config = ProcessingConfig(
            quality=request.quality
        )
        
        config = Config(
            input_path=input_path,
            output=output_config,
            processing=processing_config
        )
        
        # Update job status
        job.message = "Analyzing video file..."
        
        # Create splitter and process
        splitter = Splitter(config)
        
        # Mock progress updates (since we can't easily hook into FFmpeg progress)
        job.message = "Splitting video into segments..."
        job.progress = 25
        
        # Run the actual splitting
        output_files = splitter.process()
        
        # Update job with results
        job.status = "completed"
        job.progress = 100
        job.message = f"Successfully created {len(output_files)} segments"
        job.completed_at = datetime.now().isoformat()
        job.output_files = [f.name for f in output_files]
        
    except Exception as e:
        job = jobs[job_id]
        job.status = "failed"
        job.error = str(e)
        job.message = f"Error: {str(e)}"
        job.completed_at = datetime.now().isoformat()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)