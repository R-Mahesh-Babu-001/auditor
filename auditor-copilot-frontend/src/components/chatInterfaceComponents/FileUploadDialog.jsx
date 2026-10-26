import React, { useEffect, useRef, useState } from "react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../../../components/ui/dialog";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { uploadFileAPI } from "../../redux/actions/auditActions";

// import { useDispatch } from "react-redux";

export default function FileUploadDialog({ onFilesUploaded, trigger }) {
  const fileInputRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  //   const dispatch = useDispatch();

  const handleFileDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const VALID_MIME_TYPES = {
    'application/pdf': true,
    'application/msword': true,
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': true,
    'application/vnd.ms-excel': true,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': true,
    'text/csv': true,
    'image/png': true,
    'image/jpeg': true,
    'audio/mpeg': true
  };

  const handleFiles = (files) => {
    const limitedFiles = files.slice(0, 5 - uploadedFiles.length);
    const newFiles = limitedFiles.map((file) => {
      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        return {
          file,
          status: "error",
          errorMessage: "File too large (max 10MB)"
        };
      }

      if (!VALID_MIME_TYPES[file.type]) {
        return {
          file,
          status: "error",
          errorMessage: "Invalid file type"
        };
      }

      return {
        file,
        status: "pending"
      };
    });

    setUploadedFiles((prev) => [...prev, ...newFiles]);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleRemove = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    // Just pass the pending files to the parent component
    const pendingFiles = uploadedFiles.map(item => item.file);
    
    if (pendingFiles.length > 0) {
      onFilesUploaded(pendingFiles);
      setOpen(false); // Close dialog
      setUploadedFiles([]); // Clear local state
    }
  };


  const getStatusText = (status) => {
    switch (status) {
      case "uploading":
        return "Uploading...";
      case "success":
        return "Uploaded ✅";
      case "error":
        return "Failed ❌";
      default:
        return "";
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>

      <DialogContent
        className="sm:max-w-md"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
      >
        <DialogHeader>
          <DialogTitle>Add content to chat</DialogTitle>
        </DialogHeader>

        <div
          className="border-dashed border-2 border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer"
          onClick={() => fileInputRef.current.click()}
        >
          <p>Drag and drop a file here, or click to select</p>
          <p className="text-sm text-gray-500">
            ({uploadedFiles.length}/5 files) — Max file size: 5MB
          </p>
          <input
            ref={fileInputRef}
            type="file"
            hidden
            multiple
            accept=".pdf,.doc,.docx,.xlsx,.csv,.png,.jpg,.jpeg,.mp3"
            onChange={handleFileInput}
          />
        </div>

        {uploadedFiles?.length > 0 && (
          <div className="mt-4 space-y-1 text-sm max-h-32 overflow-y-auto">
            {uploadedFiles?.map((item, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center border rounded px-2 py-1"
              >
                <span className="truncate flex-1">{item.file.name}</span>
                <span className="ml-2 text-xs text-gray-500">{getStatusText(item.status)}</span>
                {item.status !== "uploading" && (
                  <button
                    onClick={() => handleRemove(idx)}
                    className="text-red-500 hover:text-red-700 ml-2"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        <DialogFooter className="mt-4">
          <Button onClick={handleUpload}
            // disabled
          // style={{ cursor: 'not-allowed', opacity: 0.5 }}
          //  disabled={uploadedFiles.length === 0}
          >
            Upload
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
