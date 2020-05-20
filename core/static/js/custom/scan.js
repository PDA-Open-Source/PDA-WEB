$(function () {
  var loadScanner = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var btn = $(this);
    $.ajax({
      url: '/core/scanner/',
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-popup").modal("show");
      },
      success: function (data) {
        $("#modal-popup .modal-content").html(data.html_form);
      }
    });
  };

   var getQRForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
          loadAddEntity(decrypt(data.qr_value));
      }
    });
    return false;
  };

  function loadAddEntity (qr_value) {
    var data_url = "/entities/add-entity-info/"+qr_value;
    var btn = $(this);
    $.ajax({
      url: data_url,
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-popup").modal("show");
      },
      success: function (data) {
        $("#modal-popup .modal-content").html(data.html_form);
      },
      error: function(jqXHR, textStatus, errorThrown){
        if (jqXHR.status === 404){
            $("#modal-popup").modal("hide");
            $(".notification-toaster").css("display", "block");
            $('.toast').addClass("login-error");
            $('.toast #notification-error-message').text("Invalid QR Code");
            $('.toast .toast-body .close').css('line-height',0);
            $('.toast').toast('show');
            $('.toast').on('hidden.bs.toast', function(){
                $(this).removeClass("login-error");
                $(".notification-toaster").css("display", "none");
            });
        }
      }
    });
  }

  $("#modal-popup").on("click", ".js-scan-qr", loadScanner);
  $("#modal-popup").on("submit", ".show-qr-scan-popup", getQRForm);
});
