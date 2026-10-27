import React, { useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  FolderLock,
  Database,
  ShieldCheck,
  PlaySquare,
  ShieldAlert,
  FileText,
  FileCheck2,
  Workflow,
  MessageCircle,
  Users,
  Building2,
  Cpu,
  Clock,
  Sparkles,
  Settings
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "../lib/utils";

const NAV_GROUPS = [
  {
    label: "Audit Assurance Lifecycle",
    items: [
      { id: "dashboard", label: "Executive Dashboard", icon: LayoutDashboard },
      { id: "engagements", label: "Audit Engagements", icon: FolderLock },
      { id: "evidence-datasets", label: "Evidence & Datasets", icon: Database },
      { id: "rcm", label: "Risk & Controls (RCM)", icon: ShieldCheck },
      { id: "audit-tests", label: "Tests & Execution", icon: PlaySquare },
      { id: "exceptions", label: "Exceptions & Triage", icon: ShieldAlert },
      { id: "workpapers", label: "Audit Workpapers", icon: FileText },
      { id: "findings", label: "Findings & Reports", icon: FileCheck2 },
      { id: "remediation", label: "Remediation Tracking", icon: ShieldCheck },
      { id: "continuous", label: "Continuous Auditing", icon: Clock },
    ],
  },
  {
    label: "Governance & Review",
    items: [
      { id: "itgc-sod", label: "ITGC & SoD Review", icon: Users },
      { id: "vendor-assurance", label: "Vendor Assurance", icon: Building2 },
      { id: "ai-governance", label: "AI Governance Audit", icon: Cpu },
      { id: "sop-flowchart", label: "SOP Process Maps", icon: Workflow },
    ],
  },
  {
    label: "AI Copilot Assistant",
    items: [
      { id: "chat", label: "Copilot Advisory Chat", icon: MessageCircle },
    ],
  },
  {
    label: "Configuration & System",
    items: [
      { id: "settings", label: "Workspace & Settings", icon: Settings },
    ],
  },
];

const Sidebar = ({ activeTab, setActiveTab }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div
      className={cn(
        "h-full transition-all duration-300 ease-in-out border-r border-border/40 bg-card/30 backdrop-blur-md p-3 flex flex-col shadow-sm z-40 overflow-hidden",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border/40 mb-2">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <span className="text-primary font-bold text-base flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-primary" /> AuditReady
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary font-semibold">
              v2.0
            </span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="shrink-0 hover:bg-primary/10 hover:text-primary transition-colors rounded-full h-7 w-7"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </Button>
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 space-y-4 overflow-y-auto pr-1">
        {NAV_GROUPS.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            {!collapsed && (
              <div className="px-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 mb-1">
                {group.label}
              </div>
            )}
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  className={cn(
                    "w-full justify-start text-xs h-8 px-2.5",
                    isActive && "bg-primary text-primary-foreground font-semibold shadow-sm"
                  )}
                  onClick={() => setActiveTab(item.id)}
                  title={collapsed ? item.label : undefined}
                >
                  <Icon className={cn("h-4 w-4 shrink-0", !collapsed && "mr-2")} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </Button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User profile footer */}
      <div className="pt-3 border-t border-border/40 mt-auto">
        <div className="flex items-center px-1">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
            LA
          </div>
          {!collapsed && (
            <div className="ml-2.5 overflow-hidden">
              <p className="text-xs font-semibold text-foreground truncate">Lead Internal Auditor</p>
              <p className="text-[10px] text-muted-foreground truncate">Neon / Gemini Authenticated</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
