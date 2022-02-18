import argparse
from typing import List, Optional, Union

T = 2
Taug = 3
S = 1
C, D, E, F, G, A, B = "C", "D", "E", "F", "G", "A", "B"
Cs, Ds, Fs, Gs, As = "C#", "D#", "F#", "G#", "A#"
Db, Eb, Gb, Ab, Bb = "Db", "Eb", "Gb", "Ab", "Bb"
NOTES_S = [C, Cs, D, Ds, E, F, Fs, G, Gs, A, As, B] * 10
NOTES_B = [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B] * 10

MAJOR = (T, T, S, T, T, T, S)
MINOR_HARM = (T, S, T, T, S, Taug, S)
MAJOR_STR = "major"
MINOR_STR = "minor"

IONIAN = "ionian"
DORIAN = "dorian"
PHRYGIAN = "phrygian"
LYDIAN = "lydian"
MIXOLYDIAN = "mixolydian"
AEOLIAN = "aeolian"
LOCRIAN = "locrian"

MODAL_TONE = {
    IONIAN: 0,
    DORIAN: 1,
    PHRYGIAN: 2,
    LYDIAN: 3,
    MIXOLYDIAN: 4,
    AEOLIAN: 5,
    LOCRIAN: 6,
}

I, II, III, IV, V, VI, VII = "I", "II", "III", "IV", "V", "VI", "VII"
ROMANS = [I, II, III, IV, V, VI, VII]


def get_interval(x: str, y: str) -> int:
    """Given two notes, e.g. A and C, it returns the interval in semitones, e.g. 3.

    Args:
        x (str): a note as uppercase letter. Sharps are "#", flats "b". e.g. C.
        y (str): a note as uppercase letter. Sharps are "#", flats "b". e.g. D#.

    Returns:
        int: Interval between x and y in semitones.
    """
    if x in NOTES_S:
        if y in NOTES_S:
            interval = NOTES_S.index(y) - NOTES_S.index(x)
        elif y in NOTES_B:
            interval = NOTES_B.index(y) - NOTES_S.index(x)
        else:
            raise ValueError(
                f"Couldn't find {y} among {set(NOTES_S).union(set(NOTES_B))}"
            )
    elif x in NOTES_B:
        if y in NOTES_S:
            interval = NOTES_S.index(y) - NOTES_B.index(x)
        elif y in NOTES_B:
            interval = NOTES_B.index(y) - NOTES_B.index(x)
        else:
            raise ValueError(
                f"Couldn't find {y} among {set(NOTES_S).union(set(NOTES_B))}"
            )
    else:
        raise ValueError(f"Couldn't find {y} among {set(NOTES_S).union(set(NOTES_B))}")
    return interval % 12


TRIADES = {(4, 3): "", (3, 4): "-", (3, 3): "dim", (4, 4): "+"}
SEVENTHS = {
    (4, 3, 3): "7",
    (4, 3, 4): "Δ7",
    (3, 4, 3): "-7",
    (3, 4, 4): "-Δ7",
    (3, 3, 3): "o",
    (3, 3, 4): "ø",
    (4, 4, 3): "+Δ7",
}
AVAIL_CHORDS = TRIADES | SEVENTHS


class _RawScale:
    def __init__(
        self,
        root: str = C,
        base_scale: List[int] = MAJOR,
        start_grade: Optional[int] = None,
    ):
        assert sum(base_scale) == 12, "The sum of semitones should be 12!"
        self.start_grade = 0 if start_grade == None else start_grade
        self.root = root
        self.base_scale = base_scale
        self._build_scale(self.root in NOTES_S)

    def _build_scale(self, sharp: bool):
        if sharp:
            self.__build_scale(NOTES_S)
        else:
            self.__build_scale(NOTES_B)
        self._shift_start()

    def __build_scale(self, notes: list):
        self.scale = []
        index = notes.index(self.root)
        iterseq = iter(self.base_scale)
        while index < len(notes):
            self.scale.append(notes[index])
            try:
                index += next(iterseq)
            except:
                iterseq = iter(self.base_scale)
                index += next(iterseq)
        self._resolve_sharp_flat()

    def _resolve_sharp_flat(self):
        self._avoid_base_note_and_sharp()
        self._avoid_base_note_and_flat()
        self._avoid_same_note_flat_and_sharp()

    def _fix_root(self):
        if self.root in NOTES_S and self.scale[0] in NOTES_B:
            index_root = NOTES_B.index(self.scale[0])
            self.scale = [
                NOTES_S[index_root] if note == NOTES_B[index_root] else note
                for note in self.scale
            ]
        if self.root in NOTES_B and self.scale[0] in NOTES_S:
            index_root = NOTES_S.index(self.scale[0])
            self.scale = [
                NOTES_B[index_root] if note == NOTES_S[index_root] else note
                for note in self.scale
            ]

    def _avoid_same_note_flat_and_sharp(self):
        for sharp, flat, new_sharp, new_flat in zip(
            [Ds, Gs, As], [Db, Gb, Ab], [Cs, Fs, Gs], [Eb, Ab, Bb]
        ):
            if sharp in self.scale and flat in self.scale:
                majority_sharp = self._vote_flat_or_sharp()
                if majority_sharp:
                    self.scale = [
                        new_sharp if note == flat else note for note in self.scale
                    ]
                else:
                    self.scale = [
                        new_flat if note == sharp else note for note in self.scale
                    ]

    def _avoid_base_note_and_flat(self):
        for base, sharp, flat in zip(
            [D, E, G, A, B], [Cs, Ds, Fs, Gs, As], [Db, Eb, Gb, Ab, Bb]
        ):
            if base in self.scale and flat in self.scale:
                self.scale = [sharp if note == flat else note for note in self.scale]

    def _avoid_base_note_and_sharp(self):
        for base, sharp, flat in zip(
            [C, D, F, G, A], [Cs, Ds, Fs, Gs, As], [Db, Eb, Gb, Ab, Bb]
        ):
            if base in self.scale and sharp in self.scale:
                self.scale = [flat if note == sharp else note for note in self.scale]

    def _vote_flat_or_sharp(self):
        sharp_n = sum([1 if "s" in note else 0 for note in self.scale])
        flat_n = sum([1 if "b" in note else 0 for note in self.scale])
        return sharp_n > flat_n

    def _shift_start(self):
        self.scale = self.scale[self.start_grade :]
        self._fix_root()

    def __repr__(self) -> str:
        return str("\t".join(self.scale[:7]))


