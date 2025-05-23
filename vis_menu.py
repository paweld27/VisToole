#####################################################
#                                                   #
#   VisToole - AsTeR - tech@asterlab.pl             #
#   Paweł Dorobek                                   #
#                                                   #
#   ver. 0.900      - 01.2024                       #
#                                                   #
#   python      - 3.8.10                            #
#   matplotlib  - 3.7.4                             #
#   PySimpleGUI - 4.60.5                            #
#                                                   #
#####################################################



import PySimpleGUI as sg
from tkinter import colorchooser
import matplotlib as mpl
from matplotlib.artist import Artist
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from shapes import Ellipse, Annulus, Circle, Wedge, Rectangle, Polygon, FancyArrow
from shapes import PointPatch as pp


sg.theme('Default1')
sg_bgcolor = 'lightgrey'

sg.PySimpleGUI.TOOLTIP_BACKGROUND_COLOR = "#FAD7A0"
sg.PySimpleGUI.TOOLTIP_FONT = ("Helvetica", 11)
sg.PySimpleGUI.DEFAULT_TOOLTIP_TIME = 500
sg.PySimpleGUI.DEFAULT_TOOLTIP_OFFSET = (10, 20)  #  (0, -20)

deb_box_color = '#ff00ff'
deb_box_lw = 2


#sg_cpr_text = 'made by PySimpleGUI 4.60.05'
#sg_cpr_text = 'made by free open source software'+'\n'+\
#              '          PySimpleGUI 4.60.05'

sg_cpr_text = ""


def str2dig(s):
    try:
        val = eval(str(s).replace(',', '.').lstrip('0'))
    except:
        val = 0
    return val
    

def hex2rgba(c, alpha=None):
    # alredy in Matplotlib ver. >= 3.8
    # and can be replace by mpl.colors.to_rgba
    return tuple(int(n, 16) / 255
                 for n in [c[1:3], c[3:5], c[5:7]]) \
                 + (alpha if alpha is not None else 1.,)

def hex2rgb(c):
    return hex2rgba(c)[0:3]


def rgba2rgb(rgba, background=(1, 1, 1)):
    """
    This function mixes color's tuple (r, g, b, a)

    with alpha according equations below.
    Default background=(1, 1, 1) is sufficient for almost all
    backgrounds. Even dark.
    One can get background colors using:
    # for fine dark theme:
    >>> ax.get_facecolor()
    (0.12549019607843137, 0.14901960784313725, 0.16862745098039217, 1.0)
    >>> fig.patch.get_facecolor()
    (0.08235294117647059, 0.09803921568627451, 0.10980392156862745, 1.0)
    # or for white theme - Vistoole example:
    >>> ax.get_facecolor()
    (1.0, 1.0, 1.0, 1.0)
    >>> fig.patch.get_facecolor()
    (1.0, 1.0, 1.0, 1.0)
    >>> 
    """
    if len(rgba) == 3:
        return rgba

    R, G, B = background[:3] # drop alpha here. All matplotlib get_color
    r, g, b, a = rgba        # functions don't mix alpha with r,g,b, values
                             # see above

    return (r * a + (1.0 - a) * R,
            g * a + (1.0 - a) * G,
            b * a + (1.0 - a) * B)


def get_domain(artist):

    axes = artist.axes
    if axes != None:
        if Artist.get_transform(artist) == axes.transAxes:
            domain = 'Axes'
        else:
            domain = 'Data'
    else:
        domain = 'Figure'

    return domain


class Deb_box:
    
    def __init__(self, artist):
        self.fig = artist.get_figure()
        self.axes = artist.axes
        self.domain = get_domain(artist)

        if hasattr(artist, 'get_text'):
            patch = artist.get_bbox_patch()
            if patch == None:
                patch = artist
        else:
            patch = artist

        if self.domain == 'Figure':
            deb_bbox = patch.get_window_extent()
            transform = None
        else:
            deb_bbox = patch.get_window_extent().transformed(self.axes.transAxes.inverted())
            transform = self.axes.transAxes
        
        deb_bbox = deb_bbox.expanded(1.2, 1.2)
        self.deb_rect = Rectangle(xy=deb_bbox.p0, width=deb_bbox.width,
                                  height=deb_bbox.height, transform=transform,
                                  ls='--', lw=deb_box_lw, zorder=8, 
                                  ec=deb_box_color, fill=False, clip_on=False)


        if self.domain == 'Figure':
            self.fig.add_artist(self.deb_rect)
        else:
            self.axes.add_artist(self.deb_rect)
        self.fig.canvas.draw()

    def __call__(self):
        self.deb_rect.remove()
        self.fig.canvas.draw()


