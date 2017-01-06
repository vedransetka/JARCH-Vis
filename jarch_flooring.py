# This file is part of JARCH Vis
#
# JARCH Vis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JARCH Vis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JARCH Vis.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty, IntProperty, FloatVectorProperty
from random import uniform
from mathutils import Vector
from math import tan, sin, cos, radians, sqrt
import bmesh
from . jarch_materials import image_material, mortar_material
from . jarch_utils import METRIC_INCH, METRIC_FOOT, append_all, apply_modifier_boolean


def create_flooring(mat, if_wood, if_tile, over_width, over_length, b_width, b_length, b_length2, is_length_vary,
                    length_vary, num_boards, space_l, space_w,
                    spacing, t_width, t_length, is_offset, offset, is_ran_offset, offset_vary, t_width2, is_width_vary,
                    width_vary, max_boards, is_ran_thickness, ran_thickness, th, hb_dir):

    verts = []
    faces = []

    # create siding
    if mat == "1":  # Wood
        if if_wood == "1":  # Regular
            verts, faces = wood_regular(over_width, over_length, b_width, b_length, space_l, space_w, is_length_vary,
                                        length_vary, is_width_vary, width_vary, max_boards, is_ran_thickness, ran_thickness,
                                        th)
        elif if_wood == "2":  # Parquet
            verts, faces = wood_parquet(over_width, over_length, b_width, spacing, num_boards, th)
        elif if_wood == "3":  # Herringbone Parquet
            verts, faces = wood_herringbone(over_width, over_length, b_width, b_length2, spacing, th, hb_dir, True)
        elif if_wood == "4":  # Herringbone
            verts, faces = wood_herringbone(over_width, over_length, b_width, b_length2, spacing, th, hb_dir, False)
    elif mat == "2":  # Tile
        if if_tile == "1":  # Regular
            verts, faces = tile_regular(over_width, over_length, t_width, t_length, spacing, is_offset, offset,
                                        is_ran_offset, offset_vary, th)
        elif if_tile == "2":  # Large + Small
            verts, faces = tile_ls(over_width, over_length, t_width, t_length, spacing, th)
        elif if_tile == "3":  # Large + Many Small
            verts, faces = tile_lms(over_width, over_length, t_width, spacing, th)
        elif if_tile == "4":  # Hexagonal
            verts, faces = tile_hexagon(over_width, over_length, t_width2, spacing, th)
    
    return verts, faces


def wood_herringbone(ow, ol, bw, bl, s, th, hb_dir, stepped):
    verts = []
    faces = []
    cur_x, cur_y, cur_z = 0.0, 0.0, 0.0
    x_off, y_off = 0.0, 0.0  # used for finding farther forwards points when stepped
    ang_s = s * sin(radians(45))
    s45 = s / sin(radians(45))    
    
    # step variables
    if stepped:
        x_off = cos(radians(45)) * bw
        y_off = sin(radians(45)) * bw
        
    wid_off = sin(radians(45)) * bl  # offset from one end of the board to the other inline with width
    len_off = cos(radians(45)) * bl  # offset from one end of the board to the other inline with length
    w = bw / cos(radians(45))  # width adjusted for 45 degree rotation
    
    # figure out starting position
    if hb_dir == "1":
        cur_y = -wid_off    
            
    elif hb_dir == "2":
        cur_x = ow
        cur_y = ol + wid_off
    
    elif hb_dir == "3":
        cur_y = ol
        cur_x = -wid_off
        
    elif hb_dir == "4":
        cur_x = ow + wid_off
            
    # loop going forwards
    while (hb_dir == "1" and cur_y < ol + wid_off) or (hb_dir == "2" and cur_y > 0 - wid_off) or \
            (hb_dir == "3" and cur_x < ow + wid_off) or (hb_dir == "4" and cur_x > 0 - wid_off):
        going_forwards = True
        
        # loop going right
        while (hb_dir == "1" and cur_x < ow) or (hb_dir == "2" and cur_x > 0) or (hb_dir == "3" and cur_y > 0) or \
                (hb_dir == "4" and cur_y < ol):
            p = len(verts)                        
            
            # add verts
            # forwards
            if hb_dir == "1":
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                
                if stepped and cur_x != 0:
                    verts += [(cur_x - x_off, cur_y + y_off, cur_z), (cur_x - x_off, cur_y + y_off, cur_z + th)]
                else:
                    verts += [(cur_x, cur_y + w, cur_z), (cur_x, cur_y + w, cur_z + th)]
                
                if going_forwards:
                    cur_y += wid_off
                else:
                    cur_y -= wid_off
                cur_x += len_off
                
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                if stepped:
                    verts += [(cur_x - x_off, cur_y + y_off, cur_z), (cur_x - x_off, cur_y + y_off, cur_z + th)]
                    cur_x -= x_off - ang_s
                    if going_forwards:                        
                        cur_y += y_off + ang_s
                    else:
                        cur_y -= y_off + ang_s
                else:
                    verts += [(cur_x, cur_y + w, cur_z), (cur_x, cur_y + w, cur_z + th)]
                    cur_x += s 
                
            # backwards
            elif hb_dir == "2":
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                
                if stepped and cur_x != ow:
                    verts += [(cur_x + x_off, cur_y - y_off, cur_z), (cur_x + x_off, cur_y - y_off, cur_z + th)]
                else:
                    verts += [(cur_x, cur_y - w, cur_z), (cur_x, cur_y - w, cur_z + th)]
                
                if going_forwards:
                    cur_y -= wid_off
                else:
                    cur_y += wid_off
                cur_x -= len_off
                
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                if stepped:
                    verts += [(cur_x + x_off, cur_y - y_off, cur_z), (cur_x + x_off, cur_y - y_off, cur_z + th)]
                    cur_x += x_off - ang_s
                    if going_forwards:                        
                        cur_y -= y_off + ang_s
                    else:
                        cur_y += y_off + ang_s
                else:
                    verts += [(cur_x, cur_y - w, cur_z), (cur_x, cur_y - w, cur_z + th)]
                    cur_x -= s 
            # right
            elif hb_dir == "3":
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]

                if stepped and cur_y != ol:
                    verts += [(cur_x + y_off, cur_y + x_off, cur_z), (cur_x + y_off, cur_y + x_off, cur_z + th)]                 
                else:
                    verts += [(cur_x + w, cur_y, cur_z), (cur_x + w, cur_y, cur_z + th)]
                    
                if going_forwards:
                    cur_x += wid_off
                else:
                    cur_x -= wid_off
                cur_y -= len_off
                
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                if stepped:
                    verts += [(cur_x + y_off, cur_y + x_off, cur_z), (cur_x + y_off, cur_y + x_off, cur_z + th)] 
                    cur_y += x_off - ang_s
                    if going_forwards:                        
                        cur_x += y_off + ang_s
                    else:
                        cur_x -= y_off + ang_s
                else:
                    verts += [(cur_x + w, cur_y, cur_z), (cur_x + w, cur_y, cur_z + th)]
                    cur_y -= s 
            # left
            else:
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                
                if stepped and cur_y != 0:
                    verts += [(cur_x - y_off, cur_y - x_off, cur_z), (cur_x - y_off, cur_y - x_off, cur_z + th)]
                else:
                    verts += [(cur_x - w, cur_y, cur_z), (cur_x - w, cur_y, cur_z + th)]
                    
                if going_forwards:
                    cur_x -= wid_off
                else:
                    cur_x += wid_off
                cur_y += len_off
                
                verts += [(cur_x, cur_y, cur_z), (cur_x, cur_y, cur_z + th)]
                if stepped:
                    verts += [(cur_x - y_off, cur_y - x_off, cur_z), (cur_x - y_off, cur_y - x_off, cur_z + th)]
                    cur_y -= x_off - ang_s
                    if going_forwards:                        
                        cur_x -= y_off + ang_s
                    else:
                        cur_x += y_off + ang_s
                else:
                    verts += [(cur_x - w, cur_y, cur_z), (cur_x - w, cur_y, cur_z + th)]
                    cur_y += s                    
                
            # faces
            faces += [(p, p + 1, p + 3, p + 2), (p, p + 4, p + 5, p + 1), (p + 4, p + 6, p + 7, p + 5),
                      (p + 6, p + 2, p + 3, p + 7), (p + 1, p + 5, p + 7, p + 3), (p, p + 2, p + 6, p + 4)]
        
            # flip going_right
            going_forwards = not going_forwards
            x_off *= -1 
            
        # if not in forwards position, then move back before adjusting values for next row
        if not going_forwards:
            x_off = abs(x_off)
            if hb_dir == "1":            
                cur_y -= wid_off
                if stepped:
                    cur_y -= y_off + ang_s
            elif hb_dir == "2":
                cur_y += wid_off
                if stepped:
                    cur_y += y_off + ang_s
            elif hb_dir == "3":
                cur_x -= wid_off
                if stepped:
                    cur_x -= y_off + ang_s
            else:
                cur_x += wid_off
                if stepped:
                    cur_x += y_off + ang_s              
        
        # adjust forwards
        if hb_dir == "1":
            cur_y += w + s45
            cur_x = 0
        elif hb_dir == "2":
            cur_y -= w + s45
            cur_x = ow
        elif hb_dir == "3":
            cur_x += w + s45
            cur_y = ol
        else:
            cur_x -= w + s45
            cur_y = 0
    
    return verts, faces


