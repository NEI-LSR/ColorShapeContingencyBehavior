function fig = smallfig(figname)

% function fig = smallfig(figname)
% creates a small figure panel.
% returns the handle to the figure, if asked for.

% dims in screen percentages
dims = [0.2, 0.3];  % x, y


if nargin > 0
	fg = pfigure(figname, dims(1), dims(2));
else
	fg = pfigure(dims(1), dims(2));
end;

% set(fg, 'DoubleBuffer', 'off');
sz = get(0, 'ScreenSize');
ht = sz(4);

pos = get(fg, 'Position');
fht = pos(4);

pos(1) = 30;
pos(2) = (ht - fht) - ht/10;

set(fg, 'Position', pos);

if nargout
	fig = fg;
end;

figure(fg);
refresh;

