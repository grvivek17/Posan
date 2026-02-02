# Backend Environment Configuration

## Database Connection

The backend `.env` file has been configured to use **Supabase** as the PostgreSQL database.

## Configuration File

Location: `backend/.env`

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.nzrsksoyalnoayvhscou.supabase.co:5432/postgres
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Setup Instructions

1. **Replace the password**: Change `[YOUR-PASSWORD]` with your actual Supabase database password
2. **Get your password from Supabase**:
   - Go to your Supabase project dashboard
   - Navigate to **Settings** → **Database**
   - Copy your database password
3. **Update the .env file**: Replace `[YOUR-PASSWORD]` in the connection string

## Example

If your Supabase password is `mySecurePassword123`, update the file to:

```env
DATABASE_URL=postgresql://postgres:mySecurePassword123@db.nzrsksoyalnoayvhscou.supabase.co:5432/postgres
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Supabase Connection Details

- **Host**: `db.nzrsksoyalnoayvhscou.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **SSL**: Automatically handled by Supabase

## Testing the Connection

After updating your password, test the connection:

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

If the connection is successful, you'll see:
```
INFO:     Application startup complete.
```

## Troubleshooting

### Connection Refused
- Check your Supabase project is active
- Verify the password is correct
- Ensure your IP is allowed in Supabase settings

### SSL Error
- Supabase requires SSL connections
- The psycopg2-binary package handles this automatically

### Password Contains Special Characters
- If your password has special characters, URL-encode them:
  - `@` → `%40`
  - `#` → `%23`
  - `%` → `%25`
  - etc.

## Benefits of Using Supabase

✅ **Cloud Database** - No local PostgreSQL installation needed
✅ **Auto Backups** - Automatic database backups
✅ **Scalable** - Easily scale as your app grows
✅ **Free Tier** - Generous free tier for development
✅ **Real-time** - Built-in real-time capabilities (optional)
✅ **Dashboard** - Visual database management

## Alternative: Local PostgreSQL

If you want to use a local PostgreSQL database instead, change the DATABASE_URL to:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/qrcode_db
```

And create the local database:
```sql
CREATE DATABASE qrcode_db;
```

## Next Steps

1. Update your password in `backend/.env`
2. Start the backend server
3. The database tables will be created automatically
4. Start generating QR codes!

---

**Note**: Never commit the `.env` file with real passwords to version control. It's already in `.gitignore`.
