% This function converts a MATLAB figure to a (custom) styled eps file
% and a set of commands for the psfrag utility fragmaster. This is
% extremely useful when creating figures for publications.
% 
% Gustav Eje Henter 2020-10-01

function fig2fm(figname,fmclass,fmclassopt,...
    cmwidth,aspect,fontpts,axiswidth,plotwidth,marksize,scaleall,...
    tickon,boxon,ynumeric,ieeetran)

if (nargin < 14) || isempty(ieeetran), ieeetran = false; end
if (nargin < 2) || isempty(fmclass)
    if ieeetran
        fmclass = 'IEEEtran';
    else
        fmclass = 'article';
    end
end
if (nargin < 3) || isempty(fmclassopt)
    if ieeetran
        %fmclassopt = ['a4paper,swedish,english,10pt'...
        %    ',journal,compsoc,peerreview,twoside'];
        fmclassopt = 'a4paper,english,10pt,journal,compsoc';
    else
        fmclassopt = 'english';
    end
end
if ieeetran
    if (nargin < 4) || isempty(cmwidth), cmwidth = 9; end
else
    if (nargin < 4) || isempty(cmwidth), cmwidth = 12.12364; end
end
if (nargin < 5) || isempty(aspect), aspect = 4/3; end
if (nargin < 6) || isempty(fontpts), fontpts = 10; end
if (nargin < 7) || isempty(axiswidth), axiswidth = 0.45; end
if (nargin < 8) || isempty(plotwidth), plotwidth = 0.7; end
if (nargin < 9) || isempty(marksize), marksize = 4; end
if (nargin < 10) || isempty(scaleall), scaleall = 1; end
if (nargin < 11) || isempty(tickon), tickon = true; end
if (nargin < 12) || isempty(boxon), boxon = false; end
if (nargin < 13) || isempty(ynumeric), ynumeric = true; end
%if (nargin < 14) || isempty(ieeetran), ieeetran = true; end % See above

cmwidth = scaleall*cmwidth;
fontpts = scaleall*fontpts;
axiswidth = scaleall*axiswidth;
plotwidth = scaleall*plotwidth;
marksize = scaleall*marksize;

header = {'% fragmaster file by fig2fm.m version 2020-10-01',...
    '% ',...
    '% Page and document setup:',...
    ['% fmopt: width=' num2str(cmwidth/scaleall) 'cm'],...
    ['% fmclass: ' fmclass],...
    ['% fmclassopt: ' fmclassopt],...
    '% ',...
    '% LaTeX preamble:',...
    '% head:',...
    '% \usepackage[english]{babel}',...
    '% \usepackage{amsmath}',...
    '% \usepackage{amssymb}',...
    '% \usepackage{fix-cm}',...
    '% \usepackage{fixltx2e}',...
    '% end head',...
    '',...
    '% psfrag commands:'};

%interpreter = get(0,'defaulttextinterpreter');
%set(0,'defaulttextinterpreter','none');

open([figname '.fig']);

fid = fopen([figname '_fm'],'w+');
if (fid <= -1)
    error(['Error opening file "' figname '_fm" for writing!']);
end

fprintf(fid,'%s\n',header{:});

%open([figname '.fig']); % Moved earlier than this in order to fail early

set(gcf,'PaperUnits','centimeters');
set(gcf,'PaperSize',[cmwidth cmwidth/aspect]);
set(gcf,'PaperPositionMode','manual');
set(gcf,'PaperPosition',[0 0 get(gcf,'PaperSize')]);
set(gcf,'Units','centimeters');

keepaxis = axis;
set(gcf,'Position',[1 1 cmwidth cmwidth/aspect]);
axis(keepaxis); % Prevent axis limits from changing

textobjs = findall(gcf,'Type','text')';

cbh = findall(gcf,'type','ColorBar');
childhs = [findall(gca);cbh];
childhs = reshape(childhs,1,numel(childhs));
for ch = childhs
    if isprop(ch,'FontName')
        if ieeetran
            set(ch,'FontName','cmr10');
        else
            set(ch,'FontName','CMU Serif');
        end
    end
    if isprop(ch,'FontSize')
        set(ch,'FontSize',fontpts);
    end
    if isprop(ch,'String')
        ostr = get(ch,'String');
        if ~isempty(ostr)
            ostr = strrep(ostr,'%','\%');
            set(ch,'String',ostr);
        end
    end
end

set(gca,'LineWidth',axiswidth);
if ieeetran
    set(gca,'Color','white');
    set(gcf,'Color','white');
    set(gca,'TickDir','out'); % Might cause issues; stay watchful!
else
    set(gca,'Color','none');
    set(gcf,'Color','none');
end
set(gcf,'InvertHardcopy','off');

if tickon
    set(gca,'TickLength',[0.015 0.025]); % Standard tick marks
else
    set(gca,'TickLength',[0 0]); % Disable tick marks
end

% Crop away unused space
%http://www.ligo.caltech.edu/~tfricke/matlab-tricks/plot-positions/html/
%tight_plot.html
%set(gca,'Position',get(gca,'OuterPosition') - ...
%    get(gca,'TightInset')*[-1 0 1 0; 0 -1 0 1; 0 0 1 0; 0 0 0 1]);

