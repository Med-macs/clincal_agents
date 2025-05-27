# Clinical Agents 🏥

A clinical agent system powered by LangGraph and LangChain for processing and analyzing medical information.

## Features

- 🤖 AI-powered clinical analysis
- 🔄 Real-time processing
- 📊 Interactive UI with Streamlit
- 🚀 FastAPI backend
- 🔐 Secure Google AI integration

## Prerequisites

- Python 3.8+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Google Cloud Project with enabled APIs:
  - Cloud Run
  - Artifact Registry
  - Google AI APIs
- `.env` file with required credentials

## Development

### Quick Start

The project includes a comprehensive CLI for local development:

```bash
# Make CLI executable
chmod +x cli.sh

# Install dependencies and setup environment
./cli.sh install

# Start all services
./cli.sh start-all
```

### Available CLI Commands

| Command | Description |
|---------|-------------|
| `./cli.sh help` | Show help message |
| `./cli.sh install` | Install dependencies and set up virtual environment |
| `./cli.sh start-ui` | Start only the Streamlit UI |
| `./cli.sh start-server` | Start only the FastAPI server |
| `./cli.sh clean` | Remove virtual environment and cached files |
| `./cli.sh test-api` | Test API endpoints with sample data |

## Deployment

### Google Cloud Run Setup

1. Initialize Google Cloud project:
```bash
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

2. Enable required APIs:
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com
```

3. Make deployment script executable:
```bash
chmod +x scripts/deploy.sh
```

4. Deploy to Cloud Run:
```bash
# Deploy with all stages (check, build, push, deploy)
./scripts/deploy.sh all

# Or run individual stages:
./scripts/deploy.sh check   # Run pre-deployment checks only
./scripts/deploy.sh build   # Build and tag Docker image
./scripts/deploy.sh push    # Push image to Google Container Registry
./scripts/deploy.sh deploy  # Deploy to Cloud Run
```

The deployment script will:
- Build the Docker image
- Push to Google Container Registry
- Deploy to Cloud Run
- Configure environment variables

### Environment Variables

Required environment variables:

```
GOOGLE_API_KEY=your_api_key
DATABASE_URL=postgresql://localhost/clinical_agents
DEBUG=False
ENVIRONMENT=production
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
## Supabase Setup

This project uses Supabase as the database backend. You can either use a hosted Supabase instance or run it locally.

### Option 1: Local Supabase (Recommended for Development)

1. Install Supabase CLI:

   ```bash
   brew install supabase/tap/supabase
   ```

2. Start local Supabase services:

   ```bash
   supabase start
   ```

3. Access the local Supabase dashboard at http://localhost:54323

### Option 2: Hosted Supabase

1. Create a Supabase project at [https://supabase.com](https://supabase.com)

2. Get your project URL and API key from the project settings

3. Update your `.env` file with the Supabase credentials:

   ```
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_api_key
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the agent framework
- [LangChain](https://github.com/langchain-ai/langchain) for LLM interactions
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Streamlit](https://streamlit.io/) for the UI components
