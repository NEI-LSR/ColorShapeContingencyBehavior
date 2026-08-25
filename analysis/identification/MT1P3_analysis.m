function MT1P3_analysis()
% Identification trials: monkeys and humans were shown one of the 14 
% colored shapes and then two choice options: one that matched the cue in
% color but not shape, one that matched the cue in shape but not color.
% This script computes the probability of choosing the option that matched
% the cue's color, averaged across subjects. 

MT1P3_identification(false)

end

function MT1P3_identification(doHuman)

dataDir = '../../data/identification/';
out_dir = "../../figures/figs3_4/";

% Monkey data
monkeydata = 'monkeyP3data.csv';

% Human data
n10 = 'shapecolor_10.csv';
n11 = 'shapecolor_11.csv';
n12 = 'shapecolor_12.csv';
n13 = 'shapecolor_13.csv';
n14 = 'shapecolor_14.csv';
n15 = 'shapecolor_15.csv';
n16 = 'shapecolor_16.csv';
n17 = 'shapecolor_17.csv';
n18 = 'shapecolor_18.csv';
humanNames = {n10, n11, n12, n13, n14, n15, n16, n17, n18};

% Plotting colors
redVals = [224,141,190,122,123,86,66,50,144,95,212,136,186,113];
greenVals = [152,84,170,102,186,114,188,115,172,102,151,82,166,102];
blueVals = [155,97,106,52,128,72,186,119,222,149,208,139,187,109];
barGrey = [150, 132, 153];

barCData = [redVals(:), greenVals(:), blueVals(:)];

% % warm, bright, color
stimID = [...
    1, 1, 1;...
    1, 0, 1;...
    1, 1, 2;...
    1, 0, 2;...
    0, 1, 3;...
    0, 0, 3;...
    0, 1, 4;...
    0, 0, 4;...
    0, 1, 5;...
    0, 0, 5;...
    1, 1, 6;...
    1, 0, 6;...
    0, 1, 7;...
    0, 0, 7;...
    ];
chroma = [...
    "warm";...
    "warm";...
    "warm";...
    "warm";...
    "cool";...
    "cool";...
    "cool";...
    "cool";...
    "cool";...
    "cool";...
    "warm";...
    "warm";...
    "cool";...
    "cool"];
lumVal = [...
    "bright";...
    "dim";...
    "bright";...
    "dim";...
    "bright";...
    "dim";...
    "bright";...
    "dim";...
    "bright";...
    "dim";...
    "bright";...
    "dim";...
    "bright";...
    "dim"];
hue = [...
    "red";...
    "red";...
    "gold";...
    "gold";...
    "green";...
    "green";...
    "turq";...
    "turq";...
    "blue";...
    "blue";...
    "pink";...
    "pink";...
    "grey";...
    "grey"];



if doHuman
    data = getMT1P3HumanData(humanNames);
    nms = humanNames;
    tstr = 'Human';
else
    fulldata = readtable([dataDir, monkeydata]); 
    nms = join([fulldata.subject, fulldata.datetime], "_");
    disp(unique(nms));
    data = removevars(fulldata, ["subject", "datetime"]);
    data = table2array(data);
    tstr = 'Monkey';
end
disp(tstr);
disp(unique(nms));

s1 = data(:,1);
c1 = data(:,2);
s2 = data(:,3);
c2 = data(:,4);
sq = data(:,5);
cq = data(:,6);
chosen = data(:,7);


if doHuman
    probe = sq==cq & s1~=c1 & s2~=c2;
else
    probe = s1~=c1 & s2~=c2;
end

idx = probe;

s1t = s1(idx); % shape id (1:14) in position 1
c1t = c1(idx); % color id in postition 1
s2t = s2(idx); % shape id in position 2
c2t = c2(idx); % color id in position 2
sqt = sq(idx); % cue shape id
cqt = cq(idx); % cue color id
cht = chosen(idx); % chosen index (1 or 2)

shps = [s1t,s2t];
clrs = [c1t,c2t];

choseShape = zeros(size(cht));
choseColor = zeros(size(cht));

for t = 1:length(cht)
    if shps(t, cht(t)) ==  sqt(t) %if shape at chosen idx == cue shape
        choseShape(t) = 1; % monkey chose shape over color
    else
        choseColor(t) = 1;
    end
end

allSamples = sqt;
allChoices = cht;
allShapes = [s1t,s2t];
allColors = [c1t, c2t];

uSamples = unique(s1t); % should be 1:14

