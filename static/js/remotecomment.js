$(document).ready(function() {
    basepath = "http://willow.ulminfo.fr/";
    $('.comment').each(function(i, obj) {
        $(obj).attr("id","comment" + i.toString());
        var textarea = $(obj).find("textarea").eq(0);
        var button = $(obj).find("button").eq(0);
        button.click(function() {
            $.post(basepath + 'update', {url: $(location).attr('href'), index: i, content: textarea.val()}, function(data) {
                orig_text = button.html();
                button.html("Comment updated");
                button.addClass("btn-success");
                button.delay(200).fadeOut("slow", function() {
                    button.html(orig_text)
                    button.removeClass("btn-success");
                    button.show();
                });
            }, "json");
        });
    });
    $.post(basepath + 'getall', {url: $(location).attr('href')}, function(data) {
        $.each(data.comments, function(i, row) {
        $('#comment' + row.index.toString()).find("textarea").eq(0).val(row.content);
        });
    }, "json");
});
