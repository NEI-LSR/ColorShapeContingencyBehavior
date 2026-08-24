function result = fitEllipseLSQ(x, y)
% fitEllipseLSQ  Fit an ellipse to 2D points using lsqnonlin.
% Written by ChatGPT
%
%   result = fitEllipseLSQ(x, y)
%
% Inputs:
%   x, y   - vectors of equal length containing point coordinates
%
% Output:
%   result - struct with fields:
%       .xc, .yc         ellipse center
%       .a, .b           semi-major / semi-minor axes (a >= b)
%       .theta           rotation angle in radians
%       .major_axis      full major axis length = 2*a
%       .minor_axis      full minor axis length = 2*b
%       .resnorm         final least-squares residual norm
%       .exitflag        lsqnonlin exit flag
%       .output          lsqnonlin output structure

    % ---- Input checks ----
    x = x(:);
    y = y(:);

    if numel(x) ~= numel(y)
        error('x and y must have the same number of elements.');
    end

    if numel(x) < 5
        error('At least 5 points are recommended to fit an ellipse.');
    end

    % ---- Initial guess ----
    % Center guess: centroid
    xc0 = mean(x);
    yc0 = mean(y);

    % Rough orientation guess from PCA
    X = [x - xc0, y - yc0];
    C = cov(X);
    [V, D] = eig(C);
    [~, idx] = sort(diag(D), 'descend');
    V = V(:, idx);

    theta0 = atan2(V(2,1), V(1,1));

    % Rotate points into PCA frame to estimate axis scales
    R0 = [cos(theta0), sin(theta0); -sin(theta0), cos(theta0)];
    Xr = (R0 * X')';

    % Initial semi-axis guesses from spread
    a0 = max(std(Xr(:,1)) * sqrt(2), eps);
    b0 = max(std(Xr(:,2)) * sqrt(2), eps);

    % Enforce a0 >= b0 for a cleaner parameterization
    if b0 > a0
        tmp = a0;
        a0 = b0;
        b0 = tmp;
        theta0 = theta0 + pi/2;
    end

    % Parameter vector: [xc, yc, log(a), log(b), theta]
    p0 = [xc0, yc0, log(a0), log(b0), theta0];

    % ---- Least-squares fit ----
    % Residual function: implicit ellipse equation values at the points
    residualFun = @(p) ellipseResiduals(p, x, y);

    opts = optimoptions('lsqnonlin', ...
        'Display', 'off', ...
        'MaxIterations', 1000, ...
        'MaxFunctionEvaluations', 5000, ...
        'FunctionTolerance', 1e-12, ...
        'StepTolerance', 1e-12);

    % No explicit bounds needed because a and b are parameterized as exp()
    [pfit, resnorm, residual, exitflag, output] = lsqnonlin(residualFun, p0, [], [], opts);

    % ---- Decode fitted parameters ----
    xc = pfit(1);
    yc = pfit(2);
    a = exp(pfit(3));
    b = exp(pfit(4));
    theta = pfit(5);

    % Make sure a >= b
    if b > a
        tmp = a;
        a = b;
        b = tmp;
        theta = theta + pi/2;
    end

    % Normalize theta to [-pi, pi)
    theta = mod(theta + pi, 2*pi) - pi;

    % ---- Pack results ----
    result = struct();
    result.xc = xc;
    result.yc = yc;
    result.a = a;                  % semi-major axis
    result.b = b;                  % semi-minor axis
    result.theta = theta;          % radians
    result.major_axis = 2*a;
    result.minor_axis = 2*b;
    result.resnorm = resnorm;
    result.residual = residual;
    result.exitflag = exitflag;
    result.output = output;
end

% ---- Helper: residuals for lsqnonlin ----
function r = ellipseResiduals(p, x, y)
    xc = p(1);
    yc = p(2);
    a = exp(p(3));
    b = exp(p(4));
    theta = p(5);

    % Rotate points into ellipse-aligned coordinates
    ct = cos(theta);
    st = sin(theta);

    dx = x - xc;
    dy = y - yc;

    xr =  ct*dx + st*dy;
    yr = -st*dx + ct*dy;

    % Implicit ellipse residual
    r = (xr./a).^2 + (yr./b).^2 - 1;
end