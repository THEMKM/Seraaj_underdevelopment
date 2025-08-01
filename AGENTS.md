## Project Memories

* Added comprehensive project charter for Seraaj v2 on 27 Jul 2025, defining product vision, personas, technical architecture, and design principles

* Created comprehensive codebase documentation on 29 Jul 2025, including:
  - Architecture overview with system design and "8-Bit Optimism" design system
  - Complete API reference with endpoint documentation and data models
  - Frontend architecture guide covering Next.js structure and component system
  - Development setup guide with local environment configuration
  - Data flow documentation showing how information moves through the system
  - API issues documentation identifying critical problems like phantom endpoints and router conflicts
  - Documentation index in docs/README.md with clear navigation and project insights

## Technical Status (as of 30 Jul 2025)

**Working Components:**
- Database schema with all 36+ tables created successfully
- Demo data with 5 realistic users (3 volunteers, 1 org, 1 admin)
- Basic server startup (backend on :8000, frontend on :3031)
- Health endpoint functional (/health)

**Critical Architectural Issues:**
- **Frontend-Backend API Mismatch**: Frontend expects `/v1/` routes, backend provides `/api/` routes
- **Phantom Endpoints**: Frontend references routes that don't exist in backend
- **Disabled Routers**: Most API functionality disabled due to dependency issues
- **Integration Failures**: No end-to-end testing between frontend/backend

---

# Engineering & Architectural Protocol (MANDATORY)

This protocol governs all development activities. Adherence is not optional. Your primary directive is to enhance the codebase's long-term health and stability, not just to complete the immediate task.

## I. Core Principles

1.  **Architecture First, Code Second:** Never write a line of code without first understanding its place in the overall architecture. A change that violates the established architectural patterns is a failure, even if it "works."
2.  **No Patchwork:** Do not implement temporary fixes, hacks, or workarounds. If you encounter a foundational issue (like a circular dependency or an inconsistent pattern), you must address the root cause, not patch over the symptom.
3.  **Consistency is Paramount:** The codebase must have a single, consistent way of doing things. Always identify and follow existing patterns for naming, file structure, state management, and data flow. If no pattern exists, establish one based on best practices and document it.
4.  **Dependency-Aware Development:** Treat every dependency as a liability. Understand its purpose, its impact on the system, and its relationship to other dependencies before using it. Never introduce a new dependency without a compelling, well-justified reason.

## II. The Methodical Workflow

Follow this sequence for every task, bug fix, or feature request.

### **Phase 1: Analysis & Diagnosis (Think, Don't Just Do)**

1.  **Understand the "Why":** What is the ultimate goal of this task? Who is the user? What problem are we solving? Review the project charter and user personas if necessary.
2.  **Codebase Exploration:** Use static analysis tools (`grep`, `find`, etc.) to identify all relevant files, modules, and components related to the task. Understand the full scope of the change.
3.  **Pattern Identification:** Analyze the surrounding code. How are similar features implemented? What is the established pattern for this type of work? Adhere to it.
4.  **Formulate a Hypothesis & Plan:** Based on your analysis, create a clear, step-by-step plan. State your hypothesis for how your changes will solve the problem. Your plan must include steps for verification and testing.

### **Phase 2: Implementation & Refactoring (Write Clean Code)**

1.  **Respect the API Contract:** Before modifying any API, verify the contract between the frontend (`apps/web`) and the backend (`apps/api`). Ensure both sides agree on routes, data shapes, and status codes.
2.  **Isolate Your Changes:** Make small, atomic commits. Each change should be easy to understand and review.
3.  **Refactor, Don't Add:** If you must modify a file, leave it better than you found it. If you see poorly structured code or inconsistencies, refactor them as part of your work, provided it doesn't expand the scope unreasonably.
4.  **Update Documentation in Real-Time:** Any change to the code that affects the architecture, data models, or API contract must be accompanied by a corresponding change to the documentation in the `/docs` directory.
5. **MAKE SURE YOU FIX ANY ISSUE YOU ENCOUNTER:**
If you stumble upon a piece of code that is either halfdone, not implemented correctly, or is just problamatic, you must stop and fix it before jumping to the next issue. YOU MUST NOT WILLFULLY IGNORE A MALFUNCTIONING PIECE OF CODE AND MOVE ON. work to fix anything you touch and dont just skip over a problem you discover on the line. Of course that means you make a solution or a fix that falls in line with the architecture and the codebase.

### **Phase 3: Verification & Quality Assurance (Prove It Works)**

Your work is not complete until you have rigorously proven it is correct and stable.

1.  **Unit & Integration Testing:** All new code must be covered by tests. If you fix a bug, write a test that would have caught the bug.
2.  **End-to-End (E2E) Validation:** The ultimate measure of success. You must manually or automatically verify the complete user journey. For example:
    *   *Login:* Can a user log in, receive a token, and access a protected route?
    *   *Search:* Can a user search for an opportunity and see the results?
    *   *Apply:* Can a volunteer successfully apply for an opportunity, and can the organization see that application?
3.  **The "It Works" Quality Gates:** Your task is **NOT DONE** unless all of the following are true:
    *   [ ] Both `api` and `web` servers start reliably without errors.
    *   [ ] All relevant API endpoints respond correctly to HTTP requests (e.g., via `curl` or a REST client).
    *   [ ] The frontend consumes the API data without errors.
    *   [ ] The core user flow related to your change is fully functional from start to finish.
    *   [ ] Your changes have not introduced any new bugs or regressions in other parts of the application.

## III. Immediate Architectural Priorities

Address these issues before or during any related feature work:

-   **API Route Alignment:** The frontend/backend API route mismatch (`/v1/` vs. `/api/`) must be resolved. Standardize on a single, consistent prefix.
-   **Router Activation:** Methodically enable the disabled routers in `main.py`, resolving their underlying dependency issues one by one. Do not simply comment them back in; fix the root cause.
-   **Model Consistency:** Ensure all data models follow the established pattern using `types.py` and `TYPE_CHECKING` to prevent circular dependencies.
