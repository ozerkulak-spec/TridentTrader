# 🚀 Trident Trader PRO v2.0 - Deployment Script
# One-click deployment for local and production environments

# PowerShell Deployment Script

Write-Host "🔱 Trident Trader PRO v2.0 - Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1️⃣  Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Check directory
if (-not (Test-Path "bot_v2_pro.py")) {
    Write-Host "❌ bot_v2_pro.py not found! Run from automation/ directory" -ForegroundColor Red
    exit 1
}

# Menu
Write-Host ""
Write-Host "Select deployment mode:" -ForegroundColor Cyan
Write-Host "1) 🧪 Local Development (with .env file)"
Write-Host "2) 🚀 Production Deploy (Render.com)"
Write-Host "3) 🐳 Docker Build"
Write-Host "4) 🧹 Clean & Reset"
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🧪 LOCAL DEVELOPMENT SETUP" -ForegroundColor Cyan
        Write-Host "=============================" -ForegroundColor Cyan
        
        # Create venv
        Write-Host ""
        Write-Host "2️⃣  Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
        
        # Activate venv
        Write-Host ""
        Write-Host "3️⃣  Activating virtual environment..." -ForegroundColor Yellow
        . .\venv\Scripts\Activate.ps1
        Write-Host "✅ Virtual environment activated" -ForegroundColor Green
        
        # Install dependencies
        Write-Host ""
        Write-Host "4️⃣  Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
        
        # Setup .env
        Write-Host ""
        Write-Host "5️⃣  Setting up environment..." -ForegroundColor Yellow
        if (-not (Test-Path ".env")) {
            Copy-Item ".env.example" ".env"
            Write-Host "✅ .env file created from template" -ForegroundColor Green
            Write-Host "⚠️  IMPORTANT: Edit .env file with your API keys!" -ForegroundColor Yellow
            notepad .env
        } else {
            Write-Host "✅ .env file already exists" -ForegroundColor Green
        }
        
        # Create directories
        Write-Host ""
        Write-Host "6️⃣  Creating directories..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path "data" | Out-Null
        New-Item -ItemType Directory -Force -Path "logs" | Out-Null
        New-Item -ItemType Directory -Force -Path "static" | Out-Null
        New-Item -ItemType Directory -Force -Path "templates" | Out-Null
        Write-Host "✅ Directories created" -ForegroundColor Green
        
        # Test import
        Write-Host ""
        Write-Host "7️⃣  Testing bot..." -ForegroundColor Yellow
        python -c "import bot_v2_pro; print('✅ Bot module loaded successfully')"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Bot test failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "✅ LOCAL SETUP COMPLETE!" -ForegroundColor Green
        Write-Host ""
        Write-Host "To start the bot:" -ForegroundColor Cyan
        Write-Host "  python bot_v2_pro.py" -ForegroundColor White
        Write-Host ""
        Write-Host "Or with auto-reload:" -ForegroundColor Cyan
        Write-Host "  uvicorn bot_v2_pro:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
        Write-Host ""
        Write-Host "Dashboard will be at: http://localhost:8000" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host ""
        Write-Host "🚀 PRODUCTION DEPLOYMENT (Render.com)" -ForegroundColor Cyan
        Write-Host "======================================" -ForegroundColor Cyan
        
        # Check git
        Write-Host ""
        Write-Host "2️⃣  Checking Git..." -ForegroundColor Yellow
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Git not found! Please install Git" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ $gitVersion" -ForegroundColor Green
        
        # Initialize git if needed
        if (-not (Test-Path ".git")) {
            Write-Host ""
            Write-Host "3️⃣  Initializing Git repository..." -ForegroundColor Yellow
            git init
            Write-Host "✅ Git initialized" -ForegroundColor Green
        }
        
        # Create .gitignore
        Write-Host ""
        Write-Host "4️⃣  Creating .gitignore..." -ForegroundColor Yellow
        @"
