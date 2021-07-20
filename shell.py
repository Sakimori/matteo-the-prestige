import the_prestige, asyncio
from discord_emu import *

while True:
    first = input("Command: ")
    command = []
    while first != "":
        command.append(first)
        first = input(": ")

    command_string = ""
    for line in command:
        command_string += line + "\n"
    command_string = command_string[:-1]
    try:
        comm = next(c for c in the_prestige.commands if command_string.split(" ",1)[0].split("\n",1)[0].lower() == c.name)

        asyncio.run(comm.execute(Message(), command_string[len(comm.name):], []))

    except the_prestige.CommandError as ce:
        print(str(ce))
    except:
        pass