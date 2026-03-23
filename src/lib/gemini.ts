import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export async function processDocumentText(text: string) {
  if (!text.trim()) return { summary: "No text provided.", keywords: [] };

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.0-flash-exp",
      contents: [
        {
          parts: [
            {
              text: `Analyze the following extracted text from a document. 
              1. Provide a concise summary (2-3 sentences).
              2. Extract 5-8 relevant keywords.
              3. Clean the text by removing noise, artifacts, and fixing obvious OCR errors.
              
              Respond in JSON format:
              {
                "summary": "...",
                "keywords": ["...", "..."],
                "cleaned_text": "..."
              }
              
              Text:
              ${text.substring(0, 10000)}` // Limit text size for prompt
            }
          ]
        }
      ],
      config: {
        responseMimeType: "application/json"
      }
    });

    const result = JSON.parse(response.text || "{}");
    return result;
  } catch (error) {
    console.error("Gemini NLP Error:", error);
    return {
      summary: "Failed to generate summary.",
      keywords: [],
      cleaned_text: text
    };
  }
}
