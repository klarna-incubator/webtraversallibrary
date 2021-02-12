# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Goes to a random wikipage, finds 'n' most common words in the article, where 'n' being the number of
most common words that the user wants.
"""

import collections
from collections import defaultdict

import webtraversallibrary as wtl

from .util import parse_cli_args

cli_args = parse_cli_args()
config = wtl.Config(cli_args.config)

window = wtl.Window(config)

# Navigates to a Wiki article chosen at random
window.scraper.navigate("https://en.wikipedia.org/wiki/Special:Random")

# Takes a snapshot of the current page
snapshot = window.scraper.scrape_current_page()

# Fetches all the elements with links in the current page
links = snapshot.elements.by_selector(wtl.Selector("a"))  # pylint: disable=no-member
print("Number of links in the article ", len(links))

# Gets the current URL of the page
search_url = window.driver.current_url

print("Link to the wiki article : ", search_url)

paragraphs = snapshot.elements.by_selector(wtl.Selector("div p"))  # pylint: disable=no-member
article = ""

# Fetch stopwords from a local file containing an array of stopwords
with open("examples/stopwords.txt", encoding="utf8") as f:
    stopwords = f.read()

for p in paragraphs:
    article = article + " " + p.metadata["text"]

# Find n most common words in the article, where n being the number of common words required by the user

wordcount = defaultdict(int)
for word in article.lower().split():
    if word not in stopwords:
        wordcount[word] += 1

n_print = int(input("How many most common words to print: "))
print("\nOK. The {} most common words are as follows\n".format(n_print))
word_counter = collections.Counter(wordcount)
for word, count in word_counter.most_common(n_print):
    print(word, ": ", count)

# Close the browser
window.quit()
