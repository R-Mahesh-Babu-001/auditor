import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, Play, RefreshCw, CheckCircle, Zap } from "lucide-react";
import { api } from "../../services/api";

export default function ContinuousAuditingView() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [msg, setMsg] = useState("");

  const loadRules = async () => {
    setLoading(true);
    try {
      const res = await api.getContinuousRules();
      setRules(res.continuous_rules || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleTrigger = async (ruleId) => {
    setTriggering(true);
    setMsg("");
    try {
      const res = await api.triggerContinuousRule(ruleId);
      setMsg(`Continuous rule sweep completed! Tested ${res.records_tested} records, found ${res.exceptions_found} exceptions.`);
      loadRules();
    } catch (err) {
      alert(`Trigger failed: ${err.message}`);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Continuous Auditing & Monitoring</h2>
          <p className="text-sm text-muted-foreground">
            Configure automated recurring sweeps to detect transactional exceptions and risk signals in near-real-time.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadRules} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          <span>{msg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {rules.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="text-center py-12 text-muted-foreground text-sm">
              <Zap className="w-8 h-8 mx-auto mb-2 opacity-50" />
              No continuous rules currently scheduled.
            </CardContent>
          </Card>
        ) : (
          rules.map((r) => (
            <Card key={r.id} className="flex flex-col justify-between">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <Badge variant="outline" className="font-mono text-xs text-primary">
                    {r.rule_code}
                  </Badge>
                  <Badge variant="outline" className="text-xs bg-emerald-500/10 text-emerald-600 border-emerald-500/30">
                    {r.status}
                  </Badge>
                </div>
                <CardTitle className="text-base font-semibold mt-2">{r.name}</CardTitle>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Frequency: {r.frequency} ({r.cron_expression})</span>
                </div>
              </CardHeader>
              <CardContent className="pt-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full"
                  onClick={() => handleTrigger(r.id)}
                  disabled={triggering}
                >
                  <Play className="w-3.5 h-3.5 mr-1 text-primary" /> Run Immediate Sweep
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

