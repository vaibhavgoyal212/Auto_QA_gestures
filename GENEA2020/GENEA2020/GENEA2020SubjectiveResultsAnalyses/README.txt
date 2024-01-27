README.txt file for the GENEA Challenge 2020 subjective evaluation data release

This zip archive contains the user-study results and their analysis from the GENEA Challenge 2020 (https://genea-workshop.github.io/2020/#gesture-generation-challenge). The code was written by Gustav Eje Henter and is released under a Creative Commons Attribution 4.0 International (CC BY 4.0) license.

The archive contains contains:
* This README.txt file.
* A LICENSE.txt file.
* Two JSON files containing all user-study responses included in the analysis.
* Matlab .m files for reproducing the above analysis (both tables and figures).
* A folder called "output" that contains all files written by the analysis script, along with files created when compiling the final, pretty-looking pdf figures. Code for the results table is not included in this folder since that's displayed/printed as raw text in the Matlab Command Window when running the analyses.

To re-generate/reproduce the contents in the "output" folder first run through the entire analysis script "run_analyses.m", and then run the LaTeX utility fragmaster (https://ctan.org/pkg/fragmaster) in the "output" folder. This was last tested on 2020-10-14 on MATLAB version 9.4.0.813654 (R2018a).

If you have any questions or comments, please contact:
* Gustav Eje Henter <ghe@kth.se>
* The GENEA Challenge & Workshop organisers <genea-contact@googlegroups.com>