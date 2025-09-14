# AFP_V2 - Personal Finance AI System
# Makefile for project setup and development

# Version Configuration
CREATE_VITE_VERSION = 7.1.1
NODE_MIN_VERSION = 20

.PHONY: help setup-backend setup-frontend setup-full run-backend run-frontend run-both test-backend test-frontend test-both clean-backend clean-frontend clean-all

# Default target
help:
	@echo "AFP_V2 - Personal Finance AI System"
	@echo ""
	@echo "📋 Configuration:"
	@echo "  Create-Vite: $(CREATE_VITE_VERSION)"
	@echo "  Node.js Min:  v$(NODE_MIN_VERSION)"
	@echo ""
	@echo "🚀 Quick Start Commands:"
	@echo "  setup-full      Complete setup for both backend and frontend"
	@echo "  setup-backend   Complete backend setup + install + migrations + superuser"
	@echo "  setup-frontend  Complete frontend setup + install + Vite project creation"
	@echo ""
	@echo "🏃 Development Commands:"
	@echo "  run-backend     Run Django development server (port 8000)"
	@echo "  run-frontend    Run Vite development server (port 3000)"
	@echo "  run-both        Run both backend and frontend concurrently"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  test-backend    Run Django tests"
	@echo "  test-frontend   Run Vitest tests"
	@echo "  test-both       Run all tests"
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@echo "  clean-backend   Clean backend cache and temp files"
	@echo "  clean-frontend  Clean frontend node_modules and build files"
	@echo "  clean-all       Clean everything"
	
# Complete backend setup without running server
setup-backend:
	@echo "🚀 Starting complete backend setup..."
	@echo ""
	
	# Check if .env exists
	@echo "🔍 Checking backend environment..."
	@mkdir -p backend
	@if [ ! -f backend/.env ]; then \
		if [ -f backend/example.env ]; then \
			echo "📝 Creating backend/.env from example.env..."; \
			cp backend/example.env backend/.env; \
			echo "✅ Backend .env created from example.env"; \
			echo "⚠️  Please edit backend/.env with your actual values before continuing"; \
			echo "Press Enter when ready to continue..."; \
			read dummy; \
		else \
			echo "❌ Error: backend/example.env not found!"; \
			echo "Please create backend/example.env first, then run this command again"; \
			exit 1; \
		fi; \
	else \
		echo "✅ Backend .env file exists"; \
	fi
	
	# Check Python installation
	@echo ""
	@echo "🐍 Checking Python installation..."
	@if ! command -v python3 >/dev/null 2>&1; then \
		echo "❌ Error: Python 3 is not installed!"; \
		echo "Please install Python 3 first"; \
		exit 1; \
	else \
		echo "✅ Python 3 is installed: $$(python3 --version)"; \
	fi
	
	# Create and activate virtual environment
	@echo ""
	@echo "🔧 Setting up virtual environment..."
	@if [ ! -d backend/.venv ]; then \
		echo "📦 Creating virtual environment..."; \
		cd backend && python3 -m venv .venv; \
		echo "✅ Virtual environment created"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi
	
	# Install dependencies
	@echo ""
	@echo "📦 Installing Python dependencies..."
	@cd backend && \
	source .venv/bin/activate && \
	if [ -f pyproject.toml ]; then \
		pip install -e .; \
	elif [ -f requirements.txt ]; then \
		pip install -r requirements.txt; \
	else \
		echo "⚠️  No pyproject.toml or requirements.txt found"; \
	fi
	
	# Check if Django project exists, create if not
	@echo ""
	@echo "🔍 Checking Django project..."
	@cd backend && \
	source .venv/bin/activate && \
	if [ ! -f manage.py ]; then \
		echo "📝 Creating Django project..."; \
		django-admin startproject afp_v2 .; \
		echo "✅ Django project created"; \
	else \
		echo "✅ Django project already exists"; \
	fi
	
	# Run migrations
	@echo ""
	@echo "🔄 Running Django migrations..."
	@cd backend && \
	source .venv/bin/activate && \
	python manage.py migrate
	
	# Check and create superuser
	@echo ""
	@echo "👤 Checking Django superuser..."
	@cd backend && \
	source .venv/bin/activate && \
	if python manage.py shell -c "from django.contrib.auth.models import User; print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')" | grep -q "exists"; then \
		echo "✅ Superuser already exists"; \
	else \
		echo "📝 Creating superuser with default credentials..."; \
		echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@afp.com', 'admin123')" | python manage.py shell; \
		echo "✅ Superuser created successfully!"; \
	fi; \
	echo ""; \
	echo "🔑 Superuser Credentials:"; \
	echo "   Username: admin"; \
	echo "   Email: admin@afp.com"; \
	echo "   Password: admin123"; \
	echo ""; \
	echo "⚠️  IMPORTANT: Change these credentials in production!"; \
	echo "   Access admin panel at: http://localhost:8000/admin"
	
	# Setup complete
	@echo ""
	@echo "✅ Backend setup completed successfully!"
	@echo ""
	@echo "🚀 To start the development server, run:"
	@echo "   make run-backend"
	@echo ""
	@echo "🔧 Admin panel will be available at: http://localhost:8000/admin"

