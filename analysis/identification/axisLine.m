function l = axisLine(xory, vals, lineStyle, lineWid)

% function l = axisLine(direction, xval, style, wid)
% puts a vertical line spanning the y axis at the specified x value
% If xval is a vector, puts a line at each x value
% returns the handle to the line(s)

narginchk(1, 4);

if lower(xory(1)) == 'x'
	xdir = true;
	limPropString = 'XLim';
	dataPropString = 'XData';
else
	xdir = false;
	limPropString = 'YLim';
	dataPropString = 'YData';
end;


if isa(vals, 'axes')
	ax = vals;
else
	ax = gca;
end;
ud = get(ax, 'UserData');

% see if there are any existing lines
%-=====================================
if ~isfield(ud, 'xlines')
	ud.xlines = [];
end;
if ~isfield(ud, 'ylines')
	ud.ylines = [];
end;
if xdir
	oldLines = ud.xlines;
else
	oldLines = ud.ylines;
end;

% callback to keep lines at at axis limits
%-============================================
if isa(vals, 'axes')
	axlim = get(ax, limPropString);
	
	for y = 1:length(oldLines)
		set(oldLines(y), dataPropString, axlim);
	end;
	return;
end;


%  make the lines
%-==================
hold on;
lns = zeros(size(vals));
for x = 1:length(vals)
	v = vals(x);
	axlim = get(ax,limPropString);
	
	% draw the line in the right direction
	if xdir
		ln = line(axlim, [v, v]);
	else
		ln = line([v, v], axlim);
	end;
	
	% set the line attributes
	lns(x) = ln;
	set(ln, 'Color', [0 0 0]);
	if length(lineStyle) > 1
		lstyle = lineStyle(2:end);
		lcolor = lineStyle(1);
		set(ln, 'Color', lcolor);
		set(ln, 'LineStyle', lstyle);
		set(ln, 'LineWidth', lineWid);
	else
		set(ln, 'LineStyle', lineStyle);
    end
end

% add new lines to the list
newLines = [oldLines(:); lns(:)];

% put all lines into the userdata
if xdir
	ud.xlines = newLines;
else
	ud.ylines = newLines;
end

hax = handle(gca);
hprop = findprop(hax, limPropString);
hlis = addlistener(hax, hprop, 'PostSet',...
	@(x,y) axisLine(xory, hax));
ud.hlis = hlis;

set(gca, 'UserData', ud);

if nargout
	l = lns;
end
