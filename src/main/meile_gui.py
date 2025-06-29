import main.main as Meile
import asyncio
from threading import Thread

def main():
    meilethread = Thread(target=Meile.app.run())
    meilethread.start()
    
if __name__ == "__main__":
    main()