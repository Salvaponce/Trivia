from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from trivia_app.models import Pregunta, Respuestas, Score
import random
from trivia_app.form import login_form

from urllib.request import urlopen
import ssl, json, html, time

# Create your views here.

def home(request, user = False):
    if request.session.get('score'):
        del request.session['score']
    if request.session.get('ls'):
        del request.session['ls'] 
    if request.session.get('time'):
        del request.session['time'] 
              
    #Recojo de la API de opentdb todas las categorias de preguntas que tienen
    context = ssl._create_unverified_context()
    res = urlopen('https://opentdb.com/api_category.php', context=context) 
    data = json.loads(res.read()) 
    
    if user:
        return render(request, 'home.html', {'categorias': data['trivia_categories'], 'user': user})
    return render(request, 'home.html', {'categorias': data['trivia_categories']})


def get_preguntas_categoria(num):
    context = ssl._create_unverified_context()
    res = urlopen('https://opentdb.com/api.php?amount=10&category=%s&difficulty=easy&type=multiple' %num, context=context) 
    return json.loads(res.read())['results']


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(user = username, password = raw_password)
            if user is not None:
                login(request, user)
                return render(request, 'home.html', {'user': user})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
    

def login_view(request):    
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password = request.POST['password'])            
            if user is not None:
                login(request, user)
                return home(request, user)
                #return render(request, 'home.html', {'user': user})
    else:
        form = login_form()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return home(request)


def preguntas(request, numero = 0):     
    score = request.session.get('score', 0)
        
    t = request.session.get('time')
    if t is None:
        t = int(time.time())
        request.session['time'] = t 

    # Si es la primera vez que entro en el trivial cojo las preguntas de la categoria elegida
    ls = request.session.get('ls')
    if ls is None or ls == []:
        ls = get_preguntas_categoria(request.POST.get('categoria', False))
        request.session['ls'] = ls 

    if request.method == 'POST' and numero > 0:
        if numero > 9:
    # Si el usuario no esta registrado no se guardara en ningun sitio pero igualmente se mostrara.
    # Si esta registrado se guardara la primera vez y la siguiente la comparara a la ya guardada, tambien se mostrara.
            if str(request.user) != 'AnonymousUser':
                sco = Score.objects.filter(user = request.user).first()
                if sco:
                    if sco.point < score:
                        sco.point = score
                else:
                    sco = Score.objects.create(user = request.user, point = score)
                sco.save()
            return render(request, 'result.html', {'score': score, 'time': int(time.time())-t})

        res = request.POST.get('respuesta', False)
        preg, resp, request.session['score'], *mensaje = get_preguntas_bd(res, ls, score, numero)
    
    return render(request, 'triv.html', {'n':numero, 'p':preg, 'r':resp, 'm':mensaje})


def get_preguntas_bd(res, ls, score, numero):
    # Si la categoria no puede cargarse, utilizara las preguntas y respuestas de la base de datos
    mensaje = ''
    try:
        if res == ls[numero-2]['correct_answer']:
            score += 1
        preg = html.unescape(ls[numero-1]['question'])
        resp = ls[numero-1]['incorrect_answers'] + [ls[numero-1]['correct_answer']]        
        resp = list(map(lambda x: html.unescape(x), resp))
    except:
        pregs = Pregunta.objects.filter(id = numero).first()
        preg = pregs.pregunta
        resp = Respuestas.objects.filter(pregunta = numero)
        lst = [pregs.resp_correcta]
        resp = list(map(lambda x: lst.append(x.texto), resp))
        resp = lst
        mensaje = 'We could not load the selected category'
        if res == pregs.resp_correcta:
            score += 1
        
    random.shuffle(resp)

    return preg, resp, score, mensaje


def ranking(request):
    print(type(Score.objects.all()))
    return render(request, 'ranking.html', {'lista': zip(Score.objects.all().order_by('-point'), range(1, len(Score.objects.all())+1))})