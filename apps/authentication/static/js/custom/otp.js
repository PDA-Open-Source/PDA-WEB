$(document).ready(function () {
  'use strict';

  function goToNextInput(e) {
    var key = e.which,
      t = $(e.target),
      sib = t.next('input');

    if (key !== 8) {

      if (key != 9){
        e.preventDefault();
        if ((key < 48 && key > 57) || (key < 96 && key > 105)) {
            return false;
        }
      }

      if (key === 9) {
        return true;
      }

      if (!sib || !sib.length) {
        if (sib.length !== 0) {
          sib = body.find('input').eq(0);
        }
      }
      sib.select().focus();
    } else {
      goToLastInput(e);
    }
  }

  function goToLastInput(e) {
    var key = e.which,
      t = $(e.target),
      sib = t.prev('input');
    if (!sib || sib.length) {
      sib.focus();
    }
  }

  function onKeyDown(e) {
    var key = e.which;

    if (key === 9 || key === 8 || (key >= 48 && key <= 57) || (key >= 96 && key <= 105)) {
      return true;
    }

//    if (key === 9 || key === 8 || (key >= 96 && key <= 105)) {
//      return true;
//    }

    e.preventDefault();
    return false;
  }

  function onFocus(e) {
    $(e.target).select();
  }

  $("#otp-inputs").on('keyup', 'input', goToNextInput);
  $("#otp-inputs").on('keydown', 'input', onKeyDown);
  $("#otp-inputs").on('click', 'input', onFocus);
  $(".user-otp-inputs").on('keyup', 'input', goToNextInput);
  $(".user-otp-inputs").on('keydown', 'input', onKeyDown);
  $(".user-otp-inputs").on('click', 'input', onFocus);

  $('#socionUserName').on('keydown',function(e){
        var key = e.which;
        var keyVal = e.key;
        console.log(key)
        if((key === 188 && keyVal === ',') || (key === 191 && keyVal === '?')){
            return false;
        }
   });
});