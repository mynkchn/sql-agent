from fastapi import FastAPI
import uvicorn
from SQLAgent import load_model,db,getkit,AgentCreate,AskQuestion,load_database


app=FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8082"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# configuring all the needs and requirements
try:
 model,info=load_model()
 database=load_database()
 tools=getkit(model=model,database=database).get_tools()
 agent=AgentCreate(model,tools,database)
 print('Configuration loaded successfully')
except Exception as e:
    print(f'Failed to collect configuration due error {e}')


# get configuration information
@app.get('/')
async def get_info():
    return {
        'Model':f"{info['Model']}",
        "Database":f'{database.dialect}',
        "Tools":[tool.name for tool in tools],
        "Agent":f"SQL Agent",
    }

# get database information
@app.get('/database')
def database_info():
    return {
        "Database":database.dialect,
        "Tables":database.get_table_names(), 
    }

# communicate with database in real language
@app.post('/ask')
async def query_database(question):
    result=AskQuestion(agent=agent,question=question)
    return result

# if __name__=="__main__":
#     uvicorn.run("app:app",port=5000,log_level="info")
    
