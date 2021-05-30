#!/usr/bin/env python
# Copyright (c) 2012-2013 Kyle Gorman <gormanky@ohsu.edu>
#
# Made this work for eSpeak IPA output (C. Rice) 2021/05/25
# as syllabifyIPA.py
#   Note: eSpeak should be set to --ipa=3 (underscore separators) to 
#   facilitate keeping stress as part of the vowel info.
#   in Arpabet, 1=primary, 2=secondary, 0=none, AH0 = schwa
#   Note: Rhotic vowels are units in eSpeak, so they had to be added to 
#   the list of vowels here.
#   Note: pprint changed to print consonant clusters w/o spaces.  
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# syllabify_ipa.py: prosodic parsing of eSpeak ipa transcription

from itertools import chain

## constants
SLAX   = {'ˈɪ', 'ˌɪ', 'ˈɛ', 'ˌɛ', 'ˈæ', 'ˌæ', 'ˈʌ', 'ˌʌ', 'ˈʊ', 'ˌʊ'}
VOWELS = {'ˈiː', 'ˌiː', 'iː', 'ˈeɪ', 'ˌeɪ', 'eɪ', 'ˈɑː', 'ˌɑː', 'ɑː',
          'ˈɜː', 'ˌɜː', 'ɜː', 'ˈaʊ', 'ˌaʊ', 'aʊ', 'ˈɔː', 'ˌɔː', 'ɔː',
          'ˈaɪ', 'ˌaɪ', 'aɪ', 'ˈoʊ', 'ˌoʊ', 'oʊ', 'ˈɔɪ', 'ˌɔɪ', 'ɔɪ',
          'ˈuː', 'ˌuː', 'uː', 'i', 'ɪ', 'ɛ', 'æ', 'ʌ', 'ə', 'ʊ', 'ɐ', 
		  'ˈaɪə', 'ˈaɪʊɹ', 'ˈɑːɹ', 'ɚ', 'ˈɛɹ', 'ˈɪɹ', 'ˈʊɹ', 'ˈɔːɹ', 
		  'ˈoːɹ', 'əl', 'ˈoː', 'iə',} | SLAX

## licit medial onsets

O2 = {('p', 'ɹ'), ('t', 'ɹ'), ('k', 'ɹ'), ('b', 'ɹ'), ('d', 'ɹ'),
      ('ɡ', 'ɹ'), ('f', 'ɹ'), ('θ', 'ɹ'),
      ('p', 'l'), ('k', 'l'), ('b', 'l'), ('ɡ', 'l'),
      ('f', 'l'), ('s', 'l'),
      ('k', 'w'), ('ɡ', 'w'), ('s', 'w'),
      ('s', 'p'), ('s', 't'), ('s', 'k'),
      ('h', 'j'), # "clerihew"
      ('ɹ', 'w'),}
O3 = {('s', 't', 'ɹ'), ('s', 'k', 'l'), ('t', 'ɹ', 'w')} # "octroi"

# This does not represent anything like a complete list of onsets, but
# merely those that need to be maximized in medial position.

