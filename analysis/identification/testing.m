% testing
dataDir = "../../data/identification/";
fileName = "shapecolor_11.csv";
full_Path = dataDir + fileName;

opts = detectImportOptions(full_Path, ...
    'Delimiter', ',', ...
    'VariableNamingRule', 'preserve');


data = readtable(full_Path, opts);

