/**
 * Created by mingming on 17-3-20.
 */
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

    $(".json-btn").click(function () {
        var project = $(this).attr('name');
        window.location.href = "/dashboard/api/result?project="+project+"&page=1&rows=10";
    })

});


