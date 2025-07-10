from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import user, product, update_log, auth, chatbot
import gradio as gr
from app.gradio_ui import gradio_app
from app.api import product, chatbot

app = FastAPI(
    title="E-Commerce Backend API",
    description="FastAPI backend for e-commerce platform with RAG and chatbot support",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI(title="Minimal E-Commerce RAG Chatbot")

app.include_router(product.router, prefix="/api/products", tags=["products"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(user.router, prefix="/api", tags=["users"])
# app.include_router(product.router, prefix="/api", tags=["products"])
app.include_router(update_log.router, prefix="/api", tags=["update_logs"])
# app.include_router(chatbot.router, prefix="/api", tags=["chatbot"])

app = gr.mount_gradio_app(app, gradio_app, path="/gradio")

@app.get("/")
def root():
    return {"message": "E-Commerce Backend API is running!"}
