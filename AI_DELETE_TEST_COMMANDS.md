# AI Delete Command Testing Guide

## Prerequisites
- Must be logged in as **admin** user (NOT expert or grower)
- Backend server must be running
- Frontend must be connected to backend

## Test Commands for Delete Functionality

### Delete Disease Commands

#### English Commands:
```
delete disease 1
delete disease Rust
remove disease Powdery Mildew
delete the disease Leaf Spot
```

#### Khmer Commands:
```
លុបជំងឺ 1
លុបជំងឺ Rust
```

### Delete Symptom Commands

#### English Commands:
```
delete symptom 1
delete symptom yellow spots
remove symptom brown leaves
delete the symptom wilting
```

#### Khmer Commands:
```
លុបរោគសញ្ញា 1
លុបរោគសញ្ញា ស្លឹកលឿង
```

## Testing Steps

### 1. First List Available Data
Before deleting, see what's available:
```
list all diseases
list all symptoms
```

### 2. Test Delete with ID
Try deleting by ID number:
```
delete disease 1
```

Expected result: ✅ Success message with disease name and ID

### 3. Test Delete with Name
Try deleting by name:
```
delete disease Rust
```

Expected result: ✅ Success message with disease name and ID

### 4. Test Permission Restrictions

**As Expert User (NOT admin):**
```
delete disease 1
```
Expected result: ❌ "Only admins can delete diseases. Experts can edit but cannot delete."

**As Grower User:**
```
delete disease 1
```
Expected result: ❌ "You don't have permission..."

### 5. Test Error Cases

**Non-existent Disease:**
```
delete disease NonExistentDisease123
```
Expected result: ❌ "Disease 'NonExistentDisease123' not found. Try 'list diseases' to see available diseases."

**No Entity Specified:**
```
delete disease
```
Expected result: ❌ "Please specify which disease to delete..."

## How Intent Detection Works

The system now uses **keyword pattern matching** before AI analysis:

1. **Keyword Detection**: Looks for words like:
   - Delete: `delete`, `remove`, `លុប`, `drop`
   - Disease: `disease`, `ជំងឺ`
   - Symptom: `symptom`, `រោគសញ្ញា`

2. **Entity Extraction**: Extracts the name/ID after keywords
   - "delete disease 1" → extracts "1"
   - "delete disease Rust" → extracts "Rust"
   - "now help me delete 1 diseases" → extracts "1"

3. **AI Fallback**: If keywords don't match, uses Ollama AI to analyze

## Debugging

If delete still doesn't work:

1. Check user role in browser console:
   ```javascript
   localStorage.getItem('user')
   ```
   Should show `"role": "admin"`

2. Check backend logs for intent detection:
   - Should see: `intent["action"] == "delete_disease"`

3. Test with simple command:
   ```
   delete disease 1
   ```

4. Check network tab for API response from `/api/v1/ai/admin/chat`

## Expected Behavior Summary

| User Role | List | Create | Update | Delete |
|-----------|------|--------|--------|--------|
| Grower    | ✅   | ❌     | ❌     | ❌     |
| Expert    | ✅   | ✅     | ✅     | ❌     |
| Admin     | ✅   | ✅     | ✅     | ✅     |

## Recent Fixes Applied

1. ✅ Added keyword pattern matching for delete commands
2. ✅ Detects both English and Khmer delete keywords
3. ✅ Handles numeric IDs (e.g., "delete disease 1")
4. ✅ Handles partial name matching
5. ✅ Improved error messages with suggestions
6. ✅ Permission checks for admin-only operations
