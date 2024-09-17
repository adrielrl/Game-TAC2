import pygame
from sys import exit
import math
import random
from settings import *

pygame.init()
pygame.mixer.init()

# Criando a janela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("CounterShot")
relogio = pygame.time.Clock()

# Carregar imagens
fundo = pygame.image.load("fundo.png").convert()

# Configurar Som
somTiro = pygame.mixer.Sound("somtiro.wav")
somTiro.set_volume(0.2)
inimigoMorte = pygame.mixer.Sound("inimigoMorte.wav")
inimigoMorte.set_volume(0.2)
jogadorMorte = pygame.mixer.Sound("morte.mp3")
jogadorMorte.set_volume(0.2)
pygame.mixer.music.load('somfundo.mp3')
pygame.mixer.music.set_volume(0.2)


# Definir fonte
fonte = pygame.font.Font(None, 74)

def colocarTexto(texto, fonte, janela, x, y):
    superficie_texto = fonte.render(texto, True, (255, 255, 255)) # Texto branco
    rect_texto = superficie_texto.get_rect()
    rect_texto.topleft = (x, y)
    janela.blit(superficie_texto, rect_texto)

def tela_entrada():
    tela.fill((0, 0, 0))
    colocarTexto('CounterShot', fonte, tela, LARGURA / 3, ALTURA / 3)
    colocarTexto('Pressione uma tecla ou clique para começar', fonte, tela, LARGURA / 20, ALTURA / 2)

    pygame.display.update()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                esperando = False
    
tela_entrada()
pygame.mixer.music.play(-1)


