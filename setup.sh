#!/bin/bash
# ==========================================================
# Lottery Guide — One-command setup
# ==========================================================
set -e

echo ""
echo "🎰  Lottery Guide Setup"
echo "==========================================="

# Create virtual environment
if [ ! -d "venv" ]; then
  echo "→ Creating virtual environment..."
  python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "→ Installing dependencies..."
pip install -q -r requirements.txt

# Migrate database
echo "→ Setting up database..."
python manage.py migrate --run-syncdb

# Seed formula configs (triggered by post_migrate signal)
echo "→ Seeding 75 formula configurations..."
python manage.py migrate  # triggers the post_migrate signal again

# Create superuser (optional)
echo ""
echo "  Create an admin account? (y/n)"
read -r CREATE_ADMIN
if [[ "$CREATE_ADMIN" == "y" ]]; then
  python manage.py createsuperuser
fi

echo ""
echo "==========================================="
echo "✅  Setup complete!"
echo ""
echo "  Start the server:"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "  Then open: http://127.0.0.1:8000"
echo "  Admin:     http://127.0.0.1:8000/admin"
echo "==========================================="
