import os
import sys
from random import sample, choice

import pygame

SIZE = WIDTH, HEIGHT = 800, 600
FPS = 60
UPDATE_HERO_EVENT = pygame.USEREVENT + 1
MOVE_ENEMY_EVENT = pygame.USEREVENT + 2
FONT_SIZE = 30
FREE_TILE = '.'
EMPTY_TILE = ' '
WALL_TILE = '#'
HERO_TILE = '@'
GHOST_TILE = '!'
TOP = 30  # дополнительные поля сверху
MOVES = UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
ENEMY_DELAY = 500  # задержка врагов, мс
HERO_DELAY = 100  # задержка героя, мс
DIRECTIONS = {
    'RIGHT': 0,
    'UP': 90,
    'LEFT': 180,
    'DOWN': 270
}
LEVELS = ['level1', 'level2', 'level3']
# имена файлов с уровнями, добавьте сюда свой


def load_image(name, color_key=None):
    """Загрузка изображения data/images/name"""
    fullname = os.path.join('data', 'images', name)
    # если файла не существует, то выходим
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(name):
    """Загрузка карты уровня из файла data/name"""
    name = os.path.join('data', name)
    # читаем уровень, убирая символы перевода строки
    with open(name) as map_file:
        level_map = [line.rstrip('\n') for line in map_file]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками (' ')
    return list(map(lambda x: x.ljust(max_width, EMPTY_TILE), level_map))


def start_screen():
    """Вывод стартового/справочного экрана"""
    intro_text = ["(not) PAC-MAN",
                  "",
                  "Правила игры:",
                  "",
                  "Соберите все очки,",
                  "не дайте призракам",
                  "поймать вас!",
                  "",
                  "Управление:",
                  "",
                  "Стрелки - перемещение",
                  "[P] - пауза",
                  "[H] - справка (этот текст)",
                  "[Пробел] - начало новой игры",
                  "после окончания предыдущей",
                  "любая клавиша - окончание паузы",
                  "или закрытие справки"]

    bg_image = load_image('cheerful_pacman.png')
    im_w = bg_image.get_width()
    im_h = bg_image.get_height()
    scale = min(WIDTH / im_w, HEIGHT / im_h, 1)
    new_size = int(im_w * scale), int(im_h * scale)
    bg_image = pygame.transform.scale(bg_image, new_size)
    pos_x = (WIDTH - new_size[0]) // 2
    pos_y = (HEIGHT - new_size[1]) // 2
    screen.blit(bg_image, (pos_x, pos_y))
    font = pygame.font.Font(None, FONT_SIZE)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for _event in pygame.event.get():
            if _event.type == pygame.QUIT:
                terminate()
            elif _event.type == pygame.KEYDOWN or \
                    _event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру или возвращаемся к ней
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    """Окончание работы программы"""
    pygame.quit()
    sys.exit()


def game_over(won=False):
    """Завершение программы (won - выигрыш)"""
    pygame.time.set_timer(MOVE_ENEMY_EVENT, 0)
    pygame.time.set_timer(UPDATE_HERO_EVENT, 0)
    if won:
        show_message(screen, 'You win!', pygame.Color(0, 255, 0))
    else:
        show_message(screen, 'You lose!', pygame.Color(255, 0, 0))


