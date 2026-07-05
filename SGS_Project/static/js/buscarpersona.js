ItemsDisplayPersonas = function (item) {
    if (item.text && item.documento) {
        return $(`<img src="${item.foto}" width="25px" height="25px" class="w-25px rounded-circle me-2"><span>${item.text}</span>`);
    } else if (item) {
        return item.text;
    } else {
        return ' Consultar Personas';
    }
};

function formatRepo(repo) {
    if (repo.loading) {
        return 'Buscando..';
    }
    return $(`
        <div class="d-flex align-items-center gap-2">
            <img src="${repo.foto}" width="40px" height="40px" class="rounded-circle">
            <div>
                <b>Documento:</b> ${repo.documento}<br>
                <b>Nombres:</b> ${repo.text}
                ${repo.departamento ? `<br><b>Departamento:</b> <span>${repo.departamento}</span>` : ''}
            </div>
        </div>
    `);
}
function buscarPersona(objeto, tipo = '', args = '', modemovil = false) {
    let url = objeto.data('url');

    if (!url) {
        console.error('No se encontró data-url para buscar personas');
        return;
    }

    if (objeto.hasClass('select2-hidden-accessible')) {
        objeto.select2('destroy');
    }

    objeto.select2({
        theme: "bootstrap-5",
        dropdownParent: $("#modalBase"),
        width: '100%',
        placeholder: 'Consultar Personas...',
        allowClear: true,
        minimumInputLength: 1,
        ajax: {
            url: url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term || '',
                    page: params.page || 1,
                    tipo: tipo,
                    idsagregados: args
                };
            },
            processResults: function (data) {
                console.log(data)
                return {
                    results: data.results || [],
                    pagination: {
                        more: data.more || false
                    }
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        templateResult: formatRepo,
        templateSelection: ItemsDisplayPersonas
    });
}