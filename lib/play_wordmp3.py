"""play mp3 module."""
import os
import sys
from glob import glob

from playsound import playsound

from .pre import audio_dir


def play_mp3(path, word, show_tag=True, only_American_pronunciation=True):
    """播放音频读音, 默认只播放美式发音"""
    if not word.isalpha():
        return
    filenames = []
    if only_American_pronunciation:
        for filename in glob(os.path.join(path, audio_dir, word + "-美.mp3")):
            filenames.append(filename)
    else:
        for filename in glob(os.path.join(path, audio_dir, word + "-*.mp3")):
            filenames.append(filename)
    if filenames == []:
        # maybe only UK pronunciation.
        filenames = glob(os.path.join(path, audio_dir, word + "-*.mp3"))
    filenames.sort()
    filenames.reverse()
    for filename in filenames:
        if show_tag:
            print("\rnow playing: %s" % os.path.basename(filename), end=' ')
        sys.stdout.flush()
        playsound(filename)
    if show_tag:
        print("\r %s" % (" " * 50))

    if filenames == []:
        print("[*] cannot find audio file of this word.")


if __name__ == '__main__':
    play_mp3("~/program/dictionary", "branch")
