#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
	* Kivy version 1.10.1
	* Matheus Felipe Teodoro Correia
	* matheuscorreia559@gmail.com
	*
	* Aplicativo Muhna
	----implementado
	* Jogo da memoria
	* banco de dados com placar
	* Quiz
'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image, AsyncImage
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.animation import Animation
from threading import Thread
from kivy.core.window import Window
import sqlite3
import time
import random
import json


# Variaveis globais

texto = []
inicio = 0
fim = 0

'''
	*	lembrar:
	*   	nao se esquecer que compila em python 2 (VM-buildozer)
	*   	setxkbmap br = teclado em pt-br kivy (VM-buildozer)
	*   	acerto.jpeg eh usado apenas como marcacao de acerto, nao eh uma imagem
	*
'''

Clock.max_iteration = 30

class Gerenciador(ScreenManager):  # gerenciador de telas
	def __init__(self, **kwargs):
		super(Gerenciador, self).__init__(**kwargs)


class Inserenome(BoxLayout):		#	textinput com botao de salvar no canto direito
	nome = ''
	def __init__(self, **kwargs):
		super(Inserenome, self).__init__(**kwargs)

	def salvanome(self):

		self.__class__.nome = self.ids.texinp.text
		self.ids.texinp.text = ""
		print(self.__class__.nome)

	def guardabanco(self):  # da pra usar o on_dismiss

		if(self.__class__.nome == ''):
			print("Nenhum nome salvo")

		else:
			print("Salvo no banco de dados = "+str(self.__class__.nome))
			banco = sqlite3.connect('memoria.db')
			c = banco.cursor()
			c.execute('''CREATE TABLE IF NOT EXISTS rank (nome text, pontos integer, tempo real, erros integer)''')
			parametros = (self.__class__.nome, Jogo().getPontos(), tempo, Jogo().getErros())
			c.execute("INSERT INTO rank VALUES (?,?,?,?)", parametros)
			banco.commit()
			self.__class__.nome = ''

	def setNome(self, nome = ''):
		self.__class__.nome = nome

	def getNome(self):
		return self.__class__.nome


class Menu(Screen):		#	menu inical para navegar entre as telas
	def __init__(self, **kwargs):
		super(Menu, self).__init__(**kwargs)


