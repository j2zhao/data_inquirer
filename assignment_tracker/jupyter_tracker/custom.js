define([
  'base/js/namespace',
  'base/js/events'
], function(Jupyter, events) {
  events.on('kernel_ready.Kernel', function() {
      var cell = Jupyter.notebook.get_cell(0);
      var prev_text = cell.get_text();
      if(prev_text.indexOf('%load_ext jupyter_record\n') === -1 ) {
          var cell = IPython.notebook.insert_cell_above('code');
          var notebook_name = Jupyter.notebook.notebook_name;
          cell.set_text('%load_ext jupyter_record\n%set_filename '+ notebook_name + '\n%autosave 60\n# do not change your notebook name\n# do not touch this cell');   
      }
      Jupyter.notebook.execute_cells([0]);
      document.querySelector('.input').style.display = 'none';
      // Save the notebook every minute
      setInterval(function() {
        Jupyter.notebook.save_notebook();
    }, 60000);  // 60000 milliseconds is equal to 1 minute
  })
});

// function save() {
//   IPython.notebook.save_notebook()
// }

// setInterval(save, 60000);

// document.body.addEventListener('paste', function(e) {
//   e.preventDefault();
//   alert('Copy function is disabled on this website.');
// }, true);

// document.body.addEventListener('cut', function(e) {
//   e.preventDefault();
//   alert('Cut function is disabled on this website.');
// }, true);

// document.body.addEventListener('copy', function(e) {
//   e.preventDefault();
//   alert('Cut function is disabled on this website.');
// }, true);

document.querySelector('.input').style.display = 'none';

// document.addEventListener('keydown', function(e) {
//     if ((e.metaKey || e.ctrlKey) && e.key === 'v') { // 'v' is the key for paste
//       e.preventDefault();
//       alert('Paste function is disabled on this website.');
//     }
//   });

// document.addEventListener('contextmenu', function(e) {
//     e.preventDefault();
//   }, false);
