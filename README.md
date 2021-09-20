# EMRoberts

We are working on analyzing rhyme patterns in Elizabeth Madox Roberts' early book of poems, Under the Tree. It's a good test case because it's basic. The text included in the text file is adapted from the .txt at Project Gutenberg. 

Most of the work is in Jupyter notebooks. The fixUnder notebook takes the basic book text, makes it into proto-xml, and publishes it to the text/Under folder as individual poems.

The Rhyme_Markup notebook grabs an individual poem, puts it through eSpeak (externally), then adds information in an xml way to the poem: the phonetic rendering of each line, the rhyming syllable, its CV pattern, its characterization as strong or weak, and the rhyme label for each line in the familiar AB notation.

The syllabify_ipa.py file is intended as a module. The existing syllabify module, written for the CMU dictionary, has been made to work for the IPA transciptions that eSpeak produces. It is probably incomplete due to how the two programs handle rhotacized vowels differently. For eSpeak they all have to be added by hand to the VOWELS list. We won't know it's complete until we stop getting errors in syllabification due to missing vowels. They have slowed considerably.

The ttr-test notebook is a short routine that runs a text through eSpeak and then through syllabify and returns both transcriptions. I've been using it to check words and phrases for debugging.

The Text-To-Speech notebook was for class. It shows how to download and install eSpeak and how to use it from the command line. To run ttr-test you will need to have eSpeak set up in a folder you can access.
