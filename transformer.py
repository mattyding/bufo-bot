import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class BufoTransformer(nn.Module):
    def __init__(self, vocab_size, d_model, nhead, num_encoder_layers, num_decoder_layers, dropout=0.1):
        super(BufoTransformer, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model, nhead, dropout=dropout),
            num_layers=num_encoder_layers
        )
        
        self.decoder = nn.TransformerDecoder(
            nn.TransformerDecoderLayer(d_model, nhead, dropout=dropout),
            num_layers=num_decoder_layers
        )
        
        self.fc = nn.Linear(d_model, vocab_size)
        
    def forward(self, src, tgt):
        src_embedded = self.embedding(src)
        tgt_embedded = self.embedding(tgt)
        
        src_encoded = self.encoder(src_embedded)
        tgt_decoded = self.decoder(tgt_embedded, src_encoded)
        
        output = self.fc(tgt_decoded)
        return output

# Sample usage
if __name__ == "__main__":
    # Define hyperparameters
    vocab_size = 10000  # Adjust as per your dataset
    d_model = 512
    nhead = 8
    num_encoder_layers = 6
    num_decoder_layers = 6
    dropout = 0.1
    
    # Initialize the BufoTransformer model
    model = BufoTransformer(vocab_size, d_model, nhead, num_encoder_layers, num_decoder_layers, dropout)
    
    # Define some sample input data
    src = torch.randint(0, vocab_size, (10, 32))  # (sequence length, batch size)
    tgt = torch.randint(0, vocab_size, (20, 32))  # (sequence length, batch size)
    
    # Forward pass
    output = model(src, tgt)
    
    print(output.shape)  # This will print the shape of the output tensor
