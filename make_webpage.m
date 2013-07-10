function items = make_webpage(items, target, params, page_title, page_description)
    % make_webpage(items, target, params, page_title, page_description)
    % Automagically build a pretty webpage from a set of random items
    % Simple usage : simply pass a 1-dim or 2-dims cell array containing
    % your items which can be either text, image paths, video paths, images
    % (as matrices), or more complicated structures (to be defined later)
    % You can also generate subpages by passing such a cell array as one item

    if nargin < 3, params = []; end
    if nargin >= 3 && ~isstruct(params), newparams.copy_images = params; params = newparams; end
    if nargin >= 4, params.title = page_title; end
    if nargin >= 5, params.description = page_description; end

    if ~isfield(params, 'copy_images'), params.copy_images = 0; end
    if ~isfield(params, 'title'), params.title = ''; end
    if ~isfield(params, 'description'), params.description = ''; end
    if ~isfield(params, 'paged'), params.paged = false; end
    if ~isfield(params, 'packed'), params.packed = false; end

    %%
    % Update path
    [curdir, ~, ~] = fileparts(mfilename('fullpath'));
    addpath(genpath(fullfile(curdir, 'jsonlab')));

    %%
    % Make output directory and matrix image output directory
    [target_dir, target_name, target_ext] = fileparts(target);
    if isempty(target_ext) % no extension : this is a directory path
        target_dir = target;
        target = fullfile(target_dir, 'index.html');
    end
    [target_dir, target_name, target_ext] = fileparts(target);
    out_dir = fullfile(target_dir, 'imgs', 'tmp', [target_name target_ext]);
    unix(sprintf('mkdir -p "%s"', out_dir));

    %%
    % Output images contained as matrices
    [items, ~] = output_builtin_images(items, out_dir, 1);

    %%
    % Save as json and run python
    out_json = fullfile(target_dir, 'webpage.json');
    webpage.params = params;
    webpage.params.target = target;
    webpage.params.target_dir = target_dir;
    webpage.items = items;
    savejson('', webpage, 'FileName', out_json, 'ForceRootName', 0);
    pypath = fullfile(curdir, 'jsontohtml.py');
    disp(sprintf('Running python %s %s', pypath, out_json));
    [ret, ~] = python(pypath, out_json);
    disp(ret);
end
