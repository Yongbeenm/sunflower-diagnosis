# Doctor Sunflower - Professional Rebuild Prompt

## Project Overview
Create a modern, professional web application for sunflower disease diagnosis using an expert system approach. This system helps farmers and agricultural professionals identify sunflower diseases through symptom-based diagnosis, disease library management, and multilingual support (English/Khmer).

---

## Core Features & Requirements

### 1. **Expert System Diagnosis Engine**
- **Rule-based symptom matching** with weighted scoring algorithm
- Multi-select symptom checker with confidence scores (percentage-based)
- Support for 8+ symptom categories:
  - Leaf symptoms
  - Leaf/Head symptoms
  - Whole plant symptoms
  - Stem symptoms
  - Head symptoms
  - Root symptoms
  - Seed/Seedling symptoms
  - Environmental conditions
- Real-time diagnosis with explanations showing matched symptoms
- Top 3 disease recommendations with ranked confidence scores
- Threshold-based filtering (only show diseases above 35-45% confidence)

### 2. **Disease Library Management**
- Comprehensive disease database (26+ diseases initially)
- Each disease record includes:
  - Name (English & Khmer)
  - Detailed symptoms description
  - Cause/pathogen information
  - Treatment recommendations
  - Prevention strategies
  - High-quality disease images
  - Slug-based URLs for SEO
- Disease search functionality (full-text search across all fields)
- Featured disease cards on homepage
- Disease detail pages with rich information display

### 3. **Symptom Catalog System**
- Global symptom catalog with bilingual labels
- Category-based organization
- Dynamic symptom-to-disease mapping
- Symptom checklist JSON storage per disease
- Admin tools for symptom management:
  - Create/edit/delete symptoms
  - Bulk symptom assignment to diseases
  - Category management

### 4. **User Management & RBAC**
- Three user roles with distinct permissions:
  - **User**: Basic diagnosis access, symptom history, feedback submission
  - **Expert Sunflower (Doctor)**: Disease management, symptom rules, feedback review
  - **Admin**: Full system access, user management, role assignment
- Secure authentication with Flask-Login
- Permission-based access control for routes and features
- User profile management (username, password change)

### 5. **Multilingual Support (i18n)**
- Full English and Khmer language support
- Language switcher with cookie-based persistence
- Separate i18n databases for UI strings and phrase translations
- Context processor for automatic language injection in templates
- Bilingual disease information and symptoms

### 6. **Symptom History & Analytics**
- Track all user diagnosis sessions
- Store selected symptoms and matched diseases
- Display user's diagnosis history with timestamps
- Calculate metrics:
  - Total checks performed
  - Today's checks
  - Weekly trend comparison
  - Latest diagnosis details
- Detailed view of past symptom checks with results

### 7. **Feedback System**
- User feedback submission for no-match diagnoses
- Photo upload support for evidence (PNG/JPG/WEBP)
- Link feedback to specific symptom checks
- Admin/doctor inbox for reviewing feedback
- Helps improve diagnosis accuracy over time

### 8. **Admin & Doctor Dashboards**
- **Admin Dashboard**:
  - User management (list, edit roles, view activity)
  - Disease CRUD operations
  - Symptom catalog management
  - Feedback review and response
  - System analytics and symptom check logs
  - Role management (create custom roles)
  
- **Doctor Dashboard**:
  - Disease management interface
  - Symptom checklist editor (per disease)
  - Symptom catalog tools
  - Feedback inbox
  - Diagnosis logs and pattern analysis

---

## Technical Architecture

### Backend Stack
- **Framework**: Flask 3.0+ (Python web framework)
- **Database**: 
  - Primary: SQLite (development) / MySQL (production)
  - i18n: Separate SQLite databases for EN/KM translations
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with CSRF protection
- **Security**: Password hashing, CSRF tokens, role-based access

### Frontend Requirements
- **Modern, responsive UI** (mobile-first design)
- **Professional color scheme** with good accessibility (WCAG AA)
- **Clean, intuitive navigation** with clear information hierarchy
- **Interactive symptom checker** with:
  - Grouped symptom categories (collapsible/expandable)
  - Multi-select checkboxes
  - Real-time selection counter
  - Visual feedback for selections
- **Rich disease cards** with:
  - Disease image thumbnails
  - Truncated descriptions
  - Quick view and detail links
