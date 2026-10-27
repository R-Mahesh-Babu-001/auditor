import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../../components/ui/dialog";
import { FileText, Sparkles, RefreshCw, Eye, CheckCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../../services/api";

export default function WorkpapersView() {
  const [workpapers, setWorkpapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedWp, setSelectedWp] = useState(null);
  const [viewerModal, setViewerModal] = useState(false);
  const [msg, setMsg] = useState("");

  const loadWorkpapers = async () => {
    setLoading(true);
    try {
      const res = await api.getWorkpapers();
      setWorkpapers(res.workpapers || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkpapers();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setMsg("");
    try {
      const res = await api.generateWorkpaper({
        title: `Procure-to-Pay Audit Workpaper - ${new Date().toLocaleDateString()}`,
        objective: "Evaluate operating effectiveness of three-way matching, invoice authorization, and duplicate payment controls.",
        scope: "All procurement purchase orders, goods receipts, and vendor invoices recorded in audit period.",
      });
      setMsg(`Workpaper "${res.workpaper?.title}" generated and versioned in Neon PostgreSQL!`);
      loadWorkpapers();
    } catch (err) {
      alert(`Workpaper generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audit Workpapers</h2>
          <p className="text-sm text-muted-foreground">
            Structured audit documentation synthesized by Google Gemini, grounded in deterministic test outcomes and evidence fragments.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={loadWorkpapers} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button size="sm" onClick={handleGenerate} disabled={generating}>
            <Sparkles className="w-4 h-4 mr-2" />
            {generating ? "Synthesizing with Gemini..." : "Generate Workpaper"}
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
          {workpapers.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground text-sm">
              <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
              No workpapers created yet. Click "Generate Workpaper" to synthesize documentation.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                  <tr>
                    <th className="py-2.5 px-4">Workpaper Title</th>
                    <th className="py-2.5 px-4">Version</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4">Created</th>
                    <th className="py-2.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {workpapers.map((wp) => (
                    <tr key={wp.id} className="hover:bg-muted/20">
                      <td className="py-3 px-4 font-semibold text-foreground flex items-center gap-2">
                        <FileText className="w-4 h-4 text-primary" />
                        {wp.title}
                      </td>
                      <td className="py-3 px-4 font-mono text-xs">v{wp.version_number || 1}.0</td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs capitalize">
                          {wp.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-xs text-muted-foreground">
                        {wp.created_at ? new Date(wp.created_at).toLocaleDateString() : "-"}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedWp(wp);
                            setViewerModal(true);
                          }}
                        >
                          <Eye className="w-3.5 h-3.5 mr-1" /> View Markdown
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

      {/* Workpaper Viewer Modal */}
      <Dialog open={viewerModal} onOpenChange={setViewerModal}>
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              {selectedWp?.title}
            </DialogTitle>
          </DialogHeader>
          <div className="overflow-y-auto flex-1 p-4 rounded-lg bg-card border border-border/50 prose prose-sm dark:prose-invert max-w-none">
            {selectedWp?.content_markdown ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {selectedWp.content_markdown}
              </ReactMarkdown>
            ) : (
              <div className="text-muted-foreground italic">No markdown content available.</div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