# tile large + small
def tile_ls(ow, ol, tw, tl, s, th):
    verts = []
    faces = []
    hw = (tw / 2) - (s / 2)
    hl = (tl / 2) - (s / 2)
    cur_y = tl + hl + s + s
    z = th

    while cur_y < ol:
        cur_x = -hw - s
        st_y = float(cur_y)

        while cur_x < ow:
            # large
            for i in range(5):
                p = len(verts)
                if cur_x < ow and cur_y < ol:
                    append_all(verts, [(cur_x, cur_y + tl, 0.0), (cur_x, cur_y + tl, z), (cur_x, cur_y, z),
                                       (cur_x, cur_y, 0.0)])
                    cur_x += tw
                    append_all(verts, [(cur_x, cur_y + tl, 0.0), (cur_x, cur_y + tl, z), (cur_x, cur_y, z),
                                       (cur_x, cur_y, 0.0)])

                    append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3),
                                       (p + 3, p + 7, p + 6, p + 2), (p + 1, p + 2, p + 6, p + 5),
                                       (p, p + 1, p + 5, p + 4)])

                    p = len(verts)

                    if i == 0:
                        x = cur_x + s
                        y = cur_y + s + hl
                    elif i == 1:
                        x = cur_x - tw
                        y = cur_y + tl + s
                    elif i == 2:
                        x = cur_x + s
                        y = cur_y + hl + s
                    elif i == 3:
                        x = cur_x - tw
                        y = cur_y + tl + s
                    else:
                        x = cur_x - hw
                        y = cur_y - s - hl

                    append_all(verts, [(x, y+hl, 0.0), (x, y + hl, z), (x, y, z), (x, y, 0.0)])
                    x += hw
                    append_all(verts, [(x, y+hl, 0.0), (x, y + hl, z), (x, y, z), (x, y, 0.0)])

                    append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3),
                                       (p + 3, p + 7, p + 6, p + 2), (p + 1, p + 2, p + 6, p + 5),
                                       (p, p + 1, p + 5, p + 4)])

                    # update position
                    if i == 0:
                        cur_x -= hw
                        cur_y -= s + hl + s + tl
                    elif i == 1:
                        cur_x -= hw
                        cur_y += tl + s
                    elif i == 2:
                        cur_x -= hw
                        cur_y -= tl + s + hl + s
                    elif i == 3:
                        cur_x -= hw
                        cur_y += tl + s
                    elif i == 4:
                        cur_x -= hw
                        cur_y += tl + s
                else:
                    cur_x += hw           
        cur_y = st_y + tl + s + tl + s + s + hl
                    
    return verts, faces


def tile_hexagon(ow, ol, tw, s, th):
    verts = []
    faces = []
    offset = False
    z = th
    w = tw / 2
    cur_y = 0.0
    h = w * tan(radians(30))
    r = sqrt((w * w) + (h * h))

    while cur_y < ol + tw:
        if not offset:
            cur_x = 0.0
        else:
            cur_x = w + (s / 2)

        while cur_x < ow:
            p = len(verts)
            append_all(verts, [(cur_x + w, cur_y + h, 0.0), (cur_x, cur_y + r, 0.0), (cur_x - w, cur_y + h, 0.0),
                               (cur_x - w, cur_y - h, 0.0), (cur_x, cur_y - r, 0.0), (cur_x + w, cur_y - h, 0.0)])
            append_all(verts, [(cur_x + w, cur_y + h, z), (cur_x, cur_y + r, z), (cur_x - w, cur_y + h, z),
                               (cur_x - w, cur_y - h, z), (cur_x, cur_y - r, z), (cur_x + w, cur_y - h, z)])

            n = p
            for i in range(5):
                faces.append((n + i, n + i + 1, n + i + 7, n + i + 6))

            append_all(faces, [(p + 5, p, p + 6, p + 11), (p + 3, p + 2, p + 1, p), (p + 5, p + 4, p + 3, p),
                               (p + 6, p + 7, p + 8, p + 9), (p + 9, p + 10, p + 11, p + 6)])

            cur_x += tw + s

        cur_y += r + h + s
        offset = not offset
    
    return verts, faces


