import bs

client = bs.login("email", "password")


async def main(club_tag: str):
    club = await client.get_club(club_tag)  # Getting a club
    print(f"Club Name: {club.name}")
    print(f"Club tag: {club.tag}")
    print(f"Club description: {club.description}")
    print(f"Club trophies: {club.trophies}")
    print(club.members[0].name)
    vice_presidents = [i.name for i in club.members if i.role == 'vicePresident']
    print(*vice_presidents, sep=", ")

    club_members = await client.get_club_members(club_tag,
                                                 limit=10)  # limits the number of items returned from the API response
    for i in club_members:
        print(i.name, i.role, i.trophies, sep=" - ")


if __name__ == '__main__':
    client.loop.run_until_complete(main(club_tag="#2L2CJJRQV"))
