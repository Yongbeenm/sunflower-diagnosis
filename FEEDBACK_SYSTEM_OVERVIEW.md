# Feedback System Overview

## Current Implementation

The Sunflower Expert System has a **feedback system** that allows:

### For Users (Growers):
- Submit feedback/reports about diagnosis issues
- Attach feedback to specific diagnosis sessions
- Include contact information (optional)
- View their own submitted feedback

### For Admins/Agronomists:
- View all feedback reports
- Filter by status (open, in_review, resolved)
- Update feedback status
- View linked diagnosis sessions
- Track pending feedback count in dashboard

## System Components

### Backend:
- **Route**: `/api/v1/feedback`
- **Endpoints**:
  - `GET /feedback` - List feedback (paginated)
  - `POST /feedback` - Create feedback
  - `PATCH /feedback/{id}` - Update status (admin only)

### Frontend:
- **User Page**: `/feedback` - Submit feedback form
- **Admin Page**: `/admin/feedback` - Manage feedback queue

## Current Status Flow:

```
open → in_review → resolved
```

## Common Issues to Fix

Without knowing the specific feedback issue, here are common problems:

### 1. Feedback Form Not Submitting
**Symptoms:**
- Form submission fails
- No error message shown
- Data not saved to database

**Possible Causes:**
- API endpoint not reachable
- Validation errors
- Authentication issues
- Database constraints

### 2. Admin Can't Update Status
**Symptoms:**
- Status dropdown doesn't update
- Permission errors
- Changes not saved

**Possible Causes:**
- Missing `feedback:resolve` permission
- API route not working
- Frontend mutation not triggering

### 3. Feedback Not Appearing in Admin Panel
**Symptoms:**
- Submitted feedback doesn't show in admin list
- Empty feedback queue
- Pagination issues

**Possible Causes:**
- Data not saved to DB
- Permission filtering too restrictive
- Query filtering issues

### 4. Session Linking Not Working
**Symptoms:**
- Diagnosis session not attached to feedback
- Session link broken
- Can't view linked session

**Possible Causes:**
- Invalid session ID
- UUID parsing issues
- Foreign key constraints

## What Feedback Issue Do You Need Fixed?

Please specify:

1. **What is broken?**
   - Form submission?
   - Status updates?
   - Display issues?
   - Something else?

2. **Who is affected?**
   - Growers (regular users)?
   - Admins?
   - Both?

3. **What should happen vs what actually happens?**
   - Expected behavior
   - Actual behavior
   - Any error messages

4. **When did this start?**
   - After a specific change?
   - Always been broken?
   - Intermittent?

## Quick Tests I Can Run

### Test 1: Check if feedback endpoint works
```bash
curl -X GET http://localhost:8000/api/v1/feedback \
  -H "Authorization: Bearer <token>"
```

### Test 2: Create test feedback
```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test",
    "message": "Test message",
    "contact_info": "test@example.com"
  }'
```

### Test 3: Check database
```sql
SELECT id, subject, status, created_at FROM feedback ORDER BY created_at DESC LIMIT 10;
```

## Potential Improvements I Can Implement

If you want to enhance the feedback system:

1. **Add image attachments** - Allow users to upload photos with feedback
2. **Email notifications** - Notify admins of new feedback
3. **Response system** - Allow admins to reply to feedback
4. **Priority levels** - Mark urgent feedback
5. **Categories** - Classify feedback types
6. **Search functionality** - Find feedback by keyword
7. **Export feature** - Download feedback as CSV/PDF
8. **Analytics** - Track feedback trends

## Tell Me What to Fix!

Please describe the specific feedback issue you're experiencing, and I'll:
1. Investigate the problem
2. Identify the root cause
3. Implement the fix
4. Test it works
5. Document the solution

Examples:
- "Users can't submit feedback, form doesn't work"
- "Admin status dropdown is broken"
- "Feedback doesn't show up in admin panel"
- "Session links in feedback are broken"
- "Want to add image upload to feedback form"
