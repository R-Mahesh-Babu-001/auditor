import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent } from "@/components/ui/tabs"
import { MessageCircle, FileText, FileCheck, Download } from "lucide-react"
import ChatInterface from "../components/chatInterface"
import Sidebar from "../globalComponents/SideBar"
import ModelConfigsidebar from "../globalComponents/ModelConfigsidebar"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../../components/ui/tooltip"
import { Trash } from "lucide-react";
import downloadConversation from "../hooks/downloadConversation"
import SopFlowChartScreen from "../feat/sop-flowchart/screen"
import DigitalAuditScreen from "../feat/digital-audit/screen"

export default function Home() {
  const [activeTab, setActiveTab] = useState("chat")
  const [conversation, setConversation] = useState("")

  const [model, setModel] = useState(localStorage.getItem("model") || "gpt-5.2-chat");
  const [provider, setProvider] = useState(localStorage.getItem("provider") || "azure openai");

  const [cleared, setCleared] = useState(false);

  const clearConversation = (tab) => {
    // Clear the conversation based on the active tab
    if (tab === "chat") {
      // Clear chat conversation logic
      setConversation("");
      localStorage.removeItem("chat-chatMessages")
      setCleared(true)
    }
      else if (tab === "digital-audit") {
        // Clear chat conversation logic
        setConversation("");
        localStorage.removeItem("digital-audit-chatMessages")
        setCleared(true)
    } else if (tab === "execute-analysis-scenario") {
      // Clear execute analysis scenario conversation logic
      setConversation("");
      localStorage.removeItem("execute-analysis-scenario-chatMessages")
      setCleared(true)
    } else if (tab === "document-intelligence") {
      // Clear document intelligence conversation logic
      setConversation("");
      localStorage.removeItem("document-intelligence-chatMessages")
      setCleared(true)
    } else if (tab === "compliance-check") {
      // Clear compliance check conversation logic
      setConversation("");
      localStorage.removeItem("compliance-check-chatMessages")
      setCleared(true)
    } else if (tab === "sop-flowchart") {
      // Clear SOP Flowchart conversation logic
      setConversation("");
      localStorage.removeItem("sop-flowchart-chatMessages")
      setCleared(true)
    }
  }

  const triggerConversationDownload = (tab) => {
    if (tab === "chat") {
      // console.log('chat: ', conversation);
      downloadConversation(conversation)
    } else if (tab === "execute-analysis-scenario") {
      // Clear execute analysis scenario conversation logic
      // console.log('execute: ', conversation);
      downloadConversation(conversation)

    } else if (tab === "document-intelligence") {
      // Clear document intelligence conversation logic
      // console.log('document: ', conversation);
      downloadConversation(conversation)
    }
  }

  useEffect(() => {
    if (cleared) {
      const timeout = setTimeout(() => {
        setCleared(false)
      }, 100)
      return () => clearTimeout(timeout)
    }
  }, [cleared])


  return (
    <div className="flex h-[calc(100vh-3.9rem)] overflow-hidden">
      <div className="flex-none z-30">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-transparent">
        <header className="border-b border-border/40 bg-card/30 backdrop-blur-md px-6 py-3 flex items-center justify-between sticky top-0 z-20">
          <h1 className="text-xl font-semibold tracking-tight text-foreground/90">
            {activeTab === "chat" && "Ask a business question"}
            {activeTab === "digital-audit" && "Digital Audit"}
            {activeTab === "compliance-check" && "Compliance Check"}
            {activeTab === "execute-analysis-scenario" && "Execute Analysis Scenario"}
            {activeTab === "document-intelligence" && "Document Intelligence"}
            {activeTab === "sop-flowchart" && "SOP Flowchart"}
          </h1>


          <div className="flex items-center space-x-10">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    className="hover:text-destructive transition-colors"
                    aria-label="Clear this conversation"
                    onClick={() => clearConversation(activeTab)}
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
                    disabled={conversation.length>0 ? false : true}
                    className="hover:text-destructive transition-colors"
                    aria-label="Download this conversation"
                    onClick={() => triggerConversationDownload(activeTab)}
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Download this conversation</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          <div className="text-sm text-muted-foreground flex flex-col items-end">
            {/* <div> */}

            {/* </div> */}
            <span className="font-medium">
              Provider: <span className="text-primary">
                {provider === "azure openai" ? "Azure OpenAI" : 
                 provider === "awsbedrock" ? "AWS Bedrock" : 
                 (provider || "None")}
              </span>
            </span>
            <span className="font-medium">
              Model: <span className="text-primary">{model || "None"}</span>
            </span>
          </div>
        </header>

        <main className="flex-1 p-6 overflow-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsContent value="chat" className="mt-0">
              <ChatInterface setConversation={setConversation} key={`chat-${cleared}`} action={'chat'} />
            </TabsContent>
            <TabsContent value="digital-audit" className="mt-0">
              <DigitalAuditScreen setConversation={setConversation} key={`digital-${cleared}`} action={'digital-audit'} />
              {/* <ChatInterface setConversation={setConversation} key={`digital-${cleared}`} action={'digital-audit'} /> */}
            </TabsContent>
            <TabsContent value="compliance-check" className="mt-0">
              <ChatInterface setConversation={setConversation} key={`compliance-${cleared}`} action={'compliance-check'} />
            </TabsContent>
            <TabsContent value="execute-analysis-scenario" className="mt-0">
              <ChatInterface setConversation={setConversation} key={`execute-${cleared}`} action={'execute-analysis-scenario'} />
            </TabsContent>
            <TabsContent value="document-intelligence" className="mt-0">
              <ChatInterface setConversation={setConversation} key={`doc-${cleared}`} action={'document-intelligence'} />
            </TabsContent>
            <TabsContent value="sop-flowchart" className="mt-0  h-[80vh] flex flex-col">
              <SopFlowChartScreen setConversation={setConversation} key={`doc-${cleared}`} action={'sop-flowchart'}/>
            </TabsContent>
          </Tabs>
        </main>
      </div>
      <div>
        <ModelConfigsidebar setModel={setModel} setProvider={setProvider} />
      </div>
    </div>
  )
}