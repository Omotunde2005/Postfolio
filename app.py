from fastapi import FastAPI, Body, HTTPException, status, WebSocket, Depends, Header, Query, WebSocketException, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from schema import UpdateUserSchema, UpdateBoardSchema, AddBoardTheme, TokenSchema, RefreshTokenSchema
from functions import SocialMedia, UserAuth, Token
from datetime import timedelta, datetime, timezone
from models import User, Board
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from database import users_collection, boards_collection
import settings
import jwt
from urllib.parse import parse_qs


app = FastAPI(
    title="Postfolio",
)



#                                                                 MIDDLEWARE

origins = [
    "http://locahost:5500/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


#                                                                 CURRENT USER

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id = payload["sub"]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await users_collection.find_one({"_id": ObjectId(id)})
    
    if user:
        return User(**user)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    ) 


async def get_user_via_websockets(websocket: WebSocket):
    try:
        query_string = websocket.scope.get("query_string", "").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id = payload["sub"]
    except:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION
        )
    
    user = await users_collection.find_one({ "_id": ObjectId(id)})
    if user:
        return User(**user)
    
    print("incorrect payload")
    raise WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION   
    )



#                                                                    USERS

@app.get("/")
async def home():
    hashed_pass = UserAuth.get_hashed_password("emiloju")
    return {"message": f"Welcome to the home page, your pass is, {hashed_pass}"}
        

@app.post("/register/")
async def register_user(user: User = Body(...)):
    user_exists = await users_collection.find_one({"email": user.email})
    
    if user_exists:
        return JSONResponse(status_code=400, content={"message": "User already exists"})
    else:
        hashed_password = UserAuth.get_hashed_password(user.password)
        user.password = hashed_password
        new_user = await users_collection.insert_one(user.model_dump(by_alias=True, exclude=["id"]))
        created_user = await users_collection.find_one({"_id": new_user.inserted_id})
        response = {
            "message": "User added successfully",
            "user": User(**created_user).model_dump_json(by_alias=True)
        }
        return JSONResponse(status_code=201, content=response)


