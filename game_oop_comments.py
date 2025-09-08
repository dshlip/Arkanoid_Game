#Импорт библиотек
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import pygame
from random import choice
import sqlite3

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize the font module

# Подключение базы данных
# engine=create_engine('sqlite:///play.db')  # Adjust the URL as needed
engine = create_engine("mysql://root:12345@127.0.0.1/game")
Base=declarative_base()

#Создание цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255,  0)
BLUE = (79, 119, 196)

#Таблица юзеров
class User(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True)
    name=Column(Text, nullable=False)


#Таблица результатов
class Score(Base):
    __tablename__='scores'
    id=Column(Integer, primary_key=True)
    user_id=Column(Integer, nullable=False)
    score=Column(Integer, nullable=False)


#Создание таблиц
Base.metadata.create_all(engine)

#Создание сессии
Session=sessionmaker(bind=engine)
session=Session()

# Game constants (постоянные значения)
WIDTH=800
HEIGHT=600
FPS=60
window=pygame.display.set_mode((WIDTH, HEIGHT))
clock=pygame.time.Clock()

#Загрузка изображений
fon=pygame.image.load("images/Menu With Sounds Button.jpg").convert()
fon=pygame.transform.scale(fon, (WIDTH, HEIGHT))
block=pygame.image.load("images/Block dark.png")
block=pygame.transform.scale(block, (100, 40))
fon_over=pygame.image.load("images/Game Over! с рейтингом.jpg")
fon_over=pygame.transform.scale(fon_over, (WIDTH, HEIGHT))
user_menu=pygame.image.load("images/User.jpg")
user_menu=pygame.transform.scale(user_menu, (WIDTH, HEIGHT))
victory=pygame.image.load("images/Victory.jpg")
victory=pygame.transform.scale(victory, (WIDTH, HEIGHT))
background=pygame.image.load("images/Background with Lives, Score, Time.jpg")
background=pygame.transform.scale(background, (WIDTH, HEIGHT))

block_image=pygame.image.load("images/Block Green.jpg")


#Создание блоков
def generate_blocks(variant):
    blocks=[]
    for x, y in variant:
        blocks.append(block_image.get_rect(x=x, y=y))
    return blocks


#Уровни
variants={
    0: [(100, 200), (350, 200), (600, 200)],
    1: [(50, 50), (50, 150), (50, 250), (50, 350),
        (650, 50), (650, 150), (650, 250), (650, 350)],
    2: [(50, 50), (650, 50), (175, 150), (525, 150),
        (350, 200), (175, 250), (525, 250), (50, 350), (650, 350)],
    3: [(100, 100), (100, 140), (100, 180), (100, 220), (100, 260), (100, 300), (100, 340), (100, 380),
        (350, 200), (300, 240), (400, 240), (350, 280),
        (200, 100), (300, 100), (400, 100), (500, 100), (600, 100),
        (600, 140), (600, 180), (600, 220), (600, 260), (600, 300), (600, 340), (600, 380),
        (200, 380), (300, 380), (400, 380), (500, 380), (600, 380)],
    4: [(100, 100), (200, 140), (300, 100), (400, 140), (500, 100), (600, 140),
        (100, 300), (200, 340), (300, 300), (400, 340), (500, 300), (600, 340),
        (100, 200), (200, 240), (300, 200), (400, 240), (500, 200), (600, 240)]
}


#Логика уровней
def equals_variant(count):
    if count < 5:
        return generate_blocks(variants[count])
    else:
        return "end"


#Прямоугольники и кнопки
start=pygame.Rect(280, 453, 240, 90)
input_box=pygame.Rect(300, 300, 240, 60)
sound=pygame.Rect(333, 332, 120, 50)
restart=pygame.Rect(355, 455, 90, 90)
dno=pygame.Rect(0, HEIGHT - 1, WIDTH, 1)

#Переменные игры
gamemode="menu"
count=0
music_playing=False

#Шрифты
shrift=pygame.font.Font("GangSmallYuxian.ttf", 40)
shrift_small=pygame.font.Font("GangSmallYuxian.ttf", 14)


