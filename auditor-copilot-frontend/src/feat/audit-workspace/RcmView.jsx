import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Shield, AlertOctagon, CheckCircle2, RefreshCw } from "lucide-react";
import { api } from "../../services/api";

export default function RcmView() {
  const [activeTab, setActiveTab] = useState("controls");
  const [criteria, setCriteria] = useState([]);
  const [risks, setRisks] = useState([]);
  const [controls, setControls] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadRcmData = async () => {
    setLoading(true);
    try {
      const [critRes, riskRes, ctrlRes] = await Promise.all([
        api.getCriteria(),
        api.getRisks(),
        api.getControls(),
      ]);
      setCriteria(critRes.criteria || []);
      setRisks(riskRes.risks || []);
      setControls(ctrlRes.controls || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRcmData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Risk and Control Matrix (RCM)</h2>
          <p className="text-sm text-muted-foreground">
            Audit criteria, risks, internal controls, and testing coverage grounded in COSO & IIA standards.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadRcmData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh RCM
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-3 w-96 mb-4">
          <TabsTrigger value="controls" className="flex items-center gap-1.5">
            <Shield className="w-4 h-4" /> Controls ({controls.length})
          </TabsTrigger>
          <TabsTrigger value="risks" className="flex items-center gap-1.5">
            <AlertOctagon className="w-4 h-4" /> Risks ({risks.length})
          </TabsTrigger>
          <TabsTrigger value="criteria" className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" /> Criteria ({criteria.length})
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Controls */}
        <TabsContent value="controls">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Audit Controls</CardTitle>
            </CardHeader>
            <CardContent>
              {controls.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No internal controls loaded.
                </div>
              ) : (
                <div className="space-y-3">
                  {controls.map((ctrl) => (
                    <div
                      key={ctrl.id}
                      className="p-4 rounded-lg border border-border/60 hover:border-primary/40 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-primary">
                              {ctrl.control_code}
                            </span>
                            <h4 className="text-sm font-semibold">{ctrl.name}</h4>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1.5">{ctrl.description}</p>
                        </div>
                        <div className="flex gap-1.5">
                          <Badge variant="outline" className="text-xs">
                            {ctrl.control_type}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {ctrl.frequency}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Risks */}
        <TabsContent value="risks">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Identified Audit Risks</CardTitle>
            </CardHeader>
            <CardContent>
              {risks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No risks registered in current engagement.
                </div>
              ) : (
                <div className="space-y-3">
                  {risks.map((r) => (
                    <div key={r.id} className="p-4 rounded-lg border border-border/60">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-amber-600">
                              {r.risk_code}
                            </span>
                            <h4 className="text-sm font-semibold">{r.title}</h4>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1.5">{r.description}</p>
                        </div>
                        <Badge
                          variant="outline"
                          className={
                            r.inherent_risk_rating === "high"
                              ? "bg-destructive/10 text-destructive border-destructive/30"
                              : "bg-amber-500/10 text-amber-600 border-amber-500/30"
                          }
                        >
                          {r.inherent_risk_rating || "Medium"} Risk
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Criteria */}
        <TabsContent value="criteria">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Governance & Compliance Criteria</CardTitle>
            </CardHeader>
            <CardContent>
              {criteria.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No criteria defined.
                </div>
              ) : (
                <div className="space-y-3">
                  {criteria.map((c) => (
                    <div key={c.id} className="p-4 rounded-lg border border-border/60">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-blue-600">
                              {c.criterion_code}
                            </span>
                            <h4 className="text-sm font-semibold">{c.title}</h4>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1.5">{c.summary}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {c.source_framework}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

