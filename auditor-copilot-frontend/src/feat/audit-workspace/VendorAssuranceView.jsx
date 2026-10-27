import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Building2, ShieldCheck, ShieldAlert, Play } from "lucide-react";
import { api } from "../../services/api";

const SAMPLE_VENDORS = [
  {
    vendor_name: "Cloud Infra Host Corp",
    risk_tier: "critical",
    has_soc_report: true,
    soc_report_expiry: "2027-04-30",
  },
  {
    vendor_name: "Global Payroll Solutions LLC",
    risk_tier: "high",
    has_soc_report: false,
    soc_report_expiry: null,
  },
  {
    vendor_name: "Office Stationery Direct",
    risk_tier: "low",
    has_soc_report: false,
  },
  {
    vendor_name: "Data Warehouse Tech Ltd",
    risk_tier: "high",
    has_soc_report: true,
    soc_report_expiry: "2025-12-31", // Expired
  },
];

export default function VendorAssuranceView() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  const handleRunReview = async () => {
    setRunning(true);
    try {
      const res = await api.runVendorAssurance({
        vendors: SAMPLE_VENDORS,
        use_db_suppliers: false,
      });
      setResult(res);
    } catch (err) {
      alert(`Vendor assurance review failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Vendor Third-Party Assurance Review</h2>
          <p className="text-sm text-muted-foreground">
            Verify independent assurance reports (SOC 1 Type II, SOC 2 Type II, ISO 27001) for critical suppliers.
          </p>
        </div>
        <Button size="sm" onClick={handleRunReview} disabled={running}>
          <Play className="w-4 h-4 mr-2" />
          {running ? "Evaluating Vendor Portfolio..." : "Run Vendor Assurance Audit"}
        </Button>
      </div>

      {result && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-500" />
              Vendor Assurance Results ({result.passed_count} Compliant / {result.exception_count} Gaps)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              {result.exceptions?.map((e, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-background border border-border/60 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground">{e.title}</span>
                    <Badge variant="destructive" className="text-[10px] uppercase">
                      {e.severity}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground mt-1">{e.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Vendor Portfolio Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold">Active Third-Party Vendor Portfolio</CardTitle>
          <p className="text-xs text-muted-foreground">
            Risk-tiered supplier directory and annual assurance documentation records.
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground border-b uppercase bg-muted/30">
                <tr>
                  <th className="py-2.5 px-4">Vendor Name</th>
                  <th className="py-2.5 px-4">Risk Tier</th>
                  <th className="py-2.5 px-4">SOC 1/2 Coverage</th>
                  <th className="py-2.5 px-4">Assurance Expiry</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {SAMPLE_VENDORS.map((v, idx) => (
                  <tr key={idx} className="hover:bg-muted/20">
                    <td className="py-3 px-4 font-semibold text-foreground flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-primary" />
                      {v.vendor_name}
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        variant="outline"
                        className={
                          v.risk_tier === "critical"
                            ? "bg-destructive/10 text-destructive border-destructive/30 uppercase"
                            : v.risk_tier === "high"
                            ? "bg-amber-500/10 text-amber-600 border-amber-500/30 uppercase"
                            : "uppercase text-xs"
                        }
                      >
                        {v.risk_tier}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      {v.has_soc_report ? (
                        <span className="text-xs text-emerald-600 flex items-center gap-1">
                          <ShieldCheck className="w-3.5 h-3.5" /> SOC 1 / SOC 2 Type II on file
                        </span>
                      ) : (
                        <span className="text-xs text-destructive flex items-center gap-1">
                          <ShieldAlert className="w-3.5 h-3.5" /> Missing Independent Report
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono text-xs text-muted-foreground">
                      {v.soc_report_expiry || "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

