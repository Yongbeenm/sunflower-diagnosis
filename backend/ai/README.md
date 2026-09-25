# Sunflower AI Module

Local AI integration for the Sunflower Expert System using Ollama.

## Overview

This module adds AI assistance to the existing rule-based expert system **without replacing it**. The AI helps with:

1. **Natural language symptom extraction** - Users describe symptoms in English or Khmer
2. **Conversational chatbot** - Answer questions and guide users
3. **Image analysis** - Analyze plant disease photos using vision models
4. **Expert knowledge assistance** - Help agronomists create disease entries
5. **Duplicate detection** - Identify potential duplicate disease entries

### Architecture

```
User Natural Language
        ↓
    Local AI (Ollama)
        ↓
  Structured Symptoms
        ↓
Existing Expert System ← The AI does NOT replace this
        ↓
   Rule-Based Diagnosis
        ↓
    Results + AI Explanation
        ↓
        User
```

**Important:** The final diagnosis always comes from the existing expert system in `app/services/engine/`. The AI only assists with:
- Understanding natural language
- Extracting symptoms
- Explaining results
- Helping experts create knowledge

## Setup

### 1. Install Ollama

On macOS:
```bash
brew install ollama
```

Or download from: https://ollama.ai/download

### 2. Start Ollama Server

```bash
ollama serve
```

This starts Ollama on `http://localhost:11434`

### 3. Pull Required Models

For text-only features:
```bash
ollama pull qwen2.5:7b
```

For vision features (image analysis):
```bash
# Note: Vision models require more resources
ollama pull qwen2-vl:7b   # Recommended for vision

# Or use smaller model if needed:
ollama pull qwen2-vl:4b
```

Alternative models:
- `llama3.2:3b` - Faster, less accurate
- `mistral:7b` - Good general purpose
- `llava:7b` - Alternative vision model

### 4. Configure Environment

Add to your `.env`:

```env
# Enable AI features
AI_ENABLED=true
AI_VISION_ENABLED=true

# Ollama connection
OLLAMA_HOST=http://localhost:11434

# Models (must match what you pulled)
AI_MODEL=qwen2.5:7b
AI_VISION_MODEL=qwen2-vl:7b

# Timeouts
AI_TIMEOUT=120
AI_VISION_TIMEOUT=180

# Temperature (0.0 = deterministic, 1.0 = creative)
AI_TEMPERATURE=0.7
AI_EXTRACTION_TEMPERATURE=0.3
```

### 5. Install Python Dependencies

```bash
cd backend
pip install -e ".[dev]"
```

This installs `httpx` for Ollama communication.

### 6. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

## API Endpoints

All endpoints are under `/api/v1/ai/`

### Health Check

```http
GET /api/v1/ai/health
```

Returns Ollama availability and loaded models.

### User Chatbot

```http
POST /api/v1/ai/chat
Content-Type: application/json

{
  "message": "My sunflower leaves have brown spots",
  "locale": "en",
  "conversation_id": "optional-uuid"
}
```

### Symptom Extraction

```http
POST /api/v1/ai/extract-symptoms
Content-Type: application/json

{
  "message": "Leaves turning yellow with brown circular spots",
  "locale": "en"
}
```

Returns structured symptom data and mapped symptom IDs.

### AI-Assisted Diagnosis

```http
POST /api/v1/ai/diagnose
Content-Type: application/json

{
  "message": "My sunflower has yellow leaves with brown spots",
  "locale": "en",
  "image_base64": "optional base64 image"
}
```

**Workflow:**
1. AI extracts symptoms from text/image
2. Maps to database symptom IDs
3. **Existing expert system** performs diagnosis
4. AI generates natural language explanation

### Image Analysis

```http
POST /api/v1/ai/analyze-image
Content-Type: application/json

{
  "image_base64": "base64-encoded-image-data",
  "locale": "en",
  "additional_context": "optional context"
}
```

Returns visual observations (NOT a diagnosis).

### Expert: Generate Disease Draft

```http
POST /api/v1/ai/expert/disease-draft
Content-Type: application/json
Authorization: Bearer <expert-token>

{
  "description": "Early blight causes brown spots on lower leaves...",
  "locale": "en",
  "image_base64": "optional"
}
```

Returns AI-generated disease knowledge **DRAFT** requiring expert approval.

### Expert: Check Duplicates

