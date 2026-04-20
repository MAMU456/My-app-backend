from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import auth, products , admin , vendors, orders , ratings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
"http://localhost:3000",
"https://app.netlify.com/projects/stupendous-praline-f80270"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(admin.router)
app.include_router(vendors.router) 
app.include_router(orders.router)
app.include_router(ratings.router)

@app.get("/")
def home():
    return {"message": "Distribution system backend running"}