class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.posicao = pygame.math.Vector2(JOGADOR_INICIO_X, JOGADOR_INICIO_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("personagem.png").convert_alpha(), 0, TAMANHO_JOGADOR)
        self.imagem_base_jogador = self.image
        self.rect_colisao = self.imagem_base_jogador.get_rect(center=self.posicao)
        self.rect = self.rect_colisao.copy()
        self.velocidade = VELOCIDADE_JOGADOR
        self.atirar = False
        self.tempo_tiro = 0
        self.deslocamento_arma = pygame.math.Vector2(DESLOCAMENTO_ARMA_X, DESLOCAMENTO_ARMA_Y)
        self.vida_jogador = 100

    def get_dano(self, valor_dano):
        if self.vida_jogador > 0:
            self.vida_jogador -= valor_dano
        if self.vida_jogador <= 0:
            self.vida_jogador = 0
            jogadorMorte.play()

    def rotacao_jogador(self):
        self.coordenadas_mouse = pygame.mouse.get_pos()
        self.x_diferenca_mouse_jogador = (self.coordenadas_mouse[0] - LARGURA // 2)
        self.y_diferenca_mouse_jogador = (self.coordenadas_mouse[1] - ALTURA // 2)
        self.angulo = math.degrees(math.atan2(self.y_diferenca_mouse_jogador, self.x_diferenca_mouse_jogador))
        self.image = pygame.transform.rotate(self.imagem_base_jogador, -self.angulo)
        self.rect = self.image.get_rect(center=self.rect_colisao.center)

    def entrada_usuario(self):
        self.velocidade_x = 0
        self.velocidade_y = 0

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w]:
            self.velocidade_y = -self.velocidade
        if teclas[pygame.K_s]:
            self.velocidade_y = self.velocidade
        if teclas[pygame.K_d]:
            self.velocidade_x = self.velocidade
        if teclas[pygame.K_a]:
            self.velocidade_x = -self.velocidade

        if self.velocidade_x != 0 and self.velocidade_y != 0: 
            self.velocidade_x /= math.sqrt(2)
            self.velocidade_y /= math.sqrt(2)
        self.rotacao_jogador()
        if pygame.mouse.get_pressed() == (1, 0, 0) or teclas[pygame.K_SPACE]:
            self.atirar = True
            self.disparar()
        else:
            self.atirar = False

    def disparar(self):
        if self.tempo_tiro == 0:
            somTiro.play()
            self.tempo_tiro = TEMPO_TIROS
            posicao_bala = self.posicao + self.deslocamento_arma.rotate(self.angulo)
            self.bala = Bala(posicao_bala[0], posicao_bala[1], self.angulo)
            grupo_balas.add(self.bala)
            grupo_todos_sprites.add(self.bala)

    def movimentar(self):
        self.posicao += pygame.math.Vector2(self.velocidade_x, self.velocidade_y)
        self.rect_colisao.center = self.posicao
        self.rect.center = self.rect_colisao.center

    def update(self):
        self.entrada_usuario()
        self.movimentar()
        self.rotacao_jogador()

        if self.tempo_tiro > 0:
            self.tempo_tiro -= 1

class Bala(pygame.sprite.Sprite):
     def __init__(self, x, y, angulo):
        super().__init__()
        self.image = pygame.image.load("tiro1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, ESCALA_BALA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angulo = angulo
        self.velocidade = VELOCIDADE_BALA
        self.x_vel = math.cos(self.angulo * (2 * math.pi / 360)) * self.velocidade
        self.y_vel = math.sin(self.angulo * (2 * math.pi / 360)) * self.velocidade
        self.tempo_vida_bala = TEMPO_VIDA_BALA
        self.tempo_criacao = pygame.time.get_ticks()          

     def movimento_bala(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.tempo_criacao > self.tempo_vida_bala:
            self.kill()

     def update(self):
        self.movimento_bala()

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, posicao):
        super().__init__(grupo_inimigos, grupo_todos_sprites)
        self.image = pygame.image.load("inimigo.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)
        self.rect = self.image.get_rect(center=posicao)
        self.velocidade = VELOCIDADE_INIMIGO
        self.posicao = pygame.math.Vector2(posicao)
        self.dano = 30
        self.vida = 100 

    def caçar_jogador(self):
        vetor_jogador = pygame.math.Vector2(jogador.rect.center)
        vetor_inimigo = pygame.math.Vector2(self.rect.center)
        direcao = (vetor_jogador - vetor_inimigo).normalize() if vetor_jogador != vetor_inimigo else pygame.math.Vector2()
        self.posicao += direcao * self.velocidade
        self.rect.center = self.posicao

    def verificar_colisao_jogador(self):
        if pygame.Rect.colliderect(self.rect, jogador.rect_colisao):
            jogador.get_dano(self.dano) 
            self.kill()

    def receber_dano(self, dano):
        self.vida -= dano
        if self.vida <= 0:
            self.kill()
            inimigoMorte.play()

    def update(self):
            self.caçar_jogador()
            self.verificar_colisao_jogador()

class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.deslocamento = pygame.math.Vector2()

    def desenhar_customizado(self):
        self.deslocamento.x = jogador.rect.centerx - LARGURA // 2
        self.deslocamento.y = jogador.rect.centery - ALTURA // 2

        tela.blit(fundo, -self.deslocamento)

        for sprite in grupo_todos_sprites:
            pos_offset = sprite.rect.topleft - self.deslocamento
            tela.blit(sprite.image, pos_offset)


def desenhar_vida(jogador, tela):
    pygame.draw.rect(tela, (255, 0, 0), (10, 10, 200, 20))
    pygame.draw.rect(tela, (0, 255, 0), (10, 10, jogador.vida_jogador * 2, 20))

def gerar_inimigos(grupo_inimigos, numero_inimigos):
    for _ in range(numero_inimigos):
        posicao_aleatoria = (random.randint(0, LARGURA), random.randint(0, ALTURA))
        inimigo = Inimigo(posicao_aleatoria)
        grupo_inimigos.add(inimigo)

def tela_game_over():
    tela.fill((0, 0, 0)) 
    colocarTexto('Game Over', fonte, tela, LARGURA / 3, ALTURA / 3)
    pygame.display.update()
    pygame.time.wait(2000) 
    pygame.quit()
    exit()

# Grupos de sprites
grupo_todos_sprites = pygame.sprite.Group()
grupo_balas = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()

# Instanciar objetos
jogador = Jogador()
camera = Camera()
inimigo = Inimigo((400, 400))

# Adicionar ao grupo de sprites
grupo_todos_sprites.add(jogador)
grupo_todos_sprites.add(inimigo)
gerar_inimigos(grupo_inimigos, 10)
grupo_todos_sprites.add(grupo_inimigos)

# Loop principal do jogo
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Atualizar sprites
    grupo_todos_sprites.update()

    # Verificar colisões entre balas e inimigos
    for bala in grupo_balas:
        inimigos_acertados = pygame.sprite.spritecollide(bala, grupo_inimigos, False)
        for inimigo in inimigos_acertados:
            inimigo.receber_dano(20) # Dano de 20 ao inimigo
            bala.kill()

# Verificar se o jogador está morto
    if jogador.vida_jogador <= 0:
        tela_game_over()

    camera.desenhar_customizado()
    desenhar_vida(jogador, tela)
    grupo_todos_sprites.update()

    pygame.display.update()
    relogio.tick(FPS)