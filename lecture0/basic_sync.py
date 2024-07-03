import time

start_time = time.time()

def sync_task(name, delay):
    print(f"Task {name} started")
    time.sleep(delay)
    print(f"Task {name} completed. elapsed time: {time.time()-start_time}")

def main_sync():
    print("Starting synchronous tasks...")
    sync_task("A", 3)
    sync_task("B", 2)
    sync_task("C", 1)
    print("Synchronous tasks completed")

if __name__ == "__main__":
    main_sync()
