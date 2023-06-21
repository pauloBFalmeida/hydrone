% DIFFERENTIAL EVOLUTION Optimization Method
% by Cr�stofer Hood Marques

clear;
close all;
clc;

%% Creating output files

tic;

fID = fopen('constraints.txt','w');
fprintf(fID,'%10s %10s %10s %10s %10s %10s %10s\n','Vs[kts]','D[m]',...
    'Z[-]','AE/AO[-]','P/D[-]','zP[-]','Constraint');
fclose(fID);

%% Characteristics of the problem

nv = 4;           % number of variables

% Upper and lower limits D,Z,AEdAO,PdD,
LimU = [0.8 7 1.05 1.4];
LimL = [0.5 2 0.30 0.5];

%% Method Differential Evolution

np = 30;        % population size
kmax = 30;      % Number of iterations (generations)
CR=0.5;         % factor that defines the crossover (0.5 < CR < 1)
F=0.8;          % weight function that defines the mutation (0.5 < F < 1).

xpo = zeros(np,nv);
VFi = zeros(np,4);
VFpo = zeros(np,4);

% Initial population
Xi = zeros(np,nv);
of = 0;
ofp = 0;
for i = 1:np
    display(i);
    while VFi(i,1) == 0
        for j = 1:nv
            display(j);
            if j == 2
                Xi(i,j) = randi([LimL(1,j) LimU(1,j)]);
            else
                %% Xi(i,j) = random('unif',LimL(1,j),LimU(1,j));
                Xi(i,j) = LimL(1,j)
            end
        end
        ofp = ofp+1;
        display(ofp);
        [VFi(i,1),VFi(i,2),VFi(i,3),VFi(i,4)] = F_LabH2(Xi(i,1),Xi(i,2),...
            Xi(i,3),Xi(i,4));
    end
end

VFk = zeros(np,4,kmax);
Xk = zeros(np,nv,kmax);
X = Xi;
VF = VFi;
VFk(:,:,1) = VFi(:,:);
Xk(:,:,1) = Xi(:,:);
for k = 1:kmax
    display(k);
    for i = 1:np
        alfa = randi(np,1);
        beta = randi(np,1);
        gama = randi(np,1);
        while i==alfa||i==beta||i==gama||alfa==beta||beta==gama||gama==alfa
            alfa = randi(np,1);
            beta = randi(np,1);
            gama = randi(np,1);
        end
        for j = 1:nv
            R = rand(1);
            if R <= CR
                delta1 = 0;
                delta2 = 1;
            else
                delta1 = 1;
                delta2 = 0;
            end
            xpo(i,j) = delta1*X(i,j)+delta2*(X(alfa,j)+F*(X(beta,j)-...
                X(gama,j)));
            if xpo(i,j) > LimU(j)
                xpo(i,j) = LimU(j);
            elseif xpo(i,j) < LimL(j)
                xpo(i,j) = LimL(j);
            end
        end

        xpo(i,2) = round(xpo(i,2)); % discret variable

        % Calculating objective function value for xpo
        [VFpo(i,1),VFpo(i,2),VFpo(i,3),VFpo(i,4)] = F_LabH2(xpo(i,1),...
            xpo(i,2),xpo(i,3),xpo(i,4));
        of = of+1;
        display(of);

        % Verification of the function value
        if VFpo(i,1) < VF(i,1) && VFpo(i,1) > 0
            X(i,:) = xpo(i,:);
            VF(i,:) = VFpo(i,:);
        end
    end
    VFk (:,:,k+1) = VF(:,:);
    Xk (:,:,k+1) = X(:,:);
end
%[VFmax,pVFmax] = max(VF(:,1));
%xopt = X(pVFmax,:);

tElapsed = toc;

%% Saving
tic

save('output.mat') % saving all workspace variables

%% Postprocessing

% Organising data

fID = fopen('constraints.txt','r');
Constr = textscan(fID,'%f %f %f %f %f %f %s\n','headerlines',1);
fclose(fID);

