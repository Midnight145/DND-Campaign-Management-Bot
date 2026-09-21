class FakeMember:
    def __init__(self, fake_id):
        self.id = fake_id
        self.roles = []
        self.mention = str(fake_id) + " FakeMember"
        self.display_name = str(fake_id) + " FakeMember"

    async def remove_roles(self, *roles):
        return

    async def add_roles(self, *roles):
        return

    async def send(self, *args, **kwargs):
        return
