from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from app.models import Receita, Comentario, Avaliacao
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def filtrar_categorias(request):
    receitas = Receita.objects.all()
    categorias = Receita.objects.values_list('categoria', flat=True).distinct()  # Obtém categorias únicas

    context = {
        'receitas': receitas,
        'categorias': categorias,  
    }
    return render(request, 'index.html', context)

@login_required
def adicionar_comentario(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comentario_texto = data.get('texto', '').strip()

            if not comentario_texto:
                return JsonResponse({'error': 'Texto não pode estar vazio.'}, status=400)

            # Substituindo 'usuario' por 'user'
            novo_comentario = Comentario(receita_id=pk, texto=comentario_texto, usuario=request.user)
            novo_comentario.save()

            return JsonResponse({'usuario': request.user.username, 'texto': comentario_texto})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)

@login_required
def adicionar_avaliacao(request, pk):
    if request.method == 'POST':
        receita = get_object_or_404(Receita, pk=pk)
        try:
            data = json.loads(request.body)
            nota = data.get('nota')

            if nota is not None:
                nota = int(nota)
                if nota < 0 or nota > 5:
                    return JsonResponse({'error': 'Nota deve estar entre 0 e 5.'}, status=400)

                avaliacao_existente = Avaliacao.objects.filter(receita=receita, usuario=request.user).first()
                if avaliacao_existente:
                    avaliacao_existente.nota = nota
                    avaliacao_existente.save()
                else:
                    Avaliacao.objects.create(receita=receita, usuario=request.user, nota=nota)

                media_avaliacao = receita.avaliacoes.aggregate(Avg('nota'))['nota__avg']
                media_avaliacao = int(media_avaliacao) if media_avaliacao is not None else 0
                return JsonResponse({'media_avaliacao': media_avaliacao})

            return JsonResponse({'error': 'Nota não pode estar vazia.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)

class IndexView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        receitas = Receita.objects.annotate(media_avaliacao=Avg('avaliacoes__nota')).all()
        categorias = Receita.objects.values_list('categoria', flat=True).distinct()

        categoria_selecionada = request.GET.get('categoria')
        if categoria_selecionada:
            receitas = receitas.filter(categoria=categoria_selecionada)

        for receita in receitas:
            receita.media_avaliacao = int(receita.media_avaliacao) if receita.media_avaliacao is not None else 0
            
        return render(request, self.template_name, {
            'receitas': receitas,
            'categorias': categorias,
            'categoria_selecionada': categoria_selecionada,
            'user': request.user,  # Inclui o usuário no contexto
        })


class ReceitaView(View):
    template_name = 'receitas.html'

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

        receita = get_object_or_404(Receita, pk=pk)
        comentarios = Comentario.objects.filter(receita=receita).select_related('usuario')

        media_avaliacao = receita.avaliacoes.aggregate(Avg('nota'))['nota__avg']
        media_avaliacao = int(media_avaliacao) if media_avaliacao is not None else 0

        context = {
            'receita': receita,
            'comentarios': comentarios,
            'media_avaliacao': media_avaliacao,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

        data = json.loads(request.body)
        comentario_texto = data.get('texto', '').strip()

        if not comentario_texto:
            return JsonResponse({'error': 'Texto não pode estar vazio.'}, status=400)

        novo_comentario = Comentario(receita_id=pk, texto=comentario_texto, usuario=request.user)
        novo_comentario.save()

        return JsonResponse({'usuario': request.user.username, 'texto': comentario_texto})

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            usuario = authenticate(request, username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('index')
            else:
                messages.error(request, 'Nome de usuário ou senha incorretos.')

        elif 'register' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            try:
                User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                usuario = authenticate(request, username=username, password=password)
                login(request, usuario)
                return redirect('index')

            except Exception as e:
                messages.error(request, f'Erro ao registrar: {str(e)}')

        return render(request, 'login.html')

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('index') 
