import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { useEffect, useState } from "react";
import UserInputs from "./userInputs";
import { starterSuggestionsArray } from "../../globalConstants/useCaseConstants";

const StarterSuggestions = ({ suggestionObjectId, messages, setMessages }) => {
    const [inputValue, setInputValue] = useState("")
    const [suggestionsObject, setSuggestionsObject] = useState([])

    const [selectedSuggestion, setSelectedSuggestion] = useState(null);

    const handlePromptClick = (prompt) => {
        setInputValue(prompt)
    };

    useEffect(() => {
       suggestionObjectId && setSuggestionsObject(starterSuggestionsArray.find(item => item.id === suggestionObjectId))

    }, [inputValue, suggestionObjectId])

    return (
        <div className="flex flex-col items-center justify-center px-4 space-y-6 text-center py-10 w-full min-h-[60vh] animate-in fade-in duration-500">
            <div className="flex flex-col items-center justify-center text-center w-full max-w-4xl">
                <h2 className="text-4xl font-bold tracking-tight text-foreground bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text">
                    {suggestionsObject?.heroMessage ? suggestionsObject?.heroMessage : "How can I assist with your audit needs today?"}
                </h2>
                <div style={{ minWidth: '600px', marginTop: 30, marginBottom: 40 }} className="relative z-10">
                    <UserInputs promptInputValue={inputValue} setMessages={setMessages} />
                </div>
                <div>
                    {/* <p style={{ fontSize: '20px', marginBottom: '20px' }}>Or choose from the options below...</p> */}
                    <p className="text-lg text-muted-foreground mb-5 font-medium">{suggestionsObject?.promptOptionsMessage && suggestionsObject?.promptOptionsMessage 
                    // : "Or choose from the options below..."
                    }</p>
                </div>

                <div className="flex flex-wrap justify-center gap-3">
                    {suggestionsObject?.topics?.map((suggestion) => (
                        <Badge
                            key={suggestion.label}
                            className={`${suggestion.color} px-5 py-2.5 rounded-full text-sm font-semibold cursor-pointer transition-all duration-300 hover:scale-105 shadow-sm hover:shadow-lg border border-white/20 backdrop-blur-sm ${suggestion.label === selectedSuggestion ? 'ring-2 ring-offset-2 ring-offset-background ring-primary scale-105 shadow-lg' : 'hover:-translate-y-0.5'}`}
                            onClick={() => setSelectedSuggestion(suggestion.label === selectedSuggestion ? null : suggestion.label)}
                        >
                            {suggestion.label}
                        </Badge>
                    ))}
                </div>
                {selectedSuggestion && (
                    <div className="mt-8 w-full max-w-2xl bg-white/60 dark:bg-slate-900/60 backdrop-blur-xl shadow-xl rounded-2xl p-6 border border-white/20 dark:border-white/10 animate-in zoom-in-95 duration-300">
                        <h3 className="text-xl font-semibold text-foreground mb-4 flex items-center justify-center gap-2">
                            Select a prompt for <span className="text-primary font-bold">{selectedSuggestion}</span>
                        </h3>
                        <div className="grid gap-3">
                            {suggestionsObject?.topics?.find(s => s.label === selectedSuggestion).prompts.map((prompt, index) => (
                                <Button
                                    key={index}
                                    variant="ghost"
                                    className="w-full justify-start text-left h-auto p-4 rounded-xl text-foreground/80 hover:text-primary hover:bg-primary/5 border border-transparent hover:border-primary/10 transition-all duration-200"
                                    onClick={() => handlePromptClick(prompt)}
                                >
                                    <span className="font-medium whitespace-normal leading-relaxed">{prompt}</span>
                                </Button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
            <p className="absolute bottom-4 text-xs text-muted-foreground/60 font-medium">
                <span className="font-semibold text-foreground/80">AMY</span> could make mistakes. Please verify important information.
            </p>
        </div>
    );
};

export default StarterSuggestions;
