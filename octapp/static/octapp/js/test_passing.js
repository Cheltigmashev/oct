$(document).ready(() => {
  $('.sortContainer').each(function(i) {
    $(this).sortable({
      placeholder: 'placeholder_for_sorting',
      forcePlaceholderSize: true,
      update: function(event, ui) {
        const order = $(this).sortable("toArray");
        let orderStr = '';
        for (let i = 0; i < order.length; i++) {
          if (i === order.length - 1) {
            if ($(this).hasClass('sequence_elements_div')) {
              orderStr += order[i];
            } else {
              orderStr += i + 1 + '-' + order[i];
            }
          } else {
            if ($(this).hasClass('sequence_elements_div')) {
              orderStr += order[i] + ', ';
            } else {
              orderStr += i + 1 + '-' + order[i] + ', ';
            }
          }
        }
        $(this).next().attr('value', orderStr);
      }
    });
  });

  $('.closed_question_multiple').each(function(i) {
    $(this).change( function() {
      let selected = '';
      length = $(this).children().children('input:checked').length;
      $(this).children().children('input:checked').each(function(j) {
        if (j === length - 1) {
          selected += ($(this).attr('value'));
        } else {
          selected += ($(this).attr('value') + ', ');
        }
      });
      $(this).next().attr('value', selected);
    });
  });
});
