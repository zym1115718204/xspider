/**
 * Created by mingming on 17-3-8.
 */


jQuery(document).ready(function($)
{
    // Skins

    // Styles
    $('input.icheck-11').iCheck({
        checkboxClass: 'icheckbox_square-blue',
        radioClass: 'iradio_square-pink'
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

});



jQuery(document).ready(function($)
{
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

    // Edit Project Parameters
    $('a.edit-project').click(function () {
         show_loading_bar({
                    delay: 1.5,
                    pct: 1000
         });
        // $.ajax({
        //     url: "{% url 'clawer.apis.command.update_job' %}",
        //     method: 'POST',
        //     dataType: 'json',
        //     data: {
        //         //do_update: true,
        //         //job_id: $(this).attr('job_id')
        //     },
        //     success: function(resp) {
        //         show_loading_bar({
        //             delay: .5,
        //             pct: 100,
        //             finish: function () {
        //
        //                 // Redirect after successful login page (when progress bar reaches 100%)
        //                 if (resp.accessGranted == true) {
        //                     toastr.success(resp.reason, "Status:", opts);
        //                     setTimeout(function(){ window.location.reload();},1000);
        //                 }
        //                 else {
        //                     toastr.error(resp.reason, "Status:", opts);
        //                 }
        //             }
        //         });
        //     }
        // });
    });

});
