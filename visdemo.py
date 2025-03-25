#####################################################
#                                                   #
#   Vistoole demo - AsTeR - tech@asterlab.pl        #
#   Paweł Dorobek                                   #
#                                                   #
#   last edit. 01.2024                              #
#                                                   #
#   python     - 3.8.10                             #
#   matplotlib - 3.7.4                              #
#                                                   #
#####################################################


################################################################################
####################                      ######################################
####################   Example of use     ######################################


import sys
import pandas as pd
import numpy as np
import vistoole as vs
from shapes import Annulus, Ellipse, Circle, Wedge, Rectangle, Polygon
import matplotlib.pyplot as plt
import matplotlib.patches as patches

    
###############################################################################
######                                                                   ######
######                fig, ax  should be obtained first                  ######

fig, ax = plt.subplots(num='Main')


####################   CheckButton example             ########################

boxy1 = pd.DataFrame(
    columns=
    [ 'present', 'active', 'xor', 'name',       'label'            ],
    data= [
    [ 1,         0,        1,     'rms_bx',     'RMS'              ],
    [ 1,         0,        1,     'std_bx',     'r\u2009m\u2009s≈' ],
    [ 1,         0,        1,     'mean_bx',    'mean'             ],
    [ 1,         0,        0,     'integr_bx',  'integr'           ],
    [ 1,         0,        0,     'lin_fit_bx', 'lin-fit'          ],
    [ 1,         0,        2,     'pik_pik_bx', 'pik-pik'          ],
    [ 1,         0,        2,     'tik_tik_bx', 'tik-tik'          ],
    [ 1,         0,        0,     'fft_db_bx',  'fft-dB'           ],
    [ 1,         0,        0,     'histN_bx',   'histN'            ],
    [ 0,         0,        0,     'histR_bx',   'histR'            ],
    ])


cbox1 = vs.CBoxy_mpl(boxy1, [0.89, 0.175, 0.10, 0.28],
                     fig=fig,
                     ax=ax,    # not necessary - see CBoxy_mpl definition
                     cid='cb',
                     box_props=dict(facecolor='papayawhip', picker=True),
                     frame_props=dict(facecolor='papayawhip'),
                     check_props=dict(facecolor='black'))


# second box after choosing tik-tik from the first one
boxy_level = pd.DataFrame(
    columns=
    [ 'present', 'active', 'xor', 'name',     'label'   ],
    data= [
    [ 1,         1,        1,     'y2x',      'Y -> X'  ],
    [ 1,         0,        1,     'x2y',      'X -> Y'  ],
    [ 0,         0,        2,     'Level_21', 'Lv 2 - ʃ'],
    [ 0,         1,        2,     'Level_20', 'Lv 2 - ʅ'],
    ])


lvbox = vs.CBoxy_mpl(boxy_level, [0.775, 0.175, 0.10, 0.10],
                  fig=fig, cid='lv', enabled=False,  
                  box_props=dict(facecolor='beige', picker=True),
                  frame_props=dict(facecolor='beige'),
                  check_props=dict(facecolor='black'))


def x2y_func():
    if lvbox.x2y:
        cYY.visible = True

lvbox.set_addfunc(x2y_func)

def ixy_on_off():
    if cbox1.tik_tik_bx:
        lvbox.enable = True
        lvbox.set_visible(True)
        if not(lvbox.x2y or lvbox.y2x):
            lvbox.set('y2x')
        if lvbox.x2y:
            cYY.visible = True
    else:
        lvbox.set_visible(False)
        lvbox.enable = False
    fig.canvas.draw_idle()

cbox1.set_addfunc(ixy_on_off)

###################   CheckButtons  example end   ####################



###################  interactive legend example   ####################

    
def add_leg_event(item):
    ax_line_x = legV.artists[item][0].get_xdata()
    ax_line_y = ax_line = legV.artists[item][0].get_ydata()
    x1 = min(cXX.c1.x, cXX.c2.x)
    x2 = max(cXX.c1.x, cXX.c2.x)
    s1 = ax_line_x[0]
    s2 = ax_line_x[-1]
    idx1 = 0
    idx2 = 0
    calc_values = True
    xs, xe = ax.get_xlim()
    
    if s1 > xe or s2 < xs:   # out of plot window
        calc_values = False

    """
    curr in plot window and at least one end of signal hooks to the curr window

    """
    if cXX.in_win and s1 < x2 and s2 > x1:    
        idx1 = np.nonzero(ax_line_x >= x1)[0][0]
        idx2 = np.nonzero(ax_line_x <= x2)[0][-1]            
    elif calc_values:                                # out of curr window
        cXX.visible = False
        idx1 = np.nonzero(ax_line_x >= xs)[0][0]
        idx2 = np.nonzero(ax_line_x <= xe)[0][-1]
    if calc_values:
        if idx1 == idx2:
            ax_line = ax_line_y[idx1]
        else:           
            ax_line = ax_line_y[idx1:idx2]

    if cbox1.pik_pik_bx:
        if calc_values:
            cYY.c1.y = max(ax_line)
            cYY.c2.y = min(ax_line)
        else:
            cYY.c1.y = 0
            cYY.c2.y = 0
        cYY.update_osc()
        cYY.visible = True
            

