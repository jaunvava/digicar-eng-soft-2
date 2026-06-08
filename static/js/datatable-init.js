// Inicializador padrão do DataTable para todas as tabelas do sistema.
// Basta adicionar a classe "datatable" em qualquer <table> para herdar
// paginação, ordenação e busca prontas (em pt-BR).
(function ($) {
  if (!$ || !$.fn || !$.fn.DataTable) return;

  var LANG_PT_BR = {
    decimal: ',',
    thousands: '.',
    emptyTable: 'Nenhum registro encontrado',
    info: 'Mostrando _START_ até _END_ de _TOTAL_ registros',
    infoEmpty: 'Mostrando 0 até 0 de 0 registros',
    infoFiltered: '(filtrado de _MAX_ registros no total)',
    lengthMenu: 'Exibir _MENU_ registros',
    loadingRecords: 'Carregando...',
    processing: 'Processando...',
    search: 'Pesquisar:',
    zeroRecords: 'Nenhum registro encontrado',
    paginate: {
      first: 'Primeiro',
      last: 'Último',
      next: 'Próximo',
      previous: 'Anterior'
    }
  };

  $(function () {
    $('table.datatable').each(function () {
      var $table = $(this);
      if ($.fn.DataTable.isDataTable($table)) return;

      $table.DataTable({
        language: LANG_PT_BR,
        pageLength: parseInt($table.data('page-length'), 10) || 20,
        lengthMenu: [10, 20, 50, 100],
        order: [],
        columnDefs: [
          { targets: 'no-sort', orderable: false }
        ]
      });
    });
  });
})(window.jQuery);
