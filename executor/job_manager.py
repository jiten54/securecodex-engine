import uuid
import subprocess
import os

class JobManager:
    def __init__(self):
        self.jobs = {}

    def create_job(self, file_path, level="medium"):
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "file": file_path,
            "level": level
        }
        return job_id

    def run_job(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        job["status"] = "running"
        output_path = f"protected_{os.path.basename(job['file'])}"
        
        try:
            result = subprocess.run([
                "python3", "cli/engine_cli.py", 
                job["file"], 
                "--level", job["level"],
                "--output", output_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                job["status"] = "done"
                job["output"] = output_path
            else:
                job["status"] = "failed"
                job["error"] = result.stderr
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            
        return job
