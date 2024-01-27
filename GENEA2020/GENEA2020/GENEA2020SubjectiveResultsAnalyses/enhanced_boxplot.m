% A boxplot command that plots means and cofidence intervals,
% bases whiskers on quantiles, and colours outliers differently.
% It also returns means, median, and success (value>0) probability stats.
% 
% (c) Gustav Eje Henter 2019-05-04

function allstats = enhanced_boxplot(plotdata,labels,...
    whiskerq,plotmean,outliersymbol,jitterfrac,alpha,varargin)

removenan = true;
meancolnum = 3;
meansymbol= 'd';

confxoffset = 1/6; % Relative to box width

if (nargin < 1) || ~isnumeric(plotdata) || isempty(plotdata)
    return;
end

[nsamples,ngroups] = size(plotdata);

alreadygrouped = false;
if (nargin < 2) || isempty(labels)
    labels = strread(num2str(1:ngroups),'%s');
elseif (ngroups == 1) && (size(labels,1) == numel(plotdata))
    labels = cellstr(labels);
    alreadygrouped = true;
end

if ~alreadygrouped
    groupdata = mat2cell(plotdata,nsamples,ones(1,ngroups));
    alldata = reshape(plotdata,1,[]);
    groupstrs = labels(reshape(ones(nsamples,1)*(1:ngroups),1,[]));
    nsamples = nsamples*ones(1,ngroups);
else
    groupstrs = labels;
    labels = unique_nosort(groupstrs);
    ngroups = numel(labels);
    alldata = plotdata;
    
    groupdata = cell(1,ngroups);
    nsamples = zeros(1,ngroups);
    for gn = 1:ngroups
        groupdata{gn} = alldata(...
            cellfun(@(gs) (strcmp(gs,labels{gn})),groupstrs));
        nsamples(gn) = numel(groupdata{gn});
    end
end
clear plotdata;

if (nargin < 3) || ~isnumeric(whiskerq) || isempty(whiskerq)
    whiskerq = [0.05;0.95];
elseif numel(whiskerq) < 2
    whiskerq = max(0,min(whiskerq,1-whiskerq));
    whiskerq = [whiskerq;1-whiskerq];
else
    whiskerq = whiskerq(1:2);
end

if (nargin < 4) || isempty(plotmean)
    plotmean = true;
end

if (nargin < 5) || ~ischar(outliersymbol)
    outliersymbol = '+';
end

if (nargin < 6) || ~isnumeric(jitterfrac) || isempty(jitterfrac)
    jitterfrac = 0.5; % Relative to box width
end

if removenan
    for gn = 1:ngroups
        groupdata{gn} = groupdata{gn}(~isnan(groupdata{gn}));
        nsamples(gn) = numel(groupdata{gn});
    end
end

if (nargin < 7) || ~isnumeric(alpha) || isempty(alpha)
    alpha = 0; % Relative to box width
end

boxplot(alldata,groupstrs,'Symbol','',varargin{:});
hold on;

% Compute statistics
[gmeans,gmedians,gprefs] = deal(zeros(1,ngroups));
[gwhiskervals,gmeanconfs,gmedianconfs,gprefconfs] = deal(zeros(2,ngroups));
goutliers = cell(1,ngroups);
for gn = 1:ngroups
    gdata = groupdata{gn};
    gmeans(gn) = mean(gdata);
    gmedians(gn) = median(gdata);
    gprefs(gn) = sum(gdata > 0)/sum(gdata ~= 0); % Ignore ties
    if alpha > 0
        [gmeanconfs(:,gn),gmedianconfs(:,gn),gprefconfs(:,gn)]...
            = confints(gdata,alpha);
    end
    gwhiskervals(:,gn) = quantile(gdata,whiskerq);
    mask = (gdata < gwhiskervals(1,gn)) | (gdata > gwhiskervals(2,gn));
    goutliers{gn} = gdata(mask);
end

allstats = [gmeans;gmeanconfs;gmedians;gmedianconfs;gprefs;gprefconfs]';

setwhiskers(gwhiskervals);

xcoords = findboxxcoords;

if alpha > 0
    errorbar((1:ngroups) - confxoffset*diff(xcoords),gmedians,...
        gmedians-gmedianconfs(1,:),gmedianconfs(2,:)-gmedians,...
        'r','LineStyle','none');
end

cols = get(gca,'ColorOrder');
if plotmean
    if alpha > 0
        errorbar((1:ngroups) + confxoffset*diff(xcoords),gmeans,...
            gmeans-gmeanconfs(1,:),gmeanconfs(2,:)-gmeans,...
            meansymbol,'Color',cols(meancolnum,:));
    else
        plot((1:ngroups),gmeans,meansymbol,'Color',cols(meancolnum,:));
    end
end

if ~isempty(outliersymbol)
    for gn = 1:ngroups
        outlierys = goutliers{gn};
        outlierxs = mean(xcoords(:,gn))...
            + jitterfrac*diff(xcoords(:,gn))*(rand(size(outlierys)) - 0.5);
        plot(outlierxs,outlierys,outliersymbol,'Color',cols(3,:));
    end
end

hold off;

function outvar = unique_nosort(invar)

[~,firstindices] = unique(invar,'first');
outvar = invar(sort(firstindices));

function setwhiskers(gwhiskervals)
% Adapted from http://uk.mathworks.com/matlabcentral/newsreader/view_thread/310839

% Replace upper end y value of whisker
h = flipud(findobj(gca,'Tag','Upper Whisker'));
for j=1:length(h)
    ydata = get(h(j),'YData');
    ydata(2) = gwhiskervals(2,j);
    set(h(j),'YData',ydata);
end

% Replace all y values of adjacent value
h = flipud(findobj(gca,'Tag','Upper Adjacent Value'));
for j=1:length(h)
    ydata = get(h(j),'YData');
    ydata(:) = gwhiskervals(2,j);
    set(h(j),'YData',ydata);
end

% Replace lower end y value of whisker
h = flipud(findobj(gca,'Tag','Lower Whisker'));
for j=1:length(h)
    ydata = get(h(j),'YData');
    ydata(1) = gwhiskervals(1,j);
    set(h(j),'YData',ydata);
end

% Replace all y values of adjacent value
h = flipud(findobj(gca,'Tag','Lower Adjacent Value'));
for j=1:length(h)
    ydata = get(h(j),'YData');
    ydata(:) = gwhiskervals(1,j);
    set(h(j),'YData',ydata);
end

function xcoords = findboxxcoords

h = flipud(findobj(gca,'Tag','Box'));

xcoords = zeros(2,numel(h));
for j=1:length(h)
    xdata = get(h(j),'XData');
    xcoords(1,j) = min(xdata);
    xcoords(2,j) = max(xdata);
end

function [gmeanconfs,gmedianconfs,gprefconfs] = confints(gdata,alpha)

ngd = numel(gdata);
gmean = mean(gdata);
gstd = std(gdata);

gmeanconfs = repmat(gmean,[1 2])...
    + tinv([alpha/2,1-alpha/2],ngd-1)*gstd/sqrt(ngd);

sortgdata = sort(gdata);
medianinds = [-1,1]*binoinv(1-alpha/2,ngd,0.5) + [ngd,0];
gmedianconfs = sortgdata(round(medianinds));

% Clopper-Pearson binomial confidence interval ignoring ties
[~,gprefconfs] = binofit(sum(gdata > 0),sum(gdata ~= 0),alpha);