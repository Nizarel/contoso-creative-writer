import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv
from prompty.tracer import trace
from prompty.core import PromptyStream, AsyncPromptyStream
from evaluate.evaluators import evaluate_image

from orchestrator import Task, create
from telemetry import setup_telemetry

base = Path(__file__).resolve().parent

load_dotenv()

# Response models for Swagger documentation
class HealthResponse(BaseModel):
    message: str

class ImageUploadResponse(BaseModel):
    filename: str
    location: str
    message: str
    safety: str

class ErrorResponse(BaseModel):
    detail: str

app = FastAPI(
    title="Contoso Creative Writing Assistant API",
    description="""
    A multi-agent AI system that creates well-researched, product-specific articles using Azure OpenAI services.
    
    ## Features
    
    * **Research Agent**: Uses Bing Grounding Tool to research topics
    * **Product Agent**: Finds relevant products using Azure AI Search
    * **Writer Agent**: Creates engaging articles combining research and products
    * **Editor Agent**: Reviews and refines content for quality
    * **Content Safety**: Evaluates uploaded images for harmful content
    
    ## Workflow
    
    1. Submit a research topic, product context, and writing assignment
    2. The system orchestrates multiple AI agents to create content
    3. Real-time streaming responses show progress through each agent
    4. Final article is reviewed and refined by the editor agent
    
    ## Authentication
    
    This API uses Azure authentication. Ensure proper Azure credentials are configured.
    """,
    version="1.0.0",
    contact={
        "name": "Contoso Creative Writing Team",
        "url": "https://github.com/Azure-Samples/contoso-creative-writer",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ],
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check and status endpoints"
        },
        {
            "name": "Content Creation", 
            "description": "Main article creation workflow using AI agents"
        },
        {
            "name": "Content Safety",
            "description": "Image upload and content safety evaluation"
        },
        {
            "name": "Agents",
            "description": "Information about available AI agents"
        }
    ]
)

code_space = os.getenv("CODESPACE_NAME")
app_insights = os.getenv("APPINSIGHTS_CONNECTIONSTRING")

if code_space: 
    origin_8000= f"https://{code_space}-8000.app.github.dev"
    origin_5173 = f"https://{code_space}-5173.app.github.dev"
    ingestion_endpoint = app_insights.split(';')[1].split('=')[1]
    
    origins = [origin_8000, origin_5173, os.getenv("API_SERVICE_ACA_URI"), os.getenv("WEB_SERVICE_ACA_URI"), ingestion_endpoint]
else:
    origins = [
        o.strip()
        for o in Path(Path(__file__).parent / "origins.txt").read_text().splitlines()
    ]
    origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_telemetry(app)

@app.get("/", 
         response_model=HealthResponse,
         summary="Health Check",
         description="Simple health check endpoint to verify the API is running.",
         tags=["Health"])
async def root():
    """
    Health check endpoint.
    
    Returns a simple message to confirm the API is operational.
    """
    return {"message": "Hello World"}


@app.post("/api/article",
          summary="Create Article",
          description="""
          Create a well-researched article using AI agents.
          
          This endpoint orchestrates multiple AI agents:
          1. **Researcher Agent**: Researches the given topic using Bing
          2. **Product Agent**: Finds relevant products using Azure AI Search
          3. **Writer Agent**: Creates an engaging article
          4. **Editor Agent**: Reviews and refines the content
          
          Returns a server-sent events stream with real-time progress updates.
          """,
          responses={
              200: {
                  "description": "Server-sent events stream with agent progress",
                  "content": {
                      "text/event-stream": {
                          "example": "data: {\"type\": \"message\", \"message\": \"Starting researcher agent task...\"}\n\n"
                      }
                  }
              },
              422: {"model": ErrorResponse, "description": "Validation Error"}
          },
          tags=["Content Creation"])
@trace
async def create_article(task: Task):
    """
    Create an article using the multi-agent workflow.
    
    **Request Body:**
    - **research**: Topic or context for research (e.g., "Latest camping trends for winter")
    - **products**: Context for product search (e.g., "Tents and sleeping bags")
    - **assignment**: Writing instructions (e.g., "Write an 800-word engaging article")
    
    **Response Stream Events:**
    - `message`: General progress messages
    - `researcher`: Research agent results
    - `marketing`: Product agent results  
    - `writer`: Writer agent progress and content
    - `editor`: Editor agent feedback
    - `partial`: Streaming article content
    - `error`: Error messages
    
    The response is a continuous stream of JSON objects, each representing
    progress from different agents in the workflow.
    """
    return StreamingResponse(
        PromptyStream(
            "create_article", create(task.research, task.products, task.assignment)
        ),
        media_type="text/event-stream",
    )

