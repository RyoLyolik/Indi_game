import pygame
import os
import main_win
from loading_image import load_image
import json
from inventory import *
from inventory_objects import *
import requests
import json

screen = None
size = w, h, = 720, 480
pygame.init()
font = pygame.font.Font('11939.ttf', 50)

data = open('../settings/game.json', mode='r').read()
data = json.loads(data)


def load():
    data = open('../settings/game.json', mode='r').read()
    data = json.loads(data)
    return data


inv = Invent(8, 5)
inv.cell_size = 40
inv.top = 10

items = {
    'Usual_Sword': UsualSword,
    'Secret_Sword': SecretSword
}


def load_settings():
    player_settings = open('../settings/Player.json').read()
    data = json.loads(player_settings)
    return data


class Menu:
    def __init__(self):
        global screen, data
        data = load()
        screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.buttons = Buttons()
        self.mouse = pygame.Rect(*pygame.mouse.get_pos(), 1, 1)
        self.levels = LevelsRender()
        self.settings = Settings()
        self.settings.mountains_val = data['settings']['mountains']
        self.player = PlayerSettings()
        self.all_sprites = pygame.sprite.Group()
        self.search = Search()
        self.lbar = Loadbar()
        self.auth = Auth()
        self.data_session = json.loads(open('..\\settings\\last_session.json', mode='r').read())
        if self.data_session['id'] != 0:
            response = requests.get('http://127.0.0.1:8000/load_settings/us=' + str(
                self.data_session['id']) + '+pass=' + str(self.data_session['password']))

        if response.ok:
            loaded_setting = response.text.split('|||')[0]
            loaded_setting = json.loads(loaded_setting)
            file = open('../settings/Player.json', mode='w')
            json.dump(loaded_setting, file)
            file.close()
        settings = load_settings()
        self.inv_data = [[Hand((0, 0), True), Hand((0, 2), False),
                          Hand((0, 2), False),
                          Hand((0, 3), False), Hand((0, 4), False)],
                         [Hand((1, 0), False), Hand((1, 1), False),
                          Hand((1, 2), False),
                          Hand((1, 3), False), Hand((1, 4), False)],
                         [Hand((2, 0), False), Hand((2, 1), False),
                          Hand((2, 2), False),
                          Hand((2, 3), False), Hand((2, 4), False)],
                         [Hand((3, 0), False), Hand((3, 1), False),
                          Hand((3, 2), False),
                          Hand((3, 3), False), Hand((3, 4), False)],
                         [Hand((4, 0), False), Hand((4, 1), False),
                          Hand((4, 2), False),
                          Hand((4, 3), False), Hand((4, 4), False)],
                         [Hand((5, 0), False), Hand((5, 1), False),
                          Hand((5, 2), False),
                          Hand((5, 3), False), Hand((5, 4), False)],
                         [Hand((6, 0), False), Hand((6, 1), False),
                          Hand((6, 2), False),
                          Hand((6, 3), False), Hand((6, 4), False)],
                         [Hand((7, 0), False), Hand((7, 1), False),
                          Hand((7, 2), False),
                          Hand((7, 3), False), Hand((7, 4), False)]]
        for i in range(40):
            y = i // 8
            x = i % 8
            if settings['inventory'][str(i)]["type"] == 'Hand':
                self.inv_data[x][y] = Hand((x, y), True)
            else:
                self.inv_data[x][y] = items[settings['inventory'][str(i)]['type']]((x, y), False,
                                                                                   screen,
                                                                                   size=(36, 36))
                self.inv_data[x][y].power = settings['inventory'][str(i)]['power']
                self.inv_data[x][y].upgrade_cost = settings['inventory'][str(i)]['upgrade_cost']
                self.inv_data[x][y].level = settings['inventory'][str(i)]['level']

        self.screen_update()

    def screen_update(self):
        global data, update
        name = None
        self.event = True
        level = None
        name = self.data_session['name']
        while self.event:
            if level is not None:
                self.event = False
                screen.fill((0, 0, 0))
                self.lbar.draw()
                pygame.display.flip()
                run = main_win.Window(int(level), self.settings.mountains_val)
            screen.fill((0, 0, 0))
            self.mouse = pygame.Rect(*pygame.mouse.get_pos(), 1, 1)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.event = False
                    if self.data_session['id'] != 0:
                        setting = ''.join(open('../settings/Player.json').read().split(' '))
                        save = requests.get(
                            'http://127.0.0.1:8000/update_set+id=' + self.data_session[
                                'id'] + '+pass=' + self.data_session[
                                'password'] + '+setting=' + str(setting))
                    quit(0)

                if e.type == pygame.MOUSEBUTTONDOWN:
                    if self.levels.show:
                        level = self.levels.get_lvl(pygame.mouse.get_pos())
                    elif self.search.show:
                        get_level = self.search.get_lvl(pygame.mouse.get_pos())
                        self.lbar.draw()
                        try:
                            response = requests.get(
                                'http://127.0.0.1:8000/current_lvl=' + str(get_level) + '/get')

                            if response.ok:
                                loaded_level = response.text
                                file = open('../LEVELS/lvl_' + str(get_level) + '.txt', mode='w')
                                file.write(loaded_level)
                                file.close()
                                self.levels = LevelsRender()
                        except ConnectionRefusedError:
                            pass
                        except requests.exceptions.ConnectionError:
                            pass
                        except requests.packages.urllib3.exceptions.ProtocolError:
                            pass

                    if self.buttons.show:
                        if self.buttons.levels.colliderect(
                                self.mouse):
                            self.buttons.show = False
                            self.levels.show = True

                        if self.buttons.player_set.colliderect(self.mouse):
                            self.player.show = True
                            self.buttons.show = False

                        if self.buttons.settings.rect.colliderect(self.mouse):
                            self.settings.show = True
                            self.buttons.show = False

                        if self.buttons.auth.rect.colliderect(self.mouse):
                            self.buttons.show = False
                            self.auth.show = True
                            continue

                        if self.buttons.save.colliderect(self.mouse):
                            self.save_settings()

                            continue

                        if self.buttons.load.colliderect(self.mouse):
                            self.load_settings()

                    elif self.auth.show:
                        if self.auth.back.rect.colliderect(self.mouse):
                            self.auth.show = False
                            self.buttons.show = True

                        elif self.auth.id_rect.colliderect(self.mouse):
                            self.auth.id_active = True
                            self.auth.password_active = False

                        elif self.auth.password_rect.colliderect(self.mouse):
                            self.auth.password_active = True
                            self.auth.id_active = False

                        continue

                    elif self.player.show:
                        if self.player.back.rect.colliderect(self.mouse):
                            self.player.show = False
                            self.buttons.show = True

                        inv.get_cell(pygame.mouse.get_pos(), screen)

                    elif self.search.show:
                        if self.search.back.rect.colliderect(self.mouse):
                            self.search.show = False
                            self.buttons.show = True

                    elif self.buttons.settings.rect.colliderect(
                            self.mouse) and self.settings.show is False and self.levels.show is False and self.player.show is False:
                        self.settings.show = True
                        self.buttons.show = False

                    elif self.settings.show and self.buttons.show is False and self.levels.show is False and self.player.show is False:
                        if self.settings.back.rect.colliderect(self.mouse):
                            self.settings.show = False
                            self.buttons.show = True

                    elif self.levels.back.rect.colliderect(
                            self.mouse) and self.levels.show and self.buttons.show is False:
                        self.levels.show = False
                        self.buttons.show = True

                    if self.settings.show:
                        if self.settings.mountains_rect.colliderect(self.mouse):
                            self.settings.mountains_val += 1
                            data['settings']['mountains'] = self.settings.mountains_val

                        self.save_settings()

                    elif self.buttons.search.rect.colliderect(self.mouse):
                        self.buttons.show = False
                        self.search.show = True

                if e.type == pygame.KEYDOWN:
                    if self.search.show:
                        if e.key == pygame.K_BACKSPACE:
                            self.search.text = self.search.text[:-1]

                        elif e.key == pygame.K_RETURN:
                            screen.fill((0, 0, 0))
                            self.lbar.draw()
                            pygame.display.flip()
                            response = requests.get(
                                'http://127.0.0.1:8000/current_lvl=' + self.search.text + '/get')
                            if response.ok:
                                loaded_level = response.text
                                file = open('../LEVELS/lvl_' + str(self.search.text) + '.txt',
                                            mode='w')
                                file.write(loaded_level)
                                file.close()
                                show = self.levels.show
                                self.levels = LevelsRender()
                                self.levels.show = show
                                show = None

                        elif self.search.show:
                            self.search.update(e.unicode)

                    elif self.auth.show:
                        if e.key == pygame.K_BACKSPACE:
                            if self.auth.password_active:
                                self.auth.password = self.auth.password[:-1]

                            elif self.auth.id_active:
                                self.auth.id = self.auth.id[:-1]

                        elif e.key == pygame.K_RETURN:
                            self.data_session = json.loads(
                                open('..\\settings\\last_session.json', mode='r').read())
                            self.data_session['name'] = name
                            self.data_session['password'] = self.auth.password
                            self.data_session['id'] = self.auth.id
                            self.load_settings()

                        elif e.key:
                            if self.auth.password_active:
                                self.auth.password += e.unicode

                            elif self.auth.id_active:
                                self.auth.id += e.unicode

                if e.type == pygame.KEYDOWN and e.key == pygame.K_F5:
                    show = self.search.show
                    self.search = Search()
                    self.search.show = show
                    self.load_settings()
                    show = None
            if self.player.show:
                for i in range(len(self.inv_data)):
                    for j in range(len(self.inv_data[i])):
                        inv_obj = self.inv_data[i][j]
                        if inv_obj.get_type() != 'Hand':
                            inv_obj.draw((inv_obj.place[0] * inv.cell_size + inv.left,
                                          inv_obj.place[1] * inv.cell_size + inv.top), screen)
                        if inv_obj.get_type() != 'Hand' and not self.all_sprites.has(
                                inv_obj.sprite):
                            self.all_sprites.add(inv_obj.sprite)

            else:
                self.all_sprites.empty()
            self.search.draw()
            self.search.online_levels_draw()
            self.buttons.draw()
            self.levels.draw()
            self.settings.draw()
            self.player.draw()
            self.all_sprites.draw(screen)
            self.auth.draw()

            if self.data_session['id'] != 0:
                name_draw = font.render(str(name), 1, (255, 255, 255), 5)
                name_x = (w / 2) - name_draw.get_width() // 2
                name_y = 400
                screen.blit(name_draw, (name_x, name_y))

            pygame.display.flip()

    def save_settings(self):
        setting = ''.join(open('../settings/Player.json').read().split(' '))
        save = requests.get(
            'http://127.0.0.1:8000/update_set+id=' + self.data_session[
                'id'] + '+pass=' + self.data_session[
                'password'] + '+setting=' + str(setting))

    def load_settings(self):
        request = 'http://127.0.0.1:8000/load_settings/us=' + str(
            self.data_session['id']) + '+pass=' + str(self.data_session['password'])
        auth_response = requests.get(request)
        print(auth_response.text)
        print(request)
        if auth_response.text != 'Неверный пароль':
            settings = auth_response.text.split('|||')[0]
            settings = ''.join(settings.split('\n'))
            name = auth_response.text.split('|||')[1]
            file = open('../settings/last_session.json', mode='w')
            json.dump(self.data_session, file)
            file.close()
            file = open('../settings/Player.json', mode='w')
            json.dump(json.loads(settings), file)
            file.close()

