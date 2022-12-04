"""
 █░█ █▄░█ █▀█ █▀▀ ▄▀█ █░░  █▀▀ █▄░█ █▀▄ ▀ █▀
 █▄█ █░▀█ █▀▄ ██▄ █▀█ █▄▄  ██▄ █░▀█ █▄▀ ░ ▄█
 version: 6.9
 """

import pygame as pg
import numpy as np
from numba import njit
import mysql.connector as msc
from sys import exit

screen_width = 1364
screen_height =720


def credits():
    f= open("credits.txt","w")
    tex="""
 __ __                 _    _____       _     
|  |  |___ ___ ___  __| |  |   __|___ _| |___ 
|  |  |   |  _| -_||. | |  |   __|   | . |_ -|
|_____|_|_|_| |___|___|_|  |_____|_|_|___|___|
                                version 6.9
    |------------------------|
    |Computer Science Project|
    |Vyasa Vidya Peethom     |
    |------------------------|
    .______________.
    |Group Members |
    .______________.
    |Adhityadev t.s|
    |Gaurav Krishn |
    |Pranav S      |
    .______________.

    """
    s=f.write(tex)
    print(s)

def msc():
    pass
    connect = msc.connect(host='localhost',user = 'root', passwd = 'vyasa', db ='' )
    if connect.is_connected() == False:
        print("Unable to connect to Database!")
    cursor = connect.cursor()
    cursor.execute("select * from test")
    connect.close()