class Quiz(Screen):		#Tela do Quiz
	quiz_pontos = 0
	five_caixas = []
	visit = []

	def __init__(self,**kwargs):
		super(Quiz,self).__init__(**kwargs)

	def mov(self,id = 0,arg='',*args):		#	no Quiz depois do jogador responder um pergunta ela move ele para a proxima
	
		scroll_quiz = arg.parent.parent
		self.__class__.visit[id] = 1
		for j in range(5):
			if(self.__class__.visit[j] != 1):
				scroll_quiz.scroll_to(self.__class__.five_caixas[j])
				break

	def on_enter(self, *args):		#	terminada a animacao de entrada na tela, carrega os 3 melhores do quiz

		banco = sqlite3.connect('quiz.db')
		c = banco.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS rank (nome text,pontos integer,tempo real)''')
		dump = c.execute("SELECT nome,pontos,tempo from rank order by pontos desc, tempo asc limit 3")##conta os de cima
		
		j = dump.fetchall()
		
		box = BoxLayoutCustom2()
		box.cor = 0.10,0.05,0,0
		box.add_widget(LabelBotao(text='Os 3 melhores no quiz',color=(0,0,0,1)))
		self.ids.qg.add_widget(box)
		
		box = BoxLayoutCustom2()
		box.cor = 0.10,0.05,0,.9
		box.add_widget(Tarefa_two(text='N°'))
		box.add_widget(Tarefa_two(text='Nome'))
		box.add_widget(Tarefa_two(text='Pontos'))
		box.add_widget(Tarefa_two(text='Tempo'))
		
	
		
		self.ids.qf.add_widget(box)
		ind = 1
		cor = 0.10,0.05,0,.8

		if (len(j) != 0):
			
			for dumps in j:
				box = BoxLayoutCustom2()
				if (ind % 2 == 0):
					cor = [0.30,0.14,0,1]
				else:
					cor = [0.30,0.14,0,.3]
				
				box.cor = cor
				
				box.add_widget(Tarefa_two(text=str(ind)))#posicao
				box.add_widget(Tarefa_two(text=dumps[0]))#nome
				box.add_widget(Tarefa_two(text=str(dumps[1])))#pontos
				box.add_widget(Tarefa_two(text=str(dumps[2])+'s'))#tempo
				self.ids.qf.add_widget(box)
				ind+=1
		else:
			box = BoxLayoutCustom2()
			box.cor = [0.30,0.14,0,.3]
			box.add_widget(Tarefa_two(text=str(1)))
			box.add_widget(Tarefa_two(text=str("Muhna")))
			box.add_widget(Tarefa_two(text=str("2019")))
			box.add_widget(Tarefa_two(text=str(0.1)+'s'))
			self.ids.qf.add_widget(box)
			

	def previous_screen_limpa(self, *args):		# animacao da troca de tela corre para a direita
	
		self.manager.transition.direction = 'right'
		self.manager.current = 'menu'
		self.manager.transition.bind(on_complete=self.restart_limpa)
		
		# for key,val in self.ids.items():
		#   print("key={0}, val={1}".format(key,val))
		self.__class__.quiz_pontos = 0

	def restart_limpa(self,  *args):		# animacao da troca de tela corre para a esquerda

		self.manager.transition.direction = 'left'
		self.manager.transition.unbind(on_complete=self.restart_limpa)
		self.limpatela()

	def limpatela(self,*args):#botao recomecar, limpa a tela e cria uma nova tela       
		self.parent.remove_widget(self)
		quiz = Quiz(name='quiz')
		self.parent.add_widget(quiz)
		
		Pergunta().clear()
	
	def carregaWidgets(self):		#	carrega os widgets do jogo Quiz
		box = Loading()
		self.ids.qz.add_widget(box)
		Clock.schedule_once(lambda dt: self.carregaWidgetsF(self),0.3)		#	joga 0.3s a frente a funcao carregaWidgetsF
		print("Iniciou")

	def carregaWidgetsF(self,*args):		# cria os layouts com perguntas e alternativas

		self.__class__.visit = [0]*5

		self.__class__.five_caixas = []
		
		conteudo = open('quiz.json').read()
		arquivos = json.loads(conteudo)
		#print(arquivos[19])
		cont = 0
		self.ids.qz.clear_widgets()
		for j in range(5):  
			selecionado = random.choice(arquivos)			
			pergunta = selecionado['Pergunta']			
			salvar = []
			
			for respostas in selecionado[u'Respostas']:         
				salvar.append(respostas)
		
			random.shuffle(salvar)

			adc = []
			for i in salvar:

				adc.append(i['resp'])
				adc.append(i['flag'])
				
			arquivos.remove(selecionado)
			adc.append(j)

			temp = Pergunta(pergunta=pergunta,args=adc,id=cont)

			self.__class__.five_caixas.append(temp)
			self.ids.qz.add_widget(temp)

			cont+=1
			
		self.__class__.quiz_inicial = time.time()

	def constroi(self):#coloca os widget de pergunta na tela do quiz
		for widget in self.temp:
			self.ids.qz.add_widget(widget)
		self.__class__.quiz_inicial = time.time()

	def desconstroi(self,*args):#remove todos os widgets da tela do quiz
		self.ids.qz.clear_widgets()
	
	#set e getters
	
	def setQuiz_inicial(self,valor):
		self.__class__.quiz_inicial = valor
	
	def getQuiz_inicial(self):
		return self.__class__.quiz_inicial

	def setQuiz_pontos(self, valor = 0):
		self.__class__.quiz_pontos = valor

	def getQuiz_pontos(self):
		return self.__class__.quiz_pontos


class MyLabel(Image):#redimensiona os textos
	text = StringProperty('')
	def __init__(self,**kwargs):
		super(MyLabel,self).__init__(**kwargs)
	def on_text(self, *args):
		# Just get large texture:
		l = Label(text="Selecione a quantidade de imagens para o novo jogo",color=(0,0,0,1),bold=True)#,outline_width=40,outline_color=(0.22,0.10,0.03))
		l.font_size = '50dp'  # something that'll give texture bigger than phone's screen size
		l.texture_update()
		# Set it to image, it'll be scaled to image size automatically:
		self.texture = l.texture


class GridLayout_custom(GridLayout):
	def __init__(self,**kwargs):
		super(GridLayout_custom,self).__init__(**kwargs)


class Jogo(Screen):#Tela do jogo da memoria
	contador = 0
	qtdimagens = 0
	erros = 0
	tempo = 0
	pontos = 0

	def __init__(self,**kwargs):
		super(Jogo,self).__init__(**kwargs)

	def on_enter(self):		#	terminada a animacao de entrada na tela
		
		banco = sqlite3.connect('memoria.db')
		c = banco.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS rank (nome text,pontos integer,tempo real,erros integer)''')
		dump = c.execute("SELECT nome,pontos,tempo,erros from rank order by pontos desc , erros asc ,tempo asc limit 3")##conta os de cima
		j = dump.fetchall()


		box = BoxLayoutCustom2()
		box.cor = 0.10,0.05,0,0
		box.add_widget(LabelBotao(text='Os 3 melhores no jogo da memória',color=(0,0,0,1)))
		#MyLabel(text='Os 3 melhores',size_hint_y=None,height='60dp')
		self.ids.label.add_widget(box)

		box = BoxLayoutCustom2()
		box.cor = 0.10,0.05,0,.9
		box.add_widget(Tarefa_two(text='N°'))
		box.add_widget(Tarefa_two(text='Nome'))
		box.add_widget(Tarefa_two(text='Pontos'))
		box.add_widget(Tarefa_two(text='Tempo'))
		box.add_widget(Tarefa_two(text='erros'))

		self.ids.tbox2.add_widget(box)
		ind = 1
		cor = 0.10,0.05,0,.8
		if (len(j) != 0):
			for dumps in j:
				box = BoxLayoutCustom2()
				if (ind % 2 == 0):
					cor = [0.30,0.14,0,1]
				else:
					cor = [0.30,0.14,0,.3]
				
				box.cor = cor
				box.add_widget(Tarefa_two(text=str(ind)))#posicao
				box.add_widget(Tarefa_two(text=dumps[0]))#nome
				box.add_widget(Tarefa_two(text=str(dumps[1])))#pontos
				box.add_widget(Tarefa_two(text=str(dumps[2])+'s'))#tempo
				box.add_widget(Tarefa_two(text=str(dumps[3])))#erros
				self.ids.tbox2.add_widget(box)
				ind+=1
		else:
			pnt = 2019
			tmp = 1
			for i in range(3):
				box = BoxLayoutCustom2()
				box.cor = [0.30,0.14,0,.3]
				box.add_widget(Tarefa_two(text=str('-')))
				box.add_widget(Tarefa_two(text=str('-')))
				box.add_widget(Tarefa_two(text=str('-')))
				box.add_widget(Tarefa_two(text=str('-')))
				box.add_widget(Tarefa_two(text=str('-')))
				self.ids.tbox2.add_widget(box)
				tmp += 1
				pnt -= 1

	def addImagem(self,valor):		#	adc os widgets com o text contendo os nomes das imagens      
		global inicio
		
		self.__class__.qtdimagens = valor
		inicio = time.time()		#	inicia a contagem de tempo
		cont=0

		result = random.sample(range(1,29), valor)		#	gera um vetor de tamanho valor(4,6,10) entre 1 e 28(quantidade de imagens na pasta)
		nova = result[:]								#	copia do vetor
		random.shuffle(result)							#	result foi embaralhado

		self.ids.gridlayout.size_hint_y = 1

		for j in range(valor):
			selecionado = random.choice(result)								#	sorteia um item do vetor
			selecionadoT = random.choice(nova)								#	sorteia um item do vetor
	
			result.remove(selecionado)										#	remove o item sorteado
			nova.remove(selecionadoT)										#	remove o item sorteado

			texto = "imagens/"+str(selecionado)+'.jpg'						#	gera o nome da imagem
			self.ids.gridlayout.add_widget(ImageButton(text=str(texto)))	#	adc a imagem no gridlayot

			texto = "imagens/"+str(selecionadoT)+'.jpg'
			self.ids.gridlayout.add_widget(ImageButton(text=str(texto)))

			cont+=2

	def previous_screen(self, *args):
		self.manager.transition.direction = 'right'
		self.manager.current = 'menu'
		self.manager.transition.bind(on_complete=self.restart)
	
	def restart(self,  *args):
		self.manager.transition.direction = 'left'
		self.manager.transition.unbind(on_complete=self.restart)
	
	def previous_screen_limpa(self, *args):
	
		global inicio,fim

		self.manager.transition.direction = 'right'
		self.manager.current = 'menu'
		self.manager.transition.bind(on_complete=self.restart_limpa)
		self.__class__.erros = 0
		self.__class__.pontos = 0
		self.__class__.qtdimagens = 0
		inicio = 0
		fim=0

	def restart_limpa(self,  *args):
		global texto

		self.manager.transition.direction = 'left'
		self.manager.transition.unbind(on_complete=self.restart_limpa)
		self.limpatela()
		
		self.__class__.contador = 0
		texto = []

	def limpatela(self,*args):#botao recomecar, limpa a tela e cria uma nova tela       
		self.parent.remove_widget(self)
		jogo = Jogo(name='jogo')
		self.parent.add_widget(jogo)

	def setQtdimagens(self,qtd = 0):
		self.__class__.qtdimagens = qtd

	def getQtdimagens(self):
		return self.__class__.qtdimagens

	def setContador(self,valor = 0):
		self.__class__.contador = valor

	def getContador(self):
		return self.__class__.contador

	def setErros(self, valor = 0):
		self.__class__.erros = valor

	def getErros(self):
		return self.__class__.erros

	def setTempo(self, valor = 0):
		self.__class__.tempo = valor

	def getTempo(self):
		return self.__class__.tempo
	def setPontos(self,valor = 0):
		self.__class__.pontos = valor

	def getPontos(self):
		return self.__class__.pontos;


