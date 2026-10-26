import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "../../srccomponents/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../components/ui/dialog";
import { cn } from "../lib/utils";
import PromptLibrary from "../components/chatInterfaceComponents/PromptLibrary";

const MODEL_PROVIDERS = {
  'gemini gcp': [
    { name: "gemini-3.8-flash", available: true },
    { name: "gemini-4-argon", available: true },
    { name: "gemini-3.5-flash-lite", available: true },
  ],
  'azure openai': [
    { name: "GPT-4o", available: false },
    { name: "GPT-3.5-turbo", available: false },
    { name: "GPT-4o-mini", available: false },
    { name: "gpt-5.2-chat", available: true },
  ],
  'awsbedrock': [
    { name: "Claude 3.7 Sonnet v1", available: true },
    { name: "Claude 3.5 Sonnet", available: true },
    { name: "Claude 3.5 Haiku", available: false },
    { name: "Claude 3 Haiku", available: false },
  ],
};

const DEFAULT_PROVIDER = "gemini gcp";
const DEFAULT_MODEL = "gemini-3.8-flash";

const ModelConfigSidebar = ({ setModel, setProvider }) => {
  const [collapsed, setCollapsed] = useState(true);
  const [provider, setLocalProvider] = useState(DEFAULT_PROVIDER);
  const [model, setLocalModel] = useState(DEFAULT_MODEL);
  const [promptLibraryOpen, setPromptLibraryOpen] = useState(false);

  useEffect(() => {
    // Load from localStorage if available, otherwise use defaults
    const savedProvider = localStorage.getItem("provider") || DEFAULT_PROVIDER;
    const savedModel = localStorage.getItem("model") || DEFAULT_MODEL;

    setLocalProvider(savedProvider);
    setProvider(savedProvider);

    setLocalModel(savedModel);
    setModel(savedModel);
  }, [setProvider, setModel]);

  const handleProviderChange = (value) => {
    setLocalProvider(value);
    setProvider(value);

    // Set default model based on provider - pick first available model
    // const availableModels = MODEL_PROVIDERS[value].filter(model => model.available);
    // const defaultModel = availableModels.length > 0 ? availableModels[0].name : "";

    const models = MODEL_PROVIDERS[value] || [];
    const availableModels = models.filter(model => model.available);
    const defaultModel = availableModels.length > 0 ? availableModels[0].name : "";

    setLocalModel(defaultModel);
    setModel(defaultModel);

    localStorage.setItem("provider", value);
    localStorage.setItem("model", defaultModel);
  };

  const handleModelChange = (value) => {
    setLocalModel(value);
    setModel(value);
    localStorage.setItem("model", value);
  };

  useEffect(() => {
    if (!localStorage.getItem("model")) {
      localStorage.setItem("model", DEFAULT_MODEL)
    }
    if (!localStorage.getItem("provider")) {
      localStorage.setItem("provider", DEFAULT_PROVIDER)
    }
  })

  const handlePromptSelect = (prompt) => {
    // Dispatch a custom event that the ChatInterface can listen to
    window.dispatchEvent(new CustomEvent('promptLibrarySelect', { detail: { prompt } }));
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
          {/* Button on the left if collapsed?? No, usually toggles. */}
          {/* If collapsed, show button centered? */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="shrink-0 hover:bg-primary/10 hover:text-primary transition-colors rounded-full"
          >
            {collapsed ? (
              <ChevronLeft className="w-5 h-5" />
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </Button>
          {!collapsed && (
            <p className="text-sm text-foreground my-2 ml-2 font-semibold">
              Model Configuration
            </p>
          )}
        </div>

        {/* Prompt Library Button */}
        <div className="mb-6">
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
        <Card className="border-border/40 bg-card/40 shadow-sm">
          <CardContent className="p-4 space-y-4">
            <div>
              <Label className="text-sm font-semibold text-foreground/80">Select Model Provider</Label>
              <Select value={provider} onValueChange={handleProviderChange}>
                <SelectTrigger className="w-full mt-1 bg-background/40 border-input/40">
                  <SelectValue placeholder="Choose Provider" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gemini gcp">Gemini (GCP)</SelectItem>
                  <SelectItem value="azure openai">Azure OpenAI</SelectItem>
                  <SelectItem value="awsbedrock">AWS Bedrock</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {provider && MODEL_PROVIDERS[provider] && (
              <div>
                <Label className="text-sm font-semibold text-foreground/80">Select Model</Label>
                <Select value={model} onValueChange={handleModelChange}>
                  <SelectTrigger className="w-full mt-1 bg-background/50 border-input/60">
                    <SelectValue placeholder="Choose Model" />
                  </SelectTrigger>
                  <SelectContent>
                    {(MODEL_PROVIDERS[provider] || []).map((modelOption) => (
                      <SelectItem
                        key={modelOption.name}
                        value={modelOption.name}
                        disabled={!modelOption.available}
                      >
                        {modelOption.name}
                        {!modelOption.available && " (unavailable)"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </CardContent>
        </Card>
      )}
      </div>

      {/* Glassmorphic Prompt Library Dialog with whitish tint */}
      <Dialog open={promptLibraryOpen} onOpenChange={setPromptLibraryOpen}>
        <DialogContent className="sm:max-w-2xl bg-white/98 dark:bg-white/98 border border-gray-200 dark:border-gray-300 shadow-2xl rounded-2xl p-4">
            <DialogHeader className="mb-2">
              <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-amber-600 via-amber-500 to-amber-400 dark:from-amber-300 dark:via-amber-200 dark:to-amber-100 bg-clip-text text-transparent flex items-center gap-2">
                ✨ Prompt Library
              </DialogTitle>
              <p className="text-sm text-slate-700 dark:text-slate-200 font-normal mt-1">Select from curated prompt templates</p>
            </DialogHeader>

          <PromptLibrary 
            onPromptSelect={handlePromptSelect}
            isOpen={promptLibraryOpen}
          />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ModelConfigSidebar;