%%%%% Single leg landing data %%%%%%
clear
addpath('C:\Users\Daniel.Feeney\Dropbox (Boa)\TMM Files') 
addpath('C:\Users\Daniel.Feeney\Dropbox (Boa)\TMM Files') % add path to source code

% The files should be named sub_balance_Config_trialNo - Forces.txt
input_dir = 'C:\Users\Daniel.Feeney\Dropbox (Boa)\Hike Work Research\Data\BalanceMeasures';% Change to correct filepath

cd(input_dir)
files = dir('*.txt');
dataList = {files.name};
dataList = sort(dataList);
[f,~] = listdlg('PromptString','Select data files for all subjects in group','SelectionMode','multiple','ListString',dataList);
NumbFiles = length(f);

outputAllConfigs = {'SubName','Config','TrialNo','TimeToStab','pkZ', 'stabZ', 'stabY', 'stabX','RMSx','RMSy', 'RMSvx', 'RMSvy', 'DistX', 'DistY', 'AvgVX', 'AvgVY'};

% Set constants
fThresh = 50; %Force threshold. Values below this are set to 0
steadyLength = 200; %length of window to look at steady balancing
    
for s = 1:NumbFiles
    %% Force data
    fileName = dataList{f(s)};
    fileLoc = [input_dir '\' fileName];
    forceData = importForces(fileLoc);
    splitFName = strsplit(fileName,'_'); subName = splitFName{1};
    configName = splitFName{3};
    trialNo = strsplit(splitFName{4},'-'); trialNo = str2num(trialNo{1});
   

    %Break into componentry
    ForceZ = -1 * forceData.RForceZ; %Vertical force
    ForceZ(ForceZ < fThresh) = 0;
    ForceY = forceData.RForceY; %ML Force
    ForceX = forceData.RForceX; %AP force
    
    subBW = mean(ForceZ(end-200:end-100));
    trueLanding = find(ForceZ,1) - 1; %When did they land
    % Feature extraction from each trial
    
    %Time to stabilize
    win_len = 50; %window length for steady standing
    for i = trueLanding:(length(ForceZ)-50)
        avgF(i) = mean(ForceZ(i-win_len/2:i+win_len/2));
        sdF(i) = std(ForceZ(i-win_len/2:i+win_len/2));
    end
    
    
    stabilized = zeros(1,100);
    counter = 1;
    for step = 1:length(avgF)
        if (avgF(step) > (0.95*subBW)) && (avgF(step)< (1.05*subBW)) && (sdF(step) < 25)
            stabilized(counter) = step;
            counter = counter + 1;
        end
    end
    
    stable = (stabilized(1) - trueLanding) / 100;
    balanceStart = stabilized(1);
    
    pkZ = max(ForceZ(trueLanding:stabilized(1)));
    
    stab_Z = std(ForceZ(stabilized(1):stabilized(1)+steadyLength));
    stab_Y = std(ForceY(stabilized(1):stabilized(1)+steadyLength));
    stab_X = std(ForceX(stabilized(1):stabilized(1)+steadyLength));
    
    %RMS of the demeaned x and y COP data
    rms(forceData.RCOPx(stabilized(1):stabilized(1)+steadyLength) - mean(forceData.RCOPx(stabilized(1):stabilized(1)+steadyLength))); 
    rms(forceData.RCOPy(stabilized(1):stabilized(1)+steadyLength) - mean(forceData.RCOPy(stabilized(1):stabilized(1)+steadyLength)));
    
    % Calculate COP velocity
    COPvX = diff(forceData.RCOPx) / 0.01; 
    COPvY = diff(forceData.RCOPy) / 0.01; 
    
    KinData = [stable, pkZ, stab_Z, stab_Y, stab_X, rms(forceData.RCOPx(balanceStart:balanceStart + steadyLength) - mean(forceData.RCOPx(balanceStart:balanceStart + steadyLength))),...
        rms(forceData.RCOPy(balanceStart:balanceStart + steadyLength) - mean(forceData.RCOPy(balanceStart:balanceStart + steadyLength))),...
        rms(COPvX(balanceStart:balanceStart + steadyLength)),rms(COPvX(balanceStart:balanceStart + steadyLength)), sum(abs(diff(forceData.RCOPx(balanceStart:balanceStart + steadyLength)))),...
        sum(abs(diff(forceData.RCOPy(balanceStart:balanceStart + steadyLength)))),...
        mean(abs(COPvX(balanceStart:balanceStart + steadyLength))), mean(abs(COPvY(balanceStart:balanceStart + steadyLength)))];
    
        % Tidy up and add to previous data
    KinData = num2cell(KinData);
    KinData = horzcat(subName,configName,trialNo, KinData); %modulate this to subject name and config
    outputAllConfigs = vertcat(outputAllConfigs, KinData);
    
end
% Convert cell to a table and use first row as variable names
T = cell2table(outputAllConfigs(2:end,:),'VariableNames',outputAllConfigs(1,:))
% Write the table to a CSV file
writetable(T,'SLTestFile.csv')