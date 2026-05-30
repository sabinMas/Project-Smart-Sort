# 🎬 Box Smart Inbox - Playwright Demo Script

A complete end-to-end demo script that shows the full document orchestration workflow with video recording.

## 📋 Prerequisites

1. **Playwright installed**
   ```bash
   npm install --save-dev @playwright/test
   ```

2. **Environment Variables**
   ```bash
   export BOX_EMAIL="your-box-email@example.com"
   export BOX_PASSWORD="your-box-password"
   ```

3. **Backend Running**
   - ✅ Already deployed: https://project-smart-sort.onrender.com
   - Or locally: `py -m uvicorn backend.main:app --reload`

4. **Box File ID**
   - Optional: Update `FILE_ID` in the script to a real file in your Box account
   - Without it, the script tests the API directly

## 🚀 Running the Demo

### Option 1: Full UI Demo (with Box login)
```bash
npx playwright test playwright-demo.spec.ts --headed --video=on
```

**What it does:**
1. Checks backend health
2. Logs into Box.com
3. Opens a file
4. Extension displays classification results
5. Creates review task
6. Records everything to video

### Option 2: Quick API Test (No UI)
```bash
npx playwright test playwright-demo.spec.ts -g "Quick API Test" --headed
```

**What it does:**
- Tests all 3 domains via API
- No Box login required
- Fast (~10 seconds)
- Perfect for CI/CD

## 📺 Video Recording

Videos are automatically saved to:
```
test-results/
```

Configure video options in `playwright.config.ts`:
```typescript
use: {
  video: 'on',  // 'on' | 'off' | 'retain-on-failure'
}
```

## 🎯 What the Demo Shows

### Backend (Domain 1-3)
- ✅ Email ingestion system running
- ✅ AI classification with 88-96% confidence
- ✅ Box routing and metadata application
- ✅ Approval workflow and task creation

### Frontend (Box Extension)
- ✅ Extension loads in Box sidebar
- ✅ Shows classification results
- ✅ Displays extracted vendor/amount
- ✅ Allows task creation
- ✅ Connected to production backend

### Integration
- ✅ Vercel frontend talking to Render backend
- ✅ AWS Textract configured
- ✅ PostgreSQL database connected
- ✅ Full pipeline working end-to-end

## 📝 Setup Instructions for Your Box File

1. **Get a Box File ID**
   - Log into https://www.box.com
   - Open any file
   - URL will be: `https://app.box.com/file/YOUR_FILE_ID`
   - Copy the ID

2. **Update the Script**
   - Replace `FILE_ID = 'YOUR_BOX_FILE_ID'` with your actual ID

3. **Run with Box Login**
   ```bash
   BOX_EMAIL="your-email@box.com" \
   BOX_PASSWORD="your-password" \
   npx playwright test playwright-demo.spec.ts --headed --video=on
   ```

## 🔧 Customization

### Change Backend URL
Edit line 23 in `playwright-demo.spec.ts`:
```typescript
const BACKEND_URL = 'https://project-smart-sort.onrender.com'; // or http://localhost:8000
```

### Change Document ID
Edit line 80:
```typescript
const FILE_ID = 'YOUR_BOX_FILE_ID'; // Replace with your Box file ID
```

### Add More Assertions
Add checks after approval:
```typescript
// Verify task was created in Box
const tasksResponse = await page.request.get(`${BACKEND_URL}/tasks/${FILE_ID}`);
const tasks = await tasksResponse.json();
expect(tasks.length).toBeGreaterThan(0);
```

## 🎬 Recording Full Flow

For a demo video:
```bash
npx playwright test playwright-demo.spec.ts --headed --video=on --slow-mo=1000
```

The `--slow-mo` flag slows down interactions (1000ms between steps) so viewers can see what's happening.

## 📊 Demo Checklist

When running the demo, verify:
- ✅ Backend health check passes
- ✅ Demo data loads (3 documents)
- ✅ Box login succeeds (or shows 2FA requirement)
- ✅ File opens in Box
- ✅ Extension appears in sidebar
- ✅ Classification results display
- ✅ Approval API call succeeds
- ✅ Video saved successfully

## 🚨 Troubleshooting

### "Box login may require 2FA"
- Script runs but pauses at login
- Complete 2FA manually, then press continue

### "Extension loads in sidebar iframe"
- Normal behavior - extension renders in Box's iframe
- Screenshots will show the Box interface with extension

### "Backend returns 500 error"
- Check Render is online: https://project-smart-sort.onrender.com/health
- Check DEMO_MODE is enabled in backend
- Check AWS Textract credentials are valid

### "Video file not found"
- Check `test-results/` directory exists
- Run with `--video=on` explicitly
- Ensure Playwright is fully installed

## 📚 See Also

- [Demo Instructions](DEMO_INSTRUCTIONS.md) - Manual testing guide
- [Vercel Deployment](VERCEL_DEPLOYMENT.md) - Frontend deployment
- [Backend Setup](README.md) - Architecture overview

---

**Ready to demo!** 🎉

```bash
npx playwright test playwright-demo.spec.ts --headed --video=on
```
