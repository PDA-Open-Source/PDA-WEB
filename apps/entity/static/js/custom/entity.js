var file = {};

$(function () {
  var loadForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-popup").modal("show");
        localStorage.removeItem('pdaEntityName');
      },
      success: function (data) {
        $("#modal-popup .modal-content").html(data.html_form);
      }
    });
  };

  var saveAddMemberForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#modal-popup").modal("hide");  // <-- Close the modal
          window.location.reload();
        }
        else {
          $("#modal-popup .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  var loadAdminForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-popup-admin").modal("show");
        localStorage.removeItem('pdaEntityName');
      },
      success: function (data) {
        $("#modal-popup-admin .modal-content").html(data.html_form);
      }
    });
  };

  var loadAdminScanner = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var btn = $(this);
    $.ajax({
      url: '/core/scanner/',
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-popup-admin").modal("show");
      },
      success: function (data) {
        $("#modal-popup-admin .modal-content").html(data.html_form);
      }
    });
  };

  var getAdminQRForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        loadAddEntityMember(decrypt(data.qr_value));
      }
    });
    return false;
  };

  function loadAddEntityMember(qr_value) {
    var data_url = "/entities/add-entity-admin-info/" + qr_value;
    var btn = $(this);
    $.ajax({
      url: data_url,
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-popup-admin").modal("show");
      },
      success: function (data) {
        $("#modal-popup-admin .modal-content").html(data.html_form);
        entityId = $("#entityDetailId").val();
        $("#entityId").val(entityId);
      },
      error: function(jqXHR, textStatus, errorThrown){
        if (jqXHR.status === 404 && jqXHR.statusText === "Not Found"){
            $("#modal-popup-admin").modal("hide");
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

  var saveAdminMemberForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    disableScreen();
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#modal-popup-admin").modal("hide");  // <-- Close the modal
          window.location.reload();
        }
        else {
            $('.loader-overlay').remove();
          alert("Member already added as Admin!!");
          $("#modal-popup-admin").modal("hide");
          $("#modal-popup-admin .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  $(".js-add-entity-show").click(loadForm);
  //$("#modal-popup").on("click", ".js-choose-scan-type", loadChooseScanType);
  $(document).on("submit", ".js-add-entity", function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        disableScreen();
        var SaveBtn = document.getElementById("inviteEntityBtn");
        SaveBtn.setAttribute("disabled", true);
        var form = $(this);
        $.ajax({
          url: form.attr("action"),
          data: form.serialize(),
          type: form.attr("method"),
          dataType: 'json',
          success: function (data) {
            if (data.form_is_valid) {
              $("#modal-popup-admin").modal("hide");  // <-- Close the modal
              window.location.reload();
            }
            else {
                $('.loader-overlay').remove();
              alert("Member already added as Admin!!");
               $("#modal-popup-admin").modal("hide");
              $("#modal-popup-admin .modal-content").html(data.html_form);
            }
          }
        });
        return false;
  });

    // Add Admin to Entity
  $(".add-entity-admin").click(loadAdminForm);
  $("#modal-popup-admin").on("click", ".js-scan-admin-qr", loadAdminScanner);
  $("#modal-popup-admin").on("submit", ".entity-admin-qr-scan", getAdminQRForm);
  $("#modal-popup-admin").on("submit", ".js-add-entity-admin", saveAdminMemberForm);

  var showForm = function (event) {

    event.preventDefault();
    event.stopImmediatePropagation();
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#registration-modal-popup").modal("show");
      },
      success: function (data) {
        $("#registration-modal-popup .modal-content").html(data.html_form);
      }
    });
  };

  $(".register-entity-show").click(showForm);

  $("#register-entity-form").on("change", "#fileHandler", function (event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    var fileList = document.getElementById("fileHandler").files;
    for (var i = 0; i < fileList.length; i++) {
       var ext = $('#fileHandler').val().split('.').pop().toLowerCase();
        if($.inArray(ext, ['mp4', 'mpeg', 'flv', 'png', 'jpg', 'jpeg', 'pdf', 'mov']) == -1) {
            alert('Invalid File Type! Only Files with format of mp4, mpeg, mov, flv, png, jpg, jpeg, pdf will be uploaded!!');
            }
        else {
            file[Math.random()] = fileList[i];
        }
    }
    CreateList();
    function CreateList() {
      var entityFile = $("#file-preview");
      entityFile.find("p").remove();
      var entityFileRemoveButton = $("#removeFile");
      entityFileRemoveButton.find("p").remove();
      Object.keys(file).forEach(function (key) {
        var p = document.createElement("p");
        p.setAttribute("data-url", key);
        p.innerHTML = file[key]['name'];
        p.setAttribute("style", "font-size:14px; color:grey; height:24px; overflow: hidden;");
        var a = document.createElement("p");
        a.setAttribute("data-url", key);
        a.innerHTML = "Remove File";
        a.setAttribute("style", "font-size:14px; color:red; height:24px; cursor:pointer;");
        $('#file-preview div').append(p);
        $('#removeFile div').append(a);
      });
    };

    $(document).on("click", "#removeFile div p", function () {
      var fileId = $(this).data("url");
      delete file[fileId];
      $('#file-preview div p').remove();
      $('#removeFile div p').remove();
      document.getElementById("fileHandler").value = "";
      CreateList();
    });
  });

  $(document).on("submit", "#register-entity-form", function (event) {
    disableScreen();
    event.preventDefault();
    event.stopImmediatePropagation();
    var SaveBtn = document.getElementById("registerBtn");
    var UploadBtn = document.getElementById("fileHandler");
    SaveBtn.setAttribute("disabled", true);
    UploadBtn.setAttribute("disabled", true);
    var formData = new FormData($(this)[0]);
    var files = Object.values(file);
    for (var i = 0; i < files.length; i++) {
      formData.append("inline[]", files[i]);
    }
    var formUrl = $(this).data('url');
    $.ajax(formUrl, {
      data: formData,
      method: "POST",
      dataType: false,
      contentType: false,
      processData: false,
    })
      .done(function () {
        file.length = 0;
        window.location.reload()
      })
      .fail(function () {
      });
    return false;
  });

  $(".edit-entity").click(loadForm);

  $(document).on("submit", "#edit-entity-form", function (event) {
    disableScreen();
    event.preventDefault();
    event.stopImmediatePropagation();
    var form = $(this);
    $.ajax({
      url: form.attr('data-url'),
      data: form.serialize(),
      type: form.attr('method'),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          window.location.reload()
        }
      }
    });
    return false;
  });

});
