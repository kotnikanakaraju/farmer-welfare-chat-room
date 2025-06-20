# Real-time Farmer Welfare Chat Room using FastAPI, MongoDB, Redis, AWS S3

# Requirements:
# - FastAPI + WebSocket
# - MongoDB (messages, users, farmer schema)
# - Redis (for pub/sub + caching)
# - AWS S3 (file upload)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
import boto3
import uuid
import os
import json

app = FastAPI()

# MongoDB setup
MONGO_URL = "mongodb://localhost:27017"
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.farmer_chat

# Redis setup
redis = Redis(host='localhost', port=6379, decode_responses=True)

# AWS S3 setup
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-1'
)
BUCKET_NAME = "your-bucket-name"

# In-memory connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_personal_message(self, message: str, username: str):
        websocket = self.active_connections.get(username)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for conn in self.active_connections.values():
            await conn.send_text(message)

manager = ConnectionManager()

# Farmer schema sample insertion
@app.post("/add-farmer")
async def add_farmer(data: dict):
    return await db.farmers.insert_one(data)

@app.get("/get-farmers")
async def get_farmers():
    return await db.farmers.find().to_list(100)

# Chat WebSocket
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            # Save message in MongoDB
            await db.messages.insert_one({"user": username, "message": data})
            # Publish to Redis
            await redis.publish("chat", json.dumps({"user": username, "message": data}))
            await manager.broadcast(f"{username}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(username)

# Redis pub/sub listener
import asyncio

async def redis_listener():
    pubsub = redis.pubsub()
    await pubsub.subscribe("chat")
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            await manager.broadcast(f"{data['user']}: {data['message']}")

@app.on_event("startup")
async def startup():
    asyncio.create_task(redis_listener())

# File upload to S3
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_key = f"uploads/{uuid.uuid4().hex}_{file.filename}"
    s3.upload_fileobj(file.file, BUCKET_NAME, file_key)
    return {"url": f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_key}"}

# Third-party API example (agriculture data)
import httpx
@app.get("/external-agri-data")
async def get_agri_data():
    url = "https://data.gov.in/node/356921/datastore/export/json"  # Replace with valid agri API
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Sample HTML to test WebSocket
@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <body>
            <h1>Farmer Chat Room</h1>
            <input id="username" placeholder="Enter username">
            <button onclick="connect()">Connect</button>
            <ul id="messages"></ul>
            <input id="message" placeholder="Type a message">
            <button onclick="sendMessage()">Send</button>
            <script>
                let ws;
                function connect() {
                    const username = document.getElementById('username').value;
                    ws = new WebSocket(`ws://localhost:8000/ws/${username}`);
                    ws.onmessage = (event) => {
                        const msg = document.createElement('li');
                        msg.innerText = event.data;
                        document.getElementById('messages').appendChild(msg);
                    };
                }
                function sendMessage() {
                    const message = document.getElementById('message').value;
                    ws.send(message);
                }
            </script>
        </body>
    </html>
    """)
