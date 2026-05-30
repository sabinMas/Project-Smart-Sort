# Box Extension Deployment Guide

Complete guide for deploying the Smart Sort Box UI Extension to production.

## Prerequisites

- Node.js 16+ with npm
- Box Developer account with an application configured
- Access to Box API credentials (Client ID, Client Secret, Enterprise ID)
- Deployed backend at a public URL (not localhost)

## Development Setup

### 1. Install Dependencies

```bash
cd box-extension
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_BACKEND_URL=https://your-backend-domain.com
VITE_BOX_CLIENT_ID=your_box_client_id
VITE_BOX_ENTERPRISE_ID=your_enterprise_id
```

### 3. Local Development

Start the dev server:
```bash
npm run dev
```

The extension will be available at `http://localhost:5173`

## Building for Production

### 1. Build the Extension

```bash
npm run build
```

This creates an optimized build in the `dist/` directory:
- `box-extension.js` - Main UMD bundle
- `index.html` - Entry point
- `style.css` - Compiled styles
- Source maps for debugging

### 2. Verify the Build

```bash
npm run preview
```

This serves the production build locally on `http://localhost:4173`

### 3. Upload to CDN (Optional)

For better performance, upload the `dist/` folder to a CDN:
```bash
# Example with AWS S3
aws s3 sync dist/ s3://your-bucket/box-extension/ --acl public-read

# Or with Cloudflare Pages
wrangler pages publish dist/
```

## Registering with Box

### 1. Go to Box Developer Console

Visit: https://developer.box.com/console

### 2. Select Your Application

1. Click on your application
2. Go to **Configuration** in the left sidebar
3. Find the **UI Elements** section

### 3. Create a New UI Element

1. Click **Add UI Element**
2. Configure:
   - **Element Type**: Sidebar
   - **Location**: File Details (file_details)
   - **Label**: "Document Classification"
   - **Display Name**: "Document Classification"

### 4. Upload Extension Files

Option A: **Direct File Upload** (for development)
1. Click **Upload Files**
2. Select all files from the `dist/` directory
3. Click Upload

Option B: **URL-based** (for CDN deployment)
1. Choose **URL-based delivery**
2. Enter the URL to your hosted extension:
   ```
   https://your-cdn.com/box-extension/index.html
   ```
   Or for Render/other hosting:
   ```
   https://your-app.onrender.com/box-extension/
   ```

### 5. Configure Entry Point

1. **Entry Point**: Set to `index.html` or the full URL if using CDN
2. **Manifest**: The `manifest.json` file defines:
   - Permission scopes
   - Requested API access
   - OAuth configuration

### 6. Permissions & OAuth

The extension requests these permissions (defined in `manifest.json`):
- `manage:files` - Read file details
- `manage:metadata` - Update file metadata
- `manage:tasks` - Create and manage tasks

OAuth is configured with:
- **Client ID**: From your Box app
- **Callback URL**: Box handles this automatically for UI Elements

### 7. Save & Deploy

1. Click **Save**
2. Go to **Settings** → **General**
3. Ensure OAuth 2.0 is enabled
4. Note the **OAuth 2.0 Configuration**:
   - Client ID: `utwrdq9686ub16jbtvotq2adkqubh6z0`
   - Client Secret: (in your .env)
   - Redirect URI: (auto-configured by Box)

## Testing the Extension

### 1. Enable the Extension

1. In Box Developer Console, go to **Manage General Settings**
2. Ensure your app is **Authorized**
3. Your Box account is added as an **Authorized User**

### 2. Test in Box

1. Log in to Box.com with your enterprise account
2. Open any file in Box
3. In the file preview, look for the sidebar on the right
4. You should see "Document Classification" tab
5. Click it to load the extension

### 3. Troubleshooting

**Extension doesn't appear:**
- Check Box console for errors (F12 → Console)
- Verify the file ID is being passed correctly
- Check that your backend URL is accessible
- Verify CORS is enabled on your backend

**Extension loads but shows errors:**
- Check browser console for JavaScript errors
- Verify backend API endpoints are working
- Check network tab to see API calls
- Ensure authentication tokens are being passed

**Tasks don't create:**
- Verify the assignee email exists in your Box enterprise
- Check backend logs for errors
- Confirm Box API credentials are correct

## Production Deployment Options

### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd box-extension
vercel --prod
```

Update Box configuration to use the Vercel URL.

### Option 2: Render

1. Create account at render.com
2. Create new Static Site
3. Connect to your GitHub repo
4. Build command: `npm run build`
5. Publish directory: `box-extension/dist`
6. Deploy

Update Box configuration with the Render URL.

### Option 3: AWS S3 + CloudFront

```bash
# Build
npm run build

