# Agentic RAG Chat

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)

A fully custom chatbot built with Agentic RAG (Retrieval-Augmented Generation), combining OpenAI models with a local knowledge base for accurate, context-aware, and explainable responses. Features a lightweight, dependency-free frontend and a streamlined FastAPI backend for complete control and simplicity.

![Demo](demo.gif)


## Features

- Pure HTML/CSS/JavaScript frontend with no external dependencies
- FastAPI backend with OpenAI integration
- Agentic RAG implementation with:
  - Context retrieval using embeddings and cosine similarity
  - Step-by-step reasoning with Chain of Thought
  - Function calling for dynamic context retrieval
- Comprehensive error handling and logging
- Type-safe implementation with Python type hints
- Configurable through environment variables

## Project Structure

```
agentic_rag/
├── backend/
│   ├── embeddings.py    # Embedding and similarity functions
│   ├── rag_engine.py    # Core RAG implementation
│   └── server.py        # FastAPI server
├── frontend/
│   └── index.html       # Web interface
├── requirements.txt     # Python dependencies
├── .env.sample         # Sample environment variables
└── README.md           # Documentation
```

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Git (for version control)

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

2. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

## Running the Application

### Backend Setup
1. Ensure you are in the project root directory and virtual environment is activated

2. Start the FastAPI backend:
```bash
cd backend
uvicorn server:app --reload
```
The backend will be available at `http://localhost:8000`

### Frontend Setup
1. Open the `index.html` file directly in your web browser
   - No additional setup required for the frontend
   - Recommended browsers: Chrome, Firefox, Safari

## Environment Variables
Create a `.env` file in the backend directory with the following variables:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Type your question in the input field
2. The system will:
   - Retrieve relevant context using embeddings
   - Generate a step-by-step reasoning process
   - Provide a final answer based on the context and reasoning
3. View the intermediate steps and reasoning process in the response

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_API_KEY | Your OpenAI API key | Required |
| OPENAI_MODEL | OpenAI model to use | gpt-4o-mini |
| HOST | Backend server host | 0.0.0.0 |
| PORT | Backend server port | 8000 |

## Error Handling

The application includes comprehensive error handling:

- API errors are logged and returned with appropriate status codes
- Frontend displays user-friendly error messages
- Detailed logging for debugging and monitoring
- Graceful fallbacks for common failure scenarios

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

Please ensure your code:
- Includes appropriate tests
- Follows the existing code style
- Updates documentation as needed
- Includes type hints
- Has meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Never commit your `.env` file or API keys
- Keep dependencies updated
- Follow security best practices for production deployment
- Report security issues through GitHub's security advisory

## Troubleshooting

Common issues and solutions:

1. **OpenAI API Error**
   - Verify your API key is correct
   - Check your API usage limits
   - Ensure the model name is valid

2. **Backend Connection Failed**
   - Confirm the backend server is running
   - Check the port is not in use
   - Verify firewall settings

3. **Embedding Errors**
   - Ensure input text is not empty
   - Check for proper text encoding
   - Verify numpy installation

4. **Python Version**
   - Ensure Python 3.11+ is installed
   - Check that all dependencies are correctly installed
   - Verify your OpenAI API key is valid and has sufficient credits

## Acknowledgments

- OpenAI for their API and models
- FastAPI framework
- Contributors and maintainers
