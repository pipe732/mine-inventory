from django.shortcuts import render, redirect
from .forms import EstanteForm

def crear_estante(request):
    if request.method == 'POST':
        form = EstanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_estante')
    else:
        form = EstanteForm()

    return render(request, 'crear_estante.html', {
        'form': form,
        'titulo': 'Registrar Estante'
    })


def vista_estantes(request):
    return render(request, 'estantes.html')