# 📧 Email Integration with Resend

I have set up email sending functionality using Resend!

## ✅ **What I Did:**

1. **Installed dependencies:** `pip install resend`
2. **Created Service:** `backend/app/services/email_service.py`
3. **Created Endpoint:** `POST /api/v1/email/send-test`
4. **Created Test Script:** `test_email_resend.py`

---

## 🚀 **How to Enable It:**

### **Step 1: Get Your API Key**
1. Go to **[Resend.com](https://resend.com)** and sign up/login.
2. Click **"Add API Key"**.
3. Name it "Posan App".
4. Copy the key (starts with `re_...`).

### **Step 2: Add to Environment**
1. Open `backend/.env` file.
2. Add this line:
   ```bash
   RESEND_API_KEY=re_123456789yourkeyhere
   ```
   *(Replace with your actual key)*

---

## 🧪 **How to Test:**

### **Option 1: Run the Script**
I created a script with your exact code snippet:
```bash
python test_email_resend.py
```

### **Option 2: Use the API**
You can trigger an email via the new API endpoint:
```http
POST http://localhost:8000/api/v1/email/send-test
Content-Type: application/json

{
  "to_email": "grvivek17@gmail.com",
  "subject": "Testing Posan Email"
}
```

### **Option 3: Use in Code**
You can now send emails from anywhere in your backend:

```python
from app.services.email_service import email_service

# Send simple email
email_service.send_email(
    to_email="user@example.com",
    subject="Hello",
    html_content="<p>My message</p>"
)
```

---

## 📋 **Verification Checklist:**

- [ ] `resend` installed? ✅
- [ ] API Key in `.env`? ⏳ **(Waiting for you!)**
- [ ] Email endpoint active? ✅

Once you add the key, standard emails will work immediately!
