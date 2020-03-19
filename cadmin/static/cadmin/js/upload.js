$(function () {
    $("#fileupload").fileupload({
        dataType: 'json',
        sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
        add: function( e, data ) {
            data.context = $('<div class="drag-n-drop__uploading-file upload-bar">')
                .appendTo('#uploadlist');
            
            var context_name = $('<div class="upload-bar__file-name"></div>').append(data.files[0].name);
            var progress_bar = $('<div class="upload-bar__bar"><div class="upload-bar__background"></div><div class="upload-bar__progress" style="width: 0"></div></div>');
            var abort_btn = $('<a class="upload-bar__close-btn"><svg class="upload-bar__close-icon" width="30"><use xlink:href="'+ICON_TIMES+'"></use></svg></a>')
                .attr( 'href', 'javascript:void(0)' )
                .click( function() {
                    data.abort();
                    data.context.remove();
                } );
            
            progress_bar.append(abort_btn);

            data.context.append(context_name)
                .append(progress_bar);

            data.submit();
        },
        progress: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var strProgress = progress + "%";
            data.context.find(".upload-bar__progress").css({"width": strProgress}).text(strProgress);
            
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