#!/usr/bin/env python3

from django.core.management.base import BaseCommand

import os
import re
import subprocess

from opencivicdata import models as ocdmod

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        print(args, kwargs)

        if not os.path.isdir("classifications"):
            os.makedirs("classifications")

        for billversion in ocdmod.BillVersion.objects.all():
            for billversionlink in billversion.links.all():

                t = billversionlink.text

                t = re.sub(r"\whb\d\d\d\d-\d\d\w\s*$", "", t.strip())
                t = re.sub(r"â\x80\x9c", '"', t)
                t = re.sub(r"—", ' ', t)
                t = re.sub(r"â\x80\x9d", '"', t)
                t = re.sub(r"â\x80\x83", ' ', t)
                t = re.sub(r"â\x80\x94", ' ', t)
                t = re.sub(r" h[bm]0*(\d+)-0\d(-c\d)? (\uf020 )?(CS/)*H[BM] \1 20\d\d ", ' ', t)
                t = re.sub(r" h[bm]\d+-0\d(-c\d)?$", '', t)
                t = re.sub(r"\s*R E P R E S E N T A T I V E S \uf020", '', t)
                t = re.sub(r" Page \d+ of \d+", "", t)
                t = re.sub(r" CODING: Words stricken are deletions; words underlined are additions.", "", t)

                t = re.sub(r"[^A-Za-z0-9]+", " ", t)

            sess = billversion.bill.legislative_session.name.replace("/", "-")

            othernotes = list()

            for word in billversion.bill.title.split():
                othernotes.append("titlecontains-" + word);

            for spon in billversion.bill.sponsorships.all():
                if spon.organization:
                    print("org:", spon.organization, dir(spon.organization))
                if spon.person:
                    print("person:", spon.person, dir(spon.person))
                if spon.name:
                    othernotes.append("sponsor-" + spon.name.replace(" ", ""));

            for vote in billversion.bill.votes.all():
                for voter in vote.votes.all():
                    #assert voter.option in ("yes", "no", "other", "not voting", "excused"), voter.option
                    othernotes.append("othervoter-{0}-{1}".format("".join(voter.voter_name.split()), voter.option.replace(" ", "")))

                tasks = list()

                for voter in vote.votes.all():
                    vote = None
                    voter_id = voter.voter_name

                    if voter.option == "yes":
                        vote = "-g"
                    elif voter.option == "no":
                        vote = "-s"

                    if vote:
                        tasks.append((sess, voter_id, vote, t, othernotes))

                if tasks:
                    for task in tasks:
                        run(*task)


def run(sess, voter_id, vote, t, othernotes):
    with subprocess.Popen(["sb_filter", "-d", os.path.join("classifications", voter_id), vote, "-o", "Classifier:use_bigrams:True", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as classifier:
        stdout_data, stderr_data = classifier.communicate((t + " /\n " + " /\n".join(othernotes)).encode("UTF-8"))
        print(voter_id)
        return classifier.wait()

