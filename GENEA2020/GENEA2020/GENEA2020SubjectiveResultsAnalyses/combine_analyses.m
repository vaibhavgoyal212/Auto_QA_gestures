% Code to plot two test results together
% (c) Gustav Eje Henter 2020

function combine_analyses(outpath,labelstrs,sortorder)

plotdiag = true;
edgestyle = '-';

%dispaxis = [0 100 0 100];
dispaxis = [30 90 30 90];

%legendloc = 'NorthWest';
legendloc = 'SouthEast';
boxon = true;
copyx = true;

aspect = 4/3;
%aspect = 4/2;

% Loosely based on Boynton (1989)
colororder = [0,0,0;...
    128,128,128;...
    0,255,0;...
    255,0,0;...
    247,248,0;...%255,255,0;...
    0,0,255;...
    128,0,0;...
    255,0,255;...
    255,128,128];

edgecols = (5:6);
midcol = 4;

bpfontsize = 14;

% Load processed data from the two tests
xstats = load_absstats([outpath filesep...
    'human-likeness_json_analysis.mat'],labelstrs([1,(3:end)]));
xlbl = 'Human-likeness';

ystats = load_absstats([outpath filesep...
    'appropriateness_json_analysis.mat'],labelstrs);
ylbl = 'Appropriateness';

% Deal with the fact that condition M was missing from one test
numsys = size(ystats,1);
xtrastats = zeros(size(ystats,1) - size(xstats,1),size(xstats,2));
if ~copyx
    xtrastats(:,edgecols(1)) = 0;
    xtrastats(:,edgecols(2)) = 100;
    xtrastats(:,midcol) = mean(dispaxis(1:2));
    xstr = 'no_x';
else
    boxon = false;
    xtrastats = repmat(xstats(1,:),[size(xtrastats,1),1]); % Bit of a hack
    xstr = 'copy_x';
end
xstats = [xstats(1,:);xtrastats;xstats(2:end,:)];

% Reorder systems, if desired
xstats = xstats(sortorder,:);
ystats = ystats(sortorder,:);
labelstrs = labelstrs(sortorder);

colororder = colororder(sortorder,:);
colororder = colororder/255;

clf;

hold on;
for s = 1:numsys
    plot(xstats(s,[edgecols([1 2 2 1 1])]),...
        ystats(s,[edgecols([1 1 2 2 1])]),...
        'Color',colororder(s,:),'LineStyle',edgestyle);
end

if plotdiag
    plot([0 100],[0 100],'k:');
end
hold off;

axis(dispaxis);

legend(labelstrs,'Location',legendloc);
if ~boxon
    legend boxoff;
end

xlabel(xlbl);
ylabel(ylbl);

set(gca,'FontSize',bpfontsize);
txts = findobj(gca,'Type','text');
set(txts,'FontSize',bpfontsize);
set(txts,'VerticalAlignment','Middle');
clear txts;

saveas(gcf,[outpath filesep 'joint_plot_' xstr '.fig'],'fig');
%saveas(gcf,[outpath filesep 'joint_plot_' xstr '.eps'],'epsc');

fig2fm([outpath filesep 'joint_plot_' xstr],'article',...
    'a4paper,british,12pt',17,aspect,9,[],[],5,[],[],true);

% Print basic LaTeX code for results table

disp('\begin{tabular}{@{}l|cc|cc@{}}');
disp('\toprule');
disp('& \multicolumn{2}{c|}{Human-likeness} & \multicolumn{2}{c}{Appropriateness}\\');
disp('ID & Median & Mean & Median & Mean\\');
disp('\midrule');
for s = 1:numsys
    fprintf(['%s & $%d\\in{}[%d,\\,%d]$ & $%.1f\\pm{}%.1f$ '...
        '& $%d\\in{}[%d,\\,%d]$ & $%.1f\\pm{}%.1f$\\\\\n'],labelstrs{s},...
        [xstats(s,(4:6)),round(xstats(s,1),1),...
        ceil(10*(xstats(s,3)-xstats(s,1)))/10,...
        ystats(s,(4:6)),round(ystats(s,1),1),...
        ceil(10*(ystats(s,3)-ystats(s,1)))/10]);
end
disp('\bottomrule');
disp('\end{tabular}');
disp(' ');

function absstats = load_absstats(resultsfile,truelabelstrs)

load(resultsfile,'absstats','labelstrs');

reorder = zeros(size(truelabelstrs));
for l = 1:numel(reorder)
    reorder(l) = find(strcmp(labelstrs,truelabelstrs{l}));
end

absstats = absstats(reorder,:);