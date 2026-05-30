# Box Extension Deployment Checklist

Use this checklist to deploy the extension to production.

## Pre-Deployment (Today)

- [ ] **Environment Configuration**
  - [ ] `.env` file is configured with correct values
  - [ ] `VITE_BACKEND_URL` points to your backend (not localhost)
  - [ ] `VITE_BOX_CLIENT_ID` is set correctly
  - [ ] `.env` is in `.gitignore` (not committed to git)

- [ ] **Build Testing**
  - [ ] Run: `npm install`
  - [ ] Run: `npm run build`
  - [ ] No build errors
  - [ ] `dist/` folder created with: `box-extension.js`, `style.css`, `index.html`
  - [ ] Bundle size is reasonable (479 KB JS + 7 KB CSS)

- [ ] **Code Review**
  - [ ] Review `src/App.tsx` - uses `getBoxContext()` ✅
  - [ ] Review `src/utils/boxSDK.ts` - Box API integration ✅
  - [ ] Check `vite.config.ts` - build config correct ✅
  - [ ] Check `manifest.json` - Box extension metadata ✅

- [ ] **Local Testing**
  - [ ] Backend running: `curl http://localhost:8000/health`
  - [ ] Backend has test data available
  - [ ] Test in browser: `npm run dev` at `http://localhost:5173`
  - [ ] Can connect to backend
  - [ ] Classification data displays correctly

## Deployment (Choose One)

### Option A: Vercel (Recommended - Easiest)

- [ ] **Install Vercel CLI**
  ```bash
  npm install -g vercel
  ```

- [ ] **Deploy**
  ```bash
  cd box-extension
  vercel --prod
  ```

- [ ] **Note the URL**
  - You'll see something like: `https://box-extension-xxx.vercel.app`
  - Save this URL - you'll need it for Box config

- [ ] **Verification**
  - [ ] Deployment succeeds
  - [ ] No build errors in Vercel dashboard
  - [ ] URL is accessible in browser
  - [ ] `https://your-url/index.html` loads

### Option B: AWS S3 + CloudFront

- [ ] **Create S3 Bucket**
  ```bash
  aws s3 mb s3://box-extension-prod-$(date +%s)
  ```

- [ ] **Upload Files**
  ```bash
  npm run build
  aws s3 sync dist/ s3://your-bucket-name/ --delete --acl public-read
  ```

- [ ] **Create CloudFront Distribution**
  - [ ] Set origin to S3 bucket
  - [ ] Default root object: `index.html`
  - [ ] Note the CloudFront URL

- [ ] **Verification**
  - [ ] S3 bucket contains files
  - [ ] CloudFront distribution is active
  - [ ] URL is accessible

### Option C: Render.com (Simple)

- [ ] **Create Render Account**
  - [ ] Sign up at render.com

- [ ] **Connect GitHub Repo**
  - [ ] Click "New" → "Static Site"
  - [ ] Select your GitHub repo
  - [ ] Authorize GitHub access

- [ ] **Configure Build**
  - [ ] Build Command: `npm run build`
  - [ ] Publish Directory: `box-extension/dist`

- [ ] **Deploy**
  - [ ] Click "Create Static Site"
  - [ ] Wait for deployment
  - [ ] Note the URL (something like `https://your-app.onrender.com`)

- [ ] **Verification**
  - [ ] Build succeeds
  - [ ] URL is accessible
  - [ ] `https://your-url/index.html` loads

### Option D: Docker (Self-hosted)

- [ ] **Build Docker Image**
  ```bash
  cd box-extension
  docker build -t box-extension:latest .
  ```

- [ ] **Run Container**
  ```bash
  docker run -d -p 80:80 box-extension:latest
  ```

- [ ] **Verify**
  - [ ] Container running: `docker ps`
  - [ ] Accessible at `http://localhost`

- [ ] **Deploy to Your Server**
  - [ ] Push image to registry (ECR, Docker Hub, etc.)
  - [ ] Deploy to your infrastructure
  - [ ] Note the public URL

## Box Developer Console Configuration

- [ ] **Go to Box Developer Console**
  - [ ] URL: https://developer.box.com/console
  - [ ] Select your application

- [ ] **Navigate to UI Elements**
  - [ ] Left menu → Configuration → UI Elements
  - [ ] Look for existing "Document Classification" element

- [ ] **Create or Update UI Element**
  - [ ] Click "Add UI Element" (or edit existing)
  - [ ] **Element Type**: Sidebar
  - [ ] **Location**: File Details (file_details)
  - [ ] **Label**: Document Classification
  - [ ] **Display Name**: Document Classification

