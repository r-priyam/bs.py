import bs

client = bs.login("email", "password")


async def main(tag: str):
    player = await client.get_player(tag)
    print(f"Player Name: {player.name}")


if __name__ == '__main__':
    client.loop.run_until_complete(main(tag="9P8YPU2RQ"))
