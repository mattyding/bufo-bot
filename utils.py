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

    parser.add_arg("train", "model", type=str, required=False, default="seq2seq")
    parser.add_arg("train", "epochs", type=int, required=False, default=7)
    parser.add_arg("train", "batch_size", type=int, required=False, default=64)
    parser.add_arg("train", "lr", type=float, required=False, default=0.001)

    parser.map_cmd_to_fn("connect", bufo_cmds.bufo_connect)
    parser.map_cmd_to_fn("disconnect", bufo_cmds.bufo_disconnect)
    parser.map_cmd_to_fn("train", bufo_cmds.bufo_train_model)
    parser.map_cmd_to_fn("enable", lambda slf: setattr(slf, "enable_responses", True))
    parser.map_cmd_to_fn("disable", lambda slf: setattr(slf, "enable_responses", False))
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
    return "".join([c for c in message if c.isalpha() or c in " :"]).lower()


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
    # run tests
    arr1 = [1, 2, 3, 4, 5, 4, 5, 4, 5, 4, 5, 4]
    arr2 = [1, 2, 2, 2, 2, 2, 2, 2, 2]
    arr3 = [1, 2, 3, 1, 2, 3, 1, 2, 3]
    arr4 = [1, 2, 3, 2, 3, 2, 3]
    arr5 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    arr6 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    arr7 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2]

    assert remove_repeating_pattern(arr1) == [1, 2, 3, 4, 5]
    assert remove_repeating_pattern(arr2) == [1, 2]
    assert remove_repeating_pattern(arr3) == [1, 2, 3]
    assert remove_repeating_pattern(arr4) == [1, 2, 3]
    assert remove_repeating_pattern(arr5) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert remove_repeating_pattern(arr6) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert remove_repeating_pattern(arr7) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
