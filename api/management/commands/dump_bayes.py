#!/usr/bin/env python3

from django.core.management.base import BaseCommand

import os
import re
import subprocess

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for name in os.listdir("classifications"):
            print(name)
            subprocess.call(["sb_dbexpimp", "-e", "-d", os.path.join("classifications", name), "-f", "result/"+name])
