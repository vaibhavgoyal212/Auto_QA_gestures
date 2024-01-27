% Code to analyse the test results from the GENEA Challenge 2020
% (c) Gustav Eje Henter 2014, 2015, 2016, 2018, 2019, 2020

% Set up variables

clear;

infile = 'appropriateness_test_data.json';
outpath = 'output';
typestr = 'appropriateness';

pval = 0.01;
%pval = 0.05;

nexp = 10;
nseg = 40;
%ignorepractice = true;

% Run analysis of appropriateness test

labelstrs = {'N','M','BA','BT','SA','SB','SC','SD','SE'};
neworder = [1 2 7 8 9 6 3 4 5]; % Sorted by sample median appropriateness

includesubj = true(1,125); % Set elements to false to exclude subjects

analyse_test_data(infile,outpath,typestr,...
    pval,nexp,labelstrs,neworder,includesubj);

%%

% Run analysis of human-likeness test

infile = 'human-likeness_test_data.json';
typestr = 'human-likeness';

neworder = [1 7 6 3 5 8 2 4]; % Sorted by sample median human-likeness

includesubj = true(1,125); % Set elements to false to exclude subjects

analyse_test_data(infile,outpath,typestr,...
    pval,nexp,labelstrs([1,(3:9)]),neworder,includesubj);

%%

% Produce joint plot and print LaTeX table

combine_analyses(outpath,labelstrs,(1:9));