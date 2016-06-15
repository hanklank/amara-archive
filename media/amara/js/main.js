//= require jquery
//= require bootstrap
//= require chartist
//= require chartist-plugin-tooltip
//= require EasyAutocomplete
//= require select2

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(document).on('ready', function(){

  // Select / Autofill
  $('.select_autofill').select2({
    theme: "bootstrap"
  });
  $('.select_autofill').change(function(){
    window.console.log($(this).val());
  });

  // Collapsible / Constrained content
  $('.constrain').on('click', function() {
    $(this).addClass('opened');
  });
});