def take_position(artist):
    if hasattr(artist, 'get_position'):
        xpos, ypos = artist.get_position()
    elif hasattr(artist, 'get_x'):
        xpos, ypos = artist.get_x(), artist.get_y()
    else:
        xpos = ypos = 0

    return r'(%.4f, %.4f)' % (xpos, ypos)
    

    
def patch_style(patch):
    """  curr = MoveCurr_type   """

    fig = patch.get_figure()
    axes = patch.axes

    domain = get_domain(patch)
    
    deb_rect = Deb_box(patch)
    
    title_win = 'Patch style'
    
    fc_color = patch.get_facecolor()             #(r,g,b,a)
    face_color = mpl.colors.to_hex(fc_color)     #'#rrggbb'  cuts alpha
    ed_color = patch.get_edgecolor()
    edge_color = mpl.colors.to_hex(ed_color)
    ln_width = patch.get_linewidth()

    alpha = round(fc_color[-1], 2)

    ln_alpha = ed_color[-1]

    fcx = mpl.colors.to_hex(rgba2rgb(fc_color))
    edx = mpl.colors.to_hex(rgba2rgb(ed_color))

    zorder = patch.get_zorder()
    clip_on = patch.get_clip_on()

    position = take_position(patch)
#    print(position)
       
    
    if hasattr(patch, 'angle') and not isinstance(patch, FancyArrow):
        angle = patch.angle
        angle_disabled = False
    else:
        angle = 0;
        angle_disabled = True

    gid = patch.get_gid()
    if gid == None:
        gid = ''

    title_win += ': '+gid

    jump_disabled = not hasattr(patch, 'get_position')

    def set_style():
        nonlocal deb_rect

        deb_rect()
        
        patch.set(facecolor=hex2rgba(face_color, alpha),
                  edgecolor=hex2rgba(edge_color, ln_alpha),
                  linewidth=ln_width,
                  zorder=zorder,
                  clip_on=clip_on,
                  alpha=None)  # otherwise ln_alpha does'n take effect
        if not angle_disabled:
            patch.set_angle(angle)

        if isinstance(patch, FancyArrow):
            patch.set_data(width=str2dig(win['ar_width'].get()),
                           head_width=str2dig(win['hd_width'].get()),
                           head_length=str2dig(win['hd_length'].get()))
            
        elif isinstance(patch, Annulus):
            patch.set_width(str2dig(win['an_width'].get()))
            patch.set_radii((str2dig(win['an_ra'].get()),
                             str2dig(win['an_rb'].get())))

        elif isinstance(patch, (Ellipse, Rectangle)):
            patch.set_width(str2dig(win['el_width'].get()))
            patch.set_height(str2dig(win['el_height'].get()))
           

        new_domain = domain
        if domain != 'Figure':
            new_domain = win['domain'].get()
            if new_domain != domain:
                if new_domain == 'Axes':         # data -> axes
                    if hasattr(patch, 'jumper'):
                        patch.jump_to_axes()
                        new_pos = patch.get_position()
                    else:
                        new_pos = axes.transLimits.transform(patch.get_position())
                        patch.set_position(new_pos)
                    transform = axes.transAxes
                    #patch._recompute_transform()
                else:
                    if hasattr(patch, 'jumper'):
                        patch.jump_to_data()
                        new_pos = patch.get_position()
                    else:                       # axes -> data
                        new_pos = axes.transLimits.inverted().transform(patch.get_position())
                        patch.set_position(new_pos)
                    transform = axes.transData
                    #patch._recompute_transform()

                patch.set(transform=transform)


            if isinstance(patch, FancyArrow):
                win['ar_width'].update(round(patch._width, 5))
                win['hd_width'].update(round(patch._head_width, 5))
                win['hd_length'].update(round(patch._head_length, 5))

            elif isinstance(patch, Annulus):
                win['an_width'].update(patch.width)
                win['an_ra'].update(patch.a)
                win['an_rb'].update(patch.b)

            elif isinstance(patch, (Ellipse, Rectangle)):
                win['el_width'].update(patch._width)
                win['el_height'].update(patch._height)

        position = take_position(patch)
        win['position'].update('Position: '+ position)

        deb_rect = Deb_box(patch)
        fig.canvas.draw()
        return new_domain

