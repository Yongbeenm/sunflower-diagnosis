# AI Assistant Frontend Integration

This document describes the frontend integration of the AI-powered chatbot assistant.

## Features

### AI Chat Widget
- **Floating Button**: Accessible from any page when logged in
- **Conversational Interface**: Natural language symptom description
- **Bilingual Support**: Works in English and Khmer
- **Symptom Detection**: Automatically extracts symptoms from conversation
- **Real-time Responses**: Powered by local Ollama models

## Files Created

### API Layer
- `src/api/ai.ts` - AI API client functions
  - `chatWithAI()` - Chat with conversational assistant
  - `extractSymptoms()` - Extract structured symptoms from text
  - `getAIDiagnosis()` - Full AI + Expert System diagnosis
  - `analyzeImage()` - Vision-based image analysis
  - `checkAIHealth()` - Health check endpoint

### Components
- `src/features/ai-assistant/components/AIChatWidget.tsx` - Main chat widget
  - Floating button with gradient styling
  - Chat window with message history
  - Auto-scrolling messages
  - Conversation management
  - Loading states

### Translations
- `src/locales/en.json` - English translations
- `src/locales/km.json` - Khmer translations

## Usage

The AI Chat Widget is automatically added to the main app layout and appears for all authenticated users.

### User Flow

1. **Open Chat**: Click the floating "AI Assistant" button (bottom-right)
2. **Describe Symptoms**: Type natural language descriptions like:
   - "My sunflower has brown spots on the leaves"
   - "The leaves are turning yellow and wilting"
   - "I see white powder on the stems"
3. **Get Guidance**: AI responds with questions and guidance
4. **Run Diagnosis**: If symptoms detected, AI suggests running full diagnosis

### For Developers

```typescript
import { chatWithAI, extractSymptoms, getAIDiagnosis } from '@/api/ai';

// Chat with AI
const response = await chatWithAI({
  message: "My sunflower has brown spots",
  locale: "en"
});

// Extract symptoms only
const symptoms = await extractSymptoms({
  message: "Brown circular spots on older leaves",
  locale: "en"
});

// Full AI + Expert System diagnosis
const diagnosis = await getAIDiagnosis({
  message: "Brown spots spreading upward on leaves",
  locale: "en"
});
```

## Styling

The chat widget uses:
- **Gradient Background**: Blue to purple gradient for brand consistency
- **Frosted Glass**: Semi-transparent background with backdrop blur
- **Tailwind CSS**: Utility-first styling
- **Dark Mode**: Full dark mode support
- **Responsive**: Mobile-optimized floating widget

## Configuration

No additional frontend configuration needed. The widget automatically:
- Detects user authentication status
- Uses current language (i18n)
- Maintains conversation context
- Handles errors gracefully

## Backend Requirements

Requires backend AI endpoints to be running:
- `/api/v1/ai/health` - Health check
- `/api/v1/ai/chat` - Chat endpoint
- `/api/v1/ai/extract-symptoms` - Symptom extraction
- `/api/v1/ai/diagnose` - Full diagnosis

See backend `AI_INTEGRATION.md` for setup details.

## Future Enhancements

- [ ] Voice input support
- [ ] Image upload from chat widget
- [ ] Quick symptom suggestions
- [ ] Diagnosis history integration
- [ ] Notification when symptoms detected
- [ ] Export chat transcript
- [ ] Smart reply suggestions

## Testing

```bash
# Start frontend dev server
cd frontend
npm run dev

# Open http://localhost:5173
# Log in with any user account
# Click the floating "AI Assistant" button
# Start chatting!
```

## Troubleshooting

**Widget not appearing:**
- Make sure you're logged in
- Check browser console for errors
- Verify backend is running on port 8000

**No AI responses:**
- Check backend AI health: `curl http://localhost:8000/api/v1/ai/health`
- Ensure Ollama is running: `ollama serve`
- Check backend logs for errors

**Translations missing:**
- Clear browser cache
- Restart frontend dev server
- Check `locales/en.json` and `locales/km.json`
