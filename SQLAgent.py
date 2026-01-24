from fastapi import FastAPI, Query
from enum import Enum
import uvicorn
from SQLAgent import load_model, db, getkit, AgentCreate, AskQuestion, load_database, GetPrompt


app = FastAPI()


# Language enumeration
class Language(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    GUJARATI = "gujarati"


# Language-specific instructions
LANGUAGE_INSTRUCTIONS = {
    "hindi": """
### भाषा निर्देश
आपको सभी उत्तर हिंदी में देने हैं। तकनीकी शब्दों को हिंदी में अनुवाद करें या कोष्ठक में अंग्रेजी शब्द दें।
उदाहरण: "समाधान दर (Resolution Rate)", "वार्ड (Ward)", "सर्वेक्षणकर्ता (Surveyor)"

**महत्वपूर्ण:** सभी शीर्षक, विश्लेषण, और सिफारिशें हिंदी में लिखें।
""",
    "gujarati": """
### ભાષા સૂચના
તમારે બધા જવાબો ગુજરાતીમાં આપવાના છે. તકનીકી શબ્દોનો ગુજરાતીમાં અનુવાદ કરો અથવા કૌંસમાં અંગ્રેજી શબ્દ આપો.
ઉદાહરણ: "નિરાકરણ દર (Resolution Rate)", "વોર્ડ (Ward)", "સર્વેક્ષક (Surveyor)"

**મહત્વપૂર્ણ:** બધા શીર્ષકો, વિશ્લેષણ અને ભલામણો ગુજરાતીમાં લખો.
""",
    "english": ""
}


# Store agents for different languages
agents = {}


# configuring all the needs and requirements
try:
    model, info = load_model()
    database = load_database()
    tools = getkit(model=model, database=database).get_tools()
    
    # Create agents for each language
    for lang in Language:
        lang_value = lang.value
        # Temporarily modify GetPrompt to include language instruction
        original_prompt = GetPrompt(database)
        lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang_value, "")
        
        # Inject language instruction at the beginning of the prompt
        modified_prompt = f"{lang_instruction}\n\n{original_prompt}"
        
        # You'll need to modify your SQLAgent.py to accept this
        # For now, we'll create agents dynamically in the endpoint
        if lang_value == "english":
            agents[lang_value] = AgentCreate(model, tools, database)
    
    print('Configuration loaded successfully')
except Exception as e:
    print(f'Failed to collect configuration due error {e}')


# get configuration information
@app.get('/')
async def get_info():
    return {
        'Model': f"{info['Model']}",
        "Database": f'{database.dialect}',
        "Tools": [tool.name for tool in tools],
        "Agent": f"SQL Agent",
        "Supported_Languages": ["english", "hindi", "gujarati"]
    }


# get database information
@app.get('/database')
def database_info():
    return {
        "Database": database.dialect,
        "Tables": database.get_table_names(), 
    }


# communicate with database in real language
@app.post('/ask')
async def query_database(
    question: str,
    language: Language = Query(Language.ENGLISH, description="Response language")
):
    lang_value = language.value
    
    # Add language instruction to the question itself
    if lang_value != "english":
        lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang_value, "")
        # Prepend language instruction to the question
        modified_question = f"{lang_instruction}\n\nUser Question: {question}"
        result = AskQuestion(agent=agents.get("english"), question=modified_question)
    else:
        result = AskQuestion(agent=agents.get("english"), question=question)
    
    return {
        "question": question,
        "language": lang_value,
        "result": result
    }


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, log_level="info")
