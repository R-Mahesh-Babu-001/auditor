import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ShieldAlert,
  ShieldCheck,
  FileCheck2,
  AlertTriangle,
  FolderLock,
  Layers,
  Database,
  Cpu,
  RefreshCw,
  Clock,
  ArrowRight
} from "lucide-react";
import { api } from "../../services/api";

export default function DashboardView({ onNavigate }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchKpis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDashboardKpis();
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKpis();
  }, []);

  const kpis = data?.kpis || {};
  const status = data?.engine_status || {};
  const recentRuns = data?.recent_test_runs || [];

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audit Executive Dashboard</h2>
          <p className="text-sm text-muted-foreground">
            Live audit assurance metrics grounded in Neon PostgreSQL and Google Gemini.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={fetchKpis} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh KPIs
          </Button>
        </div>
      </div>

      {/* System & Engine Status Banner */}
      <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold flex items-center gap-2">
              LLM Engine: <span className="text-primary font-bold">Google Gemini</span>
              <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/30">
                {status.model || "gemini-2.5-flash"}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Deterministic rule testing + Gemini workpaper synthesis (Azure/Bedrock decoupled).
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold flex items-center gap-2">
              Persistence: <span className="text-blue-600 font-bold">Neon PostgreSQL</span>
              <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-600 border-blue-500/30">
                schema: audit_copilot
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              47 relational audit tables + Neon PGVector vector store.
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>Error loading live dashboard metrics: {error}</span>
        </div>
      )}

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Engagements</CardTitle>
            <FolderLock className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{kpis.active_engagements ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">In-progress enterprise audits</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Evidence & Datasets</CardTitle>
            <Layers className="w-4 h-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(kpis.evidence_files ?? 0) + (kpis.audit_datasets ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {kpis.evidence_files ?? 0} files / {kpis.audit_datasets ?? 0} datasets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Test Runs Executed</CardTitle>
            <FileCheck2 className="w-4 h-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{kpis.test_runs_executed ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Deterministic automated tests</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Exceptions</CardTitle>
            <ShieldAlert className="w-4 h-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-600">
              {kpis.exceptions?.total ?? 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {kpis.exceptions?.open ?? 0} open / {kpis.exceptions?.confirmed ?? 0} confirmed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Status Rows: Findings & Remediation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Exceptions Breakdown */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center justify-between">
              Exceptions Disposition
              {onNavigate && (
                <Button variant="ghost" size="sm" onClick={() => onNavigate("exceptions")}>
                  Queue <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">Open Triage</span>
              <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">
                {kpis.exceptions?.open ?? 0}
              </Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">Under Review</span>
              <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-500/30">
                {kpis.exceptions?.in_review ?? 0}
              </Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">Confirmed Audit Exceptions</span>
              <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/30">
                {kpis.exceptions?.confirmed ?? 0}
              </Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1">
              <span className="text-muted-foreground">False Positives (Cleared)</span>
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30">
                {kpis.exceptions?.false_positive ?? 0}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Audit Findings */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center justify-between">
              Audit Findings
              {onNavigate && (
                <Button variant="ghost" size="sm" onClick={() => onNavigate("findings")}>
                  Reports <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">High Severity Findings</span>
              <Badge variant="destructive">{kpis.findings?.high ?? 0}</Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">Medium Severity Findings</span>
              <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">
                {kpis.findings?.medium ?? 0}
              </Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">Low / Advisory Findings</span>
              <Badge variant="outline">{kpis.findings?.low ?? 0}</Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1">
              <span className="font-medium text-foreground">Total Formal Findings</span>
              <span className="font-bold">{kpis.findings?.total ?? 0}</span>
            </div>
          </CardContent>
        </Card>

        {/* Remediation & Verification */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center justify-between">
              Remediation Actions
              {onNavigate && (
                <Button variant="ghost" size="sm" onClick={() => onNavigate("remediation")}>
                  Tracking <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-muted-foreground">Open Management Actions</span>
              <span className="font-bold">{kpis.remediation?.open ?? 0}</span>
            </div>
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-destructive font-medium flex items-center gap-1">
                <Clock className="w-3 h-3" /> Overdue Actions
              </span>
              <Badge variant="destructive">{kpis.remediation?.overdue ?? 0}</Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1 border-b border-border/50">
              <span className="text-emerald-600 font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" /> Verified Closed by Auditor
              </span>
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30">
                {kpis.remediation?.verified_closed ?? 0}
              </Badge>
            </div>
            <div className="flex justify-between items-center text-sm py-1">
              <span className="text-muted-foreground">RCM Coverage Ratio</span>
              <span className="text-sm font-semibold">
                {kpis.rcm?.controls ?? 0} controls / {kpis.rcm?.risks ?? 0} risks
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Test Runs Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-semibold">Recent Deterministic Test Runs</CardTitle>
            <p className="text-xs text-muted-foreground">Executed audit procedures against dataset rows.</p>
          </div>
          {onNavigate && (
            <Button variant="outline" size="sm" onClick={() => onNavigate("tests")}>
              View All Runs
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {recentRuns.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No test runs executed yet in this workspace. Run a 3-way match or duplicate detection test from the "Audit Tests & Execution" tab.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                  <tr>
                    <th className="py-2 px-3">Run ID</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Records Tested</th>
                    <th className="py-2 px-3">Exceptions Found</th>
                    <th className="py-2 px-3">Executed At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {recentRuns.map((r) => (
                    <tr key={r.id} className="hover:bg-muted/20">
                      <td className="py-2 px-3 font-mono text-xs">{r.id.slice(0, 8)}...</td>
                      <td className="py-2 px-3">
                        <Badge
                          variant="outline"
                          className={
                            r.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
                              : "bg-amber-500/10 text-amber-600 border-amber-500/30"
                          }
                        >
                          {r.status}
                        </Badge>
                      </td>
                      <td className="py-2 px-3">{r.total_records}</td>
                      <td className="py-2 px-3">
                        <span className={r.exceptions_found > 0 ? "text-destructive font-bold" : "text-emerald-600"}>
                          {r.exceptions_found}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-xs text-muted-foreground">
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