- **Dashboard widgets** showing:
  - Key metrics with icons
  - Recent activity timeline
  - Quick action buttons
  - Visual charts (optional: Chart.js integration)

### Data Models

#### Core Models:
1. **User**: id, username, email, password_hash, role, created_at, updated_at
2. **Disease**: id, slug, name, name_km, symptoms, symptoms_km, cause, cause_km, treatment, treatment_km, prevention, prevention_km, image_filename, symptom_checklist_json, created_by_id, updated_by_id, timestamps
3. **SymptomCatalog**: id, label, label_km, category, created_by_id, updated_by_id, timestamps
4. **SymptomCheck**: id, user_id, selected_count, top_disease_slug, top_disease_name, top_score, top_percent, created_at
5. **SymptomCheckSymptom**: id, check_id, symptom_key, symptom_label, category
6. **SymptomCheckResult**: id, check_id, rank, disease_id, disease_key, disease_name, score, percent, matched_json
7. **Feedback**: id, user_id, symptom_check_id, subject, message, photo_filename, status, reviewed_by_id, timestamps
8. **Role**: id, name, description, permissions (JSON)
9. **I18nMessage**: id, key, value, context (for EN/KM databases)

---

## Modern Tech Stack Recommendations

### Backend Enhancements:
- **FastAPI** (instead of Flask) for modern async support and auto-documentation
- **PostgreSQL** for robust production database with JSON support
- **Redis** for caching diagnosis results and session management
- **Celery** for async tasks (email notifications, background processing)
- **Pydantic** for data validation and serialization
- **JWT authentication** for API security
- **RESTful API** design with OpenAPI/Swagger documentation

### Frontend Modern Stack:
- **React 18+** or **Vue 3** for reactive UI
- **TypeScript** for type safety
- **Tailwind CSS** for utility-first styling
- **Shadcn/ui** or **Material-UI** for component library
- **React Query** or **SWR** for data fetching
- **Zustand** or **Pinia** for state management
- **Vite** for fast development builds
- **Progressive Web App (PWA)** capabilities for offline access

### Additional Features:
- **Image recognition AI** integration (optional):
  - TensorFlow/PyTorch model for disease detection from photos
  - Cloud vision API integration (Google Vision, AWS Rekognition)
- **Real-time chat** with experts (WebSocket/Socket.io)
- **Email notifications** for feedback responses
- **Export functionality** (PDF reports of diagnosis results)
- **Mobile app** (React Native or Flutter)
- **API rate limiting** and monitoring
- **Comprehensive logging** (structured logging with ELK stack)
- **CI/CD pipeline** (GitHub Actions, Docker deployment)

---

## UI/UX Design Guidelines

### Design Principles:
1. **Clean & Professional**: Medical/scientific aesthetic with trustworthy design
2. **Accessibility First**: WCAG AA compliance, keyboard navigation, screen reader support
3. **Mobile Responsive**: Touch-friendly, optimized for field use on smartphones
4. **Visual Hierarchy**: Clear distinction between primary/secondary actions
5. **Consistent**: Design system with reusable components

