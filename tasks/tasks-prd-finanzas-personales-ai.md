# Task List: Sistema de Finanzas Personales con AI

Generated from: `prd-finanzas-personales-ai.md`

## Relevant Files

**Backend (Django):**
- `backend/manage.py` - Django project entry point
- `backend/afp_v2/settings.py` - Django settings with OAuth, API, and security configurations
- `backend/afp_v2/urls.py` - Main URL configuration
- `backend/accounts/models.py` - User authentication and OAuth integration models
- `backend/accounts/views.py` - Authentication API endpoints and OAuth handlers
- `backend/accounts/tests.py` - Unit tests for authentication functionality
- `backend/transactions/models.py` - Transaction, Account, and Category models
- `backend/transactions/views.py` - Transaction management API endpoints
- `backend/transactions/tests.py` - Unit tests for transaction functionality
- `backend/emails/models.py` - Email template and processing models
- `backend/emails/services.py` - Email processing service and AI integration
- `backend/emails/tasks.py` - Celery tasks for asynchronous email processing
- `backend/emails/views.py` - Email management API endpoints
- `backend/emails/tests.py` - Unit tests for email processing functionality
- `backend/requirements.txt` - Python dependencies
- `backend/Dockerfile` - Docker configuration for deployment

**Frontend (React):**
- `frontend/package.json` - Node.js dependencies and scripts
- `frontend/src/App.tsx` - Main React application component
- `frontend/src/components/auth/LoginPage.tsx` - OAuth login interface
- `frontend/src/components/auth/SignupPage.tsx` - User registration interface
- `frontend/src/components/dashboard/Dashboard.tsx` - Main dashboard with transactions
- `frontend/src/components/dashboard/TransactionList.tsx` - Transaction display component
- `frontend/src/components/dashboard/AccountBalance.tsx` - Account balances component
- `frontend/src/components/emails/EmailConnection.tsx` - Email setup and connection interface
- `frontend/src/components/emails/EmailTemplateManager.tsx` - Template management interface
- `frontend/src/hooks/useAuth.ts` - Authentication state management
- `frontend/src/hooks/useTransactions.ts` - Transaction data management
- `frontend/src/services/api.ts` - API client configuration
- `frontend/src/types/index.ts` - TypeScript type definitions
- `frontend/tailwind.config.js` - Tailwind CSS configuration
- `frontend/Dockerfile` - Docker configuration for deployment

**Infrastructure:**
- `docker-compose.yml` - Development environment orchestration
- `railway.json` - Railway deployment configuration
- `.env.example` - Environment variables template
- `README.md` - Project setup and deployment instructions

### Notes

- Backend tests use Django's built-in testing framework: `python manage.py test`
- Frontend tests use Jest and React Testing Library: `npm test`
- Celery workers for email processing: `celery -A afp_v2 worker --loglevel=info`
- Redis required for Celery task queue and caching

## Tasks

- [ ] 1.0 Project Setup & Infrastructure
  - [ ] 1.1 Initialize Django backend project with proper structure
  - [ ] 1.2 Set up PostgreSQL database configuration
  - [ ] 1.3 Configure Redis for Celery task queue and caching
  - [ ] 1.4 Create React frontend project with TypeScript and Tailwind CSS
  - [ ] 1.5 Set up Docker containers for development environment
  - [ ] 1.6 Configure environment variables and secrets management
  - [ ] 1.7 Set up Railway deployment configuration
  - [ ] 1.8 Create comprehensive README with setup instructions

- [ ] 2.0 Backend Authentication & Security
  - [ ] 2.1 Implement User model with email fields for transaction processing
  - [ ] 2.2 Set up Google OAuth integration with proper scopes for Gmail API
  - [ ] 2.3 Set up Microsoft OAuth integration with proper scopes for Outlook API
  - [ ] 2.4 Implement JWT token system with automatic refresh rotation
  - [ ] 2.5 Create encrypted storage system for OAuth API tokens
  - [ ] 2.6 Implement audit logging for all API access and user actions
  - [ ] 2.7 Set up API rate limiting and security middleware
  - [ ] 2.8 Create user registration and login API endpoints
  - [ ] 2.9 Implement webhook endpoints for future integrations (Twilio)

- [ ] 3.0 Email Processing & AI Integration
  - [ ] 3.1 Create EmailProvider model to store user email addresses for processing
  - [ ] 3.2 Create EmailTemplate model to store regex patterns for banks
  - [ ] 3.3 Implement Gmail API service for reading user emails
  - [ ] 3.4 Implement Outlook/Microsoft Graph API service for reading emails
  - [ ] 3.5 Create AI service for generating regex templates from email HTML
  - [ ] 3.6 Implement email content parser using regex templates
  - [ ] 3.7 Create feedback system for improving template accuracy
  - [ ] 3.8 Set up Celery tasks for asynchronous email processing
  - [ ] 3.9 Implement email sender validation to prevent fake email processing
  - [ ] 3.10 Create API endpoints for email management and template administration

- [ ] 4.0 Transaction Management System
  - [ ] 4.1 Create Account model for different account types (checking, savings, credit, loans)
  - [ ] 4.2 Create Transaction model with proper categorization fields
  - [ ] 4.3 Create Category model with basic financial categories
  - [ ] 4.4 Implement transaction extraction logic from parsed email data
  - [ ] 4.5 Create transfer detection algorithm to identify account-to-account movements
  - [ ] 4.6 Implement balance calculation logic that handles transfers correctly
  - [ ] 4.7 Create transaction categorization service with AI assistance
  - [ ] 4.8 Implement transaction deduplication to prevent duplicates
  - [ ] 4.9 Create API endpoints for transaction CRUD operations
  - [ ] 4.10 Implement transaction filtering and search functionality

- [ ] 5.0 Frontend Application & User Interface
  - [ ] 5.1 Set up React Router for SPA navigation
  - [ ] 5.2 Create authentication context and OAuth login components
  - [ ] 5.3 Implement user registration and login pages
  - [ ] 5.4 Create main dashboard layout with navigation
  - [ ] 5.5 Build email connection setup interface
  - [ ] 5.6 Create transaction list component with filtering and pagination
  - [ ] 5.7 Build account balance display components
  - [ ] 5.8 Implement transaction categorization interface with user overrides
  - [ ] 5.9 Create email template management interface for admin users
  - [ ] 5.10 Add real-time processing status indicators
  - [ ] 5.11 Implement error handling and user feedback components
  - [ ] 5.12 Add responsive design and mobile optimization 