# Mart Price Tracker

A full-stack application for comparing product prices across Shwapno, Meena Bazar, and Unimart. Built with FastAPI and Next.js, ready for deployment on Render (backend) and Vercel (frontend).

## Features

- Real-time price comparison across multiple marts
- Mobile-friendly responsive design
- Fast and efficient scraping
- Error handling and fallbacks
- Clean and modern UI

## Tech Stack

### Backend
- FastAPI
- BeautifulSoup4
- Python 3.11
- Docker

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Axios
- Heroicons

## Local Development

### Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

### Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Deployment

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables if needed
5. Deploy!

### Frontend (Vercel)

1. Import your repository to Vercel
2. Set the following environment variable:
   - `NEXT_PUBLIC_BACKEND_URL`: Your Render backend URL
3. Deploy!

## Mobile Access

The application is fully responsive and can be accessed on mobile devices. Simply visit the Vercel deployment URL on your phone's browser.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this project for your own purposes! 