function fig = pfigure(figname, x, y)

% % function fig = pfigure(figname, x, y)
% % figname is optional
% % Creates a figure proportional to the screen size.
% % For example, pfigure(.5, .25) will make a figure window
% % half as wide as the screen and one-quarter as high, in the
% % center of the screen

if ~isstr(figname)  % no name passed
    y = x;
    x = figname;
end;

% dims in screen percentages
dims = [x, y];  % x, y

sz = get(0,'ScreenSize');
wid = sz(3)*dims(1);
ht = sz(4)*dims(2);

hmarg = (sz(3)-wid)/2;
vmarg = (sz(4)-ht)/2;

hmarg = min(hmarg, 20);
f = figure('Position',[hmarg, vmarg, wid, ht]);

pwid = 8;
pht = 10.5;

faspect = wid/ht;
paspect = pwid/pht;

overall = 1.2;

if faspect > paspect
    % if fig wider than paper, use wid
    scalefact = overall*wid/pwid;
else
    % use ht
    scalefact = overall*ht/pht;
end;

pw = wid/scalefact;
ph = ht/scalefact;
hm = (8.5 - pw)/2;
vm = (11 - ph)/2;

% set(f,'PaperPosition',[hm, vm, pw, ph]);

if isstr(figname)
    set(gcf,'NumberTitle','off');
    set(gcf,'Name',figname);
end;
%set(gcf,'MenuBar','none');

if nargout
    fig = f;
end;

figure(f);

