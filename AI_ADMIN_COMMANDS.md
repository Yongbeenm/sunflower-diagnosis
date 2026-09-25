# AI Admin Assistant - Database Management Commands

## Overview

The AI Assistant has **special capabilities for Admin and Expert users** that allow them to manage diseases and symptoms through natural language commands. This provides a powerful, conversational interface for database operations.

## Access Control

### User Roles & Permissions

| Role | Can View Data | Can Create | Can Update | Can Delete |
|------|--------------|------------|------------|------------|
| **Grower** | Limited | ❌ | ❌ | ❌ |
| **Agronomist** | ✅ | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ |

### Visual Indicators

**Admin/Expert Mode Features:**
- 🟡 **Yellow/Orange gradient** on floating button (vs blue for regular users)
- 🛡️ **Shield icon** in header
- **"Admin Mode - Can modify data"** subtitle
- Special welcome message with command hints

## Available Commands

### 1. View Data Commands

#### List All Diseases
```
"List all diseases"
"Show me all diseases"
"What diseases are in the database?"
```

**Response:** Shows list of all diseases with pathogen types

#### List All Symptoms
```
"List all symptoms"
"Show me symptoms"
"What symptoms do we have?"
```

**Response:** Shows symptoms grouped by plant part category

#### Search
```
"Search for rust"
"Find diseases with spots"
"Search symptoms about leaves"
```

**Response:** Returns matching diseases and symptoms

---

### 2. Create Commands (Agronomist/Admin Only)

#### Create Disease
```
"Create disease Powdery Mildew with pathogen fungal"
"Add a new disease called Downy Mildew"
"Create disease Rust, pathogen type is fungal"
```

**What happens:**
1. AI extracts disease name and pathogen type
2. Creates disease in database (as DRAFT)
3. Returns disease ID for further editing
4. Disease appears in admin panel

**Required permission:** `disease:create`

**Example response:**
```
✅ Successfully created disease 'Powdery Mildew' (ID: 45).

It's currently in DRAFT mode. You can edit it in the admin 
panel to add symptoms, treatment, and translations, then publish it.
```

#### Create Symptom
```
"Create symptom yellow spots on leaves"
"Add symptom wilting stems"
```

**What happens:**
1. AI extracts symptom details
2. Creates symptom with auto-generated code
3. Returns symptom ID

**Required permission:** `symptom:create`

---

### 3. Update Commands (Agronomist/Admin Only)

#### Update Disease
```
"Update disease Rust description to affects leaves and stems"
"Change Downy Mildew pathogen type to fungal"
"Update disease Powdery Mildew"
```

**What happens:**
1. AI finds the disease by name
2. Updates specified fields
3. Confirms which fields were changed

**Required permission:** `disease:update`

**Example response:**
```
✅ Updated disease 'Rust'. Fields updated: description
```

---

### 4. Delete Commands (Admin Only)

#### Delete Disease
```
"Delete disease Test Disease"
"Remove disease Old Entry"
```

**What happens:**
1. AI finds the disease
2. Permanently deletes it (including symptoms and translations)
3. Confirms deletion

**Required permission:** `disease:delete`

**⚠️ Warning:** This is permanent! Only admins can delete diseases.

**Example response:**
```
✅ Successfully deleted disease 'Test Disease' (ID: 23).
```

---

### 5. Help Command

```
"help"
"what can you do?"
"show me available commands"
```

**Response:** Shows complete list of available commands with examples

---

## Natural Language Understanding

The AI understands various phrasings:

### Create Examples:
- ✅ "Create disease Powdery Mildew with pathogen fungal"
- ✅ "Add a new disease called Rust"
- ✅ "Make a disease for bacterial wilt"
- ✅ "New disease: Downy Mildew, type: fungal"

### Update Examples:
- ✅ "Update disease Rust description to something new"
- ✅ "Change the description of Powdery Mildew"
- ✅ "Modify disease Downy Mildew"

### Delete Examples:
- ✅ "Delete disease Test"
- ✅ "Remove disease Old Entry"
- ✅ "Get rid of disease Dummy"

---

## Example Conversations

### Example 1: Creating a New Disease

**User:** "List all diseases"

**AI:** "Found 26 diseases. Showing first 20:
• Alternaria Leaf Spot (fungal)
• Bacterial Wilt (bacterial)
• Downy Mildew (fungal)
..."

**User:** "Create disease Stem Rot with pathogen fungal"

**AI:** "✅ Successfully created disease 'Stem Rot' (ID: 27).

It's currently in DRAFT mode. You can edit it in the admin panel to add symptoms, treatment, and translations, then publish it."

