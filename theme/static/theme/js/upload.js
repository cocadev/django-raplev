$(function () {
    $("#fileupload").fileupload({
        dataType: 'json',
        sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
        add: function( e, data ) {
            data.context = $('<div class="proof-gift__upload-bars"></div>').append('<div class="proof-gift__upload-bar upload-bar"></div>')
                .appendTo('#uploadlist');
        
            var context_value = $('<span class="upload-bar__value">0%</span>');
            var context_name = $('<span class="upload-bar__file"></span>').append(data.files[0].name);
            var progress_bar = $('<div class="upload-bar__progress"></div>');

            data.context.children().append(context_value).append(context_name).append(progress_bar);
            data.submit();
        },
        progress: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var strProgress = progress + "%";
            data.context.find(".upload-bar__progress").css({"width": strProgress});
            data.context.find(".upload-bar__value").text(strProgress);
            
        },
        done: function (e, data) {
            if (data.result.is_valid) {
                var values = $('.instead_of_file').val() ? $('.instead_of_file').val().split(',') : [];
                values = values.filter(function(el) {
                    return el != ''
                })
                values.push(data.result.id)
                $('.instead_of_file').val(values.join(','))
                // $("#gallery tbody").prepend(
                //     "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
                // )
            }
        }
    });
    

});

function removeFileList(id) {
    values = $('.instead_of_file').val() ? $('.instead_of_file').val().split(',') : [];
    values = values.filter(function(el) {
        return el != id
    })
    $('.instead_of_file').val(values.join(','))
    // console.log(values)
    $('[file_id='+id+']').remove()
}