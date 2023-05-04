#!/usr/bin/env python3

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

for dirname, _, filenames in os.walk('csv'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

reviews = pd.read_csv("csv/test.csv")
print(reviews.head(2))
