let intervalID;
function changeTime() {
  if (parseInt($('#timer_span').text(), 10) <= 0) {
    $('#fail_reason').attr('value', 'превышено время прохождения');
    clearInterval(intervalID);
    document.getElementById('answers_form').submit();
    alert('Время вышло! Вы не успели пройти тест за отведенное время...');
  } else {
    $('#timer_input').attr('value', parseInt($('#timer_input').attr('value'), 10) - 1);
    $('#timer_span').text(parseInt($('#timer_span').text(), 10) - 1);
  }
}
$(document).ready(() => {
  intervalID = setInterval(changeTime, 60000);
});

