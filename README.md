# MongoDB with FastAPI

This is a backend API project built with [MongoDB](https://developer.mongodb.com/) and [FastAPI](https://fastapi.tiangolo.com/). It uses websockets in the backend to ensure real-time updates.


This project is a Saas application that allows users to create a public board, add social media posts to it, and share it as a portfolio.

## Key features
1. Authentication and session management: JWT is used to handle authentication within this API. User sessions is managed through a short-lived access-token and a long-lived refresh-token

2. Boards: Users can create, edit and delete boards. They can select a title and other metadata for a board.
3. Posts: Users can also add social media posts on their board through each post's embed code. Using websockets, users' posts can be saved and updated in real time without refreshing the page.