class Level:
    """Класс для работы с игровым уровнем"""
    def __init__(self, _level):
        self.width, self.height = None, None
        self.start = None
        self.map = _level
        self.walls = []
        self.dangerous = []  # список точек, куда могут попасть призраки
        self.free = []
        self.points = []
        self.height = len(self.map)
        self.width = len(self.map[0])
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == WALL_TILE:
                    self.walls.append((x, y))
                elif self.map[y][x] == HERO_TILE:
                    self.start = x, y
                elif self.map[y][x] == FREE_TILE:
                    self.points.append((x, y))
                elif self.map[y][x] == GHOST_TILE:
                    self.dangerous.append((x, y))
        if self.start is None:
            self.start = self.get_free_tiles(1)[0]
            self.points.remove(self.start)
        if len(self.dangerous) < 3:
            exists = len(self.dangerous)
            new_places = sample(self.points, 3 - exists)
            for p in new_places:
                self.points.remove(p)
                self.dangerous.append(p)

    def shutter_point(self, x, y):
        """Уничтожение точки ("съедание" Пакманом)"""
        if (x, y) in self.points:
            self.points.remove((x, y))
            return True
        return False

    def get_tile(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.map[y][x]

    def get_free_tiles(self, k=1):
        """Получение k случайных свободных точек"""
        coords = sample(self.points, k)
        return coords

    def is_free(self, x, y):
        tile = self.get_tile(x, y)
        return tile in (FREE_TILE, EMPTY_TILE, HERO_TILE, GHOST_TILE)

    def find_path_step(self, start, target):
        """Алгоритм поиска первого шага кратчайшего пути"""
        x, y = start
        inf = self.width * self.height
        distance = [[inf] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in MOVES:
                next_x, next_y = x + dx, y + dy
                if self.is_free(next_x, next_y):
                    if distance[y][x] + 1 < distance[next_y][next_x]:
                        distance[next_y][next_x] = distance[y][x] + 1
                        prev[next_y][next_x] = x, y
                        queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == inf or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Entity(pygame.sprite.Sprite):
    """Сущности на игровой карте"""
    def __init__(self, coords, margins, cell_size, *groups):
        super(Entity, self).__init__(*groups)
        self.coords = coords
        self.margins = margins
        self.cell_size = cell_size
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        self.rect.x = self.coords[0] * self.cell_size + self.margins[0]
        self.rect.y = self.coords[1] * self.cell_size + self.margins[1]


class Person(Entity):
    """Персонажи (Пакман и призраки)"""
    def __init__(self, image, coords, margins, cell_size, *groups):
        self.image = pygame.transform.scale(load_image(image),
                                            (cell_size, cell_size))
        super(Person, self).__init__(coords, margins, cell_size, *groups)

    def set_position(self, x, y):
        self.coords = x, y

    def get_position(self):
        return self.coords


class Hero(Person):
    """Пакман"""
    def __init__(self, coords, margins, cell_size, *groups):
        super(Hero, self).__init__('pacman.png', coords, margins, cell_size,
                                   *groups)
        self.direction = 'RIGHT'

    def get_direction(self):
        return self.direction

    def set_direction(self, new_direction):
        angle = DIRECTIONS[new_direction] - DIRECTIONS[self.direction]
        self.image = pygame.transform.rotate(self.image, angle)
        self.direction = new_direction


class Ghost(Person):
    """Призраки"""
    pass


class Wall(Entity):
    """Стена на карте"""
    def __init__(self, coords, margins, cell_size, *groups):
        self.image = pygame.transform.scale(load_image('box.png'),
                                            (cell_size, cell_size))
        super(Wall, self).__init__(coords, margins, cell_size, *groups)


class Point(Entity):
    """Точка, приносящая очки при "съедании" Пакманом"""
    def __init__(self, coords, margins, cell_size, *groups):
        self.image = pygame.transform.scale(load_image('point.png'),
                                            (cell_size, cell_size))
        super(Point, self).__init__(coords, margins, cell_size, *groups)


class Game:
    """Основной класс с игровой логикой"""
    def __init__(self, size):
        self.level = None
        self.cell_size = 0, 0
        self.margins = 0, 0
        self.walls = []
        self.hero = None
        self.enemies = []
        self.points = {}
        self.score = 0
        self.level_file_name = None
        self.new(size)

    def new(self, size):
        new_level_file_name = choice(LEVELS)
        while new_level_file_name == self.level_file_name:
            new_level_file_name = choice(LEVELS)
        self.level_file_name = new_level_file_name
        self.level = Level(load_level(self.level_file_name))
        self.cell_size = min((HEIGHT - TOP) // self.level.height,
                             WIDTH // self.level.width)
        w = self.level.width * self.cell_size
        h = self.level.height * self.cell_size
        self.margins = (size[0] - w) // 2, TOP + (size[1] - TOP - h) // 2
        self.walls.clear()
        for wall_c in self.level.walls:
            self.walls.append(Wall(wall_c, self.margins, self.cell_size,
                                   all_sprites, walls))
        self.hero = Hero(self.level.start, self.margins, self.cell_size,
                         all_sprites)
        ghosts_coords = self.level.dangerous
        self.points.clear()
        for coords in self.level.points:
            self.points[coords] = Point(coords, self.margins, self.cell_size,
                                        all_sprites, points)
        green_ghost = Ghost('green_ghost.png', ghosts_coords[0], self.margins,
                            self.cell_size, all_sprites, ghosts)
        red_ghost = Ghost('red_ghost.png', ghosts_coords[1], self.margins,
                          self.cell_size, all_sprites, ghosts)
        yellow_ghost = Ghost('yellow_ghost.png', ghosts_coords[2],
                             self.margins, self.cell_size, all_sprites, ghosts)
        self.enemies = [green_ghost, red_ghost, yellow_ghost]
        self.score = 0

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        new_d = self.hero.get_direction()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
            new_d = 'LEFT'
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
            new_d = 'RIGHT'
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
            new_d = 'DOWN'
        elif pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
            new_d = 'UP'
        if self.level.is_free(next_x, next_y):
            self.hero.set_position(next_x, next_y)
            self.hero.set_direction(new_d)
            if self.level.shutter_point(next_x, next_y):
                self.score += 1
                self.points[(next_x, next_y)].kill()
                self.points.pop((next_x, next_y))

    def move_enemy(self, enemy):
        others = [en.get_position() for en in self.enemies]
        others.remove(enemy.get_position())
        next_pos = self.level.find_path_step(enemy.get_position(),
                                             self.hero.get_position())
        if next_pos not in others:
            enemy.set_position(*next_pos)

    def move_enemies(self):
        for enemy in self.enemies:
            self.move_enemy(enemy)


def show_text(_screen, pos, text, color=(255, 255, 255), size=FONT_SIZE):
    """Отрисовка текста на _screen"""
    font = pygame.font.Font(None, size)
    text = font.render(text, True, color)
    _screen.blit(text, pos)


def show_message(_screen, message, color=(255, 255, 255), size=FONT_SIZE * 3):
    """Показ сообщения в центре _screen"""
    font = pygame.font.Font(None, size)
    text = font.render(message, True, color)
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = HEIGHT // 2 - text.get_height() // 2
    text_w, text_h = text.get_size()
    pygame.draw.rect(_screen, pygame.Color(0, 0, 0),
                     (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    _screen.blit(text, (text_x, text_y))


def start_new_game():
    """Начало новой игры"""
    global playing
    pygame.time.set_timer(MOVE_ENEMY_EVENT, 0)
    pygame.time.set_timer(UPDATE_HERO_EVENT, 0)
    all_sprites.remove(*all_sprites.sprites())
    ghosts.remove(*ghosts.sprites())
    walls.remove(*walls.sprites())
    points.remove(*points.sprites())
    game.new(screen.get_size())
    playing = True
    pygame.time.set_timer(MOVE_ENEMY_EVENT, ENEMY_DELAY)
    pygame.time.set_timer(UPDATE_HERO_EVENT, HERO_DELAY)


def pause():
    """Пауза - логика событий повторяет меню справки"""
    pygame.time.set_timer(MOVE_ENEMY_EVENT, 0)
    pygame.time.set_timer(UPDATE_HERO_EVENT, 0)
    show_message(screen, 'Pause', pygame.Color(255, 255, 0))
    while True:
        for _event in pygame.event.get():
            if _event.type == pygame.QUIT:
                terminate()
            elif _event.type == pygame.KEYDOWN or \
                    _event.type == pygame.MOUSEBUTTONDOWN:
                pygame.time.set_timer(MOVE_ENEMY_EVENT, ENEMY_DELAY)
                pygame.time.set_timer(UPDATE_HERO_EVENT, HERO_DELAY)
                return  # продолжаем игру
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Pac-Man')
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    points = pygame.sprite.Group()

    start_screen()

    level = choice(LEVELS)
    game = Game(screen.get_size())

    running = True
    playing = True
    start_new_game()
    while running:
        if len(game.points) == 0:
            playing = False
            game_over(True)
        if playing and pygame.sprite.spritecollideany(game.hero, ghosts):
            playing = False
            game_over()
        for event in pygame.event.get():
            if playing:
                if event.type == UPDATE_HERO_EVENT:
                    game.update_hero()
                if event.type == MOVE_ENEMY_EVENT:
                    game.move_enemies()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_p:
                        pause()
            else:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        start_new_game()
            if event.type == pygame.KEYUP and event.key == pygame.K_h:
                start_screen()
            if event.type == pygame.QUIT:
                running = False
        clock.tick(FPS)
        if playing:
            screen.fill('black')
            all_sprites.update()
            all_sprites.draw(screen)
            show_text(screen, (0, 0), 'Score: ' + str(game.score), 'yellow')
        pygame.display.flip()
    terminate()
