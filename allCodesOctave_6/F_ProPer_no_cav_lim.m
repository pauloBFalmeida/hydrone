function [n,PO,etaO] = F_ProPer_no_cav_lim(R,Vs,t,w,etaR,zP,Z,D,PdD,AEdAO,hk,Ta)

% F_ProPer - Computation of propeller performance through Wageningen
% B-series prepellers.
% display('F_ProPer');
%% Water input data
rho = 999;         % [kg/m^3] water density
nu = 1.1390e-6;       % [m^2/s] kinematic viscosity
g = 9.80665;          % [m/s^2] gravity acceleration
patm = 101325;       % [Pa] atmospheric pressure
pv = 1704;               % [Pa] vapour pressure of seawater (15 °C)

% Unit convertion
R = R*1000/zP;          % [N]
Vs = Vs*1852/3600;      % [m/s]

% Preliminary calculations
T = R/(1-t);        % [N] thrust
Va = Vs*(1-w);      % [m/s] velocity of advance
C075R = 2.073*AEdAO*D/Z;  % Propeller chord lenght at 0.75 of radius [m]

%% Constants for calculation of thrus coef. polynomial KtM = [Ct s t u v]
KtM = [0.00880496 0 0 0 0 ; -0.204554 1 0 0 0 ; 0.166351 0 1 0 0 ; ...
       0.158114 0 2 0 0 ; -0.147581 2 0 1 0 ; -0.481497 1 1 1 0 ; ...
       0.415437 0 2 1 0 ; 0.0144043 0 0 0 1 ; -0.0530054 2 0 0 1 ; ...
       0.0143481 0 1 0 1 ; 0.0606826 1 1 0 1 ; -0.0125894 0 0 1 1 ; ...
       0.0109689 1 0 1 1 ; -0.133698 0 3 0 0 ; 0.00638407 0 6 0 0 ; ...
       -0.00132718 2 6 0 0 ; 0.168496 3 0 1 0 ; -0.0507214 0 0 2 0 ; ...
       0.0854559 2 0 2 0 ; -0.0504475 3 0 2 0 ; 0.010465 1 6 2 0 ; ...
       -0.00648272 2 6 2 0 ; -0.00841728 0 3 0 1 ; 0.0168424 1 3 0 1 ; ...
       -0.00102296 3 3 0 1 ; -0.0317791 0 3 1 1 ; 0.018604 1 0 2 1 ; ...
       -0.00410798 0 2 2 1 ; -0.000606848 0 0 0 2 ; -0.0049819 1 0 0 2 ;...
       0.0025983 2 0 0 2 ; -0.000560528 3 0 0 2 ; -0.00163652 1 2 0 2 ; ...
     -0.000328787 1 6 0 2 ; 0.000116502 2 6 0 2 ; 0.000690904 0 0 1 2 ; ...
     0.00421749 0 3 1 2 ; 0.0000565229 3 6 1 2 ; -0.00146564 0 3 2 2];

%% Finding J in order to have Kt (thrust coef.) = Kts (ship thrust coef.)
J = 0;
Kt = 1;
Kts = 0;
Kq = 0;
while Kt>Kts
  J = J+0.1;
  Kt = 0;
  for i = 1:39       % 39 is the number of rows in KtM
    Kt = Kt + KtM(i,1)*J^KtM(i,2)*PdD^KtM(i,3)*AEdAO^KtM(i,4)*Z^KtM(i,5);
  end
  Kts = J^2*T/(rho*Va^2*D^2);
end

while Kts>Kt
  J = J-0.00001;
  Kt = 0;
  for i = 1:39       % 39 is the number of rows in KtM
    Kt = Kt + KtM(i,1)*J^KtM(i,2)*PdD^KtM(i,3)*AEdAO^KtM(i,4)*Z^KtM(i,5);
  end
  Kts = J^2*T/(rho*Va^2*D^2);
end
%eKt = (Kts-Kt)/Kt; % calculation of the residual error

%% Propeller speed calculation
n = Va/(J*D);

% Reynolds number
Rn = sqrt(Va^2+(0.75*pi*D*n)^2)*C075R/nu;       % Reynolds number

%% Correction of Kt and Kq for Rn > 2e06

