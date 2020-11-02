$(document).ready(function () {
    var localStorageCountryCodes = localStorage.getItem("pda_countryCodes");
    if (localStorageCountryCodes === null) {
        var countryCodeUrl = baseURLFunction() + 'user/get-country-codes';
        $.ajax(countryCodeUrl, {
            method: "GET",
        })
        .done(function (data, textStatus, jqXHR) {
            if (data.responseCode === 200) {
                var countryCodes = data.response;
                localStorage.setItem("pda_countryCodes", JSON.stringify(countryCodes));
                countryCodes.forEach(function (item) {
                    var option = document.createElement("option");
                    option.value = item.code;
                    if (item.code.length === 2) {
                        option.text =  item.code + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + "(" + item.country + ")";
                    }
                    else if (item.code.length === 3) {
                        option.text =  item.code + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + "(" + item.country + ")";
                    }
                    else if (item.code.length === 4) {
                        option.text =  item.code + '\xa0' + '\xa0' + '\xa0' + '\xa0' + "(" + item.country + ")";
                    }
                    else if (item.code.length === 5) {
                        option.text =  item.code + '\xa0' + '\xa0' + "(" + item.country + ")";
                    }
                    if (option.value === "+91") {
                        option.selected = 'selected';
                    }
                    document.getElementById('pdaUserCountryCode').appendChild(option);
                });
            }
            else {
                $('.toast #login-error-message').text("Something went wrong...!!!");
                $('.toast').toast('show');
                $('.toast').on('hidden.bs.toast', function(){
                    $(this).removeClass("login-error");
                });
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            var statusCode = jqXHR.status;
            if (statusCode === 422) {
                var errors = jqXHR.responseJSON.errors;
                console.log(errors);
            } else {
                $('.toast #login-error-message').text("Something went wrong...!!!");
                $('.toast').toast('show');
                $('.toast').on('hidden.bs.toast', function(){
                    $(this).removeClass("login-error");
                });
            }
        });
    }
    else {
        var countryCodes = JSON.parse(localStorageCountryCodes);
        countryCodes.forEach(function (item) {
            var option = document.createElement("option");
            option.value = item.code;
            if (item.code.length === 2) {
                option.text =  item.code + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + "(" + item.country + ")";
            }
            else if (item.code.length === 3) {
                option.text =  item.code + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + '\xa0' + "(" + item.country + ")";
            }
            else if (item.code.length === 4) {
                option.text =  item.code + '\xa0' + '\xa0' + '\xa0' + '\xa0' + "(" + item.country + ")";
            }
            else if (item.code.length === 5) {
                option.text =  item.code + '\xa0' + '\xa0' + "(" + item.country + ")";
            }
            if (option.value === "+91") {
                option.selected = 'selected';
            }
            document.getElementById('pdaUserCountryCode').appendChild(option);
        });
    }
});
