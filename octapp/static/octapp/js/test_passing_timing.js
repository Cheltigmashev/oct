let intervalID;
function changeTime() {
  if (parseInt($('#timer_span').text(), 10) === 0) {
    clearInterval(intervalID);
    document.getElementById('answers_form').submit();
    alert('Отведенное на прохождение время вышло!');
  } else {
    $('#timer_input').attr('value', parseInt($('#timer_input').attr('value'), 10) - 1);
    $('#timer_span').text(parseInt($('#timer_span').text(), 10) - 1);
  }
}
$(document).ready(() => {
  intervalID = setInterval(changeTime, 60000);
});