###############################################################################################    
####                               patch menu implementation                               ####
####                                                                                       ####

    position_layout = sg.Text('Position: '+ position, font=('normal', 12), key='position',
                              tooltip=' FancyArrow -> tail position if last grab otherwise head ' + '\n' +
                                      ' Rectangle    -> lower, left or first vertex ' + '\n' +
                                      ' Ellipse          -> center ')
    
    layout1 = [        
               
        [sg.Text('Face color:  ', font=('normal', 12)),
         sg.Button(key='face', enable_events=True, button_color=('black', face_color),
                   pad=(0.1, 0.1), size=(6, 1)),

         sg.Text(face_color, font=('italic', 10), key='face_color_hex'),

         sg.Push(),

         sg.Text('alpha: ', font=('normal', 12)),
         sg.Combo(list(x/10 for x in range(10, 0, -1)) ,default_value=str(alpha),
                  key='alpha', font=('bold', 12), enable_events=True, bind_return_key=True,
                  button_arrow_color='blue', button_background_color='white', size=(5, 12)),
         
         sg.Button(key='face_al', enable_events=True, button_color=('black', fcx),
                   pad=(0.1, 0.1), size=(6, 1)),
        ],

        [sg.Text('Edge color:  ', font=('normal', 12)),
         sg.Button(key='edge', enable_events=True, button_color=('black', edge_color),
                   pad=(0.1, 0.1), size=(6, 1)),

         sg.Text(edge_color, font=('italic', 10), key='edge_color_hex'),

         sg.Push(),

         sg.Text('alpha: ', font=('normal', 12)),
         sg.Combo(list(x/10 for x in range(10, 0, -1)) ,default_value=str(ln_alpha),
                  key='ln_alpha', font=('bold', 12), enable_events=True, bind_return_key=True,
                  button_arrow_color='blue', button_background_color='white', size=(5, 12)),

         sg.Button(key='edge_al', enable_events=True, button_color=('black', edx),
                   pad=(0.1, 0.1), size=(6, 1)),
        ],

        [sg.Text('Edge width: ', font=('normal', 12)),
         sg.Combo(list(range(1, 6)) ,default_value=str(ln_width), key='lwidth', font=('bold', 12),
                  button_arrow_color='blue', button_background_color='white', size=(5, None)),

         sg.Push(),

         sg.Text('zorder: ', font=('normal', 12)),
         sg.Combo(list(range(1, 9)) ,default_value=str(zorder), key='zorder', font=('bold', 12),
                  button_arrow_color='blue', button_background_color='white', size=(4, 10),
                  enable_events=True),
         
         sg.Push(),
         
          sg.Checkbox('clip_on', clip_on,
                      key='clip_on', enable_events=True, font=('bold', 12)),
        ]
    ]

    
    transform_layout = [
        [sg.Text('Domain: ', font=('normal', 12)),
         sg.Combo(['Data', 'Axes'] , default_value=domain, 
                  key='domain', font=('bold', 12), readonly=True, disabled=jump_disabled,
                  button_arrow_color='blue', button_background_color='white', size=(5, None)),
         sg.Push(),
         sg.Text('angle: ', font=('normal', 12)),
         sg.Input(default_text=angle, key='angle', font=('normal', 12), size=(7, None),
                   disabled=angle_disabled)
         ]
        ]


    fig_domain_layout = [[ sg.Text(str(fig), font=('normal', 12)),
         sg.Push(),
         sg.Text('angle: ', font=('normal', 12)),
         sg.Input(default_text=angle, key='angle', font=('normal', 12), size=(7, None),
                   disabled=angle_disabled)
         ]]

    delete_layout = [
        [sg.HSeparator(pad=(0, 10))],
        [
         sg.Checkbox('Delete item  !!! cannot be undone !!!', False,
                     text_color='grey', background_color=sg_bgcolor,
                     key='delete', enable_events=True, font=('bold', 12),
                     tooltip="Done after 'Close'"),
         sg.Push(),
         sg.Button(' Duplicate ', key='duplicate', enable_events=True, font=('normal', 12))
        ]
      ]

    
    set_style_layout = [
            [sg.Text('  ', font=('normal', 6))],
            [sg.Push(), sg.Button('Set style', key='set_style', enable_events=True,
                                   font=('normal', 12), button_color=('white', 'green'))]]

    ok_layout = [
        [sg.HSeparator(pad=(0, 10))],

        [sg.Button(' Close ', key='Ok', font=('normal', 12), bind_return_key=True),
         sg.Push(),

         sg.Text(sg_cpr_text, font=('italic', 8)),

         sg.Push(),
         ]
        ]


    if patch in fig.get_children():
        layout = layout1 + [fig_domain_layout]
    else:
        layout = layout1 + [transform_layout]

    no_position = True

    if isinstance(patch, FancyArrow):    
        fancy_arrow_layout = [
             [ position_layout ],
             sg.Text('ar.width: ', font=('normal', 12)),
             sg.Input(default_text=round(patch._width, 5), key='ar_width', font=('normal', 12),
                      size=(7, None)),
             sg.Push(),

             sg.Text('hd.width: ', font=('normal', 12)),
             sg.Input(default_text=round(patch._head_width, 5), key='hd_width', font=('normal', 12),
                      size=(7, None)),
             sg.Push(),
         
             sg.Text('hd.length: ', font=('normal', 12)),
             sg.Input(default_text=round(patch._head_length, 5), key='hd_length', font=('normal', 12),
                      size=(7, None))
            ]
        
        layout += [fancy_arrow_layout]
        no_position = False


    elif isinstance(patch, Annulus):    
        annulus_arrow_layout = [
            [ position_layout ],
             sg.Text('an.width: ', font=('normal', 12)),
             sg.Input(default_text=round(patch.width, 5), key='an_width', font=('normal', 12),
                      size=(7, None)),
             sg.Push(),

             sg.Text('an.ra: ', font=('normal', 12)),
             sg.Input(default_text=round(patch.a, 5), key='an_ra', font=('normal', 12),
                      size=(7, None)),
             sg.Push(),
         
             sg.Text('an.rb: ', font=('normal', 12)),
             sg.Input(default_text=round(patch.b, 5), key='an_rb', font=('normal', 12),
                      size=(7, None))
            ]
        
        layout += [annulus_arrow_layout]
        no_position = False


    elif isinstance(patch, (Ellipse, Rectangle)):    
        ellipse_arrow_layout = [
            [ position_layout,
             sg.Push(),
             sg.Text('width: ', font=('normal', 12)),
             sg.Input(default_text=round(patch._width, 5), key='el_width', font=('normal', 12),
                      size=(7, None))
             ],
            [
             sg.Push(),
             sg.Text('height: ', font=('normal', 12)),
             sg.Input(default_text=round(patch._height, 5), key='el_height', font=('normal', 12),
                      size=(7, None))
             ]
            ]
        
        layout += [ellipse_arrow_layout]
        no_position = False

        
    if no_position:
        layout += [[position_layout]]

    layout += [set_style_layout] + [delete_layout] + [ok_layout]
        
 
    win = sg.Window(title_win, layout, finalize = True, return_keyboard_events=True,
                    force_toplevel=True, location=(1000, 300),
                    keep_on_top=True, modal=True,
                    )

    butt = ['face', 'edge', 'Ok', 'set_style']
    disable = map(lambda x: win[x].update(disabled=True), butt)
    enable = map(lambda x: win[x].update(disabled=False), butt)

    while True:
        event, values = win.read()            # event       ->  values
        
        if event == 'face':
            [*disable]
            inp_color = colorchooser.askcolor(color=face_color)[1]
            [*enable]
            if not inp_color in ('None', None):
                face_color = inp_color
                win['face'].update(button_color=('white', face_color))
                win['face_color_hex'].update(face_color)
                event = 'alpha'

        if event == 'edge':
            [*disable]
            inp_color = colorchooser.askcolor(color=edge_color)[1]
            [*enable]
            if not inp_color in ('None', None):
                edge_color = inp_color
                win['edge'].update(button_color=('white', edge_color))
                win['edge_color_hex'].update(edge_color)
                event = 'ln_alpha'
            
        if event == 'alpha':
            alpha = round(str2dig(win['alpha'].get()), 2)
            fcx = mpl.colors.to_hex( rgba2rgb( hex2rgb(face_color) + (alpha,) ) )
            win['face_al'].update(button_color=('black', fcx))

        if event == 'ln_alpha':
            ln_alpha = round(str2dig(win['ln_alpha'].get()), 2)
            edx = mpl.colors.to_hex( rgba2rgb( hex2rgb(edge_color) + (ln_alpha,) ) )
            win['edge_al'].update(button_color=('black', edx))

        if event == 'zorder':
            zorder = round(str2dig(win['zorder'].get()), 2)


        if event == 'duplicate':
            if domain == 'Axes':
                transform = axes.transAxes
            elif domain == 'Data':
                transform = axes.transData
            else:
                transform = fig.transFigure
                
            if isinstance(patch, FancyArrow):
                xy = patch.get_dxdy()
                new_patch = FancyArrow(-0.05, -0.05, xy[0], xy[1], width=0.01, fc='#9B9114', ec='black', gid='farr',
                                       picker=True, clip_on=False, zorder=3, transform=transform)


            elif isinstance(patch, Annulus):
                new_patch = Annulus((-0.05, -0.05), (0.05, 0.15), 0.02, angle=0,
                                    color='#9B9114', gid='annu',
                                    picker=True, clip_on=False,
                                    zorder=3, transform=transform)


            elif isinstance(patch, Ellipse):
                new_patch = Ellipse((-0.05, -0.05), 0.05, 0.15, angle=0, fc='#9B9114', ec='black', gid='elli',
                                picker=True, clip_on=False, zorder=3, transform=transform)

               
            elif isinstance(patch, Circle):
                 new_patch = Circle((-0.05, -0.05), 0.01, color=c_ax, alpha=0.7, gid='elli5', angle=45,
                                      clip_on=False, transform=transform)
     

            elif isinstance(patch, Wedge):
                new_patch = Wedge((-0.05, -0.05), 0.1, -135, 135, width=0.05, color='black', alpha=0.7,
                            gid='wedde', clip_on=False, transform=transform)
                
            elif isinstance(patch, Rectangle):
                new_patch = Rectangle((-0.05, -0.05), patch.get_width(), patch.get_height(),
                                      color='black', alpha=0.7, gid='recc',
                                      clip_on=False, transform=transform)

            elif isinstance(patch, Polygon):
                poly = patch.get_xy()
                new_patch = Polygon(poly, color='black', alpha=0.7, clip_on=False,
                                    gid='polly', angle=0,
                                    transform=transform)
                new_patch.set_position((-0.05, -0.05))



            deb_rect()

            pp.exar.append(new_patch)

            if domain == 'Figure':
                new_patch.set_position((0.1, 0.1))
                fig.add_artist(new_patch)
            else:
                axes.add_artist(new_patch)
                
            new_patch.set_picker(True)

            patch = new_patch

            deb_rect = Deb_box(patch)

            win['clip_on'].update(value=False)

            event = 'set_style'


        if event == 'set_style':
            ln_width = win['lwidth'].get()
            ln_width = round(str2dig(win['lwidth'].get()), 2)
            win['lwidth'].update(ln_width)
            alpha = round(str2dig(win['alpha'].get()), 2)
            ln_alpha = round(str2dig(win['ln_alpha'].get()), 2)
            clip_on = win['clip_on'].get()
            angle = round(str2dig(win['angle'].get()), 2)

            domain = set_style()
            

        if event in ('Escape:27', 'Cancel', sg.WIN_CLOSED):
            win.close()
            del win
            deb_rect()
            return None

        if event == 'delete':
            if win['delete'].get():
                win['delete'].update(text_color='black', checkbox_color='white',
                                     background_color='orange')
            else:
                win['delete'].update(text_color='grey', checkbox_color=sg_bgcolor,
                                     background_color=sg_bgcolor)
                 
        if event == 'Ok':
            if win['delete'].get():
                try:
                    patch.set(visible=False)
                    pp.exar.remove(patch)
                    fig.canvas.draw()
                except:
                    print('Cannot remove ', patch)
            #set_style()
            win.close()
            del win
            deb_rect()
            return


