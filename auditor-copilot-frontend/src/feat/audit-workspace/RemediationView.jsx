import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "../../../components/ui/dialog";
import { ShieldCheck, RefreshCw, Clock, CheckCircle } from "lucide-react";
import { api } from "../../services/api";

export default function RemediationView() {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);
  const [verifyModal, setVerifyModal] = useState(false);
  const [verifyNote, setVerifyNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState("");

  const loadActions = async () => {
    setLoading(true);
    try {
      const res = await api.getRemediations();
      setActions(res.actions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
  }, []);

  const handleVerifyClosure = async () => {
    if (!selectedAction) return;
    setSubmitting(true);
    try {
      await api.verifyRemediation(selectedAction.id, {
        status: "verified_closed",
        verification_note: verifyNote || "Tested remediation evidence and verified control operating effectiveness.",
      });
      setVerifyModal(false);
      setMsg(`Remediation action verified and formally closed in Neon PostgreSQL.`);
      loadActions();
    } catch (err) {
      alert(`Verification failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "verified_closed":
        return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30">Verified Closed</Badge>;
      case "overdue":
        return <Badge variant="destructive">Overdue</Badge>;
      case "in_progress":
        return <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-500/30">In Progress</Badge>;
      default:
        return <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">Open</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Remediation Tracking & Auditor Verification</h2>
          <p className="text-sm text-muted-foreground">
            Track corrective actions, management commitments, and independent auditor closure testing.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadActions} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          <span>{msg}</span>
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          {actions.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground text-sm">
              <ShieldCheck className="w-8 h-8 mx-auto mb-2 opacity-50" />
              No remediation actions currently tracked. Remediations are linked to audit findings.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                  <tr>
                    <th className="py-2.5 px-4">Action Title & Description</th>
                    <th className="py-2.5 px-4">Due Date</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4">Management Comment</th>
                    <th className="py-2.5 px-4 text-right">Auditor Verification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {actions.map((act) => (
                    <tr key={act.id} className="hover:bg-muted/20">
                      <td className="py-3 px-4 max-w-sm">
                        <div className="font-semibold text-foreground">{act.action_title}</div>
                        <div className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                          {act.action_description}
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono text-xs">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                          {act.due_date || "No due date"}
                        </span>
                      </td>
                      <td className="py-3 px-4">{getStatusBadge(act.status)}</td>
                      <td className="py-3 px-4 text-xs text-muted-foreground max-w-xs truncate">
                        {act.management_comment || "-"}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {act.status !== "verified_closed" ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedAction(act);
                              setVerifyNote("");
                              setVerifyModal(true);
                            }}
                          >
                            <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Verify Closure
                          </Button>
                        ) : (
                          <span className="text-xs text-emerald-600 font-medium">Verified & Closed</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Verification Modal */}
      <Dialog open={verifyModal} onOpenChange={setVerifyModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Auditor Verification & Sign-off</DialogTitle>
          </DialogHeader>
          {selectedAction && (
            <div className="space-y-4 py-2">
              <div>
                <h4 className="text-sm font-semibold">{selectedAction.action_title}</h4>
                <p className="text-xs text-muted-foreground mt-1">
                  {selectedAction.action_description}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold">Auditor Verification Testing Note</label>
                <Textarea
                  placeholder="Document test procedure performed to verify corrective action effectiveness..."
                  rows={3}
                  value={verifyNote}
                  onChange={(e) => setVerifyNote(e.target.value)}
                />
              </div>

              <DialogFooter>
                <Button variant="ghost" onClick={() => setVerifyModal(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleVerifyClosure}
                  disabled={submitting}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white"
                >
                  {submitting ? "Signing Off..." : "Sign-off & Close Action"}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

