import axios from "axios";
import * as XLSX from "xlsx";
import Papa from "papaparse";
import mammoth from "mammoth";
import * as pdfjsLib from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.mjs?url";
import secureLocalStorage from "react-secure-storage";

// Configure the PDF.js worker.
if (pdfjsLib && pdfjsLib.GlobalWorkerOptions) {
  pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;
}

// Configure these in the frontend .env file.
// Never put database credentials directly in frontend code.
const baseUrl = (
  import.meta.env.VITE_AI_PLAYGROUND_BASE_URL || ""
).replace(/\/+$/, "");

const API_KEY = import.meta.env.VITE_AI_PLAYGROUND_API_KEY || "";

export const AI_PLAYGROUND_WORKFLOWS = {
  EMBEDDING: {
    flowId: "c7f48ee6-fab9-4119-9670-0bb145da124e",
  },
  AGENT: {
    flowId: "b749c4bc-16f3-4749-a0fc-0395be267150",
  },
};

const requireBaseUrl = () => {
  if (!baseUrl) {
    throw new Error(
      "Missing VITE_AI_PLAYGROUND_BASE_URL. " +
        "Configure it in the frontend .env file and restart Vite."
    );
  }
};

const getAuthHeaders = () => {
  return API_KEY ? { "x-api-key": API_KEY } : {};
};

export const uploadFileAPI = async (file) => {
  try {
    requireBaseUrl();

    if (!file || !file.name) {
      throw new Error("No file was provided for upload.");
    }

    const flow = AI_PLAYGROUND_WORKFLOWS.AGENT;

    if (!flow?.flowId) {
      throw new Error(
        "The AI Playground AGENT workflow is not configured."
      );
    }

    const formData = new FormData();
    formData.append("file", file);

    const fileType = file.name.split(".").pop()?.toLowerCase();
    let fileContent = "";

    // Extract file content for local history.
    if (fileType === "txt") {
      fileContent = await file.text();
    } else if (fileType === "csv") {
      const text = await file.text();
      const parsed = Papa.parse(text, { header: true });
      fileContent = JSON.stringify(parsed.data);
    } else if (fileType === "xlsx" || fileType === "xls") {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const allSheets = {};

      workbook.SheetNames.forEach((sheetName) => {
        allSheets[sheetName] = XLSX.utils.sheet_to_json(
          workbook.Sheets[sheetName],
          { header: 1 }
        );
      });

      fileContent = JSON.stringify(allSheets);
    } else if (fileType === "docx" || fileType === "doc") {
      const arrayBuffer = await file.arrayBuffer();
      const { value } = await mammoth.extractRawText({
        arrayBuffer,
      });

      fileContent = value;
    } else if (fileType === "pdf") {
      const arrayBuffer = await file.arrayBuffer();

      const pdf = await pdfjsLib.getDocument({
        data: arrayBuffer,
      }).promise;

      const pages = [];

      for (
        let pageNumber = 1;
        pageNumber <= pdf.numPages;
        pageNumber += 1
      ) {
        const page = await pdf.getPage(pageNumber);
        const text = await page.getTextContent();

        pages.push(
          text.items.map((item) => item.str).join(" ")
        );
      }

      fileContent = pages.join("\n");
    } else {
      throw new Error(
        `Unsupported file type: ${fileType || "unknown"}`
      );
    }

    // Store extracted content locally.
    const storageKey = `FILE-DIRECTORY-${file.name}`;

    secureLocalStorage.setItem(storageKey, fileContent);

    // Update the list of stored file keys.
    const storedKeys =
      secureLocalStorage.getItem("FILE-DIRECTORY-KEYS");

    const keys = Array.isArray(storedKeys) ? storedKeys : [];

    if (!keys.includes(storageKey)) {
      keys.push(storageKey);

      secureLocalStorage.setItem(
        "FILE-DIRECTORY-KEYS",
        keys
      );
    }

    // Upload the file to the configured AI Playground endpoint.
    // Axios sets the multipart boundary automatically.
    const response = await axios.post(
      `${baseUrl}/api/v1/files/upload/${flow.flowId}`,
      formData,
      {
        headers: getAuthHeaders(),
      }
    );

    const filePath = response.data?.file_path;

    if (!filePath) {
      throw new Error(
        "The upload endpoint did not return file_path. " +
          "Check the API response and endpoint configuration."
      );
    }

    // Send the uploaded file for embedding.
    const embeddingResult = await fileIngestionAPI(filePath);

    console.log("Embedding response:", embeddingResult);

    return response.data;
  } catch (error) {
    console.error("File upload error:", error);
    throw error;
  }
};

export const fileIngestionAPI = async (filePath) => {
  try {
    requireBaseUrl();

    const flow = AI_PLAYGROUND_WORKFLOWS.EMBEDDING;

    if (!flow?.flowId) {
      throw new Error(
        "The AI Playground EMBEDDING workflow is not configured."
      );
    }

    if (!filePath) {
      throw new Error(
        "A server-side file path is required for embedding."
      );
    }

    await axios.post(
      `${baseUrl}/api/v1/run/${flow.flowId}?stream=false`,
      {
        output_type: "text",
        input_type: "text",
        tweaks: {
          "File-STjml": {
            concurrency_multithreading: 4,
            delete_server_file_after_processing: true,
            ignore_unspecified_files: false,
            ignore_unsupported_extensions: true,
            path: filePath,
            silent_errors: false,
            use_multithreading: false,
          },

          // Database credentials must remain on the backend.
          // Do not add hardcoded AstraDB tokens here.
        },
      },
      {
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
      }
    );

    return (
      `Embedding created successfully for file: ${filePath}`
    );
  } catch (error) {
    console.error("File ingestion error:", error);
    throw error;
  }
};