def edit_ml_label(title, label, msg='Label name:', rows=1, redraw=True, text_tooltip=None,
               input_tooltip=None, frame=True):

    if not hasattr(label, 'get_text'):
        return

    fig = label.get_figure()
    axes = label.axes
    domain = get_domain(label)

    deb_rect = Deb_box(label)
      
    label_text = label.get_text()

    xpos, ypos = label.get_position()

    position = r'(%.4f, %.4f)' % (xpos, ypos)


    ltext = label_text.split('\n')
    max_lab = max([*map(lambda x: len(x), ltext)])
    ww = 50
    if max_lab > ww:
        ww = max_lab + 5
    if ww > 80:
        ww = 80

    tx_style = label.get_style()
    tx_size = label.get_size()
    tx_weight = label.get_weight()
    tx_styles = ['normal', 'italic']
    tx_weights = ['normal', 'bold']
    tx_color = mpl.colors.to_hex(label.get_color())
    tx_alpha = label.get_alpha()
    if tx_alpha == None:
        tx_alpha = 1.0
    txa = mpl.colors.to_hex(rgba2rgb(hex2rgba(tx_color, alpha=tx_alpha)))
    
    tx_ma = label._get_multialignment()
    if tx_ma == None:
        tx_ma = 'left'
    zorder = label.get_zorder()
    clip_on = label.get_clip_on()
    angle = round(label._rotation, 2)  # real angle ref. horiz.line
    if angle > 180.0:
        angle -= 360.0
    keep_angle = label.get_transform_rotates_text()
   
    keep_angle_text = f'keep {domain} →'
    keep_angle_sub_text = f'(45 degree ≡ {domain} diagonal)'

    patch = label.get_bbox_patch()

    c_fig = 'red'
    c_ax = 'blue'
    c_data = 'darkgreen'
    b_fig = dict(fc='white', edgecolor=c_fig)
    b_ax = dict(fc='white', edgecolor=c_ax)
    b_data = dict(fc='white', edgecolor=c_data)


    if frame and patch == None:
        label.set_bbox(dict(fc='white',
                            edgecolor='white',
                            linewidth=1,
                            zorder=zorder,
                            clip_on=clip_on,
                            alpha=0))
        patch = label.get_bbox_patch()

    if patch != None:

        fc_color = patch.get_facecolor()             #(r,g,b,a)
        face_color = mpl.colors.to_hex(fc_color)     #'#rrggbb'  cuts alpha
        ed_color = patch.get_edgecolor()
        edge_color = mpl.colors.to_hex(ed_color)
        ln_width = patch.get_linewidth()

        fc_alpha = round(fc_color[-1], 2)

        ln_alpha = ed_color[-1]

        fcx = mpl.colors.to_hex(rgba2rgb(fc_color))
        edx = mpl.colors.to_hex(rgba2rgb(ed_color))


    def set_style():
        nonlocal label, patch, domain, deb_rect

        deb_rect()

        
        input_text = win['input'].get()
        if input_text == 'None':
            return ''
        
        # sg.popup_get_text dodaje drugi '\'
        
        input_text = '\n'.join(input_text.split('\\n'))
        tx_size = str2dig(win['tx_size'].get())
        tx_alpha = round(str2dig(win['alpha'].get()), 2)
        tx_ma = win['tx_ma'].get()
        zorder = win['zorder'].get()
        alpha = win['alpha'].get()
        clip_on = win['clip_on'].get()
        keep_angle = win['keep_angle'].get()
        angle = round(str2dig(win['angle'].get()), 2)
        style = 'italic' if win['italic'].get() else 'normal'
        weight = 'bold' if win['bold'].get() else 'normal'
        
        label.set(text = input_text,
                  size = tx_size,
                  style = style,
                  weight = weight,
                  alpha = tx_alpha,
                  color = tx_color,
                  clip_on = clip_on,
                  zorder = zorder,
                  rotation = angle,
                  va = 'baseline',
                  ha = 'left',
                  ma = tx_ma,
                  rotation_mode = 'anchor',
                  transform_rotates_text = keep_angle)

        if patch != None:
            ln_width = win['lwidth'].get()
            ln_width = round(str2dig(win['lwidth'].get()), 2)
            win['lwidth'].update(ln_width)
            fc_alpha = round(str2dig(win['fc_alpha'].get()), 2)
            ln_alpha = round(str2dig(win['ln_alpha'].get()), 2)
        
            patch.set(facecolor=hex2rgba(face_color, fc_alpha),
                      edgecolor=hex2rgba(edge_color, ln_alpha),
                      linewidth=ln_width,
                      zorder=zorder,
                      clip_on=clip_on,
                      alpha=None)  # otherwise ln_alpha does'n take effect

        
        if domain != 'Figure':
            new_domain = win['domain'].get()
            if new_domain != domain:
                if new_domain == 'Axes':         # data -> axes
                    new_pos = axes.transLimits.transform(label.get_position())
                    label.set_position(new_pos)
                    transform = axes.transAxes
                else:                            # axes -> data
                    new_pos = axes.transLimits.inverted().transform(label.get_position())
                    label.set_position(new_pos)
                    transform = axes.transData

                label.set(transform=transform)
                domain = new_domain

        position = take_position(label)
        win['position'].update('Position: '+ position)

                
        keep_angle_text = f'keep {domain} →'
        keep_angle_sub_text = f'(45 degree ≡ {domain} diagonal)'

        win['keep_angle'].update(text=keep_angle_text)
        win['sub_angle_tx'].update(keep_angle_sub_text)

        
        fig.canvas.draw()
        deb_rect = Deb_box(label)
        return input_text

