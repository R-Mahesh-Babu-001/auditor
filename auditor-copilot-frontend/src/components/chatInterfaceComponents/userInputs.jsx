import { cn } from "../../lib/utils"
import React, { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Send, Paperclip, XCircle, Loader2 } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../srccomponents/ui/select";
import FileUploadDialog from "./FileUploadDialog";

const UserInputs = ({showSuggestions, promptInputValue, message: messages, setMessages, action }) => {
  const [inputValue, setInputValue] = useState(promptInputValue || "")
  const [files, setFiles] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [isWaitingForStream, setIsWaitingForStream] = useState(false)
  
  const [complianceMode, setComplianceMode] = useState("IT");

  const model = localStorage.getItem("model") || "gemini-3.8-flash";
  const provider = localStorage.getItem("provider") || "gemini gcp";

  // Ensure a persistent user id for memory scoping
  const getUserId = () => {
    // Default fixed id for now (will be extended later)
    const fixedId = "demo_user"
    try {
      localStorage.setItem("auditor_user_id", fixedId)
    } catch (e) {
      // ignore storage errors
    }
    return fixedId
  }

  useEffect(() => {
    if (promptInputValue) {
      setInputValue(promptInputValue)
    }},[promptInputValue])

  // Listen for prompt library selections
  useEffect(() => {
    const handlePromptInput = (event) => {
      const { prompt } = event.detail;
      setInputValue(prompt);
      // Focus the textarea after setting input
      setTimeout(() => {
        const textarea = document.querySelector('textarea[placeholder*="Type your message"]');
        if (textarea) textarea.focus();
      }, 0);
    };

    window.addEventListener('promptLibraryInput', handlePromptInput);
    return () => window.removeEventListener('promptLibraryInput', handlePromptInput);
  }, []);

  const handleSubmit = async () => {
    if (!inputValue.trim() || isStreaming || isWaitingForStream) return

    // Start loading state
    setIsWaitingForStream(true)
    setIsStreaming(true)

    // 1️⃣ Add user message
    const userMessage = { 
      role: "user", 
      content: inputValue,
      attachments: files.map(file => ({ name: file.name, type: file.type, size: file.size })) 
    }
    setMessages((prev) => [...prev, userMessage])

    // 2️⃣ Create placeholder assistant message with loading indicator
    const assistantMessage = { role: "assistant", content: "", isLoading: true, model, provider }
    setMessages((prev) => [...prev, assistantMessage])

    // Clear input immediately
    const currentQuery = inputValue
    setInputValue("")
    setFiles([])

    try {
      const userId = getUserId()

      // If files were attached, ingest them into temporary chat memory first
      if (files.length > 0) {
        await ingestFilesForUser(userId)
        // After ingest, clear attached files from UI
        setFiles([])
      }

      // Determine endpoint and payload based on action
      let endpoint = "/api/chat/stream";
      let payload = {};

      // Normalize provider for backend
      let backendProvider = provider;
      if (provider === "gemini gcp" || provider === "gemini") {
        backendProvider = "gemini_gcp";
      } else if (provider === "azure openai") {
        backendProvider = "azure_openai";
      } else if (provider === "awsbedrock") {
        backendProvider = "aws_bedrock";
      }

      const llmConfig = {
        provider: backendProvider,
        model_name: model,
        temperature: 0.2
      };

      if (action === "execute-analysis-scenario") {
        endpoint = "/api/analysis/stream";
        payload = {
          scenario: currentQuery,
          llm_config: llmConfig,
          user_id: userId
        };
      } else if (action === "document-intelligence") {
        endpoint = "/api/documents/query/stream";
        payload = {
          question: currentQuery,
          llm_config: llmConfig,
          user_id: userId
        };
      } else if (action === "compliance-check") {
        endpoint = "/api/compliance/stream";
        payload = {
          query: currentQuery,
          llm_config: llmConfig,
          user_id: userId,
          mode: complianceMode
        };
      } else {
        // Default to chat
        endpoint = "/api/chat/stream";
        payload = {
          query: currentQuery,
          user_id: userId,
          llm_config: llmConfig
        };
      }

      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_BASE_URL}${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        }
      )

      if (!response.ok || !response.body) {
        throw new Error("Streaming failed")
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      let done = false
      let firstChunkReceived = false

      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading

        const chunk = decoder.decode(value || new Uint8Array())

        if (chunk) {
          // Remove "data: " prefix from each chunk
          const cleanedChunk = chunk.replace(/^data:\s*/gm, '')

          if (cleanedChunk) {
            // First chunk received - remove loading indicator
            if (!firstChunkReceived) {
              firstChunkReceived = true
              setIsWaitingForStream(false)
            }

            setMessages((prev) => {
              const updated = [...prev]
              const lastIndex = updated.length - 1
              updated[lastIndex] = {
                ...updated[lastIndex],
                content: updated[lastIndex].content + cleanedChunk,
                isLoading: false
              }
              return updated
            })
          }
        }
      }
    } catch (error) {
      console.error("Chat stream error:", error)
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: "⚠️ Sorry, something went wrong while streaming the response.",
          isLoading: false
        }
      ])
      setIsWaitingForStream(false)
    }

    setIsStreaming(false)
  }

  /* ---------- File Handling ---------- */

  const handleModalUpload = (newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
  };

  // Ingest files into backend temporary chat memory before sending the message
  const ingestFilesForUser = async (userId) => {
    if (!files || files.length === 0) return

    const form = new FormData()
    files.forEach((f) => form.append("files", f))

    let endpoint = `/api/chat/ingest?user_id=${userId}`;
    
    if (action === "execute-analysis-scenario") {
      endpoint = `/api/analysis/ingest?user_id=${userId}`;
    } else if (action === "document-intelligence") {
      endpoint = `/api/documents/ingest`;
    }

    const resp = await fetch(`${import.meta.env.VITE_BACKEND_BASE_URL}${endpoint}`, {
      method: "POST",
      body: form
    })

    if (!resp.ok) {
      console.warn("File ingest failed", await resp.text())
    }
  }


  const handleFileChange = (e) => {
    if (isStreaming || isWaitingForStream) return
    
    const selectedFiles = Array.from(e.target.files)
    if (files.length + selectedFiles.length <= 10) {
      setFiles((prev) => [...prev, ...selectedFiles])
    } else {
      alert("You can upload a maximum of 10 files.")
    }
  }

  const handleRemoveFile = (index) => {
    if (isStreaming || isWaitingForStream) return
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const isDisabled = isStreaming || isWaitingForStream

  return (
    <div className="relative">
      {/* Overlay for disabled state */}
      {isDisabled && (
        <div className="absolute inset-0 bg-white/50 backdrop-blur-[2px] z-10 rounded-lg transition-opacity duration-200" />
      )}

      {/* File Preview */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-1">
          {files.map((file, index) => (
            <div
              key={index}
              className={cn(
                "flex items-center space-x-1 bg-gray-100 px-2 py-1 rounded-lg text-sm transition-opacity",
                isDisabled && "opacity-50"
              )}
            >
              <span className="truncate">{file.name}</span>
              <button 
                onClick={() => handleRemoveFile(index)}
                disabled={isDisabled}
                className="disabled:cursor-not-allowed"
              >
                <XCircle className="h-4 w-4 text-red-500" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex items-center space-x-3 border p-2 rounded-lg shadow-md transition-all duration-200">
        <FileUploadDialog
          trigger={<Paperclip className="h-5 w-5 text-gray-500 hover:text-gray-700 cursor-pointer" />}
          onFilesUploaded={handleModalUpload}
        />

        {action === "compliance-check" && (
          <div className="flex items-center">
            <Select value={complianceMode} onValueChange={setComplianceMode}>
              <SelectTrigger className="w-[140px] h-9 text-xs border-0 bg-gray-100 focus:ring-0 focus:ring-offset-0">
                <SelectValue placeholder="Mode" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="IT">IT Policy Compliance</SelectItem>
                <SelectItem value="FINANCE">Accounting Policy Compliance</SelectItem>
                <SelectItem disabled value="SALES">Sales Policy Compliance</SelectItem>
                <SelectItem disabled value="JUSTIFICATION">Justification Notes Compliance</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        <textarea
          placeholder={
            isWaitingForStream 
              ? "Waiting for response..." 
              : isStreaming 
              ? "Receiving response..." 
              : "Type your message here..."
          }
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !isDisabled) {
              e.preventDefault()
              handleSubmit()
            }
          }}
          className={cn(
            "flex-1 h-20 resize-none rounded-md border p-2 transition-all duration-200",
            isDisabled && "text-gray-400 cursor-not-allowed bg-gray-50"
          )}
          disabled={isDisabled}
        />

        <Button
          onClick={handleSubmit}
          disabled={isDisabled || !inputValue.trim()}
          className="bg-black hover:bg-gray-800 transition-all duration-200"
        >
          {isWaitingForStream ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : isStreaming ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  )
}

export default UserInputs