# Swarm Writer

**Swarm Writer** is a FastAPI-based autonomous AI research assistant leveraging the Gemini and Tavily APIs. It orchestrates a coordinated swarm of specialized AI agents—Planner, Researcher, Editor, and Writer—to automate the end-to-end process of researching complex topics, finding academic sources, synthesizing findings, and automatically generating comprehensive, properly formatted research papers with citations in both Markdown and LaTeX.

## Features

- **Multi-Agent Architecture**: Utilizes a combination of specialized AI agents:
  - **Planner Agent**: Generates a detailed, step-by-step research plan and structural outline.
  - **Researcher Agent**: Executes the plan, searches the web/academic sources (via Tavily), and synthesizes information.
  - **Writer Agent**: Drafts the academic paper based on the research data and plan, injecting precise citations.
  - **Editor Agent**: Reviews the drafted paper against academic standards and refines the content.
- **Dual Outputs**: Generates finalized papers in both **Markdown** and professional **LaTeX** formats.
- **Live Updates**: Emits real-time progress updates via WebSockets so you can watch your swarm of agents collaborate.
- **Dockerized Environment**: Fully containerized using Docker and Docker Compose for easy deployment and live code reloading.
- **RESTful API**: Robust backend built with FastAPI, using SQLite for storing session and paper data.

## System Requirements
- [Docker](https://www.docker.com/) and Docker Compose
- Python 3.11+ (if running locally without Docker)
- API Keys:
  - [Google Gemini API Key](https://aistudio.google.com/)
  - [Tavily API Key](https://tavily.com/)

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Sanket-S-Kale/swarm-writer.git
cd swarm-writer
```

### 2. Configure Environment Variables
Copy the example environment file to create your own configuration:
```bash
cp .env.example .env
```
Open the `.env` file and populate it with your actual API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run with Docker Compose (Recommended)
You can bring up the entire system (FastAPI backend + frontend) seamlessly using Docker:
```bash
docker-compose up -d --build
```
*Note: The `docker-compose.yml` mounts the `./app` directory to enable live code reloading.*

The application will now be running at: **http://localhost:8000**

---

## Manual Installation (Without Docker)

If you prefer to run the application directly on your machine:

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The application will be accessible at **http://localhost:8000**

---

## Usage

1. **Access the Frontend**: Navigate to `http://localhost:8000` in your web browser.
2. **Provide a Topic**: Enter your research topic into the UI.
3. **Start the Swarm**: Click "Generate Report".
4. **Monitor Progress**: You will see real-time WebSocket logs as the Planner, Researcher, Writer, and Editor agents dynamically coordinate.
5. **Download the Paper**: Once complete, you can download the generated report in your choice of **Markdown** or **LaTeX**.

---

## Codebase Structure

- `/app/main.py`: The FastAPI application entrypoint, handling core API routes and WebSocket lifecycle.
- `/app/agents/`: Contains the base and specialized agents.
    - `planner.py`: Responsible for structuring the inquiry.
    - `researcher.py`: Performs web and academic queries.
    - `writer.py`: Drafts narrative text and handles LaTeX generation.
    - `editor.py`: Refines drafts.
    - `coordinator.py`: Automates the workflow across all the agents.
- `/app/tools/`: Custom tooling scripts (e.g., Tavily integrations).
- `/data/`: Local storage for SQLite databases and output files.
- `/static/`: Frontend scripts (`script.js`), styles (`style.css`), and the main HTML UI.

---

## Contributing
Contributions are always welcome. Feel free to open issues or submit pull requests. Ensure no sensitive tokens (`.env`) are included in your commits.
