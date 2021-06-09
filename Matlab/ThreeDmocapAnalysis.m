clear
clc

addpath('C:\Users\kate.harrison\Documents\GitHub\AgilityAnalysis')
input_dir = 'C:\Users\kate.harrison\Dropbox (Boa)\AgilityPerformance\BOA_anklebrace_May21';

cd(input_dir)
files = dir('*Forces.txt');
dataList = {files.name};
[f,~] = listdlg('PromptString','Select data files','SelectionMode','multiple','ListString',dataList);

NumbTrials = length(f);

Subject = cell(2, 1);
Shoe = cell(2, 1);
Movement = cell(2, 1);
%Time = cell(2, 1);

contact_time = zeros(2,1);
jumpHeight= zeros(2, 1);
Himpulse = zeros(2, 1);
Vimpulse = zeros(2,1);
% peakINV = zeros(2,1);
% peakEV = zeros(2,1);


% PeakLeftAnklePower = zeros(2, 1);
% PeakRightAnklePower = zeros(2, 1);
% PeakLeftKneePower = zeros(2, 1);
% PeakRightKneePower = zeros(2, 1);
% PeakLeftHipPower = zeros(2, 1);
% PeakRightHipPower = zeros(2, 1);
% PeakLeftAnkleMomentX = zeros(2, 1);
% PeakRightAnkleMomentX = zeros(2,1);
% PeakLeftKneeMomentX = zeros(2,1);
% PeakRightKneeMomentX = zeros(2, 1);
% PeakLeftHipMomentX = zeros(2,1);
% PeakRightHipMomentX = zeros(2, 1);
% PeakLeftKneeMomentY = zeros(2, 1);
% PeakRightKneeMomentY = zeros(2, 1);
% PeakRightAnkleMomentY = zeros(2, 1);
% PeakLeftHipAdd = zeros(2,1);
% PeakRightHipAdd = zeros(2, 1);
% PeakLeftInversion = zeros(2, 1);
% PeakRightInversion = zeros(2, 1);
% PeakRightPlantarflexion = zeros(2,1);
% PeakRightDorsiflexion = zeros(2,1);
% PeakLeftEversion = zeros(2, 1);
% PeakRightEversion = zeros(2, 1);

r = 0;
for i = 1:NumbTrials
    
    FileName = dataList(f(i));
    FileLoc = char(strcat(input_dir,'\', FileName));
    data = dlmread(FileLoc, '\t', 9 , 1);
   
    
    names = split(FileName, ["_", " "]);
    sub = names{1};
    shoe = names{3};
    move = names{4};
    %timepoint = names{4};
    
    if strcmp(move,'CMJ')
        R_ForceZ = data(:,13)*-1;
        R_ForceX = data(:,11);

    elseif strcmp(move,'Skater')
       R_ForceZ = data(:,3)*-1;
       R_ForceX = data(:,2);
    end
    
    R_ForceZ(R_ForceZ<40) = 0;
    R_ForceX(R_ForceZ<40) = 0;
    
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
        %Time{r+j} = timepoint;
        contact_time(r+j)= R_ends(j)-R_steps(j);
        ft = (R_steps(j+1)-R_ends(j))*0.01;
        vi = (9.81*ft)/2;
        jumpHeight(r+j) = 0.5*(vi^2/9.81);
%         peakINV(r+j) = max(FrontalAnkle(R_steps(j):R_ends(j))); % make sure inversion is positive
%         peakEV(r+j) = min(FrontalAnkle(R_steps(j):R_ends(j)));
        
        Himpulse(r+j) = sum((R_ForceX(R_steps(j):R_ends(j)).*0.001));
        Vimpulse(r+j) = sum((R_ForceZ(R_steps(j):R_ends(j)).*0.001));
       
%         PeakLeftAnklePower(r+j) = max(data(R_steps(j):R_ends(j), 1));
%         PeakRightAnklePower(r+j) = max(data(R_steps(j):R_ends(j), 2));
%         PeakLeftKneePower(r+j) = max(data(R_steps(j):R_ends(j), 3));
%         PeakRightKneePower(r+j) = max(data(R_steps(j):R_ends(j), 4));
%         PeakLeftHipPower(r+j) = max(data(R_steps(j):R_ends(j), 5));
%         PeakRightHipPower(r+j) = max(data(R_steps(j):R_ends(j), 6));
%         PeakLeftAnkleMomentX(r+j) = max(data(R_steps(j):R_ends(j), 7));
%         PeakRightAnkleMomentX(r+j) = max(data(R_steps(j):R_ends(j), 8));
%         PeakLeftKneeMomentX(r+j) = min(data(R_steps(j):R_ends(j), 11));
%         PeakRightKneeMomentX(r+j) = min(data(R_steps(j):R_ends(j), 12));
%         PeakLeftHipMomentX(r+j) = max(data(R_steps(j):R_ends(j), 15));
%         PeakRightHipMomentX(r+j) = max(data(R_steps(j):R_ends(j), 16));
%         PeakLeftKneeMomentY(r+j) = max(data(R_steps(j):R_ends(j), 13));
%         PeakRightKneeMomentY(r+j) = max(data(R_steps(j):R_ends(j), 14));
%         PeakRightAnkleMomentY(r+j) = max(data(R_steps(j):R_ends(j), 10));
%         PeakLeftHipAdd(r+j) = max(data(R_steps(j):R_ends(j), 43));
%         PeakRightHipAdd(r+j) = max(data(R_steps(j):R_ends(j), 44));
%         PeakLeftInversion(r+j) = max(data(R_steps(j):R_ends(j), 33));
%         PeakRightInversion(r+j) = max(data(R_steps(j):R_ends(j), 34));
%         PeakLeftEversion(r+j) = min(data(R_steps(j):R_ends(j), 33));
%         PeakRightEversion(r+j) = min(data(R_steps(j):R_ends(j), 34));
%         PeakRightPlantarflexion(r+j) = min(data(R_steps(j):R_ends(j), 32));
%         PeakRightDorsiflexion(r+j) = max(data(R_steps(j):R_ends(j), 32));
         
    end 
    
    r=length(contact_time);
    
end 

Titles = {'SubjectName', 'Shoe', 'Movement', 'ContactTime', 'jumpHeight', 'HorzImpulse'};
data = [contact_time, jumpHeight, Himpulse];
data = num2cell(data);
data = horzcat(Subject, Shoe, Movement, data);
data = vertcat(Titles, data);

writecell(data, 'CompiledAgilityData.csv')