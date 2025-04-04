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


sg.theme('Default1')
sg_bgcolor = 'lightgrey'

sg.PySimpleGUI.TOOLTIP_BACKGROUND_COLOR = "#FAD7A0"
sg.PySimpleGUI.TOOLTIP_FONT = ("Helvetica", 11)
sg.PySimpleGUI.DEFAULT_TOOLTIP_TIME = 500
sg.PySimpleGUI.DEFAULT_TOOLTIP_OFFSET = (10, 20)  #  (0, -20)


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

    
def patch_style(patch):
    """  curr = MoveCurr_type   """

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
    
    domain = get_domain(patch)
       
    fig = patch.get_figure()
    axes = patch.axes
    
    if hasattr(patch, 'angle'):
        angle = patch.angle
        angle_disabled = False
    else:
        angle = 0;
        angle_disabled = True

    grab_opt = ['head', 'middle', 'tail']
    grab = 'None'
    if hasattr(patch, 'grab'):
        grab = patch.grab

    gid = patch.get_gid()
    if gid == None:
        gid = ''

    title_win += ': '+gid

    jump_disabled = not hasattr(patch, 'get_position')

    def set_style():
        
        patch.set(facecolor=hex2rgba(face_color, alpha),
                  edgecolor=hex2rgba(edge_color, ln_alpha),
                  linewidth=ln_width,
                  zorder=zorder,
                  clip_on=clip_on,
                  alpha=None)  # otherwise ln_alpha does'n take effect
        if not angle_disabled:
            patch.set_angle(angle)

        if grab in grab_opt:
            patch.grab = grab
            patch._make_verts()
            patch.set_xy(patch.verts)
            patch.dxy = patch.get_xy() - patch.get_xy()[0]

            
        new_domain = domain
        if domain != 'Figure':
            new_domain = win['domain'].get()
            if new_domain != domain:
                if new_domain == 'Axes':         # data -> axes
                    if hasattr(patch, 'jumper'):
                        patch.jump_to_axes()
                    else:
                        new_pos = axes.transLimits.transform(patch.get_position())
                        patch.set_position(new_pos)
                    transform = axes.transAxes
                    #patch._recompute_transform()
                else:
                    if hasattr(patch, 'jumper'):
                        patch.jump_to_data()
                    else:                       # axes -> data
                        new_pos = axes.transLimits.inverted().transform(patch.get_position())
                        patch.set_position(new_pos)
                    transform = axes.transData
                    #patch._recompute_transform()

                patch.set(transform=transform)

        fig.canvas.draw()
        return new_domain

###############################################################################################    
####                               patch menu implementation                               ####
####                                                                                       ####
    
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

    grab_layout = [
         sg.Push(),
         sg.Text('grab for: ', font=('normal', 12),
                 tooltip="Active immediately"),
         sg.Combo(grab_opt , default_value=grab, enable_events=True,
                  key='grab', font=('bold', 12), readonly=True,
                  disabled = True if grab == 'None' else False,
                  button_arrow_color='blue', button_background_color='white', size=(6, None),
                  tooltip="Active immediately"),

        ]

    delete_layout = [
        [sg.HSeparator(pad=(0, 10))],
        [
         sg.Checkbox('Delete item  !!! cannot be undone !!!', False, text_color='grey',
                     key='delete', enable_events=True, font=('bold', 12),
                     tooltip="Done after 'Close'")
        ]
      ]

    ok_layout = [
        [sg.HSeparator(pad=(0, 10))],

        [sg.Button(' Close ', key='Ok', font=('normal', 12), bind_return_key=True),
         sg.Push(),

         sg.Text(sg_cpr_text, font=('italic', 8)),

         sg.Push(),
         sg.Button('Set style', key='set_style', enable_events=True, font=('normal', 12),
                   button_color=('white', 'green'))
         ]
        ]


    if patch in fig.get_children():
        layout = layout1 + [fig_domain_layout] + [grab_layout] + [delete_layout] + [ok_layout]
    else:
        layout = layout1 + [transform_layout] + [grab_layout] + [delete_layout] + [ok_layout]
        

    win = sg.Window(title_win, layout, finalize = True, return_keyboard_events=True,
                    force_toplevel=True,
                    keep_on_top=True, # modal=True,
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

        if event == 'grab':
            grab = win['grab'].get()
            patch.grab = grab
            patch._make_verts()
            patch.set_xy(patch.verts)
            patch.dxy = patch.get_xy() - patch.get_xy()[0]


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
                except:
                    print('Cannot remove ', patch)
            #set_style()
            win.close()
            del win
            return


def edit_ml_label(title, label, msg='Label name:', rows=1, redraw=True, text_tooltip=None,
               input_tooltip=None, frame=True):

    if not hasattr(label, 'get_text'):
        return

    fig = label.get_figure()
    
    domain = get_domain(label)
    
    label_text = label.get_text()

    axes = label.axes

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
        nonlocal domain
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
                
        keep_angle_text = f'keep {domain} →'
        keep_angle_sub_text = f'(45 degree ≡ {domain} diagonal)'

        win['keep_angle'].update(text=keep_angle_text)
        win['sub_angle_tx'].update(keep_angle_sub_text)

        fig.canvas.draw()
        return input_text

###############################################################################################    
####                               text/label style menu implementation                    ####
####                                                                                       ####
 

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
         ] + zorder_layout
        ]

    fig_domain_layout = [[ sg.Text(str(fig), font=('normal', 12))] + zorder_layout]


    ok_layout = [
        [sg.HSeparator(pad=(0, 10))],

        [sg.Button(' Close ', key='Ok', font=('normal', 12), bind_return_key=True),
         sg.Push(),

         sg.Text(sg_cpr_text, font=('italic', 8)),

         sg.Push(),        
         sg.Button('Set style', key='set_style', enable_events=True, font=('normal', 12),
                   button_color=('white', 'green'))
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
         sg.Checkbox('Delete item  !!! cannot be undone !!!', False, text_color='grey',
                     key='delete', enable_events=True, font=('bold', 12),
                     tooltip="Done after 'Close'")
        ]
      ]
    
    if domain == 'Figure':
        layout = text_layout + [fig_domain_layout] + [frame_layout] + \
                [delete_layout] + [ok_layout]
    else:
        layout = text_layout + [transform_layout] + [frame_layout] +  \
                [delete_layout] + [ok_layout]

  
    win = sg.Window(title, layout, finalize = True, keep_on_top=True, modal=True, return_keyboard_events=True)
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
            return label_text

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
                except:
                    print('Cannot remove ', patch)

            win.close()
            del win
            return label_text
        

if __name__ == "__main__":

    edit_ml_label('Figure title', 'qwerty')
