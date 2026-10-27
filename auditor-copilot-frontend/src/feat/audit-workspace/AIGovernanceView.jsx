import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Cpu, ShieldAlert, Play } from "lucide-react";
import { api } from "../../services/api";

const SAMPLE_AI_SYSTEMS = [
  {
    name: "AuditReady Copilot",
    system_owner: "Lead Internal Auditor",
    business_purpose: "Assisting internal auditors in P2P exception triage and workpaper generation.",
    model_provider: "Google Gemini (gemini-2.5-flash)",
    risk_tier: "Limited Risk",
    approval_records: "Approved by AI Governance Committee & CISO (2026-01-20)",
    monitoring_plan: "Continuous deterministic validation against Neon PostgreSQL truth data.",
  },
  {
    name: "Sales Outreach Bot (Shadow AI)",
    system_owner: null, // Missing
    business_purpose: "Automated prospect email generation",
    model_provider: "External Public API",
    risk_tier: null, // Missing
    approval_records: null, // Missing
    monitoring_plan: null, // Missing
  },
];

export default function AIGovernanceView() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  const handleRunReview = async () => {
    setRunning(true);
    try {
      const res = await api.runAiGovernance({
        ai_systems: SAMPLE_AI_SYSTEMS,
      });
      setResult(res);
    } catch (err) {
      alert(`AI Governance review failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">AI Governance & Shadow AI Audit</h2>
          <p className="text-sm text-muted-foreground">
            Audit enterprise AI system inventory, data processing agreements, and compliance with NIST AI RMF & EU AI Act.
          </p>
        </div>
        <Button size="sm" onClick={handleRunReview} disabled={running}>
          <Play className="w-4 h-4 mr-2" />
          {running ? "Evaluating AI Inventory..." : "Run AI Governance Audit"}
        </Button>
      </div>

      {result && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-500" />
              AI Governance Gaps Identified ({result.exception_count} Findings)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              {result.exceptions?.map((e, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-background border border-border/60 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground">{e.title}</span>
                    <Badge variant="destructive" className="text-[10px] uppercase">
                      {e.severity}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground mt-1">{e.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Systems Inventory Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold">Enterprise AI Model & Application Inventory</CardTitle>
          <p className="text-xs text-muted-foreground">
            Documented AI assets, algorithms, and compliance certifications.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {SAMPLE_AI_SYSTEMS.map((sys, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg border border-border/60 hover:border-primary/40 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-primary" />
                    <h4 className="text-sm font-semibold">{sys.name}</h4>
                  </div>
                  {sys.system_owner ? (
                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30 text-xs">
                      Governance Compliant
                    </Badge>
                  ) : (
                    <Badge variant="destructive" className="text-xs">
                      Shadow AI / Gap Flagged
                    </Badge>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 text-xs">
                  <div>
                    <span className="font-semibold text-muted-foreground">System Owner: </span>
                    <span className={sys.system_owner ? "text-foreground font-medium" : "text-destructive font-medium"}>
                      {sys.system_owner || "Missing (Not Documented)"}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-muted-foreground">Model Provider: </span>
                    <span className="text-foreground">{sys.model_provider || "Unknown"}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-muted-foreground">Risk Classification: </span>
                    <span className={sys.risk_tier ? "text-foreground" : "text-destructive"}>
                      {sys.risk_tier || "Unassessed"}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-muted-foreground">Governance Approval: </span>
                    <span className={sys.approval_records ? "text-foreground" : "text-destructive"}>
                      {sys.approval_records || "No approval on file"}
                    </span>
                  </div>
                </div>

                <div className="mt-2 text-xs">
                  <span className="font-semibold text-muted-foreground">Business Purpose: </span>
                  <span className="text-muted-foreground">{sys.business_purpose}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

