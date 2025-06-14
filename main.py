from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from auth import forgot_password, reset_password_form, reset_password_submit

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(forgot_password)
app.include_router(reset_password_form)
app.include_router(reset_password_submit)

# Create DB tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ❌ Remove this for Render
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
