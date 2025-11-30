# Samba Share Configuration for GLEH

## Overview

GLEH is configured to use your Samba share at `\10.0.10.61\gleh-data` for storing courses and ebooks. This allows courses and ebooks to be managed centrally on a network server while GLEH accesses them seamlessly.

## Configuration

### Environment Variables (.env)

The `.env` file contains your Samba credentials. **Never commit this file to git.** It's automatically ignored.

```
SAMBA_HOST=10.0.10.61
SAMBA_SHARE=gleh-data
SAMBA_USERNAME=allie
SAMBA_PASSWORD=<your-password-here>
SAMBA_MOUNT_PATH=/mnt/gleh-data
CONTENT_DIR=\10.0.10.61\gleh-data
```

### Local Development (Windows)

**For Flask (development server):**

```bash
cd C:\Users\nissa\Desktop\AI Projects\GLEH
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask run
```

The app will automatically access courses and ebooks from `\10.0.10.61\gleh-data`.

### Docker Deployment

For Docker to access the Samba share on Windows:

**Option 1: Map Samba as Network Drive (Easiest)**
1. Open File Explorer
2. Right-click "This PC" → "Map network drive"
3. Folder: `\10.0.10.61\gleh-data`
4. Username: `allie`
5. Password: `<your-samba-password>`
6. Assign drive letter (e.g., `Z:`)
7. Update `.env`: `CONTENT_DIR=Z:/gleh-data` or `CONTENT_DIR=//10.0.10.61/gleh-data`

**Option 2: Docker-Compose (Linux/Mac)**

For Linux/Mac systems, mount Samba before running Docker:

```bash
sudo mkdir -p /mnt/gleh-data
sudo mount -t cifs -o username=allie,password=$SAMBA_PASSWORD \10.0.10.61\gleh-data /mnt/gleh-data
docker-compose up
```

## Share Contents

The Samba share should contain:

```
gleh-data/
├── courses/          ← Course materials and content
│   ├── course1/
│   ├── course2/
│   └── ...
└── epub/             ← E-book files (EPUB, PDF, etc.)
    ├── book1.epub
    ├── book2.pdf
    └── ...
```

## Troubleshooting

### Share Not Accessible

1. Verify the Samba server is running: `ping 10.0.10.61`
2. Check credentials with: `net use \10.0.10.61\gleh-data /user:allie <your-password>`
3. Verify share permissions for user `allie`

### Flask Can't Find Content

1. Check `.env` file exists and `CONTENT_DIR` is correct
2. Verify the share is mounted/accessible
3. Check app logs: `docker-compose logs -f web`

### Docker Permission Issues

1. Ensure Docker has read/write permissions to the mount
2. On Linux, adjust mount options: `-o username=allie,password=$SAMBA_PASSWORD,uid=1000,gid=1000`

## Security Notes

- `.env` file is ignored by git (contains passwords)
- Never commit `.env` to version control
- For production, use environment variables instead of `.env` file
- Samba should be on a secure network (local LAN only)
- Consider using VPN for remote access

## Next Steps

1. Update `.env` with your Samba credentials (already done)
2. Test Flask locally: `flask run`
3. Verify Flask can see courses and ebooks
4. Run Docker: `docker-compose up`
5. Test Docker version at `http://localhost`

