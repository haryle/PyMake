from typing import Any, Literal

from pydantic import BaseModel

from PyMake.console.builder.cmd_builder import CmdModel
from PyMake.console.builder.env_builder import EnvModel
from PyMake.console.builder.var_builder import VarModel
from PyMake.decorators import validate_raise_exception
from PyMake.exceptions import PyMakeFormatError, UndefinedReference

Elements = Literal["env", "var", "cmd"]
TargetType = dict[Elements, Any]


@validate_raise_exception(PyMakeFormatError)
class Builder(BaseModel):
    data: TargetType
    var: VarModel = VarModel(data=None)
    env: EnvModel = EnvModel(data=None)
    cmd: CmdModel = CmdModel(data=None)

    def build(self):
        # Parse build recipe
        self.var = VarModel(data=self.data.get("var"))
        self.env = EnvModel(data=self.data.get("env"))
        self.cmd = CmdModel(data=self.data.get("cmd"))
        # Build
        self.var.build()
        self.env.build()
        self.cmd.build()
        # Validate reference
        self.validate_variables()

    def validate_reference(self, model: EnvModel | CmdModel, name: str) -> None:
        for reference in model.reference:
            if reference not in self.var.vars:
                raise UndefinedReference(
                    f"{name} has an undefined reference: {reference}"
                )

    def validate_variables(self):
        self.validate_reference(self.env, "env")
        self.validate_reference(self.cmd, "cmd")

    @property
    def positional(self) -> list[str]:
        return self.var.positional

    @property
    def default(self) -> dict[str, str]:
        return self.var.default

    @property
    def flag(self) -> dict[str, str]:
        return self.var.flag

    @property
    def required(self) -> list[str]:
        return self.var.required

    @property
    def vars(self) -> list[str]:
        return self.var.vars

    @property
    def envs(self) -> dict[str, str]:
        return self.env.envs

    @property
    def commands(self) -> list[str]:
        return self.cmd.commands


if __name__ == "__main__":
    import yaml

    data = """
    target:
        var:
            basic:
                var1: 10
                var2: 2
                var3: 14
            option: 
                all: "-all"
                quiet: "-quiet"
            sequence:
                list1: null
                list2: null
        env:
            env1: $(var1)
            env2: $(var2)
        cmd:
            - python script1.py
            - python script2.py 
    """

    data = yaml.safe_load(data)["target"]
    builder = Builder(data=data)
    builder.build()
    print(f"All Vars: {builder.vars}")
    print(f"Positional: {builder.positional}")
    print(f"Default: {builder.default}")
    print(f"Required: {builder.required}")
    print(f"Flag: {builder.flag}")
    print(f"Command: {builder.commands}")
    print(f"Envs: {builder.envs}")

    print("End")