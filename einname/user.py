class User:
    def __init__(
        self,
        id: str,
        username: str,
        global_name: str | None,
        discriminator: str | None,
        verified: bool,
        bot: bool,
        avatar: str | None,
        mfa_enabled: bool
    ):
        self.id = id
        self.username = username
        self.global_name = global_name
        self.discriminator = discriminator
        self.verified = verified
        self.bot = bot
        self.avatar = avatar
        self.mfa_enabled = mfa_enabled

    @property
    def mention(self):
        return f"<@{self.id}>"
