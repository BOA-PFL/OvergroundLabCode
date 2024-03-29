clear
clc

addpath('C:\Users\kate.harrison\Documents\GitHub\AgilityAnalysis')
input_dir = 'C:\Users\kate.harrison\Dropbox (Boa)\AgilityPerformance\BOA_mechanisticStudy\Adidas_Ubersonic_June2021\Forces\CMJ_Skater';

cd(input_dir)
files = dir('*PerformanceTestData.txt');
dataList = {files.name};
[f,~] = listdlg('PromptString','Select data files','SelectionMode','multiple','ListString',dataList);

NumbTrials = length(f);

Subject = cell(2, 1);
Shoe = cell(2, 1);
Movement = cell(2, 1);

contact_time = zeros(2,1);
jumpHeight= zeros(2, 1);
Himpulse = zeros(2, 1);
Vimpulse = zeros(2,1);
APimpulse = zeros(2,1);
CT_VertNorm = zeros(2,1);
CT_HorzNorm = zeros(2,1);

FzPeak = zeros(2,1);
FxPeak = zeros(2,1);
FyPeak = zeros(2,1);
FyPeakMin = zeros(2,1);

peakLeftAnklePower = zeros(2, 1);
peakRightAnklePower = zeros(2, 1);
peakLeftKneePower = zeros(2, 1);
peakRightKneePower = zeros(2, 1);
peakLeftHipPower = zeros(2, 1);
peakRightHipPower = zeros(2, 1);

peakLeftInversion = zeros(2, 1);
peakRightInversion = zeros(2, 1);

peakLeftEversion = zeros(2, 1);
peakRightEversion = zeros(2, 1);

peakRightKneeAbduction = zeros(2, 1);
peakLeftKneeAbduction = zeros(2, 1);
RanklePosWork = zeros(2,1);
RankleNegWork = zeros(2,1);
peakPFmoment = zeros(2,1);
peakEVmoment = zeros(2,1);
r = 0;


