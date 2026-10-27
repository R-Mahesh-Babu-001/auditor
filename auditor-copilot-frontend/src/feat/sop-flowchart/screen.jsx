
// SopFlowChartScreen.jsx
// UI for uploading a file and generating a SOP flowchart using ReactFlow.
import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, Loader2, X } from "lucide-react";
import SopFlowChartShowcaseScreen from "./flowchart_showcase";
import { medium_complexity_sop_data as dummy1 } from "./dummy_data/medium_sop";
import { easy_complexity_sop_data as dummy2 } from "./dummy_data/easy_sop";
import { high_complexity_sop_data as dummy3 } from "./dummy_data/complex_sop";
import { useFileExtractor } from "./hooks/use-file-extractor";
import { useSopFlowchartGenerator } from "./hooks/useSopFlowchartGenerator";

const exampleFlowcharts = [
  { label: "Employee Onboarding", data: dummy2 },
  { label: "Product Return Processing", data: dummy1 },
  { label: "Employee Time-Off Request", data: dummy3 },
];

/**
 * SopFlowChartScreen Component
 * UI for uploading a file, extracting SOP data, and generating a flowchart.
 * Also allows previewing example flowcharts.
 */
const SopFlowChartScreen = () => {
  // File selected by the user
  const [selectedFile, setSelectedFile] = useState(null);
  // Error message state
  const [error, setError] = useState("");
  // Flowchart data for rendering
  const [data, setData] = useState(null);
  // Currently active example label
  const [activeExample, setActiveExample] = useState(null);
  // Loading message for progress feedback
  const [loadingMessage, setLoadingMessage] = useState("");

  // Custom hooks for file extraction and flowchart generation
  const { extractData, loading: extracting, error: extractError } = useFileExtractor();
  const { generateFlowchart, flowData, loading: generating, error: generationError } =
    useSopFlowchartGenerator();

  // Update data state when flowData changes
  useEffect(() => {
    if (flowData) {
      setData(flowData);
      setActiveExample(null); // optional UX improvement
    }
  }, [flowData]);

  // Handle file input change
  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setSelectedFile(e.target.files[0]);
      setActiveExample(null);
    }
  };

  // Show sequential loading messages for better UX
  const startSequentialMessages = () => {
    setLoadingMessage("Analyzing the file...");
    setTimeout(() => setLoadingMessage("Understanding the process flow..."), 3000);
    setTimeout(() => setLoadingMessage("Generating the flowchart..."), 6000);
  };


  // Handle flowchart generation from uploaded file
  const handleGenerate = async () => {
    if (!selectedFile) return;
    setActiveExample(null);
    startSequentialMessages();
    try {
      const extracted = await extractData(selectedFile);
      if (!extracted) return;
      await generateFlowchart(extracted);
    } catch (err) {
      console.error(err);
    }
  };


  // Handle clicking an example flowchart
  const handleExampleClick = (exampleData, label) => {
    setData(null);
    setError("");
    setSelectedFile(null);
    setActiveExample(label);
    // force new reference
    setData({...exampleData});
  };

  useEffect(() => {
    if (!activeExample && flowData) {
      setData(flowData);
    }
  }, [flowData, activeExample]);


  return (
    <div className="flex flex-col items-center justify-center w-full h-full p-6 space-y-6">
      {/* Upload Card */}
      <Card className="w-full max-w-2xl shadow-lg border border-gray-200 rounded-2xl">
        <CardHeader>
          <CardTitle className="text-xl font-semibold text-gray-800">
            Upload File to Generate SOP Flowchart
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center gap-4">
            <label
              htmlFor="file-upload"
              className="w-full cursor-pointer border-2 border-dashed border-gray-300 rounded-2xl p-6 flex flex-col items-center justify-center hover:border-primary transition"
            >
              <Upload className="h-8 w-8 text-gray-500 mb-2" />
              <span className="text-gray-600 text-sm">
                {selectedFile ? selectedFile.name : "Click or drag a file to upload"}
              </span>
              <Input
                id="file-upload"
                type="file"
                accept=".pdf,.doc,.docx,.xlsx,.csv,.png,.jpg,.jpeg,.mp3"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>

            <div className="flex gap-2 w-full mt-2">
              <Button onClick={handleGenerate} disabled={extracting || generating} className="flex-1">
                {(extracting || generating) ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {loadingMessage}
                  </>
                ) : (
                  "Generate Flowchart"
                )}
              </Button>

              {(extractError || generationError) && (
                <p className="text-sm text-red-500 mt-2 font-medium">
                  {extractError || generationError}
                </p>
              )}

              {/* {loading && (
                <Button
                  variant="destructive"
                  onClick={handleStopGeneration}
                  className="flex-1"
                >
                  <X className="mr-2 h-4 w-4" />
                  Stop
                </Button>
              )} */}
            </div>

            {error && (
              <p className="text-sm text-red-500 mt-2 font-medium">{error}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Example Flowcharts */}
      <Card className="w-full max-w-2xl shadow-lg border border-gray-200 rounded-2xl">
        {/* <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800">
            Try Example Flowcharts
          </CardTitle>
        </CardHeader> */}
        <CardContent>
          <div className="flex gap-4 flex-wrap">
            {exampleFlowcharts.map((ex, idx) => (
              <Button
                key={idx}
                disabled
                onClick={() => handleExampleClick(ex.data, ex.label)}
                className={`flex-1 min-w-[120px] ${activeExample === ex.label
                    ? "bg-primary text-white hover:bg-primary/90"
                    : ""
                  }`}
              >
                {ex.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Flowchart Rendering */}
      {data && (
        <div className="w-full h-[80vh] border border-gray-200 shadow-md p-1">
          <SopFlowChartShowcaseScreen flow_data={flowData} />
        </div>
      )}
    </div>
  );
};

export default SopFlowChartScreen;
