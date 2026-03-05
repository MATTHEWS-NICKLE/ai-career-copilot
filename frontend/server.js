const express = require("express");
const axios = require("axios");
const cors = require("cors");
const path = require("path");
const multer = require("multer");
const FormData = require("form-data");
const fs = require("fs");

const upload = multer({ dest: "uploads/" });

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// proxy a multipart/form-data upload to the FastAPI backend
app.post("/upload_resume", upload.single("file"), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No file provided" });
    }

    const form = new FormData();
    form.append("file", fs.createReadStream(req.file.path), req.file.originalname);

    try {
        const response = await axios.post("http://127.0.0.1:8000/upload_resume/", form, {
            headers: form.getHeaders(),
            maxContentLength: Infinity,
            maxBodyLength: Infinity,
        });
        res.json(response.data);
    } catch (err) {
        res.status(500).json({ error: "Backend error", details: err.message });
    } finally {
        // clean up temp file
        fs.unlink(req.file.path, () => {});
    }
});

// job CRUD proxies
app.get("/jobs", async (req, res) => {
    try {
        const response = await axios.get("http://127.0.0.1:8000/jobs/");
        res.json(response.data);
    } catch (err) {
        res.status(500).json({ error: "Failed to fetch jobs" });
    }
});

app.post("/jobs", async (req, res) => {
    try {
        const response = await axios.post("http://127.0.0.1:8000/jobs/", req.body);
        res.json(response.data);
    } catch (err) {
        res.status(500).json({ error: "Failed to create job" });
    }
});

app.listen(3000, () => {
    console.log("Frontend running on http://localhost:3000");
});