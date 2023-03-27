import typer
from fastapi import FastAPI
from config.database import create_metadata
from data.seed import seed_data

app = FastAPI()

def main():
    typer.run(start_uvicorn)

def start_uvicorn(
        host: str = typer.Argument("127.0.0.1", help = "IP Address in which the server will be executed."),
        auto_reload: bool = typer.Option(False, "--auto-reload", "-r", help = "Define if the app will reload after each saving. [default: False]"),
        port: int = typer.Option(8000, "--port", "-p", help = "Port in which the server will listen."),
        create_ddl: bool = typer.Option(False, "--create-ddl", "-c", help = "Drop and Create all tables. [default: False]"),
        seed: bool = typer.Option(False, "--create-dml", "-d", help = "Insert dummy data into database. [default: False]")
    ):
    """
    Classify is a classifieds webapp built with FastAPI & SQLAlchemy.
    """
    import uvicorn
    from rich import print
    from tqdm import tqdm
    from time import sleep
    
    if create_ddl:
        print('[bold red]Creating metadata...[/bold red]')
        for i in tqdm(range(0, 100), desc = 'CREATE', colour = '#FF0000'):
            sleep(0.03)
        create_metadata()
        print('[bold green]Metadata created successfully![/bold green]')
        if seed:
            print('[bold red]Inserting initial data...[/bold red]')
            for i in tqdm(range(0, 100), desc = 'INSERT', colour = '#00FF00'):
                sleep(0.03)
            seed_data()
            print('[bold green]Data inserted successfully![/bold green]')



    uvicorn.run(
        'main:app',
        host = host,
        port = port,
        reload = auto_reload
    )

if __name__ == '__main__':
    main()