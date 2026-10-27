import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "../../../components/ui/dialog";
import { Plus, RefreshCw, Calendar, CheckCircle } from "lucide-react";
import { api } from "../../services/api";

export default function EngagementsView() {
  const [engagements, setEngagements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [auditYear, setAuditYear] = useState(new Date().getFullYear());
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState("");

  const loadEngagements = async () => {
    setLoading(true);
    try {
      const res = await api.getEngagements();
      setEngagements(res.engagements || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEngagements();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);
    setMsg("");
    try {
      await api.createEngagement({
        title,
        audit_year: parseInt(auditYear, 10),
        period_start: periodStart || null,
        period_end: periodEnd || null,
      });
      setModalOpen(false);
      setTitle("");
      setMsg("Engagement created successfully!");
      loadEngagements();
    } catch (err) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audit Engagements</h2>
          <p className="text-sm text-muted-foreground">
            Manage audit scopes, reporting periods, and engagement memberships in Neon PostgreSQL.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={loadEngagements} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button size="sm" onClick={() => setModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" /> New Engagement
          </Button>
        </div>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4" /> {msg}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {engagements.map((eng) => (
          <Card key={eng.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-start justify-between pb-2">
              <div className="space-y-1">
                <CardTitle className="text-base font-semibold">{eng.title}</CardTitle>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Audit Year: {eng.audit_year}</span>
                </div>
              </div>
              <Badge
                variant="outline"
                className={
                  eng.status === "in_progress"
                    ? "bg-primary/10 text-primary border-primary/30"
                    : "bg-muted text-muted-foreground"
                }
              >
                {eng.status}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-3 pt-2">
              <div className="text-xs text-muted-foreground flex justify-between">
                <span>Period Start:</span>
                <span className="font-medium text-foreground">{eng.period_start || "N/A"}</span>
              </div>
              <div className="text-xs text-muted-foreground flex justify-between">
                <span>Period End:</span>
                <span className="font-medium text-foreground">{eng.period_end || "N/A"}</span>
              </div>
              <div className="pt-2 border-t border-border/50 text-[11px] text-muted-foreground font-mono">
                ID: {eng.id.slice(0, 16)}...
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* New Engagement Modal */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create Audit Engagement</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate} className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="eng-title">Engagement Title</Label>
              <Input
                id="eng-title"
                placeholder="e.g. FY2026 Q1 Procure-to-Pay Internal Audit"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="eng-year">Audit Year</Label>
              <Input
                id="eng-year"
                type="number"
                value={auditYear}
                onChange={(e) => setAuditYear(e.target.value)}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="eng-start">Period Start</Label>
                <Input
                  id="eng-start"
                  type="date"
                  value={periodStart}
                  onChange={(e) => setPeriodStart(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="eng-end">Period End</Label>
                <Input
                  id="eng-end"
                  type="date"
                  value={periodEnd}
                  onChange={(e) => setPeriodEnd(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter className="pt-2">
              <Button type="button" variant="ghost" onClick={() => setModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creating..." : "Create Engagement"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

