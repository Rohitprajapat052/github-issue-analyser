# GitHub Issue Analyzer

A FastAPI-based service that fetches GitHub repository issues and analyzes them using LLM (Groq API with Llama 3.3).

## 📋 Project Description

This application provides two main endpoints:
1. **`POST /scan`** - Fetches all open issues from a GitHub repository and caches them locally
2. **`POST /analyze`** - Analyzes cached issues using natural language prompts via LLM

## 🎯 Features

- ✅ Fetch all open GitHub issues with automatic pagination
- ✅ Persistent local caching using SQLite
- ✅ LLM-powered analysis using Groq API (Llama 3.3)
- ✅ Comprehensive error handling
- ✅ Rate limit handling for GitHub API
- ✅ Support for large repositories (100+ issues)
- ✅ Type-safe with Pydantic models
- ✅ Production-ready logging
- ✅ Auto-generated API documentation

## 🔧 Prerequisites

- **Python 3.10+**
- **Groq API Key** (free tier available at https://console.groq.com)
- **GitHub Personal Access Token** (optional, for higher rate limits)

## 🚀 Installation

### 1. Clone or navigate to project directory
```bash
cd github-issue-analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get Groq API Key

1. Go to https://console.groq.com/keys
2. Sign up (free)
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### 5. Setup environment variables
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Groq API Key (Required)
GROQ_API_KEY=gsk_your_actual_key_here

# GitHub Token (optional but recommended)
GITHUB_TOKEN=your_github_token_here

# Server Port
PORT=8000
```

**Note:** GitHub token is optional. Without it, you get 60 requests/hour. With it, you get 5000 requests/hour.

**To get GitHub token (optional):**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `public_repo`
4. Copy and paste in `.env`

## ▶️ Running the Server
```bash
python app/main.py
```

Server will start at: **http://localhost:8000**

## 📡 API Usage Examples

### Health Check
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "GitHub Issue Analyzer",
  "version": "1.0.0"
}
```

### 1. Scan a Repository
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"repo": "microsoft/vscode-python"}'
```

**Response:**
```json
{
  "repo": "microsoft/vscode-python",
  "issues_fetched": 87,
  "cached_successfully": true
}
```

### 2. Analyze Issues
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "microsoft/vscode-python",
    "prompt": "What are the top 3 most common issue types? Recommend what to prioritize."
  }'
```

**Response:**
```json
{
  "analysis": "Based on analysis of 87 issues:\n\n1. **Bug Reports (45%)** - Most common issues involve extension crashes and debugging failures...\n\n2. **Feature Requests (30%)** - Users requesting enhanced IntelliSense and better notebook support...\n\n3. **Documentation Issues (15%)** - Gaps in setup guides and API documentation...\n\nRecommendation: Prioritize critical crash bugs first as they block core functionality."
}
```

### Error Examples

**Repository not scanned:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "facebook/react", "prompt": "Analyze"}'
```
```json
{
  "detail": {
    "error": "Repository not yet scanned",
    "details": "Please scan the repository 'facebook/react' first using the /scan endpoint"
  }
}
```

**Invalid repo format:**
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"repo": "invalid-format"}'
```
```json
{
  "detail": {
    "error": "Invalid repository format",
    "details": "Repository must be in format 'owner/repository-name'"
  }
}
```

**Repository not found:**
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"repo": "fake/nonexistent"}'
```
```json
{
  "detail": {
    "error": "Repository 'fake/nonexistent' not found",
    "details": "Failed to fetch issues from GitHub API"
  }
}
```

## 📚 Interactive API Documentation

**Swagger UI:** http://localhost:8000/docs
- Try endpoints directly in browser
- See request/response schemas
- View example values

**ReDoc:** http://localhost:8000/redoc
- Alternative documentation format
- Better for reading

## 💾 Storage Choice Reasoning

**Why SQLite?**

1. **Durability** - Data persists across server restarts
2. **Simplicity** - No separate database server needed
3. **Inspectable** - Easy to query with CLI: `sqlite3 issues.db`
4. **Performance** - Fast for read-heavy workloads
5. **Zero Config** - Works out of the box
6. **Sufficient** - Perfect for this use case (not millions of concurrent writes)

For production at scale, consider PostgreSQL or MongoDB.

## 🧪 Testing

### Run automated tests
```bash
# Using pytest
pytest tests/ -v

# Or directly
python tests/test_endpoints.py
```

### Manual test scenarios
```bash
# 1. Test scan with real repo
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"repo": "pallets/click"}'

# 2. Test analyze
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "pallets/click", "prompt": "Summarize in 3 bullet points"}'

# 3. Test non-existent repo
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"repo": "fake/repo"}'

# 4. Test analyze before scan
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "nodejs/node", "prompt": "Test"}'

# 5. Inspect database
sqlite3 issues.db "SELECT COUNT(*) FROM issues;"
sqlite3 issues.db "SELECT repo, COUNT(*) FROM issues GROUP BY repo;"
```

