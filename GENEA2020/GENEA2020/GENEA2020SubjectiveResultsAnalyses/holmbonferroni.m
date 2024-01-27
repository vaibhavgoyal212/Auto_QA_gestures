% h0rej = holmbonferroni(pvals,alpha)
% Perform Holm-Bonferroni correction on multiple hypothesis tests
% Input:
% pvals = Matrix of individual test p-values
% alpha = Desired upper bound on the familywise error rate
% Output:
% h0rej = Matrix (same size as pvals) indicating null hypothesis rejections
% pcorr = Matrix (same size as pvals) of corrected p-values
% Note:
% A test is performed to see if pvals is symmetric. Symmetric matrices are
% given special treatment: only the part above the diagonal is tested, with
% the results subsequently copied below the diagonal as well.
%
% (c) Gustav Eje Henter 2019, 2020-10-09

function [h0rej,pcorr] = holmbonferroni(pvals,alpha)

psize = size(pvals);

issym = (psize(1) > 0) && (psize(1) == psize(2))...
    && all(all(abs(pvals - pvals') == 0)) && (numel(pvals) ~= 1);

if issym
    n = psize(1);
    nhyp = n*(n-1)/2;
    pvals(tril(true(psize),0)) = -1;
    [pvals,porder] = sort(pvals(:));
    pvals = pvals(end-nhyp+1:end);
    porder = porder(end-nhyp+1:end);
else
    nhyp = numel(pvals);
    [pvals,porder] = sort(pvals(:));
end

sortedrej = (pvals < alpha./(nhyp:-1:1)');
sortedpcorr = cummax((nhyp:-1:1)'.*pvals);
sortedpcorr = min(sortedpcorr,1);

if ~all(sortedrej)
    k = find(~sortedrej,1,'first');
    sortedrej(1:k-1) = true;
    sortedrej(k:end) = false;
end

if issym
    h0rej = false(psize);
    h0rej(porder) = sortedrej;
    h0rej = h0rej | h0rej';
    
    pcorr = zeros(psize);
    pcorr(porder) = sortedpcorr;
    pcorr = pcorr + pcorr';
    pcorr = pcorr + eye(psize);
else
    h0rej(porder) = sortedrej;
    h0rej = reshape(h0rej,psize);
    
    pcorr(porder) = sortedpcorr;
    pcorr = reshape(pcorr,psize);
end

function x = cummax(x)

for i = 2:numel(x)
    x(i) = max(x(i-1),x(i));
end