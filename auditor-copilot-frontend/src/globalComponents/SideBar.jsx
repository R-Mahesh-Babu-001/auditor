import { useState } from "react";
import { ChevronLeft, ChevronRight, MessageCircle, FileText, FileCheck, Settings, Rocket, AppWindow, Component, Workflow, HandCoins} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "../lib/utils"
// import {useNavigate} from "react-router-dom"

const Sidebar = ({ activeTab, setActiveTab }) => {
  const [collapsed, setCollapsed] = useState(false);
  //   const [activeTab, setActiveTab] = useState("chat");
  // const navigate = useNavigate()

  return (
    <div
      className={cn(
        // h-full
        "h-full transition-all duration-300 ease-in-out border-r border-border/40 bg-card/30 backdrop-blur-md p-4 flex flex-col shadow-sm z-40",
        collapsed ? "w-20" : "w-[22rem]"
      )}
    >
      <div className="flex items-center justify-between mb-6">
        <span>
          {/* {!collapsed && (
          <h2 className="text-2xl font-bold text-primary">Invoice AI</h2>
        )} */}
          {!collapsed && (
            <p className="text-sm font-medium text-muted-foreground/80 my-2 leading-relaxed">
              As your personal audit assistant, I can help you with the following tasks...
            </p>
          )}
        </span>
        <span>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="shrink-0 hover:bg-primary/10 hover:text-primary transition-colors rounded-full h-8 w-8"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </Button>
        </span>
      </div>

      {/* {!collapsed && (
        // <p className="text-sm text-muted-foreground mb-8">
        //   Your personal invoice assistant
        // </p>
      )} */}

      <nav className="space-y-2 flex-1">
        <Button
          variant={activeTab === "chat" ? "default" : "ghost"}
          className="w-full justify-start"
          onClick={() => setActiveTab("chat")}
        >
          <MessageCircle className="mr-2 h-4 w-4" />
          {!collapsed && "Ask a business question"}
        </Button>
        <Button
          variant={activeTab === "digital-audit" ? "default" : "ghost"}
          className="w-full justify-start"
          disabled
          onClick={() => setActiveTab("digital-audit")}
        >
          {/* <MessageCircle className="mr-2 h-4 w-4" /> */}
          <AppWindow className="mr-2 h-4 w-4" />
          {!collapsed && "Digital Audit"}
        </Button>
         <Button
          variant={activeTab === "corporate-accounting" ? "default" : "ghost"}
          className="w-full justify-start"
          disabled
          onClick={() => setActiveTab("corporate-accounting")}
        >
          {/* <MessageCircle className="mr-2 h-4 w-4" /> */}
          <HandCoins className="mr-2 h-4 w-4" />
          {!collapsed && "Corporate Accounting Guidelines"}
        </Button>
         <Button
          variant={activeTab === "compliance-check" ? "default" : "ghost"}
          className="w-full justify-start"
          // disabled
          onClick={() => setActiveTab("compliance-check")}
        >
          {/* <MessageCircle className="mr-2 h-4 w-4" /> */}
          <Component className="mr-2 h-4 w-4" />
          {!collapsed && "Compliance Check"}
        </Button>
        <Button
          variant={activeTab === "execute-analysis-scenario" ? "default" : "ghost"}
          className="w-full justify-start"
          onClick={() => setActiveTab("execute-analysis-scenario")}
        >
          <FileCheck className="mr-2 h-4 w-4" />
          {!collapsed && "Execute Analysis Scenario"}
        </Button>
        <Button
          variant={activeTab === "document-intelligence" ? "default" : "ghost"}
          className="w-full justify-start"
          onClick={() => setActiveTab("document-intelligence")}
        >
          <FileText className="mr-2 h-4 w-4" />
          {!collapsed && "AI Document Analysis"}
        </Button>
        <Button
          variant={activeTab === "sop-flowchart" ? "default" : "ghost"}
          className="w-full justify-start"
          // disabled
          onClick={() => setActiveTab("sop-flowchart")}
        >
          <Workflow className="mr-2 h-4 w-4" />
          {!collapsed && "SOP to Flowchart"}
        </Button>
        <Button
          // disabled
          variant={"ghost"}
          className="w-full justify-start"
          disabled
          onClick={() => window.open("https://genailabs.azurewebsites.net/", "_blank")}
        >
          {/* <FileText  /> */}
          <Rocket className="mr-2 h-4 w-4" />
          {!collapsed && "Usecase Labs"}
        </Button>
      </nav>

      <div className="mt-auto pt-4 border-t border-border/50">
        <div className="flex items-center mb-4 px-2">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white shadow-md ring-2 ring-background">
            U
          </div>
          {!collapsed && (
            <div className="ml-3">
              <p className="text-sm font-semibold text-foreground">User Account</p>
              <p className="text-xs text-muted-foreground">Admin</p>
            </div>
          )}
        </div>
        <Button variant="outline" size="sm" className="w-full justify-start hover:bg-muted/50">
          <Settings className="w-4 h-4 mr-2" />
          {!collapsed && "Settings"}
        </Button>
      </div>
    </div>
  );
}

export default Sidebar