# Run Django development server only
run-backend:
	@echo "🚀 Starting Django development server..."
	@echo ""
	@if [ ! -d backend/.venv ]; then \
		echo "❌ Error: Virtual environment not found!"; \
		echo "Please run 'make setup-backend' first"; \
		exit 1; \
	fi
	@if [ ! -f backend/manage.py ]; then \
		echo "❌ Error: Django project not found!"; \
		echo "Please run 'make setup-backend' first"; \
		exit 1; \
	fi
	@echo "🐍 Backend running on: http://localhost:8000"
	@echo "🔧 Admin panel: http://localhost:8000/admin"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@cd backend && \
	source .venv/bin/activate && \
	python manage.py runserver

# ============================================================================
# FRONTEND COMMANDS
# ============================================================================

# Complete frontend setup
setup-frontend:
	@echo "🚀 Starting complete frontend setup..."
	@echo ""
	
	# Create frontend directory if it doesn't exist
	@echo "📁 Setting up frontend directory..."
	@mkdir -p frontend
	
	# Check Node.js installation in frontend directory
	@echo ""
	@echo "📦 Checking Node.js installation..."
	@cd frontend && \
	if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Error: Node.js is not installed!"; \
		echo "Please install Node.js (v$(NODE_MIN_VERSION) or higher) first"; \
		echo "Visit: https://nodejs.org/"; \
		exit 1; \
	else \
		echo "✅ Node.js is installed: $$(node --version)"; \
		NODE_MAJOR=$$(node --version | cut -d'.' -f1 | sed 's/v//'); \
		if [ "$$NODE_MAJOR" -lt "$(NODE_MIN_VERSION)" ]; then \
			echo "❌ Error: Node.js version $$NODE_MAJOR is too old!"; \
			echo "Please upgrade to Node.js v$(NODE_MIN_VERSION) or higher"; \
			exit 1; \
		fi; \
	fi
	
	# Check npm installation in frontend directory
	@cd frontend && \
	if ! command -v npm >/dev/null 2>&1; then \
		echo "❌ Error: npm is not installed!"; \
		echo "Please install npm first"; \
		exit 1; \
	else \
		echo "✅ npm is installed: $$(npm --version)"; \
	fi
	
	
	# Check if package.json exists, if not create Vite project
	@echo ""
	@echo "🔍 Checking frontend project..."
	@if [ ! -f frontend/package.json ]; then \
		echo "📝 Creating Vite + React + TypeScript project..."; \
		cd frontend && npm create vite@$(CREATE_VITE_VERSION) . -- --template react-ts; \
		echo "✅ Vite project created"; \
	else \
		echo "✅ Frontend project already exists"; \
	fi
	
	# Install dependencies
	@echo ""
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	
	# Note: Additional dependencies will be installed manually as needed
	@echo ""
	@echo "📝 Basic Vite project created. Additional dependencies can be installed with:"
	@echo "   cd frontend && npm install <package-name>"
	
	# Tailwind CSS can be initialized later with: cd frontend && npx tailwindcss init -p
	
	# Create basic environment file
	@echo ""
	@echo "🔧 Setting up environment variables..."
	@if [ ! -f frontend/.env.example ]; then \
		echo "📝 Creating frontend/.env.example..."; \
		echo "# Frontend Environment Variables" > frontend/.env.example; \
		echo "VITE_API_URL=http://localhost:8000" >> frontend/.env.example; \
		echo "VITE_APP_NAME=AFP V2" >> frontend/.env.example; \
		echo "VITE_APP_VERSION=0.1.0" >> frontend/.env.example; \
		echo "✅ Frontend .env.example created"; \
	else \
		echo "✅ Frontend .env.example already exists"; \
	fi
	
	@if [ ! -f frontend/.env.local ]; then \
		echo "📝 Creating frontend/.env.local from example..."; \
		cp frontend/.env.example frontend/.env.local; \
		echo "✅ Frontend .env.local created"; \
	else \
		echo "✅ Frontend .env.local already exists"; \
	fi
	
	# Setup complete
	@echo ""
	@echo "✅ Frontend setup completed successfully!"
	@echo ""
	@echo "🚀 To start the development server, run:"
	@echo "   make run-frontend"
	@echo ""
	@echo "🌐 Frontend will be available at: http://localhost:3000"