pSamples = [];
sSamples = [];
pColorChoice = [];
pShapeChoice = [];
sColorChoice = [];
sShapeChoice = [];
for s = 1:length(uSamples) % for each object
    pidx = allSamples==uSamples(s); % all trials where that object was cue
    pColorChoice(s) = sum(choseColor(pidx)); % how many times was color chosen
    pShapeChoice(s) = sum(choseShape(pidx)); % how many times was shape chosen
end

ptotal = pColorChoice + pShapeChoice; % total number of trials
%tot = ptotal;
ok = pShapeChoice;
pColorProb = pColorChoice./ptotal;
pShapeProb = pShapeChoice./ptotal;

for idx = 1:2:14 % z-test for difference between light/dark pairs;  not used
    a = idx;
    b = idx+1;
    phat = (ptotal(a).*pColorProb(a) + ptotal(b).*pColorProb(b))./(ptotal(a)+ptotal(b));

    z12 = (pColorProb(a)-pColorProb(b))./(sqrt(phat.*(1-phat)).*(1./ptotal(a) + 1./ptotal(b)));

    z12

end
phat = (ptotal(a).*pColorProb(a) + ptotal(b).*pColorProb(b))./(ptotal(a)+ptotal(b));

z12 = (pColorProb(a)-pColorProb(b))./(sqrt(phat.*(1-phat)).*(1./ptotal(a) + 1./ptotal(b)));



z = 1.96; % for 95% confidence interval
% variance of a binom var is num trials * prob of color choice *
% prob of shape choice
se = (z./(ptotal.*sqrt(ptotal))).*sqrt(pColorChoice.*pShapeChoice); % this is the half 95%CI, not the SE

% Generate polar plots
ccc= [1,1,1];
wid = 3;
f = figure;

wrappedtheta = deg2rad(0:60:360); % the hues are evenly spaced around a circle
theta = deg2rad(0:60:359);
bigtheta = deg2rad(0:360);
s1 = 1:2:12; % high lum objects
s1(end+1) = s1(1);
s2 = s1 + 1; % low lum objects
lidx = 1:2:12; % high lum objects indices
didx = lidx + 1;

% plot ellipse in back
% get xy coordinates of each match color probability
thetaAll = [theta, theta];
colorAll = [pColorProb(lidx), pColorProb(didx)];
stimNumbered = (1:1:14)'; 
chooseColorProb = pColorProb';
probTable = table(stimNumbered, chooseColorProb);
if doHuman
    outName = '../../results/identification/human_choosecolor_probs.csv';
else
    outName = '../../results/identification/monkey_choosecolor_probs.csv';
end

writetable(probTable, outName);

[xColor,yColor] = pol2cart(thetaAll,colorAll);
fit = fitEllipse(xColor, yColor);
minorAxis = fit.minor_axis;
majorAxisAngle = fit.theta;
minorAxisAngle = majorAxisAngle + pi/2;
minorAxisAngleWrapped = mod(minorAxisAngle, pi) - pi/2;

t=linspace(0, 2*pi, 200);
R = [cos(fit.theta) -sin(fit.theta); sin(fit.theta) cos(fit.theta)];
xy = R * [fit.a*cos(t); fit.b*sin(t)];
xe = xy(1,:) + fit.xc;
ye = xy(2,:) + fit.yc;
[thetaEllipse,rhoEllipse] = cart2pol(xe,ye);

% Begin plotting
p = polarplot(thetaEllipse, rhoEllipse, 'Color', 0.6.*ccc, 'LineStyle','-', 'LineWidth', .75);
hold on;
p = polarplot([minorAxisAngle, minorAxisAngle], [-0.8, 0.8], 'Color', 0.6.*ccc, 'LineStyle','-', 'LineWidth', .75);


p = polarplot(wrappedtheta, pColorProb(s1), 'k--', 'LineWidth', 1.5);
%hold on;
p = polarplot(wrappedtheta, pColorProb(s2), 'k-', 'LineWidth', 1.5);
set(gca, 'ThetaTickLabel', {});
set(gca, 'RLim', [0, 0.7]);
set(gca, 'RTick', [0, .25, 0.5]); 

if doHuman
    set(gca, 'RLim', [0, 0.38]);
    set(gca, 'RTick', [0, .15, .30]); 
end




