/**
 * Created by mingming on 17-3-19.
 */
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

    query_tasks(1);

    function query_tasks(page){
        $.ajax({
                url: "/dashboard/api/task",
                method: 'GET',
                dataType: 'json',
                data: {
                    project: project, // Defined in result page script.
                    page: page,
                    rows: 10
                },
                success: function(resp) {
                    show_loading_bar({
                        delay: .5,
                        pct: 100,
                        finish: function () {
                            // Redirect after successful login page (when progress bar reaches 100%)
                            if (resp.status == true) {
                                toastr.success(resp.message, "Message:", opts);
                                var result = resp.result;
                                var task = result.task;
                                console.log(result);
                                console.log(task);

                                var rowCount = task.length;
                                var thead = $("#result-thead");
                                var tbody = $("#result-tbody");

                                // thead.html("<tr></tr>");
                                tbody.html("<tr></tr>");
                                for (var i = 0; i < rowCount; i++){
                                    var th = $("<tr></tr>");
                                    var tr = $("<tr></tr>");
                                    var _task = task[i];
                                    var td = $(

                                        '<td>'+
                                            '<a class="text-info" href="/dashboard/task/'+ project +'/'+
                                            _task.task_id + '"' + 'target="_blank">' + _task.task_id + '</a>'+
                                        '</td>'+
                                        '<td>'+
                                            '<a class="text-secondary" href="'+ _task.url +'"' +
                                            'target="_blank">' + _task.url + '</a>'+
                                        '</td>'+
                                        '<td>'+ _task.status +'</td>'+'<td>'+_task.callback+'</td>'+
                                        '<td>'+ _task.retry_times +'</td>'+
                                        '<td>'+ _task.spend_time +'</td>'+'<td>'+_task.update_datetime+'</td>'
                                    );
                                    td.appendTo(tr);
                                    tr.appendTo(tbody);
                                }
                            }
                            else{
                                toastr.error("Update Data Failed", "Message:", opts);
                            }

                            laypage({
                                  cont: $("#example-5"),
                                  pages: result.total_page,
                                  skip: true,
                                  curr: result.page || 1,
                                  jump: function(obj, first){
                                    if(!first){
                                      query_tasks(obj.curr);
                                    }
                                  }
                                });

                            var curr_count = result.page * 10 - 10;
                            var next_count = result.page * 10;
                            if (next_count > result.total){
                                var next_count = result.total;
                            }
                            var page_info = "Show" + " " + curr_count  + " " + "to"  + " " +
                                            next_count  + " " + "of"  + " " + result.total +" entries." ;
                            $("#example-4_info").html(page_info);
                        }
                    });
                }
        });
    };

    $(".json-btn").click(function () {
        var project = $(this).attr('name');
        window.location.href = "/dashboard/api/task?project="+project+"&page=1&rows=10";
    })

});


