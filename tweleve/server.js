const express = require("express");
const os = require("os");

const app = express();
const PORT = process.env.PORT || 3000;
const registrations = [];

app.use(express.json());
app.use(express.static("public"));

// Health check - used by Docker and Kubernetes
app.get("/health", (req, res) => {
  res.json({ status: "UP", host: os.hostname() });
});

// List all registrations
app.get("/api/registrations", (req, res) => {
  res.json(registrations);
});

// Register a participant
app.post("/api/register", (req, res) => {
  const { name, email, phone, college, event } = req.body;
  if (!name || !email || !phone || !college || !event) {
    return res.status(400).json({ error: "All fields are required." });
  }
  if (registrations.some(r => r.email === email)) {
    return res.status(409).json({ error: "This email is already registered." });
  }
  const entry = { id: registrations.length + 1, name, email, college, event };
  registrations.push(entry);
  res.status(201).json({
    message: `Thank you ${name}! You are registered for ${event}.`,
    id: entry.id,
    servedBy: os.hostname()
  });
});

app.listen(PORT, () => {
  console.log(`Event Registration App running on port ${PORT}`);
});