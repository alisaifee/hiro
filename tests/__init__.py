# utter bullshit to work around pypy+six on a headless environment

from hiro import Timeline
with Timeline().freeze():
    pass


