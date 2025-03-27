from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import openai
import os
import json

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

REQUIRED_FIELDS = ["budget", "total_size", "real_estate_type", "city"]


class UserMessage(BaseModel):
    message: str
    session_data: Dict[str, Any] = {}


class BotResponse(BaseModel):
    response: str
    session_data: Dict[str, Any]


def extract_fields(user_input: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"""
    Eres un asistente especializado en bienes raíces comerciales en Mexico.
        
    Extrae los siguientes datos del mensaje del usuario y responde únicamente con un JSON valido:
    
    - budget: presupuesto del usuario (ejemplo: "20000 MXN" o "30 mil pesos", pero puede ser cualquier otra moneda)
    - total_size: tamaño requerido del espacio (ejemplo: "500 m2", extrae los valores, a veces pueden venir unidos)
    - real_estate_type: tipo de inmueble (ejemplo: "oficina", "local", "industrial", "terreno")
    - city: ciudad donde se busca el inmueble (ejemplo: "Ciudad de Mexico")
    
    Responde con un JSON valido, Si algun campo no se menciona, devuelve null en ese valor.
    
    Mensaje del usuario: "{user_input}"
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un extractor de datos profesional.",
                },
                {
                    "role": "system",
                    "content": "Solo puedes responder con el fin de obtener los campos, otra respuesta o conversacion no esta permitida",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        for field in REQUIRED_FIELDS:
            if parsed.get(field) is not None:
                session_data[field] = parsed[field]

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Respuesta invalida de OpenAI.")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"Error de OpenAI: {str(e)}")

    return session_data


@app.post("/chat", response_model=BotResponse)
def chat_with_ai(user_message: UserMessage):
    session_data = extract_fields(user_message.message, user_message.session_data)

    missing_fields = [field for field in REQUIRED_FIELDS if not session_data.get(field)]

    field_questions = {
        "budget": "¿Cual es tu presupuesto aproximado?",
        "total_size": "¿Que tamaño de espacio necesitas? (por ejemplo, 500 m2)",
        "real_estate_type": "¿Que tipo de inmueble estás buscando? (oficina, local, industrial, terreno)",
        "city": "¿En que ciudad estás buscando?",
    }

    if not missing_fields:
        summary = (
            f"Gracias por compartir toda la informacion.\n\n"
            f"Resumen de tu busqueda:\n"
            f"- Tipo de inmueble: {session_data['real_estate_type']}\n"
            f"- Ciudad: {session_data['city']}\n"
            f"- Tamaño: {session_data['total_size']}\n"
            f"- Presupuesto: {session_data['budget']}\n\n"
            f"Estoy consultando nuestra base de datos para encontrar los mejores inmuebles comerciales disponibles. En breve te mostrare las opciones mas adecuadas."
        )
        return BotResponse(response=summary, session_data=session_data)

    next_field = missing_fields[0]
    return BotResponse(
        response=field_questions[next_field],
        session_data=session_data,
    )
