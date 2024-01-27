% Code to analyse test results
% (c) Gustav Eje Henter 2014, 2015, 2016, 2018, 2019, 2020

function analyse_test_data(infile,outpath,typestr,...
    pval,nexp,labelstrs,neworder,includesubj)

converttoranks = false;
normaliserange = false;
normalisefixed = [];
prunetype = 0; % 0 => no pruning; 1 => prune ref=0; 2 => prune ref<100

showsubjbox = false; % Set to true to plot each subject's ratings

whiskerq = 0.025; % Fraction of datapoints outside each whisker
showboxmeans = true; % Show squares for means in box plot
showboxmconfs = true; % Show confidence intervals in box plot
%outliersymbol = '+'; % Set to '' to disable plotting outliers
outliersymbol = '';
jitterfrac = 0.5;
bpfontsize = 14;
xangle = 0; % Rotation angle for system labels on x-axis

aspect = 4/3;
%aspect = 4/2;

% Permute variables to use new order

ncond = numel(neworder);

labelstrs = labelstrs(neworder);

invorder(neworder) = (1:ncond);

jsn = jsondecode(fileread(infile));
subjects = [jsn.trials(:).participant_id];

nsubj = numel(unique(subjects));

subjresults = zeros(nexp,ncond,nsubj);
allresults = [];

for n = 1:nsubj
    subjresults(:,:,n) = json2result(jsn.trials(subjects == n),labelstrs);
    
    if showsubjbox
        enhanced_boxplot(subjresults(:,:,n),labelstrs,...
            whiskerq,showboxmeans,outliersymbol,jitterfrac);
        
        axis([0.5 (ncond+0.5) 0 100]);
        title(['Subject number ' int2str(n)]);
        
        subjmultimin = sum(sum(subjresults(:,:,n) == 0,2) > 1);
        subjmultimax = sum(sum(subjresults(:,:,n) == 100,2) > 1);
        if (subjmultimin > 0) || (subjmultimax > 0)
            disp(['Subject number: ' int2str(n)]);
            disp(['Number of screens with more than one 100 rating: '...
                int2str(subjmultimax)]);
            disp(['Number of screens with more than one   0 rating: '...
                int2str(subjmultimin)]);
        end
        
        disp('Paused. Press any key to continue...');
        pause;
    end
    
    if includesubj(n)
        allresults = [allresults;subjresults(:,:,n)];
    end
end

% Pruna and process data

unnat = (allresults(:,1) == 0);
incorr = (allresults(:,1) < 100); % No system rated as perfectly natural

if (prunetype == 2)
    corrresults = allresults(~incorr,:); % Only use screens where natural == 100
elseif (prunetype == 1)
    corrresults = allresults(~unnat,:); % Only use screens where natural > 0
else
    corrresults = allresults; % Use all screens/pages
end

nkept = sum(includesubj);
nretained = size(corrresults,1);

% Round to integer and limit range
nanmask = isnan(corrresults);
corrresults = round(corrresults);
corrresults = max(0,corrresults);
corrresults = min(100,corrresults);

corrresults(nanmask) = NaN;

scalerange = [0 100];

% Convert to ranks
if converttoranks
    for n = 1:nretained
        corrresults(n,:) = tiedrank(corrresults(n,:));
    end
    scalerange = [1 ncond];
end

% Scale normalisation
if ~isempty(normalisefixed)
    % "Fixed" normalisation
    mincr = corrresults(:,normalisefixed(1));
    maxcr = corrresults(:,normalisefixed(2));
    
    corrresults = 100*(corrresults - repmat(mincr,1,ncond))...
        ./repmat(maxcr - mincr,1,ncond);
elseif normaliserange
    
    % Adaptive normalisation
    mincr = min(corrresults,[],2);
    maxcr = max(corrresults,[],2);
    
    corrresults = 100*(corrresults - repmat(mincr,1,ncond))...
        ./repmat(maxcr - mincr,1,ncond);
end

% Create output directory
if ~exist(outpath,'dir')
    mkdir('.',outpath);
end

% Create a boxplot of ratings and confidence intervals
clf;
absstats = enhanced_boxplot(corrresults(:,1:end),labelstrs(1:end),...
    whiskerq,showboxmeans,outliersymbol,jitterfrac,pval*showboxmconfs);

axis([0.5 (ncond + 0.5) scalerange]);

xtickangle(xangle);

set(gca,'FontSize',bpfontsize);
txts = findobj(gca,'Type','text');
set(txts,'FontSize',bpfontsize);
set(txts,'VerticalAlignment','Middle');
clear txts;

if ~converttoranks
    if normaliserange
        ylabel('Normalised appropriateness rating','FontSize',bpfontsize);
    else
        ylabel('Appropriateness rating','FontSize',bpfontsize);
    end
else
    ylabel('Appropriateness rank (highest is best)','FontSize',bpfontsize);
end

saveas(gcf,[outpath filesep typestr '_boxplot.fig'],'fig');
%saveas(gcf,[outpath filesep typestr '_boxplot.eps'],'epsc');

fig2fm([outpath filesep typestr '_boxplot'],'article',...
    'a4paper,british,12pt',17,aspect,9,[],[],5,[],[],true);

% Perform statistical analysis of system pairs
[numcmps,dmean,dmedian,nxgty] = deal(zeros(ncond));
[pt,pwilc,pmwu,psgn,prefnoties] = deal(eye(ncond)/2);

