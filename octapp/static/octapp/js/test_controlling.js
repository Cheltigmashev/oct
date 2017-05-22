$(document).ready(() => {
  passingArea = $('div.passing_area');
  passingArea.mouseleave(() => {
      alert('Выход курсора мыши из области прохождения (списка вопросов) заблокировано контролем прохождения, прохождение теста будет принудительно завершено.');
      document.getElementById('answers_form').submit();
  });
  $('body').contextmenu(() => {
      alert('Нажатие правой клавиши мыши заблокировано контролем прохождения, прохождение теста будет принудительно завершено.');
      document.getElementById('answers_form').submit();
  });
  $('body').keydown((e) => {
      if (e.keyCode === 17 || e.keyCode === 91 || e.keyCode === 9) {
          alert('Нажатие клавиш ctrl, windows, tab заблокировано контролем прохождения, прохождение теста будет принудительно завершено.');
          document.getElementById('answers_form').submit();
        }
  });
});
