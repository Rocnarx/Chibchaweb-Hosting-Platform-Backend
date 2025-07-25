from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Conexión a tu base MySQL en Railway
DATABASE_URL = "mysql+pymysql://root:XjCKpqjYLJZrNDiaLsSbjVZDIMRYtUMU@ballast.proxy.rlwy.net:38739/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@app.post("/insertar-perfiles")
def insertar_perfiles():
    datos = [
        'perfil_admin', 'perfil_user', 'perfil_anonimo', 'test_uno', 'test_dos',
        'test_tres', 'supervisor', 'invitado_temporal', 'pruebaA', 'pruebaB',
        'perfil_beta', 'alpha_user', 'guest_account', 'test_data1', 'test_data2',
        'usuario_activo', 'usuario_inactivo', 'editor_contenido', 'moderador'
    ]

    with engine.connect() as conn:
        for valor in datos:
            conn.execute(text("INSERT INTO test (TESTPERFIL) VALUES (:valor)"), {"valor": valor})
        conn.commit()

    return {"message": f"Se insertaron {len(datos)} perfiles correctamente"}


@app.get("/perfiles")
def obtener_perfiles():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT TESTPERFIL FROM test"))
        perfiles = [row[0] for row in result]
    return {"perfiles": perfiles}