M(:,1) = Constr{1,1}; M(:,2) = Constr{1,2}; M(:,3) = Constr{1,3}; M(:,4) = Constr{1,4};
M(:,5) = Constr{1,5}; M(:,6) = Constr{1,6}; S = Constr{1,7};

C_Str = zeros(size(M)); C_Cav = zeros(size(M)); C_Res = zeros(size(M));
C_Vel = zeros(size(M)); C_Sha = zeros(size(M));

for i = 1:size(S,1)
    tfS = strcmp('Strength',S(i,1));
    if tfS == 1
        C_Str(i,:) = M(i,:);
    else
        tfC = strcmp('Cavitation',S(i,1));
        if tfC == 1;
            C_Cav(i,:) = M(i,:);
        else
            tfR = strcmp('Resonance',S(i,1));
            if tfR == 1;
                C_Res(i,:) = M(i,:);
            else
                tfV = strcmp('Velocity',S(i,1));
                if tfV == 1;
                    C_Vel(i,:) = M(i,:);
                else
                    tfSS = strcmp('ShaftSpeed',S(i,1));
                    if tfSS == 1;
                        C_Sha(i,:) = M(i,:);
                    else
                        error('Something is very wrong!');
                    end
                end
            end
        end
    end
end

C_Str( ~any(C_Str,2), : ) = []; % it removes all rows with zeros
C_Cav( ~any(C_Cav,2), : ) = [];
C_Res( ~any(C_Res,2), : ) = [];
C_Vel( ~any(C_Vel,2), : ) = [];

fID = fopen('C_Strength.txt','w');
fprintf(fID,'%10s %10s %10s %10s %10s %10s\n','Vs[kts]','D[m]',...
    'Z[-]','AE/AO[-]','P/D[-]','zP[-]');
fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f\n',C_Str');
fclose(fID);

fID = fopen('C_Cavitation.txt','w');
fprintf(fID,'%10s %10s %10s %10s %10s %10s\n','Vs[kts]','D[m]',...
    'Z[-]','AE/AO[-]','P/D[-]','zP[-]');
fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f\n',C_Cav');
fclose(fID);

fID = fopen('C_Resonance.txt','w');
fprintf(fID,'%10s %10s %10s %10s %10s %10s\n','Vs[kts]','D[m]',...
    'Z[-]','AE/AO[-]','P/D[-]','zP[-]');
fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f\n',C_Res');
fclose(fID);

fID = fopen('C_Velocity.txt','w');
fprintf(fID,'%10s %10s %10s %10s %10s %10s\n','Vs[kts]','D[m]',...
    'Z[-]','AE/AO[-]','P/D[-]','zP[-]');
