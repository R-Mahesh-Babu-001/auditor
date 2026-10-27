import { useState, useEffect } from "react";
import { Download, Trash, Database, Cpu } from "lucide-react";
import Sidebar from "../globalComponents/SideBar";
import ModelConfigSidebar from "../globalComponents/ModelConfigsidebar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import downloadConversation from "../hooks/downloadConversation";
import safeStorage from "../lib/safeStorage";

// Workspace Views
import DashboardView from "../feat/audit-workspace/DashboardView";
import EngagementsView from "../feat/audit-workspace/EngagementsView";
import EvidenceDatasetsView from "../feat/audit-workspace/EvidenceDatasetsView";
import RcmView from "../feat/audit-workspace/RcmView";
import AuditTestsView from "../feat/audit-workspace/AuditTestsView";
import ExceptionsView from "../feat/audit-workspace/ExceptionsView";
import WorkpapersView from "../feat/audit-workspace/WorkpapersView";
import FindingsView from "../feat/audit-workspace/FindingsView";
import RemediationView from "../feat/audit-workspace/RemediationView";
import ContinuousAuditingView from "../feat/audit-workspace/ContinuousAuditingView";
import ItgcSodView from "../feat/audit-workspace/ItgcSodView";
import VendorAssuranceView from "../feat/audit-workspace/VendorAssuranceView";
import AIGovernanceView from "../feat/audit-workspace/AIGovernanceView";
import SettingsView from "../feat/audit-workspace/SettingsView";
import SopFlowChartScreen from "../feat/sop-flowchart/screen";
import ChatInterface from "../components/chatInterface";

const TAB_TITLES = {
  dashboard: "Executive Audit Dashboard",
  engagements: "Audit Engagements & Scopes",
  "evidence-datasets": "Evidence Documents & Audit Datasets",
  rcm: "Risk and Control Matrix (RCM)",
  "audit-tests": "Deterministic Audit Testing Engine",
  exceptions: "Exceptions Queue & Disposition Triage",
  workpapers: "Audit Workpapers & Claim Verification",
  findings: "Audit Findings & Formal Reports",
  remediation: "Remediation Tracking & Auditor Verification",
  continuous: "Continuous Auditing & Automated Sweeps",
  "itgc-sod": "ITGC & Segregation of Duties Review",
  "vendor-assurance": "Vendor Third-Party Assurance Audit",
  "ai-governance": "Enterprise AI Governance & Shadow AI Audit",
  "sop-flowchart": "SOP Process Maps & Flowcharts",
  chat: "Audit Copilot Advisory Chat",
  settings: "System & Workspace Settings",
};

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [conversation, setConversation] = useState("");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [provider, setProvider] = useState("Google Gemini");
  const [cleared, setCleared] = useState(false);

  const clearConversation = () => {
    setConversation("");
    safeStorage.removeItem("chat-chatMessages");
    setCleared(true);
  };

  const triggerConversationDownload = () => {
    if (conversation) {
      downloadConversation(conversation);
    }
  };

  useEffect(() => {
    if (cleared) {
      const timeout = setTimeout(() => setCleared(false), 100);
      return () => clearTimeout(timeout);
    }
  }, [cleared]);

  return (
    <div className="flex h-[calc(100vh-3.9rem)] overflow-hidden">
      {/* Sidebar */}
      <div className="flex-none z-30">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-transparent overflow-hidden">
        {/* Top Header */}
        <header className="border-b border-border/40 bg-card/30 backdrop-blur-md px-6 py-2.5 flex items-center justify-between sticky top-0 z-20 shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold tracking-tight text-foreground/90">
              {TAB_TITLES[activeTab] || "Audit Copilot Workspace"}
            </h1>
            <Badge variant="outline" className="text-[11px] bg-primary/10 text-primary border-primary/20">
              Procure-to-Pay Scope
            </Badge>
          </div>

          <div className="flex items-center gap-4">
            {activeTab === "chat" && (
              <div className="flex items-center space-x-2 border-r border-border/50 pr-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        className="p-1.5 hover:text-destructive rounded hover:bg-muted/40 transition-colors"
                        aria-label="Clear chat conversation"
                        onClick={clearConversation}
                      >
                        <Trash className="w-4 h-4" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Clear this conversation</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        disabled={!conversation || conversation.length === 0}
                        className="p-1.5 hover:text-primary rounded hover:bg-muted/40 transition-colors disabled:opacity-40"
                        aria-label="Download conversation PDF"
                        onClick={triggerConversationDownload}
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Download conversation PDF</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            )}

            {/* Architecture Badges */}
            <div className="flex items-center gap-2 text-xs">
              <span className="flex items-center gap-1 text-muted-foreground font-medium">
                <Cpu className="w-3.5 h-3.5 text-primary" />
                <span className="text-foreground">{provider}</span>
                <span className="font-mono text-primary text-[11px]">({model})</span>
              </span>
              <span className="text-muted-foreground">•</span>
              <span className="flex items-center gap-1 text-muted-foreground font-medium">
                <Database className="w-3.5 h-3.5 text-blue-500" />
                <span className="text-foreground">Neon PostgreSQL</span>
              </span>
            </div>
          </div>
        </header>

        {/* Dynamic Workspace View */}
        <main className="flex-1 p-6 overflow-y-auto">
          {activeTab === "dashboard" && <DashboardView onNavigate={setActiveTab} />}
          {activeTab === "engagements" && <EngagementsView />}
          {activeTab === "evidence-datasets" && <EvidenceDatasetsView />}
          {activeTab === "rcm" && <RcmView />}
          {activeTab === "audit-tests" && (
            <AuditTestsView onNavigateToExceptions={() => setActiveTab("exceptions")} />
          )}
          {activeTab === "exceptions" && <ExceptionsView />}
          {activeTab === "workpapers" && <WorkpapersView />}
          {activeTab === "findings" && <FindingsView />}
          {activeTab === "remediation" && <RemediationView />}
          {activeTab === "continuous" && <ContinuousAuditingView />}
          {activeTab === "itgc-sod" && <ItgcSodView />}
          {activeTab === "vendor-assurance" && <VendorAssuranceView />}
          {activeTab === "ai-governance" && <AIGovernanceView />}
          {activeTab === "settings" && <SettingsView />}
          {activeTab === "sop-flowchart" && (
            <div className="h-[80vh] flex flex-col">
              <SopFlowChartScreen />
            </div>
          )}
          {activeTab === "chat" && (
            <div className="h-[calc(100vh-8.5rem)]">
              <ChatInterface
                setConversation={setConversation}
                key={`chat-${cleared}`}
                action="chat"
              />
            </div>
          )}
        </main>
      </div>

      {/* Model Config Sidebar */}
      <div>
        <ModelConfigSidebar setModel={setModel} setProvider={setProvider} />
      </div>
    </div>
  );
}
