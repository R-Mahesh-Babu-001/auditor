import axios from "axios";
import * as XLSX from "xlsx";
import Papa from "papaparse";
import mammoth from "mammoth";
import * as PDFJS from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker?url";
import secureLocalStorage from "react-secure-storage";

// Set PDF worker
// Tell pdf.js where to find the worker
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

// const baseUrl = 'https://langflow-v3-large.salmonisland-47da943e.centralindia.azurecontainerapps.io'
const baseUrl = import.meta.env.VITE_AI_PLAYGROUND_BASE_URL;
// https://langflow-v3-large.salmonisland-47da943e.centralindia.azurecontainerapps.io/api/v1/run/adda70b1-e24a-4610-926a-ca8b80ed8a02?stream=false
// const flowId = '91a3d1f1-fa91-4aff-a334-140860535fae'

const API_KEY = import.meta.env.VITE_AI_PLAYGROUND_API_KEY;

// export const AI_PLAYGROUND_WORKFLOWS = {
//     RAG: {flowId:'e322521c-1cd2-4126-a002-24458d3c6eaf'},
//     INVOICING: {flowId:'1ce871a4-e87b-4e82-beb8-b4ca7791baf6', fileComponentId:'File-EKjxA'},
//     RECONCILING : {flowId: 'f33346c4-5166-4341-83e9-3380fb00f07c',poComponent:'File-hGR2q', invoiceComponent:'File-pZRDa'}

// }

export const AI_PLAYGROUND_WORKFLOWS = {
  // AGENT : {flowId:'982dce00-8135-42f0-bec1-4d898b09cf66'},
  // EMBEDDING: { flowId: "d90bc62f-1446-45af-b057-952065d6687f" }, // OLD
  EMBEDDING: { flowId: "c7f48ee6-fab9-4119-9670-0bb145da124e" },
  AGENT: { flowId: "b749c4bc-16f3-4749-a0fc-0395be267150" },
};

// const WORKFLOWS = {
//     RAG: {flowId:'9e96ec5d-b3bc-4497-9006-97421cd8d7d9'},
//     INVOICING: {flowId:'70fc313b-4f6d-4e9b-b51e-ec803d845bb1', fileComponentId:'File-zeINU'},
//     RECONCILING: {flowId: 'adda70b1-e24a-4610-926a-ca8b80ed8a02', poComponent:'File-eclaI', invoiceComponent:'File-oqmWy'}
// }