class ImageButton(ButtonBehavior, AsyncImage):

	#lendo o json com os nomes dos anime/plantas
	conteudo = open('arquivo.json').read()
	arquivos = json.loads(conteudo)
	ident = []
	Memo_fechar = []
	tempo = 0
	flag = 0
	def __init__(self,text='',**kwargs):
		super(ImageButton,self).__init__(**kwargs)
		
		self.id = str(self.__class__.flag)
		self.text = text
		self.__class__.flag+=1
	def guardabanco_t(self):
		if(Inserenome().getNome() == ''):
			print("Nenhum nome salvo")
			banco = sqlite3.connect('memoria.db') 		#deletando a marca do BD 
			c = banco.cursor()
			c.execute("DELETE FROM rank WHERE nome like '&&&marca&&&';")
			banco.commit()

		else:
			print("Salvo no banco de dados teste = "+Inserenome().getNome()+' '+str(Jogo().getTempo()))
			
			banco = sqlite3.connect('memoria.db')
			c = banco.cursor()
			c.execute("UPDATE rank SET nome = ?  WHERE nome = '&&&marca&&&';",[Inserenome().getNome()])
			banco.commit()
		
			Inserenome().setNome(nome = '')

		self.__class__.flag = 0
		Jogo().setTempo(valor = 0)
		Jogo().setPontos(valor = 0)
		Jogo().setErros(valor = 0)
			
	def pop(self,*args):
		global inicio,fim

		Jogo().setTempo(valor = '{:0.2f}'.format(fim - inicio))
		print(Jogo().getTempo())

		banco = sqlite3.connect('memoria.db')
		c = banco.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS rank (nome text,pontos integer,tempo real,erros integer)''')

		c.execute("INSERT into rank (nome,pontos,tempo, erros) values (?,?,?,?);",['&&&marca&&&',Jogo().getPontos(),Jogo().getTempo(),Jogo().getErros()])
		
		c.execute("CREATE TEMP TABLE tmp_rank AS SELECT nome,pontos,tempo, erros FROM rank ORDER BY pontos desc, tempo asc, erros asc")


		dump = c.execute("SELECT rowid,nome,pontos,tempo,erros from tmp_rank order by pontos desc, tempo asc, erros asc")

		#print("3 de cima----------------")
		
		posicao = c.execute("select rowid from tmp_rank where nome like '&&&marca&&&'")
		posicao = posicao.fetchall()
		posicao = posicao[0][0]
		
		dump = c.execute("SELECT rowid, nome, pontos,tempo, erros from (SELECT rowid, nome, pontos,tempo,erros from (SELECT rowid, nome, pontos,tempo, erros FROM tmp_rank where rowid < ? ORDER by pontos desc, tempo asc, erros asc) as A order by  pontos asc, tempo desc, erros desc limit 3) as AB order by rowid asc;",[posicao])
		
		Vdump = []
		for a in dump.fetchall():
			Vdump.append(a)

		#print("Posicao no BD----------------")
		dump = c.execute("SELECT rowid AS posicao, nome, pontos,tempo, erros FROM tmp_rank where posicao =  ? ORDER by pontos desc, tempo asc, erros asc;",[posicao])
		
		a = dump.fetchall()
		a = a[0]
		Vdump.append(a)


		#print("3 de baixo----------------")

		dump = c.execute("SELECT posicao, nome, pontos,tempo, erros from(SELECT rowid AS posicao, nome, pontos,tempo, erros FROM tmp_rank where posicao >  ? ORDER by pontos desc, tempo asc, erros asc limit 3)  as AB order by posicao asc;",[posicao])
		
		for a in dump.fetchall():
			Vdump.append(a)
		
		pop = Popcustom(title='Fim de jogo',title_size='30sp',title_align='center',size_hint=(1,1),auto_dismiss=False,background = 'imagens/fundo.png', background_color=(0,0,0,.9),separator_color=(0,0,0,0))
		
		box = BoxLayoutCustom2()
		box.cor = 0.10,0.05,0,.9
		box.add_widget(Tarefa_two(text='N°'))
		box.add_widget(Tarefa_two(text='Nome'))
		box.add_widget(Tarefa_two(text='Pontos'))
		box.add_widget(Tarefa_two(text='Tempo'))
		box.add_widget(Tarefa_two(text='Erros'))
		pop.ids.box.add_widget(box)
		cont = 0
		#print("TUPLA=-=-=-=-=-=-=-=-")
		for tupla in Vdump:

			if (cont % 2 == 0):
				cor = [0.30,0.14,0,.6]
			else:
				cor = [0.30,0.14,0,.4]

			box = BoxLayoutCustom2()
			box.cor = cor
			if(tupla[1] == '&&&marca&&&'):
				box.add_widget(Tarefa_two(text=str(tupla[0])))#posica
				box.add_widget(InserenomeMemory())#nome
				box.add_widget(Tarefa_two(text=str(Jogo().getPontos())))#pontos
				box.add_widget(Tarefa_two(text=str(Jogo().getTempo())+'s'))#tempo
				box.add_widget(Tarefa_two(text=str(Jogo().getErros())))
				save = box
			else:
				box.add_widget(Tarefa_two(text=str(tupla[0])))
				box.add_widget(Tarefa_two(text=tupla[1]))#nome
				box.add_widget(Tarefa_two(text=str(tupla[2])))
				box.add_widget(Tarefa_two(text=str(tupla[3])+'s'))#tempo(real)
				box.add_widget(Tarefa_two(text=str(tupla[4])))
			pop.ids.box.add_widget(box)
			cont+=1

		pop.ids.scroll.scroll_to(save)
		# print(pop.ids.scroll)
		b2 = BoxLayoutCustom2(orientation='vertical',cor=(1,1,1,0))
		self.__class__.Memo_fechar = Botao_custom(text='Fechar',on_press = ImageButton.guardabanco_t ,on_release=pop.dismiss) 
		self.__class__.Memo_fechar.rgba = [0,0.20,0,1]
		b2.add_widget(self.__class__.Memo_fechar)
		pop.ids.box.add_widget(b2)
		
		#anim = Animation(size_hint=(1,1),duration=1,t='out_back')
		#anim.start(pop)
		
		c.execute("DROP TABLE tmp_rank;")
		banco.commit()
		pop.open()
		#Clock.schedule_once(pop.open, 1.2)
	

	def AcertoImg(self,text=[]):

		box = BoxLayout(orientation = 'vertical')#,padding=10,spacing=10)

		figura = Image(source=str(text))        
		box.add_widget(figura)
		
		pop = Popup(title=self.arquivos[text],title_font='DejaVuSans',separator_height='0dp',auto_dismiss=False,title_color=(1,1,1,1),title_size='30sp', content = box,size_hint=(.7,.7),title_align='center',background = 'imagens/fundo.png', background_color=(0,0,0,.8),separator_color=(0,0,0,0))#,size=(100,100))

		anim = Animation(size_hint=(1,1),duration=0.2,t='out_back')
		anim.start(pop)
		
		pop.open()
		
		Clock.schedule_once(pop.dismiss, 1)

	def troca(self,text=[]):#troca as imagens do botao
		global texto

		if(Jogo().getContador() < 2 and text != 'acerto.jpeg'):
			Jogo().setContador(valor = Jogo().getContador() + 1)
			texto.append(str(text))
			self.__class__.ident.append(self.id)
			if(self.source and self.text != 'acerto.jpeg'):
				self.source = self.text
				self.canvas.ask_update()

		Clock.schedule_once(self.conta, 0.5)#chama a funcao 0.5s a frente que verifica se a imagem eh certa
		#self.conta()

	def conta(self,text=[]):#verifica se as imagens sao iguais e altera para acerto.png, se nao ele volta para pergunta.png

		global texto,fim

		
		if(Jogo().getContador() == 2):
			if( (texto[0] == texto[1]) and (self.__class__.ident[0] != self.__class__.ident[1]) ):
				self.AcertoImg(texto[0])
				print("Memoria->acerto")
				for child in self.parent.children:
					if(child.text == texto[0] and child.text != 'acerto.jpeg' ):            
						child.source = child.text
						child.text = 'acerto.jpeg'
				Jogo().setPontos(valor = Jogo().getPontos()+1)
				if(Jogo().getPontos() == Jogo().getQtdimagens()):
					fim = time.time()
					print("FINAL JG Memoria")
					Clock.schedule_once(self.pop,1.2)           
			else:
				Jogo().setErros(valor = Jogo().getErros()+1)
				print("Memoria->erro")
				for child in self.parent.children:
					if(child.source != 'imagens/pergunta.png' and child.source != 'acerto.jpeg' and child.text != 'acerto.jpeg'  ):
						child.source = 'imagens/pergunta.png'                       
			
			Jogo().setContador(valor = 0)
			texto=[]
			self.__class__.ident=[]
	
	def setMemo_fechar(self,valor):
		self.__class__.Memo_fechar = valor

	def getMemo_fechar(self, *args):
		return self.__class__.Memo_fechar


class Tarefa_two(BoxLayout):
	def __init__(self,text='',**kwargs):
		super(Tarefa_two,self).__init__(**kwargs)
		if(text != None):   
			self.ids.label.text = text
		else:
			self.ids.label.text = ''
class Tarefa(BoxLayout):

	def __init__(self,text='',**kwargs):
		super(Tarefa,self).__init__(**kwargs)
		if(text != None):   
			self.ids.label.text = text
		else:
			self.ids.label.text = '-'


class BoxLayoutCustom(BoxLayout):
	def __init__(self,**kwargs):
		super(BoxLayoutCustom,self).__init__(**kwargs)


class BoxLayoutCustom2(BoxLayout):
	def __init__(self,**kwargs):
		super(BoxLayoutCustom2,self).__init__(**kwargs)


class Loading(BoxLayout):
	def __init__(self,**kwargs):
		super(Loading,self).__init__(**kwargs)


class Ranking(Screen):

	def __init__(self, tarefas=[], **kwargs):
		super(Ranking, self).__init__(**kwargs)

	def addWidget(self):
		texto = self.ids.texto.text
		self.ids.box.add_widget(Tarefa(text=texto))
		self.ids.texto.text = ''

	def teste(self):
		banco = sqlite3.connect('memoria.db')
		c = banco.cursor()
		dump = c.execute("SELECT nome,pontos,erros,tempo from rank ORDER BY tempo ASC, erros ASC, pontos DESC limit 20")

		contador = 1
		for linha in dump.fetchall():

			if (contador % 2 == 0):
				cor = [0, 0, 0, .4]
			else:
				cor = [0, 0, 0, .2]

			box = BoxLayoutCustom()
			box.cor = cor
			box.add_widget(Tarefa(text=str(contador)))
			box.add_widget(Tarefa(text=linha[0]))
			box.add_widget(Tarefa(text=str(linha[1])))
			box.add_widget(Tarefa(text=str(linha[2])))
			box.add_widget(Tarefa(text=str(linha[3])+'s'))
			contador += 1

			self.ids.box.add_widget(box)
		self.ids.scroll.scroll_to(box)
		self.ids.action.parent.remove_widget((self.ids.action))

	def previous_screen_limpa(self, *args):

		self.manager.transition.direction = 'right'
		self.manager.current = 'menu'
		self.manager.transition.bind(on_complete=self.restart_limpa)


	def restart_limpa(self,  *args):
		self.manager.transition.direction = 'left'
		self.manager.transition.unbind(on_complete=self.restart_limpa)
		self.limpatela()


	def limpatela(self,*args):#botao recomecar, limpa a tela e cria uma nova tela       
		self.parent.remove_widget(self)
		teste = Ranking(name='ranking')
		self.parent.add_widget(teste)



class LabelBotao(Image):

	text = StringProperty(' ')
	
	def __init__(self , **kwargs):
		super(LabelBotao, self).__init__(**kwargs)

	def on_text(self, *args):
		# Just get large texture:
		l = Label(text=self.text,font_name='RobotoMono-Regular.ttf',color=(1,1,1,1))#,outline_width=40,outline_color=(0.22,0.10,0.03))
		l.font_size = '50dp'  # something that'll give texture bigger than phone's screen size
		l.texture_update()
		# Set it to image, it'll be scaled to image size automatically:
		self.texture = l.texture

class Botao(ButtonBehavior,LabelBotao): 

	branco = ListProperty([1,1,1,1])
	preto = ListProperty([0,0,0,1])
	

	def __init__(self, **kwargs):
		super(Botao, self).__init__(**kwargs)
	def on_press(self):
		self.color = self.preto
		
	def on_release(self):
		self.color = self.branco
		

class Roundedbotao(ButtonBehavior,LabelBotao):

	branco = ListProperty([1,1,1,1])
	preto = ListProperty([0,0,0,1])
	
	def __init__(self, **kwargs):
		super(Roundedbotao, self).__init__(**kwargs)
	def on_press(self):
		self.color = self.preto 
	def on_release(self):
		self.color = self.branco
class Pergunta(BoxLayout):
	pontos = 0
	selec = 0
	tempo = 0
	quiz_fechar = []
	quiz_final = 0
	quiz_nome = ''

	def __init__(self,pergunta='',args = ["","","","","","","","",""],id=0,**kwargs):
		
		super(Pergunta,self).__init__(**kwargs)
		# for key,val in self.ids.items():
		#   print("key={0}, val={1}".format(key,val))
		self.ids.perg.text = pergunta
		self.ref = id
		
		self.ids.r1.text = args[0]#reposta
		self.ids.r10.flag = args[1]#flag certo ou errado(1 == certo, 0 == errado)
		self.ids.r10.group = str(args[8])

		self.ids.r2.text = args[2]
		self.ids.r20.flag = args[3]
		self.ids.r20.group = str(args[8])

		self.ids.r3.text = args[4]
		self.ids.r30.flag = args[5]
		self.ids.r30.group = str(args[8])

		self.ids.r4.text = args[6]
		self.ids.r40.flag = args[7]
		self.ids.r40.group = str(args[8])

		
		
	def clear(self):
		print("LIMPANDO")       
		self.__class__.pontos = 0
		self.__class__.selec = 0
		self.__class__.tempo = 0
		self.__class__.fechar = []
	def guardabanco_t(self, *args):		#	da pra usar o on_dismiss
		
		self = Pergunta()		#	self estava sendo um Button resultando em um erro
		
		if(self.__class__.quiz_nome == ''):
			print("Nenhum nome salvo")
			banco = sqlite3.connect('quiz.db')
			c = banco.cursor()
			c.execute("DELETE FROM rank WHERE nome like '&&&marca&&&';")
			banco.commit()


		else:
			print("Salvo no banco de dados quiz = "+str(self.__class__.quiz_nome)+' '+str(self.__class__.tempo))
			
			banco = sqlite3.connect('quiz.db')
			c = banco.cursor()
			c.execute("UPDATE rank SET nome = ?  WHERE nome = '&&&marca&&&';",[self.__class__.quiz_nome])
			banco.commit()

			self.__class__.quiz_nome = ''
			self.__class__.tempo = 0
			Quiz().setQuiz_pontos(0)
			
	def pop(self,*args):

		banco = sqlite3.connect('quiz.db')
		c = banco.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS rank (nome text,pontos integer,tempo real)''')
		
		c.execute("INSERT into rank (nome,pontos,tempo) values (?,?,?);",['&&&marca&&&',Quiz().getQuiz_pontos(),self.tempo])
	
		
		c.execute("CREATE TEMP TABLE tmp_rank AS SELECT nome,pontos,tempo FROM rank ORDER BY pontos desc, tempo asc")


		dump = c.execute("select rowid,nome,pontos,tempo from tmp_rank order by pontos desc, tempo asc")

		#print("3 de cima----------------")
		
		posicao = c.execute("select rowid from tmp_rank where nome like '&&&marca&&&'")
		posicao = posicao.fetchall()
		posicao = posicao[0][0]
		
		dump = c.execute("SELECT rowid, nome, pontos,tempo from (SELECT rowid, nome, pontos,tempo from (SELECT rowid, nome, pontos,tempo FROM tmp_rank where rowid < ? ORDER by pontos desc, tempo asc) as A order by  pontos asc, tempo desc limit 3) as AB order by rowid asc;",[posicao])
		
		Vdump = []
		for a in dump.fetchall():
			Vdump.append(a)

		#print("Posicao no BD----------------")
		dump = c.execute("SELECT rowid AS posicao, nome, pontos,tempo FROM tmp_rank where posicao =  ? ORDER by pontos desc, tempo asc;",[posicao])
		
		a = dump.fetchall()
		a = a[0]
		Vdump.append(a)


		#print("3 de baixo----------------")

		dump = c.execute("SELECT posicao, nome, pontos,tempo from(SELECT rowid AS posicao, nome, pontos,tempo FROM tmp_rank where posicao >  ? ORDER by pontos desc, tempo asc limit 3)  as AB order by posicao asc;",[posicao])
		
		for a in dump.fetchall():
			Vdump.append(a)
		
		pop = Popcustom(title='Fim de jogo',title_size='30sp',title_align='center',size_hint=(1,1),auto_dismiss=False,background = 'imagens/fundo.png', background_color=(0,0,0,.9),separator_color=(0,0,0,0))
		
		box = BoxLayoutCustom2()
		box.cor = 0.10,0.05,0,.9
		box.add_widget(Tarefa_two(text='N°'))
		box.add_widget(Tarefa_two(text='Nome'))
		box.add_widget(Tarefa_two(text='Pontos'))
		box.add_widget(Tarefa_two(text='Tempo'))
		pop.ids.box.add_widget(box)
		cont = 0
		#print("TUPLA=-=-=-=-=-=-=-=-")
		for tupla in Vdump:

			if (cont % 2 == 0):
				cor = [0.30,0.14,0,.6]
			else:
				cor = [0.30,0.14,0,.4]

			box = BoxLayoutCustom2()
			box.cor = cor
			if(tupla[1] == '&&&marca&&&'):
				box.add_widget(Tarefa_two(text=str(tupla[0])))#posica
				box.add_widget(Inserenome2())#nome
				box.add_widget(Tarefa_two(text=str(Quiz().getQuiz_pontos())))#pontos
				box.add_widget(Tarefa_two(text=str(self.tempo)+'s'))#tempo(real)
				save = box
			else:
				box.add_widget(Tarefa_two(text=str(tupla[0])))
				box.add_widget(Tarefa_two(text=tupla[1]))#nome
				box.add_widget(Tarefa_two(text=str(tupla[2])))
				box.add_widget(Tarefa_two(text=str(tupla[3])+'s'))#tempo(real)
		
			pop.ids.box.add_widget(box)
			cont+=1

		pop.ids.scroll.scroll_to(save)
		b2 = BoxLayoutCustom2(orientation='vertical',cor=(1,1,1,0))
		self.__class__.quiz_fechar = Botao_custom(text='Fechar',on_press = Pergunta.guardabanco_t ,on_release=pop.dismiss) 
		self.__class__.quiz_fechar.rgba = [0,0.20,0,1]
		b2.add_widget(self.__class__.quiz_fechar)
		pop.ids.box.add_widget(b2)
		
		#anim = Animation(size_hint=(1,1),duration=1,t='out_back')
		#anim.start(pop)
		
		c.execute("DROP TABLE tmp_rank;")
		banco.commit()
		
		Clock.schedule_once(pop.open, 0.5)

	def verifica(self,flag):
		
		Clock.schedule_once(lambda dt:Quiz().mov(id =self.ref,arg = self),0.4)
		
		self.__class__.selec+=1
		if(flag):
			print("Acertou")
			self.rgba = [0,0.8,0,1]
			Quiz().setQuiz_pontos(valor = Quiz().getQuiz_pontos()+1)
			
		else:
			self.rgba = [0.35,0,0,1]
			print("errou")

		for child in self.children:
			
			flag = 0
			for child1 in reversed(child.children):
				#print(type(child1))
				if(child1.name == 'checkbox'):
					child1.disabled = True
					if(child1.flag == 1):
						flag = 1
				if(flag == 1):
					if(child1.name == 'label'):
						child1.color = 0.12, 0.5, 0, 1
						flag = 0
		if(self.selec == 5):
			self.__class__.quiz_final = time.time()
			self.__class__.tempo = ('{:.2f}'.format(self.__class__.quiz_final - Quiz().getQuiz_inicial()))
			self.__class__.selec = 0
			# a = Thread(target = self.pop, args = [])
			# a.start()
			Clock.schedule_once(lambda dt: self.pop(), 0.1)
	
	def setQuiz_nome(self, nome = ''):
		self.__class__.quiz_nome = nome

	def getQuiz_nome(self):
		return self.__class__.quiz_nome

	def setQuiz_fechar(self,valor=0):
		self.__class__.quiz_fechar = valor

	def getQuiz_fechar(self, *args):
		return self.__class__.quiz_fechar


