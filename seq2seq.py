import torch
import torch.nn as nn
import torch.optim as optim

import utils as utils


class BufoSeq2Seq(nn.Module):
    def __init__(self):
        super(BufoSeq2Seq, self).__init__()
        self.load_corpus()
        input_size = len(self.corpus)
        hidden_size = 256
        output_size = len(self.corpus)
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)
        self.load_weights()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)

    # when program stops, save weights
    def __del__(self):
        self.save_weights()

    def load_weights(self):
        try:
            self.load_state_dict(torch.load("data/weights.pt"))
        except FileNotFoundError:
            print("No weights found, starting from scratch...")
        except RuntimeError:
            print("Weights file corrupted, starting from scratch...")

    def save_weights(self):
        torch.save(self.state_dict(), "data/weights.pt")

    def load_corpus(self):
        self.corpus = list(utils.load_corpus())
        # add STOP token
        self.corpus.append("<STOP>")

    def forward(self, input_seq):
        embedded = self.embedding(input_seq)
        output, hidden = self.gru(embedded)
        output = self.out(output)
        return output, hidden

    def train(self, sentence_pairs, num_epochs, batch_size, lr):
        del batch_size  # unused
        del lr  # unused
        self.load_corpus()
        for epoch in range(num_epochs):
            print(f"Epoch {epoch + 1}/{num_epochs}")
            for input_sentence, target_sentence in sentence_pairs:
                self.optimizer.zero_grad()

                # # tokenize input and target sentences
                # input_tokens = word_tokenize(input_sentence)
                # target_tokens = word_tokenize(target_sentence)
                input_tokens = input_sentence.split()
                target_tokens = target_sentence.split()
                # append stop token to target sentence
                input_tokens.append("<STOP>")
                target_tokens.append("<STOP>")

                # convert tokens to indices
                input_tensor = [self.corpus.index(token) for token in input_tokens]
                target_tensor = [self.corpus.index(token) for token in target_tokens]

                # pad to be same length
                max_len = max(len(input_tensor), len(target_tensor))
                input_tensor += [self.corpus.index("<STOP>")] * (
                    max_len - len(input_tensor)
                )
                target_tensor += [self.corpus.index("<STOP>")] * (
                    max_len - len(target_tensor)
                )

                # convert to tensors
                input_tensor = torch.tensor(input_tensor)
                target_tensor = torch.tensor(target_tensor)

                batch_size = 1  # Since we're processing one example at a time
                input_tensor = input_tensor.unsqueeze(0).expand(
                    batch_size, -1
                )  # Expand the input tensor to match batch size
                target_tensor = target_tensor.unsqueeze(0).expand(
                    batch_size, -1
                )  # Expand the target tensor

                output, _ = self.forward(input_tensor)
                loss = self.criterion(output.squeeze(0), target_tensor.squeeze(0))
                # print(loss)
                loss.backward()
                self.optimizer.step()

    def predict(self, input_sentence):
        for word in input_sentence.split():
            if word not in self.corpus:
                return None

        response = []
        # feed in words one at a time from input_sentence until STOP token is generated
        # tokenize input sentence
        input_tokens = input_sentence.split()
        # append stop token to input sentence
        input_tokens.append("<STOP>")
        # convert tokens to indices
        input_tensor = [self.corpus.index(token) for token in input_tokens]
        # convert to tensors
        input_tensor = torch.tensor(input_tensor)
        batch_size = 1  # Since we're processing one example at a time
        input_tensor = input_tensor.unsqueeze(0).expand(batch_size, -1)
        # feed in entire input sentence
        output, _ = self.forward(input_tensor)
        topv, topi = output.topk(1)
        topi = topi[0][0]
        response.append(topi)
        # repeatedly feed in response until STOP token is generated
        while topi != self.corpus.index("<STOP>") and len(response) < 20:
            # feed the entire response so far
            output, _ = self.forward(torch.tensor(response).unsqueeze(0))
            topv, topi = output.topk(1)
            topi = topi[0][0]
            response.append(topi)
        # if generated stop token
        if topi == self.corpus.index("<STOP>"):
            response.pop()

        # print(" ".join([self.corpus[index] for index in response]))
        response = utils.remove_repeating_pattern(response)
        return " ".join([self.corpus[index] for index in response])


if __name__ == "__main__":
    warning = "WARNING: You are running a testing script which will overwrite the corpus. Proceed? (y/n) "
    if input(warning) == "y":
        # make a backup copy of the corpus at data/corpus_copy.txt
        with open("data/corpus.txt", "r") as f:
            corpus = f.read()
        with open("data/corpus_copy.txt", "w") as f:
            f.write(corpus)
        print(
            "Well okay, but I copied the corpus to data/corpus_copy.txt just in case."
        )
        with open("data/corpus.txt", "w") as f:
            f.write("hello\nworld\n")
        model = BufoNN()
        model.train([("hello", "world")])
        model.save_weights()
        print(model.predict("hello"))
