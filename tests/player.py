import bs

client = bs.login("email", "password")


async def main(tag: str):
    player = await client.get_player(tag)
    print(f"Player's Name: {player.name}")
    print(f"Player's tag: {player.tag}")
    print(f"Player's exp_level: {player.exp_level}")
    print(f"Player's Club: {player.club_name}")
    print(f"Player's Club tag: {player.club_tag}")


if __name__ == '__main__':
    client.loop.run_until_complete(main(tag="#9P8YPU2RQ"))
