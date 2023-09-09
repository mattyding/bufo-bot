# custom argparser
from collections import defaultdict


class BufoArgParser:
    def __init__(self, prefix="$bufo"):
        self.prefix = prefix
        self.cmd_name_id_map = {}  # cmd name/alias -> uuid mapping
        self.cmd_fn_map = {}  # cmd uuid -> fn mapping
        self.arg_options = defaultdict(dict)  # cmd uuid -> arg name -> arg options

    def add_cmd(self, cmd_name, alias_for=None):
        if alias_for:
            if alias_for not in self.cmd_name_id_map:
                raise ValueError(f"Alias '{alias_for}' does not exist")
            self.cmd_name_id_map[cmd_name] = self.cmd_name_id_map[alias_for]
        else:
            self.cmd_name_id_map[cmd_name] = len(self.cmd_name_id_map)

    def add_arg(self, cmd_name, arg_name, type=str, required=False, default=None):
        self.arg_options[self.cmd_name_id_map[cmd_name]][arg_name] = {
            "type": type,
            "required": required,
            "default": default,
        }

    def map_cmd_to_fn(self, cmd_name, fn):
        if cmd_name not in self.cmd_name_id_map:
            raise ValueError(f"Command '{cmd_name}' does not exist")
        self.cmd_fn_map[self.cmd_name_id_map[cmd_name]] = fn

    def execute(self, cmd, args):
        # add default args
        for arg_name, arg_options in self.arg_options[
            self.cmd_name_id_map[cmd]
        ].items():
            if arg_name not in args:
                if arg_options["required"]:
                    raise ValueError(f"Missing required argument '{arg_name}'")
                else:
                    args[arg_name] = arg_options["default"]
        return self.cmd_fn_map[self.cmd_name_id_map[cmd]](**args)

    def parse_args(self, input_str):
        parts = input_str.split()

        if len(parts) < 2 or not parts[0].startswith(self.prefix):
            raise ValueError("Invalid input format")

        i = 1  # skip prefix
        while (i < len(parts)) and (not parts[i].startswith("--")):
            i += 1
        command = " ".join(parts[1:i])

        if command not in self.cmd_name_id_map:
            raise ValueError(f"Invalid command: {command}")

        args = {}

        while i < len(parts):
            if parts[i].startswith("--"):
                try:
                    arg_name, arg_value = parts[i][2:].split("=")
                except:
                    raise ValueError(f"Missing value for argument '{parts[i][2:]}'")

                # cast arg_value to specified type
                arg_value = self.arg_options[self.cmd_name_id_map[command]][arg_name][
                    "type"
                ](arg_value)
                args[arg_name] = arg_value

            else:
                raise ValueError(f"Invalid argument format: {parts[i]}")

            i += 1

        return command, args


def main():
    # run tests
    parser = BufoArgParser()
    parser.add_cmd("connect")
    parser.add_cmd("disconnect")
    parser.add_cmd("go away", alias_for="disconnect")
    parser.add_cmd("train")
    parser.add_cmd("train gpt", alias_for="train")
    parser.add_cmd("train neural network", alias_for="train")
    parser.add_arg("train", "epochs", type=int, required=False, default=7)
    parser.add_arg("train", "batch-size", type=int, required=False, default=64)
    parser.add_arg("train", "lr", type=float, required=False, default=0.001)

    # invalid input
    str1 = ""  # empty
    str2 = "$bufo"  # no command
    str3 = "bufo train"  # no prefix
    str4 = "bufo asdf"  # invalid command

    for test_str in [str1, str2, str3, str4]:
        try:
            parser.parse_args(test_str)
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
            parser.parse_args(test_str)
        except ValueError:
            assert False

    assert parser.parse_args(str4)[0] == "connect"
    assert parser.parse_args(str5)[0] == "go away"
    assert parser.parse_args(str6)[0] == "train neural network"
    assert parser.parse_args(str7)[0] == "train gpt"

    assert parser.parse_args(str4)[1] == {}
    assert parser.parse_args(str5)[1] == {}
    assert parser.parse_args(str6)[1] == {"epochs": 10, "batch-size": 32, "lr": 0.001}
    assert parser.parse_args(str7)[1] == {"epochs": 10, "batch-size": 32, "lr": 0.001}

    del parser
    # test function calling
    parser = BufoArgParser()
    parser.add_cmd("test")
    parser.add_arg("test", "arg1", type=int, required=True)
    parser.add_arg("test", "arg2", type=str, required=False, default="default")
    parser.add_arg("test", "extra_arg1", type=str, required=False)

    def test_fn(arg1, arg2, extra_arg1):
        assert arg1 == 1
        assert arg2 == "2"
        assert extra_arg1 == "sup3r_$ecr3t_p@ssw0rd"
        return "test passed"

    parser.map_cmd_to_fn("test", test_fn)

    try:
        parser.execute(*parser.parse_args("$bufo test --arg1=1 --arg2=2"))
        assert False
    except TypeError:
        pass

    assert (
        parser.execute(
            *parser.parse_args(
                "$bufo test --arg1=1 --arg2=2 --extra_arg1=sup3r_$ecr3t_p@ssw0rd"
            )
        )
        == "test passed"
    )


if __name__ == "__main__":
    main()
