import typer
from fastapi import (
    FastAPI,
    Request,
    responses,
    status
)
from fastapi_chameleon import global_init
from chameleon import PageTemplateFile
from fastapi.staticfiles import StaticFiles
from common.auth import (
    HTTPUnauthenticatedOnly, 
    HTTPUnauthorizedAccess,
    InvalidToken
)
from common.viewmodel import ViewModel
from config.database import create_metadata
from data.seed import seed_data
from middlewares.global_request import add_global_request
from middlewares.session import add_session_middleware

from views import(
    home,
    user,
    posts,
    auth,
    common,
    ad,
    auth_google,
    auth_microsoft
) 

app = FastAPI()

def main():
    config()
    typer.run(start_uvicorn)

async def seeding(ddl, dml) -> None:
    from rich import print
    from tqdm import tqdm
    from time import sleep

    if ddl:
        print('[bold red]Creating metadata...[/bold red]')
        
        for i in tqdm(range(0, 100), desc = 'CREATE', colour = '#0000FF'):
            sleep(0.03)
        await create_metadata()

        print('[bold green]Metadata created successfully![/bold green]')
        if dml:
            print('[bold red]Inserting initial data...[/bold red]')
            for i in tqdm(range(0, 100), desc = 'INSERT', colour = '#00FF00'):
                sleep(0.03)

            await seed_data()
            print('[bold red]Initial data inserted successfully...[/bold red]')

def start_uvicorn(
        create_ddl: bool = typer.Option(False, "--create-ddl", "-c", help = "Drop and Create all tables. [default: False]"),
        create_dml: bool = typer.Option(False, '--crete-dml', '-d', help = "Insert initil data into database."),
        auto_reload: bool = typer.Option(False, "--auto-reload", "-r", help = "Define if the app will reload after each saving. [default: False]"),
        host: str = typer.Argument("127.0.0.1", help = "IP Address in which the server will be executed."),
        port: int = typer.Option(8000, "--port", "-p", help = "Port in which the server will listen.")
    ):
    """
    Classify is a classifieds webapp built with FastAPI & SQLAlchemy.
    """
    import uvicorn
    import asyncio
    import platform
    
    if create_ddl:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(seeding(create_ddl, create_dml))

    uvicorn.run(
        'main:app',
        host = host,
        port = port,
        reload = auto_reload,
        reload_includes=[
            '*.pt',
            '*.css',
        ]
    )

def config():
    config_middlewares()
    config_routes()
    config_exception_handlers()
    config_templates()

def config_templates():
    global_init('templates')

def config_routes():
    app.mount('/public', StaticFiles(directory='public'), name='static')
    for view in [home, user, auth, auth_google, auth_microsoft, ad, posts, common]:
        app.include_router(view.router)

def config_middlewares():
    add_global_request(app)
    add_session_middleware(app)

def config_exception_handlers():
    async def unauthorized_access_handler(*_, **__):
        template = PageTemplateFile('./templates/errors/error-404.pt')
        vm = await ViewModel()
        content = template(**vm)
        return responses.HTMLResponse(content, status_code = status.HTTP_404_NOT_FOUND)
    
    async def internal_server_error_handler(*_, **__):
        template = PageTemplateFile('./templates/errors/error-500.pt')
        vm = await ViewModel()
        content = template(**vm)
        return responses.HTMLResponse(content, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def invalid_token_handler(request: Request, exception: InvalidToken):
        template = PageTemplateFile('./templates/errors/invalid-token.pt')
        vm = await ViewModel()
        vm.user_id = exception.user_id
        content = template(**vm)
        return responses.HTMLResponse(content, status_code = status.HTTP_400_BAD_REQUEST)
    
    async def unauthenticated_only_area_handler(*_, **__):
        return responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    
    app.add_exception_handler(HTTPUnauthorizedAccess, unauthorized_access_handler)
    app.add_exception_handler(status.HTTP_404_NOT_FOUND, unauthorized_access_handler)
    app.add_exception_handler(HTTPUnauthenticatedOnly, unauthenticated_only_area_handler)
    app.add_exception_handler(InvalidToken, invalid_token_handler)
    app.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, internal_server_error_handler)

if __name__ == '__main__':
    main()
else:
    config()