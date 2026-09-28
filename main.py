from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_token, get_current_user, hash_password, verify_password

app = FastAPI(
    title="Actividad de Entrega JWT — Alessandro",
    description="API RESTful con autenticación JWT y roles para Lenguajes de Programación.",
    version="1.0.0"
)

# Base de datos en memoria personalizada
fake_users_db = {
    "zazinha": {
        "username": "zazinha",
        "hashed_password": hash_password("code123"), # Estudiante
        "rol": "estudiante"
    },
    "sudo_profe": {
        "username": "sudo_profe",
        "hashed_password": hash_password("sudo123"), # Admin
        "rol": "admin"
    }
}

@app.post("/login", tags=["Autenticación"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint para autenticarse y obtener el JWT."""
    user_dict = fake_users_db.get(form_data.username)
    
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_token(
        data={"sub": user_dict["username"], "rol": user_dict["rol"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/publico", tags=["Endpoints"])
async def endpoint_publico():
    """Cualquiera puede acceder aquí sin estar logueado."""
    return {"mensaje": "Este es un endpoint público. No requiere JWT."}

@app.get("/privado", tags=["Endpoints"])
async def endpoint_privado(current_user: dict = Depends(get_current_user)):
    """Solo usuarios con un JWT válido (cualquier rol) pueden acceder."""
    return {"mensaje": f"Hola {current_user['username']}, tienes acceso porque estás autenticado."}

@app.get("/admin", tags=["Endpoints"])
async def endpoint_admin(current_user: dict = Depends(get_current_user)):
    """Solo usuarios autenticados con rol de administrador pueden acceder."""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere rol de administrador."
        )
    return {"mensaje": f"Bienvenido {current_user['username']}, tienes acceso de administrador."}