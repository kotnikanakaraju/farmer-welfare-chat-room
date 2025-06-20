# farmer-welfare-chat-room


🌾 Real-Time Farmer Welfare Chat Room
This project is a real-time chat application designed to support farmer welfare and communication, integrating the power of FastAPI, MongoDB, Redis, AWS S3, and third-party APIs for agricultural insights.

🔧 Tech Stack
Backend: FastAPI (WebSocket + REST APIs)

Database: MongoDB (Farmer & message storage)

Cache/Realtime: Redis Pub/Sub

Storage: AWS S3 (for file/image uploads)

External APIs: Data.gov.in or other agricultural open APIs

🚀 Features
✅ Real-time chat with WebSocket
✅ Farmer welfare schema and registration
✅ Message persistence using MongoDB
✅ Redis Pub/Sub for live chat broadcasting
✅ File upload (images/docs) to AWS S3
✅ Fetch agricultural data from external APIs
✅ Sample Web UI for chatting

📁 Project Structure

farmer-chat-app/
├── main.py                # FastAPI server
├── requirements.txt       # Project dependencies
├── .env                   # AWS credentials and DB config
├── README.md              # Project documentation
└── static/                # Static HTML UI
🧪 Installation
1. Clone the Repository

git clone https://github.com/your-username/farmer-chat-app.git
cd farmer-chat-app
2. Install Dependencies

pip install -r requirements.txt
3. Configure Environment
Create a .env file and set:

env

AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
MONGO_URL=mongodb://localhost:27017
REDIS_HOST=localhost
REDIS_PORT=6379
S3_BUCKET_NAME=your-bucket-name
▶️ Run the App

uvicorn main:app --reload
Access Web UI: http://localhost:8000

🧪 Test Features
Go to / and open two tabs.

Enter a different username on each.

Start chatting in real time.

Upload files using /upload.

View farmer data at /get-farmers.

🌿 Sample Farmer Data

{
  "farmer_id": "F123",
  "name": "Ravi Kumar",
  "village": "Rampur",
  "crop_type": "Wheat",
  "subsidy_eligible": true
}
Use /add-farmer to POST this data.

🔗 External API Example

GET /external-agri-data
Fetches sample government agriculture data from public API.

