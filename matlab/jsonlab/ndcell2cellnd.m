%%-------------------------------------------------------------------------
function out=ndcell2cellnd(item)
    % Factorize a n-d cell array into a 1-d cell array holding (n-1)-d cell
    % arrays
    sz = size(item);
    item = reshape(item, sz(sz > 1));
    sz = size(item);
    item = reshape(item, [sz(1) prod(sz(2:end))]);
    outsize = sz(1);
    out = cell(outsize, 1);
    if numel(sz) > 2 % check condition outside of the loop for performance
        for i = 1:outsize
            out{i} = reshape({item{i,:}}, sz(2:end));
        end
    else
        for i = 1:outsize
            out{i} = {item{i,:}};
        end
    end
end