### Color Palette Suggestions:
- **Primary**: Deep green (#2D5F3E) - represents agriculture/growth
- **Secondary**: Sunflower yellow (#FFB700) - brand identity
- **Accent**: Sky blue (#4A90E2) - trust/technology
- **Neutral**: Warm grays (#F5F5F5, #333333)
- **Success**: #10B981
- **Warning**: #F59E0B
- **Error**: #EF4444

### Typography:
- **Headings**: Inter, Poppins, or Montserrat (bold, clear)
- **Body**: Open Sans, Roboto, or system fonts
- **Khmer Text**: Khmer-friendly font (Noto Sans Khmer, Battambang)

### Key UI Components:
1. **Navigation Bar**: Logo, language switcher, user menu, role badge
2. **Hero Section**: Welcome message, quick stats, CTA buttons
3. **Disease Cards**: Image, title, excerpt, confidence badge, action buttons
4. **Symptom Checker**: 
   - Category accordion/tabs
   - Checkbox grid with labels
   - Selected count badge
   - Submit button with loading state
5. **Dashboard Metrics**: Card grid with icons, numbers, trend indicators
6. **Feedback Form**: Multi-step with photo upload drag-drop
7. **Data Tables**: Sortable, filterable, with pagination
8. **Modal Dialogs**: For confirmations, quick edits
9. **Toast Notifications**: Success/error messages

---

## File Structure Proposal

```
sunflower-diagnosis-v2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app initialization
│   │   ├── config.py                  # Environment configuration
│   │   ├── dependencies.py            # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py            # Auth endpoints
│   │   │   │   ├── diseases.py        # Disease CRUD
│   │   │   │   ├── diagnosis.py       # Symptom checker
│   │   │   │   ├── symptoms.py        # Symptom catalog
│   │   │   │   ├── users.py           # User management
│   │   │   │   ├── feedback.py        # Feedback system
│   │   │   │   └── admin.py           # Admin operations
│   │   │
│   │   ├── core/
│   │   │   ├── security.py            # Auth, JWT, hashing
│   │   │   ├── permissions.py         # RBAC logic
│   │   │   └── exceptions.py          # Custom exceptions
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── disease.py
│   │   │   ├── symptom.py
│   │   │   ├── diagnosis.py
│   │   │   └── feedback.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # Pydantic schemas
│   │   │   ├── disease.py
│   │   │   ├── symptom.py
│   │   │   ├── diagnosis.py
│   │   │   └── feedback.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── diagnosis_engine.py    # Expert system logic
│   │   │   ├── disease_service.py
│   │   │   ├── user_service.py
│   │   │   ├── i18n_service.py
│   │   │   └── storage_service.py     # File uploads
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # SQLAlchemy base
│   │   │   ├── session.py             # Database session
│   │   │   └── migrations/            # Alembic migrations
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── slug.py
│   │   │   ├── validators.py
│   │   │   └── image_processor.py
│   │   │
│   │   └── seeds/
│   │       ├── __init__.py
│   │       ├── diseases.json
│   │       ├── symptoms.json
│   │       └── seed_data.py
│   │
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_diagnosis.py
│   │   ├── test_diseases.py
│   │   └── test_symptoms.py
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   ├── images/
│   │   │   └── diseases/              # Disease images
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── main.tsx                   # App entry
│   │   ├── App.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                    # Reusable UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── DashboardLayout.tsx
│   │   │   │
│   │   │   ├── disease/
│   │   │   │   ├── DiseaseCard.tsx
│   │   │   │   ├── DiseaseDetail.tsx
│   │   │   │   ├── DiseaseForm.tsx
│   │   │   │   └── DiseaseList.tsx
│   │   │   │
│   │   │   ├── diagnosis/
│   │   │   │   ├── SymptomChecker.tsx
│   │   │   │   ├── SymptomCategory.tsx
│   │   │   │   ├── DiagnosisResults.tsx
│   │   │   │   └── DiagnosisHistory.tsx
│   │   │   │
│   │   │   ├── admin/
│   │   │   │   ├── UserManagement.tsx
│   │   │   │   ├── SymptomCatalog.tsx
│   │   │   │   └── FeedbackInbox.tsx
│   │   │   │
│   │   │   └── common/
│   │   │       ├── LanguageSwitcher.tsx
│   │   │       ├── SearchBar.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── DiseaseLibrary.tsx
│   │   │   ├── Diagnose.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── AdminDashboard.tsx
│   │   │   └── DoctorDashboard.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useDiagnosis.ts
│   │   │   ├── useDiseases.ts
│   │   │   └── useI18n.ts
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts              # Axios instance
│   │   │   ├── auth.ts
│   │   │   ├── diseases.ts
│   │   │   ├── diagnosis.ts
│   │   │   └── symptoms.ts
│   │   │
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── diagnosisStore.ts
│   │   │   └── i18nStore.ts
│   │   │
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── disease.ts
│   │   │   ├── symptom.ts
│   │   │   └── diagnosis.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── i18n/
│   │   │   ├── en.json
│   │   │   ├── km.json
│   │   │   └── config.ts
│   │   │
│   │   └── styles/
│   │       ├── globals.css
│   │       └── tailwind.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── .env.example
│   └── README.md
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
1. Set up project structure (backend + frontend)
2. Configure development environment (Docker, databases)
3. Implement core models and database migrations
4. Set up authentication system (JWT)
5. Create basic API endpoints (CRUD for diseases, users)
6. Build frontend scaffolding with routing

### Phase 2: Core Features (Week 3-4)
1. Implement diagnosis engine with rule-based matching
2. Build symptom catalog system
3. Create symptom checker UI with multi-select
4. Develop disease library pages
5. Implement symptom history tracking
6. Add multilingual support (i18n)

### Phase 3: Advanced Features (Week 5-6)
1. Build admin dashboard with management tools
2. Create doctor dashboard for disease/symptom management
3. Implement feedback system with photo uploads
4. Add search functionality
5. Create analytics and reporting
6. Implement role-based access control

### Phase 4: Polish & Optimization (Week 7-8)
1. UI/UX refinements and responsive design
2. Performance optimization (caching, lazy loading)
3. Accessibility improvements (WCAG AA)
4. Security hardening (rate limiting, input validation)
5. Comprehensive testing (unit, integration, e2e)
6. Documentation (API docs, user guides)

### Phase 5: Deployment & Launch (Week 9-10)
1. Set up CI/CD pipeline
2. Configure production environment (cloud hosting)
3. Database migration and seeding
4. Performance monitoring setup
5. User acceptance testing
6. Production deployment

---

## API Endpoints Design

### Authentication
```
POST   /api/v1/auth/register         # Register new user
POST   /api/v1/auth/login            # Login (returns JWT)
POST   /api/v1/auth/logout           # Logout
POST   /api/v1/auth/refresh          # Refresh JWT token
GET    /api/v1/auth/me               # Get current user
PUT    /api/v1/auth/profile          # Update profile
POST   /api/v1/auth/change-password  # Change password
```

### Diseases
```
GET    /api/v1/diseases              # List all diseases (with pagination)
GET    /api/v1/diseases/:slug        # Get disease by slug
POST   /api/v1/diseases              # Create disease (admin/doctor)
PUT    /api/v1/diseases/:id          # Update disease (admin/doctor)
DELETE /api/v1/diseases/:id          # Delete disease (admin)
GET    /api/v1/diseases/search       # Search diseases
POST   /api/v1/diseases/:id/image    # Upload disease image
```

### Diagnosis
```
POST   /api/v1/diagnosis/check       # Submit symptoms, get diagnosis
GET    /api/v1/diagnosis/history     # Get user's diagnosis history
GET    /api/v1/diagnosis/history/:id # Get specific diagnosis details
GET    /api/v1/diagnosis/symptoms    # Get all symptoms grouped by category
```

### Symptoms
```
GET    /api/v1/symptoms              # List all symptoms
GET    /api/v1/symptoms/:id          # Get symptom details
POST   /api/v1/symptoms              # Create symptom (admin/doctor)
PUT    /api/v1/symptoms/:id          # Update symptom (admin/doctor)
DELETE /api/v1/symptoms/:id          # Delete symptom (admin/doctor)
GET    /api/v1/symptoms/categories   # Get symptom categories
```

### Feedback
```
POST   /api/v1/feedback              # Submit feedback
GET    /api/v1/feedback              # List feedback (admin/doctor)
GET    /api/v1/feedback/:id          # Get feedback details
PUT    /api/v1/feedback/:id/status   # Update feedback status
POST   /api/v1/feedback/:id/respond  # Respond to feedback
```

### Admin
```
GET    /api/v1/admin/users           # List all users
PUT    /api/v1/admin/users/:id/role  # Change user role
GET    /api/v1/admin/stats           # System statistics
GET    /api/v1/admin/logs            # Diagnosis logs
GET    /api/v1/admin/roles           # List roles
POST   /api/v1/admin/roles           # Create role
```

### I18n
```
GET    /api/v1/i18n/:lang            # Get all translations for language
PUT    /api/v1/i18n/:lang/:key       # Update translation (admin)
```

---

## Testing Strategy

### Backend Tests:
- **Unit Tests**: Test individual functions (diagnosis engine, validators)
- **Integration Tests**: Test API endpoints with database
- **Security Tests**: Test authentication, authorization, CSRF protection
- **Performance Tests**: Load testing for diagnosis endpoint

### Frontend Tests:
- **Component Tests**: Test UI components in isolation (Jest + Testing Library)
- **Integration Tests**: Test user flows (symptom checker workflow)
- **E2E Tests**: Test complete scenarios (Playwright/Cypress)
- **Accessibility Tests**: Automated a11y testing (axe-core)

### Test Coverage Goals:
- Backend: >80% code coverage
- Frontend: >70% code coverage
- Critical paths: 100% coverage (auth, diagnosis, RBAC)

---

## Deployment Recommendations

### Hosting Options:
1. **DigitalOcean App Platform** (easiest, managed)
2. **AWS** (EC2 + RDS + S3 for scalability)
3. **Heroku** (simple deployment, good for MVP)
4. **Render** (modern alternative to Heroku)
5. **Self-hosted** (VPS with Docker Compose)

### Production Checklist:
- [ ] Environment variables secured (secrets management)
- [ ] HTTPS enabled (SSL certificates)
- [ ] Database backups configured (automated daily)
- [ ] Monitoring setup (Sentry, LogRocket, DataDog)
- [ ] CDN for static assets (CloudFlare, AWS CloudFront)
- [ ] Rate limiting enabled (Redis-based)
- [ ] CORS properly configured
- [ ] Database connection pooling
- [ ] Gzip compression enabled
- [ ] Security headers configured
- [ ] Error logging and alerting
- [ ] Performance monitoring (New Relic, Prometheus)

---

## Success Metrics

### Technical Metrics:
- Page load time < 2 seconds
- API response time < 200ms (95th percentile)
- Database query time < 50ms average
- 99.9% uptime
- Mobile Lighthouse score > 90

### User Metrics:
- Diagnosis completion rate > 80%
- Average symptoms selected per check: 4-6
- Feedback submission rate on no-match: > 30%
- Return user rate > 40%
- Mobile usage > 60%

### Business Metrics:
- User registration growth
- Diseases diagnosed per week
- Expert feedback response time < 24h
- System accuracy improvement over time

---

## Security Considerations

### Authentication & Authorization:
- JWT with short expiration (15 min access, 7 day refresh)
- Secure password hashing (bcrypt with 12 rounds)
- Role-based access control (RBAC) strictly enforced
- Permission decorators on all protected endpoints
- Session invalidation on logout

### Data Protection:
- SQL injection prevention (parameterized queries)
- XSS prevention (input sanitization, CSP headers)
- CSRF protection on all state-changing requests
- File upload validation (type, size, content)
- Sensitive data encryption at rest

### API Security:
- Rate limiting per user/IP
- Request size limits
- API versioning for backward compatibility
- CORS whitelist for allowed origins
- Security headers (HSTS, X-Frame-Options, etc.)

---

## Future Enhancements

### AI/ML Integration:
- Image-based disease detection using CNN models
- Predictive analytics for disease outbreaks
- Personalized recommendations based on region/season
- Chatbot for interactive diagnosis

### Mobile App:
- Native iOS/Android apps (React Native/Flutter)
- Offline mode with local database sync
- Camera integration for disease photo capture
- Push notifications for expert responses

### Community Features:
- User forums for farmers to share experiences
- Disease reports map (geolocation-based)
- Expert Q&A section
- Success story sharing

### Integration:
- Weather API integration for environmental context
- Agricultural calendar integration
- Market price integration
- Government agriculture portal integration

---

## Summary

This project requires building a robust, professional expert system for sunflower disease diagnosis with:

✅ **Modern tech stack** (FastAPI/React, PostgreSQL, Redis)  
✅ **Clean architecture** (separation of concerns, testable)  
✅ **Professional UI/UX** (responsive, accessible, intuitive)  
✅ **Comprehensive features** (diagnosis, library, analytics, RBAC)  
✅ **Multilingual support** (English/Khmer)  
✅ **Security-first approach** (authentication, authorization, validation)  
✅ **Scalable design** (microservices-ready, cloud-native)  
✅ **Production-ready** (monitoring, logging, CI/CD)

The goal is to create a tool that empowers farmers and agricultural professionals to quickly and accurately identify sunflower diseases, leading to better crop management and increased yields.

---

## How to Use This Prompt

### For AI Agents:
```
Please create a new version of the Doctor Sunflower disease diagnosis system based on the specifications in PROJECT_REBUILD_PROMPT.md. Focus on:

1. Modern tech stack (FastAPI + React with TypeScript)
2. Professional UI design with Tailwind CSS
3. Implement the diagnosis engine first
4. Follow the file structure exactly
5. Include comprehensive error handling
6. Add detailed code comments
7. Create a working MVP with core features

Start with Phase 1 and ask for confirmation before proceeding to each next phase.
```

### For Human Developers:
Read through each section carefully and use this as a blueprint for:
- Understanding project requirements
- Estimating time and resources
- Planning sprints and milestones
- Choosing appropriate technologies
- Designing system architecture
- Creating user stories and tasks

Feel free to adapt the tech stack based on your team's expertise while maintaining the core features and user experience standards.
