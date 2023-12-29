# custom paramparser
from collections import defaultdict


class FuncWrapper:
    def __init__(self, fn, async_fn=False):
        self.fn = fn
        self.async_fn = async_fn


class BufoArgParser:
    def __init__(self, prefix="$bufo"):
        self.prefix = prefix
        self.cmd_name_id_map = {}  # cmd name/alias -> uuid mapping
        self.cmd_fn_map = {}  # cmd uuid -> fn mapping
        self.param_options = defaultdict(
            dict
        )  # cmd uuid -> param name -> param options
        self.env_param = defaultdict(list)  # cmd uuid -> env_param name

    def add_cmd(self, cmd_name, alias_for=None):
        if alias_for:
            if alias_for not in self.cmd_name_id_map:
                raise ValueError(f"Alias '{alias_for}' does not exist")
            self.cmd_name_id_map[cmd_name] = self.cmd_name_id_map[alias_for]
        else:
            self.cmd_name_id_map[cmd_name] = len(self.cmd_name_id_map)

    def add_param(self, cmd_name, param_name, type=str, required=False, default=None):
        self.param_options[self.cmd_name_id_map[cmd_name]][param_name] = {
            "type": type,
            "required": required,
            "default": default,
        }

    def add_env_param(self, cmd_name, env_param_name):
        # env params are required for a function to run but not passed in by user e.g., model
        self.env_param[self.cmd_name_id_map[cmd_name]].append(env_param_name)

    def map_cmd_to_fn(self, cmd_name, fn, async_fn=False):
        if cmd_name not in self.cmd_name_id_map:
            raise ValueError(f"Command '{cmd_name}' does not exist")
        self.cmd_fn_map[self.cmd_name_id_map[cmd_name]] = FuncWrapper(fn, async_fn)

    def get_env_params(self, cmd_name):
        if cmd_name not in self.cmd_name_id_map:
            raise ValueError(f"Command '{cmd_name}' does not exist")
        return self.env_param[self.cmd_name_id_map[cmd_name]]

    async def execute(self, cmd, params):
        # add default params
        for param_name, param_options in self.param_options[
            self.cmd_name_id_map[cmd]
        ].items():
            if param_name not in params:
                if param_options["required"]:
                    raise ValueError(f"Missing required parameter '{param_name}'")
                else:
                    params[param_name] = param_options["default"]
        if self.cmd_fn_map[self.cmd_name_id_map[cmd]].async_fn:
            return await self.cmd_fn_map[self.cmd_name_id_map[cmd]].fn(**params)
        return self.cmd_fn_map[self.cmd_name_id_map[cmd]].fn(**params)

    def parse_params(self, input_str):
        parts = input_str.split()

        if len(parts) < 2 or not parts[0].startswith(self.prefix):
            raise ValueError("Invalid input format")

        i = 1  # skip prefix
        while (i < len(parts)) and (not parts[i].startswith("--")):
            i += 1
        command = " ".join(parts[1:i])

        if command not in self.cmd_name_id_map:
            raise ValueError(f"Invalid command: {command}")

        params = {}

        while i < len(parts):
            if parts[i].startswith("--"):
                try:
                    param_name, param_value = parts[i][2:].split("=")
                except:
                    raise ValueError(f"Missing value for paramument '{parts[i][2:]}'")

                # cast param_value to specified type
                param_value = self.param_options[self.cmd_name_id_map[command]][
                    param_name
                ]["type"](param_value)
                params[param_name] = param_value

            else:
                raise ValueError(f"Invalid paramument format: {parts[i]}")

            i += 1

        return command, params


def main():
    # run tests
    parser = BufoparamParser()
    parser.add_cmd("connect")
    parser.add_cmd("disconnect")
    parser.add_cmd("go away", alias_for="disconnect")
    parser.add_cmd("train")
    parser.add_cmd("train gpt", alias_for="train")
    parser.add_cmd("train neural network", alias_for="train")
    parser.add_param("train", "epochs", type=int, required=False, default=7)
    parser.add_param("train", "batch-size", type=int, required=False, default=64)
    parser.add_param("train", "lr", type=float, required=False, default=0.001)

    # invalid input
    str1 = ""  # empty
    str2 = "$bufo"  # no command
    str3 = "bufo train"  # no prefix
    str4 = "bufo asdf"  # invalid command

    for test_str in [str1, str2, str3, str4]:
        try:
            parser.parse_params(test_str)
            assert False
        except ValueError:
            pass

    # valid input
    str4 = "$bufo connect"
    str5 = "$bufo go away"
    str6 = "$bufo train neural network --epochs=10 --batch-size=32 --lr=0.001"
    str7 = "$bufo train gpt --epochs=10 --batch-size=32 --lr=0.001"

    for test_str in [str4, str5, str6, str7]:
        try:
            parser.parse_params(test_str)
        except ValueError:
            assert False

    assert parser.parse_params(str4)[0] == "connect"
    assert parser.parse_params(str5)[0] == "go away"
    assert parser.parse_params(str6)[0] == "train neural network"
    assert parser.parse_params(str7)[0] == "train gpt"

    assert parser.parse_params(str4)[1] == {}
    assert parser.parse_params(str5)[1] == {}
    assert parser.parse_params(str6)[1] == {"epochs": 10, "batch-size": 32, "lr": 0.001}
    assert parser.parse_params(str7)[1] == {"epochs": 10, "batch-size": 32, "lr": 0.001}

    del parser
    # test function calling
    parser = BufoparamParser()
    parser.add_cmd("test")
    parser.add_param("test", "param1", type=int, required=True)
    parser.add_param("test", "param2", type=str, required=False, default="default")
    parser.add_param("test", "extra_param1", type=str, required=False)

    def test_fn(param1, param2, extra_param1):
        assert param1 == 1
        assert param2 == "2"
        assert extra_param1 == "sup3r_$ecr3t_p@ssw0rd"
        return "test passed"

    parser.map_cmd_to_fn("test", test_fn)

    try:
        parser.execute(*parser.parse_params("$bufo test --param1=1 --param2=2"))
        assert False
    except TypeError:
        pass

    assert (
        parser.execute(
            *parser.parse_params(
                "$bufo test --param1=1 --param2=2 --extra_param1=sup3r_$ecr3t_p@ssw0rd"
            )
        )
        == "test passed"
    )


if __name__ == "__main__":
    main()
