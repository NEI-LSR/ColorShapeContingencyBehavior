function l = xline(yval, style, wid)

% function l = xline(yval, style, wid)
% puts a horizontal line spanning the x axis at the specified y value
% If yval is a vector, puts a line at each y value
% returns the handle to the line(s)
% parse other input args
%-=========================
lineWid = 0.5;
lineStyle = 'k-';

if nargin > 1  % have style and/or wid
	if ischar(style)
		lineStyle = style;
		if nargin == 3
			lineWid = wid;
		end;
	else
		lineWid = style;
		if nargin == 3
			lineStyle = wid;
		end;
	end;
end;


if nargout
	l = axisLine('x', yval, lineStyle, lineWid);
else
	axisLine('x', yval, lineStyle, lineWid);
end;

return


if strcmp(class(xval), 'axes')
	% callback
	ax = xval;
	ud = get(ax, 'UserData');
	xlm = get(ax, 'XLim');
	xlns = ud.xlines;
	
	for y = 1:length(ylns)
		set(ylns(y), 'XData', xlm);
	end;
	return;
end;


if nargin < 2
	wid = 0.5;
	style = 'k-';
end;

if nargin < 3
	if isstr(style)
		wid = 0.5;
	else
		style = 'k-';
	end;
end;

if nargin == 3
	if ~isstr(style)
		new_wid = style;
		style = wid;
		wid = new_wid;
	end;
end;

hold on;
lns = [];
for y = 1:length(yval)
	yv = yval(y);
	xl = get(gca,'XLim');
	ln = line(xl, [yv, yv]);
	lns = [lns; ln];
	set(ln, 'Color', [0 0 0]);
	if length(style) > 1
		set(ln, 'Color', style(1));
		lstyle = style(2:end);
		set(ln, 'LineStyle', lstyle);
	end;
end;

ud.ylines = lns;

hax = handle(gca);
hprop = findprop(hax, 'XLim');
hlis = handle.listener(hax, hprop, 'PropertyPostSet', @(x,y) xline(hax));
ud.hlis = hlis;
set(gca, 'UserData', ud);


if nargout
	l = lns;
end