for s = 1:length(theta) % for each hue
    s1 = 1+2*(uSamples(s)-1);
    s2 = s1+1;

    p = polarplot(theta(s), pColorProb(s1), 'ko');
    set(p, 'MarkerFaceColor',  barCData(s1,:)./255,'MarkerEdgeColor',  barCData(s1,:)./255, 'MarkerSize', 5);
    p = polarplot([theta(s), theta(s)],...
        [pColorProb(s1) + se(s1), pColorProb(s1) - se(s1)], 'k-',...
        'LineWidth', 1.5, 'Color', barCData(s1,:)./255);

    p = polarplot(theta(s), pColorProb(s2), 'ko');
    set(p, 'MarkerFaceColor',  barCData(s2,:)./255,'MarkerEdgeColor',  barCData(s2,:)./255, 'MarkerSize', 5);
    p = polarplot([theta(s), theta(s)],...
        [pColorProb(s2) + se(s2), pColorProb(s2) - se(s2)], 'k-',...
        'LineWidth', 1.5, 'Color', barCData(s2,:)./255);

end

fontsize(10,"points")
%title([tstr,': Color choice proportion by hue']);


exportgraphics(f,out_dir + tstr + "_polar_identification.svg",Units="inches", ...
    Width=2,Height=2,Resolution=300)
exportgraphics(f,out_dir + tstr + "_polar_identification.png",Units="inches", ...
    Width=2,Height=2,Resolution=300)
hold off;


% Generate bar plot
% 2x1.5 in
f = figure;
f.Units = "inches";
f.Position = [1 1 2.3 1.75];

b = bar(uSamples,pColorProb, 'FaceColor', 'flat', 'LineWidth', 1, 'EdgeColor', 'none');
b.CData = barCData(:,:)./255;
hold on;
barError = errorbar(uSamples, pColorProb, se, 'LineStyle', 'none', 'Color', 'k', 'LineWidth', 1);
barError.CapSize = 0; 
xlim([0.5, 14.5]);
yline(0.5, 'k--', 'LineWidth', 1);
ylim([0.0, 1.0]);
set(gca,'xtick',[]);
set(gca,'xticklabel',[]);
set(gca,'ytick',[0,.5,1]);
%set(gca,'yticklabel',['0', '0.5', '1']);
set(gca,'TickDir','out');
set(gca,'TickLength',[0.03, 0.01]);
set(gca, 'LineWidth', 1.0);
fontsize(10,"points");

exportgraphics(f, out_dir + tstr + "_bar_chart.svg",Resolution=300);
exportgraphics(f, out_dir + tstr + "_bar_chart.png",Resolution=300);

hold off; 

p = binocdf(sum(pColorProb), sum(ptotal), 0.5);
q = 1-sum(pColorProb)/sum(ptotal);

disp(' ');
disp(['all ', sprintf('%0.3f', q), ' ', sprintf('%0.5f', p)]);


% Plot scatter
f = figure;
f.Units = "inches";
f.Position = [1 1 2 2]; %1.75 1.75];
plot([0, 0.5], [0, 0.5], 'k-', 'LineWidth', 1);
hold on;

for s = 1:2:12 % length(uSamples) - 2; ignore grays

    % Add error bars
    e_y = errorbar(pColorProb(s), pColorProb(s+1), se(s+1), 'Color', barCData(s+1,:)./255, 'LineWidth', 1, 'CapSize', 0);
    e_x = errorbar(pColorProb(s), pColorProb(s+1), se(s), 'horizontal', 'Color', barCData(s,:)./255, 'LineWidth', 1, 'CapSize', 0);
    plot(pColorProb(s), pColorProb(s+1), 'ko', 'MarkerFaceColor', barCData(s,:)./255, 'MarkerEdgeColor', barCData(s,:)./255,'MarkerSize', 5, 'LineWidth', 1);
    %set(p, 'MarkerFaceColor', barCData(s,:)./255, 'MarkerEdgeColor', barCData(s,:)./255,'MarkerSize', 4);

end
%xlabel('bright');
%ylabel('dark');
%xlim([0, 0.5]);
%ylim([0, 0.5]);
xticks([0, 0.25, 0.5]);
yticks([0, 0.25, 0.5]);
%axdiag;
%title(tstr);
set(gca, 'XLim', [0, 0.5]); 
set(gca, 'YLim', [0, 0.5]); 
set(gca, 'DataAspectRatio', [1 1 1]); 
set(gca, 'PlotBoxAspectRatio', [1 1 1]); 
set(gca, 'TickDir', 'out');
set(gca,'TickLength',[0.03, 0.03]);
fontsize(10,"points");

exportgraphics(f, out_dir + tstr + "_scatter_identification.svg",Resolution=300);
exportgraphics(f, out_dir + tstr + "_scatter_identification.png",Resolution=300);
hold off;

end