### Good repos for testing

- **Small** (50-100 issues): `pallets/click`
- **Medium** (100-200 issues): `tiangolo/fastapi`
- **Note**: Very large repos (500+ issues) may hit GitHub pagination limits

## 🤖 AI Prompts Used During Development

### Initial Setup Prompts
1. "Create FastAPI project structure for GitHub issue analyzer with SQLite"
2. "Write SQLite schema for caching GitHub issues with repo indexing"
3. "Setup Pydantic models for scan and analyze endpoints with validation"

### Implementation Prompts
1. "Write Python function to fetch all GitHub issues with pagination and rate limit handling"
2. "Implement database operations with context manager for SQLite connections"
3. "Create Groq API integration for analyzing issues with llama-3.3-70b model"
4. "Handle LLM context limits when processing 100+ issues"

### Error Handling Prompts
1. "Add comprehensive error handling for GitHub API 403, 404, timeout errors"
2. "Implement retry logic for LLM API calls with max 2 attempts"
3. "Handle None values in GitHub issue body field"
4. "Validate repo format and provide clear error messages"

### Optimization Prompts
1. "Optimize issue formatting for LLM to avoid token limits"
2. "Add logging throughout application for debugging"
3. "Filter pull requests from GitHub issues endpoint results"

### Testing Prompts
1. "Create pytest test cases for FastAPI endpoints"
2. "Write tests for invalid input validation"
3. "Test error scenarios for analyze before scan"

## ⚠️ Known Limitations

1. **GitHub Rate Limits:** Without token, limited to 60 requests/hour
2. **Context Window:** Large repos (500+ issues) analyzed with most recent 50 only
3. **Pull Requests:** Filtered out (GitHub API includes PRs in issues endpoint)
4. **Concurrent Scans:** No queue system - sequential processing only
5. **Groq Rate Limits:** Free tier has request limits (check Groq dashboard)

## 📊 Database Schema
```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    repo TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    html_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_repo ON issues(repo);
```

## 🔍 Inspecting the Database
```bash
# Open database
sqlite3 issues.db

# Count total issues
SELECT COUNT(*) FROM issues;

# Show issues per repo
SELECT repo, COUNT(*) as count FROM issues GROUP BY repo;

# View recent issues
SELECT title, created_at FROM issues 
WHERE repo = 'pallets/click' 
ORDER BY created_at DESC 
LIMIT 5;

# Exit
.exit
```

## 📝 Project Structure
```
github-issue-analyzer/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Pydantic request/response models
│   ├── database.py          # SQLite operations
│   ├── github_client.py     # GitHub API integration
│   ├── llm_client.py        # Groq LLM integration
│   └── utils.py             # Helper functions
├── tests/
│   ├── __init__.py
│   └── test_endpoints.py    # API endpoint tests
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template for .env
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── issues.db               # SQLite database (auto-created)
```

## 🐛 Troubleshooting

**Server won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
PORT=8001 python app/main.py
```

**Groq API error:**
```bash
# Verify API key is set
cat .env | grep GROQ_API_KEY

# Test Groq API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

**Database locked:**
```bash
# Close any open sqlite3 sessions
# Delete and recreate
rm issues.db
python app/main.py
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**GitHub rate limit:**
```bash
# Add GITHUB_TOKEN to .env
# Get token from: https://github.com/settings/tokens
# Without token: 60 requests/hour
# With token: 5000 requests/hour
```

## 💡 Tips for Better Analysis Results

### Use Specific Prompts

**❌ Vague:**
```json
{"prompt": "Analyze these issues"}
```

**✅ Specific:**
```json
{"prompt": "Summarize in 3 bullet points: top issue categories and #1 priority"}
```

### Good Prompt Examples
```json
{"prompt": "What are the most critical bugs blocking users?"}
{"prompt": "List top 3 feature requests with highest demand"}
{"prompt": "In 100 words: main themes and what to fix first"}
{"prompt": "Categorize issues by type with percentages"}
```

## 🔄 Technology Choices

### Why Groq?
- ✅ Fast inference (cloud-based)
- ✅ Free tier available
- ✅ Production-ready API
- ✅ No local setup required
- ✅ Easy for others to test

### Why FastAPI?
- ✅ Async support for better performance
- ✅ Auto-generated API documentation
- ✅ Type validation with Pydantic
- ✅ Modern Python framework

### Why SQLite?
- ✅ Zero configuration
- ✅ File-based (portable)
- ✅ Perfect for this scale
- ✅ Easy to inspect and debug

## 📄 License

MIT License - Free to use for learning and interviews

---

**Built for job interview demonstration** 🚀

## 📞 Support

For issues or questions about this project:
1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Ensure Groq API key is valid and has remaining quota
4. Check server logs for detailed error messages

---

**Author:** Rohit Prajapat
**Purpose:** Technical Assessment / Interview Assignment
**Date:** February 2026