@app.post("/login/")
async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = form_data.username
    password = form_data.password
    user = await UserAuth.authenticate_user(users_collection, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ACCESS TOKEN
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES)
    access_token = Token.generate_access_token({"sub": user.id}, access_token_expires)
    
    # REFRESH TOKEN
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRES)
    refresh_token = Token.generate_access_token({"sub": user.id}, refresh_token_expires)

    token = TokenSchema(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")
    response = {
        "message": "Login successful",
        "token": token.dict()
    }

    return JSONResponse(status_code=200, content=response)


@app.post("/refresh-token/")
async def refresh_token(refresh_token: RefreshTokenSchema = Header(...)):
    try:
        payload = jwt.decode(refresh_token.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
        if payload["exp"] < datetime.now(timezone.utc).timestamp():
            return JSONResponse(status_code=401, content={"message": "Refresh token expired"})
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES)
        new_access_token = Token.generate_access_token({"sub": payload["sub"]}, access_token_expires)
        return JSONResponse(content={"access_token": new_access_token, "token_type": "bearer"}, status_code=200)
    
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@app.get("/user/")
async def get_user(current_user: User = Depends(get_current_user)):
    response = {
        "message": "User returned successfully",
        "user": current_user.model_dump_json(by_alias=True)
    }
    return JSONResponse(status_code=200, content=response)


@app.put("/update/user/")
async def update_user(update_data: UpdateUserSchema = Body(...), current_user: User = Depends(get_current_user)):
    if update_data.email is None:
        update_data.email = current_user.email

    if update_data.username is None:
        update_data.username = current_user.username

    update_data.last_updated = datetime.today()

    updated_user = await users_collection.find_one_and_update({"_id": ObjectId(current_user.id)}, {"$set": update_data.dict()}, return_document=ReturnDocument.AFTER)
    response = {
        "message": "User updated successfully.",
        "user": User(**updated_user).model_dump_json(by_alias=True)
    }
    return JSONResponse(status_code=200, content=response)


@app.delete("/delete/user/")
async def delete_user(current_user: User = Depends(get_current_user)): 
    await users_collection.delete_one({"_id": ObjectId(current_user.id)})
    
    response = {
        "message": "User deleted successfully"
    }
    
    return JSONResponse(content=response, status_code=201)


@app.delete("/delete/users/")
async def delete_users():
    await users_collection.delete_many({})
    return JSONResponse(status_code=200, content={"message": "All users have been deleted successfully."})



#                                                                 BOARDS



@app.get("/get/board/{board_id}/")
async def get_board_by_id(board_id: str, current_user: User = Depends(get_current_user)):
    board = await boards_collection.find_one({"_id": ObjectId(board_id)})

    if not board:
        return JSONResponse(status_code=404, content={"message": "Board does not exist"})
    
    if board_id not in current_user.boards:
        return JSONResponse(status_code=401, content={"message": "User is not authorized to access this board"})
    
    response = {
        "message": "Successful",
        "board": Board(**board).model_dump_json(by_alias=True)
    }

    return JSONResponse(status_code=200, content=response)


@app.get("/get/user/boards")
async def get_user_boards(current_user: User = Depends(get_current_user)):
    user_boards_ids = current_user.boards

    if len(user_boards_ids) == 0:
        user_boards = []

    else:
        user_boards = [Board(**await boards_collection.find_one({"_id": ObjectId(id)})).model_dump_json(by_alias=True) for id in user_boards_ids]

    response = {
        "message": "Successful",
        "boards": user_boards
    }
    #print(user_boards[0]['id'])

    return JSONResponse(status_code=200, content=response)


@app.post("/create/board/")
async def create_board(board: Board = Body(...), current_user: User = Depends(get_current_user)):
    board.user_Id = ObjectId(current_user.id)

    new_board = await boards_collection.insert_one(board.model_dump(by_alias=True, exclude=["id"])) 
    
    await users_collection.find_one_and_update({"_id": ObjectId(current_user.id)}, {"$push": {"boards": new_board.inserted_id}})
    created_board = await boards_collection.find_one({"_id": new_board.inserted_id}) 

    response = {
        "message": "Board created successfully",
        "board": Board(**created_board).model_dump_json(by_alias=True)
    }

    return JSONResponse(status_code=201, content=response)


@app.put("/update/board/{board_id}/")
async def update_board(board_id: str, board_data: UpdateBoardSchema = Body(...), current_user: User = Depends(get_current_user)):
    board = await boards_collection.find_one({"_id": ObjectId(board_id)})

    if not board:
        return JSONResponse(status_code=404, content={"message": "Board does not exist"})
    
    if board_id not in current_user.boards:
        return JSONResponse(status_code=401, content={"message": "User is not authorized to access this board"})
    
    board_data.last_updated = datetime.today()
    board_dict = {}

    for (key, value) in board_data.dict().items():
        if value is not None:
            board_dict[key] = value

    updated_board = await boards_collection.find_one_and_update({"_id": ObjectId(board_id)}, {"$set": board_dict}, return_document=ReturnDocument.AFTER)
    response = {
        "message": "Board updated successfully",
        "board": Board(**updated_board).model_dump_json(by_alias=True)
    }

    return JSONResponse(status_code=200, content=response)


@app.delete("/delete/board/{board_id}")
async def delete_board(board_id: str, current_user: User = Depends(get_current_user)):
    board = await boards_collection.find_one({"_id": ObjectId(board_id)})

    if not board:
        return JSONResponse(status_code=404, content={"message": "Board does not exist"})
    
    if board_id not in current_user.boards:
        return JSONResponse(status_code=401, content={"message": "User is not authorized to access this board"})
    
    await boards_collection.delete_one({"_id": ObjectId(board_id)})

    response = {
        "message": "User deleted successfully"
    }

    return JSONResponse(status_code=200, content=response)



@app.delete("/delete/boards/")
async def delete_boards():
    await boards_collection.delete_many({})
    return JSONResponse(status_code=200, content={"message": "All boards have been deleted successfully."})


#                                                                 BOARD POSTS

@app.websocket("/get/board/{id}")
async def get_board_by_id(websocket: WebSocket, id: str):
    await websocket.accept()
    num = 0
    for n in range(3):
        num += 1
    while True:
        print(num)
        new_post = await websocket.receive_json()
        await websocket.send_json({"message": "Post added successfully", "status": 200})


@app.websocket("/add/post/{board_id}/")
async def add_post(*, websocket: WebSocket, board_id: str, current_user: User = Depends(get_user_via_websockets)):
    await websocket.accept()
    while True:
        board_id = ObjectId(board_id)
        board = await boards_collection.find_one({"_id": board_id})  

        if not board:
            await websocket.send_json({"message": "Board does not exist", "status": 404})
            await websocket.close()

        if board_id not in current_user.boards:
            await websocket.send_json({"message": "User is not authorized to access this board", "status": 401})
            await websocket.close()

        new_post = await websocket.receive_json()
        await boards_collection.find_one_and_update(
            {"_id": board_id},
            {"$push": {"posts": new_post}}
        )
        await websocket.send_json({"message": "Post added successfully", "status": 200})
    



@app.websocket("/edit/post/{board_id}")
async def edit_post(websocket: WebSocket, board_id: str, current_user: User = Depends(get_user_via_websockets)):
    await websocket.accept()
    board_id = ObjectId(board_id)
    board = await boards_collection.find_one({"_id": board_id})    

    if not board:
        await websocket.send_json({"message": "Board does not exist", "status": 404})

    if board_id not in current_user.boards:
        await websocket.send_json({"message": "User is not authorized to access this board", "status": 401})
    
    try:
        while True:
            post_to_edit = await websocket.receive_json()
            await boards_collection.find_one_and_update(
                {"_id": board_id, "posts.id": post_to_edit["id"]},
                {"$set": {"posts.$.posts": post_to_edit["post"]}}
            )
            await websocket.send_json({"message": "Post edited successfully", "status": 200})
    
    except WebSocketDisconnect:
        await websocket.send_json({"message": "Websocket connection is closed", "status": 200})


@app.websocket("/delete/post/{board_id}")
async def delete_post(websocket: WebSocket, board_id: str, current_user: User = Depends(get_user_via_websockets)):
    await websocket.accept()
    board_id = ObjectId(board_id)

    board = await boards_collection.find_one({"_id": board_id})    
    if not board:
        await websocket.send_json({"message": "Board does not exist", "status": 404})
    
    if board_id not in current_user.boards:
        await websocket.send_json({"message": "Board does not exist", "status": 401})

    try:
        while True:
            post_to_delete = await websocket.receive_json()
            await boards_collection.update_one({"_id": board_id}, {"$pull": {"posts": {"id": post_to_delete["id"]}}})
            await websocket.send_json({"message": "Post deleted successfully", "status": 200})

    except WebSocketDisconnect:
        await websocket.send_json({"message": "Websocket connection is closed", "status": 200})



#                                                                 BOARD THEME


@app.put("/update/board/theme/{board_id}/")
async def add_board_theme(board_id: str, theme: AddBoardTheme = Body(...), current_user: User = Depends(get_current_user)):
    board = await boards_collection.find_one({"_id": ObjectId(board_id)})

    if not board:
        return JSONResponse(status_code=404, content={"message": "Board does not exist"})
    
    if board_id not in current_user.boards:
        return JSONResponse(status_code=401, content={"message": "User is not authorized to access this board"})
    
    updated_board = await boards_collection.find_one_and_update({"_id": ObjectId(board_id)}, {"theme": theme.dict()}, return_document=ReturnDocument.AFTER)

    response = {
        "message": "Theme updated successfully",
        "board": Board(**updated_board).model_dump_json(by_alias=True)
    }

    return JSONResponse(status_code=201, content=response)





#                                                                 PORTFOLIO


@app.get("/get/portfolio/{board_id}/")
async def get_portfolio(board_id: str):
    board_id = ObjectId(board_id)
    board = await boards_collection.find_one({"_id": board_id})

    if not board:
        return JSONResponse(status_code=404, content={"message": "Board does not exist"})

    response = {
        "message": "Successful",
        "board": Board(**board).model_dump_json(by_alias=True)
    }

    return JSONResponse(status_code=200, content=response)


















# @app.post(
#     "/students/",
#     response_description="Add new student",
#     response_model=StudentModel,
#     status_code=status.HTTP_201_CREATED,
#     response_model_by_alias=False,
# )
# async def create_student(student: StudentModel = Body(...)):
#     """
#     Insert a new student record.

#     A unique `id` will be created and provided in the response.
#     """
#     new_student = await student_collection.insert_one(
#         student.model_dump(by_alias=True, exclude=["id"])
#     )
#     created_student = await student_collection.find_one(
#         {"_id": new_student.inserted_id}
#     )
#     return created_student


# @app.get(
#     "/students/",
#     response_description="List all students",
#     response_model=StudentCollection,
#     response_model_by_alias=False,
# )
# async def list_students():
#     """
#     List all of the student data in the database.

#     The response is unpaginated and limited to 1000 results.
#     """
#     return StudentCollection(students=await student_collection.find().to_list(1000))


# @app.get(
#     "/students/{id}",
#     response_description="Get a single student",
#     response_model=StudentModel,
#     response_model_by_alias=False,
# )
# async def show_student(id: str):
#     """
#     Get the record for a specific student, looked up by `id`.
#     """
#     if (
#         student := await student_collection.find_one({"_id": ObjectId(id)})
#     ) is not None:
#         return student

#     raise HTTPException(status_code=404, detail=f"Student {id} not found")


# @app.put(
#     "/students/{id}",
#     response_description="Update a student",
#     response_model=StudentModel,
#     response_model_by_alias=False,
# )
# async def update_student(id: str, student: UpdateStudentModel = Body(...)):
#     """
#     Update individual fields of an existing student record.

#     Only the provided fields will be updated.
#     Any missing or `null` fields will be ignored.
#     """
#     student = {
#         k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
#     }

#     if len(student) >= 1:
#         update_result = await student_collection.find_one_and_update(
#             {"_id": ObjectId(id)},
#             {"$set": student},
#             return_document=ReturnDocument.AFTER,
#         )
#         if update_result is not None:
#             return update_result
#         else:
#             raise HTTPException(status_code=404, detail=f"Student {id} not found")

#     # The update is empty, but we should still return the matching document:
#     if (existing_student := await student_collection.find_one({"_id": id})) is not None:
#         return existing_student

#     raise HTTPException(status_code=404, detail=f"Student {id} not found")


# @app.delete("/students/{id}", response_description="Delete a student")
# async def delete_student(id: str):
#     """
#     Remove a single student record from the database.
#     """
#     delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

#     if delete_result.deleted_count == 1:
#         return Response(status_code=status.HTTP_204_NO_CONTENT)

#     raise HTTPException(status_code=404, detail=f"Student {id} not found")


