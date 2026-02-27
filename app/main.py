from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime

app = FastAPI(title="API biblioteca digital")
#modelo del libro
class Libro(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    autor: str
    año: int = Field(gt=1450, le=datetime.now().year)
    paginas: int = Field(gt=1)
    estado: Literal["disponible", "prestado"] = "disponible"

#Modelo usuario


class Usuario(BaseModel):
    nombre: str
    correo: EmailStr

app = FastAPI(title="API biblioteca digital")

libros = []
prestamos = []

#agregar libro

@app.post("/libros", status_code=status.HTTP_201_CREATED)
def registrar_libro(libro: Libro):
    for l in libros:
        if l["nombre"].lower() == libro.nombre.lower():
            raise HTTPException(
                status_code=400,
                detail="ya existe un libro con este nombre"
            )
    
    nuevo_libro = libro.dict()
    nuevo_libro["id"] = len(libros) +1 

    libros.append(nuevo_libro)
    return nuevo_libro


#ver lista (get)
@app.get("/libros", status_code=status.HTTP_200_OK)
def listar_libros():
    return libros

@app.get("/libros/buscar")
def buscar_libros(nombre:str):
    resultados = [
        libro for libro in libros
        if nombre.lower() in libro["nombre"].lower()
    ]

    if not resultados:
        raise HTTPException(
            status_code=400,
            detail="no hay libros con este nombre"
        )
    
    return resultados

#registrar prestar libro

@app.post("/prestamos", status_code=status.HTTP_201_CREATED)
def registrar_prestamo(id_libro: int, usuario: Usuario):
    
    libro_encontrado = None

    for libro in libros:
        if libro["id"] == id_libro:
            libro_encontrado = libro
            break
    
    if not libro_encontrado:
        raise HTTPException(
            status_code=404,
            detail="el libro no existe"
        )
    
    if libro_encontrado["estado"] == "prestado":
        raise HTTPException(
            status_code=400,
            detail="el libro ya esta prestado"
        )
    
    prestamo = {
        "id_prestamo": len(prestamos) +1,
        "id_libro": id_libro,
        "usuario": usuario.dict()
    }
    prestamos.append(prestamo)
    libro_encontrado["estado"] = "prestado"
    return prestamo    


#devolver el libro

@app.put("/prestamos/devolver")
def devolver_libro(id_prestamo: int):

    for prestamo in prestamos:
        if prestamo["id_prestamo"] == id_prestamo:

            for libro in libros:
                if libro["id"] == prestamo["id_libro"]:
                    libro["estado"] = "disponible"
                    break
            
            prestamos.remove(prestamo)
            return {"mensaje": "libro devuelto con exito"}
            
    raise HTTPException(
        status_code=404,
        detail="el prestamo no existe"
    )

#eliminar registro

@app.delete("/prestamos/{id_prestamo}", status_code=status.HTTP_200_OK)
def eliminar_prestamo(id_prestamo: int):

    for prestamo in prestamos:
        if prestamo["id_prestamo"] == id_prestamo:

            for libro in libros:
                if libro["id"] == prestamo["id_libro"]:
                    libro["estado"] = "disponible"
                    break
            
            prestamos.remove(prestamo)
            return {"mensaje": "prestamo eliminado con exito"}
            
    raise HTTPException(
        status_code=409,
        detail="el prestamo no existe"
    )