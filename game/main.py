import pygame
from sys import exit
import math
from settings import *

pygame.init()

# Criando a janela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tiro de Cima")
relogio = pygame.time.Clock()

# Carregar imagens
fundo = pygame.transform.scale(pygame.image.load("fundo.png").convert(), (LARGURA, ALTURA))


class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.posicao = pygame.math.Vector2(JOGADOR_INICIO_X, JOGADOR_INICIO_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("personagem2.png").convert_alpha(), 0, TAMANHO_JOGADOR)
        self.imagem_base_jogador = self.image
        self.rect_colisao = self.imagem_base_jogador.get_rect(center=self.posicao)
        self.rect = self.rect_colisao.copy()
        self.velocidade = VELOCIDADE_JOGADOR
        self.atirar = False
        self.tempo_tiro = 0
        self.deslocamento_arma = pygame.math.Vector2(DESLOCAMENTO_ARMA_X, DESLOCAMENTO_ARMA_Y)

    def rotacao_jogador(self):
        self.coordenadas_mouse = pygame.mouse.get_pos()
        self.x_diferenca_mouse_jogador = (self.coordenadas_mouse[0] - self.rect_colisao.centerx)
        self.y_diferenca_mouse_jogador = (self.coordenadas_mouse[1] - self.rect_colisao.centery)
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

        if self.velocidade_x != 0 and self.velocidade_y != 0:  # Movimento diagonal
            self.velocidade_x /= math.sqrt(2)
            self.velocidade_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or teclas[pygame.K_SPACE]:
            self.atirar = True
            self.disparar()
        else:
            self.atirar = False

    def disparar(self):
        if self.tempo_tiro == 0:
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

jogador = Jogador()

grupo_todos_sprites = pygame.sprite.Group()
grupo_balas = pygame.sprite.Group()

grupo_todos_sprites.add(jogador)

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()

    tela.blit(fundo, (0, 0))

    grupo_todos_sprites.draw(tela)
    grupo_todos_sprites.update()

    pygame.display.update()
    relogio.tick(FPS)