# Box Extension Quick Start

Get up and running in 5 minutes!

## 1. Prerequisite Check

- ✅ Backend is running at https://your-backend.com (or localhost:8000 for dev)
- ✅ Node.js 16+ installed
- ✅ Box Developer account with app created

## 2. Setup (One time)

```bash
cd box-extension

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your values
# - VITE_BACKEND_URL=your backend URL
# - VITE_BOX_CLIENT_ID=your Box Client ID
```

## 3. Development Mode

Start local dev server:
```bash
npm run dev
```

Visit: `http://localhost:5173`

## 4. Build for Production

```bash
npm run build
```

Output is in `dist/` directory.

## 5. Deploy to Box

### Option A: Direct Upload to Box
1. Go to Box Developer Console → Your App → Configuration
2. UI Elements → Create New
3. Type: Sidebar, Location: File Details
4. Upload the `dist/` folder

### Option B: Host on Server
1. Deploy `dist/` folder to your hosting (Vercel, AWS, etc.)
2. In Box configuration, set Entry Point to the URL:
   ```
   https://your-domain.com/box-extension/index.html
   ```

## File Structure

```
box-extension/
├── src/
│   ├── App.tsx                    # Main component
│   ├── utils/boxSDK.ts           # Box API utilities
│   ├── components/               # UI components
│   └── styles/                   # CSS files
├── dist/                         # Build output
├── vite.config.ts               # Vite configuration
├── tsconfig.json                # TypeScript config
├── .env                         # Environment variables
├── package.json                 # Dependencies
├── manifest.json                # Box extension config
└── BOX_DEPLOYMENT.md            # Full deployment guide
```

## Environment Variables

```env
# Backend URL (dev: http://localhost:8000, prod: https://api.example.com)
VITE_BACKEND_URL=http://localhost:8000

# Box OAuth Client ID
VITE_BOX_CLIENT_ID=your_client_id

# Box Enterprise ID
VITE_BOX_ENTERPRISE_ID=your_enterprise_id

# Environment
VITE_ENVIRONMENT=development
```

## Testing Locally

1. **Start backend** (in separate terminal):
   ```bash
   cd backend
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start frontend** (in box-extension directory):
   ```bash
   npm run dev
   ```

3. **Test in Box** (real Box account):
   - Log in to Box.com
   - Open a file
   - Look for "Document Classification" sidebar
   - Or use mock data from localStorage

## Troubleshooting

### Extension doesn't load?
- Check browser console: `F12` → `Console` tab
- Verify backend URL in `.env` is correct
- Confirm backend is running: `curl http://localhost:8000/health`

### Backend API errors?
- Check backend logs
- Verify File ID is being passed to API
- Test API directly: 
  ```bash
  curl http://localhost:8000/documents/file_123
  ```

### Build errors?
- Delete `node_modules/` and `dist/`:
  ```bash
  rm -rf node_modules dist
  npm install
  npm run build
  ```

## API Endpoints

The extension calls these backend endpoints:

- `GET /documents/{file_id}` - Get classification
- `POST /tasks/create` - Create review task
- `GET /health` - Health check

See [BOX_DEPLOYMENT.md](./BOX_DEPLOYMENT.md) for full API docs.

## Next Steps

1. Read [BOX_DEPLOYMENT.md](./BOX_DEPLOYMENT.md) for full deployment guide
2. Read [README.md](./README.md) for architecture details
3. Check backend API docs at `http://localhost:8000/docs`

---

**Need help?** Check BOX_DEPLOYMENT.md Troubleshooting section or the main project README.
