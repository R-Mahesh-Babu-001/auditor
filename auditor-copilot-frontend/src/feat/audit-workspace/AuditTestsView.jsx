import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Play, CheckCircle, RefreshCw } from "lucide-react";
import { api } from "../../services/api";

export default function AuditTestsView({ onNavigateToExceptions }) {
  const [templates, setTemplates] = useState([]);
  const [testRuns, setTestRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [resultMsg, setResultMsg] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const [tplRes, runRes] = await Promise.all([
        api.getTestTemplates(),
        api.getTestRuns(),
      ]);
      setTemplates(tplRes.templates || []);
      setTestRuns(runRes.runs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExecuteTest = async (templateCode) => {
    setExecuting(true);
    setResultMsg("");
    try {
      const res = await api.runAuditTest({
        template_code: templateCode,
        parameters: {
          tolerance_pct: 1.0,
          tolerance_amount: 50.0,
          approval_threshold: 1000.0,
        },
      });
      setResultMsg(
        `Test "${templateCode}" executed! Tested ${res.records_tested} records, found ${res.exceptions_found} exceptions.`
      );
      loadData();
    } catch (err) {
      alert(`Test execution failed: ${err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audit Tests & Deterministic Engine</h2>
          <p className="text-sm text-muted-foreground">
            Execute reproducible, deterministic Python audit rules without LLM hallucination risk.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      {resultMsg && (
        <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>{resultMsg}</span>
          </div>
          {onNavigateToExceptions && (
            <Button size="sm" variant="outline" onClick={onNavigateToExceptions}>
              View in Exceptions Queue
            </Button>
          )}
        </div>
      )}

      {/* Available Test Templates */}
      <div>
        <h3 className="text-sm font-semibold uppercase text-muted-foreground mb-3">
          Available Deterministic Test Procedures
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((tpl) => (
            <Card key={tpl.id} className="flex flex-col justify-between hover:border-primary/40 transition">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <Badge variant="outline" className="font-mono text-xs text-primary">
                    {tpl.template_code || tpl.rule_code}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {tpl.domain || tpl.category || "p2p"}
                  </Badge>
                </div>
                <CardTitle className="text-base font-semibold mt-2">{tpl.name}</CardTitle>
                <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                  {tpl.description}
                </p>
              </CardHeader>
              <CardContent className="pt-2">
                <Button
                  className="w-full"
                  size="sm"
                  onClick={() => handleExecuteTest(tpl.template_code || tpl.rule_code)}
                  disabled={executing}
                >
                  <Play className="w-3.5 h-3.5 mr-1.5" />
                  {executing ? "Executing Test..." : "Execute Test"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Test Runs History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold">Execution History</CardTitle>
          <p className="text-xs text-muted-foreground">
            Complete audit trail of tests executed against ingested datasets.
          </p>
        </CardHeader>
        <CardContent>
          {testRuns.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No tests executed yet. Click "Execute Test" above to run an audit procedure.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                  <tr>
                    <th className="py-2.5 px-3">Run ID</th>
                    <th className="py-2.5 px-3">Rule Template</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Records Tested</th>
                    <th className="py-2.5 px-3">Exceptions Found</th>
                    <th className="py-2.5 px-3">Executed At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {testRuns.map((r) => (
                    <tr key={r.id} className="hover:bg-muted/20">
                      <td className="py-2.5 px-3 font-mono text-xs">{r.id.slice(0, 8)}...</td>
                      <td className="py-2.5 px-3 font-medium">{r.template_name || r.template_code || "Audit Test"}</td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant="outline"
                          className={
                            r.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
                              : "bg-amber-500/10 text-amber-600"
                          }
                        >
                          {r.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">{r.total_records_tested}</td>
                      <td className="py-2.5 px-3">
                        <span className={r.exceptions_found > 0 ? "text-destructive font-bold" : "text-emerald-600"}>
                          {r.exceptions_found}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-xs text-muted-foreground">
                        {r.created_at ? new Date(r.created_at).toLocaleString() : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

