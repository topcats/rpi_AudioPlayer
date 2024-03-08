var timStatus_getData;

function status_getData() {
    try {
        $.getJSON("/status", function(data) {
            status_getSuccess(data);
        }).fail(function(d) {
            console.log('status_getData fail');
            status_getSuccess(null);
        });
    } catch (e) {
        console.log('status_getData failure');
        status_getSuccess(null);
    }
}

var sImageHTML = '';

function status_getSuccess(result) {
    try {
        if (result != null) {
            if (result['aPlayer'] != null && result['aPlayer'] == 'State.Playing') {
                $('#sStatus').text('Playing');
                $('#pStatus-Play').hide();
                $('#pStatus-Stop').show();
                $('#pStatus-Next').hide();
            } else if (result['aPlayerList'] != null && result['aPlayerList'] == 'State.Playing') {
                $('#sStatus').text('Playing List');
                $('#pStatus-Play').hide();
                $('#pStatus-Stop').show();
                $('#pStatus-Next').show();
            } else {
                $('#sStatus').text('Stopped');
                $('#pStatus-Play').show();
                $('#pStatus-Stop').hide();
                $('#pStatus-Next').hide();
            }
            if (result.source != null && result.source.name != null) {
                $('#sSource').text(result.source.name);
            } else {
                $('#sSource').text('');
            }
            var audiotitle = '';
            if (result.title != null && result.title != '' && result.mrl != null) {
                if (!result.title.startsWith(result.mrl.substr(result.mrl.lastIndexOf("/") + 1))) {
                    audiotitle = result.title;
                }
            }
            if (audiotitle == '') {
                if (result.source != null && result.source.name != null) {
                    audiotitle = result.source.name;
                }
            }
            $('#sTitle').html(audiotitle);

            if (result.subtitle != null) {
                $('#sProgramme').text(result.subtitle);
            } else {
                $('#sProgramme').text('');
            }

            var audioimage = '';
            if (result.image != null) {
                audioimage = '<img src="' + result.image + '">';
            } else if (result.source != null && result.source.image != null) {
                audioimage = '<img src="' + result.source.image + '">';
            } else {
                audioimage = '';
            }
            if (sImageHTML != audioimage) {
                sImageHTML = audioimage;
                $('#sImage').html(sImageHTML);
            }

            if (result['playlength'] != null && result['playlength'] > 0) {
                $('#sPlayTime').html('<span style="font-size:smaller;">' + formatNumber(result['playtime']) + '</span> / ' + formatNumber(result['playlength']));
            } else if (result['playtime'] != null && result['playtime'] > 0) {
                $('#sPlayTime').html(formatNumber(result['playtime']));
            } else {
                $('#sPlayTime').html('');
            }
            $('#sControls').show();

        } else {
            $('#sStatus').text('Unknown');
            $('#sProgramme').text('');
            $('#sPlayTime').text('');
            $('#sControls').hide();
        }
    } catch (e) {
        $('#sStatus').text('');
        $('#sSource').text('');
        $('#sTitle').text('');
        $('#sProgramme').text('');
        $('#sImage').text('');
        $('#sPlayTime').text('');
        $('#sControls').hide();
    }
}


function formatNumber(invalue) {
    var returnvalue = '';
    invaluehour = Math.floor(invalue / 3600);
    invalue %= 3600;
    invalueminute = Math.floor(invalue / 60);
    invaluesecond = invalue % 60;
    if (invaluehour != 0) {
        returnvalue = invaluehour + ':';
        if (invalueminute < 10)
            returnvalue += '0';
        returnvalue += invalueminute + ':';
    } else {
        returnvalue = invalueminute + ':';
    }
    if (invaluesecond < 10)
        returnvalue += '0';
    returnvalue += invaluesecond;

    return returnvalue;
}


var timConfig_getData;

function config_getData() {
    try {
        $.getJSON("/config", function(data) {
            config_getSuccess(data);
        }).fail(function(d) {
            console.log('config_getData fail');
            config_getSuccess(null);
        });
    } catch (e) {
        console.log('config_getData failure');
        config_getSuccess(null);
    }
}

function config_getSuccess(result) {
    try {
        $('#pSources table tbody tr').slice(1).remove();
        if (result != null) {
            if (result.sources != null && result.sources.length > 0) {
                for (var i in result['sources']) {
                    if (result['sources'][i]['image'] != null) {
                        $('#pSources table tbody').append("<tr data-sid=\"" + result['sources'][i]['id'] + "\"><th>" + result['sources'][i]['name'] + "</th><td><img src=\"" + result['sources'][i]['image'] + "\"></td><td class=\"playbackControls\"><span id=\"pSources-Play\" data-action=\"playsource\" title=\"Play Source\"></span></td></tr>");
                    } else {
                        $('#pSources table tbody').append("<tr data-sid=\"" + result['sources'][i]['id'] + "\"><th>" + result['sources'][i]['name'] + "</th><td>&nbsp;</td><td class=\"playbackControls\"><span id=\"pSources-Play\" data-action=\"playsource\" title=\"Play Source\"></span></td></tr>");
                    }
                }
            }
        }
        $("span[data-action]").off("click").click(musicplayer_setAction);
    } catch (e) {
        $('#pSources table tbody').empty();
    }
}


function musicplayer_setAction() {

    //Fire Action
    if (this) {
        var dataaction = $(this).data('action');
        var datasid = $(this).closest("tr").data('sid');
        console.log('musicplayer_setAction', dataaction, datasid);

        var sUrlPost = "/player/";
        if (dataaction == 'statusnext')
            sUrlPost += 'next';
        else if (dataaction == 'statusstop')
            sUrlPost += 'stop';
        else if (dataaction == 'statusplay')
            sUrlPost += 'play';
        else if (dataaction == 'playsource')
            sUrlPost += 'play/' + datasid;

        $.getJSON(sUrlPost + '?sid=' + Math.random(), function(data, status) {
            if (data != null) {
                if (data['result'] == true) {
                    console.log("musicplayer_setAction", dataaction, "Action All good");
                } else {
                    console.log("musicplayer_setAction", dataaction, "action not good", data);
                }
            } else {
                console.log("musicplayer_setAction", dataaction, "action failed");
            }
        });

    }
}