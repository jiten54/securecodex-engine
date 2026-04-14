import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import multer from "multer";
import { v4 as uuidv4 } from "uuid";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const upload = multer({ dest: "uploads/" });

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Job Store (In-memory for now, could be Redis)
  const jobs: Record<string, any> = {};

  // API Routes
  app.post("/api/engine/process", upload.single("file"), (req, res) => {
    const file = req.file;
    const level = req.body.level || "medium";
    const jobId = uuidv4();

    if (!file) {
      return res.status(400).json({ error: "No file uploaded" });
    }

    jobs[jobId] = {
      id: jobId,
      status: "running",
      startTime: new Date(),
      level,
    };

    const pythonProcess = spawn("python3", [
      "cli/engine_cli.py",
      file.path,
      "--level",
      level,
      "--output",
      `uploads/protected_${jobId}.py`,
    ]);

    let output = "";
    let error = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      error += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code === 0) {
        jobs[jobId].status = "done";
        jobs[jobId].outputFile = `protected_${jobId}.py`;
        jobs[jobId].log = output;
      } else {
        jobs[jobId].status = "failed";
        jobs[jobId].error = error || "Unknown error";
      }
      // Cleanup original upload
      fs.unlink(file.path, () => {});
    });

    res.json({ jobId, status: "queued" });
  });

  app.get("/api/engine/status/:jobId", (req, res) => {
    const { jobId } = req.params;
    const job = jobs[jobId];

    if (!job) {
      return res.status(404).json({ error: "Job not found" });
    }

    res.json(job);
  });

  app.get("/api/engine/download/:jobId", (req, res) => {
    const { jobId } = req.params;
    const job = jobs[jobId];

    if (!job || job.status !== "done") {
      return res.status(404).json({ error: "File not ready or job not found" });
    }

    const filePath = path.join(__dirname, "uploads", job.outputFile);
    res.download(filePath);
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
