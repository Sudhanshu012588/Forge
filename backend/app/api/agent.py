from fastapi import APIRouter
from app.core.Gemini_Model import Model
from fastapi import Body

router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)

@router.post("/chat")
def chat(msg:str = Body(embed=True)):
    model = Model("google_genai:gemini-2.5-flash")
    response = model.getResponse(msg)

    return {
        "Status":"Ok",
        "Response":response
    }
@router.post("/writeCode")
def writeCodes(msg:str=Body(embed=True)):
    model = Model("google_genai:gemini-2.5-flash")
    response = model.getResponse(msg)
    return{
        "Status":"Ok",
        "Response":response
    }