# Fugue_Generator_v2
Updated version of project done for tracks course in music at Chalmers 2020. This repository adds some additional files and explanations and changes compared to the original project. 

 Original project can be found [here](https://github.com/JohannaWarnqvist/FugueGenerator)
 Note: Project requires installation of [Mingus](http://bspaans.github.io/python-mingus/)

# Fugues
We selected fugues for this music generation project since they have a relatively strict predetermined structure. A fugue is a type of composition popular during the baroque era. It is one of the techniques J.S. Bach is most known for. It uses counterpoint, a composing technique for multiple voices, where each voice has a meaningful melody, but still creates a pleasant sounding piece when played together. The fugue is characterized by having a motive, the subject, that returns throughout the piece. Our fugues includes typical elements such as exposition at the beginning of the piece, where the voices are introduced one by one, playing the subject. It also has parts where the subject is inverted, played ”backwards” and in different keys. In the end of the piece, there is a stretto, which is a canon on the subject.

# Implementation 
We used a python package called [Mingus](http://bspaans.github.io/python-mingus/) for note represenations to reduce the workload. To generate new music we combined the use of predetermined mathemathical functions applied on an input music subject with "original" music written by our evulutionary generator, a genetic algorithm, to produce a final fugue. Since the final fugue contains multiple voices playing over each other the deterministic part of the generation helped get more plesant sounding results in general. 

The genetic algorithm has a fully autonomous evaluation process where the generated pieces are evaluated on some predetermined metric we selected during the project that were suppose to reflect desierable aspects of the piece as well an desierable harmonies combined with the main subject. 

To generate final pieces the user has the option to either send in a short music piece that will be used as a subject or use a subject generated at random in a certain key. Some examples of generated music pieces can be found in the *Generated music folder*.
