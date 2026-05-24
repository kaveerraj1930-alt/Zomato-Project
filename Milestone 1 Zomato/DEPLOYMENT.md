# Deployment Guide

This guide explains how to deploy the restaurant recommendation system with backend on Render and frontend on Vercel.

## Architecture

- **Backend**: FastAPI API deployed on Render
- **Frontend**: Next.js application deployed on Vercel
- **Database**: No database needed (data loaded from Hugging Face datasets)
- **LLM**: Groq API for AI-powered recommendations

## Backend Deployment (Render)

### Prerequisites

- Render account (free tier available)
- Groq API key

### Steps

1. **Push backend code to GitHub**
   ```bash
   cd backend
   git init
   git add .
   git commit -m "Initial backend setup"
   git push origin main
   ```

2. **Create new Web Service on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `backend` directory
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       - `GROQ_API_KEY`: Your Groq API key

3. **Deploy**
   - Click "Deploy Web Service"
   - Wait for deployment to complete
   - Copy the backend URL (e.g., `https://zomato-recommender-backend.onrender.com`)

## Frontend Deployment (Vercel)

### Prerequisites

- Vercel account (free tier available)
- Backend URL from Render deployment

### Steps

1. **Push frontend code to GitHub**
   ```bash
   cd frontend
   git init
   git add .
   git commit -m "Initial frontend setup"
   git push origin main
   ```

2. **Create new Project on Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Connect your GitHub repository
   - Select the `frontend` directory
   - Configure:
     - **Framework Preset**: Next.js
     - **Environment Variables**:
       - `NEXT_PUBLIC_BACKEND_URL`: Your backend URL from Render (e.g., `https://zomato-recommender-backend.onrender.com`)

3. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Access your frontend at the provided Vercel URL

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
export GROQ_API_KEY=your_api_key
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### Backend

- `GET /` - API health check
- `GET /metadata` - Get available locations and cuisines
- `POST /recommendations` - Generate restaurant recommendations

### Request/Response Examples

#### Get Metadata

```bash
curl http://localhost:8000/metadata
```

Response:
```json
{
  "locations": ["Bellandur", "BTM", "Indiranagar"],
  "cuisines": ["Italian", "Chinese", "Indian"]
}
```

#### Get Recommendations

```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Bellandur",
    "budget": "high",
    "cuisine": ["Italian"],
    "min_rating": 4.0
  }'
```

Response:
```json
{
  "recommendations": [
    {
      "rank": 1,
      "restaurant": {
        "name": "Restaurant Name",
        "location": "Bellandur",
        "rating": 4.5,
        "cuisines": ["Italian"],
        "price_range": "High",
        "address": "123 Main St"
      },
      "explanation": "This restaurant offers excellent Italian cuisine..."
    }
  ],
  "overall_summary": "Top 5 Italian restaurants in Bellandur..."
}
```

## Troubleshooting

### Backend Issues

- **Cold starts**: Render may take 30-60 seconds to start the backend on first request
- **Memory limits**: Free tier has 512MB RAM, may need to upgrade for production
- **API key errors**: Ensure GROQ_API_KEY is set correctly in Render environment variables

### Frontend Issues

- **CORS errors**: Backend CORS is configured to allow all origins, but in production you should specify your Vercel domain
- **Backend connection**: Ensure NEXT_PUBLIC_BACKEND_URL is set correctly in Vercel environment variables
- **Build failures**: Check that all dependencies are installed in package.json

## Cost

- **Render**: Free tier includes 750 hours/month (sufficient for development)
- **Vercel**: Free tier includes unlimited deployments and 100GB bandwidth/month
- **Groq API**: Free tier available for development

## Next Steps

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Test the full integration
4. Configure custom domains (optional)
5. Set up monitoring and logging (optional)
