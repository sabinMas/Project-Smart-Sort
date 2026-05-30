# 🎬 Live Demo Quick Start - Extension Already Registered

**Status:** Extension is already in Box Developer Console ✅  
**No registration needed!**

---

## 🚀 What You Need to Demo

### **Pre-Demo (5 minutes)**

#### 1. Verify Backend is Live
```bash
curl https://project-smart-sort.onrender.com/health | jq
```
✅ Should respond with `{"status": "ok"}`

#### 2. Log into Box
- Go to https://www.box.com
- Use your personal Box account
- The extension is already registered and ready

#### 3. Prepare Test PDFs
Have ready:
- `test_invoice_tech.pdf` (ACME Corp, $15,500)
- `test_contract_vendor.pdf`
- `test_receipt_supplies.pdf`

---

## 📧 Demo Flow (5-7 minutes)

### **Step 1: Show Backend Health (30 seconds)**
```bash
curl https://project-smart-sort.onrender.com/health | jq
```
Display the response showing the service is alive.

### **Step 2: Team Member Sends Email (1 minute)**
Team Member #1 sends:
```
TO: [your-box-email]@company.com
SUBJECT: Invoice from ACME Corporation  
ATTACHMENT: test_invoice_tech.pdf
BODY: Please classify and route this document
```

**Critical:** Must send to YOUR Box email address (not a shared one)

### **Step 3: Watch It Process (30 seconds)**
Document goes through:
1. ✅ Email arrives at SendGrid
2. ✅ Backend receives it
3. ✅ Textract extracts text
4. ✅ Cerebras classifies it
5. ✅ Sent to Box automatically
6. ✅ Task created

### **Step 4: Open in Box & Show Extension (1 minute)**
1. Log into Box.com
2. Navigate to `/Invoices` folder (or where it was organized)
3. Open the document
4. **Look at the right sidebar** - "Document Classification" extension shows:
   - Type: INVOICE
   - Confidence: 96%
   - Vendor: ACME Corporation
   - Amount: $15,500.00

### **Step 5: Show Slack Notification (30 seconds)**
- Pull up Slack channel
- Show notification that fired automatically
- Show workflow message

### **Step 6: Show Task Created (1 minute)**
- Go to Box Tasks section
- Show "Review Invoice from ACME" task
- Show it's assigned to finance team with deadline

**Total: 5-7 minutes perfectly timed!**

---

## 🔐 Key Configuration Already Done

✅ **Extension:** Registered in Box Developer Console  
✅ **Backend:** Running on Render (https://project-smart-sort.onrender.com)  
✅ **Frontend:** Deployed on Vercel (https://box-extension.vercel.app)  
✅ **Box OAuth:** Configured  
✅ **AWS Textract:** Credentials configured (1000 credits)  
✅ **Slack:** Webhook ready  

**Everything is live and connected!**

---

## 🎯 What Happens Behind the Scenes

```
Email arrives
    ↓
SendGrid webhook catches it
    ↓
Backend processes attachment:
  • Textract extracts PDF text
  • Cerebras classifies document
  • Determines it's an INVOICE
    ↓
Box Integration:
  • Organizes to /Invoices folder
  • Creates review task
  • Applies metadata tags
    ↓
Slack Notification:
  • Notifies finance team
  • Shows classification results
    ↓
Box Extension:
  • Displays results in sidebar
  • Shows vendor and amount
  • Allows approve/reject
```

---

## 🔌 Email Webhook Setup

**Current configuration in `.env`:**
```
SENDGRID_INBOUND_URL=https://thrower-unholy-emotion.ngrok-free.dev/webhooks/email
```

**This means:**
- SendGrid is configured to forward emails to your backend
- When someone sends to your Box email, it triggers the pipeline
- Backend processes it automatically

**If ngrok tunnel expires:**
- Use Render backend URL instead
- Or restart ngrok: `ngrok http 8000`

---

## 📋 Demo Checklist

Before showing judges:

- [ ] Backend health check works
- [ ] Logged into Box.com
- [ ] Test PDFs ready to send
- [ ] Extension appears in Box sidebar (try opening any file)
- [ ] Slack channel open and ready
- [ ] Team members know to send emails on your signal
- [ ] Have backup: `npx playwright test playwright-demo.spec.ts --headed --video=on`

---

## 🎯 Most Important Part

**The extension is already registered in Box.** 

When you open ANY file in Box, you should see "Document Classification" in the right sidebar. This is your extension loaded from Vercel, talking to your backend on Render.

To verify it's working:
1. Go to Box.com
2. Open any file
3. Look at right sidebar
4. You should see the extension loading

**If you don't see it:**
- Hard refresh Box (Cmd+Shift+R or Ctrl+Shift+R)
- Check browser console for errors (F12)
- Verify `box-extension/.env` has correct backend URL

---

## 🚀 You're Ready!

No setup needed. Just:
1. Have test PDFs ready
2. Tell team members when to send
3. Show judges Box opening with extension
4. Done! 🎉

Everything else is already running in production.

---

## 📚 See Also

- `DEMO_DAY_READY.md` - Complete system overview
- `TEAM_TASKS.md` - Team member instructions
- `CODEBASE_REVIEW.md` - Technical details

**Questions?** Check the guides above!
