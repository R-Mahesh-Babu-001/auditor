import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Database, Cpu, Shield, RefreshCw } from "lucide-react";
import { api } from "../../services/api";

export default function SettingsView() {
  const [currentUser, setCurrentUser] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadSettingsData = async () => {
    setLoading(true);
    try {
      const [userRes, healthRes] = await Promise.all([
        api.getCurrentUser(),
        api.getHealth(),
      ]);
      setCurrentUser(userRes);
      setHealth(healthRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettingsData();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System & Workspace Settings</h2>
          <p className="text-sm text-muted-foreground">
            Manage organization governance parameters, authentication context, and system connectivity.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadSettingsData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh Settings
        </Button>
      </div>

      {/* Tenancy & User Context */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary" /> Tenant & Auditor Context
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-semibold text-muted-foreground">Organization:</span>
              <div className="text-sm font-semibold text-foreground mt-0.5">
                {currentUser?.organization_name || "Default Enterprise Audit Org"}
              </div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Organization ID:</span>
              <div className="font-mono text-muted-foreground mt-0.5">
                {currentUser?.organization_id || "default-org"}
              </div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Authenticated Actor:</span>
              <div className="text-sm font-semibold text-foreground mt-0.5">
                {currentUser?.full_name || "Lead Internal Auditor"}
              </div>
              <div className="text-muted-foreground">{currentUser?.email || "lead.auditor@enterprise.internal"}</div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Assigned Role:</span>
              <div className="mt-0.5">
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 uppercase text-[10px]">
                  {currentUser?.role || "audit_manager"}
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Persistence Configuration */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-500" /> Database & Storage Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-semibold text-muted-foreground">Database Engine:</span>
              <div className="text-sm font-semibold text-foreground mt-0.5">Neon Serverless PostgreSQL</div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Relational Schema:</span>
              <div className="mt-0.5">
                <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-500/30 font-mono text-[11px]">
                  {health?.database?.schema || "audit_copilot"} (47 tables)
                </Badge>
              </div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Vector Store Backend:</span>
              <div className="font-mono text-foreground mt-0.5">Neon PGVector (langchain_postgres)</div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Document Storage Directory:</span>
              <div className="font-mono text-muted-foreground mt-0.5">storage/evidence_uploads/</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* LLM Engine Configuration */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Cpu className="w-4 h-4 text-primary" /> AI Engine Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-semibold text-muted-foreground">Authorized LLM Provider:</span>
              <div className="text-sm font-semibold text-primary mt-0.5">Google Gemini (Exclusive)</div>
              <p className="text-[11px] text-muted-foreground mt-0.5">Azure OpenAI & AWS Bedrock runtime paths removed.</p>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Active Model:</span>
              <div className="font-mono font-semibold text-foreground mt-0.5">
                {health?.llm?.model || "gemini-2.5-flash"}
              </div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Embeddings Model:</span>
              <div className="font-mono text-foreground mt-0.5">gemini-embedding-001 (768 dimensions)</div>
            </div>
            <div>
              <span className="font-semibold text-muted-foreground">Deterministic Guardrail:</span>
              <div className="text-emerald-600 font-medium mt-0.5">
                Pure Python Rule Engine (Zero AI arithmetic)
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
