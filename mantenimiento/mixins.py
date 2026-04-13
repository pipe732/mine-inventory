# mantenimiento/mixins.py
from django.shortcuts import redirect
from django.urls import reverse_lazy


class SesionRequeridaMixin:
    """
    Reemplaza @login_requerido para CBV.
    Usa tu sistema de sesiones propio (usuario_documento)
    en lugar del request.user de Django.
    Debe ir PRIMERO en la herencia de cada vista.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('usuario_documento'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class ContextoMixin:
    """
    Inyecta al contexto los atributos declarativos de cada vista.
    Evita repetir el mismo get_context_data en cada clase.
    """
    titulo       = ''
    subtitulo    = ''
    boton_texto  = 'Guardar'
    url_cancelar = None
    url_accion   = None   # ← URL del botón principal en listas
    label_accion = ''     # ← texto de ese botón

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo']       = self.titulo
        ctx['subtitulo']    = self.subtitulo
        ctx['boton_texto']  = self.boton_texto
        ctx['url_accion']   = self.url_accion
        ctx['label_accion'] = self.label_accion
        if self.url_cancelar:
            ctx['url_cancelar'] = reverse_lazy(self.url_cancelar)
        return ctx