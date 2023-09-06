# File containing util functions.
import discord
from collections import defaultdict
from dotenv import load_dotenv

CORPUS_FILE = "data/corpus.txt"
APPEND_FILE = "data/corpus-append.txt"  # stores new words. gets copied upon training


def init():
    load_dotenv()


def load_intents():
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return intents


def load_macros():
    macros = defaultdict(list)
    with open("macros.csv", "r") as f:
        f.readline()
        for line in f:
            line = line.split(",")
            macros[line[0]].append(line[1])
    return macros


def load_corpus():
    return set(open(CORPUS_FILE, "r").read().splitlines())


def write_word(word):
    with open("data/corpus-append.txt", "a") as f:
        f.write(word + "\n")


def sanitize(message):
    return "".join([c for c in message if c.isalpha() or c == " "]).lower()


def log_msg(message, words, prev_msg):
    message = sanitize(message.content)
    new_vocab = False
    if "bufo" in message:
        # don't log commands
        return True
    for word in message.split():
        if word not in words:
            # words.add(word)
            write_word(word)
            new_vocab = True
    input_text = prev_msg[0]
    output_text = message
    # store all pairs in a dataset file
    if prev_msg[0] != "":
        with open("data/dataset.txt", "a") as f:
            f.write(f"{input_text}\t{output_text}\n")
    prev_msg[0] = output_text
    return new_vocab


def copy_corpus():
    # copy corpus-append to corpus
    with open("data/corpus-append.txt", "r") as f:
        lines = f.readlines()
    # dedup
    lines = list(set(lines))
    with open("data/corpus.txt", "a") as f:
        f.writelines(lines)
    # clear out corpus-append
    with open("data/corpus-append.txt", "w") as f:
        f.write("")


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
