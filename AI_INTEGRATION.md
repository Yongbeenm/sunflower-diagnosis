# AI Integration Guide

## Overview

The Sunflower Expert System now includes local AI capabilities using Ollama. This document explains the integration, setup, and usage.

## What Was Added

### 1. AI Module (`backend/ai/`)

New module containing:
- **Ollama service wrapper** - Communicates with local Ollama server
- **Symptom extractor** - Converts natural language to structured symptoms
- **Chatbot service** - Conversational AI for users
- **Vision service** - Analyzes plant disease images
- **Disease assistant** - Helps experts create knowledge entries
- **Prompt templates** - System prompts for different AI tasks

### 2. New API Endpoints (`/api/v1/ai/*`)

- `GET /ai/health` - Check AI service status
- `POST /ai/chat` - Chat with AI assistant
- `POST /ai/extract-symptoms` - Extract symptoms from text
- `POST /ai/diagnose` - AI-assisted diagnosis (uses expert system)
- `POST /ai/analyze-image` - Analyze plant photos
- `POST /ai/expert/disease-draft` - Generate disease knowledge draft
- `POST /ai/expert/duplicate-check` - Check for duplicate diseases

### 3. Configuration

New environment variables in `.env`:
- `AI_ENABLED` - Enable/disable AI features
- `OLLAMA_HOST` - Ollama server URL
- `AI_MODEL` - Text model name
- `AI_VISION_MODEL` - Vision model name
- `AI_TIMEOUT` - Request timeout
- `AI_TEMPERATURE` - Generation creativity

## Architecture

