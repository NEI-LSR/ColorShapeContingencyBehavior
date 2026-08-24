function alldata = getMT1P3HumanData(nms)

dataDir = '../../data/identification/';

workerStr = 'subject_number';

shape1str = 'Answer.Choice1ImageIndex';
color1str = 'Answer.Choice1ColorIndex';
shape2str = 'Answer.Choice2ImageIndex';
color2str = 'Answer.Choice2ColorIndex';
cueShapeStr = 'Answer.CueImageIndex';
cueColorStr = 'Answer.CueColorIndex';

answerStr = 'Answer.answer';
rtStr = 'Answer.RT';

alldata = [];
allprobe = [];

allTestCorrect = {};

trainx = zeros(500, 1);
shpTotal = trainx;
shpOK = trainx;
clrTotal = trainx;
clrOK = trainx;

numok = 0;
for n = 1:length(nms)

    fnm = nms{n};

    fnm = [dataDir, fnm];
    opts = detectImportOptions(fnm, ...
        'Delimiter', ',', ...
        'VariableNamingRule', 'preserve');


    rawResults = readtable(fnm, opts);
    raw = rawResults;

    for w = 1:size(raw,1)  % loop through assignments (workers)

        ID = raw{w, workerStr};

        % find which images were presented in which order in each position
        stim1shp = raw{w, shape1str};
        stim1clr = raw{w, color1str};
        stim2shp = raw{w, shape2str};
        stim2clr= raw{w, color2str};
        qshp= raw{w, cueShapeStr};
        qclr= raw{w, cueColorStr};

        % strings into numbers
        s1 = str2double(split(stim1shp));
        n = numel(s1);
        c1 = str2double(split(stim1clr));
        s2 = str2double(split(stim2shp));
        c2 = str2double(split(stim2clr));
        sq = str2double(split(qshp));
        cq = str2double(split(qclr));

        choices = raw{w, answerStr};
        choices = split(choices);
        chosen = str2double(extractAfter(choices, "idx"));

        s1 = s1(:);
        c1 = c1(:);
        s2 = s2(:);
        c2 = c2(:);
        sq = sq(:);
        cq = cq(:);
        chosen = chosen(:);

        all = [s1, c1, s2, c2, sq, cq, chosen];


        tst = s1.*c1 == 0;

        probe = (s1~=c1) & ~ tst;

        train = ~probe & ~tst;

        try
            [tplt, sx, sy, cx, cy] = showTest(ID, all, tst, 0);


            tcorrect = sum([sy(:);cy(:)]);
            ttotal = length([sy(:);cy(:)]);
            
            % Participant included only if they performed > 75% accuracy on
            % all long-term color-to-shape and shape-to-color trials
            if sum(sy)/length(sy) > .75 && sum(cy)/length(cy) > 0.75 % inclusion criteria!
                shpTotal(sx) = shpTotal(sx)+1;
                shpOK(sx) = shpOK(sx) + sy;
                clrTotal(cx) = clrTotal(cx)+1;
                clrOK(cx) = clrOK(cx) + cy;
                allprobe = [allprobe; probe];
                alldata = [alldata; all];
                numok = numok+1;
            else

            end



        catch
        end



    end

end

end


function [h, sx, sy, cx, cy] = showTest(ID, dat, idx, doplot)

s1t = dat(idx, 1);
c1t = dat(idx, 2);
s2t = dat(idx, 3);
c2t = dat(idx, 4);
sqt = dat(idx, 5);
cqt = dat(idx, 6);
cht = dat(idx, 7);


shpq = s1t==0;
clrq = c1t==0;

shps = [s1t,s2t];
clrs = [c1t,c2t];

shapeChosen = cht;
shapeChosen(cht==1) = s1t(cht==1);
shapeChosen(cht==2) = s2t(cht==2);

colorChosen = cht;
colorChosen(cht==1) = c1t(cht==1);
colorChosen(cht==2) = c2t(cht==2);


clrTrial = sqt==0;
shpTrial = ~clrTrial;



shpTrialCorrect = sqt(shpTrial) == colorChosen(shpTrial);
clrTrialCorrect = cqt(clrTrial) == shapeChosen(clrTrial);

cx = find(clrTrial);
cy = clrTrialCorrect;
sx = find(shpTrial);
sy = shpTrialCorrect;



if doplot
    h = figure;
    plot(sx, sy, 'k-');
    hold on;
    plot(cx, cy, 'r-');
    
else
    h = 0;
end
end  