def main():
    pg.init()
    screen_width = 1364
    screen_height = 735
    pg.display.set_caption("Unreal End's ")
    font = pg.font.SysFont("Courier New", 70)
    
    sounds = load_sounds()
    m_vol, sfx_vol, music = 0.4, 0.5, 0
    set_volume(m_vol, sfx_vol, sounds)
    sounds['music'+str(music)].play(-1)
    
    stepdelay = pg.time.get_ticks()/200
    stepdelay2 = stepdelay
    click, clickdelay = 0, stepdelay
    
    screen = pg.display.set_mode((screen_width,screen_height))
        
    running, pause, options, newgame = 1, 1, 0, 2
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)
    timer = 0
    hres, halfvres, mod, frame = adjust_resolution()
    fullscreen = 0
    level, player_health, gunsp, story = 0, 0, 0, 0


    level_textures = [[0, 1, 0, 0, 1, 4],
                      [0, 2, 1, 1, 0, 3], 
                      [1, 0, 2, 1, 1, 4], 
                      [1, 3, 1, 0, 0, 1], 
                      [2, 1, 2, 1, 1, 0],
                      [2, 0, 0, 0, 0, 2]] 

    menu = [pg.image.load('Assets/Menu/menu0.png').convert_alpha()]
    menu.append(pg.image.load('Assets/Menu/options.png').convert_alpha())
    menu.append(pg.image.load('Assets/Screens/credits.png').convert_alpha())
    menu.append(pg.image.load('Assets/Menu/menu1.png').convert_alpha())
    hearts = pg.image.load('Assets/Misc/hearts.png').convert_alpha()
    colonel = pg.image.load('Assets/Sprites/colonel1.png').convert_alpha()
    hearts2 = pg.Surface.subsurface(hearts,(0,0,player_health*10,20))
    exit1 = pg.image.load('Assets/Misc/exit.png').convert_alpha()
    exit2 = 1
    exits = [pg.Surface.subsurface(exit1,(0,0,50,50)), pg.Surface.subsurface(exit1,(50,0,50,50))]
    splash = []
    for i in range(4):
        splash.append(pg.image.load('Assets/Screens/splash'+str(i)+'.png').convert())
    blood = pg.image.load('Assets/Misc/blood0.png').convert_alpha()
    blood_size = np.asarray(blood.get_size())
    sky1 = hearts.copy() 
    msg = "Press any key !"
    surf = splash[0].copy()
    splash_screen(msg, splash[0], clock, font, screen)
    msg = " "
    
    while running:
        pg.display.update()
        ticks = pg.time.get_ticks()/200
        er = min(clock.tick()/500, 0.3)
        if not pause and (player_health <= 0 or (exit2 == 0  and int(posx) == exitx and int(posy) == exity)):
            msg = ' '
            if player_health <= 0:
                credits()
                sounds['died'].play()
                newgame = 2
                surf = splash[3].copy()
            else:
                credits()
                level += 1
                player_health = min(player_health+2, 20)
                
                sounds['won'].play()
                newgame = 1
                if level > 5:
                    level, newgame = 0, 2
                    sounds['died'].play()
                    surf = splash[2].copy()
                    surf.blit(font.render('Total time: ' + str(round(timer,1)), 1, (255, 255, 255)), (20, 525))
                else:
                    msg = "Cleared level " + str(level-1)+'!'
            splash_screen(msg, surf, clock, font, screen)
            pause, clickdelay = 1, ticks
            pg.time.wait(500)

        if pg.mouse.get_pressed()[0]:
            if gunsp < 1 and not pause:
                gunsp, damage_mod = 1, 1
            if pause and ticks - clickdelay > 1:
                click, clickdelay = 1, ticks
                sounds['healthup'].play()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                    
            if event.type == pg.KEYDOWN:
                if event.key == ord('p') or event.key == pg.K_ESCAPE:
                    if not pause:
                        pause = 1
                    else:
                        if options > 0:
                            options = 0
                        elif newgame == 0:
                            pause = 0
                    pg.mouse.set_pos(400,300)

                if event.key == ord('f'): 
                    pg.display.toggle_fullscreen()
                    fullscreen =  not(fullscreen)

        if  pause:
            clock.tick(60)

            surf2, pause, options, running, newgame, adjust_res, m_vol, sfx_vol, story = pause_menu(
                surf.copy(), menu, pause, options, click, running, m_vol, sfx_vol, sounds, newgame, font, msg, level, ticks, hres, story)
            
            if adjust_res != 1:
                hres, halfvres, mod, frame = adjust_resolution(int(hres*adjust_res))
                sky = pg.surfarray.array3d(pg.transform.smoothscale(sky1, (720, halfvres*4)))
                adjust_res = 1             

            screen.blit(surf2, (0,0))
            click = 0
            
            if newgame == 1:
                newgame, pause = 0, not(pause)
                if player_health <= 0 or msg[0] != 'C':
                    surf = splash[1].copy()
                    splash_screen(' ', surf, clock, font, screen)
                    level, player_health, timer = 0, 20, -0.1

                if np.random.randint(0, 2) != music:
                    sounds['music'+str(music)].fadeout(1000)
                    music = int(not(music))
                    sounds['music'+str(music)].play(-1)
                
                msg = 'Loading...'
                surf2 = surf.copy()
                surf2.blit(font.render(msg, 1, (255, 255, 255)), (30, 500))
                surf2.blit(font.render(msg, 1, (30, 255, 155)), (32, 502))
                screen.blit(surf2, (0,0))
                pg.display.update()
                msg = ' '

                if story:
                    posx, posy, rot, rotv, maph, mapc, exitx, exity, stepscount, size = load_map(level)
                    nlevel = level_textures[level]
                    
                else:
                    size = np.random.randint(10+level*2, 16+level*2)
                    nenemies = size 
                    posx, posy, rot, rotv, maph, mapc, exitx, exity, stepscount = gen_map(size)
                    nlevel = [np.random.randint(0,3), 
                              np.random.randint(0,4), 
                              np.random.randint(0,3), 
                              np.random.randint(0,2), 
                              np.random.randint(0,2), 
                              np.random.randint(0,5), 
                              ]

                nenemies = level**2 + 10 + level 
                sprites, spsize, gun, gunsp = get_sprites(nlevel[5])
                sky1, floor, wall, bwall, door, window = load_textures(nlevel)
                sky = pg.surfarray.array3d(pg.transform.smoothscale(sky1, (720, halfvres*4)))
                enemies = spawn_enemies(nenemies, maph, size, posx, posy, level/2)
                hearts2 = pg.Surface.subsurface(hearts,(0,0,player_health*10,20))
                exit2, damage_mod, blood_scale = 1, 1, 1
                mape, minimap = np.zeros((size, size)), np.zeros((size, size, 3))
                sounds['healthup'].play()

        else:
            timer = timer + er/2
            frame = new_frame(posx-0.2*np.cos(rot), posy-0.2*np.sin(rot), rot, frame, sky, floor, hres, halfvres,
                              mod, maph, size, wall, mapc, exitx, exity, nenemies, rotv, door, window, bwall, exit2)
            
            surf = pg.surfarray.make_surface(frame)

            mape = np.zeros((size, size))
            health = player_health
            enemies, player_health, mape = enemies_ai(posx, posy, enemies, maph, size, mape, gunsp, ticks, player_health, nenemies, level/3)
            enemies = sort_sprites(posx-0.2*np.cos(rot), posy-0.2*np.sin(rot), rot, enemies, maph, size, er/3)
            if exit2 == 0:
                surf = draw_colonel(surf, colonel, posx-0.2*np.cos(rot), posy-0.2*np.sin(rot), exitx+0.5, exity+0.5,
                                    hres, halfvres, rot, rotv, maph, size)
            surf, en = draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, gun, gunsp, rotv)
            
            if int(gunsp) > 0 and damage_mod < 1:
                blood_scale = blood_scale*(1 + 2*er)
                scaled_blood = pg.transform.scale(blood, 4*blood_scale*blood_size*hres/800)
                surf.blit(scaled_blood, np.asarray([hres/2, halfvres]) - 2*blood_scale*blood_size*hres/800)
            surf = pg.transform.scale2x(surf)
            surf = pg.transform.smoothscale(surf, (screen_width, screen_height))
            surf.blit(hearts2, (20,20))

            if exit2 == 0:
                minimap[int(posx)][int(posy)] = (50, 50, 255)
                surfmap = pg.surfarray.make_surface(minimap.astype('uint8'))
                surfmap = pg.transform.scale(surfmap, (size*5, size*5))
                surf.blit(surfmap,(20, 50), special_flags=pg.BLEND_ADD)
                minimap[int(posx)][int(posy)] = (100, 100, 0)

            surf.blit(font.render(str(round(timer,1)), 1, (255, 255, 255)), (20, 525))
            surf.blit(exits[exit2], (730,20))
            screen.blit(surf, (0,0))
            

            if health > player_health:
                hearts2 = pg.Surface.subsurface(hearts,(0,0,player_health*10,20))
                sounds['hurt'].play()

            if ticks - stepdelay > 2 and stepscount != posx + posy:
                sounds['step'].play()
                stepdelay = ticks
            stepscount = posx + posy
                
            if mape[int(posx)][int(posy)] > 0:
                delaycontrol = max(0.3, 2/np.random.uniform(0.99, mape[int(posx)][int(posy)]))
                if ticks - stepdelay2 > delaycontrol:
                    sounds['step2'].play()
                    stepdelay2 = ticks
            
            if int(gunsp) > 0:
                if gunsp == 1:
                    damage_mod = 1        
                    while enemies[en][3] < 10 and damage_mod > 0.4  and en >= 0:
                        x = posx -0.2*np.cos(rot) + np.cos(rot + np.random.uniform(0, 0.05))/enemies[en][3]
                        y = posy -0.2*np.sin(rot) + np.sin(rot + np.random.uniform(0, 0.05))/enemies[en][3]
                        z = 0.5 + np.sin(rotv*-0.392699)/enemies[en][3]
                        dist2en = np.sqrt((enemies[en][0]-x)**2 + (enemies[en][1]-y)**2)
                        if dist2en < 0.1 and z > 0 and z < 0.07*enemies[en][5]:
                            if z > 0.05*enemies[en][5]:
                                enemies[en][8] = enemies[en][8] - np.random.uniform(0,2)*2
                            else:
                                enemies[en][8] = enemies[en][8] - np.random.uniform(0,2)
                        
                            enemies[en][10] = ticks
                            x = enemies[en][0] + 0.1*np.cos(rot)
                            y = enemies[en][1] + 0.1*np.sin(rot)
                            if maph[int(x)][int(y)] == 0:
                                enemies[en][0]= (x + enemies[en][0])/2 
                                enemies[en][1]= (y + enemies[en][1])/2
                            if damage_mod == 1:
                                blood_scale = enemies[en][3]
                                sounds['swoosh'].play()
                                if enemies[en][4]:
                                    sounds['hitmonster2'].set_volume(min(1, enemies[en][3])*sfx_vol)
                                    sounds['hitmonster2'].play()
                                else:
                                    sounds['hitmonster'].set_volume(min(1, enemies[en][3])*sfx_vol)
                                    sounds['hitmonster'].play()
                            damage_mod = damage_mod*0.5
                            if enemies[en][8] < 0:
                                sounds['deadmonster'].set_volume(min(1, enemies[en][3])*sfx_vol)
                                sounds['deadmonster'].play()
                                nenemies = nenemies - 1
                                if nenemies == 0:
                                    exit2, msg = 0, "Find the master!"
