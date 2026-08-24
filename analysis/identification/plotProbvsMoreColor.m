clear

resultsDir = '../../results/identification';
out_dir = "../../figures/figs3_4/";

% Load more color ratings 
moreColorPath = resultsDir + "/morecolor_probs.csv";
moreColor = readtable(moreColorPath);

% Load choice probability data
humanChooseColorPath = resultsDir + "/human_choosecolor_probs.csv";
monkeyChooseColorPath = resultsDir + "/monkey_choosecolor_probs.csv";
humanChooseColor = readtable(humanChooseColorPath);
humanChooseColor = renamevars(humanChooseColor, "chooseColorProb", "humanchooseColorProb");
monkeyChooseColor = readtable(monkeyChooseColorPath);
monkeyChooseColor = renamevars(monkeyChooseColor, "chooseColorProb", "monkeychooseColorProb");


% Join data to ensure correct color pairings
colorData = join(humanChooseColor, monkeyChooseColor);
colorData = join(colorData, moreColor);
% Remove light and dark grays
colorDataNoGray = colorData(colorData.stimNumbered ~= 13 & colorData.stimNumbered ~= 14, :);


% Calculate corr coefficients
corrType = 'Pearson';
[hrho,hpval] = corr(colorDataNoGray.pColorProb,colorDataNoGray.humanchooseColorProb, 'Type', corrType); % human
[mrho,mpval] = corr(colorDataNoGray.pColorProb,colorDataNoGray.monkeychooseColorProb, 'Type', corrType); % monkey

disp('human pearson r ');
disp(hrho);
disp(hpval);
disp('monkey pearson r ');
disp(mrho);
disp(mpval);

% Fit OLS linear regression 
hModel = fitlm(colorDataNoGray.pColorProb,colorDataNoGray.humanchooseColorProb);
mModel = fitlm(colorDataNoGray.pColorProb,colorDataNoGray.monkeychooseColorProb);

% Get line of best fit
xfit = linspace(0.3, .75, 55)';
hyfit = predict(hModel, xfit);
myfit = predict(mModel, xfit);

% Color info
% redVals = [235,141,202,122,141,86,86,50,157,95,227,136,186,113];
% greenVals = [139,84,166,102,186,114,188,115,163,102,133,82,166,102];
% blueVals = [167,97,90,52,123,72,205,119,254,149,240,139,187,109];
redVals = [224,141,190,122,123,86,66,50,144,95,212,136,186,113];
greenVals = [152,84,170,102,186,114,188,115,172,102,151,82,166,102];
blueVals = [155,97,106,52,128,72,186,119,222,149,208,139,187,109];
barCData = [redVals(:), greenVals(:), blueVals(:)];
rgb = barCData./255;
rgbNoGray = rgb(1:1:12,:);

% Plot human
f = figure;
f.Units = "inches";
f.Position = [1 1 2 2];
plot(xfit, hyfit, 'k-', 'LineWidth', 1);
hold on;
scatter(colorDataNoGray.pColorProb, colorDataNoGray.humanchooseColorProb, 28, rgbNoGray, 'filled');
xticks([0.25, 0.5, .75]);
yticks([0, 0.25, 0.5]);
set(gca, 'XLim', [0.25, .8]); 
set(gca, 'YLim', [0.0, .55]); 
set(gca, 'DataAspectRatio', [1 1 1]); 
set(gca, 'PlotBoxAspectRatio', [1 1 1]); 
set(gca, 'TickDir', 'out');
set(gca,'TickLength',[0.03, 0.03]);
fontsize(10,"points");

%exportgraphics(f, out_dir + "Human_choosecolor_vs_morecolor.svg",Resolution=300);
%exportgraphics(f, out_dir + "Human_choosecolor_vs_morecolor.png",Resolution=300);
hold off;

% Plot monkey
f = figure;
f.Units = "inches";
f.Position = [1 1 2 2];
plot(xfit, myfit, 'k-', 'LineWidth', 1);
hold on;
scatter(colorDataNoGray.pColorProb, colorDataNoGray.monkeychooseColorProb, 28, rgbNoGray, 'filled');
xticks([0.25, 0.5, .75]);
yticks([0, 0.25, 0.5]);
set(gca, 'XLim', [0.25, .8]); 
set(gca, 'YLim', [0.0, .55]); 
set(gca, 'DataAspectRatio', [1 1 1]); 
set(gca, 'PlotBoxAspectRatio', [1 1 1]); 
set(gca, 'TickDir', 'out');
set(gca,'TickLength',[0.03, 0.03]);
fontsize(10,"points");

exportgraphics(f, out_dir + "Monkey_choosecolor_vs_morecolor.svg",Resolution=300);
exportgraphics(f, out_dir + "Monkey_choosecolor_vs_morecolor.png",Resolution=300);

hold off;
