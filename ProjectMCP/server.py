from fastapi import FastAPI, HTTPException
from transformers import pipeline
from typing import Dict, Any, List
import json

app = FastAPI()

# Initialize the Hugging Face pipeline
generator = pipeline('text-generation', model='gpt2')

@app.post("/mcp/v1/generate")
async def generate(request: Dict[Any, Any]) -> Dict[str, Any]:
    try:
        # Extract input from MCP request
        if 'inputs' not in request or 'prompt' not in request['inputs']:
            raise HTTPException(status_code=400, detail="Missing 'prompt' in inputs")
        
        prompt = request['inputs']['prompt']
        
        # Generate text using Hugging Face pipeline
        result = generator(prompt, max_length=100, num_return_sequences=1)
        
        # Format response according to MCP protocol
        response = {
            "outputs": {
                "generated_text": result[0]['generated_text']
            }
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/v1/models")
async def list_models() -> Dict[str, List[Dict[str, str]]]:
    return {
        "models": [
            {
                "id": "gpt2",
                "name": "GPT-2",
                "description": "OpenAI's GPT-2 model for text generation"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
