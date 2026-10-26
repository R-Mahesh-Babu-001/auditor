import { useEffect, useState } from "react";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { starterSuggestionsArray } from "../../globalConstants/useCaseConstants";

const PromptLibrary = ({ onPromptSelect, isOpen = false }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);

  // Reset selections when dialog closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedCategory(null);
      setSelectedTopic(null);
    }
  }, [isOpen]);

  const handlePromptClick = (prompt) => {
    onPromptSelect(prompt);
    setSelectedCategory(null);
    setSelectedTopic(null);
  };

  const resetSelections = () => {
    setSelectedTopic(null);
  };

  const getCurrentCategory = () => {
    return starterSuggestionsArray.find(category => category.id === selectedCategory);
  };

  const getCurrentTopic = () => {
    const category = getCurrentCategory();
    if (!category || !selectedTopic) return null;
    return category.topics.find(topic => topic.label === selectedTopic);
  };

  return (
    <div className="mt-2 space-y-3 text-slate-900">
      {/* Category Selection */}
      {!selectedCategory && (
        <div className="space-y-4 animate-in fade-in duration-300">
          <div className="text-center text-slate-900">
            <p className="text-sm font-medium">Choose a category to get started</p>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {starterSuggestionsArray.map((category) => (
              <Badge
                key={category.id}
                className={`${category.color} px-4 py-2 rounded-full shadow-sm font-medium cursor-pointer transition-all hover:scale-105 hover:shadow-md border border-gray-200 bg-white/50`}
                onClick={() => setSelectedCategory(category.id)}
              >
                {category.label}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Selected Category View */}
      {selectedCategory && !selectedTopic && (
          <div className="space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">
              {getCurrentCategory()?.label}
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedCategory(null)}
              className="text-sm text-slate-700 hover:text-slate-900 hover:bg-gray-100 transition-colors"
            >
              ← Back
            </Button>
          </div>

          <div className="text-center text-slate-700 p-3 bg-white rounded-lg border border-gray-100">
            <p className="text-sm leading-relaxed">{getCurrentCategory()?.heroMessage}</p>
          </div>

          <div className="flex flex-wrap justify-center gap-3">
            {getCurrentCategory()?.topics.map((topic) => (
              <Badge
                key={topic.label}
                className={`${topic.color} px-4 py-2 rounded-full shadow-sm font-medium cursor-pointer transition-all hover:scale-105 hover:shadow-md border border-gray-200 bg-white/50`}
                onClick={() => setSelectedTopic(topic.label)}
              >
                {topic.label}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Topic Prompts View */}
      {selectedCategory && selectedTopic && (
        <div className="space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${getCurrentTopic()?.color}`}></span>
                {selectedTopic}
              </h3>
              <p className="text-sm text-slate-600">{getCurrentCategory()?.label}</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={resetSelections}
              className="text-sm text-slate-700 hover:text-slate-900 hover:bg-gray-100 transition-colors"
            >
              ← Back
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {getCurrentTopic()?.prompts.map((prompt, index) => (
              <Button
                key={index}
                variant="outline"
                className="w-full text-left p-3 justify-start rounded-lg text-slate-800 hover:text-slate-900 bg-white border border-gray-200 hover:bg-gray-50 focus:ring-2 focus:ring-slate-200 focus:outline-none transition duration-300"
                onClick={() => handlePromptClick(prompt)}
              >
                <span className="font-medium whitespace-normal text-sm leading-relaxed">{prompt}</span>
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PromptLibrary;
