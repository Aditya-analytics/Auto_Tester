# 🚀 API Test Agent Report

## 📊 Run Metadata
- **API Name:** Swagger Petstore
- **Endpoints Discovered:** 20
- **Endpoints Tested:** 20
- **Coverage:** 100%
- **Operations:** POST 7, PUT 2, GET 8, DELETE 3
- **Tests Generated:** 38
- **Execution Time:** 10.9 s
- **Generated On:** 24 Jul 2026, 16:48:01

## Executive Summary
⚠️ AI summary unavailable (quota exceeded).
**Fallback Summary:**
- 11 backend crashes detected.
- 2 schema violations detected.
- 11 validation failures.
- See detailed breakdown below.

**Total Tests:** 38 | **Passed:** 14 ✅ | **Failed:** 24 ❌

### 🏥 API Health Score: 47/100

---

## 📈 Endpoint Summary Table

| Endpoint | Health Status |
| -------- | ------------- |
| `POST /pet` | 🔴 Backend Crash |
| `POST /store/order` | 🔴 Backend Crash |
| `POST /user/createWithList` | 🔴 Backend Crash |
| `POST /user/createWithArray` | 🔴 Backend Crash |
| `POST /user` | 🔴 Backend Crash |
| `GET /pet/findByStatus` | ✅ Healthy |
| `GET /pet/findByTags` | ✅ Healthy |
| `GET /pet/{petId}` | 🟡 Schema Issue |
| `GET /store/inventory` | ✅ Healthy |
| `GET /store/order/{orderId}` | ✅ Healthy |
| `GET /user/{username}` | ❓ False Positive |
| `GET /user/login` | 🟡 Schema Issue |
| `GET /user/logout` | ✅ Healthy |
| `POST /pet/{petId}/uploadImage` | 📝 Doc Mismatch |
| `PUT /pet` | 🔴 Backend Crash |
| `POST /pet/{petId}` | 📝 Doc Mismatch |
| `PUT /user/{username}` | 🔴 Backend Crash |
| `DELETE /pet/{petId}` | ✅ Healthy |
| `DELETE /store/order/{orderId}` | ✅ Healthy |
| `DELETE /user/{username}` | ❓ False Positive |

## 🚨 Critical Failures (Backend Bugs)
- 🚨 **CRITICAL** | Bad data type POST (`POST /pet`)
  - Status Mismatch: Expected one of [415], got 500.
- 🚨 **CRITICAL** | Bad data type POST (`POST /store/order`)
  - Status Mismatch: Expected one of [415], got 500.
- 🚨 **CRITICAL** | Valid POST Request (Generic Body) (`POST /user/createWithList`)
  - Status Mismatch: Expected one of [200], got 500.
- 🚨 **CRITICAL** | Negative POST Request (Empty Body) (`POST /user/createWithList`)
  - Status Mismatch: Expected one of [400], got 500.
- 🚨 **CRITICAL** | Bad data type POST (`POST /user/createWithList`)
  - Status Mismatch: Expected one of [415], got 500.
- 🚨 **CRITICAL** | Valid POST Request (Generic Body) (`POST /user/createWithArray`)
  - Status Mismatch: Expected one of [200], got 500.
- 🚨 **CRITICAL** | Negative POST Request (Empty Body) (`POST /user/createWithArray`)
  - Status Mismatch: Expected one of [400], got 500.
- 🚨 **CRITICAL** | Bad data type POST (`POST /user/createWithArray`)
  - Status Mismatch: Expected one of [415], got 500.
- 🚨 **CRITICAL** | Bad data type POST (`POST /user`)
  - Status Mismatch: Expected one of [415], got 500.
- 🚨 **CRITICAL** | Bad data type PUT (`PUT /pet`)
  - Status Mismatch: Expected one of [415], got 500.
- 🚨 **CRITICAL** | Bad data type PUT (`PUT /user/{username}`)
  - Status Mismatch: Expected one of [415], got 500.

## 🧩 Schema Violations
- 🧩 **SCHEMA MISMATCH** | Valid GET Request (`GET /pet/{petId}`)
  - Schema Violation: 'name' is a required property<br>Expected: `N/A` | Received: `dict`<br>Actual Response Snippet: `{'id': 9223372036854775807, 'photoUrls': [], 'tags': []}`
- 🧩 **SCHEMA MISMATCH** | Valid GET Request (`GET /user/login`)
  - Schema Violation: {'code': 200, 'type': 'unknown', 'message': 'logged in user session:1784891890599'} is not of type 'string'<br>Expected: `string` | Received: `dict`<br>Actual Response Snippet: `{'code': 200, 'type': 'unknown', 'message': 'logged in user session:1784891890599'}`

## 📝 Documentation Mismatches
- 📝 **DOC MISMATCH** | Negative POST Request (Empty Body) (`POST /pet`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Negative POST Request (Empty Body) (`POST /store/order`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Negative POST Request (Empty Body) (`POST /user`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Negative POST Request (Empty Body) (`POST /pet/{petId}/uploadImage`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Bad data type POST (`POST /pet/{petId}/uploadImage`)
  - Status Mismatch: Expected one of [415], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Negative PUT Request (Empty Body) (`PUT /pet`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Negative POST Request (Empty Body) (`POST /pet/{petId}`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Bad data type POST (`POST /pet/{petId}`)
  - Status Mismatch: Expected one of [415], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)
- 📝 **DOC MISMATCH** | Negative PUT Request (Empty Body) (`PUT /user/{username}`)
  - Status Mismatch: Expected one of [400], got 200. (Likely documentation inconsistency. API accepted an invalid payload.)


## ❓ Potential False Positives (Resource Missing)
- ❓ **FALSE POSITIVE** | Valid GET Request (`GET /user/{username}`)
  - Status Mismatch: Expected one of [200], got 404. (Likely resource missing)
- ❓ **FALSE POSITIVE** | Valid DELETE Request (`DELETE /user/{username}`)
  - Status Mismatch: Expected one of [200], got 404. (Likely resource missing)


## ✅ Passed Tests
- ✅ **PASS** | Valid POST Request (Generic Body) (`POST /pet`)
- ✅ **PASS** | Valid POST Request (Generic Body) (`POST /store/order`)
- ✅ **PASS** | Valid POST Request (Generic Body) (`POST /user`)
- ✅ **PASS** | Valid GET Request (`GET /pet/findByStatus`)
- ✅ **PASS** | Valid GET Request (`GET /pet/findByTags`)
- ✅ **PASS** | Valid GET Request (`GET /store/inventory`)
- ✅ **PASS** | Valid GET Request (`GET /store/order/{orderId}`)
- ✅ **PASS** | Valid GET Request (`GET /user/logout`)
- ✅ **PASS** | Valid POST Request (Generic Body) (`POST /pet/{petId}/uploadImage`)
- ✅ **PASS** | Valid PUT Request (Generic Body) (`PUT /pet`)
- ✅ **PASS** | Valid POST Request (Generic Body) (`POST /pet/{petId}`)
- ✅ **PASS** | Valid PUT Request (Generic Body) (`PUT /user/{username}`)
- ✅ **PASS** | Valid DELETE Request (`DELETE /pet/{petId}`)
- ✅ **PASS** | Valid DELETE Request (`DELETE /store/order/{orderId}`)