class Buttons:
    def __init__(self):
        self.show = True
        self.w, self.h = 210, 75
        self.x, self.y = 360 - self.w // 2, 240 - self.h // 2 - self.h
        self.levels = pygame.Rect(self.x, self.y, self.w, self.h)

        self.settings = pygame.sprite.Sprite()
        self.group = pygame.sprite.Group()
        self.settings.image = load_image('settings.png')
        self.settings.image = pygame.transform.scale(self.settings.image, (64, 64))
        self.settings.rect = self.settings.image.get_rect()
        self.settings.left, self.settings.top = 0, 0

        self.search = pygame.sprite.Sprite()
        self.search.image = load_image('search.png')
        self.search.image = pygame.transform.scale(self.search.image, (64, 64))
        self.search.rect = pygame.Rect(656, 0, 64, 64)

        self.auth = pygame.sprite.Sprite()
        self.auth.image = load_image('auth.png')
        self.auth.image = pygame.transform.scale(self.auth.image, (64, 64))
        self.auth.rect = pygame.Rect(0, 400, 64, 64)

        self.save = pygame.Rect(595, 300, 128, 64)
        self.load = pygame.Rect(595, 364, 128, 64)

        self.group.add(self.settings)
        self.group.add(self.search)
        self.group.add(self.auth)

        self.player_set = pygame.Rect(self.x, self.y + 150, self.w, self.h)

    def draw(self):
        if self.show:
            self.levels = pygame.draw.rect(screen, (255, 255, 255),
                                           (self.x, self.y, self.w, self.h), 5)

            self.player_set = pygame.draw.rect(screen, (255, 255, 255),
                                               (self.x, self.y + 150, self.w, self.h), 5)
            levels = font.render('Levels', 1, (255, 255, 255), 5)
            levels_x = (w / 2) - levels.get_width() // 2
            levels_y = self.y
            screen.blit(levels, (levels_x, levels_y))

            player_text = font.render('Player', 1, (255, 255, 255), 5)
            player_x = (w / 2) - player_text.get_width() // 2
            player_y = self.y + 150
            screen.blit(player_text, (player_x, player_y))

            self.save = pygame.draw.rect(screen, (255, 255, 255), (575, 300, 172, 64), 1)
            self.load = pygame.draw.rect(screen, (255, 255, 255), (575, 364, 172, 64), 1)

            save_text = font.render('Save', 1, (255, 255, 255), 5)
            load_text = font.render('Load', 1, (255, 255, 255), 5)

            save_x = 575
            save_y = 290

            load_x = 575
            load_y = 354

            screen.blit(save_text, (save_x, save_y))
            screen.blit(load_text, (load_x,load_y))

            self.group.draw(screen)


