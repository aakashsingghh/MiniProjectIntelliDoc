import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import multer from "multer";
import fs from "fs";
import { createWorker } from "tesseract.js";
import Database from "better-sqlite3";

async function startServer() {
  const app = express();
  const PORT = 3000;

  // Database setup
  const db = new Database("docDB.db");
  db.exec(`
    CREATE TABLE IF NOT EXISTS docTable (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT,
      extracted_text TEXT,
      summary TEXT,
      keywords TEXT,
      upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Ensure uploads directory exists
  const uploadDir = path.join(process.cwd(), "uploads");
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
  }

  // Multer config
  const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, "uploads/"),
    filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname),
  });
  const upload = multer({ storage });

  app.use(express.json());

  // API Routes
  app.post("/api/upload", upload.single("file"), async (req: any, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }

      const filePath = req.file.path;
      const lang = req.body.language || "eng";

      // OCR Processing
      const worker = await createWorker(lang);
      const { data: { text } } = await worker.recognize(filePath);
      await worker.terminate();

      // Return text for NLP processing on client or server
      res.json({
        filename: req.file.filename,
        extracted_text: text,
      });
    } catch (error) {
      console.error("OCR Error:", error);
      res.status(500).json({ error: "Failed to process document" });
    }
  });

  app.post("/api/save", (req, res) => {
    const { filename, extracted_text, summary, keywords } = req.body;
    try {
      const stmt = db.prepare(
        "INSERT INTO docTable (filename, extracted_text, summary, keywords) VALUES (?, ?, ?, ?)"
      );
      const info = stmt.run(filename, extracted_text, summary, keywords);
      res.json({ id: info.lastInsertRowid });
    } catch (error) {
      console.error("DB Save Error:", error);
      res.status(500).json({ error: "Failed to save to database" });
    }
  });

  app.get("/api/documents", (req, res) => {
    const { search } = req.query;
    try {
      let docs;
      if (search) {
        const stmt = db.prepare(
          "SELECT * FROM docTable WHERE filename LIKE ? OR extracted_text LIKE ? OR keywords LIKE ? ORDER BY upload_date DESC"
        );
        const query = `%${search}%`;
        docs = stmt.all(query, query, query);
      } else {
        docs = db.prepare("SELECT * FROM docTable ORDER BY upload_date DESC").all();
      }
      res.json(docs);
    } catch (error) {
      console.error("DB Fetch Error:", error);
      res.status(500).json({ error: "Failed to fetch documents" });
    }
  });

  app.delete("/api/documents/:id", (req, res) => {
    try {
      const stmt = db.prepare("DELETE FROM docTable WHERE id = ?");
      stmt.run(req.params.id);
      res.json({ success: true });
    } catch (error) {
      console.error("DB Delete Error:", error);
      res.status(500).json({ error: "Failed to delete document" });
    }
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
