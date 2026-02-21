import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime, UTC
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import certifi, os

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
mongodb_url = os.getenv("MONGODB_URL")

import ssl, sys

import ssl, socket

print(sys.version)
print(ssl.OPENSSL_VERSION)
host = "ac-akstuqm-shard-00-00.603mlva.mongodb.net"

ctx = ssl.create_default_context()

with socket.create_connection((host, 27017), timeout=10) as s:
    with ctx.wrap_socket(s, server_hostname=host) as ss:
        print("TLS:", ss.version())
        print("Issuer:", ss.getpeercert()["issuer"])

client = MongoClient(mongodb_url)
# print(client.admin.command("ping"))
db = client["chatbot"]
collection = db["Users"]


app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    question: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# fitness  and Spiritual bot and tell me the answer with respect to the fitness things and Yoga sadhana",


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a diet specialist, give me the output accordingly in few sentence",
        ),
        ("placeholder", "{history}"),
        ("user", "{question}"),
    ]
)

llm = ChatGroq(api_key=groq_api_key, model="openai/gpt-oss-20b")
chain = prompt | llm
# response = chain.invoke({"question": "how to do push ups?"})
# print(response.content)


def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    history = []
    for chat in chats:
        history.append((chat["role"], chat["message"]))
    return history


@app.get("/")
def home():
    return {"message": "Welcome to the Diet Specialist Chatbot API!"}


@app.post("/chat")
def chat(request: ChatRequest):
    print(f"request.user_id {request.user_id}")
    print(f"response.content {request.question}")
    history = get_history(user_id=request.user_id)

    response = chain.invoke({"history": history, "question": request.question})

    collection.insert_one(
        {
            "user_id": request.user_id,
            "role": "user",
            "message": request.question,
            "timestamp": datetime.now(UTC),
        }
    )

    collection.insert_one(
        {
            "user_id": request.user_id,
            "role": "assistant",
            "message": response.content,
            "timestamp": datetime.now(UTC),
        }
    )
    return {"response": response.content}


"""
userid = input("Enter your user id : ")
while True:
    question = input("Ask a question : ")

    if question.lower() in ["exit", "quit"]:
        break

    history = get_history(user_id=userid)
    print(f"history - {history}")

    response = chain.invoke({"history": history, "question": question})
    print(response.content)
    collection.insert_one(
        {
            "user_id": userid,
            "role": "user",
            "message": question,
            "timestamp": datetime.now(UTC),
        }
    )

    collection.insert_one(
        {
            "user_id": userid,
            "role": "assistant",
            "message": response.content,
            "timestamp": datetime.now(UTC),
        }
    )
"""