### Key Principle: AI Assists, Expert System Decides

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│         "My sunflower leaves have brown spots"              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   AI Symptom Extraction                      │
│        Ollama (Local) - qwen2.5:7b or similar              │
│                                                              │
│   Extracts: {                                               │
│     "plant_part": ["leaf"],                                 │
│     "symptoms": ["spots", "discoloration"],                 │
│     "color_changes": ["brown"]                              │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               Map to Database Symptoms                       │
│   "brown spots" → symptom_id: 42                            │
│   "leaf discoloration" → symptom_id: 15                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           EXISTING EXPERT SYSTEM                             │
│        app/services/engine/scoring.py                       │
│                                                              │
│   - Rule-based weighted symptom matching                    │
│   - Pathognomonic symptom detection                         │
│   - Confidence scoring                                       │
│   - Disease ranking                                          │
│                                                              │
│   THIS IS THE AUTHORITATIVE DIAGNOSIS ENGINE                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              AI Explanation Generation                       │
│   "Based on brown spots on leaves, the most likely         │
│    disease is Early Blight (85% confidence)..."            │
└─────────────────────────────────────────────────────────────┘
                              ↓
                           User
```

## Quick Start

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

### 2. Start Ollama

```bash
ollama serve
```

### 3. Pull Models

**For basic text features:**
```bash
ollama pull qwen2.5:7b
```

**For vision (image analysis):**
```bash
ollama pull qwen2-vl:7b
```

**Alternative models:**
- `llama3.2:3b` - Faster, smaller
- `mistral:7b` - Good general purpose
- `qwen2-vl:4b` - Smaller vision model

### 4. Configure Backend

Create/update `backend/.env`:
```env
AI_ENABLED=true
AI_VISION_ENABLED=true
OLLAMA_HOST=http://localhost:11434
AI_MODEL=qwen2.5:7b
AI_VISION_MODEL=qwen2-vl:7b
```

### 5. Install Dependencies

```bash
cd backend
pip install -e ".[dev]"
```

### 6. Test Installation

```bash
# Start backend
uvicorn app.main:app --reload

# In another terminal, test health
curl http://localhost:8000/api/v1/ai/health
```

Expected response:
```json
{
  "ollama_available": true,
  "model_loaded": "qwen2.5:7b",
  "status": "ready"
}
```

## Use Cases

### 1. User Natural Language Diagnosis

**Before (manual symptom selection):**
1. User opens symptom checklist
2. Selects "leaf spots" ☑
3. Selects "brown discoloration" ☑
4. Selects "yellowing" ☑
5. Submits for diagnosis

**After (with AI):**
1. User types: "My sunflower leaves have brown spots and are turning yellow"
2. AI extracts symptoms automatically
3. Maps to database symptom IDs
4. Runs expert system diagnosis
5. Returns results with natural explanation

### 2. User Chatbot

**Example conversation:**

```
User: "What causes brown spots on sunflower leaves?"

AI: "Brown spots on sunflower leaves can be caused by several diseases 
     including fungal infections like Alternaria leaf spot or bacterial 
     diseases. Can you describe the spots more? Are they circular? 
     Do they have yellow halos?"

User: "Yes, circular brown spots with yellow edges"

AI: "That sounds like it could be Early Blight (Alternaria). I recommend
     using our diagnosis tool to get a specific evaluation. Would you 
     like me to help you describe all the symptoms you're seeing?"
```

### 3. Image Analysis

**User uploads photo:**

AI analyzes and returns:
```json
{
  "crop_identified": "sunflower",
  "plant_parts": ["leaf", "stem"],
  "visible_symptoms": ["brown circular lesions", "yellowing"],
  "spots_lesions": ["0.5-1cm brown spots with yellow halos"],
  "image_quality": "clear, well-lit",
  "possible_diseases": ["early blight", "septoria leaf spot"]
}
```

**Important:** This is visual observation, not diagnosis. User should still run expert system evaluation.

### 4. Expert Knowledge Entry

**Expert describes new disease:**

```
"Downy mildew causes pale yellow spots on upper leaf surfaces 
 with gray fuzzy growth on undersides. It thrives in cool, wet 
 conditions. Spreads rapidly in spring."
```

**AI generates draft:**
```json
{
  "disease_name_en": "Downy Mildew",
  "scientific_name": "Plasmopara halstedii",
  "pathogen_type": "fungal",
  "symptoms": [
    "pale yellow spots on leaf upper surface",
    "gray fuzzy growth on leaf underside",
    "rapid spread in spring"
  ],
  "causes": ["Plasmopara fungal pathogen"],
  "risk_factors": ["cool temperatures", "high humidity", "wet conditions"],
  "prevention": [
    "Use resistant varieties",
    "Improve air circulation",
    "Avoid overhead irrigation"
  ],
  "treatment": [
    "Apply fungicide early",
    "Remove infected leaves",
    "Improve drainage"
  ]
}
```

**Expert reviews, edits, and approves** before saving to database.

### 5. Duplicate Detection

**Expert enters:** "Sunflower Rust Disease"

**AI checks existing diseases:**
```json
{
  "is_likely_duplicate": true,
  "matches": [
    {
      "disease_id": 15,
      "disease_name": "Rust",
      "similarity_score": 0.92,
      "reason": "Same pathogen (Puccinia helianthi), same symptoms 
                (orange-brown pustules), same plant"
    }
  ],
  "recommendation": "Very likely duplicate of existing 'Rust' entry. 
                     Review before creating new entry."
}
```

## Frontend Integration (To Do)

### Option 1: Add AI Chat Button

```tsx
// In diagnosis page
<Button onClick={() => setShowAIChat(true)}>
  💬 Ask Sunflower AI
</Button>

{showAIChat && (
  <AIChatWidget 
    onSymptomExtracted={(symptoms) => {
      // Auto-fill symptom form
      setSelectedSymptoms(symptoms);
    }}
  />
)}
```

### Option 2: Natural Language Input

```tsx
<Tabs>
  <Tab label="Select Symptoms">
    {/* Existing symptom checklist */}
  </Tab>
  
  <Tab label="Describe in Words">
    <TextArea 
      placeholder="Describe what you see on your sunflower..."
      onChange={handleNaturalLanguageInput}
    />
    <Button onClick={extractAndDiagnose}>
      Diagnose
    </Button>
  </Tab>
</Tabs>
```

### Option 3: Image Upload

```tsx
<ImageUpload
  onUpload={async (imageBase64) => {
    const analysis = await api.analyzeImage(imageBase64);
    // Show observations
    // Option to run diagnosis with extracted symptoms
  }}
/>
```

## Security Considerations

### 1. AI-Generated Content Approval

**CRITICAL: Never auto-save AI content**

```python
# ❌ WRONG - Auto-save AI output
draft = await ai.generate_disease_draft(description)
await db.save_disease(draft)  # NEVER DO THIS

# ✅ CORRECT - Require approval
draft = await ai.generate_disease_draft(description)
# Store as draft with status='pending_approval'
await db.save_draft(draft, status='pending_approval', created_by=expert)
# Expert reviews in UI
# Only save when expert clicks "Approve"
```

### 2. Input Validation

All AI endpoints validate:
- Message length (max 2000 chars)
- Image size (max 10MB)
- Image format (jpg, png, webp only)
- Locale (en or km only)

### 3. Rate Limiting (Recommended)

Add rate limiting to AI endpoints:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/ai/chat")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat(...):
    ...
```

### 4. Image Storage

Images are stored securely:
- Uploaded to `uploads/disease_images/`
- Filenames sanitized (UUID-based)
- File type validated
- Size limited
- Not publicly accessible without authentication

## Performance

### Model Performance

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| qwen2.5:3b | 1.9GB | Fast | Good | Basic chat |
| qwen2.5:7b | 4.7GB | Medium | Better | Recommended |
| qwen2-vl:4b | 2.8GB | Medium | Good | Vision (resource-limited) |
| qwen2-vl:7b | 5.5GB | Slow | Better | Vision (recommended) |
| llama3.2:3b | 2.0GB | Fast | Good | Alternative |

### Optimization Tips

1. **Keep Ollama running** - Don't stop/start between requests
2. **Model stays loaded** - First request loads, subsequent requests are fast
3. **Use smaller models** for development/testing
4. **Cache common responses** - Store frequent question answers
5. **Limit conversation history** - Keep last 10 messages only

### Resource Requirements

**Minimum:**
- 8GB RAM
- 4 CPU cores
- 10GB disk space

**Recommended:**
- 16GB RAM
- 8 CPU cores
- 20GB disk space

## Monitoring

### Check AI Service Status

```bash
# Health check
curl http://localhost:8000/api/v1/ai/health

# Ollama status
curl http://localhost:11434/api/tags

# View loaded models
ollama list

# Check Ollama logs
tail -f ~/.ollama/logs/server.log
```

### Metrics to Track

1. **Response time** - Track AI endpoint latency
2. **Success rate** - % of successful AI calls
3. **Symptom mapping accuracy** - % of extracted symptoms that map to DB
4. **User satisfaction** - Feedback on AI responses
5. **Expert approval rate** - % of AI drafts approved

## Limitations

### 1. Language Support

- English: Excellent
- Khmer: Good (depends on model)
- Other languages: Not tested

### 2. Plant Coverage

Models trained on general knowledge may not know:
- Regional disease varieties
- Local disease names
- Uncommon sunflower varieties

**Solution:** Use RAG (future enhancement) to ground AI in your specific knowledge base.

### 3. Image Analysis

Vision models can:
- Identify visible symptoms
- Describe color/texture changes
- Detect some pests

Vision models cannot:
- Diagnose with certainty
- See microscopic pathogens
- Replace lab analysis

### 4. Offline Usage

- Ollama runs locally (offline-capable)
- But model downloads require internet
- Pull all models before going offline

## Troubleshooting

### Problem: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Problem: "Model not loaded"

**Solution:**
```bash
# List available models
ollama list

# Pull missing model
ollama pull qwen2.5:7b

# Verify in health check
curl http://localhost:8000/api/v1/ai/health
```

### Problem: "Request timeout"

**Solutions:**
1. Increase timeout in `.env`:
```env
AI_TIMEOUT=180
```

2. Use smaller/faster model:
```env
AI_MODEL=qwen2.5:3b
```

3. Check system resources:
```bash
top  # Check CPU/RAM usage
```

### Problem: Poor symptom extraction

**Solutions:**
1. Improve prompts in `ai/prompts/symptom_extraction.txt`
2. Use higher-quality model
3. Add few-shot examples to prompt
4. Increase extraction temperature for creativity

### Problem: Khmer responses are poor

**Solutions:**
1. Use model with better multilingual support
2. Add Khmer examples to prompts
3. Consider fine-tuning on Khmer agriculture text
4. Fall back to English with translation layer

## Future Enhancements

### 1. RAG (Retrieval Augmented Generation)

Ground AI in approved knowledge:
```
User: "What is early blight?"
  ↓
Search disease database for "early blight"
  ↓
Retrieve approved disease entry
  ↓
Feed to AI as context
  ↓
AI answers based on approved knowledge
```

### 2. Fine-Tuning

Train sunflower-specific model:
- Collect sunflower disease dataset
- Fine-tune base model
- Deploy custom model via Ollama

### 3. Multi-Modal Diagnosis

Combine text + image + environmental data:
```
Symptoms + Photo + Weather + Location → Diagnosis
```

### 4. Progressive Questioning

AI asks targeted follow-up questions:
```
"You mentioned brown spots. Are they:
 a) Circular with yellow halos?
 b) Irregular with no defined edge?
 c) Tiny pinpoint spots?"
```

### 5. Treatment Recommendations

Based on diagnosis, suggest treatments:
- Organic options
- Chemical treatments
- Cultural practices
- Timing and dosage

## Support & Contribution

### Getting Help

1. Check `backend/ai/README.md` for detailed docs
2. Review Ollama docs: https://ollama.ai/docs
3. Test with `curl` commands in this guide
4. Check application logs

### Contributing

When adding AI features:
1. **Never replace expert system** - AI assists only
2. **Require expert approval** for knowledge changes
3. **Validate all inputs** thoroughly
4. **Handle failures gracefully** - AI should fail safely
5. **Add tests** for new AI services
6. **Update prompts** in `ai/prompts/`
7. **Document** API changes

## Summary

✅ **What the AI Does:**
- Understand natural language
- Extract structured symptoms
- Analyze images for visible symptoms
- Generate knowledge drafts for experts
- Explain diagnosis results
- Detect potential duplicates

❌ **What the AI Does NOT Do:**
- Replace the expert system
- Make final diagnosis decisions
- Auto-save to knowledge base
- Replace agronomist expertise
- Guarantee medical/agricultural accuracy

The AI is a **tool to assist**, not a replacement for the existing rule-based expert system or human expertise.
