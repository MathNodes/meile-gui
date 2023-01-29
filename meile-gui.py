import src.main.main as Meile
from threading import Thread

def main():
    print("Running Meile...")
    meilethread = Thread(target=Meile.app.run())
    meilethread.start()
    
if __name__ == "__main__":
    main()