.env
venv/
__pycache__/
*.pyc
*.pyo
*.db
logs/
data/
.DS_Store
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
        Write-Host "✅ .gitignore created" -ForegroundColor Green
        
        # Commit
        Write-Host ""
        Write-Host "5️⃣  Committing files..." -ForegroundColor Yellow
        git add .
        git commit -m "Deploy Trident Trader PRO v2.0" 2>&1 | Out-Null
        Write-Host "✅ Files committed" -ForegroundColor Green
        
        # Get GitHub repo
        Write-Host ""
        Write-Host "6️⃣  GitHub Setup" -ForegroundColor Yellow
        Write-Host "   Create a new repository on GitHub: https://github.com/new" -ForegroundColor White
        Write-Host ""
        $repoUrl = Read-Host "   Enter your GitHub repo URL (https://github.com/user/repo.git)"
        
        git remote remove origin 2>&1 | Out-Null
        git remote add origin $repoUrl
        git branch -M main
        git push -u origin main
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Git push failed. Please check your repository URL and credentials" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Code pushed to GitHub" -ForegroundColor Green
        
        # Render instructions
        Write-Host ""
        Write-Host "7️⃣  Next Steps on Render.com:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   1. Go to https://render.com and sign in" -ForegroundColor White
        Write-Host "   2. Click 'New +' → 'Web Service'" -ForegroundColor White
        Write-Host "   3. Connect your GitHub repo: $repoUrl" -ForegroundColor White
        Write-Host "   4. Configure:" -ForegroundColor White
        Write-Host "      - Name: trident-trader-pro" -ForegroundColor Gray
        Write-Host "      - Environment: Python 3" -ForegroundColor Gray
        Write-Host "      - Build Command: pip install -r requirements.txt" -ForegroundColor Gray
        Write-Host "      - Start Command: python bot_v2_pro.py" -ForegroundColor Gray
        Write-Host "      - Plan: Free" -ForegroundColor Gray
        Write-Host "   5. Add Environment Variables:" -ForegroundColor White
        Write-Host "      - BINANCE_API_KEY=your_key" -ForegroundColor Gray
        Write-Host "      - BINANCE_API_SECRET=your_secret" -ForegroundColor Gray
        Write-Host "      - WEBHOOK_SECRET=random_32_chars" -ForegroundColor Gray
        Write-Host "      - USE_TESTNET=true" -ForegroundColor Gray
        Write-Host "   6. Click 'Create Web Service'" -ForegroundColor White
        Write-Host ""
        Write-Host "✅ DEPLOYMENT READY!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host ""
        Write-Host "🐳 DOCKER BUILD" -ForegroundColor Cyan
        Write-Host "================" -ForegroundColor Cyan
        
        # Check Docker
        Write-Host ""
        Write-Host "2️⃣  Checking Docker..." -ForegroundColor Yellow
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker not found! Please install Docker Desktop" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ $dockerVersion" -ForegroundColor Green
        
        # Build image
        Write-Host ""
        Write-Host "3️⃣  Building Docker image..." -ForegroundColor Yellow
        docker build -t trident-trader-pro:v2.0 .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker build failed" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Docker image built" -ForegroundColor Green
        
        # Run container
        Write-Host ""
        Write-Host "4️⃣  Starting container..." -ForegroundColor Yellow
        Write-Host "   Make sure .env file exists with your API keys!" -ForegroundColor Yellow
        
        $runContainer = Read-Host "   Start container now? (y/n)"
        if ($runContainer -eq "y") {
            docker run -d `
                --name trident-bot `
                -p 8000:8000 `
                --env-file .env `
                -v ${PWD}/data:/app/data `
                -v ${PWD}/logs:/app/logs `
                trident-trader-pro:v2.0
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Container started" -ForegroundColor Green
                Write-Host ""
                Write-Host "Dashboard at: http://localhost:8000" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "View logs: docker logs -f trident-bot" -ForegroundColor White
                Write-Host "Stop: docker stop trident-bot" -ForegroundColor White
                Write-Host "Remove: docker rm trident-bot" -ForegroundColor White
            } else {
                Write-Host "❌ Failed to start container" -ForegroundColor Red
            }
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "🧹 CLEAN & RESET" -ForegroundColor Cyan
        Write-Host "================" -ForegroundColor Cyan
        Write-Host ""
        
        $confirm = Read-Host "⚠️  This will delete venv, logs, and database. Continue? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "Cancelled" -ForegroundColor Yellow
            exit 0
        }
        
        Write-Host ""
        Write-Host "Cleaning..." -ForegroundColor Yellow
        
        Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force logs -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force data -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
        Remove-Item *.db -ErrorAction SilentlyContinue
        
        Write-Host "✅ Cleaned!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Run deployment again to reinstall" -ForegroundColor Cyan
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔱 Trident Trader PRO v2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
