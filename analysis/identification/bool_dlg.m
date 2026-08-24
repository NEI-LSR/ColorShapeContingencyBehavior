function tf_list = bool_dlg(label_strings, defaults)

% % function tf_list = bool_dlg(label_strings, defaults)
% %
% % When passed a list of strings, presents a dialog where the user
% % can choose to select or not select each item.  The selections
% % are returned in tf_list with 1 for selected and 0 for not selected.
% % The default button positions (selected or not) can be passed in the
% % optional argument defaults (a list of 1s and 0s).
% %

% make sure we have a cell
if ~iscell(label_strings)
	label_strings = cellstr(label_strings);
end;

% output
tf_list = [];

% number of items
nlabels = length(label_strings);

% if no defaults, start with all not selected
if nargin < 2
	defaults = zeros(nlabels, 1);
end;

% make sure we have the right number of defaults
if length(defaults) > nlabels
	% if too many defaults, just use the first ones
	defaults = defaults(1:nlabels);
elseif length(defaults) < nlabels
	% if not enough defaults, just use what we have, deselect remaining
	tmp = zeros(nlabels, 1);
	tmp(1:length(defaults)) = defaults;
	defaults = tmp;
end;

% make sure defaults is 1 or 0
defaults = defaults ~= 0;

% build the options string for optdlg
opts = cell(length(label_strings), 1);

% chars for dialog defaults
dchar = 'ft';

% make an item for each label
for n = 1:nlabels
	currvarname = ['var',num2str(n)];
	currlabel = label_strings{n};
	opts{n} = {'tf',currvarname,currlabel,dchar(defaults(n)+1)};
end;

if isempty(optdlg(opts))
	% cancelled by user
	return;
end;

% construct the output list
for n = 1:nlabels
	tf_list = [tf_list; eval(['var',num2str(n)])];
end;