#                               if np.random.uniform(0,1) < 0.3:
#                                 player_health = min(player_health+0.5, 20)
#                                    hearts2 = pg.Surface.subsurface(hearts,(0,0,player_health*10,20))
#                                    sounds['healthup'].play()                           
                        en = en - 1

                    if damage_mod == 1:
                        sounds['swoosh2'].play()                        
                gunsp = (gunsp + er*10)%4

            
            fps = int(clock.get_fps())
            pg.display.set_caption("Unreal Ends  FPS: " + str(fps)+ ' ' + msg)
            posx, posy, rot, rotv = movement(pg.key.get_pressed(), posx, posy, rot, maph, er, rotv)
#            
            
def movement(pressed_keys, posx, posy, rot, maph, et, rotv):
    x, y, diag = posx, posy, 0
    p_mouse = pg.mouse.get_rel()
    rot = rot + np.clip((p_mouse[0])/200, -0.2, .2)
    rotv = rotv + np.clip((p_mouse[1])/200, -0.2, .2)
    rotv = np.clip(rotv, -0.999, .999)

    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        x, y, diag = x + et*np.cos(rot), y + et*np.sin(rot), 1

    elif pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        x, y, diag = x - et*np.cos(rot), y - et*np.sin(rot), 1
        
    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        et = et/(diag+1)
        x, y = x + et*np.sin(rot), y - et*np.cos(rot)
        
    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        et = et/(diag+1)
        x, y = x - et*np.sin(rot), y + et*np.cos(rot)

    posx, posy = check_walls(posx, posy, maph, x, y)

    return posx, posy, rot, rotv