class InserenomeMemory(BoxLayout):
	
	def __init__(self,**kwargs):
		super(InserenomeMemory,self).__init__(**kwargs)
	def salvanome(self):
		if (len(self.ids.texinp.text) != 0):
			Inserenome().setNome(nome=self.ids.texinp.text)
			self.ids.box1.add_widget(Tarefa_two(text=Inserenome().getNome()))

		else:
			self.ids.box1.add_widget(Tarefa_two(text=':/'))

	def redmensiona(self):#teclado abaixo do textinput
		Window.softinput_mode = 'below_target'
	def finishScroll(self,scroll):
		Clock.schedule_once(lambda dt: scroll.scroll_to(ImageButton().getMemo_fechar()),0.5)#move o scrollview ate o botao fechar

class Inserenome2(BoxLayout):

	def __init__(self,**kwargs):
		super(Inserenome2,self).__init__(**kwargs)
	
	def salvanome(self):
		
		if (len(self.ids.texinp.text) != 0):
			Pergunta().setQuiz_nome(nome=self.ids.texinp.text)
			self.ids.box1.add_widget(Tarefa_two(text=Pergunta().getQuiz_nome()))
		else:
			self.ids.box1.add_widget(Tarefa_two(text=':/'))

	def redmensiona(self):#teclado abaixo do textinput
		Window.softinput_mode = 'below_target'
	
	def finishScroll(self,scroll):
		Clock.schedule_once(lambda dt: scroll.scroll_to(Pergunta().getQuiz_fechar(),0.5))#move o scrollview ate o botao fechar


