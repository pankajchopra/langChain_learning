from typing import List, AsyncGenerator, NoReturn
from typing_extensions import Annotated
from typing import Optional, List
import json
import uuid
import re
from app.constants import BANKER_ADVISOR_PERSONA_FILE_PATH, FINANCIAL_ADVISOR_PERSONA_FILE_PATH
from app.persona.Persona import chatbot
from redact_PII import redact_PIIs
import os
from dotenv import load_dotenv
from bson import ObjectId
from app.features.slot_filling import SlotFill
from send_message_id import nl
from mongo_query import mongo_query_help_UId_True, mongo_query_help_UId_False, mongo_query_help_True_convid, mongo_query_help_False_convid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, Response, HTTPException, status
from datetime import datetime, timedelta
from pydantic import ConfigDict, BaseModel, Field, EmailStr
import motor.motor_asyncio
from pymongo import ReturnDocument
from crud_preferences.conf import conversation_feedbacks
from crud_preferences.crud.insert import add
from crud_preferences.crud.fetch import retrieve, retrieve_by_id
from crud_preferences.crud.update import patch_preference, update_preference
from crud_preferences.crud.delete import delete
from crud_preferences.crud.delete_user import delete_users
from crud_preferences.crud.get_conversations import fetch_conversations, fetch_conversations_by_user_id, all_comm
from crud_preferences.crud.update_caption import update_caption_field
from crud_preferences.crud.feedback_collections import add_response
from crud_preferences.models import Preference, PreferencePatch
from pymongo import errors
from app.agents.advisor_agent import init_agent
from app.agents import ChatArgs, ChatAudioArgs
from app.repositories.mongo.models.message import ChatMessageModel
from app.repositories.mongo.models.user import UserModel
from app.repositories.mongo.models.conversation import ConversationModel
from langsmith import Client
from app.chat.audio_utils.SpeechToText import audio_process
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from langchain_core.agents import AgentAction
from main_factory import model_factory
#use the model factory initialisation of chatopenai and load random model instance
model_instance = model_factory().create_model_instance('openai')
model_factory().get_parameter('openai parameter') #reading config must be made dynamic
model_instance.initialize(config_dict)
config_dict
client = Client()
from dotenv import load_dotenv
load_dotenv()
from logger import logger
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/get_user_personas")
def get_user_personas():
    print("get persona called")

    response_advisor = chatbot("Financial Advisor", "Billionaire Warren Buffett", True)
    print("Advisor response", response_advisor)

    response_banker = chatbot("Banker Advisor", "Billionaire Warren Buffett", True)
    print("Advisor response", response_banker)

    response_advisor.extend(response_banker)
    print("Response", response_advisor)

    return response_advisor

def patch_user_preferences(user_id, preference: PreferencePatch):
    """update user preferences

    Sample schema:

        {
            "user_persona": {
                "preferred_questions": [1],
                "personakey": "string",
                "personavalue": "string"
            }
        }
    """
    try:
        response = patch_preference(user_id, preference)
        if response:
            return status.HTTP_200_OK
        else:
            return status.HTTP_400_BAD_REQUEST
    except errors.WriteError as err:
        logger.error(err)
        #print("error: ", err)

def get_helpful_True_UId(user_id):
    res = mongo_query_help_UId_True(user_id)
    if res:
        return f"Total count as: ({res})"
    else:
        return f"User with user_id ({user_id}) does not exist"

def get_helpful_False_UId(user_id):
    res = mongo_query_help_UId_False(user_id)
    if res:
        return f"Total count as: ({res})"
    else:
        return f"User with user_id ({user_id}) does not exist"

def get_helpful_True_conversation_id(conversation_id):
    res = mongo_query_help_True_convid(conversation_id)
    return f"Total count as: ({res})"

def get_helpful_True_conversation(conversation_id):
    res = mongo_query_help_True_convid(conversation_id)
    return f"Total count as: ({res})"

@app.get('/conversation_id_helpful_false')
def get_helpful_False_conversation_id(conversation_id):
    res = mongo_query_help_False_convid(conversation_id)
    return f"Total count as: ({res})"

@app.get('/all_preferences')
def get_all_user_preferences():
    """ find all preferences of all users"""
    messages = retrieve()
    return messages

@app.get('/{user_id}')
def get_user_preference(user_id):
    """ find all preferences of a particular user_id"""
    messages = retrieve_by_id(user_id)
    return messages

@app.post('/create_preferences')
def create_preferences(user_id, preference: Preference):
    """create user preferences"""
    response = add(user_id, preference)
    if response:
        return status.HTTP_200_OK
    else:
        return status.HTTP_400_BAD_REQUEST