@app.post("/api/upload-image",
          response_model=ImageUploadResponse,
          summary="Upload and Evaluate Image",
          description="""
          Upload an image file and evaluate it for content safety.
          
          This endpoint:
          1. Accepts image file uploads (PNG, JPG, etc.)
          2. Saves the image to the web/public directory
          3. Evaluates content safety using Azure AI services
          4. Returns safety assessment and file location
          
          **Safety Evaluation:**
          - Detects harmful or inappropriate content
          - Provides recommendations for blog inclusion
          - Uses Azure AI Content Safety services
          """,
          responses={
              200: {"model": ImageUploadResponse, "description": "Image uploaded and evaluated successfully"},
              400: {"model": ErrorResponse, "description": "Invalid file or upload error"},
              422: {"model": ErrorResponse, "description": "Validation Error"}
          },
          tags=["Content Safety"])
async def upload_image(file: UploadFile = File(..., description="Image file to upload and evaluate")):
    """
    Upload an image and evaluate it for content safety.
    
    **Parameters:**
    - **file**: Image file (multipart/form-data)
      - Supported formats: PNG, JPG, JPEG, GIF, etc.
      - File is saved to web/public directory
    
    **Safety Evaluation:**
    The uploaded image is automatically evaluated for:
    - Harmful or inappropriate content
    - Protected content that shouldn't be included in blogs
    - General safety compliance
    
    **Response:**
    - **filename**: Original filename
    - **location**: Server file path where image is stored
    - **message**: Safety evaluation message with recommendations
    - **safety**: "Yes this is safe" or empty string for unsafe content
    
    **Example Response for Safe Image:**
    ```json
    {
        "filename": "camping-tent.jpg",
        "location": "/path/to/web/public/camping-tent.jpg", 
        "message": "This image is safe to include in the blog ✅",
        "safety": "Yes this is safe"
    }
    ```
    
    **Example Response for Unsafe Image:**
    ```json
    {
        "filename": "inappropriate.jpg",
        "location": "/path/to/web/public/inappropriate.jpg",
        "message": "❌This image contains harmful content. We do not recommend including it in the blog!❌",
        "safety": ""
    }
    ```
    """

    base = Path(__file__).resolve().parents[1]

    # Set the directory for the stored image
    image_dir = os.path.join(base, 'web/public')
    print(image_dir)

    # Initialize the image path (note the filetype should be png)
    file_path  = os.path.join(image_dir, file.filename)
    
    # Save the image to the specified path
    with open(file_path, "wb") as image:
        content = await file.read()
        image.write(content)

    project_scope = {
        "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],   
        "resource_group_name": os.environ["AZURE_RESOURCE_GROUP"],
        "project_name": os.environ["AZURE_AI_PROJECT_NAME"],        
    }

    from evaluate.evaluate import evaluate_image
    print(file_path)
    result = evaluate_image(project_scope, file_path)

    if len(result) > 0:
        # Return the filename and location
        return JSONResponse({"filename": file.filename, 
                             "location": file_path,
                            "message": f'''
                            ❌This image contains the following harmful/protected content {result}. 
                            We do not recommend including it in the blog!❌''',
                            "safety": ""
                            })
    else:
        # Return the filename and location
        return JSONResponse({"filename": file.filename, 
            "location": file_path,
            "message":"This image is safe to include in the blog ✅",
            "safety": "Yes this is safe"
            })


# TODO: fix open telemetry so it doesn't slow app so much
FastAPIInstrumentor.instrument_app(app)

# Additional endpoints for API documentation
@app.get("/api/status",
         response_model=Dict[str, Any],
         summary="API Status",
         description="Get detailed API status including service health and configuration.",
         tags=["Health"])
async def get_status():
    """
    Get comprehensive API status information.
    
    Returns information about:
    - API version and status
    - Environment configuration
    - Service dependencies
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Contoso Creative Writing Assistant",
        "environment": {
            "codespace": bool(os.getenv("CODESPACE_NAME")),
            "azure_configured": bool(os.getenv("AZURE_SUBSCRIPTION_ID")),
            "openai_configured": bool(os.getenv("AZURE_OPENAI_NAME")),
            "search_configured": bool(os.getenv("AZURE_SEARCH_ENDPOINT"))
        }
    }

@app.get("/api/agents",
         response_model=Dict[str, Any],
         summary="Available Agents",
         description="Get information about available AI agents and their capabilities.",
         tags=["Agents"])
async def get_agents():
    """
    Get information about available AI agents.
    
    Returns details about each agent including:
    - Agent name and purpose
    - Input requirements
    - Output format
    """
    return {
        "agents": [
            {
                "name": "researcher",
                "description": "Conducts web research using Bing Grounding Tool",
                "input": "Research context/query",
                "output": "Structured research results with web sources"
            },
            {
                "name": "product",
                "description": "Finds relevant products using Azure AI Search",
                "input": "Product search context",
                "output": "List of matching products with similarity scores"
            },
            {
                "name": "writer", 
                "description": "Creates articles combining research and product information",
                "input": "Research results, products, and writing assignment",
                "output": "Generated article content with feedback"
            },
            {
                "name": "editor",
                "description": "Reviews and refines article content for quality",
                "input": "Article content and feedback",
                "output": "Editorial decision and improvement suggestions"
            }
        ]
    }