###############################################################################################    
####                               text/label style menu implementation                    ####
####                                                                                       ####

    position_layout = [sg.Text('Position: '+ position, font=('normal', 12), key='position')]

    zorder_layout = [
        sg.Push(),

         sg.Text('zorder: ', font=('normal', 12)),
         sg.Combo(list(range(1, 9)) ,default_value=str(zorder), key='zorder', font=('bold', 12),
                  button_arrow_color='blue', button_background_color='white', size=(4, 10),
                  enable_events=True),

         sg.Checkbox('clip_on', clip_on,
                      key='clip_on', enable_events=True, font=('bold', 12))
        ]

    transform_layout = [
        [sg.Text('Domain: ', font=('normal', 12)),
         sg.Combo(['Data', 'Axes'] , default_value=domain,
                  key='domain', font=('bold', 12), readonly=True,
                  button_arrow_color='blue', button_background_color='white', size=(5, None))
         ] + zorder_layout,
        
        position_layout
        ]

    fig_domain_layout = [[ sg.Text(str(fig), font=('normal', 12))] + zorder_layout,
                         position_layout
                         ]

    set_style_layout = [
            [sg.Push(), sg.Button('Set style', key='set_style', enable_events=True,
                                   font=('normal', 12), button_color=('white', 'green'))]]

    ok_layout = [
        [sg.HSeparator(pad=(0, 10))],

        [sg.Button(' Close ', key='Ok', font=('normal', 12), bind_return_key=True),
         sg.Push(),

         sg.Text(sg_cpr_text, font=('italic', 8)),

         sg.Push()
         ]
    ]

    text_layout = [
        [sg.Text('Change label', font=('normal', 12), tooltip=None)],

        [sg.Multiline(label_text, size=(ww, rows), enable_events=True, key='input', font=('normal', 12),
                      expand_x=True, expand_y=True, justification='left', sbar_width=16)],

        [sg.Text('Text size:   ', font=('normal', 12)),
         sg.Combo(list(range(8, 16)) ,default_value=str(tx_size), key='tx_size', font=('bold', 12),
                  button_arrow_color='blue', button_background_color='white', size=(8, None)),

         sg.Checkbox('bold', True if tx_weight == 'bold' else False,
                      key='bold', enable_events=True, font=('bold', 12)),

         sg.Checkbox('italic', True if tx_style == 'italic' else False,
                      key='italic', enable_events=True, font=('italic', 12)),

         sg.Push(),
         sg.Text('just.', font=('normal', 12)),
         
         sg.Combo(['left', 'center', 'right'] , default_value=tx_ma,
                  key='tx_ma', font=('bold', 12), readonly=True,
                  button_arrow_color='blue', button_background_color='white', size=(6, None))
         
         ],

        [sg.Text('Text color:  ', font=('normal', 12)),
         sg.Button(key='color', enable_events=True, button_color=('black', tx_color),
                   pad=(0.1, 0.1), size=(6, 1)),

         sg.Text(tx_color, font=('italic', 10), key='text_color_hex'),

         sg.Push(),

         sg.Text('alpha: ', font=('normal', 12)),
         sg.Combo(list(x/10 for x in range(10, 0, -1)) ,default_value=str(tx_alpha),
                  key='alpha', font=('bold', 12), enable_events=True, bind_return_key=True,
                  button_arrow_color='blue', button_background_color='white', size=(5, 12)),
         sg.Button(key='tx_alpha', enable_events=True, button_color=('black', txa),
                   pad=(0.1, 0.1), size=(6, 1)),
        ],
        [sg.Text('angle: ', font=('normal', 12)),
          sg.Input(default_text=angle, key='angle', font=('normal', 12), size=(7, None)),
          sg.Checkbox(keep_angle_text, True if keep_angle else False,
                      key='keep_angle', enable_events=True, font=('bold', 12)),
    
          sg.Text(keep_angle_sub_text, font=('normal', 10), key='sub_angle_tx')
        ] 
    ]

    if patch != None:
        frame_layout = [
            [sg.HSeparator(pad=(0, 10))],
               
        [sg.Text('Face color:  ', font=('normal', 12)),
         sg.Button(key='face', enable_events=True, button_color=('black', face_color),
                   pad=(0.1, 0.1), size=(6, 1)),

         sg.Text(face_color, font=('italic', 10), key='face_color_hex'),

         sg.Push(),

         sg.Text('alpha: ', font=('normal', 12)),
         sg.Combo(list(x/10 for x in range(10, 0, -1)) ,default_value=str(fc_alpha),
                  key='fc_alpha', font=('bold', 12), enable_events=True, bind_return_key=True,
                  button_arrow_color='blue', button_background_color='white', size=(5, 12)),
         
         sg.Button(key='face_al', enable_events=True, button_color=('black', fcx),
                   pad=(0.1, 0.1), size=(6, 1)),
        ],

        [sg.Text('Edge color:  ', font=('normal', 12)),
         sg.Button(key='edge', enable_events=True, button_color=('black', edge_color),
                   pad=(0.1, 0.1), size=(6, 1)),

         sg.Text(edge_color, font=('italic', 10), key='edge_color_hex'),

         sg.Push(),

         sg.Text('alpha: ', font=('normal', 12)),
         sg.Combo(list(x/10 for x in range(10, 0, -1)) ,default_value=str(ln_alpha),
                  key='ln_alpha', font=('bold', 12), enable_events=True, bind_return_key=True,
                  button_arrow_color='blue', button_background_color='white', size=(5, 12)),

         sg.Button(key='edge_al', enable_events=True, button_color=('black', edx),
                   pad=(0.1, 0.1), size=(6, 1)),
        ],

        [sg.Text('Edge width: ', font=('normal', 12)),
         sg.Combo(list(range(1, 6)) ,default_value=str(ln_width), key='lwidth', font=('bold', 12),
                  button_arrow_color='blue', button_background_color='white', size=(5, None))        
        ]
        ]
    else:
        frame_layout = []

    delete_layout = [
        [sg.HSeparator(pad=(0, 10))],
        [
         sg.Checkbox('Delete item  !!! cannot be undone !!!', False,
                     text_color='grey', background_color=sg_bgcolor,
                     key='delete', enable_events=True, font=('bold', 12),
                     tooltip="Done after 'Close'"),
         sg.Push(),
         sg.Button(' Duplicate ', key='duplicate', enable_events=True, font=('normal', 12))
        ]
      ]
    
    if domain == 'Figure':
        layout = text_layout + [fig_domain_layout] + [frame_layout] + \
                 [set_style_layout] + [delete_layout] + [ok_layout]
    else:
        layout = text_layout + [transform_layout] + [frame_layout] +  \
                 [set_style_layout] + [delete_layout] + [ok_layout]

  
    win = sg.Window(title, layout, finalize = True, keep_on_top=True, modal=True,
                    return_keyboard_events=True,  location=(1000, 300),
                    )
    win['input'].widget.config(wrap='none')  # ustawiane przez Tkinter

    butt = ['color', 'alpha', 'Ok', 'set_style', 'face', 'edge']
    disable = map(lambda x: win[x].update(disabled=True), butt)
    enable = map(lambda x: win[x].update(disabled=False), butt)

    while True:
        event, values = win.read()            # event       ->  values

        if event == 'color':
            [*disable]
            inp_color = colorchooser.askcolor(color=tx_color)[1]
            [*enable]
            if not inp_color in ('None', None):
                tx_color = inp_color
                win['color'].update(button_color=('white', tx_color))
                win['text_color_hex'].update(tx_color)
                event = 'alpha'
            
        if event == 'alpha':
            tx_alpha = round(str2dig(win['alpha'].get()), 2)
            txa = mpl.colors.to_hex( rgba2rgb( hex2rgb(tx_color) + (tx_alpha,) ) )
            win['tx_alpha'].update(button_color=('black', txa))

        if event == 'face':
            [*disable]
            inp_color = colorchooser.askcolor(color=face_color)[1]
            [*enable]
            if not inp_color in ('None', None):
                face_color = inp_color
                win['face'].update(button_color=('white', face_color))
                win['face_color_hex'].update(face_color)
                event = 'fc_alpha'

        if event == 'edge':
            [*disable]
            inp_color = colorchooser.askcolor(color=edge_color)[1]
            [*enable]
            if not inp_color in ('None', None):
                edge_color = inp_color
                win['edge'].update(button_color=('white', edge_color))
                win['edge_color_hex'].update(edge_color)
                event = 'ln_alpha'
            
        if event == 'fc_alpha':
            alpha = round(str2dig(win['fc_alpha'].get()), 2)
            fcx = mpl.colors.to_hex( rgba2rgb( hex2rgb(face_color) + (alpha,) ) )
            win['face_al'].update(button_color=('black', fcx))

        if event == 'ln_alpha':
            ln_alpha = round(str2dig(win['ln_alpha'].get()), 2)
            edx = mpl.colors.to_hex( rgba2rgb( hex2rgb(edge_color) + (ln_alpha,) ) )
            win['edge_al'].update(button_color=('black', edx))

        if event in ('Escape:27', 'Cancel', sg.WIN_CLOSED):
            win.close()
            del win
            deb_rect()
            return label_text

        if event == 'duplicate':
            deb_rect()
            if domain == 'Figure':
                label = fig.text(0.05, 0.05, 'This is copy text', clip_on=False,
                                 bbox=dict(fc='white', edgecolor='black'))
            else:
                if domain == 'Axes':
                    transform = axes.transAxes
                else:
                    transform = axes.transData
                label = axes.text(-0.05, -0.05, 'This is copy text', clip_on=False,
                                  bbox=dict(fc='white', edgecolor='black'),
                                  transform=transform)


            pp.exar.append(label)
            label.set_picker(True)

            patch = label.get_bbox_patch()

            deb_rect = Deb_box(label)

            win['clip_on'].update(value=False)

            event = 'set_style'
            

        if event == 'set_style':
            label_text = set_style()

        if event == 'delete':
            if win['delete'].get():
                win['delete'].update(text_color='black', checkbox_color='white',
                                     background_color='orange')
            else:
                win['delete'].update(text_color='grey', checkbox_color=sg_bgcolor,
                                     background_color=sg_bgcolor)

        if event == 'Ok':
            if win['delete'].get():
                try:
                    label.set(visible=False)  # better hide than remove() 
                    patch.set(visible=False)
                    pp.exar.remove(label)
                except:
                    print('Cannot remove ', patch)

            win.close()
            del win
            deb_rect()
            return label_text
        

if __name__ == "__main__":

    edit_ml_label('Figure title', 'qwerty')