@app.put('/update_preferences')
def update_preferences(user_id, preference: Preference):
    """update user preferences"""
    try:
        response = update_preference(user_id, preference)
        if response:
            return status.HTTP_200_OK
        else:
            return status.HTTP_400_BAD_REQUEST
    except errors.WriteError as err:
        logger.error(err)
        #print("error: ", err)

@app.delete('/delete_user/{user_id}')
def delete_user(user_id):
    """delete user based on user_id"""
    response = delete_users(user_id)
    if response:
        return status.HTTP_200_OK
    else:
        return status.HTTP_400_BAD_REQUEST

@app.put('/update_caption')
def update_caption(conversation_id, rename_caption):
    """create custom caption or rename the caption"""
    try:
        response = update_caption_field(conversation_id, rename_caption)
        if response:
            return status.HTTP_200_OK
        else:
            return status.HTTP_400_BAD_REQUEST
    except errors.WriteError as err:
        print("error: ", err)

@app.delete("/delete_conversation/")
def delete_conversations(conversation_id):
    """delete conversation based on conversation_id"""
    response = delete(conversation_id)
    # print("response", response)
    if response:
        return status.HTTP_200_OK
    else:
        return status.HTTP_400_BAD_REQUEST


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


# Models
class Conversations(BaseModel):
    """
    This exists because providing a top-level array in a JSON response can be a [vulnerability].
    """
    conversations: List[ConversationModel]


manager = ConnectionManager()


@app.get("/")
async def get():
    logger.info("Server starting")
    return "Welcome Home"


@app.websocket("/ws/{sampleRate}/{channelCount}")  # To include the hyperparam encoding_type,audio_id
async def websocket_endpoint(websocket: WebSocket, sampleRate: int, channelCount: int):
    await manager.connect(websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    chataudio_args = ChatAudioArgs(
        sample_rate=sampleRate,
        channel_count=channelCount,
        jencoding=""
    )

    while True:
        try:
            audio_data = await websocket.receive()
            print(audio_data)
            # print("audio_bytes:", audio_data)
            print("RECEIVED THE AUDIO BYTES TO CONVERT TO TEXT")
            print("********")
            audio_stream = audio_data["bytes"]
            print("Type of audio_stream:", type(audio_stream))
            if isinstance(audio_stream, bytes):
                response = audio_process(audio_stream, chataudio_args)
                print("response", response)

            else:
                print("Received non-binary data")

            message = {
                "time": current_time,
                "message": response
            }

            # ml.clear()
            await websocket.send_text(json.dumps(message))

        except WebSocketDisconnect:
            manager.disconnect(websocket)
            message = {"time": current_time, "message": "Offline"}
            manager.broadcast(json.dumps(message))


# API which will read the json and return the persona to the UI. User can select this from frontend UI.
# get_persona() Parse the input persona json and send it to UI

@app.websocket("/ws/{client_id}/{user_id}/{conversation_id}/{conversation_caption}/{user_persona}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, user_id: str, conversation_id: str, conversation_caption: str, user_persona: str):
    await manager.connect(websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    chat_args = ChatArgs(
        client_id=str(client_id),
        user_id=user_id,
        user_persona=user_persona,
        conversation_id=conversation_id,
        conversation_caption=conversation_caption,
        metadata={
            "client_id": str(client_id),
            "user_id": "Sandeep",
            "conversation_id": "67e2e457e-43f1-4293-afdd-70bb7cdab185",
            "user_agent": "Chrome/51.0.2704.103",
            "user_persona": user_persona,
        }
    )
    agent_memory_mongo = init_agent(chat_args)
    try:
        while True:
            message = await websocket.receive_text()
            if (
                    message != "Connect"
                    and message
                    != "Hello there, I am your assistant. How can I help you today?"
            ):
                answer = None
                runnow = None
                current_trace_id = ""

                confi_uuid = "AgentExecutor-" + str(uuid.uuid4().hex)
                answer = agent.with_config({"run_name": confi_uuid}).invoke({"input": message})

                filter_string = "eq(name, \"" + confi_uuid + "\")"
                print("Filter string ", filter_string)
                response = answer["output"]

                try:
                    runnow = next(client.log_list_runs(project_name="default", api_key=os.getenv("LANGCHAIN_API_KEY"), filter=filter_string))
                    if runnow != None:
                        current_trace_id = runnow.trace_id
                except Exception as e:
                    pass

                response = redact_PIIs(response, None)
                slotfill = os.environ.get("slotfill")
                if "LLM could not extract entities" in response:
                    answer = agent.query({"input": message})
                    response = answer["output"]

                if "Missing fields" in response:
