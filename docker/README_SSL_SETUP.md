# SSL Setup for Calibre Desktop

## Quick Start

Calibre Desktop requires HTTPS for its VNC interface to work. Follow these steps:

### 1. Generate SSL Certificates

```bash
cd docker/nginx
bash generate_ssl.sh
```

This creates self-signed SSL certificates valid for 365 days.

### 2. Start the Services

```bash
cd docker
docker compose up -d
```

### 3. Access Calibre Desktop

**URL:** https://YOUR_IP:3443

**Credentials:**
- Username: `abc` (fixed, cannot be changed)
- Password: Your `CALIBRE_PASSWORD` from `.env`

### 4. Accept the Certificate Warning

Your browser will show a security warning because we're using self-signed certificates:

1. Click "Advanced" (or "Show Details")
2. Click "Accept the Risk and Continue" (or "Proceed to localhost")

That's it! You should now see the Calibre Desktop VNC interface.

---

## Technical Details

### Why HTTPS is Required

Calibre Desktop uses [Selkies](https://github.com/selkies-project/selkies-gstreamer) for WebRTC-based VNC access. WebRTC requires secure connections (HTTPS) to function.

### Architecture

```
Browser → Nginx (port 3443/HTTPS) → Calibre (port 8080/HTTP)
```

Nginx terminates SSL and proxies to Calibre's HTTP interface.

### Certificate Details

- **Type:** Self-signed X.509 certificate
- **Key Size:** RSA 2048-bit
- **Validity:** 365 days
- **Location:** `docker/nginx/ssl/`
  - `calibre.crt` - Certificate
  - `calibre.key` - Private key

### Using Production Certificates

For production deployments, replace the self-signed certificates with proper certificates from Let's Encrypt or your certificate authority:

```bash
# Replace with your production certificates
cp /path/to/your/cert.crt docker/nginx/ssl/calibre.crt
cp /path/to/your/cert.key docker/nginx/ssl/calibre.key

# Restart Nginx
docker restart edu-nginx
```

### Nginx Configuration

The SSL proxy is configured in `docker/nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/calibre.crt;
    ssl_certificate_key /etc/nginx/ssl/calibre.key;

    location / {
        proxy_pass http://calibre:8080;
        # WebSocket support for VNC
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Troubleshooting

### SSL Certificate Errors

If you see certificate-related errors in Nginx logs:

```bash
# Check certificates exist
ls -la docker/nginx/ssl/

# Verify certificate
openssl x509 -in docker/nginx/ssl/calibre.crt -text -noout

# Regenerate if needed
cd docker/nginx
bash generate_ssl.sh
docker restart edu-nginx
```

### Connection Refused

```bash
# Check Calibre is running
docker ps --filter "name=edu-calibre"

# Check Nginx can reach Calibre
docker exec edu-nginx wget -O- http://calibre:8080 2>&1 | head
```

### Port 3443 Already in Use

Change `NGINX_HTTPS_PORT` in `.env`:

```bash
# In docker/.env
NGINX_HTTPS_PORT=4443  # or any other port
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

---

## Security Notes

1. **Self-Signed Certificates:** These are fine for local/testing deployments but browsers will show warnings.

2. **Production Use:** For production, use proper certificates from Let's Encrypt (free) or a commercial CA.

3. **Calibre Password:** Change the default password in `.env`:
   ```bash
   CALIBRE_PASSWORD=your_strong_password_here
   ```

4. **Username Cannot Be Changed:** The username `abc` is hardcoded by LinuxServer's Calibre container.

---

## Additional Resources

- [LinuxServer Calibre Documentation](https://docs.linuxserver.io/images/docker-calibre)
- [Selkies WebRTC VNC](https://github.com/selkies-project/selkies-gstreamer)
- [Let's Encrypt](https://letsencrypt.org/) - Free SSL certificates