class LevelsRender:
    def __init__(self):
        self.show = False
        self.lvls = os.listdir('../LEVELS')
        self.size = 75
        self.left, self.top = 67, 40
        self.max = 7

        self.back = pygame.sprite.Sprite()
        self.back.image = load_image('cancel.jpg')
        self.back.image = pygame.transform.scale(self.back.image, (64, 64))
        self.back.rect = self.back.image.get_rect()
        self.back.rect.left, self.back.rect.top = 0, 0
        self.group = pygame.sprite.Group()
        self.group.add(self.back)

        self.lvls_grid = []
        for lvl in range(len(self.lvls)):
            if 'lvl' and '.txt' in self.lvls[lvl]:
                if lvl % self.max == 0:
                    self.lvls_grid.append([])

                self.lvls_grid[lvl // self.max].append(self.lvls[lvl])

    def draw(self):
        if self.show == True:
            for i in range(len(self.lvls_grid)):
                for j in range(len(self.lvls_grid[i])):
                    pygame.draw.rect(screen, (255, 255, 255), (
                        j * (self.size + 10) + self.left, i * (self.size + 10) + self.top,
                        self.size,
                        self.size), 0)
                    pygame.draw.rect(screen, (0, 0, 0), (
                        j * (self.size + 10) + 3 + self.left, i * (self.size + 10) + 3 + self.top,
                        self.size - 6, self.size - 6), 0)
                    level = font.render(self.lvls_grid[i][j].split('.')[0].split('_')[-1], 1,
                                        (255, 255, 255))
                    level_x = j * (
                            self.size + 10) + self.left + self.size // 2 - level.get_width() // 2
                    level_y = i * (self.size + 10) + self.top
                    screen.blit(level, (level_x, level_y))

            self.group.draw(screen)

    def get_lvl(self, pos):
        if self.show:
            for i in range(len(self.lvls_grid)):
                for j in range(len(self.lvls_grid[i])):
                    if j * (self.size + 10) + self.left < pos[0] < j * (
                            self.size + 10) + self.left + self.size and i * (
                            self.size + 10) + self.top < pos[1] < i * (
                            self.size + 10) + self.top + self.size:
                        return self.lvls_grid[i][j].split('.')[0].split('_')[-1]
        return None


class Settings:
    def __init__(self):
        self.show = False
        self.back = pygame.sprite.Sprite()
        self.back.image = load_image('cancel.jpg')
        self.back.image = pygame.transform.scale(self.back.image, (64, 64))
        self.back.rect = self.back.image.get_rect()
        self.back.rect.left, self.back.rect.top = 0, 0
        self.group = pygame.sprite.Group()
        self.group.add(self.back)

        self.mountains = font.render('TEXT', 1, (255, 255, 255))
        self.mx = 240
        self.my = 0
        screen.blit(self.mountains, (self.mx, self.my))

        self.mountains_rect = pygame.Rect(350, 70, 96, 48)
        self.mountains_swithcer = pygame.Rect(350, 70, 48, 48)
        self.mountains_val = 1

    def draw(self):
        self.mountains_val = self.mountains_val % 2
        if self.show:
            self.back.rect = self.back.image.get_rect()
            self.back.rect.left, self.back.rect.top = 0, 0
            self.group.draw(screen)

            self.mountains = font.render('Mountains', 5, (255, 255, 255))
            self.mx = 200
            self.my = 60
            screen.blit(self.mountains, (self.mx - self.mountains.get_width() / 2, self.my))

            self.mountains_rect = pygame.draw.rect(screen, (255, 255, 255), (350, 75, 96, 48), 1)
            self.mountains_swithcer = pygame.draw.rect(screen, (255, 255, 255), (
                350 + 48 * (self.mountains_val), 75, 48, 48), 0)

        else:
            self.back.rect = pygame.Rect(0, 0, 0, 0)


class PlayerSettings:
    def __init__(self):
        self.show = False

        self.back = pygame.sprite.Sprite()
        self.back.image = load_image('cancel.jpg')
        self.back.image = pygame.transform.scale(self.back.image, (64, 64))
        self.back.rect = self.back.image.get_rect()
        self.back.rect.left, self.back.rect.top = 0, 0
        self.group = pygame.sprite.Group()
        self.group.add(self.back)

        self.player_sprite = pygame.sprite.Sprite()
        self.player_sprite.image = load_image('../textures/entities/Player/Player_1.png')
        self.player_sprite.image = pygame.transform.scale(self.player_sprite.image, (128, 256))
        self.player_sprite.rect = self.player_sprite.image.get_rect()
        self.player_sprite.rect.top = 150
        self.player_sprite.rect.left = 10

        self.group.add(self.player_sprite)

    def draw(self):
        if self.show:
            self.group.draw(screen)
            inv.render(screen)


class Search:
    def __init__(self):
        self.show = False
        self.back = pygame.sprite.Sprite()
        self.back.image = load_image('cancel.jpg')
        self.back.image = pygame.transform.scale(self.back.image, (64, 64))
        self.back.rect = self.back.image.get_rect()
        self.back.rect.left, self.back.rect.top = 0, 0
        self.text = ''
        self.max = 8

        self.left = 40
        self.top = 150
        self.size = 75

        self.group = pygame.sprite.Group()
        self.group.add(self.back)
        try:
            levels = requests.get('http://127.0.0.1:8000/get_list_of_levels').text
            levels = levels.split('\n')
        except ConnectionRefusedError:
            levels = []
        except requests.exceptions.ConnectionError:
            levels = []
        except requests.packages.urllib3.exceptions.ProtocolError:
            levels = []

        self.lvls_grid = []
        for lvl in range(len(levels)):
            if lvl % self.max == 0:
                self.lvls_grid.append([])

            self.lvls_grid[lvl // self.max].append(levels[lvl])

    def draw(self):
        if self.show:
            self.group.draw(screen)

            self.text_draw = font.render(self.text, 1, (255, 255, 255))
            self.tx = 125
            self.ty = 78
            screen.blit(self.text_draw, (self.tx, self.ty))

            pygame.draw.rect(screen, (255, 255, 255),
                             (120, 80, max(320, self.text_draw.get_width() + 10), 65), 2)

    def update(self, key):
        self.text += key

    def online_levels_draw(self):
        if self.show:
            for i in range(len(self.lvls_grid)):
                for j in range(len(self.lvls_grid[i])):
                    pygame.draw.rect(screen, (255, 255, 255), (
                        j * (self.size + 10) + self.left, i * (self.size + 10) + self.top,
                        self.size,
                        self.size), 0)
                    pygame.draw.rect(screen, (0, 0, 0), (
                        j * (self.size + 10) + 3 + self.left, i * (self.size + 10) + 3 + self.top,
                        self.size - 6, self.size - 6), 0)
                    level = font.render(self.lvls_grid[i][j].split('.')[0].split('_')[-1], 1,
                                        (255, 255, 255))
                    level_x = j * (
                            self.size + 10) + self.left + self.size // 2 - level.get_width() // 2
                    level_y = i * (
                            self.size + 10) + self.top + self.size // 2 - level.get_height() // 2
                    screen.blit(level, (level_x, level_y))

    def get_lvl(self, pos):
        if self.show:
            for i in range(len(self.lvls_grid)):
                for j in range(len(self.lvls_grid[i])):
                    if j * (self.size + 10) + self.left < pos[0] < j * (
                            self.size + 10) + self.left + self.size and i * (
                            self.size + 10) + self.top < pos[1] < i * (
                            self.size + 10) + self.top + self.size:
                        return self.lvls_grid[i][j].split('.')[0].split('_')[-1]
        return None


class Loadbar:
    def __init__(self):
        self.show = False

    def draw(self):
        l_text = font.render('Loading...', 1,
                             (255, 255, 255))
        l_x = 360 - l_text.get_width() // 2
        l_y = 400
        screen.blit(l_text, (l_x, l_y))


class Auth:
    def __init__(self):
        self.show = False
        self.back = pygame.sprite.Sprite()
        self.back.image = load_image('cancel.jpg')
        self.back.image = pygame.transform.scale(self.back.image, (64, 64))
        self.back.rect = self.back.image.get_rect()
        self.back.rect.left, self.back.rect.top = 0, 0

        self.id_active = False
        self.password_active = False

        self.id = ''
        self.password = ''

        self.group = pygame.sprite.Group()
        self.group.add(self.back)
        self.local_font = pygame.font.Font('AGENCYB.ttf', 50)

    def draw(self):
        if self.show:
            self.group.draw(screen)
            if self.id_active:
                self.id_draw = self.local_font.render(self.id, 1, (230, 230, 255))
            else:
                self.id_draw = self.local_font.render(self.id, 1, (180, 180, 180))
            self.idx = 125
            self.idy = 78
            screen.blit(self.id_draw, (self.idx, self.idy))

            if self.id_active:
                self.id_rect = pygame.draw.rect(screen, (200, 200, 255),
                                                (120, 80, max(320, self.id_draw.get_width() + 10), 65),
                                                2)
            else:
                self.id_rect = pygame.draw.rect(screen, (200, 200, 200),
                                                (120, 80, max(320, self.id_draw.get_width() + 10),
                                                 65),
                                                2)

            if self.password_active:
                self.password_draw = self.local_font.render(self.password, 1, (230, 230, 255))
            else:
                self.password_draw = self.local_font.render(self.password, 1, (180, 180, 180))
            self.passwordx = 125
            self.passwordy = 178
            screen.blit(self.password_draw, (self.passwordx, self.passwordy))
            if self.password_active:
                self.password_rect = pygame.draw.rect(screen, (200, 200, 255),
                                                      (120, 180,
                                                       max(320, self.password_draw.get_width() + 10),
                                                       65), 2)

            else:
                self.password_rect = pygame.draw.rect(screen, (200, 200, 200),
                                                      (120, 180,
                                                       max(320, self.password_draw.get_width() + 10),
                                                       65), 2)


if __name__ == '__main__':
    win = Menu()
    pygame.quit()
