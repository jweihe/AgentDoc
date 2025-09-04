"""Web API模块"""

from .app import create_app
from .routes import router
from .models import *
from .dependencies import *

__all__ = [
    "create_app",
    "router",
]