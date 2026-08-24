function l = axdiag(ax)

% % function l = axdiag(ax)
% %
% % plots a diagonal line from lower left to upper right of
% % the passed axes object.  If no axes are passed, the current
% % axes are used.
% % returns a handle to the line

neg = false;
if nargin == 0
	ax = gca;
	neg = false;
end;

if ax == -1
	ax = gca;
	neg = true;
end;

hold on;

px = xlim;
py = ylim;
if neg
	py = py([2,1]);
end;

p = plot(ax, px, py, 'k-');

if nargout
	l = p;
end;



