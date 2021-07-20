class User():
    id = 0
    name = "IBM 80"

class Channel():

    async def send(obj, text=None, embed=None):
        if text is not None:
            print(text)
        if embed is not None:
            print(embed)

class Message():
    author = User()
    channel = Channel()

class Client():
    pass