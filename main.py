"""
 █░█ █▄░█ █▀█ █▀▀ ▄▀█ █░░  █▀▀ █▄░█ █▀▄ ▀ █▀
 █▄█ █░▀█ █▀▄ ██▄ █▀█ █▄▄  ██▄ █░▀█ █▄▀ ░ ▄█
 version: 1.12
 """

import pygame as pg
import numpy as np
from numba import njit
import mysql.connector as msc
from sys import exit

def credits():
    f= open("credits.txt","w")
    tex="""
 __ __                 _    _____       _     
|  |  |___ ___ ___  __| |  |   __|___ _| |___ 
|  |  |   |  _| -_||. | |  |   __|   | . |_ -|
|_____|_|_|_| |___|___|_|  |_____|_|_|___|___|
                                version 1.12
    ---------------------
    Computer Science Project
    Vyasa Vidya Peethom
    .______________.
    |Group Members |
    .______________.
    |Adhityadev t.s|
    |Gaurav Krishn |
    |Pranav S      |
    .______________|

    """
    s=f.write(tex)
    print(s)

def main():
    pg.init()
    screen_width = 1364
    screen_height = 735
    screen = pg.display.set_mode((screen_width,screen_height))
    running = True
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)

    hres = 250 
    halfvres = int(hres*0.375) 
    mod = hres/60 

    size = 25
    nenemies = size*2 
    posx, posy, rot, maph, mapc, exitx, exity = gen_map(size)
    player_health = 10
    rotv = 0
    
    frame = np.random.uniform(0,1, (hres, halfvres*2, 3))
    sky = pg.image.load('assets/textures/bg/sky1.png')
    sky = pg.surfarray.array3d(pg.transform.smoothscale(sky, (720, halfvres*4)))/255
    floor = pg.surfarray.array3d(pg.image.load('assets/textures/floor.png'))/255
    wall = pg.surfarray.array3d(pg.image.load('assets/textures/wall.jpg'))/255
    sprites, spsize, gun, gunsp = get_sprites(hres)
    
    enemies = spawn_enemies(nenemies, maph, size)
    while running:
        ticks = pg.time.get_ticks()/200
        er = min(clock.tick()/500, 0.3)
        if player_health < 0:
            credits()
            print("hahah noob")
            running = False
        if nenemies < size and int(posx) == exitx and int(posy) == exity:
            print("pffffffffftttttttt")
            pg.time.wait(1000)
            running = False
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            if gunsp < 1 and event.type == pg.MOUSEBUTTONDOWN:
                gunsp = 1
                
        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size,
                          wall, mapc, exitx, exity, nenemies, rotv)
        surf = pg.surfarray.make_surface(frame*255)

        mape = np.zeros((size, size))
        enemies, player_health = enemies_ai(posx, posy, enemies, maph, size, mape, gunsp,
                                            ticks, player_health)
        enemies = sort_sprites(posx, posy, rot, enemies, maph, size, er/3)
        
        surf, en = draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, gun,
                                gunsp, rotv)

        surf = pg.transform.scale(surf, (screen_width, screen_height))
        
        if int(gunsp) > 0:
            if gunsp == 1:
                while enemies[en][3] > 1.25 and enemies[en][3] < 10:
                    enemies[en][8] = enemies[en][8] - np.random.uniform(1,4)
                    x = enemies[en][0] + 0.3*np.cos(rot)
                    y = enemies[en][1] + 0.3*np.sin(rot)
                    if maph[int(x)][int(y)] == 0:
                        enemies[en][0]= (x + enemies[en][0])/2 
                        enemies[en][1]= (y + enemies[en][1])/2
                    if enemies[en][8] < 0:
                        enemies[en][0] = 0
                        nenemies = nenemies - 1
                        if np.random.uniform(0,1) < 0.05:
                            player_health = min(player_health+0.5, 10)
                    en = en - 1
            gunsp = (gunsp + er*5)%4

        screen.blit(surf, (0,0))
        pg.display.update()
        fps = int(clock.get_fps())
        pg.display.set_caption("Unreal End's [Health: "+str(player_health)+" Enemies: " + str(nenemies) + " FPS: " + str(fps))
        posx, posy, rot, rotv = movement(pg.key.get_pressed(), posx, posy, rot, maph, er, rotv)



def movement(pressed_keys, posx, posy, rot, maph, et, rotv):
    x, y, rot0, diag = posx, posy, rot, 0
    if pg.mouse.get_focused():
        p_mouse = pg.mouse.get_rel()
        rot = rot + np.clip((p_mouse[0])/200, -0.2, .2)
        rotv = rotv + np.clip((p_mouse[1])/200, -0.2, .2)
        rotv = np.clip(rotv, -1, 1)

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
    maph = np.random.choice([0, 0, 0, 0, 1, 2], (size,size))
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1)
    posx, posy = np.random.randint(1, size -2)+0.5, np.random.randint(1, size -2)+0.5
    rot = np.pi/4
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
    return posx, posy, rot, maph, mapc, exitx, exity

@njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size, wall, mapc,
              exitx, exity, nenemies, rotv):
    offset = -int(halfvres*rotv)
    for i in range(hres):
        rot_i = rot + np.deg2rad(i/mod - 30)
        sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod - 30))
        frame[i][:] = sky[int(np.rad2deg(rot_i)*2%718)][halfvres-offset:3*halfvres-offset]

        x, y = posx, posy
        while maph[int(x)%(size-1)][int(y)%(size-1)] == 0:
            x, y = x +0.01*cos, y +0.01*sin

        n = np.sqrt((x-posx)**2+(y-posy)**2)
        h = int(halfvres/(n*cos2 + 0.001))

        xx = int(x*3%1*99)        
        if x%1 < 0.02 or x%1 > 0.98:
            xx = int(y*3%1*99)
        yy = np.linspace(0, 3, h*2)*99%99

        shade = 0.3 + 0.7*(h/halfvres)
        if shade > 1:
            shade = 1
            
        ash = 0 
        if maph[int(x-0.33)%(size-1)][int(y-0.33)%(size-1)] != 0:
            ash = 1
            
        if maph[int(x-0.01)%(size-1)][int(y-0.01)%(size-1)] != 0:
            shade, ash = shade*0.6, 0
            
        c = shade*mapc[int(x)%(size-1)][int(y)%(size-1)]
        for k in range(h*2):
            if halfvres - h +k +offset >= 0 and halfvres - h +k +offset < 2*halfvres:
                if ash and 1-k/(2*h) < 1-xx/99:
                    c, ash = 0.6*c, 0
                frame[i][halfvres - h +k+offset ] = c*wall[xx][int(yy[k])]
            if halfvres+3*h-k+offset-1  < halfvres*2:
                frame[i][halfvres+3*h-k+offset-1 ] = c*wall[xx][int(yy[k])]
                
        for j in range(halfvres -h -offset ): 
            n = (halfvres/(halfvres-j - offset ))/cos2
            x, y = posx + cos*n, posy + sin*n
            xx, yy = int(x*3%1*99), int(y*3%1*99)

            shade = min(0.2 + 0.8/n, 1)
            if maph[int(x-0.33)%(size-1)][int(y-0.33)%(size-1)] != 0:
                shade = shade*0.6
            elif ((maph[int(x-0.33)%(size-1)][int(y)%(size-1)] and y%1>x%1)  or
                  (maph[int(x)%(size-1)][int(y-0.33)%(size-1)] and x%1>y%1)):
                shade = shade*0.6

            frame[i][halfvres*2-j-1] = shade*(floor[xx][yy]*2+frame[i][halfvres*2-j-1])/3
            
            if nenemies < size and int(x) == exitx and int(y) == exity and (x%1-0.5)**2 + (y%1-0.5)**2 < 0.2:
                ee = j/(10*halfvres)
                frame[i][j:2*halfvres-j] = (ee*np.ones(3)+frame[i][j:2*halfvres-j])/(1+ee)

    return frame

@njit()
def vision(posx, posy, enx, eny, dist2p, maph, size):
    cos, sin = (posx-enx)/dist2p, (posy-eny)/dist2p
    x, y = enx, eny
    seen = 1
    for i in range(int(dist2p/0.05)):
        x, y = x +0.05*cos, y +0.05*sin
        if (maph[int(x-0.02)%(size-1)][int(y-0.02)%(size-1)] or
            maph[int(x-0.02)%(size-1)][int(y+0.02)%(size-1)] or
            maph[int(x+0.02)%(size-1)][int(y-0.02)%(size-1)] or
            maph[int(x+0.02)%(size-1)][int(y+0.02)%(size-1)]):
            seen = 0
            break
    return seen

@njit()
def enemies_ai(posx, posy, enemies, maph, size, mape, gunsp, ticks, player_health):
    for en in range(len(enemies)): 
        if enemies[en][8] > 0:
            x, y = int(enemies[en][0]), int(enemies[en][1])
            mape[x-1:x+2, y-1:y+2] = mape[x-1:x+2, y-1:y+2] + 1

    for en in range(len(enemies)):
        if enemies[en][8] > 0 and np.random.uniform(0,1) < 0.1:          
            enx, eny, angle =  enemies[en][0], enemies[en][1], enemies[en][6]
            health, state, cooldown = enemies[en][8], enemies[en][9], enemies[en][10]
            dist2p = np.sqrt((enx-posx)**2+(eny-posy)**2+1e-16)
            
            friends = mape[int(enx)][int(eny)] - 1
            if dist2p > 1.42: 
                friends = friends + mape[int(posx)][int(posy)]

            not_afraid = 0
            
            if  health > 1 + enemies[en][4] or health + friends > 3 + enemies[en][4]:
                not_afraid = 1
                
            if state == 0 and dist2p < 6: 
                angle = angle2p(enx, eny, posx, posy)
                angle2 = (enemies[en][6]-angle)%(2*np.pi)
                if angle2 > 11*np.pi/6 or angle2 < np.pi/6 or (gunsp >= 1 and dist2p < 3): 
                    if vision(posx, posy, enx, eny, dist2p, maph, size):
                        if not_afraid:
                            state = 1 
                        else:
                            state = 2 
                            angle = angle - np.pi
                    else:
                        angle = enemies[en][6] 

            elif state == 1: 
                if dist2p < 0.6 and ticks - cooldown > 10: 
                    enemies[en][10] = ticks 
                    player_health = player_health - np.random.uniform(0,1)/np.sqrt(1+mape[int(posx)][int(posy)])
                if not_afraid: 
                    angle = angle2p(enx, eny, posx, posy)
                else: 
                    state = 2
                    
            elif state == 2: 
                if not_afraid:
                    state = 0
                else:
                    angle = angle2p(posx, posy, enx, eny) + np.random.uniform(-0.5, 0.5) 

            enemies[en][6], enemies[en][9]  = angle+ np.random.uniform(-0.2, 0.2), state
            
    return enemies, player_health

