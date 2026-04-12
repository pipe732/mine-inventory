# mantenimiento/mixins.py
from django.shortcuts import redirect
from django.urls import reverse_lazy


class SesionRequeridaMixin:
    """
    Equivalente a @login_requerido pero para CBV.
    Django tiene LoginRequiredMixin pero ese usa request.user,
    tú usas sesiones propias — este mixin respeta tu sistema.
    Se coloca PRIMERO en la herencia para que se ejecute antes que la vista.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class ContextoMixin:
    """
    Centraliza el contexto repetido en todas las vistas.
    Solo declaras los atributos en cada vista — el mixin los inyecta.
    """
    titulo = ''
    subtitulo = ''
    boton_texto = 'Guardar'
    url_cancelar = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = self.titulo
        ctx['subtitulo'] = self.subtitulo
        ctx['boton_texto'] = self.boton_texto
        if self.url_cancelar:
            ctx['url_cancelar'] = reverse_lazy(self.url_cancelar)
        return ctx