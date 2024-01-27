function results = json2result(trials,labelstrs)

nc = numel(labelstrs);
np = numel(trials);
ns = numel(trials(1).stimuli);

results = -ones(np,nc);

for p = 1:np
    for s = 1:ns
        if iscell(trials(p).stimuli)
            stimulus = trials(p).stimuli{s};
        else
            stimulus = trials(p).stimuli(s);
        end
        
        if stimulus.attention_check
        	continue;
        end
        
        % Detect system ID for this slider
        labelstr = stimulus.condition;
        
        whichc = false(1,nc);
        for c = 1:nc
            whichc(c) = strcmp(labelstrs{c},labelstr);
        end
        if sum(whichc) ~= 1
            error('Failed to uniquely identify system!');
        end
        c = find(whichc);
        
        if results(p,c) >= 0
            warning('Overwriting existing rating. Duplicate system?');
        end
        score = stimulus.score;
        if (score < 0) || (score > 100)
            error(['Invalid score "'...
                stimulus.score '"']);
        end
        results(p,c) = score;
    end
    
    okratings = sum(results(p,:) >= 0);
    if (okratings ~= ns) && (okratings ~= ns-1)
        warning('Number of ratings differs from what is expected.');
    end
end

results(results < 0) = NaN; % Set missing entries to NaN