#!/bin/bash
################################################################################
# SSL Certificate Generation Script for GLEH
################################################################################
# Generates self-signed SSL certificates for Calibre Desktop HTTPS access
#
# Usage:
#   ./generate_ssl.sh
#
# Output:
#   ./ssl/calibre.crt  - SSL certificate
#   ./ssl/calibre.key  - Private key
################################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "SSL Certificate Generator for GLEH Calibre Desktop"
echo "========================================================================"
echo

# Create SSL directory if it doesn't exist
SSL_DIR="$(dirname "$0")/ssl"
mkdir -p "$SSL_DIR"

echo -e "${YELLOW}→${NC} Creating SSL directory: $SSL_DIR"

# Generate self-signed certificate
echo -e "${YELLOW}→${NC} Generating self-signed SSL certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$SSL_DIR/calibre.key" \
  -out "$SSL_DIR/calibre.crt" \
  -subj "/C=US/ST=State/L=City/O=GLEH/OU=Education/CN=calibre.local" \
  2>/dev/null

# Set proper permissions
chmod 644 "$SSL_DIR/calibre.crt"
chmod 600 "$SSL_DIR/calibre.key"

echo -e "${GREEN}✓${NC} SSL certificate generated successfully!"
echo
echo "Certificate details:"
echo "  Certificate: $SSL_DIR/calibre.crt"
echo "  Private Key: $SSL_DIR/calibre.key"
echo "  Valid for: 365 days"
echo
echo -e "${YELLOW}⚠${NC}  NOTE: This is a self-signed certificate."
echo "  Your browser will show a security warning."
echo "  Click 'Advanced' and 'Accept the Risk' to proceed."
echo
echo "Next steps:"
echo "  1. Go back to docker/ directory: cd .."
echo "  2. Start Docker services: docker compose up -d"
echo "  3. Access Calibre Desktop at: https://YOUR_IP:3443"
echo "  4. Username: abc"
echo "  5. Password: (from CALIBRE_PASSWORD in .env)"
echo
echo "========================================================================"
