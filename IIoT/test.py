import asyncio
from asyncio_mqtt import Client

async def main():
    async with Client("localhost") as client:
        await client.publish("test/topic", "test message")
    print("Published successfully")

asyncio.run(main())
