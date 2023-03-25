import typer
from fastapi import FastAPI
from config.database import create_metadata

app = FastAPI()

def main():
    typer.run(start_uvicorn)

def start_uvicorn(
        create_ddl: bool = typer.Option(False, "--create-ddl", "-c", help = "Drop and Create all tables. [default: False]"), 
        auto_reload: bool = typer.Option(False, "--auto-relod", "-r", help = "Define if the app will reload after each saving. [default: False]"),
        host: str = typer.Argument("127.0.0.1", help = "IP Address in which the server will be executed."),
        port: int = typer.Argument(8000, help = "Port in which the server will listen.")
    ):
    """
    Classify is a classifieds webapp built with FastAPI & SQLAlchemy.
    """
    import asyncio
    import platform
    import uvicorn
    from rich import print
    from tqdm import tqdm
    from time import sleep
    
    if create_ddl:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print('[bold red]Creating metadata...[/bold red]')
        
        for i in tqdm(range(0, 100), desc = 'Adding...'):
            sleep(0.03)
        asyncio.run(create_metadata())

        print('[bold green]Metadata created successfully![/bold green]')

    uvicorn.run(
        'main:app',
        host = host,
        port = port,
        reload = auto_reload
    )

if __name__ == '__main__':
    main()