# Run Vite development server only
run-frontend:
	@echo "🚀 Starting Vite development server..."
	@echo ""
	@if [ ! -d frontend/node_modules ]; then \
		echo "❌ Error: Node modules not found!"; \
		echo "Please run 'make setup-frontend' first"; \
		exit 1; \
	fi
	@if [ ! -f frontend/package.json ]; then \
		echo "❌ Error: Frontend project not found!"; \
		echo "Please run 'make setup-frontend' first"; \
		exit 1; \
	fi
	@echo "⚡ Frontend running on: http://localhost:3000"
	@echo "🔄 Hot reload enabled"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@cd frontend && npm run dev

# Run both backend and frontend concurrently
run-both:
	@echo "🚀 Starting both backend and frontend servers..."
	@echo ""
	@if [ ! -d backend/.venv ]; then \
		echo "❌ Error: Backend not set up!"; \
		echo "Please run 'make setup-backend' first"; \
		exit 1; \
	fi
	@if [ ! -d frontend/node_modules ]; then \
		echo "❌ Error: Frontend not set up!"; \
		echo "Please run 'make setup-frontend' first"; \
		exit 1; \
	fi
	@echo "🐍 Backend: http://localhost:8000"
	@echo "⚡ Frontend: http://localhost:3000"
	@echo "Press Ctrl+C to stop both servers"
	@echo ""
	@echo "Starting servers in 3 seconds..."
	@sleep 3
	@(cd backend && source .venv/bin/activate && python manage.py runserver) & \
	(cd frontend && npm run dev) & \
	wait

# Complete setup for both backend and frontend
setup-full: setup-backend setup-frontend
	@echo ""
	@echo "🎉 Complete setup finished!"
	@echo ""
	@echo "🚀 To start development, run:"
	@echo "   make run-both"
	@echo ""
	@echo "🌐 URLs:"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Admin:    http://localhost:8000/admin"

# ============================================================================
# TESTING COMMANDS
# ============================================================================

# Run frontend tests
test-frontend:
	@echo "🧪 Running frontend tests..."
	@if [ ! -d frontend/node_modules ]; then \
		echo "❌ Error: Frontend not set up!"; \
		echo "Please run 'make setup-frontend' first"; \
		exit 1; \
	fi
	@cd frontend && npm run test

# Run backend tests
test-backend:
	@echo "🧪 Running backend tests..."
	@if [ ! -d backend/.venv ]; then \
		echo "❌ Error: Backend not set up!"; \
		echo "Please run 'make setup-backend' first"; \
		exit 1; \
	fi
	@cd backend && source .venv/bin/activate && python manage.py test

# Run all tests
test-both: test-backend test-frontend
	@echo "✅ All tests completed!"

# ============================================================================
# CLEANUP COMMANDS
# ============================================================================

# Clean backend files
clean-backend:
	@echo "🧹 Cleaning backend files..."
	@rm -rf backend/.venv
	@rm -rf backend/__pycache__
	@rm -rf backend/*/__pycache__
	@rm -rf backend/*/*/__pycache__
	@rm -rf backend/.pytest_cache
	@rm -f backend/db.sqlite3
	@echo "✅ Backend cleaned"

# Clean frontend files
clean-frontend:
	@echo "🧹 Cleaning frontend files..."
	@rm -rf frontend/node_modules
	@rm -rf frontend/dist
	@rm -rf frontend/.vite
	@rm -f frontend/package-lock.json
	@echo "✅ Frontend cleaned"

# Clean everything
clean-all: clean-backend clean-frontend
	@echo "✅ Everything cleaned!"
