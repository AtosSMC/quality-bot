import sys
sys.path.append("..")
import json

from fastapi import Depends, HTTPException
from prompts.prompt_template import CLASSIFICATION_PROMPT
from typing import Union

def get_prompt(bot_name: str):
    db_bot = database_operations.get_bot(db, bot_name=bot_name)
     # If the bot does not exist, raise a 404 error
    if db_bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    dominio = db_bot.dominio
    tarefa = db_bot.tarefa
    empresa = db_bot.empresa
    max_words_response = db_bot.max_words_response
    prompt = CLASSIFICATION_PROMPT.format(domínio=dominio, tarefa=tarefa,empresa=empresa,max_words_response=max_words_response)
    return prompt

def validate_evaluator_response(resposta: str) -> Union[int, float, None]:
    """
    Valida a resposta e converte para int ou float.

    Args:
        resposta (str): A resposta a ser validada.

    Returns:
        int | float | None: Retorna um inteiro, float ou None.
    """
    try:
        return int(resposta.strip())
    except:
        try:
            return float(resposta.strip().replace(",", "."))
        except:
            return None  # ou -1 para indicar erro

def unpack_response(completion) -> any:
    try:
        response_unpacked = json.loads(completion)
        return response_unpacked 
    except (json.JSONDecodeError, TypeError) as e:
        return None