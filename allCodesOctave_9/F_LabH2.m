function [P_B,n,etaO,etaR] = F_LabH2(V_S,D,Z,AEdAO,PdD)
% LabH2_F computes the brake power and shaft speed for given propeller
% parameters

%   Detailed explanation goes here

% display('F_LabH2');


%% Computation of total resistance in still water

% V_S = 7;       % service speed [kn]
L = 22;        % length on waterline [m]
B = 9.6;         % breadth moulded [m]
T_F = 1.089;       % draught moulded on F.P. [m]
T_A = 1.089;       % draught moulded on A.P. [m]
nabla = 204.1;  % displacement volume [m^3]
LCB = 0; % longitudinal centre of buoyancy [% relative to 1/2L]
A_BT = 0;      % transverse bulb area [m^2]
h_B = 0;        % centre of bulb area above keel line [m]
C_M = 0.9761;     % midship section coefficient []
C_WP = 0.99999;    % waterplane area coefficient []
A_T = 0;       % transom area [m^2]
Cstern = 10;    % stern shape parameter []
apk2 = 0;     % 1+k2 (appendage)
S_APP = 0;     % wetted area of the appendage [m^2]


[Rtotal,C_B,C_P,S,apk1,C_F,C_A,Fn,i_E]=F_SWResist(L,B,T_F,T_A,nabla,...
    LCB,A_BT,h_B,C_M,C_WP,A_T,S_APP,apk2,Cstern,V_S);

%% Computation of propulsion factors in still water

% D = 0.8;          % propeller diameter [m]
% AEdAO = 0.8; % expanded area ratio []
zP = 2;         % number of propellers (single or twin-screw with conventional stern) []
% PdD = 0.65;     % pitch ratio []

[ t,w,etaR ] = F_ProFac( L,B,C_B,C_P,C_M,T_F,T_A,LCB,S_APP,S,apk1,apk2,...
    C_F,C_A,Cstern,D,AEdAO,PdD,zP);

%% Computation of propeller performance in still water

% Z = 5;          % propeller s number of blades []
hk = 0.5;      % distance of the propeller shaft to the keel [m]

try
    [n,P_O,etaO] = F_ProPer (Rtotal,V_S,t,w,etaR,zP,Z,D,PdD,AEdAO,hk,T_A);

%% Computation of brake power in still water

    etaS = 0.99;    % shaft efficience []
    etaGB = 1;      % gearbox efficience []

    P_B = P_O./(etaR.*etaS.*etaGB);

catch
    P_B = 0;
    n = 0;
    etaO = 0;
    etaR = 0;
end

% display(P_B); display(n); display(etaO); display(etaR);

end
