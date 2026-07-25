# 🚀 TestPilot AI 
**Your Intelligent Co-Pilot for API Contract Testing**

TestPilot AI is an automated, AI-driven API testing platform. Instead of writing tests manually, you simply provide your API's base URL. TestPilot AI will automatically discover your endpoints, generate intelligent test payloads, execute them against your server, and use AI to analyze and explain any failures in plain English.

## ✨ Features
- **🔍 Auto-Discovery:** Automatically scans and parses your OpenAPI/Swagger documentation (`/openapi.json`).
- **🧠 AI Test Generation:** Uses Google's Gemini AI to generate strict, schema-compliant JSON payloads for testing.
- **⚡ One-Click Execution:** Runs all generated tests simultaneously and aggregates the results (Status Codes, Response Times, etc.).
- **🛡️ Intelligent Normalization:** Automatically fixes casing and spelling hallucinations in AI-generated payloads to strictly match your OpenAPI schema properties.
- **🤖 AI Failure Explainer:** If an endpoint fails (e.g., `400 Bad Request`, `401 Unauthorized`), the AI analyzes the exact request body, response body, and status code to tell you exactly *why* it failed.
- **📊 Rich Reporting:** Generates downloadable, beautiful HTML health reports for QA teams.

## 🛠️ Tech Stack
- **Frontend:** React (Vite), TypeScript, Tailwind CSS, Lucide Icons, React-Markdown.
- **Backend:** Python, FastAPI, Pydantic, HTTPX.
- **AI Integration:** Google Gemini Pro SDK (`google-genai`).

## 🚀 Getting Started

### 1. Backend Setup
The backend handles the API discovery, AI generation, and HTTP execution.

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install "fastapi[standard]" pydantic email-validator httpx python-dotenv google-genai

# Create a .env file and add your Gemini API Key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run the backend server
uvicorn main:app --reload
```
The backend will run on `http://127.0.0.1:8000`.

### 2. Frontend Setup
The frontend provides a beautiful dashboard to manage your tests.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
The frontend will run on `http://localhost:5173`.

## 🧪 How to use the Dummy Endpoints
This project comes with two intentional dummy endpoints designed to test the AI Explainer functionality:
- `POST /api/test/login` (Always fails with 401)
- `POST /api/test/register` (Always fails with 400)

**To test them:**
1. Open the TestPilot AI frontend.
2. Enter `http://127.0.0.1:8000` as the Base URL and click **Discover**.
3. Select the two dummy endpoints.
4. Click **Proceed to Testing** -> **Execute All**.
5. Once they fail, click the **Fix it with AI** button to see the AI analyze the intentional failures!

---
*Built with ❤️ for automated QA.*
