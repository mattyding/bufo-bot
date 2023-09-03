import torch
import torch.nn as nn
import torch.optim as optim

from nltk.tokenize import word_tokenize


class BufoNN(nn.Module):
    # basic seq2seq architecture
    def __init__(self):
        super(BufoNN, self).__init__()
        self.corpus = self.load_corpus()
        input_size = len(self.corpus)
        hidden_size = 256
        output_size = len(self.corpus)
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)
        self.load_weights()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)

    def load_corpus(self):
        corpus_path = "data/corpus.txt"
        return open(corpus_path, "r").read().splitlines()

    def load_weights(self):
        try:
            self.load_state_dict(torch.load("data/weights.pt"))
        except FileNotFoundError:
            print("No weights found, starting from scratch...")
        except RuntimeError:
            print("Weights file corrupted, starting from scratch...")

    def save_weights(self):
        torch.save(self.state_dict(), "data/weights.pt")

    def refresh_corpus(self):
        self.corpus = self.load_corpus()

    def forward(self, input_seq):
        embedded = self.embedding(input_seq)
        output, hidden = self.gru(embedded)
        output = self.out(output)
        return output, hidden

    def train(self, sentence_pairs):
        self.refresh_corpus()
        for input_sentence, target_sentence in sentence_pairs:
            self.optimizer.zero_grad()

            # # tokenize input and target sentences
            # input_tokens = word_tokenize(input_sentence)
            # target_tokens = word_tokenize(target_sentence)
            input_tokens = input_sentence.split()
            target_tokens = target_sentence.split()

            # convert tokens to indices
            input_tensor = [self.corpus.index(token) for token in input_tokens]
            target_tensor = [self.corpus.index(token) for token in target_tokens]

            # pad to be same length
            max_len = max(len(input_tensor), len(target_tensor))
            input_tensor += [0] * (max_len - len(input_tensor))
            target_tensor += [0] * (max_len - len(target_tensor))

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
            loss.backward()
            self.optimizer.step()

    def predict(self, input_sentence):
        input_tokens = input_sentence.split()
        input_tensor = torch.tensor(
            [self.corpus.index(token) for token in input_tokens]
        )
        output, _ = self.forward(
            input_tensor.unsqueeze(0)
        )  # Unsqueeze to add batch dimension
        predicted_indices = output.argmax(dim=2).squeeze().tolist()
        if type(predicted_indices) == int:  # only one word predicted
            predicted_indices = [predicted_indices]
        predicted_tokens = [self.corpus[idx] for idx in predicted_indices]
        predicted_sentence = " ".join(predicted_tokens)
        return predicted_sentence


if __name__ == "__main__":
    warning = "WARNING: You are running a testing script which will overwrite the corpus. Proceed? (y/n) "
    if input(warning) == "y":
        with open("data/corpus.txt", "w") as f:
            f.write("hello\nworld\n")
        model = BufoNN()
        model.train([("hello", "world")])
        model.save_weights()
        print(model.predict("hello"))
