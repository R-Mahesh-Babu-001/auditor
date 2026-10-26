import { useState, useCallback } from "react";
import { ReactFlowData } from "./useSopFlowchartGenerator";

const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

export const useSopFlowchartApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateFlowchartFromSop = useCallback(
    async (sopText: string): Promise<ReactFlowData | null> => {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_BASE_URL}/api/sop/flowchart`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            sop_text: sopText,
          }),
        });

        if (!res.ok) {
          const errText = await res.text();
          throw new Error(errText || "Failed to generate flowchart");
        }

        const json = await res.json();
        const flowdata = JSON.parse(json.data.reactflow);
        console.log("SOP flowchart API response:", flowdata);

        return flowdata;
      } catch (err: any) {
        console.error("SOP flowchart API error:", err);
        setError(err.message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    generateFlowchartFromSop,
    loading,
    error,
  };
};
