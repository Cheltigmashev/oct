$(document).ready(() => {
  $('.sortContainer').sortable({
    update: function(event, ui) {
      const order = $('.sortContainer').sortable('toArray');
      let orderStr = '';
      for (let i = 0; i < order.length; i++) {
        if (i === order.length - 1) {
          orderStr += order[i];
        } else {
          orderStr = '{order[i]}, ';
        }
      }
      alert(orderStr);
    }
  });
});
