# LegalEase – AI-Powered Legal Document Generator

## About the Project

LegalEase is an AI-powered legal document drafting and generation platform developed using Python, FastAPI, Streamlit, and Google Gemini API.

The application helps users generate structured legal documents based on their requirements. It simplifies the document creation process through an easy-to-use interface and AI-powered generation.

## Features

- AI-powered legal document generation.
- User-friendly Streamlit interface.
- Backend API integration using FastAPI.
- Google Gemini API integration.
- Structured document formatting.
- Document generation utilities.
- Automated testing using Pytest.

## Technologies Used

- Python
- Google Gemini API
- FastAPI
- Streamlit
- Pytest
- Docker
- HTML and CSS (where applicable)

## Project Structure

LegalEase/

- ai_core/ – AI logic and Gemini document generation.
- assets/ – Project images and other resources.
- backend/ – Backend API and request/response schemas.
- document_utils/ – Document formatting and utility functions.
- frontend/ – Streamlit user interface.
- tests/ – Automated test cases.
- .env.example – Example environment configuration.
- .gitignore – Files excluded from Git tracking.
- Dockerfile – Docker image configuration.
- Procfile – Application deployment configuration.
- README.md – Project documentation.
- docker-compose.yml – Docker service configuration.
- requirements.txt – Required Python dependencies.

## Installation and Setup

1. Clone the repository:

git clone https://github.com/Indhumathi-codes/LegalEase.git

2. Navigate to the project folder:

cd LegalEase

3. Create a virtual environment:

python -m venv .venv

4. Activate the virtual environment:

Windows:

.venv\Scripts\activate

5. Install dependencies:

pip install -r requirements.txt

6. Configure your Gemini API key in the environment variables.

## Running the Application

Start the backend server:

uvicorn backend.main:app --reload

Start the frontend in another terminal:

streamlit run frontend/app.py

Open the Streamlit URL displayed in your terminal to access the application.

## Testing

This project uses Pytest to test document formatting and application functionality.

Run the tests using:

pytest -q

## Project Objectives

- Simplify legal document drafting.
- Reduce manual document preparation.
- Explore Generative AI in real-world applications.
- Integrate AI models with web applications.
- Develop practical skills in Python and API integration.

## Future Enhancements

- Support for more legal document types.
- Improved document customization.
- Additional export formats.
- Enhanced user experience.

## Developed By

**Indhumathi Ramalingam**

GitHub: https://github.com/Indhumathi-codes

---

⭐ Thank you for visiting LegalEase!