class Popcustom(Popup):
	def __init__(self,**kwargs):
		super(Popcustom,self).__init__(**kwargs)

class Botao_custom(ButtonBehavior,LabelBotao):
	def __init__(self,**kwargs):
		super(Botao_custom,self).__init__(**kwargs)
class Novo(App):
	#title = 'Muhna'
		
	def build(self):
		self.title = 'Muhna'
		self.icon = 'imagens/pergunta.png'
		Clock.max_iteration = 50

		banco = sqlite3.connect('quiz.db')
		c = banco.cursor()
		c.execute("DELETE FROM rank WHERE nome like '&&&marca&&&';")
		banco.commit()

		banco = sqlite3.connect('memoria.db')
		c = banco.cursor()
		c.execute("DELETE FROM rank WHERE nome like '&&&marca&&&';")
		banco.commit()


		return Gerenciador()
	
	def on_pause(self):
		'''
		Aqui voce pode salvar alguma coisa, caso necessario.
		Como dados de um banco de dados ainda em aberto.
		O que estiver na tela nao e necessario. Normalmente so retorne True.
		'''
		return True
	
	def on_resume(self):
		'''
		Aqui voce estara retornando ao seu App.
		Normalmente voce nao precisara fazer nada.
		'''
		pass
	def on_stop(self):

		print("Saindo na forca")
		#deletando uma marcacao dos dois BD
		banco = sqlite3.connect('quiz.db')
		c = banco.cursor()
		c.execute("DELETE FROM rank WHERE nome like '&&&marca&&&';")
		banco.commit()

		banco = sqlite3.connect('memoria.db')
		c = banco.cursor()
		c.execute("DELETE FROM rank WHERE nome like '&&&marca&&&';")
		banco.commit()
Novo().run()