def syllabify(pron, alaska_rule=True):
    """
    Syllabifies an eSpeak --ipa=3 word string
    # Alaska rule:
    >>> pprint(syllabify('ɐ_l_ˈæ_s_k_ə'.split('_'))) # Alaska
    '-ɐ-.l-ˈæ-s.k-ə-'
    >>> pprint(syllabify('ɐ_l_ˈæ_s_k_ə'.split('_'), 0)) # Alaska
    '-ɐ-.l-ˈæ-.s k-ə-'
    # huge medial onsets:
    >>> pprint(syllabify('m_ˈɪ_n_s_t_ɹ_əl'.split('_'))) # minstrel
    'm-ˈɪ-n.stɹ-əl-'
    >>> pprint(syllabify('ˈɑː_k_t_ɹ_ɔɪ'.split('_'))) # octroi
    '-ˈɑː-k.tɹ-ɔɪ-'
    # destressing
    >>> pprint(destress(syllabify('m_ˈɪ_l_ə_t_ˌɛ_ɹ_i'.split('_'))))
    'm-ɪ-.l-ə-.t-ɛ-.ɹ-i-'
    # normal treatment of 'j':
    >>> pprint(syllabify('m_ˈɛ_n_j_uː'.split('_'))) # menu
    'M-EH1-N.Y-UW0-'
    >>> pprint(syllabify('s_p_ˈæ_n_j_əl'.split('_'))) # spaniel
    'sp-ˈæ-n.j-əl-'
    >>> pprint(syllabify('k_ˈæ_n_j_ə_n'.split('_'))) # canyon
    'k-ˈæ-n.j-ə-n'
    >>> pprint(syllabify('m_ˌɪ_n_j_uː_ˈɛ_t'.split('_'))) # minuet
    'm-ˌɪ-n.j-uː-.-ˈɛ-t'
    >>> pprint(syllabify('dʒ_ˈuː_n_j_ɚ'.split('_'))) # junior
    'dʒ-ˈuː-n.j-ɚ-'
    >>> pprint(syllabify('k_l_ˈɛ_ɹ_ɪ_h_j_ˌuː'.split('_'))) # clerihew
    'kl-ˈɛ-.ɹ-ɪ-.hj-ˌuː-'
    # nuclear treatment of 'j'
    >>> pprint(syllabify('ɹ_ˈɛ_s_k_j_uː'.split('_'))) # rescue
    'ɹ-ˈɛ-s.k-juː-' 
    >>> pprint(syllabify('t_ɹ_ˈɪ_b_j_uː_t'.split('_'))) # tribute
    'tɹ-ˈɪ-b.j-uː-t'
    >>> pprint(syllabify('N EH1 B Y AH0 L AH0'.split())) # nebula
    'N-EH1-B.Y-AH0-.L-AH0-'
    >>> pprint(syllabify('S P AE1 CH UH0 L AH0'.split())) # spatula
    'S P-AE1-.CH-UH0-.L-AH0-'
    >>> pprint(syllabify('AH0 K Y UW1 M AH0 N'.split())) # acumen
    '-AH0-K.Y-UW1-.M-AH0-N'
    >>> pprint(syllabify('S AH1 K Y AH0 L IH0 N T'.split())) # succulent
    'S-AH1-K.Y-AH0-.L-IH0-N T'
    >>> pprint(syllabify('F AO1 R M Y AH0 L AH0'.split())) # formula
    'F-AO1 R-M.Y-AH0-.L-AH0-'
    >>> pprint(syllabify('V AE1 L Y UW0'.split())) # value
    'V-AE1-L.Y-UW0-'
    # everything else
    >>> pprint(syllabify('n_ə_s_t_ˈæ_l_dʒ_ɪ_k'.split('_'))) # nostalgic
    'n-ə-.st-ˈæ-l.dʒ-ɪ-k'
    >>> pprint(syllabify('CH ER1 CH M AH0 N'.split())) # churchmen
    'CH-ER1-CH.M-AH0-N'
    >>> pprint(syllabify('K AA1 M P AH0 N S EY2 T'.split())) # compensate
    'K-AA1-M.P-AH0-N.S-EY2-T'
    >>> pprint(syllabify('IH0 N S EH1 N S'.split())) # inCENSE
    '-IH0-N.S-EH1-N S'
    >>> pprint(syllabify('IH1 N S EH2 N S'.split())) # INcense
    '-IH1-N.S-EH2-N S'
    >>> pprint(syllabify('AH0 S EH1 N D'.split())) # ascend
    '-AH0-.S-EH1-N D'
    >>> pprint(syllabify('R OW1 T EY2 T'.split())) # rotate
    'R-OW1-.T-EY2-T'
    >>> pprint(syllabify('AA1 R T AH0 S T'.split())) # artist
    '-AA1 R-.T-AH0-S T'
    >>> pprint(syllabify('AE1 K T ER0'.split())) # actor
    '-AE1-K.T-ER0-'
    >>> pprint(syllabify('P L AE1 S T ER0'.split())) # plaster
    'P L-AE1-S.T-ER0-'
    >>> pprint(syllabify('b_ˈʌ_ɾ_ɚ'.split('_'))) # butter
    'b-ˈʌ-.ɾ-ɚ-'
    >>> pprint(syllabify('k_ˈæ_m_əl'.split('_'))) # camel
    'k-ˈæ-.m-əl-'
    >>> pprint(syllabify('ˈʌ_p_ɚ'.split('_'))) # upper
    '-ˈʌ-.p-ɚ-'
    >>> pprint(syllabify('b_ə_l_ˈuː_n'.split('_'))) # balloon
    'b-ə-.l-ˈuː-n'
    >>> pprint(syllabify('p_ɹ_ə_k_l_ˈeɪ_m'.split('_'))) # proclaim
    'pɹ-ə-.kl-ˈeɪ-m'
    >>> pprint(syllabify('ɪ_n_s_ˈeɪ_n'.split('_'))) # insane
    '-ɪ-n.s-ˈeɪ-n'
    >>> pprint(syllabify('ɛ_k_s_k_l_ˈuː_d'.split('_'))) # exclude
    '-ɛ-k.skl-ˈuː-d'
    """
    ## main pass
    mypron = list(pron)
    nuclei = []
    onsets = []
    i = -1
    for (j, seg) in enumerate(mypron):
        if seg in VOWELS:
            nuclei.append([seg])
            onsets.append(mypron[i + 1:j]) # actually interludes, r.n.
            i = j
    codas = [mypron[i + 1:]]
    ## resolve disputes and compute coda
    for i in range(1, len(onsets)):
        coda = []
        # boundary cases
        if len(onsets[i]) > 1 and onsets[i][0] == 'ɹ':
            nuclei[i - 1].append(onsets[i].pop(0))
        if len(onsets[i]) > 2 and onsets[i][-1] == 'j':
            nuclei[i].insert(0, onsets[i].pop())
        if len(onsets[i]) > 1 and alaska_rule and nuclei[i-1][-1] in SLAX \
                                              and onsets[i][0] == 's':
            coda.append(onsets[i].pop(0))
        # onset maximization
        depth = 1
        if len(onsets[i]) > 1:
            if tuple(onsets[i][-2:]) in O2:
                depth = 3 if tuple(onsets[i][-3:]) in O3 else 2
        for j in range(len(onsets[i]) - depth):
            coda.append(onsets[i].pop(0))
        # store coda
        codas.insert(i - 1, coda)

    ## verify that all segments are included in the ouput
    output = list(zip(onsets, nuclei, codas))  # in Python3 zip is a generator
    flat_output = list(chain.from_iterable(chain.from_iterable(output)))
    if flat_output != mypron:
        raise ValueError(f"could not syllabify {mypron}, got {flat_output}")
    return output


def pprint(syllab):
    """
    Pretty-print a syllabification
    """
    return '.'.join('-'.join(''.join(p) for p in syl) for syl in syllab)


def destress(syllab):
    """
    Generate a syllabification with nuclear stress information removed
    """
    syls = []
    for (onset, nucleus, coda) in syllab:
        nuke = [p[1:] if p[0] in {'ˈ', 'ˌ'} else p for p in nucleus]
        syls.append((onset, nuke, coda))
    return syls


if __name__ == '__main__':
    import doctest
    doctest.testmod()