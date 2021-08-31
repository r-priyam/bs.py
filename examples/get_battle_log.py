import bs
from bs import TeamBattle, SoloBattle

client = bs.login("email", "password")


async def main(tag: str):
    logs = await client.get_player_battle_log(tag)

    # Listing all the 3v3 matches with it's star player
    print("--------------- 3v3 ---------------")
    for i in logs:
        if isinstance(i.battle, TeamBattle):
            print(
                f"Map - {i.map}, Mode - {i.battle.mode}, Result - {i.battle.result.capitalize()}, Star Player - {i.battle.star_player} ({i.battle.star_player.tag})"
            )

    # Listing all the solo matches with rank
    print("--------------- Solo ---------------")
    for i in logs:
        if isinstance(i.battle, SoloBattle):
            print(f"Map - {i.map}, Your Rank - #{i.battle.rank}, #1 Player - {i.battle.players[0]}")


if __name__ == "__main__":
    client.loop.run_until_complete(main(tag="#9P8YPU2RQ"))
