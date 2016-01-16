#!/usr/bin/env python3

from django.core.management.base import BaseCommand

import os
import re
import subprocess
import json

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        if not os.path.isdir("_result"):
            os.mkdir("_result")

        for name in os.listdir("classifications"):
            subprocess.call(["sb_dbexpimp", "-e", "-d", os.path.join("classifications", name), "-f", "_result/"+name])


        word_yea_votes_per_person = dict()
        word_nay_votes_per_person = dict()

        for person in os.listdir("result"):
            with open(os.path.join("result", person), "r") as f:
                try:
                    for line in f:
                        try:
                            word, yeas, nays = line.split(",")
                        except ValueError:
                            continue
                        if word.startswith("bi:"):
                            continue
                        if re.search(r"\d", word):
                            continue

                        if word not in word_yea_votes_per_person:
                            word_yea_votes_per_person[word] = dict()
                        if word not in word_nay_votes_per_person:
                            word_nay_votes_per_person[word] = dict()

                        word_yea_votes_per_person[word][person] = int(yeas)
                        word_nay_votes_per_person[word][person] = int(nays)

                except UnicodeDecodeError:
                    print(person)
                    raise



        def outliers(word_votes_per_person):
            most_outlier_voters_by_word = dict()

            for word in word_votes_per_person:
                highest_count_for_word = list(word_votes_per_person[word].items())
                highest_count_for_word.sort(key=(lambda pair: pair[1]), reverse=True)

                num_people = len(highest_count_for_word)
                if num_people < 5:
                    continue

                median = highest_count_for_word[num_people//2][1]

                most_outlier_voters_by_word[word] = list()

                if median * 1.3 > highest_count_for_word[0][1]:
                    continue

                for person, count in highest_count_for_word[:3]:
                    score = (count+1) / (median+1)  # terrible hacky zero division avoidance
                    most_outlier_voters_by_word[word].append((person, score))

            return most_outlier_voters_by_word

        word_info = dict()

        for word, person_score in outliers(word_yea_votes_per_person).items():
            if word not in word_info:
                word_info[word] = dict()
            word_info[word]["yea"] = person_score

        for word, person_score in outliers(word_nay_votes_per_person).items():
            if word not in word_info:
                word_info[word] = dict()
            word_info[word]["nay"] = person_score

        with open("word_scores.json", "w") as out:
        json.dump(word_info, out, indent=1)
