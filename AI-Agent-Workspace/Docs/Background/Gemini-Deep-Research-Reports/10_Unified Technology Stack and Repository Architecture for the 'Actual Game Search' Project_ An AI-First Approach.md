## **User Prompt**

\- In 2023 I built a semantic game search engine (attachments: "Building Semantic Game Search\*.md")

\- The costs were too high to sustain the project

\- In September 2025 I began exploring ways to revitalize the project with modern ergonomics and cost improvements

\- AI-driven development work has been underway for building this new iteration: "Actual Game Search"/\`actualgamesearch.com\`.

\- Additional Gemini Deep Research reports were commissioned after reading an article this morning (9/6/2025) that claimed there were hard upper limits to semantic search document counts (06\_\*.md, 07\_\*.md, and 08\_\*.md, 09\_\*.md).

\- Our overall vision has shifted a bit throughout the reports but the user intentions remain largely the same

For our tenth deep research report, I want you to research what the best way to orient our repository would be \*\*for Github Copilot Agent Mode-driven development in VS Code\*\*. I will tell you right now that I already use, and expect to continue using:

\- Context7 MCP server for documentation

\- python notebooks and all LLM tools associated with them to allow robust iterative exploration of solutions

\- A \`copilot-instructions.md\` doc to always keep the AI agent grounded

\- GPT 5 as the LLM driving (I already have this setup and have been doing so thus far, just an FYI; don't sweat the GPT 5 context window since Github Copilot cuts off at 96k tokens and autosummarizes, continuing the conversation from a clean context window hydrated only with the latest user prompt and the summary of the conversation history)

I may or may not switch back and forth between using my local bioinformatics rig and Github Codespaces, but the VS Code experience should be largely the same. Let's get this architected wisely and built to win.

# ---

## **Gemini Deep Research**

This is the current plan. What changes do you want to make?

(1) Investigate the specific context-gathering mechanisms of GitHub Copilot Agent Mode in VS Code to understand how it interprets a project's structure, documentation, and code. (2) Research and propose an optimal Python project directory structure that is AI-friendly. This should include dedicated folders for source code, tests, experimental notebooks, and AI-specific instructions. (3) Formulate a comprehensive 'AI grounding' strategy. Detail the ideal content for a root README.md (project vision, architecture), the `copilot-instructions.md` (constraints, style guides), and the use of Architectural Decision Records (ADRs) to provide historical context. (4) Analyze best practices for in-code documentation that is highly effective for LLM comprehension, including Python docstring conventions (e.g., Google style), comprehensive type hinting, and strategies for linking to the external Context7 MCP documentation server. (5) Define a structured approach for managing the `notebooks/` directory. Propose a system for organizing notebooks by function (e.g., data exploration, prototyping, evaluation) and documenting experimental results for future AI context. (6) Research and outline a configuration plan to ensure environment consistency between the local machine and GitHub Codespaces. This includes defining dependencies in `pyproject.toml`, setting up a `.devcontainer/devcontainer.json` for Codespaces, and using `.vscode/settings.json` to enforce code formatting and linting standards. (7) Explore methodologies for defining and managing development tasks in a format optimized for the Copilot Agent, such as using structured markdown files in a dedicated `tasks/` directory that can be used as detailed prompts. (8) Synthesize all findings into a final architectural recommendation, presenting a clear repository layout and a summary of best practices for maintaining an AI-optimized development workflow for the 'Actual Game Search' project.

# ---

## **User Prompt**

Your current plan is a solid start, but we also very much care about you investing cognitive effort into unifying the stack itself. Once you know what Github Copilot Agent Mode (driven by GPT-5) is good at and bad at, you'll be informed enough to make the remaining tweaks to the architecture proposed in the last few Deep Research reports, potentially resolving or simply acknowledging the competing concerns of the optimal architectural stack versus the optimal stack \*\*for Github Copilot to perform exquisitely well at developing\*\*, with a gentle bias toward favoring the architecturally "right" option wherever possible.

What I am asking of you is to:

\- take the knowledge of these past research reports and Deep Think responses,

\-inform yourself of how Github Copilot really works, and

\- propose a structure of our repository that is in line with us being able to build ultra-low-cost, astonishingly-high-quality hybrid semantic/fulltext search for products (games) via product descriptions and reviews, all with customizable ranking setups (likely even for the end user making the search, reranking their own results in real-time by increasing and decreasing slider values for weights of the various ranking components)

# ---

## **Gemini Deep Research**

This is the current plan. What changes do you want to make?

(1) Investigate the context-gathering mechanisms, strengths, and weaknesses of GitHub Copilot Agent Mode in VS Code, particularly when driven by GPT-5, to establish a baseline for its development capabilities. (2) Based on the Copilot analysis, review architectural proposals from previous research reports for the hybrid semantic/full-text search engine. Critically evaluate the trade-offs between the architecturally ideal stack (for low-cost, high-quality search) and a stack optimized for Copilot's performance. (3) Propose a unified technology stack and a corresponding AI-friendly Python project directory structure that resolves these competing concerns, with a gentle bias toward the architecturally superior option. (4) Formulate a comprehensive 'AI grounding' strategy to guide Copilot. Detail the content for a root README.md (project vision, unified architecture), `copilot-instructions.md` (constraints, style guides), and Architectural Decision Records (ADRs) to document key choices and trade-offs. (5) Analyze best practices for in-code documentation (e.g., Google-style docstrings, type hinting) and linking to the external Context7 MCP server to maximize LLM comprehension within the chosen stack. (6) Define a structured approach for managing the `notebooks/` directory for prototyping and evaluating components of the hybrid search and customizable ranking system. (7) Research and outline a configuration plan to ensure environment consistency (`pyproject.toml`, `.devcontainer/devcontainer.json`) between the local machine and GitHub Codespaces. (8) Synthesize all findings into a final architectural recommendation. This report will present the unified stack, the optimal repository layout, and a workflow guide that balances architectural integrity with maximizing GitHub Copilot's development performance for the 'Actual Game Search' project.

# ---

## **User Prompt**

\> (5) Analyze best practices for in-code documentation (e.g., Google-style docstrings, type hinting) and linking to the external Context7 MCP server to maximize LLM comprehension within the chosen stack.

Not necessary; Context7 exists to serve documentation primarily for project dependencies. Other mechanisms are useful for nudging Github Copilot to comment in specific ways, but I've seen enough churn in "best practice" for this that I'm willing to wait until the dust settles and a winning strategy actually emerges. Don't sweat this part.

\> (6) Define a structured approach for managing the notebooks/ directory for prototyping and evaluating components of the hybrid search and customizable ranking system.

Nice to have but I'd prefer deeper research and higher effort investment into quality on the other points (if forced to choose)

\> (7) Research and outline a configuration plan to ensure environment consistency (pyproject.toml, .devcontainer/devcontainer.json) between the local machine and GitHub Codespaces.

One of the earlier deep research reports suggested some way of managing the python packages smoothly; this is another nice-to-have but don't sweat it if there is a zero-sum competition for attention between this and the first 4 items.

\> (8) Synthesize all findings into a final architectural recommendation. This report will present the unified stack, the optimal repository layout, and a workflow guide that balances architectural integrity with maximizing GitHub Copilot's development performance for the 'Actual Game Search' project.

Make sure that you are heavily leaning on and checking against the materials I gave you as input attachments. They are far far far richer than any internet page and represent dozens of hours of work and hundreds of websites already searched.

# ---

## **Gemini Deep Research**

Here's the updated plan. Feel free to change it or add more.

AI-Driven Project Architecture Refinement

Research Websites and Files

(1) Investigate the context-gathering mechanisms, strengths, and weaknesses of GitHub Copilot Agent Mode in VS Code, particularly when driven by GPT-5, to establish a baseline for its development capabilities. (2) Based on the Copilot analysis, conduct a deep review of the architectural proposals within the provided research attachments. Critically evaluate the trade-offs between the architecturally ideal stack (for low-cost, high-quality search) and a stack optimized for Copilot's performance. (3) Propose a unified technology stack and a corresponding AI-friendly Python project directory structure that resolves these competing concerns, with a gentle bias toward the architecturally superior option. (4) Formulate a comprehensive 'AI grounding' strategy to guide Copilot. Detail the content for a root README.md (project vision, unified architecture), \`copilot-instructions.md\` (constraints, style guides), and Architectural Decision Records (ADRs) to document key choices and trade-offs. (5) Synthesize all findings into a final architectural recommendation, heavily leaning on and cross-referencing the provided input attachments. This report will present the unified stack, the optimal repository layout, and a workflow guide that balances architectural integrity with maximizing GitHub Copilot's development performance for the 'Actual Game Search' project.

Analyze Results

Create Report

# ---

# **Report 10**

# **Unified Technology Stack and Repository Architecture for the 'Actual Game Search' Project: An AI-First Approach**

## **The AI-First Development Paradigm: A Strategic Analysis of GitHub Copilot Agent with GPT-5**

The advent of large language models (LLMs) has precipitated a fundamental shift in software development methodologies. The introduction of GitHub Copilot Agent, particularly when powered by a frontier model such as GPT-5, represents a transition from AI as a tool for code completion to AI as an active, autonomous participant in the development lifecycle. This section provides a strategic analysis of this new paradigm, deconstructing the agent's capabilities, cognitive processes, and operational constraints to establish a set of guiding principles that will inform all subsequent architectural and structural decisions for the 'Actual Game Search' project.

### **The Agentic Development Model: From Code Completion to Autonomous Peer**

The distinction between traditional AI-assisted coding and the new agentic model is not one of degree but of kind. Previous iterations of GitHub Copilot functioned primarily as sophisticated autocompletion engines, providing inline suggestions based on local context.1 The agentic model, by contrast, operates as an autonomous peer programmer, capable of executing complex, multi-step tasks based on high-level, natural-language prompts.1

This capability is realized through a persistent, iterative process known as the "agentic loop." Upon receiving a goal, the agent engages in a cycle of planning a multi-step solution, applying code changes across multiple files, running commands or tests to validate its work, and iterating based on the feedback it receives from the development environment.4 This allows it to move beyond simple code generation to tackle complex workflows such as implementing new features, refactoring code, migrating frameworks, or fixing bugs autonomously.3

This agentic functionality manifests in two distinct operational modes:

1. **Interactive IDE Agent Mode:** This is a real-time, synchronous assistant integrated directly into the developer's IDE (such as VS Code or Visual Studio).4 It functions as a "stay-in-the-loop" collaborator, where the developer provides a goal and then steers the agent, providing feedback and approving steps as it works.4 This mode offers an immediate feedback cycle, making it ideal for the core development loop of feature implementation, refactoring, and debugging. For the 'Actual Game Search' project, this interactive mode will be the primary method of AI collaboration.  
2. **Asynchronous Copilot Coding Agent:** This mode operates autonomously in a sandboxed environment powered by GitHub Actions.6 A developer assigns the agent a task, typically via a GitHub issue, and the agent works in the background to create a branch, implement changes, and ultimately submit a pull request for human review.6 This "fire-and-forget" model is best suited for well-defined, non-interactive tasks like addressing technical debt or implementing routine updates.

The strategic viability of this AI-first approach is predicated on the integration of a frontier model like GPT-5. The availability of GPT-5 within GitHub Copilot marks a significant leap in capability, offering substantial improvements in reasoning, decision-making for complex tasks, and the generation of high-quality, maintainable code with minimal prompting.10 This advanced reasoning elevates the agent from a mere executor of commands to a strategic partner capable of understanding and contributing to architectural decisions, a critical factor for the success of this project.12

### **Deconstructing the Agent's "Cognition": Context Gathering and Workspace Understanding**

The efficacy of any AI agent is a direct function of the quality and relevance of the context it can access.2 The GitHub Copilot Agent's "cognitive" process for understanding a project is a sophisticated mechanism for context aggregation and discovery. When a developer issues a prompt, the agent's backend system augments it with a rich contextual payload. This payload includes not only the user's query but also a summarized structure of the workspace (to conserve tokens), machine context such as the operating system, and descriptions of the tools available to the agent.3

Crucially, the agent is not a passive recipient of context; it is an active explorer. It is designed to autonomously determine which files and information are relevant to the task at hand.3 Its exploration process mirrors that of a human developer onboarding to a new project: it begins by reading high-level documentation like

README files to grasp the project's purpose and structure.6 It then performs searches within the codebase for keywords related to the task, reads through the discovered files, and analyzes existing code patterns and conventions to build a mental model of the application.6 While this autonomous discovery is powerful, developers can and should provide explicit guidance by referencing specific files or directories using syntax like

\#file to focus the agent's attention.3

The agent's interaction with the workspace is mediated through a defined set of tools. It functions as an orchestrator, using these tools to execute its plan.4 Standard tools allow it to perform essential actions like reading the contents of a file (

read\_file), running arbitrary commands in the integrated terminal (e.g., to install dependencies or run tests), and applying proposed code edits.3 This toolset is not static; it is extensible via the Model Context Protocol (MCP), which allows third-party services to be integrated as tools.4 This enables advanced workflows, such as using a Playwright MCP server to give the agent control over a web browser for end-to-end testing, including taking and attaching screenshots to a pull request.15

Perhaps the agent's most advanced capability is its self-correction loop. After applying a change or running a command, it actively monitors the output from the development environment. It is designed to detect syntax errors, compiler warnings, build errors, and failing test results.3 Based on this feedback, it autonomously determines a course correction, whether that involves making additional edits, running different commands, or exploring an alternative implementation strategy.4 This iterative refinement process continues until the task is successfully completed, significantly reducing the amount of manual debugging required by the human developer.

### **The Economic Reality: Managing Premium Requests and Rate Limiting**

While the capabilities of the GPT-5 powered agent are transformative, they are not without cost. Agent Mode is designated as a "premium feature" within the GitHub Copilot billing structure, and its usage is metered through a system of "premium requests".16 Each prompt submitted by a user in Agent Mode consumes a base number of these requests, which is then multiplied by the rate of the selected AI model.16 Frontier models like GPT-5 and Claude Sonnet carry a 1x multiplier, meaning they consume premium requests at the base rate. In contrast, models included with paid plans, such as GPT-4.1, have a 0x multiplier and do not deplete the user's premium request allowance.16

This consumption model introduces a significant new constraint that extends beyond budgetary concerns: "fair use" rate-limiting. Real-world user reports indicate that developers engaged in continuous, intensive use of Agent Mode with premium models can exhaust their usage limits within a few hours.18 This is particularly problematic because a single high-level prompt in Agent Mode can trigger numerous backend requests as the agent iterates through its planning and execution loop, rapidly consuming the allowance.8 When the rate limit is hit, the agent ceases to function, critically interrupting the development workflow, often in the middle of complex operations like a large-scale refactoring.18

This economic and practical reality has profound strategic implications. The most powerful models, which are necessary for the most complex tasks, cannot be used indiscriminately without risking productivity-halting interruptions. Therefore, a deliberate and disciplined approach to model selection becomes a required developer skill. The development workflow must be designed to manage this finite resource of "high-compute" AI interaction, balancing the need for the advanced reasoning of premium models against the risk of hitting usage limits.

### **Guiding Principles for an AI-First Architecture**

The preceding analysis of the Copilot Agent's capabilities, cognitive model, and operational constraints yields a set of foundational principles. These principles will serve as the primary criteria against which all architectural and structural decisions for the 'Actual Game Search' project will be evaluated.

* **Principle 1: Maximize Contextual Clarity.** The architecture, repository structure, and all associated artifacts must be designed for maximum simplicity, predictability, and self-documentation. The goal is to reduce the cognitive load on the agent, enabling it to understand the system's structure and intent with minimal ambiguity.  
* **Principle 2: Prioritize a Unified Context.** The agent's operational constraint of being limited to a single repository for any given task is a primary design driver.9 The architecture must therefore favor patterns that co-locate related code within a single version control boundary to enable effective, large-scale, AI-driven modifications.  
* **Principle 3: Engineer the Agent's Environment.** The configuration and guidance provided to the agent are not afterthoughts; they are first-class architectural concerns. Artifacts like copilot-instructions.md, setup scripts, and high-quality documentation must be engineered with the same rigor as the application code itself.  
* **Principle 4: Design for Economic Efficiency.** The development workflow and the architecture itself must account for the economic realities of premium request consumption and rate-limiting. This involves creating team-wide policies for strategic model selection to ensure sustained productivity.

The following table summarizes these key capabilities and constraints, directly linking them to their architectural implications for the project.

**Table 1: Copilot Agent (GPT-5) Capability and Constraint Matrix**

| Capability/Constraint | Description | Supporting Evidence | Architectural Implication |
| :---- | :---- | :---- | :---- |
| Autonomous Task Execution | The agent can autonomously plan and execute multi-step tasks involving code edits, tests, and terminal commands in an iterative loop. | 3 | The project should be structured to support automated testing and have clear, scriptable build processes that the agent can execute. |
| Context Gathering Scope | The agent builds context from the prompt, a summarized workspace structure, and active exploration of files like README.md. | 3 | The repository must contain high-quality, machine-readable documentation (README.md, copilot-instructions.md) that explicitly describes the architecture. |
| Self-Correction Loop | The agent monitors test results, build outputs, and lint errors to autonomously correct its own work. | 3 | A robust, fast, and reliable automated testing suite is non-negotiable. The feedback from tests is a primary input for the agent's iterative process. |
| Tool Extensibility (MCP) | The agent's capabilities can be extended with custom tools via the Model Context Protocol (MCP) to interact with external systems. | 4 | The architecture should be designed with clear APIs and service boundaries that could potentially be exposed to the agent as custom tools for advanced automation. |
| Single-Repository Limitation | The agent can only make changes within the single repository where the task was initiated; it cannot perform cross-repository refactoring. | 9 | The macro-architecture must strongly favor a monolithic or modular monolithic pattern over a microservices architecture to provide a unified context. |
| Premium Request Consumption | Agent Mode usage with premium models (like GPT-5) consumes a finite monthly allowance of premium requests. | 16 | A team-wide policy for strategic model selection is required to conserve premium requests for the most complex tasks, preventing budget overruns. |
| Rate-Limiting Workflow Impact | Intensive use of premium models can trigger "fair use" rate limits, halting the agent and disrupting developer workflow. | 8 | The development process must incorporate a workflow that alternates between premium models for complex initiation and included models for iterative refinement. |

## **Core Architectural Blueprint: Adopting a Modular Monolith for 'Actual Game Search'**

The selection of a macro-architectural pattern is the most consequential decision in a system's design. In an AI-first development context, this decision is driven not only by traditional software engineering trade-offs but also by the principles derived from the capabilities and constraints of the AI development partner. For the 'Actual Game Search' project, an analysis of these factors leads to the unequivocal recommendation of a Modular Monolith architecture. This pattern provides the optimal balance of AI navigability, long-term maintainability, and operational simplicity.

### **The Architectural Trilemma: Monolith vs. Microservices vs. Modular Monolith**

The choice of architecture exists on a spectrum of coupling and deployment strategy. Three primary patterns represent the key points on this spectrum:

* **Traditional Monolith:** This pattern involves a single, large, and often tightly coupled codebase that is deployed as a single artifact. Its primary advantages are simplicity in the early stages of development and the provision of a completely unified context for developers and tools. However, as the system grows, the lack of internal boundaries leads to high coupling, making it difficult to understand, maintain, and scale—a state often referred to as the "big ball of mud".20  
* **Microservices:** This pattern decomposes a system into a collection of small, independent services, each with its own codebase, database, and deployment pipeline. This approach offers high scalability, team autonomy, and technological flexibility. Its principal disadvantage is a massive increase in operational complexity related to deployment, monitoring, and inter-service communication. Critically for this project, it fundamentally violates the single-repository context that GitHub Copilot Agent depends upon, as the agent cannot perform a refactoring that spans multiple repositories.9  
* **Modular Monolith (The Synthesis):** This pattern represents a strategic middle ground. It is a system that is deployed as a single artifact (like a monolith) but is internally structured into a set of well-defined, highly cohesive, and loosely coupled modules.21 Each module represents a distinct business domain and has explicit, enforced boundaries. This architecture combines the operational simplicity and unified development context of the monolith with the separation of concerns and maintainability of microservices.21

### **Justification for the Modular Monolith in an AI-First Context**

The selection of the Modular Monolith is a direct consequence of applying the AI-first principles established in the previous section. It is the only architectural pattern that satisfies all the primary requirements for optimizing the effectiveness of the GitHub Copilot Agent.

The most compelling justification stems from the **Principle of Unified Context**. The agent's inability to operate across multiple repositories is a hard constraint.9 A microservices architecture, by definition, fragments the codebase into many repositories, rendering the agent incapable of performing high-value, system-wide tasks like refactoring a core domain model or implementing a feature that touches multiple services. The Modular Monolith, by containing all code within a single repository, provides the ideal, unified workspace for the agent. This enables it to execute complex, cross-module tasks seamlessly, maximizing its utility as an autonomous collaborator.

Furthermore, the pattern directly addresses the **Principle of Contextual Clarity**. While a traditional monolith also provides a unified context, its lack of internal structure creates a "context pollution" problem. In a large, undifferentiated codebase, the agent's attempts to discover relevant files can be inefficient, potentially exhausting its context window with irrelevant information.24 The Modular Monolith solves this by imposing a clear, domain-driven structure on the codebase. The explicit boundaries between modules—such as

Games, Users, and Search—create a high-level conceptual map of the application. This structure is readily understandable by both humans and the AI agent, allowing the agent to reason about the system at the module level ("refactor the authentication logic within the Users module") before delving into specific files.6 This mirrors the top-down approach a human developer would take and dramatically improves the signal-to-noise ratio of the context the agent processes.

Finally, the design of a Modular Monolith, with its emphasis on explicit contracts between modules (e.g., public APIs or clients) and the avoidance of shared database tables, prevents the high coupling that degrades large systems over time.20 This inherent discipline not only benefits human developers but also creates a more predictable and stable environment for the AI agent, reducing the likelihood of it introducing unintended side effects when modifying one part of the system.

### **Python Implementation of a Modular Monolith with FastAPI**

The 'Actual Game Search' project will implement the Modular Monolith pattern using modern Python frameworks and practices. The logical modules of the architecture will be physically represented as distinct Python packages within the source tree. This approach enforces high cohesion (code related to a single domain is grouped together) and allows for the management of low coupling through Python's import system.20

FastAPI is the ideal web framework for this architecture. Its core feature, the APIRouter, allows developers to define a set of related API endpoints in a self-contained unit.26 This maps perfectly to the modular concept, where each module will have its own

APIRouter defining its public-facing HTTP API. The main application is then composed by importing and including the routers from each module, creating a clean and scalable structure.28 While other frameworks like Django also support this pattern through concepts like "reusable apps," FastAPI's performance, async-first design, and native Pydantic integration make it the superior choice for a modern API-driven application.21

Inter-module communication, a critical aspect of maintaining loose coupling, will be handled through two primary mechanisms. For synchronous, request-response style interactions, one module will import and use a dedicated, versioned "client" class exposed by another module. For asynchronous, event-driven workflows, an in-memory event bus will be used, allowing modules to publish events without having direct knowledge of the subscribers.20 These patterns ensure that all interactions between modules are explicit and contract-based, preventing the kind of implicit, tight coupling that leads to a fragile architecture.

The following table provides a comparative analysis of the architectural patterns against the key decision criteria for this project, illustrating the rationale for selecting the Modular Monolith.

**Table 2: Architectural Pattern Decision Matrix**

| Criterion | Traditional Monolith | Microservices | Modular Monolith | Recommendation for 'Actual Game Search' |
| :---- | :---- | :---- | :---- | :---- |
| **AI Navigability (Context Scope)** | **Excellent.** Provides a single, unified repository for the agent. | **Poor.** Code is fragmented across many repositories, preventing system-wide agent operations. | **Excellent.** Provides a single, unified repository for the agent. | The pattern must support a single repository. |
| **AI Context Clarity** | **Poor.** Lack of internal boundaries leads to context pollution and difficulty in discovering relevant files in large projects. | **Good.** Each service is a small, focused context, but the overall system context is lost. | **Excellent.** Clear, domain-driven module boundaries create a high-level map of the system, focusing the agent's attention. | The pattern must provide clear internal structure. |
| **Deployment Simplicity** | **Excellent.** A single artifact to build, test, and deploy. | **Poor.** Requires complex CI/CD pipelines, service discovery, and orchestration. | **Excellent.** A single artifact to build, test, and deploy. | Simplicity is preferred to reduce operational overhead. |
| **Scalability Path** | **Fair.** Can be scaled vertically or horizontally, but the entire application must be scaled together. | **Excellent.** Individual services can be scaled independently based on load. | **Good.** While deployed as one unit, internal performance can be optimized per module. Can be evolved into microservices if necessary. | The pattern must support future growth. |
| **Team Autonomy** | **Poor.** All teams work on the same tightly coupled codebase, leading to contention. | **Excellent.** Teams can develop, deploy, and iterate on their services independently. | **Good.** Teams can work with a high degree of autonomy within their respective modules, with clear contracts for interaction. | The pattern should enable parallel development. |
| **Overall Recommendation** | **Not Recommended.** Fails on long-term maintainability and AI context clarity. | **Not Recommended.** Fundamentally incompatible with the single-repository constraint of the AI agent. | **Strongly Recommended.** Optimally balances the AI agent's need for a unified context with the engineering need for modularity and maintainability. | **Adopt Modular Monolith.** |

## **The AI-Optimized Repository: A Unified Structure for Human and Machine Cognition**

Having established the Modular Monolith as the macro-architecture, this section defines the concrete, fine-grained repository structure for the 'Actual Game Search' project. This structure is not an arbitrary choice; it is a carefully engineered environment designed to be maximally intelligible to both human developers and the GitHub Copilot Agent. It synthesizes established best practices from the Python 29 and FastAPI 26 ecosystems with the principles of modular design.20 A logical, predictable, and consistent repository layout acts as a form of "passive prompting," providing the AI agent with a clear map of the application that guides its autonomous discovery and modification processes, thereby improving its accuracy and efficiency.

### **Top-Level Directory Structure**

The root of the repository will be organized to clearly separate application code from tests, documentation, and configuration. This separation of concerns is a foundational best practice that enhances clarity for all parties interacting with the codebase.29

* **/src**: This directory will contain the main Python package for the application. Adopting a src layout is a modern standard that cleanly separates the importable source code from other project files, preventing common pathing and packaging issues and ensuring the project is installed in an editable mode correctly.28  
* **/docs**: This directory is the designated location for all human-readable documentation that is not embedded in the code itself. This includes crucial artifacts such as Architectural Decision Records (ADRs), design documents, and extended usage guides.20 Co-locating documentation with the code in the same repository ensures it is versioned and reviewed alongside the features it describes.  
* **/tests**: This directory will house the entire suite of automated tests. Its internal structure will mirror the structure of the /src directory, making it intuitive to locate the tests corresponding to a specific piece of application code.29  
* **/.github**: This directory is reserved for files specific to the GitHub platform. This includes GitHub Actions workflow files for continuous integration and deployment (CI/CD), as well as the critically important configuration files that engineer the Copilot Agent's environment, such as copilot-instructions.md and copilot-setup-steps.yaml.15  
* **Root Files**: The project root will contain essential configuration files like pyproject.toml (for project metadata and dependency management), README.md (the primary entry point for understanding the project), and .gitignore.

### **Application Structure (/src/actual\_game\_search)**

Inside the src directory, the application itself is structured to reflect the Modular Monolith architecture.

* **/src/actual\_game\_search/core**: This package serves as the foundational layer for the application, containing cross-cutting concerns that are shared by all modules. This includes the database session management, core application settings loaded from the environment, shared security utilities (e.g., password hashing, JWT handling), and the main application entry point (main.py).23 Centralizing these concerns prevents code duplication and provides a single, stable source of truth for infrastructural components.  
* **/src/actual\_game\_search/modules**: This directory is the heart of the Modular Monolith. It will contain a series of sub-packages, where each sub-package represents a distinct business domain and corresponds to a logical module in the architecture. For the 'Actual Game Search' project, initial modules will include games, users, reviews, and search.20 This physical separation enforces the logical boundaries of the architecture.  
* **/src/actual\_game\_search/main.py**: This file is the primary entry point for the FastAPI application. Its role is to initialize the global FastAPI app instance and then to "compose" the full application by importing and including the top-level APIRouter from each of the modules defined in the modules directory.26 This keeps the main entry point lean and focused on application assembly.

### **Anatomy of a Module (/src/actual\_game\_search/modules/games)**

To ensure predictability and reduce cognitive overhead for both humans and the AI agent, every module within the modules directory will adhere to a standardized internal structure. This consistency is paramount for enabling the agent to reliably locate and modify the correct files when given a high-level task.6

* \_\_init\_\_.py: An empty file that designates the directory as a Python package, making its contents importable.26  
* router.py: Contains the module's FastAPI APIRouter. This file defines all the HTTP endpoints related to the module's domain (e.g., endpoints for creating, retrieving, and updating games). It represents the module's public API contract and is the primary integration point for external clients and other modules.28  
* service.py: This file houses the core business logic for the module. The functions or classes in service.py are called by the endpoint handlers in router.py. This crucial separation of concerns ensures that the business logic is decoupled from the transport layer (HTTP), making it more reusable and easier to test in isolation.27  
* schemas.py: Defines all Pydantic models used for data validation, serialization, and documentation within the module. This includes models for request bodies, response bodies, and query parameters. Using explicit schemas ensures data integrity and provides clear, machine-readable contracts for the API.27  
* models.py: Defines the database table models for the module, typically using an ORM like SQLAlchemy. Each module is responsible for its own database tables, and these models are the Python representation of that schema.27  
* exceptions.py: Contains custom exception classes specific to the module's domain (e.g., GameNotFoundError). This allows for more granular error handling.28  
* constants.py: A place for module-specific constants, such as enum values or configuration keys.28  
* client.py (Optional): If a module needs to be consumed by other internal modules, it will expose a clean, versioned client class in this file. This client abstracts away the implementation details of the module and provides a stable, explicit contract for inter-module communication, reinforcing the principle of low coupling.20

The following table provides a detailed breakdown of the proposed repository structure, with explicit justifications for how each element benefits both human developers and the AI agent.

**Table 3: 'Actual Game Search' Proposed Repository Structure**

| Path | Description | Justification (Human & AI Benefit) |
| :---- | :---- | :---- |
| **/** | Project Root | **Human:** Central location for project-wide configuration. **AI:** Starting point for workspace analysis; location of key context files like README.md. |
| /.github/ | GitHub-specific configuration | **Human:** Centralizes CI/CD and platform-specific settings. **AI:** Location for copilot-instructions.md and copilot-setup-steps.yaml, which are critical for configuring the agent's behavior and environment. |
| /docs/ | Project documentation | **Human:** Separates narrative documentation from code for clarity. **AI:** Provides a dedicated location for the agent to find deep contextual information like Architectural Decision Records (ADRs). |
| /src/ | Main application source code | **Human:** Cleanly separates installable code from tests and config, a modern Python best practice. **AI:** Narrows the search space for application logic, preventing the agent from analyzing non-code files. |
| /tests/ | Automated tests | **Human:** Standard location for all tests, mirroring the src structure for easy navigation. **AI:** Provides a predictable location for finding and executing tests to validate its own code changes. |
| /src/actual\_game\_search/ | Main application package | **Human:** The root Python package for the application. **AI:** Defines the primary namespace for the application code. |
| .../core/ | Cross-cutting concerns | **Human:** Centralizes shared logic (DB, config, security), promoting DRY principles. **AI:** Provides a single source of truth for foundational components, ensuring consistency in generated code. |
| .../modules/ | Directory for all business modules | **Human:** The physical representation of the Modular Monolith architecture, organizing the project by business domain. **AI:** Creates a high-level, predictable map of the application's capabilities, enabling it to quickly identify the relevant area for a given task. |
| .../modules/\<module\_name\>/ | A single, self-contained module | **Human:** Encapsulates all code related to one business domain, promoting high cohesion and team autonomy. **AI:** Provides a focused, bounded context for tasks, improving the relevance of its analysis and reducing the risk of unintended side effects. |
| .../\<module\_name\>/router.py | FastAPI APIRouter for the module | **Human:** Defines the module's HTTP API. **AI:** A predictable location for finding and adding new API endpoints. |
| .../\<module\_name\>/service.py | Business logic for the module | **Human:** Separates business logic from the web layer for testability. **AI:** A predictable location for finding and modifying the core logic of a feature. |
| .../\<module\_name\>/schemas.py | Pydantic schemas for the module | **Human:** Defines data contracts for API requests/responses. **AI:** Provides explicit type and structure information, enabling the generation of type-safe, validated code. |
| .../\<module\_name\>/models.py | Database models for the module | **Human:** Defines the module's database schema. **AI:** A predictable location for finding and modifying data persistence logic. |

## **Technology Stack and Hybrid Search Implementation**

This section specifies the concrete technology stack for the 'Actual Game Search' project and provides a detailed architectural plan for its core functionality: a hybrid search system. The selected technologies are modern, performant, and well-suited to the proposed Modular Monolith architecture, while the search implementation is designed to deliver superior relevance by combining the strengths of lexical and semantic search techniques.

### **Core Technology Stack**

The technology stack is chosen to maximize developer productivity, performance, and compatibility with an AI-first workflow.

* **Language:** Python 3.12+ will be used for its rich ecosystem, readability, and strong support for modern AI and web development frameworks.  
* **Web Framework:** FastAPI is the framework of choice due to its high performance, native asynchronous support, automatic interactive documentation, and dependency injection system. Its use of Pydantic for type-hinted data validation aligns perfectly with the goal of creating a clear, explicit codebase that is easily understood by the AI agent.26  
* **Database (Relational):** PostgreSQL will serve as the primary relational database. Its robustness, advanced features, and excellent performance are well-established. The asyncpg driver will be used to enable non-blocking database operations, fully leveraging FastAPI's async capabilities.  
* **ORM:** SQLAlchemy 2.0 will be used as the Object-Relational Mapper. Its modern, async-native API provides a powerful and type-safe way to interact with the PostgreSQL database.  
* **Vector Database:** To power the semantic search component, a dedicated vector database such as Pinecone or Weaviate will be integrated. Alternatively, for simpler use cases, the pgvector extension for PostgreSQL can be utilized to store and query vector embeddings directly within the primary database.  
* **Dependency Management:** uv will be used for dependency management and virtual environment creation. Its exceptional speed significantly improves the development feedback loop compared to traditional tools like pip and venv.33  
* **Testing:** pytest is the standard for testing in the Python ecosystem, chosen for its powerful fixture system, extensive plugin library, and clear, concise syntax.  
* **Linting/Formatting:** Ruff will be used for both linting and formatting. It is an extremely fast, all-in-one tool that replaces multiple older tools (like Flake8, isort, and Black), simplifying the toolchain and providing near-instantaneous feedback to developers and the AI agent.29

### **Architecture of the Hybrid Search Module**

The central feature of the 'Actual Game Search' project is its ability to provide highly relevant search results. This will be achieved through a hybrid search architecture that intelligently combines two distinct search paradigms:

1. **Keyword-based (Lexical) Search:** This traditional method excels at matching exact keywords and phrases. It is fast and effective for queries where the user knows the specific terms they are looking for.  
2. **Vector-based (Semantic) Search:** This modern approach uses machine learning models to convert text into numerical representations (vector embeddings) that capture its meaning. Searching in this vector space allows the system to find results that are conceptually related to the query, even if they do not share the same keywords. This is crucial for understanding user intent.43

By combining these two approaches, the system can deliver results that are both precise (from keyword search) and contextually relevant (from semantic search).45 The implementation of this system will reside entirely within the dedicated

search module of the Modular Monolith, demonstrating the architecture's ability to encapsulate complex, multi-component functionality.

#### **Data Ingestion Pipeline**

Before queries can be executed, the game data must be indexed for both search types. This will be handled by an asynchronous data ingestion pipeline:

1. When a game's data (e.g., title, description, genre tags) is created or updated, it is first saved to the primary PostgreSQL database by the games module.  
2. This action triggers an asynchronous background task.  
3. The task takes the relevant text fields and passes them to an embedding service, which uses a pre-trained sentence-transformer model (e.g., from the Hugging Face library) to generate a high-dimensional vector embedding.  
4. This vector embedding is then stored in the vector database, along with a reference to the game's primary key from the PostgreSQL database.  
5. Simultaneously, the text fields are indexed by PostgreSQL's built-in full-text search capabilities.

#### **Query Execution Flow**

When a user submits a search query, the search module's service layer will execute the following steps:

1. The user's query string is received at the search API endpoint.  
2. The query string is passed through the same embedding model used during ingestion to generate a query vector.  
3. **Parallel Queries:** The service initiates two search queries concurrently to minimize latency:  
   * **Vector Query:** A k-Nearest Neighbor (kNN) similarity search is performed against the vector database using the query vector. This returns the top k results that are most semantically similar to the user's query.45  
   * **Keyword Query:** A full-text search query is executed against the PostgreSQL database to retrieve all results that match the keywords in the user's query.  
4. **Result Fusion:** The two lists of results are merged and re-ranked into a single, unified result set. A **Reciprocal Rank Fusion (RRF)** algorithm will be employed for this purpose. RRF is a technique that combines ranked lists from different sources by considering the rank of each item, rather than its absolute score. This approach is effective at balancing the outputs of the lexical and semantic searches to produce a final ranking that is more relevant than either search method could achieve alone.45 The final, fused list of results is then returned to the user.

This entire process, from receiving the request to orchestrating the parallel queries and fusing the results, is contained within the search module's service.py. This design is a powerful demonstration of the Modular Monolith pattern: it can house a complex, multi-stage workflow involving multiple data stores (PostgreSQL and a vector DB) within a single, cohesive, and clearly bounded module, all while remaining within the unified repository context required by the AI agent.

## **Engineering the Agent's Environment: A Framework for Documentation and Configuration**

In an AI-first development paradigm, documentation and configuration files transcend their traditional role as static, human-centric artifacts. They become active, prescriptive components of the development toolchain, directly shaping the behavior and effectiveness of the AI agent. A change to a file like copilot-instructions.md is analogous to modifying a compiler flag or a linter configuration—it has a direct and immediate impact on the code being generated. Therefore, these artifacts must be engineered with the same rigor as the application code itself. This section provides the "operating manual" for the AI-assisted workflow, defining the critical "soft infrastructure" and providing ready-to-use templates.

### **The README.md: The Agent's First Briefing**

The README.md file is the primary entry point to the project for any developer, human or AI. The GitHub Copilot Agent is specifically programmed to consult this file first to gain a high-level understanding of the project's purpose, structure, and conventions.6 A comprehensive and well-structured

README is therefore the first and most important piece of context provided to the agent.

The README.md for the 'Actual Game Search' project will include the following essential sections:

* **Project Title and Description:** A clear, concise summary of the project's purpose.  
* **Table of Contents:** For easy navigation of the document.  
* **Installation:** Step-by-step instructions for setting up the development environment.  
* **Usage:** A quickstart guide with concrete examples of how to run the application and use its primary API endpoints.  
* **High-Level Architecture Overview:** This is a critical section for the AI agent. It will explicitly describe the Modular Monolith architecture, name the core modules (e.g., games, users, search), and explain their respective responsibilities. This provides the agent with a conceptual map of the system before it even analyzes the code.6  
* **Contributing Guidelines:** A link to a CONTRIBUTING.md file explaining how to contribute to the project.  
* **License:** The project's open-source license.

### **copilot-instructions.md: The Agent's Prime Directive**

This is the single most influential file for guiding the agent's day-to-day behavior. Stored in the /.github/ directory, the contents of copilot-instructions.md are attached as persistent context to every request sent to the Copilot service.37 This file is where project-specific standards, architectural patterns, and coding guidelines are codified for the agent.

The following template will be used for the project's copilot-instructions.md:

# **GitHub Copilot Instructions for the 'Actual Game Search' Project**

## **Project Overview**

This project is a Python-based web application named 'Actual Game Search'. It provides a RESTful API for searching a catalog of video games using a hybrid search algorithm that combines keyword and semantic search. The backend is built as a Modular Monolith.

## **Tech Stack**

* Language: Python 3.12+  
* Web Framework: FastAPI  
* Database: PostgreSQL with SQLAlchemy 2.0 (async)  
* Vector Store: Weaviate  
* Testing: pytest  
* Linting/Formatting: Ruff

## **Project Structure**

The application follows a Modular Monolith architecture. The source code is in /src/actual\_game\_search.

* /src/actual\_game\_search/core: Contains shared application logic (database sessions, settings, etc.).  
* /src/actual\_game\_search/modules: Contains individual business domain modules.  
* Each module (e.g., /modules/games) has a standard internal structure:  
  * router.py: Defines the FastAPI API endpoints.  
  * service.py: Contains the business logic.  
  * schemas.py: Contains Pydantic data models for API requests and responses.  
  * models.py: Contains SQLAlchemy database models.

## **Coding Guidelines**

* **Asynchronous Code:** All I/O-bound operations, especially database queries and external API calls, MUST be asynchronous. All FastAPI endpoint functions MUST be defined with async def.  
* **Type Hinting:** All function signatures and class attributes MUST include comprehensive type hints using Python's typing module. Pydantic models should be used for all API data structures.  
* **Separation of Concerns:** Business logic MUST reside in service.py files. router.py files should only handle HTTP request/response logic and call service layer functions. Services MUST NOT directly access the FastAPI Request object.  
* **Docstrings:** All public modules, classes, and functions MUST have Google-style docstrings explaining their purpose, arguments, and return values.  
* **Error Handling:** Use custom exceptions defined in a module's exceptions.py for domain-specific errors. Do not catch generic Exception.

## **Testing Strategy**

* All new API endpoints added to a router.py file MUST be accompanied by corresponding integration tests in the /tests directory.  
* Business logic in service.py should have unit tests with mocked dependencies where appropriate.  
* Tests MUST follow the Arrange-Act-Assert pattern.

### **copilot-setup-steps.yaml: Configuring the Agent's Sandbox**

When using the asynchronous Copilot Coding Agent, which operates within a GitHub Actions container, it is essential to provide it with a properly configured environment. The copilot-setup-steps.yaml file in the /.github/ directory serves this purpose, defining the steps required to install dependencies and tools the agent needs to build, lint, and test its own changes.6 A properly configured sandbox ensures the agent can validate its work, leading to higher-quality pull requests that are more likely to pass CI checks.19

An example copilot-setup-steps.yaml would include:

YAML

name: "Copilot Setup Steps"  
on: workflow\_dispatch  
jobs:  
  setup:  
    runs-on: ubuntu-latest  
    steps:  
      \- name: Check out code  
        uses: actions/checkout@v4

      \- name: Set up Python  
        uses: actions/setup-python@v5  
        with:  
          python-version: '3.12'

      \- name: Install uv  
        run: pip install uv

      \- name: Install project dependencies  
        run: uv sync

### **Architectural Decision Records (ADRs): Documenting the "Why"**

To maintain a clear and traceable history of significant architectural choices, the project will adopt the practice of creating Architectural Decision Records (ADRs). ADRs are lightweight, version-controlled documents that capture not just what decision was made, but also the context in which it was made, the alternatives considered, and the anticipated consequences.35 Storing these records in the

/docs/adr directory creates an invaluable historical log. This log is essential for onboarding new team members and prevents the wasteful relitigation of past decisions.51 For an advanced AI agent powered by GPT-5, this repository of documented rationale provides a rich source of deep context, potentially allowing it to understand the historical constraints and trade-offs of the system, leading to more nuanced and appropriate suggestions.

The following standardized template will be used for all ADRs to ensure consistency and clarity.

**Table 4: Architectural Decision Record (ADR) Template**

| Section | Description |
| :---- | :---- |
| **Title** | A short, descriptive title for the decision. Example: "001: Adopt Modular Monolith Architecture" |
| **Status** | The current status of the decision (e.g., Proposed, Accepted, Deprecated, Superseded by ADR-00X). |
| **Date** | The date the decision was last updated. |
| **Context and Problem Statement** | A detailed description of the issue, business requirement, or technical challenge that necessitates a decision. This section sets the stage and explains the "why." |
| **Decision Drivers** | A bulleted list of the key factors influencing the decision, such as non-functional requirements (performance, scalability), team skills, project constraints, or strategic goals. |
| **Considered Options** | A summary of each of the viable options that were evaluated. Each option should be described briefly, along with its primary pros and cons in the context of the problem. |
| **Decision Outcome** | A clear and unambiguous statement of the chosen option. This section should state precisely what will be done. |
| **Consequences** | A balanced analysis of the results of the decision. This includes: \- **Positive:** The expected benefits and improvements. \- **Negative:** The known trade-offs, risks, or limitations introduced by the decision. |

## **Strategic Recommendations and Implementation Roadmap**

This report has established a comprehensive blueprint for the 'Actual Game Search' project, centered on an AI-first development strategy. The core of this strategy is the adoption of a Modular Monolith architecture, implemented with a modern Python and FastAPI stack, and supported by a repository structure and documentation framework meticulously engineered for collaboration with the GitHub Copilot Agent. This concluding section summarizes the key decisions, presents a practical implementation roadmap, and outlines strategies for managing the unique risks and opportunities of this approach.

### **Summary of Core Architectural Decisions**

The unified technology stack and architecture for the 'Actual Game Search' project are defined by the following key decisions:

* **Development Paradigm:** An AI-first approach, leveraging the GitHub Copilot Agent (powered by GPT-5) as an autonomous peer programmer for core development tasks.  
* **Macro-Architecture:** A Modular Monolith, chosen to provide the unified repository context required by the AI agent while ensuring long-term maintainability and scalability through clear, domain-driven internal boundaries.  
* **Technology Stack:** A high-performance, asynchronous stack featuring Python, FastAPI, PostgreSQL, and SQLAlchemy, with a dedicated vector database for semantic search.  
* **Core Functionality:** A hybrid search system that combines keyword-based and vector-based search, with results merged via a Reciprocal Rank Fusion (RRF) algorithm to maximize relevance.  
* **AI Environment Engineering:** A rigorous approach to "soft infrastructure," treating README.md, copilot-instructions.md, and Architectural Decision Records (ADRs) as active, critical components of the development toolchain.

### **Phased Implementation Roadmap**

A phased approach is recommended to ensure a stable foundation and iterative delivery of value.

* **Phase 1: Foundation and Scaffolding (Sprints 0-1)**  
  * **Objective:** Establish the complete project structure and AI environment.  
  * **Key Activities:**  
    1. Initialize the Git repository with the complete directory structure defined in Section 3\.  
    2. Create the initial README.md and copilot-instructions.md files based on the templates in Section 5\.  
    3. Author and approve ADR-001 ("Adopt Modular Monolith Architecture") and ADR-002 ("Select Core Technology Stack").  
    4. Set up the core FastAPI application shell, including database connections and configuration management.  
    5. Establish the CI/CD pipeline in GitHub Actions, including steps for linting, testing, and building.  
  * **AI Role:** The Copilot Agent will be used extensively in this phase to accelerate the creation of boilerplate code, configuration files, and initial module scaffolding.  
* **Phase 2: Core Module and Ingestion Pipeline Development (Sprints 2-N)**  
  * **Objective:** Build the foundational business domains and the data pipeline for search.  
  * **Key Activities:**  
    1. Develop the users module, including authentication and user profile management.  
    2. Develop the games module for managing the game catalog.  
    3. Implement the asynchronous data ingestion pipeline for generating and storing vector embeddings for game data.  
* **Phase 3: Hybrid Search Implementation and Feature Expansion**  
  * **Objective:** Deliver the core search functionality and build out remaining features.  
  * **Key Activities:**  
    1. Implement the search module, including the parallel query logic and the RRF result fusion algorithm.  
    2. Tune the search relevance and performance based on testing.  
    3. Develop subsequent modules as required (e.g., reviews, recommendations).

### **Managing Risks and Ensuring Quality**

Adopting an AI-first workflow introduces new categories of risk that must be actively managed.

* **Human Oversight is Non-Negotiable:** The AI agent is a powerful tool, but it is not infallible. It can produce code that is subtly incorrect, insecure, or inefficient. Therefore, a core principle of the workflow must be that all AI-generated code is subject to the same rigorous review process by a human developer as code written by any other team member.2 The developer remains the ultimate authority and is responsible for the quality of the final committed code.  
* **Budget and Rate-Limit Management:** The economic constraints of using premium AI models must be managed proactively. The team will adopt a formal policy for model selection:  
  * **GPT-5 (Premium):** To be used for complex, "zero-to-one" tasks, such as scaffolding a new module or implementing a complex algorithm from a high-level description.  
  * GPT-4.1 (Included): To be used for more iterative tasks, such as refining existing code, writing tests, generating documentation, and debugging.  
    This disciplined approach will conserve the premium request allowance and mitigate the risk of workflow interruptions from rate-limiting.  
* **Training and Onboarding:** The team's effectiveness will depend on its ability to collaborate with the agent. Training will be provided not just on the technology stack but on the practice of **effective prompt engineering**.1 A library of reusable, task-specific prompt files (  
  .prompt.md) will be created and shared within the team to ensure consistency and disseminate best practices for common workflows, such as generating new API endpoints or refactoring service logic.36

### **Conclusion: A Symbiotic Future for Human and AI Developers**

The architectural and strategic framework detailed in this report represents a deliberate step towards a new model of software development—one characterized by a symbiotic relationship between human and artificial intelligence. By consciously designing a system and a workflow that are optimized for an AI partner, the 'Actual Game Search' project is positioned to achieve a significant competitive advantage. This approach promises not to replace human developers, but to augment their capabilities, automating well-defined and repetitive implementation tasks.4 This frees up valuable engineering creativity to focus on the most challenging and impactful aspects of software creation: high-level problem-solving, complex architectural design, and innovative product development. The result is a more productive, more satisfied development team capable of delivering high-quality software at an accelerated pace.

#### **Works cited**

1. GitHub Copilot in VS Code, accessed September 6, 2025, [https://code.visualstudio.com/docs/copilot/overview](https://code.visualstudio.com/docs/copilot/overview)  
2. Best practices for using GitHub Copilot, accessed September 6, 2025, [https://docs.github.com/en/copilot/get-started/best-practices](https://docs.github.com/en/copilot/get-started/best-practices)  
3. Introducing GitHub Copilot agent mode (preview) \- Visual Studio Code, accessed September 6, 2025, [https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)  
4. Agent mode 101: All about GitHub Copilot's powerful mode \- The GitHub Blog, accessed September 6, 2025, [https://github.blog/ai-and-ml/github-copilot/agent-mode-101-all-about-github-copilots-powerful-mode/](https://github.blog/ai-and-ml/github-copilot/agent-mode-101-all-about-github-copilots-powerful-mode/)  
5. Let's try GitHub Copilot Agent mode in VS Code to build a FULL app\! \- YouTube, accessed September 6, 2025, [https://www.youtube.com/watch?v=pUK7MRzoTDc](https://www.youtube.com/watch?v=pUK7MRzoTDc)  
6. Onboarding your AI peer programmer: Setting up GitHub Copilot coding agent for success, accessed September 6, 2025, [https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/)  
7. Use agent mode \- Visual Studio (Windows) | Microsoft Learn, accessed September 6, 2025, [https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-mode?view=vs-2022](https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-mode?view=vs-2022)  
8. Use agent mode in VS Code, accessed September 6, 2025, [https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode](https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode)  
9. About GitHub Copilot coding agent, accessed September 6, 2025, [https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent](https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent)  
10. GPT-5 Now Available in Visual Studio \- Microsoft Developer Blogs, accessed September 6, 2025, [https://devblogs.microsoft.com/visualstudio/gpt-5-now-available-in-visual-studio/](https://devblogs.microsoft.com/visualstudio/gpt-5-now-available-in-visual-studio/)  
11. Microsoft incorporates OpenAI's GPT-5 into consumer, developer and enterprise offerings, accessed September 6, 2025, [https://news.microsoft.com/source/features/ai/openai-gpt-5/](https://news.microsoft.com/source/features/ai/openai-gpt-5/)  
12. GitHub Copilot Agent Mode: Enhancing Developer Workflows \- DEV Community, accessed September 6, 2025, [https://dev.to/brylie/github-copilot-agent-mode-enhancing-developer-workflows-2ae0](https://dev.to/brylie/github-copilot-agent-mode-enhancing-developer-workflows-2ae0)  
13. GPT-5 is here, and it's now available in GitHub Copilot \- YouTube, accessed September 6, 2025, [https://www.youtube.com/shorts/5nffupc2peM](https://www.youtube.com/shorts/5nffupc2peM)  
14. Using GitHub Copilot to explore a codebase, accessed September 6, 2025, [https://docs.github.com/en/copilot/tutorials/explore-a-codebase](https://docs.github.com/en/copilot/tutorials/explore-a-codebase)  
15. From chaos to clarity: Using GitHub Copilot agents to improve developer workflows, accessed September 6, 2025, [https://github.blog/ai-and-ml/github-copilot/from-chaos-to-clarity-using-github-copilot-agents-to-improve-developer-workflows/](https://github.blog/ai-and-ml/github-copilot/from-chaos-to-clarity-using-github-copilot-agents-to-improve-developer-workflows/)  
16. Requests in GitHub Copilot, accessed September 6, 2025, [https://docs.github.com/en/copilot/concepts/billing/copilot-requests](https://docs.github.com/en/copilot/concepts/billing/copilot-requests)  
17. GitHub Copilot · Your AI pair programmer, accessed September 6, 2025, [https://github.com/features/copilot](https://github.com/features/copilot)  
18. Agent mode hitting rate limit, with Copilot Pro subscription · Issue \#7416 \- GitHub, accessed September 6, 2025, [https://github.com/microsoft/vscode-copilot-release/issues/7416](https://github.com/microsoft/vscode-copilot-release/issues/7416)  
19. Best practices for using Copilot to work on tasks \- GitHub Enterprise Cloud Docs, accessed September 6, 2025, [https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/coding-agent/best-practices](https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/coding-agent/best-practices)  
20. Structuring Modular Monoliths \- DEV Community, accessed September 6, 2025, [https://dev.to/xoubaman/modular-monolith-3fg1](https://dev.to/xoubaman/modular-monolith-3fg1)  
21. What Is a Modular Monolith? \- GeeksforGeeks, accessed September 6, 2025, [https://www.geeksforgeeks.org/system-design/what-is-a-modular-monolith/](https://www.geeksforgeeks.org/system-design/what-is-a-modular-monolith/)  
22. Modular monolith in Python | breadcrumbs collector.tech, accessed September 6, 2025, [https://breadcrumbscollector.tech/modular-monolith-in-python/](https://breadcrumbscollector.tech/modular-monolith-in-python/)  
23. arctikant/fastapi-modular-monolith-starter-kit \- GitHub, accessed September 6, 2025, [https://github.com/arctikant/fastapi-modular-monolith-starter-kit](https://github.com/arctikant/fastapi-modular-monolith-starter-kit)  
24. I built the Agent mode for Github Copilot \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/GithubCopilot/comments/1hp2zve/i\_built\_the\_agent\_mode\_for\_github\_copilot/](https://www.reddit.com/r/GithubCopilot/comments/1hp2zve/i_built_the_agent_mode_for_github_copilot/)  
25. How do you make use of Copilot Agent on production-scale codebases which have large source files? : r/GithubCopilot \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/GithubCopilot/comments/1ktv390/how\_do\_you\_make\_use\_of\_copilot\_agent\_on/](https://www.reddit.com/r/GithubCopilot/comments/1ktv390/how_do_you_make_use_of_copilot_agent_on/)  
26. Bigger Applications \- Multiple Files \- FastAPI, accessed September 6, 2025, [https://fastapi.tiangolo.com/tutorial/bigger-applications/](https://fastapi.tiangolo.com/tutorial/bigger-applications/)  
27. Structuring a FastAPI Project: Best Practices \- DEV Community, accessed September 6, 2025, [https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6](https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6)  
28. FastAPI Best Practices and Conventions we used at our startup \- GitHub, accessed September 6, 2025, [https://github.com/zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)  
29. Best Practices in Structuring Python Projects \- Dagster, accessed September 6, 2025, [https://dagster.io/blog/python-project-best-practices](https://dagster.io/blog/python-project-best-practices)  
30. Structuring Your Project \- The Hitchhiker's Guide to Python, accessed September 6, 2025, [https://docs.python-guide.org/writing/structure/](https://docs.python-guide.org/writing/structure/)  
31. What is the best project structure for a Python application? \[closed\] \- Stack Overflow, accessed September 6, 2025, [https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application](https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application)  
32. How to Structure Your FastAPI Projects \- Medium, accessed September 6, 2025, [https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f](https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f)  
33. YoraiLevi/modular-monolith-fastapi: This is a modular monolith Fast API project that uses the latest and greatest tooling (uv, ruff, pyright, pydantic, pytest, fastapi, sqlmodel, etc) attempting to implement a modular monolith architecture. The repository include pre-commit hooks for ruff, pyright, and \- GitHub, accessed September 6, 2025, [https://github.com/YoraiLevi/modular-monolith-fastapi](https://github.com/YoraiLevi/modular-monolith-fastapi)  
34. Python Application Layouts: A Reference, accessed September 6, 2025, [https://realpython.com/python-application-layouts/](https://realpython.com/python-application-layouts/)  
35. About MADR \- Architectural Decision Records, accessed September 6, 2025, [https://adr.github.io/madr/](https://adr.github.io/madr/)  
36. Tips and tricks for Copilot in VS Code, accessed September 6, 2025, [https://code.visualstudio.com/docs/copilot/copilot-tips-and-tricks](https://code.visualstudio.com/docs/copilot/copilot-tips-and-tricks)  
37. How do you setup your copilot-instructions.md? : r/GithubCopilot \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/GithubCopilot/comments/1kvtrms/how\_do\_you\_setup\_your\_copilotinstructionsmd/](https://www.reddit.com/r/GithubCopilot/comments/1kvtrms/how_do_you_setup_your_copilotinstructionsmd/)  
38. Scalable FastAPI project structure \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/FastAPI/comments/1je4dsv/scalable\_fastapi\_project\_structure/](https://www.reddit.com/r/FastAPI/comments/1je4dsv/scalable_fastapi_project_structure/)  
39. Best Practices for Structuring Your FastAPI Projects | by Joël-Steve N. | Stackademic, accessed September 6, 2025, [https://blog.stackademic.com/best-practices-for-structuring-your-fastapi-projects-e66482b27d02](https://blog.stackademic.com/best-practices-for-structuring-your-fastapi-projects-e66482b27d02)  
40. Large Applications as Packages — Flask Documentation (3.1.x), accessed September 6, 2025, [https://flask.palletsprojects.com/en/stable/patterns/packages/](https://flask.palletsprojects.com/en/stable/patterns/packages/)  
41. What is the "correct" way to structure your files for larger Python projects? \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/learnpython/comments/seu5l6/what\_is\_the\_correct\_way\_to\_structure\_your\_files/](https://www.reddit.com/r/learnpython/comments/seu5l6/what_is_the_correct_way_to_structure_your_files/)  
42. 3 Python AI Projects for Beginners \- Full Tutorial \- YouTube, accessed September 6, 2025, [https://www.youtube.com/watch?v=XZdY15sHUa8](https://www.youtube.com/watch?v=XZdY15sHUa8)  
43. About hybrid search | Vertex AI | Google Cloud, accessed September 6, 2025, [https://cloud.google.com/vertex-ai/docs/vector-search/about-hybrid-search](https://cloud.google.com/vertex-ai/docs/vector-search/about-hybrid-search)  
44. Improve Your Python Search Relevance with Astra DB Hybrid Search \- DataStax \- Medium, accessed September 6, 2025, [https://datastax.medium.com/improve-your-python-search-relevance-with-astra-db-hybrid-search-3e38f8994c95](https://datastax.medium.com/improve-your-python-search-relevance-with-astra-db-hybrid-search-3e38f8994c95)  
45. Hybrid query \- Azure AI Search \- Microsoft Learn, accessed September 6, 2025, [https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)  
46. AI-Powered Documentation: The Secret to Efficient Technical Writing | 8th Light, accessed September 6, 2025, [https://8thlight.com/insights/ai-powered-documentation-the-secret-to-efficient-technical-writing](https://8thlight.com/insights/ai-powered-documentation-the-secret-to-efficient-technical-writing)  
47. Introducing the Awesome GitHub Copilot Customizations repo \- Microsoft Developer Blogs, accessed September 6, 2025, [https://devblogs.microsoft.com/blog/introducing-awesome-github-copilot-customizations-repo](https://devblogs.microsoft.com/blog/introducing-awesome-github-copilot-customizations-repo)  
48. Best practices for using GitHub Copilot to work on tasks, accessed September 6, 2025, [https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks](https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks)  
49. Architecture decision record (ADR) examples for software planning, IT leadership, and template documentation \- GitHub, accessed September 6, 2025, [https://github.com/joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)  
50. Architecture Decision Records | endjin \- Azure Data Analytics Consultancy UK, accessed September 6, 2025, [https://endjin.com/blog/2023/07/architecture-decision-records](https://endjin.com/blog/2023/07/architecture-decision-records)  
51. IASA \- Architecture Decision Record Template | Miroverse, accessed September 6, 2025, [https://miro.com/miroverse/architecture-decision-record-template/](https://miro.com/miroverse/architecture-decision-record-template/)  
52. What are Architecture Decision Records (ADR) and what should you consider when making architectural decisions? : r/softwarearchitecture \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/softwarearchitecture/comments/1gz7wco/what\_are\_architecture\_decision\_records\_adr\_and/](https://www.reddit.com/r/softwarearchitecture/comments/1gz7wco/what_are_architecture_decision_records_adr_and/)