# tile large + many small
def tile_lms(ow, ol, tw, s, th):
    verts = []
    faces = []
    small = True
    z = th
    cur_y = 0.0
    ref = (tw - s) / 2

    tw2, tl2, tw3, tl3 = ref, ref, tw, tw

    while cur_y < ol:
        cur_x = 0.0
        large = False
        while cur_x < ow:
            if small:
                if cur_x < ow < cur_x + ref:
                    tw2 = ow - cur_x
                if cur_y < ol < cur_y + ref:
                    tl2 = ol - cur_y

                p = len(verts)
                append_all(verts, [(cur_x, cur_y + tl2, 0.0), (cur_x, cur_y + tl2, z), (cur_x, cur_y, z),
                                   (cur_x, cur_y, 0.0)])
                cur_x += tw2
                append_all(verts, [(cur_x, cur_y + tl2, 0.0), (cur_x, cur_y + tl2, z), (cur_x, cur_y, z),
                                   (cur_x, cur_y, 0.0)])

                append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3),
                                   (p + 3, p + 7, p + 6, p + 2), (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p+4)])
            else:
                if not large:
                    error = []
                    for i in range(2):
                        if cur_x < ow and cur_y < ol:
                            if cur_x + ref > ow:
                                tw2 = ow - cur_x
                            if cur_y + ref > ol:
                                tl2 = ol - cur_y
                            p = len(verts)
                            append_all(verts, [(cur_x, cur_y + tl2, 0.0), (cur_x, cur_y + tl2, z), (cur_x, cur_y, z),
                                               (cur_x, cur_y, 0.0)])
                            cur_x += tw2
                            append_all(verts, [(cur_x, cur_y + tl2, 0.0), (cur_x, cur_y + tl2, z), (cur_x, cur_y, z),
                                               (cur_x, cur_y, 0.0)])
                            cur_y += tl2 + s
                            cur_x -= tw2
                            error.append(tl2)

                            append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7),
                                               (p, p + 4, p + 7, p + 3), (p + 3, p + 7, p + 6, p + 2),
                                               (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4)])
                    for i in error:
                        cur_y -= i + s
                    cur_x += tw2

                else:
                    if cur_x + tw > ow:
                        tw3 = ow - cur_x
                    if cur_y + tw > ol:
                        tl3 = ol - cur_y
                    p = len(verts)
                    append_all(verts, [(cur_x, cur_y + tl3, 0.0), (cur_x, cur_y + tl3, z), (cur_x, cur_y, z),
                                       (cur_x, cur_y, 0.0)])
                    cur_x += tw3
                    append_all(verts, [(cur_x, cur_y + tl3, 0.0), (cur_x, cur_y + tl3, z), (cur_x, cur_y, z),
                                       (cur_x, cur_y, 0.0)])

                    append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3),
                                       (p + 3, p + 7, p + 6, p + 2), (p + 1, p + 2, p + 6, p + 5), (p, p+1, p+5, p+4)])

                large = not large
            cur_x += s 
        if small:
            cur_y += tl2 + s
        else:
            cur_y += tl3 + s
        small = not small

    return verts, faces


def tile_regular(ow, ol, tw, tl, s, is_offset, offset, is_ran_offset, offset_vary, th):
    verts = []
    faces = []
    off = False
    o = 1 / (100 / offset)
    cur_y = 0.0
    z = th

    while cur_y < ol:
        cur_x = 0.0
        tl2 = tl
        if cur_y < ol < cur_y + tl:
            tl2 = ol - cur_y

        while cur_x < ow:
            p = len(verts)
            tw2 = tw
            if cur_x < ow < cur_x + tw:
                tw2 = ow - cur_x
            elif cur_x == 0.0 and off and is_offset and not is_ran_offset:
                tw2 = tw * o 
            elif cur_x == 0.0 and is_offset and is_ran_offset:
                v = tl * 0.0049 * offset_vary
                tw2 = uniform((tl / 2) - v, (tl / 2) + v)

            append_all(verts, [(cur_x, cur_y+tl2, 0.0), (cur_x, cur_y+tl2, z), (cur_x, cur_y, z), (cur_x, cur_y, 0.0)])
            cur_x += tw2
            append_all(verts, [(cur_x, cur_y+tl2, 0.0), (cur_x, cur_y+tl2, z), (cur_x, cur_y, z), (cur_x, cur_y, 0.0)])
            cur_x += s

            append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7), (p, p + 4, p + 7, p + 3),
                               (p + 3, p + 7, p + 6, p + 2), (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4)])

        cur_y += tl2 + s
        off = not off

    return verts, faces


def wood_parquet(ow, ol, bw, s, num_boards, th):
    verts = []
    faces = []
    cur_x = 0.0
    z = th
    start_orient_length = True

    # figure board length
    bl = (bw * num_boards) + (s * (num_boards - 1))
    while cur_x < ow:
        cur_y = 0.0
        orient_length = start_orient_length
        while cur_y < ol:
            bl2 = bl
            bw2 = bw

            if orient_length:
                start_x = cur_x

                for i in range(num_boards):
                    if cur_x < ow and cur_y < ol:
                        # make sure board should be placed
                        if cur_x < ow < cur_x + bw:
                            bw2 = ow - cur_x
                        if cur_y < ol < cur_y + bl:
                            bl2 = ol - cur_y
                        p = len(verts)               
                        append_all(verts, [(cur_x, cur_y, 0.0), (cur_x, cur_y, z), (cur_x + bw2, cur_y, z),
                                           (cur_x + bw2, cur_y, 0.0)])
                        cur_y += bl2
                        append_all(verts, [(cur_x, cur_y, 0.0), (cur_x, cur_y, z), (cur_x + bw2, cur_y, z),
                                           (cur_x + bw2, cur_y, 0.0)])
                        cur_y -= bl2
                        cur_x += bw2 + s

                        append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7),
                                           (p, p + 4, p + 7, p + 3), (p + 3, p + 7, p + 6, p + 2),
                                           (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4)])

                cur_x = start_x
                cur_y += bl2 + s

            else:
                for i in range(num_boards):
                    if cur_x < ow and cur_y < ol:
                        if cur_x < ow < cur_x + bl:
                            bl2 = ow - cur_x
                        if cur_y < ol < cur_y + bw:
                            bw2 = ol - cur_y
                        p = len(verts)
                        append_all(verts, [(cur_x, cur_y + bw2, 0.0), (cur_x, cur_y + bw2, z), (cur_x, cur_y, z),
                                           (cur_x, cur_y, 0.0)])
                        cur_x += bl2
                        append_all(verts, [(cur_x, cur_y + bw2, 0.0), (cur_x, cur_y + bw2, z), (cur_x, cur_y, z),
                                           (cur_x, cur_y, 0.0)])
                        cur_x -= bl2
                        cur_y += bw2 + s

                        append_all(faces, [(p, p + 3, p + 2, p + 1), (p + 4, p + 5, p + 6, p + 7),
                                           (p, p + 4, p + 7, p + 3), (p + 3, p + 7, p + 6, p + 2),
                                           (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4)])

            orient_length = not orient_length

        start_orient_length = not start_orient_length
        cur_x += bl + s
        
    return verts, faces


