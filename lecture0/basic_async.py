import asyncio
import time

start_time = time.time()

async def async_task(name, delay):
    print(f"Task {name} started")
    await asyncio.sleep(delay)
    print(f"Task {name} completed. elapsed time: {time.time()-start_time} seconds")

async def main_async():
    print("Starting asynchronous tasks...")
    await asyncio.gather(
        async_task("A", 3),
        async_task("B", 2),
        async_task("C", 1),
    )
    print("Asynchronous tasks completed")

if __name__ == "__main__":
    asyncio.run(main_async())
