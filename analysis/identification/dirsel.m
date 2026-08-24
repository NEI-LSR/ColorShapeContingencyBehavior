function [th, rh] = dirsel(theta, rho)

meanmag = mean(rho);

[xx, yy] = pol2cart(theta, rho);

xm = mean(xx);
ym = mean(yy);

[th, rh] = cart2pol(xm, ym);

rh = rh/meanmag;


return