export const uploadFileAPI = async (file) => {
  try {
    // Get the flowId based on the flag
    const flow = AI_PLAYGROUND_WORKFLOWS["AGENT"];
    if (!flow) {
      throw new Error("Invalid flag provided");
    }

    const flowId = flow.flowId;
    // console.log('uploading file to: ',flowId);

    // dispatch({type: UPLOAD_FILE_REQUEST});

    console.log("uploading file api called");
    const formData = new FormData();
    formData.append("file", file);

    // Detect file type
    const fileType = file.name.split(".").pop().toLowerCase();

    let fileContent = "";

    // Read file content based on type
    if (fileType === "txt") {
      fileContent = await file.text();
      // console.log("TXT Content:", text);
    } else if (fileType === "csv") {
      const text = await file.text();
      const parsed = Papa.parse(text, { header: true });
      fileContent = JSON.stringify(parsed.data);
      // console.log("CSV Content:", parsed.data);
    } else if (fileType === "xlsx") {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const allSheets = {};
      workbook.SheetNames.forEach((sheetName) => {
        allSheets[sheetName] = XLSX.utils.sheet_to_json(
          workbook.Sheets[sheetName],
          { header: 1 }
        );
        // console.log(`XLSX Sheet "${sheetName}":`, sheet);
      });
      fileContent = JSON.stringify(allSheets);
    } else if (fileType === "docx" || fileType === "doc") {
      const arrayBuffer = await file.arrayBuffer();
      const { value } = await mammoth.extractRawText({ arrayBuffer });
      fileContent = value;
      // console.log("DOCX/DOC Content:", value);
    } else if (fileType === "pdf") {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let textContent = "";
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const text = await page.getTextContent();
        textContent += text.items.map((item) => item.str).join(" ") + "\n";
      }
      fileContent = textContent;
      // console.log("PDF Content:", textContent);
    } else {
      console.warn("Unsupported file type:", fileType);
    }

    // Save file content securely
    secureLocalStorage.setItem(`FILE-DIRECTORY-${file.name}`, fileContent);

    // Update the list of stored file keys
    let keys = secureLocalStorage.getItem("FILE-DIRECTORY-KEYS") || [];
    if (!keys.includes(`FILE-DIRECTORY-${file.name}`)) {
      keys.push(`FILE-DIRECTORY-${file.name}`);
      secureLocalStorage.setItem("FILE-DIRECTORY-KEYS", keys);
    }
    // //Logic to upload file
    // const response = await axios.post(
    //   `${baseUrl}/api/v1/files/upload/${flowId}`,
    //   formData,
    //   {
    //     // const response = await axios.post("https://aiplayground.salmonisland-47da943e.centralindia.azurecontainerapps.io/api/v1/files/upload/1ce871a4-e87b-4e9b-b51e-ec803d845bb1", formData, {
    //     headers: {
    //       "Content-Type": "multipart/form-data",
    //       "x-api-key": `${API_KEY}`,
    //     },
    //     // responseType: 'json'
    //   }
    // );

    const embeddingResponse = await fileIngestionAPI(response.data.file_path);
    console.log("Embedding response: ", embeddingResponse);
    return response.data;

    // console.log('file uploaded: ', response.data);
    // dispatch({type: UPLOAD_FILE_SUCCESS, payload: response.data});
  } catch (error) {
    console.log("Error:", error);
    return error;
    // dispatch({
    //     type: UPLOAD_FILE_FAIL,
    //     payload: error.response?.data?.message || error.message,
    // });
  }
};

export const fileIngestionAPI = async (filePath) => {
  try {
    const flow = AI_PLAYGROUND_WORKFLOWS["EMBEDDING"];
    if (!flow) {
      throw new Error("Invalid flag provided");
    }

    const flowId = flow.flowId;

    const response = await axios.post(
      `${baseUrl}/api/v1/run/${flowId}?stream=false`,
      {
        output_type: "text",
        input_type: "text",
        tweaks: {
          "File-STjml": {
            concurrency_multithreading: 4,
            delete_server_file_after_processing: true,
            ignore_unspecified_files: false,
            ignore_unsupported_extensions: true,
            path: `${filePath}`,
            silent_errors: false,
            use_multithreading: false,
          },
          //   batch_size: null,
          //   bulk_delete_concurrency: null,
          //   bulk_insert_batch_concurrency: null,
          //   bulk_insert_overwrite_concurrency: null,
          //   collection_indexing_policy: "",
          //   collection_name: "graph_rag",
          //   keyspace: "",
          //   metadata_incoming_links_key: "",
          //   metadata_indexing_exclude: "",
          //   metadata_indexing_include: "",
          //   metric: "cosine",
          //   number_of_results: 4,
          //   pre_delete_collection: false,
          //   search_filter: {},
          //   search_query: "",
          //   search_score_threshold: 0,
          //   search_type: "MMR (Max Marginal Relevance) Graph Traversal",
          //   setup_mode: "Sync",
          //   should_cache_vector_store: true,
          //   token: [REMOVED — use a server-side secret, never commit the token],
          // },
          // "Chroma-H2OEq": {
          //   allow_duplicates: false,
          //   chroma_server_cors_allow_origins: "",
          //   chroma_server_grpc_port: null,
          //   chroma_server_host: "",
          //   chroma_server_http_port: null,
          //   chroma_server_ssl_enabled: false,
          //   collection_name: "auditor-rag-session",
          //   limit: null,
          //   number_of_results: 10,
          //   persist_directory: "auditor-copilot",
          //   search_query: "",
          //   search_type: "Similarity",
          //   should_cache_vector_store: true,
          // },
        },
      },
      {
        headers: {
          "Content-Type": "application/json",
          "x-api-key": `${API_KEY}`,
        },
      }
    );

    return `Embedding created successfully for file: ${filePath}`;
  } catch (error) {
    console.log("Error:", error);
    return error;
  }
};