- [ ] **Set Entry Point**
  - [ ] **Method 1: Direct Upload** (for testing)
    - [ ] Click "Upload Files"
    - [ ] Select all files from `dist/` folder
    - [ ] Set Entry Point to: `index.html`
  
  - [ ] **Method 2: URL-based** (for production)
    - [ ] Click "URL-based delivery"
    - [ ] Enter your deployed URL: `https://your-domain.com/box-extension/index.html`

- [ ] **Configure Permissions**
  - [ ] Check these permissions are requested:
    - [ ] `manage:files` (read file details)
    - [ ] `manage:metadata` (update file metadata)
    - [ ] `manage:tasks` (create tasks)
  - [ ] Check requested scopes in `manifest.json`:
    - [ ] `item_upload`, `item_download`, `item_preview`
    - [ ] `task_view`, `task_create`, `task_update`

- [ ] **Save Configuration**
  - [ ] Click "Save"
  - [ ] Verify no errors

## Post-Deployment Testing

- [ ] **Test in Box.com**
  - [ ] Log in to Box.com (your enterprise account)
  - [ ] Open any file in your folder
  - [ ] Look for "Document Classification" in right sidebar
  - [ ] Extension should load

- [ ] **Test Classification Display**
  - [ ] Should see document classification results
  - [ ] Should show confidence score
  - [ ] Should show extracted fields
  - [ ] Should show metadata tags

- [ ] **Test Task Creation**
  - [ ] Look for "Assign Review Task" section
  - [ ] Enter a valid email address
  - [ ] Click "Assign Task"
  - [ ] Should see success message
  - [ ] Task should appear in Box

- [ ] **Check Browser Console**
  - [ ] Open DevTools: `F12`
  - [ ] Go to "Console" tab
  - [ ] Should have no red errors
  - [ ] Check for API responses

- [ ] **Check Backend Logs**
  - [ ] Look at backend logs
  - [ ] Should see API requests from frontend
  - [ ] No 5xx errors

## Troubleshooting During Deployment

| Problem | Solution |
|---------|----------|
| Build fails with errors | See TypeScript errors, fix, rebuild |
| Extension doesn't appear | Check Box console logs, verify entry point URL |
| Extension loads but shows blank | Check browser console for JS errors, verify backend URL |
| "Failed to connect to backend" | Verify VITE_BACKEND_URL is correct and backend is running |
| Backend returns 404 | Verify file ID exists and backend endpoint is correct |
| Tasks don't create | Check assignee email is valid in Box, check backend logs |

## Performance Verification

- [ ] **Load Time**
  - [ ] Extension loads in < 2 seconds (with good connection)
  - [ ] Network tab shows reasonable request sizes

- [ ] **Bundle Size**
  - [ ] Main JS: ~480 KB (gzip: ~148 KB)
  - [ ] CSS: ~7 KB (gzip: ~2 KB)

- [ ] **API Responses**
  - [ ] GET /documents/{file_id} < 500ms
  - [ ] POST /tasks/create < 2 seconds

## Post-Deployment Checklist

- [ ] **Monitor Logs**
  - [ ] Set up log monitoring on backend
  - [ ] Set up error tracking (Sentry, Rollbar, etc.)
  - [ ] Monitor Box API rate limits

- [ ] **Update Documentation**
  - [ ] Update README with production URL
  - [ ] Document any changes for team
  - [ ] Share deployment guide with team

- [ ] **Set Up Monitoring**
  - [ ] Monitor API response times
  - [ ] Monitor error rates
  - [ ] Monitor user feedback
  - [ ] Check Box Developer Console logs regularly

- [ ] **Create Backup Plan**
  - [ ] Have rollback procedure documented
  - [ ] Know how to revert Box extension
  - [ ] Keep previous dist/ folder backed up

## Version Updates (Future)

When updating the extension:

1. Make code changes in `src/`
2. Bump version in `package.json`
3. Bump version in `manifest.json`
4. Run `npm run build`
5. Re-upload to Box or redeploy to CDN
6. Clear browser cache if needed
7. Test in Box.com
8. Monitor logs for errors

## Success Criteria

✅ **Deployment is successful when:**

- [ ] Extension loads in Box.com
- [ ] Displays classification results for files
- [ ] Can create tasks for review
- [ ] No console errors
- [ ] Backend API is being called correctly
- [ ] Users can interact with the extension
- [ ] No security warnings
- [ ] Performance is acceptable (< 2s load time)

---

**You're ready to deploy!** 🚀

Next step: Choose a deployment option above and follow the steps.

For detailed help, see **BOX_DEPLOYMENT.md**
