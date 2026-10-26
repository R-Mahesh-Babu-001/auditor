// src/hooks/useFileExtractor.ts
import { useState, useCallback } from "react";
import * as XLSX from "xlsx";
import * as pdfjsLib from "pdfjs-dist/build/pdf";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker?url";
import { createWorker } from "tesseract.js";
import mammoth from "mammoth";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
export type ExtractedResult = {
  type: string;
  content: string | object;
};

export const useFileExtractor = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const extractData = useCallback(async (file: File): Promise<ExtractedResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const extension = file.name.split(".").pop()?.toLowerCase();
      
      if (!extension) throw new Error("Invalid file type");
      // console.log(`Extracting ${extension} file...`);
      // --- TXT ---
      // if (extension === "txt") {
      //   const text = await file.text();
      //   return { type: "text", content: text };
      // }

      // --- PDF ---
      if (extension === "pdf") {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        let text = "";
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map((item: any) => item.str).join(" ") + "\n";
        }
        return { type: "pdf", content: text };
      }

      // --- WORD (.docx) ---
      // if (["docx", "doc"].includes(extension)) {
      //   const arrayBuffer = await file.arrayBuffer();
      //   const { value } = await mammoth.extractRawText({ arrayBuffer });
      //   return { type: "word", content: value };
      // }

      // --- EXCEL (.xlsx / .xls / .csv) ---
      // if (["xlsx", "xls", "csv"].includes(extension)) {
      //   const data = await file.arrayBuffer();
      //   const workbook = XLSX.read(data, { type: "array" });
      //   const sheetName = workbook.SheetNames[0];
      //   const worksheet = workbook.Sheets[sheetName];
      //   const jsonData = XLSX.utils.sheet_to_json(worksheet);
      //   return { type: "excel", content: jsonData };
      // }

      // --- IMAGE (OCR via tesseract.js) ---
      if (["png", "jpg", "jpeg"].includes(extension)) {
        const worker = await createWorker("eng");
        const { data } = await worker.recognize(file);
        await worker.terminate();
        return { type: "image", content: data.text };
      }

      throw new Error(`Unsupported file type: ${extension}`);
    } catch (err: any) {
      console.error(err);
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { extractData, loading, error };
};