def gen_map(size):
    mapc = np.random.uniform(0,1, (size,size,3)) 
    maph = np.random.choice([0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4], (size,size))
    maph[0,:] = np.random.choice([1, 2, 3, 4], size)
    maph[size-1,:] = np.random.choice([1, 2, 3, 4], size)
    maph[:,0] = np.random.choice([1, 2, 3, 4], size)
    maph[:,size-1] = np.random.choice([1, 2, 3, 4], size)
    posx, posy = np.random.randint(1, size -2)+0.5, np.random.randint(1, size -2)+0.5
    rot, rotv, stepscount = np.pi/4, 0, posx + posy
    x, y = int(posx), int(posy)
    maph[x][y] = 0
    count = 0
    while True:
        testx, testy = (x, y)
        if np.random.uniform() > 0.5:
            testx = testx + np.random.choice([-1, 1])
        else:
            testy = testy + np.random.choice([-1, 1])
        if testx > 0 and testx < size -1 and testy > 0 and testy < size -1:
            if maph[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                maph[x][y] = 0
                dtx = np.sqrt((x-posx)**2 + (y-posy)**2)
                if (dtx > size*.6 and np.random.uniform() > .999) or np.random.uniform() > .99999:
                    exitx, exity = (x, y)
                    break
            else:
                count = count+1
    
    return posx, posy, rot, rotv, maph, mapc, exitx, exity, stepscount

def load_map(level):
    mapc = pg.surfarray.array3d(pg.image.load('Assets/Levels/map'+str(level)+'.png'))
    size = len(mapc)
    maph = np.random.choice([1, 2, 3, 4], (size,size))
    colors = np.asarray([[0,0,0], [255,255,255], [127,127,127]])
    posx, exitx = None, None
    for i in range(size):
        for j in range(size):
            color = mapc[i][j]
            if (color == colors[0]).all() or (color == colors[1]).all() or (color == colors[2]).all():
                maph[i][j] = 0
                if (color == colors[1]).all():
                    posx, posy = i+0.5, j+0.5
                if (color == colors[2]).all():
                    exitx, exity = i, j
                 
    while posx == None: 
        x, y = np.random.randint(1, size), np.random.randint(1, size)
        if (mapc[x][y] == colors[0]).all():
            posx, posy = x+0.5, y+0.5
            
    while exitx == None: 
        x, y = np.random.randint(1, size), np.random.randint(1, size)
        if (mapc[x][y] == colors[0]).all():
            exitx, exity = x, y
            
    rot, rotv, stepscount = np.pi/4, 0, posx + posy
    
    return posx, posy, rot, rotv, maph, mapc/255, exitx, exity, stepscount, size

@njit(cache=True)
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size, wall, mapc,
              exitx, exity, nenemies, rotv, door, window, bwall, exit2):
    offset = -int(halfvres*rotv)
    for i in range(hres):
        rot_i = rot + np.deg2rad(i/mod - 30)
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod - 30))
        frame[i][:] = sky[int(np.rad2deg(rot_i)*2%720)][halfvres-offset:3*halfvres-offset]

        n = 0
        n2 = 0
        x, y = posx +0.2*cos, posy +0.2*sin
        for j in range(2000):
            x, y = x +0.01*cos, y +0.01*sin
            if n == 0 and maph[int(x)%(size-1)][int(y)%(size-1)] != 0: 
                n = np.sqrt((x-posx)**2+(y-posy)**2)
            if maph[int(x)%(size-1)][int(y)%(size-1)] == 2:
                n2 = np.sqrt((x-posx)**2+(y-posy)**2)
                h = halfvres/(n2*cos2 + 0.001)
                break
        cwall = wall
        if n2 > 0.5 and 3*h > int(halfvres/(n*cos2 + 0.000001)):
            xx = int(x*3%1*99)
            xxx = x%1
            if x%1 < 0.01 or x%1 > 0.99:
                xx = int(y*3%1*99)
                xxx = y%1
            yy = np.linspace(0, 3, int(h*2))*99%99

            shade = 0.3 + 0.7*(h/halfvres)
            if shade > 1:
                shade = 1
                
            if maph[int(x-0.02)%(size-1)][int(y-0.02)%(size-1)] != 0:
                shade = shade*0.8
                
            c = shade*mapc[int(x)%(size-1)][int(y)%(size-1)]
            if n2 > 3.5:
                cwall = bwall
            for k in range(int(h)*2):
                c2 = c*cwall[xx][int(yy[k])]
                h1 = int(halfvres - int(h) +k +offset -2*h +3)
                h2 = int(halfvres+3*h-k+offset-1 +2*h - 6)
                if xxx > 1/3 and xxx < 2/3 and k > h*2/3 and k < h*4/3:
                    c2 = shade*window[xx][int(yy[k])]
                if h1 >= 0 and h1 < 2*halfvres:
                    frame[i][h1] = c2
                if h2 < halfvres*2:
                    frame[i][h2] = c2

        if n == 0:
            n = 1000
        x, y = posx +n*cos, posy +n*sin    
        walltype = maph[int(x)%(size-1)][int(y)%(size-1)]
        cwall = wall
        if n > 3.5:
            cwall = bwall
        h = int(halfvres/(n*cos2 + 0.000001))

        xx = int(x*3%1*99)
        xxx = x%1
        if x%1 < 0.01 or x%1 > 0.99:
            xx = int(y*3%1*99)
            xxx = y%1
        yy = np.linspace(0, 3, int(h*2))*99%99

        shade = 0.4 + 0.6*(h/halfvres)
        if shade > 1:
            shade = 1
            
        ash = 0 
        if maph[int(x-0.33)%(size-1)][int(y-0.33)%(size-1)] != 0:
            ash = 1
            
        if maph[int(x-0.01)%(size-1)][int(y-0.01)%(size-1)] != 0:
            shade, ash = shade*0.7, 0
            
        c = mapc[int(x)%(size-1)][int(y)%(size-1)]
        cdoor = np.sqrt(np.ones(3) - c)
        c = shade*c
        start_range, stop_range = 0, int(2*h)
        if h > halfvres+abs(offset):
            start_range = int(h - halfvres - offset)
            stop_range = int(h + halfvres - offset)
        for k in range(start_range, stop_range):
            c2 = c*cwall[xx][int(yy[k])]
            h1 = int(halfvres - h +k +offset)
            h2 = int(halfvres+3*h-k+offset-3)
            if xxx > 1/3 and xxx < 2/3 and k > h*2/3:
                if walltype < 3:
                    c2 = shade*cdoor*door[xx][int(yy[k])]
                elif k < h*4/3 and walltype == 3:
                    c2 = shade*window[xx][int(yy[k])]
            if h1 >= 0 and h1 < 2*halfvres:
                if ash and 1-k/(2*h) < 1-xx/99:
                    c2, c, ash = 0.7*c2, 0.7*c, 0
                frame[i][h1] = c2
            if h2 < halfvres*2:
                frame[i][h2] = c2
                
        for j in range(int(halfvres -h -offset)): 
            n = (halfvres/(halfvres-j - offset ))/cos2
            x, y = posx + cos*n, posy + sin*n
            xx, yy = int(x*3%1*99), int(y*3%1*99)

            shade = min(0.2 + 0.8/n, 1)
            if maph[int(x-0.33)%(size-1)][int(y-0.33)%(size-1)] != 0:
                shade = shade*0.7
            elif ((maph[int(x-0.33)%(size-1)][int(y)%(size-1)] and y%1>x%1)  or
                  (maph[int(x)%(size-1)][int(y-0.33)%(size-1)] and x%1>y%1)):
                shade = shade*0.7

            frame[i][halfvres*2-j-1] = shade*(floor[xx][yy]*2+frame[i][halfvres*2-j-1])/3
            
            if exit2 == 0 and int(x) == exitx and int(y) == exity and (x%1-0.5)**2 + (y%1-0.5)**2 < 0.2:
                ee = j/(20*halfvres)
                frame[i][j:2*halfvres-j] = (ee*np.ones(3)*255+frame[i][j:2*halfvres-j])/(1+ee)

    return frame

