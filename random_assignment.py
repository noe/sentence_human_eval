#!/usr/bin/env python3

from collections import defaultdict, Counter
import sys
import argparse
import random
import os


def read_master(filename):
    sentences = []
    with open(filename) as f:
        for line in f:
            model, index, sentence = line.strip().split('\t')
            id = "{} [{}]".format(model, index)
            sentences.append((id, model, sentence))
    return sentences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--redundancy', type=int, required=True)
    parser.add_argument('--num_annotators', type=int, required=True)
    parser.add_argument('--num_models', type=int, required=True)
    parser.add_argument('--master', type=str, required=True)

    args = parser.parse_args()

    sentences = read_master(args.master)
    id2sentence = {id: sentence for id, model, sentence in sentences}
    id2model = {id: model for id, model, sentence in sentences}

    num_sents_per_model = len(sentences) // args.num_models
    num_sents_per_annotator =  num_sents_per_model * args.redundancy * args.num_models // args.num_annotators
    num_sents_per_model_per_annotator = num_sents_per_annotator // args.num_models
    count = {id: 0 for id, model, sentence in sentences}

    candidate_bag = {id for id, model, sentence in sentences}

    for annotator in range(1, args.num_annotators + 1):
        assigned_ids = set()

        while len(assigned_ids) < num_sents_per_annotator:
            if len(candidate_bag - assigned_ids) == 0:
                print("Did not converge", file=sys.stderr)
                sys.exit(-1)

            candidate_id = random.choice(tuple(candidate_bag - assigned_ids))

            model = id2model[candidate_id]
            num_assigned_same_model = len([assigned_id
                                           for assigned_id in assigned_ids
                                           if id2model[assigned_id] == model])

            if num_assigned_same_model == num_sents_per_model_per_annotator:
                continue

            if count[candidate_id] - min(count.values()) > 1:
                continue

            assigned_ids.add(candidate_id)
            count[candidate_id] += 1
            if count[candidate_id] == args.redundancy:
                candidate_bag.remove(candidate_id)

        annotator_label = "annotator_{:02d}".format(annotator)
        annotator_file = os.path.join(os.path.dirname(args.master), annotator_label + ".tsv")
        with open(annotator_file, 'w', encoding='utf-8') as f:
            for assigned_id in assigned_ids:
                model = id2model[assigned_id]
                line = "{}\t{}\t{}\t{}".format(assigned_id, model, annotator_label, id2sentence[assigned_id])
                print(line, file=f)

    print("Success", file=sys.stderr)


if __name__ == '__main__':
    main()

