$(function () {
    var notificationsList = [];
    var pageSize = 10;
    var totalNotificationLoaded = 0;
    var token = localStorage.getItem("pda_accessToken");
    if ($('#unReadNotificationCount').length === 1){
        unReadNotificationFunction();
    }
    function unReadNotificationFunction(){
        var unReadNotificationUrl = baseURLFunction() + 'session/notifications/unReadCount';
        $.ajax(unReadNotificationUrl, {
            method: "GET",
            headers: {
                "access-token":token,
            }
        })
        .done(function (data, textStatus, jqXHR) {
            if (data.responseCode === 200) {
                var unReadNotification = data.response;
                if(unReadNotification === 0){
                    $('.number').hide();
                }
                else {
                    if (unReadNotification > 99){
                        $('#unReadNotificationCount').text("99+");
                    }else{
                        $('#unReadNotificationCount').text(unReadNotification);
                    }
                    $('.number').show();
                }
            }
            else {
                $(".notification-toaster").css("display", "block");
                $('.toast #notification-error-message').text("Something went wrong...!!!");
                $('.toast').toast('show');
                $('.toast').on('hidden.bs.toast', function(){
                    $(this).removeClass("login-error");
                    $(".notification-toaster").css("display", "none");
                });
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            var statusCode = jqXHR.status;
            if (statusCode === 422) {
                var errors = jqXHR.responseJSON.errors;
                console.log(errors);
            } else {
                $(".notification-toaster").css("display", "block");
                $('.toast #notification-error-message').text("Something went wrong...!!!");
                $('.toast').toast('show');
                $('.toast').on('hidden.bs.toast', function(){
                    $(this).removeClass("login-error");
                    $(".notification-toaster").css("display", "none");
                });
            }
        });
    }

  function notificationFunction(pageNumber) {
    var notificationUrl = baseURLFunction() + 'session/notifications?pageNumber='+ pageNumber +'&pageSize='+ pageSize;
    $.ajax(notificationUrl, {
        method: "GET",
        headers: {
            "access-token":token,
            "offset":-330
        }
    })
    .done(function (data, textStatus, jqXHR) {
        if (data.responseCode === 200) {
            var notifications = data.response;
            if(notifications["total"] === 0){
                $('#loaderNotification').text("No Notification...");
            }
            notificationsList.push(...notifications["notifications"])
            $('#paginationPageNumber').val(pageNumber);
            totalNotificationLoaded = totalNotificationLoaded + notifications["notifications"].length;
            if(totalNotificationLoaded < notifications["total"]){
                $('#loadMore').show();
            }
            else if (totalNotificationLoaded === notifications["total"] || notifications["total"] === 0) {
                $('#loadMore').hide();
            }

            $('#notification-input').val(JSON.stringify(notificationsList));
            document.getElementById('notificationSubmit').click();
        }
        else {
            $(".notification-toaster").css("display", "block");
            $('.toast #notification-error-message').text("Something went wrong...!!!");
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
        var statusCode = jqXHR.status;
        if (statusCode === 422) {
            var errors = jqXHR.responseJSON.errors;
            console.log(errors);
        } else {
            $(".notification-toaster").css("display", "block");
            $('.toast #notification-error-message').text("Something went wrong...!!!");
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
    });
  }

  function notificationUpdateAsRead(notificationId, notificationItem) {
    var notificationUpdateUrl = baseURLFunction() + 'session/notifications/status';
    var notificationData = {isDeleted:false,isRead:true,notificationId:parseInt(notificationId)};
    var jsonData = JSON.stringify(notificationData);
    $.ajax(notificationUpdateUrl, {
        method: "PUT",
        contentType: "application/json",
        data: jsonData,
        headers: {
            "access-token":token,
            "offset":-330
        }
    })
    .done(function (data, textStatus, jqXHR) {
        if (data.responseCode === 200) {
            unReadNotificationFunction();
            notificationItem.removeClass('notification-div');
            notificationItem.addClass('notification-div-read');
        }
        else {
            $(".notification-toaster").css("display", "block");
            $('.toast #notification-error-message').text("Something went wrong...!!!");
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
        var statusCode = jqXHR.status;
        if (statusCode === 422) {
            var errors = jqXHR.responseJSON.errors;
            console.log(errors);
        } else {
            $(".notification-toaster").css("display", "block");
            $('.toast #notification-error-message').text("Something went wrong...!!!");
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
    });
  }

  function notificationDelete(notificationId, notificationItem) {
   disableScreen();
    var notificationDeleteUrl = baseURLFunction() + 'session/notifications/status';
    var notificationData = {isDeleted:true,isRead:true,notificationId:parseInt(notificationId)};
    var jsonData = JSON.stringify(notificationData);
    $.ajax(notificationDeleteUrl, {
        method: "PUT",
        contentType: "application/json",
        data: jsonData,
        headers: {
            "access-token":token,
            "offset":-330
        }
    })
    .done(function (data, textStatus, jqXHR) {

        if (data.responseCode === 200) {
            notificationsList = [];
            totalNotificationLoaded = 0;
            unReadNotificationFunction();
//            notificationItem.remove();
//            if($('#modal-popup-notification .modal-dialog .modal-content .modal-body ul li').length === 0){
//                $('#loaderNotification').text("No Notification...");
//                $('#loaderNotification').show();
//            }
            loadForm();
            setTimeout(function(){ $('.loader-overlay').remove(); }, 500);
        }
        else {
             $('.loader-overlay').remove();
            $(".notification-toaster").css("display", "block");
            $('.toast #notification-error-message').text("Something went wrong...!!!");
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
        $('.loader-overlay').remove();
        var statusCode = jqXHR.status;
        if (statusCode === 422) {
            var errors = jqXHR.responseJSON.errors;
            console.log(errors);
        } else {
            $(".notification-toaster").css("display", "block");
            $('.toast #notification-error-message').text("Something went wrong...!!!");
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
    });
  }

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        var pageNumber = 1;
        notificationFunction(pageNumber, pageSize);
        $("#modal-popup-notification").modal("show");
      },
      success: function (data) {
        $("#modal-popup-notification .modal-content").html(data.html_form);
      }
    });
  };

  var saveAddMemberForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
          $("#modal-popup-notification .modal-content .modal-body ul").html(data.html_notification_list);
          if(JSON.parse($('#notification-input').val()).length === 0){
            $('#loaderNotification').text("No Notification...");
          }
      }
    });
    return false;
  };

  $(".js-notification-show").click(loadForm);
  $("#modal-popup-notification").on("submit", ".js-notification-popup-content", saveAddMemberForm);

  $(document).on("click","#loadMore",function(){
    pageNumber = parseInt($('#paginationPageNumber').val());
    notificationFunction(pageNumber+1);
  });

  $(document).on("click",".list-notification-item-js",function(){
    notificationUpdateAsRead($(this).closest('li').children('#notification').val(), $(this).closest('li'));
  });

  $(document).on("click",".delete-dustbin",function(){
    //console.log($(this).parent('.col-md-1').parent('.notification-col').parent('.row').parent('.list-notification-item-delete-js').children('#notification').val());
    notificationDelete($(this).closest('li').children('#notification').val(), $(this).closest('li'));
  });

  $('#modal-popup-notification').on('hidden.bs.modal', function(){
     notificationsList = [];
     totalNotificationLoaded = 0;
  });

});
