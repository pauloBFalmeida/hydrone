%#eml
function [P_B,n,etaO,etaR] = F_LabH2_copy(V_S,D,Z,AEdAO,PdD)
% LabH2_F computes the brake power and shaft speed for given propeller
% parameters
% pause (0.5)

P_B = D + AEdAO - PdD;
n = Z;
etaO = AEdAO;
etaR = PdD;

end
