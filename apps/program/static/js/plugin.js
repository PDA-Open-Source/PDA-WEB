var file = {};
var action;
$(document).ready(function () {

  var ShowForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $('#modal-book').modal('show');
      },
      success: function (data) {
        $('#modal-book .modal-content').html(data.html_form);
      }
    });
  };

  function loadUpdateForm(topic_id) {
    var data_url = "/program/" + topic_id + "/topicupdate/";
    var btn = $(this);
    $.ajax({
      url: data_url,
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-book").modal("show");
      },
      success: function (data) {
      $('.loader-overlay').remove();
        $("#modal-book .modal-content").html(data.html_form);
      }
    });
  }

  var SaveForm = function () {
    disableScreen();
    var form = $(this);
    $.ajax({
      url: form.attr('data-url'),
      data: form.serialize(),
      type: form.attr('method'),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          window.location.reload();
        }
      }
    });
    return false;
  };

  // create program
  $(".show-program-form").click(ShowForm);

  $("#programCreateForm").on("change", "#fileUploader", function (event) {
    event.preventDefault();
    event.stopImmediatePropagation();

    var programFileList = document.getElementById("fileUploader").files;
    for (var i = 0; i < programFileList.length; i++) {
        var ext = $('#fileUploader').val().split('.').pop().toLowerCase();
        if($.inArray(ext, ['mp4', 'mpeg', 'flv', 'png', 'jpg', 'jpeg', 'pdf', 'mov']) == -1) {
            alert('Invalid File Type! Only Files with format of mp4, mpeg, mov, flv, png, jpg, jpeg, pdf will be uploaded!!');
            }
        else{
            file[Math.random()] = programFileList[i];
            }
    }

    CreateProgramDocument();
    function CreateProgramDocument() {

      // reference for the preview div
      var programFilePreview = $("#program-file-name");
      var FileRemovebutton = $("#program-file-removeBtn");

      //clear old preview files/btn's
      programFilePreview.find("p").remove();
      FileRemovebutton.find("p").remove();

      // re-render preview with updated files
      Object.keys(file).forEach(function (key) {
        var p = document.createElement("p");
        p.setAttribute("data-url", key);
        p.innerHTML = file[key]['name'];
        p.setAttribute("style", "font-size:14px; color:grey; height:24px; overflow: hidden;");
        var a = document.createElement("p");
        a.setAttribute("data-url", key);
        a.innerHTML = "Remove Uploaded File";
        a.setAttribute("style", "font-size:14px; color:red; height:24px; cursor:pointer;");
        $('#program-file-name').append(p);
        $('#program-file-removeBtn').append(a);
      });
    };

    $(document).on("click", "#program-file-removeBtn p", function () {
      var fileId = $(this).data("url");
      delete file[fileId];
      $('#program-file-name p').remove();
      $('#program-file-removeBtn p').remove();
      document.getElementById("fileUploader").value = "";
      CreateProgramDocument();
    });
  });

  $(document).on("submit", "#programCreateForm", function (event) {
    disableScreen();
    event.preventDefault();
    event.stopImmediatePropagation();
    $(this).children('#program-footer').children('#program-create-btn-container').children('#program-create-btn').attr('disabled', true);
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

  //update program
  $(".show-form").click(ShowForm);
  $('#modal-book').on("submit", ".update-form", SaveForm);

  //create topic
  $(".show-topic-form").click(ShowForm);
  $(document).on("submit", ".create-topic-form", function (event) {
        disableScreen();
        var SaveBtn = document.getElementById("submitBtn");
        SaveBtn.setAttribute("disabled", true);
        var form = $(this);
        $.ajax({
          url: form.attr("data-url"),
          data: form.serialize(),
          type: form.attr("method"),
          dataType: 'json',
          success: function (data) {
            if (data.form_is_valid) {
              loadUpdateForm(data.topic_id);
            }
          }
        });
        return false;
  });

  //update topic
  $("#topicUpdateForm").on("change", "#handleFiles", function (event) {
    event.preventDefault();
    event.stopImmediatePropagation();

    var contentFileList = document.getElementById("handleFiles").files;
    for (var i = 0; i < contentFileList.length; i++) {
    var ext = $('#handleFiles').val().split('.').pop().toLowerCase();
        if($.inArray(ext, ['mp4', 'mpeg', 'flv', 'png', 'jpg', 'jpeg', 'pdf', 'mov']) == -1) {
            alert('Invalid File Type! Only Files with format of mp4, mpeg, mov, flv, png, jpg, jpeg, pdf will be uploaded!!');
            }
        else{
            file[Math.random()] = contentFileList[i];
            }
    }

    CreateList();
    function CreateList() {

      // reference for the preview div
      var contentFilePreview = $("#file-preview");
      var FileRemovebutton = $("#removeFile");
      contentFilePreview.find("p").remove();
      FileRemovebutton.find("p").remove();
      Object.keys(file).forEach(function (key) {
        var p = document.createElement("p");
        p.setAttribute("data-url", key);
        p.innerHTML = file[key]['name'];
        p.setAttribute("style", "font-size:14px; color:grey; height:24px; overflow: hidden;");
        var a = document.createElement("p");
        a.setAttribute("data-url", key);
        a.innerHTML = "Remove Uploaded File";
        a.setAttribute("style", "font-size:14px; color:red; height:24px; cursor:pointer;");
        $('#file-preview').append(p);
        $('#removeFile').append(a);
      });
    };

    $(document).on("click", "#removeFile p", function () {
      var fileId = $(this).data("url");
      delete file[fileId];
      $('#file-preview p').remove();
      $('#removeFile p').remove();
      document.getElementById("handleFiles").value = "";
      CreateList();
    });
  });

  $(document).on("submit", "#topicUpdateForm", function (event) {
    disableScreen();
    event.preventDefault();
    event.stopImmediatePropagation();
    $(this).children('#topic-footer').children('#topic-save').attr('disabled', true);
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

  // add-member
  //var action = null;
  var loadForm = function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var btn = $(this);
    action = btn.attr("data-action");
    $.ajax({
      url: '/program/add-admin/',
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $('#modal-popup').modal('show');
      },
      success: function (data) {
        $('#modal-popup .modal-content').html(data.html_form);
      }
    });
  };

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
        loadAddMember(decrypt(data.qr_value));
      }
    });
    return false;
  };

 //loadAddMember made global

  var saveAddMemberForm = function (e) {
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
          $("#modal-popup").modal("hide");  // <-- Close the modal
          window.location.reload();
        }
        else {
          $('.loader-overlay').remove();
          alert("Member already Added!!");
          $("#modal-popup").modal("hide");
          $("#modal-popup .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };

  $(".add-admin").click(loadForm);
  $("#modal-popup").on("click", ".js-scan-qr", loadScanner);
  $("#modal-popup").on("submit", ".show-qr-scan-popup", getQRForm);
  $("#modal-popup").on("submit", ".js-add-entity", saveAddMemberForm);

      //update content

$(document).on("change", "#Filehandle", function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();

      var topicFileList = $(this).prop("files");
      for (var i = 0; i < topicFileList.length; i++) {
      var ext = $(this).val().split('.').pop().toLowerCase();
        if($.inArray(ext, ['mp4', 'mpeg', 'flv', 'png', 'jpg', 'jpeg', 'pdf', 'mov']) == -1) {
            alert('Invalid File Type! Only Files with format of mp4, mpeg, mov, flv, png, jpg, jpeg, pdf will be uploaded!!');
            }
        else{
            file[Math.random()] = topicFileList[i];
            }
      }
      $(".topic-save").attr("style", "display: block;");
      CreateContent();
      function CreateContent() {
        var contentFile = $("#filepreview div");
        contentFile.find("p").remove();
        var contentFileRemoveButton = $("#remove-File div");
        contentFileRemoveButton.find("p").remove();
        Object.keys(file).forEach(function (key) {
          var p = document.createElement("p");
          p.setAttribute("data-url", key);
          p.innerHTML = file[key]['name'];
          p.setAttribute("style", "font-size:14px; color:grey; height:24px; overflow: hidden;");
          var a = document.createElement("p");
          a.setAttribute("data-url", key);
          a.innerHTML = "Remove Uploaded File";
          a.setAttribute("style", "font-size:14px; color:red; height:24px; cursor:pointer;");
          $('#filepreview div').append(p);
          $('#remove-File div').append(a);
        });
      };

      $(document).on("click", "#remove-File div p", function () {

        event.preventDefault();
        event.stopImmediatePropagation();
        var fileId = $(this).data("url");
        delete file[fileId];
        $('#filepreview div p').remove();
        $('#remove-File div p').remove();
        document.getElementById("Filehandle").value = "";
        CreateContent();
        if (Object.keys(file).length === 0) {
            $(".topic-save").attr("style", "display: none;");
        }
      });

    });

    $(document).on("submit", "#content-UpdateForm", function (event) {
      disableScreen();
      event.preventDefault();
      event.stopImmediatePropagation();
      $(this).children('#topic-save').attr('disabled', true);
      var formData = new FormData($(this)[0]);
      var files = Object.values(file);
      for (var fileIndex = 0; fileIndex < files.length; fileIndex++) {
          formData.append("inline[]", files[fileIndex]);
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
          window.location.reload();
        })
        .fail(function () {
        });
      return false;
    });

});

function loadAddMember(qr_value) {
    var data_url = "/program/add-admin-info/" + qr_value;
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
            $("#programRole").val(action);
            programId = $("#programDetailId").val();
            $("#programId").val(programId);
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(textStatus);
            console.log(jqXHR);
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

