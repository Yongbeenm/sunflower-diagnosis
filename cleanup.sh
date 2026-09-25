#!/bin/bash
# Cleanup script for Sunflower Expert System
# Removes temporary, testing, and redundant files before pushing to GitHub

echo "🧹 Cleaning up Sunflower Expert System..."
echo ""

# Test files
echo "Removing test files..."
rm -f check_feedback.py
rm -f simple_test.py
rm -f test_admin_chat.py
rm -f check-admin.sh
rm -f add-database-env.sh
rm -f fix-database.sh
rm -f fix-delete-permissions.sql

# Old documentation
echo "Removing old/duplicate documentation..."
rm -f AI_CHANGELOG.md
rm -f AI_COMPLETE_SUMMARY.md
rm -f AI_IMPLEMENTATION_SUMMARY.md
rm -f AI_QUICKSTART.md
rm -f AI_SLIDE_GENERATION_PROMPTS.md
rm -f AI_TESTING_GUIDE.md
rm -f CRITICAL_FIX_APPLIED.md
rm -f DELETE_FIX_SUMMARY.md
rm -f FEEDBACK_FIX_SUMMARY.md
rm -f FEEDBACK_SCHEMA_FIX.md
rm -f FRONTEND_REDESIGN_PROMPT.md
rm -f INTENT_DETECTION_FLOW.md
rm -f PRESENTATION_SLIDES_OUTLINE.md
rm -f QUICK_TEST_GUIDE.md
rm -f README_AI_ADMIN_FIX.md
rm -f REDESIGN_CHANGELOG.md
rm -f TROUBLESHOOTING_DELETE.md
rm -f VIDEO_RECORDING_CHECKLIST.md
rm -f VIDEO_SCRIPT.md

# Deployment scripts (optional - uncomment if not using)
echo "Removing deployment scripts (if not needed)..."
rm -f deploy-frontend-fresh.sh
rm -f deploy-frontend.sh
rm -f deploy-simple.sh
rm -f deploy-to-vercel.sh
rm -f seed-production.sh
rm -f set-frontend-env.sh
rm -f setup-vercel-env.sh
rm -f fix-vercel-env.sh
rm -f setup-ai.sh

# macOS files
echo "Removing .DS_Store files..."
find . -name ".DS_Store" -type f -delete

# Root .env (keep only in backend/ and frontend/)
echo "Removing root .env file..."
rm -f .env
rm -f .env.example

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Files kept:"
echo "  ✅ README.md"
echo "  ✅ SETUP_INSTRUCTIONS.md"
echo "  ✅ CLEANUP_GUIDE.md"
echo "  ✅ AI_ADMIN_COMMANDS.md"
echo "  ✅ AI_INTEGRATION.md"
echo "  ✅ AI_PERMISSIONS.md"
echo "  ✅ FEEDBACK_SYSTEM_OVERVIEW.md"
echo "  ✅ Makefile"
echo "  ✅ docker-compose.yml"
echo "  ✅ .gitignore"
echo "  ✅ backend/"
echo "  ✅ frontend/"
echo "  ✅ docs/"
echo ""
echo "📝 Next steps:"
echo "  1. Review .gitignore"
echo "  2. Update README.md if needed"
echo "  3. Test: cd backend && pytest"
echo "  4. Test: cd frontend && npm run build"
echo "  5. Commit: git add -A && git commit -m 'Clean up project structure'"
echo "  6. Push: git push origin main"
echo ""
echo "🚀 Ready to push to GitHub!"
