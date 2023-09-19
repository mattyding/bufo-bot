# File containing util functions.
import discord
import logging

from argparser import BufoArgParser
import commands as bufo_cmds

CORPUS_FILE = "data/corpus.txt"
APPEND_FILE = "data/corpus-append.txt"  # stores new words. gets copied upon training
DATASET_FILE = "data/dataset.txt"


# INIT FUNCTIONS
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")],
    )


def load_intents():
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return intents


def init_parser():
    parser = BufoArgParser()
    parser.add_cmd("connect")
    parser.add_cmd("disconnect")
    parser.add_cmd("go away", alias_for="disconnect")
    parser.add_cmd("train")
    parser.add_cmd("enable")
    parser.add_cmd("disable")

    parser.add_param("train", "model", type=str, required=False, default="seq2seq")
    parser.add_param("train", "epochs", type=int, required=False, default=7)
    parser.add_param("train", "batch_size", type=int, required=False, default=64)
    parser.add_param("train", "lr", type=float, required=False, default=0.001)

    parser.add_env_param("enable", "slf")
    parser.add_env_param("disable", "slf")
    parser.add_env_param("connect", "message")
    parser.add_env_param("disconnect", "message")
    parser.add_env_param("train", "model")

    parser.map_cmd_to_fn("connect", bufo_cmds.bufo_connect, async_fn=True)
    parser.map_cmd_to_fn("disconnect", bufo_cmds.bufo_disconnect, async_fn=True)
    parser.map_cmd_to_fn("train", bufo_cmds.bufo_train_model, async_fn=True)

    def _enable(slf):
        setattr(slf, "enable_responses", True)
        logging.info("Message responses enabled")

    def _disable(slf):
        setattr(slf, "enable_responses", False)
        logging.info("Message responses disabled")

    parser.map_cmd_to_fn("enable", _enable)
    parser.map_cmd_to_fn("disable", _disable)

    return parser


# I/O FUNCTIONS
def load_corpus():
    return set(open(CORPUS_FILE, "r").read().splitlines())


def write_word_to_append_file(word):
    with open(APPEND_FILE, "a") as f:
        f.write(word + "\n")


def write_training_example(input, output):
    with open(DATASET_FILE, "a") as f:
        f.write(input + "\t" + output + "\n")


def copy_corpus():
    # copy corpus-append to corpus
    with open(APPEND_FILE, "r") as f:
        lines = f.readlines()
    # dedup
    lines = list(set(lines))
    with open(CORPUS_FILE, "a") as f:
        f.writelines(lines)
    # clear out corpus-append
    with open(APPEND_FILE, "w") as f:
        f.write("")


# STRING PROCESSING FUNCTIONS
def sanitize(message):
    cleaned_str = "".join([c for c in message if c.isalpha() or c in " "]).lower()
    return " ".join(cleaned_str.split()) # removes instances of multiple spaces


def remove_repeating_pattern(arr):
    for start in range(0, len(arr) // 2):
        for end in range(start + 1, len(arr)):
            pattern = arr[start:end]
            # check if pattern repeats until end
            # stopping midway through cycle is fine
            reminder = len(arr[start:]) % len(pattern)
            if (
                arr[start:]
                == pattern * (len(arr[start:]) // len(pattern)) + pattern[:reminder]
            ):
                return arr[:start] + pattern
    return arr


if __name__ == "__main__":
    # sanitize() unit tests
    sanitize1 = "Hello, world!"
    sanitize2 = "Hello, world! "
    sanitize3 = "     "
    sanitize4 = ".<>?/;':\"[]{}\\|!@#$%^&*()_+-="
    sanitize5 = ". . . . . . .. . "

    assert sanitize(sanitize1) == "hello world"
    assert sanitize(sanitize2) == "hello world"
    assert sanitize(sanitize3) == ""
    assert sanitize(sanitize4) == ""
    assert sanitize(sanitize5) == ""


    # remove_repeating_pattern() unit tests
    rrp1 = [1, 2, 3, 4, 5, 4, 5, 4, 5, 4, 5, 4]
    rrp2 = [1, 2, 2, 2, 2, 2, 2, 2, 2]
    rrp3 = [1, 2, 3, 1, 2, 3, 1, 2, 3]
    rrp4 = [1, 2, 3, 2, 3, 2, 3]
    rrp5 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    rrp6 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    rrp7 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2]

    assert remove_repeating_pattern(rrp1) == [1, 2, 3, 4, 5]
    assert remove_repeating_pattern(rrp2) == [1, 2]
    assert remove_repeating_pattern(rrp3) == [1, 2, 3]
    assert remove_repeating_pattern(rrp4) == [1, 2, 3]
    assert remove_repeating_pattern(rrp5) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert remove_repeating_pattern(rrp6) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert remove_repeating_pattern(rrp7) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    print("All unit tests passed!")
