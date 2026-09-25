# AI Assistant Permission Levels

## Overview
The AI Assistant has different capabilities based on user role. This document outlines what each user type can do through AI chat commands.

---

## Permission Matrix

| Action | Grower | Expert (Agronomist) | Admin |
|--------|--------|---------------------|-------|
| **View/List** diseases | ✅ | ✅ | ✅ |
| **View/List** symptoms | ✅ | ✅ | ✅ |
| **Search** data | ✅ | ✅ | ✅ |
| **Create** diseases | ❌ | ✅ | ✅ |
| **Create** symptoms | ❌ | ✅ | ✅ |
| **Update/Edit** diseases | ❌ | ✅ | ✅ |
| **Update/Edit** symptoms | ❌ | ✅ | ✅ |
| **Delete** diseases | ❌ | ❌ | ✅ |
| **Delete** symptoms | ❌ | ❌ | ✅ |
| **AI Chat** assistance | ✅ | ✅ | ✅ |
| **Image Analysis** | ✅ | ✅ | ✅ |

---

## User Roles Explained

### 1. Grower (Regular User)
**Purpose:** Farmers who need help diagnosing plant diseases

**AI Capabilities:**
- ✅ Chat with AI about plant diseases
- ✅ Upload and analyze images
- ✅ Get symptom extraction help
- ✅ View disease and symptom information
- ✅ Search for diseases/symptoms
- ❌ **Cannot modify any data**

**Example Commands:**
```
✅ "List all diseases"
✅ "Search for rust"
✅ "What are the symptoms of downy mildew?"
❌ "Create disease X" → Permission denied
❌ "Delete disease Y" → Permission denied
```

---

### 2. Expert / Agronomist
**Purpose:** Agricultural experts who maintain the knowledge base

**AI Capabilities:**
- ✅ Everything growers can do
- ✅ Create new diseases
- ✅ Create new symptoms
- ✅ Update/edit existing diseases
- ✅ Update/edit existing symptoms
- ❌ **Cannot delete** (safety measure)

**Example Commands:**
```
✅ "Create disease Powdery Mildew with pathogen fungal"
✅ "Update disease Rust description to affects young leaves"
✅ "Create symptom yellow spots on leaves"
✅ "Update symptom wilting stems"
❌ "Delete disease Test" → Only admins can delete
```

**Why Experts Can't Delete:**
- Prevents accidental data loss
- Ensures admins review before permanent deletions
- Maintains data integrity

---

### 3. Admin
**Purpose:** System administrators with full control

**AI Capabilities:**
- ✅ Everything experts can do
- ✅ Delete diseases
- ✅ Delete symptoms
- ✅ Full database control via AI

**Example Commands:**
```
✅ "Delete disease Old Test Entry"
✅ "Delete symptom Duplicate Symptom"
✅ All create/update commands
```

**Admin Responsibility:**
- Deletions are permanent
- Must verify before deleting used data
- Should backup before bulk operations

---

## Permission Error Messages

### When Grower Tries to Modify Data:
**English:**
```
"You don't have permission to [action]. Only experts and admins can modify data."
```

**Khmer:**
```
"អ្នកមិនមានសិទ្ធិ[action]ទេ។ តែអ្នកជំនាញ និងអ្នកគ្រប់គ្រងប៉ុណ្ណោះអាចកែប្រែទិន្នន័យបាន។"
```

### When Expert Tries to Delete:
**English:**
```
"Only admins can delete [data type]. Experts can edit but cannot delete."
```

**Khmer:**
```
"តែអ្នកគ្រប់គ្រងប៉ុណ្ណោះអាចលុប[data type]បាន។ អ្នកជំនាញអាចកែប៉ុន្តែមិនអាចលុបបានទេ។"
```

---

## Available Commands by Role

### All Users (Growers, Experts, Admins)

**View Commands:**
```
"List all diseases"
"List all symptoms"
"Show me diseases"
"Display symptoms"
```

**Search Commands:**
```
"Search for rust"
"Find diseases with spots"
"Search symptoms about leaves"
```

**Help:**
```
"help"
"what can you do?"
"show commands"
```

