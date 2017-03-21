/**
 * Created by mingming on 17-3-8.
 */


jQuery(document).ready(function($)
{
    /* Global Settings */

    // Progress Bar
    var opts = {
        "closeButton": true,
        "debug": false,
        "positionClass": "toast-top-right",
        "onclick": null,
        "showDuration": "500",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    var status_editor = CodeMirror.fromTextArea($(".json")[0], { //script_once_code为你的textarea的ID号
        lineNumbers: true,//是否显示行号
        mode: "application/json",　//默认脚本编码
        lineWrapping: true,//是否强制换行
        indentUnit: 4,
        styleActiveLine: true
        });

    var python_editor = CodeMirror.fromTextArea($(".python")[0], { //script_once_code为你的textarea的ID号
        lineNumbers: true,//是否显示行号
        mode: "python",　//默认脚本编码
        indentUnit: 4,
        lineWrapping: true //是否强制换行
        });


    /* debug page */

    //Edit Project
    function editProject(data) {
        $.ajax({
        url: "/dashboard/api/edit",
        method: 'POST',
        dataType: 'json',
        data: data,
        success: function(resp) {
            show_loading_bar({
                delay: .5,
                pct: 100,
                finish: function () {
                    // Redirect after successful login page (when progress bar reaches 100%)
                    if (resp.status == true) {
                        toastr.success(resp.message, "Message:", opts);
                        setTimeout(function(){ window.location.reload();},600);
                    }
                    else {
                        // alert(resp.reason);
                        toastr.error(resp.message, "Message:", opts);
                    }
                }
            });
        },
        error: function(resp) {
                        show_loading_bar({
                            delay: .5,
                            pct: 100,
                            finish: function () {
                                toastr.error("Network error.", "Message:", opts);
                            }
                        });
                    }
        });

    }

     // Run Project
    function runProject(data) {
        $.ajax({
            url: "/dashboard/api/run",
            method: 'POST',
            dataType: 'json',
            data: data,
            success: function(resp) {
                show_loading_bar({
                    delay: .5,
                    pct: 100,
                    finish: function () {
                        // Redirect after successful login page (when progress bar reaches 100%)
                        if (resp.status === true) {
                            toastr.success(resp.message, "Message:", opts);
                            var task_result = resp.task;
                            var tasks = task_result.result;

                            if(task_result.status===false){
                                status_editor.setValue(JSON.stringify(task_result));
                            }
                            else if(tasks.project != undefined ){
                                status_editor.setValue(JSON.stringify(task_result));
                            }
                            else {
                                status_editor.setValue("Debug...                                                                                ");

                                var rowCount = tasks.length;
                                var tbody = $("#url-table");
                                var task_number = $("#task-number");

                                tbody.html("<tr></tr>");
                                task_number.html(rowCount);
                                for (var i = 0; i < rowCount; i++){
                                    var task = tasks[i];
                                    var tr = $("<tr></tr>");
                                    if(task.status === false){
                                         var td = $("<td class=\"col-md-3 no-padding-textarea text-danger\">" + task.result.callback+
                                               "</td><td class=\"col-md-8 no-padding-textarea\">" + task.result.url +
                                               "</td><td class=\"col-md-1 no-padding-textarea\"><button class=\"btn btn-success btn-single btn-xs run-task\" task='"+
                                               JSON.stringify(task.result)+"'>run</button></td>");
                                    }
                                    else{
                                         var td = $("<td class=\"col-md-3 no-padding-textarea text-secondary\">" + task.result.callback+
                                               "</td><td class=\"col-md-8 no-padding-textarea text-info task-url\">" + task.result.url +
                                               "</td><td class=\"col-md-1 no-padding-textarea \"><button class=\"btn btn-success btn-single btn-xs run-task\" task='"+
                                               JSON.stringify(task.result)+"'>run</button></td>");
                                    }
                                    td.appendTo(tr);
                                    tr.appendTo(tbody);
                                }
                                $(".run-task").on('click',function(){
                                    var name = $("#script").attr("project");
                                    var task = $(this).attr('task');
                                    var data = {
                                        command: true,
                                        project: name,
                                        task:task
                                    };
                                    runProject(data);
                                });
                                 $(".task-url").on('click',function(){
                                     var task = $(this).parent().find('button').attr('task');
                                     status_editor.setValue(task);
                                     $(this).removeClass("text-info");
                                });
                                $("#task-table").removeClass("hidden");
                            }
                        }
                        else {
                            toastr.error(resp.message, "Message:", opts);
                        }
                    }
                });
            },
            error: function(resp) {
                            show_loading_bar({
                                delay: .5,
                                pct: 100,
                                finish: function () {
                                    toastr.error("Network error.", "Message:", opts);
                                }
                            });
                        }
            });

    }

    //Save Scripts
    $(".save-script").click(function () {

        var name = $("#script").attr("project");
        var script = python_editor.getDoc().getValue();
        var data = {
            command: true,
            project: name,
            script:script
        };
        // console.log(script);
        editProject(data);

    });

    //Run Scripts
    $(".run-script").click(function () {

        var name = $("#script").attr("project");
        var data = {
            command: true,
            project: name
        };
         console.log(data);
         runProject(data);
    });

    //Run Scripts


    //Run Processor


});



