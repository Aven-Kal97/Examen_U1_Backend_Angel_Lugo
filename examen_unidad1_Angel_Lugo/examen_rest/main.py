from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import Base, SessionLocal, engine
from models import Laptop


app = FastAPI()


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


def laptop_a_dict(laptop: Laptop):
    return {
        "id": laptop.id,
        "marca": laptop.marca,
        "modelo": laptop.modelo,
        "ram_gb": laptop.ram_gb,
        "disponible": laptop.disponible
    }


def inicializar_base_de_datos():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        if db.query(Laptop).count() == 0:
            laptops_iniciales = [
                Laptop(
                    marca="Dell",
                    modelo="Latitude 5440",
                    ram_gb=16,
                    disponible=True
                ),
                Laptop(
                    marca="Lenovo",
                    modelo="ThinkPad E14",
                    ram_gb=8,
                    disponible=False
                ),
                Laptop(
                    marca="HP",
                    modelo="ProBook 450",
                    ram_gb=16,
                    disponible=True
                )
            ]

            db.add_all(laptops_iniciales)
            db.commit()

    finally:
        db.close()


inicializar_base_de_datos()


@app.get("/")
def inicio():
    return {
        "mensaje": "API del laboratorio de cómputo"
    }


@app.get("/laptops")
def obtener_laptops():
    db = SessionLocal()

    try:
        laptops = db.query(Laptop).order_by(Laptop.id).all()
        return [laptop_a_dict(laptop) for laptop in laptops]

    finally:
        db.close()


@app.get("/laptops/disponibles")
def obtener_laptops_disponibles():
    db = SessionLocal()

    try:
        laptops = (
            db.query(Laptop)
            .filter(Laptop.disponible == True)
            .order_by(Laptop.id)
            .all()
        )

        return [laptop_a_dict(laptop) for laptop in laptops]

    finally:
        db.close()


@app.get("/laptops/{laptop_id}")
def obtener_laptop(laptop_id: int):
    db = SessionLocal()

    try:
        laptop = (
            db.query(Laptop)
            .filter(Laptop.id == laptop_id)
            .first()
        )

        if laptop is None:
            raise HTTPException(
                status_code=404,
                detail="Laptop no encontrada"
            )

        return laptop_a_dict(laptop)

    finally:
        db.close()


@app.post("/laptops")
def crear_laptop(datos: LaptopCreate):
    db = SessionLocal()

    try:
        nueva_laptop = Laptop(
            marca=datos.marca,
            modelo=datos.modelo,
            ram_gb=datos.ram_gb,
            disponible=True
        )

        db.add(nueva_laptop)
        db.commit()
        db.refresh(nueva_laptop)

        return laptop_a_dict(nueva_laptop)

    finally:
        db.close()