```http
POST /api/v1/ai/expert/duplicate-check
Content-Type: application/json
Authorization: Bearer <expert-token>

{
  "disease_name": "Tomato Brown Spot",
  "description": "Causes brown lesions on leaves",
  "symptoms": ["brown spots", "leaf lesions"]
}
```

## Module Structure

```
ai/
├── __init__.py
├── config.py                   # AI configuration
├── README.md                   # This file
│
├── schemas/
│   └── ai_schemas.py          # Pydantic request/response models
│
├── services/
│   ├── ollama_service.py      # Core Ollama communication
│   ├── vision_service.py      # Image analysis
│   ├── symptom_extractor.py  # NLP → structured symptoms
│   ├── chatbot_service.py     # Conversational AI
│   ├── disease_assistant.py   # Expert knowledge assistance
│   ├── prompt_loader.py       # Prompt template utilities
│   └── json_parser.py         # Robust JSON extraction
│
└── prompts/
    ├── symptom_extraction.txt # Symptom extraction prompt
    ├── chatbot.txt            # Chatbot system prompt
    ├── disease_expert.txt     # Disease draft generation
    ├── image_analysis.txt     # Vision analysis prompt
    └── duplicate_check.txt    # Duplicate detection prompt
```

## Testing

### 1. Check Health

```bash
curl http://localhost:8000/api/v1/ai/health
```

Should return:
```json
{
  "ollama_available": true,
  "model_loaded": "qwen2.5:7b",
  "status": "ready"
}
```

### 2. Test Symptom Extraction

```bash
curl -X POST http://localhost:8000/api/v1/ai/extract-symptoms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "My sunflower leaves have brown circular spots and are turning yellow",
    "locale": "en"
  }'
```

### 3. Test Chat

```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What causes brown spots on sunflower leaves?",
    "locale": "en"
  }'
```

### 4. Test Full Diagnosis

```bash
curl -X POST http://localhost:8000/api/v1/ai/diagnose \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "My sunflower has brown spots on older leaves that are spreading",
    "locale": "en"
  }'
```

## Troubleshooting

### "Cannot connect to Ollama"

1. Check if Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

2. Start Ollama:
```bash
ollama serve
```

### "Model not found"

1. List available models:
```bash
ollama list
```

2. Pull the model:
```bash
ollama pull qwen2.5:7b
```

### "Request timed out"

- Increase timeout in `.env`:
```env
AI_TIMEOUT=180
AI_VISION_TIMEOUT=300
```

- Or use a smaller/faster model

### Vision model too slow

Use smaller models:
```bash
ollama pull qwen2-vl:4b
```

Update `.env`:
```env
AI_VISION_MODEL=qwen2-vl:4b
```

## Important Notes

### 1. Expert Approval Required

**NEVER** auto-save AI-generated knowledge to the database. The workflow is:

```
AI generates draft → Expert reviews → Expert edits → Expert approves → Save to DB
```

### 2. AI Does NOT Diagnose

The AI extracts symptoms and explains results, but:
- Final diagnosis = existing expert system
- AI does NOT replace agronomist expertise
- Image analysis = observations only, not diagnosis

### 3. Khmer Language Support

The AI can understand Khmer input and respond in Khmer, but:
- Quality depends on model training
- Always verify Khmer translations
- Consider adding Khmer-specific prompts

### 4. Privacy & Security

- Ollama runs locally (no data sent to cloud)
- No OpenAI, Anthropic, or external APIs required
- User images stored in `uploads/disease_images/`
- Validate and sanitize all file uploads

### 5. Performance

- First request may be slow (model loading)
- Vision models require more RAM (8GB+ recommended)
- Consider caching frequently-used model responses
- Use conversation context wisely (keeps last 10 messages)

## Future Enhancements

### RAG (Retrieval Augmented Generation)

Add vector search over approved disease knowledge:

```
User Question → Relevant Disease Docs → AI Answer
```

Implementation ideas:
- Use `chromadb` or `qdrant` for vector storage
- Embed all approved disease/symptom content
- Query similar content before generation

### Fine-Tuning

Train a sunflower-specific model:

1. Collect sunflower disease dataset
2. Fine-tune base model (Qwen, Llama, etc.)
3. Serve via Ollama

### Advanced Vision

- Multi-image diagnosis
- Disease progression tracking
- Severity estimation from images

## Support

For issues or questions:
1. Check Ollama logs: `ollama logs`
2. Check API logs: `tail -f logs/sunflower-api.log`
3. Verify model compatibility
4. Test with smaller models first
