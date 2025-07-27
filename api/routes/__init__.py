from fastapi import APIRouter
from .carrito import router as carrito_router
from .dominios import router as dominios_router
from .perfiles import router as perfiles_router
from .tarjeta import router as tarjeta_router
from .pagos import router as pagos_router
from .landing import router as landing_router
router = APIRouter()
router.include_router(carrito_router)
router.include_router(dominios_router)
router.include_router(perfiles_router)
router.include_router(tarjeta_router)
router.include_router(pagos_router)
router.include_router(landing_router)