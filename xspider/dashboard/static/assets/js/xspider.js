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

    // Create Project
    function createProject(data) {
        $.ajax({
                url: "/dashboard/api/create",
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
                                setTimeout(function(){ window.location.href = '/dashboard/debug/'+data.project;}, 600);
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

    /* Index page */

    // Edit Page
    $('.edit-btn').click(function () {

        var tds = $(this).closest("tr").find("td");
        var group = tds.eq(0).text();
        var name = tds.eq(1).text().trim();
        var status = tds.eq(2).find('span').attr("value");
        var interval = tds.eq(3).text();
        var number = tds.eq(4).text();
        var ip_limit = tds.eq(5).text();
        var limit = tds.eq(6).text();

        $("#field-1").attr("placeholder", group).val('');
        $("#field-2").attr("placeholder", name).val('');
        $("#field-3").attr("placeholder", null).val('');
        $("#field-4").attr("placeholder", interval).val('');
        $("#field-5").attr("placeholder", number).val('');
        $("#field-6").attr("placeholder", ip_limit).val('');
        $("#field-7").attr("placeholder", limit).val('');
        $("#field-8").attr("value", status);
        $("#field-8").find("input").eq(status).prop("checked",true);

        // Styles
        $('input.icheck-11').iCheck({
            checkboxClass: 'icheckbox_square-blue',
            radioClass: 'iradio_square-pink'
        });

        // Edit Page Show
        $("#edit-page").modal('show', {backdrop: 'static'});
    });

    // Edit Submit
    $('.edit-save').click(function () {

        var flag = null;
        var inputs = $("#edit-page").find("input");
        var group = inputs.eq(0).val();
        var name = inputs.eq(1).attr('placeholder');
        var interval = inputs.eq(2).val();
        var number = inputs.eq(3).val();
        var ip_limit = inputs.eq(4).val();
        var limit = inputs.eq(5).val();
        var status = $("#field-7").attr("value");
        var data = {
            command: true,
            project: name
        };
        $("#field-8 input").each(function(){

            if($(this).prop('checked')){
                var _status = $(this).attr("value");
                if(_status===status){
                    console.log(_status);
                }
                else{
                    data["status"]=_status;
                    flag = true;
                }
            }
            else{
            }
          });

        if(group){
            data['group']=group;
            flag = true
        }

        if(interval){
            data['interval']=interval;
            flag = true
        }

        if(number){
            data['number']=number;
            flag = true
        }

        if(ip_limit){
            data['ip_limit']=ip_limit;
            flag = true
        }

        if(limit){
            data['limit']=limit;
            flag = true
        }

        // Save Edit
        if(flag){
            editProject(data);
        }
        else{
            toastr.warning("No parameters changed.", "Message:", opts);
        }
    });


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

    // Create Page
    $('.create-btn').click(function () {
        // Edit Page Show
        $("#create-page").modal('show', {backdrop: 'static'});
    });

    // Create Save
    $('.create-save').click(function () {

        var inputs = $("#create-page").find("input");
        var name = inputs.eq(0).val().toLowerCase();
        var url = inputs.eq(1).val();

        if(url == ""){
            url = "__START_URL__"
        }
        var data = {
            command: true,
            project: name,
            url: url
        };
        console.log(data);

        if(/^[a-zA-Z]+$/.test(name)){
            createProject(data);
        }
        else{
            toastr.warning("Project name is invalid. Must be a-Z", "Message:", opts);
        }
    });

    //Auto-Refresh Interval
    setInterval(function(){ window.location.reload();},60000);

});


