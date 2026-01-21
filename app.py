from fastapi import FastAPI, HTTPException
import uvicorn
from SQLAgent import load_model,db,getkit,AgentCreate,AskQuestion,load_database
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS Configuration - MUST BE BEFORE ROUTES
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "https://your-frontend-domain.com",  # Add your production domain
        "*"  # Allow all origins (use only for testing)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionRequest(BaseModel):
    question: str

# configuring all the needs and requirements
try:
    model, info = load_model()
    database = load_database()
    tools = getkit(model=model, database=database).get_tools()
    agent = AgentCreate(model, tools, database)
    print('Configuration loaded successfully')
except Exception as e:
    print(f'Failed to collect configuration due error {e}')
    raise

@app.get('/')
async def get_info():
    return {
        'Model': f"{info['Model']}",
        "Database": f'{database.dialect}',
        "Tools": [tool.name for tool in tools],
        "Agent": "SQL Agent",
    }

@app.get('/database')
def database_info():
    return {
        "Database": database.dialect,
        "Tables": database.get_table_names(), 
    }

# Fix the endpoint to accept both query params and body
@app.post('/ask')
async def query_database(request: QuestionRequest = None, question: str = None):
    try:
        # Support both body and query parameter
        query_text = request.question if request else question
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Question is required")
        
        result = AskQuestion(agent=agent, question=query_text)
        return {"result": result, "question": query_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
