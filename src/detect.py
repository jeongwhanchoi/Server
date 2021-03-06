# usr/bin/python27

from models.convnets import ConvolutionalNet
from keras.models import load_model
from keras.preprocessing import sequence
# from keras.backend import clear_session
from preprocessors.preprocess_text import clean
import sys
import string
import re
import tensorflow as tf

MATCH_MULTIPLE_SPACES = re.compile("\ {2,}")
SEQUENCE_LENGTH = 20
EMBEDDING_DIMENSION = 30

UNK = "<UNK>"
PAD = "<PAD>"



vocabulary = open("data/vocabulary.txt").read().split("\n")
inverse_vocabulary = dict((word, i) for i, word in enumerate(vocabulary))

def words_to_indices(inverse_vocabulary, words):
    return [inverse_vocabulary.get(word, inverse_vocabulary[UNK]) for word in words]



class Detector (object):
    def __init__(self, model_path):
        model = ConvolutionalNet(vocabulary_size=len(vocabulary), embedding_dimension=EMBEDDING_DIMENSION, input_length=SEQUENCE_LENGTH)
        model.load_weights(model_path)
        self.graph = tf.get_default_graph()
        self.model = model

    def detect (self, headline):
        # headline = headline.encode("ascii", "ignore")
        inputs = sequence.pad_sequences([words_to_indices(inverse_vocabulary, clean(headline).lower().split())], maxlen=SEQUENCE_LENGTH)
        with self.graph.as_default():
            clickbaitiness = self.model.predict(inputs)[0, 0]
        return clickbaitiness



detector = Detector("models/detector.h5")
if __name__ == "__main__":
    print ("headline is {0} % clickbaity".format(round(detector.detect(sys.argv[1]) * 100, 2)))