---

### Experts & Admins Only

**Create Disease:**
```
"Create disease Powdery Mildew with pathogen fungal"
"Add disease called Bacterial Wilt"
"New disease: Stem Rot, type: fungal"
```

**Create Symptom:**
```
"Create symptom yellow spots on leaves"
"Add symptom wilting stems"
"New symptom: brown leaf edges"
```

**Update Disease:**
```
"Update disease Rust description to affects young plants"
"Change Downy Mildew pathogen type to fungal"
"Modify disease Powdery Mildew"
```

**Update Symptom:**
```
"Update symptom yellow spots"
"Change symptom wilting description"
```

---

### Admins Only

**Delete Disease:**
```
"Delete disease Test Entry"
"Remove disease Old Disease"
"Get rid of disease Dummy"
```

**Delete Symptom:**
```
"Delete symptom Duplicate Symptom"
"Remove symptom Old Symptom"
```

---

## Technical Implementation

### Backend Permission Check
```python
# In admin_chat_service.py

if intent["action"] == "create_disease":
    if user_role not in ["admin", "agronomist"]:
        return permission_denied_message
    # Proceed with creation

if intent["action"] == "delete_disease":
    if user_role != "admin":
        return admin_only_message
    # Proceed with deletion
```

### Frontend Role Detection
```typescript
// In AIChatWidget.tsx

const isAdminOrExpert = user.role?.name === 'admin' || user.role?.name === 'agronomist';

// Use different endpoint based on role
if (isAdminOrExpert) {
  response = await adminChatWithAI(request);
} else {
  response = await chatWithAI(request);
}
```

---

## Security Considerations

### 1. Backend Validation
- All permissions checked on backend (never trust frontend)
- Database permissions enforced via SQLAlchemy
- Action logging for audit trail

### 2. Role Assignment
- Users assigned roles by admins only
- Roles stored in database (not JWT)
- Cannot self-promote to higher role

### 3. Deletion Safety
- Admins only for destructive operations
- Warning messages before deletion
- Cascade considerations for related data

---

## Testing Permissions

### Test as Grower
1. Login as grower user
2. Try: `"List all diseases"` → Should work
3. Try: `"Create disease Test"` → Should be denied
4. Try: `"Delete disease X"` → Should be denied

### Test as Expert
1. Login as agronomist user
2. Try: `"Create disease Test"` → Should work
3. Try: `"Update disease Test"` → Should work
4. Try: `"Delete disease Test"` → Should be denied (admin only)

### Test as Admin
1. Login as admin user
2. Try: `"Create disease Test"` → Should work
3. Try: `"Update disease Test"` → Should work
4. Try: `"Delete disease Test"` → Should work

---

## Upgrading User Permissions

To change a user's role (admins only):

1. **Via Admin Panel:**
   - Go to Users & Permissions page
   - Find user
   - Change role dropdown
   - Save

2. **Via Database:**
   ```sql
   UPDATE users SET role_id = 2 WHERE username = 'user@example.com';
   -- role_id: 1=grower, 2=agronomist, 3=admin
   ```

---

## Future Enhancements

Planned features:
- [ ] Approval workflow (expert creates → admin approves)
- [ ] Temporary elevated permissions
- [ ] Audit log viewer in AI chat
- [ ] Bulk operations with safeguards
- [ ] Undo last operation

---

## FAQ

**Q: Can experts publish diseases?**
A: Yes, experts can create and update diseases, including publishing them.

**Q: Why can't experts delete?**
A: Safety measure to prevent accidental data loss. Admins review before permanent deletions.

**Q: Can I see who made changes?**
A: Yes, all actions are logged with user ID, timestamp, and action type.

**Q: What happens if I try a command I don't have permission for?**
A: You'll receive a clear error message explaining what's needed and who can perform that action.

**Q: Can growers still use AI for diagnosis?**
A: Yes! Growers have full access to AI chat, image analysis, and diagnosis features. They just can't modify the disease/symptom database.

---

**Version:** 1.0  
**Last Updated:** 2026-09-21  
**Status:** Production Ready ✅
