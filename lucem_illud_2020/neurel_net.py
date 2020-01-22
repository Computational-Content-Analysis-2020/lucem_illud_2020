try:
    import torch
    import torch.nn
except ImportError:
    pass
import numpy as np
import nltk
import gensim

# from .proccessing import stemmer_basic, stop_words_basic, normalizeTokens

def vecToVar(vec):
    var = torch.autograd.Variable(torch.from_numpy(np.stack(vec)).unsqueeze(0))
    if torch.cuda.is_available():
        var = var.cuda()

    return var

def genVecSeq(target, model):
    vecs = []
    try:
        if isinstance(target[0], list):
            target = sum(target, [])
    except IndexError:
        pass
    for t in target:
        try:
            vecs.append(model.wv[t])
        except KeyError:
            print("KeyError: {}".format(repr(t)))
            pass
    return vecs

def genWord2Vec(df, w2vDim):
    if 'normalized_sents' not in df:
            df['tokenized_sents'] = df['text'].apply(lambda x: [nltk.word_tokenize(s) for s in nltk.sent_tokenize(x)])
            df['normalized_sents'] = df['tokenized_sents'].apply(lambda x: [normalizeTokens(s, stopwordLst = stop_words_basic) for s in x])
    vocab = df['normalized_sents'].sum()

    model = gensim.models.Word2Vec(vocab,
        hs = 1, #Hierarchical softmax is slower, but better for infrequent words
        size = w2vDim, #Dim
        window = 5, #Might want to increase this
        min_count = 0,
        max_vocab_size = None,
        )

    df['w2v_text'] = df['normalized_sents'].apply(lambda x : genVecSeq(x, model))
    return model


class BiRNN(torch.nn.Module):
    def __init__(self, input_size, hidden_size, categories, num_layers, eta):
        super(BiRNN, self).__init__()
        self.eta = eta
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.n_categories = len(categories)
        self.categories = categories
        self.epoch = 0
        if not isinstance(categories, list):
            raise TypeError("categories must be a list")

        self.lstm = torch.nn.LSTM(input_size,
                            hidden_size,
                            num_layers,
                            batch_first = True,
                            bidirectional = True)

        self.fc = torch.nn.Linear(hidden_size * 2, self.n_categories)
        if torch.cuda.is_available():
            self.cuda()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:,-1,:])
        return out

    def __repr__(self):
        """Misusing and overwriting repr"""
        return "<BiRNN-{}-{}-{}-{}>".format(self.num_layers, self.hidden_size, self.n_categories, self.epoch)

    def catToVar(self, cat):
        a = np.zeros(self.n_categories)
        a[self.categories.index(cat)] = 1
        yVec = torch.autograd.Variable(torch.from_numpy(
        a))
        if torch.cuda.is_available():
            yVec = yVec.cuda()
        return yVec.float().unsqueeze(0)

    def save(self, saveName):
        with open(saveName, 'wb') as f:
            torch.save(self, f)

    def predict(self, vec, detail = False):
        out = self(vecToVar(vec))

        retDict = {}
        for i, c in enumerate(self.categories):
            retDict['weight_{}'.format(c)] = out.data[0][i]

        total_we = sum([np.exp(v) for v in retDict.values()])

        retDict['prediction'] = self.categories[np.argmax(out.data[0])]

        for i, c in enumerate(self.categories):
            retDict['prob_{}'.format(c)] = np.exp(retDict['weight_{}'.format(c)]) / total_we

        if detail:
            return retDict['prediction'], retDict
        else:
            return retDict['prediction']