#Классы
class Palka(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() # Конструктор класса (описание)
        self.image=pygame.image.load("images/Palka.png")
        self.image=pygame.transform.scale(self.image, (100, 20))
        self.image_rect=self.image.get_rect(x=WIDTH / 2 - 50, y=530)

    def update(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.image_rect.x-=4
        if keys[pygame.K_RIGHT]:
            self.image_rect.x+=4
        if self.image_rect.x < 0:
            self.image_rect.x=0
        if self.image_rect.x > WIDTH - self.image_rect.width:
            self.image_rect.x=WIDTH - self.image_rect.width

    def restart(self):
        self.image_rect.x=WIDTH / 2 - 50
        self.image_rect.y=530

    def draw(self, window): # Отрисовка
        window.blit(self.image, self.image_rect)


class Sharik(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image=pygame.image.load("images/Sharik.png")
        self.image=pygame.transform.scale(self.image, (30, 30))
        self.image_rect=self.image.get_rect(x=WIDTH / 2 - 15, y=500)
        self.speed_x=4
        self.speed_y=4
        self.score=0
        self.health=3
        self.timing=0

    def update(self, palka, block_group, dno):
        self.image_rect.x+=self.speed_x
        self.image_rect.y+=self.speed_y

        # Столкновение с границами экрана
        if self.image_rect.x < 30 or self.image_rect.x > 740:
            self.speed_x=-self.speed_x
        if self.image_rect.y < 30 or self.image_rect.y > 570:
            self.speed_y=-self.speed_y

        # Столкновение с платформой
        if self.image_rect.colliderect(palka.image_rect):
            self.speed_y=-self.speed_y
            if self.speed_x < 0:
                self.speed_x=-abs(self.speed_x)
            else:
                self.speed_x=abs(self.speed_x)

        # Вызов метода столкновения с блоками
        self.sharik_collide(block_group)

        # Столкновение с нижней границей экрана
        if dno.colliderect(self.image_rect):
            self.health-=1
            self.restart()

    def sharik_collide(self, group): # Столкновение с блоками
        for sprite in group.sprites():
            if self.image_rect.colliderect(sprite.rect):
                self.score += 1
                self.speed_y = -self.speed_y
                sprite.kill()
            if self.score == 10:
                self.score -= 10
                self.health += 1

    def restart(self):
        self.image_rect.x=WIDTH / 2 - 15
        self.image_rect.y=500

    def draw(self, window, frame_count):
        window.blit(self.image, self.image_rect)

        # Отрисовка показателей
        shrift_small=pygame.font.Font("GangSmallYuxian.ttf", 14)
        self.timing=frame_count // FPS
        label_timing=shrift_small.render(str(self.timing), True, 'black')
        label_score=shrift_small.render(f"{self.score}", True, 'black')
        label_health=shrift_small.render(f"{self.health}", True, 'black')
        window.blit(label_score, (255, 8))
        window.blit(label_timing, (390, 8))
        window.blit(label_health, (555, 8))


class Block(pygame.sprite.Sprite):
    def __init__(self, image, rect, group):
        super().__init__()
        self.image=pygame.image.load(choice(image))
        self.rect=rect
        group.add(self)

    # Удаление блоков
    def block_collide(self, group):
        for sprite in group.sprites():
            if self.rect.colliderect(sprite.rect):
                self.kill()


# Музыка
pygame.mixer.music.load('sounds/main_theme.wav')

block_group=pygame.sprite.Group()

# Случайный цвет блоков
random_path = [
    "images/Block Blue.jpg",
    "images/Block Green.jpg",
    "images/Block Light Blue.jpg",
    "images/Block Pink.jpg",
    "images/Block Yellow.jpg"
]

# Создание блоков
def create_block_group(count):
    blocks=equals_variant(count)
    if blocks != "end":
        for block_rect in blocks:
            Block(random_path, block_rect, block_group)
        return block_group
    else:
        return "end"


colour="red"

# Создание объектов класса
palka=Palka()
sharik=Sharik()

run=True
while run:
    if gamemode == "menu": # Gamemode MENU
        pygame.display.update()

        # Обновление переменных
        sharik.health=3
        sharik.score=0
        frame_count=0
        timing=0
        count=0
        text=""
        block_group.empty()
        blocks=create_block_group(0)
        sharik.restart()
        palka.restart()

        window.blit(fon, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and start.collidepoint(event.pos):
                    print("Clicked mouse")
                    gamemode="user"
                elif event.button == 1 and sound.collidepoint(event.pos):
                    music_playing=not music_playing
                    if music_playing:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()

        # Изменение кнопки при включении и выключении музыки
        if music_playing:
            label_sound=shrift.render("on", True, BLUE)
            window.blit(label_sound, (375, 332))
        else:
            label_sound=shrift.render("off", True, BLACK)
            window.blit(label_sound, (365, 332))

    elif gamemode == "user": # Gamemode USER
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active=True
                    colour="black"
                else:
                    active=False
                    colour="red"
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        user_name=text
                        user=session.query(User).filter_by(name=user_name).first()
                        if not user:
                            user=User(name=user_name)
                            session.add(user)
                            session.commit()
                        gamemode="game"
                    elif event.key == pygame.K_BACKSPACE:
                        text=text[:-1]
                    else:
                        text+=event.unicode

        # Отрисовка экрана
        window.blit(user_menu, (0, 0))
        txt_surface=shrift.render(text, True, BLUE)
        width=max(200, txt_surface.get_width() + 10)
        input_box.w=width
        window.blit(txt_surface, (input_box.x + 25, input_box.y + 10))
        pygame.draw.rect(window, colour, input_box, 4)


    elif gamemode == "game": # Gamemode GAME
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False

        palka.update()
        sharik.update(palka, block_group, dno)

        frame_count += 1

        if sharik.health <= 0:
            gamemode="gameover"
            user_id=session.query(User).filter_by(name=text).first().id
            score_obj=Score(user_id=user_id, score=sharik.timing)
            # session.add(score_obj)
            # session.commit()

        window.blit(background, (0, 0))

        # Отрисовка блоков
        if len(block_group.sprites()) > 0:
            for block in block_group.sprites():
                window.blit(block.image, block.rect)
        else:
            count+=1
            block_group.empty()  # Clear the block group
            blocks=create_block_group(count)
            sharik.restart()
            palka.restart()
            if blocks == "end":
                gamemode = "victory"
                user_id=session.query(User).filter_by(name=text).first().id
                score_obj=Score(user_id=user_id, score=sharik.timing)
                session.add(score_obj)
                session.commit()
            else:
                sharik.restart()
                palka.restart()

        # Отрисовка платформы и шарика
        palka.draw(window)
        sharik.draw(window, frame_count)

        # Обновление экрана
        pygame.display.update()

    elif gamemode == "victory": # Gamemode VICTORY
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and restart.collidepoint(event.pos):
                    gamemode="menu"

        window.blit(victory, (0, 0))
        scores=session.query(User.name, Score.score).join(Score, User.id == Score.user_id).order_by(
            Score.score.asc()).limit(3).all()
        y_pos=330
        n=1
        for score in scores:
            score_surf=shrift_small.render(str(n) + ".  " + str(score[0]) + " " + str(score[1]) + " sec", True,
                                           (82, 41, 201))
            window.blit(score_surf, (341, y_pos))
            y_pos+=30
            n+=1

    elif gamemode == "gameover": # Gamemode GAMEOVER
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gamemode="menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and restart.collidepoint(event.pos):
                    gamemode="menu"

        window.blit(fon_over, (0, 0))
        scores=session.query(User.name, Score.score).join(Score, User.id == Score.user_id).order_by(
            Score.score.asc()).limit(3).all()
        y_pos=330
        n=1
        for score in scores:
            score_surf=shrift_small.render(str(n) + ".  " + str(score[0]) + " " + str(score[1]) + " sec", True,
                                           (185, 1, 1))
            window.blit(score_surf, (341, y_pos))
            y_pos+=30
            n+=1

    clock.tick(FPS)

pygame.quit()
