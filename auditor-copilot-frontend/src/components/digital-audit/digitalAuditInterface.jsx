
// DigitalAuditInterface.jsx
// Step-by-step UI for digital audit tasks on social media accounts/content.
import react, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Loader2, CheckCircle, AlertCircle } from "lucide-react";

/**
 * List of available digital audit tasks.
 */
// List of available digital audit tasks
const tasks = [
  { id: "account-verification", title: "Account Verification Status", description: "Check if an account is verified." },
  { id: "activity-status", title: "Activity Status Verification", description: "Analyze recent activity for legitimacy." },
  { id: "engagement-detector", title: "Concerned Engagement Detector", description: "Detect negative or abusive engagement." },
];
  
/**
 * Supported social media platforms.
 */
// Supported social media platforms
const platforms = ["Facebook", "YouTube", "Instagram", "Twitter"];

/**
 * DigitalAuditInterface Component
 * 
 * Provides a step-by-step interface for performing digital audits on social media accounts or content.
 * It guides the user through task selection, platform selection, inputting details (handle/URL),
 * and viewing the analysis report.
 */

/**
 * DigitalAuditInterface Component
 * Provides a step-by-step interface for performing digital audits on social media accounts or content.
 * Guides the user through task selection, platform selection, inputting details (handle/URL), and viewing the analysis report.
 */
const DigitalAuditInterface = () => {
    // Step state for the multi-step form wizard
    const [step, setStep] = useState(1);
    // Selected audit task
    const [selectedTask, setSelectedTask] = useState(null);
    // Selected social media platform
    const [selectedPlatform, setSelectedPlatform] = useState(null);
    // Selected handle (for account verification)
    const [handle, setHandle] = useState("");
    // Input URL (for other tasks)
    const [url, setUrl] = useState("");
    // Loading state for progress bar
    const [loading, setLoading] = useState(false);
    // Progress value (0-100)
    const [progress, setProgress] = useState(0);
    // Analysis report object
    const [report, setReport] = useState(null);

    // Mock data for handles
    const dummyHandles = ["@brandOfficial", "@user123", "@verified_page", "@random_profile"];

    /**
     * Simulates the analysis processing with a progress bar.
     * When complete, generates a mock report.
     */
    const startProcessing = () => {
        setLoading(true);
        setProgress(0);
        const interval = setInterval(() => {
            setProgress((prev) => {
                if (prev >= 100) {
                    clearInterval(interval);
                    setLoading(false);
                    generateReport();
                    return 100;
                }
                return prev + 10;
            });
        }, 150);
    };

    /**
     * Generates a mock report based on the selected task and input.
     */
    const generateReport = () => {
        setReport({
            status: "Success",
            details: selectedTask === "account-verification"
                ? `${handle} is verified ✅ on ${selectedPlatform}`
                : `URL ${url} analyzed successfully for ${selectedTask}. No major issues detected.`
        });
    };

    /**
     * Resets the interface to the initial state.
     */
    const reset = () => {
        setStep(1);
        setSelectedTask(null);
        setSelectedPlatform(null);
        setHandle("");
        setUrl("");
        setReport(null);
        setProgress(0);
        setLoading(false);
    };

    // Automatically advance to the report step when processing is done
    useEffect(() => {
        if (!loading && report && step === 4) {
            setStep(5);
        }
    }, [loading, report, step]);

  return (
    <div className="max-w-2xl mx-auto space-y-6 py-10">
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Select a Task</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {tasks.map((task) => (
              <Button
                key={task.id}
                variant={selectedTask === task.id ? "default" : "outline"}
                className="w-full justify-start"
                onClick={() => {
                  setSelectedTask(task.id);
                  setStep(2);
                }}
              >
                <div className="flex flex-col items-start">
                  <span className="font-semibold">{task.title}</span>
                  <span className="text-xs text-muted-foreground">{task.description}</span>
                </div>
              </Button>
            ))}
          </CardContent>
        </Card>
      )}

      {step === 2 && selectedTask && (
        <Card>
          <CardHeader>
            <CardTitle>Select a Platform</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {platforms.map((platform) => (
              <Button
                key={platform}
                variant={selectedPlatform === platform ? "default" : "outline"}
                className="w-full justify-start"
                onClick={() => {
                  setSelectedPlatform(platform);
                  setStep(3);
                }}
              >
                {platform}
              </Button>
            ))}
          </CardContent>
        </Card>
      )}

      {step === 3 && selectedPlatform && (
        <Card>
          <CardHeader>
            <CardTitle>{selectedTask === "account-verification" ? "Select a Handle" : "Enter a URL"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedTask === "account-verification" ? (
              dummyHandles.map((hnd) => (
                <Button
                  key={hnd}
                  variant={handle === hnd ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => {
                    setHandle(hnd);
                    setStep(4);
                  }}
                >
                  {hnd}
                </Button>
              ))
            ) : (
              <>
                <Label htmlFor="url">Social Media Post/Content URL</Label>
                <Input
                  id="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/post"
                />
                <Button
                  className="w-full"
                  onClick={() => url && setStep(4)}
                  disabled={!url}
                >
                  Continue
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {step === 4 && (handle || url) && (
        <Card>
          <CardHeader>
            <CardTitle>Processing</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              <>
                <div className="flex items-center justify-center">
                  <Loader2 className="animate-spin h-8 w-8 text-primary" />
                </div>
                <Progress value={progress} className="h-2" />
                <p className="text-center text-sm text-muted-foreground">{progress}% completed</p>
              </>
            ) : (
              <Button className="w-full" onClick={startProcessing}>
                Start Analysis
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {step === 5 && report && (
        <Card>
          <CardHeader>
            <CardTitle>Report</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center space-x-2">
              {report.status === "Success" ? (
                <CheckCircle className="text-green-500 w-6 h-6" />
              ) : (
                <AlertCircle className="text-red-500 w-6 h-6" />
              )}
              <span className="font-medium">{report.status}</span>
            </div>
            <p className="text-sm">{report.details}</p>
          </CardContent>
          <CardFooter className="justify-end">
            <Button variant="outline" onClick={reset}>
              Analyze Another
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Auto-advance to step 5 when loading finishes */}
      {/* {loading === false && (handle || url) && !report && step === 4 && setStep(5)} */}
    </div>
  );
}

export default DigitalAuditInterface