@njit()
def check_walls(posx, posy, maph, x, y): 
    if not(maph[int(x-0.1)][int(y)] or maph[int(x+0.1)][int(y)] or 
           maph[int(x)][int(y-0.1)] or maph[int(x)][int(y+0.1)]):
        posx, posy = x, y
        
    elif not(maph[int(posx-0.1)][int(y)] or maph[int(posx+0.1)][int(y)] or 
             maph[int(posx)][int(y-0.1)] or maph[int(posx)][int(y+0.1)]):
        posy = y
        
    elif not(maph[int(x-0.1)][int(posy)] or maph[int(x+0.1)][int(posy)] or 
             maph[int(x)][int(posy-0.1)] or maph[int(x)][int(posy+0.1)]):
        posx = x
        
    return posx, posy

@njit()
def angle2p(posx, posy, enx, eny):
    angle = np.arctan((eny-posy)/(enx-posx))
    if abs(posx+np.cos(angle)-enx) > abs(posx-enx):
        angle = (angle - np.pi)%(2*np.pi)
    return angle

@njit()
def sort_sprites(posx, posy, rot, enemies, maph, size, er):
    for en in range(len(enemies)):
        enemies[en][3] = 9999
        if enemies[en][8] > 0:
            enx, eny = enemies[en][0], enemies[en][1]
            speed = er*(1+enemies[en][9]/2)
            cos, sin = speed*np.cos(enemies[en][6]), speed*np.sin(enemies[en][6])
            x, y = enx+cos, eny+sin
            enx, eny = check_walls(enx, eny, maph, x, y)
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
                if vision(posx, posy, enx, eny, dist2p, maph, size):
                    enemies[en][3] = 1/dist2p

    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(number, maph, msize):
    enemies = []
    for i in range(number):
        x, y = np.random.uniform(1, msize-2), np.random.uniform(1, msize-2)
        while (maph[int(x-0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               maph[int(x-0.1)%(msize-1)][int(y+0.1)%(msize-1)] or
               maph[int(x+0.1)%(msize-1)][int(y-0.1)%(msize-1)] or
               maph[int(x+0.1)%(msize-1)][int(y+0.1)%(msize-1)]):
            x, y = np.random.uniform(1, msize-1), np.random.uniform(1, msize-1)
        angle2p, invdist2p, dir2p = 0, 0, 0 
        entype = np.random.choice([0,1])
        direction = np.random.uniform(0, 2*np.pi)
        size = np.random.uniform(7, 10)
        health = size/2
        state = 0 
        cooldown = 0 
        enemies.append([x, y, angle2p, invdist2p, entype, size, direction, dir2p, health, state, cooldown])
#                       
    return np.asarray(enemies)

def get_sprites(hres):
    sheet = pg.image.load('assets/entity/spritesheet.png').convert_alpha()
    sprites = [[], []]
    gunsheet = pg.image.load('assets/weapons/gun.png').convert_alpha() 
    gun = []
    for i in range(3):
        subgun = pg.Surface.subsurface(gunsheet,(i*800,0,800,600))
        gun.append(pg.transform.smoothscale(subgun, (hres, int(hres*0.75))))
        xx = i*32
        sprites[0].append([])
        sprites[1].append([])
        for j in range(4):
            yy = j*100
            sprites[0][i].append(pg.Surface.subsurface(sheet,(xx,yy,32,100)))
            sprites[1][i].append(pg.Surface.subsurface(sheet,(xx+96,yy,32,100)))

    spsize = np.asarray(sprites[0][1][0].get_size())*hres/800

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
        scale = min(enemies[en][3], 2)*spsize*enemies[en][5]/cos2
        vert = halfvres + halfvres*min(enemies[en][3], 2)/cos2 - offset
        hor = hres/2 - hres*np.sin(enemies[en][2])
        spsurf = pg.transform.scale(sprites[types][cycle][dir2p], scale)
        surf.blit(spsurf, (hor,vert)-scale/2)

    gunpos = (np.sin(ticks)*10*hres/800,(np.cos(ticks)*10+15)*hres/800) 
    surf.blit(gun[int(gunsp)], gunpos)

    return surf, en-1

if __name__ == '__main__':
    main()
    pg.quit()
