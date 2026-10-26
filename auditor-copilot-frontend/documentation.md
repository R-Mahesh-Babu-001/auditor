# AMY - Enterprise Auditor Copilot Documentation

## 1. Project Overview

AMY is an Enterprise Auditor Copilot designed to assist auditors with various tasks through an AI-powered interface. It aims to streamline auditing processes such as digital audits, invoice generation, and purchase order (PO) reconciliation.

**Business & Technical Goals:**
- enhance auditor productivity through AI assistance.
- Provide tools for generating and reconciling financial documents.
- Visualize complex data and flows (SOPs, digital audits).
- Ensure secure and efficient handling of sensitive audit data.

**Target Users:**
- Enterprise Auditors
- Financial Analysts
- Compliance Officers

**Key Problems Solved:**
- Manual and time-consuming reconciliation processes.
- Complexity in visualizing standard operating procedures (SOPs).
- Need for quick access to audit-related information via chat.

## 2. Tech Stack

**Frontend Framework & Build Tool:**
- **React:** v19.0.0
- **Vite:** v6.2.0 (using SWC for fast refresh)

**Languages:**
- JavaScript (ES6+)
- HTML5 / CSS3

**Styling:**
- **Tailwind CSS:** v4.0.12
- **Shadcn UI:** Reusable component library based on Radix UI.
- **Radix UI:** Headless UI primitives for accessibility.
- **Lucide React:** Icon library.

**State Management:**
- **Redux:** Global state management (redux, react-redux, redux-thunk, @reduxjs/toolkit).

**Data Visualization:**
- **Recharts:** Charting library.
- **React Flow:** Node-based graph visualization.
- **Mermaid:** Diagramming and charting tool.

**File Handling & Processing:**
- **Axios:** HTTP client.
- **jsPDF / jspdf-autotable:** PDF generation.
- **pdf-lib:** PDF modification.
- **Mammoth:** DOCX to HTML conversion.
- **PapaParse:** CSV parsing.
- **XLSX:** Excel file spreadsheet processing.
- **Tesseract.js:** OCR (Optical Character Recognition).

**AI & LLM Integration:**
- **@datastax/langflow-client:** Client for Langflow AI.
- **@langchain/core & @langchain/google-genai:** LangChain integration for LLM capabilities.

**Utilities:**
- **Date-fns:** Date utility library.
- **React Hook Form:** Form validation and handling.
- **Zod:** Schema validation.

## 3. Architecture Overview

The application follows a **feature-based architecture** built with React and Vite.

**High-Level Architecture:**
- **Single Page Application (SPA):** The app runs as a client-side SPA.
- **Component-Based:** UI is decomposed into reusable components found in `components/` and `globalComponents/`.
- **State Management:** Redux is used for managing global application state, including user sessions, chat history, and audit data.
- **Routing:** React Router (`react-router-dom`) handles client-side navigation.

**Data Flow:**
1.  **User Interaction:** Users interact with UI components (e.g., uploading files, sending chat messages).
2.  **Actions:** Interactions trigger Redux actions or direct API calls via custom hooks.
3.  **API Communication:** Axios is used to communicate with the backend (configured via `.env`).
4.  **State Update:** Redux reducers update the store based on API responses or user input.
5.  **UI Update:** Components subscribed to the Redux store re-render with new data.

## 4. Folder & File Structure

```
frontend/
├── .env                    # Environment variables
├── components.json         # Shadcn UI configuration
├── eslint.config.js        # ESLint configuration
├── index.html              # Application entry HTML
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── public/                 # Static assets
└── src/
    ├── assets/             # Images and static resources
    ├── components/         # Feature-specific components
    │   ├── chatInterfaceComponents/
    │   ├── digital-audit/
    │   └── ...
    ├── feat/               # Major feature modules
    │   ├── digital-audit/
    │   └── sop-flowchart/
    ├── globalComponents/   # Reusable global components (Header, Sidebar)
    ├── globalConstants/    # Application-wide constants
    ├── hooks/              # Custom React hooks
    ├── lib/                # Utility functions (utils.js)
    ├── pages/              # Page layout components
    ├── redux/              # Redux setup
    │   ├── actions/
    │   ├── constants/
    │   ├── reducers/
    │   └── store/
    ├── App.jsx             # Main application component
    ├── main.jsx            # React entry point
    └── index.css           # Global styles (Tailwind imports)
```