fprintf(fID,'%9.8f %9.8f %9.8f %9.8f %9.8f %9.8f\n',C_Vel');
fclose(fID);

SumC = size(C_Str,1)+size(C_Cav,1)+size(C_Vel,1)+size(C_Res,1);

PerCon = SumC/(ofp+of)*100;

PerStr = size(C_Str,1)/SumC*100; PerCav = size(C_Cav,1)/SumC*100;
PerVel = size(C_Vel,1)/SumC*100; PerRes = size(C_Res,1)/SumC*100;

cont_str2 = 0; cont_str3 = 0; cont_str4 = 0; cont_strC = 0;
for i = 1:size(C_Str)
    if C_Str(i,2) > 0.65
       %disp(C_Cav(i,:))
       cont_str2 = cont_str2+1;
    end
    if C_Str(i,3) >= 6
       %disp(C_Cav(i,:))
       cont_str3 = cont_str3+1;
    end
    if C_Str(i,4) < 2
       %disp(C_Cav(i,:))
       cont_str4 = cont_str4+1;
    end
    if C_Str(i,1) > 16 && C_Str(i,3) >= 6 && C_Str(i,6) < 2
       %disp(C_Cav(i,:))
       cont_strC = cont_strC+1;
    end
end

cont_cav = 0;
for i = 1:size(C_Cav)
    if C_Cav(i,4) < 0.675
       %disp(C_Cav(i,:))
       cont_cav = cont_cav+1;
    end
end

cont_vel1 = 0; cont_vel4 = 0; cont_vel5 = 0; cont_velC = 0;
for i = 1:size(C_Vel)
    if C_Vel(i,1) > 16
       %disp(C_Cav(i,:))
       cont_vel1 = cont_vel1+1;
    end
    if C_Vel(i,4) > 0.675
       %disp(C_Cav(i,:))
       cont_vel4 = cont_vel4+1;
    end
    if C_Vel(i,5) < 0.95
       %disp(C_Cav(i,:))
       cont_vel5 = cont_vel5+1;
    end
    if C_Vel(i,1) > 16 && C_Vel(i,4) > 0.675 && C_Vel(i,5) < 0.95
       %disp(C_Cav(i,:))
       cont_velC = cont_velC+1;
    end
end

cont_res1 = 0; cont_res3 = 0; cont_res5 = 0; cont_res6 = 0; cont_resC = 0;
for i = 1:size(C_Res)
    if C_Res(i,1) <= 12
       %disp(C_Cav(i,:))
       cont_res1 = cont_res1+1;
    end
    if C_Res(i,3) <= 3
       %disp(C_Cav(i,:))
       cont_res3 = cont_res3+1;
    end
    if C_Res(i,5) > 0.95
       %disp(C_Cav(i,:))
       cont_res5 = cont_res5+1;
    end
    if C_Res(i,6) > 1
       %disp(C_Cav(i,:))
       cont_res6 = cont_res6+1;
    end
    if C_Res(i,1) <= 12 && C_Res(i,3) <= 3 && C_Res(i,5) > 0.95 && C_Res(i,6) > 1
       %disp(C_Cav(i,:))
       cont_resC = cont_resC+1;
    end
end

VFmax = zeros(1,kmax+1); pVFmax = zeros(1,kmax+1);
VFmin = zeros(1,kmax+1); pVFmin = zeros(1,kmax+1);
VFmean = zeros(1,kmax+1); VFstd = zeros(1,kmax+1);

for k = 1:kmax+1
    [VFmax(k),pVFmax(k)] = max(VFk(:,1,k));
    [VFmin(k),pVFmin(k)] = min(VFk(:,1,k));
    VFmean(k) = mean(VFk(:,1,k));
    VFstd(k) = std(VFk(:,1,k));
end

% Plotting the objective function progress

gen = 0:kmax;

set(0,'defaultlinelinewidth',1.5);
set(0,'DefaultAxesFontSize',20);
set(0,'defaultAxesFontName','Arial');

figure
plot(gen,VFmax,'-',gen,VFmean,'-.',gen,VFmin,'--');
legend('max','mean','min','Location','northeast');
xlim([0 kmax])
xlabel('Generation')
%ylim([100 170])
ylabel('Objective function')
%set(findall(gcf,'-property','FontSize'),'FontSize',16)
print('objFunction.png')

% Plotting the optimisation progress

Xopt2 = zeros(kmax+1,nv);
for i = 1:kmax+1
    Xopt2(i,:) = Xk(pVFmin(1,i),:,i);
end

Xopt2(:,2) = Xopt2(:,2)/10;

figure
p2 = plot(gen,Xopt2);
NameArray = {'LineStyle'};
ValueArray = {'-','--','-.',':'}';
set(p2,NameArray,ValueArray)
%NameArray = {'Color'};
%ValueArray = {'k','k','k','k'}';
%set(p2,NameArray,ValueArray)
#NameArray = {'LineWidth'};
#ValueArray = {1,1,1,1}';
#set(p2,NameArray,ValueArray)
legend('D [m]','Z/10 [-]','A_E/A_O [-]','P/D [-]','Location','eastoutside');
xlabel('Generation');
xlim([0 kmax])
%ylim([0.2 0.9])
ylabel('Values of the variables')
%set(findall(gcf,'-property','FontSize'),'FontSize',12)
print('variables.png','-loose')

%toc
