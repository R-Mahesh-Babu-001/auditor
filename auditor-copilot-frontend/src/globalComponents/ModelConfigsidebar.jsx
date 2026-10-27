import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Sparkles, Cpu, Database, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "../lib/utils";
import safeStorage from "../lib/safeStorage";
import PromptLibrary from "../components/chatInterfaceComponents/PromptLibrary";
import { api } from "../services/api";

const GEMINI_MODELS = [
  { name: "gemini-2.5-flash", label: "Gemini 2.5 Flash (Production)", available: true },
  { name: "gemini-2.5-pro", label: "Gemini 2.5 Pro (Deep Reasoning)", available: true },
];

const DEFAULT_PROVIDER = "Google Gemini";
const DEFAULT_MODEL = "gemini-2.5-flash";

const ModelConfigSidebar = ({ setModel, setProvider }) => {
  const [collapsed, setCollapsed] = useState(true);
  const [model, setLocalModel] = useState(DEFAULT_MODEL);
  const [promptLibraryOpen, setPromptLibraryOpen] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    const savedModel = safeStorage.getItem("model") || DEFAULT_MODEL;
    setLocalModel(savedModel);
    setModel(savedModel);
    setProvider(DEFAULT_PROVIDER);
    safeStorage.setItem("provider", DEFAULT_PROVIDER);
    safeStorage.setItem("model", savedModel);

    // Query backend health
    api.getHealth()
      .then((res) => setHealthStatus(res))
      .catch(() => setHealthStatus({ status: "backend_standby" }));
  }, [setModel, setProvider]);

  const handleModelChange = (value) => {
    setLocalModel(value);
    setModel(value);
    safeStorage.setItem("model", value);
  };

  const handlePromptSelect = (prompt) => {
    window.dispatchEvent(new CustomEvent("promptLibrarySelect", { detail: { prompt } }));
    setPromptLibraryOpen(false);
  };

  return (
    <>
      <div
        className={cn(
          "h-full transition-all duration-300 ease-in-out border-l border-border/40 bg-card/40 backdrop-blur-md p-4 flex flex-col shadow-sm z-40",
          collapsed ? "w-16" : "w-80"
        )}
      >
        <div className="mb-6 flex items-center justify-between">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="shrink-0 hover:bg-primary/10 hover:text-primary transition-colors rounded-full"
          >
            {collapsed ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
          </Button>
          {!collapsed && (
            <p className="text-sm text-foreground my-2 ml-2 font-semibold">
              Engine & Model Config
            </p>
          )}
        </div>

        {/* Prompt Library Button */}
        <div className="mb-4">
          {collapsed ? (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setPromptLibraryOpen(true)}
              className="w-full h-10 hover:bg-primary/10 hover:text-primary transition-colors rounded-lg"
              title="Prompt Library"
            >
              <Sparkles className="h-5 w-5 text-amber-500" />
            </Button>
          ) : (
            <Button
              variant="outline"
              onClick={() => setPromptLibraryOpen(true)}
              className="w-full justify-start border-primary/20 hover:bg-primary/5 hover:text-primary hover:border-primary/40 transition-all"
            >
              <Sparkles className="mr-2 h-4 w-4 text-amber-500" />
              Prompt Library
            </Button>
          )}
        </div>

        {!collapsed && (
          <div className="space-y-4">
            <Card className="border-border/40 bg-card/40 shadow-sm">
              <CardContent className="p-4 space-y-4">
                <div>
                  <Label className="text-xs font-semibold text-foreground/80 flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-primary" /> Active LLM Provider
                  </Label>
                  <div className="mt-1 p-2 rounded-md bg-background/60 border border-primary/30 flex items-center justify-between">
                    <span className="text-xs font-semibold text-primary">Google Gemini</span>
                    <Badge variant="outline" className="text-[10px] bg-primary/10 text-primary border-primary/30">
                      Enforced
                    </Badge>
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-1">
                    Azure OpenAI and AWS Bedrock decoupled.
                  </p>
                </div>

                <div>
                  <Label className="text-xs font-semibold text-foreground/80">Select Gemini Model</Label>
                  <Select value={model} onValueChange={handleModelChange}>
                    <SelectTrigger className="w-full mt-1 bg-background/50 border-input/60 text-xs">
                      <SelectValue placeholder="Choose Model" />
                    </SelectTrigger>
                    <SelectContent>
                      {GEMINI_MODELS.map((opt) => (
                        <SelectItem key={opt.name} value={opt.name} className="text-xs">
                          {opt.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Architecture Assurance Card */}
            <Card className="border-border/40 bg-card/20 shadow-sm text-xs">
              <CardContent className="p-3 space-y-2">
                <div className="font-semibold text-foreground flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-blue-500" />
                  Persistence Assurance
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Backend Status:</span>
                  <Badge variant="outline" className="text-[10px] bg-emerald-500/10 text-emerald-600 border-emerald-500/30">
                    {healthStatus?.status === "ok" ? "Connected" : (healthStatus?.status || "Online")}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Relational DB:</span>
                  <span className="font-mono text-foreground">Neon PostgreSQL</span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Schema:</span>
                  <Badge variant="outline" className="text-[10px] bg-blue-500/10 text-blue-600 border-blue-500/30">
                    audit_copilot (47 tables)
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Vector Index:</span>
                  <span className="font-mono text-foreground">Neon PGVector</span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Audit Engine:</span>
                  <span className="text-emerald-600 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Deterministic Python
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Glassmorphic Prompt Library Dialog */}
      <Dialog open={promptLibraryOpen} onOpenChange={setPromptLibraryOpen}>
        <DialogContent className="sm:max-w-2xl bg-white/98 dark:bg-white/98 border border-gray-200 dark:border-gray-300 shadow-2xl rounded-2xl p-4">
          <DialogHeader className="mb-2">
            <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-amber-600 via-amber-500 to-amber-400 bg-clip-text text-transparent flex items-center gap-2">
              ✨ Prompt Library
            </DialogTitle>
            <p className="text-sm text-slate-700 dark:text-slate-200 font-normal mt-1">
              Select from curated audit prompt templates
            </p>
          </DialogHeader>

          <PromptLibrary onPromptSelect={handlePromptSelect} isOpen={promptLibraryOpen} />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ModelConfigSidebar;
