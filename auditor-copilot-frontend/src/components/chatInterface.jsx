
// ChatInterface.jsx
// Main chat UI for a specific action/use case, manages messages, user input, and starter suggestions.
import { useState, useEffect } from "react"
import ConversationWindow from "./chatInterfaceComponents/ConversationWindow"
import UserInputs from "./chatInterfaceComponents/userInputs.jsx"
import StarterSuggestions from "./chatInterfaceComponents/StarterSuggestions"
import { useDispatch, useSelector } from "react-redux"
import { setAction } from "../redux/actions/actionActions"
import { starterSuggestionsArray } from "../globalConstants/useCaseConstants"

/**
 * ChatInterface Component
 * 
 * This component manages the chat interface for a specific action/use case.
 * It handles displaying messages, user input, and starter suggestions.
 * 
 * @param {Object} props - Component props
 * @param {Function} props.setConversation - Function to update the parent's conversation state
 * @param {string} props.action - The current action or use case identifier (e.g., 'digital-audit')
 */

/**
 * ChatInterface Component
 * Manages the chat UI for a specific action/use case.
 * Handles message state, user input, and starter suggestions.
 *
 * @param {Object} props
 * @param {Function} props.setConversation - Updates parent conversation state
 * @param {string} props.action - Current action/use case identifier
 */
export default function ChatInterface({setConversation, action}) {
  // Messages state, initialized from localStorage for persistence
  const [messages, setMessages] = useState(() => {
    try {
      const storedMessages = localStorage.getItem(`${action}-chatMessages`)
      return storedMessages ? JSON.parse(storedMessages) : []
    } catch (e) {
      console.error("Failed to parse stored messages from localStorage:", e);
      return [];
    }
  })

  // Redux: get action info from store
  const {actionInfo} = useSelector((state) => state.actionState)
  const dispatch = useDispatch()

  // Effect: persist messages, update Redux, and notify parent on change
  useEffect(() => {
    if(actionInfo){
      // Optionally handle action info changes (e.g., update suggestions)
    }
    localStorage.setItem(`${action}-chatMessages`, JSON.stringify(messages))
    if(action){
      dispatch(setAction(action))
    }
    setConversation(messages)
  }, [messages])

  // Effect: monitor messages state (placeholder for future logic)
  useEffect(() => {
  }, [messages, setMessages])

  // Effect: listen for prompt library selections
  useEffect(() => {
    const handlePromptSelect = (event) => {
      const { prompt } = event.detail;
      // Trigger input focus and fill the input value
      const inputEvent = new CustomEvent('promptLibraryInput', { detail: { prompt } });
      window.dispatchEvent(inputEvent);
    };

    window.addEventListener('promptLibrarySelect', handlePromptSelect);
    return () => window.removeEventListener('promptLibrarySelect', handlePromptSelect);
  }, []);

  return (
    messages.length > 0 ? (
      // Render chat interface with conversation window and user input
      <div className="flex flex-col min-h-[78vh] h-auto">
        <div className="flex-1 h-full overflow-y-auto mb-1 space-top-4">
          <ConversationWindow messages={messages} setMessages={setMessages} />
        </div>
        <div className="flex-shrink-0">
          <UserInputs showSuggestions={true} message={messages} messages={messages} setMessages={setMessages} action={action} />
        </div>
      </div>
    ) : (
      // Render starter suggestions if no messages exist
      <div className="flex flex-col min-h-[78vh] h-auto">
        <div className="flex-1 h-full overflow-y-auto mb-1 space-top-4">
            <StarterSuggestions suggestionObjectId={action} message={messages} setMessages={setMessages} />
        </div>
      </div>
    )
  )
}