############################  flying content example  #############################
        
c_fig = 'red'
c_ax = 'blue'
c_data = 'darkgreen'

b_fig = dict(fc='white', edgecolor=c_fig)
b_ax = dict(fc='white', edgecolor=c_ax)
b_data = dict(fc='white', edgecolor=c_data)

txt1 = fig.text(0.25,0.75, 'Filter output',
                color=c_fig, fontsize=12, fontweight='bold', bbox=b_fig,
                rotation=35)


txt4 = ax.text(0.01, 0.8, 'Choose\nvalues\nto calculate', clip_on=True,
                rotation=-30, fontsize=12, fontweight='bold', c=c_data, bbox=b_data,
                transform_rotates_text=True) # False = keeps displey angle

txt5 = ax.text(0.8, 0.8, 'This is\npik value\nof frequency',
                rotation=30, fontsize=12, fontweight='bold', c=c_ax,
                horizontalalignment='center', clip_on=True,
                verticalalignment='top', transform_rotates_text=True,
                transform=ax.transAxes)


exar = [txt1, txt4, txt5]

elli = Ellipse((2.2, 2.5), 0.1, 1, color=c_data, alpha=0.7, clip_on=False,
                   gid='elli')
                   #transform=ax.transAxes)

elli3 = Annulus((0.05, 0.5), (0.05, 0.5), 0.02, angle=0, color=c_ax, alpha=0.7,
                gid='elli3',
                transform=ax.transAxes)
    
elli4 = Ellipse((0.05, 0.3), 0.1, 0.07, color=c_ax, alpha=0.7, gid='elli4',
                transform=ax.transAxes)
                    

exar += [elli, elli3, elli4]
    
cir1 = ax.add_artist(elli)
cir3 = ax.add_artist(elli3)
cir4 = ax.add_artist(elli4)

rec1 = Rectangle((0.4, 0.4), 0.1, 0.1, color=c_ax, alpha=0.7, gid='rec1',
                     transform=ax.transAxes)
ax.add_artist(rec1)
    

rec2 = Rectangle((0.1, 0.5), 0.2, 1, color=c_data, alpha=0.7, gid='rec2')
ax.add_artist(rec2)

exar += [rec1, rec2]

poly = [[0.2, 0.4], [0.3, 0.3], [0.25, 0.42]]
    
tri1 = Polygon(poly, color=c_ax, alpha=0.7, clip_on=False,
               gid='tri1', angle=45,
               transform=ax.transAxes)
        
ax.add_patch(tri1)

wed1 = Wedge((0.7, 0.2), 0.1, -135, 135, width=0.05, color=c_ax, alpha=0.7,
            gid='wed1',
            transform=ax.transAxes)
ax.add_patch(wed1)

exar += [tri1, wed1]
    


##########################################################
##########################################################
######                                             #######
######       standard matplotlib plot code         #######
            

fig.subplots_adjust(left=0.08, right=0.88, bottom=0.17) 
fig.set_figwidth(8) # inches
fig.set_figheight(6)
    
np.random.seed(19850531)

dt = 0.01
t = np.arange(0, 4, dt)
nse1 = np.random.randn(len(t))                 
nse2 = np.random.randn(len(t))

p1 = np.sin(2 * np.pi * 0.5 * t) * 1.5
p2 = np.sin(2 * np.pi * 0.5 * t + np.pi/3)

s1 = p1 + nse1
s2 = p2 + nse2
s3 = p1
s4 = p2

ax.plot(t, s1, label='s1')
ax.plot(t, s2, label='s2')
ax.plot(t, s3, label='s3')
ax.plot(t, s4, label='s4')

ax.set_xlim(0, 4)
ax.set_ylim(-5, 5)
ax.grid(True)
    
x_label = ax.set_xlabel('Frequency [Hz]')
y_label = ax.set_ylabel('|H[jw]|')
ax_title = ax.set_title('Matplotlib plot quick cleanup example')
                          # 'An interactive pure Matplotlib plot example'
exar += [ax_title, x_label, y_label]
                          
##################################################################################
#############                                                    #################
#############        VisToole module adds only one line of code  #################
    
"""
This almost one line adds oscilloscope-like data inspection

There are many options in this arg --       --  extra movable content 
see in Vistoole func definition     |       |   must be placed in 'exar' list
                                   \|/     \|/
"""                                
cXX, cYY, cBB, legV = vs.Vistoole('xylegexar', exar=exar,
                                   fig=fig, ax=ax, leg_addfunc=add_leg_event)
# position or label name
legV.set_focus(2, 's4')

#####################                                         #####################    
#####################  just before plt.show()  instruction    #####################

plt.show(block="idlelib" not in sys.modules)