def wood_regular(ow, ol, bw, bl, s_l, s_w, is_length_vary, length_vary, is_width_vary, width_vary, max_boards, is_r_h,
                 r_h, th):
    verts = []
    faces = []
    cur_x = 0.0
    zt = th

    while cur_x < ow:
        if is_width_vary:
            v = bw * width_vary * 0.0048
            bw2 = uniform(bw - v, bw + v)
        else:
            bw2 = bw

        if bw2 + cur_x > ow:
            bw2 = ow - cur_x
        cur_y = 0.0
        counter = 1

        while cur_y < ol:
            z = zt
            if is_r_h:
                v = z * 0.0045 * r_h
                z = uniform(z - v, z + v)
            bl2 = bl
            if is_length_vary:
                v = bl * length_vary * 0.0048
                bl2 = uniform(bl - v, bl + v)
            if (counter >= max_boards and is_length_vary) or cur_y + bl2 > ol:
                bl2 = ol - cur_y         
            p = len(verts)

            append_all(verts, [(cur_x, cur_y, 0.0), (cur_x, cur_y, z), (cur_x+bw2, cur_y, z), (cur_x+bw2, cur_y, 0.0)])
            cur_y += bl2
            append_all(verts, [(cur_x, cur_y, 0.0), (cur_x, cur_y, z), (cur_x+bw2, cur_y, z), (cur_x+bw2, cur_y, 0.0)])
            cur_y += s_l

            append_all(faces, [(p, p + 3, p + 2, p + 1), (p, p + 4, p + 7, p + 3), (p + 3, p + 7, p + 6, p + 2),
                               (p + 1, p + 2, p + 6, p + 5), (p, p + 1, p + 5, p + 4), (p + 4, p + 5, p + 6, p + 7)])
            counter += 1

        cur_x += bw2 + s_w

    return verts, faces


def tile_grout(ow, ol, depth, th):
    verts = []
    faces = []
    z = th - depth
    x = ow
    y = ol

    append_all(verts, [(0.0, 0.0, 0.0), (0.0, 0.0, z), (x, 0.0, z), (x, 0.0, 0.0), (0.0, y, 0.0), (0.0, y, z),
                       (x, y, z), (x, y, 0.0)])

    append_all(faces, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (3, 7, 6, 2), (0, 4, 7, 3)])

    return verts, faces


def tile_cutter(ow, ol):
    verts = []
    faces = []
    z = 0.5
    x = ow
    y = ol

    append_all(verts, [(0.0, 0.0, -0.5), (0.0, 0.0, z), (x, 0.0, z), (x, 0.0, -0.5), (0.0, y, -0.5), (0.0, y, z),
               (x, y, z), (x, y, -0.5)])

    append_all(faces, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (3, 7, 6, 2), (0, 4, 7, 3)])

    return verts, faces


