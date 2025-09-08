@echo off
REM Google Drive MCP Server Setup Script for Windows

echo ========================================
echo Google Drive MCP Server Setup
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found
    echo Please install Node.js 18+ from: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Node.js found: 
node --version

REM Check if npx is available
npx --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npx not found
    echo Please install Node.js 18+ from: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] npx is available

REM Create credentials directory
set CREDS_DIR=%USERPROFILE%\.config\gdrive-mcp
if not exist "%CREDS_DIR%" (
    mkdir "%CREDS_DIR%"
    echo [INFO] Created credentials directory: %CREDS_DIR%
) else (
    echo [INFO] Credentials directory exists: %CREDS_DIR%
)

echo.
echo ========================================
echo Google OAuth Setup Instructions
echo ========================================
echo.
echo To set up Google Drive MCP server, you need to:
echo.
echo 1. Go to Google Cloud Console: https://console.cloud.google.com/
echo.
echo 2. Create or select a project:
echo    - Click "Select a project" dropdown
echo    - Click "New Project" if needed
echo    - Give it a name like "MCP-GDrive-Integration"
echo.
echo 3. Enable Google Drive API:
echo    - Go to "APIs & Services" ^> "Library"
echo    - Search for "Google Drive API"
echo    - Click on it and click "Enable"
echo.
echo 4. Create OAuth 2.0 Credentials:
echo    - Go to "APIs & Services" ^> "Credentials"
echo    - Click "Create Credentials" ^> "OAuth client ID"
echo    - If prompted, configure OAuth consent screen:
echo      * Choose "External" user type
echo      * Fill in App name: "MCP GDrive"
echo      * Add your email as developer contact
echo      * Save and continue through scopes (no changes needed)
echo      * Add your email as test user
echo    - Choose "Desktop application" as application type
echo    - Name it "MCP GDrive Client"
echo    - Click "Create"
echo    - Download the JSON file
echo.
echo 5. Save the credentials:
echo    - Rename the downloaded file to "credentials.json"
echo    - Place it in: %CREDS_DIR%
echo.
echo After completing these steps, press Enter to continue...
pause >nul

REM Check for credentials file
set CREDS_FILE=%CREDS_DIR%\credentials.json
if exist "%CREDS_FILE%" (
    echo [INFO] Credentials file found: %CREDS_FILE%
    
    echo [INFO] Installing/updating Google Drive MCP server...
    npx -y @modelcontextprotocol/server-gdrive@latest --version
    
    echo [INFO] Running authentication flow...
    npx -y @modelcontextprotocol/server-gdrive auth --credentials "%CREDS_FILE%"
    
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo Setup Completed Successfully!
        echo ========================================
        echo.
        echo MCP Server Configuration for Qoder:
        echo.
        echo Server Name: gdrive
        echo Command: npx
        echo Arguments: ["@modelcontextprotocol/server-gdrive"]
        echo.
        echo Next steps:
        echo 1. Add the MCP server configuration in Qoder
        echo 2. Restart Qoder IDE
        echo 3. Test the Google Drive integration
    ) else (
        echo [ERROR] Authentication failed
        echo Please check your credentials and try again
    )
) else (
    echo [ERROR] Credentials file not found: %CREDS_FILE%
    echo Please complete the OAuth setup first
    echo.
    echo Expected file location: %CREDS_DIR%\credentials.json
)

echo.
pause