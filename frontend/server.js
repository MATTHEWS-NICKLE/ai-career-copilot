const express = require("express");
const axios = require("axios");
const cors = require("cors");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.post("/analyze", async (req, res) => {
    try {
        const response = await axios.post(
            "http://127.0.0.1:8000/match_jobs",
            {
                resume_text: req.body.resume_text
            }
        );

        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Backend error" });
    }
});

app.listen(3000, () => {
    console.log("Frontend running on http://localhost:3000");
});