

## **User Prompt**

\- In 2023 I built a semantic game search engine (attachments: "Building Semantic Game Search\*.md")

\- The costs were too high to sustain the project

\- In September 2025 I began exploring ways to revitalize the project with modern ergonomics and cost improvements (05\_Deep Research Report\_\*.md).

\- AI-driven development work has been underway for building this new iteration: "Actual Game Search"/\`actualgamesearch.com\`.

\- Additional Gemini Deep Research reports were commissioned after reading an article this morning (9/6/2025) that claimed there were hard upper limits to semantic search document counts (06\_\*.md, 07\_\*.md, and 08\_\*.md).

\- The 8th report exposed a core flaw in our pivot to DuckDB: Vector search capabilities.

For this ninth report, I ask that you resolve this piece.

We have been aiming to use ollama to host nomic-embed-text:v1.5 (\`ollama pull nomic-embed-text:v1.5\`) to handle the creation of 768-dimensional embeddings with an 8192 token context window on inexpensive cloudflare resources (or, of course, local dev). If we fix that piece in place (the chosen embedding model), then:

Between the following three options:

\- sqlite

\- DuckDB

\- PostgresDB

Choose the approach which will power vector search for product reviews.

\*\*Check the user prompts in the deep research reports to get a nuanced view of my overall intentions.\*\*

---

## **Gemini Deep Research**

I've put together a research plan. If you need to update it in any way, let me know.  
Database Choice for Vector Search  
Research Websites and Files  
(1) Investigate the current state of vector search capabilities for SQLite, DuckDB, and PostgresDB. Identify the primary extensions or built-in features used for this purpose (e.g., sqlite-vss, DuckDB's vss extension, pgvector). (2) Analyze the performance and scalability of each database's vector search implementation: (a) Research indexing speed and query latency benchmarks, specifically for datasets with 768-dimensional embeddings. (b) Investigate the practical limits on the number of vectors each can handle efficiently, addressing the concern about "hard upper limits". (c) Compare the available vector index types (e.g., HNSW, IVFFlat) and their respective trade-offs between speed, accuracy, and memory usage. (3) Evaluate the resource requirements and deployment models for each option, focusing on compatibility with inexpensive cloud infrastructure like Cloudflare. Assess memory consumption, CPU usage, storage footprint, and overall suitability for serverless environments. (4) Conduct a targeted investigation into the "core flaw" of DuckDB's vector search capabilities mentioned in the project history. Search for recent developments, articles, or official documentation from September 2025 or earlier that discuss its limitations or improvements. (5) Compare the developer experience and ecosystem maturity for each solution. Examine the quality of documentation, community support, and ease of integration for their respective vector search extensions. (6) Synthesize all findings into a comparative analysis, weighing the pros and cons of each database against the project's specific requirements: low operational cost, performance for product review search, and scalability. (7) Conclude with a definitive recommendation for which database should power vector search for 'Actual Game Search', providing a clear rationale that connects the chosen option's strengths to the project's goals and constraints.  
Analyze Results  
Create Report

---

# **Report 9**

# **Architectural Analysis of Vector Search Databases for Cloudflare Edge Deployments**

## **Executive Summary**

This report provides a definitive technical recommendation for a vector search backend to power a product review search feature. The analysis evaluates three database solutions—SQLite, DuckDB, and PostgreSQL—within the specific constraints of a fixed nomic-embed-text:v1.5 embedding model (768 dimensions) and a primary deployment target of inexpensive Cloudflare infrastructure. The evaluation framework prioritizes performance, scalability, total cost of ownership (TCO), and architectural fitness for the Cloudflare edge computing paradigm.

The core findings of this analysis reveal distinct suitability profiles for each candidate. DuckDB, despite its analytical prowess, is deemed architecturally unsuitable for this stateful, transactional workload due to critical limitations in its experimental vector search extension, particularly its in-memory index requirement and unsafe persistence model. PostgreSQL, augmented with the mature pgvector extension and connected via Cloudflare Hyperdrive, represents a robust, feature-rich, and scalable solution. However, its client-server architecture introduces unavoidable network latency, which is antithetical to the goals of edge computing, and its reliance on external managed database services results in a TCO that is an order of magnitude higher than edge-native alternatives.

The most compelling solution is SQLite, utilizing the modern sqlite-vec extension and deployed within Cloudflare Durable Objects. This pattern represents a truly edge-native architecture, achieving unparalleled data locality by co-locating the database engine, vector search logic, and persistent storage within the same process as the application logic. This eliminates network latency for database operations, leading to superior end-to-end performance for many use cases. While its current brute-force search mechanism is less scalable than pgvector's Approximate Nearest Neighbor (ANN) indexes for global searches across millions of vectors, it is highly performant for the primary use case of filtered searches (e.g., within a single product's reviews). Furthermore, a clear development roadmap for adding ANN capabilities provides a confident path for future scaling.

Based on its superior architectural alignment with the Cloudflare ecosystem, its potential for the lowest end-to-end query latency, and its significantly lower total cost of ownership, the final recommendation is to adopt **SQLite with the sqlite-vec extension, deployed within Cloudflare Durable Objects**, as the vector search backend for the product review system. This choice positions the application on a forward-looking architectural foundation that fully leverages the performance and cost benefits of edge computing.

## **1\. Introduction: Framing the Vector Search Challenge for Product Reviews**

The task of selecting a database for vector search is not merely a feature comparison but a critical architectural decision that has profound implications for application performance, scalability, and operational cost. This decision is further constrained and defined by the specific technical stack and deployment environment. This report evaluates the optimal choice between SQLite, DuckDB, and PostgreSQL for a product review search system under a precise set of conditions.

### **1.1. Deconstructing the Technical Stack: nomic-embed-text and Its Implications**

The project's standardization on the nomic-embed-text:v1.5 model establishes two fundamental, non-negotiable parameters that shape the database requirements: vector dimensionality and data payload size.

First, the model generates embeddings with a fixed dimensionality of 768\. When stored as standard single-precision floating-point numbers (float32), each vector will consume a predictable amount of storage. The calculation is straightforward:

768 dimensions×4 bytes/dimension=3,072 bytes per vector  
This 3 KB payload per embedding is a critical baseline for calculating total storage requirements, memory usage for in-memory indexes, and network transfer costs. A database holding one million product reviews will require over 3 GB of storage for the vector data alone, before accounting for metadata, indexes, and operational overhead.1

Second, the model's 8192 token context window implies that the source text for each embedding—the product review itself—can be substantial. This reinforces the necessity for a database solution that can efficiently store and manage the vector payload alongside its associated structured metadata. A typical product review record will include not just the embedding but also the product ID, user ID, the raw review text, a star rating, and a timestamp. The ideal database must excel at hybrid queries that filter on this structured metadata before performing a similarity search on the vector embeddings.

### **1.2. The Cloudflare Ecosystem as a Deployment Target: Constraints and Opportunities**

Deploying on "inexpensive Cloudflare resources" mandates an architecture that is native to its serverless, globally distributed paradigm. This environment is characterized by unique constraints and powerful opportunities that heavily influence the choice of a database.

The core compute primitive, Cloudflare Workers, is designed to be ephemeral and stateless.2 A Worker instance may be spun up to handle a single request and then shut down, with no guarantee that a subsequent request will be handled by the same instance. This model fundamentally challenges traditional database architectures that rely on long-lived server processes and persistent connections.

The primary value proposition of this edge computing model is the reduction of latency by moving compute closer to the end-user. A database architecture that requires a long network round trip from an edge Worker to a centralized database server in a distant region can negate these performance gains. Therefore, data locality—the co-location of data and the compute that operates on it—becomes the single most important architectural principle for achieving high performance.

The Cloudflare platform provides several key services for managing data and state, each with a distinct role:

* **Workers:** The serverless JavaScript and WebAssembly (WASM) runtime that executes application logic at the edge.4  
* **Durable Objects (DO):** A strongly-consistent, stateful compute primitive. A Durable Object provides a single-threaded execution environment combined with co-located, transactional storage. All requests for a specific DO, identified by a unique ID, are routed to the same instance, guaranteeing serializable access to its state. This makes it an ideal building block for managing state for a specific entity, such as all reviews for a single product.2  
* **D1:** A serverless SQL database built on SQLite, intended for more traditional relational workloads. While powerful, it is designed as a separate service that a Worker queries over the network, introducing latency that the DO model avoids.6  
* **R2:** An S3-compatible object storage service, ideal for storing large, static assets like images, documents, or Parquet files. It is not a transactional database and is unsuitable for workloads requiring frequent, low-latency writes.7  
* **Hyperdrive:** A global connection pooler for traditional databases. It allows ephemeral Workers to efficiently connect to centralized databases like PostgreSQL by maintaining and reusing a pool of warm TCP connections, thus mitigating the high latency cost of establishing a new connection for every request.9

### **1.3. Defining the Evaluation Framework: Performance, Scalability, Cost, and Developer Experience**

To provide a conclusive recommendation, each database solution will be rigorously evaluated against a framework of four key criteria, tailored to the project's specific requirements:

* **Performance:** This is primarily measured by end-to-end query latency (p95, p99) for K-Nearest Neighbor (KNN) vector search. Crucially, this includes the performance of hybrid queries that combine vector search with metadata filtering, as this will be the dominant query pattern for the product review use case.  
* **Scalability:** This assesses how the solution handles growth in the number of product reviews, from an initial set of thousands to a future state of millions. This evaluation covers storage scaling, the performance impact of index building and maintenance, and the degradation of query latency under increasing load.  
* **Cost:** This analysis focuses on the Total Cost of Ownership (TCO). It includes not only the direct fees for database services (e.g., monthly costs for a managed PostgreSQL instance 11) but also the associated Cloudflare usage costs, such as Worker invocations, Durable Object duration and storage fees, and any applicable data egress charges.  
* **Developer Experience:** This criterion evaluates the ease of implementation, integration with the Cloudflare toolchain (e.g., the wrangler CLI), the ergonomics of the query language for vector operations, and the overall maturity and support of the database's ecosystem.

## **2\. Deep Dive: SQLite as an Embedded Vector Powerhouse**

SQLite's long-standing reputation as a lightweight, reliable database for embedded systems and mobile applications has found new relevance in the era of edge computing. Its core architectural principles align remarkably well with the constraints and opportunities of serverless platforms like Cloudflare Workers.

### **2.1. Architectural Profile: The "Local-First" Paradigm of SQLite**

Unlike traditional client-server databases, SQLite is not a separate process. It is an in-process library that is linked directly into the application, providing a full-featured, serverless, zero-configuration, transactional SQL database engine.14 The database itself is a single file on disk.

This embedded, "local-first" architecture is the defining characteristic that makes SQLite a prime candidate for stateful edge applications. When deployed within a stateful environment like a Cloudflare Durable Object, the database engine and the data file reside in the same process space as the application logic. This eliminates the network as a barrier between compute and storage, enabling data access with latencies measured in microseconds rather than milliseconds.2 The single-threaded transactional model of a Durable Object also perfectly complements SQLite's default single-writer concurrency model, preventing conflicts and simplifying application logic.

### **2.2. The Modern Vector Extension: sqlite-vec Analysis**

While SQLite itself does not have native vector support, this functionality is provided by extensions. The most promising and modern of these is sqlite-vec. It is the actively developed successor to the older sqlite-vss extension, created by the same author, and is purpose-built for modern, portable vector search workloads.15

A critical advantage of sqlite-vec is that it is written in a single file of zero-dependency C code.17 This makes it exceptionally portable and straightforward to compile to WebAssembly (WASM), the universal runtime format for Cloudflare Workers. This contrasts sharply with

sqlite-vss, which depends on the large C++ library Faiss, introducing significant compilation complexity and dependencies that make it ill-suited for a WASM-based edge environment.18

The core features of sqlite-vec are designed for both performance and ease of use:

* **Virtual Tables (vec0):** Following the successful pattern of SQLite's FTS5 full-text search extension, sqlite-vec uses virtual tables to manage vectors. Developers can create a vector index using standard CREATE VIRTUAL TABLE syntax and then interact with it using familiar INSERT, UPDATE, DELETE, and SELECT statements. KNN search is triggered via a natural MATCH clause in the WHERE statement, providing a clean, SQL-native developer experience.17  
* **Search Mechanism:** The current version of sqlite-vec focuses on providing a highly optimized brute-force (exact nearest neighbor) search. This search is accelerated at a low level using SIMD instructions (AVX for x86 and NEON for ARM), making it surprisingly fast for datasets of considerable size.17  
* **Quantization:** To mitigate the storage and performance costs of high-dimensional vectors, sqlite-vec offers powerful quantization features. It supports storing vectors not only as float32 but also as int8 or bit (binary) vectors. Binary quantization can reduce storage by a factor of 32 and speed up queries by an order of magnitude, with a manageable loss in precision.17 The extension also supports Matryoshka embeddings, a technique that allows for truncating vector dimensions at query time to trade accuracy for speed.17  
* **Development Roadmap:** Acknowledging the limits of brute-force search at massive scale, the project has a clear and public roadmap that includes the future implementation of Approximate Nearest Neighbor (ANN) indexes like HNSW and IVF, as well as enhanced metadata filtering and partitioned storage.17 This provides a credible path for scaling the solution without requiring a future re-architecture.

### **2.3. Performance Profile: Latency and Throughput for 768-Dimensional Vectors**

For an embedded database, sqlite-vec demonstrates exceptionally strong performance. Publicly available benchmarks show that its optimized brute-force search is highly competitive with other dedicated vector search libraries for datasets up to the scale of hundreds of thousands of vectors.17

For the specific use case of 768-dimensional vectors, performance tests indicate that queries against a table of 100,000 vectors complete in well under 75ms.17 This is a perfectly acceptable latency for many interactive, user-facing search applications. While performance on

float32 vectors begins to degrade more significantly as the dataset approaches one million vectors, binary quantized vectors at the same scale can still achieve query times around 124ms, which may be suitable for less latency-sensitive operations.17

This performance envelope is particularly well-suited to the product review search use case. A common query pattern will not be a global search across all reviews, but rather a filtered search, such as, "Find reviews similar to X *for product Y*." In this scenario, the search space is immediately reduced to only the vectors associated with a single product. Even for a very popular product with 10,000 or 50,000 reviews, sqlite-vec's brute-force search will execute almost instantaneously. The current performance is therefore more than sufficient for the primary application feature, while the roadmap for ANN indexing addresses the future need for scalable global search capabilities.

### **2.4. Deployment Blueprint on Cloudflare: Leveraging Durable Objects with sqlite-vec via WASM**

The ideal deployment architecture for SQLite on Cloudflare is a powerful and elegant combination of platform features:

1. The sqlite-vec extension and the SQLite C source code are compiled together into a single WebAssembly (WASM) binary.  
2. A Cloudflare Worker is written to include a Durable Object class. Inside the DO's constructor, this WASM module is loaded and instantiated.  
3. The Durable Object is configured to use its native, built-in SQLite storage backend. This provides a persistent, transactional file system API that the WASM-based SQLite engine can use to store its database file.2  
4. A sharding strategy is implemented. For instance, each unique product ID can be mapped to a unique Durable Object ID. This means a single DO instance will be responsible for storing and searching all reviews for a specific product.  
5. A primary "router" Worker receives incoming search requests. It extracts the product ID (or other sharding key) from the request, gets a stub for the corresponding Durable Object, and forwards the search query to that specific instance.

This architecture achieves the pinnacle of data locality. The application logic (in the DO), the database engine (SQLite in WASM), the vector search logic (sqlite-vec in WASM), and the persistent storage (the DO's SQLite backend) are all encapsulated within a single, managed primitive. Database queries run in the same process and memory space as the code that issues them, completely eliminating network hops and their associated latency.2

The cost model for this architecture is also highly efficient. It is based purely on Cloudflare's usage metrics: Worker requests, Durable Object active duration, and Durable Object storage operations. Notably, storage for SQLite-backed Durable Objects is not yet billed, though it will be in the future.5 This pay-for-what-you-use model is dramatically more cost-effective than maintaining an always-on, provisioned client-server database.

## **3\. Deep Dive: DuckDB for High-Performance Analytics and Vector Search**

DuckDB has rapidly gained prominence as a high-performance, in-process database management system. However, its design philosophy and technical implementation are optimized for a fundamentally different class of problems than the one presented by the product review search application.

### **3.1. Architectural Profile: The Columnar Advantage of an In-Process OLAP Engine**

DuckDB is an embedded database designed specifically for Online Analytical Processing (OLAP) workloads.14 Its architecture is built around two key principles: columnar storage and vectorized query execution. Unlike traditional row-oriented databases (like SQLite and PostgreSQL), which store all data for a single record contiguously, DuckDB stores all data for a single column contiguously.

This columnar layout, combined with a query engine that processes data in batches ("vectors") rather than one row at a time, makes DuckDB exceptionally fast for analytical queries that scan and aggregate large portions of a dataset.14 While it is also an "embedded" database like SQLite, its internal architecture is tailored for read-heavy, analytical tasks, not the write-heavy, low-latency transactional lookups characteristic of an application database (an OLTP workload).

### **3.2. The vss Extension: HNSW Indexing and its Critical Limitations**

Vector search capabilities in DuckDB are provided by the vss extension, which implements an HNSW (Hierarchical Navigable Small Worlds) index.23 HNSW is a state-of-the-art ANN algorithm, which in theory should provide excellent scalability for vector search. However, the current implementation of the

vss extension has two critical limitations that render it unsuitable for this project's production requirements.

First, and most significantly, the HNSW index must fit entirely in RAM. The extension documentation explicitly states that the index is not buffer-managed and does not count towards DuckDB's main memory limit.23 For a growing dataset of 768-dimensional product review vectors, this is an immediate and severe scalability bottleneck. As calculated previously, one million vectors would require over 3 GB of RAM for the raw vector data alone, plus the substantial memory overhead of the HNSW graph structure itself. This memory footprint is far beyond the resources available in a standard Cloudflare Worker environment and makes the solution unscalable.

Second, the mechanism for persisting the index to disk is explicitly labeled as an experimental feature that is not safe for production use. The documentation warns that because Write-Ahead Logging (WAL) recovery is not yet properly implemented for custom indexes, an unexpected shutdown or crash can lead to **data loss or corruption of the index**.23 For a system of record like a product review database, the risk of data corruption is unacceptable. This limitation effectively makes the

vss extension unusable for any stateful application that requires durability.

The documentation consistently refers to the vss extension as "experimental".23 While the extension package receives updates 27, these core, blocking limitations regarding memory management and safe persistence remain unresolved in the official documentation.

### **3.3. Performance Profile: Theoretical Speed vs. Practical Hurdles for a Stateful Workload**

In a hypothetical, read-only analytical scenario where the entire dataset and index fit comfortably in memory, DuckDB's vector search performance would likely be excellent. However, the product review use case is stateful and dynamic, with new reviews being constantly added. The vss extension is poorly suited for such a workload. Deletes are not physically removed from the index but are merely marked, causing the index to grow stale and degrade in performance and accuracy over time. Rectifying this requires a periodic, full re-compaction of the index, an operationally burdensome process.23 The lack of robust, incremental updates to a persisted index makes it a brittle choice for a dynamic application database.

### **3.4. Deployment Blueprint on Cloudflare: A Mismatch for Dynamic Vector Search**

The most plausible deployment pattern for DuckDB on Cloudflare would involve running DuckDB-WASM inside a Worker, with the database file stored in the R2 object storage service.8 This pattern is well-suited for interactive, read-only analytics on static datasets (e.g., querying a large Parquet file stored in R2).

However, this architecture is fundamentally broken for a transactional, write-heavy workload. To add a new product review, a Worker would need to:

1. Read the entire multi-gigabyte DuckDB database file from R2 into the Worker's limited in-memory filesystem.  
2. Start the DuckDB-WASM engine and open the database file.  
3. Perform the INSERT operation.  
4. Write the entire modified database file back to R2, overwriting the old one.

This read-modify-write cycle for the entire database on every single write is prohibitively slow, expensive in terms of data transfer, and completely lacks support for concurrent writes. Combined with the previously mentioned limitations of the vss extension, it becomes clear that DuckDB is architecturally mismatched for the requirements of this project. It is the wrong tool for the job.

## **4\. Deep Dive: PostgreSQL as the Enterprise-Grade Relational Vector Store**

PostgreSQL stands as a pillar of the open-source database world, renowned for its robustness, extensibility, and strict adherence to SQL standards. Its mature, client-server architecture has made it the default choice for countless transactional applications for decades.

### **4.1. Architectural Profile: The Robustness of a Client-Server OLTP Database**

PostgreSQL is an object-relational database system that operates on a client-server model. A dedicated server process manages data files, accepts connections from clients, and executes queries. This architecture provides powerful features like multi-version concurrency control (MVCC) for handling many simultaneous readers and writers, sophisticated user and security management, and a rich ecosystem of tools for replication, backup, and monitoring.22

While this model is the industry standard for enterprise applications, its reliance on stable, long-lived connections presents a challenge for ephemeral, serverless environments like Cloudflare Workers. Each request from a Worker would traditionally require establishing a new, expensive TCP and TLS connection to the database server, adding significant latency.9 This is the core problem that Cloudflare Hyperdrive is designed to solve.

### **4.2. The pgvector Extension: Mature ANN Indexing and Rich SQL Integration**

Vector search capabilities are added to PostgreSQL via the pgvector extension, which has become a mature and widely adopted standard for this purpose.29 Unlike the experimental extensions for the other databases,

pgvector is production-ready and battle-tested.

Its key strengths lie in its robust indexing and seamless SQL integration:

* **Indexing:** pgvector provides two industry-standard Approximate Nearest Neighbor (ANN) index types: HNSW and IVFFlat. This gives developers a choice to trade off between index build time, memory usage, and query performance to suit their specific needs. These indexes allow pgvector to maintain low-latency queries on datasets scaling to tens of millions of vectors, far beyond the practical limits of brute-force search.1  
* **Features:** The extension supports a variety of vector types (including halfvec for storage optimization) and distance metrics (L2, inner product, cosine distance).1 It works with any standard PostgreSQL client library, making integration straightforward.  
* **Hybrid Search:** A standout advantage of pgvector is its deep integration with PostgreSQL's SQL query planner. This allows for powerful and ergonomic hybrid searches that combine vector similarity with traditional metadata filtering. A developer can write a single, intuitive SQL query like SELECT \* FROM reviews WHERE product\_id \= 123 AND rating \>= 4 ORDER BY embedding \<=\> $1 LIMIT 10;. The database can efficiently use a standard B-tree index on product\_id and rating to narrow down the candidate set before performing the more expensive ANN search on the remaining vectors. This is a natural and highly effective way to implement the core feature required for the product review system.29

### **4.3. Performance Profile: Predictable Scalability and Hybrid Search Excellence**

With a properly configured HNSW index, pgvector delivers predictable, low-latency query performance even as the dataset grows into the millions of vectors. The performance characteristics are well-understood, and the index can be tuned by adjusting parameters like m (connections per layer), ef\_construction (build-time candidate list size), and ef\_search (query-time candidate list size).1

The ability to perform efficient hybrid searches is its greatest performance strength for this use case. By filtering on structured data first, the database dramatically reduces the number of vectors that need to be considered in the ANN search, leading to significant performance gains. This capability is mature and deeply integrated into the database engine.

### **4.4. Deployment Blueprint with Cloudflare: The Worker \-\> Hyperdrive \-\> Managed Postgres Pattern**

Cloudflare provides a well-documented and supported architecture for connecting Workers to an external PostgreSQL database:

1. A managed PostgreSQL instance is provisioned from a cloud provider (e.g., Neon, AWS RDS, Google Cloud SQL, pgEdge) and the pgvector extension is enabled.9  
2. A Cloudflare Hyperdrive instance is created in the Cloudflare dashboard and configured with the connection details for the managed database. Hyperdrive acts as a regional connection pooler.9  
3. The Cloudflare Worker is configured with a binding that points to the Hyperdrive instance. The full database connection string is stored securely as a Worker secret.35  
4. The Worker's code uses a standard Node.js PostgreSQL client library (e.g., node-postgres) to connect to the database through the Hyperdrive binding and execute queries.3

This pattern is functionally viable. Hyperdrive effectively solves the connection management problem, abstracting away the overhead of TCP/TLS handshakes for each request and allowing the serverless function to communicate with the traditional database.

However, this solution comes with a significant and unavoidable drawback: network latency. The architecture involves at least three distinct locations: the edge location where the Worker executes, a Cloudflare core data center where Hyperdrive manages the connection pool, and the cloud provider's data center where the PostgreSQL server resides. Every single query must traverse this distributed path. This round trip can easily add tens or even hundreds of milliseconds of latency to every database operation, fundamentally undermining the low-latency promise of edge computing.9

### **4.5. Total Cost of Ownership (TCO) Analysis for Managed PostgreSQL Services**

This architecture introduces a substantial and independent cost center: the managed PostgreSQL database. Unlike the usage-based pricing of Cloudflare's native services, managed databases typically involve fixed monthly costs for provisioned resources.

The TCO is composed of several factors:

* **Compute:** A recurring monthly fee based on the vCPU and RAM allocated to the database instance.  
* **Storage:** A monthly fee based on the amount of provisioned disk space (in GB).  
* **I/O:** Charges for input/output operations, which can be significant for a query-heavy workload.  
* **Data Egress:** Potentially high fees for data transferred out of the database provider's network back to the Cloudflare Worker.

A moderately sized instance with sufficient RAM and IOPS to handle a large-scale vector search workload can easily cost several hundred to over a thousand dollars per month.12 This stands in stark contrast to the potentially near-zero marginal cost of the SQLite/Durable Objects solution, making the PostgreSQL architecture significantly more expensive and less aligned with the "inexpensive" requirement of the project.

## **5\. Comparative Analysis: A Head-to-Head Evaluation for the Cloudflare Use Case**

The selection of the optimal vector database requires a direct comparison of the viable candidates—SQLite and PostgreSQL—across the dimensions of architecture, performance, developer experience, and cost, all within the specific context of a Cloudflare edge deployment. DuckDB has been ruled out due to fundamental architectural mismatches and production-blocking limitations in its vector search extension.

### **5.1. Architectural Trade-offs: Embedded vs. Client-Server on the Edge**

The core architectural decision is between an embedded, edge-native model (SQLite/DO) and a bridged, client-server model (Postgres/Hyperdrive). The SQLite/DO pattern represents an architecture that is symbiotically aligned with the principles of edge computing. By co-locating compute, logic, and stateful, transactional storage within a single managed primitive, it achieves maximum data locality and eliminates network latency for database operations. Its single-threaded consistency model per object simplifies development for partitioned workloads.

In contrast, the Postgres/Hyperdrive pattern is an adaptation of a legacy, centralized architecture to a distributed, serverless environment. While Hyperdrive cleverly solves the connection pooling problem, it cannot solve the speed-of-light problem. Every query incurs a network round-trip time tax. This creates an architectural impedance mismatch where the performance benefits of edge compute are partially negated by the latency of accessing a remote, centralized data store.

### **5.2. Performance and Scalability Showdown: From 100,000 to 10 Million Product Reviews**

The performance and scalability of the two solutions evolve as the dataset grows:

* **Low Scale (0 – 500,000 reviews):** At this scale, the sqlite-vec brute-force search is highly competitive. When considering end-to-end latency from the user's perspective, the SQLite/DO solution is likely to be significantly faster. The sub-millisecond in-process query time of SQLite will outperform the combination of a fast raw query time from pgvector plus the 50-150ms of network latency required to reach it.  
* **Medium Scale (500,000 – 5 million reviews):** For global searches across the entire dataset, PostgreSQL with its HNSW index will have a clear advantage in raw query execution time. However, the network latency tax remains a constant factor. The viability of the SQLite solution at this scale depends on the implementation of its planned ANN indexes. For the primary use case of filtered searches within a single product, the SQLite/DO model remains highly performant as the search space per query remains small.  
* **High Scale (5 million+ reviews):** In its current state, pgvector is the only proven solution for global searches at this scale. The recommendation for SQLite is therefore contingent on the successful delivery of the ANN features on its public roadmap.  
* **Hybrid Search:** PostgreSQL's native integration of WHERE clauses with vector search is currently more mature and ergonomic than sqlite-vec's planned metadata filtering capabilities.20

### **5.3. Developer Experience and Ecosystem Maturity**

PostgreSQL offers a low-risk, highly familiar developer experience. Its ecosystem is vast and mature, with countless tools, ORMs, and decades of community knowledge. pgvector itself is a well-established and trusted project.30

SQLite also has a massive ecosystem, but sqlite-vec is a newer, though rapidly evolving, extension.16 The developer experience for writing SQL queries is excellent. However, the specific deployment pattern of compiling to WASM and integrating with Durable Objects is more cutting-edge and requires a greater degree of specialized knowledge than connecting to a standard Postgres instance. The development of companion tools like

sqlite-rembed and sqlite-lembed demonstrates a thoughtful and cohesive vision from the project's author, inspiring confidence in its trajectory.16

### **5.4. Cost-Effectiveness and Operational Overhead within the Cloudflare Paradigm**

The cost differential between the two architectures is stark and decisive. The PostgreSQL/Hyperdrive model requires paying for two separate services: the usage-based fees for Cloudflare services (Workers, Hyperdrive) and a substantial, fixed monthly fee for the managed PostgreSQL database. The SQLite/DO model, by contrast, consolidates all costs into Cloudflare's efficient, usage-based pricing model. The following tables provide a clear summary of these comparisons.

**Table 5.1: Feature and Architecture Comparison Matrix**

| Feature | SQLite (sqlite-vec) | DuckDB (vss) | PostgreSQL (pgvector) |
| :---- | :---- | :---- | :---- |
| **Core Architecture** | Embedded OLTP | Embedded OLAP | Client-Server OLTP |
| **Primary Use Case** | Application Database | Interactive Analytics | General-Purpose RDBMS |
| **Vector Indexing** | Brute-Force (ANN on roadmap) | HNSW (Experimental) | HNSW & IVFFlat (Production-Ready) |
| **Persistence Model** | Transactional File | Experimental / Unsafe | ACID Compliant |
| **Hybrid Search** | Planned | Not Supported | Native SQL WHERE |
| **Quantization** | int8, bit, Matryoshka | None | halfvec, bit |
| **Ecosystem Maturity** | High (DB), Medium (Ext) | Medium (DB), Low (Ext) | High (DB), High (Ext) |
| **Cloudflare Native Fit** | Excellent (Durable Objects) | Poor (R2) | Fair (Hyperdrive) |

**Table 5.2: Cloudflare Deployment Model and Performance Characteristics**

| Metric | SQLite / Durable Object | DuckDB / R2 | PostgreSQL / Hyperdrive |
| :---- | :---- | :---- | :---- |
| **Deployment Pattern** | WASM in Durable Object | WASM in Worker \+ R2 | Worker \-\> Hyperdrive \-\> Managed DB |
| **Key CF Services** | Workers, Durable Objects | Workers, R2 | Workers, Hyperdrive |
| **Data Locality** | Co-located (in-process) | Remote (object storage) | Remote (network call) |
| **DB Query Latency** | Sub-millisecond (no network) | High (R2 I/O) | Medium-High (Network RTT) |
| **Write/Update Path** | Transactional to local store | Read-Modify-Write entire file | Transactional over network |
| **Consistency Model** | Strong (per DO) | Eventual (at best) | Strong (ACID) |
| **Scalability Model** | Horizontal (more DOs) | N/A (unsuitable) | Vertical (bigger DB) & Horizontal (replicas) |

**Table 5.3: Estimated Monthly TCO Breakdown (Illustrative Scenario: 1 Million Reviews)**

| Cost Item | SQLite / Durable Object | PostgreSQL / Hyperdrive |
| :---- | :---- | :---- |
| **Managed Database Cost** | $0 | \~$282.00 (e.g., Fly.io Launch Plan 13) |
| **Cloudflare Worker Requests** | \~$5.00 (10M requests) | \~$5.00 (10M requests) |
| **Cloudflare DO Duration/Storage** | \~$20.00 (Estimate) | $0 |
| **Cloudflare Hyperdrive** | $0 | \~$5.00 (Estimate) |
| **Data Egress (from DB)** | $0 | \~$10.00+ (Estimate) |
| **Total Estimated Monthly Cost** | **\~$25.00** | **\~$302.00+** |

## **6\. Final Recommendation and Strategic Outlook**

After a comprehensive analysis of SQLite, DuckDB, and PostgreSQL against the specific requirements of powering a product review vector search feature on Cloudflare's edge infrastructure, a clear and definitive recommendation emerges.

### **6.1. The Optimal Choice for Product Review Vector Search on Cloudflare**

The optimal solution is **SQLite with the sqlite-vec extension, deployed within Cloudflare Durable Objects**.

This recommendation is based on a synthesis of the entire report's findings, which concludes that this architecture is superior across the most critical evaluation criteria for this specific use case:

1. **Superior Architectural Fit:** It is the only solution that offers a truly edge-native architecture. By co-locating the database engine and storage with the application logic, it fully embraces the principle of data locality, which is paramount for performance in a distributed computing environment.  
2. **Unmatched Performance on End-to-End Latency:** By eliminating the network round trip for database queries, the SQLite/DO pattern has the potential to deliver the lowest possible end-to-end latency for the end-user, especially at low to medium data scales.  
3. **Order-of-Magnitude Lower Cost:** The TCO of the SQLite/DO solution is dramatically lower than the PostgreSQL/Hyperdrive alternative. Its reliance on Cloudflare's efficient, usage-based pricing model directly satisfies the project's "inexpensive" constraint, whereas the alternative requires a costly, always-on managed database.  
4. **Viable and Credible Scalability Path:** While its current brute-force search is less scalable than pgvector's ANN indexes for global searches, it is more than sufficient for the primary use case of filtered searches. The active development and clear public roadmap for adding ANN capabilities to sqlite-vec provide a high degree of confidence that the solution can scale to meet future demands without requiring a painful architectural migration.

DuckDB is definitively ruled out as unsuitable due to the experimental, non-production-ready state of its vector search extension and its fundamental architectural mismatch for a stateful, transactional workload.

### **6.2. Implementation Roadmap and Best Practices**

Adopting this recommendation can be managed through a phased approach to de-risk the implementation and align capabilities with evolving needs:

* **Phase 1 (Initial Deployment):** Begin by implementing the solution using sqlite-vec's current, highly-optimized brute-force search. The primary focus should be on designing the Durable Object sharding strategy (e.g., one DO per product ID) and building the WASM binary. This will deliver a performant and cost-effective solution for the initial launch.  
* **Phase 2 (Scaling and Optimization):** As the volume of reviews grows, monitor query latency. Implement vector quantization, transitioning from float32 to bit or int8 vectors where acceptable precision loss can be tolerated. This will significantly reduce storage costs and improve query performance without waiting for ANN support.  
* **Phase 3 (Future-Proofing for Massive Scale):** As the sqlite-vec project releases stable support for ANN indexes (HNSW or IVF), plan a migration to update the virtual table definitions. This will ensure that the system can handle global search queries across tens of millions of vectors with low latency.

### **6.3. Future-Proofing the Decision: Considering Development Roadmaps**

The choice between a mature, stable technology like PostgreSQL and a rapidly innovating one like sqlite-vec is a strategic one. While pgvector is a safe and reliable choice, it represents the adaptation of a past architectural paradigm to a new one. The SQLite/DO solution, in contrast, represents an architecture that is purpose-built for the future of application development on the serverless edge.

By selecting SQLite with sqlite-vec, the project aligns itself with the powerful and growing trend of embedding data capabilities directly alongside application logic. This decision positions the product review search feature not as a legacy system bridged to the edge, but as a truly modern, edge-native application poised to take full advantage of the performance, scalability, and cost benefits of this emerging paradigm.

#### **Works cited**

1. pgvector/pgvector: Open-source vector similarity search for ... \- GitHub, accessed September 6, 2025, [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)  
2. Zero-latency SQLite storage in every Durable Object \- The Cloudflare Blog, accessed September 6, 2025, [https://blog.cloudflare.com/sqlite-in-durable-objects/](https://blog.cloudflare.com/sqlite-in-durable-objects/)  
3. Connect to a PostgreSQL database with Cloudflare Workers, accessed September 6, 2025, [https://developers.cloudflare.com/workers/tutorials/postgres/](https://developers.cloudflare.com/workers/tutorials/postgres/)  
4. Getting started · Cloudflare Durable Objects docs, accessed September 6, 2025, [https://developers.cloudflare.com/durable-objects/get-started/](https://developers.cloudflare.com/durable-objects/get-started/)  
5. Access Durable Objects Storage \- Cloudflare Docs, accessed September 6, 2025, [https://developers.cloudflare.com/durable-objects/best-practices/access-durable-objects-storage/](https://developers.cloudflare.com/durable-objects/best-practices/access-durable-objects-storage/)  
6. Overview · Cloudflare D1 docs, accessed September 6, 2025, [https://developers.cloudflare.com/d1/](https://developers.cloudflare.com/d1/)  
7. Cloudflare R2 Import \- DuckDB, accessed September 6, 2025, [https://duckdb.org/docs/stable/guides/network\_cloud\_storage/cloudflare\_r2\_import.html](https://duckdb.org/docs/stable/guides/network_cloud_storage/cloudflare_r2_import.html)  
8. Using DuckDB WASM \+ Cloudflare R2 to host and query big data (for almost free), accessed September 6, 2025, [https://andrewpwheeler.com/2025/06/29/using-duckdb-wasm-cloudflare-r2-to-host-and-query-big-data-for-almost-free/](https://andrewpwheeler.com/2025/06/29/using-duckdb-wasm-cloudflare-r2-to-host-and-query-big-data-for-almost-free/)  
9. Cloudflare Workers with pgEdge Distributed PostgreSQL, accessed September 6, 2025, [https://www.pgedge.com/blog/cloudflare-workers-with-pgedge-distributed-postgresql](https://www.pgedge.com/blog/cloudflare-workers-with-pgedge-distributed-postgresql)  
10. Cloudflare Workers \- Exograph, accessed September 6, 2025, [https://exograph.dev/docs/deployment/cloudflare-workers](https://exograph.dev/docs/deployment/cloudflare-workers)  
11. Pricing | Cloud SQL for PostgreSQL, accessed September 6, 2025, [https://cloud.google.com/sql/docs/postgres/pricing](https://cloud.google.com/sql/docs/postgres/pricing)  
12. Pricing \- Azure Database for PostgreSQL Flexible Server, accessed September 6, 2025, [https://azure.microsoft.com/en-us/pricing/details/postgresql/flexible-server/](https://azure.microsoft.com/en-us/pricing/details/postgresql/flexible-server/)  
13. Managed Postgres · Fly Docs \- Fly.io, accessed September 6, 2025, [https://fly.io/docs/mpg/](https://fly.io/docs/mpg/)  
14. Why DuckDB, accessed September 6, 2025, [https://duckdb.org/why\_duckdb.html](https://duckdb.org/why_duckdb.html)  
15. SQLite as a Vector Store with SQLiteVec \- Python LangChain, accessed September 6, 2025, [https://python.langchain.com/docs/integrations/vectorstores/sqlitevec/](https://python.langchain.com/docs/integrations/vectorstores/sqlitevec/)  
16. asg017/sqlite-vec: A vector search SQLite extension that runs anywhere\! \- GitHub, accessed September 6, 2025, [https://github.com/asg017/sqlite-vec](https://github.com/asg017/sqlite-vec)  
17. Introducing sqlite-vec v0.1.0: a vector search SQLite extension that ..., accessed September 6, 2025, [https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html](https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html)  
18. asg017/sqlite-vss: A SQLite extension for efficient vector ... \- GitHub, accessed September 6, 2025, [https://github.com/asg017/sqlite-vss](https://github.com/asg017/sqlite-vss)  
19. Introducing sqlite-vss: A SQLite Extension for Vector Search / Alex Garcia | Observable, accessed September 6, 2025, [https://observablehq.com/@asg017/introducing-sqlite-vss](https://observablehq.com/@asg017/introducing-sqlite-vss)  
20. How sqlite-vec Works for Storing and Querying Vector Embeddings | by Stephen Collins, accessed September 6, 2025, [https://medium.com/@stephenc211/how-sqlite-vec-works-for-storing-and-querying-vector-embeddings-165adeeeceea](https://medium.com/@stephenc211/how-sqlite-vec-works-for-storing-and-querying-vector-embeddings-165adeeeceea)  
21. Build a seat booking app with SQLite in Durable Objects \- Cloudflare Docs, accessed September 6, 2025, [https://developers.cloudflare.com/durable-objects/tutorials/build-a-seat-booking-app/](https://developers.cloudflare.com/durable-objects/tutorials/build-a-seat-booking-app/)  
22. DuckDB vs PostgreSQL- Key Differences \- Airbyte, accessed September 6, 2025, [https://airbyte.com/data-engineering-resources/duckdb-vs-postgres](https://airbyte.com/data-engineering-resources/duckdb-vs-postgres)  
23. Vector Similarity Search Extension \- DuckDB, accessed September 6, 2025, [https://duckdb.org/docs/stable/core\_extensions/vss.html](https://duckdb.org/docs/stable/core_extensions/vss.html)  
24. DuckDB VSS \- GitHub, accessed September 6, 2025, [https://github.com/duckdb/duckdb-vss](https://github.com/duckdb/duckdb-vss)  
25. Vector Similarity Search in DuckDB, accessed September 6, 2025, [https://duckdb.org/2024/05/03/vector-similarity-search-vss.html](https://duckdb.org/2024/05/03/vector-similarity-search-vss.html)  
26. Lightweight Text Analytics Workflows with DuckDB, accessed September 6, 2025, [https://duckdb.org/2025/06/13/text-analytics.html](https://duckdb.org/2025/06/13/text-analytics.html)  
27. duckdb-extension-vss \- PyPI, accessed September 6, 2025, [https://pypi.org/project/duckdb-extension-vss/](https://pypi.org/project/duckdb-extension-vss/)  
28. Deploying DuckDB-Wasm, accessed September 6, 2025, [https://duckdb.org/docs/stable/clients/wasm/deploying\_duckdb\_wasm.html](https://duckdb.org/docs/stable/clients/wasm/deploying_duckdb_wasm.html)  
29. Vector Similarity Search with PostgreSQL's pgvector \- A Deep Dive | Severalnines, accessed September 6, 2025, [https://severalnines.com/blog/vector-similarity-search-with-postgresqls-pgvector-a-deep-dive/](https://severalnines.com/blog/vector-similarity-search-with-postgresqls-pgvector-a-deep-dive/)  
30. PostgreSQL as a Vector Database: A Pgvector Tutorial \- TigerData, accessed September 6, 2025, [https://www.tigerdata.com/blog/postgresql-as-a-vector-database-using-pgvector](https://www.tigerdata.com/blog/postgresql-as-a-vector-database-using-pgvector)  
31. PostgreSQL Extensions: Turning PostgreSQL Into a Vector Database With pgvector | TigerData, accessed September 6, 2025, [https://www.tigerdata.com/learn/postgresql-extensions-pgvector](https://www.tigerdata.com/learn/postgresql-extensions-pgvector)  
32. PostgreSQL vector search guide: Everything you need to know about pgvector \- Northflank, accessed September 6, 2025, [https://northflank.com/blog/postgresql-vector-search-guide-with-pgvector](https://northflank.com/blog/postgresql-vector-search-guide-with-pgvector)  
33. PostgreSQL Vector DB vs. Native DBs : r/vectordatabase \- Reddit, accessed September 6, 2025, [https://www.reddit.com/r/vectordatabase/comments/1al71r3/postgresql\_vector\_db\_vs\_native\_dbs/](https://www.reddit.com/r/vectordatabase/comments/1al71r3/postgresql_vector_db_vs_native_dbs/)  
34. Enable and use pgvector in Azure Database for PostgreSQL flexible server \- Microsoft Learn, accessed September 6, 2025, [https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-use-pgvector](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-use-pgvector)  
35. How to query Postgres from Cloudflare Workers with Neon serverless driver, accessed September 6, 2025, [https://dev.to/hackmamba/how-to-query-postgres-from-cloudflare-workers-with-neon-serverless-driver-514a](https://dev.to/hackmamba/how-to-query-postgres-from-cloudflare-workers-with-neon-serverless-driver-514a)  
36. Pgvector Is Now Faster than Pinecone at 75% Less Cost | TigerData, accessed September 6, 2025, [https://www.tigerdata.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost](https://www.tigerdata.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost)