import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../srccomponents/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "../../../components/ui/dialog";
import { ShieldAlert, RefreshCw, CheckCircle, Filter, ArrowUpRight } from "lucide-react";
import { api } from "../../services/api";

export default function ExceptionsView() {
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterDisposition, setFilterDisposition] = useState("all");
  const [selectedException, setSelectedException] = useState(null);
  const [dispositionModal, setDispositionModal] = useState(false);
  const [newDisposition, setNewDisposition] = useState("confirmed_exception");
  const [rationale, setRationale] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState("");

  const loadExceptions = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterDisposition !== "all") {
        params.disposition = filterDisposition;
      }
      const res = await api.getExceptions(params);
      setExceptions(res.exceptions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExceptions();
  }, [filterDisposition]);

  const handleOpenDisposition = (exc) => {
    setSelectedException(exc);
    setNewDisposition(exc.disposition === "open" ? "confirmed_exception" : exc.disposition);
    setRationale(exc.rationale || "");
    setDispositionModal(true);
  };

  const handleSaveDisposition = async () => {
    if (!selectedException) return;
    setSubmitting(true);
    try {
      await api.setExceptionDisposition(selectedException.id, {
        disposition: newDisposition,
        disposition_comment: rationale,
      });
      setDispositionModal(false);
      setMsg(`Exception updated to "${newDisposition}".`);
      loadExceptions();
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return <Badge variant="destructive" className="bg-red-600">Critical</Badge>;
      case "high":
        return <Badge variant="destructive">High</Badge>;
      case "medium":
        return <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">Medium</Badge>;
      default:
        return <Badge variant="outline">Low</Badge>;
    }
  };

  const getDispositionBadge = (disp) => {
    switch (disp) {
      case "confirmed_exception":
        return <Badge variant="destructive">Confirmed</Badge>;
      case "false_positive":
        return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30">False Positive</Badge>;
      case "accepted_risk":
        return <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-500/30">Accepted Risk</Badge>;
      case "in_review":
        return <Badge variant="outline" className="bg-purple-500/10 text-purple-600 border-purple-500/30">In Review</Badge>;
      default:
        return <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">Open</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Exceptions & Triage Queue</h2>
          <p className="text-sm text-muted-foreground">
            Review, investigate, and disposition exceptions identified by deterministic audit testing.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <Filter className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-muted-foreground">Filter:</span>
            <Select value={filterDisposition} onValueChange={setFilterDisposition}>
              <SelectTrigger className="w-36 h-8 text-xs">
                <SelectValue placeholder="All Dispositions" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Dispositions</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="confirmed_exception">Confirmed</SelectItem>
                <SelectItem value="false_positive">False Positive</SelectItem>
                <SelectItem value="accepted_risk">Accepted Risk</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button variant="outline" size="sm" onClick={loadExceptions} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
        </div>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          <span>{msg}</span>
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          {exceptions.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground text-sm">
              <ShieldAlert className="w-8 h-8 mx-auto mb-2 opacity-50" />
              No exceptions found for the selected filter.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                  <tr>
                    <th className="py-2.5 px-4">Severity</th>
                    <th className="py-2.5 px-4">Exception Key & Title</th>
                    <th className="py-2.5 px-4">Type</th>
                    <th className="py-2.5 px-4">Disposition</th>
                    <th className="py-2.5 px-4">Observed vs Expected</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {exceptions.map((exc) => (
                    <tr key={exc.id} className="hover:bg-muted/20">
                      <td className="py-3 px-4">{getSeverityBadge(exc.severity)}</td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-foreground">{exc.title}</div>
                        <div className="text-xs text-muted-foreground font-mono mt-0.5">
                          {exc.exception_key}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs">
                          {exc.exception_type}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">{getDispositionBadge(exc.disposition)}</td>
                      <td className="py-3 px-4 max-w-xs text-xs text-muted-foreground">
                        {exc.observed_values && (
                          <div className="truncate">
                            Obs: {JSON.stringify(exc.observed_values)}
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleOpenDisposition(exc)}
                        >
                          Triage <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Disposition Modal */}
      <Dialog open={dispositionModal} onOpenChange={setDispositionModal}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Audit Exception Disposition</DialogTitle>
          </DialogHeader>
          {selectedException && (
            <div className="space-y-4 py-2">
              <div>
                <h4 className="text-sm font-semibold">{selectedException.title}</h4>
                <p className="text-xs text-muted-foreground mt-1">
                  {selectedException.description}
                </p>
              </div>

              <div className="p-3 rounded-lg bg-muted/40 text-xs space-y-1">
                <div>
                  <span className="font-semibold">Observed Values: </span>
                  <pre className="mt-1 font-mono text-[11px] bg-background/60 p-2 rounded overflow-x-auto">
                    {JSON.stringify(selectedException.observed_values, null, 2)}
                  </pre>
                </div>
                <div>
                  <span className="font-semibold">Expected Values: </span>
                  <pre className="mt-1 font-mono text-[11px] bg-background/60 p-2 rounded overflow-x-auto">
                    {JSON.stringify(selectedException.expected_values, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold">Select Disposition</label>
                <Select value={newDisposition} onValueChange={setNewDisposition}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="confirmed_exception">Confirmed Audit Exception</SelectItem>
                    <SelectItem value="false_positive">False Positive (Explain in Rationale)</SelectItem>
                    <SelectItem value="accepted_risk">Management Accepted Risk</SelectItem>
                    <SelectItem value="in_review">Further Auditor Review Needed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold">Auditor Rationale & Notes</label>
                <Textarea
                  placeholder="Document professional judgment, evidence verification, or mitigation..."
                  rows={3}
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                />
              </div>

              <DialogFooter>
                <Button variant="ghost" onClick={() => setDispositionModal(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSaveDisposition} disabled={submitting}>
                  {submitting ? "Saving..." : "Save Disposition"}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

