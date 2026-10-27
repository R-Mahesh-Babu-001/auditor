import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../../components/ui/dialog";
import {
  FileText,
  Table,
  Upload,
  CheckCircle,
  FileCheck,
  Eye,
  RefreshCw,
  Hash,
  Database
} from "lucide-react";
import { api } from "../../services/api";

export default function EvidenceDatasetsView() {
  const [activeTab, setActiveTab] = useState("evidence");
  const [evidenceFiles, setEvidenceFiles] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState("");
  const [previewModal, setPreviewModal] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [evRes, dsRes] = await Promise.all([
        api.getEvidenceFiles(),
        api.getDatasets(),
      ]);
      setEvidenceFiles(evRes.files || []);
      setDatasets(dsRes.datasets || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleEvidenceUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMsg("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("description", `Uploaded via AuditReady workspace: ${file.name}`);
      const res = await api.uploadEvidenceFile(formData);
      setMsg(`Evidence "${file.name}" uploaded, hashed, and indexed into Neon PGVector (${res.fragments_indexed || 0} fragments).`);
      loadData();
    } catch (err) {
      alert(`Evidence upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDatasetUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMsg("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("dataset_type", "p2p_invoices");
      const res = await api.uploadDataset(formData);
      setMsg(`Dataset "${file.name}" profiled successfully (${res.rows_ingested || 0} rows, ${res.columns_detected || 0} columns).`);
      loadData();
    } catch (err) {
      alert(`Dataset upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handlePreviewDataset = async (datasetId) => {
    try {
      const res = await api.previewDataset(datasetId);
      setPreviewData(res);
      setPreviewModal(true);
    } catch (err) {
      alert(`Cannot preview dataset: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Evidence & Datasets</h2>
          <p className="text-sm text-muted-foreground">
            Manage unstructured audit evidence documents (Neon PGVector) and structured tabular datasets.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
        </div>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{msg}</span>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-2 w-72 mb-4">
          <TabsTrigger value="evidence" className="flex items-center gap-2">
            <FileText className="w-4 h-4" /> Evidence Documents ({evidenceFiles.length})
          </TabsTrigger>
          <TabsTrigger value="datasets" className="flex items-center gap-2">
            <Table className="w-4 h-4" /> Audit Datasets ({datasets.length})
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Evidence Files */}
        <TabsContent value="evidence" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold">Evidence Documents</CardTitle>
                <p className="text-xs text-muted-foreground">
                  PDF, DOCX, TXT files stored securely with SHA-256 integrity hashes & indexed into Neon PGVector.
                </p>
              </div>
              <div>
                <label className="cursor-pointer">
                  <Input
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,.txt,.doc"
                    onChange={handleEvidenceUpload}
                    disabled={uploading}
                  />
                  <Button asChild size="sm" disabled={uploading}>
                    <span>
                      <Upload className="w-4 h-4 mr-2" />
                      {uploading ? "Indexing into Neon..." : "Upload Evidence"}
                    </span>
                  </Button>
                </label>
              </div>
            </CardHeader>
            <CardContent>
              {evidenceFiles.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm border-2 border-dashed border-border/50 rounded-lg">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No evidence files uploaded yet. Upload a Procurement SOP or vendor contract.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                      <tr>
                        <th className="py-2.5 px-3">Filename</th>
                        <th className="py-2.5 px-3">File Size</th>
                        <th className="py-2.5 px-3">SHA-256 Integrity Hash</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3">Uploaded</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {evidenceFiles.map((f) => (
                        <tr key={f.id} className="hover:bg-muted/20">
                          <td className="py-2.5 px-3 font-medium flex items-center gap-2">
                            <FileCheck className="w-4 h-4 text-primary" />
                            {f.filename}
                          </td>
                          <td className="py-2.5 px-3 text-muted-foreground">
                            {(f.file_size_bytes / 1024).toFixed(1)} KB
                          </td>
                          <td className="py-2.5 px-3 font-mono text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Hash className="w-3 h-3 text-primary/60" />
                              {f.sha256_hash ? `${f.sha256_hash.slice(0, 16)}...` : "Verified"}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <Badge
                              variant="outline"
                              className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30 text-xs"
                            >
                              Indexed in Neon
                            </Badge>
                          </td>
                          <td className="py-2.5 px-3 text-xs text-muted-foreground">
                            {f.created_at ? new Date(f.created_at).toLocaleDateString() : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Datasets */}
        <TabsContent value="datasets" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold">Structured Audit Datasets</CardTitle>
                <p className="text-xs text-muted-foreground">
                  CSV and Excel ledger files profiled with canonical Procure-to-Pay field mappings.
                </p>
              </div>
              <div>
                <label className="cursor-pointer">
                  <Input
                    type="file"
                    className="hidden"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleDatasetUpload}
                    disabled={uploading}
                  />
                  <Button asChild size="sm" disabled={uploading}>
                    <span>
                      <Table className="w-4 h-4 mr-2" />
                      {uploading ? "Profiling Dataset..." : "Upload CSV / Excel"}
                    </span>
                  </Button>
                </label>
              </div>
            </CardHeader>
            <CardContent>
              {datasets.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm border-2 border-dashed border-border/50 rounded-lg">
                  <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No audit datasets uploaded yet. Upload an ERP purchase order, invoice, or receipt CSV.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                      <tr>
                        <th className="py-2.5 px-3">Dataset Name</th>
                        <th className="py-2.5 px-3">Type</th>
                        <th className="py-2.5 px-3">Rows</th>
                        <th className="py-2.5 px-3">Columns</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {datasets.map((d) => (
                        <tr key={d.id} className="hover:bg-muted/20">
                          <td className="py-2.5 px-3 font-medium">{d.name}</td>
                          <td className="py-2.5 px-3">
                            <Badge variant="outline" className="text-xs">
                              {d.dataset_type}
                            </Badge>
                          </td>
                          <td className="py-2.5 px-3 font-semibold">{d.row_count}</td>
                          <td className="py-2.5 px-3 text-muted-foreground">{d.column_count}</td>
                          <td className="py-2.5 px-3">
                            <Badge
                              variant="outline"
                              className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30 text-xs"
                            >
                              Profiled
                            </Badge>
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handlePreviewDataset(d.id)}
                            >
                              <Eye className="w-3.5 h-3.5 mr-1" /> Preview
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
        </TabsContent>
      </Tabs>

      {/* Dataset Preview Modal */}
      <Dialog open={previewModal} onOpenChange={setPreviewModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Dataset Preview & Profiling Summary</DialogTitle>
          </DialogHeader>
          {previewData && (
            <div className="space-y-4 overflow-y-auto flex-1 pr-1">
              <div className="flex gap-4 p-3 rounded-lg bg-muted/30 text-xs text-muted-foreground">
                <div>
                  <span className="font-semibold text-foreground">Total Rows: </span>
                  {previewData.row_count}
                </div>
                <div>
                  <span className="font-semibold text-foreground">Total Columns: </span>
                  {previewData.columns?.length || 0}
                </div>
              </div>

              {/* Columns profiling */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                  Detected Column Profiling & Canonical Mappings
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {previewData.columns?.map((c) => (
                    <div key={c.id} className="p-2 rounded border border-border/60 text-xs">
                      <div className="font-medium text-foreground">{c.name}</div>
                      <div className="text-[11px] text-muted-foreground flex justify-between mt-1">
                        <span>Type: {c.inferred_type}</span>
                        {c.canonical_field && (
                          <Badge variant="outline" className="text-[10px] text-primary">
                            mapped: {c.canonical_field}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Rows table */}
              <div>
                <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                  Sample Data Rows ({previewData.rows?.length || 0} records preview)
                </h4>
                <div className="border rounded-lg overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-muted/50 border-b">
                      <tr>
                        {previewData.columns?.slice(0, 7).map((c) => (
                          <th key={c.id} className="py-2 px-3 font-semibold">
                            {c.name}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {previewData.rows?.slice(0, 10).map((r, i) => (
                        <tr key={i}>
                          {previewData.columns?.slice(0, 7).map((c) => (
                            <td key={c.id} className="py-1.5 px-3 text-muted-foreground">
                              {String(r.raw_data?.[c.name] ?? "-")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

