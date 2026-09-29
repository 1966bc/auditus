# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""From a frequency to the name of the note, with how far off it is, in cents.

Equal temperament, tuned to A = 440 Hz: every semitone is a ratio of the
twelfth root of two, so the distance in semitones from the A is
12 * log2(f / 440). Rounded, it gives the nearest note; what is left, times
100, is the deviation in cents, the unit a tuner shows.

Two ways of numbering the octaves are in use. The scientific one, used in
English, starts each octave on C and calls the A at 440 Hz A4. The one used
in Italy and in France calls the same A La3: the same note, one octave
number lower. The names and the shift come from the language chosen.
"""

import math


class Pitch:
    """Note names for frequencies, in one naming convention."""

    #: The reference: the A above middle C.
    A4 = 440.0

    #: Semitones from C to A within an octave: C C# D D# E F F# G G# A.
    A_INDEX = 9

    def __init__(self, names, octave_shift):
        #: The twelve names from C, as the language writes them.
        self.names = names
        #: 0 for the scientific numbering, -1 for the Italian and French one.
        self.octave_shift = octave_shift

    def __str__(self):
        return "class: {0}".format(self.__class__.__name__)

    def get_note(self, frequency):
        """(name with octave, deviation in cents) of the nearest note: 110 Hz -> ('A2', 0)."""
        semitones = 12 * math.log2(frequency / self.A4)
        nearest = round(semitones)
        cents = round((semitones - nearest) * 100)
        # Counted from the C of octave 0, where the A of octave 4 is 57.
        index = nearest + self.A_INDEX + 12 * 4
        octave = index // 12 + self.octave_shift
        name = "{0}{1}".format(self.names[index % 12], octave)
        return name, cents
