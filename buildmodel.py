import numpy
import sys
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras import utils
from tensorflow.keras.callbacks import ModelCheckpoint

file = open("GhostWriter/data/words.txt").read()

def tokenize_words(input):
   #Convert text to lowercase
   input = input.lower()

   #Initialize the tokenizer
   tokenizer = RegexpTokenizer(r'\w+')
   tokens = tokenizer.tokenize(input)

   #Move any token, that is not in the stop words, to the "filtered" words
   filtered = filter(lambda token: token not in stopwords.words('english'), tokens)
   return " ".join(filtered)

processed_inputs = tokenize_words(file)

chars = sorted(list(set(processed_inputs)))
char_to_num = dict((c, i) for i, c in enumerate(chars))

input_len = len(processed_inputs)
vocab_len = len(chars)
print ("NUMBER OF CHARACTERS: ", input_len)
print ("VOCABULARY: ", vocab_len)


seq_length = 100
x_data = []
y_data = []

#This will loop through inputs, until there are no more characters than can be turned into a sequence.
for i in range(0, input_len - seq_length, 1):

   #Defines input/output sequences:
   #Input is the current character, plus the desired length of the sequence.
   in_seq = processed_inputs[i:i + seq_length]

   #Output is the initial character, plus the total length of the sequence.
   out_seq = processed_inputs[i + seq_length]

   x_data.append([char_to_num[char] for char in in_seq])
   y_data.append(char_to_num[out_seq])

n_patterns = len(x_data)
print ("NUMBER OF PATTERNS: ", n_patterns)

X = numpy.reshape(x_data, (n_patterns, seq_length, 1))
X/float(vocab_len)

y = utils.to_categorical(y_data)

model = Sequential()
model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(256, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam')

filepath = "fix.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
desired_callbacks = [checkpoint]

model.fit(X, y, epochs=50, batch_size=256, callbacks=desired_callbacks)

filename = "model.hdf5"
model.load_weights(filename)
model.compile(loss='categorical_crossentropy', optimizer='adam')

num_to_char = dict((i, c) for i, c in enumerate(chars))

