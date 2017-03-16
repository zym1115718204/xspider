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
        indentUnit: 2,
        styleActiveLine: true
        });

    var python_editor = CodeMirror.fromTextArea($(".python")[0], { //script_once_code为你的textarea的ID号
        lineNumbers: true,//是否显示行号
        mode: "python",　//默认脚本编码
        lineWrapping: true //是否强制换行
        });

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
            url: "/dashboard/api/run_generator",
            method: 'POST',
            dataType: 'json',
            data: data,
            success: function(resp) {
                show_loading_bar({
                    delay: .5,
                    pct: 100,
                    finish: function () {
                        // Redirect after successful login page (when progress bar reaches 100%)

                        // console.log(resp.result == undefined);
                        if (resp.status === true && resp.result == undefined) {
                            toastr.success(resp.message, "Message:", opts);
                            status_editor.setValue(JSON.stringify(resp.task));
                            var result = resp.task;

                            console.log(result);
                            var rowCount = result.result.length;
                            console.log(rowCount);
                            var tbody = $("#url-table");
                            tbody.html("<tr></tr>");
                            for (var i = 0; i < rowCount; i++){
                                var task = result.result[i];
                                var tr = $("<tr></tr>");
                                var td = $("<td class=\"col-md-3 no-padding-textarea text-secondary\">" + task.result.callback+
                                           "</td><td class=\"col-md-8 no-padding-textarea\">" + task.result.url +
                                           "</td><td class=\"col-md-1 no-padding-textarea\"><button class=\"btn btn-success btn-single btn-xs run-task\" task='"+
                                           JSON.stringify(task.result)+"'>run</button></td>");
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
                                console.log(task);
                                console.log(data);
                                runProject(data);
                            });
                            // <tr><td class="col-md-3 no-padding-textarea text-secondary">parser_index</td><td class="col-md-8 no-padding-textarea">http:www.baidu.com</td> <td class="col-md-1 no-padding-textarea"><a class="btn btn-success btn-single btn-xs">run</a></td></tr>
                            $("#task-table").removeClass("hidden");

                            //setTimeout(function(){ window.location.href = '/dashboard/debug/'+name;}, 600);
                        }
                        else if(resp.status === true){

                            toastr.success(resp.message, "Message:", opts);
                            status_editor.setValue(JSON.stringify(resp.result));
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

    /*
    function showAjaxModal()
			{
				jQuery('#modal-7').modal('show', {backdrop: 'static'});

//				jQuery.ajax({
//					url: "data/ajax-content.txt",
//					success: function(response)
//					{
//						jQuery('#modal-7 .modal-body').html(response);
//					}
//				});
			}*/

    /* debug page */

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