## 5. Core Modules & Responsibilities

### Chat Interface (`components/chatInterface.jsx`)
- **Responsibility:** Handles the AI chat interaction.
- **Key Components:** `ConversationWindow`, `userInputs`, `StarterSuggestions`.
- **Interactions:** Uses `chatAgent` (backend) to process user queries.

### Digital Audit (`feat/digital-audit/`)
- **Responsibility:** Manages the digital audit workflow.
- **Key Components:** `screen.jsx`, `digitalAuditInterface.jsx`.
- **Interactions:** Fetches and displays audit data, visualizations using Recharts.

### SOP Flowchart (`feat/sop-flowchart/`)
- **Responsibility:** Visualizes Standard Operating Procedures.
- **Key Components:** `flowchart_showcase.jsx`, `screen.jsx`.
- **Interactions:** Uses React Flow/Mermaid to render flowcharts based on SOP data.

### Redux Store (`src/redux/`)
- **Responsibility:** Centralized state management.
- **Key Files:**
    - `store.js`: Configures the Redux store.
    - `*Actions.js`: Define action creators.
    - `*Reducers.js`: Handle state changes.

## 6. API / Interface Documentation

The frontend communicates with a backend service.
**Base URL:** Configured via `VITE_BACKEND_BASE_URL`.

**Key Interactions:**
- **Chat:** Sending messages to the AI agent.
- **Audit Data:** Fetching financial records for audit.
- **File Upload:** Uploading documents for analysis (PDF, Excel).

*(Detailed API endpoints should be documented here as they are discovered or implemented).*

## 7. Configuration & Environment Setup

The application uses a `.env` file for configuration.

**Environment Variables:**
- `VITE_BACKEND_BASE_URL`: Base URL for the backend API (e.g., `http://localhost:8000`).

**Config Files:**
- `vite.config.js`: Configures Vite build, aliases (`@`), and dev server proxy.
- `jsconfig.json`: Configures path aliases for VS Code IntelliSense.
- `components.json`: Configuration for Shadcn UI components.
- `eslint.config.js`: Linting rules.

## 8. Local Development Setup

**Prerequisites:**
- Node.js (v18+ recommended)
- npm or yarn

**Install Steps:**
1.  Clone the repository.
2.  Navigate to the `frontend` directory.
3.  Run `npm install` to install dependencies.

**Run Instructions:**
1.  Ensure the backend server is running (if required).
2.  Run `npm run dev` to start the development server.
3.  Access the app at `http://localhost:3000` (or the port shown in the terminal).

**Build & Test:**
- Build for production: `npm run build`
- Preview build: `npm run preview`
- Lint code: `npm run lint`

## 9. Deployment & Runtime Behavior

**Deployment Model:**
- Static site hosting (e.g., Vercel, Netlify, AWS S3 + CloudFront).
- The `dist/` folder generated by `npm run build` contains the deployable assets.

**Runtime Flow:**
1.  App loads `index.html`.
2.  React mounts `main.jsx`.
3.  `App.jsx` sets up the Router and Redux Provider.
4.  User navigates to pages which load specific features.

## 10. Error Handling & Logging

- **Error Handling:** Currently managed via standard `try-catch` blocks in async functions and hooks.
- **Logging:** Console logging is used for development debugging.
- **Monitoring:** No specific monitoring hooks integrated yet.

## 11. Security Considerations

- **API Keys:** Stored in `.env`. **Do not commit `.env` to version control.**
- **Data Protection:** Sensitive audit data should be handled securely. Ensure backend endpoints use HTTPS.
- **Secure Storage:** `react-secure-storage` is used for securely storing local data (likely encryption of localStorage).

## 12. Future Improvements & Technical Debt

- **Type Safety:** Migrate to TypeScript for better type safety and maintainability.
- **Testing:** Add unit tests (Jest/Vitest) and integration tests (Playwright/Cypress).
- **Error Boundaries:** Implement React Error Boundaries for graceful UI failure handling.
- **Performance:** Optimize bundle size and implement lazy loading for heavy feature modules.
