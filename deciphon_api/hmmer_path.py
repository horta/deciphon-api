from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from io import TextIOBase

__all__ = ["HMMERPath", "HMMERStep"]


@dataclasses.dataclass
class HMMERStep:
    hmm_cs: str
    target_cs: str
    match: str
    target: str
    score: str


def is_header(row: str):
    return row.replace(" ", "").startswith("==")


def reach_header_line(payload: TextIOBase):
    for row in payload:
        row = row.strip()
        if len(row) == 0:
            continue
        if is_header(row):
            return


def rowit(payload: TextIOBase):
    for row in payload:
        row = row.strip()
        if len(row) == 0:
            continue
        yield row


def stepit(payload: TextIOBase):
    i = rowit(payload)
    while True:
        try:
            row = next(i)
        except StopIteration:
            break

        if is_header(row):
            break

        last = row.rfind(" ")
        assert row[last:].strip() == "CS"
        hmm_cs = row[:last].strip()

        row = next(i)
        acc, start = row.split(maxsplit=2)[:2]
        offset = row.find(acc) + len(acc)
        offset = row.find(start, offset) + len(start)
        last = row.rfind(" ")
        tgt_cs = row[offset:last].strip()

        row = next(i)
        match = row.strip()

        row = next(i)
        start = row.split()[0]
        offset = row.find(start) + len(start)
        last = row.rfind(" ")
        tgt = row[offset:last].strip()

        row = next(i)
        last = row.rfind(" ")
        assert row[last:].strip() == "PP"
        score = row[:last].strip()

        assert len(hmm_cs) == len(tgt_cs) == len(match) == len(tgt) == len(score)
        for x in zip(hmm_cs, tgt_cs, match, tgt, score):
            yield HMMERStep(*x)


def pathit(payload: TextIOBase):
    reach_header_line(payload)

    while True:
        y = [x for x in stepit(payload)]
        if len(y) == 0:
            break
        yield HMMERPath(y)


def make_hmmer_paths(payload: TextIOBase):
    return [x for x in pathit(payload)]


class HMMERPath:
    def __init__(self, steps: Iterable[HMMERStep]):
        self._steps = list(steps)

    def hmm_cs_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.hmm_cs))
        return arr.decode()

    def target_cs_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.target_cs))
        return arr.decode()

    def match_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.match))
        return arr.decode()

    def target_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.target))
        return arr.decode()

    def score_stream(self):
        arr = bytearray()
        for x in self._steps:
            arr.append(ord(x.score))
        return arr.decode()

    def __len__(self):
        return len(self._steps)

    def __getitem__(self, idx: int):
        return self._steps[idx]

    def __iter__(self):
        return iter(self._steps)

    def __str__(self):
        txt = ", ".join((str(x) for x in self._steps))
        return f"HMMERPath({txt})"
