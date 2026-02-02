# Promotional Email Feature

This document describes the promotional email feature implementation for sending weekly new arrivals emails to users.

## Overview

The promotional email feature allows admins to:
- View new magazines and products from the last N days
- Preview beautifully designed HTML emails
- Send promotional emails to selected users or all users
- Create custom promotional emails

## Setup Instructions

### 1. Gmail SMTP Configuration

To send emails via Gmail SMTP, you need to generate an **App Password**:

#### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click on "2-Step Verification"
3. Follow the prompts to enable 2FA

#### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" as the app and "Windows Computer" (or other) as the device
3. Click "Generate"
4. Copy the 16-character password shown

#### Step 3: Update Environment Variables
Update your `backend/.env` file with the following:

```env
# SMTP Configuration for Promotional Emails (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=rvposhika26@gmail.com
SMTP_PASSWORD=YOUR_16_CHAR_APP_PASSWORD
SMTP_FROM_NAME=POSAN Kids Magazine
```

**Important:** Replace `YOUR_16_CHAR_APP_PASSWORD` with the App Password generated in Step 2 (without spaces).

### 2. Testing the Configuration

1. Start the backend server
2. Log in as an admin user
3. Go to Admin Dashboard → Promotional Email
4. Click "Send Test Email" to verify the setup works

## API Endpoints

All endpoints require admin authentication.

### GET `/api/v1/admin/promotional-email/smtp-status`
Check SMTP configuration status.

### GET `/api/v1/admin/promotional-email/new-arrivals?days=7`
Get new magazines and products from the last N days.

### GET `/api/v1/admin/promotional-email/subscribers`
Get all user emails for promotional campaigns.

### POST `/api/v1/admin/promotional-email/preview-weekly-arrivals?days=7`
Generate and preview the weekly arrivals email HTML.

### POST `/api/v1/admin/promotional-email/send-weekly-arrivals`
Send weekly arrivals email to selected recipients.

Request body:
```json
{
  "recipient_emails": ["user1@example.com", "user2@example.com"],
  "recipient_name": "Dear Reader",
  "days_back": 7
}
```

### POST `/api/v1/admin/promotional-email/send-custom`
Send a custom promotional email.

Request body:
```json
{
  "recipient_emails": ["user@example.com"],
  "subject": "Special Offer!",
  "heading": "🎉 Exciting News!",
  "content": "<p>Your HTML content here...</p>",
  "cta_text": "Shop Now",
  "cta_url": "https://yoursite.com/store"
}
```

### POST `/api/v1/admin/promotional-email/send-to-all-users`
Send promotional email to ALL registered users. **Use with caution!**

Request body:
```json
{
  "subject": "This Week's New Arrivals!",
  "include_new_magazines": true,
  "include_new_products": true,
  "days_back": 7,
  "custom_message": "Optional extra message"
}
```

### POST `/api/v1/admin/promotional-email/send-test?to_email=test@example.com`
Send a test email to verify SMTP configuration.

## Frontend Page

Navigate to `/admin/promotional-email` to access the admin promotional email page.

### Features:
- **SMTP Status Card**: Shows if SMTP is configured correctly
- **Weekly Arrivals Tab**: View and send weekly new arrivals emails
- **Custom Email Tab**: Compose and send custom promotional emails
- **Recipient Selection**: Select individual users or all users
- **Email Preview**: Preview the email before sending

## Email Template

The emails use a beautiful, responsive HTML template with:
- Gradient header with POSAN branding
- Magazine cards with cover images and details
- Product cards with pricing and discounts
- Call-to-action buttons
- Mobile-responsive design

## Troubleshooting

### "SMTP Authentication Error"
- Ensure you're using an App Password, not your regular Gmail password
- Verify 2FA is enabled on your Google account
- Check that the email address is correct

### "SMTP not configured"
- Verify `SMTP_USER` and `SMTP_PASSWORD` are set in `.env`
- Restart the backend server after changing environment variables

### Emails not received
- Check spam/junk folder
- Verify the recipient email address is correct
- Some email providers may delay delivery

## Files Created

### Backend
- `app/services/smtp_email_service.py` - SMTP email service with HTML templates
- `app/api/endpoints/promotional_email.py` - API endpoints for promotional emails

### Frontend
- `src/pages/AdminPromotionalEmailPage.jsx` - Admin page component
- `src/pages/AdminPromotionalEmailPage.css` - Page styles

### Configuration
- Updated `backend/.env` with SMTP settings
- Updated `backend/.env.example` with SMTP documentation
