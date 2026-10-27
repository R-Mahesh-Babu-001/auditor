import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";
import { api } from "../../services/api";

export default function FindingsView() {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadFindings = async () => {
    setLoading(true);
    try {
      const res = await api.getFindings();
      setFindings(res.findings || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFindings();
  }, []);

  const getSeverityBadge = (sev) => {
    switch (sev?.toLowerCase()) {
      case "high":
        return <Badge variant="destructive">High Severity</Badge>;
      case "medium":
        return <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">Medium Severity</Badge>;
      default:
        return <Badge variant="outline">Low Severity</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audit Findings & Reports</h2>
          <p className="text-sm text-muted-foreground">
            Formally raised internal audit findings with 5-element structure (Condition, Criteria, Cause, Effect, Recommendation).
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadFindings} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh Findings
        </Button>
      </div>

      {findings.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12 text-muted-foreground text-sm">
            <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
            No audit findings raised yet. When exceptions are confirmed in triage, they can be formalized into audit findings.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {findings.map((f) => (
            <Card key={f.id} className="border-l-4 border-l-destructive">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-muted-foreground">
                        {f.finding_code}
                      </span>
                      {getSeverityBadge(f.severity)}
                      <Badge variant="outline" className="text-xs capitalize">
                        {f.status}
                      </Badge>
                    </div>
                    <CardTitle className="text-base font-semibold mt-1">{f.title}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 pt-2 text-xs">
                {f.condition && (
                  <div>
                    <span className="font-semibold text-foreground">Condition (What was found): </span>
                    <span className="text-muted-foreground">{f.condition}</span>
                  </div>
                )}
                {f.criteria && (
                  <div>
                    <span className="font-semibold text-foreground">Criteria (Required Standard): </span>
                    <span className="text-muted-foreground">{f.criteria}</span>
                  </div>
                )}
                {f.cause && (
                  <div>
                    <span className="font-semibold text-foreground">Root Cause: </span>
                    <span className="text-muted-foreground">{f.cause}</span>
                  </div>
                )}
                {f.effect && (
                  <div>
                    <span className="font-semibold text-foreground">Financial & Operational Effect: </span>
                    <span className="text-muted-foreground">{f.effect}</span>
                  </div>
                )}
                {f.recommendation && (
                  <div className="p-2.5 rounded bg-muted/40 border border-border/50">
                    <span className="font-semibold text-primary">Auditor Recommendation: </span>
                    <span className="text-foreground">{f.recommendation}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