@njit(cache=True)
def vision(posx, posy, enx, eny, dist2p, maph, size):
    cos, sin = (posx-enx)/dist2p, (posy-eny)/dist2p
    x, y = enx, eny
    seen = 1
    x, y = x +0.25*cos, y +0.25*sin
    for i in range(abs(int((dist2p-0.5)/0.05))):
        x, y = x +0.05*cos, y +0.05*sin
        if (maph[int(x-0.02)%(size-1)][int(y-0.02)%(size-1)] or
            maph[int(x-0.02)%(size-1)][int(y+0.02)%(size-1)] or
            maph[int(x+0.02)%(size-1)][int(y-0.02)%(size-1)] or
            maph[int(x+0.02)%(size-1)][int(y+0.02)%(size-1)]):
            seen = 0
            break
    return seen

@njit(cache=True)
def enemies_ai(posx, posy, enemies, maph, size, mape, gunsp, ticks, player_health, nenemies, level=0):
    if nenemies < 5: 
        for en in range(len(enemies)): 
            if enemies[en][8] > 0:
                enx, eny =  enemies[en][0], enemies[en][1]
                dist2p = np.sqrt((enx-posx)**2 + (eny-posy)**2 + 1e-16)
                if dist2p > 10:
                    for i in range(10):
                        x, y = np.random.randint(1, size), np.random.randint(1, size)
                        dist2p = np.sqrt((x+0.5-posx)**2 + (y+0.5-posy)**2 + 1e-16)
                        if dist2p > 6 and dist2p < 8 and maph[x][y] == 0:
                            enemies[en][0], enemies[en][1] = x + 0.5, y + 0.5
                            break

    for en in range(len(enemies)): 
        if enemies[en][8] > 0:
            x, y = int(enemies[en][0]), int(enemies[en][1])
            mape[x-1:x+2, y-1:y+2] = mape[x-1:x+2, y-1:y+2] + 1

    for en in range(len(enemies)):
        if enemies[en][8] > 0 and np.random.uniform(0,1) < 0.1:         
            enx, eny, angle =  enemies[en][0], enemies[en][1], enemies[en][6]
            health, state, cooldown = enemies[en][8], enemies[en][9], enemies[en][10]
            dist2p = np.sqrt((enx-posx)**2 + (eny-posy)**2 + 1e-16)
            
            friends = mape[int(enx)][int(eny)] - 1
            if dist2p > 1.42: 
                friends = friends + mape[int(posx)][int(posy)]

            not_afraid = 0
            
            if  health > 1 + enemies[en][4] - level or health + friends > 3 + enemies[en][4] - level:
                not_afraid = 1
                
            if state == 0 and dist2p < 6:  
                angle = angle2p(enx, eny, posx, posy)
                angle2 = (enemies[en][6]-angle)%(2*np.pi)
                if angle2 > 11*np.pi/6 or angle2 < np.pi/6 or (gunsp >= 1 and dist2p < 3):
                    if vision(posx, posy, enx, eny, dist2p, maph, size):
                        if not_afraid and ticks - cooldown > 5:
                            state = 1 
                        elif dist2p < 2:
                            state = 2 
                            angle = angle - np.pi
                    else:
                        angle = enemies[en][6] 

            elif state == 1: 
                if dist2p < 0.8 and ticks - cooldown > 10: 
                    enemies[en][10] = ticks 
                    player_health = player_health - np.random.uniform(0.1, 1 + level/3)/np.sqrt(1+mape[int(posx)][int(posy)])
                    state = 2
                if not_afraid: 
                    angle = angle2p(enx, eny, posx, posy)
                else: 
                    state = 2
                    
            elif state == 2: 
                if not_afraid and ticks - cooldown > 5:
                    state = 0
                else:
                    angle = angle2p(posx, posy, enx, eny) + np.random.uniform(-0.5, 0.5) 

            enemies[en][6], enemies[en][9]  = angle+ np.random.uniform(-0.2, 0.2), state
            
    return enemies, player_health, mape

