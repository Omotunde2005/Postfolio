SECRET_KEY = "tegrrte5cghuf77jvjfe9030ki9827yr67ufji8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 50
REFRESH_TOKEN_EXPIRES = 7


# async def get_user_via_websockets(websocket: WebSocket, token: Annotated[str | None, Query()] = None):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         id = payload["sub"]
#     except:
#         print("incorrect payload")
#         raise WebSocketException(
#             code=status.WS_1008_POLICY_VIOLATION
#         )
    
#     user = await users_collection.find_one({ "_id": ObjectId(id)})
#     if user:
#         return User(**user)
    
#     print("incorrect payload")
#     raise WebSocketException(
#         code=status.WS_1008_POLICY_VIOLATION   
#     )