set(gca,'XTickMode','manual');
set(gca,'YTickMode','manual');

grid off;
if ~boxon
    box off;
    %legend boxoff;
else
    box on;
    %legend boxon;
end

for ch = childhs
    if isprop(ch,'LineWidth')
        set(ch,'LineWidth',plotwidth);
    end
    if isprop(ch,'MarkerSize')
        set(ch,'MarkerSize',marksize);
    end
end

textobjs = subst_fm_text(fid,textobjs,'Title','title','Bc',1,'','');
textobjs = subst_fm_text(fid,textobjs,'XLabel','xlabel','Bc',1,'','');
textobjs = subst_fm_text(fid,textobjs,'YLabel','ylabel','Bc',1,'','');

if strcmp(get(gca,'XScale'),'log')
    textobjs = subst_fm_text(fid,textobjs,'XTickLabel',...
        'xt','Bc',1,'$','$');
else
    textobjs = subst_fm_text(fid,textobjs,'XTickLabel',...
        'xt','Bc',1,'','');
end

if strcmp(get(gca,'YScale'),'log')
    textobjs = subst_fm_text(fid,textobjs,'YTickLabel',...
        'yt','Br',1,'$','$');
else
    if ynumeric
        textobjs = subst_fm_text(fid,textobjs,'YTickLabel',...
            'yt','Br',1,'$','$');
    else
        textobjs = subst_fm_text(fid,textobjs,'YTickLabel',...
            'yt','Br',1,'','');
    end
end

% Replace tick labels on ColorBar object, if present
if ~isempty(cbh)
    textobjs = subst_fm_text(fid,textobjs,'TickLabels',...
    	'ct','Br',1,'$','$',findall(gcf,'type','ColorBar'));
end

%set(gcf,'defaultLegendAutoUpdate','off'); % Doesn't work
[~,legendobjs] = legend;
legendstrs = get(legend,'String');
if ~strcmp(legendstrs{1},'data1')
    for li = 1:numel(legendstrs)
       lstr = legendstrs{li}; 
       if ~isempty(lstr)
           lstr = deblank(lstr);
           lstr = regexprep(lstr,'[\$_^\\{}]','');
           lstr = regexprep(lstr,'[^0-9A-Za-z]','n');
           %if (numel(lstr) > 1),
           %    lstr = lstr(1:end-1);
           %end
           %fprintf(fid,'%s\n',['\psfrag{' lstr int2str(li) '}'...
           %    '[Bc][Bc][1]{' legendstrs{li} '}']);
           fprintf(fid,'%s\n',['\psfrag{' lstr int2str(li) '}'...
               '[Bl][Bl][1]{' legendstrs{li} '}']);
           legendstrs{li} = [lstr int2str(li)];
       end
    end
    set(legend,'String',legendstrs);
    textobjs = setdiff(textobjs,legendobjs);
else
    legend off;
end

for o = 1:numel(textobjs)
    oh = textobjs(o);
    ostr = get(oh,'String');
    if ~isempty(ostr)
        tmpstr = deblank(ostr);
        tmpstr = regexprep(tmpstr,'[\$_^\\{}]','');
        tmpstr = regexprep(tmpstr,'[^0-9A-Za-z]','n');
        %if (numel(tmpstr) > 1),
        %    tmpstr = tmpstr(1:end-1);
        %end
        %fprintf(fid,'%s\n',['\psfrag{' lstr int2str(o) '}'...
        %    '[Bc][Bc][1]{' legendstrs{li} '}']);
        fprintf(fid,'%s\n',['\psfrag{' tmpstr int2str(o) '}'...
            '[Bc][Bc][1]{' ostr '}']);
        set(oh,'String',[tmpstr int2str(o)]);
    end
end

fclose(fid);

saveas(gcf,[figname '_fm'],'fig');
saveas(gcf,[figname '_fm.eps'],'epsc');

close(gcf);

%pathstr = fileparts(figname);

%set(0,'defaulttextinterpreter',interpreter);

function textobjs = subst_fm_text(fid,textobjs,property,...
    tag,align,scale,ltx,rtx,handle)

if (nargin < 9) || isempty(handle)
    handle = gca;
end
objs = get(handle,property);

if ~iscell(objs)
    objs = {objs};
end

nobjs = numel(objs);
ostr = {};
for n = 1:nobjs
    obj = objs{n};

    if ischar(obj)
        str = obj;
        for l = 1:size(str,1)
            if isempty(deblank(str(l,:)))
                continue;
            end
            ostr{end+1} = [tag int2str(n + (l-1)*nobjs)];
            fprintf(fid,'%s\n',['\psfrag{' ostr{end}...
                '}[' align '][' align '][' num2str(scale) ']{'...
                ltx deblank(str(l,:)) rtx '}']);
        end
        set(handle,property,ostr);
    else
        texthandle = get(handle,property);
        textobjs = setdiff(textobjs,texthandle);
        str = get(texthandle,'String');
        if isempty(str)
            return;
        end
        fprintf(fid,'%s\n',['\psfrag{' tag int2str(n)...
            '}[' align '][' align '][' num2str(scale) ']{'...
            ltx str rtx '}']);
        set(texthandle,'String',[tag int2str(n)]);
    end
end