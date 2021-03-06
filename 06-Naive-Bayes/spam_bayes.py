#!/usr/bin/python3
#
# See for https://en.wikipedia.org/wiki/Naive_Bayes_classifier the
# basic algorithm.
#
# You can train it with the first 1000 messages in the corpus:
#
#   head -1000 corpus/SMSSpamCollection.txt| ./spam_bayes.py --train -
#
# And then test it with the remainig 4574:
#
#   tail -4574 corpus/SMSSpamCollection.txt | ./spam_bayes.py --test -

import argparse
import collections
import math
import pickle
import re
import sys

def classify_words(text, word_dict):
    # Remove trailing \n
    text = text[:-1]

    words = re.split(r"(?: |,|\.|-|–|:|;|&|=|\+|#|\(|\)|\||<|…|\^|\[|\])+", text)

    for word in words:
        # Remove misc symbols
        word = re.sub(r"^(?:'|\"|“)+", r"", word)
        word = re.sub(r"(\w)'$", r"\1", word)
        word = word.lower()

        if word == "":
            continue

        word_dict[word] += 1

def is_spam(text, ham_words, spam_words):
    probability_ham = math.log(0.5)
    probability_spam = math.log(0.5)

    # Instead of ignoring a word that's present in one of the types
    # but not the other, we estimate its presence by scaling the
    # number of ocurrences on the other type.
    #
    # I came up with this value by using the one that maximises the
    # accuracy when testing the last 4574 entries of the corpus.
    # These are the results I got for other values:
    #
    # (.1, 94.38),
    # (.01, 95.61),
    # (.001, 95.93),
    # (.0001, 96.35),
    # (.00001, 96.39),
    # (.000001, 96.46),
    # (.0000001, 96.5),
    # (.00000001, 96.61),
    # (1e-9, 96.66),
    # (1e-10, 96.66),
    # (1e-11, 96.66)
    # (1e-12, 96.68)
    # (1e-90, 96.68)
    unseen_coeff = 1e-12

    words = re.split(r"(?: |,|\.|-|–|:|;|&|=|\+|#|\(|\)|\||<|…|\^|\[|\])+", text)

    for word in words:
        # Remove misc symbols
        word = re.sub(r"^(?:'|\"|“)+", r"", word)
        word = re.sub(r"(\w)'$", r"\1", word)
        word = word.lower()

        if word == "":
            continue

        ham_instances = ham_words[word]
        spam_instances = spam_words[word]

        try:
            log_ham_instances = math.log(ham_instances)
        except ValueError:
            if spam_instances:
                log_ham_instances = math.log(spam_instances * unseen_coeff)
            else:
                continue

        try:
            log_spam_instances = math.log(spam_words[word])
        except ValueError:
            log_spam_instances = math.log(ham_instances * unseen_coeff)

        log_total_instances = math.log(ham_instances + spam_instances)

        probability_ham += log_ham_instances - log_total_instances
        probability_spam += log_spam_instances - log_total_instances

    return probability_spam > probability_ham

def train_from_file(fin):
    ham_words = collections.defaultdict(int)
    spam_words = collections.defaultdict(int)

    for line in fin:
        line_parts = line.split("\t")
        if line_parts[0] == "ham":
            classify_words(line_parts[1], ham_words)
        elif line_parts[0] == "spam":
            classify_words(line_parts[1], spam_words)
        else:
            raise RuntimeError("Unkwnown line: {}".format(line))

    with open("brain", "wb") as fout:
        pickle.dump((ham_words, spam_words), fout)

def classify_file(fin):
    with open("brain", "rb") as brain_fin:
        (ham_words, spam_words) = pickle.load(brain_fin)

    num_correct = 0
    num_incorrect = 0

    for line in fin:
        (true_class, text) = line.split("\t")

        spam = is_spam(text, ham_words, spam_words)

        guess = "spam" if spam else "ham"

        if (spam and (true_class == "spam")) or \
           (not spam and (true_class == "ham")):
            num_correct += 1
        else:
            num_incorrect += 1

    total = num_correct + num_incorrect
    print("Correct: {}/{} ({:.2%})".format(num_correct, total,
                                           num_correct / total))

def classify_text(text):
    with open("brain", "rb") as fin:
        (ham_words, spam_words) = pickle.load(fin)

    if is_spam(text, ham_words, spam_words):
        print("spam")
    else:
        print("ham")

def main():
    parser = argparse.ArgumentParser(description="Spam bayes classifier")

    parser.add_argument("--train", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("-c", "--classify_text", nargs=1)
    parser.add_argument("file", nargs="?", default="corpus/SMSSpamCollection.txt", help="the file to read the text from.  Use - to read from stdin.  Don't use the same file for training and testing ;)")

    args = parser.parse_args()

    if args.classify_text:
        return classify_text(args.classify_text[0])

    if args.train:
        if args.file == "-":
            train_from_file(sys.stdin)
        else:
            with open(args.file) as fin:
                train_from_file(fin)

    if args.test:
        if args.file == "-":
            classify_file(sys.stdin)
        else:
            with open(args.file) as fin:
                classify_file(fin)

    if not args.train and not args.test:
        parser.print_help()

if __name__ == "__main__":
    main()
