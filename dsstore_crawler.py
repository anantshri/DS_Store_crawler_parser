#!/usr/bin/env python3
# DS_Store recursive parser by anant
# dsstore parsing inspired by https://bitbucket.org/grimhacker/ds_store_parser/src
from ds_store import DSStore
from ds_store.buddy import BuddyError 
import requests
import argparse
import ds_store

# disable https warnings
import urllib3
urllib3.disable_warnings()

# https://edmundmartin.com/random-user-agent-requests-python/ 
from random import choice
def random_headers():
    desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
    return {'User-Agent': choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

# Request as a stream https://gist.github.com/obskyr/b9d4b4223e7eaf4eedcd9defabb34f13
from io import BytesIO, SEEK_SET, SEEK_END
class ResponseStream(object):
    def __init__(self, request_iterator):
        self._bytes = BytesIO()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position = self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)
    
    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)
    def flush(self):
        return
    def close(self):
        return


def parse_ds_store(filepointer):
    entries=[]
    try:
        with DSStore.open(filepointer) as d:
            for f in d:
                filename = f.filename
                if filename not in entries:
                    entries.append(filename)
        return entries
    except BuddyError:
        return None

def get_dstore(urlpath):
    try:
        r=requests.get(url_correct(urlpath) + ".DS_Store", stream=True, verify=False, headers=random_headers(),allow_redirects=True)
        if r.status_code == 200:
            ds = ResponseStream(r.iter_content(64))
            return ds 
        else:
            return None
    except Exception as e:
        print(e)
    return None

def url_correct(url):
    if url[-1] is not "/":
        url = url + "/"
    return url 

def runme(url):
    dst = get_dstore(url)
    if dst is not None:
        entries=parse_ds_store(dst)
        if entries is not None:
            for entry in entries:
                status=0
                status=requests.head(url_correct(url)+entry,verify=False, headers=random_headers(),allow_redirects=True)
                if status.url == url_correct(url)+entry:
                    new_url = url_correct(url)+entry
                else:
                    new_url = status.url
                print(new_url + " : " + str(status.status_code))
                runme(new_url)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="URL to start with", required=True)
    args = parser.parse_args()
    url = args.input
    entries=[]
    runme(url)


if __name__ == "__main__":
    main()
