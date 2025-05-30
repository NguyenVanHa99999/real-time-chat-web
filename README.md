# Real-Time Chat Web Application

## Project Overview
A real-time chat web application built with Vue.js (frontend) and FastAPI (backend) using WebSocket for instant messaging.

## Technologies
- Frontend: Vue.js
- Backend: Python FastAPI
- Real-time Communication: WebSocket

## Setup and Installation
1. Clone the repository
2. Set up frontend:
   ```
   cd chat-frontend/vue-project
   npm install
   ```
3. Set up backend:
   ```
   cd chat-backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the Application
- Frontend: `npm run serve`
- Backend: `uvicorn main:app --reload`

## Project Structure
- `chat-frontend/`: Vue.js frontend
- `chat-backend/`: Python FastAPI backend

## Contributing
Please follow the branch naming conventions:
- Feature branches: `feat/{feature-name}`
- Test branches: `test/{test-name}`
- Hotfix branches: `hotfix-{issue-name}`
