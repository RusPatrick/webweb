(function() {
  'use strict';
  window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);
})();

// For AJAX calls
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


$('.js-like').on('click', function() {
  var $btn = $(this),
    object_id = $btn.data('id'),
    content_type = $btn.data('content_type'),
    value = $btn.data('value'),
    csrftoken = getCookie('csrftoken');


  // cur_likes_count = parseInt($('#' + content_type + '_likes_count-' + object_id).text())
  // $('#' + content_type + '_likes_count-' + object_id).text(cur_likes_count + parseInt(value))

  $.ajax({
    method: "POST",
    url: "/like",
    data: {
      "object_id": object_id,
      "value": value,
      "content_type": content_type,
      "csrfmiddlewaretoken": csrftoken,
    },
    dataType: 'json'
  })
  .done(function(data) {
    console.log(data);
    if (data.status == 'error') {
      console.log("error statement");
      // $('#' + content_type + '_likes_count-' + object_id).text(cur_likes_count)
    }
    if (data.status == 'ok') {
      console.log("ok statement");
      $btn.addClass('active')
      $btn.attr("data-toggle", "button")
      $btn.attr("aria-pressed", "true")
      $btn.attr("autocomplete", "off")
      $('#' + content_type + '_likes_count-' + object_id).text(data.likes_count)
      if (parseInt($('#' + content_type + '_likes_count-' + object_id).text()) < 0) {
        $('#' + content_type + '_likes_count-' + object_id).removeClass('text-success')
        $('#' + content_type + '_likes_count-' + object_id).addClass('text-danger')
      } else {
        $('#' + content_type + '_likes_count-' + object_id).removeClass('text-danger')
        $('#' + content_type + '_likes_count-' + object_id).addClass('text-success')
      }
    }
  })
  return false;
});

$('.js-correct').on('click', function() {
  var $btn = $(this),
    answer_id = $btn.data('id'),
    csrftoken = getCookie('csrftoken');

  $.ajax({
    method: "POST",
    url: "/blog/correct",
    data: {
      "answer_id": answer_id,
      "csrfmiddlewaretoken": csrftoken,
    },
    dataType: 'json'
  })
  .done(function(data) {
    console.log(data);
    if (data.is_correct == true) {
      $('#Answer_correct-' + answer_id).toggleClass("btn-danger")
      $('#Answer_correct-' + answer_id).toggleClass("btn-success")
      $('#Answer_correct-' + answer_id).text("Mark as incorrect")
    } else if(data.is_correct == false){
      $('#Answer_correct-' + answer_id).toggleClass("btn-success")
      $('#Answer_correct-' + answer_id).toggleClass("btn-danger")
      $('#Answer_correct-' + answer_id).text("Mark as correct")
    }
    if(data.status != 'error') {
      $('#answer_correct_sign-' + answer_id).toggle()
    }
  })
  return false;
});
