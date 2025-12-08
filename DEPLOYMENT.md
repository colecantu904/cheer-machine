# Deployment Instructions

## Vercel Deployment Setup

### 1. Environment Variables

Make sure you have the following environment variables set in your Vercel project settings:

- `SALT` - Your encryption salt (hex string)
- `NONCE` - Your encryption nonce (hex string)

To set these in Vercel:

1. Go to your project in Vercel Dashboard
2. Click on **Settings** → **Environment Variables**
3. Add both `SALT` and `NONCE` with their respective values
4. Make sure they're available for Production, Preview, and Development environments

### 2. Project Structure

The API is now structured as a Vercel Serverless Function:

- `/api/index.py` - Python serverless function that handles decryption
- `vercel.json` - Configuration for routing

### 3. Deploy

```bash
# Commit your changes
git add .
git commit -m "Configure API for Vercel deployment"
git push

# Vercel will automatically deploy
```

### 4. Local Development

For local development, you can still use uvicorn with the original FastAPI code:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server (if using the old src/app/api/index.py)
uvicorn src.app.api.index:app --reload

# Or run Next.js dev server (API won't work locally with serverless handler)
npm run dev
```

## Troubleshooting

### API returns 404

- Check that environment variables `SALT` and `NONCE` are set in Vercel
- Verify the `public/encrypted-images` directory exists and contains images
- Check Vercel function logs for errors

### CORS errors

- The serverless function includes CORS headers for all origins
- If you need to restrict origins, modify the `Access-Control-Allow-Origin` header in `/api/index.py`
