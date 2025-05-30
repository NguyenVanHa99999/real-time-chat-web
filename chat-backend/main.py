from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, Body, Query, Depends, Path, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import json
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Global dictionaries to track users and connections
fake_users = {
    "admin": {"online": False},
    "linh": {"online": False},
    "ha": {"online": False},
    "minh": {"online": False}
}

active_connections: Dict[str, WebSocket] = {}

# Lớp quản lý kết nối WebSocket
class ConnectionManager:
    def __init__(self):
        # Danh sách kết nối hoạt động
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # Chấp nhận kết nối WebSocket
        await websocket.accept()
        # Thêm kết nối vào danh sách hoạt động
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # Xóa kết nối khỏi danh sách hoạt động
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Gửi tin nhắn đến tất cả kết nối
        for connection in self.active_connections:
            await connection.send_text(message)
            
    async def broadcast_others(self, message: str, current_websocket: WebSocket):
        # Send message to all connections except the sender
        for connection in self.active_connections:
            if connection != current_websocket:
                await connection.send_text(message)

# Khởi tạo trình quản lý kết nối
manager = ConnectionManager()

# API endpoints
@app.get("/")
async def root():
    return {"message": "Real-time Chat API is running"}

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(None), 
    user_json: Dict = Body(None),
    user_agent: str = Header(None)
):
    # Accept username from either form data or JSON body
    if username is None and user_json:
        username = user_json.get("username")
    
    # Debug log
    print(f"Login attempt with username: {username}, json body: {user_json}")
    print(f"User agent: {user_agent}")
    
    if not username:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Username is required"}
        )
    
    # Check if admin and not Mac device
    if username == "admin":
        # Check if the device is a Mac by looking at the User-Agent header
        is_mac = user_agent and ("Mac" in user_agent or "Macintosh" in user_agent)
        if not is_mac:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "Admin account can only be accessed from Mac devices"}
            )
    
    if username not in fake_users:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"User '{username}' not found"}
        )
    
    # Set user status to online
    fake_users[username]["online"] = True
    
    return {
        "success": True,
        "message": f"User '{username}' logged in successfully",
        "user": {
            "username": username,
            "online": fake_users[username]["online"]
        }
    }

@app.post("/logout")
async def logout(username: str = Form(None), user_json: Dict = Body(None)):
    # Accept username from either form data or JSON body
    if username is None and user_json:
        username = user_json.get("username")
    
    if not username:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Username is required"}
        )
    
    if username not in fake_users:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"User '{username}' not found"}
        )
    
    # Set user status to offline
    fake_users[username]["online"] = False
    
    # Close WebSocket connection if exists
    if username in active_connections:
        await active_connections[username].close(code=1000, reason="Logged out")
        del active_connections[username]
    
    return {
        "success": True,
        "message": f"User '{username}' logged out successfully"
    }

@app.get("/users")
async def get_online_users(exclude: Optional[str] = Query(None)):
    online_users = []
    for username, data in fake_users.items():
        if data["online"] and username != exclude:
            online_users.append(username)
    
    return {"users": online_users}

# WebSocket connection handling
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str = Path(...)):
    # Store the connection with the username
    active_connections[username] = websocket
    # Update user status
    if username in fake_users:
        fake_users[username]["online"] = True
    
    # Connect to WebSocket
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            # Parse JSON message
            message_data = json.loads(data)
            # Broadcast message to others only, not back to sender
            await manager.broadcast_others(json.dumps(message_data), websocket)
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket)
        # Remove from active connections
        if username in active_connections:
            del active_connections[username]
        # Update user status
        if username in fake_users:
            fake_users[username]["online"] = False
        # Notify other clients
        await manager.broadcast(json.dumps({"sender": "System", "message": f"User {username} has disconnected"}))

# Keep the original endpoint for backward compatibility
@app.websocket("/ws")
async def legacy_websocket_endpoint(websocket: WebSocket):
    # Connect to WebSocket
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            # Parse JSON message
            message_data = json.loads(data)
            # Broadcast message to others only, not back to sender
            await manager.broadcast_others(json.dumps(message_data), websocket)
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket)
        # Notify other clients
        await manager.broadcast(json.dumps({"sender": "System", "message": "A user has disconnected"}))

if __name__ == "__main__":
    # Chạy server với Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
