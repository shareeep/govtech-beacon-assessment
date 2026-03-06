# MUHAMMAD SHARIFF BIN ABDUL RASHID

+65 9180 0745 | muhd.shariff01@gmail.com | [LinkedIn](https://linkedin.com/in/shariff-rashid) | [GitHub](https://github.com/shareeep) | [shariffrashid.com](https://shariffrashid.com)

---

## EDUCATION

**Singapore Management University** | Singapore
**BSc Information Systems (Product Development), 2nd Major in CS (Artificial Intelligence)** | Aug 2023 – May 2027

- Relevant Coursework: Software Project Management, Enterprise Solution Development, Web App Development, Object-Oriented Programming, Generative AI with LLMs, AI Safety
- Data Science & AI Mentee in the 11th DAP; SMU Business Analytics & Intelligence Club

---

## EXPERIENCE

### HTX (Home Team Science & Technology Agency) | Singapore

**Software Engineering Intern @ xDigital (AI Products Team)** | Jan 2026 – Present

- Developing features across a full-stack TypeScript codebase for an AI-powered procurement report system serving Whole-of-Government (WoG), contributing to report generation workflows
- Independently building a custom MCP server exposing the platform's report creation, upload, and lookup functionality as tool contracts for future agentic AI integration
- Implemented Playwright E2E test suites in GitLab CI workflows to enforce regression coverage across all product features and critical user flows, supporting the product's launch in late January
- **Technologies:** TypeScript, React, NestJS, Prisma, Playwright, GitLab CI, MCP

### Zora Health | Singapore

**Product Intern** | May 2024 – July 2024

- Executed continuous feature delivery for a B2B2C Learning Experience Platform against a strategic roadmap, prioritizing development tasks and validating technical feasibility directly with engineering
- Automated 90% of the content production pipeline by developing a custom Python script, significantly reducing manual effort and accelerating feature development cycles

---

## PROJECTS

<!-- ============================================================
     TIER 1: PRIMARY PROJECTS — SWE / AI ENGINEER FOCUSED
     Pick 4–5 of these depending on the role you're applying for.
     ============================================================ -->

### Privacy-Focused Agentic Anonymiser | [Project Page](https://shariffrashid.com/projects/pii-anonymisation-gen-ai) | Oct 2025 – Nov 2025

_An end-to-end anonymisation pipeline integrating NER, generative anonymisation, and adversarial optimisation into a single workflow. (Grade: A+)_

- Built a fully local, privacy-preserving multi-agent system with Ollama, chaining NER detection, generative replacement, and adversarial re-identification to boost anonymisation from 87% to 97%
- Fine-tuned a BERT NER model (Micro-F1 0.87) on OpenPII for PII span detection, and implemented Automatic Prompt Engineering with evolutionary mutation to optimise prompts
- Developed a FastAPI backend orchestrating LangChain pipelines and Transformers inference, with a Next.js frontend supporting DOCX upload and format-preserved download
- **Technologies:** Python, FastAPI, Next.js, LangChain, Transformers, NLTK, Mistral 7B, Ollama, BERT NER, Clinical-Longformer, DOCX Processing

### CampusG – Food Delivery Platform | [Source Code](https://github.com/shareeep/campusg) | Feb 2025 – Apr 2025

_A full-stack, microservices-based food delivery web application connecting customers and delivery runners. (Grade: A+)_

- Architected and developed containerized microservices (User, Order, Payment, Composites) using Docker, each with a dedicated PostgreSQL database to ensure service autonomy and scalability
- Engineered data consistency across distributed transactions by implementing the Saga orchestration pattern with Temporal and Kafka, including compensation logic for rollbacks
- Integrated payments using the Stripe Connect API to handle payments directly between customers and runners, using Clerk for secure user authentication
- **Technologies:** Python, Flask, Docker, PostgreSQL, Apache Kafka, Temporal, Stripe Connect, Clerk, Grafana, OutSystems REST API

### Phishing URL Detection | [Project Page](https://shariffrashid.com/projects/phishing-url-detection) | Mar 2025 – Apr 2025

_An end-to-end ML-powered phishing URL detection system with explainable predictions. (Grade: A+)_

- Trained a character-level CNN (3 convolutional blocks with batch normalisation) for phishing URL classification, achieving 94.8% accuracy on a 235K-sample dataset
- Engineered a multi-category feature set spanning lexical, host-based, and content-based signals including domain age, subdomain count, and suspicious token frequency
- Built interpretable attention heatmaps visualising per-character contributions to phishing predictions, validated against real-world Singapore government impersonation URLs
- **Technologies:** Python, PyTorch, Scikit-learn, Pandas, NumPy, Matplotlib, WHOIS API

### Aircraft Delay Propagation Analysis (Big Data on AWS) | [Project Page](https://shariffrashid.com/projects/aircraft-big-data) | Sep 2025 – Nov 2025

_A big data pipeline on AWS to analyse how individual aircraft propagate delays across the U.S. air network. (Grade: A)_

- Built an end-to-end big data pipeline on AWS processing 120M+ flight records with PySpark to identify aircraft that act as "network multipliers" for cascading delays
- Developed a two-stage cascade prediction model (Gradient Boosted Trees + MLP) using Spark MLlib, handling extreme class imbalance (95/5 split) to filter and classify cascade severity
- Designed a composite risk scoring system revealing that only 0.4% of aircraft cause disproportionate network-wide delays, enabling targeted operational interventions
- **Technologies:** PySpark, AWS (S3, Glue, EMR, Athena), Spark MLlib, Pandas, Matplotlib

### ESMOS – Cloud Migration (SaaS → IaaS) | [Project Page](https://shariffrashid.com/projects/odoo-migration-esmos) | Feb 2025 – Apr 2025

_An IaaS migration project for a subscription-based meal ordering system to improve scalability and security. (Grade: A)_

- Architected the migration from Odoo SaaS to Azure Kubernetes Service (AKS), designing a scalable IaaS architecture that reduced infrastructure costs by over 40%
- Implemented Horizontal Pod Autoscaling for 10,000+ daily users and resolved session-affinity issues with cookie-based sticky sessions, achieving 0% error rate during Locust load testing
- Established a DevSecOps pipeline using K8s YAML manifests for IaC, Cert Manager for HTTPS, RBAC/NSG for access control, and Prometheus + Grafana for observability, ticketing on Jira
- **Technologies:** Azure AKS, Azure PostgreSQL, Docker, Kubernetes, Prometheus, Grafana, Locust, Cert Manager, Jira, Git

### Hate Speech Classification with BERT | [Project Page](https://shariffrashid.com/projects/hate-speech-classification) | Oct 2025

_An investigation into fine-tuning strategies (Full vs. LoRA) for hate speech classification using transformer models._

- Fine-tuned RoBERTa-base on HateXplain (15K+ samples) achieving Macro F1 0.689, outperforming domain-specific baselines including HateBERT and a pre-trained community model
- Compared full fine-tuning vs. LoRA (0.71% of parameters) with weighted cross-entropy loss, showing full fine-tuning yields +9% F1 over LoRA for smaller encoder models
- Benchmarked 4 transformer architectures (RoBERTa, BERT, HateBERT, ELECTRA) under identical conditions, establishing RoBERTa generalises best for toxicity classification
- **Technologies:** Python, PyTorch, Hugging Face Transformers, LoRA (PEFT), Weights & Biases

### Sarcasm-Aware Hate Speech Detection (DAP Project) | [Project Page](https://shariffrashid.com/projects/hate-speech-dap) | Aug 2025 – Nov 2025

_A multi-task learning system that jointly models sarcasm and hate speech for improved implicit hate detection._

- Designed a shared-encoder multi-task architecture (BERT) with dual prediction heads — hate speech (3-class) and sarcasm (binary) — modelling the intersection of ironic tone and toxicity
- Implemented agentic classification using local LLMs (LLaMA-3-8B, Mistral via Ollama) with chain-of-thought prompting for step-by-step sarcasm-to-hate reasoning
- Explored KG-RAG to enrich classification with entity-level knowledge of slurs, dog whistles, and cultural references for improved implicit hate detection
- **Technologies:** Python, PyTorch, Hugging Face Transformers, LLaMA-3-8B, Mistral, Ollama, Neo4j, LangChain

<!-- ============================================================
     TIER 2: SUPPORTING PROJECTS
     Include selectively for full-stack, leadership, or design roles.
     ============================================================ -->

### BreadTalk Digital Transformation | [Project Page](https://shariffrashid.com/projects/breadtalk-digital-transformation) | Feb 2025 – Apr 2025

_An AI-driven digital transformation proposal for BreadTalk featuring computer vision checkout and personalised recommendations. (Grade: A)_

- Trained YOLOv11s on 324 hand-labelled images (LabelStudio) across 6 bread classes, achieving Macro F1 0.88, and deployed a real-time visual checkout demo with a live webcam feed
- Built a neural collaborative filtering recommender (AutoRec) to generate personalised product suggestions from purchase history data
- Designed mobile-first UI/UX prototypes in Figma for three integrated features (mobile ordering, AI checkout, recommendations) as part of a digital transformation roadmap
- **Technologies:** Python, YOLOv11s, LabelStudio, PyTorch, Figma

### Software Project Management – Agile Scrum | [Project Page](https://shariffrashid.com/projects/spm-agile-project-mgmt) | Aug 2025 – Nov 2025

_Scrum Master and Developer for a microservices-based application delivered over 3 sprints._

- Served as Scrum Master, facilitating sprint planning (Planning Poker), daily standups, reviews, and retrospectives (4Ls framework) across 3 two-week sprints
- Implemented a two-layer CI pipeline: local pre-push hooks for build validation (~3-4 min), backed by GitHub Actions for parallel testing across 11 services with 70% coverage enforcement
- Delivered 8 Playwright E2E test suites and unit tests for 14/17 microservices (Flask), evolving the team from manual testing (Sprint 1) to full automation (Sprint 3)
- **Technologies:** Python, Flask, Playwright, GitHub Actions, Jira, Confluence

### PetConnect – Social Platform for Pet Owners | [Source Code](https://github.com/shareeep/fishmuggers-is216) | Sep 2024 – Nov 2024

_A full-stack web application connecting pet owners with real-time chat, events discovery, and social features._

- Developed a Vue 3 SPA with Express.js backend and Firebase (Firestore, Auth, Cloud Storage), featuring real-time chat, event discovery with Google Maps API, and a social feed
- Deployed on Render with modular Express routers for posts, events, users, and friends management
- **Technologies:** Vue 3, Express.js, Firebase (Firestore, Auth, Cloud Storage), Google Maps API, Render

### DAP Co-Learning – Regression Workshop | Jan 2026

_Designed and facilitated a hands-on gradient descent workshop for 40+ mentees in the SMU DAP program._

- Developed interactive web-based demos using Gemini Canvas to visualise gradient descent mechanics (loss reduction, parameter updates) for 40+ mentees
- Co-designed workshop content with senior DAP mentors, covering linear regression fundamentals with a two-parameter (slope + bias) example
- **Technologies:** Gemini Canvas, Python, NumPy, Matplotlib

---

<!-- ============================================================
     USAGE GUIDE FOR THIS MASTER RESUME:
     
     SWE Roles: PII Anonymiser, CampusG, ESMOS, SPM Agile, PetConnect
     AI/ML Roles: PII Anonymiser, Hate Speech (BERT), Hate Speech (DAP), Phishing URL, Aircraft Big Data
     Full-Stack: CampusG, PetConnect, PII Anonymiser, SPM Agile
     Data Engineering: Aircraft Big Data, ESMOS
     Cloud/DevOps: ESMOS, CampusG, Aircraft Big Data, SPM Agile
     CV/NLP: PII Anonymiser, Hate Speech (both), BreadTalk, Phishing URL
     ============================================================ -->