def update_flooring(self, context):
    o = context.object
    mats = [i for i in o.data.materials]

    pre_scale = tuple(o.scale.copy())

    if tuple(o.scale.copy()) != (1.0, 1.0, 1.0) and o.f_object_add == "convert":
        bpy.ops.object.transform_apply(scale=True)

    dim = [(i + 0.1) * METRIC_FOOT for i in tuple(o.dimensions.copy())]
    coords = [0, 0, 0]
    verts, faces = [], []

    # generate faces and vertices
    if o.f_object_add == "add":
        verts, faces = create_flooring(o.f_mat, o.f_if_wood, o.f_if_tile, o.f_over_width, o.f_over_length, o.f_b_width,
                                       o.f_b_length, o.f_b_length2, o.f_is_length_vary, o.f_length_vary, o.f_num_boards,
                                       o.f_space_l, o.f_space_w, o.f_spacing, o.f_t_width, o.f_t_length, o.f_is_offset,
                                       o.f_offset, o.f_is_random_offset, o.f_offset_vary, o.f_t_width2,
                                       o.f_is_width_vary, o.f_width_vary, o.f_max_boards, o.f_is_ran_thickness,
                                       o.f_ran_thickness, o.f_thickness, o.f_hb_direction)
    elif o.f_object_add == "convert":
        verts, faces = create_flooring(o.f_mat, o.f_if_wood, o.f_if_tile, dim[0], dim[1], o.f_b_width, o.f_b_length,
                                       o.f_b_length2, o.f_is_length_vary, o.f_length_vary, o.f_num_boards, o.f_space_l,
                                       o.f_space_w, o.f_spacing, o.f_t_width, o.f_t_length, o.f_is_offset, o.f_offset,
                                       o.f_is_random_offset, o.f_offset_vary, o.f_t_width2, o.f_is_width_vary,
                                       o.f_width_vary, o.f_max_boards, o.f_is_ran_thickness, o.f_ran_thickness,
                                       o.f_thickness, o.f_hb_direction)

    emesh = None
    mesh = None
    if o.f_object_add in ("convert", "add"):     
        emesh = o.data
        mesh = bpy.data.meshes.new(name="flooring")
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)
        
    if o.f_object_add == "convert":
        if o.f_cut_name == "none":  # create cutter object

            for ob in context.scene.objects:
                ob.select = False

            cutter = bpy.data.objects.new(o.name + "_cutter", o.data.copy())
            context.scene.objects.link(cutter)
            cutter.location = o.location.copy()
            cutter.rotation_euler = o.rotation_euler.copy()
            cutter.scale = o.scale.copy()

            o.f_cut_name = cutter.name
            cutter.select = True
            context.scene.objects.active = cutter

            bpy.ops.object.modifier_add(type="SOLIDIFY")
            pos = len(cutter.modifiers) - 1
            cutter.modifiers[pos].offset = 0
            cutter.modifiers[pos].thickness = 1

            o.select = True
            context.scene.objects.active = o

            # getting extreme position
            tup_verts = [vert.co.to_tuple() for vert in o.data.vertices]  # get vertex data
            x, y, z = None, None, None
            for i in tup_verts:  # find smallest x and z values
                if x is None:
                    x = i[0]
                elif i[0] < x:
                    x = i[0]

                if z is None:
                    z = i[2]
                elif i[2] < z:
                    z = i[2]

                if y is None:
                    y = i[1]
                elif i[1] < y:
                    y = i[1]

            position = o.matrix_world * Vector((x, y, z))  # get world space
            coords = position
        elif o.f_cut_name in bpy.data.objects:
            (bpy.data.objects[o.f_cut_name]).name = o.name + "_cutter"
            o.f_cut_name = o.name + "_cutter"
            coords = o.location.copy()
        else:
            self.report({"ERROR"}, "Can't Find Cutter Object")
            bpy.ops.object.delete()

    for i in bpy.data.objects:
        if i.data == emesh:
            i.data = mesh

    emesh.user_clear()
    bpy.data.meshes.remove(emesh)
    
    # modifiers
    if o.f_is_bevel and o.f_mat == "1":
        bpy.ops.object.modifier_add(type="BEVEL")
        pos = len(o.modifiers) - 1
        o.modifiers[pos].segments = o.f_res
        o.modifiers[pos].width = o.f_bevel_amo
        bpy.ops.object.modifier_apply(apply_as="DATA", modifier=o.modifiers[pos].name)
    
    # set position
    if o.f_object_add == "convert":
        o.location = coords
        cutter = bpy.data.objects[o.f_cut_name]

        for ob in bpy.data.objects:
            ob.select = False

        cursor = context.scene.cursor_location.copy()
        o.select = True
        bpy.context.scene.objects.active = o
        bpy.ops.view3d.snap_cursor_to_selected()
        o.select = False

        if o.f_is_cut == "none":             
            cutter.select = True
            bpy.context.scene.objects.active = cutter
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
            bpy.ops.object.move_to_layer(layers=[False for i in range(19)].append(True))
            cutter.select = False
            o.f_is_cut = "cut"

        o.select = True
        bpy.context.scene.objects.active = o
        cutter.location = o.location.copy()
        cutter.rotation_euler = o.rotation_euler.copy()

        if pre_scale != (1.0, 1.0, 1.0):
            layers = [i for i in bpy.context.scene.layers]
            counter = 1
            true = []

            for i in layers:
                if i:
                    true.append(counter)
                counter += 1

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area
                    bpy.ops.view3d.layers(override, nr=20, toggle=True)

            cutter.select = True
            o.select = False
            bpy.context.scene.objects.active = cutter
            cutter.scale = (pre_scale[0], pre_scale[2], pre_scale[1])
            bpy.ops.object.transform_apply(scale=True)
            cutter.select = False

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area           
                    for i in true:
                        bpy.ops.view3d.layers(override, nr=i, extend=True, toggle=True)

                    bpy.ops.view3d.layers(override, nr=20, extend=True, toggle=True)
            bpy.context.scene.objects.active = o
            o.select = True
        bpy.context.scene.cursor_location = cursor  # change cursor location back to original

        # cut
        apply_modifier_boolean(bpy, o, o.f_cut_name)
   
    # create grout
    grout_ob = None
    if o.f_mat == "2":
        if o.f_object_add == "add":
            verts2, faces2 = tile_grout(o.f_over_width, o.f_over_length, o.f_grout_depth, o.f_thickness)
        else:
            c = bpy.data.objects[o.f_cut_name]
            verts2, faces2 = tile_grout(c.dimensions[0], c.dimensions[1], o.f_grout_depth, o.f_thickness)

        grout = bpy.data.meshes.new(name="grout")
        grout.from_pydata(verts2, [], faces2)
        grout_ob = bpy.data.objects.new("grout", grout)  
        context.scene.objects.link(grout_ob)
        grout_ob.rotation_euler = o.rotation_euler
        grout_ob.location = o.location

        if o.f_object_add == "convert":
            o.select = False
            grout_ob.select = True
            context.scene.objects.active = grout_ob

            apply_modifier_boolean(bpy, grout_ob, o.f_cut_name)

            grout_ob.select = False
            o.select = True
            context.scene.objects.active = o
    
    # cut tile or herringbone wood
    if o.f_object_add == "add" and (o.f_mat == "2" and o.f_if_tile in ("2", "4")) or \
            (o.f_mat == "1" and o.f_if_wood in ("3", "4")):
        verts3, faces3 = tile_cutter(o.f_over_width, o.f_over_length)

        cutter_me = bpy.data.meshes.new("cutter")
        cutter_me.from_pydata(verts3, [], faces3)
        cutter_ob = bpy.data.objects.new("cutter", cutter_me)
        context.scene.objects.link(cutter_ob)
        cutter_ob.location = o.location
        cutter_ob.rotation_euler = o.rotation_euler
        cutter_ob.scale = o.scale

        for ob in bpy.data.objects:
            ob.select = False

        o.select = True
        context.scene.objects.active = o
        apply_modifier_boolean(bpy, o, cutter_ob.name)
        o.select = False
        
        # cut grout if needed
        if o.f_mat == "2":
            grout_ob.select = True
            context.scene.objects.active = grout_ob
            apply_modifier_boolean(bpy, grout_ob, cutter_ob.name)
            grout_ob.select = False
        
        cutter_ob.select = True
        context.scene.objects.active = cutter_ob
        bpy.ops.object.delete()
        o.select = True
        context.scene.objects.active = o
    
    # add materials
    if o.f_mat == "2":  # grout material
        enter = True
        for i in mats:
            if "grout_" in i.name or len(mats) >= 2:
                enter = False
        if enter:
            mat = bpy.data.materials.new("grout_temp")
            mat.use_nodes = True
            grout_ob.data.materials.append(mat)
        else:
            mat = bpy.data.materials.get(mats[1].name)
            grout_ob.data.materials.append(mat)
    
    if o.f_is_material or o.f_mat == "2":
        enter = True
        for i in mats:
            if "flooring_" in i.name or len(mats) >= 2:
                enter = False
        if enter:
            mat = bpy.data.materials.new("flooring_" + o.name)
            mat.use_nodes = True
            o.data.materials.append(mat)
        else:
            mat = bpy.data.materials.get(mats[0].name)
            o.data.materials.append(mat)
            
    # join grout
    if o.f_mat == "2":
        vertex_group(self, context)
        for ob in bpy.data.objects:
            ob.select = False

        grout_ob.select = True
        o.select = True
        context.scene.objects.active = o
        bpy.ops.object.join()

    for i in mats:
        if i.name not in o.data.materials:
            mat = bpy.data.materials[i.name]
            o.data.materials.append(mat)
    
    # uv unwrap
    if o.f_unwrap:
        unwrap_flooring(self, context)
        if o.f_random_uv:
            random_uv(self, context)


def unwrap_flooring(self, context):
    o = context.object
    # uv unwrap
    for i in bpy.data.objects:
        i.select = False

    o.select = True
    bpy.context.scene.objects.active = o

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    bpy.ops.object.editmode_toggle()
                    override = bpy.context.copy()
                    override["area"] = area
                    override["region"] = region
                    override["active_object"] = bpy.context.selected_objects[0]
                    bpy.ops.mesh.select_all(action="SELECT")
                    bpy.ops.uv.cube_project(override)
                    bpy.ops.object.editmode_toggle()


