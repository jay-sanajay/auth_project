from fastapi import APIRouter, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from schemas import UserCreate, UserOut, ForgotPasswordRequest
from utils import hash_password, verify_password, create_reset_token, verify_reset_token
from email_utils import send_reset_email

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email, hashed_password=hash_password(user.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful", "user_id": user.id}

@router.post("/request-password-reset")
async def request_password_reset(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    token = create_reset_token(user.email)
    await send_reset_email(user.email, token)
    return {"message": "Password reset email sent"}

@router.get("/reset-password", response_class=HTMLResponse)
async def show_reset_form(token: str = Query(...)):
    email = verify_reset_token(token)
    if not token or not email:
        return HTMLResponse(content="<h3>Invalid or expired token.</h3>", status_code=400)

    return f"""
    <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    width: 350px;
                }}
                h2 {{
                    margin-bottom: 20px;
                    text-align: center;
                }}
                input {{
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                button {{
                    width: 100%;
                    padding: 10px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #0056b3;
                }}
                .error {{
                    color: red;
                    font-size: 14px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Reset Your Password</h2>
                <form id="resetForm" method="POST" action="/reset-password">
                    <input type="hidden" name="token" value="{token}" />
                    <label for="new_password">New Password:</label>
                    <input type="password" id="new_password" name="new_password" required />
                    <div id="error" class="error"></div>
                    <button type="submit">Reset Password</button>
                </form>
            </div>

            <script>
                const form = document.getElementById("resetForm");
                const passwordInput = document.getElementById("new_password");
                const errorDiv = document.getElementById("error");

                form.addEventListener("submit", function (event) {{
                    const password = passwordInput.value;
                    if (password.length < 6) {{
                        event.preventDefault();
                        errorDiv.textContent = "Password must be at least 6 characters.";
                    }}
                }});
            </script>
        </body>
    </html>
    """

@router.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    await db.commit()
    return {"message": "Password has been reset successfully"}