if Rn>2e+6
  eRn = 1;
  while eRn>0.0001
    deltaKt = 0.000353485 ...
             -0.00333758*AEdAO*J^2 ...
             -0.00478125*AEdAO*PdD*J ...
             +0.000257792*(log10(Rn)-0.301)^2*AEdAO*J^2 ...
             +0.0000643192*(log10(Rn)-0.301)*PdD^6*J^2 ...
             -0.0000110636*(log10(Rn)-0.301)^2*PdD^6*J^2 ...
             -0.0000276305*(log10(Rn)-0.301)^2*Z*AEdAO*J^2 ...
             +0.0000954*(log10(Rn)-0.301)*Z*AEdAO*PdD*J ...
             +0.0000032049*(log10(Rn)-0.301)*Z^2*AEdAO*PdD^3*J;

    deltaKq = -0.000591412 ...
              +0.00696898*PdD ...
              -0.0000666654*Z*PdD^6 ...
              +0.0160818*AEdAO^2 ...
              -0.000938091*(log10(Rn)-0.301)*PdD ...
              -0.00059593*(log10(Rn)-0.301)*PdD^2 ...
              +0.0000782099*(log10(Rn)-0.301)^2*PdD^2 ...
              +0.0000052199*(log10(Rn)-0.301)*Z*AEdAO*J^2 ...
              -0.00000088528*(log10(Rn)-0.301)^2*Z*AEdAO*PdD*J ...
              +0.0000230171*(log10(Rn)-0.301)*Z*PdD^6 ...
              -0.00000184341*(log10(Rn)-0.301)^2*Z*PdD^6 ...
              -0.00400252*(log10(Rn)-0.301)*AEdAO^2 ...
              +0.000220915*(log10(Rn)-0.301)^2*AEdAO^2;

    % Finding J in order to have Kt (thrust coef.) = Kts (ship thrust coef.)
    J = 0;
    Kt = 1;
    Kts = 0;
    Kq = deltaKq;
    while Kt>Kts
      J = J+0.1;
      Kt = deltaKt;
      for i = 1:39       % 39 is the number of rows in KtM
        Kt = Kt + KtM(i,1)*J^KtM(i,2)*PdD^KtM(i,3)*AEdAO^KtM(i,4)*Z^KtM(i,5);
      end
      Kts = J^2*T/(rho*Va^2*D^2);
    end

    while Kts>Kt
      J = J-0.00001;
      Kt = deltaKt;
      for i = 1:39       % 39 is the number of rows in KtM
        Kt = Kt + KtM(i,1)*J^KtM(i,2)*PdD^KtM(i,3)*AEdAO^KtM(i,4)*Z^KtM(i,5);
      end
      Kts = J^2*T/(rho*Va^2*D^2);
    end
    %eKt = (Kts-Kt)/Kt; % calculation of the residual error

    % Propeller speed calculation
    n = Va/(J*D);

    % New reynolds number
    RnN = sqrt(Va^2+(0.75*pi*D*n)^2)*C075R/nu;
    eRn = abs(Rn-RnN)/Rn;
    Rn = RnN;
  end
end

%% Constants for calculation of torque coef. polynomial KqM = [Cq s t u v]

KqM = [0.00379368 0 0 0 0 ; 0.00886523 2 0 0 0 ; -0.032241 1 1 0 0 ; ...
       0.00344778 0 2 0 0 ; -0.0408811 0 1 1 0 ; -0.108009 1 1 1 0 ; ...
       -0.0885381 2 1 1 0 ; 0.188561 0 2 1 0 ; -0.00370871 1 0 0 1 ; ...
       0.00513696 0 1 0 1 ; 0.0209449 1 1 0 1 ; 0.00474319 2 1 0 1 ; ...
       -0.00723408 2 0 1 1 ; 0.00438388 1 1 1 1 ; -0.0269403 0 2 1 1 ; ...
       0.0558082 3 0 1 0 ; 0.0161886 0 3 1 0 ; 0.00318086 1 3 1 0 ; ...
       0.015896 0 0 2 0 ; 0.0471729 1 0 2 0 ; 0.0196283 3 0 2 0 ; ...
       -0.0502782 0 1 2 0 ; -0.030055 3 1 2 0 ; 0.0417122 2 2 2 0 ; ...
       -0.0397722 0 3 2 0 ; -0.00350024 0 6 2 0 ; -0.0106854 3 0 0 1 ; ...
       0.00110903 3 3 0 1 ; -0.000313912 0 6 0 1 ; 0.0035985 3 0 1 1 ; ...
       -0.00142121 0 6 1 1 ; -0.00383637 1 0 2 1 ; 0.0126803 0 2 2 1 ; ...
       -0.00318278 2 3 2 1 ; 0.00334268 0 6 2 1 ; -0.00183491 1 1 0 2 ; ...
    0.000112451 3 2 0 2 ; -0.0000297228 3 6 0 2 ; 0.000269551 1 0 1 2 ; ...
       0.00083265 2 0 1 2 ; 0.00155334 0 2 1 2 ; 0.000302683 0 6 1 2 ; ...
     -0.0001843 0 0 2 2 ; -0.000425399 0 3 2 2 ; 0.0000869243 3 3 2 2 ; ...
     -0.0004659 0 6 2 2 ; 0.0000554194 1 6 2 2];

