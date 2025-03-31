from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import openai
import os
import json
from datetime import datetime
app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

REQUIRED_FIELDS = ["budget", "total_size", "real_estate_type", "city"]

class UserMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class BotResponse(BaseModel):
    response: str
    conversation: Dict[str, Any]
    finished_conversation: bool

def load_history():
    try:
        with open("conversation_history.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_history(data):
    with open("conversation_history.json", "w") as f:
        json.dump(data, f)

def generate_response(user_input: str, current_fields: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"""
        Eres un recolector de informacion, relacionado a bienes raíces comerciales.
        Solo puedes responder con el fin de recolectar information relacionado a bienes raices, cualquier otra conversacion o tema no esta permitida y esta estricamente prohibida. 
        Tu objetivo es conversar con el usuario para recopilar la siguiente información requerida:
        
        - budget: presupuesto (por ejemplo, "20000 USD")
        - total_size: tamaño requerido (por ejemplo, "500 m2")
        - real_estate_type: tipo de inmueble (por ejemplo, "oficina")
        - city: ciudad (por ejemplo, "Ciudad de México")
        
        La conversación actual en formato JSON es:
        {json.dumps(current_fields)}
        El usuario acaba de decir: "{user_input}"
        Responde de forma natural y amigable. Si aún falta algún campo requerido, continúa preguntando de manera conversacional. 
        Si todos los campos están completos, ofrece un resumen en forma de listado y iconos de check y pregunta si desea agregar información extra solo una vez. 
        Tu respuesta debe ser un JSON válido con dos llaves:
        - "conversation_finished": true o false
        - "reply": el mensaje de respuesta para el usuario.
        - "updated_fields": un objeto con la información recopilada hasta el momento (incluyendo "extra_info" si existe) y el "user_id".
        Solo responde en formato JSON
"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150,
        )
        raw = response.choices[0].message.content.strip()
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error procesando la respuesta del LLM.")

@app.post("/chat", response_model=BotResponse)
def chat(user_message: UserMessage):
    history = load_history()
    if user_message.user_id:
        user_id = user_message.user_id
    else:
        user_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

    current_fields = history.get(user_id, {})
    current_fields["user_id"] = user_id

    if all(current_fields.get(field) for field in REQUIRED_FIELDS):
        summary = "Gracias por la información. Hemos recibido los siguientes datos:\n"
        for field in REQUIRED_FIELDS:
            summary += f"- {field}: {current_fields[field]}\n"
        summary += "En breve te enviaremos las propiedades disponibles."

        return BotResponse(response=summary, conversation=current_fields, finished_conversation=True)

    result = generate_response(user_message.message, current_fields)
    updated_fields = result.get("updated_fields", {})
    updated_fields["user_id"] = user_id

    if all(updated_fields.get(field) for field in REQUIRED_FIELDS):
        summary = "Gracias por la información. Hemos recibido los siguientes datos:\n"

        summary += f"- Ciudad: {updated_fields['city']}\n"
        summary += f"- Presupuesto: {updated_fields['budget']}\n"
        summary += f"- Tipo de propiedad: {updated_fields['real_estate_type']}\n"
        summary += f"- Tamano del inmueble: {updated_fields['total_size']}\n"

        summary += "En breve te enviaremos las propiedades disponibles."
        result["reply"] = summary

    history[user_id] = updated_fields
    save_history(history)

    return BotResponse(response=result.get("reply", ""), conversation=updated_fields, finished_conversation=False)