def random_uv(self, context):
    for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        bpy.ops.object.editmode_toggle()
                        bpy.ops.mesh.select_all(action = "SELECT")
                        obj = bpy.context.object
                        me = obj.data
                        bm = bmesh.from_edit_mesh(me)      

                        uv_layer = bm.loops.layers.uv.verify()
                        bm.faces.layers.tex.verify()
                        # adjust UVs                        
                        for f in bm.faces:
                            offset = Vector((uniform(-1.0, 1.0), uniform(-1.0, 1.0)))
                            for v in f.loops:
                                luv = v[uv_layer]   
                                luv.uv = (luv.uv + offset).xy

                        bmesh.update_edit_mesh(me)
                        bpy.ops.object.editmode_toggle()


def delete_materials(self, context):
    o = context.object
    if not o.f_is_material and o.f_mat != "2":
        for i in o.data.materials:
            bpy.ops.object.material_slot_remove()

        for i in bpy.data.materials:
            if i.users == 0:
                bpy.data.materials.remove(i)


def preview_materials(self, context):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if bpy.context.object.f_is_preview:
                        space.viewport_shade = 'RENDERED'
                    else:
                        space.viewport_shade = "SOLID"


def vertex_group(self, context):
    o = context.object

    for i in bpy.data.objects:
        i.select = False

    o.select = True
    bpy.context.scene.objects.active = o

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    bpy.ops.object.editmode_toggle()
                    if "JARCH" in o.vertex_groups:
                        group = o.vertex_groups.get("JARCH")
                        o.vertex_groups.remove(group)

                    bpy.ops.object.vertex_group_add()
                    bpy.ops.object.vertex_group_assign()
                    active = o.vertex_groups.active
                    active.name = "JARCH"
                    bpy.ops.object.editmode_toggle()


def flooring_material(self, context):
    o = bpy.context.object
    if o.f_col_image == "":
        self.report({"ERROR"}, "No Color Image Entered")
        return
    if o.f_is_bump and o.f_norm_image == "":
        self.report({"ERROR"}, "No Normal Map Image Entered")
        return

    extra_rot = None
    if o.f_mat == "1" and o.f_if_wood in ("3", "4"):
        extra_rot = 45

    mat = image_material(bpy, o.f_im_scale, o.f_col_image, o.f_norm_image, o.f_bump_amo, o.f_is_bump, "flooring_use",
                         True, 0.1, 0.05, o.f_is_rotate, extra_rot)

    if mat is not None:
        if len(o.data.materials) == 0:
            o.data.materials.append(mat.copy())
        else:
            o.data.materials[0] = mat.copy()
        o.data.materials[0].name = "flooring_" + o.name
    else:
        self.report({"ERROR"}, "Images Not Found, Make Sure Path Is Correct")
        return

    if o.f_mat == "2" and len(o.data.materials) >= 2:
        mat2 = mortar_material(bpy, context, o.f_mortar_color, o.f_mortar_bump, o.data.materials[1].name)
        o.data.materials[1] = mat2.copy()
        o.data.materials[1].name = "mortar_" + o.name

    # remove extra materials
    for i in bpy.data.materials:
        if i.users == 0:
            bpy.data.materials.remove(i)

# properties
tp = bpy.types.Object
tp.f_object_add = StringProperty(default="none", update=update_flooring)
tp.f_cut_name = StringProperty(default="none")
tp.f_is_cut = StringProperty(default="none")
# type/material
tp.f_mat = EnumProperty(items=(("1", "Wood", ""), ("2", "Tile", "")), default="1", description="Material",
                        update=update_flooring, name="")
tp.f_if_wood = EnumProperty(items=(("1", "Regular", ""), ("2", "Parquet", ""), ("3", "Herringbone Parquet", ""),
                                   ("4", "Herringbone", "")), default="1", description="Wood Type",
                            update=update_flooring, name="")
tp.f_if_tile = EnumProperty(items=(("1", "Regular", ""), ("2", "Large + Small", ""), ("3", "Large + Many Small", ""),
                                   ("4", "Hexagonal", "")), default="1", description="Tile Type",
                            update=update_flooring, name="")
# measurements
tp.f_over_width = FloatProperty(name="Overall Width", min=2.00 / METRIC_FOOT, max=100.00 / METRIC_FOOT,
                                default=8.00 / METRIC_FOOT, subtype="DISTANCE", description="Overall Width",
                                update=update_flooring)
tp.f_over_length = FloatProperty(name="Overall Length", min=2.0 / METRIC_FOOT, max=100.00 / METRIC_FOOT,
                                 default=8.00 / METRIC_FOOT, subtype="DISTANCE", description="Overall Length",
                                 update=update_flooring)
tp.f_b_width = FloatProperty(name="Board Width", min=2.00 / METRIC_INCH, max=14.00 / METRIC_INCH,
                             default=6.00 / METRIC_INCH, subtype="DISTANCE", description="Board Width",
                             update=update_flooring)
tp.f_b_length = FloatProperty(name="Board Length", min=4.00 / METRIC_FOOT, max=20.00 / METRIC_FOOT,
                              default=8.00 / METRIC_FOOT, subtype="DISTANCE", description="Board Length",
                              update=update_flooring)
tp.f_b_length2 = FloatProperty(name="Board Length", min=1.00 / METRIC_FOOT, max=4.00 / METRIC_FOOT,
                               default=1.5 / METRIC_FOOT, subtype="DISTANCE", description="Board Length",
                               update=update_flooring)
tp.f_hb_direction = EnumProperty(items=(("1", "Forwards (+y)", ""), ("2", "Backwards (-y)", ""),
                                        ("3", "Right (+x)", ""), ("4", "Left (-x)", "")), name="Direction",
                                 description="Herringbone Direction", update=update_flooring)
tp.f_thickness = FloatProperty(name="Floor Thickness", min=0.75 / METRIC_INCH, max=1.5 / METRIC_INCH,
                               default=1 / METRIC_INCH, subtype="DISTANCE", description="Thickness Of Flooring",
                               update=update_flooring)
tp.f_is_length_vary = BoolProperty(name="Vary Length?", default=False, description="Vary Lengths?",
                                   update=update_flooring)
tp.f_length_vary = FloatProperty(name="Length Variance", min=1.00, max=100.0, default=50.0, subtype="PERCENTAGE",
                                 description="Length Variance", update=update_flooring)
tp.f_max_boards = IntProperty(name="Max # Of Boards", min=2, max=10, default=2,
                              description="Maximum Number Of Boards Possible In One Length", update=update_flooring)
tp.f_is_width_vary = BoolProperty(name="Vary Width?", default=False, description="Vary Widths?", update=update_flooring)
tp.f_width_vary = FloatProperty(name="Width Variance", min=1.00, max=100.0, default=50.0, subtype="PERCENTAGE",
                                description="Width Variance", update=update_flooring)
tp.f_num_boards = IntProperty(name="# Of Boards", min=2, max=6, default=4, description="Number Of Boards In Square",
                              update=update_flooring)
tp.f_space_l = FloatProperty(name="Length Spacing", min=0.001 / METRIC_INCH, max=0.5 / METRIC_INCH,
                             default=0.125 / METRIC_INCH, subtype="DISTANCE",
                             description="Space Between Boards Length Ways", update=update_flooring)
