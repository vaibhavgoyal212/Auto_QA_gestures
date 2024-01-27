% Print string (system) pairs flagged as true in binary, square matrix

% (c) Gustav Eje Henter 2016

function pairs = flaggedpairs(flagmat,labelstrs,doprint)

if (nargin < 3) || isempty(doprint),
    doprint = flase;
end

pairs = {};

nlbl = numel(labelstrs);

flagmat = flagmat' & flagmat;

for m = 1:(nlbl-1),
    for n = (m+1):nlbl,
        if flagmat(m,n),
            pairs{end+1,1} = ['(' labelstrs{m} ', ' labelstrs{n} ')'];
            if doprint,
                disp(pairs{end,1});
            end
        end
    end
end