**User:** "Update disease Stem Rot description to causes stem decay and plant collapse"

**AI:** "✅ Updated disease 'Stem Rot'. Fields updated: description"

---

### Example 2: Searching and Updating

**User:** "Search for rust"

**AI:** "**Diseases (2):**
• Rust (fungal)
• White Rust (fungal)

**Symptoms (3):**
• rust_pustules (LEAF-023)
• orange_rust_spots (LEAF-024)
• rust_colored_lesions (STEM-015)"

**User:** "Update disease Rust to add that it commonly affects young plants"

**AI:** "✅ Updated disease 'Rust'. Fields updated: description"

---

### Example 3: Permission Denied

**User (Grower role):** "Delete disease Test"

**AI:** "Only admins can delete diseases."

---

## Technical Architecture

### Backend Flow

1. **User sends message** → AI Chat Widget
2. **Frontend detects role** → Routes to `/api/v1/ai/admin/chat`
3. **AI analyzes intent** → Determines action (list, create, update, delete, search)
4. **Executes database operation** → Using SQLAlchemy with proper permissions
5. **Returns response** → Natural language confirmation + action log

### Permission Checks

```python
# Backend checks permissions at multiple levels:
1. API endpoint: @require_permission("disease:read")
2. Service layer: Checks user_role
3. Database: Validates ownership and access
```

### Safety Features

- **Draft mode by default** - New diseases aren't published immediately
- **Permission-based access** - Role-based restrictions enforced
- **Audit trail** - All actions logged with metadata
- **Confirmation messages** - Clear feedback on what was changed
- **No cascading deletes without warning** - Warns about related data

---

## Khmer Language Support

All commands work in **Khmer language** too:

```
"បង្ហាញជំងឺទាំងអស់"  →  List all diseases
"បង្កើតជំងឺ X"       →  Create disease X
"ធ្វើបច្ចុប្បន្នភាព"  →  Update...
"លុបជំងឺ"           →  Delete disease
```

---

## Best Practices

### ✅ DO:
- Use clear, descriptive disease names
- Review AI-created diseases before publishing
- Search before creating to avoid duplicates
- Use admin panel for complex edits (symptoms, weights, images)
- Test commands with "list" first to see current data

### ❌ DON'T:
- Don't delete diseases that are actively used in diagnoses
- Don't create duplicate diseases with similar names
- Don't rely solely on AI for critical data - always review
- Don't share admin credentials with untrusted users
- Don't bulk-delete without backing up data

---

## Troubleshooting

### "You don't have permission..."
**Solution:** Check your user role. Ask admin to grant appropriate permissions.

### "Disease 'X' not found"
**Solution:** Use "search for X" to find exact name. Disease names are case-insensitive but must match.

### "AI service error"
**Solution:** Ollama server may be down. Check backend logs and restart Ollama.

### Disease created but not visible
**Solution:** New diseases are created as DRAFTS. Go to admin panel → Diseases → Edit → Publish

---

## Future Enhancements

Planned features:
- [ ] Bulk operations ("Create 5 diseases from this list")
- [ ] Undo/redo capabilities
- [ ] Export/import diseases via AI chat
- [ ] AI-suggested symptom weights
- [ ] Auto-translation generation
- [ ] Voice commands
- [ ] Multi-step wizards for complex operations

---

## API Endpoint

**Endpoint:** `POST /api/v1/ai/admin/chat`

**Request:**
```json
{
  "message": "Create disease Powdery Mildew with pathogen fungal",
  "locale": "en",
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "message": "✅ Successfully created disease...",
  "conversation_id": "uuid",
  "needs_diagnosis": false,
  "metadata": {
    "intent": "create_disease",
    "actions_taken": [
      {
        "action": "created_disease",
        "disease_id": 27,
        "disease_name": "Powdery Mildew"
      }
    ],
    "is_admin_mode": true
  }
}
```

---

## Security Considerations

1. **Authentication Required** - Must be logged in
2. **Role-Based Access Control** - Permissions checked on every action
3. **SQL Injection Prevention** - All inputs sanitized via SQLAlchemy ORM
4. **Audit Logging** - All admin actions logged with user ID and timestamp
5. **Rate Limiting** - Prevents abuse (implement if needed)
6. **Input Validation** - AI extracts data, but backend validates all fields

---

## Support

For issues or feature requests:
- Check backend logs: `backend/logs/app.log`
- Verify Ollama is running: `ollama list`
- Test AI health: `GET /api/v1/ai/health`
- Contact system administrator

---

**Version:** 1.0.0  
**Last Updated:** 2026-09-21  
**Maintained By:** Sunflower Expert System Team
