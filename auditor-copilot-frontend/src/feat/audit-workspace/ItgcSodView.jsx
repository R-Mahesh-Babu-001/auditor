import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShieldAlert, RefreshCw, Play } from "lucide-react";
import { api } from "../../services/api";

const SAMPLE_USERS = [
  {
    user_id: "USR-101",
    email: "john.creator@company.internal",
    roles: ["PO_CREATION", "INVOICE_APPROVAL"],
    is_active: true,
  },
  {
    user_id: "USR-102",
    email: "sarah.finance@company.internal",
    roles: ["VENDOR_MASTER_MAINTAIN", "PAYMENT_RELEASE"],
    is_active: true,
  },
  {
    user_id: "USR-103",
    email: "bob.leaver@company.internal",
    roles: ["PO_CREATION"],
    is_active: true,
  },
  {
    user_id: "USR-104",
    email: "alice.auditor@company.internal",
    roles: ["READ_ONLY_AUDIT"],
    is_active: true,
  },
];

const SAMPLE_LEAVERS = [
  { email: "bob.leaver@company.internal", termination_date: "2026-01-15" },
];

export default function ItgcSodView() {
  const [matrix, setMatrix] = useState([]);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const loadMatrix = async () => {
    setLoading(true);
    try {
      const res = await api.getSodMatrix();
      setMatrix(res.conflict_pairs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMatrix();
  }, []);

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    try {
      const res = await api.runItgcSod({
        user_roles: SAMPLE_USERS,
        leavers: SAMPLE_LEAVERS,
        inactive_days_threshold: 90,
        persist_exceptions: false,
      });
      setAnalysisResult(res);
    } catch (err) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">ITGC & Segregation of Duties (SoD) Review</h2>
          <p className="text-sm text-muted-foreground">
            Audit conflicting user privilege pairs, terminated leavers with retained access, and dormant accounts.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadMatrix} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button size="sm" onClick={handleRunEvaluation} disabled={evaluating}>
            <Play className="w-4 h-4 mr-2" />
            {evaluating ? "Evaluating Access..." : "Run SoD & Leaver Analysis"}
          </Button>
        </div>
      </div>

      {analysisResult && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center gap-2 text-primary">
              <ShieldAlert className="w-5 h-5" /> Analysis Findings (Population: {analysisResult.population_count} users)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm">
              Identified <span className="font-bold text-destructive">{analysisResult.exception_count}</span> ITGC exceptions.
            </div>
            <div className="space-y-2">
              {analysisResult.exceptions?.map((e, idx) => (
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

      {/* Conflicting Role Matrix */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold">Standard P2P Segregation of Duties Matrix</CardTitle>
          <p className="text-xs text-muted-foreground">
            Codified toxic role combinations enforced across ERP user entitlements.
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                <tr>
                  <th className="py-2.5 px-4">Primary Entitlement</th>
                  <th className="py-2.5 px-4">Conflicting Entitlement</th>
                  <th className="py-2.5 px-4">Audit Rationale & Risk Signal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {matrix.map((pair, idx) => (
                  <tr key={idx} className="hover:bg-muted/20">
                    <td className="py-3 px-4 font-mono text-xs font-semibold text-primary">
                      {pair.role_a}
                    </td>
                    <td className="py-3 px-4 font-mono text-xs font-semibold text-destructive">
                      {pair.role_b}
                    </td>
                    <td className="py-3 px-4 text-xs text-muted-foreground">
                      {pair.rationale}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