@njit(cache=True)
def check_walls(posx, posy, maph, x, y):
    if not(maph[int(x-0.2)][int(y)] or maph[int(x+0.2)][int(y)] or 
           maph[int(x)][int(y-0.2)] or maph[int(x)][int(y+0.2)]):
        posx, posy = x, y
        
    elif not(maph[int(posx-0.2)][int(y)] or maph[int(posx+0.2)][int(y)] or 
             maph[int(posx)][int(y-0.2)] or maph[int(posx)][int(y+0.2)]):
        posy = y
        
    elif not(maph[int(x-0.2)][int(posy)] or maph[int(x+0.2)][int(posy)] or 
             maph[int(x)][int(posy-0.2)] or maph[int(x)][int(posy+0.2)]):
        posx = x
        
    return posx, posy

@njit(cache=True)
def angle2p(posx, posy, enx, eny):
    angle = np.arctan((eny-posy)/(enx-posx+1e-16))
    if abs(posx+np.cos(angle)-enx) > abs(posx-enx):
        angle = (angle - np.pi)%(2*np.pi)
    return angle

@njit(cache=True)
def sort_sprites(posx, posy, rot, enemies, maph, size, er):
    for en in range(len(enemies)):
        enemies[en][3] = 9999
        if enemies[en][8] > 0: 
            enx, eny = enemies[en][0], enemies[en][1]
            backstep = 1
            if enemies[en][9] == 1 and enemies[en][3] > 1.7 and enemies[en][3] < 10:
                backstep = -1 
            speed = backstep*er*(2+enemies[en][9]/2)
            cos, sin = speed*np.cos(enemies[en][6]), speed*np.sin(enemies[en][6])
            x, y = enx+cos, eny+sin
            enx, eny = check_walls(enx, eny, maph, x, y)
            if enx == enemies[en][0] and eny == enemies[en][1]:
                x, y = enx-cos, eny-sin
                enx, eny = check_walls(enx, eny, maph, x, y)
                if enx == enemies[en][0] and eny == enemies[en][1]:
                    if maph[int(x)][int(y)] == 0:
                        enx, eny = x, y
            if enx == enemies[en][0] or eny == enemies[en][1]: 
                enemies[en][6] = enemies[en][6] + np.random.uniform(-0.5, 0.5)
                if np.random.uniform(0,1) < 0.01:
                    enemies[en][9] = 0
            enemies[en][0], enemies[en][1] = enx, eny
            
            angle = angle2p(posx, posy, enx, eny)
            angle2= (rot-angle)%(2*np.pi)
            if angle2 > 10.5*np.pi/6 or angle2 < 1.5*np.pi/6:
                dir2p = ((enemies[en][6] - angle -3*np.pi/4)%(2*np.pi))/(np.pi/2)
                dist2p = np.sqrt((enx-posx)**2+(eny-posy)**2+1e-16)
                enemies[en][2] = angle2
                enemies[en][7] = dir2p
                if vision(enx, eny, posx, posy, dist2p, maph, size):
                    enemies[en][3] = 1/dist2p

    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(number, maph, msize, posx, posy, level=0):
    enemies = []
    for i in range(number):
        x, y = np.random.randint(1, msize-2), np.random.randint(1, msize-2)
        while maph[x][y] or (x == int(posx) and y == int(posy)):
            x, y = np.random.randint(1, msize-2), np.random.randint(1, msize-2)
        x, y = x+0.5, y+0.5
        angle2p, invdist2p, dir2p = 0, 1, 0 
        entype = np.random.choice([0,1])
        direction = np.random.uniform(0, 2*np.pi) 
        size = np.random.uniform(7, 10)
        health = size/2 + level/3
        state = np.random.randint(0,3) 
        cooldown = 0 
 #                      
        enemies.append([x, y, angle2p, invdist2p, entype, size, direction, dir2p, health, state, cooldown])
    return np.asarray(enemies)

def get_sprites(level):
    sheet = pg.image.load('Assets/Sprites/spritesheet'+str(level)+'.png').convert_alpha()
    sprites = [[], []]
    gunsheet = pg.image.load('Assets/Sprites/gun1.png').convert_alpha() 
    gun = []
    for i in range(3):
        gun.append(pg.Surface.subsurface(gunsheet,(i*800,0,800,600)))
        xx = i*32
        sprites[0].append([])
        sprites[1].append([])
        for j in range(4):
            yy = j*100
            sprites[0][i].append(pg.Surface.subsurface(sheet,(xx,yy,32,100)))
            sprites[1][i].append(pg.Surface.subsurface(sheet,(xx+96,yy,32,100)))

    spsize = np.asarray(sprites[0][1][0].get_size())

    gun.append(gun[1]) 
    gunsp = 0 
    
    return sprites, spsize, gun, gunsp

def draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, gun, gunsp, rotv):
    
    offset = int(rotv*halfvres)
    cycle = int(ticks)%3 
    for en in range(len(enemies)):
        if enemies[en][3] >  10:
            break
        types, dir2p = int(enemies[en][4]), int(enemies[en][7])
        cos2 = np.cos(enemies[en][2])
        scale = min(enemies[en][3], 2)*spsize*enemies[en][5]/cos2*hres/800
        vert = halfvres + halfvres*min(enemies[en][3], 2)/cos2 - offset
        hor = hres/2 - hres*np.sin(enemies[en][2])
        if enemies[en][3] > 0.333:
            spsurf = pg.transform.scale(sprites[types][cycle][dir2p], scale)
        else:
            spsurf = pg.transform.smoothscale(sprites[types][cycle][dir2p], scale)
        surf.blit(spsurf, (hor,vert)-scale/2)

    gunpos = (np.sin(ticks)*10*hres/800,(np.cos(ticks)*10+15)*hres/800)
    spsurf = pg.transform.scale(gun[int(gunsp)], (hres, halfvres*2))
    surf.blit(spsurf, gunpos)

    return surf, en-1

def draw_colonel(surf, colonel, posx, posy, enx, eny, hres, halfvres, rot, rotv, maph, size):
    angle = angle2p(posx, posy, enx, eny)
    angle2= (rot-angle)%(2*np.pi)
    if angle2 > 10.5*np.pi/6 or angle2 < 1.5*np.pi/6:
        dist2p = np.sqrt((enx-posx)**2+(eny-posy)**2+1e-16)
        if vision(enx, eny, posx, posy, dist2p, maph, size):
            offset = int(rotv*halfvres)
            cos2 = np.cos(angle2)
            spsize = np.asarray(colonel.get_size())
            scale = min(1/dist2p, 2)*spsize*6/cos2*hres/800
            vert = halfvres + halfvres*min(1/dist2p, 2)/cos2 - offset
            hor = hres/2 - hres*np.sin(angle2)
            if dist2p < 3:
                spsurf = pg.transform.scale(colonel, scale)
            else:
                spsurf = pg.transform.smoothscale(colonel, scale)
            surf.blit(spsurf, (hor,vert)-scale/2)
    return surf

def load_sounds():
    sounds = {}
    sounds['step'] = pg.mixer.Sound('Assets/Sounds/playerstep.mp3')
    sounds['step2'] = pg.mixer.Sound('Assets/Sounds/enemystep.mp3')
    sounds['swoosh'] = pg.mixer.Sound('Assets/Sounds/gun.mp3')
    sounds['swoosh2'] = pg.mixer.Sound('Assets/Sounds/gun2.mp3')
    sounds['hurt'] = pg.mixer.Sound('Assets/Sounds/damage.mp3')
    sounds['deadmonster'] = pg.mixer.Sound('Assets/Sounds/deadmonster.mp3')
    sounds['hitmonster'] = pg.mixer.Sound('Assets/Sounds/hitmonster.mp3')
    sounds['hitmonster2'] = pg.mixer.Sound('Assets/Sounds/hitmonster2.mp3')
    sounds['healthup'] = pg.mixer.Sound('Assets/Sounds/healthup.wav')
    sounds['died'] = pg.mixer.Sound('Assets/Sounds/died.wav')
    sounds['won'] = pg.mixer.Sound('Assets/Sounds/won.wav')
    sounds['music0'] = pg.mixer.Sound('Assets/Sounds/battlemusic0.mp3')
    sounds['music1'] = pg.mixer.Sound('Assets/Sounds/battlemusic1.mp3')

    return sounds

