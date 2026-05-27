%% Xfmer canterliver model 
clear all
clc;
%sec=Rx
%pri=Tx
%unit: nH
Lopsec = 6444;
Lscsec = 6444;
Lscpri = 2132;

Lmag = Lopsec
%Lmag*Llk/(Lmag+Llk) = Lscsec;
%Llk*ne^2 = Lscpri
syms Llk ne 
%Lmag Lscsec Lscpri
eqns = [Lmag*Llk/(Lmag+Llk) == Lscsec,Llk*ne^2 == Lscpri];
vars = [Llk ne];
[slk,sne] = solve(eqns, vars);
%Llk = vpa(slk)
%format long
Llk = vpa(slk);
ne = vpa(sne)
L11 = Lopsec
L12 = ne(2)*Lmag
L21 = ne(2)*Lmag;
L22 = ne(2)^2*(Lmag+Llk(1));
X = [L11 L12
     L21 L22];
coupling = L12/sqrt(L11*L22)