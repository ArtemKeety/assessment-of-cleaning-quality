from enum import StrEnum
from datetime import time
from dataclasses import dataclass, field

class Role(StrEnum):
    admin = 'admin'
    premium = 'premium'
    default = 'default'


@dataclass(slots=True, frozen=True, init=True)
class RateLimit:
    count: int = field(repr=True)
    times: time = field(repr=True)


@dataclass(frozen=True, slots=True, init=True)
class UserDomain:
    id: int = field(init=True)
    role: Role = field(init=True, default=Role.default)
    session: str = field(init=True, default="")

    @property
    def max_flat(self) -> int:
        match self.role:
            case self.role.premium:
                return 20
            case self.role.admin:
                return 1000
            case self.role.default:
                return 1
            case _:
                return 0

    @property
    def time_limit(self) -> RateLimit:
        match self.role:
            case self.role.premium:
                return RateLimit(count=3, times=time(minute=3))
            case self.role.admin:
                return RateLimit(count=100, times=time(minute=1))
            case self.role.default:
                return RateLimit(count=1, times=time(minute=3))
            case _:
                return RateLimit(count=10, times=time(minute=5))



def main():
    print(UserDomain(id=1, role=Role.premium).max_flat)
    print(UserDomain(id=1, role=Role.premium).time_limit)
    print(UserDomain(id=1, role=Role.admin).max_flat)
    print(UserDomain(id=1, role=Role.admin).time_limit)
    print(UserDomain(id=1, role=Role.default).max_flat)
    print(UserDomain(id=1, role=Role.default).time_limit)


if __name__ == '__main__':
    main()