for i = 1:NumbTrials
    
    FileName = dataList(f(i));
    FileLoc = char(strcat(input_dir,'\', FileName));
    data = dlmread(FileLoc, '\t', 9 , 0);
   
    
    names = split(FileName, ["_", " "]);
    sub = names{1};
    shoe = names{3};
    move = names{4};
    
    
    if strcmp(move,'CMJ')
        R_ForceZ = data(:,9)*-1;
        R_ForceX = data(:,8);
        R_ForceY = data(:,7);

    elseif strcmp(move,'Skater')
       R_ForceZ = data(:,19)*-1;
       R_ForceX = data(:,18)*-1;
       R_ForceY = data(:,17);
    end
    
    
    RankleAngleY = data(:,22);
    RkneeAngleY = data(:,23 );
    RanklePower = data(:,24);
    RkneePower = data(:,25);
    RhipPower = data(:,26);
    %LankleAngleY = 
    %LkneeAngleY = 
    LanklePower = data(:,27);
    LkneePower = data(:,28);
    LhipPower = data(:,29);
    RanklePosPower = RanklePower;
    RanklePosPower(RanklePosPower < 0) = 0;
    RankleNegPower = RanklePower;
    RankleNegPower(RankleNegPower > 0) = 0;
    RankleMomentX = data(:,33);
    RankleMomentY = data(:,34);
    R_ForceZ(R_ForceZ<40) = 0;
    R_ForceX(R_ForceZ<40) = 0;
    
%     fc = 8;
%     fs = 100;
%     
%     [b, a] = butter(4, fc/(fs/2));
%     RankleMomentX = filter(b, a, RankleMomentX);
%     RankleMomentY = filter(b, a, RankleMomentY);
    
    R_steps = zeros(1,2);
    counter = 1;

    for j = 1:length(R_ForceZ)-1
        if R_ForceZ(j) < 20 && R_ForceZ(j+1) > 20
           R_steps(counter) = j;
           counter = counter + 1;
        end
    end

    R_ends = zeros(1,2);
    counter = 1;

    for j = 1:length(R_ForceZ)-1
        if R_ForceZ(j) > 20 && R_ForceZ(j+1) < 20
           R_ends(counter) = j;
           counter = counter + 1;
        end
    end

    if R_ends(1)<R_steps(1)
        R_ends = R_ends(2:end);
    end

    if length(R_steps) > length(R_ends)
            R_steps = R_steps(1:length(R_ends)+1);
    elseif length(R_steps) <= length(R_ends)
            R_ends = R_ends(1:length(R_steps)-1);
    end
        
    steps = length(R_ends);

    for j = 1:steps
        Subject{r+j} = sub;
        Shoe{r+j} = shoe;
        Movement{r+j} = move;
        
        contact_time(r+j)= R_ends(j)-R_steps(j);
        ft = (R_steps(j+1) - R_ends(j))/100;
        vi = (9.81*ft)/2;
        jumpHeight(r+j) = 0.5*(vi^2/9.81);
        
        Himpulse(r+j) = sum((R_ForceX(R_steps(j):R_ends(j)).*0.001));
        Vimpulse(r+j) = sum((R_ForceZ(R_steps(j):R_ends(j)).*0.001));
        APimpulse(r+j) = sum(abs(R_ForceX(R_steps(j):R_ends(j)).*0.001));
        CT_VertNorm(r+j) = contact_time(r+j)/Vimpulse(r+j);
        CT_HorzNorm(r+j) = contact_time(r+j)/Himpulse(r+j);
        
        FzPeak(r+j) = max(R_ForceZ(R_steps(j):R_ends(j)));
        FxPeak(r+j) = max(R_ForceX(R_steps(j):R_ends(j)));
        FyPeak(r+j) = max(R_ForceY(R_steps(j):R_ends(j)));
        FyPeakMin(r+j) = min(R_ForceY(R_steps(j):R_ends(j)));
         peakLeftAnklePower(r+j) = max(LanklePower(R_steps(j):R_ends(j)));
         peakRightAnklePower(r+j) = max(RanklePower(R_steps(j):R_ends(j)));
         peakLeftKneePower(r+j) = max(LkneePower(R_steps(j):R_ends(j)));
         peakRightKneePower(r+j) = max(RkneePower(R_steps(j):R_ends(j)));
         peakLeftHipPower(r+j) = max(LhipPower(R_steps(j):R_ends(j)));
         peakRightHipPower(r+j) = max(RhipPower(R_steps(j):R_ends(j)));
         
%         PeakLeftInversion(r+j) = max(data(R_steps(j):R_ends(j), 33));
         peakRightInversion(r+j) = max(RankleAngleY(R_steps(j):R_ends(j)));
%         PeakLeftEversion(r+j) = min(data(R_steps(j):R_ends(j), 33));
         peakRightEversion(r+j) = min(RankleAngleY(R_steps(j):R_ends(j)));
%         PeakLeftKneeAbduction(r+j) = max(LkneeAngleY(R_steps:R_ends(j)));
         peakRightKneeAbduction(r+j) = max(RkneeAngleY(R_steps(j):R_ends(j)));
         RanklePosWork(r+j) = sum(RanklePosPower(R_steps(j):R_ends(j)))*0.01;
         RankleNegWork(r+j) = sum(RankleNegPower(R_steps(j):R_ends(j)))*0.01;
         peakPFmoment(r+j) = min(RankleMomentX(R_steps(j):R_ends(j)));
         peakEVmoment(r+j) = min(RankleMomentY(R_steps(j):R_ends(j)));
    end 
    
    r=length(contact_time);
    
end 

Titles = {'SubjectName', 'Shoe', 'Movement', 'ContactTime', 'jumpHeight','VertImpulse', 'HorzImpulse', 'APImpulse', 'CT_VertNorm', 'CT_HorzNorm', 'FzPeak', 'FxPeak', 'FyPeak', 'FyPeakMin', 'peakRankleINV', 'peakRankleEV', 'peakRkneeABD', 'pRanklePower', 'pRkneePower', 'pRhipPower', 'pLanklePower', 'pLkneePower', 'pLhipPower', 'RanklePosWork', 'RankleNegWork', 'peakPFmoment', 'peakEVmoment'};
data = [contact_time, jumpHeight, Vimpulse, Himpulse, APimpulse, CT_VertNorm, CT_HorzNorm, FzPeak, FxPeak, FyPeak, FyPeakMin, peakRightInversion, peakRightEversion, peakRightKneeAbduction, peakRightAnklePower, peakRightKneePower, peakRightHipPower, peakLeftAnklePower, peakLeftKneePower, peakLeftHipPower, RanklePosWork, RankleNegWork, peakPFmoment, peakEVmoment];
data = num2cell(data);
data = horzcat(Subject, Shoe, Movement, data);
data = vertcat(Titles, data);

writecell(data, 'CompiledAgilityData.csv')