% Calculation of torque coefficient Kq
for i = 1:47       % 47 is the number of rows in KqM
  Kq = Kq + KqM(i,1)*J^KqM(i,2)*PdD^KqM(i,3)*AEdAO^KqM(i,4)*Z^KqM(i,5);
end

% Propeller torque
Q = Kq*rho*n^2*D^5;     % [N*m]

% Open water efficiency
etaO = J*Kt/(2*pi*Kq);

% Open water power
PO = 2*pi*Q*n/1000;          % [kW]

% Propeller angular speed
n = n*60;       % [rpm]

%% Shaft speed constraint

%{
if n > 900 || n < 855
    %disp([D Z AEdAO PdD zP tmin075dD t075dD]);
    fID = fopen('constraints.txt','a');
    fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f %10s\n',...
        Vs*3600/1852,D,Z,AEdAO,PdD,zP,'ShaftSpeed');
    fclose(fID);
    error('Shaft speed constraint has been reached!');
end
%}

%% Strength constraint

Dft = D*3.280839895013123;      % [ft] diameter
PpHPdZ = PO/etaR*1.341022/Z;    % [hp/blade] propeller power per blade
Sc_psi = 19557;         % [psi] maximum allowable stress

%Dft = 20; PpHPdZ = 3312.5; Sc_psi = 6000; PdD = 1.166; n = 97.2; Z = 4;

tmin075dD = (0.0028+0.21*((2375-1125*PdD)*PpHPdZ/(4.123*n*Dft^3*...
    (Sc_psi+Dft^2*n^2/12788)))^(1/3));

t075dD = 0.0185-0.00125*Z;

%display([tmin075dD t075dD]);
if t075dD < tmin075dD
    %disp([D Z AEdAO PdD zP tmin075dD t075dD]);
    fID = fopen('constraints.txt','a');
    fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f %10s\n',...
        Vs*3600/1852,D,Z,AEdAO,PdD,zP,'Strength');
    fclose(fID);
    error('Strength constraint has been reached!');
end


%% Cavitation Constrant
h = Ta - hk;            % [m] distance from the centre of the propeller to water surface
p0 = patm+rho*g*h;      % [Pa] static pressure at the centre of the propeller

sig07R = (p0-pv)/(0.5*rho*(Va^2+(pi*0.7*n/60*D)^2)); % [] mean cavitation number at 0.7R

AO = pi*D^2/4; % [m] disc area

AE = AO*AEdAO; % [m] expanded area

Ap = (1.067-0.229*PdD)*AE; % [m] projected area for the propeller

tal07R = T/(0.5*rho*Ap*(Va^2+(pi*0.7*n/60*D)^2)); % [] thrust loading coefficient

load('BurrillCurves')
%cavLim = ctal5(sig07R); % thrust loading coefficient for the cavitation limit - MatLab only
cavLim = interp1 (sigma, tal5, sig07R,"extrap");
cavLim += 1;
%display([D Z AEdAO PdD sig07R tal07R]);
if tal07R > cavLim
    %disp([D Z AEdAO PdD zP sig07R tal07R]);
    fID = fopen('constraints.txt','a');
    fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f %10s\n',...
        Vs*3600/1852,D,Z,AEdAO,PdD,zP,'Cavitation');
    fclose(fID);
    error('Cavitation constraint has been reached!');
end

%% Peripherical velocity constraint

Vtip = pi*D*n/60;

if Vtip > 39
    %disp([D Z AEdAO PdD zP Vtip]);
    fID = fopen('constraints.txt','a');
    fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f %10s\n',...
        Vs*3600/1852,D,Z,AEdAO,PdD,zP,'Velocity');
    fclose(fID);
    error('Peripherical velocity constraint has been reached!');
end

%}

% display(n); display(PO); display(etaO);

end
