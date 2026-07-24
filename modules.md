Perfect. I think we've finally reached an architecture that is **simple, modular, scalable, and easy to explain in an interview.**

# 🚀 API Test Agent v2 - Final Module-wise Architecture (Locked)

---

# Module 1 — User Input

### Responsibility

Collect the minimum information required to start.

### Input

* Base URL / Swagger URL *(Required)*

Example

```text
https://petstore.swagger.io/v2/swagger.json
```

### Output

```python
BaseConfig
```

Contains

* base_url

---

# Module 2 — OpenAPI Crawler

### Responsibility

Download the OpenAPI/Swagger specification.

### Input

```
BaseConfig
```

### Process

* Fetch swagger.json
* Validate JSON
* Return raw specification

### Output

```
Raw OpenAPI JSON
```

---

# Module 3 — Parser + Extractor

### Responsibility

Extract only the useful metadata with minimal complexity.

### Extract

* Path
* Method
* Summary
* Description
* Tags
* Parameters
* Request Body Schema
* Response Codes
* Authentication Requirement
* Content-Type

### Output

```
Endpoint Objects
```

Example

```python
Endpoint(
    path="/pet/{petId}",
    method="GET",
    summary="Find pet",
    tags=["pet"],
    auth_required=True,
    auth_type="Bearer",
    content_type="application/json",
    parameters=[...],
    request_schema={...},
    responses=[200,404]
)
```

---

# Module 4 — Flatten Parser

### Responsibility

Convert nested OpenAPI objects into a flat list for simpler downstream processing.

### Input

```
Endpoint Objects
```

### Output

```
Flat Endpoint List
```

Every endpoint becomes one independent object.

---

# Module 5 — Endpoint Safety Filter

### Responsibility

Remove unsupported and risky endpoints before presenting them to the user.

## Authentication Filter

Supported

* None
* API Key
* Basic Auth
* Bearer Token / JWT

Hidden

* OAuth2
* OpenID Connect
* Mutual TLS
* AWS Signature
* Custom Auth

---

## Risk Filter

Hide endpoints containing keywords like

```
payment
checkout
refund
wallet
bank
withdraw
transfer
payout
invoice
reset
drop
shutdown
deleteAll
```

Each endpoint gets

```python
supported=True/False

unsupported_reason="OAuth2"

risk_level="safe"
```

### Output

```
Safe Endpoint List
```

---

# Module 6 — Endpoint Selection UI

### Responsibility

Show discovered endpoints to the user.

Grouped by

* Authentication Required
* Login/Register Pages
* Tags
* Summary

Example

```
☐ GET /users

☐ POST /login

☐ GET /orders

☐ POST /pet
```

User selects endpoints to test.

### Output

```
Selected Endpoints
```

---

# Module 7 — Credential Collector

### Responsibility

Ask only for credentials required by the selected endpoints.

Examples

If selected endpoint needs

Bearer

↓

Ask

```
JWT Token
```

If API Key

↓

Ask

```
API Key
```

If Basic Auth

↓

Ask

```
Username

Password
```

If no authentication

↓

Ask nothing.

Credentials are **never sent to the AI**.

### Output

```
Credential Object
```

---

# Module 8 — AI Test Generator

### Responsibility

Generate only meaningful, high-value test cases.

### Input

* Selected Endpoints
* Endpoint Metadata

Not

* Credentials

### AI Rules

* Batch endpoints
* Pydantic JSON Output
* Strict schema validation
* Critical test cases only
* No hallucinated endpoints

### Output

```python
StructuredTestCase
```

Contains only

* URL
* Method
* Headers Template
* Request Body
* Expected Status

---

# Module 9 — Test Executor

### Responsibility

Execute structured test cases.

### Input

* Structured Test Cases
* Credentials

### Engine

```
httpx.AsyncClient
```

Supports

* JSON
* Multipart
* Form Data
* Query Parameters
* Headers

Credentials injected here.

AI never sees secrets.

### Output

```
Execution Results
```

---

# Module 10 — Validator

### Responsibility

Simple evaluation.

Checks only

## Status Code

Flexible matching

Instead of

```
Expected == 200
```

Use

```
Allowed

200

201

202

204
```

depending on OpenAPI.

---

## Response Time

Simple SLA

```
< 2 sec

Healthy

> 2 sec

Slow
```

No strict schema validation in MVP.

### Output

```
Validation Results
```

---

# Module 11 — Report Generator

### Responsibility

Generate downloadable reports.

Formats

* HTML
* Markdown
* PDF

Include

* Health Score
* Pass Rate
* Failed APIs
* Slow APIs
* Endpoint Summary

No AI here.

---

# Module 12 — AI Fix Suggestion (On Demand)

### Responsibility

Only triggered when user clicks

```
Suggest Fix
```

### Frontend sends

* Endpoint
* Request
* Response
* Error
* Validation Result

Only then

↓

Gemini

↓

Returns

```
Possible Cause

Suggested Fix

Code Example

Best Practice
```

This prevents unnecessary API usage and keeps costs low.

---

# 🔒 Security Boundary

```
User Credentials
        │
        ▼
 Test Executor
        │
        ├──────────────┐
        │              │
        ▼              ▼
 Validation      AI Generator
                     ▲
                     │
          Endpoint Metadata Only
```

**Credentials never enter the AI layer.**

---

# Final Pipeline

```text
1. User Input
        │
2. OpenAPI Crawler
        │
3. Parser + Extractor
        │
4. Flatten Parser
        │
5. Endpoint Safety Filter
        │
6. Endpoint Selection UI
        │
7. Credential Collector
        │
8. AI Test Generator
        │
9. Async Test Executor
        │
10. Validator
        │
11. Report Generator
        │
12. AI Fix Suggestion (On Demand)
```

## Why this architecture is stronger than the previous one

* **No orchestrator layer**; each module has a single responsibility.
* **User-driven workflow**: credentials are requested only after endpoint selection.
* **AI is isolated**: it generates tests and explains failures, but never executes requests or receives secrets.
* **Safer by design**: unsupported authentication and high-risk endpoints are filtered before execution.
* **Minimal complexity**: each module has a clear input and output, making the codebase easier to maintain, test, and explain during an internship demo or technical interview.
