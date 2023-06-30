% DIFFERENTIAL EVOLUTION Optimization Method
% by Cr�stofer Hood Marques

clear;
close all;
clc;


V_S = 7;
[D, Z, AEdAO, PdD, P_B] = F_DifEvo_LH2(V_S)










% -------------------
% V_S = 7;
% Z = 5;
% D =  0.80000;
% AEdAO =  0.67589;
% PdD =  0.72236;
%
%
% [out1, out2, out3, out4] = F_LabH2(V_S,D,Z,AEdAO,PdD);
% display(out1);
% display(out2);
% display(out3);
% display(out4);

% ---------------------
% %% Characteristics of the problem
% V_S = 7.0;
% nv = 4;           % number of variables
%
% % Upper and lower limits D,Z,AEdAO,PdD,
% LimU = [0.8 7 1.05 1.4];
% LimL = [0.5 2 0.30 0.5];
%
% %% Method Differential Evolution
%
% np = 1;        % population size
% kmax = 1;      % Number of iterations (generations)
% CR=0.5;         % factor that defines the crossover (0.5 < CR < 1)
% F=0.8;          % weight function that defines the mutation (0.5 < F < 1).
%
% xpo = zeros(np,nv);
% VFi = zeros(np,4);
% VFpo = zeros(np,4);
%
% Xi = zeros(np,nv);
% of = 0;
% ofp = 0;
%
% for i = 1:np
%     display(i);
%     while VFi(i,1) == 0
%         for j = 1:nv
%             % display(j);
%             if j == 2
%                 Xi(i,j) = randi([LimL(1,j) LimU(1,j)]);
%                 % display('if');
%             else
%                 %% Xi(i,j) = random('unif',LimL(1,j),LimU(1,j));
%                 Xi(i,j) = LimL(1,j)
%             end
%             % display(i); display(j); display(Xi(i,j));
%         end
%         ofp = ofp+1;
%         display(ofp);
%         display(Xi(i,4));
%         % display([Xi(i,1),Xi(i,2),Xi(i,3),Xi(i,4)]);
%                                               % F_LabH2(V_S,D,Z,AEdAO,PdD)
%         [VFi(i,1),VFi(i,2),VFi(i,3),VFi(i,4)] = F_LabH2(V_S, Xi(i,1),Xi(i,2),Xi(i,3),Xi(i,4));
%         display('VFi');
%         display(VFi(i,1));
%         display(VFi(i,2));
%         display(VFi(i,3));
%         display(VFi(i,4));
%     end
% end
