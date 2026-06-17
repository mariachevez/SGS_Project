function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(function (cookie) {
            cookie = cookie.trim();

            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }

    return cookieValue;
}

function formModal(url, titulo, modal_size = '') {
    $.get(url)
        .done(function (html) {
            const dialog = $('#modalBase .modal-dialog');

            dialog.removeClass('modal-sm modal-md modal-lg modal-xl modal-fullscreen');

            if (modal_size) {
                dialog.addClass(modal_size);
            }
            $('#modalBaseTitle').text(titulo);
            $('#modalBaseBody').html(html);

            const modal = new bootstrap.Modal(document.getElementById('modalBase'));
            modal.show();
        })
        .fail(function (xhr, status, error) {
            const data = xhr.responseJSON;
            Swal.fire({
                icon: 'error',
                toast: true,
                theme: 'dark',
                position: 'bottom-end',
                timer: 3000,
                timerProgressBar: true,
                showConfirmButton: false,
                title: 'No se pudo cargar',
                text: data?.message || 'Error inesperado en el servidor.'
            });
        });
}

function eliminarAjax(titulo, mensaje, url) {
    Swal.fire({
        title: titulo,
        text: mensaje,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        background: '#1e1e1e',
        color: '#fff'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: url,
                type: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function () {
                    location.reload();
                },
                error: function (xhr) {
                    console.error(xhr.responseText);

                    Swal.fire({
                        icon: 'error',
                        // toast: true,
                        title: 'Error',
                        text: 'No se pudo eliminar el registro.'
                    });
                }
            });
        }
    })

}

function ToastDanger(mensaje) {
    Swal.fire({
        icon: 'error',
        text: mensaje,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        theme: 'dark'
    });
}

function ToastSuccess(mensaje) {
    Swal.fire({
        icon: 'success',
        text: mensaje,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        theme: 'dark'
    });
}