def pause_menu(surf, menu, pause, options, click, running, m_vol, sfx_vol, sounds, newgame, font, msg, level, ticks, hres, story):
    adjust_res = 1
    p_mouse = pg.mouse.get_pos()
    if options == 0: 
        if p_mouse[0] < 600 and p_mouse[1] > 200 and p_mouse[1] < 265:
            pg.draw.rect(surf,(150,250,150),(0,200,600,65))
            if click:
                if newgame == 2:
                    newgame, story = 1, 1
                else:
                    pause = 0
                pg.mouse.set_pos(400,300)
        elif p_mouse[0] < 600 and p_mouse[1] > 300 and p_mouse[1] < 365: 
            pg.draw.rect(surf,(150,150,250),(0,300,600,65))
            if click:
                if newgame == 0:
                    newgame = 1
                else:
                    newgame, story = 1, 0
        elif p_mouse[0] < 600 and p_mouse[1] > 400 and p_mouse[1] < 465: 
            pg.draw.rect(surf,(150,150,150),(0,400,600,65))
            if click:
                options = 1
        elif p_mouse[0] < 600 and p_mouse[1] > 500 and p_mouse[1] < 565: 
            pg.draw.rect(surf,(250,150,150),(0,500,600,65))
            if click:
                if newgame == 0:
                    newgame = 2
                else:
                    running = 0
        elif p_mouse[0] > 679 and p_mouse[1] > 509:
            pg.draw.circle(surf,(250,150,150),(736,556), 42)
            if click:
                options = 2
        if newgame == 0:
            surf.blit(menu[3], (0,0))
        else:
            surf.blit(menu[0], (0,0))
        if newgame == 0:
            surf.blit(font.render(msg, 1, (255, 255, 255)), (30, 100+5*np.sin(ticks-1)))
            surf.blit(font.render(msg, 1, (30, 255, 155)), (32, 100+5*np.sin(ticks)))
            surf.blit(font.render(str(level), 1, (255, 255, 255)), (675, 275+5*np.sin(ticks-1)))
            surf.blit(font.render(str(level), 1, (255, 100, 50)), (677, 275+5*np.sin(ticks)))

    elif options == 1: # options menu
        if p_mouse[0] > 50 and  p_mouse[0] < 130 and p_mouse[1] > 220 and p_mouse[1] < 290: 
            pg.draw.rect(surf,(150,250,150),(60,220,70,70))
            if click:
                adjust_res = 0.9
        elif p_mouse[0] > 650 and  p_mouse[0] < 720 and p_mouse[1] > 220 and p_mouse[1] < 290: 
            pg.draw.rect(surf,(150,250,150),(650,220,70,70))
            if click:
                adjust_res = 1.1
        elif click and p_mouse[0] > 123 and  p_mouse[0] < 646 and p_mouse[1] > 360 and p_mouse[1] < 424:
            sfx_vol = (p_mouse[0] - 123)/523
            set_volume(m_vol, sfx_vol, sounds)
        elif click and p_mouse[0] > 123 and  p_mouse[0] < 646 and p_mouse[1] > 512 and p_mouse[1] < 566:
            m_vol = (p_mouse[0] - 123)/523
            set_volume(m_vol, sfx_vol, sounds)
            
        surf.blit(menu[options], (0,0))
        pg.draw.polygon(surf, (50, 200, 50), ((123, 414), (123+523*sfx_vol, 414-54*sfx_vol), (123+520*sfx_vol, 418)))
        pg.draw.polygon(surf, (50, 200, 50), ((123, 566), (123+523*m_vol, 566-54*m_vol), (123+520*m_vol, 570)))
        surf.blit(font.render(str(hres)+" x "+str(int(hres*0.75)), 1, (255, 255, 255)), (200, 220+5*np.sin(ticks-1)))
        surf.blit(font.render(str(hres)+" x "+str(int(hres*0.75)), 1, (255, 100, 50)), (202, 220+5*np.sin(ticks)))

    elif options == 2: 
        surf.blit(menu[options], (0,0))
        
    if options > 0 and p_mouse[0] > 729 and p_mouse[1] < 60 :
        pg.draw.circle(surf,(0,0,0),(768,31), 30)
        if click:
            options = 0
        surf.blit(menu[options], (0,0))
                
    
    pg.draw.polygon(surf, (50, 50, 50), ((p_mouse), (p_mouse[0]+20, p_mouse[1]+22), (p_mouse[0], p_mouse[1]+30)))
    
    return surf, pause, options, running, newgame, adjust_res, m_vol, sfx_vol, story

def adjust_resolution(hres=250):
    hres = max(min(hres, 800), 80) 
    halfvres = int(hres*0.375) 
    mod = hres/60 
    frame = np.random.randint(0,255, (hres, halfvres*2, 3))
    
    return hres, halfvres, mod, frame

def set_volume(m_vol, sfx_vol, sounds):
    for key in sounds.keys():
        sounds[key].set_volume(sfx_vol)
    sounds['music0'].set_volume(m_vol)
    sounds['music1'].set_volume(m_vol)

def splash_screen(msg, splash, clock, font, screen):
    running = 1
    clickdelay = 0
    while running:
        clickdelay += 1
        clock.tick(60)
        surf = splash.copy()
        ticks = pg.time.get_ticks()/200
        surf.blit(font.render(msg, 1, (0, 0, 0)), (50, 450+5*np.sin(ticks-1)))
        surf.blit(font.render(msg, 1, (255, 255, 255)), (52, 450+5*np.sin(ticks)))

        p_mouse = pg.mouse.get_pos()
        pg.draw.polygon(surf, (50, 50, 50), ((p_mouse), (p_mouse[0]+20, p_mouse[1]+22), (p_mouse[0], p_mouse[1]+30)))

        screen.blit(surf, (0,0))
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN and clickdelay > 50:
                return
            elif event.type == pg.QUIT:
                pg.quit()
        if clickdelay == 180:
            msg = "Press any key..."

def load_textures(textures):
    sky1 = pg.image.load('Assets/Textures/sky/sky'+str(textures[0])+'.png')
    floor = pg.surfarray.array3d(pg.image.load('Assets/Textures/floor/floor'+str(textures[1])+'.jpg'))
    wall = pg.surfarray.array3d(pg.image.load('Assets/Textures/wall/wall'+str(textures[2])+'.jpg'))
    bwall = pg.transform.smoothscale(pg.image.load('Assets/Textures/wall/wall'+str(textures[2])+'.jpg'), (25,25))
    bwall = pg.surfarray.array3d(pg.transform.smoothscale(bwall, (100,100)))
    door = pg.surfarray.array3d(pg.image.load('Assets/Textures/wall/door'+str(textures[3])+'.jpg'))
    window = pg.surfarray.array3d(pg.image.load('Assets/Textures/wall/window'+str(textures[4])+'.jpg'))
    
    if textures[0]%3 > 0:
        floor = (floor*(1-0.2*textures[0]%3)).astype(int)
        wall = (wall*(1-0.2*textures[0]%3)).astype(int)
        bwall = (bwall*(1-0.2*textures[0]%3)).astype(int)
        door = (door*(1-0.2*textures[0]%3)).astype(int)
        window = (window*(1-0.2*textures[0]%3)).astype(int)

    return sky1, floor, wall, bwall, door, window
    

if __name__ == '__main__':
    main()
    pg.mixer.fadeout(1000)
    pg.time.wait(1000)
    pg.quit()
