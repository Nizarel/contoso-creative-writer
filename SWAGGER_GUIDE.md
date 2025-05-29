# Swagger Documentation Guide

## Overview

The Contoso Creative Writing Assistant API now includes comprehensive Swagger/OpenAPI documentation for easy exploration and testing of the API endpoints.

## Accessing Swagger Documentation

### 1. Interactive Swagger UI
Visit: `http://localhost:8000/docs`

Features:
- Interactive API explorer
- Try endpoints directly from the browser
- Real-time request/response testing
- Comprehensive endpoint documentation
- Request/response schema validation

### 2. ReDoc Documentation
Visit: `http://localhost:8000/redoc`

Features:
- Clean, readable documentation format
- Detailed schema information
- Code examples
- Downloadable OpenAPI specification

### 3. OpenAPI JSON Schema
Visit: `http://localhost:8000/openapi.json`

Raw OpenAPI 3.0 specification in JSON format for:
- API client generation
- Integration with other tools
- Custom documentation generation

## API Endpoints Overview

### Health & Status
- `GET /` - Basic health check
- `GET /api/status` - Detailed API status and configuration
- `GET /api/agents` - Information about available AI agents

### Content Creation
- `POST /api/article` - Create articles using multi-agent workflow
  - Accepts Task object with research, products, and assignment
  - Returns server-sent events stream with real-time progress
  - Includes detailed documentation of the multi-agent workflow

### Content Safety
- `POST /api/upload-image` - Upload and evaluate images for safety
  - Accepts multipart file uploads
  - Returns safety assessment and recommendations
  - Uses Azure AI Content Safety services

## Enhanced Features

### 1. Comprehensive Documentation
- Detailed endpoint descriptions
- Parameter validation and examples
- Response models and error handling
- Authentication and configuration requirements

### 2. Request/Response Models
- Pydantic models with validation
- Example payloads and responses
- Field descriptions and constraints
- Type safety and validation

### 3. Organized Structure
- Tagged endpoints for easy navigation
- Logical grouping of related functionality
- Clear API versioning and metadata
- Contact and license information

### 4. Error Documentation
- Detailed error response formats
- HTTP status code explanations
- Validation error examples
- Troubleshooting guidance

## Usage Examples

### Testing Article Creation
```bash
curl -X POST "http://localhost:8000/api/article" \
  -H "Content-Type: application/json" \
  -d '{
    "research": "Latest camping trends for winter",
    "products": "Tents and sleeping bags",
    "assignment": "Write an 800-word engaging article"
  }'
```

### Testing Image Upload
```bash
curl -X POST "http://localhost:8000/api/upload-image" \
  -F "file=@example-image.jpg"
```

### Checking API Status
```bash
curl -X GET "http://localhost:8000/api/status"
```

## Development Benefits

### 1. API Discovery
- Easy exploration of available endpoints
- Understanding of request/response formats
- Real-time testing capabilities

### 2. Client Development
- Automatic client code generation
- Type-safe API interactions
- Consistent interface documentation

### 3. Testing & Validation
- Interactive endpoint testing
- Request validation and error checking
- Response format verification

### 4. Team Collaboration
- Shared API documentation
- Clear interface contracts
- Reduced integration complexity

## Configuration

The Swagger documentation automatically reflects your current configuration:

- Environment detection (Codespaces, local, production)
- Azure service configuration status
- Available AI agents and capabilities
- Authentication requirements

## Next Steps

1. **Start the API server**: `python src/api/main.py`
2. **Open Swagger UI**: Navigate to `http://localhost:8000/docs`
3. **Explore endpoints**: Browse the interactive documentation
4. **Test functionality**: Use the "Try it out" feature
5. **Generate clients**: Download the OpenAPI spec for client generation

## Troubleshooting

### Common Issues

1. **Server not running**: Ensure the FastAPI server is started
2. **Port conflicts**: Check that port 8000 is available
3. **CORS issues**: Verify CORS configuration for your domain
4. **Authentication**: Ensure Azure credentials are properly configured

### Debug Mode

For detailed API debugging, set environment variables:
```bash
export FASTAPI_DEBUG=true
export LOG_LEVEL=DEBUG
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Prompty Documentation](https://prompty.ai/)