class Scale(_RawScale):
    def __init__(
        self,
        root: str = C,
        base_scale: Union[str, List[int]] = MAJOR,
        mode: Union[str, int] = IONIAN,
    ) -> None:
        if type(base_scale) == str:
            if base_scale.lower() == MAJOR_STR:
                base_scale = MAJOR
            elif base_scale.lower() == MINOR_STR:
                base_scale = MINOR_HARM
            else:
                raise ValueError(
                    "base_scale should be 'major' or 'minor', "
                    f"or a list of semitone intervals. Got {base_scale}."
                )
        grade = int(mode) - 1 if mode not in MODAL_TONE else MODAL_TONE[mode]
        root = self._shift_root_for_raw_scale(root, base_scale, grade)
        super().__init__(root, base_scale, grade)

    def _shift_root_for_raw_scale(self, root, base_scale, grade):
        if root in NOTES_S:
            root_idx = len(NOTES_S) - 1 - NOTES_S[::-1].index(root)
            root = NOTES_S[root_idx - sum(base_scale[:grade])]
        else:
            root_idx = len(NOTES_B) - 1 - NOTES_B[::-1].index(root)
            root = NOTES_B[root_idx - sum(base_scale[:grade])]
        return root


class _RawChords:
    def __init__(self, scale=Scale, seventh=False) -> None:
        self.scale = scale
        self.raw_chords = []
        for i in range(7):
            intervals = [0, 2, 4, 6] if seventh else [0, 2, 4]
            self.raw_chords.append(
                [self.scale.scale[i + interval] for interval in intervals]
            )

    def __repr__(self) -> str:
        out = ""
        for i, chords in enumerate(self.raw_chords):
            out = (
                out + " ".join(chords) + ("" if i == len(self.raw_chords) - 1 else "\n")
            )
        return out


class _IntervalChords(_RawChords):
    def __init__(self, scale=Scale, seventh=False) -> None:
        super().__init__(scale, seventh)
        self.chords_intervals = []
        for chord in self.raw_chords:
            self.chords_intervals.append(
                [get_interval(i, j) for i, j in zip(chord[:-1], chord[1:])]
            )

    def __repr__(self) -> str:
        out = ""
        for i, chords in enumerate(self.chords_intervals):
            out = (
                out
                + " ".join(map(str, chords))
                + ("" if i == len(self.chords_intervals) - 1 else "\n")
            )
        return out


class Chords(_IntervalChords):
    def __init__(self, scale=Scale, seventh=False) -> None:
        super().__init__(scale, seventh)
        self._get_chords()
        self._get_roman_chords()

    def _get_chords(self):
        self.chords = []
        for root, chord in zip(self.scale.scale, self.chords_intervals):
            self.chords.append(root + AVAIL_CHORDS[tuple(chord)])

    def _get_roman_chords(self):
        self.roman_chords = []
        for i, chord in enumerate(self.chords_intervals):
            roman = ROMANS[i]
            chord_flavour = AVAIL_CHORDS[tuple(chord)]
            if "-" in chord_flavour:
                chord_flavour = chord_flavour[1:]
                roman = roman.lower()
            self.roman_chords.append(roman + chord_flavour)

    def __repr__(self) -> str:
        out = "\t".join(self.roman_chords) + "\n"
        out += "\t".join(self.chords)
        return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=C)
    parser.add_argument("--base_scale", default=MAJOR)
    parser.add_argument("--mode", default=3)
    args = parser.parse_args()
    scale = Scale(args.root, args.base_scale, args.mode)
    print(scale)
    print(Chords(scale, True))
