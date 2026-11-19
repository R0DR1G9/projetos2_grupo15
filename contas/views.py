from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from rede_social.models import Perfil
from .forms import CadastroForm, EditarPerfilForm, FotoPerfilForm


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'contas/cadastro.html', {'form': form})


@login_required
def perfil(request):
    user = request.user
    perfil_social, _ = Perfil.objects.get_or_create(usuario=user)
    form_foto = FotoPerfilForm(instance=perfil_social)

    if request.method == 'POST':
        if 'remover_foto' in request.POST:
            if perfil_social.foto:
                perfil_social.foto.delete(save=True)
                messages.success(request, 'Foto de perfil removida.')
            return redirect('perfil')
        if not request.FILES.get('foto'):
            messages.error(request, 'Escolha uma imagem antes de salvar.')
            return redirect('perfil')

        antiga = perfil_social.foto.name if perfil_social.foto else None
        form_foto = FotoPerfilForm(request.POST, request.FILES, instance=perfil_social)
        if form_foto.is_valid():
            perfil_social = form_foto.save()
            if antiga and antiga != perfil_social.foto.name:
                perfil_social.foto.storage.delete(antiga)
            messages.success(request, 'Foto de perfil atualizada!')
            return redirect('perfil')

    empresa = getattr(user, 'empresa', None)   # contas antigas podem não ter CNPJ
    diagnosticos = user.diagnosticos.order_by('-data_criacao')
    ultimo = diagnosticos.first()
    return render(request, 'contas/perfil.html', {
        'empresa': empresa,
        'total_diagnosticos': diagnosticos.count(),
        'ultimo': ultimo,
        'pontuacao': ultimo.calcular_pontuacao() if ultimo else None,
        'perfil_social': perfil_social,
        'form_foto': form_foto,
    })
@login_required
def editar_perfil(request):
    form = EditarPerfilForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Informações atualizadas!')
        return redirect('perfil')
    return render(request, 'contas/editar_perfil.html', {'form': form})