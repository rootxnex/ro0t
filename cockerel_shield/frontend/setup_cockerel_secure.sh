#!/bin/bash

echo "🛡️ Setting up Cocokerel Shield secure workspace..."

# 1. Create project folders
mkdir -p ~/CockerelShield/public/{frontend,backend} mkdir -p 
~/CockerelShield/private/{ai_engine,rnd_docs} mkdir -p 
~/CockerelShield/data

# 2. Create virtual environment (optional)
python3 -m venv ~/CockerelShield/venv

# 3. Create .env file (keep secrets here)
echo "# Secrets go here" > ~/CockerelShield/.env

# 4. Create .gitignore to hide secrets
cat <<EOL > ~/CockerelShield/.gitignore .env *.pyc __pycache__/ 
scan_log.json EOL

# 5. Create README for folder structure
cat <<EOL > ~/CockerelShield/README.md
# 🛡️ Cocokerel Shield – Secure Dev Structure

📁 public/ – Safe code for Cursor (UI, API) 📁 private/ – Confidential 
AI model, startup R&D 📁 data/ – Local logs, never pushed

- Use VS Code for private folder - Use Cursor (AI off) for public code 
EOL

# 6. Create placeholder for R&D
echo "## Startup R&D Notes for Cocokerel Shield" >
~/CockerelShield/private/rnd_docs/RESEARCH.md

# 7. Print next steps
echo "✅ All folders ready!" echo "👉 Now run:" echo " cd 
~/CockerelShield" echo " source venv/bin/activate" echo " cd 
public/frontend" echo " # Build frontend here"
