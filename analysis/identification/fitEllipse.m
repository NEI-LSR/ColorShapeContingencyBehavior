function result = fitEllipseLSQ(x, y)

    x = x(:); % force input to column vector
    y = y(:);
    
    % Initial center guess using centroid  
    xc0 = mean(x);
    yc0 = mean(y);
    
    % Initial semi-major, semi-minor axis guesses
    a0 = std(x); % for an ellipse, the SDx is proportional to semi-major axis length
    b0 = std(y);
    
    % Initial orientation guess
    theta0 = 0; %pi;
    
    % Ensure major > minor
    if b0 > a0
        [a0, b0] = deal(b0, a0);
        theta0 = theta0 + pi/2;
    end
    
    % Params
    p0 = [xc0, yc0, log(a0), log(b0), theta0]; % log bc a and b must be positive
    
    % Nonlinear least squares fit
    residualFun = @(p) ellipseResiduals(p,x,y);
    
    opts = optimoptions('lsqnonlin', ...
    'Display', 'off', ...
    'MaxIterations', 1000, ...
    'MaxFunctionEvaluations', 5000, ...
    'FunctionTolerance', 1e-12, ...
    'StepTolerance', 1e-12);
    
    [pfit, resnorm, residual, exitflag, output] = ...
        lsqnonlin(residualFun, p0, [], [], opts);
    
    % Get parameters out
    xc = pfit(1);
    yc = pfit(2);
    a = exp(pfit(3));
    b = exp(pfit(4));
    theta = pfit(5);
    
    % Ensure a>=b 
    if b > a
        [a, b] = deal(b, a);
        theta = theta +pi/2;
    end
    
    % Normalize orientation angle to [-pi, pi)
    theta = mod(theta + pi, 2*pi) - pi;
    
    % Store results
    result.xc = xc;
    result.yc = yc;
    result.a = a;
    result.b = b;
    result.theta = theta;
    result.major_axis = 2*a;
    result.minor_axis = 2*b;
    result.resnorm = resnorm;
    result.residual = residual;
    result.exitflag = exitflag;
    result.output = output;

end

function r = ellipseResiduals(p, x, y)
    xc = p(1);
    yc = p(2);
    a = exp(p(3));
    b = exp(p(4));
    theta = p(5);

    % Translate and rotate points
    % Translation
    dx = x - xc;
    dy = y - yc;

    % Rotation
    ct = cos(theta);
    st = sin(theta);

    xr = ct*dx + st*dy;
    yr = -st*dx + ct*dy;

    % Implicit ellipse residual
    r = (xr./a).^2 + (yr./b).^2 - 1;

end