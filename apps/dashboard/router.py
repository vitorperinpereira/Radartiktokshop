"""Dashboard router for displaying the web app."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="apps/dashboard/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request) -> HTMLResponse:
    """Render the main weekly radar dashboard."""
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@router.get("/laboratorio", response_class=HTMLResponse)
async def content_ideas(request: Request) -> HTMLResponse:
    """Render the content ideas dashboard."""
    return templates.TemplateResponse(request=request, name="content_ideas.html", context={})


@router.get("/garagem", response_class=HTMLResponse)
async def saved_products(request: Request) -> HTMLResponse:
    """Render the saved products dashboard."""
    return templates.TemplateResponse(request=request, name="saved_products.html", context={})


@router.get("/raio-x", response_class=HTMLResponse)
async def product_detail(request: Request) -> HTMLResponse:
    """Render the product detail dashboard."""
    return templates.TemplateResponse(request=request, name="product_detail.html", context={})