# Create S3 bucket
aws s3 mb s3://box-extension-prod

# Upload
aws s3 sync dist/ s3://box-extension-prod/ --delete

# Create CloudFront distribution
# Set origin to S3 bucket
# Set default root object to index.html
```

### Option 4: Self-hosted (Docker)

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
docker build -t box-extension .
docker run -p 80:80 box-extension
```

## Environment Variables for Deployment

### Development
```env
VITE_BACKEND_URL=http://localhost:8000
VITE_BOX_CLIENT_ID=utwrdq9686ub16jbtvotq2adkqubh6z0
VITE_ENVIRONMENT=development
```

### Production
```env
VITE_BACKEND_URL=https://api.yourdomain.com
VITE_BOX_CLIENT_ID=utwrdq9686ub16jbtvotq2adkqubh6z0
VITE_ENVIRONMENT=production
```

## Performance Optimization

### 1. Minification
The build automatically minifies CSS and JavaScript.

### 2. Code Splitting
Vite automatically splits code for better caching.

### 3. Asset Compression
Enable gzip compression on your server:

```nginx
# Nginx example
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss;
gzip_min_length 1000;
```

### 4. Caching Headers
Set long expiry for versioned assets:

```nginx
# Cache JavaScript files for 1 year (Vite handles versioning)
location ~* \.js$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

## Monitoring & Logs

### Browser Console
- Check for JavaScript errors
- Look for network request failures
- Monitor API response times

### Backend Logs
Check your backend API logs for:
- Failed classification requests
- Task creation errors
- Database issues

### Box API Logs
In Box Developer Console:
1. Go to **Logs**
2. Monitor API calls
3. Check rate limits

## Updating the Extension

### 1. Make Code Changes

Edit source files in `src/`

### 2. Rebuild

```bash
npm run build
```

### 3. Redeploy

- **For Vercel**: Auto-deploys on push to main
- **For S3**: Re-run `aws s3 sync dist/...`
- **For self-hosted**: Rebuild Docker image and redeploy
- **For Box (direct upload)**: Re-upload `dist/` folder

### 4. Clear Cache (if needed)

Force users to clear browser cache:
```bash
# In manifest.json, increment version
"version": "1.0.1"
```

## API Reference

### GET /documents/{file_id}

Returns classification data for a file.

**Response:**
```json
{
  "classification": {
    "document_id": "file_123",
    "doc_type": "invoice",
    "confidence": 0.95,
    "reasoning": "Document classified as invoice based on detected invoice fields",
    "extracted_fields": {
      "vendor": "Acme Corp",
      "amount": "$1,234.56",
      "invoice_date": "2024-01-15"
    },
    "required_reviewer": "finance",
    "metadata_tags": ["invoice", "vendor-acme"],
    "classified_at": "2024-01-20T10:30:00Z"
  },
  "processing_result": {
    "status": "success",
    "destination_folder": "Invoices/2024",
    "assigned_to": "john.doe@company.com"
  }
}
```

### POST /tasks/create

Creates a Box task for document review.

**Request:**
```json
{
  "file_id": "file_123",
  "assigned_to": "reviewer@company.com",
  "due_date": "2024-02-15",
  "message": "Please review this invoice"
}
```

**Response:**
```json
{
  "task_id": "task_456",
  "status": "success",
  "assigned_to": "reviewer@company.com"
}
```

## Support & Troubleshooting

### Common Issues

**Issue: CORS errors**
- Ensure backend has CORS enabled
- Check Access-Control-Allow-Origin headers
- Verify frontend and backend URLs

**Issue: File context not received**
- Extension may not be loading in Box UI Element context
- Check browser console for Box SDK errors
- Verify manifest.json is correct

**Issue: Backend unreachable**
- Check VITE_BACKEND_URL environment variable
- Verify backend is deployed and accessible
- Check firewall/network rules
- Verify HTTPS if using HTTPS frontend

**Issue: Tasks not creating**
- Verify assignee email exists in Box
- Check Box API token is valid
- Confirm backend has Box OAuth configured

## Next Steps

1. Deploy backend to production (if not already done)
2. Build and test extension locally
3. Register extension in Box Developer Console
4. Deploy extension to CDN or hosting provider
5. Configure Box extension with public URL
6. Test with actual Box users
7. Monitor logs and error rates
8. Gather feedback and iterate

---

For additional help, see:
- Main README.md
- Box API Documentation: https://developer.box.com/
- Vite Documentation: https://vitejs.dev/
