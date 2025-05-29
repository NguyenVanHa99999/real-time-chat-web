from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, Body, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import json

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

# API endpoints
@app.get("/")
async def root():
    return {"message": "Real-time Chat API is running"}

@app.post("/login")
async def login(username: str = Form(None), user_json: Dict = Body(None)):
    # Accept username from either form data or JSON body
    if username is None and user_json:
        username = user_json.get("username")
    
    # Debug log
    print(f"Login attempt with username: {username}, json body: {user_json}")
    
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
async def websocket_endpoint(websocket: WebSocket, username: str):
    # Check if valid user
    if username not in fake_users:
        await websocket.close(code=1008, reason="User not found")
        return
    
    # Check if user is already connected
    if username in active_connections:
        await websocket.close(code=1008, reason="User already connected")
        return
    
    # Accept connection
    await websocket.accept()
    active_connections[username] = websocket
    fake_users[username]["online"] = True
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            to_user = data.get("to")
            message = data.get("message")
            
            # Validate message format
            if not to_user or not message:
                await websocket.send_json({
                    "error": True,
                    "message": "Invalid message format. Required fields: 'to' and 'message'"
                })
                continue
            
            # Check if target user is connected
            if to_user not in active_connections:
                await websocket.send_json({
                    "error": True,
                    "message": f"User '{to_user}' is not online"
                })
                continue
            
            # Forward message to target user
            try:
                await active_connections[to_user].send_json({
                    "from": username,
                    "message": message
                })
            except Exception as e:
                await websocket.send_json({
                    "error": True,
                    "message": f"Failed to send message: {str(e)}"
                })
    
    except WebSocketDisconnect:
        # Remove connection and mark user as offline
        if username in active_connections:
            del active_connections[username]
        
        fake_users[username]["online"] = False
        print(f"Client {username} disconnected")
        
        # Broadcast to other users that this user went offline
        # This could be enhanced to notify specific users who were chatting with this user
        for connection in active_connections.values():
            try:
                await connection.send_json({
                    "system": True,
                    "message": f"User {username} has gone offline"
                })
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
