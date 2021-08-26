import bs

client = bs.login("email", "pass")


async def main():
    shelly = await client.get_brawler(16000000)
    print(shelly)
    star_powers = [i.name for i in shelly.star_powers]
    gadgets = [i.name for i in shelly.gadgets]
    print(f"{star_powers = }")
    print(f"{gadgets = }")

    brawlers = await client.get_brawlers(limit=20)
    for i in brawlers:
        print(i.name, i.id)


if __name__ == '__main__':
    client.loop.run_until_complete(main())
