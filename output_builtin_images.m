function [items, out_k] = output_builtin_images(items, out_dir, out_k)
    % Recursively output images built in items to out_dir
    % out_k is the index (this sounds suboptimal, but well)

    for i = 1:size(items, 1)
        for j = 1:size(items, 2)
            % 2-d or more numeric matrix : save image
            if isnumeric(items{i, j}) && ndims(items{i, j}) >= 2
                [items{i, j}, out_k] = image_to_file(items{i, j}, out_dir, out_k);
            elseif isstruct(items{i, j}) && isfield(items{i, j}, 'type') && isfield(items{i, j}, 'data') && strcmp(items{i, j}.type, 'image')
                [items{i, j}, out_k] = image_to_file(items{i, j}.data, out_dir, out_k);
            elseif iscell(items{i, j}) % cell ? recurse !
                [modified, out_k] = output_builtin_images(items{i, j}, out_dir, out_k);
                items{i, j} = modified;
            end
        end
    end
end

function [filename, out_k] = image_to_file(im, out_dir, out_k)
    filename = fullfile(out_dir, sprintf('%08d.jpg', out_k));
    out_k = out_k + 1;
    imwrite(im, filename);
end
