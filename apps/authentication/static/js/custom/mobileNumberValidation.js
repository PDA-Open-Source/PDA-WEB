var phoneNumberMaxLength = 10;
var phoneNumberMinLength = 10;

$(document).ready(function () {
  var filter = /^\d*(?:\.\d{1,2})?$/;
  var phoneNumberLength = 10;

  var mobileNumberLength = $("#socionUserCountryCode").on("blur", function(){
      selectedCountryCode = $(this).val();
      var mobNum = $("#socionPhoneNumber").val();
      countryCodes = JSON.parse(localStorage.getItem("socion_countryCodes"));
      countryCodes.forEach(function (item){
           if(item.code == selectedCountryCode){
                phoneNumberLength = item.phoneNumberLength;
                phoneNumberMaxLength = item.phoneNumberSizeMax;
                phoneNumberMinLength = item.phoneNumberSizeMin;
           }
      });
//bypassing min max length validation
//       mobileNumberLengthValidation(filter, mobNum);
  });

//bypassing min max length validation
//   $("#socionPhoneNumber").on("blur", function () {
//     var mobNum = $(this).val();
//     selectedCountryCode = $("#socionUserCountryCode").val();
//     countryCodes = JSON.parse(localStorage.getItem("socion_countryCodes"));
//     countryCodes.forEach(function (item){
//          if(item.code == selectedCountryCode){
//                phoneNumberMaxLength = item.phoneNumberSizeMax;
//                phoneNumberMinLength = item.phoneNumberSizeMin;
//          }
//     });
//     mobileNumberLengthValidation(filter, mobNum);
//   });

  /*$("#socionPassword").on("blur", function () {
    var password = $(this).val();
      if (password.length > 0) {
        $("#passwordErrorMessage").addClass("hidden");
      } else {
        $("#passwordErrorMessage").text("Please enter your password");
        $("#passwordErrorMessage").removeClass("hidden");
        return false;
      }
  });*/

  $("#socionUserName").on("blur", function () {
    var userName = $(this).val();
      if (userName.length > 0) {
        $("#userNameErrorMessage").addClass("hidden");
      } else {
        $("#userNameErrorMessage").text("Please enter username");
        $("#userNameErrorMessage").removeClass("hidden");
        return false;
      }
  });

  function mobileNumberLengthValidation(filter, mobNum){
    if (filter.test(mobNum)) {
      if (mobNum.length >= phoneNumberMinLength && mobNum.length <= phoneNumberMaxLength) {
        $("#phoneNumberErrorMessage").addClass("hidden");
        $("#mobio-invalid").addClass("hidden");
        $("#socionPhoneNumber").css("border-top-right-radius", "0.25rem");
        $("#socionPhoneNumber").css("border-bottom-right-radius", "0.25rem");
        $("#phoneNumber").removeClass("input-field-error");
        $("#addByPhoneNumber .mobile-placeholder-text").css("height", "48px");
        $("#addByPhoneNumber .mobile-placeholder-text").css("border", "solid 0.5px #f9cfcc");
      }
        return false;
      }
    else {
      $("#phoneNumberErrorMessage").text("Please enter phone number");
      $("#phoneNumberErrorMessage").removeClass("hidden");
      $("#mobio-invalid").removeClass("hidden");
      $("#phoneNumber").addClass("input-field-error");
      $("#socionPhoneNumber").removeAttr("style");
      return false;
    }
  }
});

function checkPhoneNumberLength(mobnum){
    selectedCountryCode = $("#socionUserCountryCode").val();
    countryCodes = JSON.parse(localStorage.getItem("socion_countryCodes"));
    countryCodes.forEach(function (item){
         if(item.code == selectedCountryCode){
               phoneNumberLength = item.phoneNumberLength;
         }
    });
    if(mobnum.length >= phoneNumberMinLength && mobnum.length <= phoneNumberMaxLength){
        return true;
    } else {
        return false;
    }
}

function setInputFilter(textbox, inputFilter) {
  ["input", "keydown", "keyup", "mousedown", "mouseup", "select", "contextmenu", "drop"].forEach(function(event) {
    textbox.addEventListener(event, function() {
      if (inputFilter(this.value)) {
        this.oldValue = this.value;
        this.oldSelectionStart = this.selectionStart;
        this.oldSelectionEnd = this.selectionEnd;
      } else if (this.hasOwnProperty("oldValue")) {
        this.value = this.oldValue;
        this.setSelectionRange(this.oldSelectionStart, this.oldSelectionEnd);
      }
    });
  });
}

// Install input filters.
setInputFilter(document.getElementById("socionPhoneNumber"), function(value) {
  return /^\d*$/.test(value);
});
