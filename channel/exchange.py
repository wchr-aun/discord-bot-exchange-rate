from setup import INVALID_SETTING_MESSAGE


async def on_message(message, client, firebase_client):
    if message.author.id == client.user.id:
        return
    if not message.content.startswith("!rate"):
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return
    if len(message.content.split(" ")) == 1:
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return

    profile_id = message.author.id
    command = message.content.split(" ")[1]
    if command == "set" and len(message.content.split(" ")) == 3:
        rate = float(message.content.split(" ")[2])
        firebase_client.set_profile_rates(profile_id, rate)
        await message.channel.send(
            f"<@{profile_id}>'s rate notification is set to {rate} THB/GBP 💰"
        )
    elif command == "get":
        rate = firebase_client.get_profile_rates(profile_id)
        await message.channel.send(
            f"<@{profile_id}>'s rate notification is {rate} THB/GBP 💰"
        )
    else:
        await message.channel.send(INVALID_SETTING_MESSAGE)
