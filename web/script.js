var timStatus_getData;

function status_getData() {
    try {
        $.getJSON("/status", function (data) {
            localStorage.setItem("status", JSON.stringify(data));
            status_getSuccess(data);
        }).fail(function (d) {
            console.log('status_getData fail');
            localStorage.removeItem("status");
            status_getSuccess(null);
        });
    } catch (e) {
        console.log('status_getData failure');
        localStorage.removeItem("status");
        status_getSuccess(null);
    }
}

var sImageHTML = '';

function status_getSuccess(result) {
    try {
        if (result != null) {
            if (result['mode'] == 1 || result['mode'] == 2 || result['mode'] == 3) {
                if (result['mode'] == 1) $('#sStatus').text('Manual: Full Stop');
                if (result['mode'] == 2) $('#sStatus').text('Manual: Stop; Resume next schedule');
                if (result['mode'] == 3) $('#sStatus').text('Manual: Stop; Resume next day');
                $('#pStatus-Play').hide();
                $('#pStatus-Stop').hide();
                $('#pStatus-Next').hide();
                $('#sSource').text('');
                $('#sProgramme').text('');
                $('#sTitle').text('');
                $('#sImage').text('');
                $('#sPlayTime').text('');
            } else {
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
        $.getJSON("/config", function (data) {
            localStorage.setItem("config", JSON.stringify(data));
            config_getSuccess(data);
        }).fail(function (d) {
            console.log('config_getData fail');
            localStorage.removeItem("config");
            config_getSuccess(null);
        });
    } catch (e) {
        console.log('config_getData failure');
        localStorage.removeItem("config");
        config_getSuccess(null);
    }
}

function config_getSuccess(result) {
    try {
        $('#pSources table tbody tr').remove();
        if (result != null) {
            if (result.sources != null && result.sources.length > 0) {
                for (var i in result['sources']) {
                    var rowText = "<tr data-sid=\"" + result['sources'][i]['id'] + "\"><th>" + result['sources'][i]['name'] + "</th><td>";
                    if (result['sources'][i]['image'] != null) {
                        rowText = rowText + "<img src=\"" + result['sources'][i]['image'] + "\">";
                    } else {
                        rowText = rowText + "&nbsp;";
                    }
                    rowText = rowText + "</td><td class=\"playbackControls\"><span class=\"Sources-Play\" data-type=\"manualplay\" data-action=\"source-play\" data-sid=\"" + result['sources'][i]['id'] + "\" title=\"Play Source\"></span></td></tr>";
                    $('#pSources table tbody').append(rowText);
                }
            }
        }
        $("span[data-action]").off("click").click(musicplayer_setAction);
        $("button[data-action]").off("click").click(musicplayer_setAction);

    } catch (e) {
        $('#pSources table tbody').empty();
    }
}


function musicplayer_setAction() {

    //Fire Action
    if (this) {
        var datatype = $(this).data('type');
        var dataaction = $(this).data('action');
        var datasid = $(this).closest("tr").data('sid');
        console.log('musicplayer_setAction', datatype, dataaction, datasid);

        if (datatype == 'manualcontrol') {
            var dataSource = $("#pPlayManualSource").val();
            var dataOtherUrl = $("#pPlayManualOtherUrl").val();
            var dataOtherTitle = $("#pPlayManualOtherTitle").val();
            var dataOtherImage = $("#pPlayManualOtherImage").val();

            if (dataaction == 'manualopen')
                musicplayer_showmanual();
            else if (dataaction == 'close')
                musicplayer_closemanual();
            else if (dataaction == 'normal')
                musicplayer_doAction(0, null, null, null, null);
            else if (dataaction == 'fullstop')
                musicplayer_doAction(1, null, null, null, null);
            else if (dataaction == 'pauseschedule')
                musicplayer_doAction(2, null, null, null, null);
            else if (dataaction == 'pausesday')
                musicplayer_doAction(3, null, null, null, null);
            else if (dataaction == 'source-stop')
                musicplayer_doAction(11, dataSource, null, null, null);
            else if (dataaction == 'source-schedule')
                musicplayer_doAction(12, dataSource, null, null, null);
            else if (dataaction == 'source-day')
                musicplayer_doAction(13, dataSource, null, null, null);
            else if (dataaction == 'other-stop')
                musicplayer_doAction(21, null, dataOtherUrl, dataOtherTitle, dataOtherImage);
            else if (dataaction == 'other-schedule')
                musicplayer_doAction(22, null, dataOtherUrl, dataOtherTitle, dataOtherImage);
            else if (dataaction == 'other-day')
                musicplayer_doAction(23, null, dataOtherUrl, dataOtherTitle, dataOtherImage);
        } else if (datatype == 'manualplay') {
            datasid = $(this).data('sid');
            if (dataaction == 'source-play')
                musicplayer_doAction(12, datasid, null, null, null);
        } else {
            var sUrlPost = "/player/";
            if (dataaction == 'statusnext')
                sUrlPost += 'next';
            else if (dataaction == 'statusstop')
                sUrlPost += 'stop';
            else if (dataaction == 'statusplay')
                sUrlPost += 'play';
            else if (dataaction == 'playsource')
                sUrlPost += 'play/' + datasid;

            $.getJSON(sUrlPost + '?sid=' + Math.random(), function (data, status) {
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
}


function musicplayer_doAction(modeID, sourceID, otherUrl, otherTitle, otherImage) {
    var dataObject = { 'mode': modeID, 'source': sourceID, 'url': otherUrl, 'title': otherTitle, 'image': otherImage };

    // Post Data
    $.ajax({
        url: '/control',
        type: 'put',
        data: JSON.stringify(dataObject),
        headers: {
            "Content-Type": "application/json"
        },
        dataType: 'json'
    }).done(function (data) {
        if (data['action'] == true) {
            musicplayer_closemanual();
            config_getData();
        } else {
            window.alert("Control Action Issue\n" + data['message']);
            console.log("Sample of data:", data);
        }
    }).fail(function (d) {
        console.log('musicplayer_doAction fail');
        window.alert("Control Action Failed\n" + d);
    });

}

function musicplayer_showmanual() {
    $("#pModalBack").fadeIn();

    var status = JSON.parse(localStorage.getItem("status"));
    var config = JSON.parse(localStorage.getItem("config"));
    var manualsource = '';
    var manualOtherUrl = '';
    var manualOtherTitle = '';
    var manualOtherImage = '';
    
    $("#manualmodetext").text("Unknown");
    $("button[data-action='normal']").show();
    $("button[data-action='fullstop']").show();
    $("button[data-action='pauseschedule']").show();
    $("button[data-action='pausesday']").show();
    if (status['mode'] == 0) {
        $("button[data-action='normal']").hide();
        $("#manualmodetext").text("Normal running");
    } else if (status['mode'] == 1) {
        $("#manualmodetext").text("Full Stop");
        $("button[data-action='fullstop']").hide();
        $("button[data-action='pauseschedule']").hide();
        $("button[data-action='pausesday']").hide();
    } else if (status['mode'] == 2 || status['mode'] == 3) {
        if (status['mode'] == 2)
            $("#manualmodetext").text("Stop, Resume next schedule");
        if (status['mode'] == 3)
            $("#manualmodetext").text("Stop, Resume next day");
        $("button[data-action='pauseschedule']").hide();
        $("button[data-action='pausesday']").hide();
    } else if (status['mode'] == 11 || status['mode'] == 12 || status['mode'] == 13) {
        if (status['mode'] == 11)
            $("#manualmodetext").text("Play Source, Schedule paused");
        if (status['mode'] == 12)
            $("#manualmodetext").text("Play Source, Resume next schedule");
        if (status['mode'] == 13)
            $("#manualmodetext").text("Play Source, Resume next day");
        manualsource = config['manual']['source'];
    } else if (status['mode'] == 21 || status['mode'] == 22 || status['mode'] == 23) {
        if (status['mode'] == 21)
            $("#manualmodetext").text("Play Other, Schedule paused");
        if (status['mode'] == 22)
            $("#manualmodetext").text("Play Other, Resume next schedule");
        if (status['mode'] == 23)
            $("#manualmodetext").text("Play Other, Resume next day");
        manualOtherUrl = config['manual']['url'];
        manualOtherTitle = config['manual']['title'];
        manualOtherImage = config['manual']['image'];
    }

    // populate dropdown
    $('#pPlayManualSource')
        .find('option')
        .remove()
        .end()
        .append('<option value=""> - Select Source - </option>');
    for (var i in config['sources']) {
        $('#pPlayManualSource').append('<option value="' + config['sources'][i]['id'] + '"'+( config['sources'][i]['id'] == manualsource ? " selected" : "")+'>' + config['sources'][i]['name'] + '</option>');
    }
    $("#pPlayManualOtherUrl").val(manualOtherUrl);
    $("#pPlayManualOtherTitle").val(manualOtherTitle);
    $("#pPlayManualOtherImage").val(manualOtherImage);

    $("#pPlayManual").show();
    confedit_modalCenter("pPlayManual");
    $("span[data-action]").off("click").click(musicplayer_setAction);
    $("button[data-action]").off("click").click(musicplayer_setAction);

}

function musicplayer_closemanual() {
    $("#pPlayManual").hide();
    $("#pModalBack").fadeOut();
}


// Config Editor

function confedit_modalCenter(modalName) {
    try {
        var dv = $("#pModalBack");
        var di = $("#" + modalName);

        var newTop = ((dv.height() - di.height()) / 2);
        newTop = parseInt(newTop) + parseInt(dv.offset().top);

        var newLeft = ((dv.width() - di.width()) / 2);
        newLeft = parseInt(newLeft) + parseInt(dv.offset().left);

        di.offset({ top: newTop, left: newLeft });
    } catch (e) {
        console.log("confedit_modalCenter", e);
    }
}


function confedit_getData() {
    try {
        $.getJSON("/config", function (data) {
            confedit_getSuccess(data);
        }).fail(function (d) {
            console.log('confedit_getData fail');
            confedit_getSuccess(null);
        });
    } catch (e) {
        console.log('confedit_getData failure');
        confedit_getSuccess(null);
    }
}

function confedit_getSuccess(result) {
    try {
        // Clear Existings
        $('#pEditSource table tbody').empty();
        $('#pEditSchedule table tbody').empty();
        if (result != null) {
            // Save Local
            localStorage.setItem("config", JSON.stringify(result));
            // List Sources
            if (result.sources != null && result.sources.length > 0) {
                for (var i in result['sources']) {
                    var rowItem = "<tr data-type=\"source\" data-action=\"edit\" data-sid=\"" + result['sources'][i]['id'] + "\"><th>" + result['sources'][i]['name'] + "</th>";
                    rowItem += "<td>" + result['sources'][i]['url'] + "</td>";
                    if (result['sources'][i]['image'] != null)
                        rowItem += "<td><img src=\"" + result['sources'][i]['image'] + "\"></td>";
                    else
                        rowItem += "<td>-</td>";
                    if (result['sources'][i]['programme'] != null && result['sources'][i]['programme']['nextpvr'] != null)
                        rowItem += "<td>NextPvr: " + result['sources'][i]['programme']['nextpvr']['channel_id'] + "</td>";
                    else
                        rowItem += "<td>-</td>";
                    rowItem += "</tr>";
                    $('#pEditSource table tbody').append(rowItem);
                }
            }
            // List Schedules
            if (result.schedules != null && result.schedules.length > 0) {
                for (var i in result['schedules']) {
                    var rowItem = "<tr data-type=\"schedule\" data-action=\"edit\" data-sid=\"" + (parseInt(i) + 1) + "\"><td>";
                    for (var id in result['schedules'][i]['day']) {
                        rowItem += getDayName(result['schedules'][i]['day'][id]) + " ";
                    }
                    rowItem += "</td>";
                    rowItem += "<td>" + result['schedules'][i]['start'] + " - " + result['schedules'][i]['stop'] + "</td>";
                    rowItem += "<td>" + getSourceName(result['schedules'][i]['source']) + "</td>";
                    if (i < (result.schedules.length-1)) {
                        rowItem += "<th>" + "<button type=\"button\" data-type=\"schedule\" data-action=\"down\" data-sid=\"" + (parseInt(i) + 1) + "\" class=\"btn btn-sm\" title=\"Move Schedule Down\"><i class=\"imgInit imgEditDown\"></i></button>" + "</th>";
                    } else {
                        rowItem += "<th></th>";
                    }
                    rowItem += "</tr>";
                    $('#pEditSchedule table tbody').append(rowItem);
                }
            }
            $("tr[data-action]").off("click").on("click", confedit_Action);
            $("button[data-action]").off("click").on("click", confedit_Action);
        }
    } catch (e) {
        console.log("confedit_getSuccess", e);
        $('#pEditSource table tbody').empty();
        $('#pEditSchedule table tbody').empty();
    }

    function getSourceName(id) {
        for (var i in result['sources']) {
            if (result['sources'][i]['id'] == id) {
                return result['sources'][i]['name'];
                break;
            }
        }
    }

    function getDayName(val) {
        if (val == 0)
            return "Sun";
        else if (val == 1)
            return "Mon";
        else if (val == 2)
            return "Tue";
        else if (val == 3)
            return "Wed";
        else if (val == 4)
            return "Thu";
        else if (val == 5)
            return "Fri";
        else if (val == 6)
            return "Sat";
    }
}


function confedit_Action() {

    //Fire Action
    if (this) {
        var datatype = $(this).data('type');
        var dataaction = $(this).data('action');
        var dataid = $(this).data('sid');

        if (datatype == "schedule") {
            self.event.preventDefault();
            switch (dataaction) {
                case "down":
                    self.event.stopPropagation();
                    confedit_EditSchedulePatch(dataid);
                    break;
                case "edit":
                    confedit_EditSchedule(dataid);
                    break;
                case "save":
                    confedit_EditScheduleSave();
                    break;
                case "close":
                    confedit_EditScheduleClose();
                    confedit_getData();
                    break;
            }
        } else if (datatype == "source") {
            if (dataaction == "edit")
                confedit_EditSource(dataid);
            if (dataaction == "save")
                confedit_EditSourceSave();
            if (dataaction == "close") {
                confedit_EditSourceClose();
                confedit_getData();
            }

        }
    }
}


function confedit_EditScheduleClose() {
    $("#pEditScheduleEditor").hide();
    $("#pModalBack").fadeOut();
}

function confedit_EditSchedule(id) {
    var config = JSON.parse(localStorage.getItem("config"));

    // clear existing
    $('#pEditScheduleEditorDay0, #pEditScheduleEditorDay1, #pEditScheduleEditorDay2, #pEditScheduleEditorDay3, #pEditScheduleEditorDay4, #pEditScheduleEditorDay5, #pEditScheduleEditorDay6').prop('checked', false);
    $("#pEditScheduleEditorStart").val('');
    $("#pEditScheduleEditorStop").val('');
    $("#pEditScheduleEditorSource").val('');
    $("#pEditScheduleEditor").data('sid', '');
    $('#pEditScheduleEditorDelete').prop('checked', false);
    $('#pEditScheduleEditorDeleteRow').hide();

    // populate dropdown
    $('#pEditScheduleEditorSource')
        .find('option')
        .remove()
        .end()
        .append('<option value=""> - Select Source - </option>');
    for (var i in config['sources']) {
        $('#pEditScheduleEditorSource').append('<option value="' + config['sources'][i]['id'] + '">' + config['sources'][i]['name'] + '</option>');
    }

    if (id != null && id != 0) {
        // Set existing
        var configItem = config['schedules'][parseInt(id) - 1];
        for (var idd in configItem['day']) {
            $('#pEditScheduleEditorDay' + configItem['day'][idd]).prop('checked', true);
        }
        $("#pEditScheduleEditorStart").val(configItem['start']);
        $("#pEditScheduleEditorStop").val(configItem['stop']);
        $("#pEditScheduleEditorSource").val(configItem['source']);
        $("#pEditScheduleEditor").data('sid', id);
        $('#pEditScheduleEditorDeleteRow').show();
    } else
        $("#pEditScheduleEditor").data('sid', "0");

    // Show
    $("#pModalBack").fadeIn();
    $("#pEditScheduleEditor").show();
    confedit_modalCenter("pEditScheduleEditor");
    $("button[data-action]").off("click").click(confedit_Action);
    $(".modelClose").off("click").click(confedit_Action);

}

function confedit_EditScheduleSave() {

    // Read Data
    var dataID = $("#pEditScheduleEditor").data('sid');
    var dataDay = {
        '0': $('#pEditScheduleEditorDay0').prop('checked'),
        '1': $('#pEditScheduleEditorDay1').prop('checked'),
        '2': $('#pEditScheduleEditorDay2').prop('checked'),
        '3': $('#pEditScheduleEditorDay3').prop('checked'),
        '4': $('#pEditScheduleEditorDay4').prop('checked'),
        '5': $('#pEditScheduleEditorDay5').prop('checked'),
        '6': $('#pEditScheduleEditorDay6').prop('checked')
    };
    var dataStart = $("#pEditScheduleEditorStart").val();
    var dataStop = $("#pEditScheduleEditorStop").val();
    var dataSource = $("#pEditScheduleEditorSource").val();

    if (dataID != null && dataID == '')
        dataID = "0";

    var dataObject = { 'sid': dataID, 'Days': dataDay, 'Start': dataStart, 'Stop': dataStop, 'Source': dataSource };

    // Post Data
    let dataAction = (dataID != '0' && $('#pEditScheduleEditorDelete').prop('checked')) ? 'delete' : 'put';
    $.ajax({
        url: '/configeditor/Schedule/' + dataID,
        type: dataAction,
        data: JSON.stringify(dataObject),
        headers: {
            "Content-Type": "application/json"
        },
        dataType: 'json'
    }).done(function (data) {
        if (data['action'] == true) {
            confedit_EditScheduleClose();
            confedit_getData();
        } else {
            window.alert("Schedule Save Failed\n" + data['message']);
            console.log("Sample of data:", data);
        }
    }).fail(function (d) {
        console.log('confedit_EditScheduleSave fail');
        window.alert("Schedule Save Failed\n" + d);
    });

}

function confedit_EditSchedulePatch(id) {

    // Read Data
    var dataObject = { 'sid': id, 'Action': 'down' };

    // Post Data
    $.ajax({
        url: '/configeditor/Schedule/' + id,
        type: 'patch',
        data: JSON.stringify(dataObject),
        headers: {
            "Content-Type": "application/json"
        },
        dataType: 'json'
    }).done(function (data) {
        if (data['action'] == true) {
            confedit_getData();
        } else {
            window.alert("Schedule Move Failed\n" + data['message']);
            console.log("Sample of data:", data);
        }
    }).fail(function (d) {
        console.log('confedit_EditSchedulePatch fail');
        window.alert("Schedule Move Failed\n" + d);
    });

}


function confedit_EditSourceClose() {
    $("#pEditSourceEditor").hide();
    $("#pModalBack").fadeOut();
}

function confedit_EditSource(id) {
    var config = JSON.parse(localStorage.getItem("config"));

    // clear existing
    $("#pEditSourceEditorName").val('');
    $('#pEditSourceEditorTypeGeneric, #pEditSourceEditorTypeNextPvr').prop('checked', false);
    $("#pEditSourceEditorUrl").val('');
    $("#pEditSourceEditorImage").val('');
    $("#pEditSourceEditorChannelID").val('');
    $("#pEditSourceEditorProgrammeID").val('');
    $("#pEditSourceEditorUrlRow").show();
    $("#pEditSourceEditorImageRow").show();
    $("#pEditSourceEditorChannelIDRow").show();
    $("#pEditSourceEditorProgrammeIDRow").show();
    $("#pEditSourceEditor").data('sid', '');
    $('#pEditSourceEditorDelete').prop('checked', false);
    $('#pEditSourceEditorDeleteRow').hide();

    if (id != null && id != 0) {
        // Set existing
        var configItem = getConfigItem(id);
        $("#pEditSourceEditorName").val(configItem['name']);
        $("#pEditSourceEditorUrl").val(configItem['url']);
        $("#pEditSourceEditorImage").val(configItem['image']);
        if (configItem['programme'] != null && configItem['programme']['nextpvr'] != null) {
            $('#pEditSourceEditorTypeNextPvr').prop('checked', true);
            $("#pEditSourceEditorProgrammeID").val(configItem['programme']['nextpvr']['channel_id']);
            if (configItem['url'].includes("channel")) {
                let channelid = configItem['url'].substr(configItem['url'].indexOf("channel") + 8);
                channelid = channelid.substr(0, channelid.indexOf('&'));
                $("#pEditSourceEditorChannelID").val(channelid);
            }
        } else {
            $('#pEditSourceEditorTypeGeneric').prop('checked', true);
        }
        $("#pEditSourceEditor").data('sid', id);
        $('#pEditSourceEditorDeleteRow').show();
    } else {
        // Show Add
        $("#pEditSourceEditor").data('sid', "0");
        $('#pEditSourceEditorTypeGeneric').prop('checked', true);
    }
    // Show
    $("#pModalBack").fadeIn();
    $("#pEditSourceEditor").show();
    confedit_modalCenter("pEditSourceEditor");
    $("button[data-action]").off("click").click(confedit_Action);
    $(".modelClose").off("click").click(confedit_Action);
    $("#pEditSourceEditorTypeGeneric, #pEditSourceEditorTypeNextPvr").off("click").click(confedit_EditSourceType);
    confedit_EditSourceType();

    // Find config item by searching ID
    function getConfigItem(id) {
        for (var i in config['sources']) {
            if (config['sources'][i]['id'] == id) {
                return config['sources'][i];
                break;
            }
        }
    }
}

function confedit_EditSourceType() {
    let isGeneric = $('#pEditSourceEditorTypeGeneric').prop('checked');
    if (isGeneric) {
        $("#pEditSourceEditorUrlRow").show();
        $("#pEditSourceEditorImageRow").show();
        $("#pEditSourceEditorChannelIDRow").hide();
        $("#pEditSourceEditorProgrammeIDRow").hide();
    } else {
        $("#pEditSourceEditorUrlRow").hide();
        $("#pEditSourceEditorImageRow").hide();
        $("#pEditSourceEditorChannelIDRow").show();
        $("#pEditSourceEditorProgrammeIDRow").show();
    }
}

function confedit_EditSourceSave() {

    // Read Data
    var dataID = $("#pEditSourceEditor").data('sid');
    var dataName = $("#pEditSourceEditorName").val();
    var dataUrl = $("#pEditSourceEditorUrl").val();
    var dataImage = $("#pEditSourceEditorImage").val();
    var dataChannelID = $("#pEditSourceEditorChannelID").val();
    var dataProgrammeID = $("#pEditSourceEditorProgrammeID").val();
    var dataType = $('#pEditSourceEditorTypeGeneric').prop('checked') ? 'generic' : 'nextpvr';
    if (dataID != null && dataID == '')
        dataID = "0";

    var dataObject = { 'sid': dataID, 'Name': dataName, 'Type': dataType, 'Url': dataUrl, 'Image': dataImage, 'ChannelID': dataChannelID, 'ProgrammeID': dataProgrammeID };

    // Post Data
    let dataAction = (dataID != '0' && $('#pEditSourceEditorDelete').prop('checked')) ? 'delete' : 'put';
    $.ajax({
        url: '/configeditor/Source/' + dataID,
        type: dataAction,
        data: JSON.stringify(dataObject),
        headers: {
            "Content-Type": "application/json"
        },
        dataType: 'json'
    }).done(function (data) {
        if (data['action'] == true) {
            confedit_EditSourceClose();
            confedit_getData();
        } else {
            window.alert("Source Save Failed\n" + data['message']);
            console.log("Sample of data:", data);
        }
    }).fail(function (d) {
        console.log('confedit_EditSourceSave fail');
        window.alert("Source Save Failed\n" + d);
    });
}
