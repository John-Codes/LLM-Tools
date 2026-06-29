from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolRecord:
    package: str
    version: str | None = None

    @property
    def command(self) -> str:
        return self.package

    @property
    def requirement(self) -> str:
        return f"{self.package}=={self.version}" if self.version else self.package

    def to_dict(self) -> dict[str, str | None]:
        return {
            "package": self.package,
            "version": self.version,
            "command": self.command,
        }

