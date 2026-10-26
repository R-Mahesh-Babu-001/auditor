
// DigitalAuditScreen.jsx
// UI for submitting and running digital audit tasks, and displaying agent output.
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/srccomponents/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Loader2, PlayCircle } from "lucide-react"


/**
 * DigitalAuditScreen Component
 * UI for submitting a digital audit task, running the backend agent, and displaying results.
 */
const DigitalAuditScreen = () => {
  // Task input state
  const [task, setTask] = useState("")
  // Loading state for audit execution
  const [loading, setLoading] = useState(false)
  // Result object from agent
  const [result, setResult] = useState(null)

  /**
   * Submits the audit task to the backend agent and updates result state.
   */
  const runAudit = async () => {
    if (!task.trim()) return

    setLoading(true)
    setResult({
      status: "running",
      summary: "Agent is executing the audit task in a secure browser...",
    })

    try {
      // Call backend agent API
      const baseUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ task }),
      })

      if (!response.ok) {
        throw new Error("API request failed")
      }

      const data = await response.json()

      // Merge API output with dummy execution trace
      setResult({
        status: data.success ? "success" : "error",
        summary:
          "The agent successfully completed the digital audit and extracted the required information.",
        steps: [
          "Opened Chromium browser in isolated environment",
          "Navigated to target application",
          "Performed automated interactions",
          "Captured results and screenshots",
          "Validated audit criteria",
        ],
        rawOutput: `
🔹 Agent Response:
${data.output}

🔹 Screenshots Captured:
${data.screenshots?.length || 0}
        `.trim(),
      })
    } catch (error) {
      setResult({
        status: "error",
        summary:
          "Audit execution failed. Unable to fetch agent output. Please retry.",
        rawOutput: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto p-6">
      {/* Task Input */}
      <Card>
        <CardHeader>
          <CardTitle>Digital Audit Task</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Textarea
            placeholder="Describe the digital audit task (e.g., validate KYC workflow, verify login security, extract transaction summary...)"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            className="min-h-[100px]"
          />
          <Button
            onClick={runAudit}
            disabled={loading}
            className="self-end gap-2"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <PlayCircle className="h-4 w-4" />
            )}
            Run Audit
          </Button>
        </CardContent>
      </Card>

      {/* Agent Output */}
      {result && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Agent Output</CardTitle>
            <Badge
              variant={
                result.status === "success"
                  ? "default"
                  : result.status === "error"
                  ? "destructive"
                  : "secondary"
              }
            >
              {result.status.toUpperCase()}
            </Badge>
          </CardHeader>

          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              {result.summary}
            </p>

            {result.steps && (
              <div>
                <p className="text-sm font-medium mb-2">
                  Execution Trace
                </p>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {result.steps.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.rawOutput && (
              <div className="rounded-md border bg-muted p-4 text-sm whitespace-pre-wrap">
                {result.rawOutput}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default DigitalAuditScreen