tp.f_space_w = FloatProperty(name="Width Spacing", min=0.001 / METRIC_INCH, max=0.5 / METRIC_INCH,
                             default=0.125 / METRIC_INCH, subtype="DISTANCE",
                             description="Space Between Boards Width Ways", update=update_flooring)
tp.f_spacing = FloatProperty(name="Spacing", min=0.001 / METRIC_INCH, max=1.0 / METRIC_INCH,
                             default=0.25 / METRIC_INCH, subtype="DISTANCE", description="Space Between Tiles",
                             update=update_flooring)
tp.f_is_bevel = BoolProperty(name="Bevel?", default=False, update=update_flooring)
tp.f_res = IntProperty(name="Bevel Resolution", min=1, max=5, default=1, update=update_flooring)
tp.f_bevel_amo = FloatProperty(name="Bevel Amount", min=0.001 / METRIC_INCH, max=0.5 / METRIC_INCH,
                               default=0.15 / METRIC_INCH, subtype="DISTANCE", description="Bevel Amount",
                               update=update_flooring)
tp.f_is_ran_thickness = BoolProperty(name="Random Thickness?", default=False, update=update_flooring)
tp.f_ran_thickness = FloatProperty(name="Thickness Variance", min=0.1, max=100.0, default=50.0, subtype="PERCENTAGE",
                                   update=update_flooring)
# tile specific
tp.f_t_width = FloatProperty(name="Tile Width", min=2.00 / METRIC_INCH, max=24.00 / METRIC_INCH,
                             default=8.00 / METRIC_INCH, subtype="DISTANCE", description="Tile Width",
                             update=update_flooring)
tp.f_t_length = FloatProperty(name="Tile Length", min=2.00 / METRIC_INCH, max=24.00 / METRIC_INCH,
                              default=8.00 / METRIC_INCH, subtype="DISTANCE", description="Tile Length",
                              update=update_flooring)
tp.f_grout_depth = FloatProperty(name="Grout Depth", min=0.01 / METRIC_INCH, max=0.40 / 39.701,
                                 default=0.10 / METRIC_INCH, subtype="DISTANCE", description="Grout Depth",
                                 update=update_flooring)
tp.f_is_offset = BoolProperty(name="Offset Tiles?", default=False, description="Offset Tile Rows",
                              update=update_flooring)
tp.f_offset = FloatProperty(name="Offset", min=0.001, max=100.0, default=50.0, subtype="PERCENTAGE",
                            description="Tile Offset Amount", update=update_flooring)
tp.f_is_random_offset = BoolProperty(name="Random Offset?", default=False, description="Offset Tile Rows Randomly",
                                     update=update_flooring)
tp.f_offset_vary = FloatProperty(name="Offset Variance", min=0.001, max=100.0, default=50.0, subtype="PERCENTAGE",
                                 description="Offset Variance", update=update_flooring)
tp.f_t_width2 = FloatProperty(name="Small Tile Width", min=2.00 / METRIC_INCH, max=10.00 / METRIC_INCH,
                              default=6.00 / METRIC_INCH, subtype="DISTANCE", description="Small Tile Width",
                              update=update_flooring)
# materials
tp.f_is_material = BoolProperty(name="Cycles Materials?", default=False, description="Adds Cycles Materials",
                                update=delete_materials)
tp.f_is_preview = BoolProperty(name="Preview Material?", default=False, description="Preview Material On Object",
                               update=preview_materials)
tp.f_im_scale = FloatProperty(name="Image Scale", max=10.0, min=0.1, default=1.0, description="Change Image Scaling")
tp.f_col_image = StringProperty(name="", subtype="FILE_PATH", description="File Path For Color Image")
tp.f_is_bump = BoolProperty(name="Normal Map?", default=False, description="Add Normal To Material?")
tp.f_norm_image = StringProperty(name="", subtype="FILE_PATH", description="File Path For Normal Map Image")
tp.f_bump_amo = FloatProperty(name="Normal Strength", min=0.001, max=2.000, default=0.250,
                              description="Normal Map Strength")
tp.f_unwrap = BoolProperty(name="UV Unwrap?", default=True, description="UV Unwraps Siding", update=unwrap_flooring)
tp.f_mortar_color = FloatVectorProperty(name="Mortar Color", subtype="COLOR", default=(1.0, 1.0, 1.0), min=0.0, max=1.0,
                                        description="Color For Mortar")
tp.f_mortar_bump = FloatProperty(name="Mortar Bump", min=0.0, max=1.0, default=0.25, description="Mortar Bump Amount")
tp.f_is_rotate = BoolProperty(name="Rotate Image?", default=False, description="Rotate Image 90 Degrees")
tp.f_random_uv = BoolProperty(name="Random UV's?", default=True, description="Random UV's", update=update_flooring)


class FlooringMaterials(bpy.types.Operator):
    bl_idname = "mesh.jarch_flooring_materials"
    bl_label = "Generate\\Update Materials"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        flooring_material(self, context)
        return {"FINISHED"}


class FlooringPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_jarch_flooring"
    bl_label = "JARCH Vis: Flooring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "JARCH Vis"

    def draw(self, context):
        layout = self.layout
        if bpy.context.mode == "EDIT_MESH":
            layout.label("JARCH Vis Doesn't Work In Edit Mode", icon="ERROR")
        else:
            o = context.object
            if o is not None:
                if o.type == "MESH":                    
                    #if o.object_add == "none" and o.s_object_add == "none" and o.ro_object_add == "none":
                        if o.f_object_add in ("convert", "add"):            
                            layout.label("Material:")
                            layout.prop(o, "f_mat", icon="MATERIAL")
                            layout.label("Types:")

                            if o.f_mat == "1":
                                layout.prop(o, "f_if_wood", icon="OBJECT_DATA")
                            elif o.f_mat == "2":
                                layout.prop(o, "f_if_tile", icon="OBJECT_DATA")
                            layout.separator()
                            if o.f_object_add == "add":
                                layout.prop(o, "f_over_width")
                                layout.prop(o, "f_over_length")
                                layout.separator()

                            # width and lengths
                            layout.prop(o, "f_thickness")
                            layout.separator()
                            
                            if o.f_mat == "1":
                                layout.prop(o, "f_b_width")
                                
                                if o.f_if_wood == "1":
                                    layout.prop(o, "f_b_length")
                                layout.separator()
                                
                                if o.f_if_wood == "1": 
                                    layout.prop(o, "f_is_length_vary", icon="NLA")
                                    if o.f_is_length_vary:
                                        layout.prop(o, "f_length_vary")
                                        layout.prop(o, "f_max_boards")
                                        layout.separator()

                                    layout.prop(o, "f_is_width_vary", icon="UV_ISLANDSEL")
                                    if o.f_is_width_vary:
                                        layout.prop(o, "f_width_vary")
                                        layout.separator()

                                    layout.prop(o, "f_is_ran_thickness", icon="RNDCURVE")
                                    if o.f_is_ran_thickness:
                                        layout.prop(o, "f_ran_thickness")

                                    layout.separator()
                                    layout.prop(o, "f_space_w")
                                    layout.prop(o, "f_space_l")
                                    layout.separator()
                                elif o.f_if_wood in ("3", "4"):
                                    layout.prop(o, "f_b_length2")
                                    layout.prop(o, "f_hb_direction")
                                    layout.separator()   
                                
                                if o.f_if_wood != "1": 
                                    layout.prop(o, "f_spacing")
                                    layout.separator()

                                if o.f_if_wood == "2": 
                                    layout.prop(o, "f_num_boards")
                                    layout.separator()
                                
                                # bevel
                                layout.prop(o, "f_is_bevel", icon="MOD_BEVEL")
                                if o.f_is_bevel:
                                    layout.prop(o, "f_res", icon="OUTLINER_DATA_CURVE")
                                    layout.prop(o, "f_bevel_amo")
                                    layout.separator()
                            
                            elif o.f_mat == "2":
                                if o.f_if_tile != "4":
                                    layout.prop(o, "f_t_width")
                                    layout.prop(o, "f_t_length")
                                    layout.separator()
                                else:
                                    layout.prop(o, "f_t_width2")
                                    layout.separator()

                                if o.f_if_tile == "1":
                                    layout.prop(o, "f_is_offset", icon="OOPS")
                                    if o.f_is_offset:
                                        layout.prop(o, "f_is_random_offset", icon="NLA")
                                        if not o.f_is_random_offset:
                                            layout.prop(o, "f_offset")
                                        else:
                                            layout.prop(o, "f_offset_vary")
                                    layout.separator()

                                layout.prop(o, "f_grout_depth")
                                layout.prop(o, "f_spacing")
                                layout.separator()

                            layout.prop(o, "f_unwrap", icon="GROUP_UVS")
                            if o.f_unwrap:
                                layout.prop(o, "f_random_uv", icon="RNDCURVE")
                            layout.separator()
                            
                            if context.scene.render.engine == "CYCLES":
                                layout.prop(o, "f_is_material", icon="MATERIAL")
                            else:
                                layout.label("Materials Only Supported With Cycles", icon="POTATO")
                            
                            if o.f_is_material and context.scene.render.engine == "CYCLES":
                                layout.separator()
                                layout.prop(o, "f_col_image", icon="COLOR")
                                layout.prop(o, "f_is_bump", icon="SMOOTHCURVE")

                                if o.f_is_bump:
                                    layout.prop(o, "f_norm_image", icon="TEXTURE")
                                    layout.prop(o, "f_bump_amo")
                                layout.prop(o, "f_im_scale", icon="MAN_SCALE")
                                layout.prop(o, "f_is_rotate", icon="MAN_ROT")

                                if o.f_mat == "2":
                                    layout.separator()
                                    layout.prop(o, "f_mortar_color", icon="COLOR")
                                    layout.prop(o, "f_mortar_bump")

                                layout.separator()
                                layout.operator("mesh.jarch_flooring_materials", icon="MATERIAL")
                                layout.separator()
                                layout.prop(o, "f_is_preview", icon="SCENE")

                            layout.separator(); layout.operator("mesh.jarch_flooring_update", icon="FILE_REFRESH")
                            layout.operator("mesh.jarch_flooring_mesh", icon="OUTLINER_OB_MESH")
                            layout.operator("mesh.jarch_flooring_delete", icon="CANCEL")
                        else:
                            if o.f_object_add != "mesh":  # o.f_object_add == "none" and o.s_object_add == "none" and o.ro_object_add == "none"
                                layout.operator("mesh.jarch_flooring_convert")
                            elif o.f_object_add == "mesh":
                                layout.label("This Is A Mesh JARCH Vis Object", icon="INFO")
                    #else:
                        #layout.label("This Is Already A JARCH Vis Object", icon="POTATO")
                else:
                    layout.label("Only Mesh Objects Can Be Used", icon="ERROR")
            else:
                layout.operator("mesh.jarch_flooring_add", text="Add Flooring", icon="MESH_GRID")


class FlooringAdd(bpy.types.Operator):
    bl_idname = "mesh.jarch_flooring_add"
    bl_label = "JARCH Vis: Add Flooring"
    bl_description = "JARCH Vis: Flooring Generator"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        o = bpy.context.scene.objects.active
        o.f_object_add = "add"
        return {"FINISHED"}


class FlooringConvert(bpy.types.Operator):
    bl_idname = "mesh.jarch_flooring_convert"
    bl_label = "Convert To Flooring"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        o.f_object_add = "convert"
        return {"FINISHED"}


class FlooringUpdate(bpy.types.Operator):
    bl_idname = "mesh.jarch_flooring_update"
    bl_label = "Update Flooring"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        update_flooring(self, context)
        return {"FINISHED"}


class FlooringMesh(bpy.types.Operator):
    bl_idname = "mesh.jarch_flooring_mesh"
    bl_label = "Convert To Mesh"
    bl_description = "Converts Flooring Object To Normal Object (No Longer Editable)"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        o.f_object_add = "mesh"
        return {"FINISHED"}


class FlooringDelete(bpy.types.Operator):
    bl_idname = "mesh.jarch_flooring_delete"
    bl_label = "Delete Flooring"
    bl_options = {"UNDO", "INTERNAL"}
    
    def execute(self, context):
        o = context.object
        convert = False

        if o.f_object_add == "convert" and o.f_cut_name in bpy.data.objects:  # if converted mesh, then deal with cutter
            cutter = bpy.data.objects[o.f_cut_name]
            o.select = False
            layers = [i for i in bpy.context.scene.layers]
            counter = 1
            true = []

            for i in layers:
                if i:
                    true.append(counter)
                counter += 1

            o_layers = [i for i in bpy.context.object.layers]
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area
                    bpy.ops.view3d.layers(override, nr=20, toggle=True)

            cutter.select = True
            bpy.context.scene.objects.active = cutter
            bpy.ops.object.modifier_remove(modifier="Solidify")
            bpy.ops.object.move_to_layer(layers=o_layers)
            convert = True
            cutter.select = False

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area           
                    for i in true:
                        bpy.ops.view3d.layers(override, nr=i, extend=True, toggle=True)
                    bpy.ops.view3d.layers(override, nr=20, extend=True, toggle=True)

        m_name = o.name
        c_name = o.f_cut_name
        o.select = True
        bpy.context.scene.objects.active = o
        bpy.ops.object.delete()

        for i in bpy.data.materials:
            if i.users == 0:
                bpy.data.materials.remove(i)

        if convert:
            bpy.data.objects[c_name].name = m_name

        return {"FINISHED"}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
