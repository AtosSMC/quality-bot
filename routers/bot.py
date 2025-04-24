import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from prompts.prompt_template import CLASSIFICATION_PROMPT
from src import tasks
from src.bot_evaluator import LLMIntegrator
from config import LLM
from functools import partial
import pandas as pd
import io   

router = APIRouter(
    prefix="/bots",
    tags=["bots"],
    responses={404: {"description": "Not found"}},
)

@router.post("/evaluate_bot")
async def evaluate_bot(file: UploadFile = File(...)):
    try:
        bot_prompt = tasks.get_prompt(bot_name, db)
        bot_prompt += """            
            ### Histórico da conversa: ###
            "{chat_history}"
 
            ### Trechos dos documentos: ###
            " {context} "
 
            ### Pergunta que você deve responder: ###
            ```{question}```
 
            Assistant:"""
        
        file_content = await file.read()
        df = pd.read_csv(io.BytesIO(file_content), encoding="iso-8859-2")
        
        evaluator = BotEvaluator(df,
                                 question_col="Pergunta",  # Nome da coluna de perguntas # Nome da coluna de respostas
                                 bot_prompt=bot_prompt,
                                 evaluator_prompt=EVALUATOR_TEMPLATE, 
                                 llm=LLM,
                                 response_validator = lambda x: x

                                 )

        return evaluator.generate_response_df()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))