for c1 = 1:ncond
    for c2 = (c1+1):ncond
        ds = corrresults(:,c1) - corrresults(:,c2);
        numcmps(c1,c2) = sum(~isnan(ds));
        ds = ds(~isnan(ds));
        
        dmean(c1,c2) = mean(ds);
        dmedian(c1,c2) = median(ds);
        
        validpairs = [corrresults(:,c1),corrresults(:,c2)];
        validpairs = validpairs(~any(isnan(validpairs),2),:);
        
        [~,pt(c1,c2)] = ttest(validpairs(:,1),validpairs(:,2));
        [pwilc(c1,c2)] = signrank(validpairs(:,1),validpairs(:,2));        
        [pmwu(c1,c2)] = ranksum(validpairs(:,1),validpairs(:,2));
        
        nxgty(c1,c2) = sum(validpairs(:,1) > validpairs(:,2));
        nxgty(c2,c1) = sum(validpairs(:,1) < validpairs(:,2));
        
        nxy = nxgty(c1,c2) + nxgty(c2,c1);
        minxy = min(nxgty(c1,c2),nxgty(c2,c1));
        [psgn(c1,c2)] = binocdf(minxy,nxy,0.5)...
            + binocdf(nxy - minxy,nxy,0.5,'upper');
        
        prefnoties(c1,c2) = nxgty(c1,c2)/nxy;
        prefnoties(c2,c1) = nxgty(c2,c1)/nxy;
    end
end

mincmps = min(numcmps(numcmps > 0)),
maxcmps = max(numcmps(numcmps > 0)),
numcmps = numcmps + numcmps';

dmean = dmean - dmean';
dmedian = dmedian - dmedian';

prefties = nxgty./nretained + eye(ncond)./2;
effsizesgn = prefties - prefties';

pt = pt + pt';
pwilc = pwilc + pwilc';
pmwu = pmwu + pmwu';
psgn = psgn + psgn';

ncmp = ncond*(ncond-1)/2;
[rejt,pcorrt] = holmbonferroni(pt,pval);
[rejwilc,pcorrwilc] = holmbonferroni(pwilc,pval);
[rejmwu,pcorrmwu] = holmbonferroni(pmwu,pval);
[rejsgn,pcorrsgn] = holmbonferroni(psgn,pval);

triumask = triu(true(ncond),1);

% Plot the distribution of p-values for differernt tests
semilogy(1:ncmp,sort(pcorrt(triumask(:)),'descend'),'-',...
    1:ncmp,sort(pcorrwilc(triumask(:)),'descend'),'-',...
    1:ncmp,sort(pcorrmwu(triumask(:)),'descend'),'-',...
    1:ncmp,sort(pcorrsgn(triumask(:)),'descend'),'-');
hold on;
semilogy([1 ncmp],pval*[1 1],'k:');
hold off;

curraxis = axis;
axis([1 ncmp 10e-8 1]);

xlabel('Pair comparison number (sorted)');
ylabel('Corrected p-value');
legend('Location','NorthEast',...
    't-test','Wilcoxon signed-rank','Mann-Whitney U','Sign test',...
    'Limit of significance');

saveas(gcf,[outpath filesep typestr '_corr_pvals.fig'],'fig');
saveas(gcf,[outpath filesep typestr '_corr_pvals.eps'],'epsc');

%pcorrwilc, % Holm-Bonferroni corrected Wilcoxon signed-rank test p-values

% Print the results of the statistical tests and their differences

rejwilc, % Show a matrix of rejected Wilcoxon signed rank null hypotheses

disp('Non-significant pairs (Wilcoxon signed-rank test):');
flaggedpairs(~rejwilc,labelstrs,true);

if ~converttoranks
    twilcdisagree = rejt - rejwilc,
    disp('Pairs where Wilcoxon signed-rank test and t-test disagree:');
    flaggedpairs(twilcdisagree,labelstrs,true);
end

if converttoranks || normaliserange
    mwuwilcdisagree = rejmwu - rejwilc,
    disp(['Pairs where Wilcoxon signed-rank test '...
        'and Mann-Whitney U test disagree:']);
    flaggedpairs(mwuwilcdisagree,labelstrs,true);
end

sgnwilcdisagree = rejsgn - rejwilc,
disp('Pairs where Wilcoxon signed-rank test and sign test disagree:');
flaggedpairs(sgnwilcdisagree,labelstrs,true);

% Display system differences graphically

clf;
imagesc(sign(rejwilc.*dmedian));

colormap(gca,'gray');
%colorbar;

set(gca,'XTick',1:ncond);
set(gca,'XTickLabel',labelstrs);
set(gca,'YTick',1:ncond);
set(gca,'YTickLabel',labelstrs);

ylabel('Significant preference for system $y$...','FontSize',bpfontsize);
xlabel('...over system $x$, in terms of appropriateness','FontSize',bpfontsize);

xtickangle(xangle);

set(gca,'FontSize',bpfontsize);
txts = findobj(gca,'Type','text');
set(txts,'FontSize',bpfontsize);
set(txts,'VerticalAlignment','Middle');
clear txts;

curraxis = axis;
hold on;
plot(curraxis(1:2),curraxis(3:4),'k-');
hold off;

saveas(gcf,[outpath filesep typestr '_median_pref.fig'],'fig');
%saveas(gcf,[outpath filesep typestr '_median_pref.eps'],'epsc');
saveas(gcf,[outpath filesep typestr '_median_pref.png'],'png');

fig2fm([outpath filesep typestr '_median_pref'],'article',...
    'a4paper,british,12pt',17,aspect,9,[],[],5,[],[],true,false);

%prefnoties, % Print empirical preferences after removing ties
%effsizesgn, % Print signed effect size

% The last output is the signed effect size. See this article for details: 
% D. S. Kerby, "The simple difference formula: an approach to teaching 
% nonparametric correlation," Comprehensive Psychology, vol. 3, 2014.

save([outpath filesep typestr '_json_analysis.mat']); % Save results