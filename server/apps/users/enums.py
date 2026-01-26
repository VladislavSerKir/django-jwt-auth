from enum import IntEnum


class Role(IntEnum):
    ADMIN = 0
    USER = 1

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]

    @property
    def verbose_name(self) -> str:
        if self == Role.ADMIN:
            return 'ADMIN'
        elif self == Role.USER:
            return 'USER'
        else:
            print.warning('Unknown Role "%s"' % repr(self))
            return str(self)

    def __str__(self):
        return self.name
