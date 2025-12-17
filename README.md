# AI Community Platform (CAAFW)

A comprehensive community platform for AI enthusiasts, similar to GenAI.works, There's An AI For That, and Product Hunt.

## Features

- **AI Products & Tools**: Browse and discover AI tools and products
- **Jobs Board**: AI-related job listings from multiple sources
- **Research Papers**: Latest AI research from arXiv and Papers With Code
- **Learning Resources**: Courses, tutorials, and educational content
- **Tech News**: Aggregated news from top AI publications
- **MCP Servers**: Model Context Protocol server directory
- **Investment Data**: Startup funding and investment information
- **Community**: Hacker News, Reddit, and GitHub trending content
- **Events**: AI conferences and meetups

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Search**: Elasticsearch
- **Task Queue**: Celery with Redis broker
- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS

## Project Structure

```
ai-community-platform/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── collectors/       # Data collectors for each source
│   │   ├── core/             # Core configuration
│   │   ├── db/               # Database setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── tasks/            # Celery tasks
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app router pages
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities and API client
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml
└── .env.example
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. Clone and configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. Start services with Docker:
```bash
docker-compose up -d
```

3. Run database migrations:
```bash
cd backend
alembic upgrade head
```

4. Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

5. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

6. Start Celery workers:
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
celery -A app.tasks.celery_app beat --loglevel=info
```

## API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Data Sources

See `AI_Community_Platform_Data_Sources.md` for a complete list of integrated data sources.

## License

MIT License
