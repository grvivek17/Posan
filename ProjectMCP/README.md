# Hugging Face MCP Server

This is a Model Context Protocol (MCP) server that integrates with Hugging Face's transformers library. It provides an MCP-compliant API for text generation using the GPT-2 model.

## Features

- Text generation using Hugging Face's GPT-2 model
- MCP v1 compliant API endpoints
- FastAPI-based server implementation

## Setup

1. Ensure you have Python 3.7+ installed
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the server with:

```bash
python server.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Generate Text
- **Endpoint**: `/mcp/v1/generate`
- **Method**: POST
- **Request Format**:
  ```json
  {
    "inputs": {
      "prompt": "Your text prompt here"
    }
  }
  ```
- **Response Format**:
  ```json
  {
    "outputs": {
      "generated_text": "Generated text response"
    }
  }
  ```

### List Models
- **Endpoint**: `/mcp/v1/models`
- **Method**: GET
- **Response Format**:
  ```json
  {
    "models": [
      {
        "id": "gpt2",
        "name": "GPT-2",
        "description": "OpenAI's GPT-2 model for text generation"
      }
    ]
  }
  ```
