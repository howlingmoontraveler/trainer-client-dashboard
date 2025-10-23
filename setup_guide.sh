#!/bin/bash

# Trainer-Client Dashboard Setup Script
# This script creates all necessary files for the dashboard application

echo "Creating Trainer-Client Dashboard..."

# Create directory structure
mkdir -p templates static/css

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
Werkzeug==3.0.1
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Database
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Flask
instance/
.webassets-cache

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store

# Logs
*.log
EOF

echo "✓ Created requirements.txt and .gitignore"
echo ""
echo "========================================="
echo "Files created successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Download all files from: /home/user/trainer-client-dashboard/"
echo "2. Or copy the complete project directory to your local machine"
echo "3. Run: pip install -r requirements.txt"
echo "4. Run: python app.py"
echo "5. Access: http://localhost:5000"
echo ""
echo "Demo login:"
echo "  Username: trainer1"
echo "  Password: password123"
echo ""
